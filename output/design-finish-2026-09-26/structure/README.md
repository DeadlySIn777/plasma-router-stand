# Structural completion and its limits

The current change fixes the panel-storage retainer load path. Two slender
Ø10 rods become Ø14 rods supported through 40 mm steel sockets; the receiver
seats become 8 mm thick, widen outward 5 mm, and gain matched web relief and
underside welds. M6×20 lower screws and enlarged staging saddles complete the
change. Storage height, panel positions, chassis tube lengths and footprint
remain unchanged. The frozen Rev H files are preserved.

For a 100 N horizontal load on **one** retainer, the original cantilever screen
was 406 MPa stress and 21.5 mm linear-elastic deflection. That stress exceeds the assumed yield, so the original response cannot actually be treated as elastic. The revised rod screen is 133 MPa and
4.07 mm, with a 2.25 yield reserve against its specified 300 MPa minimum.
The socket's nominal stress is 107 MPa, giving a 2.34 reserve against 250 MPa.
This is storage containment, not a lifting device or machining datum; sliding
fit play can add up to 2.69 mm tip movement before full bearing contact.

## Routing design basis

The proposed acceptance target for light wood/plastics routing is no more than
0.20 mm static tool-to-work displacement under a 100 N load in each direction,
with no measurable slip and no residual movement exceeding 0.02 mm. It is a
target to test, not a claim that this design already achieves it. Metal milling,
large cutters, aggressive cuts and crash loads are not covered.

The actual reconstructed 20100 cross-section has vertical I=27,207.7 mm⁴.
A conservative sum of a full-load single strip, single bed beam, single ledger,
overhanging seat and ledger torsion is approximately:

| Tube wall basis | Identified member displacement at 100 N |
|---|---:|
| Nominal 3.048 mm CAD wall | 0.132 mm |
| A500 design wall 0.93 ×3.048 mm | 0.135 mm |
| Measured 2.0 mm wall sensitivity | 0.153 mm |
| Measured 1.5 mm wall sensitivity | 0.174 mm |

Rounded tube corners are included. No sand stiffness, MDF composite action or
sharing between adjacent extrusion strips is credited. The calculator also
samples actual cut tube sections at drill/service-port stations and reports
an additional conservative sensitivity using the minimum sampled section over
the whole span. Those samples do not certify every local weld or wall feature.

Only 0.065 mm remains within the proposed target after the A500 bed-member sum.
The actual guides, gantry torsion, purchased Z stage, mounts, spindle/tool,
contact stiffness, alignment and joint slip still need measured or supplier
compliance. There is no defensible finite upper bound on these missing terms
in the supplied information. The report therefore explicitly leaves
`full_machine_rigidity_qualified` false.

The existing five diagonal braces and six screw feet are retained. Calculations
include brace axial stiffness/buckling, member stress, seat prying, positive
locator shear, preload limits, slot lips, receiver welds, storage hardware,
foot stem/pad demand, and conditional tipping/sliding sensitivity. The square
fork weld is evaluated with its real perimeter; one shelf weld quantity is
explicitly a demand-scale estimate, not a finished weld-group capacity.

## Current artifacts

- [Executable calculations](calculate_structure.py) and [results](calculations.json).
- [Current joints, force targets and fabrication instructions](JOINTS.md).
- [Primary material and connection references](SOURCES.md).
- [Reinforced restraint path checker](check_reinforced_paths.py) and [results](reinforced-restraint-paths.json).
- [Original large-part routes against reinforcement](check_reinforced_large_routes.py) and [route results](routes/).

The local geometry builder is complete Rev H plus `structure_finish`; root
integration must rerun the same routes with every new Rev I extension. A
report marked stale is diagnostic evidence only. Each result carries the
source identities it actually evaluated.

## Handling difference

Preserve the original sequence: stage detached top bars 1 then 2, then bare rods
1 then 2; reinstall rods 2 then 1 after the boards; reinstall top bars 2 then 1
after the panels. Lift a rod 60 mm initially to clear its 40 mm socket. At the
horizontal staging saddle, lift **8.5 mm** before lateral travel, rather than
the earlier 6 mm. The revised route checker specifies the exact transforms.
Small screw, hand, clothing and tool-access paths remain excluded.

## Physical stiffness acceptance

With drives isolated and the spindle stopped, restrain a force gauge between
an independent work fixture and a non-cutting test mandrel at the intended tool
projection. Apply 0, 25, 50, 75 and 100 N in each X, Y and Z direction, unloading
between runs. Use an indicator referenced directly to the work support so it
measures relative tool-to-work movement rather than motion of the room/floor.
Repeat near the four work-envelope corners and center, at both relevant Z
extensions, with the intended stock/clamp arrangement.

Record force, displacement, unloading residual and fixture compliance. The
fixture must be substantially stiffer than the target or independently
characterized. Pass requires <=0.20 mm at 100 N, residual <=0.02 mm, no slip,
and repeatable readings. Repeat after each bed conversion until repeat seating
is established. This static test does not establish chatter-free cutting;
measured dynamic trials must begin with conservative cuts only after the
mechanical and electrical commissioning conditions are met.

## Integrated verification commands

```text
python output/design-finish-2026-09-26/structure/calculate_structure.py --integrated
python output/design-finish-2026-09-26/structure/check_reinforced_paths.py --integrated
python output/design-finish-2026-09-26/structure/check_temp_fixture_transfer.py --integrated
```

These flags use the complete `build_revi` model without applying the structural extension twice. The root `verify_revi_routes.py` covers the original board, panel and beam routes. The current `calculations.json` static-state results supersede the early diagnostic `static-check.json`. The frozen structural source SHA-256 is `b0e6e7f5fc7bd5d3b9e901bc13f7186f78395c78584ab3238ba249613bea9778`.
