# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestShiftGeneration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event_type = cls.env["event.type"].create({"name": "Weekly Pantry"})
        # a Monday-and-Wednesday morning shift template
        cls.env["volunteer.shift.template"].create({
            "event_type_id": cls.event_type.id, "name": "Pantry Helper",
            "weekday": "0", "start_time": 9.0, "duration_hours": 3.0,
            "slot_count": 4,
        })
        cls.env["volunteer.shift.template"].create({
            "event_type_id": cls.event_type.id, "name": "Pantry Helper",
            "weekday": "2", "start_time": 9.0, "duration_hours": 3.0,
            "slot_count": 4,
        })
        # a 2-week event starting next Monday
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start += timedelta(days=(7 - start.weekday()) % 7 or 7)
        cls.event = cls.env["event.event"].create({
            "name": "Pantry - Spring",
            "event_type_id": cls.event_type.id,
            "date_begin": start,
            "date_end": start + timedelta(days=14),
        })

    def test_generation_is_correct_and_idempotent(self):
        Shift = self.env["volunteer.shift"]
        created = Shift._generate_shifts_for_event(self.event)
        # 2 weeks x (1 Monday + 1 Wednesday) = 4 shifts
        self.assertEqual(len(created), 4)
        self.assertTrue(all(s.slot_count == 4 for s in created))
        self.assertTrue(all(s.role_id.use_shifts for s in created))
        # exactly one role was created and reused
        roles = self.event.volunteer_role_ids
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles.name, "Pantry Helper")

        # second run adds nothing
        again = Shift._generate_shifts_for_event(self.event)
        self.assertEqual(len(again), 0)
        self.assertEqual(len(self.event.volunteer_role_ids.shift_ids), 4)

    def test_weekday_and_time_placement(self):
        created = self.env["volunteer.shift"]._generate_shifts_for_event(
            self.event)
        for shift in created:
            self.assertIn(str(shift.start.weekday()), ("0", "2"))
            self.assertEqual(shift.start.hour, 9)
            self.assertEqual(shift.duration_hours, 3.0)

    def test_cron_runs_within_horizon(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "volunteer_shift.horizon_weeks", "8")
        self.env["volunteer.shift"]._cron_generate_shifts()
        self.assertTrue(self.event.volunteer_role_ids.shift_ids)
