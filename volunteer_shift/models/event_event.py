# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    volunteer_shift_count = fields.Integer(
        compute="_compute_volunteer_shift_count", string="Volunteer Shifts")

    @api.depends("volunteer_role_ids.shift_ids")
    def _compute_volunteer_shift_count(self):
        for event in self:
            event.volunteer_shift_count = len(
                event.volunteer_role_ids.shift_ids)

    def action_generate_volunteer_shifts(self):
        self.ensure_one()
        created = self.env["volunteer.shift"]._generate_shifts_for_event(self)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success" if created else "warning",
                "message": _("%s shift(s) created.", len(created)) if created
                else _("No new shifts - the templates produced nothing new "
                       "in this event's date range."),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    def action_open_volunteer_shifts(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Volunteer Shifts"),
            "res_model": "volunteer.shift",
            "view_mode": "calendar,list,form",
            "domain": [("event_id", "=", self.id)],
            "context": {"default_event_id": self.id},
        }
