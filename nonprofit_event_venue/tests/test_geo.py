# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

from ..models.geo import bearing_and_distance, destination_point


@tagged("post_install", "-at_install")
class TestGeo(TransactionCase):
    """Pure math checks on the great-circle helpers - no DB records needed,
    just run inside the Odoo test runner like everything else here."""

    def test_destination_point_east(self):
        # Moving 100m due east from the equator/prime-meridian should
        # barely change latitude and nudge longitude eastward.
        lat, lng = destination_point(0.0, 0.0, 90.0, 100.0)
        self.assertAlmostEqual(lat, 0.0, places=4)
        self.assertGreater(lng, 0.0)

    def test_destination_point_zero_distance(self):
        lat, lng = destination_point(40.0, -73.0, 45.0, 0.0)
        self.assertAlmostEqual(lat, 40.0, places=9)
        self.assertAlmostEqual(lng, -73.0, places=9)

    def test_round_trip(self):
        """destination_point and bearing_and_distance are inverses of each
        other - this is exactly what the calibration wizard leans on."""
        start_lat, start_lng = 40.7128, -74.0060  # NYC, arbitrary
        for bearing, distance in [(0, 50), (90, 120), (200, 30), (315, 500)]:
            lat, lng = destination_point(start_lat, start_lng, bearing, distance)
            back_bearing, back_distance = bearing_and_distance(
                start_lat, start_lng, lat, lng)
            self.assertAlmostEqual(back_bearing, bearing, places=3)
            self.assertAlmostEqual(back_distance, distance, places=3)
