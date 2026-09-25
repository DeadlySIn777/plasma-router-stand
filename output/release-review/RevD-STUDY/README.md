# Rev D solid-geometry study — NOT RELEASED

This is a useful CAD starting point, **not a manufacturing release or a complete machine**. It does not replace the Rev C concept PDF. No toolpaths, G-code, fabrication DXFs or permission to manufacture are included.

## Open these STEP assemblies

- `step/assembled_bare_extrusion_NOT_RELEASED.step`: 132 individual solids; bare T-slot envelope work plane at **940.8 mm**.
- `step/assembled_with_optional_mdf_NOT_RELEASED.step`: 138 solids; optional 19 mm spoilboard raises the work plane to **959.8 mm**.
- `step/stowed_with_optional_mdf_NOT_RELEASED.step`: the same 138 parts, with four beam assemblies and six cassettes stored inside the reserved cabinet space.

Units are millimeters. X is right, Y is rearward, Z is above the floor. Component names are retained in the STEP assembly. Orange parts are unresolved hardware/connection reservations. The reservoir and purchased aluminum strips are explicitly **ENVELOPE** parts; their solid volumes must not be used as material weights.

## What is modeled

The frame and removable paired beams use hollow 50.8 × 50.8 × 3.048 mm tube, with idealized square corners. The three fixed pan bearers use 1032.4 mm blanks plus end-plate reservations. Rail-cap blanks use 5/16-inch thickness, explicitly 0.0625 mm below the original 8 mm cap datum. Weld preparations and purchased tube corner radii remain unresolved.

The fixed pan has five separate sheet solids and an actual 1% floor slope: the lower face is Z747 at the front and Z735 at the rear. Its nominal sheet thickness is 0.120 inch, measured normal to the sloped floor. The rim remains Z835 and the 19 slat tops remain Z850. The sloped pan still needs cradles/shims above the Z730 bearers, and the slats still need comb supports.

Each cassette contains five **20 × 100 × 397 mm purchased-profile outer envelopes**, with two 500 × 25 × 6 mm underside tie-bar blanks in the free span. Profile cavities and slots were not invented. Six 500 × 397 mm panels, separated by 3 mm seams, form a **1003 × 1197 mm** deck. The profiles bear directly on the paired crossbeams; the former 25 mm steel panel frames and 8 mm plates are not part of this study. Each strip has nominal 49.3 mm bearing at both ends and a 298.4 mm clear span. These dimensions do not establish the profile's load capacity.

## Validation performed

The build checked every solid for validity and compared its volume to an analytical value. Each exported STEP was reimported, checking solid count, aggregate component volume and assembly bounds. All three configurations passed. Broad-phase bounding boxes followed by solid intersections found **zero overlaps greater than 0.01 mm³ among the represented parts**.

All represented stowed beam and cassette solids fit the reserved clear box X75–1080, Y65–745, Z150–700. Beam storage origins were corrected to X111.5 and Y120/230/340/450, with a 25° rise from Z185. This containment check does **not** include actual rack hardware, handles, clamps or removal paths. In particular, only about 7 mm remains between the highest stored beam and the elevation of the pan-bearer underside. Hardware projection must be resolved before fabricating storage racks.

The old illustrative beam-clamp blocks intersected panel corners. They are omitted here, with their load-bearing interface held open; zero modeled clashes does not mean a working clamp has been designed. The original cabinet side sheets also need notches or revised upper edges around the fixed pan bearers. Cabinet skins are outside this study.

## Required next steps

`manifest.json` lists 13 release holds; `validation.json` contains the individual part records and measured bounds. Resolve the purchased module/profile interfaces, actual spindle and torch, beam and cassette locators/clamps, braces and welded connections, pan/slat supports, feet, reservoir architecture, plumbing and storage hardware. Then check full motion and insertion/removal paths, specify tolerances and fabrication methods, and verify loads and deflections. No check performed here establishes overall machine stiffness, safe load, supplier-part accuracy, physical fit or CNC readiness.

## Reproduce

Source: `build_revd_study.py`. Parameters: `study-parameters.json`.

The existing environment `smart_compressor/enclosure/.venv/Scripts/python.exe` contains CadQuery 2.7.0 and OCP. Run that interpreter with `-u` and the absolute source path. The script writes only inside this study directory. It exits after flushing all validation results to avoid the local OCP shutdown fault documented by the earlier project.
