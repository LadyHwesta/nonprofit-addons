# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import FundAccountingCommon


@tagged("post_install", "-at_install")
class TestFundConstraint(FundAccountingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company.nonprofit_fund_required = True

    def _income_entry(self, dist):
        return self._entry([
            (self.account_revenue, 0.0, 100.0, dist),
            (self.account_receivable, 100.0, 0.0, None),
        ])

    def test_block_without_fund(self):
        move = self._income_entry(None)
        with self.assertRaises(ValidationError):
            move.action_post()

    def test_pass_with_full_fund(self):
        move = self._income_entry({str(self.fund_ur.id): 100})
        move.action_post()
        self.assertEqual(move.state, "posted")

    def test_split_across_two_funds(self):
        move = self._income_entry(
            {str(self.fund_ur.id): 60, str(self.fund_drp.id): 40})
        move.action_post()
        self.assertEqual(move.state, "posted")

    def test_partial_fund_blocked(self):
        move = self._income_entry({str(self.fund_ur.id): 50})
        with self.assertRaises(ValidationError):
            move.action_post()

    def test_skip_fund_check_context(self):
        move = self._income_entry(None)
        move.with_context(skip_fund_check=True).action_post()
        self.assertEqual(move.state, "posted")

    def test_toggle_off(self):
        self.company.nonprofit_fund_required = False
        move = self._income_entry(None)
        move.action_post()
        self.assertEqual(move.state, "posted")

    def test_receivable_line_not_required(self):
        # only the income line needs a fund; the balancing AR line does not
        move = self._income_entry({str(self.fund_ur.id): 100})
        move.action_post()
        self.assertEqual(move.state, "posted")
