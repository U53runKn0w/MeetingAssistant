from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager


def create_app():
    """创建并配置 Flask 应用实例"""
    app = Flask(__name__)
    CORS(app)
    app.config["JWT_SECRET_KEY"] = "meeting_assistant"
    jwt = JWTManager(app)

    # 注册路由蓝图
    from api import auth, chat, history, todos, meetings, preferences, transcript, results
    app.register_blueprint(auth.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(history.bp)
    app.register_blueprint(todos.bp)
    app.register_blueprint(meetings.bp)
    app.register_blueprint(preferences.bp)
    app.register_blueprint(transcript.bp)
    app.register_blueprint(results.bp)

    return app
