# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import ReportsCommon


@tagged("post_install", "-at_install")
class TestDonorReport(ReportsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.alice = cls.env["res.partner"].create({"name": "Alice Donor"})
        cls.bob = cls.env["res.partner"].create({"name": "Bob Lapsed"})
        cls.cleo = cls.env["res.partner"].create({"name": "Cleo Longlapsed"})

        cls._gift(cls.alice, 300.0, cls.last_year)
        cls._gift(cls.alice, 200.0, cls.today)
        cls._gift(cls.bob, 500.0, cls.last_year)          # LYBUNT
        cls._gift(cls.cleo, 500.0, cls.two_years_ago)     # SYBUNT only

    def _row(self, partner):
        return self.env["report.nonprofit.donor"].search([
            ("partner_id", "=", partner.id),
            ("company_id", "=", self.company.id),
        ])

    def test_lifetime_and_by_year(self):
        alice = self._row(self.alice)
        self.assertEqual(alice.gift_count, 2)
        self.assertAlmostEqual(alice.gift_total, 500.0)
        self.assertAlmostEqual(alice.this_year_total, 200.0)
        self.assertAlmostEqual(alice.last_year_total, 300.0)
        self.assertAlmostEqual(alice.prior_years_total, 0.0)
        self.assertEqual(alice.first_gift_date, self.last_year)
        self.assertEqual(alice.last_gift_date, self.today)

        cleo = self._row(self.cleo)
        self.assertAlmostEqual(cleo.prior_years_total, 500.0)
        self.assertAlmostEqual(cleo.this_year_total, 0.0)

    def test_lybunt_filter(self):
        lybunt = self.env["report.nonprofit.donor"].search([
            ("this_year_total", "<=", 0),
            ("last_year_total", ">", 0),
            ("company_id", "=", self.company.id),
        ])
        self.assertEqual(lybunt.partner_id, self.bob)

    def test_sybunt_filter(self):
        sybunt = self.env["report.nonprofit.donor"].search([
            ("this_year_total", "<=", 0),
            ("gift_total", ">", 0),
            ("company_id", "=", self.company.id),
        ])
        self.assertEqual(set(sybunt.partner_id.ids), {self.bob.id, self.cleo.id})

    def test_membership_not_counted(self):
        # a non-gift income account (membership) must not appear as a gift
        membership = self.env["account.account"].create({
            "code": "NFPMEMB",
            "name": "Membership Dues (test)",
            "account_type": "income",
            "company_ids": [(4, self.company.id)],
            "tag_ids": [(6, 0, [
                self.env.ref("nonprofit_base.tag_rev_membership").id])],
        })
        newbie = self.env["res.partner"].create({"name": "Dues Only"})
        self._gift(newbie, 75.0, self.today, account=membership)
        self.assertFalse(self._row(newbie))
