# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError

PAY_STATES = [
    ("none", "Nothing owed"),
    ("to_bill", "To bill"),
    ("billed", "Billed"),
    ("paid", "Paid"),
]


class EventPayoutMixin(models.AbstractModel):
    """Something we owe a person for an event: a performance fee, or staff
    hours. Billed by draft vendor bills, one per person per event."""
    _name = "event.payout.mixin"
    _description = "Event Payout"

    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id)
    bill_line_id = fields.Many2one("account.move.line", copy=False, readonly=True)
    bill_id = fields.Many2one(related="bill_line_id.move_id", string="Bill")
    pay_state = fields.Selection(
        PAY_STATES, string="Payment", compute="_compute_pay_state")

    # Subclasses: _payout_partner(), _payout_amount(), _payout_is_due(),
    # _payout_description(), _payout_product(), event_id.

    @api.depends("bill_line_id.move_id.payment_state", "bill_line_id.move_id.state")
    def _compute_pay_state(self):
        for rec in self:
            bill = rec.bill_line_id.move_id
            if bill and bill.state != "cancel":
                rec.pay_state = "paid" if bill.payment_state in ("paid", "in_payment") else "billed"
            elif rec._payout_is_due() and rec._payout_amount() > 0:
                rec.pay_state = "to_bill"
            else:
                rec.pay_state = "none"

    def _payout_ready(self):
        """What can be billed now: due, with an amount and a person, and not
        billed yet (a cancelled bill can be billed again)."""
        return self.filtered(
            lambda r: r._payout_is_due() and r._payout_amount() > 0 and r._payout_partner()
            and (not r.bill_line_id or r.bill_line_id.move_id.state == "cancel"))

    def action_create_bills(self):
        """Draft vendor bills for everything ready, one per person per
        event, a line for each performance or shift."""
        ready = self._payout_ready()
        if not ready:
            raise UserError(_("Nothing to bill: only confirmed performances and staff with a "
                              "fee or hours, a contact, and no bill yet are billed."))
        groups = defaultdict(lambda: self.browse())
        for rec in ready:
            groups[(rec._payout_partner(), rec.event_id)] |= rec
        bills = self.env["account.move"]
        for (partner, event), recs in groups.items():
            company = event.company_id or self.env.company
            bill = self.env["account.move"].with_company(company).create({
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_origin": event.name,
                "ref": event.name,
                "invoice_line_ids": [(0, 0, {
                    "product_id": rec._payout_product().id,
                    "name": rec._payout_description(),
                    "quantity": 1,
                    "price_unit": rec._payout_amount(),
                    "tax_ids": [(5, 0, 0)],
                }) for rec in recs],
            })
            for rec, line in zip(recs, bill.invoice_line_ids):
                rec.bill_line_id = line
            partner._payout_mark_1099_nec()
            bills |= bill
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "name": _("Bills"),
            "view_mode": "list,form",
            "domain": [("id", "in", bills.ids)],
            "context": {"default_move_type": "in_invoice"},
        }


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _payout_mark_1099_nec(self):
        """With the 1099 module installed, someone paid for performing or
        working an event is a 1099-NEC contractor: marked, with a note, so the
        yearly summary totals them. A contact already given a 1099 type is
        left alone (untick it for a corporation, which gets no 1099)."""
        if "is_1099" not in self._fields:
            return
        nec = self.env.ref("l10n_us_form_1099.1099_type_nec", raise_if_not_found=False)
        for partner in self.filtered(lambda p: not p.is_1099 and not p.type_1099_id):
            partner.sudo().write({"is_1099": True, "type_1099_id": nec.id if nec else False})
            partner.message_post(body=_(
                "Marked as a 1099-NEC contractor: billed for an event. Untick \"Is a 1099?\" "
                "if they're a corporation."))
