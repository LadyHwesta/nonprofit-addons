# -*- coding: utf-8 -*-
{
    "name": "eLearning: Stage Manager",
    "version": "19.0.1.0.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: the performer roster, stages, and running a show",
    "description": """
eLearning: Stage Manager
=========================

A short, self-contained eLearning course for whoever runs live performances at
an event: the performer roster, stages, building a Run of Show, hard times, and
the printed sheet. Install this module and the course appears in eLearning
already built.

Only depends on ``nonprofit_event_entertainment``.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["website_slides", "nonprofit_elearning_theme", "nonprofit_event_entertainment"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "application": False,
}
