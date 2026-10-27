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

    title: str = Field(..., min_length=1, max_length=150, description="문의 제목")
    category: TicketCategoryEnum = Field(..., description="문의 분류")
    content: str = Field(..., min_length=1, description="문의 상세 내용")
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





class ThreadItemDTO(BaseModel):
    id: int
    type: str  # "inquiry" | "resolution"
    round: int
    author_id: Optional[Any] = None
    author_name: str
    date: Optional[str] = None
    content: str

class ResolutionNoteDTO(BaseModel):
    id: int
    date: Optional[str] = None
    author_name: Optional[str] = "IT 담당자"
    content: str

class FollowUpInquiryDTO(BaseModel):
    id: int
    date: Optional[str] = None
    author_name: Optional[str] = "작성 직원"
    content: str

class TicketLogDTO(BaseModel):
    id: int
    date: Optional[str] = None
    author_name: Optional[str] = "시스템"
    body: str
    message_type: Optional[str] = "notification"

class TicketRestartDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: Optional[str] = Field(default=None, description="재문의 사유 및 추가 질문 내용")

class TicketUpdateResolutionDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resolution_note: str = Field(..., min_length=5, description="수정할 조치 내용")
    if_match_write_date: Optional[str] = Field(default=None, description="낙관적 락킹용 이전 write_date")

class TicketRateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rating: str = Field(..., pattern="^[1-5]$", description="만족도 별점 (1~5)")
    rating_comment: Optional[str] = Field(default=None, max_length=500, description="만족도 한줄평")
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
    timeline: List[ThreadItemDTO] = []
    resolutions: List[ResolutionNoteDTO] = []
    follow_ups: List[FollowUpInquiryDTO] = []
    logs: List[TicketLogDTO] = []

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

class TicketStatsDataDTO(BaseModel):
    total: int = 0
    waiting: int = 0
    in_progress: int = 0
    resolved: int = 0
    overdue: int = 0

class TicketStatsResponseDTO(BaseModel):
    status: str = "success"
    data: TicketStatsDataDTO
