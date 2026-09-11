# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestParadeEntry(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create({
            "name": "Pride Parade 2027",
            "date_begin": datetime.now() + timedelta(days=90),
            "date_end": datetime.now() + timedelta(days=90, hours=6),
            "parade_enabled": True,
        })
        cls.area_a = cls.env["event.parade.staging.area"].create({
            "event_id": cls.event.id, "name": "Lot A", "sequence": 1,
            "capacity": 1,
        })
        cls.area_b = cls.env["event.parade.staging.area"].create({
            "event_id": cls.event.id, "name": "Lot B", "sequence": 2,
        })

    def _make_entry(self, name="Rainbow Riders", **extra):
        vals = {
            "event_id": self.event.id,
            "name": name,
            "contact_name": "Jamie Rivera",
            "contact_email": "jamie@example.com",
            "waiver_accepted": True,
        }
        vals.update(extra)
        return self.env["event.parade.entry"].create(vals)

    def test_create_notifies_coordinator(self):
        coordinator = self.env["res.users"].create({
            "name": "Parade Coordinator", "login": "parade_coord",
        })
        self.event.parade_coordinator_id = coordinator
        entry = self._make_entry()
        activity = entry.activity_ids.filtered(
            lambda a: a.user_id == coordinator)
        self.assertTrue(activity, "coordinator should get a To-Do")

    def test_state_machine(self):
        entry = self._make_entry()
        self.assertEqual(entry.state, "submitted")

        with self.assertRaises(UserError):
            entry.action_confirm()  # not approved yet

        entry.action_approve()
        self.assertEqual(entry.state, "approved")

        with self.assertRaises(UserError):
            entry.action_confirm()  # no staging area yet

        entry.staging_area_id = self.area_b
        entry.action_confirm()
        self.assertEqual(entry.state, "confirmed")

        entry.action_withdraw()
        self.assertEqual(entry.state, "withdrawn")

    def test_reject_then_reset(self):
        entry = self._make_entry()
        entry.action_reject()
        self.assertEqual(entry.state, "rejected")
        entry.action_reset_to_submitted()
        self.assertEqual(entry.state, "submitted")

    def test_over_capacity_is_a_soft_warning(self):
        entry1 = self._make_entry("First")
        entry2 = self._make_entry("Second")
        for entry in (entry1, entry2):
            entry.staging_area_id = self.area_a  # capacity 1
            entry.action_approve()

        entry1.action_confirm()
        message_count_before = len(self.area_a.message_ids)
        entry2.action_confirm()  # now 2 confirmed in a capacity-1 area

        self.assertEqual(entry2.state, "confirmed")  # not blocked
        self.assertGreater(len(self.area_a.message_ids), message_count_before)

    def test_step_off_wizard_sequences_confirmed_entries(self):
        entry1 = self._make_entry("First", sequence=1)
        entry2 = self._make_entry("Second", sequence=2)
        for entry in (entry1, entry2):
            entry.staging_area_id = self.area_b
            entry.action_approve()
            entry.action_confirm()

        start = datetime(2027, 6, 1, 10, 0, 0)
        wizard = self.env["nonprofit.parade.step_off.wizard"].create({
            "event_id": self.event.id,
            "start_time": start,
            "gap_minutes": 5,
        })
        wizard.action_apply()

        self.assertEqual(entry1.step_off_time, start)
        self.assertEqual(entry2.step_off_time, start + timedelta(minutes=5))

    def test_step_off_wizard_requires_confirmed_entries(self):
        wizard = self.env["nonprofit.parade.step_off.wizard"].create({
            "event_id": self.event.id,
            "start_time": datetime(2027, 6, 1, 10, 0, 0),
            "gap_minutes": 5,
        })
        with self.assertRaises(UserError):
            wizard.action_apply()
