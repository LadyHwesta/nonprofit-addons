# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class VolunteerShiftSwap(models.Model):
    _name = "volunteer.shift.swap"
    _description = "Volunteer Shift Swap Request"
    _inherit = ["mail.thread"]
    _order = "create_date desc, id desc"

    assignment_id = fields.Many2one(
        "event.volunteer.assignment", string="Shift Assignment", required=True,
        ondelete="cascade")
    shift_id = fields.Many2one(
        related="assignment_id.shift_id", store=True, string="Shift")
    event_id = fields.Many2one(related="shift_id.event_id", store=True)
    offered_by_id = fields.Many2one(
        related="assignment_id.partner_id", store=True, string="Offered By")
    claimed_by_id = fields.Many2one(
        "res.partner", string="Claimed By", tracking=True)
    state = fields.Selection(
        selection=[
            ("open", "Open"),
            ("claimed", "Claimed"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="open", required=True, tracking=True)
    note = fields.Char()

    @api.constrains("assignment_id")
    def _check_assignment_is_shift(self):
        for swap in self:
            if not swap.assignment_id.shift_id:
                raise UserError(_(
                    "Shift swaps only apply to shift-based assignments."))

    def action_claim(self, partner):
        self.ensure_one()
        if self.state not in ("open", "claimed"):
            raise UserError(_("This swap is no longer open."))
        if partner == self.offered_by_id:
            raise UserError(_("You can't claim your own shift."))
        clash = self.env["event.volunteer.assignment"].search_count([
            ("shift_id", "=", self.shift_id.id),
            ("partner_id", "=", partner.id),
            ("state", "in", ("draft", "confirmed")),
        ])
        if clash:
            raise UserError(_("You're already on this shift."))
        self.write({"claimed_by_id": partner.id, "state": "claimed"})
        return True

    def action_approve(self):
        for swap in self:
            if swap.state != "claimed" or not swap.claimed_by_id:
                raise UserError(_("Nobody has claimed this swap yet."))
            swap.assignment_id.with_context(
                skip_volunteer_capacity=True).write(
                {"partner_id": swap.claimed_by_id.id,
                 "check_in": False, "check_out": False, "no_show": False})
            swap.state = "approved"
            swap.assignment_id.message_post(body=_(
                "Shift handed over from %(giver)s to %(taker)s.",
                giver=swap.offered_by_id.display_name,
                taker=swap.claimed_by_id.display_name))
        return True

    def action_reject(self):
        self.write({"state": "rejected"})
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True
