# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class TicketResolveDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    resolution_note: str = Field(..., min_length=5, description="조치 완료 내용")
    if_match_write_date: Optional[str] = Field(default=None, description="낙관적 락킹용 이전 write_date")
    expected_write_date: Optional[str] = Field(default=None, description="낙관적 락킹용 이전 write_date 호환 필드")

class TicketUpdateResolutionDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    resolution_note: str = Field(..., min_length=5, description="수정할 조치 내용")
    if_match_write_date: Optional[str] = Field(default=None, description="낙관적 락킹용 이전 write_date")
    expected_write_date: Optional[str] = Field(default=None, description="낙관적 락킹용 이전 write_date 호환 필드")

class TicketRestartDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    reason: Optional[str] = Field(default=None, description="재문의 사유 및 추가 질문 내용")
    content: Optional[str] = Field(default=None, description="추가 답변/질문 내용 호환 필드")

class TicketAssignDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    assignee_id: Optional[int] = Field(default=None, description="지정할 IT 담당자 ID (미입력 시 본인 배정)")
    officer_id: Optional[int] = Field(default=None, description="지정할 IT 담당자 ID 호환 필드")
    reason: Optional[str] = Field(default=None, description="담당자 변경 및 인계 사유")

class TicketCloseDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    note: Optional[str] = Field(default=None, description="직권 종결 사유")
    reason: Optional[str] = Field(default=None, description="직권 종결 사유 호환 필드")

class TicketCancelDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    reason: Optional[str] = Field(default=None, description="문의 취소 사유")

class TicketPendingDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    reason: Optional[str] = Field(default=None, description="답변 대기 요청 사유")

class TicketRateDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    rating: str = Field(..., description="만족도 별점 (1~5)")
    rating_comment: Optional[str] = Field(default=None, max_length=500, description="만족도 한줄평")
    comment: Optional[str] = Field(default=None, max_length=500, description="만족도 한줄평 호환 필드")
    if_match_write_date: Optional[str] = Field(default=None, description="낙관적 락킹용 이전 write_date")
    expected_write_date: Optional[str] = Field(default=None, description="낙관적 락킹용 이전 write_date 호환 필드")

    @field_validator("rating", mode="before")
    @classmethod
    def normalize_rating(cls, v):
        s = str(v).strip()
        if s not in {"1", "2", "3", "4", "5"}:
            raise ValueError("Rating must be between 1 and 5.")
        return s
