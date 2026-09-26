# Rev H water and service changes

The extension makes the reservoir accessible through small hatches and defines a real refill spout and washout cover. The whole water subsystem is still **not a released installation**: purchased connection dimensions, supported hose routes and wet commissioning remain open.

The source is `output/release-review/RevE-ENGINEERING/water_completion.py`. Call `extend_router_model(model)` after building Rev G; it mutates the model and returns metadata. Rev G's stored-state clone preserves these parts. `extend_stored_model(model, source)` is an intentional no-op. `hatch_service_model(model)` returns a separate service configuration; it must never be named a cutting state.

## Fabricated service access

| Item | Definition |
|---|---|
| Clarified-bay opening | 320 × 175 mm; X350–670, Y965–1140 |
| Settling-bay opening | 270 × 100 mm; X460–730, Y1200–1300 |
| Covers | 360 × 215 and 310 × 140 mm, 3.048 mm steel; each has six M5 fasteners and a welded lifting tab |
| Seals | Two 2 mm EPDM perimeter gaskets; verify coolant compatibility |
| Cover parking | Each cover stands upright in two welded 40 mm-deep U pockets, with end stops beyond its full width |
| Front cover parking | Y931.952–935, Z436.096–651.096 before the lifting-tab projection |
| Rear cover parking | Y1164.952–1168, Z436.096–576.096 before the lifting-tab projection |

The main equipment lid stays installed. The openings allow a vacuum wand and long brush to enter both sides of the settling weir; they do not claim unrestricted hand access everywhere. Full tank cleaning reach must be demonstrated on the fabricated tank. Removing the entire equipment lid is still major disassembly with its pump, trays, tools and vent disconnected; no new full-lid withdrawal claim is made.

Isolate the machine and empty the tank before washout. Remove the six screws from one cover, retain its gasket on the fixed lid, lift the cover and welded tab 50 mm, move it to its pocket plane, turn it upright, and lower it 49 mm into both pockets. Open the second cover afterward. The verification leaves the first parked cover in place while moving the second. Restore both covers and seals before operation.

The nominal geometry checks do not model fingers, wrench movement, gasket adhesion, loose fastener storage or fabrication error. The open state omits the twelve removed hatch screws explicitly. The lifting-tab holes are hand-tool features, not rated hoist points.

## Refill outlet and washout cover

The refill spout is a welded NPS 1/2 SCH40 miter assembly, OD21.3 / ID15.8 mm. Its centerline is `(385,1255,695) → (385,1255,885) → (385,1215,885) → (385,1215,865)`. Two paired 45-degree miter joints form the turns. The individual centerline lengths are 190, 40 and 20 mm; the source notes distinguish those dimensions from longer raw blanks. Both STEP and the pan-floor DXF include the actual riser penetration. A separate relieved steel stay joins the riser to the pan rear wall.

The outlet ends at Z865, **30 mm above the Z835 pan rim**. The installation must preserve at least 25 mm air gap and keep the discharge open. The lower end is called out 1/2 NPT male for a receipt-fit hose adapter. Weld integrity, pressure-rated hose/adapter selection and the pump's actual connection locations remain installation checks. No hose has been invented between unmeasured pump ports and this spout.

The old unmodeled 1.5-inch cleanout cap is replaced with a real four-bolt flange, gasket and cover below the rear shelf. The neck is 62.048 mm long, from Z116 to the inside floor at Z178.048. Its lower end is plain and welded to the flange; the former NPT-cap instruction is superseded. The nominal 90 mm flange is at Z110–116, the gasket at Z108–110 and the 4 mm cover at Z104–108. Four M6×25 screws, washers and nuts close it. This large opening is for washing out an **already emptied** tank, not controlling a full 115 L discharge.

## What remains a space reservation

The gravity drain axis is X900/Y1270. The new model visibly reserves 70×70×43.398 mm for the pan reducer, 125 mm cube for the selected valve, and 70×70×55 mm for the union/tail connection. These are guarded purchased reserves; their apparent end-to-end contact is an allocation, not evidence that selected NPT parts fit those face datums. The downstream tail must disconnect before basket removal; actual union release and wrench spaces still require the selected dimensions.

The existing [U.S. Solid valve specification](https://ussolid.com/products/u-s-solid-motorized-ball-valve-1-stainless-steel-electrical-ball-valve-with-full-port-9-24-v-ac-dc-2-wire-auto-return-html) confirms the selected auto-return behavior and approximate one-minute charging requirement. Its reviewed product page did not provide the needed fitting datum drawing. The [SEAFLO pump listing](https://seaflodirect.com/seaflo-24v-1-8-gpm-120-psi-31-series-dc-diaphragm-pump-self-priming-high-pressure-water-pump-for-rvs-boats-agriculture-and-cleaning-w-built-in-pressure-switch/) identifies SFDP2-018-120-31; it does not close the existing unknown port-axis/mount-foot geometry. These pages were checked on 26 September 2026. No supplier message was sent and no purchase price is re-quoted here.

The valve maker's [dimensioned product photograph](https://ussolid.com/cdn/shop/files/JFMSV00009.png?v=1748243315&width=1280), retained as `valve-manufacturer-spec.png`, labels 4.3, 3.2 and 3.0 inch extents (109.22, 81.28 and 76.2 mm). It still omits the pipe-axis-to-actuator offset and thread make-up. The 125 mm reservation is an equipment-space allocation, **not an envelope proven about the fixed drain axis**: aligning the real ports may require moving or enlarging it. The adjacent purchased union/reducer connections also remain unqualified. The second retained image is the manufacturer's product photograph, not a dimensioned drawing.

The 115 L charge limit, permanently open tank vent, gravity return, isolated refill pump and existing water-control sequence stay in force. The compressor and CV-15HS do not pressurize or evacuate this tank. Automatic draining remains a controls function; mechanical mode conversion is manual.

## Evidence and outstanding work

`verify_water_completion.py` rebuilds the machine, checks closed router/bed-stored and upright hatch states, verifies eight conservative continuous hatch-path segments against fixed solids, and reconstructs every added/changed flat from its fabrication metadata. `verification.json` preserves the earlier water-only proof **before the subsequent refill-routing refinements**; its recorded source hash identifies that earlier run. Current release evidence must use the final source-matched integrated report.

Run the same checker with `--integrated` to build through `build_revh` and save `integrated-verification.json` separately. That mode also checks two movements of the empty-tank washout cover after removing its four fastener sets, records the 0–1150 by 0–1450 mm plan bounds, and rejects changes to any CAD source while the run is in progress. The washout cover is hand-held at the final withdrawal point; no catch vessel or storage support is implied by that pose.

The refill riser was moved to X385 to keep its lower connection allocation at X335–435/Y1205–1305/Z575–695. This separates the connection from the staged bed hoops on its left and the rear hatch's opening sweep on its right. The allocation is included as a guarded amber solid in the CAD and in all subsequent integrated path checks; final hose/fitting selection still has to fit it.

**Final integrated service check:** the closed router and bed-stored configurations each contain 1,448 valid single solids and no unresolved overlaps; the open service configuration contains 1,436 after explicitly removing the twelve hatch screws. All ten continuous service-path segments passed against the full Rev H geometry and remained inside the stated chassis plan. The final run recorded no source changes, and its recorded CAD source hashes matched the files immediately afterward. These nominal results do not close the purchased plumbing, human-access or physical commissioning requirements above.

| Audit issue | Result of this extension |
|---|---|
| FW01 | Refill spout, washout closure and visible drain allocations added. Purchased fit, plumbing support, suction strainer and complete hose routing remain open. |
| FW04 | Routine washout now uses local hatch paths, so it does not require the failed full-lid/rear-brace maneuver. Full lid remains major disassembly; actual cleaning reach needs demonstration. |
| FW08 | No invented enclosure door or cooling design. Actual hinge/latch/door sweep, cable glands, panel layout and VFD heat rejection remain open. |

Changed pre-existing solids: `WT_LID`, `WP_FLOOR`, `WT_CLEANOUT_NECK`. The first two have matching rebuilt local solids and flat metadata; the neck's local pipe length matches its installed solid. The 2×2 chassis, tank internal volume and machine footprint are unchanged.
