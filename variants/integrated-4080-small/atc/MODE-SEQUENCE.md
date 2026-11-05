# Mode sequence - passive captured ATC

Use the current integrated 4080 small-machine assemblies. The bed's current
continuous rigid-body maximum Y is 1182.8457 mm; it remains ahead of the fixed
ATC/parked assembly. The actual root bed/guard/stop checks govern the combined
changeover, rather than an old cassette envelope.

## Wood mode

1. Bed closed on its fitted support/locator system, with positive retention.
2. Front motion stops on their operating datums; home/square the machine.
3. Splash screens in their internal storage racks; plasma start inhibited.
4. Plasma hood on its storage hooks with keepers/R clips fitted. Its two M4x6
   service screws are held in owned tool storage.
5. Owner router head docked; actual boot/spindle registrations calibrated.
6. Magazine normally parked 200 mm. For a tool change, confirm zero spindle
   speed and head/boot flyover clearance, then move the existing slide to 0.
   Its integral tongues enter the passive capture roofs/guides; no endpoint
   bolt or separate unlock actuator is required.
7. Require deployed endpoint and both seated capture confirmations, energized
   axis and qualified axial holding/preload before the spindle approaches a
   pocket. Use the actual calibrated manufacturer engagement routine and
   tool setter. Source pocket XY axes are 507.5/552.5/597.5/642.5, Y1100;
   the source body's bottom Z1051.85 is not a nut engagement plane.
8. Raise the loaded tool/boot to confirmed clearance, stop the spindle, then
   park the magazine 200 mm before returning to full-bed cutting.
9. Any capture/endpoint/energy/tool-state fault inhibits continuation and
   requires recovery. There is no claim of a power-loss axial lock.

## Plasma changeover

1. Stop/isolate both cutting sources. Remove the router head module, retain
   the shared receiver, and lock the common carriage at the prescribed rear
   service pose before the integrated bed/stop/guard handling sequence.
2. Keep the magazine at 200 mm. Automatic deployment is inhibited in plasma
   mode and whenever the plasma hood is fitted.
3. Fit the hood from its hooks by the reversed checked path. Seat its two
   outboard tabs on the deployed receiver roofs and insert two M4x6 screws.
   No long spacers cross beneath the housing.
4. Follow the current integrated front-stop parking/refit and splash-screen
   handling sequences. Positive stop state, bed state, guards, tool dock and
   plasma isolation remain controller commissioning requirements.
5. Verify the gravity water/overflow system and actual torch interfaces before
   enabling plasma; the ATC source model does not qualify those systems.

## Return to wood

After plasma isolation and cleanup, remove the two M4x6 cover screws and keep
both in owned tool storage. Remove both storage keepers as needed. Lift the
cover 500 mm, rotate it 90 degrees about Y, shift 390 mm left/70 mm rear,
lower 1182.35 mm and insert 90 mm right onto its hooks. Refit keepers/R clips.
The continuous cover route and 8 mm screw-release sweeps pass the subsystem
check. Reinstall and verify the actual router head and calibrated boot joint.

Automatic mode logic is controller-independent at this stage. Pin assignments,
sensor part numbers/placements, RPM/engagement calibration, force qualification
and the actual executable controller M6 routine require binding to the received
hardware and vendor integration package. No guessed G-code is authorized by
this sequence document.
