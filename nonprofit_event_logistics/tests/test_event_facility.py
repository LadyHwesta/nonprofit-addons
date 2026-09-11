# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import EventLogisticsCommon


@tagged("post_install", "-at_install")
class TestEventFacility(EventLogisticsCommon):
    def test_create_and_link_to_crew_booking(self):
        vendor = self.env["res.partner"].create({"name": "Porta-Potty Co"})
        booking = self.env["event.crew.booking"].create({
            "event_id": self.event.id, "partner_id": vendor.id,
            "service_type": "sanitation",
        })
        facility = self.env["event.facility"].create({
            "event_id": self.event.id,
            "name": "Restroom Cluster A",
            "facility_type": "restroom",
            "quantity": 4,
            "crew_booking_id": booking.id,
        })
        self.assertEqual(facility.crew_booking_id, booking)
        self.assertFalse(facility.latitude)
        self.assertFalse(facility.longitude)

    def test_placement(self):
        facility = self.env["event.facility"].create({
            "event_id": self.event.id, "name": "Hand Wash Station",
            "facility_type": "hand_wash",
        })
        facility.write({"latitude": 40.7128, "longitude": -74.0060})
        self.assertAlmostEqual(facility.latitude, 40.7128, places=4)
