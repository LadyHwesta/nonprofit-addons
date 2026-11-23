# -*- coding: utf-8 -*-
{
    "name": "Event Performer Payouts",
    "version": "19.0.1.0.0",
    "category": "Marketing/Events",
    "summary": "A fee on each booked performance and staff hours, turned into draft vendor bills (1099-NEC ready)",
    "description": """
Event Performer Payouts
=======================

Pays the people who make an event happen. Each performance in a stage's
Run of Show gets an agreed fee, and each confirmed staff assignment is paid
its hours times the shift's hourly rate. Create Bills turns what's owed
into draft vendor bills, one per person per event, ready to check and pay.
If the 1099 module (l10n_us_form_1099) is installed, a person billed this
way is marked as a 1099-NEC contractor, so the yearly 1099-NEC summary
totals them.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["account", "nonprofit_event_entertainment", "nonprofit_event_logistics"],
    "data": [
        "data/product_data.xml",
        "views/event_views.xml",
    ],
    "installable": True,
    "application": False,
}
