# Small machine: removable rear ATC dock candidate

This variant preserves the original 800 × 1000 × 100 mm machine and all frozen Rev I artifacts. It adds a **reviewable frame-supported dock candidate**, not a verified RapidChange kit or finished automatic conversion. No parts have been ordered and no machine files have been flashed.

![Actual candidate CAD](output/SMALL_ATC_CONTEXT.png)

- [Dock STEP](output/step/SMALL_ATC_DOCK_CANDIDATE.step)
- [CAD source](build_small_atc.py)
- [Bounded fit report](output/fit-report.json)
- [Bare-carrier continuous route proof](output/carrier-route-report.json)
- [Preview input/output binding](output/preview-verification.json)
- [Part operations](output/part-operations.json)
- [Manufacturer research and price conflict](../common/atc/README.md)
- [Reserved controls interfaces](../common/controls/ATC-INTEGRATION.md)

## Space and structure

The carrier uses a 906 mm length of 2 × 2 × 0.120 inch square tube, two steel wings and a **560 × 180 × 6.35 mm undrilled shelf**. Its tube ends at X122/1028 leave 2 mm clearance from the fixed pin blocks during extraction. Two proposed welded angle seats connect to the inside faces of the existing upper frame tubes. Four independent hard pads support the carrier, with three primary pads and a fitted fourth. A round/diamond locator pair establishes lateral position. Four M6 drawbolts clamp the carrier; the locator pins are not vertical supports.

The shelf occupies X295–855 / Y950–1130 / Z959.8–966.15 mm. The crossbeam is behind the MDF at Y1130–1180.8. The carrier underside clears the finished MDF by **1.0 mm nominally**, so this layout depends on bed flatness, squareness, clean surfaces and limited deflection. It is a packaging candidate, not a proven operating gap. The new frame welds and carrier stiffness still need load-based qualification; no strength rating is implied by a valid STEP.

The fixed blocks have Ø11 × 6 mm counterbores for flush M6 heads, and the receivers use M5 tapped holes for top-down screws. The ATC-specific left/right receiver parts move their outer M5 columns 5 mm inward to retain full bearing after the outer carrier wings are trimmed for turning clearance. Eight M5 × 16 ISO7380 button heads use the conservative Ø9.5 × 2.75 mm envelope from [HPC Europe's dimensional sheet](https://shop.hpceurope.com/pdf/gbPDFauto/BHC.pdf). Both locator attachments use match-reamed Ø4 dowels; clearance screws alone do not establish repeatability. Installed fits and pin clocking follow the [common locator interface](../common/location/README.md).

The final metal stack uses fixed seat Z964, receiver underside Z978, receiver top/wing underside Z990 and wing top Z996.35. Each 26 mm support pad bears directly against the wing. The CAD calculation checks all four 20 × 14 mm bearing footprints minus the clearance bore. It also records 5.25 mm material beyond each outer M5 head and 6 mm beyond each outer M6 washer. These are geometric bearing checks, not a bolt/weld capacity rating. The `receiver_underside_mm` metadata refers specifically to the receiver, not the low shelf or tube.

With the dock deployed, the proposed full-Z **nominal tool-axis rectangle is 800 × 788.6 mm**, X175–975 and Y121.4–910. It still needs a complete sweep with actual tools. It is not a qualified work envelope or a promise that every stock edge or clamp is machinable. The earlier suggested Y940 rear cutoff is insufficient at low Z: the spindle body's 32.5 mm radius approaches the plate starting at Y950. The Y910 limit retains a nominal 7.5 mm planar clearance. Above Y910, motion belongs to a dedicated retract-and-ATC procedure; it is excluded from ordinary routing.

The inherited spindle lower envelope at full retract is Z1060. Relative to the magazine shelf at Z966.15, that gives **93.85 mm apparent clearance**; the crossbeam is higher, at Z1003.8. Its simplified geometry does not identify the actual nut face, installed cutter tip or RapidChange socket datum. Consequently it does **not** prove the manufacturer's 90 mm clearance requirement or an engagement move. The magenta 520 × 120 × 120 mm cage is an unverified webpage-metadata allocation. It must never be machined or bought as if it were supplier CAD.

## Verification boundary

The fit report checks 63 dock solids and STEP readback, internal interference, six explicit router poses against the complete inherited machine, and the unverified allocation volume at a retracted approach pose. Five intended placements are clear. It deliberately includes the rear low-Z case as a rejection case: the dock occupies part of the original travel. The 120 mm high allocation volume also intersects the retracted spindle; that scenario cannot be accepted as a working magazine envelope. These are bounded static checks, not a continuous routing-envelope proof. A center X575 / Y910 / Zlift0 case is separately recorded in the carrier-route report.

The separate bare-carrier handling proof covers 17 named moving parts through five continuous segments (85 individual solid/segment checks). Exact minimum distances and conservative displacement bounds cover the paths. The two pins during coaxial extraction use an analytic containment check: maximum pin Ø9.995 versus minimum installed bush Ø10.013, with a narrowing tip and Ø12 wing clearance. The continuous turn stays inside a conservative X59.596–1090.373 / Y414.627–1445.404 mm envelope; this follows face-corner trigonometric extrema, not sampled endpoint acceptance. No actual magazine, leads or lifting apparatus is included.

Frozen Rev I source and acceptance reports are not overwritten. The new carrier weldment is exported as one connected solid. Its magazine hole pattern remains blank. The cage is shown in the context mesh, not included as fictitious purchased parts in the dock STEP or BOM.

## Removal, protection and reinstallation

The checked initial state is manual and unloaded: stop and isolate spindle operation, remove cutting tools, place the gantry at Y275 / X575 / Zlift100, disconnect identified magazine electrical connectors and remove four carrier drawbolts plus four washers. Small-hardware transfer and human access are not included. The 17 moving metal parts, including the carrier, have approximately **10.16 kg nominal mass** at steel density 7850 kg/m³; actual magazine, tools, cables and hardware variation add to this.

The bare assembly has a continuous geometric route entirely within the machine footprint:

1. Lift 20 mm to disengage the locating pins.
2. Translate 225 mm forward in Y.
3. Lower 1 mm so the receiver tops remain below the stationary Y datum strips during the turn.
4. Turn 90° counterclockwise about X575 / Y930.
5. Lift 700 mm into an overhead allocation, ending approximately X540–780 / Y415–1445 / Z1672–1722.8 mm.

This establishes an internal geometry option, **not supported parking or a complete ATC conversion**. Positive suspension, a stationary overhead rest, load restraint and protection have not been designed or rated, and no owned hoist is assumed. The actual magazine and its cover/cord envelope must be added to the proof. A lowered rear storage proposal was rejected; it is not the proposed solution. Do not install the frame seats until the overhead support/transfer mechanism and actual magazine fit are qualified. The original machine remains the fallback without this retrofit.

For plasma mode the HDPE magazine, tools, optics and electrical connections need verified removal into a dry protected enclosure, or a separately qualified heat/splash barrier. The manufacturer's dust cover is not claimed as a plasma splash shield. No air purge, waterproof rating, automated drawer, lift or removal interlock is implied by this CAD. The reserved dock-presence input is only an interface plan until an actual device and location are designed.

On reinstallation: clean the metal datums, seat the carrier, clamp against the pads without lifting a datum, inspect tool clearance, then verify/reprobe the pocket references before enabling M6. An ATC return target of ≤0.05 mm is proposed for a measured 20-cycle test. It is not established performance. Homing repeatability, gantry yaw, temperature, spindle tram and pocket calibration require their own alignment allowances.

## What closes the remaining design

1. Select the exact current ER11 linear magazine and obtain its dimensioned CAD, mounting pattern, cover sweep and electrical specification.
2. Measure the spindle nut, actual retract/engagement datums and available tool-length travel; identify and verify the VFD reverse and low-speed behavior.
3. Replace the cage with supplier geometry, drill the carrier only from that verified drawing and verify continuous approach/retreat with real tools.
4. Design the positive lifting/resting fixture and dry protection for the checked overhead allocation; then repeat the route with the actual magazine and all leads. The existing no-outside-footprint requirement has not been relaxed.
5. Qualify the frame retrofit, pads, deflection, installed locator fits and repeatability; implement and bench-test the separately documented I/O and M6 logic.

The approximately $700 magazine allowance excludes shipping, tax, toolsetter, additional nuts/collets, the dock, electronics and fabrication. There is no defensible delivered total for this optional addition yet.
