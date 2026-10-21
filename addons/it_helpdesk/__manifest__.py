{
    "name": "사내 IT 헬프데스크",
    "version": "1.0",
    "summary": "사내 IT문제 해결 게시판",
    "author": "j",
    "category": "Services/Helpdesk",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/ticket_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
