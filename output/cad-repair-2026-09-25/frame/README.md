# Frame detail corrections — 25 September 2026

These changes repair FW02 geometry, FW03 manufactured shield definition and FW05 nominal clearance from the historical CAD audit. They do not release the complete machine for fabrication.

## Cabinet stringers — FW02

Both `CAB_STRINGER` instances now contain two actual Ø6.0 mm bores through both tube walls. The local axes are X12.7 / Y12.6 and X12.7 / Y486.8, along Z. The nominal Ø5.5 mm screw shank has 0.25 mm radial clearance. Hole coordinates and the drilling operation appear in the part notes, which feed `part-operations.json` when the package is regenerated.

The stringer/screw collision exceptions were removed. The distinct self-drilling engagement into the bearer wall remains intentional. Both corrected individual stringer STEP samples were read back and checked; their removed volume equals four wall penetrations by a Ø6.0 mm drill. Screw-to-stringer overlap is zero.

## Drip shield — FW03

The former flat sheet with unspecified hems is replaced by an actual two-piece welded shield: a 436.4 × 233.211660 × 1.5 mm roof and a 436.4 × 20 × 1.5 mm front lip. Both are plain mild steel, continuously sealed at their joint and coated after welding. Both local flats match their STEP shapes. There are no bends and no assumed K factor or bend allowance.

The roof mounts rear high at a 1% slope, with front underside datum (356.8, 236.8, 675.5) mm. Four separate 3.048 mm tabs weld to the cage stringers; four modeled M5x20 screws and M5 nyloc nuts retain the shield through real Ø5.5 mm holes. No enclosure holes or load-bearing roof features are assumed. Roof-to-tab contact is verified. The roof and front lip fuse into a valid single-solid weldment.

The rear edge intentionally has no downturned lip, so it cannot catch the enclosure during withdrawal. After removing all four M5 bolts/nuts, translate the shield 230 mm forward parallel to its slope and lower it 100 mm into the front bay for hand removal. The route was sampled at 10 mm stations against the modeled frame, water equipment and nominal enclosure reserve, with no clashes. The reserve is not an actual door/hinge/latch model.

The installed shield clears the nominal enclosure by **2.6499 mm**. After welding and coating, verify at least 2 mm actual roof-to-enclosure clearance and 1 mm actual bearer clearance through the withdrawal route; rework the shield/tabs if those gauges fail. The selected enclosure drawing, fabrication distortion and physical service check remain release holds.

## Drained-level guard — FW05

The PAN_EMPTY carrier mount moved from Z802 to Z812; its guard underside moved from Z740 to Z750. Its dedicated backrail limits nominal carrier adjustment to Z812–832. The lowest possible setting including slot/shank radial play is Z811.7.

The rebuilt guard has **10.6713 mm** minimum distance to the actual sloped pan floor. At the lowest slot-play position it has **10.3713 mm**, leaving **2.3713 mm** for combined fabrication/datum variation while preserving the specified **8 mm minimum as-built clean gap**. Verify the whole guard footprint with a gauge after welding; rework a bracket that fails that gap. The carrier remains removable for brushing and washout.

This moves the float and therefore changes its relationship to water level. **The supplier's actual reed trip offset and the 60-second post-trip drain performance remain wet-commissioning holds.** Do not lower or extend the slots to recover an assumed trip point, and do not treat this float as proof of a bone-dry pan.

## Verification and limits

`verify_frame_repairs.py` freshly builds 443 frame/water/control components. All are valid single solids; the subset has zero unresolved positive-volume intersections. The constrained PAN_EMPTY carrier was also checked at both physical slot-play limits and 2 mm stations through the range. These sampled geometry checks are not a full machine motion or structural qualification.

`verification.json` contains source hashes, exact measurements, drilling metadata, collision results and generated STEP readback results. The STEP/DXF files in this evidence folder are verification samples; the main package still needs regeneration by the integration build.

FW03 manufactured geometry is now defined; its fit to the actual selected enclosure remains part of FW08 integration. FW01 plumbing, FW04 reservoir service, FW07 full-frame qualification and FW08 vendor enclosure integration remain open.
