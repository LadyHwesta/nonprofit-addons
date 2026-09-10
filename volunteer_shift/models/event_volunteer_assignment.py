# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_ACTIVE_STATES = ("draft", "confirmed")


class EventVolunteerAssignment(models.Model):
    _inherit = "event.volunteer.assignment"

    shift_id = fields.Many2one(
        "volunteer.shift", string="Shift", ondelete="cascade", index=True)
    shift_start = fields.Datetime(
        related="shift_id.start", store=True, string="Shift Start")
    shift_stop = fields.Datetime(related="shift_id.stop", store=True)
    check_in = fields.Datetime(copy=False)
    check_out = fields.Datetime(copy=False)
    hours = fields.Float(
        compute="_compute_hours", store=True, string="Hours Served",
        help="Actual time between check-in and check-out.")
    no_show = fields.Boolean(
        copy=False,
        help="Volunteer did not turn up. Excluded from hours reporting.")

    @api.depends("check_in", "check_out")
    def _compute_hours(self):
        for rec in self:
            if rec.check_in and rec.check_out and rec.check_out > rec.check_in:
                rec.hours = (
                    rec.check_out - rec.check_in).total_seconds() / 3600.0
            else:
                rec.hours = 0.0

    @api.constrains("role_id", "partner_id", "state", "shift_id")
    def _check_assignment(self):
        if self.env.context.get("skip_volunteer_capacity"):
            return
        shift_based = self.filtered("shift_id")
        whole_event = self - shift_based
        if whole_event:
            super(EventVolunteerAssignment, whole_event)._check_assignment()

        for rec in shift_based:
            if rec.state not in _ACTIVE_STATES:
                continue
            dup = self.search_count([
                ("id", "!=", rec.id),
                ("shift_id", "=", rec.shift_id.id),
                ("partner_id", "=", rec.partner_id.id),
                ("state", "in", _ACTIVE_STATES),
            ])
            if dup:
                raise ValidationError(_(
                    "%(name)s is already on the %(shift)s shift.",
                    name=rec.partner_id.name, shift=rec.shift_id.display_name))
        for shift in shift_based.shift_id:
            if shift.slot_count and shift.filled_count > shift.slot_count:
                raise ValidationError(_(
                    "The %(shift)s shift only needs %(n)s volunteer(s). "
                    "Raise its slot count to add more.",
                    shift=shift.display_name, n=shift.slot_count))

    # ------------------------------------------------------------------
    # Check-in / out
    # ------------------------------------------------------------------
    def action_check_in(self):
        for rec in self:
            if rec.state != "confirmed":
                raise UserError(_(
                    "Only a confirmed volunteer can check in."))
            rec.write({"check_in": fields.Datetime.now(), "no_show": False})
        return True

    def action_check_out(self):
        for rec in self:
            if not rec.check_in:
                raise UserError(_("Check in before checking out."))
            rec.check_out = fields.Datetime.now()
        return True

    def action_mark_no_show(self):
        self.write({"no_show": True, "check_in": False, "check_out": False})
        return True

    # ------------------------------------------------------------------
    # Portal self check-in / out
    # ------------------------------------------------------------------
    def _portal_can_check(self):
        """A volunteer may self check-in/out from when the shift is within
        the grace window of starting, until it ends."""
        self.ensure_one()
        if not self.shift_id:
            return False
        now = fields.Datetime.now()
        grace = self.shift_id._checkin_grace()
        opens = self.shift_id.start - timedelta(minutes=grace)
        return opens <= now <= self.shift_id.stop
