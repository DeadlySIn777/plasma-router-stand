# GM1 — Garcia Mechanical Table

Plasma and router CNC table. Public working design for **800 mm X / 1000 mm Y / 100 mm Z nominal travel**.

**Current revision: GM1 Rev J working CAD (26 September 2026). It is not a finished, fabrication-ready or operational plasma machine.** Rev J meets the owner's bed requirement: one waterproof bed module of about 63 kg (galvanized steel, aluminum T-slot, HDPE top, no MDF). Six M10 screws hold it down, and an overhead beam-and-trolley hoist lifts it out of the front of the machine for plasma work. Rev J also carries the reservoir service hatches, washout closure, refill spout and Z-adapter blank from the base branch's Rev H (26 September, the owner's other session), with the spout moved clear of the module. That Rev H keeps the in-footprint six-panel bed; it and Rev G stay documented as the alternative. This design was first published on this branch as "Rev H" and was renamed Rev J so the two designs don't share a name.

## Open the current design

- [Rev J CAD package: the bed module, how to change beds, what was checked](output/release-review/RevJ-CAD/README.md)
- [Router assembly STEP](output/release-review/RevJ-CAD/step/RevJ_ROUTER.step); [plasma layout with the module out](output/release-review/RevJ-CAD/step/RevJ_PLASMA_LAYOUT.step) (no invented plasma head); [bed module alone](output/release-review/RevJ-CAD/step/RevJ_BED_MODULE.step)
- [Current component schedule](output/release-review/RevJ-CAD/cutlist.csv); [what Rev J changes in the shopping list](outputs/reve-30510/actual-cost/REVJ-PROCUREMENT-DELTA.md)
- [Drive modules, receiving check](output/receiving/MOTION-MODULES.md): Y modules ordered; X and Z to be ordered Monday 28 Sep (please confirm); [HGR20 guide rails (still to order): receiving check and Y-rail cut planner](output/receiving/HGR20-RAIL-KITS.md)
- [26 Sep follow-up: owner decisions, procurement, open controls findings and what is left to finish](output/followup-2026-09-26/README.md)
- Six-panel alternative, Rev H (other session, 26 September): [CAD package](output/release-review/RevH-CAD/README.md), [completion report](output/design-completion-2026-09-26/README.md), [verification index](output/design-completion-2026-09-26/ACCEPTANCE.md), [scrap tube guide](output/design-completion-2026-09-26/SCRAP-TUBE-GUIDE.md) and [X/Y lead check](output/design-completion-2026-09-26/CONTROL-SCALE-CHECK.md). The [concept PDF](output/pdf/plasma-router-stand-concept.pdf) shows this Rev H.
- Earlier revision: [Rev G CAD package](output/release-review/RevG-CAD/README.md) and [repair evidence](output/cad-repair-2026-09-25/README.md).

![GM1 Rev J router CAD](output/release-review/RevJ-CAD/previews/RevJ_ROUTER.png)

## What changed

**Rev J: the bed.** Nine cut-only 1197 mm 20100 profiles sit on a welded 2 × 2 steel frame, topped by two HDPE plates that the machine surfaces in place. Six seat pads and sealed M10 sleeves in the ledgers take the six drawdowns, and two pins locate the module. For plasma, it lifts 70 mm in place, so every part passes above the pan floats, then travels 1.42 m forward out of the front window on the hoist. That path was checked with the sling modeled, at three hook heights, with the gantry parked at the rear. Rev G's storage racks and slat end reliefs are gone.

**From the base branch's Rev H:** two gasketed reservoir hatches with upright cover parking, a bolted washout flange and cover, drain space reserves, a welded NPS 1/2 refill spout with a 30 mm air gap, a Z-adapter transfer blank and a braked Z-motor candidate envelope. Rev J moves the refill riser from Y1255 to Y1215.4 because the module's rear crossmember stands over the original spot, and sets the module's end crossmembers and deck 15 mm rearward for clearance. Static, nine-pose motion, hoist-path and water-service checks all pass on the combined model.

Rev G, which Rev J keeps apart from the bed, also corrected adapter slot orientation, cabinet stringer bores, the two-piece welded drip shield and drained-level guard clearance. Unknown Z-carriage fastening and defective legacy torch clamps are guarded; the model does not supply guessed M6 carriage bolts or call a bed-out layout an operating plasma setup.

Nominal CAD and path checks do not establish whole-machine stiffness, joint capacity, actual interface compatibility, operator access, physical retention or machining accuracy. See the current evidence for exact scope and limits. The **VIV ARC CUT-50** identification still needs exact version/interface information; an AG-60 listing does not identify the owner's actual torch geometry or starting circuitry.

## Sources, history and cost

The active generator is [build_revj.py](output/release-review/RevE-ENGINEERING/build_revj.py), with the bed in [bed_revj.py](output/release-review/RevE-ENGINEERING/bed_revj.py) and the water service in [water_revj.py](output/release-review/RevE-ENGINEERING/water_revj.py). Shared Python sources remain in the legacy-named directory for reproducibility; **current exports are only in RevJ-CAD**, RevH-CAD holds the six-panel Rev H from build_revh.py and RevG-CAD the earlier Rev G. The [29-finding audit](output/cad-reaudit-2026-09-25/README.md) and old Rev E/F exports are historical evidence. They have not been relabeled as the new design.

The [actual-price audit](outputs/reve-30510/actual-cost/REAL-COST.md) was re-baselined to Rev J on 26 September 2026: **$5,336.10** priced, with 51 required entries still unpriced. It is a partial register, not a complete build total ([Rev J procurement delta](outputs/reve-30510/actual-cost/REVJ-PROCUREMENT-DELTA.md)). The [earlier price workbook](outputs/reve-30510/CNC-plasma-RevE-budget.xlsx) has not been rebuilt and still shows Rev E quantities. Apart from the owner's drive-module order (the two Y HMS40 modules, 26 September; X and Z to follow on 28 September), no purchase, vendor message, hardware flashing or manufacturing release is recorded. The owner chose the BTT Rodent controller on 26 September; the Kraken firmware in `RevE-ENGINEERING/controls/` is now a reference and fallback.

CadQuery/OpenCascade generate the model; ReportLab generates the concept brief. Runtime paths are local Windows paths. A clean-machine rebuild and Fusion import have not been certified. [Controller work](RevE-ENGINEERING/controls/) is the Kraken prototype; the owner has since chosen the BTT Rodent, whose port is not written yet.

The [original snapshot manifest](REPOSITORY-SNAPSHOT.json) describes the initial import only. Third-party sources retain their existing license notices; this repository grants no new rights over supplier material.
