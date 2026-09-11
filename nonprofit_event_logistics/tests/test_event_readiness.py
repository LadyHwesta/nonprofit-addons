# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import tagged

from .common import EventLogisticsCommon


@tagged("post_install", "-at_install")
class TestEventReadiness(EventLogisticsCommon):
    def test_logistics_counts(self):
        self.env["event.permit"].create({
            "event_id": self.event.id, "name": "Food Health Permit",
            "state": "approved",
        })
        self.env["event.permit"].create({
            "event_id": self.event.id, "name": "Alcohol Permit",
        })
        self.assertEqual(self.event.permit_count, 2)
        self.assertEqual(self.event.permit_approved_count, 1)

        role = self.env["event.staff.role"].create({"name": "Ushers"})
        shift = self.env["event.staff.shift"].create({
            "event_id": self.event.id, "role_id": role.id,
            "start": datetime.now() + timedelta(days=30),
            "stop": datetime.now() + timedelta(days=30, hours=4),
            "headcount_needed": 4,
        })
        self.env["event.staff.assignment"].create({
            "shift_id": shift.id,
            "partner_id": self.env["res.partner"].create({"name": "W1"}).id,
        })
        self.assertAlmostEqual(self.event.staffing_fill_pct, 0.25, places=3)

        vendor = self.env["res.partner"].create({"name": "Stage Co"})
        self.env["event.crew.booking"].create({
            "event_id": self.event.id, "partner_id": vendor.id,
            "service_type": "stage", "state": "confirmed",
        })
        self.env["event.crew.booking"].create({
            "event_id": self.event.id, "partner_id": vendor.id,
            "service_type": "sound",
        })
        self.assertEqual(self.event.crew_booking_count, 2)
        self.assertEqual(self.event.crew_confirmed_count, 1)

        self.env["event.facility"].create({
            "event_id": self.event.id, "name": "Restroom Cluster A",
            "facility_type": "restroom",
        })
        self.assertEqual(self.event.facility_count, 1)

    def test_readiness_cron_raises_one_consolidated_activity(self):
        coordinator = self.env["res.users"].create({
            "name": "Logistics Coordinator", "login": "logistics_coord",
        })
        self.event.logistics_coordinator_id = coordinator
        self.event.date_begin = datetime.now() + timedelta(days=10)

        self.env["event.permit"].create({
            "event_id": self.event.id, "name": "Fire Safety Permit",
        })

        self.env["event.event"]._cron_event_readiness_check()
        activities = self.event.activity_ids.filtered(
            lambda a: a.user_id == coordinator)
        self.assertEqual(len(activities), 1)
        self.assertIn("permit", activities.note.lower())

        # Running again shouldn't pile on a second activity.
        self.env["event.event"]._cron_event_readiness_check()
        activities = self.event.activity_ids.filtered(
            lambda a: a.user_id == coordinator)
        self.assertEqual(len(activities), 1)

    def test_readiness_cron_skips_events_with_nothing_open(self):
        self.event.date_begin = datetime.now() + timedelta(days=10)
        self.env["event.event"]._cron_event_readiness_check()
        self.assertFalse(self.event.activity_ids)

    def test_readiness_cron_ignores_far_off_events(self):
        self.event.write({
            "date_begin": datetime.now() + timedelta(days=90),
            "date_end": datetime.now() + timedelta(days=90, hours=8),
        })
        self.env["event.permit"].create({
            "event_id": self.event.id, "name": "Fire Safety Permit",
        })
        self.env["event.event"]._cron_event_readiness_check()
        self.assertFalse(self.event.activity_ids)
