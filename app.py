import json

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import asyncio

from action.models import MeetingRecord
from agent import create_agent, run_query_async, meeting
from db.manager import MeetingDB
from db.service import MeetingService

app = Flask(__name__)
CORS(app)  # 允许所有来源跨域，开发阶段很方便

agent = create_agent()

TOOL_CONFIG = {
    "extract_meeting_basic_info": {
        "name": "会议基本信息",
        "icon": "bi-info-circle",
        "color": "#2563eb",  # 蓝色
        "desc": "提取会议时间、参会人、主题等核心基础信息"
    },
    "parse_meeting_agenda_conclusion": {
        "name": "议程与结论",
        "icon": "bi-list-check",
        "color": "#10b981",  # 绿色
        "desc": "解析会议讨论议程、达成的结论和关键决策"
    },
    "generate_meeting_todo": {
        "name": "待办事项",
        "icon": "bi-calendar-check",
        "color": "#f59e0b",  # 橙色
        "desc": "生成需要执行的待办事项及责任人、截止时间"
    },
    "mark_meeting_follow_up": {
        "name": "跟进项标记",
        "icon": "bi-exclamation-triangle",
        "color": "#8b5cf6",  # 紫色
        "desc": "标记需要后续跟进的事项和重点关注内容"
    }
}


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(TOOL_CONFIG)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    meeting_text = data.get("meeting_text")

    if not meeting_text or meeting_text.strip() == "":
        return jsonify({"error": "请输入有效的会议记录内容！"}), 400

    results = {}
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        tools = list(TOOL_CONFIG.keys())
        for tool in tools:
            results[tool] = loop.run_until_complete(
                run_query_async(agent, f"Use {tool} on: {meeting_text}")
            )

        return jsonify({
            "success": True,
            "results": results
        })

    except Exception as e:
        return jsonify({"error": f"分析失败：{str(e)}"}), 500


@app.route('/api/chat', methods=['GET'])
def chat():
    m = request.args.get('meeting', meeting)
    query = request.args.get('query', '请总结会议内容')

    def generate():
        agent_executor = create_agent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_agent():
            async for event in agent_executor.astream_events(
                    {"input": query, "meeting": m},
                    version="v2",
            ):
                kind = event["event"]

                # 不包含Observation
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield f"data: {json.dumps({'type': 'stream', 'content': content})}\n\n"

                elif kind == "on_tool_start":
                    tool_name = event["name"]
                    yield f"data: {json.dumps({'type': 'status', 'content': f'正在调用工具: {tool_name}...'})}\n\n"

                elif kind == "on_tool_end":
                    tool_output = event["data"].get("output")
                    # 重要：手动构造 Observation 标签发给前端
                    yield f"data: {json.dumps({'type': 'observation', 'content': f'Observation: {tool_output}'})}\n\n"

                elif kind == "on_chain_end" and event["name"] == "AgentExecutor":
                    yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"

        gen = run_agent()

        try:
            while True:
                chunk = loop.run_until_complete(gen.__anext__())
                yield chunk
        except StopAsyncIteration:
            pass
        finally:
            loop.close()

    return Response(generate(), mimetype='text/event-stream')


# 新增处理会议记录的API
@app.route("/api/process_meeting", methods=["POST"])
def process_meeting():
    data = request.json
    user_id = data.get("user_id")
    meeting_text = data.get("meeting_text")

    if not all([user_id, meeting_text]):
        return jsonify({"error": "缺少用户ID或会议记录"}), 400

    try:
        # 1. 初始化服务
        db = MeetingDB()
        service = MeetingService(db)

        # 2. 提取会议信息
        meeting_record = MeetingRecord(
            basic_info=extract_basic_info(meeting_text),
            agendas=extract_agendas(meeting_text),
            todos=extract_todos(meeting_text),
            follow_ups=extract_follow_ups(meeting_text),
            raw_text=meeting_text,
            user_id=user_id
        )

        # 3. 保存到数据库
        meeting_id = service.process_meeting_record(meeting_record)

        return jsonify({
            "success": True,
            "meeting_id": meeting_id,
            "message": "会议记录处理完成"
        })

    except Exception as e:
        return jsonify({"error": f"处理失败: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
