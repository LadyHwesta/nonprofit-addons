# -*- coding: utf-8 -*-
from odoo import fields, models


class EventType(models.Model):
    _inherit = "event.type"

    volunteer_shift_template_ids = fields.One2many(
        "volunteer.shift.template", "event_type_id",
        string="Recurring Volunteer Shifts")
