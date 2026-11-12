# -*- coding: utf-8 -*-
{
    "name": "Volunteer Shifts",
    "version": "19.0.1.2.0",
    "category": "Marketing/Events",
    "summary": "Break a volunteer role into timed shifts with check-in/out, "
               "hours tracking, recurring generation, swaps and a portal",
    "description": """
Volunteer Shifts
================

Extends *Event Volunteer Roles*: a role can be run as one whole-event
assignment (the default) or broken into **shifts** - a role, a time
window and a slot count.

* **Shifts** (``volunteer.shift``) with live filled / needed counts and an
  empty / partial / full / over badge, on the event form and a calendar.
* **Check-in / check-out** on the assignment - actual hours are computed
  and stored; a **no-show** flag.
* **Recurring shifts** - ``volunteer.shift.template`` lines on an event
  type (weekday, start time, length, role, slots); a nightly cron
  materialises them for events inside the generation horizon, once.
* **Portal** ``/my/shifts`` - a volunteer's upcoming and past shifts,
  lifetime hours, self check-in / out while a shift is on, and shift-swap
  offers other volunteers can claim (coordinator approves).
* **Hours reporting** - ``report.volunteer.hours`` (pivot / graph by
  volunteer, event, event type) and a per-volunteer **annual hours
  certificate** PDF.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["event_volunteer", "portal"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/volunteer_shift_views.xml",
        "views/event_volunteer_views.xml",
        "views/volunteer_shift_swap_views.xml",
        "report/volunteer_hours_report_views.xml",
        "report/volunteer_hours_certificate_report.xml",
        "wizard/volunteer_hours_certificate_views.xml",
        "views/res_config_settings_views.xml",
        "views/volunteer_shift_portal_templates.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
