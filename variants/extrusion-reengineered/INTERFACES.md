# XR1 motion interfaces — engineering development

This integration removes both continuous 1,450 mm steel cap bars and both continuous steel Y datum strips. The owned HGR20 guides carry the gantry loads directly on the inner faces of the 4080 upper beams. The HMS40 modules remain drive-only; removing independent guides would change the load path and is outside this design.

No purchasing, price assumption, CAM release, real torch dimension or new ownership assumption is established here. `motion.py` builds named review solids; `interface-audit.json` records its checks and source hashes. `motion-fabrication.csv` includes custom parts and standard fasteners that must remain in the material ledger until actual ownership or a nonoverlapping owned-stock nest is proved.

## Planes and geometry

| Interface | XR1 nominal geometry | Consequence |
|---|---|---|
| Upper 4080 beams | Bottom Z973; top Z1053; section 40 wide × 80 high | Inner side-slot centres Z993/1033; guide centre stays Z1033. |
| Left / right HGR20 seats | X50.8 / X1099.2; Y15–1435; Z1023–1043 | No 8 mm datum strip. The 20 mm rail base spans the 8.2 mm slot mouth with nominal 5.9 mm lands on each side. |
| Guide block outputs | Left X80.8; right X1069.2 | Both block/shoe groups move 8 mm toward the outside. Y block spacing remains 180 mm. |
| Y side shoes | Left X80.8–93.5; right X1056.5–1069.2; Z1011–1142.3 | Existing beam mounting coordinates stay in Y/Z. Link window is widened from 33 to 49 mm, retaining 7.35 mm height. |
| HMS40 base | Z1065.7, from nominal 12.7 mm pads on Z1053 | Module only rises 1.7625 mm. Guide, gantry and tool Z stay unchanged. |
| Y module centres | X25.4 / 1124.6; nonmotor end Y1220 | Body envelope Y95–1220; complete inline-motor envelope Y19–1220. Actual endpoint and cables remain unmeasured. |
| Y drive link | End-height difference 1.7625 mm over 80 mm Y | 1.262093° inclination; eye distance 80.019413 mm. Nominal rod engagement 9.990294 mm each. Existing spherical joints accommodate the modeled angular change, subject to real assembly clearance. |
| Plasma drop | 148 mm; 110 × 218 × 12.7 mm plate | Tracks the slat reduction from Z911 to Z878. Actual torch grip, nozzle and cable remain absent. |

The short saddle pad's inboard edge stops 0.5 mm before the guide mounting face: left X−19.7–50.3, right X1099.7–1169.7. Extending the pad to X60 would collide with the top 2 mm of the moving guide block; that defect was found and corrected in the targeted check.

## Fasteners can be assembled and serviced

Each HMS40 has three candidate saddle stations, Y190/700/1100. These clear the top fishplates at Y60–140, 590–670 and 1140–1220: the middle station's spacer envelope has 6 mm nominal clearance. All pad extents remain within the modeled module body Y95–1220; support gaps are 510/400 mm. Each station consists of a 70 × 60 × 12.7 mm horizontal pad and a 60 × 80 × 9.525 mm outboard plate. Two underside M4 screw heads sit in Ø7.5 × 4 mm pockets, leaving an 8.7 mm pad web and nominal 7.3 mm engagement for M4 × 16 in the module's bottom sliding nuts. The nominal bottom-slot separation is 28 mm. Actual slot opening, nut shape, engagement and permissible support spacing remain supplier/measurement holds.

Preassemble the module to its pads from below before lowering it onto the beams. Two M5 × 25 edge screws join each pad to its side plate. Four M6 × 25 frame screws attach each side plate through solid 6.4 mm compression spacers to the outboard side slots at Z993/1033; their heads are outside the module and remain accessible. No screw is hidden underneath an installed module and then incorrectly assumed tightenable. The small edge-joint ligaments, thread pullout, spacer bearing and clamp slip still require proof loading. CAD shows the external frame screw grip/head; the unknown in-slot thread/nut bodies are deliberately absent.

Gantry end brackets are selectively retained as two integral billet parts, each with a 150 × 80 × 82.7 mm finished envelope: a 12.7 mm horizontal flange and 70 mm downstand. The web is shifted 8 mm outward to meet the revised shoe planes. Existing four M8 beam-slot coordinates per end remain unchanged; four M6 × 22 screws per end pass the 12.7 mm shoe and engage nominally 9.3 mm in the web. There are no gussets, separate flange/web edge joints, or changes in the inherited long X guide-face plate. Raw billets need machining allowance beyond the listed finished envelopes and are not credited to the two owned thin sheets.

Each Y link support is two flat parts: a 99.8 × 48 × 6.35 mm flange and a 48 × 40 × 12.7 mm web. Two flush M5 × 20 screws engage nominally 13.65 mm in the web; their Y positions clear the existing M6 cross-holes. The wider flange passes through the widened shoe window. No integral support billet or welded aluminum joint is assumed.

All six link clevises are also retained as integral 40 × 48 × 32 mm billet parts, preserving the original 6 mm sole, 6 mm ears, 7 mm ear gap and common 6H7 pin bore. This removes the proposed ear/base edge joints and their 24 additional M3 fasteners. The main corner and clevises follow the user's preference for billet on selected load-path parts. Saddle pads and Y-link support plates remain economical flat parts. The custom clamp, Z carrier, long X guide-face plate and other inherited fabricated head parts remain explicitly included in the fabrication manifest rather than being assumed owned.

Four short welded steel stop carriers replace the old cap attachment. Their lower legs attach to the inboard lower side slot at Z993, their floors stay below Z1009, and towers support a landing above the blocks while retaining the original stop-base footprint. These are fabricated plate assemblies, not deep machined billets. The floors and towers are positioned outside the moving block extremes. Each carrier needs a weld/joint and low-speed crash-energy check. They are commissioning buffers, not a rated high-speed emergency stop.

## Real interfaces still control release

- **Rail screws:** The recovered iMetrx drawing gives Ø6 through / Ø9.5 counterbore × 8.5 deep, but inconsistent pitch/end arithmetic. Sliding T-slot nuts remove the need to invent a custom bar hole pattern. Use every verified real rail fixing position and appropriately rated M5-compatible nuts; select screw length from the actual nut engagement and root clearance. No rail screw pattern is modeled until measured. Do not replace these with M6 screws through nominal Ø6 holes.
- **Rail seating:** The existing seat targets remain 0.05 mm per 1,000 mm and 0.05 mm parallelism over travel. A profile's external dimensions do not establish these. Measure face straightness/twist under final bolt torque; align with hard shims at the actual rail mounting stations or another explicitly designed rigid seat correction. Do not use soft isolation washers in the guide clamp stack. If the actual profile cannot meet alignment under load, this direct mount is not qualified.
- **Extrusion section:** Only nominal dimensions were read from the primary drawing: 40 × 80, slot centres 20/60, mouth 8.2, core Ø6.8. T-nut fit, permissible tightening, section properties and straightness are not guaranteed by that picture. The frame's separate stiffness requirement remains in `params.py`.
- **HMS40:** The recovered drawing nominally gives 28 mm bottom M4-slot separation, 65.5 mm output height, 4 × M4 output threads depth10 on a 30 × 30 pattern, and a 16 mm screw with selected 10 mm lead. None of this replaces measuring the user's delivered module, actual lead, bottom nuts or endpoints. The drawing identifies its 57 × 56 inline-motor variant.
- **Z/tool:** Output height, along-travel hole pitch, actual thread/depth, retention at power loss, cutter projection and torch interfaces remain guarded. The plasma insert is unbored. There is no invented cutter wiring or operational plasma claim.
- **Wet/electrical service:** Keep plasma work return off the linear bearings by connecting it directly to the work/slat system. Provide deliberate protective bonding independently of dirty bearing contact. Shield aluminum/steel joints from wet debris; any corrosion barrier must preserve hard structural seating and a deliberate bonding point. No claim of electrical isolation follows from paint, extrusion or T-slot nuts.
- **Material credit:** Two nominal 12 inch owned sheets are finite shared inventory. The pad, sideplate, foot, head and other frame-plate allocations must be nested together. Every remaining fabricated part stays in the new-stock takeoff until physically verified owned.

Primary nominal sources: [HMS40 engineering drawing](https://m.media-amazon.com/images/S/aplus-media-library-service-media/e029d02f-52aa-453f-bd88-9a2b586ceecb.jpg), [4080 section drawing](https://m.media-amazon.com/images/I/61wXCBace9L._SL1500_.jpg), and the locally preserved `output/release-review/sources/iMetrx-HGR20-dimensioned-drawing.jpg`. These drawings supply the stated nominal fields, not a certification of the assembled machine.
