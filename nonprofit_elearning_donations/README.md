# eLearning: Processing Donations

A pure-data module: installing it drops a ready-built course,
*"Processing Donations"*, into Odoo's **eLearning** app.

## What's in the course

Recording a cash/check gift, a restricted gift, and an in-kind gift;
fundraising-event income and the quid-pro-quo split; donor analytics with
LYBUNT/SYBUNT filters and year-end contribution statements. A 4-question
quiz at the end.

Screenshots in `static/img/` come from a local test database with sample data.

## Access

Gated (`visibility="members"`, `enroll="invite"`); everyone in
`donation.group_donation_user` is auto-enrolled via `enroll_group_ids`.

## Dependencies

Only `website_slides` + `donation_base` + `donation`.

Content is adapted from `docs/handbook.html`'s donation-specific parts of
Part 3 and the fundraising slice of Part 5.
