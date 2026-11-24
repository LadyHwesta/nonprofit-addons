# -*- coding: utf-8 -*-
import logging

from markupsafe import Markup

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    donation_id = fields.Many2one('donation.donation', readonly=True, copy=False)

    # -- the donor -----------------------------------------------------------

    def _nonprofit_is_anonymous_partner(self, partner):
        public = self.env['website'].sudo().search([]).user_id.partner_id
        return partner in public

    def _nonprofit_donor_partner(self):
        """The contact for this gift: found by email, or created from what the
        donor typed in the form."""
        self.ensure_one()
        Partner = self.env['res.partner'].sudo()
        email = (self.partner_email or '').strip()
        partner = email and Partner.search(
            [('email', '=ilike', email), ('company_id', 'in', (False, self.company_id.id))],
            order='id', limit=1)
        return partner or Partner.create({
            'name': self.partner_name or email or _("Anonymous donor"),
            'email': email or False,
            'country_id': self.partner_country_id.id,
            'lang': self.partner_lang or False,
        })

    def _create_payment(self, **extra_create_values):
        """Book the payment on the donor, not on the website's anonymous visitor."""
        for tx in self.filtered(
                lambda t: t.is_donation and t._nonprofit_is_anonymous_partner(t.partner_id)):
            tx.partner_id = tx._nonprofit_donor_partner()
        return super()._create_payment(**extra_create_values)

    # -- the donation ---------------------------------------------------------

    def _nonprofit_gift_and_fees(self):
        """(gift, fees the donor covered). The fees come from "Donations: Donor
        Covers the Fees" when it's installed."""
        self.ensure_one()
        covered = self['donation_fee_covered'] if 'donation_fee_covered' in self._fields else 0.0
        gift = self['donation_gift_amount'] if covered else self.amount
        return gift, covered or 0.0

    def _nonprofit_record_donation(self):
        self.ensure_one()
        payment = self.payment_id
        method_line = payment.payment_method_line_id
        if not method_line.donation:
            # The Donations app only books through methods marked for donations.
            method_line.sudo().donation = True
        gift, fees = self._nonprofit_gift_and_fees()
        lines = [(0, 0, {'product_id': self.env.ref(
            'nonprofit_website_donation.product_online_donation').id,
            'quantity': 1, 'unit_price': gift})]
        if fees:
            lines.append((0, 0, {'product_id': self.env.ref(
                'nonprofit_website_donation.product_donor_covered_fees').id,
                'quantity': 1, 'unit_price': fees}))
        donation = self.env['donation.donation'].sudo().with_company(self.company_id).create({
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'donation_date': fields.Date.context_today(self, self.last_state_change),
            'payment_method_line_id': method_line.id,
            'payment_ref': self.reference,
            'check_total': self.amount,
            'payment_transaction_id': self.id,
            'line_ids': lines,
        })
        donation.validate()
        receivable = donation.move_id.line_ids.filtered(
            lambda line: line.display_type == 'payment_term').account_id
        to_match = (donation.move_id.line_ids | payment.move_id.line_ids).filtered(
            lambda line: line.account_id == receivable and not line.reconciled)
        to_match.reconcile()
        self.donation_id = donation
        return donation

    def _post_process(self):
        super()._post_process()
        for tx in self.filtered(lambda t: t.is_donation and t.state == 'done'
                                and t.payment_id and not t.donation_id):
            try:
                with self.env.cr.savepoint():
                    tx._nonprofit_record_donation()
            except Exception as exc:
                _logger.exception(
                    "nonprofit_website_donation: no donation created for %s", tx.reference)
                tx.payment_id.sudo().message_post(body=Markup("%s<br/>%s") % (
                    _("This online donation wasn't added to Donations automatically. Create it "
                      "by hand, or fix the cause and ask your administrator to retry:"),
                    str(exc)))
