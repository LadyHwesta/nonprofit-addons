# eLearning: Volunteer Coordination

A pure-data module: installing it drops a ready-built course,
*"Volunteer Coordination"*, into Odoo's **eLearning** app.

## What's in the course

Adding roles to an event and running them as shifts, recurring weekly
shifts, day-of check-in/out and no-shows, shift swaps, screening
(skills/background checks/waivers/minors) and making a role require it,
and volunteer hours reporting/certificates. A 4-question quiz at the end.

Screenshots in `static/img/` come from a local test database with sample data.

## Access

Gated (`visibility="members"`, `enroll="invite"`); everyone in
`event.group_event_user` is auto-enrolled via `enroll_group_ids`.

## Dependencies

Only `website_slides` + `event_volunteer` + `volunteer_shift` +
`volunteer_profile`.

Content is adapted from `docs/handbook.html`'s Parts 6, 7, and the
volunteer-hours slice of Part 6's Reporting section.
