# GM1 Rev H — one-piece hoisted router bed

**GM1 — Garcia Mechanical Table.** Working design for review, **not released for purchasing, fabrication, CAM or operation.** Amber parts in the previews are purchased-part envelopes whose interfaces are not all verified.

Rev H answers the owner's requirement of 26 September 2026: *one piece, lifted out with a winch, at most about 12 screws of M8–M12, waterproof for mist coolant when cutting aluminum.* It replaces the Rev G six-panel manual bed. The rest of the machine (frame, water table, controls packaging, motion) is unchanged from Rev G.

- [Router assembly STEP](step/RevH_ROUTER.step) — bed module installed
- [Plasma layout STEP](step/RevH_PLASMA_LAYOUT.step) — module out of the machine; spindle, clamp hardware and drawdowns stored (no plasma torch is modeled)
- [Bed module STEP](step/RevH_BED_MODULE.step) — the part the hoist carries
- Previews: [router](previews/RevH_ROUTER.png), [front](previews/RevH_ROUTER_front.png), [plasma layout](previews/RevH_PLASMA_LAYOUT.png), [module](previews/RevH_BED_MODULE.png), [module underside](previews/RevH_BED_MODULE_underside.png)
- [Component schedule](cutlist.csv), [operations](part-operations.json), [individual STEP parts](parts/), [flat DXFs](dxf/), [tube cutting plan](TUBE-CUT-PLAN.md), [sheet nesting](nesting/sheet-nesting.json)
- Checks: [hoist path with rigging](handling-check.json), [nine motion poses](motion/revh-full-machine-poses.json), validations for the [router](RevH_ROUTER-validation.json), [plasma layout](RevH_PLASMA_LAYOUT-validation.json) and [module](RevH_BED_MODULE-validation.json), [manifest and source hashes](engineering-manifest.json)
- [What Rev H changes in the shopping list](../../../outputs/reve-30510/actual-cost/REVH-PROCUREMENT-DELTA.md)

![Rev H router](previews/RevH_ROUTER.png)

## How Rev H meets the requirement

| Owner requirement | Rev H |
|---|---|
| One piece, lifted out with a winch | One welded, galvanized module, **about 63 kg** (model estimate; weigh it). Four lift lugs take a 4-leg sling to an overhead beam-and-trolley hoist. |
| At most about 12 screws, M8–M12 | **Six M10 × 80** stainless socket screws hold it down; two Ø10 pins locate it. Nothing else is removed for a bed change. |
| Waterproof for mist coolant on aluminum | No wood or MDF. Hot-dip galvanized steel, 6063 aluminum T-slot, HDPE top plates, stainless (A4) fasteners. |

Rev G needed 52 screws, 24 loose nuts and 18 separate pieces handled for each change. Rev F was one piece, but it was 87 kg and relied on MDF surfaced in the machine.

## The module

| Item | Nominal model |
|---|---|
| Stack (Z above floor) | ledger 840 → 6 mm seat pads 846 → 2 × 2 rails 846–896.8 → 2 × 2 crossmembers 870–920.8 → 20100 T-slot 920.8–940.8 → HDPE 940.8–**958.8** (same work height as Rev G) |
| Frame | Two 2 × 2 × .120 side rails, 1,337 mm with welded end caps, X62–112.8 and X1037.2–1088; four 2 × 2 × .120 crossmembers, 912.4 mm, at Y85.4 / 476 / 867 / 1257.4, each closed by 6 mm end plates welded over the full rail height |
| T-slot deck | Nine cut-only 20100 profiles, 1,197 mm (one saw cut per 1,220 mm bar), X125–1025 × Y73–1270, slots front-to-back. Each is held by one M5 screw per crossmember from inside the tube into a square nut in its bottom slot (36 screws, installed once) |
| Top | Two HDPE plates, 398 × 1,000 × 18 mm finished from 3/4 in sheet, X176–574 and X576–974, Y130–1130. Surfaced in the machine. Twelve counterbored M5 screws into top-slot nuts. One fixed hole per plate, slots and oversize holes elsewhere, because HDPE grows about 0.15 mm per metre per °C |
| Lift lugs | Four 3/8 in plates welded to the end crossmembers at X150 and X1000, beyond both deck ends; Ø14 holes for 3/8 in screw-pin shackles |
| Seating | Six 6 mm pads welded on the ledger tops (front, middle and rear on each side), faced coplanar after welding. The M10 screws go through compression sleeves in the rails into sealed, tapped sleeves welded through the sand-filled ledgers before filling. The left front pin fits a round hole; the right front pin fits a slot along X |
| Mass and centre of mass | 63.4 kg: steel weldment 31.7, aluminum strips 17.8, HDPE 13.6, hardware 0.3. Centre of mass X575.0, Y662.9, Z912.2, midway between the four lugs |

The HDPE plates are the precision work surface; surface them in place after the module is seated. For a vise or fixture plate, remove one HDPE plate (six screws) and bolt the vise to the T-slots. The side strips (X125–176, X974–1025) and both deck ends stay uncovered for clamps. In X both plates lie inside the tool-centre travel (X175–975). In Y they run 130–1130, so a surfacing cutter of 25 mm diameter or more reaches their whole face. That holds for the nominal travel (Y121.4–1121.4) and also if the ZBX80 turns out to put the tool up to 20 mm further back ([receiving check](../../receiving/MOTION-MODULES.md)).

**Stiffness screen, not a rating:** a crossmember treated as a simply supported 912 mm beam deflects about 0.07 mm under 200 N at midspan (I = 222,160 mm⁴). A side rail between pads (645 mm) deflects about 0.06 mm under 500 N. Joint stiffness, pad flatness and the whole machine loop are not included.

## Changing beds

Router to plasma:

1. Router off and isolated. Remove the spindle or raise Z fully.
2. Gantry at the front: remove the two **rear** M10 screws. They sit under the Y guide shoes when the gantry is at the back.
3. Gantry to the rear stop, head at X575. Remove the other four screws. All six and their washers go in the bolt tray on the reservoir lid.
4. Shackle the 4-leg sling to the four lugs, take up the slack and **lift 70 mm**. The pins leave the pads, and every part of the module passes at least 6 mm above the pan-float backrails.
5. Run the trolley forward about 1.42 m, guiding the module through the front window by hand. It has 11.2 mm to the frame legs on each side. Two people.
6. Lower the module onto its stand in front of the machine. Don't leave it hanging over a walkway. Clear chips, then follow the plasma water sequence ([WATER-CONTROL.md](../RevE-ENGINEERING/WATER-CONTROL.md)).

Plasma to router is the reverse. The last 70 mm lowers the module onto the pins; then refit the six screws (anti-seize, 30 N·m nominal) and re-probe the HDPE. With the module out, the seat pads (top Z846) stay 4 mm below the slat tops (Z850), and the slats are back to full height without the Rev G end reliefs. Wide plasma sheets therefore rest on the slats.

## What the owner provides

- **Hoist and beam:** overhead beam over the machine centreline, running from above the module's centre of mass (Y663) to at least 1.6 m in front of the machine, with trolley and hoist rated well above the module (a 250 kg class hoist is ample for 63 kg). **Hook height:** with the recommended sling (hook 1.0 m above the lug holes, legs about 1.26 m, 52° from horizontal), the hook sits at about 1.99 m above the floor with the module raised. Add the hoist's own headroom to find the minimum beam height, typically 2.4–2.6 m. A 0.7 m hook rise also passed the check, but its legs are at 42°, flatter than the usual 45° minimum.
- **Rigging:** 4-leg chain or round-sling bridle and four 3/8 in screw-pin shackles, sized for the module with the leg angle above.
- **Stand:** a stand or cart for the 1,026 × 1,337 mm module in front of the machine, clear of the lug and pin positions. Plan about 1.5 m of floor in front of the machine.

The hoist parks in front of the machine during cutting; the gantry and Z motor (top Z1370) pass under the beam line.

## What was checked

| Check | Result |
|---|---|
| Static interference, router state | 910 solids, 0 unresolved overlaps; STEP reimport matches |
| Static interference, plasma layout and module alone | 761 and 149 solids, 0 unresolved overlaps |
| Nine router poses (X/Y/Z travel corners and centre) | **Pass**: 910 solids in each pose, 0 unresolved overlaps ([motion check](motion/revh-full-machine-poses.json)) |
| Hoist path, module and 4-leg sling as one rigid body, gantry at the rear stop, spindle left in place as an obstacle | **Pass** at hook heights 0.7, 1.0 and 2.0 m above the lug holes: 74 sampled poses each (lift every 5 mm, travel every 25 mm), 0 intersections |

Nearest modeled gaps with the module raised 70 mm: frame legs 11.2 mm each side; float backrails 13.7–14.5 mm (6 mm above their tops); Y-block bolts 18.8 mm; Y guide shoes 23.2 mm; Z slide body 29.2 mm. The steepest sling (2.0 m) passes 22.3 mm from the X rail. These are nominal CAD gaps. Weld distortion, sling stretch, swing and debris all use them up.

Not checked or not released: rigging hardware, beam and hoist ratings; chain sag and shackle bodies; module weight; proof load of the lugs (lift once at twice the module mass before first use); pad coplanarity and repeat-seating map; actual 20100 section, nut fit and M5 preload; galvanizing distortion; the owner stand; human handling.

## What changed from Rev G

- **Removed:** six panels and 24 aluminum ties, four beams with feet, seats and sleeves, two removable front seats, 16 clamp bridges, six MDF spoilboards, all storage racks and the hardware rack on the cabinet cage. The controls cabinet no longer needs the bed reinstalled before it can be opened.
- **Restored:** full-height plasma slats (Rev G relieved both ends by 22 mm).
- **Added:** the module, six seat pads, six ledger sleeves, the bolt tray, and the module hardware listed in the cut list.
- **Extrusion:** nine 1,197 mm pieces from the same five two-packs (ten bars, one spare) instead of thirty 397 mm pieces.

Sources are in [RevE-ENGINEERING](../RevE-ENGINEERING/): `bed_revh.py` (module and receiver), `build_revh.py` (exports), `verify_revh_motion.py`, `revh_handling_check.py`, `render_revh.py`. Rev G ([RevG-CAD](../RevG-CAD/README.md)) stays as the in-footprint manual alternative.
