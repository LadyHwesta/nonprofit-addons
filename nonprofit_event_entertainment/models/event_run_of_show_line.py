# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

LINE_TYPES = [
    ("performance", "Performance"),
    ("announcement", "Announcement"),
]

BOOKING_STATES = [
    ("invited", "Invited"),
    ("confirmed", "Confirmed"),
    ("declined", "Declined"),
    ("cancelled", "Cancelled"),
]


class EventRunOfShowLine(models.Model):
    """One item in a stage's own run of show - either a performer's
    set or a non-performance item (an announcement, a raffle drawing,
    an MC introduction) slotted in at the right point. Ordered by
    sequence within a stage; computed_start/computed_end are a rolling
    clock computed from set lengths, running from the stage's own
    start_time - see _compute_schedule.
    """
    _name = "event.run_of_show.line"
    _description = "Run of Show Item"
    _inherit = ["mail.thread"]
    _order = "stage_id, sequence, id"

    stage_id = fields.Many2one(
        "event.entertainment.stage", string="Stage", required=True, ondelete="cascade",
        index=True)
    event_id = fields.Many2one(
        related="stage_id.event_id", store=True, string="Event")
    sequence = fields.Integer(default=10)
    line_type = fields.Selection(
        LINE_TYPES, default="performance", required=True, tracking=True)
    performer_id = fields.Many2one(
        "event.performer", string="Performer", ondelete="restrict",
        tracking=True)
    title = fields.Char(
        compute="_compute_title", store=True, readonly=False,
        help='Defaults to the performer\'s own name for a performance - '
             'type your own for an announcement (e.g. "Raffle Drawing"). '
             'Not required at the database level - a stored computed '
             'field is only populated by its compute *after* the initial '
             'insert, so a NOT NULL constraint here would reject the row '
             'before the compute ever runs. Enforced instead by '
             '_check_title_is_set below, which runs after the full '
             "create()/compute cycle.")
    duration_minutes = fields.Integer(
        string="Duration (minutes)", compute="_compute_duration_minutes",
        store=True, readonly=False,
        help="Defaults from the performer's own default set length - "
             "still freely editable, since the same act might play a "
             "different length set at this particular event.")
    planned_start_override = fields.Datetime(
        string="Hard Time",
        help='A fixed start time this item must hit regardless of how '
             'the schedule is running (e.g. "headliner must start at '
             '9:00 PM sharp") - every later item on this stage shifts '
             'to start after it.')
    computed_start = fields.Datetime(
        string="Start", compute="_compute_schedule", store=True)
    computed_end = fields.Datetime(
        string="End", compute="_compute_schedule", store=True)
    booking_state = fields.Selection(
        BOOKING_STATES, default="invited", required=True, tracking=True,
        help="Only meaningful for a performance - an announcement has "
             "nothing to confirm.")
    notes = fields.Text(help="Cues, tech notes, etc.")

    _duration_positive = models.Constraint(
        "CHECK (duration_minutes > 0)",
        "Duration must be a positive number of minutes.")

    @api.constrains("line_type", "performer_id")
    def _check_performance_needs_a_performer(self):
        for line in self:
            if line.line_type == "performance" and not line.performer_id:
                raise ValidationError(_(
                    "A performance needs a performer - pick one, or "
                    "switch this item to an Announcement."))

    @api.constrains("title")
    def _check_title_is_set(self):
        for line in self:
            if not line.title:
                raise ValidationError(_(
                    "Every run of show item needs a title - an "
                    "announcement needs one typed in by hand."))

    @api.depends("performer_id")
    def _compute_title(self):
        for line in self:
            if not line.title and line.performer_id:
                line.title = line.performer_id.name

    @api.depends("performer_id")
    def _compute_duration_minutes(self):
        for line in self:
            if line.duration_minutes:
                continue
            line.duration_minutes = line.performer_id.default_set_length or 10

    @api.depends(
        "stage_id.start_time", "stage_id.line_ids.sequence",
        "stage_id.line_ids.duration_minutes",
        "stage_id.line_ids.planned_start_override")
    def _compute_schedule(self):
        """A rolling clock can't be expressed as "depends on the
        previous sibling" - so this recomputes every line of every
        affected stage as a whole, not just the lines in `self`. A
        hard-time override on any line resets the clock for
        everything after it, which is exactly why the whole stage has
        to be walked in sequence order each time.
        """
        for stage in self.mapped("stage_id"):
            clock = stage.start_time or fields.Datetime.now()
            for line in stage.line_ids.sorted("sequence"):
                start = line.planned_start_override or clock
                end = start + timedelta(minutes=line.duration_minutes or 0)
                line.computed_start = start
                line.computed_end = end
                clock = end

    def action_confirm(self):
        for line in self:
            if line.booking_state not in ("invited",):
                raise UserError(_("Only an invited booking can be confirmed."))
        self.write({"booking_state": "confirmed"})

    def action_decline(self):
        for line in self:
            if line.booking_state not in ("invited", "confirmed"):
                raise UserError(_(
                    "Only an invited or confirmed booking can be declined."))
        self.write({"booking_state": "declined"})

    def action_cancel(self):
        self.write({"booking_state": "cancelled"})

    def action_reinvite(self):
        for line in self:
            if line.booking_state not in ("declined", "cancelled"):
                raise UserError(_(
                    "Only a declined or cancelled booking can be re-invited."))
        self.write({"booking_state": "invited"})
