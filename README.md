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
- `donation_base/`, `donation/` — OCA's donation stack (donations with lines,
  tax receipts, in-kind gifts, campaigns, bank-statement matching, thank-you
  letters), **forward-ported 18.0 → 19.0** and vendored here. See
  [`VENDORED.md`](VENDORED.md).

_Planned (see the project plan): `volunteer_shift` (shifts, check-in/out, hours,
recurring shifts, coordinator dashboard), `volunteer_profile` (skills,
background checks, waivers, onboarding), `nonprofit_fund_accounting` (restriction
enforcement + releases, net-asset roll-forward), `nonprofit_reports` (MIS Builder
Statement of Activities / Financial Position, donor analytics, IRS year-end
statements)._

## Third-party

OCA modules this suite depends on that aren't on an installable 19.0 channel yet
are vendored at the repo root (never in a directory named `vendor/` — that name
on the addons path shadows Bootstrap's `scss/vendor/` and breaks
`web.assets_web`). Each keeps its own upstream licence.

External OCA modules that _do_ have a 19.0 branch and are just added to the
addons path (not vendored): `mis-builder`, `account-budgeting`.

## Testing

[`testing/`](testing/) is a self-contained local Odoo 19 + Postgres instance —
see [`testing/README.md`](testing/README.md).

## Compatibility

Targets **Odoo 19.0**, tracked on `main` (mirrored to a `19.0` branch). Version
ports to other Odoo versions go on their own version branch.

## License

LGPL-3 (see [`LICENSE`](LICENSE)), unless a module's own manifest says otherwise
(vendored OCA modules keep their AGPL-3 / LGPL-3).
