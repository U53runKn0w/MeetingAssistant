from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.manager import db

bp = Blueprint('meetings', __name__)


@bp.route('/api/meetings', methods=['GET'])
@jwt_required()
def get_meetings():
    """获取用户的所有会议"""
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        meetings = db.get_user_meetings(user_id)
        return jsonify({"code": 200, "data": meetings}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@bp.route('/api/meetings/<int:meeting_id>', methods=['GET'])
@jwt_required()
def get_meeting(meeting_id):
    """获取指定会议的详细信息"""
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        meeting = db.get_meeting(meeting_id, user_id)
        if not meeting:
            return jsonify({"code": 404, "message": "会议不存在"}), 404
        return jsonify({"code": 200, "data": meeting}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@bp.route('/api/meetings/<int:meeting_id>/summary', methods=['PUT'])
@jwt_required()
def update_meeting_summary(meeting_id):
    """更新会议纪要和状态"""
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    data = request.get_json()
    summary = data.get('summary')
    status = data.get('status', 'completed')

    if not summary:
        return jsonify({"code": 400, "message": "纪要内容不能为空"}), 400

    try:
        success = db.update_meeting_summary(meeting_id, user_id, summary, status)
        if not success:
            return jsonify({"code": 404, "message": "会议不存在"}), 404
        return jsonify({"code": 200, "message": "更新成功"}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
