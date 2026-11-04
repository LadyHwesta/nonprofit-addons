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

## Installing on a running system

Install this module only after upgrading the suite's event modules, which adds
their permission tiers and moves existing users across. Do both in one command:

```
odoo-bin -c <config> -d <database> -i nonprofit_roles -u event_volunteer,nonprofit_event_venue,nonprofit_event_logistics,nonprofit_event_parade,nonprofit_event_entertainment --stop-after-init
```

Installing it alone on an out-of-date database stops with an error and changes
nothing in this module. Usually the error names the upgrade you need, but if
Entertainment already has run of show data it's a foreign key error instead.
The fix is the same.

The upgrade keeps people's access: Events Administrators become Manager in all
five areas, and Events Users become User. Databases that already have the tiers
are left alone. It doesn't assign nonprofit roles, so do that per person.

## A real limit worth knowing

Permission tiers are per *domain* (Venue, Logistics, Parade,
Entertainment, Volunteers), not per *model* within a domain. Vendor
Coordinator's "edit-level on Logistics" genuinely means edit rights
across all of Logistics (permits, staff shifts, crew booking,
facilities), not narrowly scoped to crew bookings alone - there's no
finer-grained group to restrict that further without splitting
Logistics into its own sub-domains, which nothing here does today.

Every role also includes core Events access, and that isn't read-only. Events
Users, including General Volunteer/Staff, can create and edit events and can
create, edit, and delete tickets and vendor booths. So a role listed as read-only
on Venue can still change booths.

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
