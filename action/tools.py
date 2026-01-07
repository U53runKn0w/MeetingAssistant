import json
from contextlib import suppress
from datetime import datetime
from typing import List
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from db.manager import db
from .models import BasicInfo, AgendaConclusion, TodoItem, FollowUp, Preference


@tool
def search_term_explanation(terms: str) -> str:
    """
    【适用场景】当会议中出现AI不理解的专有名词、技术术语、行业术语时使用。
    【调用时机】遇到陌生名词、缩写、专业术语需要联网查询解释时。
    【参数要求】terms可以是一个或多个名词，多个名词用逗号分隔。例如："AGI, RAG" 或 "微服务架构"。
    【返回内容】返回每个名词的简要解释，包含定义、背景和应用场景。
    【工作原理】使用DuckDuckGo搜索引擎查询术语的定义和解释信息。
    """
    try:
        from ddgs import DDGS

        # 解析输入的多个术语
        term_list = [t.strip() for t in terms.split(',') if t.strip()]

        results = []

        for term in term_list:
            try:
                # 使用DuckDuckGo搜索，添加重试机制和更简单的搜索参数
                ddgs = DDGS()
                search_results = []

                # 尝试搜索，最多重试2次
                for attempt in range(3):
                    try:
                        search_results = list(ddgs.text(
                            f"{term} 是什么 定义",
                            max_results=2,
                            timeout=10
                        ))
                        if search_results:
                            break
                    except Exception as e:
                        if attempt < 2:
                            continue
                        raise

                if not search_results:
                    results.append({
                        "term": term,
                        "explanation": f"未找到关于「{term}」的相关解释信息，可能是网络连接问题或该术语过于生僻。"
                    })
                    continue

                # 整合搜索结果
                explanations = []
                for result in search_results:
                    body = result.get('body', '')
                    if body:
                        # 简化解释，提取关键信息
                        explanation = body[:200] + "..." if len(body) > 200 else body
                        explanations.append(explanation)

                # 生成简洁的解释摘要
                if explanations:
                    combined_explanation = " ".join(explanations[:2])  # 只取前两个结果
                else:
                    combined_explanation = f"找到相关结果但无法提取解释内容。"

                results.append({
                    "term": term,
                    "explanation": combined_explanation
                })

            except Exception as e:
                results.append({
                    "term": term,
                    "explanation": f"搜索「{term}」时遇到网络错误，请稍后重试。"
                })

        # 格式化返回结果
        if len(results) == 1:
            return f"【{results[0]['term']}】{results[0]['explanation']}"
        else:
            formatted_result = []
            for r in results:
                formatted_result.append(f"【{r['term']}】{r['explanation']}")
            return "".join(formatted_result)

    except ImportError:
        return "错误：请先安装duckduckgo-search库（pip install duckduckgo-search）"
    except Exception as e:
        return f"搜索服务异常：{str(e)}"


shared_llm = ChatDeepSeek(model="deepseek-chat", temperature=0, streaming=True)


@tool
def extract_meeting_basic_info(text: str) -> dict:
    """
    【适用场景】当需要初始化会议纪要的头部信息（主题、时间、人员、时长）时使用。
    【调用时机】通常在处理会议录音开场白或会议通知文本时首先调用。
    【参数要求】text 应为会议的前 5-10% 内容或包含自我介绍的关键片段。
    【返回内容】返回包含 attendees(list), time(ISO string), subject(str), duration(str) 的字典。
    """
    structured_llm = shared_llm.with_structured_output(BasicInfo)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个精准的元数据提取专家。请从会议片段中提取信息：
         1. 参会人：仅提取人名，去除职位，存入列表。
         2. 时间：识别日期和具体时刻，统一转换为 ISO 8601 格式（YYYY-MM-DD HH:mm）。
         3. 主题：用 15 字以内的简洁短语概括。
         4. 时长：提取如“1小时”、“45分钟”等描述。
         注意：若某项信息未提及，请填入“未知”或空列表，严禁幻想。"""),
        ("user", "{text}")
    ])
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    return result.model_dump()


@tool
def parse_meeting_agenda_conclusion(text: str) -> List[dict]:
    """
    【适用场景】提取会议的核心讨论点及最终达成的共识。
    【调用时机】用于构建纪要的“议程回顾”或“核心决议”模块。
    【参数要求】传入包含实质性讨论的文本段落。若文本过长，请分段调用。
    【返回内容】返回对象列表，每个对象包含 agenda(议题) 和 conclusion(结论)。
    """

    class AgendaList(BaseModel):
        items: List[AgendaConclusion]

    structured_llm = shared_llm.with_structured_output(AgendaList)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的会议速记员。请对关键讨论内容进行结构化提炼：
         - 议程（agenda）：描述讨论的具体问题或事项（如“关于Q3预算的审核”）。
         - 结论（conclusion）：描述最终达成的决定、共识或明确的现状（如“通过预算，但需削减20%营销费用”）。
         注意：忽略寒暄和无意义的插嘴，每项议程必须对应一个明确的结论。"""),
        ("user", "{text}")
    ])
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    return [item.model_dump() for item in result.items]


@tool
def generate_meeting_todo(text: str) -> List[dict]:
    """
    【适用场景】识别会议中明确分配的任务、责任人及截止日期。
    【调用时机】当文本出现“负责”、“跟进”、“完成”、“截止日期”等动词时调用。
    【参数要求】包含任务分配指令的关键句。
    【返回内容】返回 todo 列表，包含 owner(负责人), task(任务描述), deadline(截止时间，默认为“待确认”)。
    """

    class TodoList(BaseModel):
        todos: List[TodoItem]

    structured_llm = shared_llm.with_structured_output(TodoList)
    # 获取当前日期，方便 LLM 换算“明天”、“下周”
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""你是一个严谨的项目经理。当前时间是：{current_date}。
             请从文本中提取行动项，并遵守以下规则：
             1. 负责人（owner）：具体人名或部门。
             2. 任务（task）：以动词开头的具体动作描述。
             3. 截止日期（deadline）：
                - 必须转化为具体的时间格式 (YYYY-MM-DD HH:MM)。
                - 如果文本说“明天”，请根据当前时间 {current_date} 计算出日期。
                - 如果只提到日期没提到小时，默认设为 18:00。
                - 若文本中完全未提及时间，统一填入“待确认”。"""),
        ("user", "{text}")
    ])
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    return [todo.model_dump() for todo in result.todos]


@tool
def mark_meeting_follow_up(text: str) -> List[dict]:
    """
    【适用场景】识别会议中未达成一致、存在争议、有风险或需要会后调研的事项。
    【调用时机】当讨论出现“不确定”、“以后再说”、“需要确认”、“存在风险”等信号词时使用。
    【参数要求】反映意见分歧或不确定性的上下文。
    【注意】不要将已确定的 Todo 误认为 Follow-up。
    """

    class FollowUpList(BaseModel):
        follow_ups: List[FollowUp]

    structured_llm = shared_llm.with_structured_output(FollowUpList)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个敏锐的风险控制专家。请识别会议中的“尾巴”：
         - 争议点（topic）：双方各执一词、尚未达成一致的矛盾点。
         - 待核实（reason）：因数据缺失、权限不足或时间限制而推迟到会后处理的事项。
         注意：区分“待办事项”与“跟进事项”，后者通常包含不确定性和需要进一步调研的属性。"""),
        ("user", "{text}")
    ])
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    return [fu.model_dump() for fu in result.follow_ups]


@tool
def generate_user_preferences(param: str) -> List[dict]:
    """
    【适用场景】当用户明确提出对总结格式、称呼方式、关注重点有特殊要求时，将其持久化到数据库。
    【调用时机】用户说“以后请叫我X总”、“总结里多关注技术细节”或“我不需要表格”等个性化指令时。
    【参数要求】以json字符串给出，有两个参数：text为用户的原始要求短语，username为用户名。
    【副作用】此操作会直接修改数据库，请在确认用户意图后调用。
    """

    class PreferenceList(BaseModel):
        preferences: List[Preference]

    param = json.loads(param)
    username = param["username"]
    text = param["text"]
    structured_llm = shared_llm.with_structured_output(PreferenceList)
    prompt_analyze_preference = ChatPromptTemplate.from_messages([
        ("system", """你是一个资深用户体验设计师。你的目标是将非结构化的用户要求转化为标准偏好：
         1. 归类逻辑：
            - 若涉及“怎么称呼”、“语气” -> 类别：个人身份
            - 若涉及“表格”、“HTML”、“排版” -> 类别：输出格式
            - 若涉及“关注点”、“只看老板说话” -> 类别：内容权重
         2. 标准化：参考现有类别 {existing_prefs}，语义相近的必须强行统一，严禁创建冗余类别。
         3. 简洁化：偏好值（preference）应为具体的设定词（如“精简模式”、“专业商务”）。"""),
        ("user", f"{text}")
    ])
    chain = prompt_analyze_preference | structured_llm
    user_id = db.get_user_id(username.strip())
    existing_prefs = db.get_user_preference_dict(user_id=user_id)
    result = chain.invoke({"text": text, "existing_prefs": existing_prefs})
    result_return = [result.model_dump() for result in result.preferences]

    for pref in result_return:
        with suppress(Exception):
            db.add_user_preference(
                user_id=user_id,
                category=pref['category'],
                preference_val=pref['preference']
            )
    return result_return


@tool
def get_user_info(username: str) -> dict:
    """
    【适用场景】Agent 启动时的“第一步”操作。用于加载用户的个性化画像。
    【调用时机】在处理任何具体请求前，先调用此工具以了解用户的偏好（Preference）和历史背景。
    【参数要求】username必须是系统中存在的标准用户名，直接给出值，不要用json。
    【输出价值】获取到的 preferences 应用于指导 Final Answer 的 HTML 风格和内容侧重点。
    """

    user_id = db.get_user(username.strip()).get('user_id')
    pref = db.get_user_preference_dict(user_id=user_id)
    meetings = db.get_user_meetings(user_id=user_id)
    for meeting in meetings:
        del meeting["summary"]
    todos = db.get_user_todos(user_id=user_id)
    return {
        "preferences": pref,
        "meetings": meetings,
        "todos": todos
    }
