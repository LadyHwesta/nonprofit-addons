# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

_ACTIVITY_PREFIX = "Background check expiring:"


class ResPartner(models.Model):
    _inherit = "res.partner"

    # --- Skills -------------------------------------------------------
    volunteer_skill_ids = fields.Many2many(
        "volunteer.skill", "res_partner_volunteer_skill_rel",
        "partner_id", "skill_id", string="Volunteer Skills")

    # --- Background check -------------------------------------------
    background_check_state = fields.Selection(
        selection=[
            ("none", "Not started"),
            ("requested", "Requested"),
            ("cleared", "Cleared"),
            ("expired", "Expired"),
        ],
        default="none", string="Background Check", tracking=True)
    background_check_date = fields.Date(string="Cleared On", tracking=True)
    background_check_expiry = fields.Date(string="Re-check Due", tracking=True)
    background_check_valid = fields.Boolean(
        compute="_compute_background_check_valid",
        search="_search_background_check_valid", string="Background Check OK")
    background_check_expiring_soon = fields.Boolean(
        compute="_compute_background_check_valid")

    # --- Waiver ----------------------------------------------------
    waiver_signed = fields.Boolean(string="Waiver Signed", tracking=True)
    waiver_date = fields.Date(string="Waiver Date", tracking=True)
    waiver_current = fields.Boolean(
        compute="_compute_waiver_current", search="_search_waiver_current",
        string="Waiver Current")

    # --- Minor / emergency / misc --------------------------------
    is_minor = fields.Boolean(string="Under 18")
    guardian_id = fields.Many2one(
        "res.partner", string="Parent / Guardian",
        domain="[('is_company', '=', False), ('id', '!=', id)]")
    emergency_contact_name = fields.Char()
    emergency_contact_phone = fields.Char()
    tshirt_size = fields.Selection(
        selection=[
            ("xs", "XS"), ("s", "S"), ("m", "M"), ("l", "L"),
            ("xl", "XL"), ("xxl", "2XL"), ("xxxl", "3XL"),
        ],
        string="T-Shirt Size")
    volunteer_orientation_done = fields.Boolean(string="Orientation Done")
    volunteer_orientation_date = fields.Date(string="Orientation Date")

    # ------------------------------------------------------------------
    @api.model
    def _bgcheck_validity_months(self):
        return self._config_int("volunteer_profile.bgcheck_validity_months", 24)

    @api.model
    def _bgcheck_warn_days(self):
        return self._config_int("volunteer_profile.bgcheck_warn_days", 45)

    @api.model
    def _waiver_validity_months(self):
        return self._config_int("volunteer_profile.waiver_validity_months", 12)

    @api.model
    def _config_int(self, key, default):
        param = self.env["ir.config_parameter"].sudo().get_param(
            key, str(default))
        try:
            return max(int(param), 0)
        except (TypeError, ValueError):
            return default

    @api.depends("background_check_state", "background_check_expiry")
    def _compute_background_check_valid(self):
        today = fields.Date.context_today(self)
        warn = today + relativedelta(days=self._bgcheck_warn_days())
        for partner in self:
            not_expired = (
                not partner.background_check_expiry
                or partner.background_check_expiry >= today)
            partner.background_check_valid = bool(
                partner.background_check_state == "cleared" and not_expired)
            partner.background_check_expiring_soon = bool(
                partner.background_check_state == "cleared"
                and partner.background_check_expiry
                and partner.background_check_expiry <= warn)

    def _search_background_check_valid(self, operator, value):
        if operator != "=":
            return NotImplemented
        today = fields.Date.context_today(self)
        domain = [
            ("background_check_state", "=", "cleared"),
            "|", ("background_check_expiry", "=", False),
            ("background_check_expiry", ">=", today),
        ]
        return domain if value else ["!", *domain]

    @api.depends("waiver_signed", "waiver_date")
    def _compute_waiver_current(self):
        cutoff = fields.Date.context_today(self) - relativedelta(
            months=self._waiver_validity_months())
        for partner in self:
            partner.waiver_current = bool(
                partner.waiver_signed and partner.waiver_date
                and partner.waiver_date >= cutoff)

    def _search_waiver_current(self, operator, value):
        if operator != "=":
            return NotImplemented
        cutoff = fields.Date.context_today(self) - relativedelta(
            months=self._waiver_validity_months())
        domain = [
            ("waiver_signed", "=", True),
            ("waiver_date", ">=", cutoff),
        ]
        return domain if value else ["!", *domain]

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_request_background_check(self):
        self.write({"background_check_state": "requested"})

    def action_mark_background_cleared(self):
        today = fields.Date.context_today(self)
        self.write({
            "background_check_state": "cleared",
            "background_check_date": today,
            "background_check_expiry": today + relativedelta(
                months=self._bgcheck_validity_months()),
        })

    def action_sign_waiver(self):
        self.write({
            "waiver_signed": True,
            "waiver_date": fields.Date.context_today(self),
        })

    # ------------------------------------------------------------------
    # Eligibility (used by the sign-up guards)
    # ------------------------------------------------------------------
    def _volunteer_eligibility_errors(self, role):
        """Return a list of human-readable reasons ``self`` can't take
        ``role`` (or a shift of it). Empty list = eligible."""
        self.ensure_one()
        errors = []
        if role.requires_background_check and not self.background_check_valid:
            errors.append(_("a current background check"))
        if role.requires_waiver and not self.waiver_current:
            errors.append(_("a signed liability waiver"))
        missing_skills = role.required_skill_ids - self.volunteer_skill_ids
        if missing_skills:
            errors.append(_(
                "these skills: %s", ", ".join(missing_skills.mapped("name"))))
        return errors

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------
    @api.model
    def _cron_flag_background_checks(self):
        today = fields.Date.context_today(self)
        lapsed = self.search([
            ("background_check_state", "=", "cleared"),
            ("background_check_expiry", "<", today),
        ])
        lapsed.write({"background_check_state": "expired"})

        coordinator = self.env.company.volunteer_coordinator_id
        warn = today + relativedelta(days=self._bgcheck_warn_days())
        expiring = self.search([
            ("background_check_state", "=", "cleared"),
            ("background_check_expiry", "!=", False),
            ("background_check_expiry", "<=", warn),
        ])
        for partner in expiring:
            already = partner.activity_ids.filtered(
                lambda a: (a.summary or "").startswith(_ACTIVITY_PREFIX))
            if already:
                continue
            partner.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=partner.background_check_expiry,
                summary=_("%(prefix)s %(date)s", prefix=_ACTIVITY_PREFIX,
                          date=partner.background_check_expiry),
                note=_(
                    "%(name)s's background check expires on %(date)s. "
                    "Start the re-check before it lapses.",
                    name=partner.display_name,
                    date=partner.background_check_expiry),
                user_id=(coordinator.id or self.env.uid),
            )
