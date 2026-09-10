# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import ReportsCommon


@tagged("post_install", "-at_install")
class TestDonorStatement(ReportsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.big = cls.env["res.partner"].create({"name": "Major Gift"})
        cls.small = cls.env["res.partner"].create({"name": "Small Gift"})
        cls._gift(cls.big, 400.0, cls.today)
        cls._gift(cls.big, 150.0, cls.today)   # total 550 >= 250
        cls._gift(cls.small, 50.0, cls.today)  # below 250 threshold

    def _wizard(self, **kw):
        vals = {
            "company_id": self.company.id,
            "date_from": self.today.replace(month=1, day=1),
            "date_to": self.today.replace(month=12, day=31),
        }
        vals.update(kw)
        return self.env["nonprofit.donor.statement.wizard"].create(vals)

    def test_candidate_filtering_by_min_amount(self):
        wizard = self._wizard()
        action = wizard.action_print()
        self.assertEqual(action["type"], "ir.actions.report")
        self.assertIn(self.big.id, action["context"]["active_ids"])
        self.assertNotIn(self.small.id, action["context"]["active_ids"])

    def test_report_values_totals(self):
        wizard = self._wizard(partner_ids=[(6, 0, [self.big.id])])
        data = {
            "wizard_id": wizard.id,
            "company_id": self.company.id,
            "date_from": str(wizard.date_from),
            "date_to": str(wizard.date_to),
        }
        values = self.env["report.nonprofit_reports.donor_statement"] \
            ._get_report_values([self.big.id], data)
        self.assertAlmostEqual(values["totals"][self.big.id], 550.0)
        self.assertEqual(len(values["gifts"][self.big.id]), 2)

    def test_render_html(self):
        # wkhtmltopdf may be absent in CI; exercise the template via HTML
        wizard = self._wizard()
        report = self.env.ref("nonprofit_reports.action_report_donor_statement")
        html, content_type = self.env["ir.actions.report"]._render_qweb_html(
            report.report_name, [self.big.id],
            data={
                "wizard_id": wizard.id,
                "company_id": self.company.id,
                "date_from": str(wizard.date_from),
                "date_to": str(wizard.date_to),
            })
        self.assertEqual(content_type, "html")
        self.assertIn(b"Contribution Statement", html)
        self.assertIn(b"Major Gift", html)
