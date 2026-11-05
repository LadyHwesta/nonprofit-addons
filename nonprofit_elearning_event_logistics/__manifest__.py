# -*- coding: utf-8 -*-
{
    "name": "eLearning: Logistics Lead",
    "version": "19.0.1.2.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: permits, temp staff, crews, and facilities",
    "description": """
eLearning: Logistics Lead
===========================

A short, self-contained eLearning course for whoever handles permits,
temporary hourly staffing, crew bookings, and facilities - building a
permit checklist, staff shift check-in/out, crew day-of contacts, placing
facilities on the vendor map, and reading the Logistics tab's readiness
numbers. Install this module and the course appears in eLearning already
built.

Only depends on ``nonprofit_event_logistics``.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["website_slides", "nonprofit_elearning_theme", "nonprofit_event_logistics"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "application": False,
}
