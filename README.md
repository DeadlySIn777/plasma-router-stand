# Plasma / router CNC stand

Public working design for **800 mm X / 1000 mm Y / 100 mm Z nominal travel**.

**Current revision: Rev I.** It adds a floating/breakaway head mechanism,
stronger storage restraints, supported plumbing and defined water/tool control
circuits. It is still an engineering design with open measured interfaces and
integration work, **not a fabrication-ready or operational machine**.

**New development variants:** [small-machine RapidChange ATC, a full-sheet 4x8
machine, and repeatable removable table interfaces](variants/README.md). These
have their own CAD and checks. Their supplier interfaces and physical
qualification remain open; they do not replace or inherit the Rev I release status.

## Open the current design

- [Current CAD package and limitations](output/release-review/RevI-CAD/README.md)
- [Router assembly STEP](output/release-review/RevI-CAD/step/RevI_ROUTER.step)
- [Bed stored assembly STEP](output/release-review/RevI-CAD/step/RevI_BED_STORED.step)
- [Plasma head hardware STEP](output/release-review/RevI-CAD/step/RevI_PLASMA_HARDWARE.step) — measured torch not yet installed
- [Updated concept PDF](output/pdf/plasma-router-stand-concept.pdf)
- [Changes, evidence and reproduction](output/design-finish-2026-09-26/README.md)
- [Current verification index](output/design-finish-2026-09-26/ACCEPTANCE.md)
- [Every original audit finding](output/design-finish-2026-09-26/FINDING-DISPOSITION.md)
- [Remaining engineering and measured inputs](output/design-finish-2026-09-26/OPEN-ITEMS.md)
- [Mechanical component schedule](output/release-review/RevI-CAD/cutlist.csv)
- [Selected controls schedule](output/design-finish-2026-09-26/controls/selected-components.json)
- [Scrap tube lengths and inspection inputs](output/design-completion-2026-09-26/SCRAP-TUBE-GUIDE.md)
- [X/Y lead check and arrival measurements](output/design-completion-2026-09-26/CONTROL-SCALE-CHECK.md)

![Current router CAD](output/release-review/RevI-CAD/previews/RevI_ROUTER.png)

## Design and changes

Ten 1220 mm extrusion bars yield thirty 397 mm strips in six 500 × 397 mm
panels. The bare bed is 1003 × 1211 mm. Panels, four support beams and separate
spoilboards store inside the chassis. Conversion is manual and retains 52
primary release fasteners plus restraint/tool operations. It is not an
automatic or quick bed changer.

The head now has twin guides, 6 mm captured float, cone/V/flat magnetic release,
sealed detection switches, machined clamp features and internal parking. Its
replaceable insert remains unbored until the actual torch is measured. The
plasma hardware view is therefore a mechanism assembly, not an invented
ready-to-cut VIV ARC CUT-50 setup.

Storage rods increase from 10 to 14 mm with 40 mm sockets and thicker seats.
Actual-section calculations replace the earlier incomplete stiffness claim.
The proposed light-routing target is 0.20 mm tool-to-work displacement at
100 N; known bed members alone account for about 0.135 mm. Actual motion,
mount, joint and tool compliance remain unqualified. Sand receives no
elastic-stiffness credit.

The water system gains a supported drain/flange, removable tail and parking
cup, strainer carrier, corrected pump orientation and supported pressure and
suction hose routes. The reservoir stays vented. A compressor or venturi is
not connected to the fabricated tank.

[Current controls](output/design-finish-2026-09-26/controls/README.md) retain
Kraken V1.1 with onboard drivers. Actual terminal circuits, timer contacts,
isolated run request, restart prevention and a selected C41S speed converter
are defined. Separate [isolated head inputs](output/design-finish-2026-09-26/controls/HEAD-INTERFACE.md)
connect the float and breakaway switches. Router Z zero remains manual; the
parked plasma float is not a spindle touchplate. The populated panel, complete stop/power/brake system, actual
VFD/cutter interface and physical commissioning remain unfinished.

The selected X/Y catalog variants specify **10 mm lead**, meaning movement
per screw revolution, not screw diameter. The selected SFU1605 Z has 5 mm
lead. Verify delivered modules before final calibration and adapter drilling.

The 2 × 2 tube list remains 30 blanks totaling 29,472 mm / 96.69 ft net, using
3.048 mm modeled wall. Actual scrap lengths, remaining wall and condition
must be recorded before nesting. The mechanical cut list is not a complete
electrical BOM or a current delivered purchase total.

## Evidence, history and cost

The [verification index](output/design-finish-2026-09-26/ACCEPTANCE.md) binds
current assembly, pose, route, service, mechanism, circuit and export reports
to their source files. These checks have explicit limits: nominal clear
geometry does not establish physical rigidity, force thresholds, operator
access, live electrical behavior or machining accuracy.

The active generator is [build_revi.py](output/release-review/RevE-ENGINEERING/build_revi.py).
Shared Python sources retain their legacy directory name; **current exports
are in RevI-CAD**. Rev H, Rev G, older exports and the
[29-finding audit](output/cad-reaudit-2026-09-25/README.md) are preserved as
historical evidence. They are not relabeled as current results.

[Earlier prices](outputs/reve-30510/CNC-plasma-RevE-budget.xlsx) and the
[actual-price audit](outputs/reve-30510/actual-cost/REAL-COST.md) are historical
procurement research. Quantities changed; neither is a complete Rev I build
total. No purchase, vendor message, firmware flash or machine operation is
implied by this public design record.

CadQuery/OpenCascade generate exchange geometry; ReportLab generates the
concept brief. This is not a native Fusion feature-history or machine-specific
CAM release. The [original snapshot manifest](REPOSITORY-SNAPSHOT.json)
describes the initial import only. Supplier material retains its existing
license notices; this repository grants no new rights over it.
