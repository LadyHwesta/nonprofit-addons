# -*- coding: utf-8 -*-
from odoo import fields, models


class DonationDonation(models.Model):
    _inherit = 'donation.donation'

    payment_transaction_id = fields.Many2one(
        'payment.transaction', string="Online Payment", readonly=True, copy=False, index=True,
        help="The website donation this was created from.")

    def _prepare_counterpart_move_line(self, total_company_cur, total_currency):
        """An online donation was already paid: the website payment debited the
        bank side and credited the donor's receivable. So the donation's entry
        debits that receivable instead, and the two are matched: the money is
        booked once, as a donation."""
        if not self.payment_transaction_id:
            return super()._prepare_counterpart_move_line(total_company_cur, total_currency)
        self.ensure_one()
        receivable = self.commercial_partner_id.with_company(
            self.company_id).property_account_receivable_id
        positive = self.company_currency_id.compare_amounts(total_company_cur, 0) > 0
        return {
            'debit': total_company_cur if positive else 0.0,
            'credit': 0.0 if positive else -total_company_cur,
            'account_id': receivable.id,
            'partner_id': self.commercial_partner_id.id,
            'currency_id': self.currency_id.id,
            'amount_currency': total_currency,
            'name': self.number,
            'display_type': 'payment_term',
        }
