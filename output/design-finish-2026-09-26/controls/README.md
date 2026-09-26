# Rev I controls - one baseline and an actual water wiring model

**Current controller: BIGTREETECH Kraken V1.1, existing grblHAL X/Y1/Y2/Z port, onboard drivers.** The Rodent/THCAD selection appended to an older plasma document is not the current design. No replacement motion controller, outside motor drivers, firmware flash or untested THCAD decoder is introduced here. The upstream source and compiled prototype remain in `RevE-ENGINEERING/controls`.

This revision supplies [a normally-off isolated run schematic and restart prevention](RUN-INTERFACE.md), [terminal-by-terminal connections](TERMINALS.md), a [machine-readable netlist](terminal-netlist.json), and a [finite-delay circuit test](verification.json). The simulator traces voltage through real named contacts and diode directions; it is not the earlier Boolean truth table. It covers the water controls, mode-relay allocation and tool-request gating. Mains power, the certified stop subsystem and the unidentified cutter interface are separate boundaries, not silently simulated successes.

## Changes to the circuit

1. Replace both AH3-3 timers with **Finder 80.01.0.240.0000**, function **AI**. A1 is positive and A2 is 0 V; 15 is common, 18 delayed NO, 16 delayed NC. B1 and 16 are unused. T_CLOSE is nominally 12 seconds on the 20-second range, verified at least 10 seconds. T_DRAIN is nominally 75 seconds on the 2-minute range, verified at least 60 seconds. This resolves the missing documented DC contact rating and avoids using an instantaneous pole as a timed pole. Retain a full timer-power interruption of at least 100 ms when a reset is required. [Finder primary data, printed page 3](https://cdn.findernet.com/app/uploads/S80EN.pdf).
2. Add **680 ohm, 3 W, 5%** flameproof resistors from each timed output to control 0 V, before the ready-OR diode or downstream switches. These establish a minimum resistive contact load even when downstream contacts open. At 21.6-26.4 V and resistor tolerance, each dissipates 0.653-1.079 W. Mount above the backplate on covered, heat-resistant supports, away from wiring and plastic. Common float-chain current remains below the 200 mA design ceiling under the stated conservative coil/input allocation.
3. Use the normal **Schneider XB5AD33** three-position/two-NO selector to operate two **Finder 55.34.9.024.0000** four-pole relays with **94.04** sockets. The extra contacts come from actual relays, not fictional extra selector poles. KM_R and KM_P use poles 1/2 for water functions, pole 3 for tool selection, and opposite pole 4 NC for coil interlocking. OFF opens both selector contacts. Normal mutually exclusive selector operation is required; this ordinary interlock is not a safety-rated fault discriminator. [Selector](https://www.se.com/uk/en/product/XB5AD33/selector-switch-plastic-black-%C3%B822-3-positions-stay-put-2-no/), [relay/socket primary data](https://cdn.findernet.com/app/uploads/S55EN.pdf).
4. Retain the six existing **40.52.9.024.0000 / 95.05** water relays. K_READY's status pole now drives the defined 24 V input load below, rather than an unknown MCU pull-up. The two added tool-command relays are **40.52.9.024.5000** gold-contact candidates for low-level dry interfaces, in 95.05 sockets; their suitability still depends on the actual VFD and plasma-interface contact requirements. No dummy load is added to an unknown cutter trigger. [Finder contact material and socket data](https://cdn.findernet.com/app/uploads/S40EN.pdf).

Pump SSRs, branch fuses, wire sizing and flyback protection retain the selected Rev H definitions. The new wiring uses ten 40.52 relays in total (six water, two tool, one request, one run-arm), two 55.34 mode relays, two 80.01 timers and two existing RM1D060D20 pump SSRs. Account for all of them in the panel and eventual price total. There is no new delivered-price claim.

## Exact controller boundary

| Function | Kraken physical connection | Current electrical definition |
|---|---|---|
| Combined machine permission | EXP2 pin 7 / PG6 | Optically isolated active-low status; configure and verify input polarity on the board |
| Hardware stop status | EXP1 pin 2 / PG4 | Separate isolated status; does not replace the hardware stop circuit |
| Float probe | EXP2 pin 4 / PE11 | [Defined isolated NC float](HEAD-INTERFACE.md): healthy LOW / open HIGH; parked float is not a router touchplate |
| Arc OK / DOWN / UP | EXP1 pins 8 / 7 / 6, PD12 / PD13 / PD14 | Outputs of a compatible isolated external THC; no raw arc voltage or THCAD frequency |
| Run request | EXP1 pin 4 / PG2 | AQY212GS normally-off isolated request, release-to-rearm relays, then hardware permission and selected tool relay |
| Speed request | BLTouch SERVO / PE9 | [C41S isolated speed conversion](SPEED-INTERFACE.md), buffered input, commissioning setting $33=200 Hz |

The [official Kraken documentation](https://global.bttwiki.com/Kraken.html) specifies 3.3 V logic and a 200 x 113 mm board. The current firmware covers V1.1 S1-S4 with 50 milliohm sense resistors; V1.0 is a different current-sense configuration. Existing 500 mA RMS settings are unloaded commissioning defaults. The new water netlist does not change motor settings.

**IF_READY input detail:** HEAD_SAFE -> K_READY:11/14 through XW:31/32 -> 1 kohm, 2 W, 5% resistor -> LTV-817 pin 1. Pin 2 goes to field 0 V. Place a 1N4148 anti-parallel across the LED (anode pin 2, cathode pin 1). On the controller side, pin 3 goes to controller ground; pin 4 goes to PG6 and a 4.7 kohm pull-up to controller 3.3 V. Keep the two ground domains separate. Nominal healthy contact closure pulls PG6 low. The field LED current screen is 19.24-26.74 mA over the specified supply/resistor/Vf limits, and the resistor stays below 0.68 W. That field load exceeds the ordinary relay's 300 mW minimum; it does not expose PG6 to 24 V. CTR, saturation, input thresholds, power sequencing and wiring polarity must be checked on the actual interface. [LITEON primary photocoupler data](https://optoelectronics.liteon.com/upload/download/DS-70-96-0016/LTV-8X7%20series%20%20Rev.S.PDF).

This describes a low-voltage status interface, not a plasma arc-voltage isolator, a finished PCB or HF immunity certification. Do not use it for PWM speed conversion. The [run-interface schematic and limits](RUN-INTERFACE.md) now define the output stage and restart-prevention relays. The [head-interface schematic](HEAD-INTERFACE.md) now defines the isolated PE11 float input and three series NO seated-head contacts driving XH:5/6. It includes actual component/terminal selections, load bounds and delay tests against this circuit. The run and head PCB/layout and physical behavior remain unreleased until verified. An optocoupler's component test voltage does not certify an assembled panel.

## Operator controls and bed confirmation

Use the following complete Schneider controls; these quantities are separate physical devices:

| Function | Part and quantity | Actual block terminals | Required closure |
|---|---|---|---|
| MODE | 1 x XB5AD33 | Two NO blocks, each marked 13/14; tagged MODE_R and MODE_P | Router closes only MODE_R; center OFF opens both; plasma closes only MODE_P |
| SETUP/RUN | 1 x XB5AD25 | 21/22 NC and 13/14 NO | NC closes in SETUP; NO closes in RUN |
| AUTO/DRAIN | 1 x XB5AD25 | 21/22 NC and 13/14 NO | NC closes in AUTO; NO closes in DRAIN |
| FILL | 1 x XB5AA35, green flush momentary | 13/14 NO and 21/22 NC | Press closes NO and opens NC; release reverses both |
| BED CONFIRM | 1 x XB5AG03, key 455 | Two NO blocks, each marked 13/14; tagged BED_R and BED_P | Router checked closes BED_R; center UNCONFIRMED opens both; plasma checked closes BED_P |

Schneider's [complete-device catalog](https://productinfo.se.com/nadigest/5c51d645347bdf0001f1f280/Master/17719_MAIN%20%28bookmap%29_0000052086.xml/%24/_17719042_51082) identifies the maintained positions and contact-body assemblies. The [FILL datasheet](https://iportal.se.com/Contents/docs/SQD-XB5AA35_DATASHEET.PDF) supplies 13/14 NO and 21/22 NC; FILL and XB5AD25 use the same ZB5AZ105 contact body. The [MODE datasheet](https://iportal.se.com/Contents/docs/SQD-XB5AD33.PDF) lists 13/14 NO for its two separate blocks. Block identity distinguishes the pair; the drawing does not invent a second block stamped 23/24. Fit position labels only after the complete assembled switch passes the continuity table above.

The terminal renderer now states **physical contact form** separately from **logical closed condition**. In particular, `setup=true` closes the factory NC contact at SETUP_RUN:21/22; `setup=false` closes its factory NO contact at 13/14. A Boolean inversion in the simulator is not a purchased NC contact. The selected XB5AA35 is a flush button, not a guarded assembly; any added guard still needs a compatible part and mounting detail.

B_CLEAR and B_LOCK are **operator-confirmed configuration contacts**, not automatic bed sensors or torque measurement. The selected [XB5AG03 primary datasheet](https://iportal.se.com/Contents/docs/SQD-XB5AG03.PDF) specifies three maintained positions, two NO blocks and key withdrawal in any position. Its labels are ROUTER CHECKED / UNCONFIRMED / PLASMA CHECKED and must list the six panels, four beams, separate spoilboards, locks and tool exchange inspection. Keep it UNCONFIRMED during conversion. BED_P:13/14 connects through XW:23/24; BED_R:13/14 connects through XW:25/26. These XW numbers are panel field terminals, not contact-block stamping. Key removal does not force UNCONFIRMED. Physical control-station mounting remains to be detailed.

## What the circuit test establishes

The test uses nine pickup/dropout combinations, real latch contacts, timers, diode directions and open field contacts. It checks deliberate start, fill self-hold, normal stop, power return with FILL held, bed/level/stop faults, both single SSR-short cases, mode tool selection and hardware permission loss. The resistor and common float-current calculations include tolerances. Tests are generated from the actual connection graph, with an independent expectation for each sequence.

The short-interruption counterexample is deliberate: a 5 ms loss followed by recovery can resume pumping if a relay takes 50 ms to release and FILL remains held. Ordinary suppressed relays cannot guarantee a latched response to arbitrarily short pulses. The passing fill interruption cases use 150 ms and tool permission interruptions use 300 ms; this is a tested model assumption, not a measured relay limit. Mechanically latched stop/mode controls must not be replaced by brief software pulses. Any requirement to latch shorter transients needs a separately validated fault latch, followed by hardware tests. The test reports this limit rather than hiding it under PASS.

No PL/category claim, stop-distance claim, dual-fault tolerance, automatic standstill proof or verified brake timing follows from this model. Whole-machine release still needs the actual control panel, stop/power circuit, Z restraint behavior, physical run/PWM interfaces, firmware commissioning and identified VIV ARC CUT-50 connection. Those are distinct engineering tasks, not completed by the water simulation.

The [selected speed-converter interface](SPEED-INTERFACE.md) replaces the previously unspecified converter and 5 kHz assumption with C41S Rev1.1 and a 200 Hz commissioning setting. It requires a separate buffered input; the slow PhotoMOS run channel cannot carry this PWM.
