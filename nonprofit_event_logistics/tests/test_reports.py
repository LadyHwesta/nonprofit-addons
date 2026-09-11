# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import tagged

from .common import EventLogisticsCommon


@tagged("post_install", "-at_install")
class TestLogisticsReports(EventLogisticsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["event.permit"].create({
            "event_id": cls.event.id, "name": "Fire Safety Permit",
            "issuing_authority": "City Fire Marshal",
        })
        role = cls.env["event.staff.role"].create({"name": "Security"})
        shift = cls.env["event.staff.shift"].create({
            "event_id": cls.event.id, "role_id": role.id,
            "start": datetime.now() + timedelta(days=30),
            "stop": datetime.now() + timedelta(days=30, hours=8),
            "headcount_needed": 1,
        })
        worker = cls.env["res.partner"].create({
            "name": "Jordan Lee", "phone": "555-0100",
        })
        cls.env["event.staff.assignment"].create({
            "shift_id": shift.id, "partner_id": worker.id,
        })
        vendor = cls.env["res.partner"].create({"name": "Loud & Clear Sound"})
        cls.env["event.crew.booking"].create({
            "event_id": cls.event.id, "partner_id": vendor.id,
            "service_type": "sound", "day_of_contact_name": "Casey",
            "day_of_contact_phone": "555-0199",
        })
        cls.env["event.facility"].create({
            "event_id": cls.event.id, "name": "Restroom Cluster A",
            "facility_type": "restroom", "quantity": 4,
        })

    def _render(self, xml_id):
        report = self.env.ref(xml_id)
        return self.env["ir.actions.report"]._render_qweb_html(
            report.report_name, [self.event.id])

    def test_permit_status_report_renders(self):
        html, content_type = self._render(
            "nonprofit_event_logistics.action_report_permit_status")
        self.assertEqual(content_type, "html")
        self.assertIn(b"Fire Safety Permit", html)
        self.assertIn(b"City Fire Marshal", html)

    def test_staffing_roster_renders(self):
        html, content_type = self._render(
            "nonprofit_event_logistics.action_report_staffing_roster")
        self.assertEqual(content_type, "html")
        self.assertIn(b"Jordan Lee", html)
        self.assertIn(b"555-0100", html)

    def test_crew_day_of_sheet_renders(self):
        html, content_type = self._render(
            "nonprofit_event_logistics.action_report_crew_day_of_sheet")
        self.assertEqual(content_type, "html")
        self.assertIn(b"Loud", html)
        self.assertIn(b"Casey", html)
        self.assertIn(b"Restroom Cluster A", html)
