# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import EventEntertainmentCommon


@tagged("post_install", "-at_install")
class TestEventRunOfShowLine(EventEntertainmentCommon):

    def _make_line(self, **extra):
        vals = {"stage_id": self.stage.id, "performer_id": self.performer.id}
        vals.update(extra)
        return self.env["event.run_of_show.line"].create(vals)

    def test_title_defaults_to_the_performers_name(self):
        line = self._make_line()

        self.assertEqual(line.title, "The Wandering Fiddlers")

    def test_title_stays_editable_after_the_default_fires(self):
        line = self._make_line()

        line.title = "The Wandering Fiddlers - Headline Set"

        self.assertEqual(line.title, "The Wandering Fiddlers - Headline Set")

    def test_announcement_needs_its_own_title(self):
        line = self.env["event.run_of_show.line"].create({
            "stage_id": self.stage.id, "line_type": "announcement",
            "title": "Raffle Drawing", "duration_minutes": 10,
        })

        self.assertEqual(line.title, "Raffle Drawing")
        self.assertFalse(line.performer_id)

    def test_performance_without_a_performer_raises(self):
        with self.assertRaises(ValidationError):
            self.env["event.run_of_show.line"].create({
                "stage_id": self.stage.id, "line_type": "performance",
                "title": "Someone", "duration_minutes": 30,
            })

    def test_announcement_without_a_title_raises(self):
        with self.assertRaises(ValidationError):
            self.env["event.run_of_show.line"].create({
                "stage_id": self.stage.id, "line_type": "announcement",
                "duration_minutes": 10,
            })

    def test_sequential_schedule_computes_cumulative_times(self):
        first = self._make_line(sequence=10, duration_minutes=30)
        second = self._make_line(sequence=20, duration_minutes=45)
        third = self.env["event.run_of_show.line"].create({
            "stage_id": self.stage.id, "line_type": "announcement",
            "title": "Sponsor Thank-Yous", "sequence": 30,
            "duration_minutes": 5,
        })

        self.assertEqual(first.computed_start, self.stage.start_time)
        self.assertEqual(first.computed_end, datetime(2027, 9, 25, 18, 30, 0))
        self.assertEqual(second.computed_start, datetime(2027, 9, 25, 18, 30, 0))
        self.assertEqual(second.computed_end, datetime(2027, 9, 25, 19, 15, 0))
        self.assertEqual(third.computed_start, datetime(2027, 9, 25, 19, 15, 0))
        self.assertEqual(third.computed_end, datetime(2027, 9, 25, 19, 20, 0))

    def test_hard_time_override_shifts_every_later_line(self):
        first = self._make_line(sequence=10, duration_minutes=30)
        second = self._make_line(
            sequence=20, duration_minutes=45,
            planned_start_override=datetime(2027, 9, 25, 21, 0, 0))
        third = self._make_line(sequence=30, duration_minutes=20)

        self.assertEqual(first.computed_end, datetime(2027, 9, 25, 18, 30, 0))
        # second has a hard time well past when it would otherwise start
        self.assertEqual(second.computed_start, datetime(2027, 9, 25, 21, 0, 0))
        self.assertEqual(second.computed_end, datetime(2027, 9, 25, 21, 45, 0))
        # third follows from second's real (overridden) end, not the
        # original flowing schedule
        self.assertEqual(third.computed_start, datetime(2027, 9, 25, 21, 45, 0))

    def test_reordering_sequence_recomputes_the_schedule(self):
        first = self._make_line(sequence=10, duration_minutes=30)
        second = self._make_line(sequence=20, duration_minutes=45)

        second.sequence = 5  # second now runs first

        self.assertEqual(second.computed_start, self.stage.start_time)
        self.assertEqual(first.computed_start, datetime(2027, 9, 25, 18, 45, 0))

    def test_booking_state_machine(self):
        line = self._make_line()
        self.assertEqual(line.booking_state, "invited")

        line.action_confirm()
        self.assertEqual(line.booking_state, "confirmed")

        with self.assertRaises(UserError):
            line.action_confirm()  # already confirmed, not invited anymore

        line.action_decline()
        self.assertEqual(line.booking_state, "declined")

    def test_cancel_works_from_any_state(self):
        line = self._make_line()
        line.action_confirm()

        line.action_cancel()

        self.assertEqual(line.booking_state, "cancelled")
