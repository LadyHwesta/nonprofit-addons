# -*- coding: utf-8 -*-
{
    "name": "eLearning: Processing Donations",
    "version": "19.0.1.0.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: recording gifts, receipts, and donor reporting",
    "description": """
eLearning: Processing Donations
================================

A short, self-contained eLearning course for whoever records gifts and
runs donor reports - cash/check/restricted/in-kind donations, tax
receipts, fundraising events, and the LYBUNT/SYBUNT donor lists and
year-end contribution statements. Install this module and the course
appears in eLearning already built.

Only depends on ``donation_base`` + ``donation``.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": ["website_slides", "donation_base", "donation"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "application": False,
}
