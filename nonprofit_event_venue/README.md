# Event Venue Map

Extends *Events Booths* (`event_booth`, stock Odoo CE): give every booth a
plain **row + spot number**, and a real venue map fills itself in.

## What it adds

### Rows and placement

- `event.venue.row` - one per row/section of a venue, ordered by
  `sequence` (the order they actually sit on the ground, starting from
  whichever one you'll calibrate from).
- `event.booth` gains `row_id` + `spot_number` (unique per row), a
  computed `booth_label` ("Row C · Spot 12"), and computed, stored
  `latitude`/`longitude`.

### Calibration - no trigonometry required

The event form gets a **Vendor Map** tab with a *Calibrate from two
points...* button. Read two real-world coordinates off Google Maps,
OpenStreetMap, or a phone GPS reading on-site:

1. Spot 1 on a reference row.
2. Any other spot number on that same row.
3. Spot 1 on a different row.

The wizard works out the venue's spot bearing/spacing and row
bearing/spacing from those three points and stores them on the event.
Every booth's `latitude`/`longitude` is then computed automatically from
its row/spot - assign the row and spot number, and the pin follows.

### The live map

*Open Vendor Map* (event form, once calibrated) shows every placed booth
as a colored pin on an OpenStreetMap-tiled map - teal for available,
green for rented - click a pin's popup title to jump to that booth's
record. Built with a vendored **Leaflet.js** (`static/lib/leaflet`, MIT/
BSD-2-Clause, shipped with the module - no external account or CDN
dependency at runtime).

A **Vendor Load-In Manifest** PDF (event's Print menu) lists booths
grouped by row in spot order - the paper backup for morning-of setup.

### Vendor requirements

A booth can be flagged **Needs Power** and given a **Spots Wide** count
(2+ for a double-wide vendor, etc.) - a booth's row/spot display and its
load-in manifest row both show the full range it occupies (e.g. "5-6"),
and placing a second booth that would overlap that range is blocked
(`_check_no_spot_overlap`). A separate **Vendor Requirements** PDF lists
every booth with its vendor, spot(s), power needs, and width - sorted by
vendor, for planning power drops and load-in coordination ahead of the
day-of manifest above.

## A note on the map tiles

The public OpenStreetMap tile server this module points at has a usage
policy meant for light, non-commercial traffic - entirely fine for a
handful of staff viewing a placement map. If this ever gets embedded on
a public-facing, high-traffic page, swap the tile URL in
`static/src/venue_map/venue_map_action.js` for a provider with a real
free tier (MapTiler, Stadia Maps) or self-hosted tiles - the rest of the
code is unaffected.

## A note on accuracy

The two-point calibration assumes a reasonably regular grid - rows
roughly parallel, spots roughly evenly spaced. It's a placement map, not
a survey. If a real row curves or spacing varies, the printed manifest
(plain row + spot text) is always the source of truth.
