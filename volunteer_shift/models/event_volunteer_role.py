# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class EventVolunteerRole(models.Model):
    _inherit = "event.volunteer.role"

    use_shifts = fields.Boolean(
        string="Run as Shifts",
        help="Break this role into timed shifts instead of one whole-event "
             "sign-up. Volunteers then sign up per shift.")
    shift_ids = fields.One2many(
        "volunteer.shift", "role_id", string="Shifts", copy=True)
    shift_count = fields.Integer(compute="_compute_shift_count")

    @api.depends("shift_ids")
    def _compute_shift_count(self):
        for role in self:
            role.shift_count = len(role.shift_ids)

    @api.depends(
        "use_shifts", "shift_ids.filled_count", "shift_ids.confirmed_count",
        "shift_ids.seats_available", "shift_ids.slot_count")
    def _compute_counts(self):
        super()._compute_counts()
        for role in self.filtered("use_shifts"):
            total_slots = sum(role.shift_ids.mapped("slot_count"))
            role.filled_count = sum(role.shift_ids.mapped("filled_count"))
            role.confirmed_count = sum(role.shift_ids.mapped("confirmed_count"))
            role.seats_available = sum(role.shift_ids.mapped("seats_available"))
            if not role.filled_count:
                role.fill_state = "empty"
            elif role.filled_count < total_slots:
                role.fill_state = "partial"
            elif role.filled_count == total_slots:
                role.fill_state = "full"
            else:
                role.fill_state = "over"

    def action_view_shifts(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Shifts - %s", self.name),
            "res_model": "volunteer.shift",
            "view_mode": "list,calendar,form",
            "domain": [("role_id", "=", self.id)],
            "context": {"default_role_id": self.id},
        }
