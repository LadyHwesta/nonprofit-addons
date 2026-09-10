# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # --- Organisation ------------------------------------------------------
    is_nonprofit_org = fields.Boolean(
        string="Is a Non-Profit",
        help="This organisation is a tax-exempt non-profit.")
    nonprofit_org_type = fields.Selection(
        selection=[
            ("501c3", "501(c)(3) - Charitable"),
            ("501c4", "501(c)(4) - Social Welfare"),
            ("501c6", "501(c)(6) - Business League"),
            ("church", "Church / Religious"),
            ("school", "School / Educational"),
            ("government", "Government / Public"),
            ("other", "Other"),
        ],
        string="Non-Profit Type")
    tax_exempt_id = fields.Char(
        string="EIN / Tax-Exempt ID",
        help="Employer Identification Number of the tax-exempt organisation.")

    # --- Donor -----------------------------------------------------------
    donor_type = fields.Selection(
        selection=[
            ("individual", "Individual"),
            ("household", "Household"),
            ("foundation", "Foundation"),
            ("corporation", "Corporation"),
            ("government", "Government"),
            ("other", "Other"),
        ],
        string="Donor Type")

    # --- Contact preferences / consent ----------------------------------
    no_solicit = fields.Boolean(
        string="Do Not Solicit",
        help="Never contact this person for fundraising appeals.")
    no_mail = fields.Boolean(
        string="No Postal Mail",
        help="Exclude from printed mailings (appeals, newsletters, receipts).")
    no_email = fields.Boolean(
        string="No Email",
        help="Exclude from fundraising and newsletter emails.")

    # --- Households ----------------------------------------------------
    household_id = fields.Many2one(
        "res.partner", string="Household",
        domain="[('is_company', '=', False), ('id', '!=', id)]",
        help="Groups individuals who share a household for giving roll-ups "
             "(e.g. spouses credited jointly).")
    household_member_ids = fields.One2many(
        "res.partner", "household_id", string="Household Members")
    household_member_count = fields.Integer(
        compute="_compute_household_member_count")

    @api.depends("household_member_ids")
    def _compute_household_member_count(self):
        for partner in self:
            partner.household_member_count = len(partner.household_member_ids)
