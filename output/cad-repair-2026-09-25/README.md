# Rev G repairs and remaining work — 25 September 2026

**The previous model was incomplete and inaccurate. Rev G changes the geometry; it does not declare the machine finished.** Current exports are in [RevG-CAD](../release-review/RevG-CAD/README.md). The historical 29-finding audit is preserved unchanged.

## Corrected design

- Six 500 x397 mm panels replace the hoisted module. Ten 1220 mm bars supply thirty 397 mm pieces; 29 mm/bar remains for kerfs and trim.
- Four 924 mm beams, actual bearing seats, compression sleeves and round/relieved locators connect the bed to the chassis. Front seats unbolt after beam1 rests independently on beam2, opening the lowering portal.
- Six separate spoilboards are modeled after the 1 mm skim. Their faces lie inside nominal X175..975/Y121.4..1121.4 center travel; actual cutter and guard clearance is still required.
- All 24 loose top-slot nuts leave the extrusion before panel rotation and are stored threaded onto their removed screws. No imaginary nut retention.
- Actual stringer holes, a welded sloped drip shield, guard floor clearance and adapter recess orientation replace incorrect geometry. Unsupported carriage bolts and defective legacy torch clamps are omitted.

## Verification and limits

Both exported configurations contain 1283 valid solids, with zero unresolved static overlaps above the checker threshold; STEP readback checks solid counts and total volume. There are 201 individual STEP parts and 103 flat DXFs. Purchased or guarded interfaces are excluded from production-part exports.

- [Full-machine router poses](motion/revg-full-machine-poses.json): nine discrete positions; no continuous cutting or dual-Y-skew claim.
- [Panel handling](motion/revg-panel-path.json): 36 conservative continuous segments, in order 6→1, with already stored panels retained as obstacles.
- [Spoilboard handling](spoil-transfer-check.json): 60 continuous segments, in order 4, 3, 2, 1, 6, 5; nuts remain installed until boards are off.
- [Beam handling](beam-path-check.json): 25 continuous segments in order 1, 2, 3, 4, including temporary resting on beam2.
- [Nut evacuation](nut-evacuation-check.json): 24 nuts, each sliding to the open profile end and lifting through the joint. Travel to the tray and pickup/finger access are excluded.
- [Targeted motion and export corrections](motion/README.md); [frame repair evidence](frame/README.md).

These are nominal geometry checks. Zero overlap allows intentional contact and does not provide a fabrication-tolerance margin. Large-part paths exclude hands, small fasteners, front-seat/tool transfers, cables, joint capacity and positive storage/temporary-restraint qualification. The spindle/torch interfaces and whole-machine stiffness remain incomplete.

## Conversion is manual

The proposed sequence removes 52 screws/clamp fasteners plus 24 loose nuts, as well as the panels, boards, beams, two front seats and router tool. It is not automatic or advertised as quick-change. Manual handling remains an explicit working assumption pending owner preference. The [detailed sequence](bed-architecture.md) includes nominal masses, actual waypoints and limitations. Reinstall the bed to empty the racks before cabinet service.

## Status of every original finding

“Geometry corrected” addresses the cited CAD defect only. “Partial” and “open” are not closed engineering requirements. No total closure count is used to suggest manufacturing readiness.

| Finding | Current status | Change or remaining requirement |
|---|---|---|
| BED01 | PARTIAL | Six panels, separate boards and four beams now store inside the frame. Prescribed large-part paths are checked continuously. Manual preference, small-part transfers, human access and positive retention remain open. |
| BED02 | OLD DEFECT REMOVED | Unsupported MDF sub-bed and its five broken-edge seats are absent. New 20 mm ties carry 15 mm washers with nominal full bearing; slot/preload qualification remains BED04. |
| BED03 | PARTIAL | No unreachable full sub-bed surfacing is specified. Six spoilboard faces lie inside nominal center travel. Final cutter/guard clearance, seat map and repeat-installation accuracy remain unqualified. |
| BED04 | OPEN | Actual T-slot lips and M5 nuts still carry preload. No unsupported torque, uplift or creep rating is issued. |
| BED05 | PARTIAL | Gap-bridging weldnuts replaced by bearing plates, attached bosses and real compression sleeves. Weld strength, local tube-wall loads and tightening method still need qualification. |
| BED06 | PARTIAL | Round/relieved locator geometry is defined. Front seats are removable with clearance bolts; no automatic return-to-zero is claimed. Map seats and re-probe; qualify repeatability and fits. |
| BED07 | PARTIAL | 10 x 5.5 mm tie slots provide +/-2.25 mm nominal lateral M5-shank movement. Actual accumulated profile tolerances must fit that allowance. |
| BED08 | GEOMETRY CORRECTED | Finished spoilboards are 18 mm, explicitly skimmed 1 mm from rough 19 mm stock. The STEP now represents that finished stack. |
| BED09 | OPEN | Legacy strength screen is not used as whole-machine evidence. Tool, gantry, frame, seats, joints and feet require a combined load/deflection analysis. |
| BED10 | OLD JOINT REMOVED | MDF-to-steel TEK restraint is absent from the new bed. Independent cabinet TEK fasteners are a separate detail; new panel/beam joints still need qualification. |
| BED11 | PARTIAL | No assumed owner winch, sling or external parking. Manual components have nominal masses and routes. Handling preference, reach and restraint remain unqualified. |
| BED12 | PARTIAL | New continuous geometric checks cover ordered panel, board and beam paths with previously stored parts. They exclude fingers, tolerance stack, small-part transfers and retention; nine router poses are still discrete samples. |
| BED13 | PARTIAL | Nominal panel mass ~3.866 kg and beam mass ~5.060 kg use modeled solids and stated densities. Weigh finished assemblies; real hardware, welds and residue are not validated by those estimates. |
| BED14 | OPEN | Frame, feet, pan and reservoir support/load stability have no released structural rating. |
| MT01 | GEOMETRY CORRECTED | Both adapter front recesses have matching vertical STEP/DXF orientation; reconstructed void comparison passes. The physical purchased mating interface remains guarded. |
| MT02 | GUARDED, NOT COMPLETED | Invalid legacy torch-clamp solids are excluded from Rev G and guarded in source. A real measured torch clamp still needs design. |
| MT03 | OPEN | No installed, dimensioned plasma torch, floating head or breakaway. The second assembly is named BED_STORED and is not an operational plasma setup. |
| MT04 | CHECK FIXED | Motion fixture uses the actual raised rail-cap datum; the earlier22 clashes were fixture errors. Targeted and full-machine pose results are reported separately. |
| MT05 | OPEN / CLAIM CORRECTED | Supplier70 mm spacing applies to smaller5 mm holes; thread, longitudinal pitch and output height are unconfirmed. Removed guessedM6 screws; adapter production export is guarded. |
| MT06 | OPEN | HMS/HGR/Z mounting, actual motor/driver requirements and power-loss Z retention are unresolved. |
| MT07 | OPEN | Operational cutters, torch geometry, cable/lead bends, workholding and independent dual-Y skew still need integrated checks. |
| FW-01 | OPEN | Selected valve, pump, fittings and complete hoses/service route are not fully modeled. The CAD pan/tank does not imply an operational automatic water system. |
| FW-02 | GEOMETRY CORRECTED | Cabinet stringers now contain the specified6 mm bores through both walls; unsupported screw/stringer collision allowances removed. |
| FW-03 | GEOMETRY CORRECTED | Undefined folded cap replaced by actual sloped roof, separate welded lip, four cage tabs and M5 fasteners. Sampled shield service path checked against the frame subset; actual cabinet door still unknown. |
| FW-04 | OPEN | A fully demonstrated reservoir lid removal route past the rear brace is still absent. Trays on the lid must be emptied for service. |
| FW-05 | GEOMETRY CORRECTED | Drained-level guard moved upward. Minimum nominal clearance including slot play is 10.3713 mm, with 8 mm as-built requirement. Wet calibration remains open. |
| FW-06 | OPEN | Right pan guards remain close to maximum nominal tool center. Actual cutting tool/torch and useful plasma area need verification. |
| FW-07 | OPEN | Full frame stiffness, fastening, foot reactions, leveling and overturning are not qualified. |
| FW-08 | OPEN | Stored parts occupy the cabinet access zone: reinstall the bed to empty racks before cabinet service. Actual enclosure door, thermal layout, glands and hose separation remain open. |

## Reproduction

Use CadQuery 2.7/OpenCascade, ezdxf 1.4.4 and Python 3.12 for the CAD scripts. Run `build_revg.py` from the shared source directory; it writes the separate RevG-CAD package. The checks in this folder and `verify_revg_motion.py` / `verify_revg_panel_path.py` reproduce the evidence. Run `render_revg.py` after exports, then the repository-root `build_concept_revg.py` for the PDF review copy. Sources and readback hashes are recorded with the outputs.

The current square-tube schedule nests 30 modeled 2 x 2 x 0.120 inch blanks into five full 20-foot bars with 3 mm kerf / 10 mm trim. This excludes other tube sizes and is a cutting schedule, not a material quote. General sheet nesting is a layout envelope, not a recommendation to buy whole sheets for small parts. The owner’s 12 x 12 aluminum stock quantity/alloy is unverified. Twenty-four 250 x 20 ties cannot all come from one 12 x 12 piece.

No new total delivered price, final CAM post, firmware release, supplier message or purchase is implied. The [supplier request](SUPPLIER-DRAWING-REQUEST.md) is an unsent draft.
