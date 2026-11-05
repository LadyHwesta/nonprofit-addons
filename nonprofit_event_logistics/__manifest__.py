# -*- coding: utf-8 -*-
{
    "name": "Event Logistics",
    "version": "19.0.1.2.2",
    "category": "Marketing/Events",
    "summary": "Permits, temp staff shifts, crew bookings and facility placement",
    "description": """
Event Logistics
================

The coordination layer stock Odoo doesn't have for permits, temporary
hourly staffing, and vendor/crew day-of logistics - while leaving
``project`` and ``purchase`` to do what they already do well.

* **Permits** (``event.permit``) - type, issuing authority, permit #,
  submit-by/approval/expiry dates, a deadline-reminder cron. A permit
  checklist template on the event type generates the same list every
  year for a recurring event.
* **Temporary staff shifts** (``event.staff.shift`` /
  ``event.staff.assignment``) - a role, a headcount, a time window,
  check-in/out with computed hours (no CE payroll app exists, so this
  produces clean hours for whoever runs payroll externally).
* **Crew bookings** (``event.crew.booking``) - the vendor/crew, service
  type, an optional linked Purchase Order, load-in/out times, and a
  day-of contact.
* **Facilities** (``event.facility``) - portable toilets, hand-wash
  stations, first aid, water stations - placed with a click-to-drop-pin
  mode added to the existing Vendor Map from ``nonprofit_event_venue``.
* A **Logistics tab** on the event with at-a-glance readiness numbers,
  and a consolidated, deduped coordinator To-Do when the event is
  approaching with open items.
* Starter reports for the logistics team: a **Permit Status Report**, a
  **Staffing Roster** (shift by shift, who's assigned), and a combined
  **Crew & Facilities Day-Of Sheet**.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["event", "mail", "purchase", "nonprofit_event_venue"],
    "data": [
        "security/nonprofit_event_logistics_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/event_permit_views.xml",
        "views/event_type_permit_template_views.xml",
        "views/event_staff_views.xml",
        "views/event_crew_booking_views.xml",
        "views/event_facility_views.xml",
        "report/permit_status_report.xml",
        "report/staffing_roster_report.xml",
        "report/crew_day_of_sheet_report.xml",
        "views/event_event_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "nonprofit_event_logistics/static/src/venue_map_facilities/venue_map_facilities_patch.scss",
            "nonprofit_event_logistics/static/src/venue_map_facilities/venue_map_facilities_patch.js",
            "nonprofit_event_logistics/static/src/venue_map_facilities/venue_map_facilities_patch.xml",
        ],
    },
    "application": False,
}
