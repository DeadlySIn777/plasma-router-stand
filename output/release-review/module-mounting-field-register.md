# Exact module drawing field register — 24 September 2026

**25 September correction:** the ZBX80 70 mm transverse dimension belongs to the smaller Ø5 output fixing-hole row, not the larger Ø7 bores. The earlier appended adapter/M6 interpretation below is superseded by the [corrected source evidence](../cad-repair-2026-09-25/motion/z-interface-resolution.md). Output-face height, longitudinal hole pitch and thread/depth remain unresolved. The corrected model omits the unsupported M6 carriage screws and guards the adapter from individual fabrication export.

**HMS40 nominal mating dimensions recovered; ZBX80 output interface remains partial.** This register now includes the detailed HMS40 engineering drawing from the exact listing's A+ images. The earlier main-gallery search missed that drawing.

“Verified” below means a legible nominal seller dimension on the exact ASIN gallery. It does not mean a measured, revision-controlled or toleranced manufacturing dimension. No holes were scaled from photographs.

## KHMOS HMS40 — 800 and 1000 mm travel

Exact listings: [800 mm B0C7GQTRRX](https://www.amazon.com/dp/B0C7GQTRRX?th=1) and [1000 mm B0C7GN24S1](https://www.amazon.com/dp/B0C7GN24S1?th=1). Both exact-ASIN HTML snapshots contain the same six primary gallery image URLs.

Saved engineering drawing: [HMS40 drawing dated 2026-02-10](sources/HMS40-dimensioned-drawing-2026-02-10.jpg). [Original supplier image](https://m.media-amazon.com/images/S/aplus-media-library-service-media/e029d02f-52aa-453f-bd88-9a2b586ceecb.jpg). Drawing title HMS40-L□□-S□□-M57-BC, Sichuan Khmos Technology Co., Ltd. Use the unbracketed 57×56 inline-stepper dimensions; bracketed dimensions refer to an alternate motor flange.

| Published field | Nominal value | Use |
|---|---:|---|
| Total inline length | stroke + 201 mm | S+145 plus 56 mm motor; use 1001 / 1201 mm, replacing rounded marketing lengths |
| Carriage along × across | 65 × 48 mm | Published nominal interface envelope |
| Output face above mounting bottom | 65.5 mm | Published datum height |
| Top mounting holes | 4 × M4, depth 10 mm | 30 × 30 mm pattern |
| Along-motion hole offsets from nonmotor carriage end | 16 / 46 mm | Derived rear margin 19 mm; pattern is not centered along the 65 mm length |
| Across-motion hole edge margins | 9 / 9 mm | Derived from centered 30 mm pitch across 48 mm |
| Bottom slots | M4 nuts, 28 mm center pitch | Nut section/engagement still needs matching hardware |
| Side slot | M3, 19 mm above bottom | Published slot centerline |
| Carriage side holes | 4 × M3 depth 6, bilateral | At 32.5 mm along the carriage; 15 mm below top then 10 mm lower |
| Nonmotor end cap | 42 mm wide, 60 mm high | Published nominal envelope |
| Motor / bracket | 57 mm wide × 56 mm long / 75 mm high | Cable exit remains un-dimensioned |
| Net mass 800 / 1000 travel | 3.9 / 4.6 kg | Printed drawing table |
| Selected screw | 16 mm diameter, 10 mm lead | Printed repeatability ±0.03 mm is not machine accuracy |

Remaining: base-slot cavity/nut engagement, motor current/torque-speed data and cable exit, unambiguous output position at stroke endpoints and overtravel, plus guide-load qualification for routing. Top mating plates can now use a sourced hole pattern instead of invented holes.

The [official HMS40 page](https://www.khmos.com/high-performance-easy-access/hms40) has an empty Downloads block. The official [2D drawings](https://www.khmos.com/download/1930836141977767936.html) and [3D models](https://www.khmos.com/download/1930836162129567744.html) pages both return a no-content message. Snapshots are saved. No public usable CAD file was found.

## RATTMMOTOR ZBX80 — exact 100 mm travel ASIN

Exact listing: [B09MVYGLNQ](https://www.amazon.com/dp/B09MVYGLNQ?th=1).

| Saved seller drawing | Original |
|---|---|
| [Top view](sources/B09MVYGLNQ-gallery-2.jpg) | [Amazon image](https://m.media-amazon.com/images/I/61WxScULDML._SL1500_.jpg) |
| [Side view](sources/B09MVYGLNQ-gallery-3.jpg) | [Amazon image](https://m.media-amazon.com/images/I/61HH-r4RqQL._SL1500_.jpg) |
| [Bottom view](sources/B09MVYGLNQ-gallery-4.jpg) | [Amazon image](https://m.media-amazon.com/images/I/51wBxuUiRML._SL1500_.jpg) |
| [Four output fixing holes identified](sources/B09MVYGLNQ-gallery-8.jpg) | [Amazon image](https://m.media-amazon.com/images/I/71E5oziXi9L._SL1500_.jpg) |

| Published field | Nominal value |
|---|---:|
| Total length including inline motor | 330 mm |
| Base between outer end faces | 219 mm |
| Between inner end faces | 195 mm |
| Each end plate thickness | 12 mm |
| Base width | 80 mm |
| Carriage along travel × transverse width | 50 × 90 mm |
| Nonmotor end height / motor end height from bottom | 67 / 78 mm |
| Base extrusion height | 20 mm |
| Carriage body height | 35 mm |
| Motor width | 57 mm |
| Bottom and side fastening nuts | M5 movable nuts |

The **35 mm carriage body height is not the mounting-plane-to-output-face height**. That assembled stack dimension remains unknown.

Gallery 8 identifies four output fixing holes. The top drawing labels the smaller holes **diameter 5 mm**, and gives **70 mm transverse spacing**. It does not specify the pitch along travel, thread, thread depth, datum or tolerance. **Do not create a 70 × assumed-value hole pattern or reinterpret diameter 5 as M5.** Larger holes are marked diameter 7, but not established as usable mounting holes.

The bottom drawing also prints 14, 26, 54 and 66 mm profile annotations. Keep them attached to the original graphic; no complete T-slot centerline/undercut geometry or fastening scheme is established. Gallery 5's “30150” extrusion label conflicts with the 80 mm dimensioned width and is not used for CAD.

Still needed: complete base and carriage mating drawings, output-face height, travel endpoint datums and overtravel, motor lead/connector envelope, and revision-controlled drawing or STEP for this exact product.

## Release consequence

Use the recovered dimensions to correct provisional envelopes. Keep final hole machining and the fully checked assembly release on hold until the suppliers provide the missing drawing fields and the CAD is checked against them. No supplier messages or purchases were performed.

The structured values and missing fields are in [module-mounting-field-register.json](module-mounting-field-register.json). Exact-ASIN HTML snapshots and original seller gallery images are saved in the sources folder.

## Z slide (RATTMMOTOR ZBX80-class, 100 mm stroke) — owner-supplied drawing, 25 September 2026

The owner supplied the listing's dimensioned top-view drawing (330 mm class). "Imported" below means a legible nominal dimension on that drawing; it is not a measured or toleranced manufacturing dimension. The drawing is a TOP view only.

| Published field | Nominal value | Use |
|---|---:|---|
| Overall length incl. motor | 330 mm | Matches modeled envelope stack |
| Slide body length x width | 219 x 80 mm | Matches the modeled base envelope |
| End blocks | 12 mm each | Bearing/end-block thickness |
| Carriage plate along x across | 50 x 90 mm | Confirms the modeled 50 x 90 output envelope |
| Carriage holes | phi7 and phi5 | phi7 pair spacing 70 mm ACROSS the body |
| Motor | NEMA23 (57 sq) | Inline behind a coupler housing |

Adopted into CAD: TOOL_ADAPTER_110 (110 x 110 x 12.7) carries two vertical 7 x 30 slots at the 70 mm across-pattern, absorbing the UNDIMENSIONED along-travel hole pitch, and the shared spindle/torch clamp pattern moved outboard to X±45. Remaining measure-on-receipt fields: along-travel hole pitch, tapped-vs-through carriage holes, mounting-plane-to-output height (the 80 mm stack stays an assumption), base-slot fastening, endpoint and cable datums. Torch interface note: the AG-60 straight body barrel is ~Ø27.9 with an M22 x 1.5 head thread (owner-supplied); the parked TORCH_CLAMP halves use bore Ø28.00/+0.05.
