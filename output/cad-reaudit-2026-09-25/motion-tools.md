# Motion and tooling CAD re-audit - 25 September 2026

**Status: NOT RELEASED.** Seven findings distinguish actual manufacturing/configuration defects from unresolved inputs and test limitations. No CAD source or historical report was changed.

## Fresh checks and a corrected earlier interpretation

The saved **22 clashes per motion state are caused by the standalone test fixture**. It omits the 6 mm rail-cap rise made by the integrated frame builder. With the cap datum corrected in memory before drilling, all five original motion configurations passed: **295 valid single-solid parts each, zero unresolved intersections, zero local/world volume differences**. Each state retains 54 documented purchased-envelope overlaps. This is a motion-and-caps check, not a continuous full-machine certification.

The parent `check_full_machine_poses.py` additionally completed **nine fresh full-machine router configurations: all eight X/Y/Z travel-box corners plus center**. Every configuration contained **967 valid solids with zero unresolved intersections**. Evidence: `full-machine-poses.json`. These checks cover the represented machine solids; actual cutters, workpieces, operational plasma tooling, cables and independent-Y skew remain unresolved.

The adapter DXF and both torch-clamp STEP files were also inspected directly. The DXF has rotated counter-slot machining geometry; the torch-clamp solids lack their described bolt holes. These are confirmed delivered-artifact defects, independent of supplier uncertainty.

## MT01 - P1 - Adapter front counter-slots are rotated 90 degrees in the delivered DXF

Evidence classification: confirmed manufacturing defect.

motion_details.py makes each front recess with slot2D(30,11,90), so the recess must be vertical in local XY. Its operation record omits angle, and cad_helpers.write_dxf emits every operation-slot horizontally. Fresh ezdxf extents show the first recess spans X5..35/Y39.5..50.5, whereas the solid recess requires X14.5..25.5/Y30..60; the second spans X75..105 instead of X84.5..95.5. Through-slots are correctly vertical.

Following the supplied milling-operation DXF will cut recesses across the adapter instead of along its carriage adjustment slots, leaving unrecessed screw positions and removing different material. The generic DXF syntax/audit pass cannot detect this.

Required action: Carry the slot angle in non-through operation metadata, rotate operation geometry in write_dxf, regenerate adapter STEP/DXF/operations, and compare the recess orientations and depths explicitly.

Sources: `motion_details.py:543`, `motion_details.py:550`, `motion_details.py:553`, `cad_helpers.py:111`.

## MT02 - P1 - Exported torch-clamp halves do not contain their claimed fastening features

Evidence classification: confirmed incomplete manufactured geometry.

tool_parking.py creates each half with one cylindrical subtraction only. Importing TORCH_SPLIT_CLAMP_REAR.step and FRONT.step confirms one radius14 cylindrical trough on local Y, with no M6 mounting bores or pinch bores. The rear stock is110x45.25x40 and front110x44.75x40. Both trough axes are at localX55/Z40 on the upper stock face; no installed assembly transform defines how those two open troughs become the claimed spindle-compatible clamp. Notes nonetheless specify four M6 mounting holes and two M6x60 pinch screws.

The provided solids cannot be fabricated into the described bolted clamp without redesign/missing operations. These parts are exported with ordinary engineering status, rather than being guarded incomplete purchased interfaces. The user-reported VIV ARC CUT-50 and a similar AG-60 listing do not verify an exact27.9mm owned barrel diameter.

Required action: Define the actual owned torch barrel/insulated clamping zone from measurement or its exact drawing, design and model both clamp halves and every fastening operation, prove the installed orientation, and guard the incomplete parts until that is done.

Sources: `tool_parking.py:33`, `tool_parking.py:34`, `tool_parking.py:37`, `motion_details.py:600`, `cad_helpers.py:166`.

## MT03 - P1 - Plasma setup CAD has no installed plasma cutting tool

Evidence classification: confirmed configuration omission.

export_states.plasma_model removes MOD_* bed parts and parks TOOL_SPINDLE_65x259, but otherwise retains the router head and its65mm split clamp. Both TORCH_CLAMP halves remain on the tank lid. The saved RevE_PLASMA_SETUP validation inventory agrees. There is no torch body, nozzle/tip datum, installed28mm clamp, float/breakaway stack, gas lead or torch cable envelope in this state.

A zero-intersection plasma setup result only verifies the bed-conversion display. It cannot verify plasma cut reach, torch-to-slat/float-bracket clearance, pierce/retract height, touch-off, or the tool-change geometry.

Required action: Create the real plasma-tool assembly and a distinct installed plasma configuration with its measured nozzle datum, mount, floating/breakaway mechanism and cable envelope; then verify travel and state transitions.

Sources: `export_states.py:27`, `export_states.py:35`, `export_states.py:42`, `motion_details.py:559`, `tool_parking.py:39`.

## MT04 - P2 - The 22 stored motion clashes come from an unraised cap fixture

Evidence classification: confirmed verification-fixture defect; physical-collision claim disproved for these pairs.

geometry_base defines caps atZ1050. Integrated make_frame raises them6mm before make_motion cuts the stop holes. check_motion_states omits make_frame and therefore checks caps6mm too low. All22 saved pairs involve those caps: two datum overlaps63800mm3 each, four guide-block overlaps6432.5mm3 each, eight cap-bolt overlaps141.37167mm3 each and eight nuts285.70342mm3 each. Fresh checks using caps initiallyZ1056, then the unchanged make_motion, pass all five original states:295 valid parts/state,0 unresolved overlaps,0 local/world volume mismatches. There are54 explicitly permitted overlaps/state.

The committed standalone test is genuinely failing, but those22 clashes are not evidence of physical collisions in the assembled geometry. MOTION-VERIFICATION.md also carries obsolete291-part zero-clash prose.

Required action: Make the test share the assembled cap datum before hole generation and regenerate its report/prose from actual results. Do not waive the overlaps or translate already-drilled caps, which moves the holes to the wrong height.

Sources: `geometry_base.py:135`, `frame_details.py:23`, `check_motion_states.py:29`, `motion_details.py:74`, `MOTION-VERIFICATION.md:3`.

## MT05 - P1 - Z output attachment is provisional and its slot/thread claims are not sufficient to choose hardware

Evidence classification: confirmed release hold plus unsupported fastening instructions.

The adapter has two7x30 vertical slots70mm apart and only two M6x16 screws, both at localY45. The note claims these cover15..45mm along-travel hole pitches, but a30mm-long slot cannot span two45mm-separated rows. For a centered6mm shank, the available center travel in that7x30 slot is approximately24mm. The note also proposes M6 screws into a diameter7 hole if tappedM6: a true7mm existing bore has no material to form a6mm-major-diameter internal thread. A through-bolt/nut solution is possible in principle, but carriage thickness, rear access, engagement and screw length remain unverified. The source explicitly leaves the Z base slots, output plane height and longitudinal pattern unresolved.

The listed screw/nut alternatives and15..45mm claim must not be treated as a manufacturing specification. Two modeled bolt axes do not establish actual supplier hole fit or joint capacity.

Required action: Resolve a measured or supplier-approved mating drawing; specify the exact hole type, number of bolts, washers/nuts and engagement, and revise the slot claim and provisional adapter. Preserve the hold until the joint has a defined load path.

Sources: `motion_details.py:538`, `motion_details.py:543`, `motion_details.py:546`, `motion_details.py:548`, `motion_details.py:555`.

## MT06 - P1 - HMS/HGR/Z mounting and power-off Z retention are still unresolved

Evidence classification: confirmed open design interfaces.

The source guards the HGR20 rail-hole pattern, HMS40 bottom-slot nut cavity/base fastening and endpoint datum, motor current/torque/cable outlet, and ZBX80 base/output geometry. No normally engaged brake or counterbalance is selected or represented. X/Y stops and three home switches are modeled; the Z home bracket and Z travel stops are not. The nominal100mm Z travel assertion is not a restraint or limit design.

The purchased modules cannot yet be ordered with a complete verified attachment package, and the suspended tool is not released for powered commissioning or a power-loss condition.

Required action: Close exact supplier/measured interfaces, select the Z retention arrangement and its attachments, add its envelope and release criteria, and complete Z limits/homing before freezing the CAD.

Sources: `motion_details.py:364`, `motion_details.py:494`, `motion_details.py:524`, `motion_details.py:604`, `motion_details.py:605`, `motion_details.py:606`, `motion_details.py:607`, `motion_details.py:609`.

## MT07 - P2 - Travel and service checks omit operational cutters, leads and dual-Y skew

Evidence classification: confirmed validation coverage limitation; no new physical collision asserted.

make_motion accepts one common gantry_y, so both Y sides always move together; neither the five corrected motion-subsystem states nor the nine fresh full-machine router poses exercise independent-Y homing/skew or a stalled-side condition. The parent check_full_machine_poses.py checked all eight nominal X/Y/Z travel-box corners plus center, with 967 valid solids and zero unresolved intersections in every pose (full-machine-poses.json). The spindle is a 65 x 259 mm cylinder with an explicitly assumed body/tip reference; no collet, cutting bit or workholding/toolpath envelope is installed. Cable chains, connector projections, hose bend radii and way covers are explicit remaining holds.

The nine full-machine router poses establish sampled static clearance for the represented solids. Nominal X800/Y1000/Z100 and those poses cannot certify continuous clearance, usable machining volume with actual tools/workpieces, service access, operational plasma geometry or auto-squaring behavior.

Required action: Define actual cutting-tool and plasma-tip datums and permissible stickout/workholding, include leads/covers, then extend the full-machine checks to the completed operational assemblies, continuous/swept motion and a bounded dual-Y squaring/skew scenario. Keep the test scope visible.

Sources: `motion_details.py:356`, `motion_details.py:357`, `motion_details.py:561`, `motion_details.py:564`, `motion_details.py:608`, `motion_details.py:609`, `check_motion_states.py:17`, `check_motion_states.py:43`, `full-machine-poses.json:1`.

## Additional covered items

- X/Y kinematic arithmetic agrees with the nominal 800/1000 mm travels. The modeled spindle axis is Y121.4-1121.4; its body bottom is Z960-1060. These are body datums, not a verified tool-tip cutting volume.
- Nominal fastener stack arithmetic checks: HGH M5 engagement5.3 mm; HMS M4 engagement8 mm; clevis M4 engagement6 mm; beam screw projection11.3 mm; rod coupler internal gap8 mm. This does not prove strength/preload or missing purchased mating features.
- Read all five adjustable float-carrier definitions and guard service instructions. The drawings explicitly leave actual float geometry/trip offsets to supplier verification and wet setting. No additional certain sensor CAD defect was assigned in this bounded review.
- Independent-Y squaring/skew, actual cutters and workholding, plasma tool stack, cable/air-lead bend envelopes, way covers and continuous tool-change/service paths remain outside the verified geometry.

Exact references, source hashes, artifact dimensions and fresh test results are in `motion-tools.json`.
