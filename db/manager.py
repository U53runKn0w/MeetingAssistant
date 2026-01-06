import os
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, select, inspect
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional
from datetime import datetime, timezone

from config import meeting
from db.models import Base, User, Meeting, Attendee, Todo, Preference, ChatSession, DialogStep


class MeetingDB:
    def __init__(self, db_url: str = "sqlite:///db/db.sqlite"):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(bind=self.engine)

        sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init.sql")
        insert_sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "insert.sql")
        inspector = inspect(self.engine)

        if not inspector.has_table("users"):
            if os.path.exists(sql_path):
                print(f"检测到数据库未初始化，正在执行 {sql_path} ...")
                try:
                    conn = self.engine.raw_connection()
                    cursor = conn.cursor()

                    # 1. 执行建表脚本 (init.sql)
                    with open(sql_path, 'r', encoding='utf-8') as f:
                        script = f.read()
                        cursor.executescript(script)

                    # 2. 执行数据插入脚本 (insert.sql) - 建议加个判断是否存在
                    print(f"正在执行数据插入 {insert_sql_path} ...")
                    with open(insert_sql_path, 'r', encoding='utf-8') as f:
                        script = f.read()
                        cursor.executescript(script)

                    # 提交事务
                    conn.commit()
                    print("数据库初始化成功！")

                except Exception as e:
                    print(f"数据库初始化失败: {e}")
            else:
                print("未找到 init.sql，将仅创建空表。")

    # --- 用户操作 ---
    def add_user(self, username: str, password: str) -> int:
        with self.SessionLocal() as session:
            new_user = User(username=username, password=password)
            session.add(new_user)
            session.commit()
            return new_user.user_id

    def get_user(self, username: str) -> Optional[Dict]:
        with self.SessionLocal() as session:
            stmt = select(User).where(User.username == username)
            user = session.execute(stmt).scalar_one_or_none()
            return {"user_id": user.user_id, "username": user.username} if user else None

    def check_user(self, username: str, password: str):
        with self.SessionLocal() as session:
            stmt = select(User).where(User.username == username, User.password == password)
            return session.execute(stmt).scalar_one_or_none() is not None

    def get_user_id(self, username):
        user = self.get_user(username)
        return None if user is None else user["user_id"]

    # --- 会议操作 ---
    def add_meeting(self, user_id: int, subject: str, start_time: datetime,
                    duration: Optional[int] = None,
                    attendees: Optional[List[str]] = None) -> int:
        with self.SessionLocal() as session:
            meeting = Meeting(
                user_id=user_id,
                subject=subject,
                start_time=start_time,
                duration=duration
            )
            if attendees:
                meeting.attendees = [Attendee(name=name) for name in attendees]

            session.add(meeting)
            session.commit()
            return meeting.meeting_id

    def get_user_meetings(self, user_id: int) -> List[Dict]:
        with self.SessionLocal() as session:
            stmt = select(Meeting).where(Meeting.user_id == user_id).order_by(Meeting.start_time.desc())
            results = session.execute(stmt).scalars().all()
            return [
                {"meeting_id": m.meeting_id, "subject": m.subject, "start_time": m.start_time.isoformat()}
                for m in results
            ]

    def get_meeting(self, meeting_id: int, user_id: int) -> Optional[Dict]:
        with self.SessionLocal() as session:
            stmt = select(Meeting).where(Meeting.meeting_id == meeting_id, Meeting.user_id == user_id)
            meeting = session.execute(stmt).scalar_one_or_none()
            if not meeting:
                return None

            return {
                "meeting_id": meeting.meeting_id,
                "subject": meeting.subject,
                "attendees": [a.name for a in meeting.attendees],
                "todos": [{"task": t.task, "owner": t.owner} for t in meeting.todos]
            }

    # --- 待办事项批量操作 ---
    def add_todos(self, user_id: int, meeting_id: int, todos_data: List[Dict]) -> None:
        with self.SessionLocal() as session:
            new_todos = [
                Todo(
                    user_id=user_id,
                    meeting_id=meeting_id,
                    owner=t["owner"],
                    task=t["task"],
                    deadline=t.get("deadline"),
                    status=t.get("status", "pending")
                ) for t in todos_data
            ]
            session.add_all(new_todos)
            session.commit()

    def update_todos(self, todos_data: List[Dict]) -> None:
        with self.SessionLocal() as session:
            for t_data in todos_data:
                stmt = select(Todo).where(Todo.todo_id == t_data["todo_id"])
                todo = session.execute(stmt).scalar_one_or_none()
                if todo:
                    todo.user_id = t_data.get("user_id", todo.user_id)
                    todo.owner = t_data.get("owner", todo.owner)
                    todo.task = t_data.get("task", todo.task)
                    todo.deadline = t_data.get("deadline", todo.deadline)
                    todo.status = t_data.get("status", todo.status)

            session.commit()

    def get_user_todos(self, user_id: int) -> List[Dict]:
        with self.SessionLocal() as session:
            stmt = select(Todo).where(Todo.user_id == user_id).order_by(Todo.deadline.desc())
            results = session.execute(stmt).scalars().all()
            return [
                {"todo_id": t.todo_id, "task": t.task, "deadline": t.deadline.isoformat(), "status": t.status}
                for t in results
            ]

    # --- 用户偏好操作 (使用 Upsert 逻辑) ---
    def add_user_preference(self, user_id: int, category: str, preference_val: str):
        with self.SessionLocal() as session:
            # 查找是否存在
            stmt = select(Preference).where(Preference.user_id == user_id, Preference.category == category)
            pref = session.execute(stmt).scalar_one_or_none()

            if pref:
                pref.preference = preference_val
            else:
                pref = Preference(user_id=user_id, category=category, preference=preference_val)
                session.add(pref)

            session.commit()
            return pref.preference_id

    def get_user_preference_dict(self, user_id: int) -> Dict[str, str]:
        with self.SessionLocal() as session:
            stmt = select(Preference).where(Preference.user_id == user_id)
            prefs = session.execute(stmt).scalars().all()
            return {p.category: p.preference for p in prefs}

    def delete_user_preference(self, user_id: int, category: str):
        with self.SessionLocal() as session:
            stmt = select(Preference).where(Preference.user_id == user_id, Preference.category == category)
            pref = session.execute(stmt).scalar_one_or_none()
            if pref:
                session.delete(pref)
                session.commit()
                return True
            return False

    def get_history_list(self, user_id: int) -> List[Dict]:
        """获取侧边栏简易列表"""
        with self.SessionLocal() as session:
            stmt = select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc())
            results = session.execute(stmt).scalars().all()
            return [
                {
                    "session_id": s.session_id,
                    "title": s.query or "新对话",
                    "meeting": s.meeting or meeting,
                    "created_at": s.created_at.isoformat()
                } for s in results
            ]

    def get_chat_detail(self, session_id: str) -> List[Dict]:
        """获取某个对话的完整 ReAct 过程"""
        with (self.SessionLocal() as session):
            stmt = select(DialogStep).where(DialogStep.session_id == session_id).order_by(DialogStep.sequence_order.asc())
            results = session.execute(stmt).scalars().all()
            steps = [
                {"type": step.type, "text": step.content}
                for step in sorted(results, key=lambda r: r.sequence_order)
            ]
            return steps

    def create_chat_session(self, user_id: int, query: str, meeting: str) -> str:
        """创建一个新的会话并返回 ID"""
        new_id = str(uuid.uuid4())
        with self.SessionLocal() as session:
            chat_session = ChatSession(session_id=new_id, user_id=user_id, query=query, meeting=meeting,
                                       created_at=datetime.now(ZoneInfo("Asia/Shanghai")))
            session.add(chat_session)
            session.commit()
            return new_id

    def save_chat_steps(self, session_id: str, steps_data: List[Dict]):
        """
        批量保存 ReAct 步骤
        :param session_id: 所属会话 ID
        :param steps_data: 格式为 [{'type': '...', 'text': '...'}, ...] 的列表
        """
        with self.SessionLocal() as session:
            for idx, item in enumerate(steps_data):
                # 将前端/模型输出的 'text' 映射到数据库的 'content'
                step = DialogStep(
                    session_id=session_id,
                    sequence_order=idx,
                    type=item.get('type'),
                    content=item.get('text'),
                    created_at=datetime.now(ZoneInfo("Asia/Shanghai"))
                )
                session.add(step)

            try:
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"保存对话步骤失败: {e}")
                raise e

    def save_chat_step(self, session_id: str, step_data: Dict, sequence_order: int):
        """
        实时保存单个 ReAct 步骤
        :param session_id: 所属会话 ID
        :param step_data: 格式为 {'type': '...', 'text': '...'} 的字典
        :param sequence_order: 步骤序号
        """
        with self.SessionLocal() as session:
            step = DialogStep(
                session_id=session_id,
                sequence_order=sequence_order,
                type=step_data.get('type'),
                content=step_data.get('text'),
                created_at=datetime.now(ZoneInfo("Asia/Shanghai"))
            )
            session.add(step)

            try:
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"保存单个对话步骤失败: {e}")
                raise e

    def delete_chat_session(self, session_id: str, user_id: int) -> bool:
        """
        删除会话及其关联的所有步骤
        :param session_id: 会话唯一ID
        :param user_id: 用户ID（安全校验，确保用户只能删除自己的记录）
        """
        with self.SessionLocal() as session:
            # 1. 先查找该会话
            stmt = select(ChatSession).where(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            )
            chat_session = session.execute(stmt).scalar_one_or_none()

            if chat_session:
                # 2. 执行删除。由于我们在 models.py 中定义了 relationship 的 cascade，
                # 删除 chat_session 会自动删除关联的 chat_steps。
                session.delete(chat_session)
                session.commit()
                return True
            return False


db = MeetingDB()
