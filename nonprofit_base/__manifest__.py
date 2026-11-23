# -*- coding: utf-8 -*-
{
    "name": "Non-Profit Base",
    "version": "19.0.1.2.0",
    "category": "Accounting",
    "summary": "Non-profit organisation and donor fields, fund/program/function/"
               "grant analytic plans, and an add-on US chart of accounts",
    "description": """
Non-Profit Base
===============

The foundation the rest of the non-profit suite builds on.

* **Partner fields** - mark an organisation as a non-profit (501(c)(3),
  501(c)(4), church, school, government...), record its EIN, classify a
  donor (individual / household / foundation / corporation / government),
  set do-not-solicit / -mail / -email consent flags, and group people
  into households.
* **Analytic plans as data** - *Fund*, *Program*, *Function* and *Grant*
  analytic plans, each with a starter set of accounts (Fund:
  Unrestricted / With Donor Restrictions - Purpose / - Time / Perpetual;
  Function: Program Services / Management & General / Fundraising).
  Fund accounting enforcement lives in ``nonprofit_fund_accounting``.
* **Add-on chart of accounts** - a wizard (*Accounting > Configuration >
  Add Non-Profit Accounts*) that layers a UCOA-derived non-profit account
  set - contributions, grants, special events, in-kind, functional
  expense pools, net-asset classes, restriction-release clearing -
  **onto** whatever localisation chart is already installed. It never
  touches the localisation template, skips codes that already exist, and
  is safe to re-run. An optional code prefix keeps the added accounts out
  of the localisation's numbering.

Accounts carry ``account.account.tag`` records that the
``nonprofit_reports`` MIS templates and the Form 990 functional-expense
schedule key off.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["account", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "data/account_account_tag.xml",
        "data/analytic_plan.xml",
        "views/res_partner_views.xml",
        "wizard/nonprofit_coa_import_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
