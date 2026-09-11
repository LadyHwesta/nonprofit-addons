# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import EventLogisticsCommon


@tagged("post_install", "-at_install")
class TestEventStaff(EventLogisticsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.role = cls.env["event.staff.role"].create({"name": "Security"})
        cls.shift = cls.env["event.staff.shift"].create({
            "event_id": cls.event.id,
            "role_id": cls.role.id,
            "start": datetime.now() + timedelta(days=30),
            "stop": datetime.now() + timedelta(days=30, hours=8),
            "headcount_needed": 1,
        })
        cls.worker_a = cls.env["res.partner"].create({"name": "Jordan Lee"})
        cls.worker_b = cls.env["res.partner"].create({"name": "Sam Diaz"})

    def test_fill_state_progression(self):
        self.assertEqual(self.shift.fill_state, "empty")
        self.env["event.staff.assignment"].create({
            "shift_id": self.shift.id, "partner_id": self.worker_a.id,
        })
        self.assertEqual(self.shift.fill_state, "full")

    def test_capacity_guard_blocks_overfill(self):
        self.env["event.staff.assignment"].create({
            "shift_id": self.shift.id, "partner_id": self.worker_a.id,
        })
        with self.assertRaises(ValidationError):
            self.env["event.staff.assignment"].create({
                "shift_id": self.shift.id, "partner_id": self.worker_b.id,
            })

    def test_capacity_guard_bypass_context(self):
        self.env["event.staff.assignment"].create({
            "shift_id": self.shift.id, "partner_id": self.worker_a.id,
        })
        # With skip_staff_capacity, over-filling is allowed.
        assignment = self.env["event.staff.assignment"].with_context(
            skip_staff_capacity=True).create({
                "shift_id": self.shift.id, "partner_id": self.worker_b.id,
            })
        self.assertTrue(assignment)
        self.assertEqual(self.shift.fill_state, "over")

    def test_check_in_out_computes_hours(self):
        assignment = self.env["event.staff.assignment"].create({
            "shift_id": self.shift.id, "partner_id": self.worker_a.id,
        })
        with self.assertRaises(UserError):
            assignment.action_check_out()  # no check-in yet

        assignment.action_check_in()
        self.assertTrue(assignment.check_in)
        assignment.check_out = assignment.check_in + timedelta(hours=6)
        self.assertAlmostEqual(assignment.hours, 6.0, places=3)

    def test_no_show(self):
        assignment = self.env["event.staff.assignment"].create({
            "shift_id": self.shift.id, "partner_id": self.worker_a.id,
        })
        assignment.action_mark_no_show()
        self.assertEqual(assignment.state, "no_show")
        # A no-show frees the slot back up.
        second = self.env["event.staff.assignment"].create({
            "shift_id": self.shift.id, "partner_id": self.worker_b.id,
        })
        self.assertTrue(second)
        self.assertEqual(self.shift.fill_state, "full")
