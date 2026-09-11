# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EventBooth(models.Model):
    _inherit = "event.booth"

    row_id = fields.Many2one(
        "event.venue.row", string="Row", index=True,
        domain="[('event_id', '=', event_id)]")
    spot_number = fields.Integer(string="Spot #")
    booth_label = fields.Char(compute="_compute_booth_label", store=True)
    latitude = fields.Float(
        digits=(10, 7), compute="_compute_geo_position", store=True)
    longitude = fields.Float(
        digits=(10, 7), compute="_compute_geo_position", store=True)

    _row_spot_uniq = models.Constraint(
        "unique(row_id, spot_number)",
        "Another booth is already assigned to this row and spot.")

    @api.depends("row_id.label", "spot_number")
    def _compute_booth_label(self):
        for booth in self:
            if booth.row_id and booth.spot_number:
                booth.booth_label = "%s · Spot %s" % (
                    booth.row_id.label, booth.spot_number)
            else:
                booth.booth_label = False

    @api.depends(
        "row_id.sequence", "spot_number",
        "row_id.event_id.map_enabled",
        "row_id.event_id.map_origin_lat", "row_id.event_id.map_origin_lng",
        "row_id.event_id.map_spot_bearing_deg",
        "row_id.event_id.map_spot_spacing_m",
        "row_id.event_id.map_row_bearing_deg",
        "row_id.event_id.map_row_spacing_m")
    def _compute_geo_position(self):
        for booth in self:
            if not (booth.row_id and booth.spot_number):
                booth.latitude = False
                booth.longitude = False
                continue
            lat, lng = booth.row_id.event_id._venue_point(
                booth.row_id.sequence, booth.spot_number)
            booth.latitude = lat if lat is not False else False
            booth.longitude = lng if lng is not False else False
