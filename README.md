# Non-Profit Addons

Odoo 19 **Community** modules for US non-profit organizations — volunteer shift
management, fund accounting, donations, and a non-profit chart of accounts that
layers onto an existing localization.

## Modules

- [`event_volunteer/`](event_volunteer/) — volunteer roles with slot quotas on
  events, website self sign-up / withdraw, capacity guards, reminder emails, a
  participation report. Deployment-neutral: nothing here is non-profit- or
  club-specific. Also used by the club suite in
  [`LadyHwesta/odoo-addons`](https://github.com/LadyHwesta/odoo-addons); this
  repo is its home.
- [`nonprofit_base/`](nonprofit_base/) — partner org/donor/consent fields and
  households; the Fund/Program/Function/Grant `account.analytic.plan` records;
  and a wizard (*Accounting → Configuration → Add Non-Profit Accounts*) that
  layers a UCOA-derived, Form-990-tagged chart of accounts onto an existing
  localisation chart — idempotent, prefix-able, never replaces.
- [`nonprofit_fund_accounting/`](nonprofit_fund_accounting/) — enforces a Fund
  analytic account (100%) on income/expense postings per company; a
  *Restriction Releases* workflow that posts the balanced net-assets-released
  entry between two clearing accounts; and a per-fund net-asset roll-forward
  report.
- [`nonprofit_reports/`](nonprofit_reports/) — donor analytics
  (`report.nonprofit.donor` with LYBUNT / SYBUNT filters), a Form 990
  functional-expense pivot, a year-end contribution-statement wizard + QWeb PDF,
  and MIS Builder *Statement of Activities* / *Statement of Financial Position*
  templates. Needs `mis_builder` on the addons path.
- `donation_base/`, `donation/` — OCA's donation stack (donations with lines,
  tax receipts, in-kind gifts, campaigns, bank-statement matching, thank-you
  letters), **forward-ported 18.0 → 19.0** and vendored here. See
  [`VENDORED.md`](VENDORED.md).

_Planned (see the project plan): `volunteer_shift` (shifts, check-in/out, hours,
recurring shifts, coordinator dashboard), `volunteer_profile` (skills,
background checks, waivers, onboarding)._

## Third-party

OCA modules this suite depends on that aren't on an installable 19.0 channel yet
are vendored at the repo root (never in a directory named `vendor/` — that name
on the addons path shadows Bootstrap's `scss/vendor/` and breaks
`web.assets_web`). Each keeps its own upstream licence.

External OCA modules that _do_ have a 19.0 branch and are just added to the
addons path (not vendored): `mis-builder` (needs OCA `reporting-engine` +
`server-ux` too) — required by `nonprofit_reports`; `account-budgeting`.
`testing/start.sh` picks these up from `~/dev/<repo>` (override with the
`OCA_*` env vars).

## Testing

[`testing/`](testing/) is a self-contained local Odoo 19 + Postgres instance —
see [`testing/README.md`](testing/README.md).

## Compatibility

Targets **Odoo 19.0**, tracked on `main` (mirrored to a `19.0` branch). Version
ports to other Odoo versions go on their own version branch.

## License

LGPL-3 (see [`LICENSE`](LICENSE)), unless a module's own manifest says otherwise
(vendored OCA modules keep their AGPL-3 / LGPL-3).
