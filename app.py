import json

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import asyncio

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager

from agent import create_agent, meeting
from db.manager import db

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
    m = request.json.get('meeting', meeting)
    if m.strip() == '':
        m = meeting
    query = request.json.get('query', '请总结会议内容')
    if query.strip() == '':
        query = '请总结会议内容'
    # 获取当前登录用户的身份（即登录时传入的 identity）
    current_user = get_jwt_identity()

    def generate():
        agent_executor = create_agent()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_agent():
            async for event in agent_executor.astream_events(
                    {"input": query, "meeting": m, "username": current_user},
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
