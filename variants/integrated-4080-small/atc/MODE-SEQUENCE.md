# Manual mode setup and automatic tool-change boundary

These are functional interlocks for later controller implementation. They are
not firmware, operating G-code or evidence of an energized machine test.

1. Isolate cutting power and positively retain Z. Remove the complete torch or
   owner spindle/boot module using its common quick dock. Do not dismantle the
   owner's working boot/clamp or use the dust actuator for another purpose.
2. Park the common gantry toward the front at guideY275 while handling the
   cover. Remove the two storage L keepers. Withdraw both captive cover M4
   screws6 mm, then follow the proven cover route to storage. Refit both L
   keepers and R clips. Reverse this route when preparing plasma mode.
3. The stage may move only with the cover stored, both endpoint clamp bolts
   removed, the head in its checked bypass pose and the kit/tool/stock envelopes
   within the accepted limits. The actual limit inputs and pin/clamp sensing
   must agree with the physical state; do not derive seated status from motor
   step count. The slide is horizontal; no self-locking claim is made.
4. Approach the selected end stop slowly, insert the left round/right relieved
   locator bolts and apply the verified clamping process. The motor does not
   provide the locked tool-change reaction path. Fit both nuts/washers before
   any tool change. Pin and clamp capacity remain actual hardware qualification.
5. Wood cutting requires the full bed down, all retention engaged, water below
   the dry-work threshold, cover stored and magazine **parked/locked**. Deploy
   the magazine only for a tool change with the tool at the verified bypass/
   clearance pose. Park and lock it again before machining the full field.
   The existing owner boot needs its calibrated clearance position. Spindle
   reverse/speed and real tool setter/nut-sensing operation must follow the
   manufacturer's implementation with the actual pocket coordinates.
6. Plasma mode requires the bed fully raised on both positive stays, magazine
   parked/locked, cover installed/clamped and spindle cutting power inhibited.
   The actual plasma start/THC circuit, isolation and EMI controls are separate
   commissioning requirements. A pilot-arc label alone does not identify them.
7. Bed movement occurs with the entire tool module removed, all guide sections
   stored, complete front stops parked400mm rearward and the common gantry at
   guideY1275/X975/Zlift250. The ATC is parked with its cover fitted. Its fixed
   and parked material is behind the current moving bed's continuous
   Y1182.8457 bound. Restore the stops before restoring guides, using the
   checked route for the actual bed angle, and verify retention/state inputs
   before permitting motion. Fixed bed receivers are checked separately in the
   combined machine changeover report.

Current actuator identity, slide travel, clamp geometry and whole-boot moving
scope were already supplied. These are not new questions for the owner. Actual
machine registration, exact supplier CAD, load/retention/thermal tests and
complete delivered cost remain explicit verification work.
