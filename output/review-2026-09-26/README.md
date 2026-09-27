# Review of the other session's Rev H, Rev I and variants — 26 September 2026

The owner asked for this review ("check it out"). It covers everything the other session pushed to `codex/initial-import` on 26 September:

- `9e3dd66`: Rev H.
- `4a67463`: Rev I.
- `ca9728b`: development variants.
- `38e9314`: retractable-ATC study.

Four independent reviews covered controls, mechanical design and the plasma head, water and cabinet, and the variants. The most important claims were then re-checked directly:

- the Rodent pin map, read from grblHAL's own [`btt_rodent_map.h`](https://github.com/grblHAL/ESP32/blob/master/main/boards/btt_rodent_map.h);
- the mode-switch race, re-run on the other session's own circuit simulator;
- the plasma reach, from the shared Z geometry;
- the cabinet drip lip and door, from the recorded solids.

**Owner decisions this review holds the work to:**

- **Controller:** BTT Rodent with grblHAL, reconfirmed on 26 September: "we're going to use the Rodent, not the Kraken".
- **Drive modules:** HMS40 X/Y with 10 mm lead, and a ZBX80 Z with 5 mm lead. Y is ordered; X and Z are to be ordered on 28 September.
- **Cutter:** VIV ARC CUT-50.
- **Bed architecture:** still the owner's open choice, so it is not judged here.

**Status, 27 September.** Five findings now have a design fix in the [GM1 controls package](../controls-2026-09-27/README.md), which works with either bed line. It is simulated only, not built or wired. The five:

- blockers 1–3 (Rodent inputs, E-stop, mode race);
- the welded-relay major finding;
- the Modbus major finding.

On the Rodent's inputs, BTT's own schematic shows six isolated inputs, not five: E1-MAX, on GPIO39 or 37, is unused by grblHAL's map. Once RS485 is dropped, two spindle-header pins are also free. Together these cover all real-time signals.

**Status, later on 27 September.** After the owner said "finish it", the one-piece bed line moved to [Rev K](../release-review/RevK-CAD/README.md), and the GM1 controls gained M9–M11. Between them they give design fixes for:

- **Blocker 4 (plasma reach).** A 135 mm drop bracket, sized for the owner's torch: a PT31-style straight machine torch, 270 × 28 mm (photo of 27 Sep; seller's figures). The torch tip reaches Z845 at the bottom of Z.
- **The cabinet.** A shorter drip lip, so the door opens; 30 entries on bonded gland plates; a filter fan; the VFD outside; the torch-start relay at the cutter.
- **Water and coolant:**
  - the router drain closes after its dwell;
  - a drain screen;
  - a fill watchdog;
  - NBR seals;
  - a manual drain;
  - a suction line without a high point;
  - a 32 mm refill air gap.
- **The float trip.** It now stops a cut.
- **The level-sensor guards.** They are handled by an operating rule, checked in CAD: with the torch low, plasma paths stay at X955 or less in the sensor band, since no sheet can lie over the sensors anyway. At the top of Z the torch clears them.

Still open:

- the float switch's margin and side load: set at commissioning; a lever-actuated switch if it sticks;
- the magnet preload offset;
- sludge carry-over to the pickup, and the strainer clamped through its bowl;
- the variants findings;
- the other minor findings.

Rev I, the six-panel line, has none of these fixes.

## Bottom line

The other session's work is careful, and its own evidence reproduces:

- Its Rev I acceptance index regenerates **30/30 PASS**, byte-identical.
- A fresh rebuild gives **1,669 solids with 0 unresolved intersections**, matching its record exactly.
- Its structure arithmetic reproduces, for example 0.1344 mm against its 0.1345 mm.
- The service check is PASS and current, and the variants package check is 243/243 PASS.

Its checks prove the geometry and bookkeeping it set out to prove. They do not catch four problems that block building it as drawn.

## Blockers

1. **The controls are built on the Kraken, which the owner rejected, and the Rodent is short of inputs.**
   - Rev I's `controls/README.md` says "Current controller: BIGTREETECH Kraken V1.1… The Rodent/THCAD selection… is not the current design". The head interface uses Kraken pins (PE11), and the ATC plan reserves Kraken STM32 pins. The variants' `requirements.json` records "Preserve the preference for Kraken onboard motor drivers" as confirmed.
   - **What the Rodent actually has** (grblHAL's own board map):
     - Four onboard TMC2160 drivers, all used by X, Y, Y2 and Z.
     - **Five inputs in grblHAL's map:** four limits and one probe. *Correction, 27 September:* BTT's schematic shows a sixth isolated input, E1-MAX (GPIO39 on V1.1, GPIO37 on V1.0), which the map leaves unused.
     - `CONTROL_ENABLE 0`: no E-stop, feed hold, cycle start or door input.
     - One RS485 port, which takes the spindle-direction pin when Modbus is on.
     - Flood and mist outputs, and an I2C header on GPIO27/26.
   - **Gaps in grblHAL:**
     - The map is marked untested.
     - The ESP32 build does not include the plasma (THC) plugin.
     - There is no ESP32 counter code for the THCAD-300.
     - The plugin needs a separate arc-OK input.
   - **Demand:** this machine needs about nine real-time inputs: four limits, probe, E-stop, permission/door, arc-OK and the THCAD frequency. It is eight if the E-stop removes the board's power, as the [GM1 controls](../controls-2026-09-27/README.md) now do.
   - **What keeping the Rodent means:**
     - a custom board map;
     - an MCP23017 on the I2C header for slow status signals only;
     - a hardwired safety stop;
     - either THC firmware work (enable the plugin on ESP32 and write a pulse-counter THCAD port), or an external up/down THC, which the owner earlier ruled out.
   - **Decision for the owner:** accept that work, or reconsider the controller.
2. **There is no E-stop or power-removal circuit.** The stop exists only as contacts that drop the tool-permission relays. On the Rodent the stop cannot even reach the firmware, so the axes would keep moving after a stop. Needed: a category 0/1 stop on a dual-channel monitored safety relay with manual reset. It removes motor DC, VFD mains (or STO) and cutter mains, with an auxiliary contact to a firmware E-stop input.
3. **Turning the mode switch with the start signal held can fire the wrong tool.**
   - This was re-run here on their own `circuit.py` simulator:
     - **Router → plasma:** the torch relay pulls in, with the router bed still in place and no water, in 39 of 54 relay-timing combinations, for up to 190 ms.
     - **Plasma → router:** the spindle relay pulls in, in 17 of 54, for up to 90 ms.
     - **Start signal released first:** zero.
   - "Never change mode during a job" is only a procedure.
   - **Fix:**
     - latch the mode relays so they can change only in SETUP;
     - put a per-mode ready contact in each tool coil;
     - drop the run-arm relay on any mode change;
     - add this case to `verify_circuit.py`.
4. **The plasma torch cannot reach the work.**
   - All designs share the same Z geometry. At the bottom of the 100 mm Z stroke, the tool plate's lower edge is at Z1070 (Rev J) and Rev I's head clamp face is at Z1095. The slats that carry plasma sheets are at Z850.
   - The torch would have to project about **215–245 mm** below its clamp. At that projection the float and breakaway geometry, and the play at the nozzle, change completely.
   - The router is fine: its bit reaches the bed at Z958.8.
   - Nothing states or checks this, and **it applies to Rev J too**.
   - **Fix:** a plasma drop bracket of about 150 mm, or a machine torch chosen for the projection, plus a torch envelope in the plasma checks and a plasma-mode Z limit.

## Major

- **A single welded relay contact starts a tool.** K_REQUEST, K_RUN_ARM or KM_R welded shut energizes the torch or spindle, and the Finder relays are not force-guided. **Fix:** force-guided relays with NC feedback, or a monitored safety relay for tool enable.
- **Modbus can bypass the hardware run permission.** If the VFD takes its run command over RS485, M3/M4 starts the spindle with the permission open. **Fix:** run and reverse by terminals through the permission relays, speed only over RS485, and an isolated RS485 link.
- **Cabinet:**
  - **Heat:** the sealed 500 × 400 × 200 mm box sheds only about 30 W at 10 K rise. The 1.5 kW spindle VFD alone loses about 45–75 W. The component list also omits the Rodent, THCAD, 48 V supply and VFD.
  - **Door:** the drip-cap front lip hangs 9.5 mm below the new box top and 16.5 mm in front of the door, so a side-hinged door hits it after about **2.4°**. Verified from the solids: lip Z655.5–675.5, box top Z665.
  - **Cable entries:** only 8 (2 mains, 6 signal) for about 18 field cables.
  - **EMC:** no bonding for EMC glands.
  - **HF:** the torch-start relay sits in the logic panel, so HF-exposed leads enter the cabinet.
- **Water and coolant:**
  - **Router mode:** it opens the pan drain and leaves it open. With no drain screen, chips, aluminum fines and the owner's mist coolant go to the plasma reservoir. Aluminum fines in inhibited water give off hydrogen, and the tank vents under the pan.
  - **Pump:** there is no valve-position feedback and no fill time limit, so a valve jammed by slag lets the pump run indefinitely.
  - **Seals:** EPDM seals are not oil-tolerant, so confirm the coolant is water-based.
  - **Sludge:** it carries over to the pickup, and a partly blocked basket overflows onto the lid by the pump.
  - **Strainer:** it is clamped through its bowl threads.
  - **Draining:** there is no manual drain for freezing or water changes.
  - **Suction line:** Rev I's is 3/8 in with a high point.
  - **Applies to Rev J:** the drain, coolant, sludge and manual-drain points apply to Rev J's water system too.
- **Plasma head:**
  - The float switch is held only 0.1 mm past its worst-case operating point, and its plunger is pushed sideways.
  - Outside probing, a float trip triggers nothing: no feed hold or alarm, and only 4.35 mm remain before the hard stop.
- **Variants:**
  - The ATC pin plan is on the Kraken.
  - The small machine's **100 mm Z leaves 3.85 mm of margin** for a fixed RapidChange dock. The retractable tray is blocked by any clamped stock.
  - The fixed dock takes 21% of the Y travel.
  - Neither design places a tool setter.
  - The shared locators land on **none** of the 4 × 8 bed beams: 0% bearing under the pin blocks and 46–51% under the seats.
  - The 4 × 8 ATC hood sits inside the head's own X travel.

## Minor

- **Magnet preload:** it is off the seat-triangle centroid, so the breakaway force depends on direction.
- **Torch lead:** no strain relief or service loop is defined.
- **Level-sensor guards:** they stand 10–35 mm above the slats at X ≥ 966.
- **Structure budget:** it is vertical only. The gantry bending term is simple to add, about 0.018 mm per 100 N.
- **Refill spout:** its air gap is 30 mm, just under the usual two-bore rule of 31.6 mm. This applies to Rev J's moved spout too.
- **Stale documents:** WATER-CONTROL and WATER-ELECTRICAL-REVIEW still describe the timers Rev I replaced.
- **Locator bushings:** the press fit closes the bore by up to 0.012 mm while acceptance uses the loose F7 band.
- **ATC pocket target:** the ≤0.05 mm repeatability target is tighter than the pins allow.
- **Report hashes:** reports are written with Windows line endings and hashed as bytes, so a Linux re-run marks them stale.
- **Cost register:** it was never updated for Rev H or Rev I. Rev I adds 164 part numbers (388 pieces) over Rev G, including 42 purchased item types, and none of them are priced.

## What these findings mean for Rev J

Rev J shares the Z geometry, the water system and the controller decision. Five findings apply to it:

- the plasma reach (blocker 4);
- the router-mode drain, coolant and sludge points;
- the refill spout air gap;
- the cabinet heat, if the VFD goes inside;
- everything about the Rodent's inputs.

Rev J has no plasma head or Rev I control circuit, so the head and circuit findings are Rev I's.

## The 4 × 8 for a friend

The variant is a layout, not a buildable design.

**Still to select or design:**

- the long-axis rack drive and motors;
- an X drive (a screw is too slow at 1.7 m);
- the gantry section;
- the Z;
- the torch and spindle mounts;
- THC inputs;
- flat mounting surfaces for 2.9 m rails;
- the electrical panel.

**Estimates, all rough, for a first build:**

- **Purchased parts:** about **$8k–19k**, mostly driven by the plasma cutter and the bed.
- **Labor:** about **330–660 hours**. $1,000 of labor for that is $1.50–3 an hour.

**At a $15,000 price:** about $12k is left for parts. That fits rack-and-pinion Y, stepper motors, a 2.2 kW spindle, a budget-to-mid plasma with THC, a slat water table and about 600 kg of steel. It does not fit servos, a Hypertherm and an ATC together.

**The $50k quote:** it usually includes an industrial plasma with tuned cut charts, servo drives, a machined frame, software, a certified panel, warranty, installation and support.

**Before promising "better and stronger":**

1. Commission the small machine, including plasma and THC.
2. Build and measure the 4 × 8 frame and one long axis.
3. Price it with a written spec and acceptance test, parts paid up front, staged payments and "prototype, as-is" terms.

## Recommended order of work

1. **Owner: choose the bed line.** Choose Rev J's hoisted one-piece bed or Rev I's in-footprint six panels, and give design work to one session.
2. **Owner: confirm the Rodent plan.** Accept the Rodent with an I/O expander, a custom map, a hardwired safety stop and the THC firmware work (or an external THC), or reconsider the controller.
3. **Safety circuit, for either line:**
   - monitored safety-relay stop;
   - force-guided tool relays;
   - latched mode selection;
   - run and reverse gated by hardware.
4. **Plasma reach:** a drop bracket and torch selection. Measure the CUT-50 torch first.
5. **Water:**
   - a drain screen;
   - drain closed or capped in router mode (or a separate router drip tray);
   - a fill watchdog;
   - coolant-rated seals;
   - a manual drain.
6. **Cabinet:**
   - the VFD outside or ventilated;
   - the drip lip raised;
   - 24 or more cable entries with EMC bonding;
   - the torch-start relay moved to a shielded box at the cutter.
7. **Cost register:** re-baseline it to the chosen line.
