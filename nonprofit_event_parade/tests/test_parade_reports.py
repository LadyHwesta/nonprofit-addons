# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestParadeReports(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create({
            "name": "Pride Parade 2027",
            "date_begin": datetime.now() + timedelta(days=90),
            "date_end": datetime.now() + timedelta(days=90, hours=6),
            "parade_enabled": True,
        })
        cls.area = cls.env["event.parade.staging.area"].create({
            "event_id": cls.event.id, "name": "Lot A",
        })

    def _confirmed_entry(self, name, sequence=10):
        entry = self.env["event.parade.entry"].create({
            "event_id": self.event.id, "name": name,
            "contact_name": "Contact", "contact_email": "c@example.com",
            "waiver_accepted": True, "staging_area_id": self.area.id,
            "sequence": sequence,
        })
        entry.action_approve()
        entry.action_confirm()
        return entry

    def test_entry_number_uniqueness(self):
        e1 = self._confirmed_entry("Alpha")
        e2 = self._confirmed_entry("Beta")
        e1.entry_number = 1
        with self.assertRaises(ValidationError):
            e2.entry_number = 1

    def test_zero_entry_number_does_not_collide(self):
        # Both left unnumbered (0) - must not be treated as a collision.
        e1 = self._confirmed_entry("Alpha")
        e2 = self._confirmed_entry("Beta")
        self.assertEqual(e1.entry_number, 0)
        self.assertEqual(e2.entry_number, 0)

    def test_auto_number_entries(self):
        e1 = self._confirmed_entry("Zebra Crew", sequence=20)
        e2 = self._confirmed_entry("Alpha Crew", sequence=10)
        self.event.action_auto_number_entries()
        # Ordered by staging area then sequence, not by name.
        self.assertEqual(e2.entry_number, 1)
        self.assertEqual(e1.entry_number, 2)

    def test_auto_number_requires_confirmed_entries(self):
        with self.assertRaises(UserError):
            self.event.action_auto_number_entries()

    def test_entry_list_reports_render(self):
        self._confirmed_entry("Alpha")
        self._confirmed_entry("Zebra")
        self.event.action_auto_number_entries()

        for xml_id in (
            "nonprofit_event_parade.action_report_parade_entry_list_by_number",
            "nonprofit_event_parade.action_report_parade_entry_list_by_name",
        ):
            report = self.env.ref(xml_id)
            html, content_type = self.env["ir.actions.report"]._render_qweb_html(
                report.report_name, [self.event.id])
            self.assertEqual(content_type, "html")
            self.assertIn(b"Alpha", html)
            self.assertIn(b"Zebra", html)

    def test_entry_sign_report_renders(self):
        entry = self._confirmed_entry("Rainbow Riders")
        entry.entry_number = 7
        report = self.env.ref(
            "nonprofit_event_parade.action_report_parade_entry_sign")
        html, content_type = self.env["ir.actions.report"]._render_qweb_html(
            report.report_name, [entry.id])
        self.assertEqual(content_type, "html")
        self.assertIn(b"Rainbow Riders", html)
        self.assertIn(b"7", html)

    def test_print_entry_signs_requires_confirmed_entries(self):
        with self.assertRaises(UserError):
            self.event.action_print_entry_signs()

    def test_print_entry_signs_action(self):
        self._confirmed_entry("Rainbow Riders")
        action = self.event.action_print_entry_signs()
        self.assertEqual(action["type"], "ir.actions.report")
