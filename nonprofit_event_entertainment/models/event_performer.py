# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EventPerformer(models.Model):
    """A reusable act/performer - contact and rider details carry
    across every event this act plays, rather than being re-typed
    into each event's own run of show.
    """
    _name = "event.performer"
    _description = "Event Performer"
    _order = "name"

    name = fields.Char(required=True, help="Act or stage name.")
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one(
        "res.partner", string="Contact",
        help="The performer's own contact record, if any - phone/email "
             "are read from here rather than duplicated.")
    genre = fields.Char()
    default_set_length = fields.Integer(
        string="Default Set Length (minutes)", default=30,
        help="Prefills a new booking's own duration - still freely "
             "overridable per event, since the same act might play a "
             "shorter or longer set at different events.")
    technical_rider = fields.Text(
        string="Technical Rider",
        help="Equipment/stage requirements - power, mics, monitors, "
             "backline, etc.")
    notes = fields.Text()
    booking_ids = fields.One2many(
        "event.run_of_show.line", "performer_id", string="Bookings")
    booking_count = fields.Integer(compute="_compute_booking_count")

    @api.depends("booking_ids")
    def _compute_booking_count(self):
        for performer in self:
            performer.booking_count = len(performer.booking_ids)
