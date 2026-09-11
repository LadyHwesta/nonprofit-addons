# -*- coding: utf-8 -*-
from odoo import fields, models


class EventStaffRole(models.Model):
    _name = "event.staff.role"
    _description = "Temporary Staff Role"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
