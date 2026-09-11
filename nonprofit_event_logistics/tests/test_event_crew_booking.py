# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import EventLogisticsCommon


@tagged("post_install", "-at_install")
class TestEventCrewBooking(EventLogisticsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Loud & Clear Sound"})

    def _make_booking(self, **extra):
        vals = {
            "event_id": self.event.id,
            "partner_id": self.vendor.id,
            "service_type": "sound",
            "load_in": datetime.now() + timedelta(days=30),
            "load_out": datetime.now() + timedelta(days=30, hours=10),
        }
        vals.update(extra)
        return self.env["event.crew.booking"].create(vals)

    def test_state_machine(self):
        booking = self._make_booking()
        self.assertEqual(booking.state, "planned")

        with self.assertRaises(UserError):
            booking.action_mark_on_site()  # not confirmed yet

        booking.action_confirm()
        self.assertEqual(booking.state, "confirmed")
        booking.action_mark_on_site()
        self.assertEqual(booking.state, "on_site")
        booking.action_mark_complete()
        self.assertEqual(booking.state, "complete")

        with self.assertRaises(UserError):
            booking.action_cancel()  # can't cancel a completed booking

    def test_booking_without_purchase_order_is_allowed(self):
        booking = self._make_booking()
        self.assertFalse(booking.purchase_order_id)
        booking.action_confirm()
        self.assertEqual(booking.state, "confirmed")

    def test_cancel_from_planned(self):
        booking = self._make_booking()
        booking.action_cancel()
        self.assertEqual(booking.state, "cancelled")
