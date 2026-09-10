# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    volunteer_shift_default_hours = fields.Float(
        string="Default shift length (h)",
        config_parameter="volunteer_shift.default_hours", default=3.0)
    volunteer_checkin_grace_mins = fields.Integer(
        string="Check-in grace (minutes)",
        config_parameter="volunteer_shift.checkin_grace_mins", default=15,
        help="How long before a shift starts a volunteer may self check in "
             "from the portal.")
    volunteer_shift_horizon_weeks = fields.Integer(
        string="Recurring shift horizon (weeks)",
        config_parameter="volunteer_shift.horizon_weeks", default=4,
        help="How far ahead the nightly job materialises recurring shifts.")
