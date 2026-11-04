# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.tests import tagged

from .common import EventEntertainmentCommon


@tagged("post_install", "-at_install")
class TestEventStage(EventEntertainmentCommon):

    def test_start_time_defaults_from_the_event(self):
        stage = self.env["event.entertainment.stage"].create({
            "event_id": self.event.id, "name": "Acoustic Tent",
        })

        self.assertEqual(stage.start_time, self.event.date_begin)

    def test_start_time_is_not_overridden_when_given_explicitly(self):
        explicit = datetime(2027, 9, 25, 19, 30, 0)
        stage = self.env["event.entertainment.stage"].create({
            "event_id": self.event.id, "name": "Acoustic Tent",
            "start_time": explicit,
        })

        self.assertEqual(stage.start_time, explicit)

    def test_line_count(self):
        self.assertEqual(self.stage.line_count, 0)
        self.env["event.run_of_show.line"].create({
            "stage_id": self.stage.id, "performer_id": self.performer.id,
        })

        self.assertEqual(self.stage.line_count, 1)
