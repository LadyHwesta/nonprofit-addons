# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..models.geo import bearing_and_distance, destination_point


class VenueMapCalibrate(models.TransientModel):
    _name = "nonprofit.venue.map.calibrate"
    _description = "Calibrate Venue Map"

    event_id = fields.Many2one("event.event", required=True)

    origin_row_id = fields.Many2one(
        "event.venue.row", string="Reference row", required=True,
        domain="[('event_id', '=', event_id)]",
        help="Spot 1 on this row is the point you'll read the first "
             "coordinate from.")
    origin_lat = fields.Float(
        string="Spot 1 latitude", digits=(10, 7), required=True)
    origin_lng = fields.Float(
        string="Spot 1 longitude", digits=(10, 7), required=True)

    spot_calib_number = fields.Integer(
        string="Second spot #", default=2,
        help="Any other spot number on the same reference row.")
    spot_calib_lat = fields.Float(
        string="That spot's latitude", digits=(10, 7), required=True)
    spot_calib_lng = fields.Float(
        string="That spot's longitude", digits=(10, 7), required=True)

    row_calib_row_id = fields.Many2one(
        "event.venue.row", string="Second row", required=True,
        domain="[('event_id', '=', event_id), ('id', '!=', origin_row_id)]",
        help="A different row. You'll read the coordinate of its Spot 1.")
    row_calib_lat = fields.Float(
        string="Its Spot 1 latitude", digits=(10, 7), required=True)
    row_calib_lng = fields.Float(
        string="Its Spot 1 longitude", digits=(10, 7), required=True)

    @api.constrains("spot_calib_number")
    def _check_spot_calib_number(self):
        for wizard in self:
            if wizard.spot_calib_number == 1:
                raise UserError(_(
                    "The second spot must be a different spot number than "
                    "1 (that's the reference point itself)."))

    def action_apply(self):
        self.ensure_one()
        if self.row_calib_row_id.sequence == self.origin_row_id.sequence:
            raise UserError(_(
                "The reference row and the second row have the same "
                "sequence - give the rows distinct sequence numbers first "
                "so the row axis has something to measure."))

        spot_bearing, spot_dist = bearing_and_distance(
            self.origin_lat, self.origin_lng,
            self.spot_calib_lat, self.spot_calib_lng)
        spot_diff = self.spot_calib_number - 1
        if spot_diff < 0:
            spot_bearing = (spot_bearing + 180) % 360
            spot_diff = -spot_diff
        spot_spacing = spot_dist / spot_diff

        row_bearing, row_dist = bearing_and_distance(
            self.origin_lat, self.origin_lng,
            self.row_calib_lat, self.row_calib_lng)
        row_diff = self.row_calib_row_id.sequence - self.origin_row_id.sequence
        if row_diff < 0:
            row_bearing = (row_bearing + 180) % 360
            row_diff = -row_diff
        row_spacing = row_dist / row_diff

        # The two coordinates we were given are for the reference row's
        # Spot 1, which may not be the row-sequence-0 anchor. Walk back
        # along the freshly-computed row axis to find the true anchor.
        origin_lat, origin_lng = destination_point(
            self.origin_lat, self.origin_lng,
            (row_bearing + 180) % 360,
            self.origin_row_id.sequence * row_spacing)

        self.event_id.write({
            "map_origin_lat": origin_lat,
            "map_origin_lng": origin_lng,
            "map_spot_bearing_deg": spot_bearing,
            "map_spot_spacing_m": spot_spacing,
            "map_row_bearing_deg": row_bearing,
            "map_row_spacing_m": row_spacing,
            "map_enabled": True,
        })
        return {"type": "ir.actions.act_window_close"}
