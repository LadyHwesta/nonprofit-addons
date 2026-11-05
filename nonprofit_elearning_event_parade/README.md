# eLearning: Parade Coordinator

A pure-data module: installing it drops a ready-built course,
*"Parade Coordinator"*, into Odoo's **eLearning** app.

## What's in the course

Turning on public applications and setting a deadline, reviewing/
approving/rejecting entries, staging areas and lineup order vs. entry
number, the Set Step-Off Times wizard, and the four parade-day
printables (lineup sheet, two entry lists, entry signs). A 4-question
quiz at the end.

Screenshots in `static/img/` come from a local test database with sample data.

## Access

Gated (`visibility="members"`, `enroll="invite"`); everyone in
`event.group_event_user` is auto-enrolled via `enroll_group_ids`.

## Dependencies

Only `website_slides` + `nonprofit_event_parade`.
