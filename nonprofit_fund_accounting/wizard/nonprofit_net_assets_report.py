# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class NonprofitNetAssetsReport(models.TransientModel):
    _name = "nonprofit.net.assets.report"
    _description = "Net-Asset Roll-Forward"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")
    date_from = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(
            month=1, day=1))
    date_to = fields.Date(
        required=True, default=fields.Date.context_today)
    line_ids = fields.One2many(
        "nonprofit.net.assets.report.line", "report_id", string="Funds")

    def _fund_accounts(self):
        plan = self.env.ref(
            "nonprofit_base.analytic_plan_fund", raise_if_not_found=False)
        if not plan:
            raise UserError(_(
                "The Fund analytic plan is missing - install nonprofit_base."))
        return self.env["account.analytic.account"].sudo().search(
            [("root_plan_id", "=", plan.id)]), plan

    def _operating_by_fund(self, plan, date_from, date_to):
        """{fund_id: (revenue, expense)} from posted income/expense move
        lines in the date window, split by Fund analytic distribution."""
        release_accounts = (
            self.company_id.nonprofit_release_restricted_account_id
            | self.company_id.nonprofit_release_unrestricted_account_id
        )
        domain = [
            ("parent_state", "=", "posted"),
            ("company_id", "=", self.company_id.id),
            ("display_type", "=", "product"),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("account_id.account_type", "in",
             ["income", "income_other", "expense", "expense_depreciation",
              "expense_direct_cost"]),
            ("account_id", "not in", release_accounts.ids),
        ]
        result = {}
        AnalyticAccount = self.env["account.analytic.account"].sudo()
        for line in self.env["account.move.line"].search(domain):
            account_type = line.account_id.account_type
            for key, pct in (line.analytic_distribution or {}).items():
                ids = [int(x) for x in str(key).split(",") if x]
                for analytic in AnalyticAccount.browse(ids):
                    if analytic.root_plan_id != plan:
                        continue
                    revenue, expense = result.get(analytic.id, (0.0, 0.0))
                    share = line.balance * pct / 100.0
                    if account_type in ("income", "income_other"):
                        revenue -= share  # credit balance is negative
                    else:
                        expense += share
                    result[analytic.id] = (revenue, expense)
        return result

    def _releases_by_fund(self, date_from, date_to):
        """{fund_id: (released_in, released_out)} from posted releases."""
        releases = self.env["nonprofit.restriction.release"].search([
            ("state", "=", "posted"),
            ("company_id", "=", self.company_id.id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ])
        result = {}
        for release in releases:
            rin_id, rout_id = release.fund_to_id.id, release.fund_from_id.id
            rin, _out = result.get(rin_id, (0.0, 0.0))
            result[rin_id] = (rin + release.amount, _out)
            _in, rout = result.get(rout_id, (0.0, 0.0))
            result[rout_id] = (_in, rout + release.amount)
        return result

    def action_compute(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise UserError(_("The start date is after the end date."))
        funds, plan = self._fund_accounts()
        epoch = fields.Date.to_date("1900-01-01")
        day_before = fields.Date.subtract(self.date_from, days=1)

        prior_op = self._operating_by_fund(plan, epoch, day_before)
        prior_rel = self._releases_by_fund(epoch, day_before)
        period_op = self._operating_by_fund(plan, self.date_from, self.date_to)
        period_rel = self._releases_by_fund(self.date_from, self.date_to)

        self.line_ids.unlink()
        lines = []
        for fund in funds:
            p_rev, p_exp = prior_op.get(fund.id, (0.0, 0.0))
            p_in, p_out = prior_rel.get(fund.id, (0.0, 0.0))
            beginning = p_rev - p_exp + p_in - p_out

            rev, exp = period_op.get(fund.id, (0.0, 0.0))
            r_in, r_out = period_rel.get(fund.id, (0.0, 0.0))
            ending = beginning + rev - exp + r_in - r_out

            if any((beginning, rev, exp, r_in, r_out, ending)):
                lines.append((0, 0, {
                    "fund_id": fund.id,
                    "beginning_balance": beginning,
                    "revenue": rev,
                    "expense": exp,
                    "released_in": r_in,
                    "released_out": r_out,
                    "ending_balance": ending,
                }))
        self.line_ids = lines
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "views": [(self.env.ref(
                "nonprofit_fund_accounting."
                "nonprofit_net_assets_report_result_form").id, "form")],
        }


class NonprofitNetAssetsReportLine(models.TransientModel):
    _name = "nonprofit.net.assets.report.line"
    _description = "Net-Asset Roll-Forward Line"
    _order = "fund_id"

    report_id = fields.Many2one(
        "nonprofit.net.assets.report", required=True, ondelete="cascade")
    currency_id = fields.Many2one(related="report_id.currency_id")
    fund_id = fields.Many2one("account.analytic.account", string="Fund")
    beginning_balance = fields.Monetary()
    revenue = fields.Monetary()
    expense = fields.Monetary()
    released_in = fields.Monetary(string="Restrictions Released In")
    released_out = fields.Monetary(string="Restrictions Released Out")
    ending_balance = fields.Monetary()
