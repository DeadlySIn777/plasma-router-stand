# Motion purchase decision and physical interfaces - 26 September 2026

The two Y modules are already ordered. Keep that selection. The selected X and Z
listings match the requested nominal travels, but the Z assembly is not a
verified ready-to-install tool axis. This distinction matters before Monday's
order: the frame can be designed now; purchased mating holes and power-off
retention cannot be declared solved from the existing pictures.

| Item | Confirmed primary evidence | Decision |
| --- | --- | --- |
| Y pair, KHMOS B0C7GN24S1 | Exact Amazon variation is 1000 mm stroke, 10 mm lead. | Ordered; retain. Measure the supplied mounting nuts, nut access and stroke-end datums on arrival. |
| X, KHMOS B0C7GQTRRX | Exact Amazon variation is 800 mm stroke, 10 mm lead. Same HMS40 family as Y. | Correct intended travel/lead candidate. Base mounting and actual supplied motor current remain to be checked before final plates/current settings. |
| Z, RATTMMOTOR B09MVYGLNQ | 100 mm stroke; 219 mm base / 330 mm overall; 80 mm base width; SFU1605. Current listing specifies 3 A, 1.2 N.m, single motor output shaft. | Correct travel candidate, but hold a claim of installation-ready compatibility. Needs four output-hole details, output-face height, mounting nuts, and a qualified power-off restraint. |
| Proposed brake-motor alternative | STEPPERONLINE 23HS30-5004D-B280; dimensions and static brake rating below. | An optional replacement for the supplied Z motor, not a confirmed bolt-on accessory. Reserve its envelope; validate the coupling, flange and retention behavior before purchase/use. |

Sources: [X exact listing](https://www.amazon.com/dp/B0C7GQTRRX),
[Y exact listing](https://www.amazon.com/dp/B0C7GN24S1),
[Z exact listing](https://www.amazon.com/dp/B09MVYGLNQ).
The listing identifies M5 movable nuts on Z; that does not establish the
carriage output fixing-hole thread. The Y/X gallery mentions M3/M4 slot nuts;
it does not give the complete undercut, engagement, insertion and torque data.

## A concrete power-off retention route

The replacement candidate is a two-phase 5 A motor with an integrated power-off
brake: 57 x 57 x 116.5 mm body, diameter8 x21 mm shaft, 15 mm D-flat, brake
2.8 N.m static /24 V /4.5 W. Its body is60.5 mm taller than the original modeled
motor. The manufacturer page displayed **$40.90 goods only, China stock** on this
check; shipping, tax and delivered availability are unverified. Do not add that
amount to a supposed delivered build total.
[Manufacturer product page](https://www.omc-stepperonline.com/nema-23-stepper-motor-2-0nm-283-22oz-in-with-24v-4-5w-electromagnetic-brake-23hs30-5004d-b280).

The CAD reserves the published body envelope at the original flange-plane
assumption and marks it as a replacement candidate. It does **not** claim that
the manufacturer's complete STEP was imported. Its linked technical downloads
could not be retrieved through the available tools. Shaft/pilot/bolt-circle
alignment, coupling bore and engagement require a mating drawing or measurement;
NEMA23 alone does not prove that the complete replacement fits.

The static screen uses an explicitly chosen20 kg moving assembly plus200 N
downward external load and a3.0 design factor. With a5 mm lead and no credit for
screw friction, required holding torque is about0.946 N.m, giving a2.96 ratio
to the stated static brake rating. These are **screening loads**, not a measured
moving mass, a structural load rating or an emergency-stop result. A screw,
coupling or attachment failure is downstream of the motor brake.

The brake must be energized to release only after motor torque is established;
on a normal stop it must engage before drive torque is removed. Abrupt supply
loss still needs the actual brake response time, engagement energy limit,
worst-case drop test with a protected dummy load and suitable independent
support for maintenance. The public static specification does not close these
dynamic questions. The coil needs a separately rated24 V switched circuit;
it is not connected to a motor phase or logic pin. An unloaded500 mA driver
commissioning setting is not a loaded-axis holding qualification.

A counterbalance alone was not substituted: changing between the spindle and
torch changes the suspended load. No cheap spring was assigned a fictitious
force, stroke or failure behavior. The nominal single-ended stock motor is also
not drawn with an imaginary rear shaft for an add-on brake.

## Adapter correction actually implemented

`motion_completion.py` replaces the two unverified carriage slots with a
110 x110 x12.7 mm transfer-drill blank. The four known custom clamp holes and
their rear counterbores remain. All four purchased output-hole positions,
fastener/head dimensions and engagement must come from a recorded measurement
before the generator will produce that pattern. It rejects intersecting head
pockets and insufficient edge material. The guarded blank is not evidence that
the110 mm outline will suit every possible supplier revision.

The adapter's output mounting face is the datum; the current80 mm module stack
still controls an assumed placement in the whole machine. Once measured,
rebuild the head position and recheck actual tool reach. Transfer drilling means
marking centers with the plate aligned and then drilling the removed plate;
never use the purchased guide as a drill fixture with chips entering its rails.

The existing clamp instructions falsely referred to a known diameter28 AG60
torch and parked clamp. That stale statement is removed by the integration
extension. A separate torch-clamp generator takes an explicit measured insulated
barrel diameter, a40 mm usable clamp zone and nozzle offset. It has no diameter
default. It produces a review candidate only; it does not supply the missing
floating touch-off, breakaway, torch body, lead envelope or electrical interface.

## What this closes and what it does not

- Closes the misleading assumed-slot geometry and stale diameter28 torch claim.
- Establishes an actual purchasable brake-motor option with source dimensions,
  published static torque and a bounded screening calculation.
- Does not close Z mounting fasteners, normally engaged retention qualification,
  a real operational plasma head, cable bend/strain relief, supplier load ratings
  or whole-machine rigidity. The9-pose result covers nominal rigid solids only.

## Search boundary

The exact ASIN product pages and their gallery images were checked again.
[KHMOS's manufacturer index](https://www.khmos.com/) identifies HMS40 as a
single-rail ball-screw module. Earlier text calling it a belt module was wrong.
The index was discoverable but direct manufacturer-page retrieval returned403;
the RATTMMOTOR home site was unavailable through the tools. Searches located
third-party ZBX80 CAD and a300 mm manual, but neither was substituted for the
exact supplied100 mm revision. No vendor was contacted.

Historical source evidence remains in
`output/cad-repair-2026-09-25/motion/z-interface-resolution.md` and
`output/release-review/sources/module-gallery-source-manifest.json`.
