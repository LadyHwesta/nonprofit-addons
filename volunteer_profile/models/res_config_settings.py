# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    volunteer_coordinator_id = fields.Many2one(
        related="company_id.volunteer_coordinator_id", readonly=False)
    volunteer_bgcheck_validity_months = fields.Integer(
        string="Background check valid for (months)",
        config_parameter="volunteer_profile.bgcheck_validity_months", default=24)
    volunteer_bgcheck_warn_days = fields.Integer(
        string="Background check warning window (days)",
        config_parameter="volunteer_profile.bgcheck_warn_days", default=45)
    volunteer_waiver_validity_months = fields.Integer(
        string="Waiver valid for (months)",
        config_parameter="volunteer_profile.waiver_validity_months", default=12)
