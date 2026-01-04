import json
from contextlib import suppress
from typing import List
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from db.manager import db
from .models import BasicInfo, AgendaConclusion, TodoItem, FollowUp, Preference

shared_llm = ChatDeepSeek(model="deepseek-chat", temperature=0, streaming=True)


@tool
def extract_meeting_basic_info(text: str) -> dict:
    """
    【功能】从会议的关键片段中提取元数据（基础信息）。
    【输入限制】输入应为包含会议背景、自我介绍或开场白的关键语句，而非全量冗长的转录文本。
    【提取字段】
    - attendees: 参会人员姓名列表
    - time: 会议具体日期及时间点
    - subject: 会议讨论的核心主题
    - duration: 会议总耗时
    【应用场景】用于填充会议纪要的头部基本信息。
    """
    structured_llm = shared_llm.with_structured_output(BasicInfo)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "从会议文本中提取参会人、时间、主题和时长，时间需转换为ISO格式"),
        ("user", "{text}")
    ])
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    return result.model_dump()


@tool
def parse_meeting_agenda_conclusion(text: str) -> List[dict]:
    """
    【功能】分析会议关键讨论点并总结结论。
    【输入限制】输入应为经过初步筛选的、包含实质性讨论内容的关键句集合，无关部分请用...省略。
    【提取字段】
    - agenda: 核心议题或具体的讨论点
    - conclusion: 最终达成的共识、定论或处理方案
    【应用场景】用于构建会议纪要的正文“议程回顾”部分。
    """

    class AgendaList(BaseModel):
        items: List[AgendaConclusion]

    structured_llm = shared_llm.with_structured_output(AgendaList)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个会议记录员。请基于关键讨论内容，提取所有核心议题及其对应结论。"),
        ("user", "{text}")
    ])
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    return [item.model_dump() for item in result.items]


@tool
def generate_meeting_todo(text: str) -> List[dict]:
    """
    【功能】从会议执行相关的关键句中提取 Action Items（待办事项）。
    【输入限制】输入应为涉及任务分配、责任归属、截止日期要求的关键语句，无关部分请用...省略。
    【提取字段】
    - owner: 明确的任务负责人姓名
    - task: 具体的任务描述
    - deadline: 完成时限（若未提及则填“待确认”）
    【应用场景】用于生成会议纪要底部的任务分工表。
    """

    class TodoList(BaseModel):
        todos: List[TodoItem]

    structured_llm = shared_llm.with_structured_output(TodoList)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个项目经理。请从提供的关键句中识别待办事项，确保包含负责人和具体任务。"),
        ("user", "{text}")
    ])
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    return [todo.model_dump() for todo in result.todos]


@tool
def mark_meeting_follow_up(text: str) -> List[dict]:
    """
    【功能】识别关键句中隐含的风险、争议或后续需调研的未决事项。
    【输入限制】输入应为表现出意见分歧、不确定性或需要“会后再议”的关键描述，无关部分请用...省略。
    【提取字段】
    - topic: 争议点或待核实的技术/业务问题
    - reason: 需要跟进的具体原因（如：数据不足、需跨部门协调等）
    【应用场景】用于风险提示及作为下次会议的预研输入。
    """

    class FollowUpList(BaseModel):
        follow_ups: List[FollowUp]

    structured_llm = shared_llm.with_structured_output(FollowUpList)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个风险控制专家。请从关键句中识别出尚未解决、存在争议或需要进一步核实的点。"),
        ("user", "{text}")
    ])
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    return [fu.model_dump() for fu in result.follow_ups]


@tool
def generate_user_preferences(text: str, user_id: int) -> List[dict]:
    """
    【功能】从用户描述中提取个性化偏好设置。
    【输入限制】
    - text: 输入应为用户明确表达的喜好、习惯或特定需求的描述。
    - user_id: 用于标识用户身份的id。
    【提取字段】
    - category: 偏好类别（如：通知设置、界面主题、语言偏好等）
    - preference: 具体的偏好值或选项
    【应用场景】用于定制化用户体验及系统推荐。
    """

    class PreferenceList(BaseModel):
        preferences: List[Preference]

    structured_llm = shared_llm.with_structured_output(PreferenceList)
    prompt_analyze_preference = ChatPromptTemplate.from_messages([
        ("system", """你是一个用户体验设计师，你需要从用户问题中提取偏好，并直接输出标准化结果：
         1. 若新类别与现有类别（{existing_prefs}）语义相同（如“所在部门”和“部门”），必须统一为现有类别名称
         2. 若为新类别，需简化名称（如“我希望的称呼方式”→“称呼”）"""),
        ("user", "{text}")
    ])
    chain = prompt_analyze_preference | structured_llm
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
def get_user_info(username: str):
    """
    【功能】查询指定用户在提问前的历史画像数据，包括个性化偏好、历史会议记录及历史待办事项。
    【输入限制】
    - username: 用户的标准账号名称或系统登录名。
    【提取字段】
    - preferences: 用户已锁定的偏好设置字典（如主题、通知习惯等）。
    - meetings: 该用户参与过的历史会议列表。
    - todos: 分配给该用户的所有待办事项及其完成状态。
    【应用场景】在执行任何个性化操作前（如生成会议总结、规划任务），用于初始化用户上下文背景。
    """

    user_id = db.get_user(username).get('user_id')
    pref = db.get_user_preference_dict(user_id=user_id)
    meetings = db.get_user_meetings(user_id=user_id)
    todos = db.get_user_todos(user_id=user_id)
    return {
        "preferences": pref,
        "meetings": meetings,
        "todos": todos,
    }