# -*- coding: utf-8 -*-
from odoo import Command, fields
from odoo.tests import tagged

from .common import FundAccountingCommon


@tagged("post_install", "-at_install")
class TestNetAssetsReport(FundAccountingCommon):
    @classmethod
    def _post_entry(cls, lines):
        move = cls.env["account.move"].create({
            "move_type": "entry",
            "date": cls.today,
            "journal_id": cls.misc_journal.id,
            "line_ids": [
                Command.create({
                    "account_id": acc.id, "debit": dr, "credit": cr,
                    "analytic_distribution": dist,
                })
                for acc, dr, cr, dist in lines
            ],
        })
        move.action_post()
        return move

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company.nonprofit_fund_required = True
        cls.today = fields.Date.context_today(cls.env.user)
        cls.year_start = cls.today.replace(month=1, day=1)

        # restricted contribution 1,000
        cls._post_entry([
            (cls.account_revenue, 0.0, 1000.0, {str(cls.fund_drp.id): 100}),
            (cls.account_receivable, 1000.0, 0.0, None),
        ])
        # program expense 300 against the same restricted fund
        cls._post_entry([
            (cls.account_expense, 300.0, 0.0, {str(cls.fund_drp.id): 100}),
            (cls.account_receivable, 0.0, 300.0, None),
        ])
        # release 400 from restricted-purpose to unrestricted
        cls.env["nonprofit.restriction.release"].create({
            "fund_from_id": cls.fund_drp.id,
            "fund_to_id": cls.fund_ur.id,
            "amount": 400.0,
            "journal_id": cls.misc_journal.id,
            "date": cls.today,
        }).action_post()

    def _run(self):
        report = self.env["nonprofit.net.assets.report"].create({
            "company_id": self.company.id,
            "date_from": self.year_start,
            "date_to": self.today,
        })
        report.action_compute()
        return {line.fund_id: line for line in report.line_ids}, report

    def test_roll_forward_numbers(self):
        by_fund, _report = self._run()

        drp = by_fund[self.fund_drp]
        self.assertEqual(drp.beginning_balance, 0.0)
        self.assertEqual(drp.revenue, 1000.0)
        self.assertEqual(drp.expense, 300.0)
        self.assertEqual(drp.released_out, 400.0)
        self.assertEqual(drp.released_in, 0.0)
        self.assertEqual(drp.ending_balance, 300.0)

        ur = by_fund[self.fund_ur]
        self.assertEqual(ur.revenue, 0.0)
        self.assertEqual(ur.released_in, 400.0)
        self.assertEqual(ur.ending_balance, 400.0)

    def test_release_accounts_excluded_from_revenue(self):
        _by_fund, report = self._run()
        self.assertEqual(sum(report.line_ids.mapped("revenue")), 1000.0)
