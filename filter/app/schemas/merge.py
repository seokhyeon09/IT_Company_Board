# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, field_validator

from app.core.messages import MSG_MERGE_REASON_TOO_LONG, MSG_MERGE_TARGET_REQUIRED

MAX_MERGE_REASON_LENGTH = 500


class TicketMergeRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_id: int
    reason: Optional[str] = None
    if_match_write_date: Optional[str] = None

    @field_validator("target_id", mode="before")
    @classmethod
    def validate_target_id(cls, v: Any) -> int:
        if isinstance(v, bool) or not isinstance(v, int) or v <= 0:
            raise ValueError(MSG_MERGE_TARGET_REQUIRED)
        return v

    @field_validator("reason", mode="before")
    @classmethod
    def validate_reason(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(MSG_MERGE_REASON_TOO_LONG)
        cleaned = v.strip()
        if len(cleaned) > MAX_MERGE_REASON_LENGTH:
            raise ValueError(MSG_MERGE_REASON_TOO_LONG)
        return cleaned or None


class TicketMergeResultDTO(BaseModel):
    id: int
    ticket_number: str
    status: str
    merged_into_id: Optional[int] = None
    merged_into_number: Optional[str] = None


class TicketMergeResponseDTO(BaseModel):
    status: str = "success"
    data: TicketMergeResultDTO


class MergeCandidateDTO(BaseModel):
    id: int
    ticket_number: str
    title: str
    status: str
    author_name: str
    create_date: Optional[str] = None
    score: float


class MergeCandidatesDataDTO(BaseModel):
    candidates: List[MergeCandidateDTO] = []


class MergeCandidatesResponseDTO(BaseModel):
    status: str = "success"
    data: MergeCandidatesDataDTO


class MergedTicketDTO(BaseModel):
    id: int
    ticket_number: str
    title: str
    status: str
    author_name: str
