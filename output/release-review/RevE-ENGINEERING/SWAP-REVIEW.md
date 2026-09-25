# Rev F sampled bed-module hoist review

Generated 2026-09-25T05:46:40.852248+00:00.

**Result: PASS SAMPLED PATH.** 92 sampled poses, 22 actual-solid intersection checks, 0 recorded failures.

The fixed source assembly contained 726 retained obstacles. Fixed X extent -28.400 to 1178.400 mm was never exceeded. The sampled moving envelope is X55.000 to 1095.000, Y-1376.000 to 1326.000, Z834.000 to 1519.800 mm.

## What was checked

The complete one-piece module - steel ladder, lift ears, both MDF layers, all ten strips, deck fasteners and both optional spoilboards - moves as one rigid body with the four drawdown bolts removed. Every fixed part except the removable spindle/torch remains an obstacle, including slats, pan floats, float guards, sensors, reservoir and controls.

The path is three pure translations: +Z 60 lift (5 mm steps), -Y 1400 forward exit (25 mm steps), +Z 500 hoist. Key modeled clearances at handling height: crossmember undersides (Z917.3 lifted) pass the Z910 float backrails by 7.3 mm and the slat tops by 67.3 mm; lift-ear tops (Z1001 lifted) and the trimmed spoilboards pass beneath or between the rear-parked Y guide shoes with 10 mm minimum; the notched MDF right edge clears the float posts in plan. Nominal source-geometry gaps; fabrication variation and debris reduce them.

Rigging is NOT modeled: sling legs, hook travel and winch anchorage are owner scope. Keep the four-leg sling symmetric; the ear holes sit above the module center of mass.

## Reproduction and source scope

Run `swap-path-checks.py` with the project CadQuery environment. `swap-path-checks.json` records every sampled transform, the obstacle inventory, source hashes and BREP fingerprints. `bed-configurations.json` records the module part list and the removed-for-handling bolts.

A passing source-geometry check does not verify unseen vendor dimensions, rigging capacity, electrical safety or ergonomics. Recheck the path if the head, cabinet, sensor, cable or guard envelope changes.
