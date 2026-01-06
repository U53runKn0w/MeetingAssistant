from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.manager import db

bp = Blueprint('todos', __name__)


@bp.route('/api/todos', methods=['GET'])
@jwt_required()
def get_todos():
    """获取用户的所有待办事项"""
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        todos = db.get_user_todos(user_id)
        return jsonify({"code": 200, "data": todos}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@bp.route('/api/todos', methods=['POST'])
@jwt_required()
def add_todos():
    """为特定会议添加待办事项"""
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


@bp.route('/api/todos/update', methods=['PUT'])
@jwt_required()
def update_todos():
    """批量更新待办状态或内容"""
    data = request.json
    todos_data = data.get('todos')  # 格式: [{"todo_id": 1, "status": "completed"}]

    if not todos_data:
        return jsonify({"code": 400, "message": "无效的数据"}), 400

    try:
        db.update_todos(todos_data)
        return jsonify({"code": 200, "message": "更新成功"}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@bp.route('/api/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    """更新单个待办事项"""
    data = request.json
    try:
        db.update_todos([{"todo_id": todo_id, **data}])
        return jsonify({"code": 200, "message": "更新成功"}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
