# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_funder = fields.Boolean(string="Funder", help="Gives grants (a foundation, agency or company).")
    grant_ids = fields.One2many("nonprofit.grant", "funder_id", string="Grants")
    grant_count = fields.Integer(compute="_compute_grant_count")

    @api.depends("grant_ids")
    def _compute_grant_count(self):
        for partner in self:
            partner.grant_count = len(partner.grant_ids)

    def action_view_grants(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Grants from %(funder)s", funder=self.name),
            "res_model": "nonprofit.grant",
            "view_mode": "kanban,list,form",
            "domain": [("funder_id", "=", self.id)],
            "context": {"default_funder_id": self.id},
        }
