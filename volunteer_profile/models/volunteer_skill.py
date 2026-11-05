# -*- coding: utf-8 -*-
from odoo import fields, models


class VolunteerSkill(models.Model):
    _name = "volunteer.skill"
    _description = "Volunteer Skill"
    _order = "category, name"

    name = fields.Char(required=True, translate=True)
    category = fields.Selection(
        selection=[
            ("general", "General"),
            ("medical", "Medical / First Aid"),
            ("trade", "Trade / Hands-on"),
            ("language", "Language"),
            ("driving", "Driving"),
            ("admin", "Administrative"),
            ("other", "Other"),
        ],
        default="general", required=True)
    active = fields.Boolean(default=True)
    partner_count = fields.Integer(compute="_compute_partner_count")

    _name_uniq = models.Constraint(
        "unique(name)", "That skill already exists.")

    def _compute_partner_count(self):
        data = self.env["res.partner"].sudo()._read_group(
            [("volunteer_skill_ids", "in", self.ids)],
            groupby=["volunteer_skill_ids"], aggregates=["__count"])
        counts = {skill.id: n for skill, n in data}
        for skill in self:
            skill.partner_count = counts.get(skill.id, 0)

    def action_view_volunteers(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Volunteers - %s", self.name),
            "res_model": "res.partner",
            "view_mode": "list,form",
            "domain": [("volunteer_skill_ids", "in", self.id)],
        }
