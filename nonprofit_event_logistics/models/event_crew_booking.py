# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

SERVICE_TYPES = [
    ("stage", "Stage"),
    ("sound", "Sound"),
    ("lighting", "Lighting"),
    ("security", "Security"),
    ("sanitation", "Sanitation"),
    ("generator_power", "Generator / Power"),
    ("tent_rental", "Tent Rental"),
    ("barricade", "Barricades / Fencing"),
    ("waste_removal", "Waste Removal"),
    ("other", "Other"),
]


class EventCrewBooking(models.Model):
    _name = "event.crew.booking"
    _description = "Event Crew / Vendor Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "load_in, id"

    event_id = fields.Many2one(
        "event.event", string="Event", required=True, ondelete="cascade",
        index=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner", string="Vendor / Crew", required=True, tracking=True)
    service_type = fields.Selection(
        SERVICE_TYPES, default="other", required=True, tracking=True)
    service_type_other = fields.Char(string="Service (other)")
    purchase_order_id = fields.Many2one(
        "purchase.order", string="Purchase Order",
        domain="[('partner_id', '=', partner_id)]",
        help="Optional - not every booking runs through a formal PO (e.g. "
             "an in-kind sponsor).")
    load_in = fields.Datetime()
    load_out = fields.Datetime()
    day_of_contact_name = fields.Char()
    day_of_contact_phone = fields.Char()
    state = fields.Selection(
        selection=[
            ("planned", "Planned"),
            ("confirmed", "Confirmed"),
            ("on_site", "On Site"),
            ("complete", "Complete"),
            ("cancelled", "Cancelled"),
        ],
        default="planned", required=True, tracking=True, copy=False)
    notes = fields.Text(help="Equipment list, special instructions, etc.")

    def action_confirm(self):
        for booking in self:
            if booking.state != "planned":
                raise UserError(_("Only a planned booking can be confirmed."))
        self.write({"state": "confirmed"})

    def action_mark_on_site(self):
        for booking in self:
            if booking.state != "confirmed":
                raise UserError(_(
                    "Only a confirmed booking can be marked on-site."))
        self.write({"state": "on_site"})

    def action_mark_complete(self):
        self.write({"state": "complete"})

    def action_cancel(self):
        for booking in self:
            if booking.state == "complete":
                raise UserError(_("A completed booking can't be cancelled."))
        self.write({"state": "cancelled"})
