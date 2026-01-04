from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import PromptTemplate
import config
import asyncio
from action.tools import extract_meeting_basic_info, parse_meeting_agenda_conclusion, generate_meeting_todo, \
    mark_meeting_follow_up, generate_user_preferences, get_user_info
from config import template, meeting, template_no_meeting, template_mindmap


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

    tools = [generate_user_preferences]

    prompt = PromptTemplate.from_template(template_no_meeting)

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
