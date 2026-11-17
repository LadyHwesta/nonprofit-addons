# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class EventRunOfShowLine(models.Model):
    _name = "event.run_of_show.line"
    _inherit = ["event.run_of_show.line", "event.payout.mixin"]

    fee = fields.Monetary(
        string="Fee", currency_field="currency_id",
        help="What this act is paid for this performance. Billed once it's confirmed.")

    @api.depends("fee", "booking_state", "line_type", "performer_id.partner_id")
    def _compute_pay_state(self):
        return super()._compute_pay_state()

    def _payout_partner(self):
        self.ensure_one()
        return self.performer_id.partner_id

    def _payout_amount(self):
        self.ensure_one()
        return self.fee if self.line_type == "performance" else 0.0

    def _payout_is_due(self):
        self.ensure_one()
        return self.line_type == "performance" and self.booking_state == "confirmed"

    def _payout_description(self):
        self.ensure_one()
        when = fields.Datetime.context_timestamp(self, self.computed_start).strftime("%Y-%m-%d %H:%M") \
            if self.computed_start else ""
        return _("Performance: %(title)s, %(event)s %(when)s",
                 title=self.title or self.performer_id.name, event=self.event_id.name, when=when).strip()

    def _payout_product(self):
        return self.env.ref("event_performer_payout.product_performer_fee")
