# Rev I service detailing

This extension adds supported plumbing, a removable gravity drain tail, a strainer carrier and corrected cabinet packaging to the frozen Rev H model. The historical Rev H source and reports are unchanged. It does **not** declare unmeasured purchased interfaces, wet operation or cabinet heat rejection complete.

Source: `output/release-review/RevE-ENGINEERING/service_finish.py`. The integration API is `extend_router_model(m)` followed by the existing stored-state builder; `extend_stored_model(m, source)` is an intentional no-op because these parts stay fixed during bed conversion. `tail_service_model(source)` creates the parked drain-tail state. Run the complete integrated check with `verify_service_finish.py --builder build_revi`.

## Changes that are actually defined

- The pan drain has a fabricated reducer and support ledge, a rear-wall strap, threaded NPS 1 stubs, a four-bolt Ø90 mm flange connection, and a straight 90 mm removable tail. The fixed flange starts at Z = 542 mm so the catch basket can lift 103 mm without striking it. A welded cup holds the detached tail at X = 1040 mm, Y = 1270 mm, clear of the basket. These parts serve the gravity drain of a permanently vented tank; they are not pressure-vessel fittings.
- Pressure and suction routes use Parker 801-6 hose with three 80 mm radius bends per route. The published specifications are a 75 mm minimum bend radius, 15.9 mm outside diameter, 350 psi pressure rating and 28 inHg suction rating. Three split steel supports carry the pressure hose. A rear stanchion and four guide plates carry the suction hose. Guides take soft liners; matching Parker 82 Series end fittings are required. Enlarged solid routes check a 2 mm radial routing allowance against the actual CAD, including the supports.
- The strainer carrier sits in the right-side bay, clear of the torch-head parking bay. Two capped 25.4 mm tube posts carry a bolted 6 mm tray. Two removable top bridges restrain the strainer after fitted soft pads are installed. The whole strainer lifts 120 mm after both connections and the top bridges are removed. The bridges stack in the unused strip of their own carrier tray. The bowl is serviced after lifting the strainer out of its carrier; the design does not rely on downward bowl clearance beneath the tray.
- The pump is turned 180 degrees in its existing envelope so its head faces the right plumbing bay. The four tray bores move to world X = 806/864 mm and Y = 850.5/935.5 mm. The local plate solid and flat use those same coordinates.
- The selected VEVOR enclosure uses its published dimensions of 500 × 400 × 200 mm. Its marketing label, 20 × 16 × 8 inches, is rounded. A 350 × 450 × 2 mm backplate, two separate gasketed gland cover plates, their bolts and actual back-panel/rail drilling are now present. The custom gland windows are conditional on the received bottom cutout and folded returns; check that fit before cutting the purchased enclosure.

## Service sequence

For basket cleaning, drain the pan and disable the pump first. Remove all four drain flange bolts, nuts and washers. Move the tail and its gasket 6 mm down, 90 mm forward, 40 mm up, 140 mm right, 90 mm rearward, then 47.904 mm down into the parking cup. The basket can then lift 103 mm. The CAD proof covers nominal rigid paths within the chassis plan; it does not model hands, sludge adhesion, a full heavy basket or manufacturing tolerances.

For strainer cleaning, isolate the pump, drain the connections and disconnect both hoses. Remove the four top-bridge screws. Lift each bridge 20 mm and rotate it 90 degrees about its vertical centerline. Move it 73.5 mm left, then move bridge 1 rearward 39 mm and bridge 2 forward 31 mm. Lower bridge 1 by 140 mm and bridge 2 by 137 mm to stack on their own carrier tray within X = 1007.5–1022.5 mm, Y = 876–993 mm and Z = 500–506 mm. The bridges clear the two tray mounting-bolt heads and remain independent of loose hardware in the main bin. Lift the strainer 120 mm vertically, supporting its weight. Reconnect the hoses and wet-test for suction leaks before operation.

Cabinet work requires electrical isolation and an empty front panel-storage bay. The two gland plates have a checked 12 mm downward withdrawal after their cables and fasteners are removed. The purchased door's hinge, return flange and lock cannot be reconstructed from the vendor's overall dimensions; their opening sweep remains unqualified. Bed conversion still stays within the machine footprint.

## Remaining purchase/fit gates

| Interface | What is established | What still requires measurement or qualification |
|---|---|---|
| USS-MSV00009 valve | The exact-SKU primary drawing gives L = 72 mm, d = 25 mm, H = 49 mm and an 81.6 × 62.1 × 58 mm actuator. The drain path has a conservative outer allocation and physical support. | The vendor photo also labels a 3.2 in (about 81 mm) face length. Confirm the actual version, stem-to-port-axis offset and NPT thread engagement. Fit and trim both nipples before welding to the fixed flange datum. |
| SEAFLO SFWS-500-02 | The official drawing gives a 97 mm body length, 167 mm length including tails and 117 mm overall height. The carrier and removal path are modeled. | Transverse width and port-axis height are not dimensioned. The model's 97 mm transverse acceptance width is a design limit, not a vendor measurement. Fit pads and end connections after receipt. |
| SEAFLO SFDP2-018-120-31 | Published family envelope and foot pattern; head oriented toward the new plumbing bay. The selected pump has 3/8-18 FNPT ports, a 24 V supply and a 120 psi cutoff. | Foot thickness, exact port axes and final mounting-bolt lengths. The short pump/strainer hose and end adapters have bounded fitting zones; they are not completed connected solids. |
| Hose end fittings | The selected hose has published pressure, vacuum and bend ratings. Main spans and supports have explicit CAD routes. | Use matching Parker 82 Series fittings. Verify that the actual elbow and adapter stack fits the recorded end zones without touching other solids. The connection zones do not override interference. Wet-test suction prime, flow and pressure; verify additive and pulsation compatibility. |
| Cabinet | Published body/backplate dimensions, custom gland cover flats and drilled cage interfaces. | Actual hinge/lock, bottom cutout, sealing washers, backplate standoffs/retention, actual VFD/PSU losses, airflow and complete populated controls layout. No retained IP/NEMA rating is asserted after modifications. |

The tank remains permanently vented and the whole circuit charge stays limited to 115 L. There is no compressed-air or venturi connection to the reservoir. Keep the 30 mm nominal refill air gap and verify at least 25 mm after fabrication. Commissioning must include leak tests, blocked or dirty filter behavior, level-switch calibration, overflow capacity and control interlocks.

## Verification evidence

The **current service verification authority** is [verification-build_revi.json](verification-build_revi.json), which passed against the frozen integrated Rev I sources on 26 September 2026. All four static states are clear: router and stored have 1,669 parts each; tail parked and hatches open have 1,657 parts each. All 37 local-flat checks and all 28 continuous segments across nine service paths pass. Both hose routes, enlarged by 2 mm radially, clear the complete stored model. Every checked service path stays within the 1,150 × 1,450 mm chassis plan.

No CAD source or checker changed during that run. The report binds service source `9738b260ce8f61c7ca45b46c212b1559057bdb1b1505885bcc0616045bc228e5`, motion source `3f3555a24bf84ce7444d3f5f516fe8c414e56689671d662310edddc4df16da3f` and checker `c2f0cc1c5750d7c7514d19fb77eab48ce52932edfa40acf466cf9274a646fdde`, together with the remaining CAD source hashes.

`initial-check.json`, `verification-build_revh.json`, `historical-verification-build_revi-before-final-freeze.json` and `historical-interrupted-motion-9f3fe821.md` are **historical diagnostics**, retained to explain earlier route corrections and the revoked motion freeze. Their failed or superseded paths are not current operating instructions. `strainer-focused-build_revi.json` is an earlier, limited check of the corrected bridge parking and strainer lift; the complete integrated report above supersedes it as the service verification authority.

The full report records CAD and checker hashes, all static interference results, local-flat regeneration, continuous paths and enlarged hose sweeps. Nominal geometry verification does not qualify unmeasured vendor interfaces or physical machine operation.

Root project tooling owns final assembly exports, updated PDF and release status. This subtask creates no Git commit and performs no publication.



