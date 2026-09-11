# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_ACTIVE_STATES = ("confirmed",)


class EventStaffAssignment(models.Model):
    _name = "event.staff.assignment"
    _description = "Temporary Staff Assignment"
    _order = "id"

    shift_id = fields.Many2one(
        "event.staff.shift", string="Shift", required=True, ondelete="cascade",
        index=True)
    event_id = fields.Many2one(
        related="shift_id.event_id", store=True, string="Event")
    partner_id = fields.Many2one(
        "res.partner", string="Worker", required=True)
    state = fields.Selection(
        selection=[("confirmed", "Confirmed"), ("no_show", "No-Show")],
        default="confirmed", required=True, copy=False)
    check_in = fields.Datetime(copy=False)
    check_out = fields.Datetime(copy=False)
    hours = fields.Float(
        compute="_compute_hours", store=True, string="Hours Worked")

    @api.depends("check_in", "check_out")
    def _compute_hours(self):
        for rec in self:
            if rec.check_in and rec.check_out and rec.check_out > rec.check_in:
                rec.hours = (
                    rec.check_out - rec.check_in).total_seconds() / 3600.0
            else:
                rec.hours = 0.0

    @api.constrains("shift_id", "partner_id", "state")
    def _check_capacity(self):
        if self.env.context.get("skip_staff_capacity"):
            return
        for rec in self:
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
                    "%(name)s is already assigned to the %(shift)s shift.",
                    name=rec.partner_id.name, shift=rec.shift_id.display_name))
        for shift in self.shift_id:
            if shift.headcount_needed and shift.filled_count > shift.headcount_needed:
                raise ValidationError(_(
                    "The %(shift)s shift only needs %(n)s worker(s). Raise "
                    "the headcount to add more.",
                    shift=shift.display_name, n=shift.headcount_needed))

    def action_check_in(self):
        for rec in self:
            if rec.state != "confirmed":
                raise UserError(_("Only a confirmed worker can check in."))
            rec.write({"check_in": fields.Datetime.now()})
        return True

    def action_check_out(self):
        for rec in self:
            if not rec.check_in:
                raise UserError(_("Check in before checking out."))
            rec.check_out = fields.Datetime.now()
        return True

    def action_mark_no_show(self):
        self.write({"state": "no_show", "check_in": False, "check_out": False})
        return True
