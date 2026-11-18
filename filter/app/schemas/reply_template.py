# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import TicketCategoryEnum

ALLOWED_TEMPLATE_CATEGORIES = {""} | {c.value for c in TicketCategoryEnum}


class ReplyTemplateUpsertDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=60, description="상용구 이름")
    category: str = Field(default="", description="분류 (''은 공통)")
    body: str = Field(..., min_length=1, max_length=3000, description="상용구 본문")

    @field_validator("name", "body", mode="before")
    @classmethod
    def strip_text(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in ALLOWED_TEMPLATE_CATEGORIES:
            raise ValueError("유효하지 않은 분류입니다.")
        return v


ReplyTemplateCreateDTO = ReplyTemplateUpsertDTO
ReplyTemplateUpdateDTO = ReplyTemplateUpsertDTO


class ReplyTemplateItemDTO(BaseModel):
    id: int
    name: str
    category: str = ""
    body: str
    is_mine: bool = False
    write_date: Optional[str] = None


class ReplyTemplateListResponseDTO(BaseModel):
    status: str = "success"
    data: List[ReplyTemplateItemDTO] = []


class ReplyTemplateResponseDTO(BaseModel):
    status: str = "success"
    data: ReplyTemplateItemDTO


class ReplyTemplateDeleteResponseDTO(BaseModel):
    status: str = "success"
