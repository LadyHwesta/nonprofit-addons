# Volunteer Profile & Screening

The screening side of volunteer management: skills, background checks with
expiry, a liability waiver, minor/guardian, and guards that stop an
un-cleared volunteer from signing up for a role that needs clearance.

## What it adds

### Skills

`volunteer.skill` (name + category) as a taxonomy; `volunteer_skill_ids`
on the contact. A role gets **Required Skills**, and a shift can
**Suggest Volunteers** - `action_suggest_volunteers()` returns the people
who have every required skill, are cleared / waivered if the role needs
it, and aren't already booked on an overlapping shift. Ships a starter
skill list.

### Who can see this data

Skills, screening, waiver, minor and emergency contact fields can only be
read, changed or searched by people with a Volunteer tier. Everyone else
doesn't see the tab, the search filters or the waiver report, and tracked
changes are hidden from them in the chatter and in email notifications.
Sign-up checks still run for everyone. They report only which requirement
is unmet. These fields aren't copied when a Contact is duplicated.

### Background checks

On the contact's **Volunteer** tab: state (not started / requested /
cleared / expired), *Cleared On* and *Re-check Due* dates.
*Mark Cleared* sets the dates (validity from settings, default 24
months). A daily cron flips lapsed clearances to **expired** and, for
checks due within the warning window (default 45 days), raises a To-Do
for the **Volunteer Coordinator** set in Settings - once.
`background_check_valid` and `waiver_current` are searchable.

### Waiver

A *Waiver Signed* flag + date, a **Record Waiver Accepted** button, a
configurable validity (default 12 months), and a printable QWeb
**Volunteer Liability Waiver** (acceptance checkbox, no e-signature
module) on the contact *Print* menu - it adapts for minors.

### Details

Under-18 + parent/guardian, emergency contact name/phone, T-shirt size,
orientation done + date.

### Screening guards

A role (or a shift of it) flagged **Requires Background Check** /
**Requires Waiver**, or carrying **Required Skills**, refuses a sign-up
from a volunteer who doesn't meet them - on the website
(`action_portal_volunteer` / `action_portal_signup`, a `UserError`
listing what's missing) and in the back office (an
`account.move`-style `@api.constrains`, bypassable with
`skip_volunteer_eligibility` in the context).

## Requirements

Odoo 19 Community, `volunteer_shift`. No extra Python packages.

## Tests

`--test-tags=/volunteer_profile`: clear sets dates + validity; cron
expires lapsed checks and raises a single coordinator To-Do;
`background_check_valid` / `waiver_current` search; portal + back-office
sign-up blocked then allowed, skip-context bypass, existing assignment
not retro-blocked; skill suggestion filters on skills, clearance,
overlap and already-assigned.
