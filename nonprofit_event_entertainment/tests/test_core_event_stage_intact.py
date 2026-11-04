# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from .common import EventEntertainmentCommon


@tagged("post_install", "-at_install")
class TestCoreEventStageIntact(EventEntertainmentCommon):
    """This module once declared ``_name = "event.stage"``, which silently
    replaced core's pipeline model. Guards against that coming back."""

    def test_core_stage_keeps_its_own_fields(self):
        stage_fields = self.env["event.stage"]._fields
        self.assertIn("pipe_end", stage_fields)
        self.assertNotIn("event_id", stage_fields)

    def test_performance_stages_stay_out_of_the_pipeline(self):
        self.assertNotEqual(self.stage._table, self.env["event.stage"]._table)
        self.assertEqual(self.event.stage_ids, self.stage)
        self.assertEqual(self.event.stage_id._name, "event.stage")

    def test_core_cleanup_job_moves_ended_events(self):
        ended_stage = self.env["event.stage"].search([("pipe_end", "=", True)], limit=1)
        self.assertTrue(ended_stage)
        now = fields.Datetime.now()
        event = self.env["event.event"].create({
            "name": "Already Over",
            "date_begin": now - timedelta(days=2),
            "date_end": now - timedelta(days=1),
        })

        self.env["event.event"]._gc_mark_events_done()

        self.assertEqual(event.stage_id, ended_stage)
