# Full HDPE / uncut 20100 bed

The bed now uses **ten continuous 1220 mm 20100 profiles**, over **two full
1000 × 1219.2 × 12.7 mm HDPE rectangles**. The profiles overhang each sheet by
0.4 mm at each end, allowing both sheets to come from one nominal 48 × 96 inch
sheet. Each HDPE layer has 80 ordinary circular through holes. No pockets,
slots, counterbores or surfacing are required in the HDPE.

The full profile faces run Y−40..1180; the HDPE runs Y−39.6..1179.6.
Four 980 mm 4080 crossmembers support the profiles at Y100/395/780/1140.
Eighty fitted metal columns bypass HDPE in the profile-fastener preload path.
The profiles remain uncut and undrilled. Actual die, bottom-slot nut, sleeve
length and received sheet thickness are fitting acceptance items.

The top is **Z967.8 mm**. The 12 mm front hinge is at **Y−100, Z967.8**;
the permanent front bay is part of the machine's normal footprint. The whole
bed folds upright within that footprint, leaving the plasma area open. Its
main upright envelope is Y−100..−14.6 and reaches **Z2247.8 mm**. This requires
overhead clearance. The longer 270 × 120 × 9.525 mm aluminum hinge sidearms
replace the earlier short arms; their two 80 × 40 × 10 mm spacers remain
separate parts. Global material allocation, rather than this folder, decides
whether either part receives owned-stock credit.

Four M8 side drawdowns retain the closed bed through metal end caps/spacers.
Remove those complete sets and the complete installed head/tool module before
changeover. Keep the common dock, positively retained Z and gantry at the
qualified machine park **Y1275 / X975 / Z250**, with motion locked. Remove guide
screens into their actual under-pan racks, and park/clamp the magazine 200 mm
rearward with its hood fitted. Disconnect the front stop switches' service
connectors and park both complete stop assemblies: 40 mm inboard, 400 mm
rearward, then reseat against the park datums and secure them. The stop transfer
has its own source-bound route proof at bed 0° and 90°. After the bed is upright
and positively pinned, restore and secure both complete stops at their original
operating datums, reconnect/prove the NC inputs and retention interlock, and
rehome at commissioning speed before motion. Actual connectors, interlock and
physical handling remain acceptance items. The local bed proof alone does not
qualify this full-machine operating sequence.

Paired gas springs assist lifting. The selected ARANA 28 inch / 200 lb listing
is a **candidate**, not verified OEM CAD: its compressed dimension is unpublished
and the listing contains inconsistent force text. Required acceptance is
compressed length ≤450 mm, expanded length ≥700 mm, verified 200 lb / 889 N
per-unit force, and the modeled housing/socket envelopes. The nominal mounting
eye distance varies **484.875..688.269 mm**. Metal brackets adapt the actual ball
stud neck; no substitute actuator is silently claimed owned.

The ideal rear-edge force calculation gives **56–79 N**, but that edge rises
above normal reach. A separate reach screen transfers the grip at 35° to the
actual mid-side edge at Y550, 650 mm from the hinge: maximum grip height is
**1702 mm** and nominal force is **102–142 N**, for deck masses **62.2–66.6 kg**.
With one effective spring that reachable-grip case rises to **310–351 N**.
The model is static and excludes tools/workpieces/clamps; clear the bed before
lifting. These figures do not qualify manual handling or an unmeasured assembly mass.
The gas/stay assemblies' own changing weight is outside that ideal deck-force
model; their actual masses and force curve must be included in physical acceptance.

Paired telescopic stays receive independent 10 mm through pins in the upright
position. The gas springs are not positive holding devices. The index-hole row
is an interface proposal and has **no assigned fall-arrest or impact rating**.
A validated supported transition/catch method, actual pin/clevis/weld capacity
and physical handling trial remain necessary before operating the mechanism.
The four stay pivot pin/retainer sets are selected-fit hardware: only their
clevis/eye bores are in the current CAD. In particular, the moving outer clevis
face X44.45 is 1.15 mm inside the rail end X43.3. A generic outboard bolt head
or nut would foul the rail; the actual retained-pin envelope or a revised
clevis must be modeled and checked before fabrication release.

Useful files:

- [Closed bed STEP](output/FULL_BED_WOOD.step)
- [Upright bed STEP](output/FULL_BED_UPRIGHT.step)
- [Local source-bound geometry and force report](output/bed-local-check.json)
- [Reachable-grip force sensitivity](output/bed-handling-reach-screen.json)
- [Complete machine changeover boundary check](output/bed-machine-changeover-check.json)
- [HDPE drilling coordinates](output/HDPE-DRILL.csv)
- [First HDPE layer round-drill DXF](output/FULL_HDPE_1_ROUND_DRILL.dxf)
- [Second HDPE layer round-drill DXF](output/FULL_HDPE_2_ROUND_DRILL.dxf)
- [DXF readback and source check](output/HDPE-drill-dxf-check.json)
- [Additive takeoff and nonadditive references](output/bed-takeoff.csv)
- [Custom STEP index](output/custom-part-index.json)
- [Pan support screen](output/pan-front-structure-screen.json)

`build_bed.py --local` reproduces the local checks and exports. The rigid bed
rotation is continuously bounded. Its ten telescoping-assist poses are finite
samples and are labeled accordingly. `check_machine_changeover.py` separately
checks the final frame, retained actual dock, parked ATC and stored-screen/water
utilities. The current source-bound combined report passes the continuous rigid
bed path against 791 actual external components with zero unresolved pairs; all
ten finite assist poses also pass. The earlier real Z-end and front-stop
collisions were resolved by moving the full faces/rear support 40 mm forward
and parking the complete stop assemblies during the tilt. Failed reports with
`before-rear-shift` in their names are retained diagnostic history.

The 100 N wood-bed compliance screen sums 0.0710 mm profile bending, 0.1866 mm
crossmember bending and 0.0387 mm receiver bending: **0.2962 mm** under its
specified section/support assumptions. It excludes slot/joint compliance,
modified-profile details and the gantry/Z/spindle/tool loop. It is not a steel
machining qualification or measured machine accuracy.

The pan has separate supports at Y300/630/1180. The full-brim screen uses the
actual slat/drain notches, free support rotations and no floor/composite-flange
credit: rib deflection 0.0932 mm plus the supported floor-bay estimate 1.0629 mm
gives **1.1561 mm**. Actual floor support, weld distortion, corrosion, overflow
flow and thermal behavior still require physical acceptance.
