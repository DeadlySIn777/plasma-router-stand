# Current integrated 4080 small machine — manufacturing and budget

This folder belongs to the **integrated** 800 × 1000 machine with owned
300 mm catalog-travel Z, assessed working Z250, original owner router head,
full drill-only HDPE/20100 bed and selected 200 mm magazine slide. It does
not apply the old four-cassette takeoff or the old 83-blank stock credits.

Use `stock-and-hardware-families.csv` for the concise stock/hardware view,
`detailed-requirements.csv` for the component-to-source crosswalk, and
`current-drawing-index.csv` for actual current custom-part STEP references.
Both CSV views describe the same requirements: do not add their quantities
together. Wood/plasma display assemblies are alternative modes of one machine.
`NONADDITIVE_REFERENCE` rows are included parts or assembly references, not
extra purchases. Empty new quantity means a held count or selection, never zero.

The frame/motion custom STEPs are regenerated from the current assembly
factory and reimported individually. They include the widened frame, raised
fixed gantry, paired 4080 beams, actual repaired Z-link joint and front stops.
Removed front bearer/arm/angle parts are excluded from the current index and
their fastener station counts are reduced. Old frozen world poses are not
silently reused. Subsystem indexes retain the bed, selected head and selected
magazine slide exports from their own final manifests.

The new front pan beam is at Y300. Its two stepped steel hangers each use
one 160 × 325.85 × 6.35 mm flat blank plus an 80 × 80 × 6.35 mm bearing seat.
The current-custom report proves four 22 × 22 mm raw datum blanks fit the
unused side band of the left new hanger blank; finish them to 20 × 20 mm.
They are four new parts, with no extra raw-stock purchase and no owned-stock
credit. Their row is explicitly nonadditive to the already counted hanger
material. The exact remaining metal distance and separate blank gaps are
recorded in the nest proof.

The front stop modules use separate operating and parked datum blocks.
The four datum anchor sets are new. Four additional M6 slot nuts remain at
the parked module axes; the original operating nuts stay in place. The four
original module bolts/washers are reused during the transfer. Connector,
lead slack and positive state-interlock selections remain held requirements.

Finished bounding blanks do not include saw/facing cleanup allowance. Keep
integral billets and one-piece angles integral. A welded assembly's bounding
box is not an instruction to buy that whole box as solid billet; use its
specified constituent stock set and current finished STEP. Supplier profile
slot/core cavities, rail patterns, thread engagement, clamp/torch interfaces
and actual material properties remain physical qualification gates. Nominal
thread-major cylinders in STEP are not tap-drill diameters.

`exclusive-stock-nests.json` allocates the one owned 12-inch half-inch sheet
only to four main head plates and six small head blanks. The one owned
three-eighth-inch sheet is separately allocated to the two full-thickness
270 × 120 mm bed hinge arms, the shared gravity ledge and the router side rib.
These are 14 exclusive blanks in total: ten half-inch and four three-eighth-inch.
The rib's 20 × 110 mm footprint at sheet coordinates276,2 lies in the unused
right strip,4 mm beyond the hinge-arm blanks. Its three M4x25 screws and two
ground4 × 20 mm dowels are new hardware. The supplied clamp and boot remain
unchanged; the rib clears the known boot body by7.75 mm across its full
vertical stroke, independent of vertical home. Actual dowel fits, material,
preload, slip and torsion still require qualification. The four ATC drop
plates and the slide base are new 6.35 mm material. The two 10 mm hinge spacers
are also new: 9.525 mm stock does not satisfy 10 mm. The two owned raw sheets are not new
purchases. No other carrier, gantry, clevis, ATC arm or plasma part gets those
same credits. Nominal nests require actual size/alloy/temper/flatness and
machining allowance verification; chips, split thickness and unused strips
do not become additional free stock.

Eight retained bed pins have current drawings and explicit hardware. The four
stay pivots and two full-open locks use six M6 DIN937 low nuts and six1.6 × 14 mm
split pins. Two plain12 mm hinge pins face inward and use outside18OD/12.2ID
custom washers and2 × 16 mm split pins; there are no M8 hinge nuts. A new
19.05 × 304.8 mm C45/4140 bar supplies all eight pins and four hinge rings:
four33 mm blanks, two35 mm blanks, two40 mm hinge packs and seven3 mm kerfs
use303 mm. Each hinge pack includes its pin, washer, shim and two internal
kerfs. Finished parts and this raw-stock option are nonadditive; the bar is
not owned stock. Capacity and actual fits remain physical qualifications.

The bed fasteners use eighty M6 DIN9021 bridge washers, 18 OD/6.4 ID by
1.6 mm, below the crossmembers. They bear across the 13.1 mm sleeve bores;
the 65.4 mm metal columns bypass HDPE preload. Purchase eighty M5x75 socket
screws and finish each to 72.0 +/-0.1 mm under the head, with an end chamfer
no longer than 0.4 mm. The nominal slot-nut engagement is 2.7 mm, with 1.0 mm
tip projection and 1.1 mm cavity reserve. Received extrusion, washer bearing,
screw finish and nut capacity still need acceptance. The receiving ledgers
use 22 mm clearance holes for the washers; dry-arm screw access remains
12.5 mm. Hole positions and the work surface stay at their existing datums.

The two full 1000 × 1219.2 × 12.7 mm HDPE layers cut across the full factory
48-inch width of one 48 × 96-inch sheet. Two 1000 mm crosscuts plus saw kerfs
fit the 96-inch dimension. No routed HDPE pockets, counterbores, slots,
notches or facing are authorized. Ten 20100 profiles stay uncut at 1220 mm.
The HDPE and bed profiles are new costs because no purchase receipt or
physical ownership was established.
The indexed `HDPE-DRILL.csv` and two round-drill DXFs provide 80 holes per
layer: one 13.2 mm datum hole and 79 × 22 mm clearance holes. Their origin is
the sheet's left/front corner (world X75/Y−39.6). These are circular through
drills only. The four 980 mm metal crossmembers have their own distinct
sleeve-bore and end-core operations; do not confuse those with HDPE drilling.

`owned-equipment-register.json` excludes already owned motion modules,
guide rails/blocks, drives/controller, spindle/VFD, original working clamp/
boot/actuator, electronics enclosure, cutter/torch and compressor from new
equipment cost. Inspect actual supplied fasteners and interfaces; assembly
ownership does not prove every new custom screw, slot nut or spare channel.
The selected magazine slide is counted once as owner-reported motion, with
its component envelopes nonadditive. The RapidChange kit is not proven owned.

`4080-cut-stock-options.json` is a nonadditive raw-bar planning view. Choose
one compatible supplier stock plan. The two long headers cannot come from
1500 mm bars. Raw bar packs are not extra stock on top of the cut requirements.
The actual supplier die, section properties, kerf and end cleanup govern the
final cut plan; no cheap bar price is extrapolated into an invalid header.

## The $1,000 budget does not pass

Observed public unit prices extended for the required quantities already give:

| Required core goods | Goods basis |
| --- | ---: |
| Five 1220 mm two-profile 20100 packs | $399.95 |
| One black 48 × 96 × ½-inch HDPE sheet, both layers | $225.75 |
| RapidChange four-pocket ER11 Basic magazine | $400.00 |
| **Core goods alone** | **$1,025.70** |

That is $25.70 over the cap before the frame, pan, slats, feet, hardware,
receiver, freight or tax. The known Basic goods subset including the gas
strut pair and tool setter is $1,108.94. The separately sold $5 mounting
package is not purchased: four matched M6x55 screws are already in the actual
hardware takeoff. The preferred Pro IR upgrade makes that subset $1,208.94.
Adding the separately verified motorized drain valve makes the Basic subset
$1,159.36. These remain incomplete goods
subtotals, **not a complete shipped quote**. The selected gas pair uses a
dated $33.24 sale price; its $36.97 typical price adds $3.73. Its compressed
length is unpublished and a force-rating bullet contradicts the selected
variant, so physical fit/force acceptance remains a real purchase gate.
Four ball studs are included with that pair and are not added again.
Five packs are a required-price
extension, not confirmed available cart quantity. HDPE/ATC freight and all
tax remain unknown. The black sheet saves$34.65 against the earlier white
sheet at the same nominal thickness and size; no HDPE layer was deleted.

The product URLs, observed variant/shipping limits and every unpriced cost
category are in `price-and-budget-register.json`. No order, account-history
screen, private delivery address or fabricated shipping figure is published.
`budget_gate=FAIL` stays explicit even if reconciliation tests pass.

[selected-cart-evidence.json](selected-cart-evidence.json) records the dated,
selected AliExpress project fastener packs and their actual variant/pack
quantities. The cart is partial and remains subject to the final BOM and
received grade/fit checks. Other hardware, structural stock, HDPE, ATC and wet
materials are not established as staged by that evidence. Use its current
contents rather than copying a cart subtotal into the build total.

Regenerate current custom parts with the CAD Python runtime using
`export_current_custom.py`; after all subsystem takeoffs/indexes are final,
run `build_pack.py` with plain Python. `manufacturing-check.json` binds input
and output hashes, quantity/nest/index checks and budget arithmetic. A passed
reconciliation report is not a fabrication/operating release or a claim that
supplier interfaces and the existing boot's installed home registration were
physically measured. See the machine-level status for those remaining gates.
