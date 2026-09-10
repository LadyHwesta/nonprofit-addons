# Volunteer Shifts

Extends *Event Volunteer Roles*: a role can be run whole-event (the
default) or broken into timed **shifts**, with check-in/out, hours,
recurring generation, swaps and a volunteer portal.

## What it adds

### Shifts

- `volunteer.shift` - a role, a start/stop, a slot count. Live
  *signed-up / needed* counts and an empty / partial / full / over badge,
  a `duration_hours`, and a `time_state` (upcoming / in progress / past).
- `event.volunteer.role` gets **Run as Shifts**; when on, its counts on
  the event form aggregate over the shifts and volunteers sign up per
  shift. The event form gets a *Shifts* stat button and a calendar.
- `event.volunteer.assignment` gets `shift_id`, `check_in` / `check_out`
  (hours computed and stored), and `no_show`. Capacity and the
  one-signup rule are enforced per shift when `shift_id` is set;
  `skip_volunteer_capacity` in context still bypasses.

### Recurring shifts

`volunteer.shift.template` lines on an **event type** - a role name,
weekday, start hour (UTC), length and slots. A daily cron
(`_cron_generate_shifts`) materialises them for events whose type has
templates and that start inside the horizon (default 4 weeks), creating
the role if needed and skipping shifts it already made. *Generate shifts
from event type* on the event form runs it on demand.

### Portal - `/my/shifts`

Upcoming and past shifts, lifetime hours, self **check-in / check-out**
while a shift is on (from `grace` minutes before the start until it
ends), an **offer for swap** button, and a list of shifts other
volunteers have given up that you can **take** (the coordinator approves
in *Events → Shift Swaps*).

### Reporting

- `report.volunteer.hours` - pivot / graph / list of logged hours by
  volunteer, program (event type), event, role, month.
- **Volunteer Hours Certificate** wizard + QWeb PDF, one per volunteer
  for a chosen year, listing every shift and the total.

### Settings

Settings → Events → Registration: default shift length, check-in grace
window, recurring-shift horizon.

## Requirements

Odoo 19 Community, `event_volunteer`, `portal`. No extra Python packages.
wkhtmltopdf for the certificate PDF (HTML fallback otherwise).

## Tests

`--test-tags=/volunteer_shift`: shift counts / fill state / capacity /
one-signup; role counts aggregate over shifts; check-in/out hours;
no-show; swap offer → claim → approve reassigns the volunteer; recurring
generation is correct and idempotent, cron respects the horizon; the
`/my/shifts` portal page renders and the home card shows; `web.assets_web`
SCSS-clean guard.
