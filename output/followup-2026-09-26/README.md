# GM1 follow-up after Rev G — 26 September 2026

**Still not released for fabrication or operation.** This page records the work done on top of the Rev G repair (`a61d634`), what it found, and what is still needed to finish the machine. The machine is now named **GM1 — Garcia Mechanical Table** (owner, 26 September 2026). The current design on this branch is [Rev L](../release-review/RevL-CAD/README.md) (27 September): [Rev K](../release-review/RevK-CAD/README.md) with a 300 mm Z and the owner's RapidChange tool changer on the bed module. Rev K is [Rev J](../release-review/RevJ-CAD/README.md)'s one-piece bed, completed with the other session's Rev I head, plumbing and cabinet and with the review's fixes. Rev J was first published on this branch as "Rev H" and renamed on the evening of 26 September (see below). Rev G is described in its [CAD package](../release-review/RevG-CAD/README.md) and the [repair report](../cad-repair-2026-09-25/README.md).

## What changed in this follow-up

- **The Z body raised over the tool changer (Rev L, 27 September, evening).** Looking at the Rev L picture, the owner said "when it retracts, or it moves forward it will hit the autochanger", and "it has the lid on the autochanger too". They were right: the Z body's lower end sat 90 mm below the magazine top, so the changer could only move with the head parked at X975 first, and a wrong move would have driven the Z body into the magazine. Now:
  - the ZBX80 sits 110 mm higher on the Z carrier, on a 220 mm tall drop adapter whose lower 110 mm is the Rev K adapter, so the spindle, the plasma head and the tool axis are unchanged;
  - the Z body's lower end (Z1150) is level with the gantry's X blocks and carrier (Z1143), and a 12 mm lid allocation sits on the magazine; the magazine is lowered 10 mm so the closed lid passes 10.65 mm under the gantry when parked (the stock allowance under the deployed dock becomes 40 mm);
  - the checks now run the dock with the head at X175, X575 and X975, and drive the gantry over the deployed magazine: all clear;
  - the one rule left is "Z up before the dock moves", and controls **M14** enforces it in hardware through a second contact of the Z top switch.
  - **On the 300 mm stroke:** with the body raised, a 200 mm Z would put the spindle nose only 15 mm above the lid at full up, where RapidChange asks for 90; the 300 gives 128.
- **Frame fill holes moved (Rev L, 27 September).** The owner asked "are all my holes aligned so the sand fills the rails?" and is thinking of epoxy sand.
  - Each of the 18 frame tubes is its own sealed compartment with one fill hole; nothing connects them. Rev K's holes were placed for access. Even a runny mix would fill the top rails and front cross tubes only about a quarter full, and the legs about three-quarters.
  - Rev L moves each hole to its tube's high end (`ballast_revl.py`). By the model's estimate, epoxy sand fills every tube over 93 % in two pours with the frame tilted 15°. Dry sand fills over 91 % with each tube stood near vertical.
  - The holes are Ø30, drilled with a step bit.
  - The rebuilt Rev L package and all its checks pass with the new holes. The procedure is in the [build order](../release-review/RevL-CAD/BUILD-ORDER.md#6-filling-the-frame).
  - **Enclosure:** the owner looked at a plastic box of about 460 × 320 × 160 mm. It is too small for the panel and the gland plates, and it does not shield. The design needs a steel box of at least 500 × 400 × 200 mm, like the VEVOR 20 × 16 × 8 in in the register.
- **Parts on the way (owner, 27 September).** The plasma cutter and the torch are in hand. All the drive modules are ordered, the Z slide with a 300 mm stroke. The only parts still to wait for are the extra rails (the HGR20 guide kits) and the bed extrusion. [BUILD-ORDER.md](../release-review/RevL-CAD/BUILD-ORDER.md) sorts the build by what each step waits for:
  - the frame, water pan, cabinet frame, plasma head and gantry parts can start now;
  - the rails gate the gantry and every powered move;
  - the extrusion gates only the router bed and the tool changer, so plasma can come first.

  The receiving records and the cost register's order status are updated.
- **Rev L, the owner's tool changer (27 September):** [package](../release-review/RevL-CAD/README.md).
  - **300 mm Z** (ordered, 27 September). The lowest spindle reach is unchanged; the nut rises to Z1260, 128 mm above the magazine's lid, where RapidChange asks for 90 mm. Later that day the body was raised 110 mm over the changer (above).
  - **The dock rides on the bed module**, so it lifts out with the bed for plasma and nothing extra comes off the machine. Two MGN12 rails on the T-slot strips, a U-shaped carrier, 200 mm of travel, a worm gearmotor and belt, a fitted front stop and two sensors. The magazine is the other session's 520 × 60 × 80 mm allocation at Z1050.35.
  - **Tool-change rule:** first drawn with the Z slide's lower end below the magazine top, so the head had to park at X975 while the dock moved. Superseded the same evening by the raise (above): now only "Z up before the dock moves".
  - **Bed changes:** deploy the dock and unplug it before the lift; the hook goes over Y745 (the module is now about 74 kg) and the roll is 1.52 m.
  - **Controls M12–M13:** spindle reverse through a force-guided direction relay, and the dock drive, interlocked with the spindle-run relay and the E-stop. 1,424 simulated checks pass with M14's Z-top dock enable (1,386 before it, 1,173 before M12); the Rodent pin plan passes 25 checks.
  - **Checks:** router and plasma poses at Z 0 and 300, the dock's travel, tool-change poses, the forbidden front approach (clashes, as expected), a 50 mm stock allowance under the deployed dock, and the hoist path with the dock on the module at three hook heights. All pass.
  - **Shopping list:** [REVL-PROCUREMENT-DELTA.md](../../outputs/reve-30510/actual-cost/REVL-PROCUREMENT-DELTA.md), unpriced.
- **Rev K, after the owner's "finish it" (27 September):** [package](../release-review/RevK-CAD/README.md). The one-piece line is chosen as the one to complete, because it is the bed the owner asked for in this session; the owner can still pick Rev I instead.
  - **Folded in from Rev I:** its floating/breakaway plasma head, drain valve and tail, strainer carrier, hoses and cabinet.
  - **Plasma reach fixed:** a 135 mm drop bracket sized for the owner's torch. The owner sent a photo of a PT31-style straight machine torch, 270 mm long with a 28 mm barrel. The tip reaches Z845 at the bottom of Z, 5 mm below the slats. Near the pan level sensors, plasma paths stay at X955 or less.
  - **Water fixed:**
    - a drain screen;
    - a manual reservoir drain;
    - NBR seals;
    - a suction line without a high point;
    - a 32 mm refill air gap.
  - **Controls (M9–M11):** the router-mode drain closes after its dwell, a fill watchdog, and a float trip that stops a cut. 1,173 simulated checks pass.
  - **Cabinet fixed:** a shorter drip lip so the door opens, 30 bonded gland entries, a filter fan, the VFD outside, and the torch-start relay moved to the cutter.
  - **Checks:** all pass. Static: 1,220, 1,074 and 149 solids, 0 unresolved. 9 router poses and 12 plasma poses; the torch tip reaches 5 mm below a slat top, within the float travel. The hoist path at three hook heights, and the water and cabinet checks.
  - **Shopping list:** [REVK-PROCUREMENT-DELTA.md](../../outputs/reve-30510/actual-cost/REVK-PROCUREMENT-DELTA.md). All Rev K additions are unpriced.
  - **Owner question, 27 September:** can it cut steel with a 6 mm end mill at 12k rpm and 0.005 in passes? Answered in the session: yes, as light-duty work. The cut needs about 40 W and 10–20 N. Use a 3–4 flute coated carbide at about 0.02 mm per tooth, short stick-out and chip clearing. The frame's side stiffness is not yet calculated.
- **GM1 controls for either bed line (27 September, while the owner's answers were pending):** [package](../controls-2026-09-27/README.md). It builds on Rev I's relay circuit, imported unchanged, and keeps its water logic.
  - **E-stop:** a dual-channel safety relay drives two contactors. They remove the Rodent's 48 V, VFD mains and plasma mains, and the Z brake engages.
  - **Mode race fixed:** per-mode ready relays sit in each tool coil.
  - **Welded relays:** the start chain is force-guided with monitored pickups, plus a second request relay and a second SETUP contact.
  - **No RS485:** the VFD runs only through its FWD terminal.
  - **Rodent pin plan:** the board has six isolated inputs plus two 3.3 V header pins once RS485 is dropped, enough for the eight real-time signals, so no I/O board is needed for them. A draft grblHAL board map is included.
  - **Status:** simulated, not built, wired or flashed. Blocker 4 (plasma reach) and the cabinet and water findings stay open.
- **Base branch merged a fourth time: retractable ATC (`dfdf5da`, 00:54 UTC on 27 September).**
  - **What arrived:** the other session added [retractable ATC mechanisms](../../variants/retractable-atc/README.md) for both machine variants: a 200 mm slide, automatic pin release, a longer Z for the small machine and a side bay for the 4x8. It comes with CAD and a controls model.
  - **How it merged:** only `README.md` conflicted; it now lists the new work. The files were merged unchanged and not reviewed in depth.
  - **Controller conflict:** the slide and shutter run on the Kraken's spare drivers S5 and S6. The Rodent's four drivers are all used by X, Y, Y2 and Z, and grblHAL's Rodent map has no fifth motor. On the owner's Rodent these mechanisms would therefore need a different drive arrangement.
- **Review of the other session's work** (owner request, 26 Sep evening): [review](../review-2026-09-26/README.md).
  - **Its checks reproduce:** Rev I acceptance 30/30 and a fresh rebuild with 0 clashes.
  - **Blockers:** Kraken-based controls against the Rodent decision, on a Rodent that has only 5 inputs (corrected on 27 September: 6, since grblHAL's map leaves E1-MAX unused) and no THC support on ESP32; no E-stop or power-removal circuit; a mode-switch race that can fire the wrong tool, verified on its own simulator; and a plasma torch that must project about 215–245 mm to reach the slats, which affects Rev J too.
- **Base branch merged a third time: development variants (`ca9728b`, 22:15 UTC).**
  - **What arrived:** the other session added a small-machine RapidChange ATC dock, a full-sheet 4x8 machine layout and shared removable-table locators, in `variants/`. They were merged unchanged.
  - **Conflicting records:** the variants' [requirements record](../../variants/requirements.json) lists "Keep bed conversion within the machine footprint" and "Preserve the preference for Kraken onboard motor drivers" as confirmed requests. This session recorded the one-piece bed that leaves through the front on a hoist, and the BTT Rodent. These records conflict, and only the owner can settle them.
  - **Controller settled:** the owner reconfirmed the BTT Rodent that evening ("we're going to use the Rodent, not the Kraken"). Rev I's Kraken circuits, its isolated head inputs and the variants' ATC pin reservation need porting to the Rodent.
  - **If the other session's bed record stands:** Rev J's hoisted bed is not what the owner wants. This branch would then keep only its receiving checks, rail-length explanation and cost-register work.
- **Base branch merged again: the other session's Rev I (`4a67463`, 21:15 UTC).**
  - **What Rev I is:** the next step of the six-panel line. It adds a guided floating/breakaway plasma head (insert unbored until the torch is measured), 14 mm storage rods, bed-joint calculations, drain, strainer and hose supports, a corrected cabinet, and Kraken V1.1 terminal circuits with isolated head inputs.
  - **How it merged:** only `README.md` conflicted. It now presents Rev J and Rev I side by side, without choosing between them.
  - **Not in Rev J:** Rev I's head, plumbing, cabinet, structure and control work. Rev I's controls follow the Kraken, while the owner chose the Rodent in this session.
  - **Next:** folding Rev I's non-bed work into the one-piece bed would be another integration, so it waits for the owner's choice of line.
- **Base branch merged: two different "Rev H" designs (evening of 26 September).**
  - **What arrived:** the owner's other session pushed its own Rev H to the base branch (`9e3dd66`). It keeps the six-panel bed stored in the frame, adding storage restraints, and adds reservoir service hatches, a washout flange, a refill spout, drain reserves, a Z-adapter transfer blank and a braked Z-motor candidate. Its [completion report](../design-completion-2026-09-26/README.md) records that the one-piece question "has no answer" in that session.
  - **The rename:** this branch's one-piece bed answers the owner's requirement given here, so it stays the current design. It was renamed **Rev J** because the base's Rev H uses the same folder names. The letter I was skipped, but the other session used Rev I later that night; see the next item. The base's Rev H files are unchanged, and that design stays documented as the six-panel alternative.
  - **What Rev J takes from the base's Rev H:** its water-service and Z-adapter work, unchanged except for the refill spout. The spout's riser stood under the module's rear crossmember, so `water_revj.py` moves it from Y1255 to Y1215.4 (between slats 18 and 19) and turns its head along −X. It keeps the 30 mm air gap, and a floor gusset replaces its stay. The module's end crossmembers and deck move 15 mm rearward, which leaves 21 mm between the spout and the module.
  - **Checks on the combined model, all pass:** static (978/829/149 solids, 0 unresolved overlaps), nine motion poses, the hoist path at three hook heights, and the water-service paths (both hatch covers and the washout cover). One gap got tighter: with the steepest sling checked (hook 2.0 m above the lug holes), one rear leg passes 8.6 mm from the rear-parked X rail. The recommended 1.0 m hook rise keeps every leg more than 40 mm clear.
- **Rev J bed, to the owner's requirement.** One waterproof bed module of about 63 kg: a galvanized 2 × 2 steel frame, nine 1,197 mm T-slot profiles from the same five two-packs, and two HDPE plates surfaced in place, with no MDF. Six M10 screws hold it and two pins locate it. For plasma work it lifts 70 mm in place and leaves through the front window on the owner's overhead beam-and-trolley hoist.
  - **Checks:** static interference (0 unresolved overlaps in the router, bed-out and module-only states), nine motion poses (pass) and the hoist path with the 4-leg sling modeled at hook heights 0.7, 1.0 and 2.0 m (pass, 0 intersections; nearest gap 11.2 mm to the frame legs).
  - **Removed:** Rev G's racks, trays and slat end reliefs.
  - Details are in the [Rev J package](../release-review/RevJ-CAD/README.md); the shopping-list changes are in [REVJ-PROCUREMENT-DELTA.md](../../outputs/reve-30510/actual-cost/REVJ-PROCUREMENT-DELTA.md).
- **Cost register re-baselined to Rev J.** Priced scope is now **$5,336.10** ($5,249.85 goods + $86.25 known shipping, including the $82 price the owner reported for the 1,200 mm rail kit), 73 priced lines and 51 unpriced entries. The Rev G bed rows (MDF, ties, rack stock, N3, N5) are superseded, N1 is 48 stainless nuts, and the Rev J HDPE, stainless, lug bar, 8 ft tube and galvanizing rows are unpriced, as are the Rev H water-service items: 4 mm washout plate (MET-GAP-24), NPS 1/2 refill pipe (MET-GAP-25), and hatch and washout fasteners (HW-GAP-H03). The three new gaskets come out of the existing EPDM sheet. The SteelMart request lists Rev J stock.
- **Drive modules: all ordered.** The owner reported ordering the "rail kits" on 26 September 2026, clarified them as 1000 × 800 × 100, and said the HMS40 spec sheet and ZBX80 drawings shared that day "are ordered": the two HMS40 1000 mm Y drives (M02), the HMS40 800 mm X drive (M01) and the ZBX80 Z slide (M03). The owner's other session recorded the same day that the Y modules were ordered and X and Z would follow. On 27 September the owner confirmed all the modules ordered, the Z with a 300 mm stroke. The [drive-module receiving check](../receiving/MOTION-MODULES.md) lists what to measure on arrival, which closes the drive-interface holds. The ZBX80 listing's side view scales to about 60–67 mm from base to carriage top, where the model assumes 80 mm; that one measurement moves the whole tool 13–20 mm in Y.
- **HGR20 guide rails: kept; still to come** (27 September: with the bed extrusion, the only parts the owner is waiting on). The owner decided on 26 September to keep them ($110 for the 1,500 mm kit and $82 for the 1,200 mm kit, owner-reported). The design's separate HGR20 guides (M04, M05) carry the gantry and cutting loads; the HMS40 modules, whose 1000 × 800 × 100 strokes are the machine travel, only push. Their [receiving check](../receiving/HGR20-RAIL-KITS.md) and `plan_rail_cuts.py` are ready. The Y-rail cut cannot be fixed before measuring: plausible hole patterns give 10/70, 40/40 or 73/7 mm off the two ends, and 40/40 would split a counterbore on one of them.
- **Controller chosen: BTT Rodent with grblHAL** (owner, 26 September 2026). This closes CW-01. The Kraken purchase, CB1 and Pi4B host boards and host USB cable left the priced register; the owner already owns a Kraken, now kept as the fallback. The Rodent board is listed as unpriced scope, and the external THC box is no longer planned.
- **Cost register reconciled with Rev G and the controller choice** (before the Rev J re-baseline above). Priced scope was **$5,348.40** ($5,262.15 goods + $86.25 known shipping; it was $5,810.24 on Rev E quantities), with **49 unpriced entries**. This is not a cheaper build; new Rev G items remain unpriced. Details are in [REAL-COST.md](../../outputs/reve-30510/actual-cost/REAL-COST.md). The Excel workbook could not be rebuilt here (`build_budget.mjs` needs the private `@oai/artifact-tool` runtime), so it still shows Rev E quantities.
- **Stock-fit check.** `outputs/reve-30510/actual-cost/check_revg_stock_fit.py` packs every Rev G flat part onto the sheet and plate sizes in the register, including flat parts that have no DXF, using the project's own packer.
- **Legacy generators.** The Rev B/C and Rev F brief generators no longer write to `output/pdf/plasma-router-stand-concept.pdf`. The base branch has since replaced that PDF with its six-panel Rev H review copy; there is no Rev J concept PDF yet.
- **Wording.** The water sequence now names the Rev J drawdowns and hoist, with the Rev G parts as the alternative, and the cutter is the owner-reported VIV ARC CUT-50 rather than "unknown".

An earlier version of pull request #1 carried fixes for the Rev F hoisted bed. Rev G replaced that design, so those changes were dropped rather than merged. Their 397 mm cut instructions and hoist wording would now be wrong.

## Procurement findings on Rev G

| ID | Finding | Status |
|---|---|---|
| RG-P1 | The two 6 mm TOOL_PARK_CRADLE plates do not fit on the single 24 × 48 in 1/4 plate (MET13) with the other 89 six-mm parts. | Added a 1/4 × 12 × 12 in piece (or buy the plate as 24 × 60 in). |
| RG-P2 | No register row covered 2 mm steel (28 rack guides), 3/8 in aluminum (24 panel ties), round bar for 12 compression sleeves, or 30 × 30 × 3 mm tube (2 rack forks). | Added as unpriced scope with sizes that fit. |
| RG-P3 | `RevG-CAD/nesting/sheet-nesting.json` only nests parts with a DXF, so it omits the two tool cradles, 15 stainless float-guard pieces, the vent cap and the small bosses and spacers. | The stock-fit check includes them. The Rev G nesting still under-counts. |
| RG-P4 | The eight 18 mm hollow beam feet (G_BEAM_FOOT_18) had no stock allocation. `bed_cassettes.py` models each as an 18 mm slice of 2 × 2 × .120 tube with one face trimmed to 50 mm. | Allocated to the 825.6 mm left on tube bar 5 (168 mm needed with cuts). |
| RG-P5 | The rack forks use metric 30 × 30 × 3 mm tube, uncommon in the US; 1-1/4 × 1/8 in changes the fork. | Open: CAD check before substituting. |
| RG-P6 | The priced DIN 7349 washer (W1) is 2 mm thick; Rev G models 1.5 mm under each M5 × 16 tie screw, and the thicker washer shortens thread engagement. | W1 not adopted; 72 washers unpriced. |
| RG-P7 | The rail-screw quantity (M5 × 16, one per kept hole) depends on the measured pitch: about 88 at P 60 or 130 at P 40. | Order after the rails are measured. |
| RG-P8 | With the Rev E hardware removed, the Nutty order ($90.37) falls below its $100 free-shipping threshold, adding $10.95. | Adding the unpriced Rev G fasteners to that order may remove it. |

## Controls findings still open

The controller files did not change in Rev G. These points, found while re-checking the control documents on 25 September, still stand:

| ID | Finding |
|---|---|
| CW-01 | **Resolved 26 Sep 2026: Rodent.** Every wiring document and the compiled image still describe the Kraken, so the Rodent board map, pin allocation, THCAD counter support and RS485 VFD link are now the controls work. |
| CW-02 | No cutter-facing start or arc-sensing interface is defined for the VIV ARC CUT-50. |
| CW-09 | All four normally-open contacts on the mode selector are used by the water circuit; none is allocated to route the tool-run request (PG2) only to the selected tool. |
| CW-10 | No input tells the controller which physical mode is selected, so a firmware/selector mismatch is caught only by procedure. |
| CW-11 | The combined PG6 permissive (bed, water, breakaway, door) has no series drawing, and its polarity and fail-safe behavior depend on an unspecified isolator stage. |
| CW-12 | The E-stop, STOP_OK and PG4 contact budget is unreconciled, and the RESET button has no firmware input because that pin is the E-stop. |
| CW-13 | Part numbers disagree between documents: flyback diode MBR20100CTG versus STPS20100CT, and 1 A fuse 0287001.L versus 0287001.U. |

**Status, 27 September.** The [GM1 controls](../controls-2026-09-27/README.md) address these in design, simulated only:

- **CW-09:** each tool coil path runs through its own mode's relay pole and its own mode's ready relay.
- **CW-10, in part:** polled MCP23017 status shows which mode's water sequence is ready.
- **CW-11:** a drawn, terminal-numbered permission chain, with its polarity defined at the Rodent's E1-MAX door input.
- **CW-12:** the safety relay's contacts are allocated. The Rodent needs no E-stop input because the stop removes its power, and RESET belongs to the safety relay.

For CW-01, the board map and pin allocation are drafted and the RS485 link is dropped. What remains is the ESP32 THCAD driver and adding the plasma plugin to the ESP32 build. CW-02 and CW-13 stay open.

## What is needed to finish

**Owner answers received on 27 September 2026:**

- **Bed line: the one-piece bed** ("the one piece"). Rev K is the current design, and Rev I stays as the alternative.
- **Torch:** not yet known ("idk yet"). The owner will measure it. Later that day the torch is in hand: measure it before the insert is bored ([build order](../release-review/RevL-CAD/BUILD-ORDER.md)). Rev K is drawn for the PT31-style torch in the photo, and the bracket slots cover a clamp 90–140 mm above the tip.
- **CUT-50 start:** the torch trigger, and it starts in mid-air, so it is an HF start. The K_TS relay's contact goes across the trigger terminals, in its shielded box at the cutter ([GM1 controls](../controls-2026-09-27/README.md)).
- **Rodent and VFD:** not ordered yet. The design assumes a Rodent V1.1 and the VFD that comes with the spindle kit. Nothing is waiting on them.
- **Tool changer: yes, a RapidChange ATC on this machine.**
  - **Order the Z slide with a 300 mm stroke**, not 100 or 200 mm: the same ZBX80 type (SFU1605, NEMA23). Its listing offers strokes from 100 to 600 mm.
  - RapidChange asks for at least 90 mm between the magazine and the spindle nut with Z fully up. The magazine rides on a tray above clamped stock, at Z1050.35. A 200 mm Z gives 110 mm there, 20 mm to spare; **300 mm gives 210 mm**, room for longer tools, taller clamps and whatever the delivered magazine really measures.
  - Rev L mounts the tool changer on the bed module, which keeps that magazine height. An earlier version of this note (`3a674bf`) expected the magazine up to 45 mm higher, to clear the bed lift; the bed-mounted layout avoids that. 300 mm stays the recommendation, for the margin.
  - The longer slide keeps the spindle's lowest reach; the Z body only grows upward. The top of the braked Z motor goes from Z1430.5 to about Z1630, 1.63 m above the floor. Nothing on the machine is above it, and the 8 ft ceiling and the A-frame hoist are clear of it.
  - The magazine itself is small: RapidChange gives 60 mm for its width. The design allows 520 × 60 × 80 mm (about 20 × 2.4 × 3 in); that envelope is not from supplier drawings.
  - Fitted in [Rev L](../release-review/RevL-CAD/README.md), with spindle reverse and the dock drive in the controls (M12, M13).
- **Shop:** a container with an 8 ft ceiling. Rev K's plan is a rolling A-frame gantry with a low-headroom hoist and the 0.7 m sling that passed the hoist-path check ([hoist in the container](../release-review/RevK-CAD/README.md#hoist-in-the-container)).
- **Parts (later on 27 September):** the plasma cutter and the torch are in hand. All the drive modules are ordered, the Z with a 300 mm stroke. The only parts still to wait for are the extra rails (the HGR20 kits) and the bed extrusion. [BUILD-ORDER.md](../release-review/RevL-CAD/BUILD-ORDER.md) lists what can be built before they arrive.

**Owner answers received on 26 September 2026:**

- **Controller:** BTT Rodent + grblHAL.
- **Order:** the 1000 × 800 × 100 drive modules. The other session's record says the Y modules are ordered and X and Z follow on 28 September.
- **Frame tube:** the owner is sourcing 2 × 2 tube at a scrapyard (other session's record). The Rev J package lists the 32 blanks to look for.
- **Bed requirement:** one-piece bed lifted out with a winch, released by at most about 12 screws of M8–M12, and waterproof for mist coolant when cutting aluminum.
- **Hoist:** an overhead beam with a trolley.
- **Bed top:** HDPE plates.
- **Name:** GM1 — Garcia Mechanical Table.

Rev J implements the bed answers. Rev G's six manual panels and MDF spoilboards did not meet them; Rev F was one piece but 87 kg and relied on MDF.

**Still needed from the owner:**

1. **Which line: answered on 27 September, the one-piece line** (Rev K, now Rev L with the tool changer). Please give design work to one session at a time. If you choose Rev I, this branch's bed module is dropped, and the Rodent choice and cost register would need carrying over. **Controller: settled, the Rodent** (owner, 26 Sep, reconfirmed after Rev I). **Bed conversion:** the variants' record says it stays within the machine footprint, while Rev J lifts the bed out on a hoist. Please say which you want. Please give design work to one session at a time; two sessions working in parallel is how the designs split.
2. **Hoist and bed stand:** a container with an 8 ft ceiling (27 Sep). Please confirm it is a standard 20 or 40 ft container, about 2.39 m inside. Rev K plans a rolling A-frame gantry. Still to choose: the A-frame and hoist, and where the module stand goes; the stand needs about 1.5 m of floor in front of the machine.
3. **Cutter:** it starts from the trigger, in mid-air (an HF start; 27 Sep). The cutter and the torch are in hand (27 Sep). Measure the torch before the clamp insert is bored, check the torch fits the cutter, and note the work-lead size ([build order](../release-review/RevL-CAD/BUILD-ORDER.md)).
4. **Orders: all drive modules ordered** (27 Sep), the Z with a 300 mm stroke. Still to come: the HGR20 guide kits and the bed extrusion. Record the quantities and price paid on delivery.
   - **Z: ordered with the 300 mm stroke.** The ATC was decided on 27 September (above). Rev L's pose checks cover Z 0–300.
   - The other session's ATC drives its slide from the Kraken's spare motor drivers, which the Rodent does not have, and was drawn on the six-panel bed. Rev L instead gives the dock a 24 V gearmotor on two relays, driven through the Rodent's I/O expander, and mounts it on the one-piece bed.
5. **Owned aluminum:** alloy and thickness of the 12 × 12 in pieces.
6. **Scrap tube:** for each piece of 2 × 2 tube, its usable length, measured wall and price, checked against the Rev J list.

**Engineering work that can proceed once those arrive:**

- Transfer-drill the Y datum bars and X guide face from the measured rails; replace the HGR20 hold in `motion_details.py`.
- Supplier data or measurements for the HMS40 base, ZBX80 output interface and spindle clamp (unsent request: `output/cad-repair-2026-09-25/SUPPLIER-DRAWING-REQUEST.md`), then design Z power-loss retention.
- Bed module: weigh it, proof-lift it once at twice its mass, map the six seat pads and the repeat seating, and test the M5 strip joints. Then build a combined stiffness budget (BED09).
- Controls: the [GM1 controls](../controls-2026-09-27/README.md) now cover the Rodent board map and pin allocation (RS485 dropped), and a terminal-numbered stop, permission and mode chain (CW-09 to CW-12). Still to do:
  - the ESP32 THCAD driver;
  - the plasma plugin in the ESP32 build;
  - the cutter interface (CW-02);
  - the interface board layout;
  - the bench tests.
- Procurement: quotes for the 51 unpriced entries and freight (the SteelMart request is ready but unsent); rebuild the workbook; regenerate the concept PDF for Rev J (it now shows the six-panel Rev H).
