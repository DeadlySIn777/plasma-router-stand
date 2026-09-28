# GM1 Rev L rotary variant — what the tube-notching rotary adds to the shopping list

The owner asked (28 September): "can we add a 4th axis for the plasma/cnc? plasma for tube knotching". The design is in
[RevL-ROTARY-CAD](../../../output/release-review/RevL-ROTARY-CAD/README.md). It adds nothing to the bed module and changes
nothing on the machine that is already ordered; the shelf bolts to the frame's rear upper cross tube with two bolts, in
sleeves welded through that tube before the frame is filled.

**Nothing here is priced from a quote.** The [actual-price audit](REAL-COST.md) still stands at the Rev J scope, **$5,336.10**;
the Rev K, Rev L and BT30 deltas are unpriced too, and this adds to them.

## Why there is no fifth driver

The BTT Rodent has four stepper drivers and GM1 uses all four (X, Y1, Y2, Z). The rotary therefore runs on the **X driver
through a plug swap** at the cabinet: the X motor's cable and the rotary's cable end in the same 4-pin plug, and only one is
in the X receptacle. No controller, driver or firmware change; the tube turns on what the controller calls X, and the torch
runs along Y on the two squared Y motors.

## New purchased parts

| Qty | Part | For | About |
|---|---|---|---|
| 1 | Hollow rotary axis for plasma/CNC: four-jaw independent chuck about Ø125 (K72-125 class), through-bore 40–50 mm, belt reduction about 6:1, NEMA 23 stepper (2.8 A class, 4-wire), rated for a 25 kg tube | ROTARY_AXIS_ALLOCATION and its chuck; envelope 210 × 200 × 175 with the axis 116 mm over the base | $300–450 |
| 1 | 2 × 4 × .083 in steel rectangular tube, 0.7 m (2 × 240 + 118, plus cuts) | ROT_RAIL_L, ROT_RAIL_R, ROT_TIE, the U on the rear cross tube | $20 |
| 1 | A36 plate 1/4 in, 220 × 240 | ROT_PLATE, the shelf | $12 |
| 2 | M10 × 130 hex bolt, nut, washers, and a steel sleeve (12 mm OD, 51 mm long) welded through the rear cross tube | Shelf to the frame | $6 |
| 4 | M8 bolts, nuts and washers (or the unit's own) | Rotary base to the shelf plate | $3 |
| 1 | 4-pin motor plug to match the X motor's cabinet receptacle, 3 m of 4 × 18 AWG shielded cable | Rotary motor lead, plugged in place of the X motor | $15 |
| 1 | Adjustable roller stand (pipe roller), 0.6–1.1 m | Supports tubes longer than about 1.2 m at the front of the machine | $40 |
| – | Steel round tube Ø60 × 3 (the checked workpiece) | Workpiece, the owner's stock | – |

About **$400–550** in all, the rotary itself being nearly all of it.

## What it needs that is already there

- The plasma head's float touch-off (M11): the tube top is probed like a plate.
- The Rev K torch reach: the torch axis comes back to Y1073.6, so the nearest cut is 306 mm from the jaws; notches go at the tube's free end.
- The second E-stop (M20) at the back of the frame, by the chuck.
- Two M10 sleeves through the rear upper cross tube, welded before the frame is filled (a build-order item if the rotary is wanted).

## Not included

- CAM for tube notching (a tube-unwrapping post: Fusion's wrap, SheetCAM's rotary post, or a free tube-notch generator) and the
  settings macro described in the README ($100 in steps per degree or per mm of arc, X soft limit off, X left out of the homing
  cycle, THC off for the job).
- A splash guard between the chuck and the pan's rear wall if slag reaches the jaws (a strip of sheet, not drawn).
- A tailstock: the tube is cantilevered from the chuck; long tubes rest on the roller stand at the front.
