# Retractable ATC controls — executable engineering candidate

This directory defines the large-machine automatic **200 mm dock slide, two spring-engaged end locks, and 164 mm outer shutter with a separate retaining catch**. The executable profile is explicitly `large`; it remains unqualified and cannot enable by default. The small machine has no selected independent outer shutter or integrated magazine closure solution. Its control profile is unavailable: `Config(machine_variant="small")` raises an error. Do not emulate shutter feedback, bypass the catch, or reuse the large profile on the small mechanism. The reusable sequence is a prototype for a future separately integrated small profile. Actual sensor mounting and load capacity still require physical qualification. This is a router ATC candidate: the added common run gate also requires ROUTER mode even while parked. Plasma operation stays inhibited until a separate magazine removal/protection workflow is qualified; the shutter is not plasma protection.

The delivered [state machine](interlock.py), [input decoder](input_adapter.py), [pin/component plan](io_plan.json), [wiring](WIRING.md) and [offline verification](verification.json) are concrete design artifacts. They do not operate hardware. The existing Kraken firmware still disables S5/S6; no modified binary, M6 macro, automatic spindle reversal or live tool change is delivered here. The default model refuses permission until its explicitly simulated qualification condition is supplied. Changing that condition is not commissioning.

## Allocation and mechanism

| Function | Connection | Definition |
|---|---|---|
| X, Y1, Y2, Z | Existing Kraken S1–S4 | Preserve current port and 50 mΩ V1.1 sense values |
| 200 mm dock slide | Onboard S5 | PG9 STEP, PG10 DIR, PG13 active-low EN, PD2 CS; 75 mΩ |
| 164 mm outer shutter (large only) | Onboard S6 | PG11 STEP, PD7 DIR, PG12 active-low EN, PA15 CS; 75 mΩ |
| Both dock lock-release coils | PE13 / EXP2 pin 1 | Isolated command to K_RACK_RELEASE; two separately fused loads |
| Shutter catch-release coil | PE14 / EXP2 pin 6 | Isolated command to K_SHUTTER_RELEASE |
| Additional run permission | PD10 / J14 pin 2, PS_ON | Isolated K_ATC_GATE; normally open contact inserted in the existing hardware permission path |
| 14 dock feedback inputs | MCP23017 at 0x20, I2C2 PB10/PB11 | Isolated field loops; polled, no new EXTI assignments |
| Actual magazine internal cover | Existing PE12 reservation | Kept separate from S6 outer shutter; protocol remains unidentified |

Six independent PM-U25-P optical sensors confirm rack/catch pin endpoints; four separate mechanical switches confirm slide/shutter endpoints. Their field circuits and quiescent load are included in [WIRING.md](WIRING.md). Optical fouling can mimic an endpoint; these ordinary controls do not establish a safety rating.

PD15 direction, PG8 toolsetter, PG7 IR, PF10 dock presence and PE11 plasma float remain reserved as before. EXP2 cannot simultaneously serve an LCD/SD accessory. The onboard TF interface is separate but its grblHAL support is still not integrated. Sources: [BTT board documentation](https://global.bttwiki.com/Kraken.html), [official configuration](https://github.com/bigtreetech/BIGTREETECH-Kraken).

The selected 8 mm/revolution actuator gives **400 pulses/mm at 16 microsteps**, hence 80,000 pulses for slide travel and 65,600 for shutter travel. Ten mm/s is a 4 kHz pulse stream before acceleration. The candidate current ceiling is 1.18 A RMS, keeping sinusoidal peak below the motor's 1.68 A phase rating; start unloaded at 0.5 A RMS and qualify torque/temperature. These are design choices, not a proven thrust rating. Each S5/S6 driver must use **75 mΩ individually**; the existing global 50 mΩ constant cannot be reused. [Actuator data](https://www.omc-stepperonline.com/download/17E19S1684MB-300RS.pdf).

The control model measures logical travel **0 = park, 200 = deployed**. The large mechanism builder uses the opposite geometric parameter, **CAD slide = 0 at change and 200 at park**, so its adapter must use `CAD_slide=200-control_slide`. Physical DIR and switch polarity must be commissioned; a sign inferred from CAD is not a wiring test. Shutter logical travel is 0 = closed, 164 = open.

Each motion output includes an absolute pulse-position target as well as velocity. The future pulse scheduler must clamp the pulse budget to that target independently of the polling loop: **80,000 slide pulses and 65,600 shutter pulses** between endpoints, never “keep running until timeout.” The model faults at a counted endpoint without its confirmation and rejects nonfinite/out-of-range counters. This prevents intentional overrun after a missing limit but does not make pulse counts into physical-position feedback or prevent lost steps.

## Automatic sequence

1. Power-up enters **BOOT_UNKNOWN**, outputs inhibited. Inspect the machine and establish actual parked position, parked pin engagement, closed outer shutter, engaged closed shutter catch and closed kit cover. Require fresh stopped-spindle feedback and a fresh homed/idle/axis-clear lease. A released request and a deliberate acknowledgement can then establish PARKED_LOCKED. No automatic homing with an unknown attached tool is performed.
2. A new tool-change request removes run permission. Require a fresh 300 ms stopped-spindle interval after this removal. Release the shutter catch, raise S6 to the open switch and expected pulse count, then de-energize the catch release and prove the catch extended at the upper position. The kit cover must separately report open.
3. Release **both** rack pins. Each must report retracted and not extended. Deploy S5, requiring 200 mm counted travel and deployed endpoint feedback. Remove release power and prove the deployed pin extended at that position. A parked pin extending into free air is not evidence of deployed engagement.
4. A fresh M6 toolpath session may now enter TOOL_CYCLE. Run permission requires deployed position, engaged deployed lock, captured open shutter, open kit cover, valid IR, fresh feedback and that exact session. Axes move only under the still-unimplemented, validated M6 trajectory adapter. The model requires observed running feedback after a spindle request, then fresh standstill after completion; a permanently high stopped signal cannot finish the cycle.
5. After completion, require a **new axis-clear lease for the current pose epoch**, release both rack pins, retract 200 mm, prove parked endpoint and parked pin engagement, release the shutter catch, lower S6, prove closed covers, stop S6, and enter CAPTURE_SHUTTER_CLOSED. De-energize catch release and require stable extended/not-retracted feedback at the closed detent before restoring PARKED_LOCKED permission; a missing capture faults after the pin timeout. A coordinate reset, re-home, new motion or stale lease invalidates the clearance handoff.

**Required relay re-arm handoff:** dropping K_ATC_GATE during each conversion also drops K_RUN_ARM. When TOOL restores the gate, the future M6 adapter must hold the physical PG2 spindle request LOW long enough for K_ATC_GATE to close and K_RUN_ARM to pick up before issuing any spindle request or acting on toolpath permission. Qualify this release-to-rearm interval on the actual relays, supply and wiring; the offline TOOL state exposes permission immediately and does not model that relay dwell. PG6 is upstream readiness, not confirmation of either new gate contact or run-arm pickup. A held-high request must not be used to force re-arming.

The [normal trace](normal-sequence.json) records this sequence through the idealized test plant. Its timing is not a measured cycle time. Initial diagnostic deadlines are 30 s slide, 25 s shutter, 3 s pin operation, 15 s stop and 120 s tool sequence; they must be set from bench measurements and permitted stop behavior.

## Failure and recovery

Permission loss, power loss, stale/replayed input, I2C/register faults, contradictory switches, missing lock/cover/IR feedback and invalid handoffs latch a fault. The model immediately removes pulse requests, unlock power, toolpath permission and run permission. It commands **HOLD**, not automatic closure, to an unidentified kit cover. The actual kit must support a tested equivalent before its adapter can be enabled.

No automatic retract or retry is permitted with a tool partly threaded into a pocket. Isolate tool power, support the tool, inspect its attachment and recover under a separately validated service procedure. Re-home/verify coordinates after possible lost steps; manually establish the inspected parked/locked/closed state. Then release all requests and provide a new acknowledgement. Holding RESET or a spindle request high cannot restart the operation.

The shutter catch must be verified at the stopped **open and closed detents**. Its ladder does not establish a guaranteed power-loss arrest distance or dynamically qualified upward ratcheting. This design makes no self-locking claim for TR8×8 screws. Mid-travel power-loss behavior still requires the mechanical capture/counterbalance design and physical tests. A pulse count is not an encoder; coherent false sensor indications, misadjusted cams, a missing receiver or a welded permission contact can defeat ordinary control diagnostics. These are not rated safety functions.

## Verification and firmware boundary

Run `python variants/retractable-atc/controls/verify_controls.py` from the repository root. The source-bound report includes behavioral checks, all 1,024 combinations of ten critical tool-cycle confirmations, independent idealized mechanism guards, fault injection at each normal state, wrong-end pin rejection, restart behavior, GPIO conflicts, MCP decoding and electrical arithmetic. It reports `firmware_compiled=false`, `hardware_tested=false`, `machine_release=false` explicitly.

A future firmware adapter must implement the two auxiliary pulse schedulers, SPI arbitration and per-driver current sense, controller watchdog, input polling/readback, spindle feedback timestamps, axis-clear/session leases, release-to-rearm handoff, and exact kit M6 commands. It must first remove only S5/S6 from the old unused-driver initialization while retaining S7/S8 disabled. The existing four-motor map/axis-count guard and global driver current code need actual integration; copying these pin values into a configuration is insufficient. Baseline source remains untouched.

Remaining release gates are specific: exact RapidChange kit/cover/IR and VFD run/stop/reversal interfaces; physical shutter/rack captures and sensor mounts; measured solenoid pull/release times; supply/fuse/wire verification; a fabricated isolated board and harness; commissioned auxiliary firmware; and observed tool retention/runout and repeated tool-change tests. The independent hardware E-stop and original run-arm chain remain required; this Python model is not a safety PLC.
