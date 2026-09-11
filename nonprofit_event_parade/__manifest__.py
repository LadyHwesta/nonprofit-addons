# -*- coding: utf-8 -*-
{
    "name": "Event Parade Lineup",
    "version": "19.0.1.0.0",
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
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["event", "mail", "website"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "wizard/parade_step_off_wizard_views.xml",
        "report/parade_lineup_report.xml",
        "views/event_parade_staging_area_views.xml",
        "views/event_parade_entry_views.xml",
        "views/portal_templates.xml",
        "views/event_event_views.xml",
    ],
    "application": False,
}
