# -*- coding: utf-8 -*-
from odoo import api, fields, models

_ACTIVE_STATES = ("confirmed",)


class EventStaffShift(models.Model):
    _name = "event.staff.shift"
    _description = "Temporary Staff Shift"
    _order = "start, id"

    name = fields.Char(
        compute="_compute_name", store=True, readonly=False,
        help="Defaults to the role name; override for e.g. \"Security - "
             "Overnight\".")
    event_id = fields.Many2one(
        "event.event", string="Event", required=True, ondelete="cascade",
        index=True)
    role_id = fields.Many2one(
        "event.staff.role", string="Role", required=True, ondelete="restrict")
    start = fields.Datetime(required=True)
    stop = fields.Datetime(required=True)
    headcount_needed = fields.Integer(default=1)
    hourly_rate = fields.Float(
        help="Informational - there's no payroll app in Community edition. "
             "Use this to keep the rate on record for whoever runs payroll.")
    assignment_ids = fields.One2many(
        "event.staff.assignment", "shift_id", string="Assignments", copy=False)

    duration_hours = fields.Float(compute="_compute_duration_hours", store=True)
    filled_count = fields.Integer(compute="_compute_counts", store=True)
    seats_available = fields.Integer(compute="_compute_counts", store=True)
    fill_state = fields.Selection(
        selection=[
            ("empty", "Nobody yet"),
            ("partial", "Partly filled"),
            ("full", "Full"),
            ("over", "Over-filled"),
        ],
        compute="_compute_counts", store=True, string="Coverage")

    _stop_after_start = models.Constraint(
        "CHECK (stop > start)", "A shift must end after it starts.")
    _headcount_not_negative = models.Constraint(
        "CHECK (headcount_needed >= 0)",
        "A shift can't need a negative number of people.")

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

    @api.depends("headcount_needed", "assignment_ids.state")
    def _compute_counts(self):
        for shift in self:
            active = shift.assignment_ids.filtered(
                lambda a: a.state in _ACTIVE_STATES)
            shift.filled_count = len(active)
            shift.seats_available = max(
                shift.headcount_needed - shift.filled_count, 0)
            if not shift.filled_count:
                shift.fill_state = "empty"
            elif shift.filled_count < shift.headcount_needed:
                shift.fill_state = "partial"
            elif shift.filled_count == shift.headcount_needed:
                shift.fill_state = "full"
            else:
                shift.fill_state = "over"
