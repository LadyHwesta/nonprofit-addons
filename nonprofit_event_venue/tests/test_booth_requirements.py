# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBoothRequirements(TransactionCase):
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
        cls.row = cls.env["event.venue.row"].create({
            "event_id": cls.event.id, "label": "Row A", "sequence": 0,
        })

    def _make_booth(self, spot_number, spot_width=1, **extra):
        vals = {
            "event_id": self.event.id,
            "booth_category_id": self.category.id,
            "row_id": self.row.id,
            "spot_number": spot_number,
            "spot_width": spot_width,
            "name": "Booth",
        }
        vals.update(extra)
        return self.env["event.booth"].create(vals)

    def test_spot_range_display_single(self):
        booth = self._make_booth(5)
        self.assertEqual(booth.spot_range_display, "5")
        self.assertEqual(booth.booth_label, "Row A · Spot 5")

    def test_spot_range_display_double_wide(self):
        booth = self._make_booth(5, spot_width=2)
        self.assertEqual(booth.spot_range_display, "5-6")
        self.assertEqual(booth.booth_label, "Row A · Spot 5-6")

    def test_double_wide_blocks_overlapping_neighbor(self):
        self._make_booth(5, spot_width=2)  # occupies 5-6
        with self.assertRaises(ValidationError):
            self._make_booth(6)  # collides with the double-wide booth

    def test_double_wide_allows_non_overlapping_neighbor(self):
        self._make_booth(5, spot_width=2)  # occupies 5-6
        booth = self._make_booth(7)
        self.assertTrue(booth)

    def test_needs_power_flag(self):
        booth = self._make_booth(1, needs_power=True)
        self.assertTrue(booth.needs_power)
