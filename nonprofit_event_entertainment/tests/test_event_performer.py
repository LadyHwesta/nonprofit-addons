# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.tests import tagged

from .common import EventEntertainmentCommon


@tagged("post_install", "-at_install")
class TestEventPerformer(EventEntertainmentCommon):

    def test_default_set_length_prefills_a_new_booking(self):
        line = self.env["event.run_of_show.line"].create({
            "stage_id": self.stage.id,
            "performer_id": self.performer.id,
        })

        self.assertEqual(line.duration_minutes, 45)

    def test_booking_count_reflects_bookings_across_multiple_events(self):
        other_event = self.env["event.event"].create({
            "name": "Spring Fair 2028",
            "date_begin": datetime(2028, 4, 10, 12, 0, 0),
            "date_end": datetime(2028, 4, 10, 18, 0, 0),
        })
        other_stage = self.env["event.entertainment.stage"].create({
            "event_id": other_event.id,
            "name": "Main Stage",
            "start_time": datetime(2028, 4, 10, 12, 0, 0),
        })
        self.env["event.run_of_show.line"].create({
            "stage_id": self.stage.id, "performer_id": self.performer.id,
        })
        self.env["event.run_of_show.line"].create({
            "stage_id": other_stage.id, "performer_id": self.performer.id,
        })

        self.assertEqual(self.performer.booking_count, 2)
