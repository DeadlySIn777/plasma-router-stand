# GM1 follow-up after Rev G — 26 September 2026

**Still not released for fabrication or operation.** This page records the work done on top of the Rev G repair (`a61d634`), what it found, and what is still needed to finish the machine. The machine is now named **GM1 — Garcia Mechanical Table** (owner, 26 September 2026). The current design is [Rev J](../release-review/RevJ-CAD/README.md), first published on this branch as "Rev H" and renamed on the evening of 26 September (see the first item below). Rev G is described in its [CAD package](../release-review/RevG-CAD/README.md) and the [repair report](../cad-repair-2026-09-25/README.md).

## What changed in this follow-up

- **Base branch merged: two different "Rev H" designs (evening of 26 September).**
  - **What arrived:** the owner's other session pushed its own Rev H to the base branch (`9e3dd66`). It keeps the six-panel bed stored in the frame, adding storage restraints, and adds reservoir service hatches, a washout flange, a refill spout, drain reserves, a Z-adapter transfer blank and a braked Z-motor candidate. Its [completion report](../design-completion-2026-09-26/README.md) records that the one-piece question "has no answer" in that session.
  - **The rename:** this branch's one-piece bed answers the owner's requirement given here, so it stays the current design. It was renamed **Rev J** because the base's Rev H uses the same folder names; Rev I is skipped. The base's Rev H files are unchanged, and that design stays documented as the six-panel alternative.
  - **What Rev J takes from the base's Rev H:** its water-service and Z-adapter work, unchanged except for the refill spout. The spout's riser stood under the module's rear crossmember, so `water_revj.py` moves it from Y1255 to Y1215.4 (between slats 18 and 19) and turns its head along −X. It keeps the 30 mm air gap, and a floor gusset replaces its stay. The module's end crossmembers and deck move 15 mm rearward, which leaves 21 mm between the spout and the module.
  - **Checks on the combined model, all pass:** static (978/829/149 solids, 0 unresolved overlaps), nine motion poses, the hoist path at three hook heights, and the water-service paths (both hatch covers and the washout cover). One gap got tighter: with the steepest sling checked (hook 2.0 m above the lug holes), one rear leg passes 8.6 mm from the rear-parked X rail. The recommended 1.0 m hook rise keeps every leg more than 40 mm clear.
- **Rev J bed, to the owner's requirement.** One waterproof bed module of about 63 kg: a galvanized 2 × 2 steel frame, nine 1,197 mm T-slot profiles from the same five two-packs, and two HDPE plates surfaced in place, with no MDF. Six M10 screws hold it and two pins locate it. For plasma work it lifts 70 mm in place and leaves through the front window on the owner's overhead beam-and-trolley hoist.
  - **Checks:** static interference (0 unresolved overlaps in the router, bed-out and module-only states), nine motion poses (pass) and the hoist path with the 4-leg sling modeled at hook heights 0.7, 1.0 and 2.0 m (pass, 0 intersections; nearest gap 11.2 mm to the frame legs).
  - **Removed:** Rev G's racks, trays and slat end reliefs.
  - Details are in the [Rev J package](../release-review/RevJ-CAD/README.md); the shopping-list changes are in [REVJ-PROCUREMENT-DELTA.md](../../outputs/reve-30510/actual-cost/REVJ-PROCUREMENT-DELTA.md).
- **Cost register re-baselined to Rev J.** Priced scope is now **$5,336.10** ($5,249.85 goods + $86.25 known shipping, including the $82 price the owner reported for the 1,200 mm rail kit), 73 priced lines and 51 unpriced entries. The Rev G bed rows (MDF, ties, rack stock, N3, N5) are superseded, N1 is 48 stainless nuts, and the Rev J HDPE, stainless, lug bar, 8 ft tube and galvanizing rows are unpriced, as are the Rev H water-service items: 4 mm washout plate (MET-GAP-24), NPS 1/2 refill pipe (MET-GAP-25), and hatch and washout fasteners (HW-GAP-H03). The three new gaskets come out of the existing EPDM sheet. The SteelMart request lists Rev J stock.
- **Drive modules: Y ordered, X and Z on Monday.** The owner reported ordering the "rail kits" on 26 September 2026, clarified them as 1000 × 800 × 100, and said the HMS40 spec sheet and ZBX80 drawings shared that day "are ordered": the two HMS40 1000 mm Y drives (M02), the HMS40 800 mm X drive (M01) and the ZBX80 100 mm Z slide (M03). The owner's other session recorded the same day that the Y modules are ordered and on the way, and that X and Z will be ordered on Monday 28 September. The records now follow that split; please confirm. The [drive-module receiving check](../receiving/MOTION-MODULES.md) lists what to measure on arrival, which closes the drive-interface holds. The ZBX80 listing's side view scales to about 60–67 mm from base to carriage top, where the model assumes 80 mm; that one measurement moves the whole tool 13–20 mm in Y.
- **HGR20 guide rails: kept, still to order.** The owner decided on 26 September to keep them ($110 for the 1,500 mm kit and $82 for the 1,200 mm kit, owner-reported). The design's separate HGR20 guides (M04, M05) carry the gantry and cutting loads; the HMS40 modules, whose 1000 × 800 × 100 strokes are the machine travel, only push. Their [receiving check](../receiving/HGR20-RAIL-KITS.md) and `plan_rail_cuts.py` are ready. The Y-rail cut cannot be fixed before measuring: plausible hole patterns give 10/70, 40/40 or 73/7 mm off the two ends, and 40/40 would split a counterbore on one of them.
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

## What is needed to finish

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

1. **Which bed:** this branch's Rev J one-piece module, which follows the requirement above, or the base branch's six-panel Rev H? Both are in the repository, and Rev J is marked current. Please give design work to one session at a time; two sessions working in parallel is how both came to be called Rev H.
2. **Hoist and bed stand:** the ceiling or beam height available. With the recommended sling the hook is at about 1.99 m with the module raised, plus the hoist's own headroom. Also the hoist and trolley to be bought, and where the module stand goes; it needs about 1.5 m of floor in front of the machine.
3. **Cutter photos:** the VIV ARC CUT-50 rating plate, front and rear panels, and torch connector. These identify the version, start method and any CNC/arc-voltage connections.
4. **Orders:** confirm the X and Z drive modules on Monday, the quantities and price paid, and when the HGR20 guide kits are ordered.
5. **Owned aluminum:** alloy and thickness of the 12 × 12 in pieces.
6. **Scrap tube:** for each piece of 2 × 2 tube, its usable length, measured wall and price, checked against the Rev J list.

**Engineering work that can proceed once those arrive:**

- Transfer-drill the Y datum bars and X guide face from the measured rails; replace the HGR20 hold in `motion_details.py`.
- Supplier data or measurements for the HMS40 base, ZBX80 output interface and spindle clamp (unsent request: `output/cad-repair-2026-09-25/SUPPLIER-DRAWING-REQUEST.md`), then design Z power-loss retention.
- Bed module: weigh it, proof-lift it once at twice its mass, map the six seat pads and the repeat seating, and test the M5 strip joints. Then build a combined stiffness budget (BED09).
- Controls: the Rodent port (board map, pin allocation, THCAD counter, RS485 VFD), then one terminal-numbered schematic covering the selector contacts, mode agreement, permissive chain and stop chain (CW-03, CW-09 to CW-12).
- Procurement: quotes for the 51 unpriced entries and freight (the SteelMart request is ready but unsent); rebuild the workbook; regenerate the concept PDF for Rev J (it now shows the six-panel Rev H).
