# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from datetime import date
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.messages import MSG_ABSENT_UNTIL_INVALID

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class OfficerAbsenceDTO(BaseModel):
    is_absent: bool = False
    absent_until: Optional[str] = None


class OfficerAbsenceResponseDTO(BaseModel):
    status: str = "success"
    data: OfficerAbsenceDTO


class OfficerAbsenceUpdateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_absent: bool
    absent_until: Optional[str] = Field(default=None, description="부재 종료일 (YYYY-MM-DD)")

    @field_validator("absent_until", mode="before")
    @classmethod
    def validate_absent_until(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(MSG_ABSENT_UNTIL_INVALID)
        cleaned = v.strip()
        if not cleaned:
            return None
        if not _DATE_RE.match(cleaned):
            raise ValueError(MSG_ABSENT_UNTIL_INVALID)
        try:
            date.fromisoformat(cleaned)
        except ValueError as exc:
            raise ValueError(MSG_ABSENT_UNTIL_INVALID) from exc
        return cleaned
