from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.manager import db

bp = Blueprint('preferences', __name__)


@bp.route('/api/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """获取用户偏好"""
    username = get_jwt_identity()
    user_id = db.get_user_id(username)
    try:
        prefs = db.get_user_preference_dict(user_id)
        # 将字典转换为列表格式方便前端循环
        prefs_list = [{"category": k, "value": v} for k, v in prefs.items()]
        return jsonify({"code": 200, "data": prefs_list}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@bp.route('/api/preferences', methods=['POST'])
@jwt_required()
def update_preference():
    """更新偏好"""
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


@bp.route('/api/preferences/<category>', methods=['DELETE'])
@jwt_required()
def delete_preference(category):
    """删除偏好"""
    username = get_jwt_identity()
    user_id = db.get_user_id(username)

    if not category:
        return jsonify({"code": 400, "message": "缺少分类"}), 400

    try:
        db.delete_user_preference(user_id, category)
        return jsonify({"code": 200, "message": "偏好已删除"}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
