# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged

SCREENING_FIELDS = (
    "volunteer_skill_ids", "background_check_state", "background_check_date",
    "background_check_expiry", "background_check_valid",
    "background_check_expiring_soon", "waiver_signed", "waiver_date",
    "waiver_current", "is_minor", "guardian_id", "emergency_contact_name",
    "emergency_contact_phone", "tshirt_size", "volunteer_orientation_done",
    "volunteer_orientation_date",
)


@tagged("post_install", "-at_install")
class TestScreeningPrivacy(TransactionCase):
    """Screening data has to be closed to non-Volunteer users everywhere,
    not only hidden on the form, while sign-up checks keep working."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contact = cls.env["res.partner"].create({"name": "Sample Contact"})
        cls.plain = new_test_user(
            cls.env, login="sp_plain",
            groups="base.group_user,base.group_partner_manager")
        cls.viewer = new_test_user(
            cls.env, login="sp_viewer",
            groups="base.group_user,event_volunteer.group_volunteer_viewer")
        cls.manager = new_test_user(
            cls.env, login="sp_manager",
            groups="base.group_user,event_volunteer.group_volunteer_user")
        cls.portal = new_test_user(
            cls.env, login="sp_portal", groups="base.group_portal")
        cls.role = cls.env["event.volunteer.role"].create({
            "event_id": cls.env["event.event"].create({
                "name": "Clinic Day",
                "date_begin": "2030-01-01 09:00:00",
                "date_end": "2030-01-01 17:00:00",
            }).id,
            "name": "Nurse", "slot_count": 1,
            "requires_background_check": True,
        })

    def test_every_field_refuses_anyone_who_does_not_manage_volunteers(self):
        for user in (self.plain, self.viewer):
            contact = self.contact.with_user(user)
            for name in SCREENING_FIELDS:
                with self.subTest(user=user.login, field=name), \
                        self.assertRaises(AccessError):
                    contact.read([name])

    def test_searching_on_screening_refuses_a_user_without_a_tier(self):
        partners = self.env["res.partner"].with_user(self.plain)
        with self.assertRaises(AccessError):
            partners.search([("background_check_state", "=", "cleared")])

    def test_people_who_manage_volunteers_can_read(self):
        values = self.contact.with_user(self.manager).read(
            list(SCREENING_FIELDS))[0]
        self.assertEqual(values["background_check_state"], "none")

    def test_tracked_changes_hide_from_a_user_without_a_tier(self):
        self.contact.action_mark_background_cleared()
        self.env.flush_all()
        self.env.cr.precommit.run()
        trackings = self.contact.message_ids.sudo().tracking_value_ids
        self.assertTrue(trackings)

        self.assertFalse(trackings._filter_has_field_access(
            self.env(user=self.plain)))
        self.assertFalse(trackings._filter_has_field_access(
            self.env(user=self.viewer)))
        self.assertTrue(trackings._filter_has_field_access(
            self.env(user=self.manager)))
        # Email notifications must leave them out too.
        self.assertFalse(trackings._filter_free_field_access())

    def test_user_without_a_tier_can_still_work_with_contacts(self):
        partners = self.env["res.partner"].with_user(self.plain)

        created = partners.create({"name": "New Contact"})
        created.write({"name": "Renamed Contact"})
        created.copy()

        self.assertEqual(created.name, "Renamed Contact")

    def test_duplicating_a_contact_leaves_screening_behind(self):
        self.contact.action_mark_background_cleared()
        self.contact.write({"is_minor": True,
                            "emergency_contact_name": "Next Of Kin"})

        duplicate = self.contact.copy()

        self.assertEqual(duplicate.background_check_state, "none")
        self.assertFalse(duplicate.is_minor)
        self.assertFalse(duplicate.emergency_contact_name)

    def test_portal_eligibility_check_still_works(self):
        partner = self.env["res.partner"].with_user(self.portal).browse(
            self.portal.partner_id.id)
        role = self.role.sudo()

        self.assertTrue(partner._volunteer_eligibility_errors(role))

        self.portal.partner_id.action_mark_background_cleared()
        self.env.invalidate_all()
        self.assertFalse(partner._volunteer_eligibility_errors(role))

    def test_portal_can_read_a_skill(self):
        skill = self.env.ref("volunteer_profile.skill_first_aid")

        self.assertEqual(
            skill.with_user(self.portal).read(["partner_count"])[0]["id"],
            skill.id)

    def test_search_filters_only_show_with_a_tier(self):
        def filters(user):
            view = self.env.ref("base.view_res_partner_filter")
            search = self.env["res.partner"].with_user(user).get_view(
                view_id=view.id, view_type="search")["arch"]
            return "bgcheck_ok" in search

        self.assertFalse(filters(self.plain))
        self.assertFalse(filters(self.viewer))
        self.assertTrue(filters(self.manager))

    def test_waiver_report_only_offered_with_a_tier(self):
        def offered(user):
            actions = self.env["ir.actions.actions"].with_user(user)
            bindings = actions.get_bindings("res.partner").get("report", [])
            waiver = self.env.ref("volunteer_profile.action_report_volunteer_waiver")
            return any(b["id"] == waiver.id for b in bindings)

        self.assertFalse(offered(self.plain))
        self.assertFalse(offered(self.viewer))
        self.assertTrue(offered(self.manager))

    def test_viewer_gets_no_buttons_that_search_on_screening(self):
        shift = self.env["volunteer.shift"].with_user(self.viewer).get_view(
            view_type="form")["arch"]
        skill = self.env["volunteer.skill"].with_user(self.viewer).get_view(
            view_type="form")["arch"]

        self.assertNotIn("action_suggest_volunteers", shift)
        self.assertNotIn("action_view_volunteers", skill)
