# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import ReportsCommon


@tagged("post_install", "-at_install")
class TestMisReports(ReportsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Seed Donor"})
        cls._gift(partner, 1000.0, cls.today)  # revenue on a soa_revenue account
        # an expense on the soa_expense account
        cls.env["account.move"].create({
            "move_type": "entry",
            "date": cls.today,
            "journal_id": cls.misc_journal.id,
            "line_ids": [
                (0, 0, {"account_id": cls.expense_account.id,
                        "debit": 400.0, "credit": 0.0}),
                (0, 0, {"account_id": cls.account_receivable.id,
                        "debit": 0.0, "credit": 400.0}),
            ],
        }).action_post()

    def _compute(self, xmlid):
        instance = self.env.ref("nonprofit_reports.%s" % xmlid).sudo()
        instance.company_id = self.company
        return instance.compute()

    def _row(self, result, label):
        for row in result["body"]:
            if label in (row.get("label"), row.get("description")):
                return row
        return None

    def test_statement_of_activities_computes(self):
        result = self._compute("mis_instance_soa_current_year")
        self.assertTrue(result["body"])

        revenue = self._row(result, "Total Revenue and Support")
        self.assertIsNotNone(revenue)
        self.assertAlmostEqual(revenue["cells"][0]["val"], 1000.0)

        change = self._row(result, "Change in Net Assets")
        self.assertIsNotNone(change)
        self.assertAlmostEqual(change["cells"][0]["val"], 600.0)

    def test_statement_of_financial_position_computes(self):
        result = self._compute("mis_instance_sofp_current_year")
        self.assertTrue(result["body"])
        self.assertIsNotNone(self._row(result, "Total Net Assets"))
