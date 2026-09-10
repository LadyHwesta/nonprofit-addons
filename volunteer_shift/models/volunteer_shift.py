# -*- coding: utf-8 -*-
from datetime import datetime, time, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# Assignment states that occupy a slot (mirrors event_volunteer).
_ACTIVE_STATES = ("draft", "confirmed")


class VolunteerShift(models.Model):
    _name = "volunteer.shift"
    _description = "Volunteer Shift"
    _order = "start, id"

    name = fields.Char(
        compute="_compute_name", store=True, readonly=False,
        help="Defaults to the role name; override for e.g. 'Setup Crew - "
             "Morning'.")
    role_id = fields.Many2one(
        "event.volunteer.role", string="Role", required=True,
        ondelete="cascade", index=True)
    event_id = fields.Many2one(
        related="role_id.event_id", store=True, index=True, string="Event")
    start = fields.Datetime(required=True)
    stop = fields.Datetime(required=True)
    slot_count = fields.Integer(
        string="Slots Needed", default=1,
        help="How many volunteers this shift needs.")
    assignment_ids = fields.One2many(
        "event.volunteer.assignment", "shift_id", string="Volunteers",
        copy=False)

    template_id = fields.Many2one(
        "volunteer.shift.template", string="From Template", readonly=True,
        ondelete="set null", copy=False)

    duration_hours = fields.Float(
        compute="_compute_duration_hours", store=True, string="Length (h)")
    filled_count = fields.Integer(compute="_compute_counts", store=True)
    confirmed_count = fields.Integer(compute="_compute_counts", store=True)
    seats_available = fields.Integer(compute="_compute_counts", store=True)
    fill_state = fields.Selection(
        selection=[
            ("empty", "Nobody yet"),
            ("partial", "Partly filled"),
            ("full", "Full"),
            ("over", "Over-filled"),
        ],
        compute="_compute_counts", store=True, string="Coverage")
    time_state = fields.Selection(
        selection=[
            ("upcoming", "Upcoming"),
            ("in_progress", "In progress"),
            ("past", "Past"),
        ],
        compute="_compute_time_state", string="When")

    _stop_after_start = models.Constraint(
        "CHECK (stop > start)",
        "A shift must end after it starts.",
    )
    _slot_count_positive = models.Constraint(
        "CHECK (slot_count >= 0)",
        "A shift can't need a negative number of people.",
    )

    @api.depends("role_id.name")
    def _compute_name(self):
        for shift in self:
            if not shift.name:
                shift.name = shift.role_id.name

    @api.depends("start", "stop")
    def _compute_duration_hours(self):
        for shift in self:
            if shift.start and shift.stop:
                shift.duration_hours = (
                    shift.stop - shift.start).total_seconds() / 3600.0
            else:
                shift.duration_hours = 0.0

    @api.depends("slot_count", "assignment_ids.state")
    def _compute_counts(self):
        for shift in self:
            active = shift.assignment_ids.filtered(
                lambda a: a.state in _ACTIVE_STATES)
            shift.filled_count = len(active)
            shift.confirmed_count = len(
                active.filtered(lambda a: a.state == "confirmed"))
            shift.seats_available = max(
                shift.slot_count - shift.filled_count, 0)
            if not shift.filled_count:
                shift.fill_state = "empty"
            elif shift.filled_count < shift.slot_count:
                shift.fill_state = "partial"
            elif shift.filled_count == shift.slot_count:
                shift.fill_state = "full"
            else:
                shift.fill_state = "over"

    @api.depends("start", "stop")
    def _compute_time_state(self):
        now = fields.Datetime.now()
        for shift in self:
            if shift.stop and shift.stop < now:
                shift.time_state = "past"
            elif shift.start and shift.start <= now:
                shift.time_state = "in_progress"
            else:
                shift.time_state = "upcoming"

    def _assignment_for(self, partner):
        self.ensure_one()
        return self.assignment_ids.filtered(
            lambda a: a.partner_id == partner and a.state in _ACTIVE_STATES)[:1]

    def action_portal_signup(self, partner):
        """Sign ``partner`` up for this shift (portal path)."""
        self.ensure_one()
        Assignment = self.env["event.volunteer.assignment"]
        if not partner:
            raise UserError(_("You need to be signed in."))
        if self._assignment_for(partner):
            raise UserError(_(
                "You're already on the %s shift.", self.display_name))
        if self.seats_available <= 0:
            raise UserError(_(
                "The %s shift is already full.", self.display_name))
        return Assignment.create({
            "role_id": self.role_id.id,
            "shift_id": self.id,
            "partner_id": partner.id,
            "state": "confirmed",
            "source": "portal",
        })

    def _checkin_grace(self):
        param = self.env["ir.config_parameter"].sudo().get_param(
            "volunteer_shift.checkin_grace_mins", "15")
        try:
            return max(int(param), 0)
        except (TypeError, ValueError):
            return 15

    # ------------------------------------------------------------------
    # Recurring generation
    # ------------------------------------------------------------------
    @api.model
    def _generation_horizon_weeks(self):
        param = self.env["ir.config_parameter"].sudo().get_param(
            "volunteer_shift.horizon_weeks", "4")
        try:
            return max(int(param), 0)
        except (TypeError, ValueError):
            return 4

    def _role_for_template(self, event, template):
        role = event.volunteer_role_ids.filtered(
            lambda r: r.name == template.name)[:1]
        if not role:
            role = self.env["event.volunteer.role"].create({
                "event_id": event.id,
                "name": template.name,
                "slot_count": template.slot_count,
                "use_shifts": True,
            })
        elif not role.use_shifts:
            role.use_shifts = True
        return role

    @api.model
    def _generate_shifts_for_event(self, event):
        """Materialise this event's type's shift templates. Idempotent."""
        templates = event.event_type_id.volunteer_shift_template_ids
        if not templates or not event.date_begin or not event.date_end:
            return self.browse()
        window_start = max(event.date_begin, fields.Datetime.now())
        created = self.browse()
        for template in templates:
            role = self._role_for_template(event, template)
            day = window_start.date()
            while day <= event.date_end.date():
                if str(day.weekday()) == template.weekday:
                    start = datetime.combine(day, time()) + timedelta(
                        hours=template.start_time)
                    if start >= window_start and start <= event.date_end:
                        stop = start + timedelta(hours=template.duration_hours)
                        exists = self.search_count([
                            ("template_id", "=", template.id),
                            ("start", "=", start),
                            ("role_id", "=", role.id),
                        ])
                        if not exists:
                            created |= self.create({
                                "role_id": role.id,
                                "template_id": template.id,
                                "name": template.name,
                                "start": start,
                                "stop": stop,
                                "slot_count": template.slot_count,
                            })
                day += timedelta(days=1)
        return created

    @api.model
    def _cron_generate_shifts(self):
        now = fields.Datetime.now()
        until = now + timedelta(weeks=self._generation_horizon_weeks())
        events = self.env["event.event"].search([
            ("event_type_id.volunteer_shift_template_ids", "!=", False),
            ("date_end", ">=", now),
            ("date_begin", "<=", until),
        ])
        for event in events:
            self._generate_shifts_for_event(event)
