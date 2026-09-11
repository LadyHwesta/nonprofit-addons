# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventBooth(models.Model):
    _inherit = "event.booth"

    row_id = fields.Many2one(
        "event.venue.row", string="Row", index=True,
        domain="[('event_id', '=', event_id)]")
    spot_number = fields.Integer(string="Spot #")
    spot_width = fields.Integer(
        string="Spots Wide", default=1,
        help="How many consecutive spots this booth occupies - 2 for a "
             "double-wide vendor, etc.")
    needs_power = fields.Boolean(string="Needs Power")
    booth_label = fields.Char(compute="_compute_booth_label", store=True)
    spot_range_display = fields.Char(
        compute="_compute_booth_label", store=True,
        help="e.g. \"5\" for a single spot, \"5-6\" for a double-wide.")
    latitude = fields.Float(
        digits=(10, 7), compute="_compute_geo_position", store=True)
    longitude = fields.Float(
        digits=(10, 7), compute="_compute_geo_position", store=True)

    # No DB-level unique(row_id, spot_number) constraint: an Integer column
    # has no "unset" state (0 is a real stored value, not NULL), so two
    # booths in the same row that both haven't been assigned a spot yet
    # would collide at 0 and be rejected. _check_no_spot_overlap below
    # (which explicitly skips spot_number 0) is the real, complete check -
    # it also handles multi-spot overlap, which a plain unique() can't.
    _spot_width_positive = models.Constraint(
        "CHECK (spot_width >= 1)",
        "A booth needs to be at least 1 spot wide.")

    @api.depends("row_id.label", "spot_number", "spot_width")
    def _compute_booth_label(self):
        for booth in self:
            if booth.row_id and booth.spot_number:
                if booth.spot_width and booth.spot_width > 1:
                    last_spot = booth.spot_number + booth.spot_width - 1
                    booth.spot_range_display = "%s-%s" % (
                        booth.spot_number, last_spot)
                else:
                    booth.spot_range_display = str(booth.spot_number)
                booth.booth_label = "%s · Spot %s" % (
                    booth.row_id.label, booth.spot_range_display)
            else:
                booth.booth_label = False
                booth.spot_range_display = False

    @api.constrains("row_id", "spot_number", "spot_width")
    def _check_no_spot_overlap(self):
        for booth in self:
            if not (booth.row_id and booth.spot_number):
                continue
            first = booth.spot_number
            last = booth.spot_number + (booth.spot_width or 1) - 1
            others = self.search([
                ("id", "!=", booth.id), ("row_id", "=", booth.row_id.id),
                ("spot_number", "!=", False),
            ])
            for other in others:
                other_first = other.spot_number
                other_last = other.spot_number + (other.spot_width or 1) - 1
                if first <= other_last and other_first <= last:
                    raise ValidationError(_(
                        "%(booth)s (spot %(range)s) overlaps with "
                        "%(other)s (spot %(other_range)s) on %(row)s.",
                        booth=booth.name, range=booth.spot_range_display,
                        other=other.name, other_range=other.spot_range_display,
                        row=booth.row_id.label))

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
