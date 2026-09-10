# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ReportVolunteerHoursCertificate(models.AbstractModel):
    _name = "report.volunteer_shift.hours_certificate"
    _description = "Volunteer Hours Certificate"

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        year = int(data.get("year") or fields.Date.today().year)
        partners = self.env["res.partner"].browse(docids)

        rows = {}
        totals = {}
        for partner in partners:
            lines = self.env["report.volunteer.hours"].search([
                ("partner_id", "=", partner.id),
                ("year", "=", year),
            ], order="date")
            rows[partner.id] = lines
            totals[partner.id] = sum(lines.mapped("hours"))

        return {
            "doc_ids": docids,
            "doc_model": "res.partner",
            "docs": partners,
            "year": year,
            "rows": rows,
            "totals": totals,
            "company": self.env.company,
        }
