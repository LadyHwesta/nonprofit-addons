# -*- coding: utf-8 -*-
from odoo import fields, models

from .event_permit import PERMIT_TYPES


class EventTypePermitTemplate(models.Model):
    _name = "event.type.permit.template"
    _description = "Permit Checklist Template"
    _order = "event_type_id, days_before_start desc"

    name = fields.Char(required=True)
    event_type_id = fields.Many2one(
        "event.type", string="Event Type", required=True, ondelete="cascade",
        index=True)
    permit_type = fields.Selection(PERMIT_TYPES, default="other", required=True)
    days_before_start = fields.Integer(
        string="Submit By (days before start)", default=30,
        help="How many days before the event this permit application "
             "should be submitted, by default.")
    active = fields.Boolean(default=True)


class EventType(models.Model):
    _inherit = "event.type"

    permit_template_ids = fields.One2many(
        "event.type.permit.template", "event_type_id",
        string="Permit Checklist")
