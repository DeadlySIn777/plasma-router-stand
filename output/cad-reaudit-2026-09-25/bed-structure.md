# Bed, exchange module and structural CAD reaudit — 25 September 2026

**Status: NOT RELEASED FOR FABRICATION / CAD-CAM HANDOFF.** The current Rev F bed has confirmed fastening/process/requirement conflicts and several unqualified joint and tolerance details. No CAD was changed. This report distinguishes proved geometry from missing verification; it does not certify every possible failure mode.

## Scope and independent work

Read-only audit of current Rev F bed in RevE-ENGINEERING folder. No design edits or generator output refresh. Root team covers global STEP/DXF inventory and motion/tools/water systems.

The fresh bed-only reconstruction produced 246 valid components including two ledger fixtures. Direct B-rep measurements found a 1.4944465 mm weldnut-to-ledger gap. The left/right rails were proven identical after end-for-end rotation, avoiding a false shared-part-number finding. The reconstructed profile section is612.973813 mm² with Ixx 27207.732889 mm4. Coordinate and engineering arithmetic were recalculated independently.

The saved full-system swap check remains 92 samples/22 Boolean checks with matching source hashes. It was inspected, not rerun for this bed sub-audit. Full assembly/export verification is handled by the parent audit. All fresh geometry queries returned results; the CAD interpreter was interrupted only after it lingered at teardown.

## Findings

### BED01 — HIGH — The exchange route violates the within-footprint requirement

**Evidence:** confirmed requirement conflict.

The source commands +60 mm Z, -1400 mm Y and then +500 mm Z. The saved moving envelope is Y -1376 to 1326 mm; only X footprint is checked. build_reve_engineering explicitly parks the module outside the machine. The visible user instruction rejects front clearance and requires the swap within the machine footprint. An owner-supplied 567 kg overhead winch is a source assertion, not an established user input.

**Effect:** A passing sampled path does not satisfy the selected architecture requirement. The design requires a front corridor and off-machine support/parking that the user rejected.

**Required closure:** Select a mechanically defined in-footprint exchange/storage architecture, or record an explicit user-approved requirement change before treating this as the chosen design. Include support, retention and storage in CAD.

Sources: `swap-path-checks.py:19,20,49,50,70,139,140,141`, `build_reve_engineering.py:48,51`, `MECHANICAL-ENGINEERING.md:31,100,102`. Rechecks/extends prior M05.

### BED02 — HIGH — Five deck clamping stations break the MDF support edge

**Evidence:** confirmed geometry defect.

MDF spans X105.8 to 1044.2. Strip 1 screws at X103.5 and Y176.5/676.5/1176.5 have axes2.3 mm outside the MDF. Strip 10 screws at X1043.5 and Y426.5/926.5 have axes only 0.7 mm inside the right edge (the earlier audit incorrectly said0.9 mm). Their Ø5.5 holes, Ø16 underside pockets and Ø15 washers therefore lack complete seats. All fifty CAD fasteners exist; five complete bearing stations do not.

**Effect:** The intended MDF/washer/screw load path is absent or truncated at these stations. Valid B-rep solids and zero interference cannot detect the missing bearing area.

**Required closure:** Relocate the five stations to supported bottom-slot centers or redesign the support width; recheck the full washer and pocket footprint against edges, notches and crossmembers, then regenerate both MDF layers and drawings.

Sources: `bed_details.py:18,22,23,115,119,124,164,166`. Rechecks/extends prior M01.

### BED03 — HIGH — The required full-face surfacing operation is outside the tool envelope

**Evidence:** confirmed process-envelope conflict.

The MDF support is X105.8..1044.2/Y76.5..1273.5. The nominal tool center is X175..975/Y121.4..1121.4. Required center overreach margins are 69.2 mm in X,44.9 mm at the front and 152.1 mm at the rear. Reaching a rear outside corner in this unchanged setup would require cutter radius 167.102 mm, before any spindle, clamp or guard collision check. Reface instructions also require removing and reinstalling this surface-dependent module.

**Effect:** The proposed datum-making operation cannot be completed over the whole support with normal small-router tooling in the stated setup. Unsurfaced regions would support the extrusion differently.

**Required closure:** Define a feasible machined datum process with fixture and cutter access, change the support/motion placement, or specify external machining from measured final datums. Do not claim weld and ledger errors disappear until the operation is achievable and reinstallation repeatability is checked.

Sources: `bed_details.py:18,135,138,141,210`, `motion_details.py:614,617`, `MECHANICAL-ENGINEERING.md:35,90,91`. Rechecks/extends prior M02.

### BED04 — HIGH — The selected M5 joint still loads the extrusion lips under tightening

**Evidence:** confirmed incorrect load-path claim.

The upward screw head and washer bear under the MDF; the square nut is above the bottom-slot lips at TOP+1.3. Tightening pulls that nut downward against the lips. Both the lips and MDF are in the preload path. The strength screen says the nut loads the lips only under uplift and removes the earlier tightening limit. Snug plus a quarter turn is not a quantified preload; nominal M5 × 0.8 advances0.2 mm per quarter turn.

**Effect:** Assembly preload may govern this thin-lip/MDF joint. A600 N pull test does not establish a safe uncontrolled tightening method or sustained MDF compression/creep limit.

**Required closure:** Qualify the actual extrusion/nut/washer/MDF joint for assembly preload, local uplift, shear and creep; issue a controlled fastening method and replacement/reinspection limits. Do not automatically reinstate the prior0.35 N m number without validation.

Sources: `bed_details.py:163,164,166,167,168`, `strength-screen.py:48,49,50,51,52,54`, `MECHANICAL-ENGINEERING.md:39`. Rechecks/extends prior M03.

### BED05 — HIGH — Four drawdown weldnuts have an unclosed physical attachment detail

**Evidence:** confirmed nominal separation; actual joint capacity unverified.

The ledger receives an Ø18 top-wall pocket. The modeled nut is AF13,6.5 mm tall at Z833.5..840; its maximum corner diameter is 15.011 mm, entirely inside the pocket. Fresh B-rep distance from BED_WELDNUT_1_1 to the ledger is 1.4944465 mm. It therefore has no bearing or contact with parent ledger metal in the model, while notes say weld it below the top wall. The strength screen applies an estimated 7.5 kN preload per M8 and checks only bolt/sleeve stress.

**Effect:** The welded nut is the stationary anchor for the removable bed. A gap-bridging weld may be designable, but its preparation, effective throat, load path and compatibility with the selected purchased nut are absent. This is not proof that a properly redesigned weld would fail.

**Required closure:** Detail the actual purchased weldnut, weld/bearing seat and assembly access. Use a compatible hole/seat or a designed bridge plate/boss; specify the weld and qualify local tube-wall load transfer at the chosen preload before releasing the ledger machining.

Sources: `bed_details.py:60,61,62,65,67,68,81,85`, `strength-screen.py:44,45,46`, `MECHANICAL-ENGINEERING.md:37,86`. New detail from this audit.

### BED06 — HIGH — Locator fits and receiver engagement are not manufacturing-defined

**Evidence:** confirmed missing fit definition and mislabeled receiver detail.

Two round Ø10 pins are spaced 1442.573 mm diagonally. They are to be pressed into nominal Ø10 rail bores and enter nominal Ø10.05 ledger holes. No press/sliding fit class, relative position tolerance, match-ream sequence or relieved second locator is specified. The ledger receiver is only the 3.048 mm top wall; no separate bushing is modeled or listed. A6 mm projecting pin therefore has3.048 mm actual wall engagement, not6 mm of bushing support.

**Effect:** Weld distortion, location error and relative thermal movement can prevent seating or force the rails away from their intended support. Repeatability and wear cannot be inferred from nominal CAD coordinates. This is a missing verification, not proof that a correctly match-machined two-pin assembly cannot fit.

**Required closure:** Define a datum/fit scheme, typically one round locator plus a relieved locator or an equivalently justified alternative, with actual bushings if required. Specify machining after welding, positional/height tolerances, lead-in and retention, and measure repeated install flatness.

Sources: `bed_details.py:58,62,65,74,86,87,88,89`, `MECHANICAL-ENGINEERING.md:25,37,86,87,91`. New detail from this audit.

### BED07 — MEDIUM — Nominal strip-width tolerance is not absorbed solely at free edges

**Evidence:** confirmed omission in tolerance analysis.

Documentation assumes ten butted strips each100 ±0.2 mm and says width stack is absorbed at free edges. However MDF Ø5.5 screw holes and spoilboard holes are laid out on exact 100 mm pitch, while nuts move with each bottom/top slot. Nine width increments can shift the last strip origin by ±1.8 mm relative to the fixed-hole pattern. M5-in-Ø5.5 clearance alone is only 0.25 mm radial; actual nut/slot lateral freedom must be included rather than assumed. A strip 10 pocket at X1003.5/Y676.5 ends at X1011.5, only 0.5 mm from the notch at X1012.

**Effect:** The chosen manufacturing tolerance stack can misalign fasteners or consume a notch bearing margin even after the five edge stations are corrected. The actual vendor tolerance has not been certified.

**Required closure:** Inspect the actual profile and nut, calculate the cumulative lateral fit, and define independent strip datums, compensated hole locations or designed transverse clearance without weakening bearing seats. Carry the supplier tolerance and water-guard clearance through the check.

Sources: `MECHANICAL-ENGINEERING.md:29`, `MANUFACTURING-HANDOFF.md:11`, `bed_details.py:23,24,113,115,119,124,153,155,176,177`. New detail from this audit.

### BED08 — MEDIUM — The modeled final stack omits the instructed1 mm skim

**Evidence:** confirmed dimensional inconsistency.

CAD uses two finished 12.7 mm layers fromZ895.4 to920.8, then 20 mm extrusion and 19 mm spoilboard. The process removes 1.0 mm from the top layer without initial stock allowance or compensating positions. Following that process produces support Z919.8, bare top 939.8 and spoil top 958.8, one millimeter below the nominal exported planes. A further permitted 1 mm reface changes the stack again.

**Effect:** Model workplanes, remaining screw/cavity clearance and fabrication instructions do not describe the same final condition.

**Required closure:** Separate rough and final thicknesses, define the finished support plane and remaining reface limit, and propagate those dimensions to screw lengths, nut engagement, work offsets and clearance checks.

Sources: `bed_details.py:12,18,19,135,138,164,167,193,201,202,210`, `MECHANICAL-ENGINEERING.md:17,20,21,90`. Rechecks/extends prior M06.

### BED09 — MEDIUM — The stiffness screen is not an upper bound on full machine compliance

**Evidence:** confirmed unsupported interpretation.

Fresh nominal section properties are area 612.973813 mm² and Ixx 27207.732889 mm4. The one crossmember/one strip simple-beam arithmetic gives about0.148 mm/100 N and0.74 mm/500 N, but excludes MDF local compression, contact seating, joint rotation and whole-frame/tool compliance. The screen credits strips bonded to MDF; the model specifies screws and glue only between the MDF layers. Continuous contact between unmachined rail/ledger surfaces is also an idealization, not a verified bearing condition.

**Effect:** The statement that actual displacement is substantially lower or bounded by this sum is unsupported. Static strength, stiffness, accuracy and repeatability are separate properties.

**Required closure:** Retain the member arithmetic as a limited screening result, remove unsupported bond/bound claims, establish acceptable bed-to-tool deflection, and verify the complete structural loop under representative loads and humidity/reinstallation cycles.

Sources: `strength-screen.py:27,28,32,33,37,38,39,40,43,89`, `bed_details.py:77,79,129,136`, `MECHANICAL-ENGINEERING.md:35,53,54,61,63`. Rechecks/extends prior M07.

### BED10 — MEDIUM — TEK restraint and pull-through are not qualified for the actual assembly

**Evidence:** confirmed arithmetic error; strength verification open.

A #12-14 screw has nominal pitch25.4/14=1.814286 mm; a 3.048 mm wall spans 1.68 nominal pitches, not 1.1. Effective formed engagement still depends on the selected drill point and thread geometry. The screen calls TEKs registration only, although router clamp/uplift reactions pass from strip to MDF and then require restraint to the steel ladder. Sixteen screws are modeled; their published pullout/pull-through and the glued MDF connection are not established.

**Effect:** Counting nominal wall pitches or deadweight compression does not qualify local uplift, shear, MDF crushing or preload retention.

**Required closure:** Select the exact screw and characterize its joint in the actual tube/MDF stack for pullout, head pull-through and assembly stripping, including representative local clamp loads. Correct the pitch arithmetic and retain a realistic load path.

Sources: `bed_details.py:117,118,131,142,143,144,147`, `strength-screen.py:50,52,53,54`. Rechecks/extends prior M08.

### BED11 — HIGH — The sling and support system is outside the collision and load analysis

**Evidence:** confirmed missing verification.

The saved path excludes sling legs, hook, track, anchorage and off-machine support. At 87 kg, four equal vertical reactions are 213 N each; a two-leg share is 427 N per leg before sling angle or dynamic effects. With a central hook 1.2 m above ears and roughly 815 mm horizontal corner reach, equal four-leg tension is about 258 N and two-leg tension about 516 N. End ears are plates in XZ, so fore-aft sling forces bend them out of plane. The source claim that each ear sees under 300 N assumes favorable sharing.

**Effect:** A 567 kg/87 kg ratio is a component nameplate ratio, not a complete lifting system margin. No evidence establishes the assumed winch or that it is suitable to hold a suspended bed. Rigging can also collide when the rigid module solids do not.

**Required closure:** After resolving the footprint architecture, define a lifting-rated device, support/parking mechanism, actual rigging and credible unequal sharing; verify ear/weld/anchor loads and sweep the full rigging envelope. Weigh the finished module and include an operating stability/load case.

Sources: `bed_details.py:95,98,100,102,208`, `strength-screen.py:55,56`, `swap-path-checks.py:127,129,156,159`, `MECHANICAL-ENGINEERING.md:98,100,102`. Rechecks/extends prior M10.

### BED12 — MEDIUM — Sampled positive-volume checks do not certify tolerance or continuous clearance

**Evidence:** confirmed verification limitation.

The saved path has 92 poses and 22 actual-solid checks, with source hashes matching current files. It samples the initial lift at 5 mm and translations/hoist at 25 mm, ignores intersections<=0.02 mm³ and enforces X limits only. Reported narrow nominal clearances include 7.3 mm over float backrails and 10 mm under guide shoes; no fabrication, deformation, cable or rigging envelope is included. The result is honestly labeled PASS SAMPLED PATH but cannot clear these excluded requirements.

**Effect:** Intermediate contact, protrusions or tolerance accumulation can remain undetected. A fresh identical nominal run would not close the missing physical clearances.

**Required closure:** Define and check a swept-volume or justified adaptive clearance analysis for all retained hardware and attachments, include uncertainty margins and the actual footprint, and then verify physical clearances during commissioning.

Sources: `swap-path-checks.py:49,50,91,104,113,114,127,129,139,140,141`, `MECHANICAL-ENGINEERING.md:77,96,100`. New detail from this audit.

### BED13 — MEDIUM — Lifting mass has inconsistent estimation bases

**Evidence:** confirmed bookkeeping discrepancy, not an overweight finding.

The manifest gives 87.0 kg using selected steel/MDF/aluminum solids plus 2.5 kg allowance; saved path gives 85.10 kg using all MOD_* nominal solids and material-name density mapping. The path incorrectly treats material containing fender as aluminum. Fresh component sum with the M5 fender washers treated as steel is about 85.16 kg. Neither includes real weld metal, glue, coating or measured hardware variations; no verified center of gravity is recorded.

**Effect:** The difference is small but the differing values and claimed lifting margin should not be presented as a single verified mass or load distribution.

**Required closure:** Use one explicit mass basis, correct the washer density classification, include additions/uncertainty and compute center of gravity for the selected rigging. Replace the estimate with a weighed value before use.

Sources: `bed_details.py:197,198,199,200,206,207`, `swap-path-checks.py:54,55,56,57,58,59,60`, `MECHANICAL-ENGINEERING.md:102`. New detail from this audit.

### BED14 — MEDIUM — Frame and pan support assumptions do not define a released structural rating

**Evidence:** confirmed scope gap in strength verification.

The screen assumes 650 kg gross machine mass, a 200 kg pan/slat/stock case, 200 kg tank support, 25 kg workstock and 100 N cutting force without a measured load inventory or user-approved performance target. Six feet with all pads touching do not alone prove a worst reaction of exactly one third of total weight; reactions depend on load placement, floor and frame compliance. Ideal brace buckling and simple beam checks omit welded joint behavior, frame racking, floor/anchors, dynamic cutting and tolerance-induced contact.

**Effect:** These are useful preliminary cases, but they do not certify rigidity, load capacity or accuracy for every operating configuration. Filling tubes with sand adds mass/damping rather than a demonstrated elastic stiffness increase.

**Required closure:** Define the actual mass/load envelope and performance targets; evaluate complete operating cases and load transfer through welds, feet, pan bearers and frame, then measure tool-to-bed deflection and repeatability. Keep the documented sand limitation.

Sources: `strength-screen.py:24,27,28,29,41,57,58,59,60,61,62,64,65,66,67,89`, `frame_details.py:27,33,38,40,43,53,58,67,80,97,105,106`, `MECHANICAL-ENGINEERING.md:65,67`. New detail from this audit.

## Checks that did not identify a defect

- Both MOD_RAIL instances are the same manufacturable part after end-for-end 180 degree rotation: exact symmetric difference 0mm3. Different raw local coordinates are not sufficient to declare a shared-part-number defect.
- Five 2-packs of 1220 mm20100 provide the required ten 1197 mm strips. Each loses23 mm including saw kerf; old 30 short-piece plans do not govern current Rev F.
- Both 938.4x1197 lower/upper MDF blanks fit one 1220x2440 sheet with reasonable kerf/margins by orienting 1197 across 1220 and two 938.4 lengths along 2440.
- Fresh nominal section and bed component geometry are valid CAD solids. Geometric validity is not mechanical release.

## Limits and release evidence

This audit uses nominal CAD, local source records and the visible user requirements. It does not verify actual supplier dimensions, stock/material certificates, physical welds, electrical commissioning, floor capacity, lifting hardware or machine accuracy. Historical Rev E six-cassette files must remain identifiable as superseded study geometry; the current one-piece design cannot inherit their acceptance statements.

Before manufacturing handoff: resolve the architecture/footprint, close edge fasteners and feasible datum process, define the nut/locator/tolerance joints, reconcile final machined stack, qualify the fastening/load path, and rerun whole-machine clearance and drawing checks for the corrected source. Physical validation then establishes deflection, flatness and reinstallation repeatability.

Machine-readable findings, exact source line anchors, evidence calculations and SHA-256 source hashes are in `bed-structure.json`.
