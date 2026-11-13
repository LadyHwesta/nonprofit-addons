# -*- coding: utf-8 -*-
{
    "name": "eLearning: Managing Grants",
    "version": "19.0.1.0.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: the Grants app, from prospect to final report",
    "description": """
eLearning: Managing Grants
==========================

A short, self-contained eLearning course for whoever writes and looks
after grants: the pipeline and deadlines, awarding a grant and its fund,
invoicing the funder, spending and releasing restricted money, and the
reports the funder needs. Install this module and the course appears in
eLearning already built.

Only depends on ``nonprofit_grant``.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["website_slides", "nonprofit_elearning_theme", "nonprofit_grant"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "application": False,
}
