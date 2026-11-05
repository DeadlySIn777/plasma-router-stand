# Selected common dock: actual owner head and matching plasma module

The selected interface uses the unchanged owner clamp/boot on a **full-thickness
146 x175 x12.7 mm billet head plate**. A146 x132 x12.7 mm receiver stays on Z
in both modes. The matching plasma plate is146 x110 x12.7 mm, joined to the
existing drop by a110 x114 x12.7 mm U-splice. The direct110 mm adapter below
is an **unselected comparison**; do not purchase both architectures.

The router plate now carries one9.525 x20 x110 mm side rib, cut from the unused
right strip of the owned3/8-inch sheet at raw coordinates276,2. Three recessed
M4x25 socket screws attach it; two ground4 x20 mm dowels carry longitudinal
shear by positive bearing. The owner clamp and boot remain unchanged. The
rib and all its fasteners lie beyond the complete boot's X envelope by at
least7.75 mm, independent of its unknown vertical home and50 mm travel.

The ideal fully composite plate/rib calculation includes unsymmetric bending:
effective I rises from24,922 to69,128 mm4. The100 N/50 mm projection case
falls from0.250 to0.090 mm in that ideal model. This requires a qualified
connection: the screen shows3.35 N/mm longitudinal shear flow and877 N maximum
rib axial force. Bolt preload, actual aluminum alloy, matched dowel fit,
bearing capacity, microslip and torsion remain unqualified. The computed
improvement does not establish complete-machine stiffness or steel machining.

Use `plasma_quick_dock.integrate_motion(plasma, gantry_y, head_x, z_lift, **kwargs)`
for the entire selected motion group. Assessment coordinates are X175..975,
guide Y275..1275 and Zlift0..250 mm within the nominal owned300 mm module.
The wrapper caps the frozen source at200 mm and translates only original
`Y_X_Z_tool` parts by the extra lift; new head/dock parts are generated directly
at requested Z. Do not add that lift a second time. No controller setting is applied.

The fixed receiver's eight bodies are `move!='head'` entries from
`quick_dock.local_parts()`; fixed means fixed to the Z output. All new selected
head/dock components therefore belong to `Y_X_Z_tool` in a machine sweep.

Two accessible M6x25 screws above the owner clamp retain the seated head with
12.3 mm nominal engagement and0.4 mm rear reserve. They withdraw12.8 mm inside
extended cages, leaving0.5 mm clearance. The supported complete head then pulls
18 mm forward. The existing owner spindle/boot assembly need not be dismantled.
The geometry does not qualify actual head mass, hand support or lifting.

The four source clamp bores remain50 x30 mm.6 mm spacers and M5x25/steel
spreaders give10.998 mm head-plate engagement and1.702 mm rear reserve. Exact
washer-seat area remains96.996% for three and86.963% for one; the source clamp
is not cut to hide that detail. Washer bridge/preload capacity remains held.

The selected nominal spindle axis is `Y=guideY−169.302059 mm`, X=headX.
Z970 remains an uncalibrated reference, not an actual nut plane. The boot is
preserved at its explicitly unregistered reference pose; nonzero `boot_lift`
requires `boot_registration_z_mm`. Its floor equation remains
`1050.582086 + Zlift + boot_registration_z_mm + boot_lift`.
The owner already supplied its identity,50 mm whole-boot motion and working
assembly confirmation. Only its installed registration remains unencoded.

The plasma U-splice clears the cages. Eight M6x16 screws have full modeled
head seats,9.4 mm splice engagement and3.3 mm tip reserve. The custom drop's
upper four bores change to6.6 mm clearance/10.5 x6.1 mm rear counterbores.
The other107 retained plasma-stack components keep exact prior world poses;
torch height is unchanged and the shared Z receiver stays installed.

Four main plates, two cages and four spacers fit **one owned304.8 mm square
half-inch sheet**, with2 mm outer margin and4 mm contour gaps. It is a
full-sheet contour nest, not saw blanks with further facing allowance.
The gravity ledge requests a30 x12.7 mm footprint from the3/8 sheet; the parent
combined allocation must reconcile it. The plasma drop/Z carrier and old83
blank schedule receive no duplicate half-inch stock credit.

- [Selected stock/takeoff check](output/selected-head-pack/selected-head-pack-check.json)
- [Router dock and continuous removal](output/quick-dock/quick-dock-check.json)
- [Matching plasma interface proof](output/plasma-quick-dock/plasma-dock-check.json)
- [Selected requirements](output/selected-head-pack/selected-head-requirements.csv)
- [Retained plasma takeoff](output/selected-head-pack/retained-plasma-source-requirements.csv)
- [Spindle reference provenance](spindle-reference-evidence.json)

The selected checks prove new nominal interface geometry, continuous known-head
removal and relative motion over working Z250. Actual working boot registration,
supplier output attachment, physical strength, handling and loaded ATC operation
remain separate qualifications. No USD1,000/shipping claim is made by this pack.

## Earlier direct110 mm adapter comparison — unselected

This integration replaces the invented split clamp with the **unchanged supplied
65 mm owner clamp**. The original clamp, whole dust boot, brush groove and
working Pegelong 50 mm arrangement remain owner equipment.

`owner_head.actual_head_parts(gantry_y, head_x, z_lift, boot_lift)` returns named
world-space solids; `integrate_motion(...)` removes the provisional router
clamp and dedicated screws before inserting this head. Working assessment
coordinates are X175..975 / guide Y275..1275 / Z lift0..200 mm. Geometry moves by
the stated rigid translations; this does not apply controller settings.

The existing 110 x110 x12.7 mm adapter outer shape and old features are retained.
Four new M5x0.8 taps match the actual clamp's 50 x30 pattern. Measured from the
adapter's lower-left face corner, their coordinates are **(30,22), (80,22),
(30,52), (80,52) mm**. Use 4.2 mm pilots for the selected tap/process; 5 mm
major-diameter holes in review CAD are not drill-size instructions. Transfer
the actual Z output pattern to the removed custom adapter, never the module.

Four 6 mm long, 10 OD / 5.5 ID spacers clear the boot's rear cheeks by nominal
1.5 mm in the illustrated pose. A 3 mm spacer trial was rejected for interference.
Four M5x25 screws and 10 OD / 5.3 ID x1 mm steel spreader washers give nominal
10.998 mm adapter engagement and 1.702 mm reserve before its rear face.
The original clamp has a small interruption in one counterbore seat. The
spreader supports the complete 8.5 mm screwhead; washer-to-original-seat area
is reported as 96.996% for three and 86.963% for one. Its actual bearing/bridge
capacity, fastener preload and material are still qualification items; no
source-clamp material has been removed to hide that detail.

The nominal spindle axis moves about 3 mm forward: X=head command,
Y=guide command−156.602059 mm. The old Z970 lower reference remains an
**uncalibrated setup parameter**, not an actual nut/collet plane. The owned kit
is the previously selected Zhong Hua Jiang 65 mm, 1.5 kW ER11 kit, ASIN
B0BF5R3LNC. A current manufacturer family page states 268 mm overall, differing
from the earlier 259 mm envelope. Neither dimension establishes the received
nose/grip/collet geometry. The optional conservative family cylinder is labeled
as such and is excluded from exact owner-part fit claims.

## Preserved working boot registration

The owner already confirmed that the entire boot moves 50 mm, the actuator is
Pegelong B0D6BCQCVR, the clamp matches its supplied uncut STEP, and the actual
assembly works. None of those identities needs to be requested again.

The two separate supplied STEP bodies do not encode the working joint/home
transform. The exact boot is included in an explicitly named reference export.
Its old inferred pose is not animated as a working assembly. The factory
refuses a nonzero boot lift unless `boot_registration_z_mm` is explicitly
provided. That registration must locate the existing assembly; it is not a
license to cut the clamp or redesign the boot. No replacement actuator or
new working joint is selected.

At the reference transform, boot floor Z is
`1050.582086 + Zlift + boot_registration_z_mm + boot_lift`.
The current magazine capacity top is Z1159.15. A5 mm flyover gap therefore
requires that floor equation to be at least1164.15 during flyover. Actual
engagement needs the selected vendor body/nut/IR geometry and calibrated
spindle datum; an old provisional minimum docking height is not applicable.
The actual boot home and spindle/nut datum must be registered before claiming
a complete automatic change.

## Files and verification

- `output/OWNER_CLAMP_ADAPTER110_WITH_M5_ROWS.step`: corrected custom adapter.
- `output/EXACT_OWNER_CLAMP_ON_Z_ADAPTER.step`: actual clamp/custom mounting.
- `output/OWNER_HEAD_WITH_UNREGISTERED_BOOT_REFERENCE.step`: exact boot at its
  labeled reference registration; not the qualified moving working assembly.
- `output/head-integration-check.json`: source hashes, exact seats, owner-solid
  preservation, STEP readback and continuous relative-motion proof for the
  known clamp/adapter against the retained candidate motion.
- `output/head-requirements.csv`: owned assemblies and the small new mounting
  requirement set. No material is credited from an already allocated blank.

Reproduce with the project CadQuery Python and `build_head.py`. The completed
known-clamp check is separate from full working-boot, supplier-output,
strength, electrical/ATC operation and machine-level release.
