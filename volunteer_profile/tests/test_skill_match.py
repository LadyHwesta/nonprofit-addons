# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSkillMatch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_aid = cls.env.ref("volunteer_profile.skill_first_aid")
        cls.spanish = cls.env.ref("volunteer_profile.skill_spanish")
        cls.event = cls.env["event.event"].create({
            "name": "Outreach",
            "date_begin": datetime.now() + timedelta(days=2),
            "date_end": datetime.now() + timedelta(days=2, hours=8),
        })
        cls.role = cls.env["event.volunteer.role"].create({
            "event_id": cls.event.id, "name": "Translator-Medic",
            "use_shifts": True, "requires_background_check": True,
            "required_skill_ids": [(6, 0, [cls.first_aid.id, cls.spanish.id])],
        })
        cls.shift = cls.env["volunteer.shift"].create({
            "role_id": cls.role.id,
            "start": datetime.now() + timedelta(days=2),
            "stop": datetime.now() + timedelta(days=2, hours=4),
            "slot_count": 5,
        })

        def vol(name, skills, cleared=True):
            p = cls.env["res.partner"].create({"name": name})
            p.volunteer_skill_ids = [(6, 0, [s.id for s in skills])]
            if cleared:
                p.action_mark_background_cleared()
            return p

        cls.full = vol("Full Match", [cls.first_aid, cls.spanish])
        cls.partial = vol("Partial", [cls.first_aid])
        cls.uncleared = vol("No Check", [cls.first_aid, cls.spanish],
                            cleared=False)
        cls.busy = vol("Busy Betty", [cls.first_aid, cls.spanish])

        other_shift = cls.env["volunteer.shift"].create({
            "role_id": cls.role.id,
            "start": datetime.now() + timedelta(days=2, hours=1),
            "stop": datetime.now() + timedelta(days=2, hours=3),
            "slot_count": 2,
        })
        cls.env["event.volunteer.assignment"].create({
            "role_id": cls.role.id, "shift_id": other_shift.id,
            "partner_id": cls.busy.id, "state": "confirmed",
        })

    def test_suggestion_filters(self):
        action = self.shift.action_suggest_volunteers()
        suggested = set(action["domain"][0][2])
        self.assertIn(self.full.id, suggested)
        self.assertNotIn(self.partial.id, suggested)     # missing Spanish
        self.assertNotIn(self.uncleared.id, suggested)   # no background check
        self.assertNotIn(self.busy.id, suggested)        # overlapping shift

    def test_excludes_already_on_this_shift(self):
        self.env["event.volunteer.assignment"].create({
            "role_id": self.role.id, "shift_id": self.shift.id,
            "partner_id": self.full.id, "state": "confirmed",
        })
        action = self.shift.action_suggest_volunteers()
        self.assertNotIn(self.full.id, action["domain"][0][2])
