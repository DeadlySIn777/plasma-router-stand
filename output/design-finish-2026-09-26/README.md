# Rev I design repairs — 26 September 2026

Rev I adds a guided floating/breakaway head, stronger storage restraints,
supported plumbing with service paths, and defined water/tool control circuits
to the frozen Rev H design. It is a working engineering package, **not a
finished fabrication or operating-machine release**.

The current [verification index](ACCEPTANCE.md) identifies the source-matching
reports. An intermediate report marked failed or stale is diagnostic history,
not acceptance. Read the index before using counts or pass claims below.

## Current design

- [CAD package](../release-review/RevI-CAD/README.md), including router, stored-bed and plasma-head-hardware assemblies.
- [Updated concept PDF](../pdf/plasma-router-stand-concept.pdf).
- [Original findings and current disposition](FINDING-DISPOSITION.md).
- [Remaining engineering and measured inputs](OPEN-ITEMS.md).
- [Structural joints and load targets](structure/JOINTS.md).
- [Head mechanism, transfer sequence and limitations](motion/README.md).
- [Combined bed and tool conversion sequence](motion/CONVERSION-SEQUENCE.md).
- [Water/cabinet geometry and servicing](service/README.md).
- [Kraken control baseline and terminal circuits](controls/README.md).
- [Isolated float-probe and breakaway interfaces](controls/HEAD-INTERFACE.md).
- [Current part inventory and material layouts](../release-review/RevI-CAD/cutlist.csv).
- [Arrival measurement worksheet](../design-completion-2026-09-26/motion/ARRIVAL-MEASUREMENTS.md) and [scrap tube guide](../design-completion-2026-09-26/SCRAP-TUBE-GUIDE.md).

## Changes and their purpose

| Area | Corrected definition | Remaining physical limit |
|---|---|---|
| Head mechanism | Twin guides, captured 6 mm float, cone/V/flat magnetic release, switch cams, machined clamp halves and internal parking | Actual torch bore/nozzle, cable and tether, probing/release forces and tilted separation remain unqualified |
| Storage restraints | Ø14 rods, 40 mm sockets, thicker seats, defined engagement and revised transfer heights | These contain stored parts; they are not rated lifting hardware |
| Bed rigidity and joints | Actual extrusion section, member/joint calculations, explicit force targets and slot-lip coupon procedure | Purchased motion compliance and full tool-to-work stiffness cannot be inferred from isolated beams |
| Drain and filter service | Supported reducer/flange, removable tail with parking cup, removable strainer bridges and supported hoses | Actual purchased port makeup and end-fitting stacks require receipt fit and wet testing |
| Cabinet | Correct 500 × 400 × 200 mm nominal body, backplate, gland covers and drilled supports | Purchased hinge/lock/standoffs and a complete populated/thermal panel remain unfinished |
| Controls | Actual relay poles/terminals, timed water circuit, isolated run request, release-to-rearm behavior and selected speed conversion | Hardware stop/power/brake integration and the identified cutter interface remain separate unfinished work |

The manual conversion keeps the six panels, four beams, separate spoilboards
and storage hardware inside the chassis. It retains 52 primary release
fasteners plus restraint/tool operations; it is not an automatic or quick bed
changer. The structure and head reports define the additional handling steps.

The bare deck is 1003 × 1211 mm. Ten 1220 mm extrusion bars supply thirty
397 mm pieces: five two-packs, not five individual bars. Six separate
spoilboards sit within the nominal router center envelope. Cutting access
still depends on the actual tool, guards and clamping.

X/Y catalog lead remains **10 mm per screw revolution**; Z is specified as
SFU1605 / 5 mm lead. Travel, screw diameter and lead are different dimensions.
The arriving modules still need measured mating datums before adapter holes
can become manufacturing definitions.

The 2 × 2 tube list remains 30 blanks, 29,472 mm / 96.69 ft net. The model uses
3.048 mm wall. Random scrap requires its own sound-length nest and wall/condition
record. Sand adds stationary mass; no calculation credits it with elastic
stiffness. Owned aluminum quantity and alloy remain unverified.

## How to reproduce the current evidence

CAD uses CadQuery 2.7/OpenCascade and ezdxf. From the repository root:

```text
python output/release-review/RevE-ENGINEERING/build_revi.py
python output/design-finish-2026-09-26/verify_revi.py
python output/design-finish-2026-09-26/verify_revi.py --steps-only
python output/design-finish-2026-09-26/verify_revi_routes.py
python output/design-finish-2026-09-26/structure/calculate_structure.py --integrated
python output/design-finish-2026-09-26/structure/check_reinforced_paths.py --integrated
python output/design-finish-2026-09-26/structure/check_temp_fixture_transfer.py --integrated
python output/design-finish-2026-09-26/service/verify_service_finish.py --builder build_revi
python output/design-finish-2026-09-26/motion/verify_motion_finish.py
python output/design-finish-2026-09-26/motion/verify_motion_finish.py --integrated --builder build_revi
python output/design-finish-2026-09-26/motion/verify_head_package.py
python output/design-finish-2026-09-26/motion/check_transfer_staging.py
python output/design-finish-2026-09-26/motion/check_router_transfer.py
python output/design-finish-2026-09-26/motion/check_conversion_prerequisites.py
python output/design-finish-2026-09-26/controls/verify_circuit.py
python output/design-finish-2026-09-26/controls/verify_run_interface.py
python output/design-finish-2026-09-26/controls/verify_head_interface.py
python package_revi.py
python output/release-review/RevE-ENGINEERING/render_revi.py
python output/design-finish-2026-09-26/render_head_detail.py
python build_concept_revi.py
python output/design-finish-2026-09-26/final_acceptance.py
```

Do not change source files during these runs. Each report binds its actual
inputs; an old pass does not qualify a modified part. Rendering needs NumPy,
Pillow and the repository renderer; the PDF additionally needs ReportLab,
pypdf and the recorded Windows fonts. Review the rendered PDF before copying
it to the stable concept path. This documents the local build, not a certified
clean-machine environment or native Fusion feature history.

Previous audits, revisions and cost workbooks are preserved as history.
Earlier quantities and prices are not a delivered Rev I build total. No
manufacturing G-code, purchase, supplier message, controller flash, live motion
or cutting operation is part of this revision.
