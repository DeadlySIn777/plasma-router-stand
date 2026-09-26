# Drive modules — receiving and measuring (HMS40 ×3, ZBX80)

**Status (26 September 2026): the Y modules are ordered and on the way; the X module and the Z slide are to be ordered on Monday 28 September.** That split comes from the owner's other session, recorded on the base branch the same day. This file first recorded all three as ordered, from the owner's message that the shared spec sheets "are ordered", so please confirm. The HMS40 spec sheet (KHMOS drawing HMS40-L□□-S□□□-M57-BC) and the ZBX80 listing drawings shared that day are the selected items; the owner first described them as "1000x800x100". They are:

| Row | Listing | Use | Quantity in the design |
|---|---|---|---:|
| M02 | [KHMOS HMS40, 1000 mm stroke, 10 mm lead, NEMA23](https://www.amazon.com/dp/B0C7GN24S1) | Y drives (one per side) | 2 |
| M01 | [KHMOS HMS40, 800 mm stroke, 10 mm lead](https://www.amazon.com/dp/B0C7GQTRRX) | X drive | 1 |
| M03 | [RATTMMOTOR ZBX80, 100 mm, SFU1605, NEMA23](https://www.amazon.com/dp/B09MVYGLNQ) | Z slide | 1 |

Please confirm the quantities (the machine needs **two** 1000 mm modules), the price paid and the delivery dates in [the register](drive-modules-receiving-register.json).

**The HGR20 guide-rail kits are still needed.** In this design the HMS40 modules only push; the separate HGR20 rails ([M04, M05](HGR20-RAIL-KITS.md)) carry the gantry and the cutting loads. The HMS40's own internal 12 × 8 guide is rated 20 kg horizontal with 12–15 N·m moments, while a 100 N side load on a 250 mm tool lever is already 25 N·m. Those kits are not recorded as ordered.

## What the drawings already give, and what the model uses

**HMS40** (supplier drawing HMS40-L□□-S□□□-M57-BC dated 10 Feb 2026, `output/release-review/sources/HMS40-dimensioned-drawing-2026-02-10.jpg`, and the listing the owner sent):

| Item | Supplier value | Model |
|---|---|---|
| Screw and lead | Ø16 ball screw, 10 mm lead | 10 mm lead |
| Rated thrust / max speed | 251 N / 350 mm/s at 10 mm lead | 250 N screen load |
| Payload rating | 20 kg horizontal, 10 kg vertical | drive-only use |
| Length with NEMA23 stepper | L = S + 145: 1145 mm (1000 stroke), 945 mm (800 stroke) | body S + 125, motor from S + 145 |
| Section, carriage top | 42 wide × 60 high; carriage top 65.5 above base | same |
| Carriage fixing | 4 × M4, 10 deep, on 30 × 30 | same |
| Base fixing | two bottom slots with M4 slide nuts, 28 mm apart; M3 slide nuts in the side slots | **hold**: slot cavity and nut not modeled |
| End of travel | drawing marks motion limits of 50 mm at the motor end and 10 mm at the far end; the reference faces are not fully clear | **hold**: endpoint datum |
| Mass | 4.6 kg (1000), 3.9 kg (800) | not used |
| Motor | Standard NEMA23 5756 stepper (57 mm frame, 56 mm long); current and torque curve not published | **hold** |
| Coupling | Φ8 × Φ10 (8 mm motor shaft to 10 mm screw end) | not modeled |
| Sensors | FC-SPX307 NPN, mounted outside the module (the sheet does not say whether they are included) | model uses roller switches; **check** what arrived |
| Repeatability | ±0.02 mm per 300 mm (listing); ±0.03 in the drawing table | not used |

**ZBX80** (listing images `B09MVYGLNQ-gallery-*.jpg`):

| Item | Listing value | Model |
|---|---|---|
| Body | 219 × 80, 12 mm end blocks, 330 overall with the motor | same |
| Carriage | 90 across × 50 along; Ø5 holes 70 apart across, plus Ø7 bores | **hold**: thread and along-travel pitch |
| Heights | end block 67 high at the free end, 78 at the motor end; base 20 high | not all used |
| Base face to carriage top | not dimensioned; about **60–67 mm** when the side view is scaled | **80 mm assumed** |
| Base fixing | M5 slide nuts in the base slots; bottom view dimensions 80 overall, 66, 54, 26 and 14 across the slots | **hold**: slot positions to confirm |
| Screw | SFU1605, 5 mm lead | — |

If the ZBX80 output face really is 60–67 mm above its base instead of 80, the whole tool sits 13–20 mm further back than modeled. The tool-axis Y range would move 13–20 mm rearward, from Y121.4–1121.4 to about Y134–141 at the front limit and Y1134–1141 at the rear. The front spoilboard edge (Y130) would then be a few millimetres in front of the tool axis, still reachable with a cutter of normal radius, but the tool sweep and clearances must be re-run.

## Measure on receipt

**Each HMS40:**
1. Overall length, width, height; carriage top height above the base bottom; carriage top hole pattern and thread depth.
2. Power off, move the carriage by hand to each end. Measure the carriage position from each end-block face: this is the endpoint datum.
3. Bottom slots: number, spacing, opening width, cavity depth, the nuts supplied (thread and size) and how far they slide.
4. Motor label (model, rated current, step angle), lead exit and connector; coupling; any sensor supplied. If FC-SPX307 NPN sensors came with the modules, note their thread, cable and supply voltage: they could replace the modeled roller switches, subject to the Rodent input check.

**ZBX80:**
1. **Base bottom face to carriage top face**: the key number for the head position.
2. All carriage holes (Ø5 and Ø7): position from two carriage edges, tapped or clearance, thread and depth, and whether reachable from behind.
3. Base slot positions and nut thread; carriage position at each end of travel; motor label.
4. **Back-drive test**: stand the slide vertical with the motor unpowered and a representative weight on the carriage. Does it creep down? Whatever the result, a normally-engaged brake or counterbalance is still required before a suspended tool is enabled (Z power-loss hold).

Record the values in `drive-modules-receiving-register.json`. The model can then be updated (tool axis position, adapter plate holes, base clamps, travel stops) and the motion and bed checks re-run.
