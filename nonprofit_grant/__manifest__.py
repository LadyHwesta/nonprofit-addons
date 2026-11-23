# -*- coding: utf-8 -*-
{
    "name": "Grants",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Grants from prospect to close-out: deadlines, awards, payments, reports and spending against the grant's own fund",
    "description": """
Grants
======

For the grants an organization applies for and receives.

* **Pipeline**: each grant moves through Prospect, Letter of Inquiry,
  Writing, Submitted, Awarded, Declined and Closed, on a kanban board,
  with the funder, program officer, amounts requested and awarded, and
  the application deadline (a to-do for the grant's owner).
* **Its own fund**: an awarded grant gets a restricted Fund (the suite's
  fund accounting) and, optionally, a Program, so every expense coded to
  it counts as spent from the grant. The grant shows awarded, received,
  spent and left to spend.
* **Payments**: the funder's expected installments, each turned into an
  invoice to the funder on the grants revenue account and tracked until
  it's paid.
* **Reports**: the narrative and financial reports the funder requires,
  with due dates and reminders, a calendar of every deadline, and the
  submitted report attached.
* **Funders**: contacts marked as funders, with their grants one click
  away.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["nonprofit_fund_accounting", "account", "mail"],
    "data": [
        "security/nonprofit_grant_security.xml",
        "security/ir.model.access.csv",
        "data/nonprofit_grant_stage_data.xml",
        "data/ir_sequence_data.xml",
        "views/nonprofit_grant_stage_views.xml",
        "views/nonprofit_grant_report_views.xml",
        "views/nonprofit_grant_payment_views.xml",
        "views/nonprofit_grant_views.xml",
        "views/res_partner_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": True,
}
