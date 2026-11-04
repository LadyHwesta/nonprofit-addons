# -*- coding: utf-8 -*-
"""Move performance stages off core's ``event.stage`` model.

Versions before 19.0.1.1.0 declared ``_name = "event.stage"``, the name core
Odoo already uses for the event pipeline (New, Booked, Ended...). A second
``_name`` without ``_inherit`` replaces the existing model in the registry, so
core's fields such as ``pipe_end`` vanished at runtime and both models shared
the ``event_stage`` table.

This runs before the renamed model is set up, and:

* moves rows that belong to this module (they have an ``event_id``; core's
  pipeline stages never do) into their own table, keeping their ids so run of
  show lines stay attached,
* puts ``event_stage`` back the way core expects it,
* removes this module's external ids on core's model and on the fields it
  added. Left in place, the end-of-update cleanup would treat them as deleted
  data and unlink core's own ``ir.model`` record.
"""
import logging

_logger = logging.getLogger(__name__)

MODULE = "nonprofit_event_entertainment"
OWN_COLUMNS = ("event_id", "start_time", "latitude", "longitude", "notes")
OWN_FIELDS = OWN_COLUMNS + ("line_ids", "line_count")


def _column_type(cr, table, column):
    cr.execute(
        """SELECT data_type FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s""",
        (table, column),
    )
    row = cr.fetchone()
    return row[0] if row else None


def _move_stage_rows(cr):
    """Copy this module's rows out, then delete them from core's table.

    The new table can already exist: installing another module with this code
    on disk can make Odoo create it before this upgrade runs.
    """
    if _column_type(cr, "event_stage", "name") == "jsonb":
        name_sql = """CASE WHEN jsonb_typeof(name) = 'object'
                           THEN COALESCE(name->>'en_US',
                                         (SELECT value FROM jsonb_each_text(name) LIMIT 1))
                           ELSE name #>> '{}' END"""
    else:
        name_sql = "name"

    cr.execute("""
        CREATE TABLE IF NOT EXISTS event_entertainment_stage (
            id SERIAL PRIMARY KEY,
            event_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            sequence INTEGER,
            start_time TIMESTAMP NOT NULL,
            latitude NUMERIC,
            longitude NUMERIC,
            notes TEXT,
            create_uid INTEGER,
            create_date TIMESTAMP,
            write_uid INTEGER,
            write_date TIMESTAMP
        )
    """)
    cr.execute(f"""
        INSERT INTO event_entertainment_stage
            (id, event_id, name, sequence, start_time, latitude, longitude,
             notes, create_uid, create_date, write_uid, write_date)
        SELECT id, event_id, {name_sql}, sequence, start_time, latitude,
               longitude, notes, create_uid, create_date, write_uid, write_date
          FROM event_stage
         WHERE event_id IS NOT NULL
        ON CONFLICT (id) DO NOTHING
    """)
    moved = cr.rowcount
    cr.execute("""
        SELECT setval(pg_get_serial_sequence('event_entertainment_stage', 'id'),
                      GREATEST((SELECT COALESCE(MAX(id), 0) FROM event_entertainment_stage), 1))
    """)

    # Run of show lines keep their stage_id values, which now mean the new
    # table. The ORM adds the replacement foreign key when the model loads.
    cr.execute("""
        SELECT con.conname
          FROM pg_constraint con
          JOIN pg_class rel ON rel.oid = con.conrelid
          JOIN pg_class ref ON ref.oid = con.confrelid
         WHERE con.contype = 'f'
           AND rel.relname = 'event_run_of_show_line'
           AND ref.relname = 'event_stage'
    """)
    for (constraint,) in cr.fetchall():
        cr.execute(f'ALTER TABLE event_run_of_show_line DROP CONSTRAINT "{constraint}"')

    # An event could have landed in a performance stage, since the pipeline
    # lists every row. Send those to the first real pipeline stage.
    cr.execute("""
        UPDATE event_event
           SET stage_id = (SELECT id FROM event_stage
                            WHERE event_id IS NULL
                            ORDER BY sequence, id LIMIT 1)
         WHERE stage_id IN (SELECT id FROM event_stage WHERE event_id IS NOT NULL)
    """)
    repointed = cr.rowcount
    cr.execute("DELETE FROM event_stage WHERE event_id IS NOT NULL")
    _logger.info(
        "%s: moved %s performance stages, repointed %s events",
        MODULE, moved, repointed,
    )


def _restore_core_table(cr):
    for column in OWN_COLUMNS:
        cr.execute(f'ALTER TABLE event_stage DROP COLUMN IF EXISTS "{column}"')
    # This module's non-translated Char can have converted core's translated
    # name column to varchar.
    if _column_type(cr, "event_stage", "name") != "jsonb":
        cr.execute("""
            ALTER TABLE event_stage ALTER COLUMN name TYPE jsonb
            USING jsonb_build_object('en_US', name)
        """)


def _remove_metadata(cr):
    """Detach this module from core's model record, and delete its own fields."""
    cr.execute(
        """DELETE FROM ir_model_data
            WHERE module = %s AND model = 'ir.model'
              AND name = 'model_event_stage'""",
        (MODULE,),
    )
    cr.execute(
        """DELETE FROM ir_model_data
            WHERE module = %s AND model = 'ir.model.fields'
              AND name LIKE 'field\\_event\\_stage\\_\\_%%'""",
        (MODULE,),
    )
    # Odoo removes this module's old access rules at the end of the update
    # anyway. Doing it here means they can't briefly apply to core's stages.
    cr.execute(
        """DELETE FROM ir_model_access WHERE id IN (
               SELECT res_id FROM ir_model_data
                WHERE module = %s AND model = 'ir.model.access'
                  AND name LIKE 'access\\_event\\_stage\\_%%')""",
        (MODULE,),
    )
    cr.execute(
        """DELETE FROM ir_model_data
            WHERE module = %s AND model = 'ir.model.access'
              AND name LIKE 'access\\_event\\_stage\\_%%'""",
        (MODULE,),
    )
    cr.execute(
        """DELETE FROM ir_model_fields
            WHERE model = 'event.stage' AND name = ANY(%s)""",
        (list(OWN_FIELDS),),
    )


def migrate(cr, version):
    if not version or not _column_type(cr, "event_stage", "event_id"):
        return
    _move_stage_rows(cr)
    _restore_core_table(cr)
    _remove_metadata(cr)
