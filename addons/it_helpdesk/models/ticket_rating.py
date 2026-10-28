# -*- coding: utf-8 -*-
from odoo import models, fields

class HelpDeskTicketRating(models.Model):
    _name = "it.helpdesk.ticket.rating"
    _description = "IT 문의 고객 만족도 평가 이력"
    _order = "round asc, id asc"

    ticket_id = fields.Many2one(
        "it.helpdesk.ticket",
        string="대상 티켓",
        required=True,
        ondelete="cascade",
        index=True,
    )
    round = fields.Integer(string="차수", default=1)
    rating = fields.Selection(
        [
            ("0", "미평가"),
            ("1", "1점 (매우 불만)"),
            ("2", "2점 (불만)"),
            ("3", "3점 (보통)"),
            ("4", "4점 (만족)"),
            ("5", "5점 (매우 만족)"),
        ],
        string="만족도",
        required=True,
    )
    rating_comment = fields.Text(string="만족도 한줄평")
    author_id = fields.Many2one(
        "res.users",
        string="평가 직원",
        default=lambda self: self.env.user,
        readonly=True,
    )
    create_date = fields.Datetime(string="평가일시", readonly=True)
