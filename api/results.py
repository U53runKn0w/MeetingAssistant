from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.manager import db

bp = Blueprint("results", __name__, url_prefix="/api/results")


@bp.route("/save", methods=["POST"])
@jwt_required()
def save_meeting_results():
    """保存会议分析结果"""
    try:
        username = get_jwt_identity()
        # 从username获取user_id
        user_id = db.get_user_id(username)

        if user_id is None:
            return jsonify({"code": 401, "message": "用户不存在"}), 401

        data = request.get_json()

        # 验证必要字段
        if not data:
            return jsonify({"code": 400, "message": "请求数据不能为空"}), 400

        # 调用数据库方法保存结果
        result = db.save_meeting_results(user_id, data)

        return jsonify({
            "code": 200,
            "message": "保存成功",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"保存失败: {str(e)}"
        }), 500
