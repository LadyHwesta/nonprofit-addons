# -*- coding: utf-8 -*-
from odoo import fields, models


class EventParadeStagingArea(models.Model):
    _name = "event.parade.staging.area"
    _description = "Parade Staging Area"
    _inherit = ["mail.thread"]
    _order = "sequence, id"

    event_id = fields.Many2one(
        "event.event", string="Event", required=True, ondelete="cascade",
        index=True)
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    capacity = fields.Integer(
        help="Rough number of entries this area can comfortably hold. "
             "A soft guide, not an enforced limit - real parades flex.")
    arrival_instructions = fields.Text()
    entry_ids = fields.One2many(
        "event.parade.entry", "staging_area_id", string="Entries")
    entry_count = fields.Integer(compute="_compute_entry_count")

    def _compute_entry_count(self):
        counts = dict(self.env["event.parade.entry"]._read_group(
            [("staging_area_id", "in", self.ids)],
            ["staging_area_id"], ["__count"],
        )) if self.ids else {}
        counts = {area.id: count for area, count in counts.items()}
        for area in self:
            area.entry_count = counts.get(area.id, 0)
