# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class EventVolunteerRole(models.Model):
    _inherit = "event.volunteer.role"

    requires_background_check = fields.Boolean(
        string="Requires Background Check",
        help="A volunteer must have a current background check to take this "
             "role.")
    requires_waiver = fields.Boolean(
        string="Requires Waiver",
        help="A volunteer must have a current signed liability waiver.")
    required_skill_ids = fields.Many2many(
        "volunteer.skill", "volunteer_profile_role_skill_rel",
        "role_id", "skill_id", string="Required Skills")

    def action_portal_volunteer(self, partner):
        self.ensure_one()
        errors = partner._volunteer_eligibility_errors(self)
        if errors:
            raise UserError(_(
                "The %(role)s role needs %(missing)s.",
                role=self.name, missing="; ".join(errors)))
        return super().action_portal_volunteer(partner)
