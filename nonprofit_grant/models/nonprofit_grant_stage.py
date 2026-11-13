# -*- coding: utf-8 -*-
from odoo import fields, models


class NonprofitGrantStage(models.Model):
    _name = "nonprofit.grant.stage"
    _description = "Grant Stage"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string="Folded in Kanban")
    is_awarded = fields.Boolean(
        string="Awarded",
        help="Grants here have been awarded: they need an award amount and get a fund.")
    is_declined = fields.Boolean(string="Declined")
    is_closed = fields.Boolean(
        string="Closed", help="The grant is finished: spent, reported and closed out.")
