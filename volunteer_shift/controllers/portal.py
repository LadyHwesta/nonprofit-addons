# -*- coding: utf-8 -*-
from odoo import fields, http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

_ACTIVE_STATES = ("draft", "confirmed")


class VolunteerShiftPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "volunteer_shift_count" in counters:
            partner = request.env.user.partner_id
            values["volunteer_shift_count"] = request.env[
                "event.volunteer.assignment"].search_count([
                    ("partner_id", "=", partner.id),
                    ("shift_id", "!=", False),
                    ("state", "in", _ACTIVE_STATES),
                    ("shift_stop", ">=", fields.Datetime.now()),
                ])
        return values

    def _my_assignment(self, assignment_id):
        partner = request.env.user.partner_id
        assignment = request.env["event.volunteer.assignment"].sudo().browse(
            assignment_id).exists()
        if not assignment or assignment.partner_id != partner:
            return None
        return assignment

    @http.route(["/my/shifts"], type="http", auth="user", website=True)
    def my_shifts(self, **kw):
        partner = request.env.user.partner_id
        Assignment = request.env["event.volunteer.assignment"].sudo()
        now = fields.Datetime.now()
        base = [("partner_id", "=", partner.id), ("shift_id", "!=", False),
                ("state", "in", _ACTIVE_STATES)]
        upcoming = Assignment.search(
            base + [("shift_stop", ">=", now)], order="shift_start")
        past = Assignment.search(
            base + [("shift_stop", "<", now)], order="shift_start desc", limit=50)
        lifetime_hours = sum(Assignment.search([
            ("partner_id", "=", partner.id), ("hours", ">", 0)]).mapped("hours"))
        open_swaps = request.env["volunteer.shift.swap"].sudo().search([
            ("state", "=", "open"),
            ("offered_by_id", "!=", partner.id),
            ("shift_id.start", ">=", now),
        ])
        values = self._prepare_portal_layout_values()
        values.update({
            "page_name": "volunteer_shifts",
            "upcoming": upcoming,
            "past": past,
            "lifetime_hours": lifetime_hours,
            "open_swaps": open_swaps,
            "now": now,
        })
        return request.render("volunteer_shift.portal_my_shifts", values)

    def _redirect_shifts(self, message=None, ok=True):
        url = "/my/shifts"
        if message:
            from urllib.parse import urlencode
            url += "?" + urlencode(
                {"shift_msg": message, "shift_ok": "1" if ok else "0"})
        return request.redirect(url)

    @http.route(["/my/shift/<int:assignment_id>/checkin"], type="http",
                auth="user", website=True, methods=["POST"])
    def my_shift_checkin(self, assignment_id, **post):
        assignment = self._my_assignment(assignment_id)
        if not assignment:
            return request.not_found()
        if not assignment._portal_can_check():
            return self._redirect_shifts(
                _("That shift isn't open for check-in right now."), ok=False)
        try:
            assignment.action_check_in()
        except UserError as exc:
            return self._redirect_shifts(exc.args[0], ok=False)
        return self._redirect_shifts(_("Checked in. Thanks for being here!"))

    @http.route(["/my/shift/<int:assignment_id>/checkout"], type="http",
                auth="user", website=True, methods=["POST"])
    def my_shift_checkout(self, assignment_id, **post):
        assignment = self._my_assignment(assignment_id)
        if not assignment:
            return request.not_found()
        try:
            assignment.action_check_out()
        except UserError as exc:
            return self._redirect_shifts(exc.args[0], ok=False)
        return self._redirect_shifts(
            _("Checked out - %.2f hours logged.", assignment.hours))

    @http.route(["/my/shift/<int:assignment_id>/offer-swap"], type="http",
                auth="user", website=True, methods=["POST"])
    def my_shift_offer_swap(self, assignment_id, **post):
        assignment = self._my_assignment(assignment_id)
        if not assignment or not assignment.shift_id:
            return request.not_found()
        existing = request.env["volunteer.shift.swap"].sudo().search_count([
            ("assignment_id", "=", assignment.id),
            ("state", "in", ("open", "claimed")),
        ])
        if not existing:
            request.env["volunteer.shift.swap"].sudo().create({
                "assignment_id": assignment.id,
                "note": post.get("note") or False,
            })
        return self._redirect_shifts(_("Your shift is offered for swap."))

    @http.route(["/my/shift/swap/<int:swap_id>/claim"], type="http",
                auth="user", website=True, methods=["POST"])
    def my_shift_claim_swap(self, swap_id, **post):
        partner = request.env.user.partner_id
        swap = request.env["volunteer.shift.swap"].sudo().browse(swap_id).exists()
        if not swap:
            return request.not_found()
        try:
            swap.action_claim(partner)
        except UserError as exc:
            return self._redirect_shifts(exc.args[0], ok=False)
        return self._redirect_shifts(
            _("Claimed - the coordinator will confirm the swap."))
