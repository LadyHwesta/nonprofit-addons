# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVolunteerShift(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create({
            "name": "Food Drive",
            "date_begin": datetime.now() + timedelta(days=7),
            "date_end": datetime.now() + timedelta(days=7, hours=8),
        })
        cls.role = cls.env["event.volunteer.role"].create({
            "event_id": cls.event.id, "name": "Sorter", "use_shifts": True,
            "slot_count": 1,
        })
        cls.shift = cls.env["volunteer.shift"].create({
            "role_id": cls.role.id,
            "start": datetime.now() + timedelta(days=7),
            "stop": datetime.now() + timedelta(days=7, hours=3),
            "slot_count": 2,
        })
        cls.p1 = cls.env["res.partner"].create({"name": "Vol One"})
        cls.p2 = cls.env["res.partner"].create({"name": "Vol Two"})
        cls.p3 = cls.env["res.partner"].create({"name": "Vol Three"})

    def _assign(self, partner):
        return self.env["event.volunteer.assignment"].create({
            "role_id": self.role.id, "shift_id": self.shift.id,
            "partner_id": partner.id, "state": "confirmed",
        })

    def test_shift_counts_and_fill_state(self):
        self.assertAlmostEqual(self.shift.duration_hours, 3.0, places=3)
        self.assertEqual(self.shift.fill_state, "empty")
        self._assign(self.p1)
        self.assertEqual(self.shift.filled_count, 1)
        self.assertEqual(self.shift.fill_state, "partial")
        self._assign(self.p2)
        self.assertEqual(self.shift.fill_state, "full")
        self.assertEqual(self.shift.seats_available, 0)

    def test_shift_capacity_enforced(self):
        self._assign(self.p1)
        self._assign(self.p2)
        with self.assertRaises(ValidationError):
            self._assign(self.p3)

    def test_one_signup_per_shift(self):
        self._assign(self.p1)
        with self.assertRaises(ValidationError):
            self._assign(self.p1)

    def test_role_counts_aggregate_over_shifts(self):
        shift2 = self.env["volunteer.shift"].create({
            "role_id": self.role.id,
            "start": datetime.now() + timedelta(days=7, hours=3),
            "stop": datetime.now() + timedelta(days=7, hours=6),
            "slot_count": 2,
        })
        self._assign(self.p1)
        self.env["event.volunteer.assignment"].create({
            "role_id": self.role.id, "shift_id": shift2.id,
            "partner_id": self.p2.id, "state": "confirmed",
        })
        self.role.invalidate_recordset()
        self.assertEqual(self.role.filled_count, 2)
        self.assertEqual(self.role.seats_available, 2)  # 4 slots - 2 filled
        self.assertEqual(self.role.fill_state, "partial")

    def test_check_in_out_hours(self):
        a = self._assign(self.p1)
        a.check_in = datetime(2026, 1, 1, 9, 0, 0)
        a.check_out = datetime(2026, 1, 1, 12, 30, 0)
        self.assertAlmostEqual(a.hours, 3.5)

    def test_no_show_clears_times(self):
        a = self._assign(self.p1)
        a.check_in = datetime.now()
        a.action_mark_no_show()
        self.assertTrue(a.no_show)
        self.assertFalse(a.check_in)
        self.assertEqual(a.hours, 0.0)

    def test_swap_flow_reassigns_partner(self):
        a = self._assign(self.p1)
        swap = self.env["volunteer.shift.swap"].create({"assignment_id": a.id})
        swap.action_claim(self.p3)
        self.assertEqual(swap.state, "claimed")
        swap.action_approve()
        self.assertEqual(swap.state, "approved")
        self.assertEqual(a.partner_id, self.p3)

    def test_swap_claim_guards(self):
        a = self._assign(self.p1)
        swap = self.env["volunteer.shift.swap"].create({"assignment_id": a.id})
        with self.assertRaises(Exception):
            swap.action_claim(self.p1)  # own shift
