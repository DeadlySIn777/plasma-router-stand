# Follow-up on Rev G — 26 September 2026

**Still not released for fabrication or operation.** This page records the work done on top of the Rev G repair (`a61d634`), what it found, and what is still needed to finish the machine. Rev G itself is described in the [Rev G CAD package](../release-review/RevG-CAD/README.md) and the [repair report](../cad-repair-2026-09-25/README.md).

## What changed in this follow-up

- **Drive modules ordered.** The owner reported ordering the "rail kits" on 26 September 2026 and clarified them as 1000 × 800 × 100: the two HMS40 1000 mm Y drives (M02), the HMS40 800 mm X drive (M01) and the ZBX80 100 mm Z slide (M03). The [drive-module receiving check](../receiving/MOTION-MODULES.md) lists what to measure on arrival, which closes the drive-interface holds. The ZBX80 listing's side view scales to about 60–67 mm from base to carriage top, where the model assumes 80 mm; that one measurement moves the whole tool 13–20 mm in Y.
- **HGR20 guide rails still to order.** The design's separate HGR20 guides (M04, M05) carry the gantry and cutting loads; the HMS40 modules only push. Their [receiving check](../receiving/HGR20-RAIL-KITS.md) and `plan_rail_cuts.py` are ready. The Y-rail cut cannot be fixed before measuring: plausible hole patterns give 10/70, 40/40 or 73/7 mm off the two ends, and 40/40 would split a counterbore on one of them.
- **Controller chosen: BTT Rodent with grblHAL** (owner, 26 September 2026). This closes CW-01. The Kraken purchase, CB1 and Pi4B host boards and host USB cable left the priced register; the owner already owns a Kraken, now kept as the fallback. The Rodent board is listed as unpriced scope, and the external THC box is no longer planned.
- **Cost register reconciled with Rev G and the controller choice.** Priced scope is now **$5,348.40** ($5,262.15 goods + $86.25 known shipping; it was $5,810.24 on Rev E quantities), with **49 unpriced entries**. This is not a cheaper build; new Rev G items remain unpriced. Details are in [REAL-COST.md](../../outputs/reve-30510/actual-cost/REAL-COST.md). The Excel workbook could not be rebuilt here (`build_budget.mjs` needs the private `@oai/artifact-tool` runtime), so it still shows Rev E quantities.
- **Stock-fit check.** `outputs/reve-30510/actual-cost/check_revg_stock_fit.py` packs every Rev G flat part onto the sheet and plate sizes in the register, including flat parts that have no DXF, using the project's own packer.
- **Legacy generators.** The Rev B/C and Rev F brief generators no longer write to `output/pdf/plasma-router-stand-concept.pdf`, which now holds the Rev G review copy.
- **Wording.** The water sequence now names the Rev G bed parts and fasteners, and the cutter is the owner-reported VIV ARC CUT-50 rather than "unknown".

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

**Owner answers received on 26 September 2026:** controller = BTT Rodent + grblHAL; the order was the 1000 × 800 × 100 drive modules; and a new bed requirement: **one-piece bed lifted out with a winch the owner plans to buy, released by at most about 12 screws of M8–M12, and waterproof for mist coolant when cutting aluminum.** Rev G's six manual panels and MDF spoilboards do not meet that, so the bed needs a new revision. Rev F was one piece but relied on MDF and an unreachable surfacing pass.

**Still needed from the owner:**

1. **Bed module details:** where the lifted module goes (out of the front and set down, or hung), and the hoist to be bought (overhead beam or gantry crane, capacity).
2. **Cutter photos:** the VIV ARC CUT-50 rating plate, front and rear panels, and torch connector. These identify the version, start method and any CNC/arc-voltage connections.
3. **Orders:** quantities and price paid for the drive modules, and whether the HGR20 guide kits are already owned or still to order.
4. **Owned aluminum:** alloy and thickness of the 12 × 12 in pieces.

**Engineering work that can proceed once those arrive:**

- Transfer-drill the Y datum bars and X guide face from the measured rails; replace the HGR20 hold in `motion_details.py`.
- Supplier data or measurements for the HMS40 base, ZBX80 output interface and spindle clamp (unsent request: `output/cad-repair-2026-09-25/SUPPLIER-DRAWING-REQUEST.md`), then design Z power-loss retention.
- Joint tests: slot-lip preload on the panel ties (BED04), seat and beam fastening, and locator repeatability; then a combined stiffness budget (BED09).
- Controls: the Rodent port (board map, pin allocation, THCAD counter, RS485 VFD), then one terminal-numbered schematic covering the selector contacts, mode agreement, permissive chain and stop chain (CW-03, CW-09 to CW-12).
- Bed: a one-piece, waterproof, winch-lifted module to the new requirement, then re-run the static, motion and handling-path checks.
- Procurement: quotes for the 48 unpriced entries and freight; rebuild the workbook; regenerate the concept PDF after the next CAD change.
