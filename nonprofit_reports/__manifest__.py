# -*- coding: utf-8 -*-
{
    "name": "Non-Profit Reports",
    "version": "19.0.1.1.0",
    "category": "Accounting",
    "summary": "Donor analytics (LYBUNT/SYBUNT), Form 990 functional-expense "
               "pivot, year-end contribution statements, and MIS Builder "
               "Statement of Activities / Financial Position templates",
    "description": """
Non-Profit Reports
==================

Reporting on top of ``nonprofit_base`` (and its account tags / analytic
plans).

* **Donor analytics** - ``report.nonprofit.donor`` is a read-only view
  with one row per donor: lifetime total, gift count, first / last /
  largest gift, and this-year / last-year / prior-year totals. List,
  pivot and graph views, plus **LYBUNT** (gave last year, nothing this
  year) and **SYBUNT** (gave some year, nothing this year) filters. Built
  from posted journal items on contribution-tagged income accounts, so it
  works with or without the ``donation`` module.
* **Form 990 functional-expense schedule** - a pivot of analytic items on
  the *Function* plan: natural expense account x Program / Management &
  General / Fundraising.
* **Year-end contribution statement** - a wizard and QWeb PDF, one
  statement per donor for a date range, listing each gift with the IRS
  written-acknowledgement and quid-pro-quo language. Also on the contact
  *Print* menu.
* **MIS Builder templates** - ``mis.report`` records and ready-to-run
  instances for a **Statement of Activities** (revenue by source, expense
  by function, change in net assets) and a **Statement of Financial
  Position** (assets, liabilities, net assets by restriction), keyed off
  the ``nonprofit_base`` account tags.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["nonprofit_base", "mis_builder"],
    "data": [
        "security/ir.model.access.csv",
        "report/nonprofit_donor_statement_report.xml",
        "wizard/nonprofit_donor_statement_views.xml",
        "views/nonprofit_donor_report_views.xml",
        "views/functional_expense_views.xml",
        "data/mis_report_statement_of_activities.xml",
        "data/mis_report_statement_of_financial_position.xml",
        "data/mis_report_instances.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
