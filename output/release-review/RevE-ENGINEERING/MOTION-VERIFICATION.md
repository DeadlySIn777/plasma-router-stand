# Rev E motion geometry and manufacturing review

The motion module contains **291 valid solids**. Five configurations passed the positive-volume interference test: the parked state and four X/Y travel corners, with Z at alternating ends of its 100 mm stroke. The checks found **zero unpermitted intersections** and **zero differences between local part volume and assembly part volume**. These are geometry checks, not a continuous-motion or structural certification.

The exact checked source hash and configurations are in `motion-validation.json`. The full machine exporter performs its own assembly and STEP round-trip checks. The final source is `motion_details.py`; its entry point is `make_motion(model, gantry_y=1275, head_x=575, z_lift=100, tool='router')`.

## Geometry and load path

| Item | Definition |
|---|---|
| Y guide midpoint | Y 275–1275 mm |
| X tool carriage center | X 175–975 mm |
| Y guides | Two HGR20 rails, nominal cut length 1420 mm; two blocks on each rail, 180 mm center spacing |
| X guides | Two 1200 mm HGR20 rails; four blocks, 160 mm horizontal and 60 mm vertical center spacing |
| Y guide center height | Z 1033 mm |
| Gantry beam | 1200 mm 80/20 40-8080; bottom Z 1155 mm; beam center is 80 mm behind Y guide midpoint |
| X carrier | 260 mm wide, 12.7 mm thick; lower edge Z 1143 and upper edge Z 1313.2 |
| Y drive shoe | 6.35 mm thick, sourced HMS40 mounting pattern |
| X drive shoe | 19.05 mm thick; its higher link platform clears the 75 mm motor bracket at the right travel end |
| Axial links | Three links, 80 mm pin centers, using SKF SA6C/SAL6C rod ends |
| Work-bed swap | Remove every component in group `removable_tool`; leave the Z stage and its carriage installed |

HGR guides carry the gantry and cutting moments. The HMS40 modules provide axial thrust through spherical links, rather than acting as the router's sole moment guides. Their thrust is still applied above the output face: 25.35 mm on Y and 38.05 mm on X. A 250 N axial force therefore produces 6.34 and 9.51 N·m respectively on the module output. These moments must be included in the overall strength screen; “drive only” does not mean zero moment.

The selected spindle envelope is the full **65 × 259 mm**, with a stated mass of 2.7 kg. A custom two-piece clamp now has its own defined bore, split gap, pinch screws and recessed mounting screws. It does not depend on the unknown bolt pattern of the clamp supplied with the spindle kit. The connection from that adapter to the Z module remains guarded for the missing supplier drawing.

## Defined joints

- Two Y side plates connect to four guide blocks through 16 M5 × 18 screws. The X carrier connects to four blocks through another 16 M5 × 18 screws. Nominal engagement in the published 6 mm-deep block threads is 5.3 mm.
- Three HMS shoes use the published four M4 holes: 30 × 30 mm pitch, along offsets 16/46 mm, transverse offsets 9/39 mm. M4 × 10 screws seat on a 2 mm remaining web and engage 8 mm in the specified 10 mm-deep threads. Counterbore depth follows the actual shoe thickness.
- Six machined clevises have a 7 mm gap, 6 mm ears and a horizontal 6 mm shoulder pin. Two 0.5 mm race spacers fill each bearing gap. Shoulder screws, washers and prevailing-torque nuts retain the joints. The pin's threaded section does not run in the bearing.
- Three 28 mm steel hex couplers receive M6 × 1 RH and LH threads, with 10 mm engagement at each end. RH/LH jam nuts lock adjustment. The couplers, clevises and support brackets are custom parts requiring machining; they are not included in the module prices.
- Sixteen 80/20 **40-3915** M8 T-nuts connect the beam feet and X guide face. M8 × 16 screws project 11.3 mm into the profile, engaging the 5.9 mm nut with nominal clearance to the cavity bottom. Fit must be checked against the actual purchased profile before final torque.
- The custom spindle clamp uses two M6 × 60 pinch screws and four recessed M6 × 20 mounting screws. Its final bore is machined with a 0.50 mm split shim installed. Clamp screw torque and spindle retention require physical verification.

Threaded CAD bores represent nominal thread envelopes. Part notes state pilot diameter, pitch and engagement. Flat-file pilots and counterbore operations are separate from through-cut holes. The large machined brackets require the STEP file and its machining notes; a perimeter DXF alone does not define them.

## Stops, homing and switch geometry

X has physical buffers at carriage-center X 168 and 982 mm. Y has buffers at guide-midpoint Y 268 and 1282 mm. Normal software travel is X 175–975 and Y 275–1275. Three home switches are modeled: X, Y1 and Y2. The fourth Z home interface depends on the missing Z mounting and endpoint drawing. No extra opposite-end input channel has been added.

The switch selection is Omron D2VW-01L2-1M, with the same mechanical envelope available as the UL-wire variant **D2VW-01L2-1MS**. These gold-contact switches use a 24 V isolated input at approximately 5 mA. Their signals must be level-shifted to the Kraken; 24 V must never reach a controller pin. COM/NC wiring gives an open circuit when the switch operates or its cable breaks. This is a homing/limit input, not a safety-rated stop circuit.

Switch cams have a 10 mm ramp and a 20 mm flat overtravel land. The CAD positions the 4.8 mm roller tangent to the cam: on the ramp it applies the radius correction `R × (sqrt(1 + slope²) − 1)`. The small lever and internal mechanism are not modeled. No collision is waived merely because the switch is actuated. Set the actual trip positions with a meter at low speed; published operating-position tolerance is not machine repeatability.

The steel stop feet clear the HMS motor-bracket envelope by 2.1 mm nominal. The lower X carrier clears the Y plate top by 0.7 mm nominal; keep the combined machined/shimmed vertical tolerance within 0.2 mm and verify the resulting clearance. At 600 mm/min and 20 mm/s², ideal stopping distance is 2.5 mm before control latency. The buffers are for commissioning at that low speed. They do not establish a permissible high-speed crash energy.

## Assembly and inspection

1. Finish welding the chassis before machining and shimming the guide datums. Do not use a weld-distorted rail cap as an assumed precision reference.
2. Attach the gantry beam feet and X guide face before installing rails that cover counterbored screw access. Confirm screw tips do not bottom in T-slots.
3. Fit the separate guide structure and move it manually through its travel before coupling the HMS drives. The spherical links must not pull misaligned guides into position.
4. Install the rods at 80 mm pin centers, square the two Y sides, tighten jam nuts and apply witness marks. Maintain at least 9 mm coupler engagement.
5. Set home cams, software limits and physical buffer clearances at low speed. Verify independent Y1/Y2 operation before automatic squaring.
6. Install the spindle clamp and check retention only after the Z output interface and power-loss restraint are resolved. Remove the complete tool assembly for the bed swap.

## Genuine remaining release holds

1. **ZBX80 output and base:** mounting-plane-to-output height, longitudinal output hole pitch/thread/depth, base-slot engagement, stroke endpoint datums and cable outlet. The currently reserved 80 mm output stack is explicitly an assumption. No fabricated Z hole pattern has been substituted for this data.
2. **HGR20 rail holes:** the seller's P40/E20/1500 drawing does not close dimensionally. Factory hole pitch and end datums must be resolved before the Y rails are cut and mating holes are drilled. The guide rails and custom guide plates are guarded accordingly.
3. **HMS40 base attachment:** bottom-slot nut cavity/engagement and exact stroke endpoint datums are missing. The nominal top interface is sourced; the bottom fasteners cannot yet be released. Motor current, torque-speed and connector envelopes are also unconfirmed.
4. **Z restraint and mode tooling:** no selected power-off brake or counterbalance is installed. A ballscrew is not assumed self-locking. The exact plasma torch mount and its approximately 110 mm mode-height change still depend on actual torch and Z dimensions.
5. **Cable and cover integration:** chain anchors, way covers and the actual spindle/torch cable bend envelopes are not closed by this module. They require final whole-machine integration.

These holds prevent a claim that the complete machine is ready to order or manufacture. The CAD contains a substantially detailed motion structure, not a released or commissioned machine.

## Source records

- [HMS40 exact dimensioned supplier drawing](../sources/HMS40-dimensioned-drawing-2026-02-10.jpg).
- [iMetrx guide drawing](../sources/iMetrx-HGR20-dimensioned-drawing.jpg).
- [SKF spherical plain bearing and rod-end catalog](https://www.skf.com/binaries/pub12/Images/0901d19680154a05-06116_1-EN_tcm_12-122020.pdf), SA6C/SAL6C table.
- [80/20 40-3915 T-nut](https://8020.net/40-3915.html) and [40-8080 profile](https://8020.net/40-8080.html).
- [Omron D2VW manufacturer data sheet](https://components.omron.com/sites/components.omron.com.us/files/datasheet_pdf/C095-E1.pdf).

Quantities are in `motion-component-quantities.json`. Child envelopes marked `INCLUDED_...` are not additional purchases. Price observations and separate unquoted machining allowances are in `motion-cost-handoff.json`.
