# Motion subsystem verification

**Result: PASS** for the sampled nominal configurations below.

Original two rail-cap blanks after frame_details.make_frame sets their assembled datum, before make_motion drills holes. Other frame parts and spacers are excluded from this subsystem screen.

| Gantry Y | Head X | Z lift | Valid solids | Unresolved intersections | Documented overlaps |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1275 | 575 | 100 | 293 | 0 | 52 |
| 275 | 175 | 0 | 293 | 0 | 52 |
| 275 | 975 | 100 | 293 | 0 | 52 |
| 1275 | 175 | 100 | 293 | 0 | 52 |
| 1275 | 975 | 0 | 293 | 0 | 52 |

Local/world volume mismatches: 0.

Five configurations of the motion subsystem only. No claim of continuous swept-volume clearance or complete machine strength/commissioning.

The original unraised fixture was 6 mm too low and produced 22 spurious clashes per state. The test now obtains the cap datum from the assembly frame builder. Supplier interfaces, operational tool/cable geometry and Z retention remain unresolved; a passing screen does not release those items.

Exact source hashes, cap bounds and configurations are recorded in `motion-validation.json`.
