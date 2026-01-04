from typing import List
from pydantic import BaseModel, Field


class BasicInfo(BaseModel):
    attendees: List[str] = Field(description="参会人姓名列表")
    time: str = Field(description="会议日期和时间")
    subject: str = Field(description="会议主题")
    duration: str = Field(description="会议持续时长")


class AgendaConclusion(BaseModel):
    agenda: str = Field(description="会议议题/讨论点")
    conclusion: str = Field(description="针对该议题达成的结论或共识")


class TodoItem(BaseModel):
    owner: str = Field(description="负责人姓名")
    task: str = Field(description="待办事项具体内容")
    # 方案 A：仍使用 str，但明确格式要求
    deadline: str = Field(
        description="截止时间，格式为 YYYY-MM-DD HH:MM。若无具体时间则写日期。若完全未提及则标注'待确认'")

    # 方案 B（更严格）：使用 Optional[datetime]
    # deadline: Optional[datetime] = Field(description="截止时间")


class FollowUp(BaseModel):
    topic: str = Field(description="需要跟进的争议点或未决事项")
    reason: str = Field(description="需要跟进的原因或待核实的信息")


class Preference(BaseModel):
    category: str = Field(description="偏好类别")
    preference: str = Field(description="具体偏好值")


class MeetingRecord(BaseModel):
    basic_info: BasicInfo
    agendas: List[AgendaConclusion]
    todos: List[TodoItem]
    follow_ups: List[FollowUp]
    raw_text: str  # 原始会议记录
    user_id: int  # 关联的用户ID
