from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, DateTime, Boolean, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
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
    content: Mapped[Optional[str]] = mapped_column(Text)
    duration: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="meetings")
    attendees: Mapped[List["Attendee"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")
    todos: Mapped[List["Todo"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")


class Attendee(Base):
    __tablename__ = "attendees"

    attendee_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.meeting_id", ondelete="CASCADE"))

    meeting: Mapped["Meeting"] = relationship(back_populates="attendees")


class Todo(Base):
    __tablename__ = "todos"

    user_id: Mapped[int] = mapped_column(nullable=False)
    todo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.meeting_id", ondelete="CASCADE"))
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="pending")

    meeting: Mapped["Meeting"] = relationship(back_populates="todos")


class Preference(Base):
    __tablename__ = "preference"

    preference_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    preference: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="preferences")

    __table_args__ = (UniqueConstraint("user_id", "category", name="uq_user_category"),)


class Conversation(Base):
    __tablename__ = "conversations"

    conv_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.meeting_id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' 或 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_used: Mapped[Optional[str]] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())

    # 反向关联
    meeting: Mapped["Meeting"] = relationship(back_populates="conversations")