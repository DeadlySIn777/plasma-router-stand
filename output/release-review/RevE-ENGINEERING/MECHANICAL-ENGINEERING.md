# Rev F mechanical definition and independent checks

All dimensions are millimeters. Coordinates use X left to right, Y front to rear and Z upward. The source model and its generated drawings govern individual part geometry. This document explains the load paths, tolerances and assembly sequence. It does not claim that unknown purchased interfaces have been verified.

Rev F replaces the six-cassette bed with a ONE-PIECE hoisted module. The purchased 20100 strips are cut-only parts; flatness comes from an in-machine surfacing pass on the MDF sub-bed, not from machined receiver seats.

## Bed dimensions and operating datums

| Item | Dimension or position |
|---|---|
| Nominal X/Y/Z travel | 800 / 1,000 / 100 |
| T-slot bed | 1,000 X × 1,197 Y, ten butted strips |
| Strips | Ten 100 × 1,197 × 20, ONE saw cut each, no drilling |
| Strip origin | X 73.5; Y 76.5 |
| Module side rails | 2 × 2 × .120 tube, 1,290 long, X 55–105.8 and 1,044.2–1,095, Y 30–1,320, on the ledger tops Z 840 |
| Crossmembers | Four 2 × 1.5 × .120 laid flat, 938.4 long, centers Y 75/475/875/1,275, top Z 895.4 |
| MDF sub-bed | Two 12.7 layers, 938.4 × 1,197, X 105.8–1,044.2, Y 76.5–1,273.5, top Z 920.8 |
| Float notches in MDF | Right edge, X ≥ 1,012, Y 565–755 and 1,162–1,232 |
| Optional spoilboards | Two 465.6 × 1,197 × 19, X 108–1,039.2 |
| Bare aluminum top | Z 940.8 (unchanged from Rev E) |
| With 19 mm spoilboard | Z 959.8 (unchanged) |
| Permanent plasma slat tops | Z 850 |
| Lift ears | Four, 6 mm plate on the rail ends, hole Ø16 at Z 916, top Z 941 |
| Drawdowns | Four M8 × 70 at (80.4/1,069.6, 49.6/1,300.4), outside the deck plan |
| Locators | Two Ø10 dowels, (80.4, 150) and (1,069.6, 1,200), 6 mm into ledger bushings |
| Nominal welded frame | 1,150 X × 1,450 Y |
| Fixed side brace extent | X −28.4 to 1,178.4 |

The stock bed is larger than the cutting travel. Slots run the full 1,197 with no cross seams. Strip width stack (ten widths at 100 ± 0.2) is absorbed at the two free edges; nothing indexes off the outer strip faces.

The front opening is the module exit: the pan front is at Y 105 and the front crossmember is lowered to Z 100.8–151.6, leaving the window between the front legs (1,048.4 wide) open from Z 151.6 to the top rails. The module exits forward through it at handling height on the owner's overhead winch.

## Load paths and restraint

Cutting loads pass from the strips into the glued two-layer MDF sub-bed, into four flat 2 × 1.5 crossmembers, into two 2 × 2 rails that bear CONTINUOUSLY on the fixed receiver ledgers. There are no feet, seats, shims or machined receiver plane: after the ladder and MDF are installed, the router faces the MDF top in place (1.0 mm nominal skim), so ledger, weld and stock tolerances never reach the aluminum.

Two diagonal Ø10 dowels locate the module; they press through both rail walls and project 6 mm into bushing holes in the ledger top walls. Four M8 × 70 drawdowns clamp the rails through welded OD18/ID9 compression sleeves into DIN 929 weld nuts under the ledger top walls. All four sit OUTSIDE the deck plan (Y 49.6 and 1,300.4), reachable straight down with a socket. Torque 12 N·m on clean, dry seats.

Strip fastening: each strip carries five DIN 562 square nuts end-loaded into its bottom slot; M5 × 25 button screws with Ø15 fender washers enter from BELOW through the MDF (Ø16 × 6 underside pockets in the lower layer). Fifty screws total, installed with the module out of the machine on stands after the surfacing pass. The 0.35 N·m thin-lip torque discipline of Rev E no longer exists — the screws clamp MDF, not aluminum lips, and the keyhole anchors, retaining washers and jam nuts are deleted.

The MDF layers glue together and fasten to the crossmember top walls with sixteen #12-14 × 32 self-drilling screws in Ø12 × 6 top pockets; heads finish 3 mm below the pre-surfacing MDF face, below the maximum reface depth.

Both spoilboards ride the module through the hoist. Their trim to X 108–1,039.2 is a hoist-clearance requirement (guide-shoe bands and block-bolt heads), not an aesthetic choice; nominal cutting X 175–975 lies fully on the boards. Do not substitute full-width boards.

## Independent elastic screen

The reproducible calculations are in `strength-screen.py` and `strength-screen.json`. They use steel E = 200 GPa and aluminum E = 69 GPa and report their assumptions explicitly.

| Check | Calculated result |
|---|---|
| One 2 × 1.5 flat crossmember, 938.4 mm simple span, 100 N central load | ~0.077 mm deflection |
| One 20100 strip, one 400 mm bay, simply supported, 100 N central load | ~0.071 mm deflection |
| Conservative sum of those two deflections | ~0.148 mm |
| Same sum at 500 N local vertical load | ~0.74 mm |
| Ideal side-brace pinned buckling load | 42.4 kN |
| Ideal rear-brace pinned buckling load | 24.0 kN |
| M8 sleeve compression at estimated 7.5 kN preload | About 39 MPa |
| X actuator moment: 250 N drive force at 38.05 mm offset | 9.51 N·m |
| Y actuator moment: 250 N drive force at 25.35 mm offset | 6.34 N·m |

The two-member sum deliberately excludes what the Rev F sandwich actually adds: the strip is CONTINUOUS over four supports (not simply supported in one bay), the glued MDF spreads point loads across several strips and members, and the rails bear continuously instead of spanning. Each effect reduces the real number substantially; the screen is a bounding case, not a prediction. The Rev E screen printed smaller single-member numbers under different spans and cannot be compared line-for-line. Prototype-verify: MDF screw pull-out with the selected screws, TEK engagement in the 3.048 wall, and bed indicated flatness after the surfacing pass.

The profile section property comes from the reconstructed supplier cross-section, including its voids. It is not manufacturer-certified. These member calculations exclude joint rotation, complete frame deformation, gantry torsion, guide preload, spindle/tool compliance and cutting dynamics. They must not be advertised as a whole-machine accuracy or load rating.

The stationary frame receives the sand ballast. Sand increases mass and damping; it is not credited with increasing the elastic tube section stiffness. Do not fill the bed module or the gantry. Fill only after welding, cleaning and coating, and weigh the actual charge. The ledger fill ports are at Y 1,370, behind the module rail span.

The front crossmember is lowered for the module exit, so lateral racking resistance must come through the welded rear brace, the side braces, the pan-bearer connections and the continuous frame. The side and rear braces use 1 × 1 × .083 inch square tube with 160 × 160 × 3 gussets and sufficient weld overlap. Their ideal axial checks do not replace an assessment of the complete weldment.

## Motion support requirement

The HMS40 modules cannot be accepted as the only router guides on the basis of their 20 kg horizontal load label. The manufacturer's listed moments are MY 13, MP 12 and MR 15 N·m. A 100 N lateral tool force at a 250 mm lever arm is 25 N·m before head weight.

The design therefore retains the user's HMS40 actuators as drives and adds independent linear guides carrying the gantry and head. Floating axial links connect the drives to the guided structure without intentionally transmitting the tool moments into the small actuator carriages. Two Y blocks on each side have 180 mm center spacing. Two X rails have 60 mm vertical separation, with two blocks per rail at 160 mm spacing.

The floating links retain a drive-force moment because their pins sit above the actuator output plane. At a 250 N axial screen load, the final X offset of 38.05 mm produces 9.51 N·m and the Y offset of 25.35 mm produces 6.34 N·m. These isolated static components are below the least listed 12 N·m moment; combined loading, impact and fatigue are not thereby qualified. Set acceleration from measured moving masses and align the links so router support loads do not pass through the drive shoes.

Module-hoist clearance constraints on the motion structure: all retained Y carriage/shoe hardware bottoms stay at or above Z 1,011, and the inboard-protruding block-bolt heads reach X 106.5 / 1,043.5. The 60 mm handling lift places lift-ear tops at Z 1,001 (10 mm clear) and the trimmed spoilboard tops at Z 1,019.8 between the shoe bands. Recheck the sampled path if any of this hardware changes.

The iMetrx guide drawing's rail-hole pitch and end dimensions are inconsistent for the 1,500 mm rail length. Transfer-drilling from an inspected purchased rail is an explicit fabrication operation, not an invented exact hole pattern. The Z slide's plan dimensions are now imported from the owner-supplied listing drawing (body 219 × 80, carriage 90 × 50, φ7/φ5 holes at 70 across); the slotted TOOL_ADAPTER_110 absorbs the undimensioned along-travel pitch and stays PROVISIONAL until the carriage is transfer-verified. The mounting-plane-to-output height remains an explicit 80 mm assumption until the unit is measured; do not fix head-mount positions from it alone.

## Fabrication and assembly sequence

1. Cut, deburr and identify all tube and plate parts. Keep guide datums and the pan/tank sealing faces free of weld spatter. The ten 20100 strips take one saw cut each (1,220 → 1,197) and nothing else.
2. Fixture the six legs, side rails and front/rear ties on a verified reference surface. Tack, measure both diagonals, alternate welds, and recheck after cooling. Weld the lowered front tie, rear/side braces, gussets and tank supports before machining or shimming the final datums.
3. Weld the M16 foot closure/nut assemblies and install the custom feet. Set all six pads into contact.
4. Drill the four Ø18 drawdown pockets and two Ø10.05 dowel bushings in the ledger top walls; weld the four DIN 929 nuts inside. Protect the bores from paint. No receiver pads, no Z 846 shimming — the surfacing pass replaces that datum work.
5. Weld the module ladder: two 1,290 rails, four flat crossmembers, four lift ears, four compression sleeves. Stress-relieve, then press the two dowels through the rail walls. Rail tops are NOT precision surfaces.
6. Fit the pan-bearer hanger/endplate joints, cradles, pan hold-downs, slat combs, pan and vented reservoir. Follow `WATER-CONTROL.md` for plumbing and controls.
7. Finish the guide mounting datums; fit the independent guides, gantry and HMS drives per the motion section.
8. Set the ladder on the ledgers (dowels engaged), torque the four M8s. Screw and glue the two MDF layers to the crossmembers (16 TEK screws, heads 3 mm deep). SURFACE the MDF top 1.0 mm nominal in the machine with the router head.
9. Hoist the module onto stands. End-load the square nuts, place the ten strips on the surfaced MDF, and drive the fifty M5 × 25 button screws up from below. Verify an actual nut fits the supplied slot before purchasing all hardware. Reinstall the module; the dowels re-establish position.
10. Optionally fit the two spoilboards (twenty M5 × 20 DIN 7991 into top-slot nuts, heads 3 mm deep). Weigh the finished module, verify the 4-leg sling geometry, and perform a slow first hoist along the sampled path with no loose cables or plumbing in the window.

## Module exchange

The actual poses and sampled collision results are in `swap-path-checks.json`; the current JSON status controls whether the modeled route passed. The checks cover solid interference, not a proof of continuous clearance or rigging behavior.

Preconditions: machine isolated; spindle or torch removed to its cradle; gantry parked at the rear datum; water drained; four drawdowns removed to the internal tray; sling slack taken up BEFORE the last bolt comes out.

The route is three pure translations, one rigid body: lift +60, translate −Y 1,400 out the front window, hoist +500. Reverse to install; the dowels engage on the final descent. Key modeled clearances at handling height: crossmember undersides pass the Z 910 float backrails by 7.3 mm; lift ears pass 10 mm under the parked guide shoes; trimmed spoilboards pass between the shoe bands. Fabrication variation and debris reduce these numbers — keep the pan floats and their guards undamaged and the route swept clean.

The module estimate is ~86 kg including both spoilboards, against a 567 kg (1,250 lb) winch: better than 6× margin. Rigging (sling legs, hook height ≥ 1.2 m above the ears, winch anchorage or trolley track) is owner scope and is not modeled. Remove router chips and MDF dust from the pan, slats and rails before enabling plasma; no automatic sensor can verify cleanliness.
