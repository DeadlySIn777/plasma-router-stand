# Rev H completion work - 26 September 2026

This revision makes concrete changes to the bed, water service and motion definitions. **It does not finish the entire machine.** The remaining items include actual purchased mating dimensions, a complete plasma head, full rigidity/load qualification and electrical/plumbing integration.

## Current artifacts

- [Rev H CAD package](../release-review/RevH-CAD/README.md)
- [Concept PDF](../pdf/plasma-router-stand-concept.pdf)
- [Scrap tube shopping guide](SCRAP-TUBE-GUIDE.md)
- [Confirmed owner inputs](USER-INPUTS.md)
- [X/Y lead and controller scale check](CONTROL-SCALE-CHECK.md)
- [Motion order/interface decisions](motion/ORDER-AND-INTERFACES.md) and [arrival measurement record](motion/ARRIVAL-MEASUREMENTS.md)
- [Bed changes and handling instructions](bed/README.md)
- [Water changes and exact service scope](water/README.md)

## What changed

| Area | Concrete Rev H change | Remaining limitation |
|---|---|---|
| Bed top-slot nuts | Twelve retained strips replace 24 loose nuts | Actual extrusion fit, thread engagement and controlled preload need qualification |
| Stored beams | Four through-bolts and eight welded compression sleeves tie the beam stacks to their shelves | Restraint/weld/rack load capacity and actual access are unqualified |
| Panel/spoilboard storage | Removable panel retainers and an indexed folding spoilboard guard | Follow the phase-specific conversion sequence; physical fit and handling still need demonstration |
| Temporary beam parking | Two boxed keepers locate the first beam on the second during front-seat work | Contains the nominal stack; not a rated lifting fixture |
| Reservoir access | Two service hatches, seals, fasteners, cover parking and a real washout closure | Full cleaning reach, loose-fastener handling and wet testing remain |
| Refill path | Defined fabricated spout, pan penetration and support; 30 mm nominal air gap | Pump/valve ports, adapters, supported hoses and actual clearance remain unresolved |
| Z adapter | Known tool-side holes retained; fictitious output slots removed | Output height, four-hole pattern, thread/depth and attachment capacity remain unverified |
| Z power-off holding | A sourced braked-motor candidate is reserved and statically screened | Coupling/flange fit, dynamic response and complete load-path qualification remain open |

The selected X and Y catalog variants both specify **10 mm lead**. The user has ordered Y; X and Z are planned for Monday. The exact catalog checks do not inspect the order or delivered hardware. Firmware's existing X/Y scale calculation already uses 10 mm lead; no firmware was changed or flashed.

## Verification records

- [Combined evidence acceptance index](ACCEPTANCE.md)
- [Integrated assemblies, shared parts and nine router poses](verification.json)
- [Independent final STEP readback](step-verification.json)
- [Export inventory and material-layout verification](package-verification.json)
- [Integrated hatch and washout service paths](water/integrated-verification.json)
- Bed route and restraint evidence is linked from the bed report; original Rev G proofs are retained as historical records.

The final source-matching verification index passes. Both assemblies contain 1,448 valid solids with zero unresolved intersections; all nine checked router poses pass. The continuous proofs include 121 original board/panel/beam segments, 86 added restraint segments, 20 temporary-keeper transfer segments and 10 water-service segments. The two final keeper insertion segments repeat checks in the restraint report. Both final STEP files were independently reimported and matched to their recorded hashes, counts and volumes.

The export inventory contains 331 part numbers, 242 unguarded individual STEP files and 134 flat DXFs, with no missing or stale individual files. Nominal dry panel mass is approximately 4.00 kg each including retained strips and screws, excluding separate spoilboards and work; weigh actual panels. The four-page concept PDF was rendered and all pages visually reviewed.

Read each report's `status`, source hashes and scope. Static clearances are nominal. Continuous handling checks cover the stated solids and preconditions; they do not model the operator, flexible leads, manufacturing error or structural deformation. Valid files and clear paths do not establish a safe or accurate cutting machine.

## What still prevents a finished CAD/CAM handoff

1. Measure the arriving Y interfaces and obtain or measure the selected Z output interface. The current source identifies each required datum; the adapter stays guarded until those values exist.
2. Measure the owned torch and identify the exact VIV ARC CUT-50 version/interface. Its floating touch-off, breakaway and lead routing are still unfinished. A generic AG-60 product picture cannot finish this geometry or wiring.
3. Establish actual scrap lengths, remaining wall/condition and usable aluminum inventory. Qualify the complete frame-to-tool-to-bed load path and repeat installation behavior; sand adds mass, not elastic stiffness.
4. Finish purchased plumbing fit, hose support, cable chains/way covers, enclosure door/thermal layout, wiring and physical interlock/brake tests.

The 2 x 2 tube schedule remains 30 blanks, 29,472 mm net. Actual scrap prices and yields are not yet known. Historical cost workbooks are not a current delivered build total. The public repository contains review work, not an instruction to order every listed item or execute every DXF as a through cut.

No vendor messages, purchases, controller flashing or machine operation occurred in this work. The old 29-finding audit remains unchanged; these new artifacts do not retrospectively relabel its findings as closed.
