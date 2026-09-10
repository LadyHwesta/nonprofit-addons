# Non-Profit Reports

Reporting on top of `nonprofit_base` - donor analytics, a Form 990
functional-expense pivot, year-end contribution statements, and MIS
Builder financial statements. All of it keys off the `nonprofit_base`
account tags and analytic plans.

## What it adds

### Donor analytics

**Accounting → Reporting → Non-Profit → Donor Analytics**
(`report.nonprofit.donor`, a read-only SQL view). One row per donor:

| Column | |
| --- | --- |
| Lifetime Giving, Gifts | totals over all time |
| First / Last / Largest gift | |
| This Year / Last Year / Prior Years | rolling-year totals vs. the calendar year |

List, pivot and graph views. Search filters: **Gave This Year**,
**LYBUNT** (`this_year <= 0 and last_year > 0`), **SYBUNT**
(`this_year <= 0 and lifetime > 0`), **Lifetime ≥ 1,000**.

Source: posted journal items on income accounts tagged as gifts
(`NFP 990: Contributions …`, grants, fundraising events, in-kind) - so it
works whether contributions come through the `donation` module or plain
invoices / journal entries. Membership dues and program-service revenue
are deliberately excluded.

### Form 990 functional-expense schedule

**… → Non-Profit → Functional Expenses (990 Part IX)** - a pivot of
analytic items on the *Function* plan: natural expense account (rows) x
Program / Management & General / Fundraising (columns), amount as the
measure.

### Year-end contribution statements

**… → Non-Profit → Year-End Contribution Statements** - a wizard (date
range, optional donor list, minimum-total threshold, default $250) that
prints one QWeb PDF per donor: every gift in the period, the total, and
the IRS §170(f)(8) written-acknowledgement / quid-pro-quo language. Also
on the contact **Print** menu.

### MIS Builder templates

Two `mis.report` templates and ready-to-run instances (current fiscal
year):

* **Statement of Activities** - revenue by source, expense by function
  (informational; the 990 pivot is the real functional breakdown), and
  change in net assets.
* **Statement of Financial Position** - total assets, total liabilities,
  net assets, and net assets split into *with* / *without donor
  restrictions* via the net-asset tags. A *Current-Year Surplus Not Yet
  in Net Assets* line flags the un-closed result.

Open them from **Accounting → Reporting** (MIS Reports). Add a
fund-filtered column set on the instance for a by-fund statement.

## Requirements

Odoo 19 Community, `nonprofit_base`, and **`mis_builder`** (OCA
`mis-builder` 19.0, which also needs OCA `reporting-engine` and
`server-ux` on the addons path). No extra Python packages beyond what
`mis_builder` requires. wkhtmltopdf for the statement PDF (falls back to
HTML without it).

## Tests

`./testing` harness, `--test-tags=/nonprofit_reports` (9): donor view
lifetime / by-year aggregates, LYBUNT and SYBUNT filters, non-gift income
excluded; statement wizard threshold filtering, report values, HTML
render; both MIS instances compute and the Statement of Activities totals
tie.
