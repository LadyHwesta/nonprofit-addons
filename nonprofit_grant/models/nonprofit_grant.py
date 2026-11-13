# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

DEADLINE_SUMMARY = "Application due"


class NonprofitGrant(models.Model):
    """A grant the organization is seeking or has received."""
    _name = "nonprofit.grant"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Grant"
    _order = "deadline_date, id desc"

    name = fields.Char(string="Grant", required=True, tracking=True,
                       help='e.g. "Youth Arts 2027" or the funder\'s program name.')
    reference = fields.Char(readonly=True, copy=False, default=lambda self: _("New"))
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")
    color = fields.Integer()
    user_id = fields.Many2one(
        "res.users", string="Owner", default=lambda self: self.env.user, tracking=True,
        help="Who writes and looks after this grant; gets its reminders.")

    funder_id = fields.Many2one(
        "res.partner", string="Funder", required=True, tracking=True,
        help="The foundation, agency or company giving the grant.")
    contact_id = fields.Many2one(
        "res.partner", string="Program Officer",
        domain="[('parent_id', '=', funder_id)]",
        help="The person at the funder you deal with.")
    stage_id = fields.Many2one(
        "nonprofit.grant.stage", string="Stage", tracking=True, index=True,
        default=lambda self: self.env["nonprofit.grant.stage"].search([], limit=1),
        group_expand="_read_group_stage_ids", copy=False)
    is_awarded = fields.Boolean(related="stage_id.is_awarded")
    is_declined = fields.Boolean(related="stage_id.is_declined")

    amount_requested = fields.Monetary(tracking=True)
    amount_awarded = fields.Monetary(tracking=True)
    deadline_date = fields.Date(string="Application Deadline", tracking=True)
    submitted_date = fields.Date(tracking=True)
    decision_date = fields.Date(string="Decision Date")
    period_start = fields.Date(string="Grant Period From")
    period_end = fields.Date(string="Grant Period To")
    restriction = fields.Selection(
        [("purpose", "Restricted to a purpose"), ("time", "Restricted to a time period"),
         ("unrestricted", "Unrestricted")],
        default="purpose", required=True, tracking=True,
        help="What the funder lets the money be used for.")
    purpose = fields.Html(help="What the grant pays for, in the funder's terms.")

    fund_id = fields.Many2one(
        "account.analytic.account", string="Fund", copy=False, tracking=True,
        help="This grant's own fund. Expenses coded to it count as spent "
             "from the grant. Made automatically when the grant is awarded.")
    program_id = fields.Many2one(
        "account.analytic.account", string="Program",
        domain=lambda self: self._program_domain(),
        help="The program this grant supports, if any.")

    report_ids = fields.One2many("nonprofit.grant.report", "grant_id", string="Reports")
    payment_ids = fields.One2many("nonprofit.grant.payment", "grant_id", string="Payments")
    report_count = fields.Integer(compute="_compute_report_count")

    amount_invoiced = fields.Monetary(compute="_compute_money")
    amount_received = fields.Monetary(compute="_compute_money")
    amount_spent = fields.Monetary(compute="_compute_money",
                                   help="Expenses coded to this grant's fund.")
    amount_left = fields.Monetary(string="Left to Spend", compute="_compute_money")
    spent_percent = fields.Float(string="% Spent", compute="_compute_money")
    amount_released = fields.Monetary(
        compute="_compute_money",
        help="Released from restriction so far (Restriction Releases from this fund).")
    next_deadline = fields.Date(
        compute="_compute_next_deadline",
        help="The next thing due: the application, or the next report.")

    # -- defaults and display ---------------------------------------------

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return stages.search([])

    @api.model
    def _program_domain(self):
        plan = self.env.ref("nonprofit_base.analytic_plan_program", raise_if_not_found=False)
        return [("root_plan_id", "=", plan.id)] if plan else []

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", _("New")) == _("New"):
                vals["reference"] = self.env["ir.sequence"].next_by_code("nonprofit.grant") or _("New")
        grants = super().create(vals_list)
        grants._sync_deadline_todo()
        grants.filtered("is_awarded")._on_awarded()
        return grants

    def write(self, vals):
        result = super().write(vals)
        if {"deadline_date", "user_id", "stage_id", "submitted_date"} & set(vals):
            self._sync_deadline_todo()
        if "stage_id" in vals or "amount_awarded" in vals:
            self.filtered("is_awarded")._on_awarded()
        return result

    @api.depends("reference", "name")
    def _compute_display_name(self):
        for grant in self:
            grant.display_name = f"{grant.reference} {grant.name}" if grant.reference else grant.name

    @api.constrains("amount_requested", "amount_awarded")
    def _check_amounts(self):
        for grant in self:
            if grant.amount_requested < 0 or grant.amount_awarded < 0:
                raise ValidationError(_("Grant amounts can't be negative."))

    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for grant in self:
            if grant.period_start and grant.period_end and grant.period_end < grant.period_start:
                raise ValidationError(_("The grant period ends before it starts."))

    # -- money --------------------------------------------------------------

    @api.depends("report_ids")
    def _compute_report_count(self):
        for grant in self:
            grant.report_count = len(grant.report_ids)

    @api.depends("amount_awarded", "fund_id", "payment_ids.state", "payment_ids.amount")
    def _compute_money(self):
        Line = self.env["account.analytic.line"].sudo()
        Release = self.env["nonprofit.restriction.release"].sudo()
        for grant in self:
            payments = grant.payment_ids
            grant.amount_invoiced = sum(payments.filtered(lambda p: p.state != "expected").mapped("amount"))
            grant.amount_received = sum(payments.mapped("amount_paid"))
            spent = released = 0.0
            if grant.fund_id:
                column = grant.fund_id.plan_id._column_name()
                lines = Line.search([(column, "=", grant.fund_id.id), ("amount", "<", 0)])
                spent = -sum(lines.mapped("amount"))
                released = sum(Release.search([
                    ("fund_from_id", "=", grant.fund_id.id), ("state", "=", "posted")]).mapped("amount"))
            grant.amount_spent = spent
            grant.amount_released = released
            grant.amount_left = grant.amount_awarded - spent
            grant.spent_percent = (spent / grant.amount_awarded * 100) if grant.amount_awarded else 0.0

    def _application_pending(self):
        """Still to apply: not submitted, and not past the decision
        (awarded, declined or closed)."""
        self.ensure_one()
        stage = self.stage_id
        return not self.submitted_date and not (stage.is_awarded or stage.is_declined or stage.is_closed)

    @api.depends("deadline_date", "submitted_date", "stage_id", "report_ids.due_date", "report_ids.state")
    def _compute_next_deadline(self):
        for grant in self:
            dates = [r.due_date for r in grant.report_ids if r.state == "todo" and r.due_date]
            if grant.deadline_date and grant._application_pending():
                dates.append(grant.deadline_date)
            grant.next_deadline = min(dates) if dates else False

    # -- award --------------------------------------------------------------

    def _grants_plan(self):
        """The Grants sub-plan of the Fund plan, so grant funds are Funds."""
        return self.env.ref("nonprofit_grant.analytic_plan_fund_grants")

    def _on_awarded(self):
        for grant in self:
            if not grant.amount_awarded:
                raise UserError(_(
                    "Enter the amount awarded for %(grant)s before moving it to %(stage)s.",
                    grant=grant.display_name, stage=grant.stage_id.name))
            if not grant.fund_id:
                grant.fund_id = self.env["account.analytic.account"].create({
                    # Odoo shows the funder (partner) after it already.
                    "name": _("Grant: %(name)s", name=grant.name),
                    "code": grant.reference,
                    "plan_id": grant._grants_plan().id,
                    "partner_id": grant.funder_id.id,
                    "company_id": grant.company_id.id,
                })
                grant.message_post(body=_("Fund %(fund)s created for this grant.",
                                          fund=grant.fund_id.display_name))

    def action_create_fund(self):
        self._on_awarded()

    # -- reminders ----------------------------------------------------------

    def _sync_deadline_todo(self):
        """One to-do for the owner on the application deadline, while the
        grant hasn't been submitted."""
        todo = self.env.ref("mail.mail_activity_data_todo")
        for grant in self:
            existing = grant.activity_ids.filtered(
                lambda a: a.activity_type_id == todo and a.summary == _(DEADLINE_SUMMARY))
            wanted = grant.deadline_date and grant.user_id and grant._application_pending()
            if not wanted:
                existing.unlink()
                continue
            if existing:
                existing.write({"date_deadline": grant.deadline_date, "user_id": grant.user_id.id})
            else:
                grant.activity_schedule(
                    "mail.mail_activity_data_todo", date_deadline=grant.deadline_date,
                    summary=_(DEADLINE_SUMMARY), user_id=grant.user_id.id,
                    note=_("Application for %(grant)s to %(funder)s is due.",
                           grant=grant.name, funder=grant.funder_id.name))

    # -- buttons ------------------------------------------------------------

    def action_view_spending(self):
        self.ensure_one()
        if not self.fund_id:
            raise UserError(_("This grant has no fund yet."))
        column = self.fund_id.plan_id._column_name()
        return {
            "type": "ir.actions.act_window",
            "name": _("Spending: %(grant)s", grant=self.name),
            "res_model": "account.analytic.line",
            "view_mode": "list,form",
            "domain": [(column, "=", self.fund_id.id), ("amount", "<", 0)],
        }

    def action_release_restriction(self):
        """Release what's been spent and not yet released, using the fund
        accounting release form, prefilled."""
        self.ensure_one()
        if not self.fund_id:
            raise UserError(_("This grant has no fund yet."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Release from Restriction"),
            "res_model": "nonprofit.restriction.release",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_fund_from_id": self.fund_id.id,
                "default_amount": max(self.amount_spent - self.amount_released, 0.0),
                "default_program_id": self.program_id.id or False,
                "default_note": _("Grant %(grant)s: spent on its purpose.", grant=self.display_name),
            },
        }

    def action_view_reports(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Reports: %(grant)s", grant=self.name),
            "res_model": "nonprofit.grant.report",
            "view_mode": "list,form,calendar",
            "domain": [("grant_id", "=", self.id)],
            "context": {"default_grant_id": self.id},
        }
