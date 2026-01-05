import json
from datetime import datetime

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import asyncio

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager

from action.models import MeetingRecord, BasicInfo, AgendaConclusion, TodoItem, FollowUp
from agent import create_agent, meeting, create_mindmap_chain, create_pref_agent
from db.manager import db
from db.service import MeetingService

app = Flask(__name__)
CORS(app)  # 允许所有来源跨域
app.config["JWT_SECRET_KEY"] = "meeting_assistant"
jwt = JWTManager(app)


@app.route("/api/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    remember = request.json.get("remember")

    if db.check_user(username, password):
        # 创建访问令牌
        if remember:
            access_token = create_access_token(identity=username, expires_delta=False)
        else:
            access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "用户名或密码错误"}), 401


@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    # m = request.json.get('meeting', meeting)
    # if m.strip() == '':
    #     m = meeting
    # query = request.json.get('query', '请总结会议内容')
    # if query.strip() == '':
    #     query = '请总结会议内容'
    # current_user = get_jwt_identity()

    data = request.json
    m_text = data.get('meeting', '').strip()
    query = data.get('query', '请总结会议内容')
    meeting_id = data.get('meeting_id')

    current_user = get_jwt_identity()
    user_info = db.get_user(current_user)
    user_id = user_info['user_id']

    # 1. 自动创建会议逻辑 (如果只有文本没有 ID)
    created_new_meeting = False
    if not meeting_id and m_text:
        default_subject = f"会议记录 {datetime.now().strftime('%m-%d %H:%M')}"
        meeting_id = db.add_meeting(
            user_id=user_id,
            subject=default_subject,
            start_time=datetime.now(),
            content=m_text
        )
        created_new_meeting = True

    # 2. 【关键】保存用户的提问 (Role: user)
    if meeting_id:
        db.add_conversation(meeting_id=meeting_id, role='user', content=query)

    def generate():

        if created_new_meeting:
            yield f"data: {json.dumps({'type': 'meeting_created', 'content': {'id': meeting_id, 'title': default_subject}})}\n\n"

        agent_executor = create_agent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        ai_response_accumulator = ""

        async def run_agent():
            nonlocal ai_response_accumulator
            async for event in agent_executor.astream_events(
                    {"input": query, "meeting": m_text, "username": current_user},
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
            if meeting_id and ai_response_accumulator:
                db.add_conversation(meeting_id=meeting_id, role='assistant', content=ai_response_accumulator)
            loop.close()

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/chat/test', methods=['POST'])
@jwt_required()
def chat_test():
    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_agent():
            with open("config/demo_result.txt") as f:
                yield f.read()

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


@app.route('/api/mindmap', methods=['POST'])
@jwt_required()
def gen_mindmap():
    c = request.json.get('conclusion', '')

    def generate():
        chain = create_mindmap_chain()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_agent():
            async for event in chain.astream_events(
                    {"conclusion": c},
                    version="v2",
            ):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield f"data: {json.dumps({'type': 'stream', 'content': content})}\n\n"

                elif kind == "on_tool_start":
                    tool_name = event["name"]
                    yield f"data: {json.dumps({'type': 'status', 'content': f'正在调用工具: {tool_name}...'})}\n\n"

                elif kind == "on_tool_end":
                    tool_output = event["data"].get("output")
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


@app.route('/api/preference', methods=['POST'])
@jwt_required()
def gen_preference():
    c = request.json.get('query')
    if c is None:
        return Response("请输入文本", mimetype='text/event-stream'), 500

    def generate():
        chain = create_pref_agent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_agent():
            async for event in chain.astream_events(
                    {"query": c},
                    version="v2",
            ):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield f"data: {json.dumps({'type': 'stream', 'content': content})}\n\n"

                elif kind == "on_tool_start":
                    tool_name = event["name"]
                    yield f"data: {json.dumps({'type': 'status', 'content': f'正在调用工具: {tool_name}...'})}\n\n"

                elif kind == "on_tool_end":
                    tool_output = event["data"].get("output")
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


@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    current_user = get_jwt_identity()
    user_info = db.get_user(current_user)
    if not user_info:
        return jsonify({"msg": "User not found"}), 404

    # 调用 db.manager 中的方法获取该用户的会议列表
    meetings = db.get_user_meetings(user_info['user_id'])
    return jsonify(meetings), 200


@app.route('/api/save_meeting', methods=['POST'])
@jwt_required()
def save_meeting():
    data = request.json
    current_user = get_jwt_identity()
    user_id = db.get_user(current_user)['user_id']

    try:
        # 构建 Pydantic 对象
        record = MeetingRecord(
            user_id=user_id,
            raw_text=data.get('raw_text', ''),
            basic_info=BasicInfo(**data['extract_meeting_basic_info']),
            agendas=[AgendaConclusion(**item) for item in data['parse_meeting_agenda_conclusion']],
            todos=[TodoItem(**item) for item in data['generate_meeting_todo']],
            follow_ups=[FollowUp(**item) for item in data['mark_meeting_follow_up']]
        )

        # 调用 Service 保存 (需要初始化 Service)
        service = MeetingService(db)
        meeting_id = service.process_meeting_record(record)

        return jsonify({"msg": "保存成功", "meeting_id": meeting_id}), 200
    except Exception as e:
        print(e)
        return jsonify({"msg": f"保存失败: {str(e)}"}), 500


@app.route('/api/meetings/<int:meeting_id>', methods=['GET'])
@jwt_required()
def get_meeting_detail(meeting_id):
    current_user = get_jwt_identity()
    user_info = db.get_user(current_user)

    # 这一步会去查数据库
    meeting_ = db.get_meeting(meeting_id, user_info['user_id'])

    if not meeting_:
        return jsonify({"msg": "Meeting not found"}), 404

    return jsonify(meeting_), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
