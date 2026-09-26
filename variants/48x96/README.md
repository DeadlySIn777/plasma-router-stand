# Full-sheet 48 × 96 in hybrid — development layout

This is a separate, parametric development variant for a **1219.2 × 2438.4 mm usable sheet**, with the long direction along Y. That interpretation of “4 × 8” remains an explicit assumption. The model has a fabricated frame, wet pan, removable aluminum carriers, separate HDPE wear panels and space for a right-side RapidChange magazine. It is **not ready for fabrication or parts ordering**: purchased motion, docking hardware integration and the physical conversion sequence remain unfinished. Frozen Rev I files are not imported or changed.

Open [router STEP](router.step), [plasma/storage STEP](plasma_layout.step), or the [dimensioned plan](layout-plan.svg). [Router preview](layout-router.png) and [plasma preview](layout-plasma.png) are rendered directly from the CAD using a per-pixel depth buffer. Orange bodies are unselected motion allocations; purple is an ATC space allocation, not a verified product body.

## Dimensions and reach

| Item | Current dimension / position |
|---|---|
| Overall frame, including feet | 1950 × 2950 mm; eight legs |
| Usable sheet | 1219.2 × 2438.4 mm, starting at X180 / Y230 |
| Router deck | 1320 × 2550 mm, starting at X130 / Y175 |
| Removable modules | 3 columns × 6 rows; 18 carriers and 18 independent HDPE tops |
| Each panel | 438.667 × 423.333 mm; 2 mm gaps |
| Carrier construction | 38.1 × 25.4 × 3.175 mm aluminum RHS, two internal ribs, 6.35 mm backing plate |
| HDPE wear top | 12.7 mm; finished top Z912.7 |
| Grid / carrier / wear-top planes | Z829.55 / Z855.55 / Z912.7 |
| Grid-to-wear-top allocation | 83.15 mm = 26 mm docking interval + 38.1 mm frame + 6.35 mm backing + 12.7 mm HDPE |
| Full-deck surfacing tool-center bounds | X117.3–1462.7, Y162.3–2737.7, for a 12.7 mm cutter radius |
| Total X tool-center allocation including ATC | X117.3–1800; magazine center X1700 |
| X axis body allocation | X75–1875, including an assumed 80 mm carriage width |
| Y gantry allowance | Tool-to-gantry offset 100 mm; carriage half-length 90 mm; both travel extremes stay inside the frame |
| Wet pan inside | 1360 × 2590 mm; 2 mm sheet; floor underside Z650 |
| Water / slat planes | 50 mm nominal water depth, water Z702, slat tops Z710 |
| Vented reservoir | 450 × 1500 × 400 mm internal; 270 L gross / 230 L working allocation |
| Dry ATC bay | 600 × 200 mm in plan at X1600–1800 / Y400–1000 |

Full-sheet coverage and full-deck surfacing are different requirements; this allocation provides the latter as well as the former. Those arithmetic bounds do not establish real end-stop clearance, drive mounting, spindle reach, gantry collision clearance or ATC tool-length capacity. The smaller machine’s 800 / 1000 mm modules and 100 mm Z are not being silently stretched into this design.

## Frame, removable bed and storage

The main frame uses nominal 2 × 2 × 0.120 in steel tube, eight legs and deep side trusses. Actual junkyard tube wall, grade, corrosion, straightness and usable lengths must replace the nominal assumptions before a fabrication cut list is issued. Rail preparation strips are 8 mm machining/welding allowances, with no guessed rail holes.

The seven removable transverse grid beams use **4 × 2 × 0.120 in RHS on edge**. This is a stock alternative for the grid, not a requirement to replace all salvaged 2 × 2 chassis tube. Compared with two parallel 2 × 2 members per beam, the seven beams fall from 84.46 to 64.69 kg. Under an illustrative 500 N central load across a 1320 mm ideal simple span, elastic deflection falls from 0.270 to 0.100 mm; section stiffness increases by 2.69 times. These calculations do not qualify welds, connections, local walls, gantry stiffness or the complete tool-to-work load path. Stacking two tubes vertically cannot receive equivalent composite stiffness credit without a designed shear connection.

Each aluminum carrier is about **5.53 kg**, and each independent HDPE top about **2.24 kg**, before docking and clamp hardware. Splitting the bed avoids a single large aluminum/HDPE assembly. The [common locating interface](../common/location/README.md) provides a representative round/diamond pin concept and support cartridges; it is **not integrated into all 18 carriers here**. The reserved 26 mm lower interface keeps unnotched carrier tube above the upper receiver blocks. Pin projection above that plane still requires a properly machined carrier pocket. Clamp seats, attachment holes, HDPE expansion clearances and all actual locator loads remain open.

The plasma STEP places all 18 aluminum carriers, all 18 wear tops and all seven grid beams in separate poses inside the 1950 × 2950 mm plan footprint. **These are allocated storage poses, not supported storage racks.** Retention, spark shielding, handles, insertion paths and the complete manual conversion order have not been modeled or proved. The arrangement must not be treated as an instruction to leave parts unsupported. Its current purpose is to expose the volume that real racks and handling paths must fit.

## Water and mass tradeoff

The pan holds **176.12 L** at the nominal 50 mm depth. The reservoir working allocation leaves **53.88 L** beyond that volume for wet lines, heel/sludge and operational reserve. It stays vented; this layout does not qualify a pressure fill/drain scheme, pump, valve, hose route or automatic drain timing.

Pan and tank sheet were reduced from a heavy 3.048 mm first pass to 2 mm, with explicit pan bearers and a 225 mm tank stiffener grid. A simple one-way elastic strip screen gives approximately 1.56 mm pan deflection and 16.61 MPa bending stress at 50 mm water head over 425 mm support pitch. A 225 mm tank wall strip at a conservative full 400 mm water head gives approximately 0.98 mm deflection. These are preliminary screens; weld restraint, distortion, corrosion allowance, global support behavior and leak testing remain to qualify.

| Nominal modeled material | First pass | Current |
|---|---:|---:|
| Seven removable grid beams | 84.46 kg | 64.69 kg |
| Pan sheet | 101.32 kg | 63.99 kg |
| Bare reservoir sheet | 58.56 kg | 35.26 kg |
| Current reservoir stiffeners | Not included | 22.83 kg |
| Rail preparation strips | 46.10 kg | 29.04 kg |
| Entire modeled dry layout | 730.28 kg | **684.59 kg** |

The overall reduction is only 45.69 kg because the revised model also adds real pan support members, grid load pads and tank stiffeners. The current reservoir assembly is roughly 58.10 kg, so thinning its sheet alone is not a large net saving. **684.59 kg remains a heavy development candidate, not a finished budget recommendation.** It excludes motion hardware, motors, reducers, fasteners, cables, weld metal, ATC tools, stock and water. Adding only the nominal pan water gives approximately 860.71 kg. Stock loads, support reactions and floor/foot design remain unqualified. No purchase price or shipping quote is implied by these calculated masses.

## Long-axis drive choice

The provisional long axis uses independently driven racks on the two sides. Long rotating screws need a speed check before selection. For illustration, the THK permissible-speed expression with a 2900 mm bearing span, 20 mm **root** diameter and fixed-supported ends gives about 359 rpm; at 10 mm lead that is only 3.59 m/min. The formula already includes its stated critical-speed factor. Root diameter is not nominal diameter, and bearing and DN limits still apply. This example supports investigating rack drive or a rotating-nut alternative; it does not prohibit every possible ball-screw system. [THK speed selection](https://www.thk.com/us/en/products/ball_screw/selection/0007/), [THK equation and end-support factors](https://tech.thk.com/en/products/pdf_download.php?file=E_15_BallScrew.pdf).

Rack sections can be joined for long travel, but mounting accuracy, mesh and backlash need an actual selected rack/pinion/reducer design. Two motors on opposite Y sides are not the same thing as a preloaded dual-pinion mechanism on one rack. A module-2, 20-tooth pinion and 3:1 reduction would move 41.89 mm per motor revolution; the modeled 25.13 m/min at 600 motor rpm is arithmetic only, not an attainable feed rating. [Atlanta rack systems](https://atlantadrives.com/racks.htm), [Atlanta preload arrangements](https://atlantadrives.com/systems1.htm).

With rail centers 1800 mm apart, a 1 mm side-to-side position mismatch implies about 0.000556 rad of small-angle yaw and about 0.677 mm difference in Y position across the full sheet width. The Y error varies across X; it does not increase merely because the gantry travels farther along Y. Dual homing switches address initial squaring; they do not by themselves detect every cutting stall or structural deflection.

## ATC and remaining interfaces

The right-side bay preserves separate dry space and tool-center reach. Exact magazine endcaps, pocket pitch, cover sweep, fasteners, spindle reversal behavior, tool projection and Z approach must come from the selected kit. The common study requests at least 90 mm approach clearance, but this layout does not prove it for a real tool stack. See [RapidChange source review](../common/atc/README.md) and [controller integration study](../common/controls/ATC-INTEGRATION.md). No manufacturer bolt pattern is invented in these STEP files.

The next design gates are selected rail/carriage/drive interfaces and capacity; complete gantry and joint stiffness; carrier docking and thermal movement details; retained storage racks and an in-footprint conversion path; real spindle/torch/ATC assemblies and clearance; supported water routing and service access; cabinet, grounding, plasma interference protection and control interlocks. Stock loading/unloading access also needs a real handling plan. The current allocation is not an energized machine or a claim of automatic mode conversion.

## Evidence and reproduction

- [Layout report](layout-verification.json): 347 valid single solids per state, STEP re-import counts/volumes, deck coverage, plan containment and named reach checks. Physical release fields are explicitly false.
- [Static report](static-verification.json): 338 fabricated solids per state, zero unexpected positive-volume intersections. Nine unselected motion/ATC allocations are excluded. The checker uses AABB broadphase and exact Boolean intersections for candidates; the cleared final geometry has zero positive-overlap broadphase candidates. This does not test handling paths or strength.
- [Preview record](preview-verification.json): source and image hashes for the technical renders. Both 3D states were visually inspected after the per-pixel depth-buffer correction; the plan labels were also checked after encoding repair.
- [Independent package verification](package-verification.json): fresh STEP imports compared with a fresh parametric build, current source/report/artifact bindings and explicit hold fields. Passing that check certifies this bounded package, not fabrication readiness.

Run `python layout.py`, `python check_static.py`, `python render.py`, then `python check_package.py` from this folder using a CadQuery-capable environment. The renderer also requires NumPy and Matplotlib. All dimensions are millimeters.
