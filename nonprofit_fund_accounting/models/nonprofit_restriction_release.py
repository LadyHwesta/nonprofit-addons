# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class NonprofitRestrictionRelease(models.Model):
    _name = "nonprofit.restriction.release"
    _description = "Release from Donor Restriction"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Reference", required=True, copy=False, readonly=True,
        default=lambda self: _("New"))
    company_id = fields.Many2one(
        "res.company", required=True, readonly=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")
    date = fields.Date(
        required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        default="draft", required=True, tracking=True)

    fund_from_id = fields.Many2one(
        "account.analytic.account", string="Released From (restricted)",
        required=True, tracking=True,
        domain="[('root_plan_id', '=', fund_plan_id)]")
    fund_to_id = fields.Many2one(
        "account.analytic.account", string="Released To",
        required=True, tracking=True,
        domain="[('root_plan_id', '=', fund_plan_id)]",
        default=lambda self: self.env.ref(
            "nonprofit_base.analytic_account_fund_unrestricted",
            raise_if_not_found=False))
    fund_plan_id = fields.Many2one(
        "account.analytic.plan", compute="_compute_fund_plan_id")

    program_id = fields.Many2one(
        "account.analytic.account", string="Program",
        default=lambda self: self.env.company.nonprofit_default_program_id)
    function_id = fields.Many2one(
        "account.analytic.account", string="Function",
        default=lambda self: self.env.company.nonprofit_default_function_id)

    amount = fields.Monetary(required=True, tracking=True)
    journal_id = fields.Many2one(
        "account.journal", string="Journal", required=True,
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]",
        default=lambda self: self.env["account.journal"].search(
            [("type", "=", "general"),
             ("company_id", "=", self.env.company.id)], limit=1))
    move_id = fields.Many2one(
        "account.move", string="Journal Entry", readonly=True, copy=False)
    note = fields.Text()

    @api.depends_context("uid")
    def _compute_fund_plan_id(self):
        plan = self.env.ref(
            "nonprofit_base.analytic_plan_fund", raise_if_not_found=False)
        for release in self:
            release.fund_plan_id = plan

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "nonprofit.restriction.release") or _("New")
        return super().create(vals_list)

    def _analytic_distribution(self, fund):
        dist = {str(fund.id): 100.0}
        if self.program_id:
            dist[str(self.program_id.id)] = 100.0
        if self.function_id:
            dist[str(self.function_id.id)] = 100.0
        return dist

    def _prepare_move_vals(self):
        self.ensure_one()
        company = self.company_id
        restricted = company.nonprofit_release_restricted_account_id
        unrestricted = company.nonprofit_release_unrestricted_account_id
        return {
            "move_type": "entry",
            "journal_id": self.journal_id.id,
            "date": self.date,
            "company_id": company.id,
            "ref": _("Release from restriction: %s", self.name),
            "line_ids": [
                (0, 0, {
                    "name": _("Net assets released - %s", self.fund_from_id.name),
                    "account_id": restricted.id,
                    "debit": self.amount,
                    "credit": 0.0,
                    "analytic_distribution": self._analytic_distribution(
                        self.fund_from_id),
                }),
                (0, 0, {
                    "name": _("Net assets released - %s", self.fund_to_id.name),
                    "account_id": unrestricted.id,
                    "debit": 0.0,
                    "credit": self.amount,
                    "analytic_distribution": self._analytic_distribution(
                        self.fund_to_id),
                }),
            ],
        }

    def _check_ready_to_post(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only a draft release can be posted."))
        if self.amount <= 0:
            raise UserError(_("The amount to release must be positive."))
        if self.fund_from_id == self.fund_to_id:
            raise UserError(_(
                "The released-from and released-to funds must be different."))
        if not (self.company_id.nonprofit_release_restricted_account_id
                and self.company_id.nonprofit_release_unrestricted_account_id):
            raise UserError(_(
                "Set the two 'Net Assets Released' accounts in Accounting "
                "Settings (Non-Profit Fund Accounting) before posting a "
                "release."))
        if not self.journal_id:
            raise UserError(_("Select a journal for the release entry."))

    def action_post(self):
        for release in self:
            release._check_ready_to_post()
            move = self.env["account.move"].create(release._prepare_move_vals())
            move.action_post()
            release.write({"move_id": move.id, "state": "posted"})
        return True

    def action_cancel(self):
        for release in self:
            if release.move_id and release.move_id.state == "posted":
                release.move_id._reverse_moves(
                    [{"date": fields.Date.context_today(release)}], cancel=True)
            elif release.move_id:
                release.move_id.button_draft()
                release.move_id.unlink()
            release.state = "cancelled"
        return True

    def action_draft(self):
        self.filtered(lambda r: r.state == "cancelled").write({"state": "draft"})

    def action_view_move(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": self.move_id.id,
            "view_mode": "form",
        }
