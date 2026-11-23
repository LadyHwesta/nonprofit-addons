# Non-profit suite: overlap and screen review (2026-11-12)

What a new customer would trip over, from reading every module's menus,
models and dependencies. Nothing here is changed yet; each item has a
suggested fix to decide on.

## Things in the wrong place

**1. Day-to-day work is hidden under Events › Configuration.**
Permits, Staff Shifts, Crew Bookings and Facilities (event logistics) are
work people do every week, but they sit next to settings like Event
Templates. Nobody looks in Configuration for this.
*Fix:* a **Logistics** menu in Events (Permits, Staff Shifts, Crew
Bookings, Facilities), leaving only Staff Roles in Configuration.

**2. Parade has no menu at all.**
Parade entries and staging areas are only reachable from inside an
event's form or the website. There's no list of all entries to work from.
*Fix:* Events › **Parade** › Entries, Staging Areas.

**3. Volunteers adds four entries to the Events menu bar.**
Volunteers, Volunteer Shifts, Shift Swaps and Volunteer Reporting all sit
at the top level of Events, and Volunteer Skills is under Configuration ›
Volunteers. That's a lot of menu bar for one topic.
*Fix:* one **Volunteers** menu in Events holding Volunteers, Shifts,
Swaps and Reports. Or, if volunteers matter more than events to most
customers, its own **Volunteers** app.

**4. Two different "Non-Profit" menus in Accounting.**
Accounting › Non-Profit (Restriction Releases, Net-Asset Roll-Forward)
and Accounting › Reporting › Non-Profit (Donor Analytics, Functional
Expenses, Year-End Statements). Same name, two places, different things.
*Fix:* keep one **Non-Profit** menu in Accounting for the fund work and
the 990 report; move donor reports to the Donations app (see 6).

## Things that do the same job twice

**5. Two ways to send donors their yearly statement.**
OCA's `donation_base` already makes numbered annual tax receipts
(Donations › Tax Receipts, with an "annual" wizard). Our
`nonprofit_reports` adds Year-End Contribution Statements in Accounting.
A treasurer won't know which one is "the" receipt.
*Fix:* pick one. OCA's receipts are the numbered legal record, so the
cleaner choice is to keep those and turn ours into their printed layout
(or remove ours).

**6. Donor reporting is split between two apps.**
The Donations app has its own Reporting menu; our Donor Analytics
(LYBUNT/SYBUNT) lives in Accounting.
*Fix:* move Donor Analytics into Donations › Reporting, where people
already look at donors.

**7. Two kinds of shifts with the same name.**
`volunteer_shift` (volunteers: check-in, hours, swaps, portal) and
`nonprofit_event_logistics` Staff Shifts (paid temp staff). Different
purposes, but both are "shifts" on an event, on different screens.
*Fix:* name them clearly (**Volunteer Shifts** / **Paid Staff Shifts**)
and put them side by side in the event's form. Merging them into one
model isn't worth it unless customers ask.

## Naming and packaging

**8. "Donation" vs "Non-Profit".** The OCA app is called "Donation"
(singular), while everything else says "Non-Profit". Rename the app menu
to **Donations** from our `nonprofit_base`, without touching OCA's code.

**9. Installing roles installs everything.** `nonprofit_roles` depends on
every event module plus Project, Employees and Website, so a customer who
only wants donations and roles gets the whole suite. That works against
the demo plan's "partial install as the teaser".
*Fix:* split roles per area (donation roles, volunteer roles, event
roles), each depending only on its own modules.

## Suggested order

1. Menus (1-4, 8): small, safe, the biggest visible difference.
2. Year-end receipts (5): needs your call on which to keep.
3. Donor reports and shift naming (6-7).
4. Splitting roles (9): before the demo site.

---

## Status (2026-11-12, later)

Done, tested, not yet committed:

- **1-4 menus:** Events › **Logistics** (Permits, Paid Staff Shifts, Crew
  Bookings, Facilities; Staff Roles stays in Configuration), Events ›
  **Parade** (Entries, Staging Areas), one Events › **Volunteers** menu
  (Volunteers, Shifts, Shift Swaps, Reports), and one Accounting ›
  **Non-Profit** menu with **Funds** and **Reports** sections. Courses and
  the handbook give the new paths; the three affected courses reload on
  upgrade (their lessons are noupdate), as earlier course fixes did.
- **5 receipts:** new `nonprofit_donation_receipts` (installs itself when
  Donations and Non-Profit Reports are both present). The Donations app's
  numbered, tracked receipts now print as a US donor acknowledgement: EIN,
  each gift, the value of any goods or services received, and the
  170(f)(8) wording. The separate Year-End Statements menu is hidden then,
  so donors get one receipt. Without the Donations app, the statement is
  still the yearly receipt.
- **7 naming:** "Paid Staff Shifts" (logistics) vs "Volunteers › Shifts".

Not done:

- **6 donor analytics** stays in Accounting › Non-Profit › Reports rather
  than moving to the Donations app: it reads accounting entries, so it
  works without the Donations app, and moving it would make Non-Profit
  Reports require Donations.
- **8 and 9: done (commit 5145636), differently from the plan below.**
  Roles keep their IDs in `nonprofit_roles`, which now needs only
  `nonprofit_base`; each role's rights per area are in
  `models/res_groups.py` (ROLE_RIGHTS) and applied to whatever is
  installed, at install and on every registry load. No add-on modules, no
  moving records. The Donation app shows as "Donations" via
  `nonprofit_base`. The add-on plan below is kept only for the record.
- Pre-existing, not ours: OCA `donation`'s own test fails on a database
  without demo data (it uses a demo product). Harmless in real use.

### Roles split plan (item 9)

Keep the role groups (Chair, Treasurer, ...) and their IDs in
`nonprofit_roles`, depending only on `nonprofit_base`, with just the
accounting and base rights. Each area's rights move to a small add-on that
installs itself when that area is present and adds its rights to the same
roles:

| Add-on | Installs with | Adds |
|---|---|---|
| `nonprofit_roles_donation` | Donations | donation rights; renames the app "Donations" |
| `nonprofit_roles_volunteer` | Volunteer shifts + profiles | volunteer rights |
| `nonprofit_roles_events` | Venue, Logistics, Parade, Entertainment | event-area rights |
| `nonprofit_roles_office` | Project, Employees, Website | the Chair's and Operating Officer's extras |

The catch: an existing database upgrading `nonprofit_roles` doesn't
install new add-ons by itself, so a role would briefly lose its area
rights. The upgrade step would install the matching add-ons in the same
run. That needs testing on a copy of TFL's setup before it goes live.
