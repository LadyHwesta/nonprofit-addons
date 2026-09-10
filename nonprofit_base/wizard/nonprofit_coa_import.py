# -*- coding: utf-8 -*-
import csv

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import file_open

CSV_PATH = "nonprofit_base/data/us_ucoa_nonprofit.csv"


class NonprofitCoaImportWizard(models.TransientModel):
    _name = "nonprofit.coa.import.wizard"
    _description = "Add Non-Profit Accounts"

    company_id = fields.Many2one(
        "res.company", string="Company", required=True,
        default=lambda self: self.env.company)
    code_prefix = fields.Char(
        string="Code Prefix",
        help="Prepended to every account code from the template, e.g. '9' turns "
             "'4000' into '94000'. Use this to keep the added accounts clear of "
             "the numbering your localisation chart already uses. Leave blank to "
             "import the codes as-is.")
    skip_existing = fields.Boolean(
        string="Skip Codes That Already Exist", default=True,
        help="On: an account whose (prefixed) code is already in use is left "
             "untouched and the rest are still imported. Off: the import stops "
             "with an error listing the clashes so you can pick a prefix.")

    created_count = fields.Integer(readonly=True)
    skipped_count = fields.Integer(readonly=True)
    result_summary = fields.Text(readonly=True)

    def _iter_template_rows(self):
        with file_open(CSV_PATH, "r") as csv_file:
            for row in csv.DictReader(csv_file):
                yield row

    def _resolve_tags(self, tag_xmlids):
        tags = self.env["account.account.tag"]
        for xmlid in filter(None, (tag_xmlids or "").split("|")):
            tags |= self.env.ref("nonprofit_base.%s" % xmlid.strip())
        return tags

    def action_import(self):
        self.ensure_one()
        company = self.company_id
        prefix = (self.code_prefix or "").strip()
        Account = self.env["account.account"].with_company(company)

        rows = list(self._iter_template_rows())
        target_codes = [prefix + r["code"] for r in rows]
        existing = Account.search([
            ("code", "in", target_codes),
            ("company_ids", "in", company.id),
        ])
        existing_codes = set(existing.mapped("code"))

        clashes = [c for c in target_codes if c in existing_codes]
        if clashes and not self.skip_existing:
            raise UserError(_(
                "These account codes already exist in %(company)s: %(codes)s.\n"
                "Set a code prefix, or tick 'Skip Codes That Already Exist'.",
                company=company.display_name, codes=", ".join(sorted(clashes))))

        created, skipped = self.env["account.account"], 0
        for row in rows:
            code = prefix + row["code"]
            if code in existing_codes:
                skipped += 1
                continue
            created |= Account.create({
                "code": code,
                "name": row["name"],
                "account_type": row["account_type"],
                "reconcile": row["reconcile"] not in ("", "0", "False", "false"),
                "company_ids": [fields.Command.link(company.id)],
                "tag_ids": [
                    fields.Command.set(self._resolve_tags(row["tag_xmlids"]).ids)
                ],
            })

        self.created_count = len(created)
        self.skipped_count = skipped
        self.result_summary = _(
            "%(created)d account(s) added to %(company)s, %(skipped)d skipped "
            "(already existed).",
            created=len(created), company=company.display_name, skipped=skipped)

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "views": [(self.env.ref(
                "nonprofit_base.nonprofit_coa_import_wizard_result_form").id, "form")],
            "target": "new",
        }

    def action_open_accounts(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Chart of Accounts"),
            "res_model": "account.account",
            "view_mode": "list,form",
            "domain": [("company_ids", "in", self.company_id.id)],
        }
