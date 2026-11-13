# -*- coding: utf-8 -*-
from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError

GRANTS_REVENUE_CODE = "4020"  # "Government and Foundation Grants" in nonprofit_base's chart


class NonprofitGrantPayment(models.Model):
    """One installment the funder is expected to pay."""
    _name = "nonprofit.grant.payment"
    _description = "Grant Payment"
    _order = "expected_date, id"

    grant_id = fields.Many2one("nonprofit.grant", required=True, ondelete="cascade", index=True)
    name = fields.Char(required=True, default=lambda self: _("Payment"),
                       help='e.g. "First installment".')
    expected_date = fields.Date(required=True)
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(related="grant_id.currency_id")
    company_id = fields.Many2one(related="grant_id.company_id", store=True)
    move_id = fields.Many2one("account.move", string="Invoice", copy=False, readonly=True)
    state = fields.Selection(
        [("expected", "Expected"), ("invoiced", "Invoiced"), ("paid", "Received")],
        compute="_compute_state", store=True)
    amount_paid = fields.Monetary(string="Received", compute="_compute_state", store=True)

    @api.depends("move_id.state", "move_id.payment_state", "move_id.amount_residual", "amount")
    def _compute_state(self):
        for payment in self:
            move = payment.move_id
            if not move or move.state == "cancel":
                payment.state, payment.amount_paid = "expected", 0.0
            elif move.state == "posted" and move.payment_state in ("paid", "in_payment"):
                payment.state, payment.amount_paid = "paid", move.amount_total
            else:
                payment.state = "invoiced"
                payment.amount_paid = (move.amount_total - move.amount_residual) if move.state == "posted" else 0.0

    def _revenue_account(self):
        company = self.grant_id.company_id
        Account = self.env["account.account"].with_company(company)
        account = Account.search([("code", "=", GRANTS_REVENUE_CODE), ("company_ids", "in", company.id)], limit=1)
        return account or Account.search(
            [("account_type", "=", "income"), ("company_ids", "in", company.id)], limit=1)

    def action_create_invoice(self):
        """A draft invoice to the funder for this installment, on the grants
        revenue account and the grant's fund (and program)."""
        for payment in self:
            grant = payment.grant_id
            if payment.move_id and payment.move_id.state != "cancel":
                raise UserError(_("%(payment)s already has an invoice.", payment=payment.name))
            if not grant.fund_id:
                raise UserError(_("Award the grant first: it needs its fund."))
            account = payment._revenue_account()
            if not account:
                raise UserError(_("No income account to put grant revenue on."))
            distribution = {str(grant.fund_id.id): 100.0}
            if grant.program_id:
                distribution[str(grant.program_id.id)] = 100.0
            payment.move_id = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": grant.funder_id.id,
                "company_id": grant.company_id.id,
                "invoice_date": payment.expected_date,
                "invoice_origin": grant.display_name,
                "invoice_line_ids": [Command.create({
                    "name": _("%(grant)s: %(payment)s", grant=grant.name, payment=payment.name),
                    "quantity": 1,
                    "price_unit": payment.amount,
                    "account_id": account.id,
                    "tax_ids": [Command.clear()],
                    "analytic_distribution": distribution,
                })],
            })
        return self[:1].action_open_invoice() if len(self) == 1 else True

    def action_open_invoice(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": self.move_id.id,
            "view_mode": "form",
        }
