# -*- coding: utf-8 -*-
from odoo import fields, models

WEEKDAYS = [
    ("0", "Monday"), ("1", "Tuesday"), ("2", "Wednesday"), ("3", "Thursday"),
    ("4", "Friday"), ("5", "Saturday"), ("6", "Sunday"),
]


class VolunteerShiftTemplate(models.Model):
    _name = "volunteer.shift.template"
    _description = "Recurring Volunteer Shift"
    _order = "event_type_id, weekday, start_time"

    name = fields.Char(
        string="Role", required=True,
        help="The volunteer role these shifts fill. A role with this name is "
             "created on the event if it does not exist yet.")
    event_type_id = fields.Many2one(
        "event.type", string="Event Type", required=True, ondelete="cascade",
        index=True)
    weekday = fields.Selection(WEEKDAYS, required=True, default="5")
    start_time = fields.Float(
        string="Start", required=True, default=9.0,
        help="Hour of the day the shift starts (UTC), e.g. 9.5 = 09:30.")
    duration_hours = fields.Float(string="Length (h)", required=True, default=3.0)
    slot_count = fields.Integer(string="Slots", default=1)
    active = fields.Boolean(default=True)
