# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import ValidationError

_ACTIVE_STATES = ("draft", "confirmed")


class EventVolunteerAssignment(models.Model):
    _inherit = "event.volunteer.assignment"

    @api.constrains("partner_id", "role_id", "state")
    def _check_volunteer_eligibility(self):
        if self.env.context.get("skip_volunteer_eligibility"):
            return
        for rec in self:
            if rec.state not in _ACTIVE_STATES or not rec.role_id:
                continue
            errors = rec.partner_id._volunteer_eligibility_errors(rec.role_id)
            if errors:
                raise ValidationError(_(
                    "%(name)s can't take %(role)s yet - still needs "
                    "%(missing)s.",
                    name=rec.partner_id.display_name, role=rec.role_id.name,
                    missing="; ".join(errors)))
