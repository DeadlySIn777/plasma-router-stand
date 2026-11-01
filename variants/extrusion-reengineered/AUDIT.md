# XR2 audit and release conditions

XR2 closes the independent mechanical details left open in XR1. It preserves
the wood/carving and steel-sheet-plasma application and the user's USD1,000
delivered cap. Pricing is paused; no complete delivered price is asserted.

The user selected full-bed ATC and authorized a different Z. Current nominal
travel is800X/1000Y/200Z. The original100Z is superseded, not silently stretched
or counted as an owned200Z. The selected nominalZXHT80-200 has preserved
primary drawings; the brake-motor provision has a separate interface gate.

## Implemented details and their evidence

| Detail | XR2 implementation | Evidence |
|---|---|---|
| Mounted guards | Formed steel guide guards, removable ledger armor, supported receiver roof, actual clips/holes/hardware | shield-check.json; shield-manufacturing.json |
| Receiver cleaning | Framed large hatch with rim-bearing metal supports, real hinges and positive open locks; brush access | service-check.json |
| Rare receiver replacement | Reversible disassembly and supported pan parking; no HGR rail removal or assumed owned hoist | service-check.json; bed_service.py |
| Plywood joinery | Separate skins and half-lapped ribs with fit clearance, operation tables and matched flat profiles | bed-manufacturing-check.json |
| Dry docking/clamping | Metal datums with controlled bedding/retention, compression sleeves, full-seat clipped fender washers | bed.py; bed-fabrication.csv |
| Slat retention/expansion | Center notches/keys limit walk; ends float; cold bearing and thermal sensitivity are recorded | bed-manufacturing-check.json |
| Pan/overflow fabrication | Separate flat wet-pan plates with a weld schedule; bolted removable overflow and supported plumbing | bed-manufacturing-check.json; water-check.json |
| Bed conversion | Entire tool module and plasma armor removed; fixed guards and parked ATC retained; complete path enclosures | transfer-check.json |
| Retractable ATC | Supported200travel mechanism, whole rail holes after trimming, hard location, endpoint retention, protected parking | atc-check.json; atc-manufacturing.json |
| Z clearance | User-authorized real200stroke replacement; preserved low datum and higher retract; conditional brake package | interface-audit.json; sources/Z200/ |
| Relative axis motion | Shared translations canceled between motion groups; three cam-following rollers bounded separately with explicit mating-cam checks | internal-continuous-check.json |
| Custom manufacturing pack | Current individual STEP solids with read-back checks; explicitly limited cross-section DXFs and transforms | custom-parts-check.json |
| CAM setup | Actual wear-pad solids, boundaries and measured-WCS instructions, with file hashes | cam-reference-check.json |
| Stock efficiency | Finite owned-plate allocation, profile nests and combined new-steel blank nests | owned-stock-check.json; profile-nesting.json; steel-nesting.json |

All evidence is bound to the current sources in package-check.json.
A green digital review covers these report scopes. It does not manufacture
supplier dimensions or qualify a complete operating machine.

## Supplier interfaces still needed before final mating drawings or orders

- Confirm the exact magazine model/CAD, retained tools, pocket/nut planes,
  mounting holes and complete end-cap/cover envelope against the ATC acceptance
  specification. Replaceable mounting blanks are defined; unpublished supplier
  holes are not invented. These are unresolved mating interfaces, not just tests.
- Confirm theZXHT80-200 base/output fixing pattern and depths, actual shaft,
  coupling and motor flange/pilot. The documented brake-motor candidate is not
  a proven drop-in replacement. Resolve those interfaces before purchasing or
  machining the mating parts; select a compatible brake/coupling combination.
- Confirm the owned X/Y modules, real travel/lead, guide/block dimensions and
  hole positions, real extrusion die/slot/core, track profile, spindle/nut and
  torch grip/nozzle. Pilot arc alone does not identify the cutter start circuit.
- Confirm all stock sizes, alloy/temper, plywood thickness/grain, adhesive
  system and actual bolt/nut grip stacks. Nominal thread bores in assembly STEP
  files are not tap-drill instructions.

The source records state exactly what the public supplier drawings establish.
No supplier was contacted or account changed. Do not substitute an old cart,
a dimension inferred from a photo, or a previous variant's hole pattern.

## Physical acceptance before commissioning

1. Square and align the actual guides and profile seats under final tightening.
   Verify screw engagement, tip clearance, washer seating and access at every
   joint. Check100N framework/bed response in both directions on all axes,
   then measure the complete tool-to-work loop separately. The0.30mm target
   is not a measured pass. Select any proof load from the real allowables.
2. Measure fixed/moving masses and CGs, level all eight feet and check dry
   sliding/tipping at extreme poses. No receiver water or freestanding cabinet
   is credited as attached ballast. Check joint slip and dynamic response.
3. Verify brake hold, release/engage sequence, loss-of-power motion and dynamic
   stopping with the actual Z/motor/coupler. A static2Nm brake rating alone does
   not qualify the assembly or its electrical control.
4. Cold-test pan leaks, drain/overflow throughput, receiver useful capacity and
   service connections. Verify the selected tote's actual rim, liquid load
   and thermal suitability. Keep the reservoir atmospheric.
5. Trial cassette conversion and rare service with final hoses, guards, ATC,
   measured weights, handling tools and restraints. CAD separation does not
   establish hand clearance, reach or a rated lifting/support system.
6. Clean out wood dust and qualify protected wood, receiver, hoses and guide
   temperatures during representative plasma duty. Nonsealed guards are not
   a fume-extraction system.
7. Verify the real cutter's isolated start/arc interfaces, bonding/work return,
   touch-off/breakaway and EMI behavior. Verify ATC docking repeatability,
   loaded pocket alignment, tool sensing and spindle/VFD sequence before
   enabling automatic tool changes.

## Calculation limits

The elastic reports are closed-form component sensitivities, not assembled
frame FEA. The half-lap calculation assumes composite coupling across the
notched grid and omits local notch/Vierendeel/adhesive transfer compliance.
Its unnotched glue demand is not peak joint stress. Actual profile lips,
contacts, fasteners, glue durability, thermal distortion and the owned motion
stack remain outside a claimed complete rigidity qualification.

The modeled ATC stock/clamp and retained-tool envelopes are limits of the
checked case, not unlimited stock height or verified supplier tooling.
No posted G-code or successful automaticM6 cycle is asserted. This lightweight
variant is not qualified for steel milling. The4x8 remains separate work.
