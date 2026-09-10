# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _nonprofit_fund_coverage(self, fund_plan):
        """Percentage of this line's analytic distribution that lands on
        accounts belonging to ``fund_plan``."""
        self.ensure_one()
        covered = 0.0
        AnalyticAccount = self.env["account.analytic.account"].sudo()
        for key, percentage in (self.analytic_distribution or {}).items():
            account_ids = [int(x) for x in str(key).split(",") if x]
            accounts = AnalyticAccount.browse(account_ids)
            if any(a.root_plan_id == fund_plan for a in accounts):
                covered += percentage
        return covered

    @api.constrains("analytic_distribution", "account_id", "parent_state",
                    "company_id")
    def _check_nonprofit_fund(self):
        if self.env.context.get("skip_fund_check"):
            return
        fund_plan = self.env.ref(
            "nonprofit_base.analytic_plan_fund", raise_if_not_found=False)
        if not fund_plan:
            return
        for line in self:
            if line.parent_state != "posted" or line.display_type != "product":
                continue
            if not line.company_id.nonprofit_fund_required:
                continue
            account_type = line.account_id.account_type or ""
            if not (account_type.startswith("income")
                    or account_type.startswith("expense")):
                continue
            coverage = line._nonprofit_fund_coverage(fund_plan)
            if float_compare(coverage, 100.0, precision_digits=2) != 0:
                raise ValidationError(_(
                    "Fund accounting is on for %(company)s. The \"%(account)s\" "
                    "line on %(move)s must be assigned 100%% to Fund analytic "
                    "accounts before it can be posted (currently %(pct).0f%%).",
                    company=line.company_id.display_name,
                    account=line.account_id.display_name,
                    move=line.move_id.display_name,
                    pct=coverage,
                ))
