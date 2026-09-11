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
- [`volunteer_shift/`](volunteer_shift/) — extends `event_volunteer`: a role can
  be run as timed **shifts** with check-in/out and computed hours, recurring
  shift generation from an event type, a `/my/shifts` portal with self
  check-in and shift swaps, an hours pivot report and a per-volunteer annual
  hours-certificate PDF.
- [`volunteer_profile/`](volunteer_profile/) — volunteer **skills** taxonomy,
  **background-check** tracking with an expiry cron + coordinator To-Do, a
  printable **liability waiver**, minor/guardian and emergency-contact fields,
  and sign-up **screening guards** (a role/shift that requires a background
  check, waiver or skills refuses an unqualified volunteer) plus a
  shift *Suggest Volunteers* skill-match.
- `donation_base/`, `donation/` — OCA's donation stack (donations with lines,
  tax receipts, in-kind gifts, campaigns, bank-statement matching, thank-you
  letters), **forward-ported 18.0 → 19.0** and vendored here. See
  [`VENDORED.md`](VENDORED.md).

All seven planned modules are in place; see the module READMEs for detail.

## Events: vendors, stage shows, parades

Fundraising and street-fair-style events (beer/wine/swag sales, drag and
other live performances, a full Pride event with vendors/parade/stage
shows) mostly run on **stock Odoo 19 CE apps** — install these, no
module here required:

- `event` + `event_sale` — events, tickets, registrations.
- `event_booth` + `event_booth_sale` — vendor booths, availability,
  sale-order-linked rental.
- `website_event_track` — stage shows/performances as `event.track`
  records against `event.track.location` ("stages"), with a built-in
  double-booking guard per location.
- `point_of_sale` (+ `pos_event_sale` for ticket sales through a POS) —
  beer/wine/swag sales.
- `project` + `purchase` — general event-planning tasks and actual
  procurement (e.g. ordering a porta-potty rental). Kept doing what
  they already do well rather than reinvented.
- Routing event revenue to a Program analytic tag (for the reports in
  `nonprofit_reports`) is a **configuration** step — an
  `account.analytic.distribution.model` record — not code.

Three gaps those stock apps don't cover get their own modules here:

- [`nonprofit_event_venue/`](nonprofit_event_venue/) — give every booth a
  plain **row + spot number**; a two-point calibration wizard (read two
  coordinates off a map, no trigonometry) turns that into a live,
  OpenStreetMap-based **vendor placement map** plus a load-in manifest PDF.
- [`nonprofit_event_parade/`](nonprofit_event_parade/) — a **public,
  no-login parade-entry application page**, coordinator approve/reject
  and staging-area/lineup-order assignment, a step-off-time wizard, and
  a parade lineup sheet PDF.
- [`nonprofit_event_logistics/`](nonprofit_event_logistics/) — **permits**
  with a checklist template + deadline reminders, **temporary hourly
  staff shifts** with check-in/out hours (no CE payroll to feed - just
  clean hours for whoever runs it externally), **crew/vendor bookings**
  (optionally linked to a Purchase Order) with day-of contacts, and
  **facility placement** (portable toilets, hand-wash stations...) via a
  click-to-drop-pin mode added to the vendor map above. A Logistics tab
  on the event shows readiness at a glance, with one consolidated
  coordinator To-Do as the event approaches if anything's still open.

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
