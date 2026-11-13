# -*- coding: utf-8 -*-
{
    "name": "eLearning: Vendor Coordinator",
    "version": "19.0.1.2.1",
    "category": "Website/eLearning",
    "summary": "eLearning course: booths, the vendor map, and load-in reports",
    "description": """
eLearning: Vendor Coordinator
==============================

A short, self-contained eLearning course for whoever manages vendor
booths at an event - booth categories, row/spot addressing, needs-power
and double-wide spots, calibrating and reading the live Vendor Map, and
the printable load-in reports. Install this module and the course
appears in eLearning already built.

Only depends on ``nonprofit_event_venue``.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["website_slides", "nonprofit_elearning_theme", "nonprofit_event_venue"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "application": False,
}
