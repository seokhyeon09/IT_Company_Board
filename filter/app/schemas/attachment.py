# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class AttachmentDTO(BaseModel):
    id: int
    name: str
    mimetype: str = "application/octet-stream"
    file_size: Optional[int] = 0
    create_date: Optional[str] = None

class AttachmentDetailDTO(AttachmentDTO):
    datas: str

MAX_BASE64_SIZE = 7_000_000  # 5MB binary data encoded as Base64 (~6.99MB)

class AttachmentUploadDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = Field(..., min_length=1, max_length=200, description="파일명")
    datas: str = Field(..., min_length=1, max_length=MAX_BASE64_SIZE, description="Base64 인코딩 파일 데이터 (최대 5MB)")
    mimetype: Optional[str] = Field(default="application/octet-stream", description="MIME 타입")
    file_size: Optional[int] = Field(default=None, description="파일 크기")
