# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError

from ..models.nonprofit_donor_report import GIFT_TAG_XMLIDS


class NonprofitDonorStatementWizard(models.TransientModel):
    _name = "nonprofit.donor.statement.wizard"
    _description = "Year-End Contribution Statements"

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company)
    date_from = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(
            month=1, day=1))
    date_to = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(
            month=12, day=31))
    partner_ids = fields.Many2many(
        "res.partner", string="Donors",
        help="Leave empty for every donor with a gift in the period.")
    min_amount = fields.Monetary(
        string="Minimum Total", default=250.0,
        help="Skip donors whose total giving in the period is below this.")
    currency_id = fields.Many2one(related="company_id.currency_id")

    def _gift_account_ids(self):
        tags = self.env["account.account.tag"]
        for xmlid in GIFT_TAG_XMLIDS:
            tag = self.env.ref(xmlid, raise_if_not_found=False)
            if tag:
                tags |= tag
        return self.env["account.account"].search([
            ("tag_ids", "in", tags.ids),
            ("company_ids", "in", self.company_id.id),
        ])

    def _candidate_partners(self):
        if self.partner_ids:
            return self.partner_ids
        groups = self.env["account.move.line"]._read_group(
            domain=self._gift_domain(),
            groupby=["partner_id"],
        )
        return self.env["res.partner"].browse([g[0].id for g in groups if g[0]])

    def _gift_domain(self, partner=None):
        domain = [
            ("parent_state", "=", "posted"),
            ("company_id", "=", self.company_id.id),
            ("account_id", "in", self._gift_account_ids().ids),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
        ]
        if partner is not None:
            domain.append(("partner_id", "=", partner.id))
        return domain

    def action_print(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise UserError(_("The start date is after the end date."))
        partners = self._candidate_partners()
        keep = self.env["res.partner"]
        for partner in partners:
            lines = self.env["account.move.line"].search(
                self._gift_domain(partner))
            if sum(-l.balance for l in lines) >= self.min_amount:
                keep |= partner
        if not keep:
            raise UserError(_(
                "No donor reached the %(min)s minimum in gifts between "
                "%(start)s and %(end)s.",
                min=self.min_amount, start=self.date_from, end=self.date_to))
        data = {
            "wizard_id": self.id,
            "company_id": self.company_id.id,
            "date_from": fields.Date.to_string(self.date_from),
            "date_to": fields.Date.to_string(self.date_to),
        }
        return self.env.ref(
            "nonprofit_reports.action_report_donor_statement"
        ).report_action(keep, data=data, config=False)


class ReportDonorStatement(models.AbstractModel):
    _name = "report.nonprofit_reports.donor_statement"
    _description = "Donor Contribution Statement"

    def _get_report_values(self, docids, data=None):
        data = data or {}
        wizard = self.env["nonprofit.donor.statement.wizard"].browse(
            data.get("wizard_id"))
        company = self.env["res.company"].browse(
            data.get("company_id")) or self.env.company
        date_from = fields.Date.to_date(data.get("date_from"))
        date_to = fields.Date.to_date(data.get("date_to"))
        partners = self.env["res.partner"].browse(docids)

        gifts = {}
        totals = {}
        for partner in partners:
            domain = [
                ("parent_state", "=", "posted"),
                ("company_id", "=", company.id),
                ("partner_id", "=", partner.id),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
            ]
            if wizard:
                domain.append(
                    ("account_id", "in", wizard._gift_account_ids().ids))
            lines = self.env["account.move.line"].search(domain, order="date")
            gifts[partner.id] = lines
            totals[partner.id] = sum(-line.balance for line in lines)

        return {
            "doc_ids": docids,
            "doc_model": "res.partner",
            "docs": partners,
            "company": company,
            "date_from": date_from,
            "date_to": date_to,
            "gifts": gifts,
            "totals": totals,
        }
