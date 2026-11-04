# eLearning: Access Rights and Roles

A pure-data module: installing it drops a ready-built course, *"Access Rights
and Roles"*, into Odoo's **eLearning** app.

## What's in the course

How roles, tiers, and the Administrator setting fit together, what each tier
and role allows, the Events access every role includes, how to assign a role,
what happens to new and upgraded users, and how to check access works. A
4-question quiz at the end.

Screenshots in `static/img/` come from a local test database with sample data.
If the user form changes in a later Odoo version, retake them.

## Access

Gated (`visibility="members"`, `enroll="invite"`); everyone in
`base.group_erp_manager` is auto-enrolled via `enroll_group_ids`.

## Dependencies

`website_slides` + `nonprofit_elearning_theme` + `nonprofit_roles`.
