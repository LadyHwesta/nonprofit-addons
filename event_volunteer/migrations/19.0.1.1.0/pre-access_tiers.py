# -*- coding: utf-8 -*-
"""Remember who had event access before this module got its own tiers.

Older versions granted access through core's Events groups. This version's
access rules use this module's own groups instead, so existing users would
lose access on upgrade. The post script grants them the matching tier.

Databases that already have the tier groups are skipped, so access an admin
has since set by hand isn't widened again.
"""
TABLE = "np_access_migration_volunteer"


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """SELECT 1 FROM ir_model_data
            WHERE module = %s AND model = 'res.groups' AND name = %s""",
        ("event_volunteer", "group_volunteer_viewer"),
    )
    if cr.fetchone():
        return
    cr.execute(f"DROP TABLE IF EXISTS {TABLE}")
    cr.execute(f"""
        CREATE TABLE {TABLE} AS
        WITH RECURSIVE implying(old_group, gid) AS (
            SELECT d.name, d.res_id
              FROM ir_model_data d
             WHERE d.module = 'event' AND d.model = 'res.groups'
               AND d.name IN ('group_event_user', 'group_event_manager')
            UNION
            SELECT i.old_group, r.gid
              FROM implying i
              JOIN res_groups_implied_rel r ON r.hid = i.gid
        )
        SELECT DISTINCT i.old_group, rel.uid
          FROM implying i
          JOIN res_groups_users_rel rel ON rel.gid = i.gid
          JOIN res_users u ON u.id = rel.uid
         WHERE NOT COALESCE(u.share, FALSE)
    """)
