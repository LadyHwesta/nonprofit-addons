# -*- coding: utf-8 -*-
from odoo import fields, models

from .geo import destination_point


class EventEvent(models.Model):
    _inherit = "event.event"

    row_ids = fields.One2many("event.venue.row", "event_id", string="Rows")
    row_count = fields.Integer(compute="_compute_row_count")

    map_enabled = fields.Boolean(
        string="Vendor Map",
        help="Turn on once the venue has been calibrated below, to show "
             "booths with a row/spot number on the live map.")
    map_origin_lat = fields.Float(
        string="Origin Latitude", digits=(10, 7),
        help="Latitude of Spot 1 on the row with sequence 0 - the anchor "
             "the whole grid is built from. Filled in by the calibration "
             "wizard; only edit by hand if you know the exact coordinate.")
    map_origin_lng = fields.Float(string="Origin Longitude", digits=(10, 7))
    map_spot_bearing_deg = fields.Float(
        string="Spot Bearing (°)", digits=(5, 2),
        help="Compass bearing from one spot to the next spot along a row.")
    map_spot_spacing_m = fields.Float(
        string="Spot Spacing (m)", digits=(6, 2),
        help="Distance between two adjacent spots on the same row, in "
             "meters.")
    map_row_bearing_deg = fields.Float(
        string="Row Bearing (°)", digits=(5, 2),
        help="Compass bearing from one row to the next row.")
    map_row_spacing_m = fields.Float(
        string="Row Spacing (m)", digits=(6, 2),
        help="Distance between two adjacent rows, in meters.")

    def _compute_row_count(self):
        counts = dict(self.env["event.venue.row"]._read_group(
            [("event_id", "in", self.ids)], ["event_id"], ["__count"],
        )) if self.ids else {}
        counts = {event.id: count for event, count in counts.items()}
        for event in self:
            event.row_count = counts.get(event.id, 0)

    def _venue_point(self, row_sequence, spot_number):
        """(lat, lng) for a given row sequence / spot number on this event's
        calibrated grid, or (False, False) if the map isn't calibrated yet.
        """
        self.ensure_one()
        if not self.map_enabled:
            return False, False
        lat, lng = self.map_origin_lat, self.map_origin_lng
        if spot_number and spot_number != 1:
            lat, lng = destination_point(
                lat, lng, self.map_spot_bearing_deg,
                (spot_number - 1) * self.map_spot_spacing_m)
        if row_sequence:
            lat, lng = destination_point(
                lat, lng, self.map_row_bearing_deg,
                row_sequence * self.map_row_spacing_m)
        return lat, lng

    def action_view_venue_rows(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "nonprofit_event_venue.action_event_venue_row")
        action["domain"] = [("event_id", "=", self.id)]
        action["context"] = {"default_event_id": self.id}
        return action

    def action_view_vendor_map(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "nonprofit_event_venue.action_vendor_map")
        action["context"] = {"default_event_id": self.id, "event_id": self.id}
        return action
