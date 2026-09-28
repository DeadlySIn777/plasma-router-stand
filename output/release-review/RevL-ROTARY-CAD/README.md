# GM1 Rev L, rotary variant: a 4th axis for plasma tube notching

**Working design, not a fabrication release.** The owner asked (28 September): "can we add a 4th axis for the plasma/cnc? plasma for tube knotching". This package is [Rev L](../RevL-CAD/README.md) (frame, water table, plasma head, Z, dock) with one bolt-on addition at the back of the frame: a hollow four-jaw rotary on a shelf over the rear cross tube, its axis along Y on the tool-axis centre line (X575), so a tube in its chuck lies forward over the water pan and the torch notches it by running along Y while the tube turns. Nothing on the bed module changes, the module still slides out of the front window for a bed change, and the rotary stays fitted for router work. Sources: [`rotary_revl.py`](../RevL-ROTARY-ENGINEERING/rotary_revl.py), [`build_revl_rotary.py`](../RevL-ROTARY-ENGINEERING/build_revl_rotary.py), [`verify_revl_rotary.py`](../RevL-ROTARY-ENGINEERING/verify_revl_rotary.py); Rev L's sources are used unchanged.

## Why it is a plug swap, not a fifth axis

The BTT Rodent has **four stepper drivers**, and GM1 uses all four: X, Y1, Y2 (the second, squared Y motor) and Z. There is no fifth output, and no spare GPIO set for an external driver. So the rotary runs on the **X driver**: its motor cable ends in the same 4-pin plug as the X motor's, and one of the two is in the cabinet's X receptacle. In rotary mode:

- the tube lies along Y, so the torch moves along the tube on the two Y motors (squared, homed, unchanged);
- "X" commands turn the tube: the post-processor writes the rotation as X, in degrees or in mm of arc, and a macro sets `$100` to match ([controls, rotary mode](../../controls-2026-09-27/README.md#rotary-mode-tube-notching-on-the-x-driver));
- the X carriage stays where it was put. Its ball screw is not self-locking, so don't lean on the gantry during a tube job, and re-home X after swapping back.

**Swap only with the E-stop pressed** (the 48 V is off through K1/K2): a stepper driver that is hot-plugged loses its output stage. The relay logic, the door input and the torch-start chain are untouched; the [second E-stop](../../controls-2026-09-27/README.md) (M20) is at this end of the machine, by the chuck.

## Why the back, not the front

The first draft put the chuck at the front on a cross tube between the front legs. The hoist check caught it: the bed module leaves the machine by rising 70 mm and sliding out of the front window, and the chuck sat in that path. The rear upper cross tube (Y1399–1450, Z679–730) is behind everything that moves: the module's rear edge is at Y1347.8, the gantry's beam stops at Y1395 and 1155 up, and the dock's beams and motor sit at the sides.

## Where it sits

| Item | Rotary variant |
|---|---|
| Shelf | A U of 2 × 4 × .083 in steel tube on edge: two 240 mm rails at X465–516 and X634–685, from the rear cross tube's front face (Y1399) to Y1639, and a 118 mm tie at the back; a 1/4 in plate 220 × 240 on top (Z831.6–837.95). The rails sit on the cross tube (Z730) and cantilever 189 mm behind it |
| Fixing | Two M10 × 130 through-bolts, one per rail, in **sleeves welded through the rear cross tube before the frame is filled** (bolts and sleeves not drawn; the build order lists the sleeves) |
| Rotary | Allocation 210 × 200 × 175 on the plate (spindle housing, about 6:1 belt reduction, NEMA 23), axis at **X575, Z954.3**. Chuck Ø125 × 65 (K72-125 class, four independent jaws, hollow), face toward the machine at **Y1380** |
| Clearance to the bed | The chuck face is 32 mm behind the bed module's rear edge (Y1347.8) and 15 mm behind the BT30 variant's carrier tray when parked (Y1365): the rotary stays fitted in router mode with either dock, and the module lifts and slides out of the front as before |
| Tube | Along Y from 20 mm inside the jaws (Y1400) forward. A Ø60 tube runs Z924.3–984.3; a Ø100 tube Z904.3–1004.3, 54.3 mm over the slats (Z850) and 69.3 mm over the pan walls (Z835). Long tubes pass out of the front over the low front cross tubes (Z152) and the cabinet's drip cap (Z679); a roller stand supports them there |
| Torch reach | The torch axis runs Y73.6–1073.6 (Rev K), so the nearest cut to the jaws is **306 mm** from them and 1000 mm of tube is under the torch: notches go at the tube's free end, and the shortest piece is about 320 mm. A Ø60 tube's top is touched at z_lift 139.3, a Ø100 tube's at 159.3, within the 300 mm Z |
| Mass | About 19.07 kg on the rear cross tube (the rotary and chuck 13.5 kg as placeholders) |

**The cut.** Probe the tube's top line with the float (the same touch-off as on a plate), set the standoff, run THC off. The CAM unwraps the tube surface: X (the rotation) and Y (along the tube). The chuck's independent jaws centre round and square tube; check the delivered unit's through-bore (40–50 mm on the units this envelope was drawn from) against the tube you want to pass through it. The plasma head is 117 mm wide, so at plate height keep the torch 110 mm off a chucked tube's axis.

## What was checked

`verify_revl_rotary.py` → [revl-rotary-checks.json](revl-rotary-checks.json). Every record is hash-bound to its sources (this folder's and Rev L's).

| Check | Result |
|---|---|
| Ø60 × 1200 tube (Y200–1400): torch tip on the tube top at Y200, Y575 and Y1073.6 (z_lift 139.3), then 4 mm over it | **Pass**: 6 poses; the touch meets nothing but the tube, the cut height nothing |
| Torch at Z0 beside the tube, 110 mm either side of its axis (X465 and X685 at Y575) | **Pass**: clear of the tube, tip on a slat within the float |
| Ø100 tube at the cut height (z_lift 163.3) | **Pass**: clear; the head hardware stays above the tube |
| Ø60 × 1500 tube out of the front, torch at Y200 | **Pass**: clear over the front cross tubes and the cabinet |
| Plasma: Rev L's nine corner poses and Rev K's three, with the rotary fitted and no tube | **Pass**: 12 poses, 0 unresolved overlaps; over slat 8 the tip is 5.0 mm below the slat top, within the 6 mm float |
| Router: the nine corner poses with the module in and the dock parked, and the dock deployed at the rear stop | **Pass**: 10 poses, 0 unresolved overlaps |
| Chuck face behind the bed module's rear edge | 32.2 mm (at least 10 required; 15 mm behind the BT30 dock's parked tray) |
| Nearest cut to the jaws | 306.4 mm (under 320 required) |
| Hoist path with the dock deployed and the rotary fitted: hook 0.7, 1.0 and 2.0 m above the lugs, 70 mm up then 1.52 m out of the front | **Pass**, 78 sampled poses each. Nearest gaps: 0.7 m: MOD_RAIL_L to MF_LEG_1_1 11.2 mm; 1 m: MOD_RAIL_L to MF_LEG_1_1 11.2 mm; 2 m: SLING_LEG_3 to X_RAIL_1 2.8 mm. |
| Static interference of the exported states: router with the rotary fitted (1,308 solids), plasma with the tube (1,082), new parts (6) | 0 unresolved overlaps; STEP reimport matches |

10 of 10 checks pass; 1,717 s; sources unchanged during the run.

These are nominal CAD checks: static positions of allocations. They do not cover the rotary's runout, the tube's sag between the jaws and the torch, the unit's real footprint, or the cut itself.

## Still open

- **The rotary unit.** Envelope only. Its base holes, height to the axis, through-bore and motor come from the delivered unit; the shelf plate is drilled from it and the touch-off heights follow its axis height.
- **Tube sag.** The tube is a cantilever from the chuck: a 50 × 50 × 3 tube droops 0.3 mm at 1.25 m, a 25 × 25 × 1.5 tube 1.3 mm. The float touch-off at the notch corrects the start height; long or thin tubes rest on the roller stand at the front.
- **Slag on the jaws.** The chuck is 306 mm from the nearest cut. A strip of sheet between the chuck and the pan's rear wall would keep slag off it; not drawn.
- **Short pieces.** Anything under about 320 mm cannot reach the torch from the jaws: notch it on the end of a longer bar and cut it off after.
- **CAM.** A tube-unwrapping post that writes the rotation as X, and the settings macro, are not in this repository.
- **The BT30 variant** shares this rotary unchanged (same frame, gantry and plasma head); its parked spindle sits on the reservoir lid at Z500, far below the tube, and its longer carrier tray parks 15 mm in front of the chuck. Not checked as a separate package.
- **Rev L's open items** still apply.

## Sources

- [`rotary_revl.py`](../RevL-ROTARY-ENGINEERING/rotary_revl.py): the shelf, the rotary and tube allocations.
- [`build_revl_rotary.py`](../RevL-ROTARY-ENGINEERING/build_revl_rotary.py): the exports in this folder ([manifest](engineering-manifest.json), [cut list](cutlist.csv), [step](step), [dxf](dxf), [previews](previews)).
- [`verify_revl_rotary.py`](../RevL-ROTARY-ENGINEERING/verify_revl_rotary.py): the checks above.
- [What it adds to the shopping list](../../../outputs/reve-30510/actual-cost/REVL-ROTARY-PROCUREMENT-DELTA.md).
