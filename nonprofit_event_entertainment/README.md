# Event Entertainment

The "stage-show" event category this suite has always meant to
cover, alongside vendor booths (`nonprofit_event_venue`), the parade
(`nonprofit_event_parade`), and day-of logistics
(`nonprofit_event_logistics`). A reusable performer roster, per-stage
scheduling, and a printable Run of Show for events with live
performers.

## What it adds

### Performers

`event.performer` - a reusable roster, not re-typed per event: a
contact (`res.partner`, optional), genre, a default set length in
minutes, and free-text technical rider notes (power, mics, monitors,
backline). A recurring act's own details carry across every event it
plays - its "Bookings" tab shows its history across all of them.

### Stages

`event.entertainment.stage` - one event can have several independent schedules
(Main Stage, Acoustic Tent, ...), each with its own start time. Placed
either by typing a coordinate or with a **click-to-drop-pin mode**
added to `nonprofit_event_venue`'s existing live Vendor Map (a *Place
Stages* toggle, the same shape `nonprofit_event_logistics` already
added for facilities - both compose on the same map independently,
whether one or both modules are installed).

### The Run of Show

`event.run_of_show.line` - an ordered, drag-to-reorder list per stage,
mixing two kinds of item:

- **Performances** - linked to a roster performer, whose default set
  length prefills the duration (still freely editable per booking).
  Each gets a confirmation status - Invited, Confirmed, Declined,
  Cancelled - the same shape `event.crew.booking` already uses for
  vendor confirmation.
- **Announcements** - a raffle drawing, sponsor thank-yous, an MC
  introduction, a set-change break - anything that isn't a performer's
  own set. Just a title and a duration, slotted into the schedule at
  whatever point it's needed.

**The schedule computes itself.** Every item's start/end time is a
rolling clock, running forward from the stage's own start time by set
length. Drag an item to reorder it and every following time recomputes.
A **hard time** (`planned_start_override`) on any item pins it to a
fixed clock time regardless of how the schedule is running up to that
point (e.g. "the headliner must start at 9:00 PM sharp") - every later
item then flows from *that* item's real end time, not the original
flowing schedule.

### The Run of Show report

One PDF per stage (`Print Run of Show`, on the stage's own form) - a
plain, large-type table of clock time, item title, and duration, with
announcements marked distinctly from performances. The actual sheet a
stage manager holds during the show.

## Not yet live-verified

Rendering the PDF report itself needs `wkhtmltopdf`, not available in
this project's own local dev environment - same documented gap every
other QWeb PDF report in this suite already has. The scheduling logic
itself (cumulative times, hard-time overrides, reordering) is tested
directly.
