from datetime import datetime

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager

from agent import create_agent, meeting, create_mindmap_chain, create_pref_agent, generate_answer
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
    username = get_jwt_identity()
    m = request.json.get('meeting', meeting)
    query = request.json.get('query', '请总结会议内容')
    session_id = request.json.get('session_id')
    step_offset = request.json.get('step_offset', 0)  # 新增：从第几步开始输出
    if m.strip() == '':
        m = meeting
    if query.strip() == '':
        query = '请总结会议内容'
    if not session_id:
        user_id = db.get_user_id(username)
        session_id = db.create_chat_session(user_id, query, m)
    else:
        # 拉取聊天记录
        pass

    agent_executor = create_agent()
    return Response(generate_answer(agent_executor, {"input": query, "meeting": m, "username": username}, session_id, step_offset),
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
    query = request.json.get('query')
    if query is None:
        return Response("请输入文本", mimetype='text/event-stream'), 500
    current_user = get_jwt_identity()
    chain = create_pref_agent()
    return Response(generate_answer(chain, {"input": query, "username": current_user}), mimetype='text/event-stream')


@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    """侧边栏接口：获取历史列表"""
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        data = db.get_history_list(user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history/<session_id>', methods=['GET'])
@jwt_required()
def get_chat_detail(session_id):
    """详情接口：点击侧边栏项后加载对话内容"""
    try:
        steps = db.get_chat_detail(session_id)
        if not steps:
            return jsonify({"error": "未找到记录"}), 404
        return jsonify(steps), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history/save', methods=['POST'])
@jwt_required()
def save_conversation():
    """保存新对话接口（模型回答完成后调用）"""
    req_data = request.json  # 期望格式: { "title": "...", "steps": [...] }
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        # 1. 创建 Session
        session_id = db.create_chat_session(user_id, req_data.get('title'))
        # 2. 保存步骤
        db.save_dialog_steps(session_id, req_data.get('steps'))
        return jsonify({"status": "success", "session_id": session_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history/<session_id>', methods=['DELETE'])
@jwt_required()
def delete_history(session_id):
    """删除指定的历史记录"""
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        success = db.delete_chat_session(session_id, user_id)
        if success:
            return jsonify({"message": "删除成功"}), 200
        else:
            return jsonify({"error": "未找到记录或无权删除"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 1. 获取用户的所有待办事项
@app.route('/api/todos', methods=['GET'])
@jwt_required()
def get_todos():
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        todos = db.get_user_todos(user_id)
        return jsonify({"code": 200, "data": todos}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 2. 为特定会议添加待办事项
@app.route('/api/todos', methods=['POST'])
@jwt_required()
def add_todos():
    data = request.json
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    meeting_id = data.get('meeting_id')
    todos_list = data.get('todos')  # 格式: [{"owner": "张三", "task": "写报告", "deadline": datetime}]

    if not all([user_id, meeting_id, todos_list]):
        return jsonify({"code": 400, "message": "缺少必要参数"}), 400

    try:
        # 注意：这里需要处理 deadline 字符串转 datetime 对象（如果数据库模型需要的话）
        for t in todos_list:
            if t.get('deadline') and isinstance(t['deadline'], str):
                t['deadline'] = datetime.fromisoformat(t['deadline'])

        db.add_todos(user_id, meeting_id, todos_list)
        return jsonify({"code": 200, "message": "添加成功"}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 3. 批量更新待办状态或内容
@app.route('/api/todos/update', methods=['PUT'])
@jwt_required()
def update_todos():
    data = request.json
    todos_data = data.get('todos')  # 格式: [{"todo_id": 1, "status": "completed"}]

    if not todos_data:
        return jsonify({"code": 400, "message": "无效的数据"}), 400

    try:
        db.update_todos(todos_data)
        return jsonify({"code": 200, "message": "更新成功"}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 4. 更新单个待办事项
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    data = request.json
    try:
        db.update_todos([{"todo_id": todo_id} | data])
        return jsonify({"code": 200, "message": "更新成功"}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@app.route('/api/meetings', methods=['GET'])
@jwt_required()
def get_meetings():
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        meetings = db.get_user_meetings(user_id)
        return jsonify({"code": 200, "data": meetings}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 获取用户偏好
@app.route('/api/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        prefs = db.get_user_preference_dict(user_id)
        # 将字典转换为列表格式方便前端循环
        prefs_list = [{"category": k, "value": v} for k, v in prefs.items()]
        return jsonify({"code": 200, "data": prefs_list}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 更新偏好 (可选)
@app.route('/api/preferences', methods=['POST'])
@jwt_required()
def update_preference():
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    data = request.json
    category = data.get('category')
    value = data.get('value')

    if not category or not value:
        return jsonify({"code": 400, "message": "缺少分类或值"}), 400

    try:
        db.add_user_preference(user_id, category, value)
        return jsonify({"code": 200, "message": "偏好已更新"}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
