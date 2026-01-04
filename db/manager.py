from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional
from datetime import datetime

from db.models import Base, User, Meeting, Attendee, Todo, Preference


class MeetingDB:
    def __init__(self, db_url: str = "sqlite:///db/db.sqlite"):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

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


db = MeetingDB()
