# Selected-slide ATC carrier

This replaces the separate guide/belt axis with the owner's selected **311 mm
overall, 200 mm travel SFU1605 module**. Both original supplied drawings are
preserved in `sources`. The module's nominal underside slot positions and
4-M6 carriage count are known. Its actual nut profile, complete carriage-hole
coordinates/depth and exact carriage height are not supplied by those drawings.
The custom supplier-side faces remain clearly identified transfer-drill faces.

`actual_atc_parts(deployment, pins_withdrawn=False, hood='stored')` returns
physical component tuples for the integrated root assembly. Deployment is
0 mm at the working row and 200 mm parked. `acceptance_parts()` returns separate
purple capacity volumes; these are not manufacturer solids or hole templates.
The 520 × 60 × 120 mm capacity is an engineering acceptance requirement. The
60 mm body width comes from the FAQ; it does not establish complete endcap,
IR sensor or cable clearance. The shop's generic 52 × 12 × 12 cm family entry
is not an exact installed-kit drawing or proof that the complete kit fits this
60 mm longitudinal field. Complete-kit dimensions remain a release hold.
The working row is temporary: park the magazine again before full-bed cutting.

The horizontal module lies at Y1230–1541, with a separate motor reservation
ending Y1597. It fits the 1600 mm table. Its 600 mm 4080 crosscarrier is supported
at both endpoints by fixed reaction docks. Two standard ground-shoulder bolts
locate and clamp the chosen endpoint. They are manual setup fasteners, removed
before stage travel, not an automatic pin release. Right receiver bores have
1 mm extra relief along X to avoid forcing two round locators into a rigid
thermal-spacing constraint. This does not eliminate thermal pocket calibration.

The nominal tool row is Y1100. The raised bed is Z967.8; magazine base is
Z1039.15. A 40 mm workpiece/clamp envelope and 26.35 mm maximum below-base tool
projection retain 5 mm clearance. A conservative **120 mm kit-height capacity**
requires 244.15 mm lift for a P50 loaded tool and a 5 mm flyover gap. The owned
300 mm axis is assessed by the root design over 250 mm; no replacement Z is
inferred. The actual spindle/nut and existing boot registration are separate
source-fitting gates.

The 1.9 mm steel cover is removable for wood mode and fitted over the parked
magazine for plasma. It weighs approximately 4.20 kg as finished modeled parts,
excluding weld and coating additions. Two captive M4 clamps retain it; welded
spacers prevent loose spacer handling. Its entire manual changeover remains
inside the table plan: remove the two storage keepers, retract the cover clamps,
lift 500 mm, rotate 90 degrees about Y, move 390 mm left/70 mm rear, lower onto
the storage level, then insert 90 mm right onto the hooks and refit both keepers.
The continuous enclosure check covers these movements, not only the stored pose.
Actual grip, weight, tolerance and operator handling still need commissioning.

The included two 1085.7 mm flat 4080 crossbearers, four drop plates and cover
hanger belong to this takeoff. Do not count them again in the chassis schedule.
Their nominal extrusion core fixing is **M8**, not M6 in a 6.8 mm core. Ordinary
M6/T-nut fixings on the profile faces remain distinct. Exact received extrusion
slots, nuts, cavity depth and modified-section capacity require fitting checks.

Run `build_atc.py` with the project CadQuery interpreter. It exports the two
assemblies, 31 custom part STEPs, a takeoff, source hashes, static/continuous
motion checks, cover handling proof and a conditional stiffness screen under
`output`. The current source proves nominal geometry; it does not qualify
strength, joints, actual suppliers, complete machine compliance or operation.

## Current supplier boundary

The [official FAQ](https://rapidchangeatc.com/faq/) still routes mounting/pocket
CAD through Discord; the public channel result provides no attachment. It
reports a 60 mm body, ER11 tool diameter limit of 15 mm, and alignment sensitivity
around 0.2 mm. Reverse spindle control, a calibrated engage height and actual
nut compatibility remain necessary. IR detection monitors the real nut state.

The [current product form](https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/)
lists four-pocket Basic at $400, Pro with IR at $500, and Premium with IR/cover
at $600, before shipping/tax. Tool setters and mounting packages are additional.
The generic family dimension block is not a selected-variant mounting drawing.
No kit is assumed owned or free. See `sources/current-primary-evidence.json`.

The actual magazine/endcaps, nut/IR planes, pockets, cable exits and slide mating
pattern are still required to replace the capacity volumes with exact vendor
geometry. No drilling pattern, executable M6 routine or verified kit fit has
been invented. All fabrication/operating release flags remain false.
