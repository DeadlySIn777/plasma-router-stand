# Current integrated 4080 small machine - manufacturing and budget

This is the current 800 x 1000 mm wood/carving and plasma table with the
owned 300 mm catalogue-travel Z, a 250 mm assessed working domain, original
owner head, HDPE/20100 bed and selected 200 mm magazine slide. The separate
4x8 studies and steel-machining qualification are outside this package.

Use `stock-and-hardware-families.csv` for the compact stock view,
`detailed-requirements.csv` for the source crosswalk and
`current-drawing-index.csv` for current STEP/DXF references. These describe
the same requirements; their quantities are not additive. Wood and plasma
assemblies are alternative modes of one machine. `NONADDITIVE_REFERENCE`
rows identify included parts, raw-stock options or assembly references.
An empty new quantity is an unresolved count or selection, never zero.

## Current frame and gantry

The six-post 4080 frame has continuous 1760 mm headers and two 1250 mm
4080 gantry beams. Ten sleeved couplers and the existing lower brackets
remain. A 1200 x 112 x 6.35 mm steel rail face with fitted rear lands replaces
the two aluminum rail strips; four 32 x 80 x 6.35 mm steel top bridges tie
the upper faces. Transfer the actual owned rail pattern after datum fitting.
The current STEP specifies the counterbores, retained mounting axes and
coupler-head access. Actual section properties, welds, preload, joint slip
and full tool-to-work stiffness remain qualification gates.

The front pan beam is at Y300 and is 26 mm lower. Each stepped hanger uses
one 160 x 351.85 x 6.35 mm new steel bounding blank plus an 80 x 80 x 6.35 mm
bearing seat. Four stop-datum blanks, four gantry caps and ten rear lands
fit the unused side bands of these already-required new hanger blanks,
with explicit separation and cleanup allowances. Those small parts do not
require another hanger blank and receive no owned-material credit. The
long rail face is a separate new purchase; its minimum cleanup blank is
1202 x 114 x 6.35 mm.

The front stops keep their operating contact geometry and park 400 mm
rearward before bed tilt. Four datum anchor sets and four parked M6 slot nuts
are new; the operating bolts/washers are reused. Complete guide sections
are stored before stop transfer. Gantry motion stays disabled until the
operating stops are restored. Connectors, cable slack and state interlocks
remain held selections.

## Bed and retained hardware

Ten 20100 profiles finish at 1220 mm. Eight are cut from two genuine
four-profile 1500 mm packs; two come from a factory 1220 mm two-pack. Allow
3 mm saw kerf on each of the eight cuts, leaving 277 mm nominal tails.
Actual profile die, straightness, slot-nut fit and lip capacity need acceptance.

One 1000 x 1200 x 12.7 mm HDPE rectangle comes from one nominal 48 x 48 x
half-inch sheet. It covers the cutting area, with 0.4 mm front and 19.6 mm
rear track overhang. The supplier's +/-6.35 mm sheet cut tolerance still
nominally allows this rectangle, but actual thickness, squareness and
flatness need inspection. No routed pockets, slots, notches, counterbores
or facing are authorized. The current single HDPE drill DXF and
`HDPE-DRILL.csv` specify 80 round through holes: one 13.2 mm datum and
79 clearance holes of 22 mm. The sheet origin is world X75/Y-39.6.

Four 980 mm 4080 crossmembers stand 80 mm high by 40 mm along Y, at
Y110/395/780/1140. Their metal columns are 92.7 mm long. Eighty steel
M6 DIN9021 bridge washers, 18 OD / 6.4 ID x 1.6 mm, bridge the 13.1 mm
crossmember bores. Purchase eighty M5x100 socket screws and finish them to
99.3 +/-0.1 mm under the head, with an end chamfer no longer than 0.4 mm.
Nominal nut engagement is 2.7 mm, tip projection 1.0 mm and cavity reserve
1.1 mm. The lower nuts are DIN562 M5 thin square nuts, nominal 8 mm across
flats and 2.7 mm high; they are distinct from 4080 M6 slot nuts. Actual
washer seats, stack thickness, thread fit and capacity remain acceptance items.

The workplane stays Z967.8. Steel receiver angles and remaining dry arms
are 27.3 mm lower than the former two-layer/flat-crossbar stack. The receiver
bearing level is Z855.1. The hinge arms are now 270 x 128 x 9.525 mm. Rear dry-arm access is
D12.5 through the profile at X125/1025, Y1140. These are open front/outboard
corner notches, clearing the outer screw heads during initial tilt; no thin
1.1 mm end ligament is retained. Use the current profile-operation STEP. Actual
drilled-section properties remain unqualified.

Eight retained pins have current drawings: four stay pivots, two full-open
locks and two plain 12 mm front hinges. The first six use six M6 DIN937 low
nuts and six 1.6 x 14 mm cotters. The two inward-headed hinges use custom
18 OD / 12.2 ID x 1.6 mm washers and two 2 x 16 mm cotters, with no M8 hinge
nuts. A new 19.05 x 304.8 mm C45/4140 bar supplies all eight pins and four
hinge rings in a 303 mm nested plan including the stated kerfs. Finished
parts and this raw option are nonadditive. Material, weld, bearing, fit,
handling and pin capacity still require physical qualification.

The gas candidates are now a pair rated 150 lb / 667 N each. Require
compressed eye length <=445 mm and expanded length >=700 mm; the modeled
operating range is 456.18-658.29 mm. No old 200 lb offer, price or force curve
is retained. Gas springs assist handling; separate positive pins retain the
open stays. Controlled transition and actual fall protection are unqualified.

## Exclusive owned stock and wet fabrication

The owned 12-inch half-inch aluminum square supplies four main head plates
and six smaller head blanks. The owned three-eighth-inch square supplies
two 270 x 128 mm hinge arms, the gravity ledge and the router rib: 14 exclusive
blanks in total, ten plus four. `exclusive-stock-nests.json` controls the
actual placements and cleanup gaps. The rib footprint is 20 x 110 mm at
sheet coordinates 276,2; its three M4x25 screws and two ground 4 x 20 mm
dowels are new. No other custom billet receives the same stock credit.
Actual alloy, temper, condition and dimensions still require acceptance.

The pan, slats, keeper stations and upstream drain are 26 mm lower. Plasma
slat tops are Z852. The upper overflow is three flat welded strips: one
44 x 383 x 1.9 mm back and two 18.1 x 383 x 1.9 mm sides. It has no separate
bottom cap. The lower gutter has a corrected 44 mm floor width, two cheeks
and an exit deflector; its Z410 outlet preserves the 19 mm receiver air gap.
Current utility stock replaces the obsolete legacy overflow schedule.

Six guide panels, eighteen clip plates and fourteen rack plates have current
flat cutting profiles and exact assembled-union proofs. Their assembly rows
are nonadditive. The two unchanged curved overflow brackets retain a forming
coupon/calibration gate. Valve fit, pipe supports, receiver usable liquid
capacity, water-tightness, thermal behavior and control interlocks remain open.

`owned-equipment-register.json` excludes the owned motion, extra guides,
drives/controller, spindle/VFD, original clamp/boot/actuator, enclosure,
cutter/torch, compressor and owner-reported magazine slide. The RapidChange
kit, tracks, HDPE and unallocated custom stock are new requirements.

## Cost and staged carts

Dated selected-source observations on 5 November 2026 give:

| Required core goods | Goods basis |
| --- | ---: |
| Two four-profile 1500 mm SeekLiny packs at $129.99 | $259.98 |
| One two-profile 1220 mm SeekLiny pack | $82.99 |
| One US Plastic 42707 recycled black 48 x 48 x half-inch sheet | $191.86 |
| RapidChange four-pocket ER11 Basic magazine | $400.00 |
| **Core goods** | **$934.83** |

The core is $90.87 below the previous selected-source $1025.70 case. It
leaves $65.17 before every other required item. The partial carts contain
16 variants / 33 packs / 538 pieces, at $455.05 goods: AliExpress 13 variants /
26 packs at $78.32, plus Amazon 3 variants / 7 packs at $376.73. The Amazon
portion includes the same $342.97 tracks and eighty M5x100 screws at $33.76.
Included BNUOK nuts/washers are unallocated extras; they do not replace the
specified bridge washers or profile slot nuts.

Counting the shared tracks once gives **$1046.91 core plus staged hardware**.
The required $50 tool setter makes that subset **$1096.91**, before any 4080
frame, pan, remaining parts, freight or tax. The separately sold vendor
mounting package is not bought; four M6x55 custom-mount screws are already
requirements. Basic lacks tool detection; the selected state interface and
conflicting Pro upgrade prices remain unresolved.

The 1500 mm stock's final Amazon cart estimate is **December 9-24**, superseding
an earlier November detail-page estimate. The 1220 mm pack and M5 screws
show November 9. These selected Amazon lines show free Prime to 30510.
AliExpress displays free shipping, but the exact Alto address is unconfirmed.
HDPE/ATC freight and sales tax remain unknown. No order has been placed.

`price-and-budget-register.json`, `selected-cart-evidence.json` and
`cart-coverage-check.json` identify prices, selected variants, delivery limits
and remaining unstaged requirements. The **$1000 delivered budget fails**;
no unavailable long-profile teaser or unquoted charge is treated as a saving.
The frame stock, pan/slats, new billets, remaining hardware/slot nuts/feet,
matched gas springs, drain fittings, ATC sensing/tool contents and delivery
costs remain outside this partial priced set.

## Rebuild and review

The custom-parts exporter reimports each current STEP. After final subsystem
indexes and takeoffs, run `build_pack.py`; it binds source/output hashes,
quantities, stock nests, drawings and budget arithmetic. Run the procurement
and cart-coverage helpers after the master BOM is current. For the whole
machine, regenerate the assembly and adaptive STEP readback/previews before
the printable review. Nominal geometry and passed reconciliation do not
qualify actual supplier interfaces, machining, full rigidity or operation.
All fabrication, CAM and operating release flags remain false.
