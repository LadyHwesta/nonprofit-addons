# -*- coding: utf-8 -*-
{
    "name": "eLearning: Access Rights and Roles",
    "version": "19.0.1.1.1",
    "category": "Website/eLearning",
    "summary": "eLearning course: choosing roles, what each one allows, and checking access",
    "description": """
eLearning: Access Rights and Roles
===================================

A short, self-contained eLearning course for whoever manages user accounts:
how roles and Viewer/User/Manager tiers fit together, what each one allows,
how to assign them, and how to check they work. Install this module and the
course appears in eLearning already built.

Only depends on ``nonprofit_roles``.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["website_slides", "nonprofit_elearning_theme", "nonprofit_roles"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "application": False,
}
