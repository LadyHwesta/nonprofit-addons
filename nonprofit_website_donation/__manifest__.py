# -*- coding: utf-8 -*-
{
    'name': 'Nonprofit: Website Donations as Donations',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Donations',
    'summary': "Online gifts from the website's Donation block become donations, with receipts",
    'description': """
Nonprofit: Website Donations as Donations
=========================================

Odoo's website Donation block takes the money, but the gift never reaches
the Donations app: no donation record, no donor history, no tax receipt.
This module closes that gap. When an online donation is paid:

- the donor becomes (or is matched to, by email) a contact, instead of the
  website's anonymous visitor;
- a donation is created and validated in the Donations app, so it appears in
  donor history and reports and gets its numbered tax receipt as usual;
- if the donor chose to cover the processing fees (module "Donations: Donor
  Covers the Fees"), the donation has two lines: the gift, and the fees the
  donor covered. Both are on the receipt by default; untick "Is Eligible for a
  Tax Receipt" on the fees product if your accountant advises otherwise;
- the donation's journal entry is matched to the online payment, so the money
  is booked once.

If anything stops the donation from being created (for example a missing
account), the payment still goes through and a note on it says what to fix.
""",
    'author': 'Tiesa',
    'website': 'https://meskis.net',
    'license': 'AGPL-3',
    'support': 'sales@meskis.net',
    'depends': ['donation', 'website_payment'],
    'data': [
        'data/product_data.xml',
        'views/donation_views.xml',
    ],
    'installable': True,
}
