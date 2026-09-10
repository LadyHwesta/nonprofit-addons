# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError

_ACTIVE_STATES = ("draft", "confirmed")


class VolunteerShift(models.Model):
    _inherit = "volunteer.shift"

    requires_background_check = fields.Boolean(
        related="role_id.requires_background_check", readonly=True)
    requires_waiver = fields.Boolean(
        related="role_id.requires_waiver", readonly=True)
    required_skill_ids = fields.Many2many(
        related="role_id.required_skill_ids", readonly=True,
        string="Required Skills")

    def action_portal_signup(self, partner):
        self.ensure_one()
        errors = partner._volunteer_eligibility_errors(self.role_id)
        if errors:
            raise UserError(_(
                "The %(shift)s shift needs %(missing)s.",
                shift=self.display_name, missing="; ".join(errors)))
        return super().action_portal_signup(partner)

    def _overlapping_busy_partners(self):
        self.ensure_one()
        overlaps = self.env["volunteer.shift"].search([
            ("id", "!=", self.id),
            ("start", "<", self.stop),
            ("stop", ">", self.start),
        ])
        return self.env["event.volunteer.assignment"].search([
            ("shift_id", "in", overlaps.ids),
            ("state", "in", _ACTIVE_STATES),
        ]).partner_id

    def action_suggest_volunteers(self):
        self.ensure_one()
        role = self.role_id
        domain = [("is_company", "=", False)]
        if role.required_skill_ids:
            domain.append(
                ("volunteer_skill_ids", "in", role.required_skill_ids.ids))
        candidates = self.env["res.partner"].search(domain)
        busy = self._overlapping_busy_partners()
        already = self.assignment_ids.filtered(
            lambda a: a.state in _ACTIVE_STATES).partner_id
        eligible = candidates.filtered(
            lambda p: p not in busy and p not in already
            and not p._volunteer_eligibility_errors(role))
        return {
            "type": "ir.actions.act_window",
            "name": _("Suggested Volunteers - %s", self.display_name),
            "res_model": "res.partner",
            "view_mode": "list,form",
            "domain": [("id", "in", eligible.ids)],
            "context": {"default_is_company": False},
        }
