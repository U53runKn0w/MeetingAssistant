from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.manager import db

bp = Blueprint('history', __name__)


@bp.route('/api/history', methods=['GET'])
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


@bp.route('/api/history/<session_id>', methods=['GET'])
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


@bp.route('/api/history/save', methods=['POST'])
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


@bp.route('/api/history/<session_id>', methods=['DELETE'])
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
