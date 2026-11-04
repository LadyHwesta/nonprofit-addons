# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    stage_ids = fields.One2many(
        "event.entertainment.stage", "event_id", string="Stages")
    stage_count = fields.Integer(compute="_compute_stage_count")

    @api.depends("stage_ids")
    def _compute_stage_count(self):
        for event in self:
            event.stage_count = len(event.stage_ids)

    def action_view_entertainment_stages(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "nonprofit_event_entertainment.action_event_stage")
        action["domain"] = [("event_id", "=", self.id)]
        action["context"] = {"default_event_id": self.id}
        return action
