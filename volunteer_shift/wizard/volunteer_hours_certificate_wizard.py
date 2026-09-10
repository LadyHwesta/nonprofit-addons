# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class VolunteerHoursCertificateWizard(models.TransientModel):
    _name = "volunteer.hours.certificate.wizard"
    _description = "Volunteer Hours Certificates"

    year = fields.Integer(
        required=True, default=lambda self: fields.Date.today().year)
    partner_ids = fields.Many2many(
        "res.partner", string="Volunteers",
        help="Leave empty for everyone with logged hours that year.")

    def action_print(self):
        self.ensure_one()
        partners = self.partner_ids
        if not partners:
            groups = self.env["report.volunteer.hours"]._read_group(
                domain=[("year", "=", self.year)], groupby=["partner_id"])
            partners = self.env["res.partner"].browse(
                [g[0].id for g in groups if g[0]])
        if not partners:
            raise UserError(_("No volunteer hours logged for %s.", self.year))
        return self.env.ref(
            "volunteer_shift.action_report_volunteer_hours_certificate"
        ).report_action(partners, data={"year": self.year}, config=False)
