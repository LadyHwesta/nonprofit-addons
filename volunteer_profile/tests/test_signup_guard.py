# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSignupGuard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.skill = cls.env.ref("volunteer_profile.skill_first_aid")
        cls.event = cls.env["event.event"].create({
            "name": "Clinic Day",
            "date_begin": datetime.now() + timedelta(days=5),
            "date_end": datetime.now() + timedelta(days=5, hours=8),
        })
        cls.role = cls.env["event.volunteer.role"].create({
            "event_id": cls.event.id, "name": "Nurse", "slot_count": 3,
            "requires_background_check": True, "requires_waiver": True,
            "required_skill_ids": [(6, 0, [cls.skill.id])],
        })
        cls.newbie = cls.env["res.partner"].create({"name": "Unready Uma"})
        cls.ready = cls.env["res.partner"].create({"name": "Ready Rhea"})
        cls.ready.action_mark_background_cleared()
        cls.ready.action_sign_waiver()
        cls.ready.volunteer_skill_ids = [(6, 0, [cls.skill.id])]

    def _assign(self, partner, **ctx):
        return self.env["event.volunteer.assignment"].with_context(**ctx).create({
            "role_id": self.role.id, "partner_id": partner.id,
            "state": "confirmed",
        })

    def test_backoffice_blocked_then_allowed(self):
        with self.assertRaises(ValidationError):
            self._assign(self.newbie)
        assignment = self._assign(self.ready)
        self.assertTrue(assignment)

    def test_skip_context_bypasses(self):
        assignment = self._assign(self.newbie, skip_volunteer_eligibility=True)
        self.assertTrue(assignment)

    def test_portal_role_signup_message(self):
        with self.assertRaises(UserError) as cm:
            self.role.action_portal_volunteer(self.newbie)
        msg = cm.exception.args[0]
        self.assertIn("background check", msg)
        self.assertIn("waiver", msg)
        self.assertIn("First Aid", msg)
        # ready volunteer goes through
        self.assertTrue(self.role.action_portal_volunteer(self.ready))

    def test_portal_shift_signup(self):
        self.role.use_shifts = True
        shift = self.env["volunteer.shift"].create({
            "role_id": self.role.id,
            "start": datetime.now() + timedelta(days=5),
            "stop": datetime.now() + timedelta(days=5, hours=4),
            "slot_count": 2,
        })
        with self.assertRaises(UserError):
            shift.action_portal_signup(self.newbie)
        self.assertTrue(shift.action_portal_signup(self.ready))

    def test_losing_clearance_after_signup(self):
        first = self._assign(self.ready)
        # losing the clearance doesn't retro-block the existing assignment
        self.ready.write({"background_check_state": "expired"})
        self.assertEqual(first.state, "confirmed")
        # but a fresh sign-up for the now-lapsed volunteer is refused
        second_role = self.env["event.volunteer.role"].create({
            "event_id": self.event.id, "name": "Nurse 2", "slot_count": 1,
            "requires_background_check": True,
        })
        with self.assertRaises(ValidationError):
            self.env["event.volunteer.assignment"].create({
                "role_id": second_role.id, "partner_id": self.ready.id,
                "state": "confirmed"})
