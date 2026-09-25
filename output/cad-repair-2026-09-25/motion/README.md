# Motion export repairs — 25 September 2026

MT01 and MT04 are repaired in the generators. MT05's misleading dimensions and fastening instructions are corrected, but the physical Z-carriage connection remains unresolved.

- **MT01:** non-through DXF slots now retain their angle. Both adapter recesses are vertical, 30×11 mm and 6.6 mm deep. The check reconstructed each exported DXF contour and compared its extruded void to the imported STEP pocket: symmetric volume difference below 1e-9 mm³. STEP readback is valid; DXF units are millimetres and its audit passes.
- **MT04:** the motion test now obtains the actual rail-cap datum from `frame_details.make_frame`, before drilling motion holes. The earlier targeted motion-and-caps check covered five configurations of 293 valid solids each, with zero unresolved intersections and zero local/world volume mismatches. This is a separate subsystem check; its count is two lower than the corrected audit fixture because the unsupported M6 carriage screws were removed.
- **MT05:** the exact supplier drawing assigns 70 mm transverse spacing to the smaller Ø5 fixing holes. No confirmed thread, longitudinal pitch or output mounting-face height was found. The adapter is guarded from individual production exports and the two unsupported M6 carriage screws are absent. See [Z-interface evidence](z-interface-resolution.md).

[Adapter evidence](adapter-export-check.json), [motion results](motion-validation.json) and [generated motion summary](motion-validation.md) record the results and source hashes. `check_adapter_export.py` reproduces the targeted adapter check. The motion test supports `--output-dir` so validation evidence can be regenerated without replacing historical records.

`TOOL_ADAPTER_110.PROVISIONAL.step`, its DXF and operations JSON are explicit comparison artifacts. They do not release the supplier mating interface for manufacture. Export an integrated revision to a clean output directory: the current exporter skips guarded parts but does not remove stale individual files from previous exports.

## Integrated Rev G verification

The corrected working CAD is exported separately in [RevG-CAD](../../release-review/RevG-CAD). Its [engineering manifest](../../release-review/RevG-CAD/engineering-manifest.json) records **1283 valid solids and zero unresolved intersections in both ROUTER and BED_STORED configurations**, with successful STEP round trips. Historical Rev E/F outputs and the historical audit are retained separately. BED_STORED is a storage layout, not an operational plasma assembly.

The final [full-machine motion evidence](revg-full-machine-poses.json) passes **nine complete router poses**: all eight X/Y/Z travel-box corners plus center. Every pose contains 1283 valid world and local solids, zero unresolved intersections and zero local/world volume mismatches. The run used the actual frame-raised cap datum and completed with unchanged source hashes. These remain sampled static axis positions; continuous axis motion, cutters, workpieces, hoses/cables and independent-Y skew are not proved.

The final [ordered panel-path evidence](revg-panel-path.json) proves **36 path segments for six panels**, stored in order 6→1. The complete straight translations use swept AABB bounds against actual fixed solids. Rotations use 2-degree cells with radius-based bounds covering all intermediate angles, rather than relying only on sampled poses. All bounds were clear above the 1e-6 mm³ Boolean volume tolerance and remained inside the original machine footprint; the smallest conservative footprint margin was 7.665 mm. Every final panel placement matches its CAD storage datum, and source hashes remained unchanged throughout the run.

Panel-path preconditions are explicit: router spindle/clamps already stored; six spoilboards, 24 screws, 24 top-slot nuts and 16 panel-clamp sets already removed and stored; four support beams, their bolts and the removable front seats/bolts still installed. Already stored panels remain in the fixed geometry for each later move. This panel check **does not prove those prerequisite transfers, beam or front-seat handling, human hand clearance, physical tolerance clearance or safe manual handling**. No mounting strength, Z retention or unresolved purchased interface is released by these checks.

`verify_revg_motion.py` and `verify_revg_panel_path.py` in the engineering source folder reproduce these final checks. Files with `preliminary` or `before-pinchbolt-storage-fix` in their names retain superseded verification runs and are not the final evidence.
