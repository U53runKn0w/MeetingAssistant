import json

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate
import config
import asyncio
from action.tools import extract_meeting_basic_info, parse_meeting_agenda_conclusion, generate_meeting_todo, \
    mark_meeting_follow_up, generate_user_preferences, get_user_info
from config import template, meeting, template_perference, template_mindmap
from db.manager import db


def create_agent(callbacks=None):
    callbacks = callbacks or []

    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        max_retries=2,
        callbacks=callbacks,
        streaming=True,
        stop_sequences=["\nObservation:"],
    )

    tools = [extract_meeting_basic_info,
             parse_meeting_agenda_conclusion,
             generate_meeting_todo,
             mark_meeting_follow_up,
             get_user_info]

    prompt = PromptTemplate.from_template(template)

    react_agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    agent_executor = AgentExecutor(
        agent=react_agent,
        tools=tools,
        verbose=config.VERBOSE,
        max_iterations=config.MAX_ITERATIONS,
        handle_parsing_errors=True,
        callbacks=callbacks,
    )

    return agent_executor


def create_pref_agent(callbacks=None):
    callbacks = callbacks or []

    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        max_retries=2,
        callbacks=callbacks,
        streaming=True,
        stop_sequences=["\nObservation:"],
    )

    tools = [extract_meeting_basic_info,
             parse_meeting_agenda_conclusion,
             generate_meeting_todo,
             mark_meeting_follow_up,
             generate_user_preferences]

    prompt = PromptTemplate.from_template(template_perference)

    react_agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    agent_executor = AgentExecutor(
        agent=react_agent,
        tools=tools,
        verbose=config.VERBOSE,
        max_iterations=config.MAX_ITERATIONS,
        handle_parsing_errors=True,
        callbacks=callbacks,
    )

    return agent_executor


def create_mindmap_chain(callbacks=None):
    callbacks = callbacks or []

    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        max_retries=2,
        callbacks=callbacks,
        streaming=True,
        stop_sequences=["\nObservation:"],
    )

    prompt = PromptTemplate.from_template(template_mindmap)
    chain = prompt | llm | StrOutputParser()

    return chain


async def run_query_async(agent_executor, query: str, has_meeting: bool = True):
    print(f"🤔 用户问题: {query}")

    async for event in agent_executor.astream_events(
            {"input": query, "meeting": meeting} if has_meeting else {"input": query},
            version="v2",
    ):
        kind = event["event"]

        if kind == "on_tool_start":
            print(f"\n[工具开始] 正在使用: {event['name']}")

        elif kind == "on_tool_end":
            print(f"[工具完成] 结果: {event['data'].get('output')}")

        elif kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                if content.endswith("\n\n"):
                    content = content[:-1]
                print(content, end="", flush=True)


def parse_react_content(full_text):
    patterns = [
        {'label': 'Thought', 'marker': 'Thought:'},
        {'label': 'Action', 'marker': 'Action:'},
        {'label': 'Action Input', 'marker': 'Action Input:'},
        {'label': 'Final Answer', 'marker': 'Final Answer:'}
    ]

    # 寻找标识符位置
    positions = []
    for p in patterns:
        index = full_text.find(p['marker'])
        if index != -1:
            positions.append({'index': index, 'label': p['label'], 'marker': p['marker']})

    # 按索引排序
    positions.sort(key=lambda x: x['index'])

    if not positions:
        return [{'type': 'Thought', 'text': full_text}]

    result = []
    for i in range(len(positions)):
        start = positions[i]['index'] + len(positions[i]['marker'])
        end = positions[i + 1]['index'] if i + 1 < len(positions) else len(full_text)

        content = full_text[start:end].strip()
        result.append({
            'type': positions[i]['label'],
            'text': content
        })

    return result


async def run_agent_async_generator(executor, data, session_id=None):
    # 用于存储最终解析后的结构化消息数组
    final_chat_history = []
    # 模拟前端的 rawAgentBuffer
    raw_agent_buffer = ""

    if session_id:
        yield f"data: {json.dumps({'type': 'meta', 'content': session_id})}\n\n"

    async for event in executor.astream_events(data, version="v2"):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                raw_agent_buffer += content  # 累积 buffer
                yield f"data: {json.dumps({'type': 'stream', 'content': content})}\n\n"

        elif kind == "on_tool_start":
            tool_name = event["name"]
            yield f"data: {json.dumps({'type': 'status', 'content': f'正在调用工具: {tool_name}...'})}\n\n"

        elif kind == "on_tool_end":
            # 1. 遇到 Observation 前，先解析并归档之前的 Agent Buffer
            if raw_agent_buffer:
                parsed_segments = parse_react_content(raw_agent_buffer)
                final_chat_history.extend(parsed_segments)
                raw_agent_buffer = ""  # 清空，同前端逻辑

            # 2. 处理 Observation
            tool_output = event["data"].get("output")
            # 模拟前端 content.substring(content.indexOf(':') + 1).trim()
            obs_text = str(tool_output).strip()
            final_chat_history.append({'type': 'Observation', 'text': obs_text})

            yield f"data: {json.dumps({'type': 'observation', 'content': f'Observation: {tool_output}'})}\n\n"

        elif kind == "on_chain_end" and event["name"] == "AgentExecutor":
            # 最后结束前，处理残留在 buffer 中的 Final Answer
            if raw_agent_buffer:
                parsed_segments = parse_react_content(raw_agent_buffer)
                final_chat_history.extend(parsed_segments)

            # --- 存储逻辑 ---
            # 在这里将 final_chat_history 存入数据库
            db.save_chat_steps(session_id, final_chat_history)
            # print("完整消息记录:", json.dumps(final_chat_history, ensure_ascii=False, indent=2))

            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"


def generate_answer(chain, data, session_id=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    gen = run_agent_async_generator(chain, data, session_id)

    try:
        while True:
            chunk = loop.run_until_complete(gen.__anext__())
            yield chunk
    except StopAsyncIteration:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    # agent = create_agent()
    agent = create_pref_agent()
    while True:
        try:
            user_input = input("👤 请输入您的问题: ").strip()
            if not user_input or user_input.strip() == "":
                continue
            asyncio.run(run_query_async(agent, user_input))
            print()
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出，祝您旅途愉快！\n")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}\n")
            continue
