# -*- coding: utf-8 -*-
{
    "name": "Non-Profit Fund Accounting",
    "version": "19.0.1.1.0",
    "category": "Accounting",
    "summary": "Enforce a Fund analytic account on income/expense postings, "
               "release donor restrictions with a balanced entry, and roll "
               "net assets forward by fund",
    "description": """
Non-Profit Fund Accounting
==========================

Builds on ``nonprofit_base`` to turn the *Fund* analytic plan into real
fund accounting.

* **Fund required on income & expense** - with *Require a Fund on
  income/expense postings* enabled (per company), an ``account.move``
  cannot be posted while any income or expense line is not assigned 100%
  to *Fund* analytic accounts. Bypass for opening balances / migrations
  with ``skip_fund_check`` in the context.
* **Release from restriction** - a wizard picks a restricted Fund, an
  amount, a date and (optionally) a Program / Function, then posts a
  balanced journal entry between the two *Net Assets Released* clearing
  accounts, carrying the from- and to-Fund analytic accounts. Each
  release is kept as a ``nonprofit.restriction.release`` record.
* **Net-asset roll-forward** - a report that shows, per Fund, the
  beginning balance, revenue, expense, restrictions released in / out and
  the ending balance over a date range.
* **Settings** - the require-a-Fund toggle, a default Program and
  Function, and the two release clearing accounts (auto-detected from the
  ``nonprofit_base`` chart when present).
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["nonprofit_base"],
    "post_init_hook": "_autodetect_release_accounts",
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/nonprofit_restriction_release_views.xml",
        "wizard/nonprofit_net_assets_report_views.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
