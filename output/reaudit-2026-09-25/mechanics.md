# Mechanical reaudit — 25 September 2026

**Status: NOT RELEASED.** Current one-piece bed has confirmed fastening, datum-process and verification defects. This is a bounded audit of the saved snapshot, not an assertion that every possible failure has been found. No CAD source was changed and no export was regenerated.

The directory is named RevE while the current bed and mechanical documentation call the architecture Rev F. The JSON records SHA-256 hashes and exact line references for this snapshot.

## M01 — HIGH — Five deck fastener stations have inadequate MDF support

Evidence status: confirmed source geometry.

MDF spans X105.8–1044.2. For strip 1, alternating screw X103.5 at Y176.5/676.5/1176.5 is 2.3 mm outside its left edge. For strip 10, X1043.5 at Y426.5/926.5 is only 0.9 mm inside the right edge. These are Ø5.5 through holes with Ø16 underside pockets and Ø15 washers.

Three screws have axes outside the board; two more through holes and all five washer/pocket seats break the board edge. The specified 50 sound clamping stations are not achieved.

Required action: Move these five fasteners to supported bottom-slot centers, then recheck all washer footprints against the notched MDF and crossmembers and regenerate affected CAD/DXF.

Sources: `bed_details.py:18`, `bed_details.py:115`, `bed_details.py:119`, `bed_details.py:124`.

## M02 — HIGH — Promised in-machine surfacing cannot reach the complete MDF support face with the stated travel

Evidence status: confirmed dimensions; cutter and alternative setup unresolved.

MDF is X105.8–1044.2/Y76.5–1273.5. The nominal tool axis is X175–975/Y121.4–1121.4. Unreachable axis margins are 69.2 mm each X side, 44.9 mm front and 152.1 mm rear. Reaching the rear outer corners in this setup would require cutter radius at least hypot(69.2,152.1)=167.1 mm, before collision checks.

Flatness is made dependent on a machining operation that the chosen motion envelope does not support. A normal small-router surfacing bit cannot create the full bearing plane in one installed setup.

Required action: Define a feasible datum/surfacing process, resize/reposition the support, or use independently referenced shop machining. Verify actual cutter reach and collisions; do not assert all weld/ledger tolerance disappears.

Sources: `bed_details.py:18`, `bed_details.py:135`, `motion_details.py:614`, `motion_details.py:617`, `MECHANICAL-ENGINEERING.md:35`.

## M03 — HIGH — Bottom-slot lips still carry screw preload

Evidence status: confirmed incorrect load-path statement.

M5 screws run upward from washers below MDF into square nuts located above the extrusion bottom lips (TOP+1.3 mm). Tightening pulls each nut down against the lips and the screw head/washer up against MDF. Both the lips and MDF lie in the preload load path.

The statements that the nut bears on lips only under uplift and that torque is reacted by MDF instead of lips are mechanically incorrect. Removing the prior torque restriction and using snug-plus-quarter-turn is not justified.

Required action: Calculate or test the selected nut/lip/washer/MDF joint for assembly preload and service uplift; issue an appropriate controlled tightening method. Do not infer that the former 0.35 N m value is automatically correct either.

Sources: `bed_details.py:164`, `bed_details.py:167`, `strength-screen.py:49`, `MECHANICAL-ENGINEERING.md:39`.

## M04 — HIGH — Current motion verification is failing while prose claims zero clashes

Evidence status: confirmed report inconsistency; physical collision diagnosis unresolved.

Current motion-validation.json contains 22 clashes in each of five states, 295 parts per state, and a source SHA matching current motion_details.py. The first reported overlap is RAIL_CAP_1_BLANK/Y_DATUM_L at 63,800 mm³. MOTION-VERIFICATION.md still claims 291 solids and zero unpermitted intersections. Full assembly validation separately reports zero unresolved intersections.

The motion subsystem test and assembled geometry disagree. This may reflect the standalone test fixture using unmodified rail caps; it is not evidence that all 22 are physical machine collisions. It is nevertheless a failed current verification that cannot be presented as passing.

Required action: Reconcile the standalone fixture with the assembled frame, rerun the actual supported configurations and update prose/package status from the resulting report.

Sources: `motion-validation.json:3`, `motion-validation.json:13`, `motion-validation.json:14`, `check_motion_states.py:29`, `MOTION-VERIFICATION.md:3`.

## M05 — HIGH — Current exchange path leaves the machine footprint

Evidence status: confirmed requirement conflict against visible user instruction.

The present one-piece bed route is +60 mm lift, −1400 mm Y translation, then +500 mm hoist. Recorded moving envelope extends to Y−1376 mm. Storage explicitly parks the module outside the machine. The visible user requirement was to keep the swap within the machine footprint.

The modeled architecture does not satisfy the user’s footprint requirement. References to an owner 567 kg winch are not supported by the user messages available to this audit agent.

Required action: Restore an in-footprint architecture or obtain an explicit scope change. Treat the hoist, anchorage, track and park position as unresolved, not existing verified infrastructure.

Sources: `MECHANICAL-ENGINEERING.md:100`, `engineering-manifest.json:104`, `build_reve_engineering.py:48`.

## M06 — MEDIUM — One-millimeter surfacing allowance is absent from modeled final stack

Evidence status: confirmed dimensional inconsistency.

The model builds two finished 12.7 mm MDF layers from Z895.4 to Z920.8, then places strips at Z920.8. Assembly instructions remove 1.0 mm from the upper MDF before fitting strips. That operation would lower the support face and bare/spoil workplanes by 1.0 mm relative to the modeled values unless stock allowance or compensating placement is added.

Final datums, screw engagement and clearance checks do not describe the stated fabrication sequence exactly.

Required action: Define rough and final layer thicknesses and a final support plane, then propagate it through strip/spoilboard/fastener heights and CAM setup notes.

Sources: `bed_details.py:18`, `bed_details.py:135`, `bed_details.py:138`, `bed_details.py:203`.

## M07 — MEDIUM — Stiffness commentary credits an unmodeled bond and overstates the bound

Evidence status: confirmed unsupported analysis premise.

strength-screen.py says strips are bonded to the MDF; the bed assembly instead defines 50 screws, bare MDF top and glue only between MDF layers. The 0.148 mm/100 N sum excludes MDF compression, joint rotation and full frame deformation. MECHANICAL-ENGINEERING.md calls this a bounding case and claims actual deflection is substantially lower.

Correct simple-member arithmetic does not bound whole-bed/tool compliance. The proposed MDF joint may help load sharing, but its magnitude is not established by these calculations.

Required action: Remove unsupported bond/bound statements or define and qualify a real composite joint. Establish a target and verify complete bed-to-tool displacement, joint creep and reinstallation repeatability.

Sources: `strength-screen.py:37`, `MECHANICAL-ENGINEERING.md:61`, `MECHANICAL-ENGINEERING.md:63`, `bed_details.py:129`, `bed_details.py:136`.

## M08 — MEDIUM — TEK thread-pitch arithmetic and restraint description need correction

Evidence status: confirmed arithmetic error; capacity remains unresolved.

#12-14 has nominal pitch 25.4/14 = 1.8143 mm. A 3.048 mm wall spans 1.68 pitches, not the claimed about 1.1. Actual effective threads also depend on the screw drill point and thread geometry. Calling TEKs only registration ignores possible local strip/clamp uplift transferred through the MDF.

The fastening screen is not a selected screw’s tested connection capacity.

Required action: Use the exact screw product and load path to establish pullout/pull-through and tightening limits; retain the physical drive/strip test.

Sources: `strength-screen.py:53`, `bed_details.py:144`.

## M09 — HIGH — Known motion interface and power-loss restraint holds remain open

Evidence status: confirmed unresolved design inputs.

Current motion source explicitly leaves Z output mounting height/pitch/base slot fastening, HGR rail-hole datums, HMS base mounting and endpoint/current data, Z brake/counterbalance, cable-chain anchors and tool cable sweep unresolved. The Z mounting stack still assumes 80 mm.

The model is not ready to order all interface hardware or issue complete manufacturing/CAM setup instructions; nominal X800/Y1000/Z100 is not a certified usable cutting envelope.

Required action: Close supplier/measured interface drawings and select/test power-loss retention, then recalculate usable tool motion and issue guarded parts only when their inputs are resolved.

Sources: `motion_details.py:603`, `motion_details.py:607`, `engineering-manifest.json:197`.

## M10 — MEDIUM — Winch rating ratio is not a complete lifting-system margin

Evidence status: confirmed unverified rigging assumptions.

The manifest estimates 87.0 kg; the swap report estimates 85.1 kg under a different mass basis; prose says about 86 kg. A 567 kg winch rating divided by module mass is only a load/rating ratio. Sling load sharing, sling angle, ear out-of-plane loading, anchorage and trolley track are not modeled; four equal leg reactions are assumed in the under-300 N ear statement.

A greater-than-six ratio cannot release the complete hoist arrangement, and a cable winch capacity alone does not establish suitability for a suspended load.

Required action: Identify a lifting-rated device and full support/rigging arrangement, calculate credible unequal sling loading and ear/weld forces, verify mass, and provide a stable parking/support method if the architecture is retained.

Sources: `strength-screen.py:56`, `MECHANICAL-ENGINEERING.md:102`, `engineering-manifest.json:101`.

## Independent checks

- The current square-tube cut schedule has 28 blanks, net 28,356 mm, from five 20-foot bars. All identities/quantities match the current cutlist; kerf and trim arithmetic passes. Three bars retain only 6 mm beyond the stated trim and cuts, so full usable stock length matters.
- Current assembly/router/plasma STEP file hashes match their validation records (967/967/731 solids). Their existing reports claim zero unresolved static intersections. This does not supersede the failing standalone motion test.
- The motion source hash matches its report, but all five states record 22 clashes. Diagnose the test fixture before treating those as physical collisions or clearing them.
- The current sampled hoist report has 92 poses, 22 boolean checks and no reported failures; source hashes match. It is a sampled path for a module that travels outside the machine footprint, with rigging excluded.

Machine-readable evidence, all source hashes and exact references: `mechanics.json`.
