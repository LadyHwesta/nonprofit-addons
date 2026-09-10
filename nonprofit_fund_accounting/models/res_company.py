# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    nonprofit_fund_required = fields.Boolean(
        string="Require a Fund on income/expense postings",
        help="Block posting a journal entry while any income or expense line "
             "is not assigned 100% to Fund analytic accounts.")
    nonprofit_default_program_id = fields.Many2one(
        "account.analytic.account", string="Default Program",
        domain="[('root_plan_id', '=', nonprofit_fund_program_plan_id)]")
    nonprofit_default_function_id = fields.Many2one(
        "account.analytic.account", string="Default Function",
        domain="[('root_plan_id', '=', nonprofit_fund_function_plan_id)]")
    nonprofit_release_restricted_account_id = fields.Many2one(
        "account.account", string="Release - Restricted Side",
        check_company=True,
        help="Income account debited when releasing a donor restriction "
             "(the 'with donor restrictions' side).")
    nonprofit_release_unrestricted_account_id = fields.Many2one(
        "account.account", string="Release - Unrestricted Side",
        check_company=True,
        help="Income account credited when releasing a donor restriction "
             "(the 'without donor restrictions' side).")

    # Helper related fields so the settings-view domains can resolve the plans.
    nonprofit_fund_program_plan_id = fields.Many2one(
        "account.analytic.plan", compute="_compute_nonprofit_plan_ids")
    nonprofit_fund_function_plan_id = fields.Many2one(
        "account.analytic.plan", compute="_compute_nonprofit_plan_ids")

    @api.depends_context("uid")
    def _compute_nonprofit_plan_ids(self):
        program = self.env.ref(
            "nonprofit_base.analytic_plan_program", raise_if_not_found=False)
        function = self.env.ref(
            "nonprofit_base.analytic_plan_function", raise_if_not_found=False)
        for company in self:
            company.nonprofit_fund_program_plan_id = program
            company.nonprofit_fund_function_plan_id = function

    def _nonprofit_autodetect_release_accounts(self):
        """Fill the two release clearing accounts from the nonprofit_base
        chart tags when they are not set yet. Safe to call repeatedly."""
        tag_restricted = self.env.ref(
            "nonprofit_base.tag_release_restricted", raise_if_not_found=False)
        tag_unrestricted = self.env.ref(
            "nonprofit_base.tag_release_unrestricted", raise_if_not_found=False)
        if not (tag_restricted and tag_unrestricted):
            return
        Account = self.env["account.account"]
        for company in self:
            if not company.nonprofit_release_restricted_account_id:
                company.nonprofit_release_restricted_account_id = Account.search([
                    ("tag_ids", "in", tag_restricted.id),
                    ("company_ids", "in", company.id),
                ], limit=1)
            if not company.nonprofit_release_unrestricted_account_id:
                company.nonprofit_release_unrestricted_account_id = Account.search([
                    ("tag_ids", "in", tag_unrestricted.id),
                    ("company_ids", "in", company.id),
                ], limit=1)
