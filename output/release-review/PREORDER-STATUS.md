# CNC / plasma build — pre-order review

**Historical Rev D review. Rev E engineering work supersedes this review's geometry and implementation status.** Active mechanical files are in [RevE-ENGINEERING](RevE-ENGINEERING/). The [Kraken firmware package](../../RevE-ENGINEERING/controls/README.md) has been implemented and compiled. The earlier $5,745 figure below remains a historical planning allowance; it does not include all changes in Rev E. This file preserves the findings that prompted the redesign.

Reviewed 24 September 2026. **NOT RELEASED FOR PURCHASE, FABRICATION OR CAM.**

The user's requirement is a checked design before ordering any parts. The previous five-pack extrusion recommendation was a stock-yield and price calculation, not approval of the machine design. Existing concept PDFs, renders and the older BOM must not be used as manufacturing instructions or a final shopping list.

## Current result

The 800 mm X / dual 1000 mm Y / 100 mm Z arrangement remains a design target. Several purchased-part interfaces and the router/plasma controller configuration are unresolved. A new Rev D solid model is a fit study only. Its STEP format does not establish manufacturing readiness.

## Work completed in this review

- Created [reproducible CadQuery solid geometry](RevD-STUDY/build_revd_study.py) and three STEP study exports in RevD-STUDY/step: assembled bare extrusion (132 solids), assembled with optional MDF (138), and stowed with optional MDF (138). Nominal steel tubes are hollow, and the pan floor now has the specified 1% slope.
- All represented solids passed CAD validity checks. Export/reimport checks preserved solid counts, bounds and volumes. No positive-volume intersections above 0.01 mm³ were found among represented static components; the modeled parked beams and panels fit the defined storage box.
- These checks omit the motion assembly, tool movement, swap movement, final clamps/fasteners, pan cradle and other unresolved components. Missing supports or clamps are not counted as completed designs merely because removing them removes an intersection. The detailed validation and part-specific limitations are in RevD-STUDY/validation.json and manifest.json.
- Located dimensioned images on the exact Z-module Amazon listing. They improve the known outer envelope but do not completely specify its carriage mounting holes. Supplier-dependent interfaces remain held.
- Marked the older procurement brief as superseded in design basis so its costs and hardware are not mistaken for a released shopping list.

### Findings that can change the purchases

1. **Motion module qualification is incomplete.** KHMOS's HMS40 page gives 10 mm-lead payload figures of 20 kg horizontal and 10 kg vertical, and moment figures MY=13, MP=12, MR=15 N·m. These are not a tool-point stiffness specification. An illustrative 100 N lateral force acting 250 mm from a carriage produces 25 N·m; 50 N produces 12.5 N·m, before applicable gravity and acceleration moments. This does not prove the proposed cut will apply either force, but it prevents approving a long router overhang from the payload figure alone. Exact geometry, mass, axis orientation, combined-load interpretation and supplier ratings are needed. The single X carriage and both Y carriages must be checked, including asymmetric reactions at the X travel limits. Source: https://www.khmos.com/high-performance-easy-access/hms40 . A read-only HTML snapshot is in sources/khmos-hms40.html; the site's technical images returned access errors.

2. **Neither chosen printer motherboard has a verified complete live-THC configuration.** Kraken and Manta M5P remain hardware candidates. Ordinary motion support is insufficient to approve coordinated plasma height control, anti-dive, Arc OK, torch-start isolation and fault behavior. See motion-firmware-gate.md and its pinned primary references. No substitute motherboard or external driver has been silently selected.

3. **The bed change is a mechanical redesign.** Ten nominal 1220 mm sticks can yield thirty 397 mm pieces. Five pieces per cassette give six nominal 500 × 397 mm cassettes; three-millimetre seams give a 1003 × 1197 mm deck. This is stock arithmetic, not a tolerance or flatness guarantee. Existing drawing clamps intersect the panel corners. The current study removes those placeholder clamp solids and marks the actual clamping design unresolved.

4. **Bed height and the tool change need a consistent stack.** The new fit-study candidate seats the 20 mm extrusion directly on the 920.8 mm beam plane. Six-millimetre underside joining strips sit between the beam contact zones. Bare deck top is 940.8 mm; a nominal 19 mm spoilboard gives 959.8 mm. This replaces the old 25 mm cassette frame; it is not the old frame with thicker material stacked on top. Do not mix the two designs. The plasma slat plane is 850 mm, so the two work planes differ by 109.8 mm with spoilboard. Separate indexed tool mounting positions, actual tool gauge lengths, stock thickness and safe retract positions must be checked. Nominal 100 mm Z travel is not proof that both modes fit.

5. **Storage has a feasible nominal orientation, but the full swap is unverified.** Store each cassette 397 mm across, 500 mm tall, with its thickness along cabinet depth. Thus two banks do not consume 1000 mm of cabinet width. The unmodeled handles, fasteners, retainers, beam parking and insertion path remain to be checked. The requirement is a swap within the machine footprint. Final parked positions alone do not prove the insertion/removal path stays within it. Existing 1150 mm width is chassis steel only; gantry, rail caps and other overhangs must be included in the final overall envelope.

6. **The water system is not detailed.** Pan floor slope, cradle contacts, slat capture, drain/overflow holes, cleanouts, reservoir capacity and service access require actual parts and joints. The new study can model the slope but does not release sheet developments or the fluid circuit. A pump/vented-reservoir allowance is used only for the lean budget below. The compressed-air displacement alternative needs its own specified chamber, low-pressure controls and cost; a vented tank is not to be sealed and substituted as a pressure chamber. The owned CV-15HS remains a vacuum generator, not an assumed dirty-water pump.

7. **Supplier interfaces are not defined for fabrication.** Exact HMS40 and ZBX80 mounting drawings, spindle-clamp footprint, torch dimensions, extrusion slot cavity/T-nut engagement and actual receiver hardware are needed. The previous render used a generic spindle envelope, not the selected kit's complete body and clamp. Hole patterns will not be inferred from perspective pictures or unrelated module variants.

## Lean budget — estimate, not a quote

USD, delivery destination Alto GA 30510. Most rows are planning allowances. Shipping is a reserve, not a carrier quotation. This replaces neither the old workbook nor a released bill of materials.

| Assembly | Budget USD |
|---|---:|
| Four motion modules, advertised prices | 868 |
| Chassis, bracing, feet, finish, skins and internal storage | 1,096 |
| Gantry beam and mounts | 300 |
| Six extrusion cassettes, joining/support parts, MDF and ordinary clamps | 795 |
| Kraken-based controls and electrical hardware provisions | 861 |
| Spindle and basic routing accessories | 455 |
| Torch mount and isolated interface provision | 135 |
| Pan, slats and DIY vented reservoir material allowance | 400 |
| Automatic water hardware, pump-based allowance | 360 |
| Fabrication consumables and limited services | 175 |
| Unquoted shipping reserve | 300 |
| **Provisional total before tax** | **5,745** |

The extrusion component within the $795 bed allowance is $399.95: five two-packs at $79.99, advertised free delivery. It is not added twice. Source: https://www.amazon.com/dp/B0BXNWK99C . Motion prices and the $309.99 spindle kit were checked earlier on this review date; see ../bom/motion_research.json and ../../outputs/alto-30510/bom-data.json. The spindle price includes its VFD and clamp. Controller provisions are conditional on the unresolved firmware decision.

This budget excludes sales tax, paid fabrication labor beyond the limited allowance, new plasma cutter/compressor, shop dust/fume extraction, paid CAD/CAM software and the unresolved firmware-development work. Structural changes or different motion hardware would change the total. It is not a guaranteed complete operational-machine price. The older workbook's roughly $9,114 pump-route figure describes the former design and is not this estimate.

## Conditions for release

- Confirm intended stock thickness, use case and fabrication process. Set measurable machine accuracy, repeatability, tool-point deflection, payload and speed criteria; verify they match this budget and selected modules.
- Fix exact purchased variants and obtain revision-matched dimensions, load data and electrical interfaces. Close every supplier-dependent mounting dimension before generating adapter holes.
- Model all load-carrying parts, joints, clamps and fasteners. Check access, seating, tolerances, weld distortion allowances, rail alignment and adjustment. Evaluate structure and carriage moments for the defined load cases; an attractive render or frame-only deflection calculation is insufficient.
- Check full X/Y/Z movement, both tools, intended stock, homing and retract margins, cables/hoses, mode-change sequence and stowage paths against the complete machine envelope.
- Validate the selected controller firmware and isolated plasma interface as an exact configuration. Document independent Y homing, E-stop, spindle/torch isolation, power-loss behavior and water interlocks. Establish a commissioning test plan; computer checks cannot replace later physical acceptance tests.
- Produce a matched revision of assembly STEP, individual manufactured parts, process-appropriate DXFs, dimensioned drawings, material specifications, tolerances, weld/joint details, cut list, fastener schedule, wiring/fluid schematics and BOM. Reopen exports and compare dimensions/part counts against the source model.
- Generate machine-specific CAM only after the fabrication machine, tooling, workholding and postprocessor are known. Simulate and review toolpaths. No generic G-code is to be represented as ready to run.
- Reprice the released BOM, identify owned equipment, and verify shipping and tax. Only then issue the purchasing list.

## Missing user inputs requested

Exact owned plasma cutter model; whether plates/frame are DIY or shop-fabricated; maximum wood/plastic stock thickness. Questions have been sent in the task. Neutral STEP and DXF formats are the default unless a native CAD format is specified later.

No purchases or supplier messages have been made.
