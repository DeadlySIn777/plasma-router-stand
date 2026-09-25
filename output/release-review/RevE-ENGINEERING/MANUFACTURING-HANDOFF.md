# Rev F manufacturing handoff

This is an engineering package in millimetres. The current release status is recorded in `PACKAGE-STATUS.md`; the existence of a STEP or DXF file does not release an unresolved supplier interface.

## Design basis

The requested nominal travel is X 800 mm, dual Y 1000 mm and Z 100 mm. Travel is actuator stroke, not a promise that every point on the larger support bed is machinable. Soft limits, home positions, tool offsets and the practical cutting envelope must follow the completed motion definition.

The selected modules are KHMOS HMS40 (X ASIN B0C7GQTRRX, two Y ASIN B0C7GN24S1) and RATTMMOTOR ZBX80 (B09MVYGLNQ). Independent guide rails carry router cutting moments; the small HMS40 carriages transmit drive force through floating links. Kraken V1.1 supplies the four onboard motor channels. No external stepper-driver boxes are included.

The router deck is a ONE-PIECE hoisted module: a welded steel ladder (two 2 × 2 × .120 rails at 1290, four 2 × 1.5 × .120 flat crossmembers at 938.4, four 6 mm lift ears), two glued 12.7 mm MDF layers surfaced in place by the machine, and ten full-length 20100 strips. Five packs of the selected extrusion contain ten 1220 mm sticks; each takes ONE cut to 1197 mm, no drilling. The nominal butted deck is 1000 × 1197 mm; the width stack of ten 100 ± 0.2 strips is absorbed at the free edges. Strips fasten with fifty M5 × 25 button screws from below into DIN 562 square nuts in the bottom slots; the module clamps to the ledgers with four M8 × 70 drawdowns and locates on two Ø10 dowels.

The bare extrusion workplane is Z 940.8 mm. A nominal 19 mm spoilboard makes Z 959.8 mm. Plasma slats are at Z 850 mm. The 109.8 mm difference exceeds the Z module's 100 mm travel, so tool changes require distinct, defined head mounting positions. Do not try to cover both modes solely by changing a work coordinate.

## File use

| Files | Purpose | Before manufacture |
|---|---|---|
| `step/*.step` | Complete assembly states and placement | Check the state name, unresolved interfaces and collision report. |
| `parts/*.step` | Nominal individual solid parts | Match part number, revision, material and operations. Purchased envelopes are reference geometry. |
| `dxf/*.dxf` | Flat-part contours and labeled machining references | Use millimetres. Inspect the layer meanings; a tap or pocket reference is not a through-cut command. |
| `cutlist.csv` / `.json` | Quantities, material, stock and operation notes | Exclude purchased envelopes from fabrication. Read guarded-export status. |
| `tube-cut-plan.json` / `TUBE-CUT-PLAN.md` | Full-length 2 × 2 tube blank nesting | Use the stated saw kerf and end trim. Do not pre-cut stock in half without re-nesting. |
| `nesting/*.dxf` | Material/thickness-specific placement | Select through-cut layers only. Stock borders and part marks are non-cut references. |
| `nesting/sheet-nesting.json` | Part counts and layout checks | Small material groups may be ordered as cut blanks or flat bar instead of whole sheets. |

DXFs are nominal geometry. The fabricator must apply its own tool diameter or kerf compensation, pierce lead-ins, tabs, cut order, feeds, workholding and verified machine postprocessor. No generic G-code is supplied: a program posted for an unspecified machine is not a usable manufacturing release.

## Fabrication sequence

1. Resolve the supplier and interface fields in the current status register before buying mating parts or drilling interface plates. Confirm the actual selected revisions and options.
2. Cut structural blanks from the final cut list. Deburr and identify every part. Add internal weld nuts, compression sleeves and access features before closing tubes. Keep sand out until welding and leak checks are finished.
3. Fixture the frame from its rail datum surfaces. Tack, measure both diagonals and rail-plane twist, then weld in a balanced sequence. Recheck after cooling; an as-welded tube surface is not a precision guide datum.
4. Finish the specified rail caps, seats and adapter faces. Where the cut list says 6.000, 8.000 or 12.000 mm finished thickness, do not silently substitute 6.35, 7.9375 or 12.7 mm stock. Machine the specified finished dimension or revise all affected interfaces and recheck the CAD.
5. Assemble the pan and vented reservoir, preserving drain slope, cleanout access, separate overflow routes and a permanently open vent. Leak-test before paint and electrical installation. Fill only to the stated 115 L total inventory mark with the pan drained.
6. Assemble and align the guides, gantry and drive-only links. Install limit targets and hard stops from the completed motion drawing. Verify free movement over the entire stroke before connecting motor power.
7. Weld the module ladder and set it on the ledgers. Screw and glue the MDF layers to the crossmembers, then surface the MDF top in the machine. Hoist the module onto stands, fit the strips with their square nuts and underside screws, reinstall, and only then fit the optional spoilboards. Verify the sampled hoist route with the weighed finished module.
8. Finish and ballast only stationary frame members. Recheck leveling and geometry with operating water inventory and the intended bed installed.
9. Install the segregated electrical panel, shields and cable management from the completed terminal drawing. Perform the low-current controller procedure in `controls/COMMISSIONING.md` before cutting.

Weld sizes, fastener engagement, pocket depths and tapping operations come from the part notes and detailed drawings; this sequence does not replace them. Measurement during assembly is normal commissioning work, separate from unresolved design dimensions.

## Supplier evidence and inspection

- The HMS40 dimensioned drawing establishes the carriage's 30 × 30 mm M4 mounting pattern, 65.5 mm top height and stroke-dependent overall envelope. It does not establish the actual motor torque-speed curve or winding-current convention.
- The selected iMetrx rail drawing gives M5 × 6 block holes and a stated 40 mm rail-hole pitch. Its 1500 mm rail/end-offset arithmetic is inconsistent. Resolve the exact drilled rail pattern or use a fully defined adjustable mounting scheme; do not substitute another brand's hole pitch.
- The ZBX80 listing provides the broad envelope but does not fully dimension the output mounting pattern or assembled mounting height. Customer reviews and scaled photographs do not close these mating dimensions.
- The spindle kit is the selected 65 × 259 mm, 1.5 kW, ER11 kit. Its supplied clamp and VFD are already included in the purchase price. The earlier ER17 mention is not a verified option for this ASIN.

Receipt inspection and subsequent machine testing remain necessary even after the design is released. Supplier confirmation closes missing design data; physical inspection checks that the delivered parts match it.
