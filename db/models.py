from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, DateTime, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # 关系映射
    meetings: Mapped[List["Meeting"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    preferences: Mapped[List["Preference"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Meeting(Base):
    __tablename__ = "meetings"

    meeting_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration: Mapped[Optional[int]] = mapped_column(Integer)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="meetings")
    attendees: Mapped[List["Attendee"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")
    todos: Mapped[List["Todo"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")


class Attendee(Base):
    __tablename__ = "attendees"

    attendee_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.meeting_id", ondelete="CASCADE"))

    meeting: Mapped["Meeting"] = relationship(back_populates="attendees")


class Todo(Base):
    __tablename__ = "todos"

    # `todo_id` is the primary key; `user_id` should be a ForeignKey to users.user_id
    todo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.meeting_id", ondelete="CASCADE"), nullable=True)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="pending")

    meeting: Mapped["Meeting"] = relationship(back_populates="todos")


class Preference(Base):
    __tablename__ = "preferences"

    preference_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="preferences")

    __table_args__ = (UniqueConstraint("user_id", "category", name="uq_user_category"),)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    # 使用 Mapped 风格定义
    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)  # 通常存储 UUID 字符串
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    query: Mapped[Optional[str]] = mapped_column(String(255))
    meeting: Mapped[Optional[str]] = mapped_column(String())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # 关系映射：显式定义 back_populates 以获得更好的 IDE 支持
    steps: Mapped[List["DialogStep"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class DialogStep(Base):
    __tablename__ = "dialog_steps"

    step_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # Thought, Action, Observation, etc.
    content: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # 关系映射
    session: Mapped["ChatSession"] = relationship(back_populates="steps")