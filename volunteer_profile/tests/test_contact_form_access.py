# -*- coding: utf-8 -*-
from lxml import etree

from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestContactFormAccess(TransactionCase):
    """A Contact has to open for internal users with no Volunteer tier.

    The form's Volunteer tab holds a tag field on volunteer.skill, which
    only Volunteer tiers can read. The web client loads whatever the
    form lists, so showing that field to anyone else failed the whole
    form with an Access Error. Superuser skips access rights, so this
    has to run as the real user.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contact = cls.env["res.partner"].create({"name": "Sample Contact"})
        cls.plain_user = new_test_user(
            cls.env, login="vp_plain_user", groups="base.group_user")
        cls.viewer_user = new_test_user(
            cls.env, login="vp_viewer_user",
            groups="base.group_user,event_volunteer.group_volunteer_viewer")
        cls.volunteer_user = new_test_user(
            cls.env, login="vp_volunteer_user",
            groups="base.group_user,event_volunteer.group_volunteer_user")

    def _open_contact(self, user):
        """Load the form the way the web client does, return its fields."""
        partner = self.env["res.partner"].with_user(user)
        views = partner.get_views([(False, "form")])
        arch = etree.fromstring(views["views"]["form"]["arch"])
        names = {
            node.get("name") for node in arch.iter("field")
            if node.get("name") in partner._fields
        }
        spec = {
            name: {"fields": {"display_name": {}}}
            if partner._fields[name].relational else {}
            for name in names
        }
        partner.browse(self.contact.id).web_read(spec)
        return names

    def test_contact_opens_without_a_volunteer_tier(self):
        names = self._open_contact(self.plain_user)

        self.assertNotIn("volunteer_skill_ids", names)
        self.assertNotIn("background_check_state", names)

    def test_contact_opens_for_a_volunteer_viewer_without_the_tab(self):
        names = self._open_contact(self.viewer_user)

        self.assertNotIn("volunteer_skill_ids", names)

    def test_volunteer_managers_still_see_the_tab(self):
        names = self._open_contact(self.volunteer_user)

        self.assertIn("volunteer_skill_ids", names)
        self.assertIn("background_check_state", names)
