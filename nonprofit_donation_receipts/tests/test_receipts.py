# -*- coding: utf-8 -*-
import time

from odoo import Command
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDonationReceipts(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")
        cls.company.vat = "12-3456789"
        journal = cls.env["account.journal"].create(
            {"type": "bank", "name": "Receipts test bank", "company_id": cls.company.id})
        account = cls.env["account.account"].create({
            "name": "Receipts test payments", "code": "TESTRCPT",
            "company_ids": [Command.set([cls.company.id])],
            "account_type": "asset_current", "reconcile": True})
        cls.method = cls.env["account.payment.method.line"].create({
            "name": "Receipts test method", "company_id": cls.company.id,
            "payment_account_id": account.id, "donation": True, "journal_id": journal.id,
            "payment_method_id": cls.env.ref("account.account_payment_method_manual_in").id})
        cls.donor = cls.env["res.partner"].create({"name": "Dana Donor", "city": "Santa Rosa"})
        # Our own product: the module's sample ones only exist with demo data.
        cls.gift = cls.env["product.product"].create({
            "name": "Gift", "type": "service", "donation_type": "donation", "tax_receipt_ok": True,
            "taxes_id": [Command.clear()], "supplier_taxes_id": [Command.clear()]})

    def _receipt(self, lines, total):
        donation = self.env["donation.donation"].create({
            "company_id": self.company.id, "check_total": total,
            "partner_id": self.donor.id, "donation_date": time.strftime("%Y-%m-%d"),
            "payment_method_line_id": self.method.id, "tax_receipt_option": "each",
            "line_ids": [Command.create(line) for line in lines]})
        donation.validate()
        self.assertTrue(donation.tax_receipt_id)
        return donation.tax_receipt_id

    def _html(self, receipt):
        html, _type = self.env["ir.actions.report"]._render_qweb_html(
            "donation_base.report_donation_tax_receipt", receipt.ids)
        return html.decode()

    def test_receipt_has_what_a_us_donor_needs(self):
        receipt = self._receipt([{
            "product_id": self.gift.id, "quantity": 1, "unit_price": 250}], 250)
        html = self._html(receipt)
        self.assertIn(receipt.number, html)
        self.assertIn("Dana Donor", html)
        self.assertIn("EIN", html)
        self.assertIn("12-3456789", html)
        self.assertIn("170(f)(8)", html)
        self.assertIn("No goods or services were provided", html)

    def test_goods_or_services_received_are_shown(self):
        gala = self.env["product.product"].create({
            "name": "Gala dinner", "type": "service", "donation_type": "donation",
            "tax_receipt_ok": False,
            "taxes_id": [Command.clear()], "supplier_taxes_id": [Command.clear()]})
        receipt = self._receipt([
            {"product_id": self.gift.id, "quantity": 1, "unit_price": 100},
            {"product_id": gala.id, "quantity": 1, "unit_price": 60}], 160)
        html = self._html(receipt)
        self.assertIn("Value of goods or services you received", html)
        self.assertIn("Goods or services were provided only where shown", html)
        self.assertNotIn("No goods or services were provided", html)

    def test_only_one_yearly_receipt_menu(self):
        menu = self.env.ref("nonprofit_reports.menu_nonprofit_donor_statement")
        self.assertFalse(menu.active)
