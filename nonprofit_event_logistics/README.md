# Event Logistics

Permits, temporary hourly staffing, and vendor/crew day-of logistics for
events - the coordination layer stock Odoo doesn't have, while leaving
`project` (general event-planning tasks) and `purchase` (actual
procurement) to do what they already do well.

## What it adds

### Permits

`event.permit` - type (alcohol, food/health, street closure, noise/sound,
fire/safety, assembly/occupancy, parade route, other), issuing authority,
permit number, responsible person, submit-by/approval/expiry dates. A
deadline-reminder cron flags a not-started permit whose submit-by date is
approaching, and an approved permit whose expiry is approaching, with a
To-Do to the responsible person (deduped - only raised once).

A **permit checklist template** on the event type
(`event.type.permit.template`) means a recurring event (e.g. an annual
Pride festival) doesn't have to retype its known permit list every year -
*Generate permits from event type* on the event's Logistics tab
materialises it, skipping anything already generated.

### Temporary staff shifts

`event.staff.shift` / `event.staff.assignment` - a role
(`event.staff.role`: Security, Setup Crew, Ushers...), a headcount needed,
a time window, and check-in/out with computed hours - the same shape as
`volunteer_shift`'s shifts, but for paid workers. There's no Community
Edition payroll app (and Odoo's own shift-scheduling app, `planning`, is
Enterprise-only), so this stops at producing clean hours worked; running
payroll stays external. `hr_recruitment` (stock CE) is still the tool for
the actual hiring pipeline if wanted - this only starts once someone's
hired.

### Crew bookings

`event.crew.booking` - the vendor/crew, a service type (stage, sound,
lighting, security, sanitation, generator/power, tent rental, barricades,
waste removal), an *optional* linked Purchase Order (not every booking
runs through a formal PO - an in-kind sponsor, for instance), load-in/out
times, and a day-of contact name/phone (often not the same person who
signed the contract).

### Facilities

`event.facility` - portable toilets, hand-wash stations, first aid, water
stations, generators, dumpsters. Placed either by typing a coordinate or
with a **click-to-drop-pin mode** added to `nonprofit_event_venue`'s
existing live Vendor Map (a *Place Facilities* toggle appears once that
module is installed) - reusing the one map instead of building a second.

### The Logistics tab

On the event form: permits approved/total, staffing filled %, crews
confirmed/total, and a facility count, plus the four lists inline. A daily
readiness cron, starting 14 days before an event (configurable via
`nonprofit_event_logistics.readiness_horizon_days`), raises **one**
consolidated To-Do for the event's Logistics Coordinator listing what's
still open - deliberately one activity, not a flood of separate ones.

### Starter reports

Three reports, meant as a first pass to tune with the Logistics Lead:

- **Permit Status Report** - every permit, its authority/number,
  submit-by/expiry dates, responsible person, and status.
- **Staffing Roster** - shift by shift (role, time window, fill count),
  with who's assigned and their phone number.
- **Crew & Facilities Day-Of Sheet** - one page: every crew booking
  (service, load-in/out, day-of contact) and every facility (type,
  quantity, who services it) - the thing to have printed and in-pocket
  on event day.
