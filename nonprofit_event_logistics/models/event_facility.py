# -*- coding: utf-8 -*-
from odoo import fields, models

FACILITY_TYPES = [
    ("restroom", "Restroom"),
    ("hand_wash", "Hand Wash Station"),
    ("first_aid", "First Aid"),
    ("water_station", "Water Station"),
    ("generator", "Generator"),
    ("dumpster", "Dumpster / Waste"),
    ("other", "Other"),
]


class EventFacility(models.Model):
    _name = "event.facility"
    _description = "Event Facility"
    _order = "facility_type, name"

    event_id = fields.Many2one(
        "event.event", string="Event", required=True, ondelete="cascade",
        index=True)
    name = fields.Char(required=True)
    facility_type = fields.Selection(
        FACILITY_TYPES, default="other", required=True)
    quantity = fields.Integer(default=1)
    crew_booking_id = fields.Many2one(
        "event.crew.booking", string="Provided / Serviced By",
        domain="[('event_id', '=', event_id)]")
    latitude = fields.Float(
        digits=(10, 7),
        help="Set by typing a coordinate, or by dropping a pin on the "
             "event's Vendor Map (Placement mode).")
    longitude = fields.Float(digits=(10, 7))
    servicing_schedule = fields.Text(
        help="e.g. \"Pumped daily at 6am\", \"Restocked every 4 hours\".")
