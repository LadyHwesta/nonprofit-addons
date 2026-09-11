# -*- coding: utf-8 -*-
from odoo import fields, models


class EventVenueRow(models.Model):
    _name = "event.venue.row"
    _description = "Event Venue Row"
    _order = "sequence, id"

    event_id = fields.Many2one(
        "event.event", string="Event", required=True, ondelete="cascade",
        index=True)
    label = fields.Char(required=True, help="e.g. \"Row A\" or \"North Side\"")
    sequence = fields.Integer(
        default=10,
        help="Order along the row axis from the venue's calibrated origin - "
             "row 0 is the anchor row.")
    booth_ids = fields.One2many("event.booth", "row_id", string="Booths")
    booth_count = fields.Integer(compute="_compute_booth_count")

    _label_event_uniq = models.Constraint(
        "unique(event_id, label)",
        "A row with this label already exists for this event.")

    def _compute_booth_count(self):
        counts = dict(self.env["event.booth"]._read_group(
            [("row_id", "in", self.ids)], ["row_id"], ["__count"],
        )) if self.ids else {}
        counts = {row.id: count for row, count in counts.items()}
        for row in self:
            row.booth_count = counts.get(row.id, 0)
