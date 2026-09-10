# -*- coding: utf-8 -*-
from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class FundAccountingCommon(AccountTestInvoicingCommon):
    @classmethod
    def get_default_groups(cls):
        # fund accounting needs Analytic Accounting enabled for the test user
        return super().get_default_groups() | cls.env.ref(
            "analytic.group_analytic_accounting")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        cls.misc_journal = cls.company_data["default_journal_misc"]
        cls.account_revenue = cls.company_data["default_account_revenue"]
        cls.account_expense = cls.company_data["default_account_expense"]
        cls.account_receivable = cls.company_data["default_account_receivable"]

        cls.fund_ur = cls.env.ref(
            "nonprofit_base.analytic_account_fund_unrestricted")
        cls.fund_drp = cls.env.ref(
            "nonprofit_base.analytic_account_fund_restricted_purpose")
        cls.fund_drt = cls.env.ref(
            "nonprofit_base.analytic_account_fund_restricted_time")

        # the two release clearing accounts fund_accounting expects
        cls.release_restricted = cls.env["account.account"].create({
            "code": "NFP4900", "name": "Net Assets Released - Restricted",
            "account_type": "income", "company_ids": [Command.link(cls.company.id)],
        })
        cls.release_unrestricted = cls.env["account.account"].create({
            "code": "NFP4910", "name": "Net Assets Released - Unrestricted",
            "account_type": "income", "company_ids": [Command.link(cls.company.id)],
        })
        cls.company.write({
            "nonprofit_release_restricted_account_id": cls.release_restricted.id,
            "nonprofit_release_unrestricted_account_id": cls.release_unrestricted.id,
        })

    def _entry(self, lines):
        """lines: list of (account, debit, credit, analytic_distribution)"""
        return self.env["account.move"].create({
            "move_type": "entry",
            "journal_id": self.misc_journal.id,
            "line_ids": [
                Command.create({
                    "account_id": acc.id, "debit": dr, "credit": cr,
                    "analytic_distribution": dist,
                })
                for acc, dr, cr, dist in lines
            ],
        })
