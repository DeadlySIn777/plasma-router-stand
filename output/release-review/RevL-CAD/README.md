# GM1 Rev L — 300 mm Z and a RapidChange tool changer on the bed

**GM1 — Garcia Mechanical Table.** Working design for review, **not released for purchasing, fabrication, CAM or operation.** In the previews, amber parts are purchased-part envelopes and magenta parts are allocations for the tool changer's magazine and stored cutters, not supplier drawings.

Rev L is [Rev K](../RevK-CAD/README.md) with these changes, all from 27 September 2026:

- **A 300 mm Z slide** instead of 100 mm. Ordered on 27 September.
- **A RapidChange-type automatic tool changer** ("yes i do"; "the rapidautochanger or something like that"). Its magazine retracts on a short slide, so the 800 × 1000 mm work area stays free.
- **Frame fill holes at each tube's high end.** The owner asked "are all my holes aligned so the sand fills the rails?" and is thinking of epoxy sand. See [Frame fill](#frame-fill).
- **The Z body raised 110 mm over the tool changer.** The owner caught it in the picture: "when it retracts, or it moves forward it will hit the autochanger", and "it has the lid on the autochanger too". The Z body's lower end sat below the magazine top, so the changer could only move with the head parked out of its way, by software alone. Now the body sits 110 mm higher on its carrier, on a taller tool adapter, and clears the magazine and a lid allowance by 17.65 mm: the changer can move with the head anywhere, and the gantry can cross the deployed magazine, with Z up. A hardwired interlock (controls M14) lets the dock move only with Z at its top. See [The 300 mm Z](#the-300-mm-z) and [Tool change](#tool-change-one-rule).

Everything else is Rev K's, unchanged: the frame apart from its fill holes, the one-piece bed module and its hoist, the water table, the plasma head and torch, the cabinet. The GM1 controls gain spindle reverse and the tool-changer drive (M12 and M13 in the [controls README](../../controls-2026-09-27/README.md)).

- [Router assembly STEP](step/RevL_ROUTER.step): dock parked, gantry at the rear stop, Z fully up
- [Bed module STEP](step/RevL_BED_MODULE.step): the module with the dock deployed, as the hoist lifts it
- [Dock STEP](step/RevL_DOCK.step): the tool changer alone, deployed
- [New parts](step/RevL_NEW_PARTS.step): the dock's parts, the 300 mm Z body and the frame parts whose fill holes moved, with the [component schedule](cutlist.csv), [operations](part-operations.json), [individual STEP parts](parts/) and [flat DXFs](dxf/)
- Previews: [router](previews/RevL_ROUTER.png), [router from the right](previews/RevL_ROUTER_side.png), [tool change](previews/RevL_TOOL_CHANGE.png), [dock close-up](previews/RevL_DOCK_DETAIL.png), [bed module](previews/RevL_BED_MODULE.png)
- Checks: [poses, dock travel, tool change and hoist path](revl-checks.json), [manifest and source hashes](engineering-manifest.json), and the validations of each STEP
- [What Rev L adds to the shopping list](../../../outputs/reve-30510/actual-cost/REVL-PROCUREMENT-DELTA.md)
- **[What to build while the parts arrive](BUILD-ORDER.md)**: the owner has the plasma cutter and torch, and all the drive modules are ordered (27 Sep). The HGR20 rails and the bed extrusion are still to come.

![Rev L dock close-up, deployed](previews/RevL_DOCK_DETAIL.png)

## The 300 mm Z

The ZBX80 is the same type with a longer body, and it sits 110 mm higher on the Z carrier than in Rev K. The spindle hangs where it did:

- The spindle nut still reaches Z960 at the bottom, 1.2 mm above the HDPE, so nothing changes for cutting. At the top it is at **Z1260** instead of 1060. The tool axis is unchanged.
- The body is 419 mm long, as the owner's listing drawing for the 300 mm stroke gives (530 mm with the motor). It runs **Z1150–1569**. Its lower end block (Z1150–1162) is level with the gantry's X blocks and Z carrier (Z1143), so nothing on the gantry hangs lower than the carrier plate, and the tool changer's lid allocation (top Z1132.35) passes under all of it.
- **Why it is raised.** In Rev L as first drawn the body's lower end was at Z1040, 90 mm below the magazine top. The changer could only move, and the gantry could only come near it, with the head first parked at X975; a wrong move would have driven the Z body into the magazine. Raising the body puts the whole gantry above the changer.
- **The drop adapter.** The tool adapter that bolts to the Z carriage is now 110 × 220 × 12.7 mm instead of 110 × 110 (`TOOL_ADAPTER_110x220_DROP`). Its lower 110 mm is the Rev K adapter, so the spindle clamp and the plasma drop bracket mount unchanged; the two carriage slots sit 110 mm higher, at its top. Stiffness screen: the 12.7 plate cantilevered 110 mm deflects about 0.04 mm per 100 N at the clamp; light cuts (10–20 N) give under 0.01 mm. It stays provisional until the carriage is measured.
- **Bolting.** The Z carrier plate is unchanged (Z1143–1313). The body's base overlaps it over its lowest 163 mm; use at least three M5 slide nuts per base slot there.
- The braked motor's top moves to **Z1740.5**, 1.74 m above the floor. Nothing on the machine is above it, and it is under the 8 ft ceiling (2.44 m) and the A-frame beam.
- The plasma torch tip still reaches Z845–1145.
- The plasma torch tip now reaches Z845–1145.

**Why 300 and not 200.** RapidChange asks for at least 90 mm between the magazine and the spindle nut with Z fully up. The magazine sits on a tray above clamped stock, at Z1050.35.

- A 200 mm Z would give 110 mm, which is 20 mm to spare.
- A 300 mm Z gives **210 mm**. That leaves room for longer tools, taller clamps, and whatever the delivered magazine and its cover really measure. The allocation here is 80 mm tall, and the kit's real height is not published.
- The cost is a slightly dearer slide, 100 mm more height and about a second more per tool change.

An earlier note (commit `3a674bf`) said the dock would have to sit up to 45 mm higher to clear the bed lift. It doesn't: Rev L mounts it on the bed module instead (below), which keeps the other session's magazine height. The recommendation stays 300 mm, for the margin.

## The tool changer (dock)

The dock rides **on the one-piece bed module**, behind the HDPE. Every part is named `MOD_ATC_*`, so it is part of the module:

- **It lifts out with the bed.** Nothing has to come off the machine before a bed change.
- **Plasma never sees it.** In plasma mode the module, and the dock with it, are on their stand outside the machine.
- **Nothing is added to the frame.**

The other session's carrier (base branch, [retractable ATC](../../../variants/retractable-atc/README.md)) was drawn for the six-panel bed. On this bed its rails and shelves would sit where the module rises 70 mm, and where the rear lifting lugs and sling legs are. Rev L keeps its heights and its 200 mm stroke and moves the guides onto the module.

| Item | Rev L |
|---|---|
| Guides | Two HIWIN MGNR12 rails, 281 mm, one MGN12H block each, at X295 and X855 |
| Rail beams | 1 × 2 in steel tube on two T-slot feet each, bolted into the strips' top slots at X275/315 and X835/875, behind the HDPE (Y1170–1280). Each beam runs back past the module's rear edge to Y1445 |
| Rail seat | Steel bar on the tube, machined flat at Z1007 after welding |
| Carrier | One 1/4 in steel plate at Z1020–1026.35: a tray under the magazine and two arms back to the blocks. The middle behind the tray is open |
| Magazine | Allocation 520 × 60 × 80 mm on two blank aluminum saddles; support plane **Z1040.35**; pocket line **Y1100** when deployed. A 12 mm lid allocation sits on top (Z1132.35), so the closed magazine passes 10.65 mm under the gantry's X blocks and Z carrier when parked |
| Stored cutters | Up to 15 mm diameter, hanging at most 36.55 mm below the magazine (Z1013.8), through a window in the tray |
| Travel | 200 mm. **Deployed:** magazine at Y1070–1130, over the rear 60 mm of the bed. **Parked:** Y1270–1330, behind the Z body and under the gantry |
| Drive | 24 V worm gearmotor (about 30 rpm) and a GT2 belt on the right beam; about 20 mm/s, 10 s end to end. The worm holds the carrier |
| Stops and sensing | A fitted front stop is the deployed datum (the pocket positions depend on it); a soft rear stop. One end microswitch per direction cuts the motor at the end. Two M8 inductive sensors tell the Rodent where the carrier is |
| Connection | One M12 8-pin plug at the back of the module, for the motor and the sensors. Unplug it before a lift. The magazine's cover and IR lead need a second plug, not yet defined |
| Mass | About **10.6 kg**, with 3.3 kg allowed for the magazine and cutters. The module becomes about 74 kg |

**Clamping near the back of the bed.** When deployed, the tray covers the rear 65 mm of the HDPE (Y1065–1130), with its lowest screw heads at Z1015 and the stored cutters at Z1003.8. In that strip, keep stock and clamps under **40 mm** tall (50 before the magazine was lowered 10 mm to fit its lid under the gantry). Elsewhere the dock does not limit them.

### Tool change: one rule

The Z body and the rest of the gantry now clear the magazine and its lid, so the only thing that can hit the changer is the spindle itself, low over it. **Rule: the dock moves, and the gantry crosses the deployed magazine, only with Z within 73 mm of its top** (z_lift ≥ 227.35: a 40 mm cutter in the spindle then clears the lid by 15 mm). Controls **M14** enforces it in hardware: the dock motor's feed runs through a second contact of the Z top switch, so the dock cannot move unless Z is at its top, whatever the firmware does.

The sequence:

1. Stop the spindle and raise Z fully.
2. Deploy the dock, from anywhere, and wait for its "deployed" sensor.
3. Move the gantry to the pocket line (gantry Y1253.6) and along X to each pocket. RapidChange unloads in reverse (M4, about 1600 rpm) and loads forward (M3, about 1500 rpm). Go back up to full Z between pockets.
4. Raise Z fully, park the dock, wait for "parked", and carry on.

The RapidChange grblHAL macros can use their normal approach. The checks below drive the gantry over the deployed magazine with Z up, and run the dock with the head at X175, X575 and X975: all clear.

### Changing beds with the dock

**Router to plasma:**

1. SETUP, bed key UNCONFIRMED. Take the spindle out, as in Rev K.
2. Z fully up, gantry to the rear stop, head at X575. **Deploy the dock.**
3. **Unplug the dock** at the back of the module.
4. Lift and roll out as in Rev K, with two changes:
   - **Hook over Y745**, the module's new centre of mass, instead of Y670. With the 0.7 m sling, the rear legs are about 70 mm shorter than the front ones. Use a chain sling with shortening clutches.
   - **Roll about 1.52 m** instead of 1.42, because the dock's rear end is at Y1449.
5. Set the module down with the magazine up. It sticks up about 175 mm above the HDPE with the lid.
6. Plasma as in Rev K.

**Plasma to router:** lower the module in and refit the six screws, as in Rev K. Then plug in the dock, park it (Z up) and **probe the pocket reference** before the first tool change. RapidChange needs the pockets within 0.2 mm, and the module's locating pins are not proven to that.

## Frame fill

The frame's 18 tubes are separate sealed compartments, each with one fill hole. Nothing connects them.

Rev K's holes were placed for access. With a runny mix and the frame level, they fill the legs about 78 % and the top rails and front cross tubes about 25 %.

`ballast_revl.py` moves each hole to its tube's high end. The Ø30 weld bung and M20 plug are unchanged:

| Tubes | Hole | Epoxy sand | Dry sand |
|---|---|---|---|
| 6 legs | 35 mm below the top (Z965). Outer face on the front legs; rear face on the others, whose outer faces carry the brace gussets | 95–96 % | 96 % |
| 2 top rails | In the rear end cap (new part SAND_ENDCAP_2IN_PORTED) | 97 % | 100 % |
| 4 lower side tubes | On top, 40 mm from the rear end | 99 % | 93 % |
| 2 bed ledgers | On top at Y1370, unchanged | 98 % | 94 % |
| 4 cross tubes | At the right-hand end: on top of three, on the front face of the front lower tube | 94–100 % | 92–96 % |

- **Epoxy sand:** two pours. First with the rear raised 15° (the legs and the front-to-back tubes), then with the right side raised 15° (the cross tubes).
- **Dry sand:** stand each tube near vertical.

The percentages are the model's estimate: the part of each cavity below a level surface through the lowest point of its hole. The procedure is in the [build order](BUILD-ORDER.md#6-filling-the-frame). The old holes are closed in the model, nothing else in the frame changes, and every pose check below includes the new holes.

## Controls

These are M12 to M14 in the [GM1 controls](../../controls-2026-09-27/README.md), with their simulation checks (1,424 pass).

- **Spindle reverse (M12).** RapidChange unloads with the spindle in reverse. A force-guided relay K_DIR at the end of the run chain sends the run command to FWD or REV, never both. The Rodent's spindle direction goes to the V-MOS HE1 output (GPIO2).
- **Dock drive (M13).** Two relays (run and direction) drive the gearmotor. Its 24 V comes through the E-stop contactors and a spindle-run interlock, so the dock cannot move while the spindle is commanded, and it stops at every E-stop. The end microswitches stop it even if a relay welds.
- **Z-top enable (M14).** The dock motor's feed passes a second contact of the Z top switch, closed only with the Z carriage at its top. The dock cannot move with the spindle low, whatever the macro commands, even with the run relay welded.
- **I/O.** The Rodent reads the two dock sensors and drives the two relays through its MCP23017 expander. Inputs and outputs are reserved there for the magazine's IR check and cover.
- The RapidChange electrical interface (cover, IR) comes from the delivered kit.

## What was checked

`verify_revl.py` → [revl-checks.json](revl-checks.json). Every record is hash-bound to its sources.

| Check | Result |
|---|---|
| Router: the X/Y/Z travel corners (Z 0 and 300) and the centre, dock parked | **Pass**: 9 poses, 0 unresolved overlaps |
| Plasma: the same nine poses and Rev K's three plasma-only poses, module and dock out | **Pass**: tip Z845–1145; over slat 8 it is 5.0 mm below the slat top, within the 6 mm float |
| Dock travel, 0–200 mm in 20 mm steps, gantry at the rear stop, Z up, with the head at X175, X575 and X975 | **Pass**: 33 positions. The changer moves with the head anywhere |
| Gantry over the deployed magazine with Z up: gantry Y1150, 1200 and 1230 at head X575, and Y1150 at X345 and X805 | **Pass**: clear. Before the raise this pose clashed |
| Z body above the lid allocation | 17.65 mm (Z1150 over Z1132.35) |
| Tool change: spindle on the pocket line at X345, X575 and X805, at Z up and 5.65 mm above the lid | **Pass** |
| Tool change: nut at the magazine plane | Only the pocket interface is touched: the magazine, lid and stored-cutter allocations, and at the end pockets the saddle blanks by 0.35 mm, because the spindle is drawn as a Ø65 cylinder right down to the nut. The Z body, adapter and clamp clear the dock |
| The Z rule | The dock may move with z_lift ≥ 227.35 (a 40 mm cutter clears the lid by 15 mm); the check requires that to be at least 65 mm below the top, so the M14 interlock's "Z at top" has margin |
| Deployed dock against 40 mm of stock and clamps over the HDPE | **Pass**: clear |
| RapidChange 90 mm rule | 127.65 mm from the lid to the nut at full Z (219.65 from the magazine plane) |
| Hoist path with the dock deployed on the module: hook 0.7, 1.0 and 2.0 m above the lugs, over Y745, rolled 1.52 m | **Pass**, 78 sampled poses each, and no sling leg touches the dock. At 0.7 and 1.0 m the nearest gaps are Rev J's: frame legs 11.2 mm, float backrails 14.5 mm. At 2.0 m a rear leg passes **2.9 mm** from the rear-parked X rail (8.6 mm in Rev K), because the hook moved back over the new centre of mass: don't use the 2.0 m sling. The container plan uses 0.7 m |
| Frame fill: one hole per frame tube; none faces down in its fill attitude; every tube at least 90 % full (epoxy with the 15° tilts, dry sand near vertical) | **Pass**. The lowest estimates are 93.7 % (epoxy, front lower cross tube) and 91.9 % (dry sand, rear upper cross tube). Every pose above includes the moved holes |
| Static interference of the exported states: router with the dock parked (1,299 solids), bed module with the dock deployed (228), dock (79), new and changed parts (136) | 0 unresolved overlaps; STEP reimport matches |

These are nominal CAD checks. They do not cover stiffness at the pocket, the delivered magazine, cable routing, or the sling's real shackles.

## Still open

- **The magazine.** Pocket count, pitch, mounting holes, nut datum, cover sweep and cable come from the delivered RapidChange kit. The saddles stay blank until then. Its height sets the parked clearance: the 80 mm allocation leaves 12.6 mm under the gantry's Z carrier at the rear stop.
- **Pocket accuracy.** RapidChange asks for 0.2 mm. The front stop and the preloaded belt clamp should repeat to 0.05 mm; prove it in 20 cycles with an indicator. Probe the pocket reference after every bed install.
- **Stiffness.** One block per rail. The load at the pocket is a nut threading on at low speed, but check the tray's deflection under a 150 N push at the pocket.
- **Drive parts.** The gearmotor, pulleys, belt clamp spring and sensors are chosen by function. Fit the gearmotor's face to the motor plate once it is in hand.
- **Tool length.** A tool setter is not drawn. It could sit on the dock's right saddle.
- **Chips and coolant.** The rails, belt and gearmotor sit at the back of the bed. Cover the rails (a sheet-metal cover or bellows) and use a sealed gearmotor or shield it; neither is drawn. The sensors and the plug are IP67 parts.
- **The Z slide.** The 300 mm listing drawing confirms the 419 mm body. The height from its base to the carriage top is still not dimensioned: the model assumes 80 mm, and the drawing scales to about 62 mm. If it is about 62, the spindle and torch sit about 18 mm further back and the checks are re-run. Measure it, the carriage and the end blocks on receipt, as MOTION-MODULES.md lists.
- **The lid.** Its 12 mm closed height is an allowance, and its open sweep (it slides along the magazine) is not drawn. Check the kit's cover against the 520 mm length and the height budget: cutters 40 mm above the HDPE below, the gantry's Z1143 above.
- **The drop adapter.** Provisional until the Z carriage is measured; a 12.7 plate. If the first cuts show chatter, add two side ribs.
- **Rigging.** The chain sling needs shortening clutches for the rear legs. At the 0.7 m hook height the front legs sit at about 41°; use rigging rated for that angle. Don't use a 2.0 m hook rise: a rear leg then passes 2.9 mm from the X rail.
- **Frame fill.** The fill percentages are geometric. A real pour leaves voids unless each tube is vibrated, so weigh the frame before and after.
- **Rev K's open items** still apply.

## Sources

In [RevL-ENGINEERING](../RevL-ENGINEERING/), kept apart so the Rev K and shared RevE-ENGINEERING source inventories are unchanged:

- `build_revl.py`: builds the states and exports them; Rev K's `build_revk.py` is used unchanged.
- `z300.py`: the 300 mm Z slide on Rev J's motion model, raised 110 mm with the drop adapter.
- `atc_revl.py`: the dock.
- `ballast_revl.py`: the frame's fill holes, and their fill estimates.
- `verify_revl.py`: the checks above.
- `render_revl.py`: the previews.
