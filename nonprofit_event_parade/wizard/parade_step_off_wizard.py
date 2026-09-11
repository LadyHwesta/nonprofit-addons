# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ParadeStepOffWizard(models.TransientModel):
    _name = "nonprofit.parade.step_off.wizard"
    _description = "Set Parade Step-Off Times"

    event_id = fields.Many2one("event.event", required=True)
    staging_area_id = fields.Many2one(
        "event.parade.staging.area", string="Staging Area only",
        domain="[('event_id', '=', event_id)]",
        help="Leave empty to walk every confirmed entry for the event, "
             "ordered by staging area then lineup order.")
    start_time = fields.Datetime(required=True)
    gap_minutes = fields.Integer(
        string="Gap Between Entries (minutes)", default=3, required=True)

    @api.constrains("gap_minutes")
    def _check_gap_minutes(self):
        for wizard in self:
            if wizard.gap_minutes <= 0:
                raise UserError(_("The gap between entries must be positive."))

    def action_apply(self):
        self.ensure_one()
        domain = [("event_id", "=", self.event_id.id), ("state", "=", "confirmed")]
        if self.staging_area_id:
            domain.append(("staging_area_id", "=", self.staging_area_id.id))
        entries = self.env["event.parade.entry"].search(
            domain, order="staging_area_id, sequence, id")
        if not entries:
            raise UserError(_(
                "No confirmed entries to schedule - confirm entries for "
                "the lineup first."))

        current = self.start_time
        for entry in entries:
            entry.step_off_time = current
            current = current + timedelta(minutes=self.gap_minutes)
        return {"type": "ir.actions.act_window_close"}
