# Event Performer Payouts

Pays the people who make an event happen: the acts on the running order
(`nonprofit_event_entertainment`) and hired staff such as a bartender
(`nonprofit_event_logistics`). Everything owed becomes a **draft vendor
bill**, one per person per event, ready to check and post in Accounting.

## What it adds

- **A fee on each performance** in a stage's running order. Only
  **confirmed** performances with a fee are owed.
- **Pay for staff hours**: on a staff shift with an hourly rate, each
  assignment shows hours × rate. It is owed once the person has checked out.
- **Pay status** on every line (To bill / Billed / Paid) with a link to its
  bill. The status follows the bill: if a bill is cancelled, the line can be
  billed again.
- **On the event**, totals still to bill and already billed, and a
  **Bill Performers & Staff** button (shown to people who can make bills)
  that drafts every bill at once, grouped per person.
- Two service products, **Performer Fee** and **Event Staff Hours**, which
  can be bought but not sold. Bills carry no taxes by default.

## 1099-NEC (United States)

If `l10n_us_form_1099` is installed, anyone billed this way who has no 1099
setting yet is marked as a 1099 vendor of type **NEC**, with a note on their
contact, so their payments appear in the 1099-NEC summary. Untick it on the
contact if they are a corporation (corporations generally don't get a 1099).
Contacts that already have a 1099 setting are left alone.

## Not covered

Crew booked through purchase orders (`nonprofit_event_logistics`) keeps its
own purchase-order billing. Payment itself is the normal vendor-bill payment
in Accounting.
