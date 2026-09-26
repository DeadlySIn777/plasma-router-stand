# Rev I floating and breakaway head

The new source builds **103 physical head components** and a lid-mounted parking cradle. It replaces the earlier clamp-only concept with a guided float, metal travel stops, a three-point magnetic release, four sealed switches, a replaceable insulating clamp insert, a splash screen, fixed lead support, and tether attachment eyes. The default insert is an actual **unbored blank**; no owner's torch dimensions are invented.

`motion_finish.py` preserves the Rev H model and measurements. Its integration APIs are `extend_router_model`, `extend_stored_model`, and `plasma_hardware_model`. The last one installs the head hardware on the custom tool adapter after the router is parked. It does not establish the unmeasured ZBX80 output fixing pattern, motor coupling, actual torch, cable loop, plasma start circuit, or THC interface.

## Defined mechanism

| Item | Definition |
|---|---|
| Fixed plate | 110 × 130 × 9.525 mm, four M6 custom attachment taps on 90 × 26 mm pattern |
| Guides | Two ground Ø8 × 118 mm shafts, 60 mm apart; end-tapped M4 |
| Bearings | Four igus RJ4JP-01-08, nominal Ø8 / Ø15 / 24 mm; two 23.85 mm spacers |
| Float | 6 mm upward travel; captured 8 mm metal stop inside 14 mm pocket |
| Bearing capture | Bolted end plates; nominal 0.15 mm axial clearance across the bearing/spacer stack |
| Coupling | Hardened R3 buttons against one 90° cone, one 90° V, and one flat; six constraints without three-cone overconstraint |
| Retention | Three CSN-20 pot magnets, 20 × 6 mm, nominal 0.20 mm target gap |
| Float detection | Omron D2HW-C202MR NC, separate ramp and dwell cam |
| Head-presence detection | Three Omron D2HW-C203MR NO contacts in series; separation opens the circuit |
| Tool clamp | Matched aluminium halves; Ø48 insert register, 40 mm grip height, 0.5 mm split |
| Insert | Split insulating blank; generator accepts only a measured 20–40 mm barrel and at least 40 mm straight grip |
| Splash screen | 110 × 60.5 × 1.5 mm stainless, Ø50 clearance opening, separate welded tabs |
| Parking | Three welded feet and machined steel pads; two M5×18 retaining screws; 5.825 mm tapped-foot engagement |
| Work mounting screws | Four dedicated M6×16; 9.3 mm engagement after the adapter's 6.7 mm web |

The router's M6×20 screws are too long for the new head plate and are **not reused**. They stay with the router clamp. The plasma-head screws have their own positions in the existing hardware tray.

The shaft sockets, bearing housings, locator contacts and clamp bore require machining. These are not all laser-cut sheet parts. The 110 × 130 mm backplate fits within the user's nominal 12 × 12 inch stock, but its alloy and remaining usable area must be checked. The 22 mm carriage body, 25 mm deep guide crossbars and 30 mm clamp halves need thicker stock; they are not charged to the owned 3/8-inch or 1/2-inch pieces.

## Primary supplier evidence

- [igus RJ4JP-01 product family](https://www.igus.com/product/drylin_RJ4JP_01) and [manufacturer dimension table/CAD selector](https://igus.partcommunity.com/3d-cad-models/rj4jp-01-linear-bearings-igus?info=igus%2Fdrylin_lineargleitlager%2Fr_runde_wellen_schnell_leise%2Frj4jp_01.prj): RJ4JP-01-08, nominal bore8, outside15, length24 mm. The model includes the load-bearing envelope and omits cosmetic circlip grooves because the custom caps provide axial capture. Actual housing/shaft fit remains a measured assembly check.
- [Omron D2HW manufacturer datasheet](https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2hw.pdf), saved in `sources/omron-d2hw.pdf`: M3 mounting centers13 ±0.1 mm, first center2.65 mm from the case edge, locating posts on both sides. Operating position6.4 ±0.2, free-position maximum7.2, total-travel-position maximum5.1 mm from the mounting datum. The selected wired switches have sealed bodies; their loose lead ends still need protection. The purchased body is a conservative mating envelope, not a reverse-engineered internal switch.
- [CSN-20 manufacturer datasheet](https://www.supermagnete.de/eng/data_sheet_CSN-20.pdf): diameter20, height6, bore4.5, countersink9.46 ×2.48 mm, nominal direct-contact normal pull87.3 N per magnet, maximum80°C. **261.9 N is the sum of three catalog contact ratings, not the installed release force at a 0.2 mm gap.** Coating, target flatness, steel thickness, gap and temperature affect force.

The originally considered CSN-13 magnets were replaced during this revision's design work. The final source, geometry and parts list use **CSN-20**.

## Purchased fastener envelopes

The selected unknurled socket heads use actual supplier maxima: M3 Ø5.5 ×3, M4 Ø7 ×4, and M5 Ø8.5 ×5 mm. The M6 model uses Ø10.2 ×6 to conservatively contain the selected Ø10 ×6 head. [Accu M3](https://www.accu.co.uk/api/product-datasheet?id=642039), [M4](https://www.accu.co.uk/api/product-datasheet?id=151797), [M5](https://www.accu.co.uk/metric-cap-head-screws/250442-SSCF-M5-18-A2-R360), [M6](https://www.accu.co.uk/metric-cap-head-screws/250454-SSCF-M6-16-A2-R360).

The magnet screws are specifically [ISO10642 M4×16, Ø8.96 ×2.48 mm heads](https://www.accu.co.uk/countersunk-socket-head-screws/251236-SSK-M4-16-A2-R360); 16 mm includes the countersunk head. The magnet recess is Ø9.46. Button fixing counterbores are Ø6 ×3 mm, stop fixing counterbores Ø7.5 ×4, and clamp fixing counterbores Ø8 ×4. The lower cam screw center is V96.5, leaving0.25 mm nominal clearance to the bridge with the full Ø5.5 head. Do not substitute larger knurled heads without another clearance check. `head-package-verification.json` checks all56 head, cradle and work-mount fasteners, plus the exact current STEP/DXF inventory.

## Detection and force checks

The float cam crosses the switch's operating range at approximately **1.0–1.65 mm** float, including allowance for the contact radius of the real plunger. The cam then reaches a constant dwell. The modeled pin remains at least6.1 mm above its mounting datum, leaving1.0 mm to the manufacturer's total-travel limit; the remaining float does not crush the plunger. Use1 mm/s for initial probing, calibrate the actual switch offset, and measure controller stopping overtravel. Geometry does not prove electrical response or stop distance.

The three seated contacts detect release at separated points. They are ordinary detection switches, **not a rated safety circuit**. The [defined head-input schematic](../controls/HEAD-INTERFACE.md) supersedes the old provisional5 V loop: separately current-limited24 V loops drive two AQY212GS receivers. Three series NO presence contacts gate XH:5/6; the NC float gives PE11 healthy LOW / open HIGH. Its checker verifies the terminal graph, current/logic bounds and300 ms fault/recovery model. Frozen CAD metadata retains the older provisional electrical wording as history. Actual PCB, harness, switch timing and EMI qualification remain open. The parked float is not a router touchplate; router Z zero is manual.

A CAD density screen gives about **2.36 kg** for the complete head, **1.67 kg** for the floating hardware and **1.08 kg** for the detachable clamp/plate hardware, excluding the actual torch, its lead, and a tether. Aluminium was screened at2700 kg/m³, steel at7850, polymer at1400 and switch envelopes at1700. These are design estimates, not weighed purchased masses.

With a hypothetical1 kg torch/lead contribution, gravity on the floating group is about26.2 N before guide friction. Therefore this design does **not** claim low-force probing on unsupported thin sheet. Measure the actual touch-off force on the intended work support. An ohmic interface or a properly selected counterbalance is a separate change if that force is unacceptable.

For the same hypothetical1 kg payload, the detachable group is about2.08 kg. A screening vertical acceleration of1 m/s² gives22.5 N. A45 mm forward lever and50 mm locator span correspond to roughly20.3 N of peel reaction before lateral lead loads, switch forces, shock and margin. This explains why installed retention must be tested and why the smaller magnets were rejected. It is **not** a coupling capacity certification. Adjust the spacer/shim stack only after measuring both reliable seating and release in the relevant impact directions.

The metal stop retains the carriage at both float extremes. This does not prevent the entire machine Z axis from falling if its ballscrew back-drives: the independently documented brake-motor fit, power-loss behavior and sequencing still apply.

## What must be measured before machining the insert or energizing

Record the actual torch's barrel diameter at several angles, straight grip length, allowable clamp load, nozzle datum, lead diameter/bend radius and temperature limits. The insert generator rejects missing evidence, diameters outside20–40 mm, grip shorter than40 mm, or roundness above0.10 mm. Its20 and40 mm verification cases are synthetic boundary tests, not measurements of the owned AG-60.

The fixed saddle provides a real attachment for a supply-lead strap. It does not invent a cable loop or a supplier bend radius. A slack loop and a rated nonconductive separation tether must be installed, dimensioned and tested. The two tether eyes are bolted parts; no unspecified tether is counted as an installed restraint. The splash screen does not establish an80°C magnet temperature or the insert's thermal suitability.

The proposed torch axis is80.6 mm forward of the custom adapter,35.1 mm farther forward than the current router axis. Under the inherited placement assumptions, its nominal Y-axis center range changes from121.4–1121.4 mm to86.3–1086.3 mm. This is not a claim that all1000 mm of nominal Y travel lies over a usable cutting bed, and no nozzle Z datum is supplied without a measured torch.

## Manual transfer inside the frame

The complete head is too deep for the 54.2 mm gap between the front frame and the water pan. The defined transfer therefore separates the splash screen, front clamp with its insert, rear insert, and release plate with rear clamp. The remaining guide assembly has a maximum forward depth of 50.525 mm. Parts pass through the gap at the right side, within the machine outline, then mount to the adapter. This is a manual, disconnected sequence with no torch installed.

The head proof begins after the router spindle/clamp is parked, with the temporary panel/beam state prepared by the separate staging sequence. It removes the screen first, then the front clamp with its insert, then the rear insert, then the release plate/rear-clamp group. The remaining guide assembly moves to the adapter and receives its four M6 mounting screws. Reassembly order is rear clamp/plate, screen, rear insert, then front clamp/insert. The four small clamp/screen screws return from their explicit tray positions. Actual torch removal, flexible leads, tether handling and human grips are outside this nominal rigid sequence.

The actual first aluminium bed panel temporarily occupies the normal rear-left panel position, X73.5–573.5 / Y890.5–1287.5 mm, with its top at Z940.8 mm. Existing beams3/4 support it and the existing clamp sets retain it. All six spoilboards stay stored. Beam1 moves into the empty front/lower rack slot and uses the existing front-row M6×130 locks. The head parts rest on defined broad faces on the temporary panel. Each group has verified contact with the actual extrusion and its gravity projection lies inside the support polygon. These static contact checks do not qualify impact, friction or clamp capacity.

`transfer-staging-verification.json` proves temporary bed preparation and restoration; `integrated-verification.json` separately proves the head paths and checks every final head part. Removed small screws have defined hardware-tray positions, while their individual unscrewing and hand-access paths remain excluded. The earlier complete-head and MDF-support procedures are superseded diagnostics. Router spindle/clamp transfer is a separate service proof; it is not implied by head-transfer acceptance.

## Verification and files

- `mechanism-verification.json`: 14 static float/release combinations, continuous6 mm float and8 mm normal release, seven flat/solid reconstructions, input rejection and synthetic bore-limit tests.
- `head-cad/`: named103-solid head STEP, 30 individual fabricated-part STEP readbacks, DXFs, operations and cut list. Unbored measured-interface inserts and purchased parts remain guarded.
- `integrated-verification.json`: final PASS for68 continuous split-head segments,12 full intermediate static states,4 actual support/contact checks and109 unique final parts. The entire rigid XY sweep stays withinX180–982/Y52–1166.9 mm. The report binds the CAD sources, wrapper, head-path helper, staging helper and continuous solver.
- `head-package-verification.json`: final PASS for56 screw envelopes,103-solid assembly STEP readback,30 individual STEP files and7 DXFs, with no missing or obsolete files.
- `diagnostics/`: superseded path evidence, including the rejected MDF staging approach. These files do not establish release acceptance.

The continuous guide proof uses a conservative exact swept cylinder. The relieved cam uses two verified conservative boxes swept backwards through the full release displacement. Cone/V/flat contacts use their monotonic opening geometry for outward normal release, because a generic distance bound cannot certify departure from exact initial tangency. Tilting release, force thresholds, human reach and grasp, actual fit tolerances, cable motion, thermal conditions and energized commissioning are not proved by these nominal-solid checks.

Run from the repository root with the CadQuery environment:

```powershell
& 'C:/Users/Gluis/OneDrive/Documents/ChatGPT/New project/smart_compressor/enclosure/.venv/Scripts/python.exe' output/design-finish-2026-09-26/motion/verify_motion_finish.py
& 'C:/Users/Gluis/OneDrive/Documents/ChatGPT/New project/smart_compressor/enclosure/.venv/Scripts/python.exe' output/design-finish-2026-09-26/motion/verify_motion_finish.py --integrated --builder build_revi
```
