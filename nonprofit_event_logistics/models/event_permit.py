# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

PERMIT_TYPES = [
    ("alcohol", "Alcohol"),
    ("food_health", "Food / Health"),
    ("street_closure", "Street Closure"),
    ("noise_sound", "Noise / Amplified Sound"),
    ("fire_safety", "Fire / Safety"),
    ("assembly_occupancy", "Assembly / Occupancy"),
    ("parade_route", "Parade Route"),
    ("other", "Other"),
]


class EventPermit(models.Model):
    _name = "event.permit"
    _description = "Event Permit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "submit_by_date, id"

    event_id = fields.Many2one(
        "event.event", string="Event", required=True, ondelete="cascade",
        index=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    permit_type = fields.Selection(
        PERMIT_TYPES, default="other", required=True, tracking=True)
    permit_type_other = fields.Char(string="Type (other)")
    issuing_authority = fields.Char()
    permit_number = fields.Char()
    responsible_id = fields.Many2one(
        "res.users", string="Responsible", tracking=True,
        default=lambda self: self.env.user)

    state = fields.Selection(
        selection=[
            ("not_started", "Not Started"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("denied", "Denied"),
        ],
        default="not_started", required=True, tracking=True, copy=False)
    submit_by_date = fields.Date(
        string="Submit By", help="Application deadline.")
    submitted_date = fields.Date(readonly=True, copy=False)
    approval_date = fields.Date(readonly=True, copy=False)
    expiry_date = fields.Date(
        help="Leave empty if this permit doesn't expire/renew separately "
             "from the event itself.")
    notes = fields.Text()

    template_id = fields.Many2one(
        "event.type.permit.template", string="From Template", readonly=True,
        ondelete="set null", copy=False)

    def action_submit(self):
        for permit in self:
            if permit.state != "not_started":
                raise UserError(_(
                    "Only a not-started permit can be marked submitted."))
        self.write({
            "state": "submitted", "submitted_date": fields.Date.context_today(self),
        })

    def action_approve(self):
        for permit in self:
            if permit.state != "submitted":
                raise UserError(_(
                    "Only a submitted permit can be approved."))
        self.write({
            "state": "approved", "approval_date": fields.Date.context_today(self),
        })

    def action_deny(self):
        for permit in self:
            if permit.state not in ("submitted", "not_started"):
                raise UserError(_(
                    "A denied permit must have been not-started or "
                    "submitted."))
        self.write({"state": "denied"})

    def action_reset_to_not_started(self):
        self.write({
            "state": "not_started", "submitted_date": False,
            "approval_date": False,
        })

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------
    @api.model
    def _reminder_days(self):
        param = self.env["ir.config_parameter"].sudo().get_param(
            "nonprofit_event_logistics.permit_reminder_days", "10")
        try:
            return max(int(param), 0)
        except (TypeError, ValueError):
            return 10

    @api.model
    def _cron_flag_permit_deadlines(self):
        today = fields.Date.context_today(self)
        warn = today + relativedelta(days=self._reminder_days())

        due_soon = self.search([
            ("state", "=", "not_started"),
            ("submit_by_date", "!=", False),
            ("submit_by_date", "<=", warn),
        ])
        for permit in due_soon:
            permit._flag_once(
                "Permit due soon",
                _("%(name)s (%(event)s) must be submitted by %(date)s and "
                  "hasn't been started.",
                  name=permit.name, event=permit.event_id.name,
                  date=permit.submit_by_date))

        expiring = self.search([
            ("state", "=", "approved"),
            ("expiry_date", "!=", False),
            ("expiry_date", "<=", warn),
        ])
        for permit in expiring:
            permit._flag_once(
                "Permit expiring soon",
                _("%(name)s (%(event)s) expires on %(date)s - start the "
                  "renewal.",
                  name=permit.name, event=permit.event_id.name,
                  date=permit.expiry_date))

    # ------------------------------------------------------------------
    # Generate from the event type's checklist
    # ------------------------------------------------------------------
    @api.model
    def _generate_permits_for_event(self, event):
        """Materialise this event's type's permit checklist. Idempotent -
        skips a template that already produced a permit for this event."""
        templates = event.event_type_id.permit_template_ids
        if not templates:
            return self.browse()
        existing_template_ids = set(self.search([
            ("event_id", "=", event.id), ("template_id", "!=", False),
        ]).template_id.ids)
        created = self.browse()
        for template in templates:
            if template.id in existing_template_ids:
                continue
            submit_by = False
            if event.date_begin:
                submit_by = fields.Date.to_date(event.date_begin) - \
                    relativedelta(days=template.days_before_start)
            created |= self.create({
                "event_id": event.id,
                "template_id": template.id,
                "name": template.name,
                "permit_type": template.permit_type,
                "submit_by_date": submit_by,
            })
        return created

    def _flag_once(self, prefix, note):
        self.ensure_one()
        already = self.activity_ids.filtered(
            lambda a: (a.summary or "").startswith(prefix))
        if already:
            return
        self.activity_schedule(
            "mail.mail_activity_data_todo",
            summary=prefix,
            note=note,
            user_id=(self.responsible_id.id or self.env.uid),
        )
