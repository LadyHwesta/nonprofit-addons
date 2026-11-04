# -*- coding: utf-8 -*-
"""Grant the tier matching the access each user had before this upgrade.

Events Administrators get this module's Manager tier, and Events Users get its
User tier. See pre-access_tiers.py for how they were captured.
"""
import logging

from odoo import SUPERUSER_ID, Command, api

_logger = logging.getLogger(__name__)

TABLE = "np_access_migration_logistics"


def migrate(cr, version):
    cr.execute("SELECT to_regclass(%s)", (TABLE,))
    if not cr.fetchone()[0]:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    Users = env["res.users"].with_context(active_test=False)
    cr.execute(f"""
        SELECT uid, BOOL_OR(old_group = 'group_event_manager')
          FROM {TABLE} GROUP BY uid
    """)
    rows = cr.fetchall()
    for is_manager, tier in ((True, "manager"), (False, "user")):
        users = Users.browse(
            [uid for uid, manager in rows if manager is is_manager]
        ).exists()
        group = env.ref(f"nonprofit_event_logistics.group_logistics_{tier}")
        users.write({"group_ids": [Command.link(group.id)]})
        _logger.info("%s: granted %s to %s users", "nonprofit_event_logistics", group.name, len(users))
    cr.execute(f"DROP TABLE {TABLE}")
