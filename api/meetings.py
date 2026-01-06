from flask import Blueprint, jsonify
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
