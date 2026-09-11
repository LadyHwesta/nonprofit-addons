# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta

from odoo.tests import HttpCase, tagged

CSRF_RE = re.compile(rb'name="csrf_token" value="([^"]+)"')


@tagged("post_install", "-at_install")
class TestParadePortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create({
            "name": "Pride Parade 2027",
            "date_begin": datetime.now() + timedelta(days=90),
            "date_end": datetime.now() + timedelta(days=90, hours=6),
            "parade_enabled": True,
        })

    def test_apply_form_loads(self):
        resp = self.url_open("/event/%s/parade/apply" % self.event.id)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Parade Entry Application", resp.content)

    def test_submit_creates_entry_and_dedupes_partner(self):
        existing = self.env["res.partner"].create({
            "name": "Jamie Rivera", "email": "jamie@example.com",
        })
        csrf_token = self._get_csrf_token()
        self.url_open(
            "/event/%s/parade/apply/submit" % self.event.id,
            data={
                "csrf_token": csrf_token,
                "name": "Rainbow Riders",
                "contact_name": "Jamie Rivera",
                "contact_email": "jamie@example.com",
                "entry_type": "walking_group",
                "participant_count": "12",
                "waiver_accepted": "1",
            },
        )
        entry = self.env["event.parade.entry"].search(
            [("event_id", "=", self.event.id), ("name", "=", "Rainbow Riders")])
        self.assertTrue(entry)
        self.assertEqual(entry.state, "submitted")
        self.assertEqual(entry.partner_id, existing)
        self.assertEqual(entry.participant_count, 12)

    def test_submit_without_waiver_shows_error(self):
        csrf_token = self._get_csrf_token()
        resp = self.url_open(
            "/event/%s/parade/apply/submit" % self.event.id,
            data={
                "csrf_token": csrf_token,
                "name": "No Waiver Crew",
                "contact_name": "Alex",
                "contact_email": "alex@example.com",
            },
        )
        self.assertIn(b"accept the liability waiver", resp.content)
        entry = self.env["event.parade.entry"].search(
            [("name", "=", "No Waiver Crew")])
        self.assertFalse(entry)

    def test_deadline_closes_the_form(self):
        self.event.parade_entry_deadline = datetime.now() - timedelta(days=1)
        csrf_token = self._get_csrf_token()
        resp = self.url_open(
            "/event/%s/parade/apply/submit" % self.event.id,
            data={
                "csrf_token": csrf_token,
                "name": "Late Crew",
                "contact_name": "Alex",
                "contact_email": "alex@example.com",
                "waiver_accepted": "1",
            },
        )
        self.assertIn(b"closed", resp.content)
        entry = self.env["event.parade.entry"].search(
            [("name", "=", "Late Crew")])
        self.assertFalse(entry)

    def _get_csrf_token(self):
        # The test client's opener carries the session cookie across
        # requests, so the token embedded in this GET's form is valid for
        # a following POST from the same client.
        resp = self.url_open("/event/%s/parade/apply" % self.event.id)
        match = CSRF_RE.search(resp.content)
        self.assertTrue(match, "csrf token not found in the apply page")
        return match.group(1).decode()
