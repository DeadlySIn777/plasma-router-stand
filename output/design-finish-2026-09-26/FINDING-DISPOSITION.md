# Original audit findings against Rev I

This records the current design response to all 29 findings from the
[25 September audit](../cad-reaudit-2026-09-25/README.md). The historical audit
is unchanged. A corrected nominal feature does not establish a complete
machine, supplier fit or physical qualification. Current evidence is bound in
[ACCEPTANCE.md](ACCEPTANCE.md); remaining tasks are in [OPEN-ITEMS.md](OPEN-ITEMS.md).

| Finding | Current disposition |
|---|---|
| BED01 — outside-footprint exchange | Forward hoist/cart architecture removed. Small panels, beams and separate boards use internal storage and explicitly checked routes. Head transfer is separately defined. Human handling and tolerances still need demonstration. |
| BED02 — unsupported fastener seats | Defective MDF sub-bed removed. New ties provide nominal washer seats; the actual slot-lip clamp capacity remains conditional. |
| BED03 — unreachable full surfacing | Unreachable full sub-bed skim removed. Six reachable spoilboard faces replace it. Actual cutter/workholding/guard clearance and repeat seating remain open. |
| BED04 — extrusion lips under preload | Captive nut strips are modeled. No ordinary M5 torque-table value is released; specified actual-profile coupon testing must establish permissible preload/uplift. |
| BED05 — unattached weldnuts | Gapped weldnuts replaced by defined bearing plates, bosses and compression sleeves. Current joint instructions specify force targets and conditional load checks. Weld and actual wall quality still require qualification. |
| BED06 — undefined locating fits | Round/relieved locators, engagement and storage receiver fits are defined. Actual manufacturing fits and repeat seating must be measured; clearance-bolted front seats do not automatically return to zero. |
| BED07 — accumulated strip tolerance | Slotted ties provide nominal lateral adjustment. Delivered profiles must fit the available allowance. |
| BED08 — missing skim in stack | Corrected: finished spoilboards are 18 mm after a 1 mm skim from 19 mm rough stock. |
| BED09 — incomplete stiffness bound | Actual bed-section/member calculations and proposed 100 N / 0.20 mm target are supplied. Full tool-to-work compliance remains unqualified; missing motion/joint terms are not assigned zero. |
| BED10 — TEK bed restraint | Original MDF-to-steel TEK joint removed. Current panel/beam joints have different defined load paths; actual fastening capacity still needs qualification. |
| BED11 — omitted sling/support system | Assumed owner winch and sling removed. Manual storage retainers and temporary keepers are modeled. Load screens and routes do not prove human grasp, reach or handling capacity. |
| BED12 — sampled clearance | Specified bed/storage/service/head routes use continuous or conservative swept-solid checks. Router and plasma-head travel corners plus center remain discrete samples; real leads, hands, skew and tolerances are excluded. |
| BED13 — inconsistent handling mass | Current inventory-based density estimates include captive hardware. They remain nominal dry estimates; weigh actual assemblies including residue and installed hardware. |
| BED14 — unreleased frame/pan rating | Braces, seats, storage rods, feet and support demands have conditional screens. Actual stock, welds, floor/contact and complete frame/tool-loop qualification remain open. |
| MT01 — rotated adapter DXF recesses | Corrected in the inherited repair and rechecked through common manufacturing definitions. Unknown purchased output holes remain guarded. |
| MT02 — missing clamp features | Defective old clamps replaced by machined halves, actual attachment/pinch features and a replaceable unbored insert. A production bore requires measured torch evidence. |
| MT03 — absent plasma head | Float/breakaway hardware, stops, magnets, guides and detection are now modeled. The installed hardware state intentionally contains no invented torch; actual torch/start/THC integration is still open. |
| MT04 — false cap collisions | Earlier 22 clashes were a fixture datum error, not machine collisions. Current full-machine poses use the raised rail-cap datum. |
| MT05 — guessed Z output attachment | Fictitious output mounting claims removed. Transfer blank preserves known custom tool-side features while awaiting actual output pattern, thread depth and height. |
| MT06 — mounting and power-off Z retention | Catalog module identity/lead and optional brake-motor envelope are documented. Actual rail/carriage/motor/coupling fit and complete power-loss behavior remain unqualified. |
| MT07 — incomplete operating envelope | Router and new head hardware poses checked. Actual cutter, torch/nozzle, tool leads, workholding, way protection and dual-Y skew still need integrated qualification. |
| FW-01 — incomplete water hardware/service | Supported drain/reducer/flange, tail parking, hose spans, pump orientation and removable strainer carrier now have CAD and service checks. Final measured fitting stacks and wet behavior remain open. |
| FW-02 — missing cabinet bores | Corrected stringer bores retained; new enclosure/rail/gland-cover fastening holes are modeled. |
| FW-03 — undefined folded cap | Replaced by defined sloped welded roof/lip/tabs; there is no fictitious folded-sheet development. |
| FW-04 — obstructed reservoir lid | Two accessible gasketed hatches, internal cover parking and washout provide the intended service route. This does not certify removal of the entire loaded lid or reach to every internal surface. |
| FW-05 — floor/guard clearance | Guard elevation corrected, retaining the specified minimum as-built clearance and wet calibration requirement. |
| FW-06 — guard/tool clearance | Head hardware is checked at travel extremes. Actual nozzle/cutter, useful cutting area and guard clearance remain dependent on measured tooling. |
| FW-07 — frame/support stability | Conditional stiffness, brace, joint, foot, tipping and sliding screens supplied. No complete physical frame/support rating is released. |
| FW-08 — cabinet service | Correct nominal cabinet/backplate and removable gland plates modeled. Empty front storage racks for service. Purchased door/lock/standoffs, populated control layout and heat rejection remain unfinished. |

No closure percentage is used: several findings concern different aspects of
the same unresolved measured interface or whole-machine behavior.
