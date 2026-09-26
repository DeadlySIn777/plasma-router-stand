# Rev I router spindle and clamp transfer

[router-transfer-verification.json](router-transfer-verification.json) is the current router-transfer geometry record. The complete run passed eight ordered routes containing 68 continuous segments, including restoration. Five transient interference snapshots contain all 1,669 parts and have no unresolved intersections. The parked and restored spindle and both clamp halves match their prescribed solids exactly. All checked motion stays inside X = 0–1150 mm and Y = 0–1450 mm.

The run binds motion source `3f3555a24bf84ce7444d3f5f516fe8c414e56689671d662310edddc4df16da3f`, staging helper `5eb15e7d426e8bfb13d90d6fb5340f424f58237d813e1f9e6735b379ddd491a3` and this task's checker `48b5c14c0ea5fc5b70c26b9db721f213531409ea46f9e198f396f06920567425`. All recorded source files were unchanged during the run. Repeat with `check_router_transfer.py` using the CAD Python environment.

## Required machine state

Use the separately proved panel1/beam1 preparation in [check_transfer_staging.py](check_transfer_staging.py). Keep the router installed while the six bare boards and panels 2–6 are stored. Panel1 becomes the temporary rear work surface on beams 3 and 4, retained by its four existing panel clamps. Beam1 rests on beam2 with both temporary keepers engaged. Only then remove its front seats. Beam1 stays in this temporary upper position throughout the router transfer.

The front portal must remain open to its full 105 mm depth. A beam stored in the front/lower slot would reduce the available depth to 54.2 mm, which cannot pass the 65 mm spindle. The other bed-route and prerequisite reports must also pass; this router report does not replace them.

Isolate the machine electrically, disconnect the spindle cable and remove the cutter. Park the gantry at its rear/high position: X = 575 mm, Y = 1275 mm, Z lift = 100 mm. The proof contains the disconnected 65 × 259 mm spindle envelope and no actual torch.

## Removal and parking

1. **Support the spindle before opening its clamp.** Put the two pinch screws in their modeled hardware-tray locations. The rear clamp remains bolted to the adapter. Move the front cap 80 mm forward, 170 mm left, then 26.4 mm forward. Lower it 244.2 mm onto the clean, dry temporary panel1 surface. Its resting bounds are X = 350–460 mm, Y = 970–1014.75 mm, bottom Z = 940.8 mm. The spindle remains supported by the operator during this step; a helper can handle the cap.
2. **Move the bare spindle through the open front portal.** Withdraw it 80 mm forward from the rear clamp. Move its axis to X = 900 mm, then Y = 70 mm. Lower its bottom from Z = 1060 mm to Z = 350 mm. Carry it vertically rearward to Y = 600 mm, beyond the cabinet. Move its axis left to X = 865 mm and rotate 90 degrees about global Y to lay its axis along +X. Raise the axis to Z = 620 mm, move the left end to X = 500 mm, then move rearward to Y = 1080 mm. Slide axially 260.5 mm right through the open cradle recesses, then lower 20.3 mm into the seats. The final axis runs from X = 760.5 to 1019.5 mm at Y = 1080 mm and Z = 599.7 mm.
3. **Remove and park the rear clamp.** The spindle now rests in its two existing cradles. Remove the four clamp-mount screws to their modeled tray locations. Withdraw the rear half 80 mm forward. Use the right-front lane with its lower-left corner at X = 845 mm, Y = 50 mm, and lower its bottom to Z = 600 mm. Move rearward to Y = 600 mm, then left to X = 430 mm. Move rearward to Y = 1180 mm, shift left to X = 300 mm and lower onto the lid at Z = 433.096 mm.
4. **Move the front cap from panel1 to the lid.** Lift it 40 mm from the table. Use the same right-front lane and X = 430 mm bypass, but finish at Y = 1230 mm. Shift left to X = 300 mm and lower onto the lid at Z = 433.096 mm. The temporary table is now clear for the plasma-head parts.

The X = 430 mm clamp lane passes beside the staged panel-rack guard uprights before shifting left into the existing parking locations. The bare spindle enters its cradles axially at Z = 620 mm, below the refill hose. Carrying the entire closed clamp directly down into the cradles was rejected because it intersected that hose.

Fit the spindle's prescribed retaining straps before leaving it parked. Strap material, routing and restraint qualification remain physical acceptance items; they are not included as modeled solids in this path proof.

## Restoration

Return the plasma head to its defined parking cradle and recreate the same temporary panel1/beam1 state before bringing the router back. Reverse the four routes in order: front cap from lid to panel1; rear clamp from lid to adapter; spindle from cradles to rear clamp; front cap from panel1 to the spindle. Secure the rear-clamp mount screws before returning the spindle. Support the spindle continuously until the front cap and pinch screws have been fitted and the clamp has been accepted. The checker independently executes these reverse movements against the corresponding actual part states.

Only after the router is retained should the temporary keepers, beam1, seats, panels and boards follow their coordinated restoration procedure. Reconnect power after completing the machine checks.

## What the proof establishes

The checker tests the complete phased CAD, not isolated moving parts. At the two coincident split-bore interfaces, exact relative cylinder sweeps establish clearance throughout departure and return. Their capsule-shaped swept solids are intersected with the matching clamp material; no unproved contacting pair is silently ignored. All other obstacles use the continuous minimum-distance bound. The cradle seating path also passes.

The interference snapshots do not make handheld poses self-supporting. Operator grip, reach, finger clearance, the physical handling trial, clamp torque, strap retention, real cable/connector extensions, supplier mounting interfaces and dimensional tolerances remain outside this nominal rigid-body proof. Keep the actual spindle within the modeled envelope or repeat the path check with its measured shape.

`router-transfer-closed-clamp-rejected.json` and `router-transfer-distance-contact-diagnostic.json` are historical diagnostics. Their rejected or incomplete routes are not current instructions.
