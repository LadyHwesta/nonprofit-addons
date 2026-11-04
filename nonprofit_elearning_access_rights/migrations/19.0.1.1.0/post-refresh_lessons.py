# -*- coding: utf-8 -*-
"""Update lessons whose facts changed when General Volunteer/Staff lost Events
User access.

The course data is noupdate, so a normal upgrade wouldn't change them. This
replaces these two lessons, including any local edits to them.
"""
from lxml import etree

from odoo import SUPERUSER_ID, api
from odoo.tools import file_open

MODULE = "nonprofit_elearning_access_rights"
LESSONS = ("lesson_core_events", "lesson_roles")


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    with file_open(f"{MODULE}/data/slide_channel_data.xml", "rb") as data:
        tree = etree.parse(data)
    for xml_id in LESSONS:
        lesson = env.ref(f"{MODULE}.{xml_id}", raise_if_not_found=False)
        if not lesson:
            continue
        field = tree.xpath(f"//record[@id='{xml_id}']/field[@name='html_content']")[0]
        lesson.html_content = "".join(
            etree.tostring(child, encoding="unicode") for child in field
        )
        lesson.name = tree.xpath(f"//record[@id='{xml_id}']/field[@name='name']")[0].text
