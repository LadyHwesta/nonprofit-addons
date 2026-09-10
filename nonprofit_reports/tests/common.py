# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import Command, fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class ReportsCommon(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        cls.misc_journal = cls.company_data["default_journal_misc"]
        cls.account_receivable = cls.company_data["default_account_receivable"]

        cls.today = fields.Date.context_today(cls.env.user).replace(month=6, day=15)
        cls.last_year = cls.today - relativedelta(years=1)
        cls.two_years_ago = cls.today - relativedelta(years=2)

        cls.contrib_account = cls.env["account.account"].create({
            "code": "NFPREV1",
            "name": "Contributions - Unrestricted (test)",
            "account_type": "income",
            "company_ids": [Command.link(cls.company.id)],
            "tag_ids": [Command.set([
                cls.env.ref("nonprofit_base.tag_rev_contrib_unrestricted").id,
                cls.env.ref("nonprofit_base.tag_soa_revenue").id,
            ])],
        })
        cls.expense_account = cls.env["account.account"].create({
            "code": "NFPEXP1",
            "name": "Program Expense (test)",
            "account_type": "expense",
            "company_ids": [Command.link(cls.company.id)],
            "tag_ids": [Command.set([
                cls.env.ref("nonprofit_base.tag_soa_expense").id,
                cls.env.ref("nonprofit_base.tag_function_program").id,
            ])],
        })

    @classmethod
    def _gift(cls, partner, amount, date, account=None):
        move = cls.env["account.move"].create({
            "move_type": "entry",
            "date": date,
            "partner_id": partner.id,
            "journal_id": cls.misc_journal.id,
            "line_ids": [
                Command.create({
                    "account_id": cls.account_receivable.id,
                    "partner_id": partner.id,
                    "debit": amount, "credit": 0.0,
                }),
                Command.create({
                    "account_id": (account or cls.contrib_account).id,
                    "partner_id": partner.id,
                    "debit": 0.0, "credit": amount,
                }),
            ],
        })
        move.action_post()
        return move
