# -*- coding: utf-8 -*-
{
    "name": "Non-Profit Donation Receipts",
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "summary": "Donations' numbered tax receipts, printed as a US donor "
               "acknowledgement (EIN, each gift, goods-or-services values)",
    "description": """
Non-Profit Donation Receipts
============================

Installs itself when both the Donations app (OCA ``donation``) and
``nonprofit_reports`` are present, so donors get **one** yearly receipt:

* The Donations app's numbered, tracked tax receipts are printed with
  what a US donor needs to keep: the organization and its EIN, each gift
  with its date, the value of any goods or services received in return,
  and the IRS section 170(f)(8) acknowledgement wording.
* The separate Year-End Contribution Statements menu from
  ``nonprofit_reports`` is hidden while this is installed (it comes back
  if this is uninstalled). Without the Donations app, that statement is
  still the yearly receipt.
""",
    "author": "Tiesa",
    "license": "AGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["donation", "nonprofit_reports"],
    "data": [
        "data/menus.xml",
        "report/donation_tax_receipt_report.xml",
    ],
    "auto_install": True,
    "installable": True,
    "application": False,
    "uninstall_hook": "uninstall_hook",
}
