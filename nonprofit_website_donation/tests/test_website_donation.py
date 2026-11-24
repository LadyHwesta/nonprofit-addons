# -*- coding: utf-8 -*-
from odoo.tests import tagged

from odoo.addons.account_payment.tests.common import AccountPaymentCommon


@tagged('post_install', '-at_install')
class TestWebsiteDonationRecorded(AccountPaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.public_partner = cls.env['website'].sudo().search([], limit=1).user_id.partner_id

    _count = 0

    def _paid_donation(self, amount=25.0, email='ada@example.com', **values):
        TestWebsiteDonationRecorded._count += 1
        tx = self._create_transaction(
            flow='direct', amount=amount, state='done', partner_id=self.public_partner.id,
            reference=f'donation-test-{self._count}', **values)
        # As website_payment's donation route does: the donor's details are set
        # after the transaction is created (creating it fills them from the
        # anonymous visitor).
        tx.write({'is_donation': True, 'partner_name': 'Ada Donor', 'partner_email': email,
                  'partner_country_id': self.env.ref('base.us').id})
        tx._post_process()
        return tx

    def test_an_online_gift_becomes_a_validated_donation(self):
        tx = self._paid_donation()
        donation = tx.donation_id
        self.assertTrue(donation, "no donation created")
        self.assertEqual(donation.state, 'done')
        self.assertEqual(donation.payment_transaction_id, tx)
        self.assertAlmostEqual(donation.amount_total, 25.0)
        self.assertEqual(donation.partner_id.email, 'ada@example.com')
        self.assertNotEqual(donation.partner_id, self.public_partner)

    def test_the_donor_gets_their_receipt(self):
        tx = self._paid_donation()
        self.assertTrue(tx.donation_id.tax_receipt_id)
        self.assertAlmostEqual(tx.donation_id.tax_receipt_id.amount, 25.0)

    def test_the_payment_is_booked_on_the_donor_and_matched(self):
        tx = self._paid_donation()
        self.assertEqual(tx.payment_id.partner_id, tx.donation_id.partner_id)
        receivable = tx.donation_id.move_id.line_ids.filtered(
            lambda line: line.display_type == 'payment_term')
        self.assertTrue(receivable.reconciled, "donation not matched to the payment")
        payment_receivable = tx.payment_id.move_id.line_ids.filtered(
            lambda line: line.account_id == receivable.account_id)
        self.assertTrue(payment_receivable.reconciled)

    def test_a_returning_donor_is_matched_by_email(self):
        first = self._paid_donation(email='Repeat@Example.com')
        second = self._paid_donation(email='repeat@example.com')
        self.assertEqual(first.donation_id.partner_id, second.donation_id.partner_id)

    def test_covered_fees_are_their_own_line_on_the_receipt(self):
        tx = self.env['payment.transaction']
        if 'donation_fee_covered' not in tx._fields:
            self.skipTest("Donations: Donor Covers the Fees isn't installed")
        tx = self._paid_donation(
            amount=26.06, donation_gift_amount=25.0, donation_fee_covered=1.06)
        lines = tx.donation_id.line_ids.sorted('amount')
        self.assertEqual(lines.mapped('amount'), [1.06, 25.0])
        self.assertEqual(lines[0].product_id, self.env.ref(
            'nonprofit_website_donation.product_donor_covered_fees'))
        self.assertAlmostEqual(tx.donation_id.tax_receipt_id.amount, 26.06)

    def test_an_ordinary_payment_is_left_alone(self):
        tx = self._create_transaction(flow='direct', state='done')
        tx._post_process()
        self.assertFalse(tx.donation_id)
