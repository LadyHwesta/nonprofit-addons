# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api
from odoo.tools import convert_file


def migrate(cr, version):
    """The course data is noupdate, so reload it to bring the roles table up
    to date with Grants (2026-11-13). This replaces any hand edits made to
    these lessons."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    convert_file(
        env, "nonprofit_elearning_access_rights", "data/slide_channel_data.xml", {},
        mode="init", noupdate=True)
