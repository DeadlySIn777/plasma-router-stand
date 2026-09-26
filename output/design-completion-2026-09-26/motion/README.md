# Motion completion extension - 26 September 2026

This package makes concrete changes while preserving unresolved supplier
interfaces. It is not a machine release.

- `motion_completion.py` in the engineering source directory supplies
  `extend_router_model(m)` and `extend_stored_model(stored, source)` for Rev H.
- The inaccurate two-slot Z adapter becomes a guarded transfer-drill blank.
  All four known custom clamp holes remain. No output fasteners are invented.
- A labelled replacement-motor alternative reserves the sourced
  23HS30-5004D-B280 body with integrated power-off brake. Shaft/coupling/flange
  fit and dynamic brake behavior remain unqualified.
- A separate torch-clamp generator requires an explicit measured insulated
  barrel. The synthetic30 mm test case is not the owner's torch and is not
  exported as a project tool.

## Verification

`verification.json` records **9 of9 full Rev G baseline poses clear**, including
all eight nominal travel-box corners and center. Each contained1,283 solids;
all local solids were valid and world/local volume matched. There were no
unresolved positive-volume overlaps. The source hash stayed unchanged during
the157.5 second run. These results apply to the motion extension on Rev G;
concurrent bed/water extensions need the final combined Rev H check.

This report is the earlier motion-only development check. Later metadata
corrections leave its recorded source hash historical. Use the fresh combined
`../verification.json` and `../step-verification.json`, when present and passing,
for the integrated Rev H source/export state.

The API also rejected a missing torch measurement record and overlapping output
head pockets. The blank's DXF was written and reread with the shared exporter.
No delivered adapter machining pattern is implied by the guarded blank.

The static brake calculation is recorded separately from the geometric result.
It is not an assertion of dynamic arrest, cable clearance, rigidity or a fully
operational plasma assembly.

Read [the order and interface sheet](ORDER-AND-INTERFACES.md) before purchasing
the remaining X/Z items, and use [the arrival record](ARRIVAL-MEASUREMENTS.md)
for the already-ordered Y pair. No supplier was contacted and no purchase made.
