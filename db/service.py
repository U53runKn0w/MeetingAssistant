import string
from datetime import datetime
from typing import List, Optional
from hashlib import md5

from action.models import MeetingRecord, AgendaConclusion, FollowUp
from db.manager import MeetingDB
from db.models import Meeting, Attendee, Todo, User


def convert_todos(todo_list: list) -> List[Todo]:
    """内部逻辑：处理日期转换并返回待办对象列表"""
    orm_todos = []
    for t in todo_list:
        # 兼容性处理：如果 deadline 是字符串且包含特殊字符
        deadline_dt = None
        if hasattr(t, 'deadline') and t.deadline and t.deadline != "待确认":
            try:
                # 尝试转换，若失败则保持 None
                deadline_dt = datetime.fromisoformat(t.deadline)
            except (ValueError, TypeError):
                deadline_dt = None

        orm_todos.append(Todo(
            owner=t.owner,
            task=t.task,
            deadline=deadline_dt,
            status="pending"
        ))
    return orm_todos


def update_todos(todo_id: int, owner: Optional[string], task: Optional[string], deadline: Optional[datetime], status: Optional[string] ) -> None:
    allowed_status = ["pending", "in_progress", "completed", "cancelled"]
    if status and status not in allowed_status:
        raise ValueError(f"Invalid status: {status}. Allowed values are: {allowed_status}")
    db = MeetingDB()
    todo_dict = {"todo_id": todo_id}
    if owner is not None:
        todo_dict["owner"] = owner
    if task is not None:
        todo_dict["task"] = task
    if deadline is not None:
        todo_dict["deadline"] = deadline
    if status is not None:
        todo_dict["status"] = status

    db.update_todos([todo_dict])


class MeetingService:
    def __init__(self, db: MeetingDB):
        self.db = db

    def user_login(self, username: str, password: str) -> int:
        """
        用户登录验证，成功返回用户ID，失败抛出异常
        """
        with self.db.SessionLocal() as session:
            user = session.query(User).filter(User.username == username).first()
            if not user or user.password_hash != md5(password).hexdigest():
                raise ValueError("用户名或密码错误")
            return user["user_id"]

    def process_meeting_record(self, record: MeetingRecord) -> int:
        """
        处理并保存完整的会议记录
        利用 ORM 的关联关系实现原子化存储
        """
        with self.db.SessionLocal() as session:
            try:
                # 1. 解析基础数据
                try:
                    start_time = datetime.fromisoformat(record.basic_info.time)
                    duration = int(record.basic_info.duration) if record.basic_info.duration else None
                except (ValueError, TypeError):
                    raise ValueError("无效的时间格式或会议时长")

                # 2. 构建 Meeting ORM 对象及其子对象树
                new_meeting = Meeting(
                    user_id=record.user_id,
                    subject=record.basic_info.subject,
                    start_time=start_time,
                    duration=duration
                )

                # 3. 添加参会人
                if record.basic_info.attendees:
                    new_meeting.attendees = [
                        Attendee(name=name) for name in record.basic_info.attendees
                    ]

                # 4. 添加议程结论
                new_meeting.agendas = [
                    AgendaConclusion(agenda=a.agenda, conclusion=a.conclusion)
                    for a in record.agendas
                ]

                # 5. 添加待办事项
                new_meeting.todos = convert_todos(record.todos)

                # 6. 添加待跟进事项
                new_meeting.follow_ups = [
                    FollowUp(topic=f.topic, reason=f.reason)
                    for f in record.follow_ups
                ]

                # 7. 一次性提交到数据库 (原子事务)
                session.add(new_meeting)
                session.commit()

                # 刷新以获取数据库生成的 meeting_id
                session.refresh(new_meeting)
                return new_meeting.meeting_id

            except Exception as e:
                session.rollback()
                print(f"Error saving meeting: {e}")
                raise
