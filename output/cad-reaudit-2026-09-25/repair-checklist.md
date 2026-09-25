# CAD repair checklist

All findings are open. The audit did not modify the design. Complete the architecture and datum work before freezing dependent details.

Audit records: 29; high priority: 14; medium priority: 15.

- [ ] **BED01 / P1 — The exchange route violates the within-footprint requirement**
  Select a mechanically defined in-footprint exchange/storage architecture, or record an explicit user-approved requirement change before treating this as the chosen design. Include support, retention and storage in CAD. See [Bed and structure](bed-structure.md).

- [ ] **BED02 / P1 — Five deck clamping stations break the MDF support edge**
  Relocate the five stations to supported bottom-slot centers or redesign the support width; recheck the full washer and pocket footprint against edges, notches and crossmembers, then regenerate both MDF layers and drawings. See [Bed and structure](bed-structure.md).

- [ ] **BED03 / P1 — The required full-face surfacing operation is outside the tool envelope**
  Define a feasible machined datum process with fixture and cutter access, change the support/motion placement, or specify external machining from measured final datums. Do not claim weld and ledger errors disappear until the operation is achievable and reinstallation repeatability is checked. See [Bed and structure](bed-structure.md).

- [ ] **BED04 / P1 — The selected M5 joint still loads the extrusion lips under tightening**
  Qualify the actual extrusion/nut/washer/MDF joint for assembly preload, local uplift, shear and creep; issue a controlled fastening method and replacement/reinspection limits. Do not automatically reinstate the prior0.35 N m number without validation. See [Bed and structure](bed-structure.md).

- [ ] **BED05 / P1 — Four drawdown weldnuts have an unclosed physical attachment detail**
  Detail the actual purchased weldnut, weld/bearing seat and assembly access. Use a compatible hole/seat or a designed bridge plate/boss; specify the weld and qualify local tube-wall load transfer at the chosen preload before releasing the ledger machining. See [Bed and structure](bed-structure.md).

- [ ] **BED06 / P1 — Locator fits and receiver engagement are not manufacturing-defined**
  Define a datum/fit scheme, typically one round locator plus a relieved locator or an equivalently justified alternative, with actual bushings if required. Specify machining after welding, positional/height tolerances, lead-in and retention, and measure repeated install flatness. See [Bed and structure](bed-structure.md).

- [ ] **BED11 / P1 — The sling and support system is outside the collision and load analysis**
  After resolving the footprint architecture, define a lifting-rated device, support/parking mechanism, actual rigging and credible unequal sharing; verify ear/weld/anchor loads and sweep the full rigging envelope. Weigh the finished module and include an operating stability/load case. See [Bed and structure](bed-structure.md).

- [ ] **FW-01 / P1 — Selected water hardware and its complete service route are missing from the CAD**
  Use verified selected valve/pump/strainer envelopes and connection datums; model supported gravity plumbing, hose bend envelopes, the anti-siphon discharge and removal spaces. Include an installation drawing with fitting/thread types and receipt-selected nipple lengths. Do not invent supplier dimensions. See [Frame, water and packaging](frame-water-packaging.md).

- [ ] **FW-07 / P1 — Whole-frame rigidity and support stability remain unverified**
  Set a required tool-to-work deflection budget and actual load cases, then check the assembled frame, connections, feet and support surface with appropriate analysis and/or a measured load test. Determine mass/center of gravity for router/plasma/service configurations and close anchoring/leveling requirements. Preserve the member-screen qualification. See [Frame, water and packaging](frame-water-packaging.md).

- [ ] **MT01 / P1 — Adapter front counter-slots are rotated 90 degrees in the delivered DXF**
  Carry the slot angle in non-through operation metadata, rotate operation geometry in write_dxf, regenerate adapter STEP/DXF/operations, and compare the recess orientations and depths explicitly. See [Motion and tools](motion-tools.md).

- [ ] **MT02 / P1 — Exported torch-clamp halves do not contain their claimed fastening features**
  Define the actual owned torch barrel/insulated clamping zone from measurement or its exact drawing, design and model both clamp halves and every fastening operation, prove the installed orientation, and guard the incomplete parts until that is done. See [Motion and tools](motion-tools.md).

- [ ] **MT03 / P1 — Plasma setup CAD has no installed plasma cutting tool**
  Create the real plasma-tool assembly and a distinct installed plasma configuration with its measured nozzle datum, mount, floating/breakaway mechanism and cable envelope; then verify travel and state transitions. See [Motion and tools](motion-tools.md).

- [ ] **MT05 / P1 — Z output attachment is provisional and its slot/thread claims are not sufficient to choose hardware**
  Resolve a measured or supplier-approved mating drawing; specify the exact hole type, number of bolts, washers/nuts and engagement, and revise the slot claim and provisional adapter. Preserve the hold until the joint has a defined load path. See [Motion and tools](motion-tools.md).

- [ ] **MT06 / P1 — HMS/HGR/Z mounting and power-off Z retention are still unresolved**
  Close exact supplier/measured interfaces, select the Z retention arrangement and its attachments, add its envelope and release criteria, and complete Z limits/homing before freezing the CAD. See [Motion and tools](motion-tools.md).

- [ ] **BED07 / P2 — Nominal strip-width tolerance is not absorbed solely at free edges**
  Inspect the actual profile and nut, calculate the cumulative lateral fit, and define independent strip datums, compensated hole locations or designed transverse clearance without weakening bearing seats. Carry the supplier tolerance and water-guard clearance through the check. See [Bed and structure](bed-structure.md).

- [ ] **BED08 / P2 — The modeled final stack omits the instructed1 mm skim**
  Separate rough and final thicknesses, define the finished support plane and remaining reface limit, and propagate those dimensions to screw lengths, nut engagement, work offsets and clearance checks. See [Bed and structure](bed-structure.md).

- [ ] **BED09 / P2 — The stiffness screen is not an upper bound on full machine compliance**
  Retain the member arithmetic as a limited screening result, remove unsupported bond/bound claims, establish acceptable bed-to-tool deflection, and verify the complete structural loop under representative loads and humidity/reinstallation cycles. See [Bed and structure](bed-structure.md).

- [ ] **BED10 / P2 — TEK restraint and pull-through are not qualified for the actual assembly**
  Select the exact screw and characterize its joint in the actual tube/MDF stack for pullout, head pull-through and assembly stripping, including representative local clamp loads. Correct the pitch arithmetic and retain a realistic load path. See [Bed and structure](bed-structure.md).

- [ ] **BED12 / P2 — Sampled positive-volume checks do not certify tolerance or continuous clearance**
  Define and check a swept-volume or justified adaptive clearance analysis for all retained hardware and attachments, include uncertainty margins and the actual footprint, and then verify physical clearances during commissioning. See [Bed and structure](bed-structure.md).

- [ ] **BED13 / P2 — Lifting mass has inconsistent estimation bases**
  Use one explicit mass basis, correct the washer density classification, include additions/uncertainty and compute center of gravity for the selected rigging. Replace the estimate with a weighed value before use. See [Bed and structure](bed-structure.md).

- [ ] **BED14 / P2 — Frame and pan support assumptions do not define a released structural rating**
  Define the actual mass/load envelope and performance targets; evaluate complete operating cases and load transfer through welds, feet, pan bearers and frame, then measure tool-to-bed deflection and repeatability. Keep the documented sand limitation. See [Bed and structure](bed-structure.md).

- [ ] **FW-02 / P2 — Cabinet stringers claim predrilled clearance holes but export as plain tubes**
  Cut the two through-clearance holes into each stringer solid and individual export, add their local dimensions to fabrication operations, and narrow/remove the exception once the clearance is real. Retain the separate intentional self-drilling penetration in the bearer wall. See [Frame, water and packaging](frame-water-packaging.md).

- [ ] **FW-03 / P2 — Drip-cap flat pattern does not define the instructed folded part**
  Choose the actual folded cap geometry and attachment, model the installed folded shape, then supply a developed flat with bend lines, radii, bend allowance and corner reliefs. Check door swing and lifting/removal using the selected enclosure. See [Frame, water and packaging](frame-water-packaging.md).

- [ ] **FW-04 / P2 — Reservoir lid removal has no demonstrated route past the rear brace**
  Define and collision-check a practical washout service sequence with lid-mounted equipment, cable/hose disconnects and handling clearance. If that needs pan removal, state it. Otherwise introduce a suitable service hatch or a structurally justified removable obstruction, then rerun the assembled route. See [Frame, water and packaging](frame-water-packaging.md).

- [ ] **FW-05 / P2 — Drained-level guard has only 0.672 mm clearance to the pan floor**
  Allocate a minimum as-built/debris clearance and adjust the guard or sensor arrangement accordingly. Preserve adequate adjustment travel and wet-calibrate the resulting drained threshold and delay. Check access for cleaning the narrow gap. See [Frame, water and packaging](frame-water-packaging.md).

- [ ] **FW-06 / P2 — Pan guards are outside center travel but very close to its right edge**
  Integrate the selected torch/nozzle/clamp and stock envelopes in plasma operating states. Define any reduced usable cut region or relocate guards outside the complete envelope; do not equate center travel with clear tool clearance. See [Frame, water and packaging](frame-water-packaging.md).

- [ ] **FW-08 / P2 — Cabinet access is plausible but an enclosure block does not prove service clearance**
  Use the selected enclosure drawing to model or conservatively bound the door/hinges/latch and removable panel; verify access, transfer holes, cable bend/entry spaces and thermal layout. Retain packaging-envelope release status until closed. See [Frame, water and packaging](frame-water-packaging.md).

- [ ] **MT04 / P2 — The 22 stored motion clashes come from an unraised cap fixture**
  Make the test share the assembled cap datum before hole generation and regenerate its report/prose from actual results. Do not waive the overlaps or translate already-drilled caps, which moves the holes to the wrong height. See [Motion and tools](motion-tools.md).

- [ ] **MT07 / P2 — Travel and service checks omit operational cutters, leads and dual-Y skew**
  Define actual cutting-tool and plasma-tip datums and permissible stickout/workholding, include leads/covers, then extend the full-machine checks to the completed operational assemblies, continuous/swept motion and a bounded dual-Y squaring/skew scenario. Keep the test scope visible. See [Motion and tools](motion-tools.md).
