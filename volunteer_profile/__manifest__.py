# -*- coding: utf-8 -*-
{
    "name": "Volunteer Profile & Screening",
    "version": "19.0.1.0.2",
    "category": "Marketing/Events",
    "summary": "Volunteer skills, background-check tracking with expiry, "
               "liability waiver, minor/guardian, and role screening guards",
    "description": """
Volunteer Profile & Screening
=============================

Adds the volunteer-management side that events don't cover: who is
cleared to do what.

* **Skills** - a ``volunteer.skill`` taxonomy on the contact; a role can
  require skills, and a shift can *suggest volunteers* who have them and
  are free.
* **Background checks** - state (not started / requested / cleared /
  expired), clearance and expiry dates, a nightly job that flips lapsed
  clearances to *expired* and raises a To-Do for the volunteer
  coordinator ahead of expiry.
* **Liability waiver** - a printable QWeb waiver with an acceptance
  checkbox (no e-signature module), a *signed* flag with date, and a
  configurable validity period.
* **Minor / guardian**, emergency contact, T-shirt size, orientation
  done.
* **Screening guards** - a role or shift flagged *requires background
  check* / *requires waiver* refuses a sign-up (portal and back office)
  from a volunteer who isn't cleared or hasn't a current waiver, with a
  message saying exactly what's missing.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["volunteer_shift"],
    "data": [
        "security/ir.model.access.csv",
        "data/volunteer_skill_data.xml",
        "data/ir_cron.xml",
        "report/volunteer_waiver_report.xml",
        "views/volunteer_skill_views.xml",
        "views/res_partner_views.xml",
        "views/event_volunteer_views.xml",
        "views/volunteer_shift_views.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
