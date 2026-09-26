# Plasma / router CNC stand

Public working design for **800 mm X / 1000 mm Y / 100 mm Z nominal travel**.

**Current revision: Rev H integrated working CAD. It is not a finished, fabrication-ready or operational plasma machine.** Six removable panels, four beams and separate spoilboards store inside the frame. Rev H adds captive bed hardware, storage restraints and reservoir service details. Manual handling remains the working assumption; it is not recorded as an owner-approved preference.

## Open the current design

- [Current CAD package and limitations](output/release-review/RevH-CAD/README.md)
- [Router assembly STEP](output/release-review/RevH-CAD/step/RevH_ROUTER.step)
- [Bed stored assembly STEP](output/release-review/RevH-CAD/step/RevH_BED_STORED.step) — storage layout, with no invented plasma head
- [Updated concept PDF](output/pdf/plasma-router-stand-concept.pdf)
- [Current changes, evidence and remaining work](output/design-completion-2026-09-26/README.md)
- [Verification index](output/design-completion-2026-09-26/ACCEPTANCE.md)
- [Current component schedule](output/release-review/RevH-CAD/cutlist.csv)
- [Scrap tube lengths and inspection inputs](output/design-completion-2026-09-26/SCRAP-TUBE-GUIDE.md)
- [X/Y lead check and arrival measurements](output/design-completion-2026-09-26/CONTROL-SCALE-CHECK.md)

![Current router CAD](output/release-review/RevH-CAD/previews/RevH_ROUTER.png)

## What changed

Ten selected 1220 mm extrusion bars yield thirty 397 mm strips, assembled into six 500 x 397 mm panels. Twelve retained nut strips eliminate retrieval of 24 loose spoilboard nuts. Defined panel retainers, a folding spoilboard guard, sleeved beam-stack locks and two temporary boxed keepers add restraint geometry. The top bars and rods move separately along the checked routes. The original 52 release fasteners remain, with additional restraint operations; this is not a quick or automatic changer.

Two gasketed reservoir hatches have internal cover-parking pockets, and the washout now has a bolted flange and closure. A fabricated refill pipe and stay define its path and air gap. The Z adapter is a transfer-drill blank with known tool-side holes; unpublished carriage holes are omitted. An optional braked-motor candidate has a sourced envelope and static rating, with fit and stopping behavior still unqualified.

The selected X and Y catalog variants both specify **10 mm lead**, meaning travel per screw revolution, not screw diameter. Verify the delivered modules before final calibration. The 2 x 2 tube schedule remains 30 blanks totaling 29,472 mm (96.69 ft) net; actual scrap lengths and remaining wall still need recording.

Nominal CAD and path checks do not establish whole-machine stiffness, joint capacity, actual interface compatibility, operator access, physical retention or machining accuracy. See the current evidence for exact scope and limits. The **VIV ARC CUT-50** identification still needs exact version/interface information; an AG-60 listing does not identify the owner's actual torch geometry or starting circuitry.

## Sources, history and cost

The active generator is [build_revh.py](output/release-review/RevE-ENGINEERING/build_revh.py). Shared Python sources remain in the legacy-named directory for reproducibility; **current exports are only in RevH-CAD**. The [29-finding audit](output/cad-reaudit-2026-09-25/README.md), [Rev G repair evidence](output/cad-repair-2026-09-25/README.md) and older exports are historical evidence. They have not been relabeled as the new design. The Rev H manifest explicitly separates historical baseline metadata from current completion details.

[Earlier price workbook](outputs/reve-30510/CNC-plasma-RevE-budget.xlsx) and [actual-price audit](outputs/reve-30510/actual-cost/REAL-COST.md) are historical procurement research. Quantities changed; neither is a current complete build total. No purchase, vendor message, hardware flashing or manufacturing release occurred.

CadQuery/OpenCascade generate the model; ReportLab generates the concept brief. Runtime paths are local Windows paths. A clean-machine rebuild and Fusion import have not been certified. [Controller work](RevE-ENGINEERING/controls/) is a separate prototype and was not redesigned or deployed with this mechanical repair.

The [original snapshot manifest](REPOSITORY-SNAPSHOT.json) describes the initial import only. Third-party sources retain their existing license notices; this repository grants no new rights over supplier material.
