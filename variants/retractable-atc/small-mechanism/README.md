# Small machine: retracting ATC carrier candidate

This is a detailed, modeled **200 mm carrier with automatic endpoint locks**, on the existing 800 mm X / 1000 mm Y machine. It is **not an operational ATC release**. The proposed 200 mm Z replacement, exact magazine interface and small-machine cover still need completion/qualification; the small automatic controls profile remains disabled. The confirmed 100 mm Z has not silently been changed into a purchased 200 mm unit.

[Deployed full machine](../previews/small-deployed-full.png) · [Parked full machine](../previews/small-parked-full.png) · [Deployed mechanism](../previews/small-deployed-mechanism.png) · [Parked mechanism](../previews/small-parked-mechanism.png)

- [Full deployed STEP](output/step/SMALL_CONTEXT_DEPLOYED.step) and [full parked STEP](output/step/SMALL_CONTEXT_PARKED.step): 1,940 bodies each, including 1,669 context bodies derived from Rev I with the documented Z/fastener substitutions, 270 new mechanism parts and one visibly distinct magazine allocation.
- [Carrier deployed](output/step/SMALL_DEPLOYED.step), [travelling](output/step/SMALL_TRAVELLING.step), [parked](output/step/SMALL_PARKED.step): 270 bodies each.
- [Verification](verification.json), [structural screens](structure-check.json), [revised panel handling](panel-transfer-check.json), [additional Z/pin checks](supplement-check.json).
- [Cut list](output/cutlist.csv), [machining operations](output/part-operations.json), [individual STEP files](output/parts), [millimeter DXFs](output/dxf).
- [Shared hardware sources](../hardware/source-data.json), [Delta actuator](../hardware/LOCK-ACTUATOR.md), [pin sensors](../hardware/PIN-SENSORS.md), [controls](../controls/README.md).

## Geometry and usable space

| Item | Definition |
|---|---|
| Working stock/fixture assumption | Combined 50 mm above finished MDF at Z = 958.8 mm; top = 1008.8 mm |
| Full proposed cutting rectangle | X = 175–975, Y = 121.4–1121.4; 800 × 1000 mm |
| Rail | Two 350 mm MGNR12, four MGN12H blocks; 80 mm block-center pitch |
| Guide axes | X = 121 / 1029; Y = 1070–1420; rail base Z = 1007 |
| Carrier movement | CAD 0 = deployed, CAD 200 = parked; controls coordinate = 200 − CAD coordinate |
| Rail end reserves | 10.1 / 14.1 mm using 45.8 mm maximum block length |
| Drive | 17E19S1684MB4-300RS, TR8 × 8 × 300, 1.68 A per phase; nut faces motor |
| Screw end reserve | 10 mm with full 11 mm nut body engaged at park |
| Open carrier floor | Z = 1020: 11.2 mm above assumed stock/fixture top |
| Magazine support plane | Z = 1050.35; two 40 × 65 × 6.35 mm replaceable aluminum blanks |
| Unverified magazine allocation | 520 × 60 × 80 mm, deployed X = 315–835 / Y = 1070–1130 |
| Maximum accepted closed height | 87.65 mm for the stated 5 mm nominal upper screen |
| Tool clearance window | X = 335–815, deployed Y = 1065–1120; entire cutter envelope must fit |
| Maximum tool projection below magazine base | 36.55 mm for 5 mm clearance over the assumed 50 mm stock/fixture prism |

The model keeps the deep crossbeam behind Y = 1126.4, beyond the full-stock edge 1121.4, throughout translation. The guides are outside the 800 mm tool-center span. The clearance requirement also includes the loaded cutters: a longer projecting tool or taller clamp invalidates this 50 mm case. Magazine bolt holes, pocket centerline and end-cap/cover details have **not** been invented. The solid magenta box is an acceptance allocation, not supplier material; its overlap with mounting fasteners is not an approved manufacturer fit.

The proposed Z200 context preserves the lower nominal datum, extends the fixed module upward and raises the nominal retracted spindle 100 mm. It is a layout allocation. Actual Z200 carriage/pilot/holes, motor retention, cutting reach and nut datum must be matched to a selected supplier. The manufacturer's stated 90 mm setup clearance is not a substitute for that measurement. [RapidChange FAQ](https://rapidchangeatc.com/faq/).

## Load path and fabrication

Six welded, gusseted steel shelves bear against the underside of the existing chassis tubing. Finished steel spacers establish the datum. Two bolted 33 × 420 × 12.7 mm rail bars support the miniature guides. The moving steel wings, endcaps, 50.8 × 25.4 × 3.175 mm tube and open carrier form a welded subassembly. Machine/check the rail seats after welding; blue color does not mean aluminum.

The fabricated moving pieces total approximately 5.26 kg; all fabricated pieces total 12.32 kg. These are not complete carriage or machine masses: bought guides, fasteners, motor and real magazine/tools are excluded. The two aluminum magazine blanks can be finished 6.35 mm from the owned 3/8-inch stock only after its condition/alloy and available quantity are checked. The welded carrier remains steel.

The right rail bar has a 5 mm-long underside relief, 5.9 mm deep, leaving 6.8 mm over the existing rear gusset. Each wing's outer 2 mm underside edge is relieved 1.75 mm to clear existing Y-block screw heads while preserving its top fastener seat. These are machining operations in the STEP and DXF, not optional grinding after assembly.

[Structural calculations](structure-check.json) use 150 N vertical load and 19 Nm nut torque, separated by physical axis. They report weak-axis bending from vertical-spindle torque and torsion from a 50 mm eccentric vertical load. The scalar sum of named elastic effects is approximately 0.178 mm before guide/joint/spindle compliance. That does **not** establish the manufacturer's 0.2 mm pocket alignment requirement; installed loaded-pocket verification is still required. Sound steel properties are assumptions: unknown scrap condition, weld defects and corrosion are not qualified by the calculation.

## Locks and sensing

Two guided 6 mm steel pins engage 4 mm into separate carrier holes at the deployed and parked endpoints. They withdraw 6 mm, leaving 2 mm nominal running clearance. Steel housings and fitted endpoint stops carry reactions. The solenoid only withdraws an unloaded pin through an equal-arm 20 mm slotted bellcrank; it does not carry the tool-change torque.

Both Delta 24 V coils must be available to release both pins for travel. Allocate at least 0.8 A plus supply/temperature margin. Each pin has two separate PM-U25-P sensors and an opaque target attached to its actual lower stem: upright withdrawn sensor and inverted engaged sensor. The sensors impose no mechanical switch force. PNP outputs need the isolated input circuits; never wire 24 V directly to the Kraken GPIO. Four sensors are required for this small two-pin carrier; the shared six-sensor schedule applies to the large variant's three locks.

Pivot, follower and clevis pins have modeled heads and upset-tail retention. Peen only after assembly, preserve the specified free gaps and verify articulation; disassembly replaces these pins. The selected Delta face uses 8-32 screws with 2.675 mm nominal engagement. The delivered blind depth must be at least 3.175 mm, and the fork must supply the stated useful engagement depth; these unpublished dimensions remain inspection gates. The return spring is a force/space specification, not a verified catalog selection. Hot-force margin, friction, fouling and release timing remain physical tests.

## Baseline substitution and sequence

Only the **new combined context** substitutes one rear-left panel-clamp screw, ID `G_PANEL_CLAMP_BOLT_4_1`, with an ISO 7380-1 M6 × 35 button head, diameter 10.5 / height 3.3 mm. Its 35 mm shank and original 7.4 mm nominal thread overlap remain at the same datum. The 10.5 mm head bears entirely on the existing 12 mm OD washer (0.75 mm radial outside margin); washer ID 6.4 mm remains unchanged. This avoids the translating nut bracket. The frozen Rev I files are unchanged. Source: [Accu M6 × 35 class 10.9](https://www.accu.co.uk/socket-button-screws/494822-SSB-M6-35-10-9). New rail bar mounts use twelve M6 × 20 screws and twelve 3.2 mm thin M6 nuts, retaining 2.15 mm nominal thread projection. [Norelem thin-nut data](https://norelem.co.uk/medias/07212-Datasheet-4102-Hexagon-nuts-thin-type-DIN-439-ISO-4035-en.pdf?context=bWFzdGVyfHJvb3R8MTkzNDUyfGFwcGxpY2F0aW9uL3BkZnxhR1ZtTDJnMFpDODVORGN6TmpZMU9ESTJPRFEyTHpBM01qRXlYMFJoZEdGemFHVmxkRjgwTVRBeVgwaGxlR0ZuYjI1ZmJuVjBjMTkwYUdsdVgzUjVjR1ZmUkVsT1h6UXpPVjlKVTA5Zk5EQXpOUzB0Wlc0dWNHUm18YWZiYmYyZDY4YzBhZjdkMTE3ZGUwZjI1YWY4OWMwMzU5ZjJmOGVkMmFhMDdjYjY2NjRlMGYzMDU1ZTU2MWFlNg).

Carrier sequence: retract the spindle to its verified clearance datum, park the gantry forward, confirm stock/clamps/tools remain in the approved envelope, unload the engaged pin against the stop, energize release and verify both withdrawn sensors, translate 200 mm, approach the same endpoint stop at limited force, remove release power and verify actual endpoint engagement before allowing a tool operation. Stop if an endpoint or pin state disagrees. The current small controls profile intentionally refuses automatic M6 until a real dust-cover solution is defined.

Panel removal changes because the fixed rear supports obstruct the old 60 mm vertical lift. The candidate sequence removes panels 1, 2, 3, 4, 6, 5 into storage slots 6, 5, 4, 3, 2, 1 respectively. The rear-right panel lifts 20 mm, moves 407 mm forward, then rises another 40 mm. The rear-left panel lifts 2 mm, shifts 110 mm right into the empty bay, lifts another 18 mm, moves 407 mm forward, then rises 40 mm. The [panel report](panel-transfer-check.json) is authoritative for whether every segment passed. Reassembly reverses the revised sequence. The spoilboard checker separately repeats all 60 original rigid-board segments with the new ATC present. The beam checker uses the actual permuted panel solids in their new rack slots. Rear beam 4 lifts 30 mm, shifts 25 mm left, moves forward to datum Y1150, lowers 10 mm, advances to Y900 below the front hardware, rises 60 mm and restores X before the original front transfer. All 31 beam segments and 60 spoilboard segments pass with the parked ATC installed. Small-fastener transfer, restraint-transition hand access and flexible leads remain outside these rigid-part proofs.

## Reproduce and release boundary

For a fresh regeneration, run `build.py`, `verify.py`, `verify_panels.py`, `verify_other_routes.py spoil`, `verify_beams_revised.py`, `verify_supplement.py`, `structure_check.py`, then `finalize.py` using the CAD Python environment. The final index binds every report, source and active exported artifact. The current preserved STEP files have an [exact geometry-equivalence record](annotation-equivalence.json) for the later DXF cross-slot annotation correction; `verify.py --skip-context-export` verifies that record and the existing STEP hashes without rewriting them. Individual exports are 39 fabricated STEP parts and 24 DXFs; standard fasteners and sourced bought envelopes remain assembly-only.

The modeled carrier and bounded checks can be reviewed now. Outstanding release work is specific: actual magazine CAD/pocket/cover/tool projection; a selected Z200 module and its retention; small-machine cover and flexible wiring; spring and Delta inspection/force tests; real loaded-pocket alignment; and commissioning/handling checks beyond the rigid spoilboard, panel and beam routes. No purchase or firmware flash was performed.
