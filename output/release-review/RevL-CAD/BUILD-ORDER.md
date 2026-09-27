# GM1 Rev L — what to build while the parts arrive

**Owner, 27 September 2026:**

- The plasma cutter (CUT-50) and the torch are in hand.
- All the drive modules are ordered, the Z slide with a 300 mm stroke.
- The only parts still to wait for are the extra rails and the bed extrusion.

The extra rails are the [HGR20 guide kits](../../receiving/HGR20-RAIL-KITS.md). The bed extrusion is the nine 20100 deck profiles.

This page sorts the [Rev L](README.md) work by what each step waits for, so the build can start now. It follows the part operations of [Rev K](../RevK-CAD/part-operations.json) and [Rev L](part-operations.json). Every part is still marked "review before fabrication": the design is checked in CAD, not signed off. Check each part against its drawing ([Rev K DXFs](../RevK-CAD/dxf/) and [STEP parts](../RevK-CAD/parts/), and Rev L's [DXFs](dxf/) and [parts](parts/)).

| Work | Waits for |
|---|---|
| The torch and cutter checks, the frame and its fill holes, the water pan and reservoir, the cabinet frame, the plasma head and bracket, the gantry's aluminum parts, and welding the bed module | Nothing: start now |
| The Z carrier's and Z adapter's holes to the slide; the HMS40 base fixings | The drive modules (ordered) |
| The rail holes in the Y datum bars and the X guide face, so the whole gantry | **The HGR20 rails. No motion without them** |
| The router bed (strips and HDPE top) and the tool changer | **The bed extrusion. Plasma does not need it**: it runs with the module out |
| Any powered motion | The controls, not yet recorded as bought (see the end of this page) |

## 1. Now

### The torch

The design took the seller's figures (270 mm long, 28 mm barrel) and a photo. With the torch in hand, measure it before the insert is bored ([Rev K: head, bracket and torch](../RevK-CAD/README.md)):

1. **Barrel:** its diameter with calipers, round within 0.10 mm over a straight 40 mm length. Bore the split insert to the measured diameter + 0.10 (drawn 28.10 for 28). The clamp collar is sized from the same measurement.
2. **Clamp height:** the clamp's lower face sits 115 mm above the nozzle tip, on the straight barrel. The drawing assumes the straight barrel starts about 105 mm above the tip. The bracket slots take a clamp from 90 to 140 mm above the tip. If the straight barrel can't take the clamp in that range, send the measurements: the bracket changes.
3. **Lead:** its outside diameter and how tightly it bends, for the lead saddle. It needs a service loop for the full 300 mm Z stroke plus the 6 mm float.

### The CUT-50

- Plug the torch in and confirm it fits the cutter: connector and air. That fit was not verified.
- Find the torch-trigger circuit's voltage and current from the manual or the maker. The relay that closes it (K_TS, in its box at the cutter) is chosen to suit them. Don't probe it live.
- Note the work-lead size: it sizes the arc-OK current sensor ([controls buying notes](../../controls-2026-09-27/README.md)).

### Steel and aluminum that wait for nothing

- **Frame.** The 2 × 2 tube list is Rev J's: 32 blanks, from the scrapyard or new ([tube cutting plan](../RevJ-CAD/TUBE-CUT-PLAN.md)). Cut, fixture and weld it, with the feet.
  - Weld the six M10 sleeves through both walls of the ledgers, sealed. Tap them M10 at least 25 mm deep after welding.
  - Weld the six seat pads, face them coplanar within 0.1 mm (fly-cut or shim-map), then drill them through into the sleeves.
  - Drill the 18 fill holes (Ø30, one per tube) where the Rev L drawings put them: at each tube's high end ([section 6](#6-filling-the-frame)).
  - **Fill the frame last**, after all welding, coating and drilling ([section 6](#6-filling-the-frame)).
- **Y datum bars.** Weld them to the upper chassis, then finish-machine the rail seats: flat within 0.05 mm per metre and parallel within 0.05 mm over the travel. Leave the rail holes: they are transfer-drilled from the rails.
- **Bed module weldment:** side rails, crossmembers, end plates, compression sleeves, caps and the four lift lugs. Weld it now. **Hold the strip-screw holes and the galvanizing until the first 20100 bar is in hand.** The holes are nine Ø5.5 in each crossmember top, with Ø14 access holes below. Check the bar's bottom slot on that hole line and a square nut's fit, then drill, then galvanize.
- **Water pan and reservoir**, pan bearers and cradles, float guards, overflow catch, hatches, drain parts, refill spout and gusset. Grind the cradle webs to the measured floor slope. Drill the holes for bought parts (pump feet, float nuts) from the parts themselves.
- **Cabinet frame.** Build it now. Each rail's two bolt holes are transfer-drilled from the enclosure's back panel once it is bought.
- **Plasma head** (Rev I's floating head) and the **135 mm drop bracket** (1/2 in 6061). Bore the insert after the torch is measured (above). Set the switch trips at commissioning.
- **Gantry aluminum parts:** Y shoes, gantry end brackets, X guide face, Z carrier, link supports, clevis billets, HMS40 drive shoes. Two sets of holes wait:
  - the X guide face's rail holes, transfer-drilled from the X rails;
  - the Z carrier's holes for the Z slide, measured from the slide.

  Mill the X guide face's two rail seats coplanar within 0.03 mm. The Y shoes and the Z carrier take the HGH20CA blocks on the standard 32 × 36 mm M5 pattern; check it against the delivered blocks. The X guide face bolts to the 80/20 40-8080 beam with M8 T-nuts, so the beam is needed too.
- **Tool park, bolt tray and the head's parking pads** on the reservoir lid.
- **Tool changer steel parts** (Rev L): cut the beams, seat bars, carrier, upstands, stops, brackets, motor plate and feet. They are welded on the finished module (section 4).

## 2. When the drive modules arrive

- Measure each one as [MOTION-MODULES.md](../../receiving/MOTION-MODULES.md) lists, and write the values in its register. On the ZBX80, two numbers matter most:
  - **the height from its base to its carriage top.** The model assumes 80 mm; the listing drawing does not dimension it but scales to about 62 mm. If it is not 80, the tool axis moves (further back if it is lower) and the pose checks are re-run.
  - **the 300 mm body length.** 419 mm on the listing drawing for the 300 mm stroke, as modeled.
- Do the Z back-drive test: stand it vertical, unpowered, with a weight on the carriage.
- Then drill the Z carrier and the Z tool adapter blank from the measured slide, and the HMS40 base fixings from the measured slot nuts.
- The braked Z motor is bought only after the ZBX80 is measured.

## 3. When the HGR20 rails arrive

This gates the gantry and every powered move.

1. Receive and measure them as [HGR20-RAIL-KITS.md](../../receiving/HGR20-RAIL-KITS.md) lists. Run `plan_rail_cuts.py`, then cut the Y rails to 1,420 mm.
2. Transfer-drill the rail holes in the Y datum bars (tapped M5) and the X guide face from the actual rails.
3. Fill the frame once all drilling is done ([section 6](#6-filling-the-frame)).
4. Assemble the gantry:
   - rails and blocks;
   - Y shoes and end brackets;
   - the 80/20 beam and X guide face;
   - the Z carrier with the Z slide;
   - the HMS40 drives with their thrust links.

## 4. When the bed extrusion arrives

This gates the router bed and the tool changer only.

1. Cut the nine profiles from 1,220 to 1,197 mm: one saw cut each, no drilling. The tenth bar is spare.
2. Test a sample strip joint before setting a torque.
3. If the module's holes and galvanizing were held, do them now. Then fit the strips: 36 M5 screws, from inside the crossmembers into bottom-slot nuts.
4. Fit the two HDPE plates: twelve counterbored M5 screws into top-slot nuts, one fixed hole per plate.
5. Proof-load the module lift at twice its mass before its first hoist. Set it on its pins with the six M10 drawdowns (anti-seize, 30 N·m nominal).
6. Surface the HDPE in the machine once it runs.
7. **Tool changer:**
   - weld the dock to its feet on the module;
   - machine the rail seats flat with the module level;
   - fit the MGN12 rails (cut to 281 mm, first hole 10 mm from the front end), carrier and drive;
   - fit the front stop after welding, then probe the pocket reference.

   The magazine saddles are drilled from the RapidChange kit once it is chosen and delivered.

## 5. Plasma can come before the router bed

Plasma runs with the bed module out: the torch cuts on the slats over the water pan. So the first plasma cut needs:

- the frame;
- the pan, slats and water system;
- the gantry, so the rails and all the modules;
- the head and torch;
- the controls.

It does not need the bed extrusion. The router needs the module, and the tool changer needs the module and the RapidChange kit.

## 6. Filling the frame

Each of the 18 frame tubes is its own sealed compartment with one fill hole. Nothing connects the tubes, so each is filled on its own. Rev K's holes were placed for access. Even a runny mix would only fill the top rails and the front cross tubes about a quarter full and the legs about three-quarters. **Rev L moves each hole to its tube's high end** ([ballast_revl.py](../RevL-ENGINEERING/ballast_revl.py)):

| Tubes | Hole |
|---|---|
| 6 legs | 35 mm below the top (Z965). Outer face on the two front legs, rear face on the other four |
| 2 top rails | In the rear end cap. That cap gets its own part number, SAND_ENDCAP_2IN_PORTED |
| 4 lower side tubes | On top, 40 mm from the rear end |
| 2 bed ledgers | On top at Y1370, as before |
| 4 cross tubes | At the right-hand end: on top of three, on the front face of the front lower tube, which is covered on top |

**Drilling:** every hole is round, Ø30 through the 3 mm wall.
- Use a step bit that reaches 30 mm: a 4–32 mm bit, or a 1/4–1-3/8 in bit stopped at its 1-3/16 in (30.2 mm) step.
- Centre-punch the spot, run the bit slow with cutting oil, and it goes through in one pass.
- If your bit tops out at 1-1/8 in (28.6 mm), finish with a 30 mm hole saw.

**Epoxy sand** (the owner is considering it):
- **Before you fill:**
  - Do all welding, drilling (including the Y rail holes) and painting first.
  - Never weld on the frame afterwards: the heat burns the epoxy and gives off toxic fumes. The fill is permanent.
- **Mix:** a pourable mix of dry, fine sand and a slow, low-viscosity epoxy. The tubes hold about 36 L. Expect roughly 12–15 L of epoxy and about 70 kg of fill.
- **Pouring:** pour in lifts, and vibrate each tube as it fills (a sander held against it works).
- **Stage 1:** raise the rear of the frame about 15° (rear feet about 375 mm up). Pour the 6 legs, the 2 top rails, the 4 lower side tubes and the 2 ledgers. Every hole is then at its tube's high end.
- **Stage 2:** once stage 1 has cured, raise the right side about 15° (about 300 mm). Pour the 4 cross tubes.
- **Result:** the model's estimate for these two stages is over 93 % of every tube. The small pocket above each hole's lower edge stays empty.
- **Plugs:** the threaded plugs are not needed. Pour through the plain 30 mm hole, which is easier than the plug fitting's 18.5 mm bore, and push a plastic hole plug in once it cures.

**Dry sand:**
- It does not run along a tube at 15°, so stand each tube near vertical:
  - the legs with the frame upright;
  - the front-to-back tubes with the frame on its front end;
  - the cross tubes with the frame on its left side.
- Vibrate the tube and top it up, then fit the M20 plug. The estimate is over 91 % of every tube.
- Dry sand can be emptied again through the plugs.

Either way, weigh the frame before and after. The design counts the fill as mass and damping, not strength.

## Not recorded as bought yet

These are in the [cost register](../../../outputs/reve-30510/actual-cost/REAL-COST.md), the [Rev K delta](../../../outputs/reve-30510/actual-cost/REVK-PROCUREMENT-DELTA.md), the [Rev L delta](../../../outputs/reve-30510/actual-cost/REVL-PROCUREMENT-DELTA.md) and the [controls README](../../controls-2026-09-27/README.md). Skip anything already bought.

- **Controls:**
  - the BTT Rodent V1.1;
  - the GM1 relay, safety and power parts;
  - the cabinet enclosure: a **steel** box at least 500 × 400 × 200 mm, like the VEVOR 20 × 16 × 8 in in the register (E05). The panel layout needs about 330 × 430 mm, and the floor takes two 175 × 150 mm gland plates. A plastic box does not shield the Rodent from the plasma's high-frequency start.

  Nothing moves under power without them.
- **Spindle kit** with its VFD (1.5 kW, 110 V, ER11, Ø65 body). Machine the spindle clamp's bore against the actual spindle.
- **Gantry beam:** 80/20 40-8080, 1,200 mm, and 16 M8 T-nuts. They were priced in an 8020.net cart ($272.11 with freight and tax), not ordered.
- **Water parts:** pump, floats, valves, hoses and fittings.
- **Materials and hardware:** HDPE sheet, fasteners, and the extra plate and stainless the deltas list.
- **Tool changer:** the RapidChange kit and the dock's bought parts.
- **The braked Z motor**, after the ZBX80 is measured.
- **Frame fill:** epoxy and fine dry sand, or dry sand alone ([section 6](#6-filling-the-frame)). If you pour epoxy without the threaded plugs, add 18 push-in hole plugs for 30 mm (1-3/16 in) holes.
