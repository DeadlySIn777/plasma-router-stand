# Plasma / router CNC stand

Public working design for **800 mm X / 1000 mm Y / 100 mm Z nominal travel**.

**Current revision: Rev G corrected working CAD. It is not a finished, fabrication-ready or operational plasma machine.** The historical Rev F hoisted bed failed the required within-footprint conversion. Rev G replaces it with six small panels, four beams and separate spoilboards stored inside the frame. Manual handling is the working assumption; it is not recorded as an owner-approved preference.

## Open the current design

- [Current CAD package and limitations](output/release-review/RevG-CAD/README.md)
- [Router assembly STEP](output/release-review/RevG-CAD/step/RevG_ROUTER.step)
- [Bed stored assembly STEP](output/release-review/RevG-CAD/step/RevG_BED_STORED.step) — storage layout, with no invented plasma head
- [Updated concept PDF](output/pdf/plasma-router-stand-concept.pdf)
- [Repair evidence and finding-by-finding status](output/cad-repair-2026-09-25/README.md)
- [Current component schedule](output/release-review/RevG-CAD/cutlist.csv)

![Current router CAD](output/release-review/RevG-CAD/previews/RevG_ROUTER.png)

## What changed

The ten purchased 1220 mm extrusion bars yield thirty 397 mm strips, assembled into six 500 x 397 mm panels. Full bearing seats, beam compression sleeves, round/relieved locators, supported aluminum ties, separate reachable spoilboards and internal racks replace the one-piece module. The front seats unbolt after the first beam is independently parked, opening a path for the four beams to lower inside the frame. Loose spoilboard nuts are removed before any panel rotates.

The revision also corrects adapter slot orientation, cabinet stringer bores, the two-piece welded drip shield and drained-level guard clearance. Unknown Z-carriage fastening and defective legacy torch clamps are guarded; the model no longer supplies guessed M6 carriage bolts or calls the stored-bed view an operating plasma setup.

Nominal CAD and path checks do not establish whole-machine stiffness, joint capacity, actual interface compatibility, operator access, physical retention or machining accuracy. See the current evidence for exact scope and limits. The **VIV ARC CUT-50** identification still needs exact version/interface information; an AG-60 listing does not identify the owner's actual torch geometry or starting circuitry.

## Sources, history and cost

The active generator is [build_revg.py](output/release-review/RevE-ENGINEERING/build_revg.py). Shared Python sources remain in the legacy-named directory for reproducibility; **current exports are only in RevG-CAD**. The [29-finding audit](output/cad-reaudit-2026-09-25/README.md) and old Rev E/F exports are historical evidence. They have not been relabeled as the new design.

[Earlier price workbook](outputs/reve-30510/CNC-plasma-RevE-budget.xlsx) and [actual-price audit](outputs/reve-30510/actual-cost/REAL-COST.md) are historical procurement research. Quantities changed in Rev G; neither is a current complete build total. No purchase, vendor message, hardware flashing or manufacturing release occurred.

CadQuery/OpenCascade generate the model; ReportLab generates the concept brief. Runtime paths are local Windows paths. A clean-machine rebuild and Fusion import have not been certified. [Controller work](RevE-ENGINEERING/controls/) is a separate prototype and was not redesigned or deployed with this mechanical repair.

The [original snapshot manifest](REPOSITORY-SNAPSHOT.json) describes the initial import only. Third-party sources retain their existing license notices; this repository grants no new rights over supplier material.
