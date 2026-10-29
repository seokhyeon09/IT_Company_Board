# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class OfficerItemDTO(BaseModel):
    id: int
    name: str
    login: str

class OfficerListResponseDTO(BaseModel):
    status: str = "success"
    data: List[OfficerItemDTO] = []

class RelatedTicketDTO(BaseModel):
    id: int
    ticket_number: str
    title: Optional[str] = None
    category: Optional[str] = None
    status: str
    is_faq: bool = False
    resolution_summary: Optional[str] = None
    create_date: Optional[str] = None

class EmailNotificationDTO(BaseModel):
    id: str
    ticket_id: int
    ticket_number: str
    ticket_title: Optional[str] = None
    event_type: str
    recipient_name: str
    recipient_email: str
    sender_email: str = "it-helpdesk-noreply@company.com"
    subject: str
    body_preview: str
    sent_at: Optional[str] = None
    status: str = "발송완료 (모의)"
    is_read: bool = False

class EmailNotificationListResponseDTO(BaseModel):
    status: str = "success"
    total: int = 0
    data: List[EmailNotificationDTO] = []

class NotificationReadDTO(BaseModel):
    notification_ids: List[str]

class NotificationReadResponseDTO(BaseModel):
    status: str = "success"
    data: Dict[str, Any] = {}

class OfficerStatItemDTO(BaseModel):
    officer_id: int
    officer_name: str
    officer_email: str
    total_assigned: int = 0
    in_progress_count: int = 0
    resolved_count: int = 0
    overdue_count: int = 0
    sla_compliance_rate: float = 100.0
    avg_rating: float = 0.0
    rating_count: int = 0
    avg_resolution_hours: float = 0.0
    resolved_measured_count: int = 0

class CategoryStatItemDTO(BaseModel):
    category: str
    label: str
    count: int = 0
    percentage: float = 0.0
    avg_resolution_hours: float = 0.0

class OfficerStatsDataDTO(BaseModel):
    officers: List[OfficerStatItemDTO] = []
    category_breakdown: List[CategoryStatItemDTO] = []
    unassigned_count: int = 0
    total_active_tickets: int = 0
    overall_avg_rating: float = 0.0
    overall_sla_rate: float = 100.0
    overall_avg_resolution_hours: float = 0.0

class OfficerStatsResponseDTO(BaseModel):
    status: str = "success"
    data: OfficerStatsDataDTO

class TicketStatsDataDTO(BaseModel):
    total: int = 0
    waiting: int = 0
    in_progress: int = 0
    pending: int = 0
    resolved: int = 0
    overdue: int = 0

class TicketStatsResponseDTO(BaseModel):
    status: str = "success"
    data: TicketStatsDataDTO
