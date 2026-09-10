# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    nonprofit_fund_required = fields.Boolean(
        related="company_id.nonprofit_fund_required", readonly=False)
    nonprofit_default_program_id = fields.Many2one(
        related="company_id.nonprofit_default_program_id", readonly=False)
    nonprofit_default_function_id = fields.Many2one(
        related="company_id.nonprofit_default_function_id", readonly=False)
    nonprofit_release_restricted_account_id = fields.Many2one(
        related="company_id.nonprofit_release_restricted_account_id", readonly=False)
    nonprofit_release_unrestricted_account_id = fields.Many2one(
        related="company_id.nonprofit_release_unrestricted_account_id", readonly=False)

    def action_nonprofit_detect_release_accounts(self):
        self.company_id._nonprofit_autodetect_release_accounts()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
