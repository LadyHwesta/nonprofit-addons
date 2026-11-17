# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class EventEvent(models.Model):
    _inherit = "event.event"

    payout_to_bill = fields.Monetary(
        string="Owed, Not Billed", compute="_compute_payouts", currency_field="payout_currency_id")
    payout_billed = fields.Monetary(
        string="Billed", compute="_compute_payouts", currency_field="payout_currency_id")
    payout_currency_id = fields.Many2one(
        "res.currency", compute="_compute_payouts")

    def _payout_records(self):
        self.ensure_one()
        lines = self.env["event.run_of_show.line"].search([("event_id", "=", self.id)])
        staff = self.env["event.staff.assignment"].search([("event_id", "=", self.id)])
        return lines, staff

    def _compute_payouts(self):
        for event in self:
            lines, staff = event._payout_records()
            records = list(lines) + list(staff)
            event.payout_currency_id = (event.company_id or self.env.company).currency_id
            event.payout_to_bill = sum(r._payout_amount() for r in records if r.pay_state == "to_bill")
            event.payout_billed = sum(r._payout_amount() for r in records if r.pay_state in ("billed", "paid"))

    def action_bill_performers_and_staff(self):
        self.ensure_one()
        lines, staff = self._payout_records()
        ready_lines, ready_staff = lines._payout_ready(), staff._payout_ready()
        if not (ready_lines or ready_staff):
            raise UserError(_("Nothing to bill for %(event)s yet: performances are billed once "
                              "confirmed with a fee, staff once checked out.", event=self.name))
        bills = self.env["account.move"]
        for recs in (ready_lines, ready_staff):
            if recs:
                bills |= self.env["account.move"].search(recs.action_create_bills()["domain"])
        return {
            "type": "ir.actions.act_window", "res_model": "account.move", "name": _("Bills"),
            "view_mode": "list,form", "domain": [("id", "in", bills.ids)],
            "context": {"default_move_type": "in_invoice"},
        }
