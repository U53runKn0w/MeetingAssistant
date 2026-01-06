from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required

from agent import create_agent, meeting, create_mindmap_chain, create_pref_agent, generate_answer

bp = Blueprint('chat', __name__)


@bp.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    from flask_jwt_extended import get_jwt_identity
    from db.manager import db

    username = get_jwt_identity()
    m = request.json.get('meeting', meeting)
    query = request.json.get('query', '请总结会议内容')
    session_id = request.json.get('session_id')
    step_offset = request.json.get('step_offset', 0)
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


@bp.route('/api/chat/test', methods=['POST'])
@jwt_required()
def chat_test():
    def fake_gen():
        with open("config/demo_result.txt") as f:
            yield f.read()

    return Response(fake_gen(), mimetype='text/event-stream')


@bp.route('/api/mindmap', methods=['POST'])
@jwt_required()
def gen_mindmap():
    conclusion = request.json.get('conclusion', '')
    chain = create_mindmap_chain()
    return Response(generate_answer(chain, {"conclusion": conclusion}), mimetype='text/event-stream')


@bp.route('/api/preference', methods=['POST'])
@jwt_required()
def gen_preference():
    from flask_jwt_extended import get_jwt_identity

    query = request.json.get('query')
    if query is None:
        return Response("请输入文本", mimetype='text/event-stream'), 500
    current_user = get_jwt_identity()
    chain = create_pref_agent()
    return Response(generate_answer(chain, {"input": query, "username": current_user}), mimetype='text/event-stream')
