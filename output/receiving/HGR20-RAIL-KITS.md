# HGR20 rail kits — receiving, measuring and cutting

**Status: required, and kept by owner decision on 26 September 2026.** The owner reports about $150 for all four rails; they are not yet recorded as ordered. The "rail kits" ordered earlier that day were the HMS40 and ZBX80 drive modules (see [MOTION-MODULES.md](MOTION-MODULES.md)), whose strokes of 1000 × 800 × 100 mm are the machine travel. In this design those modules only push; these HGR20 guides carry the gantry and cutting loads. Before buying a combined set, check that it has two rails of at least 1,420 mm for Y (1,500 cut down) and two of at least 1,200 mm for X, with four HGH20CA blocks per pair. HGH20CA is the square 44 mm block this design uses; do not substitute flanged HGW20CC. When ordered, record the listings, price paid and delivery dates in [the register](hgr20-receiving-register.json).

| Kit | Listing | Contents | Use in Rev G |
|---|---|---|---|
| M04 | [B0FFMMPC3B](https://www.amazon.com/dp/B0FFMMPC3B) | Two 1500 mm HGR20 rails, four HGH20CA blocks | Y axis: both rails cut to **1420 mm**, two blocks per rail |
| M05 | [B0FFMN9KNC](https://www.amazon.com/dp/B0FFMN9KNC) | Two 1200 mm HGR20 rails, four HGH20CA blocks | X axis: both rails used at **1200 mm**, two blocks per rail |

Together the kits supply exactly what the Rev G model uses (`PURCHASED_HGR20_1420` ×2, `PURCHASED_HGR20_1200` ×2, `PURCHASED_HGH20CA` ×8).

## Why the rails are longer than the stroke

A guide rail has to be the stroke plus the length of the blocks riding on it, or the blocks run off the ends.

| Axis | Stroke | Blocks on each rail | Minimum rail | Rail in the design |
|---|---:|---|---:|---:|
| Y | 1,000 mm | two HGH20CA, 180 mm apart: 257.5 mm from the front of one to the back of the other | 1,257.5 mm | 1,420 mm (1,500 cut down; the extra leaves room for the end stops) |
| X | 800 mm | two HGH20CA spanning 237.5 mm | 1,037.5 mm | 1,200 mm, the full gantry beam |
| Z | 100 mm | none: the ZBX80 has its own guides | — | — |

The HMS40 modules follow the same rule: the 1,000 mm-stroke module is 1,145 mm long (L = S + 145).

## Why the rails must be measured before anything is cut or drilled

The seller's table gives HGR20 hole pitch **P = 40 mm** and end distance **E = 20 mm**, whereas the common HGR20 pattern is P = 60 mm. The CAD therefore has no rail-screw holes: the Y datum bars and the X guide face get their holes transfer-drilled from the actual rails. The Y cut position depends on the real pattern. On a 1500 mm rail, `plan_rail_cuts.py` gives:

| Possible factory pattern | Cut off end A | Cut off end B | Resulting end distances | Smallest margin |
|---|---:|---:|---|---:|
| P 60, 30 mm at both ends | 10 | 70 | 20 / 20 | 10 |
| P 40, 30 mm at both ends | 40 | 40 | 30 / 30 | 4.25 |
| P 40, 20 mm at end A, 40 mm at end B | 73 | 7 | 27 / 33 | 7 |

The obvious "40 mm off each end" is wrong for the third pattern: it would leave half a counterbore on the kept rail end. Measure first.

## On delivery

1. **Check contents and damage.** Four rails, eight blocks, fittings. Look for bent rails, dented raceways and rust. Photograph labels and packing.
2. **Do not slide a block off its rail** unless it goes onto the plastic transfer rail it was shipped with. Many HGR-type blocks lose their balls when run off the rail end. Keep the rails oiled and wrapped until installation.
3. **Mark end A** of each rail with a paint pen (for example the end nearest the maker's arrow or reference-edge mark) and give the rails the IDs Y1, Y2, X1, X2 used in the register.
4. **Measure each rail** and write the values into `hgr20-receiving-register.json`:
   - length; width and height at several points;
   - number of holes; each hole centre measured from end A with a tape hooked on end A, or at least the first-hole centre, the last-hole distance from end B and the first-to-last distance (pitch = first-to-last ÷ (holes − 1));
   - counterbore diameter and depth, through-hole diameter;
   - bow: rail on a known-flat surface, largest feeler-gauge gap underneath; side bow against a straightedge or taut string. The Y datum seat target is 0.05 mm per 1000 mm, so record what you see.
5. **Measure each block** (the design assumes the seller's table): width 44, length 77.5, height from rail base to block top 30, top holes 32 across × 36 along, **M5 threads at least 6 mm deep**. Check the thread depth with a screw and depth gauge: the model's M5 × 18 plate screws expect about 5.3 mm of engagement. Note any play or roughness when the block is run along the rail by hand.
6. **Run the planner**: `python3 output/receiving/plan_rail_cuts.py`. It reads the register and writes `rail-cut-plan.json` with the cut distance from each end, the resulting end distances and the valid cut ranges. `OK` means every margin is at least 2 mm; a tight or invalid result means re-measure, then ask before cutting.

## Cutting the Y rails

- Move the blocks onto their transfer rail first, or keep them well away from the cut and fully covered.
- The raceways are hardened: use an abrasive cut-off wheel with light, cool passes, not a bandsaw. Heat tint on the raceway means too much heat.
- Mark each cut from its own end. The kerf goes on the **offcut** side of the mark.
- Deburr and lightly chamfer both cut ends, clean out all grit, oil, then re-measure: 1420 mm and the end distances predicted by the plan.

## What the measurements unlock

- **Transfer-drilled rail holes** in the two Y datum bars and the X guide face, after those parts are welded and finish-machined. Tap M5 in the steel datum bars.
- **Rail screws**: M5 × 16 socket head, one per kept hole. Quantity is not yet in the cost register because it depends on the pitch: about 24 per Y rail and 20 per X rail at P 60, or 35 per Y rail and 30 per X rail at P 40.
- **The CAD hold** "HGR20: seller P40/E20/1500 hole dimensions conflict" in `motion_details.py` can then be replaced with the measured pattern.

The HMS40 drive modules, Z slide and plasma torch have their own open interface requests (`output/cad-repair-2026-09-25/SUPPLIER-DRAWING-REQUEST.md`); receiving the rails does not close those.
