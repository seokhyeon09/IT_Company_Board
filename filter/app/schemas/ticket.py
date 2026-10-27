# -*- coding: utf-8 -*-
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class TicketCategoryEnum(str, Enum):
    HW = "hw"
    SW = "sw"
    NETWORK = "network"
    ACCOUNT = "account"
    ETC = "etc"

class TicketPriorityEnum(str, Enum):
    LOW = "0"
    NORMAL = "1"
    HIGH = "2"
    URGENT = "3"

class TicketStatusEnum(str, Enum):
    SUBMITTED = "submitted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELED = "canceled"

class TicketCreateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=2, max_length=150, description="문의 제목")
    category: TicketCategoryEnum = Field(..., description="문의 분류")
    content: str = Field(..., min_length=5, description="문의 상세 내용")
    priority: TicketPriorityEnum = Field(default=TicketPriorityEnum.NORMAL, description="우선순위 (0: 낮음, 1: 보통, 2: 높음, 3: 긴급)")

    @field_validator("priority", mode="before")
    @classmethod
    def coerce_priority(cls, v: Any) -> str:
        """Convert int or label into strict enum string ('0', '1', '2', '3')."""
        if v is None:
            return "1"
        s = str(v).strip().lower()
        mapping = {
            "0": "0", "low": "0", "낮음": "0",
            "1": "1", "normal": "1", "보통": "1",
            "2": "2", "high": "2", "높음": "2",
            "3": "3", "urgent": "3", "긴급": "3",
        }
        if s in mapping:
            return mapping[s]
        raise ValueError(f"Invalid priority '{v}'. Must be 0, 1, 2, or 3.")

class TicketResolveDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resolution_note: str = Field(..., min_length=5, description="조치 완료 내용")
    if_match_write_date: Optional[str] = Field(default=None, description="낙관적 락킹용 이전 write_date")

class TicketResponseDTO(BaseModel):
    id: int
    ticket_number: str
    title: Optional[str] = None
    category: Optional[str] = None
    status: str
    priority: str
    deadline: Optional[str] = None
    is_overdue: bool = False
    author_id: Any = None
    assignee_id: Any = None
    assignee_name: Optional[str] = "배정 대기"
    create_date: Optional[str] = None
    write_date: Optional[str] = None
    is_faq: bool = False
    rating: Optional[str] = None

class TicketDetailResponseDTO(TicketResponseDTO):
    content: Optional[Any] = None
    resolution_note: Optional[Any] = None
    author_name: Optional[Any] = None
    rating_comment: Optional[Any] = None

    @field_validator("content", "resolution_note", "author_name", "rating_comment", mode="before")
    @classmethod
    def clean_false_to_none(cls, v: Any):
        if v is False or v == "False":
            return None
        return v

class TicketListResponseDTO(BaseModel):
    status: str = "success"
    total: int
    data: List[TicketResponseDTO]
