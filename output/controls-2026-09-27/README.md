# GM1 controls: the stop, the start chain and the Rodent wiring (27 September 2026)

The [26 September review](../review-2026-09-26/README.md) found three problems in the controls that block building GM1 on either bed line:

- There is no E-stop or power-removal circuit.
- Turning the mode switch with the start signal held can fire the wrong tool.
- The design is built on the Kraken, which the owner rejected, and the Rodent is short of inputs.

It also found two major problems: a single welded relay contact can start a tool, and a Modbus command can bypass the hardware run permission.

This package fixes all five. It applies to both bed lines: Rev J (one-piece hoisted bed) and Rev I (six panels in the footprint).

**What it builds on.** It starts from the other session's Rev I relay circuit (`output/design-finish-2026-09-26/controls/circuit.py`). That file is imported read-only and left unchanged, and its hash is recorded.

**What is kept.** Rev I's water logic is kept as is:

- fill, drain and timers;
- bed confirmation;
- mode relays;
- head interface.

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
VFD FWD/COM   = K_VFD_RUN   + K_RUN_ARM + K_REQ_B in series
Cutter START  = K_TORCH_RUN + K_RUN_ARM + K_REQ_B in series
Rodent E1-MAX = K_REQ_A NC  || K_RUN_ARM NO   (open = requested but not armed)
```

Rev I's release-to-rearm rule is unchanged: a held request never re-arms after a stop, a permission loss or a mode change. Only a fresh request does. SETUP is the personnel-safe state, because no single welded or shorted contact can start a tool in SETUP.

In RUN, the Rodent's single output stage remains a single point of failure: the GPIO and the U_RUN PhotoMOS. If it shorts, the tool keeps running after the Rodent drops its request, exactly as if the Rodent commanded it. The E-stop still stops it.

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
| Status (polled) | OLED header, I2C | 27, 26 | MCP23017 on 5 V reads K_READY, K_PERMIT, router-ready and plasma-ready. Display only. |

**Firmware work this needs:**

- Add the plasma plugin to the ESP32 build; it is not there today.
- Write the ESP32 THCAD capture driver. The THCAD code in grblHAL exists only for other chips, marked tentative and unfinished.
- Enable the MCP23017.
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
| 4 | Omron G7SA-2A2B 24 VDC + P7SA-10F | K_REQ_A, K_REQ_B, K_VFD_RUN, K_TORCH_RUN | Candidate |
| 2 | Omron G7SA-3A1B 24 VDC + P7SA-10F | K_READY, K_PERMIT | Candidate |
| 1 | Omron G7SA-5A1B 24 VDC + P7SA-14F | K_RUN_ARM | Candidate |
| 2 | Finder 40.52.9.024.5000 + 95.05 | K_RDY_R, K_RDY_P (gold contacts for the low-level status loops) | Candidate |
| 1 | Finder 80.01.0.240.0000, set 3 s | T_BRAKE | As Rev I's timers |
| 1 | Schneider ZBE101 contact block | Second SETUP/RUN channel | Candidate |
| 1 | NEMA23 stepper with 24 V power-off brake | Z motor | Already required; see the drive-module receiving check |
| 1 | Isolated 0–10 V to 0–10 V signal conditioner | Spindle speed | To select |
| 1 | Isolated DC current switch for the work lead | Arc OK | To select |
| 1 | 48 V to 24 V DC-DC | V-MOS supply (mist) | To select |
| 1 | Interface board: MCP23017, 2 × SN74LVC1G17, AQY212GS (U_RUN), 3.3 V LDO, resistors | Rodent side | Schematic level; no PCB yet |

**Retired from Rev I's list:**

- **CNC4PC C41S.** It needs a raw PWM pin, which the Rodent does not have.
- **LTV-817 permission input.** Its job is now the E1-MAX door input.
- **Four Finder 40.52 relays**, which were K_REQUEST, K_RUN_ARM, K_VFD_RUN and K_TORCH_RUN.
- **K_READY's Finder relay.**

The five remaining Finder water relays, the mode relays, the timers, the pump SSRs, the selectors and the head interface are unchanged.

## What the simulation shows

All 984 checks pass ([gm1-circuit-verification.json](gm1-circuit-verification.json)). Unless stated otherwise, each ran with every combination of relay pickup (5, 10 and 20 ms) and dropout (5, 20 and 50 ms), in the way Rev I tested its own circuit.

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
- **Welded contacts.** Every NO contact of every start-chain relay was welded in turn, 104 cases in all. Each case was run with the relay's other contacts free or stuck, and in both modes.
  - None starts a tool in SETUP.
  - None restarts a tool without a fresh request.
  - In every case the Rodent can still stop the tool by dropping its request.
  - **Welds that block the next start, so the fault shows:** K_PERMIT:13-14, K_PERMIT:23-24, K_PERMIT:33-34, K_REQ_A:13-14, K_REQ_B:13-14, K_REQ_B:23-24, K_RUN_ARM:13-14, K_RUN_ARM:23-24, K_RUN_ARM:33-34, K_RUN_ARM:43-44, K_RUN_ARM:53-54, K_TORCH_RUN:13-14, K_VFD_RUN:13-14.
  - **Welds another channel covers instead:** K_RDY_P:11-14, K_RDY_P:21-24, K_RDY_R:11-14, K_RDY_R:21-24, K_READY:13-14, K_READY:23-24, K_READY:33-34. A welded K_READY is revealed instead by the fill check: FILL will not start.
  - **Mode-relay welds (non-force-guided):** KM_P:11-14, KM_P:21-24, KM_P:31-34, KM_R:11-14, KM_R:21-24, KM_R:31-34. Whether the machine arms again depends on how the relay sticks. In either case, the per-mode ready relay keeps the other tool off.
- **Shorted contacts.** Any single start-chain contact shorted while armed and idle (74 cases) never starts a tool without a request. Any single start-chain or SETUP contact shorted in SETUP, with the Rodent requesting a tool (80 cases), never starts a tool.
- **The review's Rev I weld cases, re-run on the Rev I circuit for comparison:**
  - K_REQUEST:21-24 welded, request dropped: torch still on: **yes**
  - K_RUN_ARM:21-24 welded, door cycled with request held: torch restarts: **yes**
  - KM_R:31-34 welded in plasma mode: spindle starts with the torch: **yes**
  - None of these happens in the new circuit.
- **The known single point:** a shorted run-request output stage keeps the tool running after the Rodent drops its request. The model confirms this. The E-stop stops it, and it cannot run a tool in SETUP.
- **Rodent door input.** It is closed in SETUP and when armed. It opens when the Rodent requests a tool before the machine is ready, or after a permission loss. It closes again once the request drops.

## Limits

- **It is a model, not a measurement.** It checks the connection graph with assumed relay, contactor and safety-relay timings, not measured ones. Record the real times at commissioning.
- **The safety relay is modeled by function only:** two channels, a discrepancy lock, and a reset through the feedback loop. Its terminal numbers, cross-short detection, reset type and response times come from the purchased unit.
- **Mains wiring is specified here but not simulated.** The same goes for:
  - contactor and brake sizing;
  - the VFD and cutter interfaces;
  - the interface board layout;
  - EMC.
- **Water-contact glitches** shorter than a relay's dropout can still resume a held fill, as in Rev I.
- **Two findings are not dealt with here:**
  - the plasma torch cannot reach the work (blocker 4);
  - the cabinet findings: heat, drip lip, gland count and EMC.

## Needed from the owner

1. **Rodent version.** V1.1 puts E1-MAX on GPIO39; V1.0 uses GPIO37.
2. **VFD model.** Needed: its FWD/COM input type, its analog input range and impedance, and whether it has STO (safe torque off).
3. **CUT-50 details.** The start circuit and the work-lead size, to choose the arc-OK current switch.

## Reproduce

```text
python output/controls-2026-09-27/verify_gm1_circuit.py   # about 15 minutes; writes gm1-circuit-verification.json
python output/controls-2026-09-27/verify_rodent_io.py     # writes rodent-io.json
```

`verify_gm1_circuit.py` also regenerates [gm1-terminal-netlist.json](gm1-terminal-netlist.json) and [GM1-TERMINALS.md](GM1-TERMINALS.md), the terminal-by-terminal connection list.
