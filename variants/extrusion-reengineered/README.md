# XR1 — re-engineered small 4080 wood/plasma table

This is the current small-table design. It replaces the previous 4040, welded
budget-frame and unoptimized all-4080 cart proposals. It uses the user's owned
motion modules, guide rails, drives, spindle/VFD and fabrication tools.
The electronics enclosure is also already owned and excluded from new purchases.

**Engineering development, not a fabrication/CAM release.** The complete
mechanical-table budget is **USD 1,000 delivered**. That is a design constraint;
this revision contains no new prices, quote or purchasing authorization. The
old Amazon cart is superseded and was left untouched during this redesign.

![Actual XR1 CAD](review/overview.png)

## Open this revision

- [Woodworking assembly](review/XR1_WOOD.step)
- [Plasma assembly with dry cassettes stored](review/XR1_PLASMA.step)
- [Frame assembly](review/XR1_FRAME.step)
- [Printable design review](../../output/pdf/plasma-router-stand-XR1-review.pdf)
- [Audit and release conditions](AUDIT.md)
- [Structure calculations and limits](review/STRUCTURE.md)
- [Bed construction and conversion](BED.md)
- [Water and thermal details](WATER.md)
- [Motion interfaces](INTERFACES.md)
- [Retained ATC requirement and unresolved interfaces](ATC-INTERFACE.md)
- [Requirements and owned equipment](requirements.json)

## What changed and why

The frame has six posts, two upper Y rails and three transverse pan bearers.
The two rear posts stand on short 4080 base beams that carry additional rear
feet. This extends the support polygon toward the parked gantry while staying
inside the existing plan footprint. There are eight feet. Rear posts bear
directly on their base beams; the other four posts run directly to foot plates.
Fishplates maintain alignment and bearing angles carry the pan and dry-bed
arms. Structural gravity loads do not depend solely on bracket friction.

Main horizontal 4080 beams have their 80 mm dimension vertical. Short dry-bed
arms lie flat because their cantilever is only 75.2 mm. The nominal frame
contains **12.3574 m of finished 4080**. Stock length, pack quantities and saw
kerf must be nested before purchasing; finished length is not an order quantity.
The decorative extrusion grooves in the model establish mounting envelopes,
not actual section stiffness, weight or T-nut capacity.

The independent Y guides mount on the upper extrusion's inner faces, removing
the two long steel guide strips. Six short side-access actuator saddles replace
the two long steel top caps. Per the user's preference, the two gantry end
brackets and six compact clevis mounts remain integral billet parts for stiffness
and alignment. Y-link supports use bolted plate construction. The actual module slots, guide hole pattern, delivered lead and
Z retention remain measured interfaces. No 10 mm lead is assumed.

The dry bed consists of four plywood torsion boxes with replaceable
MDF wear pads and aluminum T-slot tracks. Independent aluminum ledgers carry
them; the pan floor does not carry router cutting loads. Track bolts clamp
through metal compression sleeves and solid blocking rather than pulling
against unsupported MDF. Metal location and separate hold-downs control return
position. Do not put precision locating pins directly into wood or HDPE.

Both structural skins are 12.7 mm plywood, with a 39.05 mm ribbed core and
6.35 mm replaceable MDF wear layer, totaling 70.8 mm. All eight structural
skins fit one 4-by-8 plywood sheet with the strong face-grain direction along
the 932 mm span. The rib grid needs defined glue/half-lap joinery; a fused
review solid does not imply overlapping raw strips assemble unchanged.

The pan is set lower and rearward to preserve a front cassette transfer channel.
Dry cassettes park in covered storage under the pan. Only plain steel pan/slats
are exposed to the hot plasma zone. Thermal shields, cleaning, cooldown and
physical temperature tests remain necessary before stored wood can be qualified
for use during plasma operation.

Remove the entire spindle/clamp module or the entire plasma drop/head/torch
module before cassette transfer. Only the common Z adapter remains. Remove
the eight M6 cassette clamp sets, retain Z, park the gantry and open the storage
door. Install the next tool module after converting the bed. Removing only
the torch does not establish clearance for the long plasma-head bracket.

Water drains by gravity to a vented receiver. The owned CV-15HS is not used as a
liquid pump. This mechanical baseline does not pressurize a fabricated pan or
receiver. Automatic valve/pump hardware is not assumed installed or qualified.
The user's selected red 20-gallon tote is the reservoir candidate, with a
712 × 470 × 389 mm external clearance envelope. Require 65 L of measured
usable capacity; nominal storage volume is not a verified liquid rating.
The [reservoir interface record](reservoir-interface.json) distinguishes
the photo's body dimensions from the larger lid/handle dimensions.

## Reach and stiffness targets

Nominal axis travel remains **800 X × 1,000 Y × 100 Z mm**. The full carrier
outline is larger than the axis-center rectangle. The defined in-machine dry
surfacing field has a **770 × 960 mm enclosing outline**, X190–960 and Y141.4–1101.4,
with tracks, seams and screw locations as CAM keep-outs. It allows up
to a 15 mm cutter radius within the nominal router center-travel limits.
Outer carrier material and locator ears are not claimed to be fully surfacable
in the machine. Actual cutter length, workpiece, clamps and Z clearance still
determine useful cutting depth.

The framework/ledger/bed deflection target is **0.30 mm at 100 N**, with a 300 N
sensitivity case. Component calculations are conditional on the specified
extrusion and wood properties and qualified joints. They do not establish the
complete spindle-to-work stiffness of the owned gantry, guides, actuators and
tool stack. This variant is for woodworking and steel-sheet plasma; it is not
a steel-milling machine qualification.

## Reproduce the evidence

Run from this directory with a Python environment containing CadQuery 2.7,
NumPy, Pillow and VTK:

```text
python structure_screen.py --fabrication
python bed_screen.py
python check_owned_stock.py
python cutplan.py
python audit_motion.py --manifest
python build.py
python check_travel.py
python check_transfer.py
python water_check.py
python audit_package.py
```

The bed fabrication CSV is a maintained candidate schedule; its metadata binds
it to the current geometry. Keep the explicit unselected shield, service and
hardware rows when updating it. Do not price missing interfaces as zero.

The CAD scripts flush output and use `os._exit` to avoid the known local OCCT
interpreter-teardown fault. Each report states its scope. A valid STEP solid
is evidence of geometry validity, not evidence of stiffness or safe operation.
The final package index binds the evidence to source hashes and marks any
stale report. The 4×8 and retractable ATC variants remain separate development
work; no old test result or price is inherited by XR1.
