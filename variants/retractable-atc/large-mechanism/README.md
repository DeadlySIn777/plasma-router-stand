# 4 × 8 retractable ATC mechanism — development package

This is the large machine's detailed 200 mm retractable-magazine mechanism. It preserves the 1,219.2 × 2,438.4 mm sheet and the 1,320 × 2,550 mm removable bed. It is **not a fabrication release or a verified RapidChange kit installation**. The current status is governed by [verification.json](verification.json), with its exact source and exported-artifact hashes.

## Open the actual assembly

- [Deployed mechanism](deployed-mechanism.step) and [deployed full machine](deployed-machine.step).
- [Parked mechanism](parked-mechanism.step) and [parked full machine](parked-machine.step).
- [Deployed preview](../previews/large-deployed-full.png), [parked preview](../previews/large-parked-full.png), and [mechanism detail](../previews/large-deployed-mechanism.png).
- [Part inventory](parts-inventory.json), [stock and operations](stock-and-operations.csv), and [export summary](export-summary.json).

Gray machine context is the preceding 4 × 8 development layout. Purple bodies are unselected motion/storage allocations. The old magazine block is removed. This package shows the structural adapter strips, not an invented purchased magazine.

## What is built in CAD

Two 350 mm HIWIN-reference rails, four MGN12H blocks and a 300 mm TR8×8 integrated-screw NEMA 17 actuator drive a 200 mm slide. Two rail bars and an open aluminum H-frame replace a heavy solid base plate. The frame attaches through steel saddles, compression sleeves, actual chassis holes and bolts; it does not merely rest on the chassis.

The moving carriage has two raised adapter strips with a 40 mm center opening. Their structural fasteners are modeled. Supplier mounting holes are intentionally absent until the actual kit drawing or measurements exist. A conditional 25 mm-wide central loaded-tool corridor extends 24 mm below the adapter underside. The separate 160 × 600 × 120 mm magazine body allowance is a packaging limit, not a supplier dimension.

Both slide endpoints have hard stops and spring-applied, solenoid-released Ø6 mm pins. Each pin has a bronze guide, carriage receiver, extension stop, retained cross pins, a 45° translating fork cam, a fabricated leaf return, and two separately mounted Panasonic PM-U25-P sensors. The two fixed pin centers are (1550,470) and (1750,530) mm. The free pin at the other endpoint is not proof of locking: its correct position sensor and the corresponding pin sensor must agree.

The outer shutter has a separate screw motor, actual POM guides and 164 mm travel. Its rear guide bridges above the moving nut carrier, clearing the complete slide stroke. A separate guided pin holds the shutter at both detents. The steel shutter, return flange, lift arm and steel ladder form a compatible weldment. The ladder has 10 mm nominal window pitch and a dedicated open detent. **This does not establish a maximum power-loss fall distance.** Coil release delay, acceleration, missed windows and rebound require physical testing.

The three Delta coils have fixed front stops, removable rear axial caps and inset side keepers. Each rear cap uses two actual M3×10 screws through a 4 mm plate into 8 mm blind taps: 6 mm engagement and 2 mm nominal bottom reserve. Removing that cap permits axial body withdrawal while the side keeper and guided plunger remain installed. The body is retained geometrically; no friction clamping force is inferred from nominal contact. The shutter-catch cover and its welded right downstand lift together after four M4 screws are removed; two fixed mounting brackets remain on the hood.

## Dimensions and clearances

| Item | Nominal value |
|---|---:|
| Slide travel | 200 mm |
| Shutter travel | 164 mm |
| Rail length | 350 mm |
| Two blocks per rail, center spacing | 80 mm |
| MGN12H nominal / catalog maximum length | 45.4 / 45.8 mm |
| End allowance with maximum block length | 12.1 mm each end |
| Shutter nut to screw end, open | 10 mm |
| Tallest bonnet to gantry lower chord | 8 mm |
| Hood outer edge to right Y-carriage allocation | 7.5 mm |
| Full-deck routing X-axis centers | 117.3–1462.7 mm |
| Full-deck routing Y-axis centers | 162.3–2737.7 mm |

The full gantry Y sweep and the allocated head over the full deck are screened with the mechanism parked. Low-Z head movement into the dry ATC bay is a separate controlled operation; this package does not claim that every X/Z combination can pass through a parked hood. Final guide, frame and purchased-kit tolerances must be budgeted against these nominal clearances.

## Fabrication files and assembly

Every file in `parts/` is exported from the final solid, including post-construction cuts. For a planar blank, the matching file in `flat/` contains **actual solid sections at the Z values named by each layer**. Thus later roof cutouts, blind bores, counterbores and service slots are represented instead of an obsolete early sketch. These are inspection/CAM-input sections, not a single-depth cut program: do not send all overlaid section layers to a plasma cutter. Use the local STEP and the depth notes in the operations CSV to distinguish through cuts, pockets and tapped bores. Weldments and tubes that are not planar blanks have 3D STEP and stock/operation records; they are not mislabeled as sheet-metal flat patterns.

All threaded cylinders are nominal major-diameter representations. Select the proper tap drill, thread class, cutting allowance and actual bolt lengths in fabrication. MGN carriage M3×12 screws have 3.5 mm head counterbores, about 2.8 mm modeled engagement and 0.7 mm nominal bottom clearance; verify supplied block depth and screw length. Upper M5×12 heads sit flush in Ø9 × 5 mm counterbores; the strip has 1.35 mm of fully supported material below each head. Stand M5 taps are 15 mm deep from each end with 10 mm remaining web. Rear motor and nut-carrier M5 taps are 9 mm deep. Compression sleeves must be fitted before closing the chassis tube; this is not an external weld through an inaccessible wall.

Weld and straighten the rail support frame before machining rail planes and the stop datums. Fit the steel lock module, bronze guides and actual pin stops before setting leaf preload. Install the pin and fork cams before swaging the designated follower/clevis heads. A swaged pin is serviced by removing its sacrificial head and replacing the pin; it is not claimed to be a reusable snap-ring joint. The exposed leaf springs require certified spring stock and an actual force/cycle check.

The nominal service paths are recorded in [service-verification.json](service-verification.json). Isolate both actuator supplies, secure the slide, mechanically support the shutter, disconnect the coil leads and allow the coil to cool. Service each coil separately with the others installed:

- Deploy lock: remove its two M3 rear-cap screws, withdraw the rear cap +50 mm X, withdraw the coil body +70 mm X, then lower the detached body 20 mm.
- Park lock: the corresponding movements are −50 mm X for the cap and −70 mm X for the coil, followed by the same 20 mm lowering.
- Shutter catch: remove the four cover screws and lift the cover/downstand 60 mm. Remove the two rear-cap screws, withdraw the rear cap +50 mm X and lift it 60 mm. Withdraw the coil +55 mm X, then lift it 60 mm through the open service area. The roof opening stops at X1807, ahead of the structural beam at X1808.

The linked plungers and sacrificial swaged pins remain installed during these body-only routes. Reverse the paths for replacement. These are nominal rigid-body routes with manually supported detached parts, not a complete hands/tools/cable service qualification. Delivered terminal boots, internal plunger retention and actual tolerances must be checked. A previously attempted module-lowering route failed and is not the prescribed procedure.

## Load and material screen

The calculation uses the manufacturer's approximate 19 N·m nut torque with a factor of two, giving a **38 N·m working screening case**, not a certified design load. A 540 mm front/rear guide spacing gives a 70.37 N in-plane couple. Vertical-axis spindle torque is distinguished from torsion about a tube's own long axis. The report separately evaluates 250 N vertical and lateral loads on each 304.2 mm cantilever, plus a 500 N single-pin screening load.

These are member-only elastic calculations. They do not establish weld strength, bolt slip, HAZ material properties, rail accuracy, chassis compliance or pocket alignment under tightening torque. HIWIN load data apply to the specified HIWIN parts; inexpensive look-alike rails do not inherit those ratings. The supplied motor's holding torque does not establish moving thrust, speed margin or reliable shutter lifting.

The inventory contains actual modeled quantities and stock envelopes. Purchased fasteners and motors are separate from fabricated material mass. The user's 12 × 12 inch aluminum pieces cannot supply the long carriage and rail bars; additional stock is required. Only sourced goods observations are carried: two motors at $17.88 each, three Delta coils at $23.72 each, and six PM-U25-P sensors at $13 each. That is $184.92 for those items alone. The sensors were listed on backorder. Rails, steel/aluminum, fasteners, wiring, shipping and tax remain unquoted; this is not a delivered build total.

## Remaining CAD integration and physical holds

1. Actual magazine hole pattern, body/end-cap geometry, pocket pitch, loaded tools, manufacturer cover travel and the actual tool-change approach remain unselected/unmeasured. The adapter is a supported blank.
2. Cable routing, strain relief, terminal boots, actuator covers around exposed screw ends and complete tool-assisted maintenance envelopes are not detailed. Supplied solenoid terminals must be checked before fabricating keeper/end plates. The hood has intentional drive/service openings and is not sealed.
3. Pin receiver fits, spring temper and fatigue, hot coil pull force, practical friction, ratchet impact/arrest, actuator running thrust, rail accuracy and stop repeatability need measured qualification. A position drawn in CAD is not an electrical safety function.
4. Welding procedures, dissimilar-metal isolation, bolt tightening/preload, actual reclaimed-tube wall thickness/corrosion, local load paths and the complete machine/tool stiffness require fabrication inspection and proof loading.
5. Firmware for the extra stepper axes and tested sequence integration remain governed by [the controls package](../controls/README.md). Opening or closing the outer shutter requires actual catch-retracted feedback. Park/closed alone does not authorize plasma; the hood is not qualified plasma protection.
6. Flat-section DXFs do not replace a reviewed machining setup or a developed sheet-metal bend pattern. Tube wall drilling is located in the actual solid and operations, not a fabricated claim of a complete tube-laser program.

## Sources and reproduction

Primary geometry and observed goods references are in [hardware/source-data.json](../hardware/source-data.json), [LOCK-ACTUATOR.md](../hardware/LOCK-ACTUATOR.md) and [PIN-SENSORS.md](../hardware/PIN-SENSORS.md). The report binds those files, this README, the builder, exporter and verifier. Vendor PDFs remain outside the public deliverables.

Run `export.py`, then `service_check.py`, then `verify.py` using the repository's CadQuery environment. Verification checks all part solids, exact endpoint intersections, continuous enclosing slide/shutter sweeps, constant rail/screw profiles, nominal loaded allocations, full-deck head/gantry clearances the cap-removal path, current export inventory, and the source-current coil service proof. Passing these named checks does not remove the holds above.
