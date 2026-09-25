# Fabrication operations for the Rev F solid model

All dimensions are millimeters. The STEP geometry and `part-operations.json` distinguish custom parts from purchased clearance envelopes. The files are an engineering definition; purchased interfaces marked **GUARDED** are not released for fabrication.

## Stock and datums

- Main tubes are nominal 2 × 2 × 0.120 inch steel: 50.8 mm outside and 3.048 mm wall. Square tube corners in the model are idealized; do not treat an unmachined tube face as a precision rail datum.
- Braces use 1 × 1 × 0.083 inch tube: 25.4 mm outside and 2.1082 mm wall.
- Custom 6, 8 and 12 mm plate dimensions remain metric. Finish 6 mm from 1/4 inch stock, 8 mm from 3/8 inch stock, and 12 mm from 1/2 inch stock. Do not substitute a thinner imperial plate without updating the adjoining datums.
- Module rails are 2 × 2 × 0.120 at 1290 mm; crossmembers are 2 × 1.5 × 0.120 laid flat at 938.4 mm. Rail caps use actual 5/16 inch thickness, 7.9375 mm. The MDF sub-bed is two layers of 1/2 inch (12.7 mm); spoilboards finish 3/4 inch stock to 19 mm.
- Module rail tops are Z890.8 on the Z840 ledgers; crossmember tops Z895.4; surfaced MDF top nominal Z920.8; the aluminum deck is Z940.8; the 19 mm spoilboard is Z959.8. Plasma slats are Z850. Raised rail-cap tops are Z1063.9375. There are no ground receiver faces in Rev F: the in-machine MDF surfacing pass replaces that datum work.

## Reading the DXFs

`CUT_OUTER`, `CUT_HOLES` and `CUT_INNER` define through-cut geometry. Layers beginning `MILL_` or `CSK_` identify secondary machining and must not be included in a through-cut laser program. `MACHINING_NOTES` gives the machining side, depth and thread callouts.

The pan-bearer hanger STEP uses an 8 mm nominal thread envelope. Its DXF correctly uses a **6.8 mm pilot**, followed by **M8 × 1.25 through tapping**. Other guarded supplier mating patterns must be measured or sourced before drilling. A generic drawing file is not machine-specific CAM or G-code.

Some compound guard notches are issued as individual STEP solids only. Use their local solid geometry and part notes to create the sheet layout; no ambiguous overlapping through-cut contours are supplied.

## Machined details

- Foot pads: 80 × 80 × 12.7 mm, four 9 mm anchor holes and a central 32 mm diameter pocket **2 mm deep from the top**. Floor-anchor selection is site-specific.
- Drawdown sleeves: 18 mm outside diameter, 9 mm bore, 50.8 mm length, four total, welded through both rail walls and finished flush both faces. No counterbore: the M8 × 70 head seats on the rail top outside the deck plan.
- Lift ears: four 6 mm plates, 50.8 × 100 mm outline with Ø16 hole at 75 mm; continuous 3 mm weld around the rail end perimeter.
- MDF layers: Ø5.5/Ø5.7 through holes per the DXF; lower layer takes Ø16 × 6 underside pockets at the fifty deck-screw stations, upper layer takes Ø12 × 6 top pockets at the sixteen frame-screw stations. Surface the assembled top 1.0 mm nominal IN THE MACHINE after the frame screws are torqued.
- Deck strips: ONE saw cut to 1197 mm. No drilling, no keyholes, no tie-bar slots. Fifty M5 × 25 ISO 7380 button screws with Ø15 fender washers enter from below into DIN 562 bottom-slot square nuts.
- Spoilboards: one left and one right, 465.6 × 1197 × 19 mm from a single 1220 × 2440 sheet. The X 108–1039.2 trim is a hoist-clearance requirement; do not substitute full-width boards.
- Spoilboard screws: M5 × 20 DIN 7991 into DIN 562 top-slot nuts. Counterbore 10 mm diameter × 3 mm, then countersink a further 2.25 mm at 90 degrees. Heads sit 3 mm below the initial board surface. Limit routine surfacing to 2 mm before resetting or replacing the board.
- Sand plugs: M20 × 1.5 threaded shank, 10 mm long; 28 mm diameter × 6 mm head with a 6 mm hex socket, 4 mm deep. The mating bung is 30 mm outside diameter × 10 mm long; drill 18.5 mm before tapping M20 × 1.5.

## Assembly and verification

Complete welding and coating before adding dry ballast. Do not weld a filled tube. Measure actual ballast mass rather than assuming complete packing. The ledger fill ports sit at Y1370, behind the module rail span. Seal the MDF edges and underside after the surfacing pass; the top face stays bare under the aluminum.

The pan has a 1% rearward slope. Its cradle webs follow that slope; fit them without pulling the pan out of shape. Weld and water-test the pan and reservoir before installing controls. The reservoir is permanently vented and must never be connected to compressor pressure or vacuum.

Float carriers have adjustable mounting slots and removable guards. Their modeled mounting heights are initial settings, not the electrical trip planes. Wet-calibrate minimum, normal, high-high and reservoir-low levels. The low pan sensor plus timed draining does not prove a perfectly dry pan.

The upper pan float guards begin at X978, only 3 mm outside the nominal maximum head-axis position X975, at Y600, Y660 and Y720. The modeled router body is above their Z910 upper extent. **The eventual torch body and cable sweep must be checked against these guards before claiming the full 800 mm nominal axis travel as usable plasma cutting width.** An inboard torch-mount offset may resolve the interface, but its geometry depends on the actual torch. No such offset or torch bolt pattern is assumed in this package.

The controls cabinet is a conservative 508 × 406.4 × 203.2 mm purchased envelope standing upright in the front bay (X371.8–778.2, Y251.8–455, Z165–673), door forward, on a bolt-on 1 × 1 tube cage under pan bearers 1 and 2. Transfer-drill the enclosure back-panel pattern onto the cage rails; pre-drill the stringers Ø5.5 so the #12 screws self-drill only the bearer walls. A clip-on 1.5 mm drip cap covers the top in the 6.2 mm gap below the bearers. Thermal layout, glands and the internal panel remain open. Routine service is through the front door with power isolated — no draining, no pan or bed removal.

Follow the independent module-hoist procedure and its sampled swept-volume check. Remove all four drawdowns to the tray and take up sling slack before the last bolt. The bed check does not model rigging and does not certify the separate handheld spindle transfer.
