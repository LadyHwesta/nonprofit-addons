# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import Command, fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import new_test_user, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestNonprofitGrant(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The accounting test user runs these; give it Grants too.
        cls.env.user.group_ids |= cls.env.ref("nonprofit_grant.group_grant_manager")
        cls.today = fields.Date.today()
        cls.funder = cls.env["res.partner"].create(
            {"name": "Community Foundation", "is_company": True, "is_funder": True})
        cls.writer = new_test_user(cls.env, login="writer", name="Grant Writer",
                                   groups="nonprofit_grant.group_grant_user")
        cls.viewer = new_test_user(cls.env, login="viewer", name="Board Member",
                                   groups="nonprofit_grant.group_grant_viewer")
        cls.awarded = cls.env.ref("nonprofit_grant.stage_awarded")
        cls.declined = cls.env.ref("nonprofit_grant.stage_declined")

    def _grant(self, **vals):
        return self.env["nonprofit.grant"].create(dict({
            "name": "Youth Arts 2027", "funder_id": self.funder.id,
            "amount_requested": 10000.0, "deadline_date": self.today + timedelta(days=30),
            "user_id": self.writer.id,
        }, **vals))

    def _award(self, grant, amount=8000.0):
        grant.write({"amount_awarded": amount, "stage_id": self.awarded.id})
        return grant

    # -- pipeline -----------------------------------------------------------

    def test_new_grant_gets_a_reference_and_a_deadline_todo(self):
        grant = self._grant()
        self.assertTrue(grant.reference.startswith("GR/"))
        self.assertEqual(grant.stage_id, self.env.ref("nonprofit_grant.stage_prospect"))
        todo = grant.activity_ids
        self.assertEqual(todo.user_id, self.writer)
        self.assertEqual(todo.date_deadline, grant.deadline_date)

    def test_submitting_clears_the_deadline_todo(self):
        grant = self._grant()
        grant.submitted_date = self.today
        self.assertFalse(grant.activity_ids)

    def test_moving_the_deadline_moves_the_todo(self):
        grant = self._grant()
        later = self.today + timedelta(days=45)
        grant.deadline_date = later
        self.assertEqual(grant.activity_ids.date_deadline, later)
        self.assertEqual(len(grant.activity_ids), 1)

    def test_declined_clears_the_todo(self):
        grant = self._grant()
        grant.stage_id = self.declined
        self.assertFalse(grant.activity_ids)

    # -- award and fund ------------------------------------------------------

    def test_award_needs_an_amount(self):
        grant = self._grant()
        with self.assertRaisesRegex(UserError, "amount awarded"):
            grant.stage_id = self.awarded

    def test_award_creates_a_grant_fund_under_funds(self):
        grant = self._award(self._grant())
        fund = grant.fund_id
        self.assertTrue(fund)
        self.assertEqual(fund.plan_id, self.env.ref("nonprofit_grant.analytic_plan_fund_grants"))
        self.assertEqual(fund.root_plan_id, self.env.ref("nonprofit_base.analytic_plan_fund"))
        self.assertEqual(fund.partner_id, self.funder)
        # Awarding again (e.g. editing the amount) doesn't make a second fund.
        grant.amount_awarded = 9000.0
        self.assertEqual(grant.fund_id, fund)

    # -- money ---------------------------------------------------------------

    def test_invoicing_and_receiving_a_payment(self):
        grant = self._award(self._grant())
        payment = self.env["nonprofit.grant.payment"].create({
            "grant_id": grant.id, "name": "First installment",
            "expected_date": self.today, "amount": 4000.0})
        self.assertEqual(payment.state, "expected")
        payment.action_create_invoice()
        invoice = payment.move_id
        self.assertEqual(invoice.partner_id, self.funder)
        self.assertEqual(invoice.amount_total, 4000.0)
        self.assertEqual(invoice.invoice_line_ids.analytic_distribution, {str(grant.fund_id.id): 100.0})
        self.assertFalse(invoice.invoice_line_ids.tax_ids)
        invoice.action_post()
        self.assertEqual(payment.state, "invoiced")
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids).create({})._create_payments()
        self.assertEqual(payment.state, "paid")
        self.assertEqual(grant.amount_received, 4000.0)
        self.assertEqual(grant.amount_invoiced, 4000.0)

    def test_no_invoice_before_award(self):
        grant = self._grant()
        payment = self.env["nonprofit.grant.payment"].create({
            "grant_id": grant.id, "expected_date": self.today, "amount": 100.0})
        with self.assertRaisesRegex(UserError, "Award the grant first"):
            payment.action_create_invoice()

    def test_spending_from_the_fund(self):
        grant = self._award(self._grant())
        bill = self.env["account.move"].create({
            "move_type": "in_invoice", "partner_id": self.partner_a.id,
            "invoice_date": self.today,
            "invoice_line_ids": [Command.create({
                "name": "Art supplies", "quantity": 1, "price_unit": 2000.0,
                "account_id": self.company_data["default_account_expense"].id,
                "tax_ids": [Command.clear()],
                "analytic_distribution": {str(grant.fund_id.id): 100.0},
            })],
        })
        bill.action_post()
        grant.invalidate_recordset()
        self.assertAlmostEqual(grant.amount_spent, 2000.0)
        self.assertAlmostEqual(grant.amount_left, 6000.0)
        self.assertAlmostEqual(grant.spent_percent, 25.0)
        action = grant.action_release_restriction()
        self.assertEqual(action["context"]["default_fund_from_id"], grant.fund_id.id)
        self.assertAlmostEqual(action["context"]["default_amount"], 2000.0)

    # -- reports -------------------------------------------------------------

    def test_report_todo_and_submission(self):
        grant = self._award(self._grant())
        report = self.env["nonprofit.grant.report"].create({
            "grant_id": grant.id, "name": "Interim report",
            "due_date": self.today + timedelta(days=90)})
        self.assertEqual(report.activity_ids.user_id, self.writer)
        self.assertEqual(grant.next_deadline, report.due_date)
        report.action_mark_submitted()
        self.assertEqual(report.state, "submitted")
        self.assertFalse(report.activity_ids)
        self.assertFalse(grant.next_deadline)

    def test_next_deadline_is_the_application_before_submission(self):
        grant = self._grant()
        self.assertEqual(grant.next_deadline, grant.deadline_date)

    # -- funders and access --------------------------------------------------

    def test_funder_sees_their_grants(self):
        self._grant()
        self._grant(name="Second")
        self.assertEqual(self.funder.grant_count, 2)
        self.assertEqual(self.funder.action_view_grants()["domain"],
                         [("funder_id", "=", self.funder.id)])

    def test_viewer_reads_but_cannot_change(self):
        grant = self._grant()
        self.assertEqual(grant.with_user(self.viewer).name, "Youth Arts 2027")
        with self.assertRaises(AccessError):
            grant.with_user(self.viewer).write({"name": "Changed"})

    def test_writer_creates_but_cannot_delete(self):
        grant = self.env["nonprofit.grant"].with_user(self.writer).create(
            {"name": "Mine", "funder_id": self.funder.id})
        with self.assertRaises(AccessError):
            grant.unlink()

    def test_awarded_grant_has_no_application_deadline_left(self):
        grant = self._award(self._grant())
        self.assertFalse(grant.submitted_date)
        self.assertFalse(grant.next_deadline)
        self.assertFalse(grant.activity_ids)
