# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EventStage(models.Model):
    """A named performance area for one event - Main Stage, Acoustic
    Tent, etc. Each stage runs its own independent, ordered schedule
    (event.run_of_show.line) starting from its own start_time.
    """
    _name = "event.stage"
    _description = "Event Stage"
    _order = "sequence, name"

    event_id = fields.Many2one(
        "event.event", string="Event", required=True, ondelete="cascade",
        index=True)
    name = fields.Char(required=True, help='e.g. "Main Stage", "Acoustic Tent".')
    sequence = fields.Integer(default=10)
    start_time = fields.Datetime(
        required=True,
        help="The schedule's own zero point - the first item's start "
             "time, unless it has its own hard-time override.")
    latitude = fields.Float(
        digits=(10, 7),
        help="Set by typing a coordinate, or by dropping a pin on the "
             "event's Vendor Map (Place Stages mode).")
    longitude = fields.Float(digits=(10, 7))
    notes = fields.Text(help="Power/sound specs, etc.")
    line_ids = fields.One2many(
        "event.run_of_show.line", "stage_id", string="Run of Show")
    line_count = fields.Integer(compute="_compute_line_count")

    @api.depends("line_ids")
    def _compute_line_count(self):
        for stage in self:
            stage.line_count = len(stage.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("start_time") and vals.get("event_id"):
                event = self.env["event.event"].browse(vals["event_id"])
                vals["start_time"] = event.date_begin
        return super().create(vals_list)
