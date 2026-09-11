# Event Parade Lineup

Public parade-entry applications, staging areas, and a lineup sheet for
parade morning.

## What it adds

### Public application

`/event/<id>/parade/apply` - no login required. A community group gives
their unit name, contact info, entry type, size, special requirements,
and accepts a click-through liability waiver. Submitting creates an
`event.parade.entry` in `submitted` state, raises a To-Do for the
event's `parade_coordinator_id`, and emails the applicant a confirmation.
Turn it on per event with **Accepting Parade Entries**; an optional
**deadline** closes the page automatically afterward.

### Review and lineup

Coordinators **approve / reject** a submitted entry, then assign a
**staging area** (`event.parade.staging.area`) and a lineup **order**
before **confirming** it for the lineup. A **"Set Step-Off Times"**
wizard walks every confirmed entry - staging area, then order - and
stamps a step-off time a fixed number of minutes after the one before.

### Parade day

The **Parade Lineup Sheet** PDF (event's Print menu) lists confirmed
entries by staging area and order, with step-off time, contact, and
special requirements - the paper marshals actually carry.
