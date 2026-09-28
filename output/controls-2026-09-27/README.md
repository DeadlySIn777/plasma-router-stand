# GM1 controls: the stop, the start chain and the Rodent wiring (27 September 2026)

The [26 September review](../review-2026-09-26/README.md) found three problems in the controls that block building GM1 on either bed line:

- There is no E-stop or power-removal circuit.
- Turning the mode switch with the start signal held can fire the wrong tool.
- The design is built on the Kraken, which the owner rejected, and the Rodent is short of inputs.

It also found two major problems: a single welded relay contact can start a tool, and a Modbus command can bypass the hardware run permission.

This package fixes all five. It applies to both bed lines: Rev J (one-piece hoisted bed) and Rev I (six panels in the footprint).

**Later on 27 September** three more changes were added for Rev K ([RevK-CAD](../release-review/RevK-CAD/README.md)):

- M9: the router-mode drain closes after its dwell.
- M10: a fill watchdog.
- M11: the torch float switch stops a cut.

M9 and M10 close the review's water findings on the controls side. M11 closes its "a float trip triggers nothing" finding.

**Later again, for Rev L** ([RevL-CAD](../release-review/RevL-CAD/README.md)), the owner's RapidChange tool changer needed two more:

- M12: spindle reverse, because RapidChange unloads a tool with the spindle in reverse (M4).
- M13: the drive for the tool changer's retracting magazine.
- M14: the dock motor is fed through the Z top switch, so the dock can only move with Z up.

**What it builds on.** It starts from the other session's Rev I relay circuit (`output/design-finish-2026-09-26/controls/circuit.py`). That file is imported read-only and left unchanged, and its hash is recorded.

**What is kept.** Rev I's water logic is kept, with three changes:

- Fill, drain and timers are kept, except that the router drain now closes after its dwell (M9) and the fill has a watchdog (M10).
- Bed confirmation is kept.
- The mode relays are kept.
- The head interface is kept, with the float switch added to its loop (M11).

**What is replaced:**

- the stop;
- the tool-permission chain;
- the tool outputs;
- the controller interface.

The owner's controller decision is built in: BTT Rodent with grblHAL.

**Status:** design and simulation only. Nothing has been built, wired, compiled or flashed, and no safety category or performance level is claimed. The run results are in [gm1-circuit-verification.json](gm1-circuit-verification.json) and [rodent-io.json](rodent-io.json).

## What changed

| # | Change | Review item it closes |
|---|---|---|
| M1 | **E-stop.** A dual-channel safety relay (SR) with manual reset drives two contactors, K1 and K2. One main pole of each, in series, switches each of: the Rodent's 48 V, VFD mains and plasma-cutter mains. The contactors' mirror NC contacts form the reset feedback loop. A third safety contact feeds Rev I's water and tool permission chains, replacing its two field stop contacts. The Z brake is powered through K1 and K2 and a 3 s on-delay, so it engages whenever either contactor opens. | Blocker 2: no E-stop |
| M2 | **Per-mode ready relays.** K_RDY_R (router water sequence done) and K_RDY_P (plasma water sequence done) sit in series in the spindle and torch coil paths. A tool can only start after its own mode's 75 s or 12 s sequence has finished. So a mode change with the start held cannot fire the other tool. | Blocker 3: mode race |
| M3 | **Force-guided start chain.** Every start-chain relay is force-guided (Omron G7SA). Each can only pick up while the next one down is released: K_READY checks K_PERMIT, K_PERMIT checks K_RUN_ARM, and K_RUN_ARM checks both request relays and both tool relays. A welded contact then blocks the next start. | Major: welded relays |
| M4 | **Two request relays.** Both follow the Rodent's one run request. K_REQ_A feeds the tool coils. K_REQ_B is in series in both tool outputs, so the Rodent can still stop a tool when one request or tool relay is welded. | Major: welded relays |
| M5 | **Second SETUP channel.** An added ZBE101 contact block on the SETUP/RUN selector sits ahead of K_RUN_ARM. SETUP now blocks every tool through two independent contacts. | Major: welded relays |
| M6 | **Tool outputs and no RS485.** Each tool output is three contacts in series, from three different relays. The VFD takes run only through its FWD terminal and speed only through isolated 0–10 V. With no RS485, no serial command can start the spindle. | Major: Modbus bypass |
| M7 | **Door input to the Rodent.** A dry contact pair opens only when the Rodent requests a tool that is not armed. grblHAL treats that as a safety door: feed hold, spindle off. So when the hardware stops a tool mid-cut, the axes stop too. | Blocker 1 (part): permission input |
| M8 | **Fill check.** K_READY's NC contact is added to the fill-arm pickup. If K_READY welds, FILL will not start in SETUP, which reveals the fault. | Major: welded relays |
| M9 | **Router drain closes.** Latch relay K_DRAINED picks up when the 75 s drain dwell ends. Its NC contact drops the drain request, so the valve closes, and its NO contacts hold router-ready in place of the timer. It holds only while router mode is selected (fed through KM_R) and the pan stays empty (K_EMPTY_B, a second relay on the empty-float line). | Major: router mode leaves the drain open |
| M10 | **Fill watchdog.** On-delay timer T_FILL runs while the fill is commanded; its NC contact is in the K_FILL self-hold. A fill that has not reached the fill-stop float in time stops and needs a new FILL press. Set it to 25 min, then to 1.5 × the timed fill. | Major: no fill time limit |
| M11 | **Float stop.** The torch float switch is wired in series with the three head-presence switches in the U_HEAD loop. A float trip during a cut drops the permission (torch off) and opens the door input (feed hold). During probing the request is low, so nothing holds and the chain re-arms when the float returns. | Major: a float trip triggers nothing |
| M12 | **Spindle reverse.** A force-guided direction relay K_DIR sits at the end of the three-contact run chain. Its NC contact passes the run command to the VFD's FWD terminal and its NO contact to REV, so the VFD never sees both. The Rodent's spindle direction (V-MOS HE1, GPIO2) drives it. It only chooses the direction; the run chain still starts and stops the spindle. | Owner's tool changer (Rev L) |
| M13 | **Tool-changer drive.** The dock's 24 V gearmotor is fed through the E-stop contactors and K_VFD_RUN's NC contact, so it cannot move while the spindle is commanded, stops if the spindle starts, and stops at every E-stop. A run relay and a direction relay drive it, so the two directions can never be driven at once. An end microswitch for each direction stops it at the end of travel, even if a relay welds. | Owner's tool changer (Rev L) |
| M14 | **Dock enable from the Z top switch.** With the Z body raised over the changer, the only crash left is the spindle low over the magazine while the dock moves. The dock feed passes a second, NO, contact of the Z top switch (LS_ZTOP 13-14) ahead of K_DOCK_RUN, so the dock cannot move unless the Z carriage is at its top, whatever the firmware commands and even with K_DOCK_RUN welded. The switch's first contact stays the Rodent's Z limit. | Owner's catch on the Rev L picture (27 Sep): "when it retracts, or it moves forward it will hit the autochanger" |

## How a stop works

The E-stop button has two NC contact blocks, one per safety-relay channel. Pressing it, or losing the safety-circuit fuse, has these effects:

- **The safety relay drops K1 and K2**, removing the Rodent's 48 V, VFD mains and plasma mains. Either contactor alone breaks every path.
- **The permission chains drop:**
  - the tool relays drop;
  - the pump stops.
- **The Z brake loses power and engages**, because its supply runs through the K1 and K2 auxiliary contacts.
- **The Rodent is unpowered**, so it restarts after the stop. grblHAL must be set to require homing after power-up. The Wi-Fi web interface drops and reconnects once the board is back up.

This is a stop category 0: power is removed and the spindle coasts. A single welded contactor still leaves every power path open, and the welded contactor then blocks the reset.

**Resetting.** Release the E-stop, then press and release RESET. The safety relay closes only if both contactors are released, since their mirror contacts sit in the reset circuit. It then refuses to restart after a single-channel opening until both channels have opened.

The reset re-powers the machine but starts nothing:

- The Rodent boots with its run request low.
- Both tools still need a fresh request.
- The Z brake releases 3 s after power returns.

**Choosing the safety relay.** It needs:

- two channels;
- three NO safety contacts;
- a feedback loop for external contactors;
- a *monitored* reset, which acts on the release of the button.

The model shows why the last point matters: with a level-triggered reset, a stuck button restarts the machine as soon as the E-stop is released.

The Pilz PNOZ X2.8P 24VACDC 3n/o 1n/c (777301) has the contacts. Confirm from its manual whether its manual reset is monitored; if it is not, choose a unit that is. Take the terminal numbers and reset wiring from the purchased unit's manual.

Acceptance test: hold RESET and release the E-stop. The contactors must stay open until RESET is released.

**What to check at commissioning:**

- **K1/K2 ratings.** One pole of each contactor, in series, must break the Rodent's DC current (up to 10 A) at 60 V DC. Confirm this from Schneider's DC-1 table. If it fails, use four-pole contactors with two poles each in the 48 V line.
- **Cutter current.** Size K1/K2 to the cutter nameplate current, I1max, at AC-1. The LC1D18 is 32 A.
- **Coil suppressors.** Fit Schneider's suppressor module on each K1/K2 coil, not a plain diode. A plain diode slows the release beyond the dropout times modeled here.
- **Z hold after a restart.** Confirm that the Z motor holds before the brake releases. If grblHAL leaves the drivers off at boot, move the brake release to a Rodent V-MOS output in series with K1/K2.

## How a tool start works now

```text
water ready chain (Rev I) --K_PERMIT NC--> K_READY (holds itself)
HEAD_SAFE --K_READY--> K_RUN_ARM NC --> K_PERMIT (holds itself) --> PERMIT
PERMIT --SETUP/RUN block B (RUN)--> ARM_SRC
ARM_SRC --K_REQ_A NC, K_REQ_B NC, K_VFD_RUN NC, K_TORCH_RUN NC--> K_RUN_ARM (holds itself)
Rodent GPIO25 -> U_RUN PhotoMOS -> K_REQ_A + K_REQ_B coils
ARM_SRC --K_RUN_ARM--> --K_REQ_A--> REQUEST
REQUEST --KM_R--> --K_RDY_R--> K_VFD_RUN      REQUEST --KM_P--> --K_RDY_P--> K_TORCH_RUN
VFD FWD or REV = K_VFD_RUN + K_RUN_ARM + K_REQ_B in series, then K_DIR: NC to FWD, NO to REV (M12)
Cutter START  = K_TORCH_RUN + K_RUN_ARM + K_REQ_B in series
Rodent E1-MAX = K_REQ_A NC  || K_RUN_ARM NO   (open = requested but not armed)
```

Rev I's release-to-rearm rule is unchanged: a held request never re-arms after a stop, a permission loss or a mode change. Only a fresh request does. SETUP is the personnel-safe state, because no single welded or shorted contact can start a tool in SETUP.

In RUN, the Rodent's single output stage remains a single point of failure: the GPIO and the U_RUN PhotoMOS. If it shorts, the tool keeps running after the Rodent drops its request, exactly as if the Rodent commanded it. The E-stop still stops it.

## Router drain, fill watchdog and float stop (M9–M11)

**Router drain (M9).**

- Entering router mode opens the pan drain, as in Rev I. The plasma water runs back to the reservoir through the new drain screen (Rev K).
- Once the pan has been empty for 75 s the drain closes and the router is ready.
- From then on, coolant and chips stay in the pan. Vacuum them out before switching to plasma: that step is on the Rev K pre-plasma checklist.
- If liquid reaches the empty float, router-ready drops and the drain opens again, followed by a new 75 s dwell.
- Leaving router mode clears the latch.
- An E-stop does not clear it, so the router is ready again right after the reset.
- The DRAIN override selector opens the drain while it is on, as before.

```text
KM_R 11-14 -> DR_REQ --K_DRAINED 11-12 (NC)--> D_R2 --> drain valve relay K_DRAIN
T_DRAIN 15-18 --> D_TD --> RR (router ready)      T_DRAIN 15-18 --> D_SET --> K_DRAINED coil
DR_REQ --K_DRAINED 11-14 --K_EMPTY_B 11-14--> K_DRAINED coil   (self-hold: router mode and pan empty)
RE --K_DRAINED 21-24--> RR                                     (router ready without the timer)
```

**Fill watchdog (M10).** T_FILL is a Finder 80.01 on-delay timer, like Rev I's. It is powered with the fill command, and its NC contact is in the K_FILL self-hold. Set it to 25 min at first: the pump's 7 L/min open flow needs about 13–18 min for 80 L. Then time a real fill and set T_FILL to 1.5 times that. A fill stopped by the watchdog needs a new FILL press. Holding FILL keeps the pump running only while it is held.

**Float stop (M11).** Wire the float switch (NC, opens on touch-off) in series with the three head-presence contacts. That loop drives both U_HEAD (the XH:5-6 head-safe input) and U_PROBE (the Rodent probe input).

- **During probing:** the Rodent sees the trip on its probe pin. The request is low, so the door input stays closed. The chain re-arms within about 50 ms of the float returning, well before M3 at pierce height.
- **During a cut:** a trip is a collision. The torch stops and grblHAL holds feed.

**Cutter start at the cutter.** The review found HF-exposed torch-start leads entering the cabinet. The XPLASMA output stays a dry contact chain in the cabinet. At the cutter, it switches the coil of an interposing relay, K_TS, in a small shielded die-cast box bolted to the cutter:

- K_TS's contact closes the cutter's torch trigger: the owner confirmed on 27 September that the CUT-50 starts from its trigger. The trigger leads stay at the cutter.
- The box has its own 24 V supply, fed from the cutter's mains after K1/K2, so K_TS cannot pull in after an E-stop.
- Use a relay with reinforced coil-to-contact isolation and a flyback diode.
- Bond the box to the cutter chassis. Run the cable to the cabinet shielded, through an EMC gland.

## Spindle reverse and the tool-changer drive (M12–M14)

RapidChange unloads a tool by spinning the spindle in reverse at about 1600 rpm and loads it forward at about 1500 rpm. Its grblHAL macros use M4 and M3, so the VFD needs its REV input, and the Rodent needs a spindle direction output.

```text
XVFD:COM --K_REQ_B 13-14--K_RUN_ARM 33-34--K_VFD_RUN 13-14--> K_DIR common
K_DIR 31-32 (NC) --> VFD FWD          K_DIR 13-14 (NO) --> VFD REV
Rodent GPIO2 (V-MOS HE1, spindle direction) --> K_DIR coil      K_DIR 23-24 --> MCP23017 GPA7 (direction status)

K1/K2 aux (Z-brake supply) --F_DOCK 2 A--K_VFD_RUN 41-42 (NC)--LS_ZTOP 13-14 (NO, Z at top)--> DOCK_24V
DOCK_24V --K_DOCK_RUN--> K_DOCK_DIR: NC --LS_OUT (NC)--> motor out (deploy)
                                     NO --LS_IN (NC)---> motor in (park)
MCP23017 GPB0 --ULN2803A--> K_DOCK_RUN coil    GPB1 --ULN2803A--> K_DOCK_DIR coil (on = toward parked)
Dock sensors (M8 PNP) --optocouplers--> MCP23017 GPA4 (deployed), GPA5 (parked)
```

- **K_DIR** is an Omron G7SA-2A2B, force-guided like the start chain. A welded contact cannot close both FWD and REV. A welded K_DIR would run the spindle in reverse on M3, so its spare NO contact reports the direction to the MCP23017. The tool-change macro reads it before each start.
- **K_DOCK_RUN and K_DOCK_DIR** are Finder 40.52 relays. K_DOCK_RUN switches the motor's +24 V (pole 1) and 0 V (pole 2). K_DOCK_DIR's two poles reverse the motor. Change direction only with K_DOCK_RUN off.
- **LS_ZTOP (M14).** The Z top limit switch gets a second, NO, contact (a two-circuit switch, or a second switch beside it) that closes only with the Z carriage at its top. It sits in the dock feed, in the cabinet, and is not a Rodent input. The tool-change macro raises Z fully before it commands the dock; if it does not, the dock simply does not move. Fit it so it closes within the last 2 mm of Z travel, above the point where a 40 mm cutter clears the magazine lid by 15 mm (Rev L: z_lift 227 of 300).
- **End microswitches.** LS_OUT opens when the drive tab reaches the deployed stop, LS_IN at the parked stop. Each has a 1N4007 across it, so the motor can always back away from the end. Set LS_OUT to open about 2 mm after the tab touches the front stop, so the belt-clamp spring is preloaded; the worm then holds it.
- **The dock may move in SETUP** (it has to, for a bed change) and in RUN, but only with the spindle stopped. Keep hands clear: it moves at about 20 mm/s.
- **The macros** must approach the pockets from the rear stop with the head at X975 whenever the dock moves or is out (Rev L README). They read the dock sensors with M66 and drive the dock with M64/M65.

## Wiring by terminal

**[GM1-WIRING-BY-TERMINAL.md](GM1-WIRING-BY-TERMINAL.md)** lists every screw terminal, the numbered wire on it and where that wire's other end lands, device by device: rails, fuses, the safety relay and contactors, every relay and timer, the door switches, the gantry and bed-module cables, the Rodent's connectors, the interface board, the VFD and the cutter box. The [wire list](gm1-wire-list.csv) has the same wires one per row with colour and size. `gm1_wiring.py` generates both from [the simulated netlist](gm1-terminal-netlist.json) and records the netlist's hash in [gm1-wiring.json](gm1-wiring.json); it checks that no terminal carries more than two wires.

What it decides beyond the netlist (wiring decisions, not simulated behaviour):

- **Rails.** The 0 V, C, S, +24 V, BRK and V nets, and the router-ready and fill-coil nets, each get a bridged terminal group (X0V, XC, XS24, X24, XBRK, XV, X_RR, X_FILLCOIL): one wire per side of each position, no daisy chains through relay sockets. Rev I's XW:1-4 and the old stop-loop links XW:21-22 / XH:1-2 are not fitted.
- **Field devices** wire only to their own XW/XH position; the gantry's Z-top second contact and the Z brake land on a small XG strip; the dock's motor, end switches and sensors go through the M12 connector XD (pins 1-2 motor through the end switches, 3-4 sensor supply, 5-6 sensor signals, 7-8 spare).
- **The dock motor** reverses on K_DOCK_DIR's two poles (12 and 24 to M1, 22 and 14 to M2, jumpered on the socket) with K_DOCK_RUN switching +24 V and 0 V; the end switches sit in the motor leads on the module with their diodes. The netlist models the two directions as two loads.
- **The interface board's ULN2803A outputs are low-side:** relay coils take + from XC and their A2 goes to the board's OUT terminal. The V-MOS loads (K_DIR coil, mist valve) sit between the Rodent HE+ and HE- pins, fed from the 48-to-24 V DC-DC after K1 and K2.
- **Two 0 V domains**, never joined: field 0 V (X0V) and the controller side (Rodent GND, the OLED, CN51-53, the board's RUN, I2C, ARC and THC terminals).

The page ends with the BT30 variant's additions (M15, M16), which are wiring instructions only until they are added to `gm1_circuit.py`.

## Rodent wiring

The pin plan and the board facts behind it are in [rodent-io.json](rodent-io.json). The facts come from:

- BTT's Rodent manual (v1.03) and V1.0.2 schematic, from `github.com/bigtreetech/Rodent`;
- grblHAL's `btt_rodent_map.h`.

[gm1_rodent_map.h](gm1_rodent_map.h) is the matching grblHAL board map. It is a draft: not compiled and not flashed. It passes a C-preprocessor pass, which is how it was checked, and with Modbus enabled it stops with an error, as intended. It has not been through the ESP32 toolchain.

The board has six isolated inputs: five endstops plus the probe. The review counted five, because grblHAL's map leaves E1-MAX unused. Its spindle headers are plain 3.3 V GPIOs.

Dropping RS485 frees GPIO14 and GPIO15. That covers the eight real-time inputs GM1 needs. The E-stop needs no input, because it removes the board's power.

| Signal | Rodent connector | GPIO | Wiring |
|---|---|---|---|
| X, Y1, Y2, Z home/limit | X-MAX, Y-MAX, E0-MAX, Z-MAX | 35, 34, 32, 33 | NC switches, signal to GND; SW_VCC jumper on 12 V. The VCC jumper is prohibited above 24 V. |
| Plasma float (probe) | Probe | 36 | Rev I's U_PROBE PhotoMOS switches VProbe (12 V) onto the signal pin. J44 is not fitted. Seated reads HIGH; a trip or open wire reads LOW. Router Z zero stays manual. |
| GM1 door input | E1-MAX | 39 (V1.1), 37 (V1.0) | Dry contacts K_REQ_A NC and K_RUN_ARM NO in parallel. grblHAL safety door. |
| Arc OK | Sp-Direction header | 15 | Dry output of an isolated DC current switch on the work lead, with a 4.7 kΩ pull-up to 3.3 V. Plasma plugin `$367`. |
| THCAD-300 frequency | Sp-Feedback header | 14 | THCAD output through an SN74LVC1G17 on 3.3 V. Use the `/64` or `/128` divider, because the header has 0.1 µF to ground. Read by a new ESP32 capture driver. |
| Run request | Sp-Enable header | 25 | Rev I's run interface: pull-down, buffer and AQY212GS. It drives both request relays. |
| Spindle speed | SP-PWM terminal | 13 | Onboard 0–10 V through an isolated signal conditioner to the VFD. Set `$33 = 5000`. |
| Router mist | V-MOS HE0 | 4 | 24 V solenoid. Feed V-MOS from a DC-DC after K1/K2, never from the field 24 V. |
| Spindle direction | V-MOS HE1 | 2 | K_DIR coil (M12). M4 energizes it: the VFD runs REV. Same V-MOS supply as the mist. |
| Status and tool changer (polled) | OLED header, I2C | 27, 26 | MCP23017 on 5 V. Inputs: K_READY, K_PERMIT, router-ready, plasma-ready, dock deployed, dock parked, RapidChange IR (reserved), K_DIR. Outputs: dock run, dock direction, magazine cover (reserved). |

**Firmware work this needs:**

- Add the plasma plugin to the ESP32 build; it is not there today.
- Write the ESP32 THCAD capture driver. The THCAD code in grblHAL exists only for other chips, marked tentative and unfinished.
- Enable the MCP23017, and expose its pins as aux ports for M62–M66 so the tool-change macros can use them.
- Build with the spindle direction output (GPIO2).
- Set up the RapidChange grblHAL macros: pocket coordinates, and the rear-stop approach from the Rev L README.
- Set the input polarities.

The owner ruled out an external THC box on 25 September, so this firmware route is the plan.

## Parts

All parts are unpriced; the cost register gets them when it is re-baselined to the chosen bed line. The same list, with the parts retired from Rev I, is in [gm1-components.json](gm1-components.json). Terminal marks, coil currents and minimum loads must be checked against each maker's datasheet at purchase.

| Qty | Part | Role | Status |
|---|---|---|---|
| 1 | Pilz PNOZ X2.8P 24VACDC 3n/o 1n/c (777301), or an equivalent with a monitored reset | Safety relay | Candidate; confirm the reset type |
| 2 | Schneider TeSys LC1D18BD, 24 V DC coil | K1, K2 | Candidate; confirm DC rating as above |
| 1 | E-stop pushbutton, Ø40, latching, turn to release, two NC blocks | E-stop | Select; add stations in series per channel |
| 1 | Blue momentary pushbutton, 1 NO | RESET | Select |
| 5 | Omron G7SA-2A2B 24 VDC + P7SA-10F | K_REQ_A, K_REQ_B, K_VFD_RUN, K_TORCH_RUN, K_DIR (M12) | Candidate |
| 2 | Omron G7SA-3A1B 24 VDC + P7SA-10F | K_READY, K_PERMIT | Candidate |
| 1 | Omron G7SA-5A1B 24 VDC + P7SA-14F | K_RUN_ARM | Candidate |
| 2 | Finder 40.52.9.024.5000 + 95.05 | K_RDY_R, K_RDY_P (gold contacts for the low-level status loops) | Candidate |
| 1 | Finder 80.01.0.240.0000, set 3 s | T_BRAKE | As Rev I's timers |
| 2 | Finder 40.52.9.024.0000 + 95.05 | K_DRAINED, K_EMPTY_B (M9) | As Rev I's water relays |
| 1 | Finder 80.01.0.240.0000, set 25 min, then 1.5 × the timed fill | T_FILL (M10) | As Rev I's timers |
| 1 | 24 V DC relay with reinforced coil-contact isolation, socket and flyback diode | K_TS, cutter start at the cutter | To select |
| 1 | Die-cast aluminium box about 120 × 80 × 55, EMC gland, 24 V 10–15 W supply | K_TS box at the cutter | To select |
| 1 | Schneider ZBE101 contact block | Second SETUP/RUN channel | Candidate |
| 1 | NEMA23 stepper with 24 V power-off brake | Z motor | Already required; see the drive-module receiving check |
| 1 | Isolated 0–10 V to 0–10 V signal conditioner | Spindle speed | To select |
| 1 | Isolated DC current switch for the work lead | Arc OK | To select |
| 1 | 48 V to 24 V DC-DC | V-MOS supply (mist) | To select |
| 2 | Finder 40.52.9.024.0000 + 95.05 | K_DOCK_RUN, K_DOCK_DIR (M13) | As Rev I's water relays |
| 1 | 2 A time-delay fuse and holder | F_DOCK (M13) | Select |
| 2 | Roller-lever microswitch, NC, IP67, with a 1N4007 across each | LS_OUT, LS_IN, dock end of travel (M13) | Select to fit the Rev L stop blocks |
| 1 | Z top limit switch with two circuits (or a second switch beside the Z limit), NO contact for the dock feed | LS_ZTOP (M14) | Select with the Z limit switch |
| 1 | Interface board: MCP23017, 2 × SN74LVC1G17, AQY212GS (U_RUN), 3.3 V LDO, ULN2803A, 2 × PC817 (dock sensor inputs), resistors | Rodent side | Schematic level; no PCB yet |

**Retired from Rev I's list:**

- **CNC4PC C41S.** It needs a raw PWM pin, which the Rodent does not have.
- **LTV-817 permission input.** Its job is now the E1-MAX door input.
- **Four Finder 40.52 relays**, which were K_REQUEST, K_RUN_ARM, K_VFD_RUN and K_TORCH_RUN.
- **K_READY's Finder relay.**

The five remaining Finder water relays, the mode relays, the timers, the pump SSRs, the selectors and the head interface are unchanged.

## What the simulation shows

All 1424 checks pass ([gm1-circuit-verification.json](gm1-circuit-verification.json)); 1386 before M14, 1173 before M12–M13. Unless stated otherwise, each ran with every combination of relay pickup (5, 10 and 20 ms) and dropout (5, 20 and 50 ms), in the way Rev I tested its own circuit.

- **Rev I's own behaviors are kept.** These checks were repeated on the new graph:
  - fill arm, self-hold, stops and release-to-rearm;
  - water faults and pump SSR shorts;
  - power loss;
  - a held request at power-up;
  - only the selected tool runs;
  - hardware-chain stops and their recovery;
  - the drain dwell;
  - no backfeed from the drain override.
- **E-stop.** It was tested from four states: router running, plasma running, SETUP and filling. Timings covered three relay and three contactor combinations.
  - It removed the 48 V, VFD mains and plasma mains within 60 ms (worst modeled case).
  - The tool outputs themselves opened within 70 ms.
  - The pump stopped and the Z brake engaged.
  - Releasing the E-stop alone restores nothing.
  - A monitored reset ignores a stuck button, and a single-channel opening locks out the reset until both channels open.
  - A welded contactor leaves every power path open and blocks the reset.
  - The brake releases 3.01 s after power returns.
  - A request held through a stop and reset starts nothing.
- **Mode race.** The review's test, re-run on the new circuit: the mode switch is turned with the start held, with the bed key and water left as they were, or also switched. In the new circuit the other tool fired in 0 of 216 cases. The same test on the Rev I circuit:
  - router → plasma, bed key and water unchanged: 39 of 54, up to 190 ms
  - router → plasma, bed key and water also switched: 0 of 54
  - plasma → router, bed key and water unchanged: 17 of 54, up to 90 ms
  - plasma → router, bed key and water also switched: 0 of 54
- **Welded contacts.** Every NO contact of every start-chain relay, and of the direction relay K_DIR, was welded in turn, 112 cases in all. Each case was run with the relay's other contacts free or stuck, and in both modes.
  - None starts a tool in SETUP.
  - None restarts a tool without a fresh request.
  - In every case the Rodent can still stop the tool by dropping its request.
  - **Welds that block the next start, so the fault shows:** K_PERMIT:13-14, K_PERMIT:23-24, K_PERMIT:33-34, K_REQ_A:13-14, K_REQ_B:13-14, K_REQ_B:23-24, K_RUN_ARM:13-14, K_RUN_ARM:23-24, K_RUN_ARM:33-34, K_RUN_ARM:43-44, K_RUN_ARM:53-54, K_TORCH_RUN:13-14, K_VFD_RUN:13-14.
  - **Welds another channel covers instead:** K_RDY_P:11-14, K_RDY_P:21-24, K_RDY_R:11-14, K_RDY_R:21-24, K_READY:13-14, K_READY:23-24, K_READY:33-34. A welded K_READY is revealed instead by the fill check: FILL will not start. A welded K_DIR (13-14 or 23-24) still lets the chain arm and stop normally; it shows on the direction status input, and with 13-14 welded the spindle runs in reverse.
  - **Mode-relay welds (non-force-guided):** KM_P:11-14, KM_P:21-24, KM_P:31-34, KM_R:11-14, KM_R:21-24, KM_R:31-34. Whether the machine arms again depends on how the relay sticks. In either case, the per-mode ready relay keeps the other tool off.
- **Shorted contacts.** Any single start-chain or K_DIR contact shorted while armed and idle (82 cases) never starts a tool without a request. Any single start-chain, K_DIR or SETUP contact shorted in SETUP, with the Rodent requesting a tool (88 cases), never starts a tool.
- **The review's Rev I weld cases, re-run on the Rev I circuit for comparison:**
  - K_REQUEST:21-24 welded, request dropped: torch still on: **yes**
  - K_RUN_ARM:21-24 welded, door cycled with request held: torch restarts: **yes**
  - KM_R:31-34 welded in plasma mode: spindle starts with the torch: **yes**
  - None of these happens in the new circuit.
- **The known single point:** a shorted run-request output stage keeps the tool running after the Rodent drops its request. The model confirms this. The E-stop stops it, and it cannot run a tool in SETUP.
- **Rodent door input.** It is closed in SETUP and when armed. It opens when the Rodent requests a tool before the machine is ready, or after a permission loss. It closes again once the request drops.
- **Router drain (M9).** Checked in all nine relay-timing combinations:
  - The drain opens on entering router mode.
  - It stays open through the 75 s dwell, then closes with the router ready.
  - Liquid at the empty float reopens it, and a new dwell follows.
  - An E-stop leaves it closed, and the router is ready right after the reset.
  - The DRAIN override selector opens it while it is on.
  - Unlocking the bed drops ready without opening it.
  - Leaving router mode clears the latch. Returning with water in the pan opens the drain again.
  - A welded K_DRAINED contact never lets the spindle run in plasma mode, or the torch start before its water sequence.
  - A stuck latch keeps the drain closed, and the router never becomes ready with water in the pan, so the fault shows.
- **Fill watchdog (M10).** Simulated with the watchdog at 20 s:
  - An unattended fill stops at the watchdog time and stays off.
  - A new FILL press starts a new period.
  - The fill-stop float still ends a normal fill.
  - Holding FILL keeps the pump running past the watchdog; releasing it stops the pump.
  - With the 25 min panel setting, a normal fill is not cut short at 10 min.
- **Float stop (M11).** Checked in all nine timing combinations:
  - A float trip during a cut stops the torch and opens the door input, so grblHAL holds feed.
  - During probing the door input stays closed, and the chain re-arms within 150 ms.
  - The torch then starts on the next request.
- **Spindle reverse (M12).** In all nine timing combinations:
  - M3 closes FWD only; M4 closes REV only, and the direction status input shows it.
  - Dropping the request stops the spindle in either direction.

  Also:
  - FWD and REV were never both closed in 24 combinations of mode, direction, request and a welded K_DIR.
  - Plasma mode never ran the spindle.
  - A reverse request in SETUP runs nothing.
- **Tool-changer drive (M13).** In all nine timing combinations:
  - The dock moves out or in as commanded, and each end switch stops it with the command held.
  - A spindle start stops a moving dock.
  - The dock cannot move while the spindle runs, forward or reverse.

  Also:
  - A welded K_VFD_RUN keeps it from moving.
  - An E-stop stops it.
  - It can move in SETUP for a bed change.
- **Dock enable from the Z top switch (M14).** In all nine timing combinations: with Z below its top the dock does not move in either direction, whatever is commanded; at the top it moves; Z leaving the top stops a moving dock at once. A welded K_DOCK_RUN still cannot move the dock with Z below its top.
  - A welded K_DOCK_RUN still stops at the end switch.
  - Direction changes never drive both directions.

## Limits

- **It is a model, not a measurement.** It checks the connection graph with assumed relay, contactor and safety-relay timings, not measured ones. Record the real times at commissioning.
- **The safety relay is modeled by function only:** two channels, a discrepancy lock, and a reset through the feedback loop. Its terminal numbers, cross-short detection, reset type and response times come from the purchased unit.
- **Mains wiring is specified here but not simulated.** The same goes for:
  - contactor and brake sizing;
  - the VFD and cutter interfaces;
  - the interface board layout;
  - EMC.
- **Water-contact glitches** shorter than a relay's dropout can still resume a held fill, as in Rev I.
- **The float stop (M11)** is simulated as the existing head-loop input. The float switch, its cam and the probe optocoupler are not simulated.
- **Spindle reverse and the dock (M12–M13).** The VFD's behavior with FWD and REV and its direction-change ramp are not simulated. The dock motor is modeled as one load per direction; its current, the second relay poles, the back-off diodes and the sensors are wiring details, not simulated.
- **The plasma reach and the cabinet findings** are mechanical. They are dealt with in [Rev K](../release-review/RevK-CAD/README.md):
  - the drop bracket and torch;
  - the drip lip, glands, fan and VFD placement.

## Buying notes (nothing is waiting on the owner)

The Rodent and the VFD are not ordered yet (owner, 27 Sep). These are the choices the design assumes.

1. **Rodent: buy the V1.1**, the current version.
   - The board map already uses its GPIO39 for the door input.
   - If a V1.0 arrives instead, change that one line to GPIO37.
2. **VFD: use the one in the spindle kit.** These kits have run terminals (FWD and REV to COM or DCM) and a 0–10 V speed input, and that is all this design uses. The tool changer needs the REV terminal (M12); check the delivered unit has one. The cabinet's VFD mount allows up to 180 × 160 × 250 mm.
3. **CUT-50:**
   - **It starts in mid-air** (owner, 27 Sep). That is a high-frequency (HF), non-contact start.
   - **Start circuit:** it starts from the torch trigger. K_TS's NO contact goes across the trigger terminals, in its shielded box at the cutter. Choose K_TS with reinforced coil-to-contact isolation.
   - **Routing:** run the torch lead and work lead away from the motor, limit and probe cables.
   - **At commissioning:**
     - note the work-lead size, which sizes the arc-OK current sensor;
     - check that the trigger circuit's voltage and current suit K_TS's contact.

## Reproduce

```text
python output/controls-2026-09-27/verify_gm1_circuit.py   # about 15 minutes; writes gm1-circuit-verification.json
python output/controls-2026-09-27/verify_rodent_io.py     # writes rodent-io.json
```

`verify_gm1_circuit.py` also regenerates [gm1-terminal-netlist.json](gm1-terminal-netlist.json) and [GM1-TERMINALS.md](GM1-TERMINALS.md), the terminal-by-terminal connection list.
