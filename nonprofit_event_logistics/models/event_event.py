# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

_READY_CREW_STATES = ("confirmed", "on_site", "complete")
_OPEN_PERMIT_STATES = ("not_started", "submitted", "denied")


class EventEvent(models.Model):
    _inherit = "event.event"

    logistics_coordinator_id = fields.Many2one(
        "res.users", string="Logistics Coordinator",
        help="Gets one consolidated To-Do when the readiness check finds "
             "open items as the event approaches.")

    permit_ids = fields.One2many("event.permit", "event_id", string="Permits")
    permit_count = fields.Integer(compute="_compute_logistics_counts")
    permit_approved_count = fields.Integer(compute="_compute_logistics_counts")

    staff_shift_ids = fields.One2many(
        "event.staff.shift", "event_id", string="Paid Staff Shifts")
    staff_shift_count = fields.Integer(compute="_compute_logistics_counts")
    staffing_fill_pct = fields.Float(compute="_compute_logistics_counts")

    crew_booking_ids = fields.One2many(
        "event.crew.booking", "event_id", string="Crew Bookings")
    crew_booking_count = fields.Integer(compute="_compute_logistics_counts")
    crew_confirmed_count = fields.Integer(compute="_compute_logistics_counts")

    facility_ids = fields.One2many(
        "event.facility", "event_id", string="Facilities")
    facility_count = fields.Integer(compute="_compute_logistics_counts")

    @api.depends(
        "permit_ids.state", "staff_shift_ids.headcount_needed",
        "staff_shift_ids.filled_count", "crew_booking_ids.state",
        "facility_ids")
    def _compute_logistics_counts(self):
        for event in self:
            event.permit_count = len(event.permit_ids)
            event.permit_approved_count = len(
                event.permit_ids.filtered(lambda p: p.state == "approved"))

            event.staff_shift_count = len(event.staff_shift_ids)
            needed = sum(event.staff_shift_ids.mapped("headcount_needed"))
            filled = sum(event.staff_shift_ids.mapped("filled_count"))
            # Stored as a 0-1 fraction (not 0-100) - the "percentage" widget
            # multiplies by 100 itself when displaying it.
            event.staffing_fill_pct = (
                1.0 if not needed else min(filled / needed, 1.0))

            event.crew_booking_count = len(event.crew_booking_ids)
            event.crew_confirmed_count = len(
                event.crew_booking_ids.filtered(
                    lambda c: c.state in _READY_CREW_STATES))

            event.facility_count = len(event.facility_ids)

    def action_generate_permits_from_type(self):
        self.ensure_one()
        created = self.env["event.permit"]._generate_permits_for_event(self)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Permits generated"),
                "message": _(
                    "%(count)s permit(s) added from %(type)s's checklist.",
                    count=len(created),
                    type=self.event_type_id.name or _("this event's type")),
                "type": "success",
            },
        }

    def action_view_logistics_permits(self):
        return self._logistics_action(
            "nonprofit_event_logistics.action_event_permit")

    def action_view_logistics_staff_shifts(self):
        return self._logistics_action(
            "nonprofit_event_logistics.action_event_staff_shift")

    def action_view_logistics_crew_bookings(self):
        return self._logistics_action(
            "nonprofit_event_logistics.action_event_crew_booking")

    def action_view_logistics_facilities(self):
        return self._logistics_action(
            "nonprofit_event_logistics.action_event_facility")

    def _logistics_action(self, xml_id):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
        action["domain"] = [("event_id", "=", self.id)]
        action["context"] = {"default_event_id": self.id}
        return action

    # ------------------------------------------------------------------
    # Readiness cron
    # ------------------------------------------------------------------
    @api.model
    def _readiness_horizon_days(self):
        param = self.env["ir.config_parameter"].sudo().get_param(
            "nonprofit_event_logistics.readiness_horizon_days", "14")
        try:
            return max(int(param), 0)
        except (TypeError, ValueError):
            return 14

    @api.model
    def _cron_event_readiness_check(self):
        now = fields.Datetime.now()
        horizon = now + relativedelta(days=self._readiness_horizon_days())
        events = self.search([
            ("date_begin", ">=", now), ("date_begin", "<=", horizon),
        ])
        for event in events:
            event._flag_readiness_issues()

    def _flag_readiness_issues(self):
        self.ensure_one()
        open_permits = self.permit_ids.filtered(
            lambda p: p.state in _OPEN_PERMIT_STATES)
        under_shifts = self.staff_shift_ids.filtered(
            lambda s: s.fill_state in ("empty", "partial"))
        open_crews = self.crew_booking_ids.filtered(
            lambda c: c.state not in _READY_CREW_STATES)
        if not (open_permits or under_shifts or open_crews):
            return

        prefix = "Logistics check"
        already = self.activity_ids.filtered(
            lambda a: (a.summary or "").startswith(prefix))
        if already:
            return

        lines = []
        if open_permits:
            lines.append(_(
                "%(n)s permit(s) not yet approved.", n=len(open_permits)))
        if under_shifts:
            lines.append(_(
                "%(n)s staff shift(s) under-filled.", n=len(under_shifts)))
        if open_crews:
            lines.append(_(
                "%(n)s crew booking(s) not yet confirmed.", n=len(open_crews)))

        self.activity_schedule(
            "mail.mail_activity_data_todo",
            summary=_("%(prefix)s: %(event)s", prefix=prefix, event=self.name),
            note="\n".join(str(line) for line in lines),
            user_id=(self.logistics_coordinator_id.id or self.env.uid),
        )
