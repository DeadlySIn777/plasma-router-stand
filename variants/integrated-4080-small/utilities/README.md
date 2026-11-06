# Integrated wet utilities and guide screens

The pan, combs, slats, overflow, red atmospheric receiver, service hatch and
receiver heat roof remain. The former cassette cabinet and its guide shields
are excluded. The former100mm pan-support shims are removed; three fitted
25×20mm shim packs now support the real300mm bearer. The whole pan, slats,
pan supports and installed keeper stations are26mm lower. Slat tops areZ852;
the wood workplane staysZ967.8. Front pan keepers move530mm rearward onto
the630mm bearer. Their bosses grow3.18mm and matching pan ears, shoulders,
caps and bolts gain3.18mm locally before the common26mm lowering. Rear
keeper shapes translate down26mm without a shape change. Front shim bottoms
areZ780.5; their tops follow the sloping pan underside.

The drain leaves the left pan outlet atX128/Y180/Z800.48, turns forward to
X102, then down through a vertical1in full-port motorized valve atY45. The
valve body spansZ642.72–724 and its actuator faces inboard. Downstream hose
starts atZ642.72, stays atX102 past the assist corridor
before moving toX78 atY595. All sections are level or descending; the final
return has a19mm air gap. The red receiver is vented and has no compressor
connection. CV-15HS is not assigned a water-pumping function.

The overflow upper channel now uses three flat welded strips: one44×383×1.9mm
back and two18.1×383×1.9mm sides, fromZ465 to848. It has no separate bottom
cap. The sloping lower return, two side cheeks and53.9×44mm exit deflector
remain at their original heights, preserving theZ410 outlet and19mm air gap
above theZ391 receiver lid. The two unchanged formed support brackets move
down26mm with the pan.

`export_lowered_wet.py` issues the current complete overflow STEP, individual
installed-piece STEPs, mm flat-strip and cheek DXFs, a176.1×44×1.9mm lower-floor
rough blank, and an installed pan-pose overlay. The floor blank corrects the
obsolete40.2mm width to the actual44mm floor. Its small end bevel and installed
slope follow the STEP; the rough rectangle is not a finished cutting template.
The three-strip union and complete nine-piece overflow union match current
source geometry exactly. The unchanged bracket development remains a forming
reference requiring received-steel coupon calibration. The current takeoff
lists all overflow stock once and identifies superseded legacy collector,
gutter, deflector and bracket rows.

The selected [U.S. Solid valve](https://ussolid.com/products/u-s-solid-motorized-ball-valve-1-stainless-steel-electrical-ball-valve-with-full-port-9-24-v-ac-dc-2-wire-auto-return-html)
was listed at$50.42 before unquoted shipping. Its rounded3.2×3×4.3in package
dimensions allocate space; they are not an exact supplier solid or thread
template. The [manufacturer manual](https://file.ussolid.com/content/JFMSV/JFMSV-User-manual.pdf)
allows gravity-fed use. The2-wire NC auto-return must charge energized for at
least60seconds before reliable power-off return. Actual unions, permitted
mounting orientation, pipe support and isolated controller wiring remain
acceptance items. The maximum ambient temperature is40°C.

Six472×94.3×1.9mm steel screen sections protect the inboard rail faces. Their
X75–76.9 andZ1013–1107.3 envelope clears moving hardware which invalidated a
single tall fixed shield. These are direct splash screens. Complete HMS
module protection still requires compatible manufacturer wipers or bellows;
the screens are not a sealed enclosure or tested fume-control system.

Each section has one welded clip and two removableM6 fasteners. Before the
bed tilts, transfer sections in orderL1,L2,L3,R1,R2,R3 to the two under-pan
racks. The rear section first moves250mm forward while still outside the ATC.
The sections turn across the center and use the corridor matching the bed
position: Y−114.2..−63.1 with the flat bed, orY25.8..76.9 with the bed positively
pinned upright. They lower first
to200mm to clear the low front crossbar, then move behind that crossbar before
lowering to their storage level. Racks hold all sections inside the machine
atY100–572, with lower edges at80/280/480mm. The same12fasteners retain them
through their existing clip holes in storage. Head tooling must be removed,
the bed empty and at its selected endpoint, and common head parkedX975/Y1275/Z250
throughout. Restore both front stops before restoring the guide sections.
The fixed rack webs are now630.5mm tall; anchor-flange bottoms areZ698.6,
matching the lowered front pan bearer. Storage ledges and guide-section poses
remain unchanged.

The guide fabrication schedule is explicit: six screen panels, eighteen clip
plates and fourteen rack plates, all1.9mm plain steel. Each clip uses three
welded flats; each rack uses one perforated web, two edge returns, one drilled
anchor and three ledges. Eight mm DXFs define their actual outlines and holes.
Their assembled unions reproduce all six guide sections and both racks with
zero difference from source solids. Clip/rack assembly references are
nonadditive; the individual flat-stock rows control material quantities.
These parts use welded joints and require no bend allowance.

`utility_parts(guards_fitted=True)` returns retained wet equipment, the new
drain and fitted guide sections. `guards_fitted=False` returns the actual
stored sections and fixed racks for changeover. Generated check reports state
the scope and source hashes. Neither supplier fit, hot-water rating,65L usable
receiver capacity, real gas-spring fall control nor controller interlocks are
established by nominal collision checks. Received-material bracket forming
calibration, actual slot fit, weld distortion and weld qualification are still
required before fabrication release. The overflow and guide flat stock and current installed poses have
their own source-bound report in`output/lowered-wet-fabrication-check.json`.
