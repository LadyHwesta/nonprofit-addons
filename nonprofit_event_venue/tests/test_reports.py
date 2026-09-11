# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVenueReports(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create({
            "name": "Pride 2027",
            "date_begin": datetime.now() + timedelta(days=60),
            "date_end": datetime.now() + timedelta(days=60, hours=8),
        })
        category = cls.env["event.booth.category"].create({"name": "Food"})
        row = cls.env["event.venue.row"].create({
            "event_id": cls.event.id, "label": "Row A", "sequence": 0,
        })
        vendor = cls.env["res.partner"].create({"name": "Taco Truck"})
        cls.booth = cls.env["event.booth"].create({
            "event_id": cls.event.id, "booth_category_id": category.id,
            "row_id": row.id, "spot_number": 5, "spot_width": 2,
            "needs_power": True, "name": "Booth 1", "partner_id": vendor.id,
        })

    def test_vendor_manifest_renders(self):
        report = self.env.ref(
            "nonprofit_event_venue.action_report_vendor_manifest")
        html, content_type = self.env["ir.actions.report"]._render_qweb_html(
            report.report_name, [self.event.id])
        self.assertEqual(content_type, "html")
        self.assertIn(b"Row A", html)
        self.assertIn(b"5-6", html)

    def test_vendor_requirements_renders(self):
        report = self.env.ref(
            "nonprofit_event_venue.action_report_vendor_requirements")
        html, content_type = self.env["ir.actions.report"]._render_qweb_html(
            report.report_name, [self.event.id])
        self.assertEqual(content_type, "html")
        self.assertIn(b"Taco Truck", html)
        self.assertIn(b"2 spots", html)
