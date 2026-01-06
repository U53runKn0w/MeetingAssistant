from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from db.manager import db

bp = Blueprint('auth', __name__)


@bp.route("/api/login", methods=["POST"])
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


@bp.route("/api/user/info", methods=["GET"])
@jwt_required()
def get_user_info():
    username = get_jwt_identity()
    user = db.get_user(username)
    if user:
        return jsonify({
            "user_id": user["user_id"],
            "username": user["username"],
            "nickname": user.get("nickname"),
            "role": user.get("role")
        }), 200
    return jsonify({"msg": "用户不存在"}), 404
