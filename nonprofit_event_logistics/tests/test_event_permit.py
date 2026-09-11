# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import EventLogisticsCommon


@tagged("post_install", "-at_install")
class TestEventPermit(EventLogisticsCommon):
    def _make_permit(self, **extra):
        vals = {"event_id": self.event.id, "name": "Amplified Sound Permit"}
        vals.update(extra)
        return self.env["event.permit"].create(vals)

    def test_state_machine(self):
        permit = self._make_permit()
        self.assertEqual(permit.state, "not_started")

        with self.assertRaises(UserError):
            permit.action_approve()  # not submitted yet

        permit.action_submit()
        self.assertEqual(permit.state, "submitted")
        self.assertTrue(permit.submitted_date)

        permit.action_approve()
        self.assertEqual(permit.state, "approved")
        self.assertTrue(permit.approval_date)

    def test_deny_and_reset(self):
        permit = self._make_permit()
        permit.action_submit()
        permit.action_deny()
        self.assertEqual(permit.state, "denied")
        permit.action_reset_to_not_started()
        self.assertEqual(permit.state, "not_started")

    def test_deadline_cron_flags_and_dedupes(self):
        permit = self._make_permit(
            submit_by_date=fields_date_soon(),
        )
        self.env["event.permit"]._cron_flag_permit_deadlines()
        activities = permit.activity_ids.filtered(
            lambda a: (a.summary or "") == "Permit due soon")
        self.assertEqual(len(activities), 1)

        # Running again shouldn't duplicate the activity.
        self.env["event.permit"]._cron_flag_permit_deadlines()
        activities = permit.activity_ids.filtered(
            lambda a: (a.summary or "") == "Permit due soon")
        self.assertEqual(len(activities), 1)

    def test_deadline_cron_ignores_far_off_permits(self):
        permit = self._make_permit(
            submit_by_date=(datetime.now() + timedelta(days=90)).date(),
        )
        self.env["event.permit"]._cron_flag_permit_deadlines()
        self.assertFalse(permit.activity_ids)

    def test_expiry_cron_flags_approved_permit(self):
        permit = self._make_permit()
        permit.action_submit()
        permit.action_approve()
        permit.expiry_date = fields_date_soon()
        self.env["event.permit"]._cron_flag_permit_deadlines()
        activities = permit.activity_ids.filtered(
            lambda a: (a.summary or "") == "Permit expiring soon")
        self.assertEqual(len(activities), 1)

    def test_generate_from_template_is_idempotent(self):
        event_type = self.env["event.type"].create({"name": "Pride Festival"})
        self.env["event.type.permit.template"].create({
            "event_type_id": event_type.id,
            "name": "Street Closure Permit",
            "permit_type": "street_closure",
            "days_before_start": 45,
        })
        self.event.event_type_id = event_type

        created = self.env["event.permit"]._generate_permits_for_event(self.event)
        self.assertEqual(len(created), 1)
        self.assertEqual(
            created.submit_by_date,
            (self.event.date_begin - timedelta(days=45)).date())

        # Running again shouldn't duplicate.
        created_again = self.env["event.permit"]._generate_permits_for_event(
            self.event)
        self.assertFalse(created_again)
        self.assertEqual(
            self.env["event.permit"].search_count(
                [("event_id", "=", self.event.id)]),
            1)


def fields_date_soon():
    return (datetime.now() + timedelta(days=3)).date()
