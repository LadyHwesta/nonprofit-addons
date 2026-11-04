# Non-Profit Organization Roles

Composes this suite's own per-domain permission tiers - plus Accounting,
Donation, Projects, HR, and Website - into named roles that match how a
nonprofit is actually run, instead of leaving every admin to hand-assign
a pile of technical-sounding checkboxes per person.

## Why this needed its own module

Every event-domain module in this suite (venue, logistics, parade,
entertainment, volunteers) used to share Odoo's own blanket
`event.group_event_user`/`event.group_event_manager` - there was no way
to give someone "manages volunteers" without also handing them venue,
logistics, parade, and entertainment management. Installing this module
adds a real Viewer/User/Manager tier to each of those five domains
(Manager implies User implies Viewer, same pattern OCA's own `donation`
module already uses), then composes the roles below from them.

## The roles

| Role | Full manage | Read-only elsewhere |
|---|---|---|
| **General Volunteer/Staff** | - | Venue, Logistics, Parade, Entertainment, Volunteers, Donation |
| **Chair Person** | Everything, plus core Event scheduling | - (not Settings/Technical) |
| **Operating Officer** | Logistics (incl. facilities), Volunteers, HR | Venue, Parade, Entertainment, Donation, Accounting |
| **Treasurer** | Accounting, Donation | Venue, Logistics, Parade, Entertainment, Volunteers |
| **Fundraising Manager** | Donation (campaigns, tax receipts, thank-yous) | Venue, Logistics, Parade, Entertainment, Volunteers, Accounting |
| **Program Director** | Venue + Logistics + Parade + Entertainment + Volunteers (the whole event program) + core Event scheduling + Projects | Donation, Accounting |
| **Marketing & Communications Director** | Website/event public pages, Donation campaign messaging | Venue, Logistics, Parade, Entertainment, Volunteers |
| **Volunteer Coordinator** | Volunteers only | Venue, Logistics, Parade, Entertainment, Donation |
| **Logistics Coordinator** | Logistics only | Venue, Parade, Entertainment, Volunteers, Donation |
| **Vendor Coordinator** | Venue (incl. vendor/exhibitor booths) + edit-level on Logistics (crew booking) | Parade, Entertainment, Volunteers, Donation |
| **Parade Coordinator** | Parade only | Venue, Logistics, Entertainment, Volunteers, Donation |

**General Volunteer/Staff** is added to Odoo's own default user template
(Settings > Users > Default User Template) on install - every brand-new
internal user starts here. Upgrade an existing user's role from Settings
> Users > a user's own Access Rights tab (or Preferences, depending on
`groups_id` visibility settings).

**Administrator** (`base.group_system`) is untouched - none of these
roles grant Settings/Technical access.

## A real limit worth knowing

Permission tiers are per *domain* (Venue, Logistics, Parade,
Entertainment, Volunteers), not per *model* within a domain. Vendor
Coordinator's "edit-level on Logistics" genuinely means edit rights
across all of Logistics (permits, staff shifts, crew booking,
facilities), not narrowly scoped to crew bookings alone - there's no
finer-grained group to restrict that further without splitting
Logistics into its own sub-domains, which nothing here does today.

## HR, Projects, and Website

Added as real dependencies because three of the roles above need them
and nothing in this suite modeled an equivalent:

- **Operating Officer** needs `hr` (there's no HR model anywhere in this
  suite).
- **Program Director** needs `project` ("manage all projects" - there's
  no project-management model in this suite either; this role gets
  `project.group_project_manager` directly).
- **Marketing & Communications Director** needs `website`
  (`website.group_website_designer`) for the public event pages - no
  marketing/communications model exists here.

Installing this module pulls all three of those apps in, suite-wide.
