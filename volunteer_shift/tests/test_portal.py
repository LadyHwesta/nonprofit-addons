# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestVolunteerShiftPortal(HttpCase):
    def test_my_shifts_page(self):
        user = self.env["res.users"].create({
            "name": "Portal Vol", "login": "portal_vol", "password": "portal_vol",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })
        partner = user.partner_id
        event = self.env["event.event"].create({
            "name": "Coat Drive",
            "date_begin": datetime.now() + timedelta(days=3),
            "date_end": datetime.now() + timedelta(days=3, hours=6),
        })
        role = self.env["event.volunteer.role"].create({
            "event_id": event.id, "name": "Greeter", "use_shifts": True,
        })
        upcoming = self.env["volunteer.shift"].create({
            "role_id": role.id,
            "start": datetime.now() + timedelta(days=3),
            "stop": datetime.now() + timedelta(days=3, hours=3),
            "slot_count": 3,
        })
        past = self.env["volunteer.shift"].create({
            "role_id": role.id,
            "start": datetime.now() - timedelta(days=10),
            "stop": datetime.now() - timedelta(days=10) + timedelta(hours=2),
            "slot_count": 3,
        })
        self.env["event.volunteer.assignment"].create({
            "role_id": role.id, "shift_id": upcoming.id,
            "partner_id": partner.id, "state": "confirmed",
        })
        done = self.env["event.volunteer.assignment"].create({
            "role_id": role.id, "shift_id": past.id,
            "partner_id": partner.id, "state": "confirmed",
        })
        done.check_in = datetime.now() - timedelta(days=10)
        done.check_out = datetime.now() - timedelta(days=10) + timedelta(hours=2)

        self.authenticate("portal_vol", "portal_vol")
        resp = self.url_open("/my/shifts")
        self.assertEqual(resp.status_code, 200)
        body = resp.text
        self.assertIn("Coat Drive", body)
        self.assertIn("Greeter", body)
        self.assertIn("lifetime hours", body)

        home = self.url_open("/my")
        self.assertEqual(home.status_code, 200)
        self.assertIn("Volunteer Shifts", home.text)


@tagged("post_install", "-at_install")
class TestBackendAssets(HttpCase):
    """A dir named `vendor` on the addons path silently breaks
    web.assets_web; guard against it (see club_membership)."""

    def test_web_assets_web_compiles_without_scss_error(self):
        self.authenticate("admin", "admin")
        page = self.url_open("/odoo")
        self.assertEqual(page.status_code, 200)
        match = re.search(
            r'href="([^"]*web\.assets_web[^"]*\.css[^"]*)"', page.text)
        self.assertTrue(match, "web.assets_web stylesheet link not on /odoo")
        css = self.url_open(match.group(1))
        self.assertEqual(css.status_code, 200)
        self.assertNotIn("A css error occured", css.text)
        self.assertNotIn("css_error_message", css.text)
