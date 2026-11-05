# -*- coding: utf-8 -*-
{
    "name": "Event Parade Lineup",
    "version": "19.0.1.2.1",
    "category": "Marketing/Events",
    "summary": "Public parade-entry applications, staging areas and a lineup sheet",
    "description": """
Event Parade Lineup
====================

* A **public application page** (``/event/<id>/parade/apply``, no login
  required) where a community group applies for a parade entry - unit
  name, type, size, special requirements, a click-through liability
  waiver. Submitting raises a To-Do for the parade coordinator and emails
  the applicant a confirmation.
* Coordinators **approve / reject / confirm** entries, assign a
  **staging area** and a lineup **order** (drag to reorder).
* A **"Set Step-Off Times"** wizard stamps every confirmed entry's
  step-off time sequentially, staging area by staging area.
* A **Parade Lineup Sheet** PDF - staging area, order, step-off time,
  unit, contact, special requirements - for marshals on parade morning.
* An **entry number** ("Assign Entry Numbers" gives every confirmed entry
  one, sequentially) plus two printable **Parade Entry List** PDFs (by
  number, by name) and a big, one-per-page **Entry Sign** PDF (8.5x11
  landscape) for holding up along the route.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["event", "mail", "website"],
    "data": [
        "security/nonprofit_event_parade_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "wizard/parade_step_off_wizard_views.xml",
        "report/parade_lineup_report.xml",
        "report/parade_entry_list_report.xml",
        "report/parade_entry_sign_report.xml",
        "views/event_parade_staging_area_views.xml",
        "views/event_parade_entry_views.xml",
        "views/portal_templates.xml",
        "views/event_event_views.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "nonprofit_event_parade/static/src/scss/parade_entry_sign_report.scss",
        ],
    },
    "application": False,
}
