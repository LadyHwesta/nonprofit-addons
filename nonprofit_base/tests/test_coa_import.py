# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestNonprofitCoaImport(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        cls.Wizard = cls.env["nonprofit.coa.import.wizard"].with_company(cls.company)
        cls.template_codes = [
            row["code"]
            for row in cls.env["nonprofit.coa.import.wizard"]._iter_template_rows()
        ]

    def _accounts(self, codes, prefix=""):
        return self.env["account.account"].with_company(self.company).search([
            ("code", "in", [prefix + c for c in codes]),
            ("company_ids", "in", self.company.id),
        ])

    def test_01_imports_full_set(self):
        wizard = self.Wizard.create({"company_id": self.company.id})
        wizard.action_import()

        self.assertEqual(wizard.created_count, len(self.template_codes))
        self.assertEqual(wizard.skipped_count, 0)
        self.assertEqual(
            len(self._accounts(self.template_codes)), len(self.template_codes))

        # tags came across
        contrib = self._accounts(["4000"])
        self.assertIn(
            self.env.ref("nonprofit_base.tag_rev_contrib_unrestricted"),
            contrib.tag_ids)

    def test_02_second_run_is_noop(self):
        self.Wizard.create({"company_id": self.company.id}).action_import()
        second = self.Wizard.create({"company_id": self.company.id})
        second.action_import()

        self.assertEqual(second.created_count, 0)
        self.assertEqual(second.skipped_count, len(self.template_codes))

    def test_03_existing_code_is_skipped(self):
        self.env["account.account"].with_company(self.company).create({
            "code": "4000",
            "name": "Pre-existing 4000",
            "account_type": "income",
            "company_ids": [(4, self.company.id)],
        })
        wizard = self.Wizard.create({"company_id": self.company.id})
        wizard.action_import()

        self.assertEqual(wizard.created_count, len(self.template_codes) - 1)
        self.assertEqual(wizard.skipped_count, 1)
        # the pre-existing account was left untouched
        self.assertEqual(self._accounts(["4000"]).name, "Pre-existing 4000")

    def test_04_no_skip_raises_on_collision(self):
        self.env["account.account"].with_company(self.company).create({
            "code": "4000",
            "name": "Pre-existing 4000",
            "account_type": "income",
            "company_ids": [(4, self.company.id)],
        })
        wizard = self.Wizard.create({
            "company_id": self.company.id,
            "skip_existing": False,
        })
        with self.assertRaises(UserError):
            wizard.action_import()

    def test_05_code_prefix(self):
        wizard = self.Wizard.create({
            "company_id": self.company.id,
            "code_prefix": "9",
        })
        wizard.action_import()

        self.assertEqual(wizard.created_count, len(self.template_codes))
        self.assertTrue(self._accounts(["4000"], prefix="9"))
        self.assertFalse(self._accounts(["4000"]))

    def test_06_plans_and_tags_exist(self):
        for xmlid in (
            "analytic_plan_fund", "analytic_plan_program",
            "analytic_plan_function", "analytic_plan_grant",
        ):
            self.assertTrue(self.env.ref("nonprofit_base.%s" % xmlid))
        # analytic-account reads need sudo under the restricted test user
        self.assertEqual(
            self.env.ref(
                "nonprofit_base.analytic_account_fund_unrestricted").sudo().plan_id,
            self.env.ref("nonprofit_base.analytic_plan_fund"))
