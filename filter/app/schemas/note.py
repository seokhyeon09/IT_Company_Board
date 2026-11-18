# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, field_validator

from app.core.messages import MSG_NOTE_EMPTY, MSG_NOTE_TOO_LONG

MAX_NOTE_LENGTH = 2000


class InternalNoteCreateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError(MSG_NOTE_EMPTY)
        cleaned = v.strip()
        if not cleaned:
            raise ValueError(MSG_NOTE_EMPTY)
        if len(cleaned) > MAX_NOTE_LENGTH:
            raise ValueError(MSG_NOTE_TOO_LONG)
        return cleaned


class InternalNoteDTO(BaseModel):
    id: int
    author_id: Optional[Any] = None
    author_name: Optional[str] = "시스템"
    date: Optional[str] = None
    content: str


class InternalNoteResponseDTO(BaseModel):
    status: str = "success"
    data: InternalNoteDTO
