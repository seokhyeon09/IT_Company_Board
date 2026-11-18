# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class SlaReportRangeDTO(BaseModel):
    date_from: str
    date_to: str
    unit: str
    category: Optional[str] = None


class SlaReportSummaryDTO(BaseModel):
    created: int = 0
    resolved: int = 0
    on_time: int = 0
    breached: int = 0
    on_time_rate: Optional[float] = None
    avg_resolution_hours: Optional[float] = None
    open_now: int = 0
    overdue_now: int = 0
    paused_now: int = 0
    avg_paused_hours: Optional[float] = None


class SlaReportSeriesItemDTO(BaseModel):
    period: str
    created: int = 0
    resolved: int = 0
    on_time: int = 0
    breached: int = 0
    on_time_rate: Optional[float] = None
    avg_resolution_hours: Optional[float] = None


class SlaReportCategoryItemDTO(BaseModel):
    category: str
    label: str
    created: int = 0
    resolved: int = 0
    on_time_rate: Optional[float] = None
    avg_resolution_hours: Optional[float] = None


class SlaReportPriorityItemDTO(BaseModel):
    priority: str
    label: str
    created: int = 0
    resolved: int = 0
    on_time_rate: Optional[float] = None
    avg_resolution_hours: Optional[float] = None


class SlaReportDataDTO(BaseModel):
    range: SlaReportRangeDTO
    summary: SlaReportSummaryDTO
    series: List[SlaReportSeriesItemDTO] = []
    by_category: List[SlaReportCategoryItemDTO] = []
    by_priority: List[SlaReportPriorityItemDTO] = []


class SlaReportResponseDTO(BaseModel):
    status: str = "success"
    data: SlaReportDataDTO
