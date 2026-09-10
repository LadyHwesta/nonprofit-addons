# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNonprofitPartnerFields(TransactionCase):
    def test_org_fields(self):
        org = self.env["res.partner"].create({
            "name": "Helping Hands Inc",
            "is_company": True,
            "is_nonprofit_org": True,
            "nonprofit_org_type": "501c3",
            "tax_exempt_id": "12-3456789",
        })
        self.assertTrue(org.is_nonprofit_org)
        self.assertEqual(org.nonprofit_org_type, "501c3")

    def test_household_rollup(self):
        head = self.env["res.partner"].create({"name": "Jordan Rivers"})
        partner = self.env["res.partner"]
        partner.create({"name": "Alex Rivers", "household_id": head.id})
        partner.create({"name": "Sam Rivers", "household_id": head.id})

        self.assertEqual(head.household_member_count, 2)
        self.assertEqual(
            set(head.household_member_ids.mapped("name")),
            {"Alex Rivers", "Sam Rivers"})
