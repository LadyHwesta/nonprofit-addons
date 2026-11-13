# -*- coding: utf-8 -*-
{
    "name": "eLearning: Parade Coordinator",
    "version": "19.0.1.2.1",
    "category": "Website/eLearning",
    "summary": "eLearning course: parade applications, staging, lineup, and signs",
    "description": """
eLearning: Parade Coordinator
==============================

A short, self-contained eLearning course for whoever runs the parade -
turning on public applications, reviewing/approving entries, staging
areas and lineup order vs. entry number, the step-off-time wizard, and
the printable lineup sheet, entry lists, and entry signs. Install this
module and the course appears in eLearning already built.

Only depends on ``nonprofit_event_parade``.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["website_slides", "nonprofit_elearning_theme", "nonprofit_event_parade"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "application": False,
}
