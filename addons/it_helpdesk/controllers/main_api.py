# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

from ..utils import (
    GATEWAY_SHARED_SECRET,
    ConcurrencyError,
    parse_iso_utc,
    _safe_html_text,
    _clean_html,
    _extract_thread_content,
    _format_datetime_utc,
    verify_gateway_request,
)
from .auth_api import AuthAPIController
from .ticket_query_api import TicketQueryAPIController, LIST_FIELDS
from .ticket_workflow_api import TicketWorkflowAPIController
from .attachment_api import AttachmentAPIController

_logger = logging.getLogger(__name__)

class ITHelpdeskAPIController(
    AuthAPIController,
    TicketQueryAPIController,
    TicketWorkflowAPIController,
    AttachmentAPIController,
):
    """Integrated Modular Controller for IT Helpdesk Headless API.
    
    Combines domain-specific sub-controllers via multi-inheritance mixin pattern:
    - AuthAPIController: /api/v1/auth/login
    - TicketQueryAPIController: /api/v1/tickets/list, /stats, /detail, /create, /update
    - TicketWorkflowAPIController: /api/v1/tickets/resolve, /rate, /toggle-faq, /restart,
                                   /update-resolution, /assign, /start-progress, /pending,
                                   /close, /cancel
    - AttachmentAPIController: /api/v1/tickets/upload-attachment, /get-attachment
    """
    pass
