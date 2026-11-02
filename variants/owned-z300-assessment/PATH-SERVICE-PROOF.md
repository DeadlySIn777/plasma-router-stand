# Owned Z300 candidate: changeover and service geometry

The candidate now has a passing, source-consistent path/service geometry check in
`output/candidate-path-service-check.json` (schema `owned-z300-path-service-check/v1`).
This is evidence for the candidate assembly, not a fabrication or operating release.

`path_service_check.py` constructs the retained motion group using the frozen XR2
`motion.motion_parts(False,1275,575,200)`, then explicitly applies the stock-motor
300 mm physical-body overlay, both custom joint repairs and the six-part front-stop
repair. The scene adapter is cross-checked against `candidate_motion_factory.py`.
It removes the complete
tool modules as the original changeover procedure requires. The common Z remains
at X575, gantry Y1275, Z lift200. The assessed operating domain remains X800 × Y1000
× Z200; use of the additional 100 mm stroke is outside this check.

All **406 retained motion components** are checked against **1,560 regenerated
enclosures or brush/slot checkpoints**. These comprise 32 continuous cassette
segments, four continuous front-cover segments, five cover-slot checkpoints, one
continuous hatch sweep, eight brush solids, 1,504 continuous pan sub-enclosures,
two continuous receiver movements, one union-tool access box, and three
continuous receiver-roof removal enclosures. Every pair separates by an axis;
no exact intersection candidates or positive intersections remain. Every checked
normal changeover enclosure stays inside the 1150 × 1450 mm machine plan.

The cassette path is unchanged: remove 1→2→3→4, restore 4→3→2→1, with complete
spindle/clamp or plasma drop/head/torch modules removed throughout. Stored panels,
guide guards, parked ATC and the common Z remain. The full cassette path is covered
by analytic linear/rotation enclosures, not finite pose sampling. The five slot
checkpoints corroborate the unchanged continuous slot/axis proof inherited below.

The candidate check deliberately reuses the passing frozen XR2 evidence for
unchanged frame, bed, cassette, docking, storage, accessory, hinge, water-volume
and temporary-support geometry. It validates every source hash in the inherited
transfer, service, water and shield reports, records each report's own hash, and
recomputes every path against the entire replacement motion group. Cassette
segment bounds, all five pan-stage aggregate bounds, tote paths and hatch sweep
match the original route bounds to numerical tolerance. Additional checks include
the candidate motion group in the union-tool and roof-removal paths, where the
original check omitted that group. No imported factory or filesystem method is
patched; no baseline source or report is rewritten.

Rare pan/tote replacement retains the supported gantry and HGR guides, but requires
removal of **both** the ATC rail/drive/lock assembly and its independently mounted
hood/support assembly, receiver roof, heatshields, specified ledgers/front arms,
slats and disconnected wet fittings. The existing two-person pan-handling sequence,
two minimum 500 N props, dunnage and at least 1920 mm free overhead remain required.
The external empty-tote handoff belongs to rare maintenance; normal cassette
conversion requires no external swap space.

This closes the **nominal CAD path conflict question for the stated candidate and
park**, while preserving physical holds: received module dimensions and mounting,
actual mass/lead, power-off Z retention, joint/stiffness/handling tests, flexible
hose/cable routes, and tote usable capacity, loading and thermal/liquid compatibility.
Removal handling of disconnected accessories and carrying them away are not proved.
The candidate is therefore still **not released for fabrication or operation**.

Reproduce with the CadQuery-enabled Python interpreter:

```powershell
python variants/owned-z300-assessment/path_service_check.py
```
