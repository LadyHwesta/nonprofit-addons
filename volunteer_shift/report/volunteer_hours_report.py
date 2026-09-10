# -*- coding: utf-8 -*-
from odoo import fields, models


class ReportVolunteerHours(models.Model):
    _name = "report.volunteer.hours"
    _description = "Volunteer Hours"
    _auto = False
    _order = "date desc"

    partner_id = fields.Many2one("res.partner", string="Volunteer", readonly=True)
    event_id = fields.Many2one("event.event", readonly=True)
    event_type_id = fields.Many2one(
        "event.type", string="Program", readonly=True)
    role_id = fields.Many2one("event.volunteer.role", string="Role", readonly=True)
    shift_id = fields.Many2one("volunteer.shift", readonly=True)
    date = fields.Date(readonly=True)
    year = fields.Integer(readonly=True)
    hours = fields.Float(readonly=True)
    assignment_count = fields.Integer(readonly=True)

    @property
    def _table_query(self):
        return """
            SELECT
                a.id AS id,
                a.partner_id AS partner_id,
                a.event_id AS event_id,
                e.event_type_id AS event_type_id,
                a.role_id AS role_id,
                a.shift_id AS shift_id,
                s.start::date AS date,
                date_part('year', s.start)::int AS year,
                a.hours AS hours,
                1 AS assignment_count
            FROM event_volunteer_assignment a
            JOIN volunteer_shift s ON s.id = a.shift_id
            JOIN event_event e ON e.id = a.event_id
            WHERE a.state <> 'cancelled'
              AND COALESCE(a.no_show, FALSE) = FALSE
              AND a.hours > 0
        """
