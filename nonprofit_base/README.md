# Non-Profit Base

The foundation the rest of the non-profit suite builds on: partner
fields, the analytic plans fund accounting needs, and a wizard that adds
a non-profit chart of accounts *on top of* whatever localisation chart is
already installed.

## What it adds

### Partner fields (`res.partner`)

A **Non-Profit** tab on the contact form:

- **Organisation** (companies only): `is_nonprofit_org`, and when set,
  `nonprofit_org_type` (501(c)(3) / 501(c)(4) / 501(c)(6) / church /
  school / government / other) and `tax_exempt_id` (EIN).
- **Donor**: `donor_type` (individual / household / foundation /
  corporation / government / other) and `household_id` - a self-reference
  that groups individuals into a household for joint giving credit. The
  tab lists the household's members with a live count.
- **Contact preferences**: `no_solicit`, `no_mail`, `no_email` consent
  flags. Search filters for *Non-Profit Orgs* and *Do Not Solicit*.

### Analytic plans (data, `noupdate`)

Four `account.analytic.plan` records with starter accounts:

| Plan | Starter accounts |
| --- | --- |
| **Fund** | Unrestricted; With Donor Restrictions - Purpose; - Time; Perpetual (Endowment) |
| **Function** | Program Services; Management & General; Fundraising |
| **Program** | General Program |
| **Grant** | *(none - one per award, added by the org)* |

Enforcement (mandatory Fund applicability, the income/expense constraint,
restriction releases, net-asset roll-forward) is in
`nonprofit_fund_accounting`.

### Add-on chart of accounts

**Accounting → Configuration → Add Non-Profit Accounts** opens a wizard
(`nonprofit.coa.import.wizard`) that reads
[`data/us_ucoa_nonprofit.csv`](data/us_ucoa_nonprofit.csv) - a UCOA-derived
subset mapped to Form 990 lines (contributions with/without donor
restrictions, grants, fundraising events + direct-benefit contra, in-kind,
membership dues, program service fees, investment/other income, net-asset
released clearing, functional expense pools, net-asset classes) - and
creates each account in the chosen company.

- **Layers on, never replaces**: it only ever `create()`s; existing
  accounts (localisation template included) are left alone.
- **Idempotent**: an account whose (prefixed) code already exists is
  skipped; a second run adds nothing.
- **Code Prefix**: prepended to every template code (e.g. `9` → `94000`)
  to keep the added accounts clear of the localisation's numbering.
- **Skip Codes That Already Exist** (default on): off makes a collision
  abort the run with the list of clashing codes instead of skipping them.

Each created account carries `account.account.tag` records
(`NFP 990: …`, `NFP Function: …`, `NFP: Statement of Activities - …`) that
the `nonprofit_reports` MIS templates and 990 schedule key off.

## Requirements

Odoo 19 Community, `account` + `contacts`. No extra Python packages.

## Tests

`./testing` harness, `--test-tags=/nonprofit_base`: full-set import,
second-run no-op, collision skip, no-skip abort, code prefix, plans/tags
present, partner org + household roll-up. 8 tests.
