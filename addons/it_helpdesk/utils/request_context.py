# -*- coding: utf-8 -*-
from odoo.http import request

_mock_request = None

def set_mock_request(req):
    """Set mock request for testing environments."""
    global _mock_request
    _mock_request = req

def get_current_request():
    """Retrieve active Odoo request, checking mock request first."""
    if _mock_request is not None:
        return _mock_request
    try:
        from odoo.addons.it_helpdesk.controllers import main_api
        return getattr(main_api, 'request', request)
    except Exception:
        return request
