# Actual manufacturer housing and passive ATC docks

The selected owned motion module remains the 311 mm overall / 200 mm travel
SFU1605 unit. Its published outer dimensions and underside channel axes are
preserved. The carriage's unpublished four-M6 pattern/depth and actual channel
nut/cavity fit remain supplier-side transfer-fit interfaces.

## Recovered manufacturer geometry

`sources/ER20_4_Standard_20240204.step` is the original four-solid manufacturer
installation model, downloaded from the manufacturer's existing Discord channel.
It is already **60 mm wide**, not a scaled 54 mm model. The official FAQ says
ER11, ER16 and ER20 share the external geometry and differ in their sockets.
The provenance, file hash, dated source and limits are in
`sources/manufacturer-housing-provenance.json`.

The unscaled housing is 271.2 x 60 x 80.8 mm overall. Its body is
212 x 60 x 51.2 mm. Four pocket axes are X507.5 / 552.5 / 597.5 / 642.5,
Y1100 when deployed. Four actual mounting axes are X481 / 669 and
Y1080 / 1120, with D6.35 through bores and D11 x 7 mm counterbores.
The model is a dated installation shell; internal ER11 sockets, nut engagement
planes, IR optics and cable exits are not represented. Confirm the supplied
kit revision/template and calibrate the loaded nut engagement height.

The housing now sits at Z1051.85 on two 28 x 60 x 12.7 mm pads. Four M6x55
socket screws have 10.8 mm nominal pad engagement, 1.9 mm tip reserve and
1 mm head recess in the source counterbores. Separate central M6x30 screws
attach the pads from below, so opposing fasteners do not share the same holes.
The existing 600 mm 4080 rear carrier is reused. Two 28 x 242 x 25.4 mm
billet arms now lie directly under the actual mounting X axes and bolt to that
carrier. This avoids buying another 4080 member and increases the arm bending
section substantially. No additional owned-sheet credit is assumed.

Four retained-tool capacity cylinders use D21 mm, including allowance around
the manufacturer-listed 19.5 mm ER11 nut OD; the maximum cutting-tool diameter
is 15 mm. Their 26.35 mm below-base projection leaves 2 mm nominal lateral
clearance to the arms. These are capacity envelopes, not actual ER11 socket or
tool solids. The whole-kit conservative capacity is 520 x 60 x 107.3 mm above
the revised base, retaining the previous Z1159.15 ceiling. A P50 loaded tool
retains 10.85 mm nominal flyover clearance at 250 mm lift; minimum lift with a
5 mm gap remains 244.15 mm. The actual existing boot's registered moving joint
and spindle/nut reference still require installation binding.

## Automatic straight-line docking

The old manual endpoint shoulder bolts, nuts, washers and their access bores
are removed. The moving end plates now have integral lowered horizontal tongues
and bearing lands machined from two 80 x 60 x 25.4 mm billets. Steel roofs and
cheeks capture the tongues at both deployed and parked endpoints. Chamfered
entries allow the existing slide to drive directly in and out. The two-sided
left guide constrains lateral motion/yaw; the right receiver floats laterally
for thermal spacing. Opposite front/rear stops define the two endpoint datums.

Nominal roof/lower-tongue clearances and total left X free play are 0.15 mm.
Finish guides/seats **after welding**, fit indexed shims as needed and accept
0.10-0.20 mm measured clearances over the full stroke. The right outer X float
is 1.2 mm. These are explicit fitted metal interfaces, not assumed as-welded
accuracy or a claim of friction self-locking. The selected slide must maintain
qualified axial holding/preload while changing tools. No power-loss axial lock
is claimed. Both endpoint/capture confirmations, energized-axis state, zero
spindle speed before magazine motion, boot clearance, wood mode and stored hood
must participate in the actual controller interlocks. A fault inhibits tool
change and latches an alarm.

The ideal 100 N arm-plus-beam bending screen is approximately **0.06164 mm**.
A separate conditional wall screen records a chosen 20 Nm torque case.
Neither calculation includes impact transients, actual profile/rail joints,
contact/weld qualification, thermal behavior or measured motor holding force.
They are scoped engineering screens, not complete operating qualification.

## Removable plasma cover

The 1.9 mm steel hood now weighs approximately 4.161 kg as finished modeled
parts, excluding weld/coating. Rear openings follow the relocated deeper arms;
lower local reliefs clear the fixed capture guides. Two small welded side tabs
seat on the deployed receiver roofs, retained by **two short M4x6 screws**.
Their nominal steel engagement is 4.1 mm with 2.25 mm tip reserve. The old long
compression spacers and arm-mounted cover clamps are eliminated.

Remove the two M4 screws into owned tool storage before lifting the cover.
Then lift 500 mm, rotate 90 degrees about Y, shift 390 mm left/70 mm rear,
lower onto the storage level and insert 90 mm right onto its hooks. Refit the
storage keepers/R clips. The continuous route and 8 mm screw release are
checked inside the machine footprint. The route inside an unspecified owned
tool-storage box is not modeled. The hood is a direct-spatter barrier, not a
sealed extraction enclosure or a thermally qualified cover.

## Outputs and export requirement

Run `build_atc.py` with the project CadQuery interpreter. The current output
contains two read-back-checked assemblies, 29 current custom STEP parts,
`atc-takeoff.csv`, source hashes and full subsystem geometry checks. New
hardware includes six M6x30, four M6x55 and two M4x6 screws. Ten compatible
carrier M6 slot nuts are required (four end, two centre, four arm). The four
manufacturer solids are nonpurchased family installation references. Basic
excludes IR/dust cover and may omit the family endcaps; their display does not
assert exact Basic box contents. One chosen kit is counted separately. The separate vendor mounting-screw package is not
purchased in addition to these custom M6x55 mounts.

**Use `actual_atc.add_assembly_part(asm, name, shape, color)` when exporting the
manufacturer housing in a larger assembly.** The original topcap is valid in
its local definition, but baking its roughly one-metre translation into its
small trim curves causes an OCC STEP reimport failure. An explicit assembly
location preserves the unmodified source geometry and passes readback. This
is a placement/export correction, not a simplification of the housing.

The four-pocket Basic kit remains $400 before freight/tax on the direct
manufacturer form. Its absent IR must be supplied through a selected Pro
upgrade or qualified external detection/controller interface before unattended
operation; that interface remains an explicitly unpriced selection hold. Cheaper AliExpress-compatible retrofit ATC has not been
verified; see `budget-options.json`. No whole-machine delivered-budget or
fabrication/operating release is asserted by this subsystem report.
