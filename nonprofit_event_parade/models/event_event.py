# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class EventEvent(models.Model):
    _inherit = "event.event"

    parade_enabled = fields.Boolean(
        string="Accepting Parade Entries",
        help="Turn on to open the public parade-application page for this "
             "event.")
    parade_entry_deadline = fields.Datetime(
        help="Optional cutoff - after this, the public application page "
             "shows a closed message instead of the form.")
    parade_coordinator_id = fields.Many2one(
        "res.users", string="Parade Coordinator",
        help="Gets a To-Do for every new parade application. Defaults to "
             "whoever reviews it if left empty.")
    parade_entry_ids = fields.One2many(
        "event.parade.entry", "event_id", string="Parade Entries")
    parade_entry_count = fields.Integer(compute="_compute_parade_entry_count")
    parade_staging_area_ids = fields.One2many(
        "event.parade.staging.area", "event_id", string="Staging Areas")

    def _compute_parade_entry_count(self):
        counts = dict(self.env["event.parade.entry"]._read_group(
            [("event_id", "in", self.ids)], ["event_id"], ["__count"],
        )) if self.ids else {}
        counts = {event.id: count for event, count in counts.items()}
        for event in self:
            event.parade_entry_count = counts.get(event.id, 0)

    def action_view_parade_entries(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "nonprofit_event_parade.action_event_parade_entry")
        action["domain"] = [("event_id", "=", self.id)]
        action["context"] = {"default_event_id": self.id}
        return action

    def action_view_parade_staging_areas(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "nonprofit_event_parade.action_event_parade_staging_area")
        action["domain"] = [("event_id", "=", self.id)]
        action["context"] = {"default_event_id": self.id}
        return action

    def action_auto_number_entries(self):
        self.ensure_one()
        entries = self.parade_entry_ids.filtered(
            lambda e: e.state == "confirmed"
        ).sorted(key=lambda e: (e.staging_area_id.sequence, e.sequence, e.id))
        if not entries:
            raise UserError(_(
                "No confirmed entries to number yet - confirm entries for "
                "the lineup first."))
        for number, entry in enumerate(entries, start=1):
            entry.entry_number = number
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Entry numbers assigned"),
                "message": _(
                    "%(count)s confirmed entries numbered 1-%(count)s.",
                    count=len(entries)),
                "type": "success",
            },
        }

    def action_print_entry_signs(self):
        self.ensure_one()
        entries = self.parade_entry_ids.filtered(
            lambda e: e.state == "confirmed")
        if not entries:
            raise UserError(_("No confirmed entries to print signs for yet."))
        return self.env.ref(
            "nonprofit_event_parade.action_report_parade_entry_sign"
        ).report_action(entries, config=False)
