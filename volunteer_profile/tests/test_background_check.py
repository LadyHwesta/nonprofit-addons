# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBackgroundCheck(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Screened Sam"})
        cls.today = fields.Date.context_today(cls.env.user)

    def test_clear_sets_dates_and_validity(self):
        self.partner.action_mark_background_cleared()
        self.assertEqual(self.partner.background_check_state, "cleared")
        self.assertEqual(self.partner.background_check_date, self.today)
        self.assertEqual(
            self.partner.background_check_expiry,
            self.today + relativedelta(months=24))
        self.assertTrue(self.partner.background_check_valid)

    def test_cron_expires_lapsed(self):
        self.partner.write({
            "background_check_state": "cleared",
            "background_check_date": self.today - relativedelta(years=3),
            "background_check_expiry": self.today - relativedelta(days=1),
        })
        self.assertFalse(self.partner.background_check_valid)
        self.env["res.partner"]._cron_flag_background_checks()
        self.assertEqual(self.partner.background_check_state, "expired")

    def test_cron_raises_activity_for_expiring(self):
        coordinator = self.env["res.users"].create({
            "name": "Coord", "login": "vp_coord",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
        })
        self.env.company.volunteer_coordinator_id = coordinator
        self.partner.write({
            "background_check_state": "cleared",
            "background_check_expiry": self.today + relativedelta(days=10),
        })
        self.env["res.partner"]._cron_flag_background_checks()
        todo = self.partner.activity_ids.filtered(
            lambda a: "Background check expiring" in (a.summary or ""))
        self.assertTrue(todo)
        self.assertEqual(todo.user_id, coordinator)
        # a second run does not pile on another
        self.env["res.partner"]._cron_flag_background_checks()
        self.assertEqual(len(self.partner.activity_ids.filtered(
            lambda a: "Background check expiring" in (a.summary or ""))), 1)

    def test_search_background_check_valid(self):
        self.partner.action_mark_background_cleared()
        other = self.env["res.partner"].create({"name": "Unscreened"})
        found = self.env["res.partner"].search([
            ("background_check_valid", "=", True), ("id", "in",
             [self.partner.id, other.id])])
        self.assertEqual(found, self.partner)

    def test_waiver_currency(self):
        self.partner.action_sign_waiver()
        self.assertTrue(self.partner.waiver_current)
        self.partner.waiver_date = self.today - relativedelta(months=18)
        self.assertFalse(self.partner.waiver_current)
