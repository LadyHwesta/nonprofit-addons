# eLearning: Fund Accounting for Treasurers

A pure-data module: installing it drops a ready-built course, *"Fund
Accounting for Treasurers"*, straight into Odoo's **eLearning** app
(`website_slides`) - nothing to author by hand.

## What's in the course

Four sections: getting set up (the non-profit chart of accounts, fund
options), Fund/Program/Function (the three questions every transaction
answers), recording a vendor bill and releasing restricted funds, and
board/IRS reporting (Statement of Activities/Financial Position, the 990
functional-expense grid). A 4-question quiz at the end.

## Access

The course is gated (`visibility="members"`, `enroll="invite"`) rather
than public, and everyone already in `account.group_account_user` (Odoo's
"Show Full Accounting Features" group) is auto-enrolled via
`enroll_group_ids` - no manual step to add your bookkeeper/treasurer.

## Dependencies

Only `website_slides` + `nonprofit_base` + `nonprofit_fund_accounting` -
an org that doesn't run this suite's donation or events modules doesn't
need to install anything else to get this course.

Content is adapted from `docs/handbook.html`'s Parts 1, 2, 4, and 5.
