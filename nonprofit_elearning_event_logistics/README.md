# eLearning: Logistics Lead

A pure-data module: installing it drops a ready-built course,
*"Logistics Lead"*, into Odoo's **eLearning** app.

## What's in the course

Building a permit checklist from an event type and its deadline/expiry
reminders, staff shifts and check-in/out, crew bookings and day-of
contacts, placing facilities on the vendor map, and the Logistics tab's
readiness numbers plus its consolidated reminder. A 4-question quiz at
the end.

Screenshots in `static/img/` come from a local test database with sample data.

## Access

Gated (`visibility="members"`, `enroll="invite"`); everyone in
`event.group_event_user` is auto-enrolled via `enroll_group_ids`.

## Dependencies

Only `website_slides` + `nonprofit_event_logistics` (which itself pulls
in `nonprofit_event_venue`, so the facility-placement lesson's mention of
the vendor map is always accurate for anyone who installs this course).
