# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

REPORT_SUMMARY = "Grant report due"


class NonprofitGrantReport(models.Model):
    """A report the funder requires: narrative, financial, or both."""
    _name = "nonprofit.grant.report"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Grant Report"
    _order = "due_date, id"

    grant_id = fields.Many2one("nonprofit.grant", required=True, ondelete="cascade", index=True)
    name = fields.Char(required=True, help='e.g. "Interim report" or "Final financial report".')
    report_type = fields.Selection(
        [("narrative", "Narrative"), ("financial", "Financial"), ("both", "Narrative and financial")],
        string="Type", default="both", required=True)
    due_date = fields.Date(required=True, tracking=True)
    state = fields.Selection(
        [("todo", "To do"), ("submitted", "Submitted")], default="todo", required=True, tracking=True)
    submitted_date = fields.Date(tracking=True)
    attachment_ids = fields.Many2many("ir.attachment", string="Submitted Report")
    note = fields.Text()
    user_id = fields.Many2one(related="grant_id.user_id", string="Owner", store=True)
    funder_id = fields.Many2one(related="grant_id.funder_id", store=True)
    company_id = fields.Many2one(related="grant_id.company_id", store=True)
    is_overdue = fields.Boolean(compute="_compute_is_overdue")

    @api.depends("due_date", "state")
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for report in self:
            report.is_overdue = report.state == "todo" and report.due_date and report.due_date < today

    @api.depends("name", "grant_id")
    def _compute_display_name(self):
        for report in self:
            report.display_name = f"{report.grant_id.name}: {report.name}" if report.grant_id else report.name

    @api.model_create_multi
    def create(self, vals_list):
        reports = super().create(vals_list)
        reports._sync_todo()
        return reports

    def write(self, vals):
        result = super().write(vals)
        if {"due_date", "state", "grant_id"} & set(vals):
            self._sync_todo()
        return result

    def _sync_todo(self):
        """A to-do for the grant's owner on the due date, until submitted."""
        todo = self.env.ref("mail.mail_activity_data_todo")
        for report in self:
            existing = report.activity_ids.filtered(lambda a: a.activity_type_id == todo)
            owner = report.grant_id.user_id
            if report.state != "todo" or not owner:
                existing.unlink()
                continue
            if existing:
                existing.write({"date_deadline": report.due_date, "user_id": owner.id})
            else:
                report.activity_schedule(
                    "mail.mail_activity_data_todo", date_deadline=report.due_date,
                    summary=_(REPORT_SUMMARY), user_id=owner.id,
                    note=_("%(report)s for %(funder)s.", report=report.display_name,
                           funder=report.funder_id.name))

    def action_mark_submitted(self):
        self.write({"state": "submitted", "submitted_date": fields.Date.context_today(self)})
        for report in self:
            report.grant_id.message_post(body=_("%(report)s submitted.", report=report.name))

    def action_reopen(self):
        self.write({"state": "todo", "submitted_date": False})
