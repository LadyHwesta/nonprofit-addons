# -*- coding: utf-8 -*-
{
    "name": "eLearning: Volunteer Coordination",
    "version": "19.0.1.2.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: roles, shifts, screening, and volunteer hours",
    "description": """
eLearning: Volunteer Coordination
==================================

A short, self-contained eLearning course for whoever schedules and
screens volunteers - roles and shifts, recurring shifts, day-of check-in/
out and swaps, screening (skills/background checks/waivers/minors), and
hours reporting. Install this module and the course appears in eLearning
already built.

Only depends on ``event_volunteer`` + ``volunteer_shift`` +
``volunteer_profile``.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": [
        "website_slides", "nonprofit_elearning_theme",
        "event_volunteer", "volunteer_shift", "volunteer_profile",
    ],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "application": False,
}
