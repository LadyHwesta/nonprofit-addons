# -*- coding: utf-8 -*-
{
    "name": "eLearning: Fund Accounting for Treasurers",
    "version": "19.0.1.3.2",
    "category": "Website/eLearning",
    "summary": "eLearning course: funds, programs, functions, and board/IRS reporting",
    "description": """
eLearning: Fund Accounting for Treasurers
==========================================

A short, self-contained eLearning course (Odoo's *eLearning* app) for
whoever records money and pulls board/990 reports - covers the Fund/
Program/Function/Grant model, recording a vendor bill against a fund,
releasing restricted funds, and the board and IRS reports. Install this
module and the course appears in eLearning already built - nothing to
author by hand.

Only depends on ``nonprofit_base`` + ``nonprofit_fund_accounting`` - an
org that doesn't run donations or events doesn't need to install
anything else to get this course.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": [
        "website_slides", "nonprofit_elearning_theme",
        "nonprofit_base", "nonprofit_fund_accounting",
    ],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "application": False,
}
