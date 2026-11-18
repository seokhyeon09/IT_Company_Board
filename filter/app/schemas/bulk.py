# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.core.messages import (
    MSG_BULK_EMPTY_TICKETS,
    MSG_BULK_INVALID_ACTION,
    MSG_BULK_INVALID_ID,
    MSG_BULK_MAX_TICKETS,
    MSG_BULK_NOTE_TOO_LONG,
    MSG_BULK_OFFICER_REQUIRED,
    MSG_BULK_REASON_TOO_LONG,
)

VALID_BULK_ACTIONS = ("assign", "assign_auto", "start_progress", "close")
MAX_BULK_TICKETS = 50


class TicketBulkRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_ids: List[int]
    action: Literal["assign", "assign_auto", "start_progress", "close"]
    officer_id: Optional[int] = None
    reason: Optional[str] = None
    note: Optional[str] = None

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, v: Any) -> str:
        if not isinstance(v, str) or v not in VALID_BULK_ACTIONS:
            raise ValueError(MSG_BULK_INVALID_ACTION)
        return v

    @field_validator("ticket_ids", mode="before")
    @classmethod
    def validate_ticket_ids(cls, v: Any) -> List[int]:
        if not isinstance(v, list) or len(v) == 0:
            raise ValueError(MSG_BULK_EMPTY_TICKETS)
        deduped: List[int] = []
        seen = set()
        for item in v:
            if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
                raise ValueError(MSG_BULK_INVALID_ID)
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        if len(deduped) > MAX_BULK_TICKETS:
            raise ValueError(MSG_BULK_MAX_TICKETS)
        return deduped

    @field_validator("officer_id", mode="before")
    @classmethod
    def validate_officer_id(cls, v: Any) -> Optional[int]:
        if v is None:
            return None
        if isinstance(v, bool) or not isinstance(v, int) or v <= 0:
            raise ValueError(MSG_BULK_OFFICER_REQUIRED)
        return v

    @field_validator("reason", mode="before")
    @classmethod
    def validate_reason(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(MSG_BULK_REASON_TOO_LONG)
        cleaned = v.strip()
        if len(cleaned) > 500:
            raise ValueError(MSG_BULK_REASON_TOO_LONG)
        return cleaned or None

    @field_validator("note", mode="before")
    @classmethod
    def validate_note(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(MSG_BULK_NOTE_TOO_LONG)
        cleaned = v.strip()
        if len(cleaned) > 2000:
            raise ValueError(MSG_BULK_NOTE_TOO_LONG)
        return cleaned or None

    @model_validator(mode="after")
    def validate_assign_requires_officer(self) -> "TicketBulkRequestDTO":
        if self.action == "assign" and not self.officer_id:
            raise ValueError(MSG_BULK_OFFICER_REQUIRED)
        return self


class BulkTicketItemResultDTO(BaseModel):
    id: int
    ticket_number: Optional[str] = None
    ok: bool
    message: str


class BulkTicketResultDataDTO(BaseModel):
    action: str
    total: int
    success_count: int
    fail_count: int
    results: List[BulkTicketItemResultDTO] = []


class BulkTicketResponseDTO(BaseModel):
    status: str = "success"
    data: BulkTicketResultDataDTO
