# -*- coding: utf-8 -*-
{
    "name": "Event Entertainment",
    "version": "19.0.1.0.0",
    "category": "Marketing/Events",
    "summary": "A reusable performer roster, per-stage scheduling, and a printable Run of Show",
    "description": """
Event Entertainment
====================

The "stage-show" event category this suite has always meant to cover,
alongside vendor booths (``nonprofit_event_venue``), the parade
(``nonprofit_event_parade``), and day-of logistics
(``nonprofit_event_logistics``).

* A reusable **Performer roster** (``event.performer``) - contact,
  genre, a default set length, and technical rider notes carry across
  every event a recurring act plays, instead of being re-typed each
  time.
* **Stages** (``event.stage``) - one event can have several
  independent schedules (Main Stage, Acoustic Tent, ...), each with
  its own start time and, optionally, a position on the existing
  Vendor Map (the same click-to-place-a-pin flow
  ``nonprofit_event_logistics`` already gives facilities).
* A **Run of Show** (``event.run_of_show.line``) per stage - an
  ordered, drag-to-reorder list of performance and announcement
  items. Each item's start/end time is computed automatically from
  set lengths, running forward from the stage's own start time. A
  "hard time" override on any item (e.g. "headliner must start at
  9:00 PM sharp") pushes every later item forward from there.
  Announcements (a raffle drawing, sponsor thank-yous, an MC
  intro) slot into the same ordered list as performances, at
  whatever point they're needed.
* Booked performers get a confirmation status (Invited / Confirmed /
  Declined / Cancelled), matching how ``nonprofit_event_logistics``
  already tracks crew/vendor confirmation.
* A printable **Run of Show** report, one per stage - the actual
  sheet a stage manager holds during the show.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["event", "mail", "nonprofit_event_venue"],
    "data": [
        "security/ir.model.access.csv",
        "views/event_performer_views.xml",
        "report/run_of_show_report.xml",
        "views/event_stage_views.xml",
        "views/event_event_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "nonprofit_event_entertainment/static/src/venue_map_stages/venue_map_stages_patch.scss",
            "nonprofit_event_entertainment/static/src/venue_map_stages/venue_map_stages_patch.js",
            "nonprofit_event_entertainment/static/src/venue_map_stages/venue_map_stages_patch.xml",
        ],
    },
    "application": False,
}
