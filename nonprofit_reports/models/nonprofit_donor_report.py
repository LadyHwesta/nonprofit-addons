# -*- coding: utf-8 -*-
from odoo import fields, models

# Revenue tags that count as a "gift" for donor analytics.
GIFT_TAG_XMLIDS = (
    "nonprofit_base.tag_rev_contrib_unrestricted",
    "nonprofit_base.tag_rev_contrib_restricted",
    "nonprofit_base.tag_rev_grants",
    "nonprofit_base.tag_rev_special_events",
    "nonprofit_base.tag_rev_inkind",
)


class NonprofitDonorReport(models.Model):
    _name = "report.nonprofit.donor"
    _description = "Donor Analytics"
    _auto = False
    _rec_name = "partner_id"
    _order = "gift_total desc"

    partner_id = fields.Many2one("res.partner", string="Donor", readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    currency_id = fields.Many2one(related="company_id.currency_id")

    gift_total = fields.Monetary(string="Lifetime Giving", readonly=True)
    gift_count = fields.Integer(string="Gifts", readonly=True)
    first_gift_date = fields.Date(readonly=True)
    last_gift_date = fields.Date(readonly=True)
    largest_gift = fields.Monetary(readonly=True)
    this_year_total = fields.Monetary(string="This Year", readonly=True)
    last_year_total = fields.Monetary(string="Last Year", readonly=True)
    prior_years_total = fields.Monetary(string="Prior Years", readonly=True)

    def _gift_tag_ids(self):
        ids = []
        for xmlid in GIFT_TAG_XMLIDS:
            tag = self.env.ref(xmlid, raise_if_not_found=False)
            if tag:
                ids.append(tag.id)
        return ids or [0]

    @property
    def _table_query(self):
        tag_ids = ",".join(str(i) for i in self._gift_tag_ids())
        return """
            SELECT
                min(l.id) AS id,
                l.partner_id AS partner_id,
                l.company_id AS company_id,
                sum(-l.balance) AS gift_total,
                count(DISTINCT l.move_id) AS gift_count,
                min(l.date) AS first_gift_date,
                max(l.date) AS last_gift_date,
                max(-l.balance) AS largest_gift,
                COALESCE(sum(-l.balance) FILTER (
                    WHERE date_part('year', l.date) = date_part('year', CURRENT_DATE)
                ), 0) AS this_year_total,
                COALESCE(sum(-l.balance) FILTER (
                    WHERE date_part('year', l.date) = date_part('year', CURRENT_DATE) - 1
                ), 0) AS last_year_total,
                COALESCE(sum(-l.balance) FILTER (
                    WHERE date_part('year', l.date) < date_part('year', CURRENT_DATE) - 1
                ), 0) AS prior_years_total
            FROM account_move_line l
            JOIN account_move m ON m.id = l.move_id
            WHERE m.state = 'posted'
              AND l.partner_id IS NOT NULL
              AND l.account_id IN (
                  SELECT account_account_id FROM account_account_account_tag
                  WHERE account_account_tag_id IN (%s)
              )
            GROUP BY l.partner_id, l.company_id
        """ % tag_ids
