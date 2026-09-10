# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    volunteer_coordinator_id = fields.Many2one(
        "res.users", string="Volunteer Coordinator",
        help="Gets the To-Do when a volunteer's background check is about to "
             "expire.")
