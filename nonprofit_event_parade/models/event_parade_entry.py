# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class EventParadeEntry(models.Model):
    _name = "event.parade.entry"
    _description = "Parade Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, id"

    event_id = fields.Many2one(
        "event.event", string="Event", required=True, ondelete="cascade",
        index=True, tracking=True)
    name = fields.Char(
        string="Unit / Contingent Name", required=True, tracking=True)
    org_name = fields.Char(string="Organization")
    partner_id = fields.Many2one("res.partner", string="Contact", tracking=True)
    contact_name = fields.Char(required=True)
    contact_email = fields.Char(required=True)
    contact_phone = fields.Char()

    entry_type = fields.Selection(
        selection=[
            ("float", "Float"),
            ("vehicle", "Vehicle"),
            ("marching_band", "Marching Band"),
            ("walking_group", "Walking Group"),
            ("equestrian", "Equestrian"),
            ("other", "Other"),
        ],
        default="walking_group", required=True, tracking=True)
    participant_count = fields.Integer(string="Participants")
    vehicle_count = fields.Integer(string="Vehicles")
    linear_feet_needed = fields.Float(string="Linear Feet Needed")
    sound_amplification = fields.Boolean(
        string="Sound Amplification",
        help="Needs a sound truck/speakers - flag for marshal coordination.")
    special_requirements = fields.Text()

    waiver_accepted = fields.Boolean(string="Liability Waiver Accepted", copy=False)
    waiver_accepted_date = fields.Datetime(readonly=True, copy=False)

    state = fields.Selection(
        selection=[
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("confirmed", "Confirmed for Lineup"),
            ("rejected", "Rejected"),
            ("withdrawn", "Withdrawn"),
        ],
        default="submitted", required=True, tracking=True, copy=False)
    rejection_reason = fields.Text()

    staging_area_id = fields.Many2one(
        "event.parade.staging.area", string="Staging Area", tracking=True,
        domain="[('event_id', '=', event_id)]")
    sequence = fields.Integer(
        default=10, help="Lineup / marching order.")
    entry_number = fields.Integer(
        string="Entry #", copy=False,
        help="The number printed on this entry's sign and used in the "
             "printed entry lists - a stable identifier, separate from "
             "lineup order (which can still be rearranged during staging).")
    step_off_time = fields.Datetime(copy=False)
    notes = fields.Text(string="Internal Notes")

    @api.constrains("event_id", "entry_number")
    def _check_entry_number_unique(self):
        # entry_number is 0 (not NULL) until assigned - an Integer column
        # has no "unset" state - so a plain SQL unique constraint would
        # reject the second unnumbered entry for an event. Skip zero here
        # and only enforce uniqueness once a real number is assigned.
        for entry in self:
            if not entry.entry_number:
                continue
            dup = self.search_count([
                ("id", "!=", entry.id),
                ("event_id", "=", entry.event_id.id),
                ("entry_number", "=", entry.entry_number),
            ])
            if dup:
                raise ValidationError(_(
                    "Entry #%(number)s is already used by another entry "
                    "for this event.", number=entry.entry_number))

    @api.model_create_multi
    def create(self, vals_list):
        entries = super().create(vals_list)
        entries._notify_coordinator()
        return entries

    def _notify_coordinator(self):
        for entry in self:
            coordinator = entry.event_id.parade_coordinator_id
            entry.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=_("New parade entry: %s", entry.name),
                note=_(
                    "%(org)s submitted a parade entry (%(type)s, %(count)s "
                    "participants) for %(event)s. Review and approve or "
                    "reject it.",
                    org=entry.org_name or entry.contact_name,
                    type=dict(entry._fields["entry_type"].selection).get(
                        entry.entry_type),
                    count=entry.participant_count,
                    event=entry.event_id.name),
                user_id=(coordinator.id or self.env.uid),
            )

    def action_approve(self):
        for entry in self:
            if entry.state != "submitted":
                raise UserError(_("Only a submitted entry can be approved."))
        self.write({"state": "approved"})

    def action_reject(self):
        for entry in self:
            if entry.state not in ("submitted", "approved"):
                raise UserError(_(
                    "Only a submitted or approved entry can be rejected."))
        self.write({"state": "rejected"})

    def action_withdraw(self):
        for entry in self:
            if entry.state in ("rejected", "withdrawn"):
                raise UserError(_("This entry is already closed out."))
        self.write({"state": "withdrawn"})

    def action_confirm(self):
        for entry in self:
            if entry.state != "approved":
                raise UserError(_(
                    "Only an approved entry can be confirmed for lineup."))
            if not entry.staging_area_id:
                raise UserError(_(
                    "Assign a staging area before confirming %s for the "
                    "lineup.", entry.name))
        self.write({"state": "confirmed"})
        self._warn_if_staging_area_over_capacity()

    def _warn_if_staging_area_over_capacity(self):
        """A capacity is a rough guide, not an enforced limit - real
        parades flex. Post a chatter warning instead of blocking."""
        for area in self.mapped("staging_area_id").filtered("capacity"):
            confirmed = self.env["event.parade.entry"].search_count([
                ("staging_area_id", "=", area.id), ("state", "=", "confirmed"),
            ])
            if confirmed > area.capacity:
                area.message_post(body=_(
                    "%(area)s now has %(confirmed)s confirmed entries, "
                    "over its guideline capacity of %(capacity)s.",
                    area=area.name, confirmed=confirmed, capacity=area.capacity))

    def action_reset_to_submitted(self):
        for entry in self:
            if entry.state not in ("approved", "rejected"):
                raise UserError(_(
                    "Only an approved or rejected entry can be reset."))
        self.write({"state": "submitted"})
