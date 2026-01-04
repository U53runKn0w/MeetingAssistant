from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager

from agent import create_agent, meeting, create_mindmap_chain, create_pref_agent, run_agent_async_generator, generate_answer
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
    username = get_jwt_identity()

    agent_executor = create_agent()
    return Response(generate_answer(agent_executor, {"input": query, "meeting": m, "username": username}),
                    mimetype='text/event-stream')


@app.route('/api/chat/test', methods=['POST'])
@jwt_required()
def chat_test():
    def fake_gen():
        with open("config/demo_result.txt") as f:
            yield f.read()

    return Response(fake_gen(), mimetype='text/event-stream')


@app.route('/api/mindmap', methods=['POST'])
@jwt_required()
def gen_mindmap():
    c = request.json.get('conclusion', '')
    chain = create_mindmap_chain()
    return Response(generate_answer(chain, {"conclusion": c}), mimetype='text/event-stream')


@app.route('/api/preference', methods=['POST'])
@jwt_required()
def gen_preference():
    c = request.json.get('query')
    if c is None:
        return Response("请输入文本", mimetype='text/event-stream'), 500
    current_user = get_jwt_identity()
    chain = create_pref_agent()
    return Response(generate_answer(chain, {"query": c, "username": current_user}), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run(debug=True, port=5000)
