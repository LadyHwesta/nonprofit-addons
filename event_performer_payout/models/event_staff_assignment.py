# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class EventStaffAssignment(models.Model):
    _name = "event.staff.assignment"
    _inherit = ["event.staff.assignment", "event.payout.mixin"]

    amount = fields.Monetary(
        string="Pay", currency_field="currency_id", compute="_compute_amount",
        help="Hours worked times the shift's hourly rate.")

    @api.depends("hours", "shift_id.hourly_rate")
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec._payout_amount()

    @api.depends("hours", "shift_id.hourly_rate", "state", "check_out")
    def _compute_pay_state(self):
        return super()._compute_pay_state()

    def _payout_partner(self):
        self.ensure_one()
        return self.partner_id

    def _payout_amount(self):
        self.ensure_one()
        return round((self.hours or 0.0) * (self.shift_id.hourly_rate or 0.0), 2)

    def _payout_is_due(self):
        self.ensure_one()
        return self.state == "confirmed" and bool(self.check_out)

    def _payout_description(self):
        self.ensure_one()
        return _("%(role)s, %(event)s: %(hours).2f h at %(rate).2f",
                 role=self.shift_id.role_id.name or self.shift_id.name or _("Staff"),
                 event=self.event_id.name, hours=self.hours, rate=self.shift_id.hourly_rate)

    def _payout_product(self):
        return self.env.ref("event_performer_payout.product_event_staff")
