# GM1 Rev K — one-piece bed, completed for router and plasma

**GM1 — Garcia Mechanical Table.** Working design for review, **not released for purchasing, fabrication, CAM or operation.** Amber parts in the previews are purchased-part envelopes whose interfaces are not all verified.

> **Continued as [Rev L](../RevL-CAD/README.md) (27 September 2026).** Rev L keeps Rev K unchanged and adds a 300 mm Z and the owner's RapidChange tool changer, mounted on the bed module. With Rev L, the bed-change steps below gain two (deploy the tool changer, unplug it), the hook moves over Y745 and the roll is 1.52 m.

Rev K is where the one-piece bed line stands after the owner's "finish it" (27 September 2026). It is [Rev J](../RevJ-CAD/README.md) with three additions:

- The other session's **Rev I head, plumbing and cabinet**, adopted and adapted to the one-piece bed.
- The **owner's torch**, from the photo sent on 27 September: a straight PT31-style machine torch, 270 mm long with a 28 mm barrel (seller's figures).
- Fixes for the **findings of the [26 September review](../../review-2026-09-26/README.md)** that were still open: plasma reach, the cabinet, water and coolant, and the float trip. The controls side is in the [GM1 controls](../../controls-2026-09-27/README.md) (M9–M11).

The bed module, frame, water table and motion are Rev J's, unchanged. **The owner chose this one-piece line on 27 September** ("the one piece"). The other session's six-panel [Rev I](../RevI-CAD/README.md) stays in the repository as the alternative.

- [Router assembly STEP](step/RevK_ROUTER.step): bed module installed, plasma head and bracket parked on the reservoir lid
- [Plasma assembly STEP](step/RevK_PLASMA.step): module out, router tool stored, head, drop bracket and torch on the Z adapter
- [Bed module STEP](step/RevK_BED_MODULE.step): the part the hoist carries (unchanged from Rev J)
- Previews: [router](previews/RevK_ROUTER.png), [router front](previews/RevK_ROUTER_front.png), [plasma](previews/RevK_PLASMA.png), [plasma front](previews/RevK_PLASMA_front.png), [module](previews/RevK_BED_MODULE.png)
- [Component schedule](cutlist.csv), [operations](part-operations.json), [individual STEP parts](parts/), [flat DXFs](dxf/)
- Checks: [poses, hoist path and water fixes](revk-checks.json), validations for the [router](RevK_ROUTER-validation.json), [plasma](RevK_PLASMA-validation.json) and [module](RevK_BED_MODULE-validation.json), [manifest and source hashes](engineering-manifest.json)
- [What Rev K adds to the shopping list](../../../outputs/reve-30510/actual-cost/REVK-PROCUREMENT-DELTA.md)

![Rev K plasma](previews/RevK_PLASMA.png)

## What Rev K adds to Rev J

| Area | Rev K | Review finding |
|---|---|---|
| Plasma reach | A 1/2 in aluminum **drop bracket** between the Z adapter and the Rev I head. It lowers the head 135 mm and moves it 12.7 mm forward. The torch tip reaches **Z845 at the bottom of Z**, 5 mm below the slat tops, and Z945 at the top. | Blocker 4 |
| Plasma head | Rev I's floating (6 mm) and breakaway head, unchanged except the clamp insert is bored to 28.10 mm for the owner's torch. A 28 mm clamp collar on the barrel sets the torch height on every refit. | Rev I work adopted |
| Level sensors | An operating rule, checked: with the torch low, plasma paths stay at X955 or less in the sensor band (Y558–765). No sheet can lie over the sensors anyway. At the top of Z the torch clears them at full X. | Minor: sensor guards above the slats |
| Float trip | The float switch now stops a cut: torch off and feed hold (controls M11). | Major: a float trip triggers nothing |
| Router coolant | The pan drain closes after the router-mode dwell (controls M9), and a **screen basket** in the pan drain catches chips and dross. | Major: router mode leaves the drain open |
| Pump | Fill watchdog (controls M10). | Major: no fill time limit |
| Seals | Nitrile (NBR) instead of EPDM wherever water or coolant reaches. | Major: EPDM not oil-tolerant |
| Draining | A **manual drain valve** on the reservoir with a garden-hose outlet. | Major: no manual drain |
| Suction line | Rerouted so it only rises from the pickup to the strainer. | Major: 3/8 in line with a high point |
| Refill spout | 2 mm higher: 32 mm air gap. | Minor: 30 mm air gap |
| Plumbing | Rev I's drain valve and removable tail, strainer carrier and hoses. The pressure hose is lowered 20 mm to meet the Rev J spout. | Rev I work adopted |
| Cabinet | Rev I's 500 × 400 × 200 box with four fixes: a shorter drip lip so the door opens, 30 cable entries on two bonded gland plates, a filter fan and exhaust filter, and the VFD moved outside under its own drip roof. | Majors: door, entries, EMC, heat |
| Torch start | The start relay moves to a shielded box at the cutter (controls README), so no HF-exposed lead enters the cabinet. | Major: HF leads in the cabinet |

## Plasma: head, bracket and torch

**The torch.** The owner's photo shows a straight PT31-style machine torch: 270 mm long, 28 mm barrel, pink ceramic cup with a standoff guide. The model uses the seller's two figures. The lower 105 mm (cup, guide, front sleeve and ring collar) is a Ø30 envelope, because those diameters are not published. The straight rear barrel starts about 105 mm above the tip, scaled from the photo.

**Where it sits.** The clamp holds the rear barrel with its lower face **115 mm above the tip**, clear of the ring collar. The torch axis is at machine X and Y = gantry Y − 201.4. So at full travel the torch reaches:

- X175–975 by Y73.6–1073.6;
- on the slats (X135–1015, Y150–1233), a cutting area of **800 × 924 mm**.

The rear 160 mm of the slats is out of the torch's reach. Set work zero with the torch, not the spindle.

**The level sensors.** The three pan level sensors (X978–1015, Y578–745) stand 10–35 mm above the slat tops, so no sheet can lie over them.

- With the torch below Z900, keep plasma paths at **X955 or less in the band Y558–765**. CAM sheet limits do this; a plasma-mode soft limit in the firmware would enforce it.
- At the top of Z (tip Z945), the torch clears them at full X, so homing and fully raised rapids are safe.

A sideways offset of the head was tried to move the torch out of their way and dropped: at X175 the head is only 13.5 mm from the gantry's left Y shoe and its bolts.

**Z limit.** At the bottom of Z the tip is 5 mm below the slat tops. With no sheet, the 6 mm float takes that up before its hard stop, so Z can bottom out without damage. With a sheet on the slats, the float switch trips first: while probing, the Rodent's probe input stops the move; during a cut, the M11 float stop drops the torch and holds feed. The bottom of the Z stroke is the plasma Z limit; no Z soft-limit change is needed between tools.

**Setting it up (once, at commissioning):**

1. **Bore the insert.** Measure the barrel with calipers: diameter, roundness within 0.10 mm, and a straight 40 mm. Then bore the split insert to the measured diameter + 0.10. The model shows 28.10 for the seller's 28.
2. **Set the torch height.** Clamp the torch with the insert's lower face 115 mm above the nozzle tip. Fit the clamp collar on the barrel against the clamp top.
3. **Set the bracket.** Jog Z to the bottom with the torch over a slat gap. Loosen the four M6 slot screws and set the head so the nozzle is 5 mm below the slat tops: use a straightedge across two slats and a 5 mm gauge. Tighten the screws and scribe a witness line. The slots give ±25 mm, so a torch clamped 90–140 mm above its tip still fits.
4. **Set the float and presence switches** with shims as Rev I describes, then prove each one. The review found the float switch set only 0.1 mm past its worst-case operating point, with the cam pushing its pin sideways. Set it at least 0.5 mm past, and use a lever-actuated variant if the pin sticks.

**Router mode.** Take the torch out of the clamp (two M4 pinch screws; the collar stays on the barrel) and hang it by its lead. Unbolt the bracket from the Z adapter (four M6 nuts) and lay head and bracket on their back on the three pads on the reservoir lid. Two M5 screws hold them. Fit the spindle. The four M6 × 30 screws, washers and nuts go in the hardware bin.

**Lead.** Strap the torch lead to the head's lead saddle and give it a service loop for the full Z stroke and the 6 mm float. The lead's support above the machine is owner scope.

## Water and coolant

**Router mode now:**

1. Selecting ROUTER opens the pan drain. The plasma water runs back to the reservoir through the new drain screen.
2. Once the pan has been empty for 75 s, the drain **closes** and the router is ready. From then on, coolant and chips that get past the waterproof bed module stay in the pan.
3. If liquid ever reaches the empty float, the router stops and the drain opens again for a new dwell.

**Before plasma (checklist addition):**

1. Vacuum chips and coolant out of the pan.
2. Lift out the drain screen by its tab, empty it and refit it.

Aluminium fines left in the water make hydrogen. Empty the screen after long plasma cuts too.

**Manual drain.** It sits on the reservoir's right wall, at the clarified bay's floor: a 1/2 in half coupling, then a street elbow turned rearward, a full-port ball valve and a garden-hose outlet with cap. Reach it from the right side of the machine, below the frame's side rail.

- Screw on a hose to a floor drain, uncap and open the valve. It empties the clarified bay to 4 mm.
- The settling bay behind its weir holds about 6 L. That empties through the existing washout cover.
- Drain both for freezing weather.

**Suction.** Rev I ran the suction hose up to Z710 and back down to the strainer at Z620, so air collected at the top. Rev K runs its rear leg at Z540 and enters the strainer end zone from below, so the line only rises. Two posts on standoffs from the tank's rear wall carry it. The hose stays 3/8 in; at 7 L/min it runs at about 1.6 m/s, which carries bubbles along. Commissioning test: the pump primes from dry within 30 s and fills at 5 L/min or more. If it fails, change to 1/2 in hose.

**Seals.** The reservoir lid gasket, both hatch gaskets, the washout gasket and the drain-tail gasket are 2 mm nitrile (NBR), because router coolant reaches the water.

## Cabinet

- **Door.** The drip cap's front lip is 8 mm instead of 20 mm. Its lower edge is 2.5 mm above the box top, so a side-hinged door swings under it; before, it hit the lip after about 2.4°.
- **Cable entries.** Two 175 × 150 stainless gland plates cover 145 × 120 floor windows. There are 30 entries for about 28 field cables:
  - power plate: 4 × M25 (mains in, VFD supply, cutter supply, spare) and 6 × M20 (four motors, Z brake, spare);
  - signal plate: 20 × M16.

  EMC glands on the motor, VFD-control, THCAD, head and torch-start cables; nylon glands elsewhere; blanking plugs in the spares. Bond both plates to the PE stud with a 16 mm² braid.
- **Heat.** The Rodent, supplies, relays and contactors inside make about 60 W; the sealed box sheds only about 33 W at a 10 K rise. An IP54 filter fan low on the left wall blows in, and an exhaust filter leaves high on the right. They need about 20 m³/h for a 10 K rise; specify 40 m³/h or more free-blowing. The box becomes IP54. Keep components 45 mm clear of the fan.
- **VFD outside.** The VFD loses 45–110 W on its own. It sits on a 3 mm plate welded to the cage's right upright and stringer, under its own drip roof, with 100 mm of air above and below. The envelope allows 180 × 160 × 250 mm; confirm the owner's unit. Read its keypad from the right side of the machine.

## Hoist in the container

The owner said on 27 September that the machine goes in a container with an **8 ft ceiling**. Inside a standard container that is about 2.39 m. The container's roof and walls can't carry a hoist beam, and the recommended 1.0 m sling height needs about 2.3 m to the beam plus the beam itself: no margin. What fits:

- **A rolling A-frame gantry** over the front of the machine, with its legs outside the machine's sides.
  - Clear span between its legs at least 1.3 m (the machine is 1.15 m wide).
  - Rated 250 kg or more (the module is about 63 kg).
  - Beam underside set to about 2.0–2.1 m.
  - Lock the casters while lifting.
- **A low-headroom hoist:** a chain hoist or mini electric hoist on a trolley, hook no more than 0.35 m below the beam at full lift.
- **The short sling** from the hoist check: the hook 0.7 m above the lug holes, legs about 1.03–1.05 m long at 42–43° from horizontal.
  - Use rigging rated at that angle: each leg then carries about 23 kg.
  - That hook height passed the hoist-path check: 74 sampled poses, 0 contacts.
  - The raised hook sits at about 1.69 m, so the beam underside needs about 2.0 m with the hoist.
  - That clears the Z motor top (1.43 m) by about 0.57 m.

**To lift:**

1. Park the gantry at the rear stop.
2. Roll the A-frame so its hook is over the module's centre of mass (machine Y670).
3. Lift 70 mm.
4. Roll the whole A-frame forward about 1.42 m, guiding the module out through the front window.
5. Lower the module onto its stand.

Put the machine with its front along the container's length. It needs about 1.5 m of floor in front, and a 20 ft container leaves room for the stand and walking space.

**Fumes.** Plasma in a closed container needs an exhaust fan pulling from next to the table, and a fresh-air inlet at the far end. The water table cuts the smoke but does not remove it. Router mist coolant also needs the air moved.

## Changing beds

As [Rev J](../RevJ-CAD/README.md#changing-beds), with the head and water steps added.

**Router to plasma:**

1. SETUP, bed key UNCONFIRMED. Take the spindle out and store it in its cradle.
2. Remove the six M10 drawdowns, lift the module 70 mm and roll it out on the A-frame (Rev J steps 2–6; [hoist in the container](#hoist-in-the-container)). The head goes on after the module is out: the hoist path was checked with the router head, not the plasma torch.
3. Take the head and bracket off the lid pads, bolt the bracket to the Z adapter at its witness line and fit the torch down to its collar.
4. Vacuum the pan and empty the drain screen.
5. MODE PLASMA, bed key PLASMA CHECKED, FILL.

**Plasma to router:**

1. SETUP. Take the torch out of the clamp and park head and bracket on the lid.
2. MODE ROUTER. The pan drains to the reservoir.
3. When the pan is empty, empty the drain screen.
4. Lower the module in and refit the six M10 screws.
5. Fit the spindle and set the bed key to ROUTER CHECKED. The drain closes 75 s after the pan emptied, and the router is ready.

## What was checked

| Check | Result |
|---|---|
| Static interference, router state | 1,220 solids, 0 unresolved overlaps; STEP reimport matches |
| Static interference, plasma state and module alone | 1,074 and 149 solids, 0 unresolved overlaps |
| Nine router poses: the X/Y/Z travel corners and the centre, plasma head parked | **Pass**: 1,220 solids in each, 0 unresolved |
| The same nine poses in plasma: head, bracket and torch on the Z, module out | **Pass**: 1,074 solids in each, 0 unresolved. Torch axis X175–975 and Y73.6–1073.6; tip at Z845 (bottom of Z) and Z945 (top) |
| Torch over slat 8 at the bottom of Z | The tip is **5.0 mm** below the slat top. This is the only contact, and the 6 mm float takes it up |
| Level-sensor band (Y660): X955 at the bottom of Z, and X975 at the top | **Pass**: both clear |
| Hoist path: module and 4-leg sling, hook 0.7, 1.0 and 2.0 m above the lugs | **Pass**: 74 sampled poses each, 0 intersections. The nearest gaps are Rev J's: frame legs 11.2 mm, float backrails 14.5 mm, Y-block bolts 18.8 mm. At the 2.0 m rise, one rear leg passes 8.6 mm from the rear-parked X rail |
| Water fixes | Refill air gap 32 mm (31.6 needed). Drain screen clear of the neck: its flange rests 0.31 mm above the neck. Manual drain hole 3.95 mm above the tank floor. The suction line only rises, and its highest point is its end at the strainer (Z628) |
| Cabinet | 30 cable entries (24 needed); drip lip 2.5 mm above the box top |
| Sources | Every record is hash-bound to its sources, and no source changed during the runs |

These are nominal CAD checks. They do not cover rigidity, the torch's true nose diameters, cable and hose routing, or weld distortion.

## Still open

- **Torch:** the owner does not yet know which torch they will use (27 Sep) and will measure it. Measure the barrel before boring the insert; if the barrel is not 28 mm, the insert bore and the collar change, and the bracket slots cover a clamp 90–140 mm above the tip. The PT31 torch's nose diameters, lead and connector fit to the CUT-50 are not verified.
- **Head:**
  - release force and float trip;
  - the tether;
  - the float switch margin (set at commissioning, see above);
  - the magnet preload offset noted by the review;
  - thermal limits near the arc.
- **Plumbing:** the pump's port positions, strainer ports and all hose-end fittings are receipt-fit. The review's note that Rev I clamps the strainer through its bowl threads is not addressed: support it by its body when fitting.
- **Cabinet:** the fan, glands and VFD are chosen by function. Measure the temperature rise at full load. The enclosure's hinge, latch and cut-outs need the received box.
- **Controls:** the GM1 circuit is simulated only; see its README for what the owner still needs to send.
- **Rev J's own open items:**
  - selecting the A-frame and hoist for the container (see above);
  - the module stand;
  - galvanizing distortion;
  - pad coplanarity.
- **Not part of this line:** the ATC variants still assume the Kraken's spare drivers.

## Sources

In [RevK-ENGINEERING](../RevK-ENGINEERING/), kept apart so the shared RevE-ENGINEERING source inventory is unchanged:

- `build_revk.py`: builds the model and exports it; Rev J's `build_revj.py` is used unchanged.
- `revk_water.py`: spout, drain screen, manual drain and NBR seals.
- `revk_service.py`: Rev I drain and strainer, the pressure hose lowered 20 mm, and the suction reroute.
- `revk_cabinet.py`: the cabinet changes.
- `plasma_drop.py`: bracket, torch and parking.
- `verify_revk.py`: poses, hoist path and water checks.
- `render_revk.py`: previews.

The GM1 controls changes are in [../../controls-2026-09-27](../../controls-2026-09-27/README.md).
