# Integrated 4080 small table

This is the current small wood/carving and plasma design. It integrates the
owner's original clamp/boot geometry, full HDPE/20100 bed, owned 300 mm Z and
selected 200 mm magazine slide into one source assembly. It supersedes the
provisional heads, plywood cassettes and separate belt magazine proposals.
**It is a review model, not a released fabrication, CAM or operating package.**

- [Wood mode STEP](output/INTEGRATED_4080_SMALL_WOOD.step)
- [Plasma mode STEP](output/INTEGRATED_4080_SMALL_PLASMA.step)
- [Changeover at 45 degrees STEP](output/INTEGRATED_4080_SMALL_CHANGEOVER.step)
- [Printable current review](../../output/pdf/plasma-router-stand-integrated-4080-review.pdf)
- [Current status and unresolved requirements](STATUS.md)
- [Stock, hardware, ownership and budget](manufacturing/README.md)
- [Assembly source and independent STEP readback](output/assembly-check.json)
- [Subsystem clearance check](output/integration-clearance-check.json)

![Current wood mode](output/INTEGRATED_4080_SMALL_WOOD.png)

The cutting travel remains 800 mm X by 1000 mm Y. The owned Z has 300 mm
catalogue travel; this design assesses a 250 mm working domain. No controller
limits or steps-per-mm settings have been changed. The complete machine is
not qualified for steel milling.

The six-post frame uses 4080, with continuous 1760 mm headers from Y-160 to
Y1600. The front posts move to Y-100 to support the bed's parking bay. Two
1250 mm 4080 gantry profiles replace the former 8080 beam, with ten sleeved
couplers and two retained-hole rail datum bars. Their actual section, joints
and load sharing still require qualification; the decorative profile model
does not establish stiffness.

The 1000 by 1220 mm workbed has ten uncut 20100 profiles on two full HDPE
layers and four 980 mm 4080 crossbearers. Metal sleeves bypass plastic bolt
preload. Eighty 18 OD/6.4 ID by 1.6 mm crossmember bridge washers complete the
fastener bearing path. The eighty M5x75 stock screws finish to 72.0 mm under
the head; the metal columns remain 65.4 mm long. The work surface is Z967.8.
Actual washer/section bearing and
slot-nut capacity still require qualification. Front hinges, rear drawdowns and
fitted side bearing ledgers carry the bed. Two gas springs assist handling;
separate pinned telescoping stays support the upright state. The full bed
stands ahead of the plasma working sweep, inside the permanent machine plan.
Its highest nominal point is approximately 2247.8 mm. The full faces span Y-40 to Y1180; the rear crossbearer is Y1140, keeping the retained long-Z lower end clear during tilt.

The complete front stop assemblies retain their cutting-mode geometry. For
bed changeover they are manually parked 400 mm rearward using the same header
slots, with fixed datum blocks for return. Gantry motion remains disabled
until they are refitted. Guide sections are stored before moving the stops;
the stops are refitted before restoring the guides. The complete head/tool
module is removed, with the common Z parked at Y1275, X975 and lift250.
Its supported handling and off-axis parking remain a separate qualification.

The exact owner clamp and boot STEP bodies stay unchanged. A 146 by 175 by
12.7 mm billet head plate removes as a complete module from the shared dock.
The fixed 146 by 132 mm receiver retains the raised output contact while
clearing the bed's tilt arc. A matching plasma plate and splice reuse the
existing float/breakaway mechanism. The actual working boot registration and
spindle nose datum remain unencoded; a purple family cylinder is context.
One 9.525 by 20 by 110 mm side rib now stiffens the router plate using unused
owned three-eighth-inch stock, three M4x25 screws and two ground 4x20 mm dowels.
It clears the supplied boot body by 7.75 mm in X for any vertical home and
the full 50 mm boot stroke. The hole-aware ideal composite bending screen
falls from 0.250 to 0.093 mm at 100 N with 50 mm tool projection. Actual bolt
preload, dowel fit, joint slip, torsion and alloy remain qualification gates.

All eight bed support/hinge pins now have explicit retention geometry and
drawings. Four stay pivots and two full-open locks use M6 DIN937 low nuts and
1.6x14 mm split pins. The two plain 12 mm front hinge pins face inboard and
use outside custom washers and 2x16 mm split pins; they require no M8 nuts.
One new three-quarter-inch by 12-inch steel bar supplies all eight pins and
four hinge rings through a 303 mm nested cut plan. This is new stock.

The magazine parks in the rear bay on the selected 311 mm overall / 200 mm
travel SFU1605 stage. Integral billet tongues enter passive steel capture
roofs/guides at both endpoints; the slide deploys and retracts without manual
endpoint fasteners or another lock actuator. The original 60 mm-width
manufacturer four-pocket housing, pocket XY axes and mounting pattern are
integrated without scaling. Two 28 by 242 by 25.4 mm billet arms use the
existing 600 mm 4080 carrier. Purple volumes remain capacity allocations for
tool/kit clearance. Actual ER11 sockets, nut engagement, IR/cables, received
revision, powered axial holding force and controller interlocks still require
qualification. A removable steel cover, retained by two short M4x6 service
screws, protects the parked magazine during plasma mode.

The pan bears at Y300, Y630 and Y1180. The new front bearer hangs from the
headers on welded steel bearing seats. The conservative full-brim rib/floor
screen gives 1.156 mm nominal displacement without composite flange credit;
this is a pan screen, not full-machine FEA. The receiver is atmospheric. The
motorized gravity drain and independent overflow never pressurize the red
consumer tote. Six short removable rail splash screens have under-pan storage.
They do not replace actual module wipers/bellows or thermal qualification.

![Current plasma mode](output/INTEGRATED_4080_SMALL_PLASMA.png)

## Budget result

The USD 1000 complete new-parts delivered cap **does not pass**. The current
observed goods extension for ten tracks ($399.95), the sheet supplying both
HDPE layers (one black sheet, $225.75) and a Basic four-pocket magazine ($400)
is already **$1025.70**, before any 4080 frame, pan, hardware, shipping or tax. This is a
dated selected-source comparison, not a universal market minimum or a landed
quote. Required stock quantity and all delivery charges are not verified.

Known owned equipment and the two declared aluminum sheets are excluded.
The two sheets have 14 exclusive blanks: ten from the half-inch sheet and
four from the three-eighth-inch sheet. No plate is credited twice. Tracks,
full HDPE sheets and the RapidChange kit have no established ownership credit.
See the [price register](manufacturing/price-and-budget-register.json), with
source links, unknown charges and new-material requirements kept explicit.
The [selected AliExpress cart evidence](manufacturing/selected-cart-evidence.json)
records only the dated project fastener selections. It is a partial cart,
not the complete BOM, a purchase, or a complete delivered build quote.

## Reproduce and review

Use the existing CadQuery interpreter. Run `mechanical.py`, the selected head
builders, `atc/build_atc.py`, `bed/build_bed.py --local`, the bed drill/takeoff
helpers, `utilities/build_utilities.py`, the two guide routes and front-stop
transfer check, then `bed/check_machine_changeover.py` and `check_integration.py`.
Run `assembly.py`, followed by `verify_assembly_outputs.py` for adaptive mass
readback and complete fitted-camera previews; then regenerate the manufacturing
pack. The older standalone nonlocal bed builder does not represent the current
parked-stop/common-dock changeover context. Reports bind their inputs by SHA-256
and state their scope. A successful
STEP readback proves valid exported solids, not a working machine. Use the
current status file to distinguish geometric checks, actual-interface holds,
physical qualification and the failed delivered-budget requirement.
