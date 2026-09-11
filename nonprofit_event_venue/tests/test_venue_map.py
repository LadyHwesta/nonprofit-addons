# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged

from ..models.geo import destination_point


@tagged("post_install", "-at_install")
class TestVenueMap(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create({
            "name": "Pride 2027",
            "date_begin": datetime.now() + timedelta(days=60),
            "date_end": datetime.now() + timedelta(days=60, hours=8),
        })
        cls.category = cls.env["event.booth.category"].create({
            "name": "Food Vendor",
        })
        cls.row_a = cls.env["event.venue.row"].create({
            "event_id": cls.event.id, "label": "Row A", "sequence": 0,
        })
        cls.row_b = cls.env["event.venue.row"].create({
            "event_id": cls.event.id, "label": "Row B", "sequence": 3,
        })
        # Ground truth this test's calibration inputs are derived from -
        # never seen by the code under test, only by the assertions.
        cls.true_origin = (40.0, -75.0)
        cls.true_spot_bearing, cls.true_spot_spacing = 90.0, 10.0
        cls.true_row_bearing, cls.true_row_spacing = 0.0, 25.0

    def _make_booth(self, row, spot_number, name="Booth"):
        return self.env["event.booth"].create({
            "event_id": self.event.id,
            "booth_category_id": self.category.id,
            "row_id": row.id,
            "spot_number": spot_number,
            "name": name,
        })

    def _true_point(self, row_sequence, spot_number):
        lat, lng = self.true_origin
        if spot_number != 1:
            lat, lng = destination_point(
                lat, lng, self.true_spot_bearing,
                (spot_number - 1) * self.true_spot_spacing)
        if row_sequence:
            lat, lng = destination_point(
                lat, lng, self.true_row_bearing,
                row_sequence * self.true_row_spacing)
        return lat, lng

    def test_calibration_and_booth_positions(self):
        spot_lat, spot_lng = self._true_point(0, 4)
        row_lat, row_lng = self._true_point(3, 1)

        wizard = self.env["nonprofit.venue.map.calibrate"].create({
            "event_id": self.event.id,
            "origin_row_id": self.row_a.id,
            "origin_lat": self.true_origin[0],
            "origin_lng": self.true_origin[1],
            "spot_calib_number": 4,
            "spot_calib_lat": spot_lat,
            "spot_calib_lng": spot_lng,
            "row_calib_row_id": self.row_b.id,
            "row_calib_lat": row_lat,
            "row_calib_lng": row_lng,
        })
        wizard.action_apply()

        self.assertTrue(self.event.map_enabled)
        self.assertAlmostEqual(
            self.event.map_origin_lat, self.true_origin[0], places=6)
        self.assertAlmostEqual(
            self.event.map_origin_lng, self.true_origin[1], places=6)
        self.assertAlmostEqual(
            self.event.map_spot_bearing_deg, self.true_spot_bearing, places=2)
        self.assertAlmostEqual(
            self.event.map_spot_spacing_m, self.true_spot_spacing, places=2)
        self.assertAlmostEqual(
            self.event.map_row_bearing_deg, self.true_row_bearing, places=2)
        self.assertAlmostEqual(
            self.event.map_row_spacing_m, self.true_row_spacing, places=2)

        booth1 = self._make_booth(self.row_a, 1, "Booth 1")
        booth2 = self._make_booth(self.row_a, 4, "Booth 2")
        booth3 = self._make_booth(self.row_b, 1, "Booth 3")

        for booth, (row_seq, spot) in (
            (booth1, (0, 1)), (booth2, (0, 4)), (booth3, (3, 1)),
        ):
            exp_lat, exp_lng = self._true_point(row_seq, spot)
            self.assertAlmostEqual(booth.latitude, exp_lat, places=6)
            self.assertAlmostEqual(booth.longitude, exp_lng, places=6)
            self.assertEqual(
                booth.booth_label, "%s · Spot %s" % (booth.row_id.label, spot))

    def test_booth_without_row_has_no_position(self):
        booth = self.env["event.booth"].create({
            "event_id": self.event.id,
            "booth_category_id": self.category.id,
            "name": "Unplaced",
        })
        self.assertFalse(booth.latitude)
        self.assertFalse(booth.longitude)
        self.assertFalse(booth.booth_label)

    def test_row_spot_unique_per_row(self):
        self._make_booth(self.row_a, 1, "First")
        with self.assertRaises(ValidationError):
            self._make_booth(self.row_a, 1, "Duplicate spot")

    def test_unassigned_spot_number_does_not_collide(self):
        # Both left at the default spot_number (0, unassigned) - this must
        # NOT be treated as a collision the way two real matching spot
        # numbers would be.
        self._make_booth(self.row_a, 0, "Unplaced 1")
        booth = self._make_booth(self.row_a, 0, "Unplaced 2")
        self.assertTrue(booth)

    def test_calibrate_rejects_same_sequence_rows(self):
        same_seq_row = self.env["event.venue.row"].create({
            "event_id": self.event.id, "label": "Row A2", "sequence": 0,
        })
        wizard = self.env["nonprofit.venue.map.calibrate"].create({
            "event_id": self.event.id,
            "origin_row_id": self.row_a.id,
            "origin_lat": 40.0, "origin_lng": -75.0,
            "spot_calib_number": 2,
            "spot_calib_lat": 40.0001, "spot_calib_lng": -75.0,
            "row_calib_row_id": same_seq_row.id,
            "row_calib_lat": 40.0, "row_calib_lng": -75.0001,
        })
        with self.assertRaises(Exception):
            wizard.action_apply()
