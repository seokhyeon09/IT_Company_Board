# -*- coding: utf-8 -*-
from __future__ import annotations
from enum import Enum

class TicketCategoryEnum(str, Enum):
    HW = "hw"
    SW = "sw"
    NETWORK = "network"
    ACCOUNT = "account"
    ETC = "etc"

class TicketPriorityEnum(str, Enum):
    LOW = "0"
    NORMAL = "1"
    HIGH = "2"
    URGENT = "3"

class TicketStatusEnum(str, Enum):
    SUBMITTED = "submitted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELED = "canceled"
