# Rev F package status

**Not released for ordering or fabrication. Fusion has not been opened.**

Rev F replaces the six-cassette bed with a ONE-PIECE hoisted module: welded steel ladder on the receiver ledgers, two machine-surfaced 12.7 mm MDF layers, ten cut-only full-length 20100 strips, four lift ears and four M8 drawdowns. Mode change is four bolts and the owner overhead winch. The engineering files below are current working deliverables. Successful solid checks and compiled firmware do not resolve the missing component interfaces.

| Evidence | Current result |
|---|---|
| RevE_ASSEMBLED_ENGINEERING.step: STEP readback and current file hash | PASS |
| RevE_ASSEMBLED_ENGINEERING.step: no unresolved static intersections | PASS |
| RevE_ASSEMBLED_ENGINEERING.step: current mechanical component count | PASS |
| RevE_PLASMA_SETUP.step: STEP readback and current file hash | PASS |
| RevE_PLASMA_SETUP.step: no unresolved static intersections | PASS |
| RevE_PLASMA_SETUP.step: current mechanical component count | PASS |
| RevE_ROUTER.step: STEP readback and current file hash | PASS |
| RevE_ROUTER.step: no unresolved static intersections | PASS |
| RevE_ROUTER.step: current mechanical component count | PASS |
| Motion definition included in assembly manifest | PASS |
| Sampled motion configurations free of unresolved intersections | PASS |
| Motion report source hash and local/world geometry agree | OPEN / FAIL |
| Sampled one-piece module hoist path report passed | PASS |
| Hoist report matches current geometry and checker source hashes | PASS |
| Nesting quantity, edge, DXF audit checks | PASS |
| Controller static/compiled-image checks | PASS |
| Water logic/inventory analytical screen | PASS |
| Current concept PDF content checks and file hash | PASS |
| All eight current concept PDF pages visually reviewed | PASS |
| Source-priced scope and grouped shipping reconcile | PASS |
| Unknown complete delivered total remains blank | PASS |
| Price register matches current research files | PASS |

## Cost

The current **priced portion is $5,810.24 USD before tax**: $5,734.94 in sourced goods and $75.30 in known or advertised shipping. This is a partial register, not the complete build price. 43 required scope entries still need a price or design decision, and other vendor shipping remains unquoted.

[Current workbook](../../../outputs/reve-30510/CNC-plasma-RevE-budget.xlsx) now separates priced items, remaining requirements and alternatives. The former $7,663.82 estimate is superseded: its allowances and $300 shipping reserve were not actual quotes. Owner fabrication labor remains $0. The unsupported $200 skin allowance is removed. The audit also found understated billet stock and omitted small-stock requirements, so no simple subtraction is presented as a finished total.

[Actual-cost findings and source register](../../../outputs/reve-30510/actual-cost/REAL-COST.md). The 80/20 beam and 16 T-nuts were configured together: $193.01 goods + $61.30 UPS Ground + $17.80 estimated tax = $272.11 to ZIP 30510. No order was placed. No cheaper rod-end or welded-bracket redesign has been adopted or credited as complete.

## Remaining motion design work

- Z slide: owner-supplied listing drawing closed the plan dims (body 219x80, ends 12, carriage 90x50, phi7/phi5 holes, 70 across). Output mounting-plane height, along-travel hole pitch/thread and base-slot fastening remain measure-on-receipt; the slotted TOOL_ADAPTER_110 is PROVISIONAL until transfer-verified.
- HGR20: seller P40/E20/1500 hole dimensions conflict. Actual factory holes must be verified before rail cutting or custom datum drilling.
- HMS40: base nut cavity and endpoint datum not published. Rail caps require a verified base clamp/nut design; motor current and torque-speed curves missing.
- Z power-loss retention: no selected normally-engaged brake/counterbalance. A ballscrew must not be assumed self-locking. Do not enable a suspended tool until retention is designed and tested.
- Head projection uses an explicit80 mm Z stack assumption. Final tool sweep and claimed usable1000 Y must be recalculated when supplier datum is recovered.
- X/Y physical stops and three home switches are modeled. Z home bracket and travel stops depend on the unresolved Z supplier endpoint/output geometry. Cable-chain anchors, way covers and spindle/torch cable bend envelopes still require final integration.

## Remaining electrical and procurement definition

- Confirm the owner-reported VIV ARC CUT-50 against its exact model/revision and document its trigger, starting method and arc-sensing interface. The AG-60 body listing does not establish those interfaces. Live plasma compatibility remains unverified. See PLASMA-COMPATIBILITY.md.
- Complete shared selector/contact blocks, bed/guard confirmation, isolated interfaces and physical panel layout. Water-circuit relays, suppression, branch fuses and terminal allocation are now specified in WATER-ELECTRICAL-REVIEW.md; timer DC contact suitability and pump starting-current/fuse instructions remain open.
- Obtain actual material, purchased-hardware and delivery prices. Custom cutting, finishing and machining are owner-performed; their operations remain in the drawings with no outside-shop labor budget. No supplier inquiry or purchase has been sent.
- Resolve guarded supplier interfaces and final full-travel clearances before manufacturing. Final process-specific CAM needs the fabricator’s machine, tooling and postprocessor.
- Check the actual torch body against the upper float guards: their X978 edge is only 3 mm beyond the nominal X975 maximum head axis. Final torch offset and usable plasma cutting area remain unresolved.
- Complete the cabinet VFD heat rejection, isolation hardware, panel layout, cable-chain anchors, way covers and cable bend envelopes. A purchased enclosure reserve is not a completed panel layout; transfer-drill its back-panel pattern onto the cage rails.
- Prototype-verify the Rev F bed fastening: MDF screw pull-out with the selected screws, TEK engagement in the 3.048 crossmember wall, and a first hoist with the module weighed and the sling geometry checked.

Cabinet service: RESOLVED by the Rev F relocation. The enclosure stands upright in the front bay under the water table, door forward through the open front window, on a bolt-on cage under pan bearers 1 and 2. Routine electrical service requires no draining and no pan or bed removal; the old horizontal above-tank placement and its blocked lid are deleted.

## Package navigation

- [Design, efficiency and control priorities](DESIGN-EFFICIENCY-REVIEW.md)
- [Manufacturing handoff](MANUFACTURING-HANDOFF.md)
- [Cut list](cutlist.csv)
- [Tube cut plan](TUBE-CUT-PLAN.md)
- [Flat-part nesting](nesting/sheet-nesting.json)
- [Metal suppliers, posted prices and delivery gaps](METAL-SOURCING.md)
- [Water control and operator sequence](WATER-CONTROL.md)
- [Water electrical components and terminal allocation](WATER-ELECTRICAL-REVIEW.md)
- [Fabrication operations and drawing limitations](FABRICATION-OPERATIONS.md)
- [Plasma cutter and torch compatibility](PLASMA-COMPATIBILITY.md)
- [Kraken firmware and pin map](../../../RevE-ENGINEERING/controls/README.md)
- [Controller commissioning](../../../RevE-ENGINEERING/controls/COMMISSIONING.md)
- [Supplier dimensions register](../module-mounting-field-register.md)
- [Unsent supplier drawing requests](../SUPPLIER-DATA-REQUESTS-DRAFT.md)

Prototype load, wet-transfer, electrical and cutting tests are subsequent commissioning steps. They are not claimed complete and are not substitutes for finishing the missing design dimensions.
