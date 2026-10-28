# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Re-export definitions for 100% backward compatibility
from app.schemas.common import (
    TicketCategoryEnum,
    TicketPriorityEnum,
    TicketStatusEnum,
)
from app.schemas.attachment import (
    AttachmentDTO,
    AttachmentDetailDTO,
    AttachmentUploadDTO,
)
from app.schemas.workflow import (
    TicketResolveDTO,
    TicketUpdateResolutionDTO,
    TicketRestartDTO,
    TicketAssignDTO,
    TicketCloseDTO,
    TicketCancelDTO,
    TicketPendingDTO,
    TicketRateDTO,
)
from app.schemas.insight import (
    OfficerItemDTO,
    OfficerListResponseDTO,
    RelatedTicketDTO,
    EmailNotificationDTO,
    EmailNotificationListResponseDTO,
    NotificationReadDTO,
    NotificationReadResponseDTO,
    OfficerStatItemDTO,
    CategoryStatItemDTO,
    OfficerStatsDataDTO,
    OfficerStatsResponseDTO,
    TicketStatsDataDTO,
    TicketStatsResponseDTO,
)

__all__ = [
    "TicketCategoryEnum",
    "TicketPriorityEnum",
    "TicketStatusEnum",
    "AttachmentDTO",
    "AttachmentDetailDTO",
    "AttachmentUploadDTO",
    "TicketResolveDTO",
    "TicketUpdateResolutionDTO",
    "TicketRestartDTO",
    "TicketAssignDTO",
    "TicketCloseDTO",
    "TicketCancelDTO",
    "TicketPendingDTO",
    "TicketRateDTO",
    "OfficerItemDTO",
    "OfficerListResponseDTO",
    "RelatedTicketDTO",
    "EmailNotificationDTO",
    "EmailNotificationListResponseDTO",
    "NotificationReadDTO",
    "NotificationReadResponseDTO",
    "OfficerStatItemDTO",
    "CategoryStatItemDTO",
    "OfficerStatsDataDTO",
    "OfficerStatsResponseDTO",
    "TicketStatsDataDTO",
    "TicketStatsResponseDTO",
    "TicketCreateDTO",
    "TicketUpdateDTO",
    "ThreadItemDTO",
    "ResolutionNoteDTO",
    "FollowUpInquiryDTO",
    "TicketLogDTO",
    "TicketResponseDTO",
    "TicketDetailResponseDTO",
    "TicketListResponseDTO",
]

class TicketCreateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=150, description="문의 제목")
    category: TicketCategoryEnum = Field(..., description="문의 분류")
    content: str = Field(..., min_length=1, description="문의 상세 내용")
    priority: TicketPriorityEnum = Field(
        default=TicketPriorityEnum.NORMAL,
        description="우선순위 (0: 낮음, 1: 보통, 2: 높음, 3: 긴급)"
    )
    attachments: Optional[List[AttachmentUploadDTO]] = Field(default=None, description="초기 첨부파일 목록")

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

class TicketUpdateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Optional[str] = Field(default=None, min_length=1, max_length=150, description="문의 제목")
    category: Optional[TicketCategoryEnum] = Field(default=None, description="문의 분류")
    priority: Optional[TicketPriorityEnum] = Field(default=None, description="우선순위")
    content: Optional[str] = Field(default=None, min_length=1, description="문의 상세 내용")

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
    attachments: List[AttachmentDTO] = []
    pending_reason: Optional[str] = None
    related_tickets: List[RelatedTicketDTO] = []
    email_notifications: List[EmailNotificationDTO] = []

    @field_validator("content", "resolution_note", "author_name", "rating_comment", "pending_reason", mode="before")
    @classmethod
    def clean_false_to_none(cls, v: Any):
        if v is False or v == "False":
            return None
        return v

class TicketListResponseDTO(BaseModel):
    status: str = "success"
    total: int
    data: List[TicketResponseDTO]
