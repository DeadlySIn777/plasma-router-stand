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
preload. The work surface is Z967.8. Front hinges, rear metal drawdowns and
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

The magazine parks in the rear bay on the selected 311 mm overall / 200 mm
travel SFU1605 stage. Endpoint reaction seats and removable shoulder fasteners
support its working and parked poses. These endpoint fasteners are manual;
the slide does not have a qualified automatic pin-release cycle. Purple
magazine/tool volumes are capacity allocations, not actual supplier CAD.
A removable steel cover protects the parked magazine during plasma mode.

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
HDPE layers ($260.40) and a Basic four-pocket magazine ($400) is already
**$1060.35**, before any 4080 frame, pan, hardware, shipping or tax. This is a
dated selected-source comparison, not a universal market minimum or a landed
quote. Required stock quantity and all delivery charges are not verified.

Known owned equipment and the two declared aluminum sheets are excluded.
The two sheets have exclusive nests; no plate is credited twice. Tracks,
full HDPE sheets and the RapidChange kit have no established ownership credit.
See the [price register](manufacturing/price-and-budget-register.json), with
source links, unknown charges and new-material requirements kept explicit.

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
