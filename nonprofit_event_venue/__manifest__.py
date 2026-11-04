# -*- coding: utf-8 -*-
{
    "name": "Event Venue Map",
    "version": "19.0.1.1.0",
    "category": "Marketing/Events",
    "summary": "Row/spot vendor placement with a live OpenStreetMap vendor map",
    "description": """
Event Venue Map
===============

Extends *Events Booths* (``event_booth``): give every booth a plain
**row + spot number** and a real venue map fills itself in.

* **Rows** (``event.venue.row``) - one per row/section of the venue,
  ordered by sequence.
* A **calibration wizard** - read two real-world coordinates off Google
  Maps/OpenStreetMap/a phone GPS and it works out the venue's bearing and
  spacing for you, no trigonometry required.
* Every booth then just needs a row + spot number; its latitude/longitude
  are computed automatically from the calibration.
* A live **Vendor Map** (OpenStreetMap tiles via a vendored Leaflet.js,
  no external service account needed) showing every booth as a colored
  pin, click-through to the booth record.
* A **Vendor Load-In Manifest** PDF - booths grouped by row in spot order,
  for morning-of setup.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["event_booth"],
    "data": [
        "security/nonprofit_event_venue_security.xml",
        "security/ir.model.access.csv",
        "wizard/venue_map_calibrate_views.xml",
        "report/vendor_manifest_report.xml",
        "report/vendor_requirements_report.xml",
        "views/event_venue_row_views.xml",
        "views/event_booth_views.xml",
        "views/vendor_map_action.xml",
        "views/event_event_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "nonprofit_event_venue/static/lib/leaflet/leaflet.css",
            "nonprofit_event_venue/static/lib/leaflet/leaflet.js",
            "nonprofit_event_venue/static/src/venue_map/venue_map_action.scss",
            "nonprofit_event_venue/static/src/venue_map/venue_map_action.js",
            "nonprofit_event_venue/static/src/venue_map/venue_map_action.xml",
        ],
    },
    "application": False,
}
