# Rev D T-slot cassette fit review

Date: 2026-09-24. Scope: independent dimensional review of the current Rev C geometry and the proposed six-cassette T-slot replacement. This is a design-study check, not a fabrication release, verified load rating, or CAM package.

## Proposed geometric change

Use ten nominal 1,220 mm stocks of the selected 20 × 100 mm extrusion, cut into thirty nominal 397 mm lengths. Five strips make each nominal 500 X × 397 Y mm cassette; six cassettes form a 1,003 X × 1,197 Y mm deck with 3 mm seams. The nominal cutting travel remains 800 X × 1,000 Y mm. The physical bed is not the reachable tool envelope.

The original assembly coordinates use the chassis front-left corner as X0/Y0 and the nominal floor as Z0. Keep that convention for the study:

| Item | Rev D candidate dimension / location, mm |
|---|---|
| Cassette X origins | 73.5 and 576.5 |
| Cassette Y origins | 76.5, 476.5 and 876.5 |
| Overall deck X limits | 73.5 to 1,076.5 |
| Overall deck Y limits | 76.5 to 1,273.5 |
| Beam centerlines Y | 75, 475, 875 and 1,275 |
| Each paired beam bearing width | 101.6 along Y |
| Finished paired beam length | 1,044 along X, from 53 to 1,097 |
| Beam top / extrusion bearing datum | Z920.8 |
| Bare extrusion top | Z940.8 |
| Top with nominal 19 mm spoilboard | Z959.8 before surfacing |
| Optional cassette tie bars | Two nominal 500 × 25 × 6, local Y75–100 and Y297–322, underside Z914.8–920.8 |

The tie-bar sizes and positions are geometric candidates. Their material, fastening pattern, head clearance and connection strength are unresolved. They must not be located in the beam-bearing zones. Vendor profile wall and slot drawings must govern drilling and T-nut selection.

## Checks that pass at nominal dimensions

- Each 397 mm strip has 49.3 mm bearing length at each end. The clear span between adjacent bearing edges is 298.4 mm. This is geometry only; extrusion deflection and local wall strength are unverified.
- The new bed is centered across the chassis. It sits 20.5 mm inside the finished beam end at both sides. The deck's 1,003 mm width does not have to fit the 1,005 mm cabinet opening because the cassettes are stored separately.
- A cassette stores with **500 mm vertical and 397 mm horizontal**, not 500 mm horizontal. Six panels in two banks of three fit the nominal original storage outline: X origins 130 and 623; Y origins 525, 580 and 635; bottom Z150. Top Z650 remains below the cabinet top Z705.
- The candidate 20 mm extrusion plus 6 mm underside tie bars plus 19 mm MDF gives a 45 mm packed depth before protruding hardware. The former cassette was 52 mm deep. The original 55 mm storage pitch therefore has 10 mm nominal free depth per slot with the proposed candidate stack. Folded handles and protruding fasteners still require validation.
- The full stored beam needs its section and 30 mm riser feet included, not just a sloping centerline. Rotating a 1,044 mm beam with a 50.8 mm section and 30 mm foot projection through 25 degrees makes the original X85 origin intrude past the cabinet's left inside edge. The CAD-study agent found that X100 clears the physical side; the recommended centered candidate is approximately X111.5, giving a predicted X90.0–1,065.1 envelope and approximately 15 mm clearance each side within the conservative X75–1,080 usable box. At Z185 origin the predicted top is about Z672.3, below the Z700 usable ceiling. These values remain subject to its full solid and rack-hardware collision check.
- The pan exterior spans X115–1,035; the ledgers occupy X50.8–101.6 and X1,048.4–1,099.2. There is 13.4 mm nominal lateral pan-to-ledger clearance on each side.
- The beam underside is Z870; plasma slat tops are Z850, giving 20 mm nominal vertical clearance. The pan rim is Z835. The T-slot replacement itself introduces no direct pan contact in the nominal envelopes.
- One 1,220 mm stick yields three 397 mm strips: 1,191 mm net plus three 3 mm saw kerfs consumes 1,200 mm, leaving 20 mm for end trim, stock tolerance and offcut. Actual cut plan must use the saw's measured kerf and received stock length. No spare full strip is included.

## Critical defects and unresolved interfaces

### 1. Existing beam clamp solids intersect the bed

`build_bed_system.py`, function `beam()`, places clamp solids at X67–85 and X1,065–1,083, Y centerline ±18, Z921–928. These already overlap the former panel corners. The proposed deck increases the X overlap to 11.5 mm. This is an actual interference in the schematic geometry, not a hypothetical tolerance issue.

**Bounded study fix:** omit the placeholder clamp solids and mark the beam-retention interface HOLD, or represent a selected retention assembly entirely below the Z920.8 bearing plane with accessible hardware. Do not silently move an unspecified clamp into an apparently clear area and call its manufacture resolved. All beam and panel retention, contact pads and locators need actual geometry before release.

### 2. Independent head locations remain required

The bare T-slot plane is 90.8 mm above the plasma slat plane. With nominal 19 mm MDF the difference is 109.8 mm, exceeding the 100 mm Z stroke. A torch tip starting at Z850 would only reach Z950 after an ideal full 100 mm retraction, below the Z959.8 MDF plane.

**Bounded fix:** retain removal of the torch before fitting the dry bed and keep separate indexed router and torch mounting references. Do not infer tool clearance from stroke alone. Confirm tool gauge length, work thickness, homing reserve, dust shoe, clamp geometry and full travel before fixing the head datum. The old 154.2 mm gantry-to-bed clearance becomes 167.2 mm above nominal MDF, but that is a structural gap, not usable cutting thickness.

### 3. The actual spindle is not modeled

`build_bed_system.py` renders a generic 72 × 72 × 180 mm spindle box. The selected ER11 spindle evidence says 65 mm diameter × 259 mm length. The generic body is therefore 79 mm shorter in its axial envelope. Tool, collet, mounting position and cable outlet remain unspecified. The Z module is also an approximate 80 × 38 × 219 mm body with a schematic motor/coupling extension.

**Bounded fix:** replace the generic spindle with a correctly sized supplier envelope and label the mounting datum HOLD until its dimensioned drawing or measurements arrive. Import or reconstruct the module carriage and mounting patterns from verified drawings. A rendered block touching another block is not an attachment design.

### 4. Tube-pair load sharing is not established

At a shared row boundary, the upstream panel ends on the upstream tube and the downstream panel starts on the downstream tube. Each panel therefore bears on one tube of each pair. End diaphragms alone do not prove equal load sharing under a midspan point load. The former 0.023 mm paired-beam deflection claim was conditional; its 0.047 mm single-tube case is the more conservative beam-only case until the connection and load distribution are modeled. Neither number is a whole-bed stiffness or accuracy rating.

**Bounded fix:** retain the full support/load path in the study; define cross-ties, cassette connections and machined/shimmed bearing datums before structural checks. Obtain the selected extrusion section properties and allowable connection details, or test a representative supported assembly. Do not substitute an unspecified solid 20 × 100 bar's inertia for the hollow extrusion.

### 5. Pan and slat support geometry is incomplete

`build_bed_system.py` draws a flat 3 mm pan floor at Z735, while the design text calls for a 1% slope with floor elevation Z735–747. Pan bearer tops are Z730, leaving an unmodeled 5 mm gap at the low point. The slats are floating boxes without comb racks or retention details.

**Bounded fix:** add a defined cradle/shim load path that supports the actual sloped floor without distorting it, and add the comb/rack parts. Drain boss, weld preparation, bend relief, sealing and hose access must follow the actual pan construction. The study can show the slope and clearance envelope while these interfaces are HOLD.

The original cabinet sidewalls also collide with the pan bearers: sidewalls at X65–70 and X1,080–1,085, Y55–755, Z130–705 intersect bearers at Y175–225 and Y675–725, Z679.2–730. Notch the nonstructural cabinet sidewalls around those crossings or revise their top-edge profile while preserving structural bearer positions. The stored beam's predicted Z672.3 top has only about 6.9 mm clearance to a crossing pan bearer's Z679.2 underside; protruding retention hardware and rack thickness must be checked. These defects are separate from the cassette size, which fits its nominal storage outline.

### 6. Reach and collision envelopes remain unproven

The module stroke labels are not enough to locate the spindle center over the full nominal work area. Supplier carriage center offsets, hard-stop clearance, homing allowance, the head's Y offset and motor/cable envelopes are not verified. Gantry bending, adapter stiffness and module moment ratings also remain open.

**Bounded fix:** define a tool-center-point coordinate system from actual mounting drawings, then check both end positions and swept solids. The present drawing may state nominal axis travel, but may not label the entire 800 × 1,000 mm rectangle a verified usable machining area.

The [KHMOS HMS40 manufacturer page](https://www.khmos.com/high-performance-easy-access/hms40) lists moment values **MY 13 N·m, MP 12 N·m and MR 15 N·m**, explicitly labeled in N·m. Its mounting-axis illustration is still needed to associate those values with this installation. As a screening example only, a 100 N transverse tool load at a 250 mm lever arm produces **25 N·m**; a 50 N load at that arm produces **12.5 N·m**, before head-weight moments and acceleration. The first exceeds every listed moment value; the second is already above the lowest listed value. These forces are illustrative, not an assertion about the user's actual cutting operation, and 250 mm is a provisional screening arm, not a measured supplier datum. Components and combined loading must be checked in the manufacturer's coordinate system. The old render puts the X-module body's mid-height at Z1167 and the candidate MDF plane at Z959.8, a 207.2 mm vertical difference; the actual carriage bearing center and tool offsets are not yet established. Even a 100 N load with a 200 mm relevant arm would give 20 N·m. A 20 kg payload label does not establish adequate cutting stiffness, moment capacity or accuracy. Supplier speed limits also depend on payload and configuration; the headline speed cannot be applied to all loads.

**Readiness consequence:** the selected HMS40 assembly is not yet qualified for the proposed router. Keep it in the vendor-dependent study, but do not release fit-specific mounts or assert CNC cutting capability until moment direction, complete head mass/offset, intended cutting forces, desired deflection and combined-load conditions are resolved.

### 7. Procurement substitutions and tolerances must be coordinated

Five nominal 100 mm strips establish a nominal 500 mm cassette width. The listing's tolerance remark is not a complete dimensional, straightness or flatness specification. Seams and contact pads must accommodate measured stock; do not force five variable strips into an exact-width pocket. US-stock changes in the older BOM also affect dimensions: 1/4-inch end plates require different beam-tube cut lengths than 6 mm plates. The new cassette replaces the old 25 mm welded panel frame and 8 mm plate; those old parts must not remain in Rev D cuts or cost totals.

**Bounded fix:** use one canonical parameter set for the CAD, cut list, BOM and drawings; mark vendor-dependent drilling as HOLD. Keep the 19 mm spoilboard thickness an explicit nominal input; actual US 3/4-inch stock is nominal 19.05 mm.

## Full-machine footprint, not just chassis size

The chassis nominal outline is 1,150 X × 1,450 Y. Existing geometry extends beyond it:

| Existing feature | Coordinate bounds, mm | Consequence |
|---|---|---|
| Gantry beam | X−25 to 1,175 | Overall known width 1,200 |
| Y rail cap plates | X−24.6 to 1,174.6 | Almost the same width as gantry |
| Front/rear feet | Y−15 to 1,464.2 | Overall known depth 1,479.2 |
| Side parked covers | X−8 to −4 and 1,154 to 1,158 | Inside the existing rail/gantry overhang |

Thus the **known nominal static envelope is at least 1,200 W × 1,479.2 D mm**, excluding unmodeled hoses, cable chains, connectors, control-box placement and full motion sweep. Do not advertise 1,150 × 1,450 mm as the complete footprint. No external bed-storage cart is needed in the candidate concept; operator access, hand clearance, removal paths and the lift sequence still need a physical or swept-volume mock-up.

## Files inspected

- `plasma_router_stand/build_bed_system.py`
- `plasma_router_stand/bed_system_pages.py`
- `plasma_router_stand/build_design.py`
- `plasma_router_stand/output/bed-system/design-parameters.json`
- `plasma_router_stand/output/bom/extrusion_amazon.json`
- `plasma_router_stand/output/bom/motion_research.json`
- `plasma_router_stand/output/bom/metals_research.md`
- `plasma_router_stand/outputs/alto-30510/Procurement-brief.md`
- `plasma_router_stand/output/release-review/sources/khmos-hms40.html` (manufacturer page snapshot supplied by root)

This review authorizes no purchases and changes no existing Rev C geometry. The separate Rev D CAD study can implement the bounded geometric candidates above while preserving explicit HOLD status for unresolved manufacture and interfaces.
