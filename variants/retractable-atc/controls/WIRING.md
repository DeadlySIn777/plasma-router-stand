# Retractable dock terminal and circuit definition

This candidate circuit is allocated to the large-machine 164 mm shutter profile. The small-machine automatic profile is unavailable until its actual cover/closure mechanism and feedback are integrated; unused signals must never be simulated to satisfy this circuit.
This is a low-voltage schematic candidate, not a finished PCB or installation release. All numbers prefixed **XA** are new panel terminals. Manufacturer contact and IC pin numbers are identified separately. [io_plan.json](io_plan.json) is the machine-readable allocation. The existing [run circuit](../../../output/design-finish-2026-09-26/controls/RUN-INTERFACE.md) stays independent; no sensor or software output bridges its stop contacts.

## Supply domains and connector pinning

**LOGIC3V3/LOGIC0** come from the Kraken logic supply; J22 SWD pin 1 is 3.3 V and pin 3 is ground in the referenced board schematic. Verify actual V1.1 labels before connection. **C24V/FIELD0** are the existing isolated 24 V control supply, screened here over 21.6–26.4 V. **AUX24_SAFE** is a separately fused actuator feed removed by the hardware auxiliary stop/power system. Its contactor design is not invented here. Never power added coils from HEAD_SAFE or the PhotoMOS head loop.

P10 I2C: **1 = 5 V (leave disconnected), 2 = LOGIC0, 3 = PB10 SCL, 4 = PB11 SDA**. BTT shows 4.7 kΩ pull-ups from SCL/SDA to 3.3 V. Keep the expander in the control cabinet, short wiring, 100 kHz; no moving I2C cable. Verify rise time on the actual bus. The schematic supplied locally is V1.0; the official common V1.0/V1.1 mapping supports these signals but actual V1.1 header orientation still needs continuity checks. [BTT primary files](https://github.com/bigtreetech/BIGTREETECH-Kraken).

U_IO is **MCP23017-E/SP, 28-pin SPDIP**: pin 9 = LOGIC3V3, pin 10 = LOGIC0, pin 12 = SCL, pin 13 = SDA. Pins 15/16/17 to LOGIC0 give address 0x20. Pin 18 RESET gets 10 kΩ to 3V3 and a controller-reset connection only after electrical validation; initial design permits a manual reset switch to LOGIC0 with required≥1 µs low. Add 100 nF X7R directly 9–10 and 1 µF nearby. Pins 11/14 are NC; 19/20 interrupt outputs unconnected. Pins 8/28 (GPB7/GPA7) are explicitly unused output-low. **They must not be sensor inputs**: [Microchip RevD](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf) corrects the older RevC limitation. All fourteen remaining pins are inputs; no interrupt lines are added.

## Fourteen isolated inputs: eight dry-contact channels and six PNP channels

The four slide/shutter endpoint channels and four unselected VFD/kit channels use two-wire **dry contact** loops. Pin sensors use the separate PNP circuit below. For a dry-contact channel:

`C24V -> F_INPUT(0.25A) -> 3.32kΩ 1% 0.6W -> XA:odd -> NO confirmation contact -> XA:even -> AQY212GS LED pin1; LED pin2 -> FIELD0.`

Across LED1–2 fit 22 kΩ, 1% and a 1N4148 with cathode at LED1. The current-limiting resistor is before the outgoing field conductor. On the isolated logic side: `LOGIC3V3 ->4.7kΩ1% -> GPIO node ->330Ω1% -> AQY pin4; AQY pin3 ->LOGIC0`. Add 4.7 nF C0G from GPIO node to LOGIC0. The output is a floating NO PhotoMOS contact; neither field return nor cable shield connects to LOGIC0. Closed confirmation pulls logic LOW. Open wire/power loss reads HIGH/unconfirmed. [Panasonic](https://industry.panasonic.com/ac/cdn/e/control/relay/photomos/catalog/semi_eng_gu1a_aqy21_gs.pdf), [Omron switch data](https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2hw.pdf).

| XA pair | Feedback | MCP pin |
|---|---|---|
|1–2|Park endpoint|GPA0 /21|
|3–4|Deployed endpoint|GPA1 /22|
|5–6|Park pin fully extended|GPA2 /23|
|7–8|Park pin fully retracted|GPA3 /24|
|9–10|Deployed pin fully extended|GPA4 /25|
|11–12|Deployed pin fully retracted|GPA5 /26|
|13–14|Outer shutter fully open|GPA6 /27|
|15–16|Outer shutter fully closed|GPB0 /1|
|17–18|Shutter catch pin extended|GPB1 /2|
|19–20|Shutter catch pin retracted|GPB2 /3|
|21–22|Spindle stopped feedback|GPB3 /4|
|23–24|Spindle running feedback|GPB4 /5|
|25–26|Kit internal cover open|GPB5 /6|
|27–28|Kit internal cover closed|GPB6 /7|

The **four slide/shutter endpoint contacts** can use Omron **D2HW-C203MR**, black COM / blue NO, subject to actual brackets, cams and overtravel. Their published small-load reference is 5 V / 1 mA; the dry loop supplies about 5.57–8.12 mA including a 1 V low-supply wiring/contact-drop allowance.

The **six pin endpoint sensors** are separate **Panasonic PM-U25-P** units. Use one independent sensor and flag per endpoint, not the complementary outputs of one sensor. Brown receives fused C24V; blue returns to FIELD0; white is the Dark-ON confirmation output. Insulate unused black Light-ON separately. For each PNP channel use this circuit instead of the dry loop:

`C24V -> F_INPUT -> XA:odd -> sensor brown; sensor white -> XA:even -> 3.32 kΩ -> AQY LED pin 1; sensor blue -> dedicated return terminal -> FIELD0.`

The LED shunt, reverse diode and isolated logic circuit remain the same. In the PNP channels the 3.32 kΩ resistor is **after the white return**, not in the brown supply. No 24 V conductor connects to an MCP or MCU pin.

| Pin endpoint | Brown supply | White Dark-ON return | Blue FIELD0 return |
|---|---|---|---|
| Park pin extended | XA5 | XA6 | XA41 |
| Park pin retracted | XA7 | XA8 | XA42 |
| Deployed pin extended | XA9 | XA10 | XA43 |
| Deployed pin retracted | XA11 | XA12 | XA44 |
| Shutter catch extended | XA17 | XA18 | XA45 |
| Shutter catch retracted | XA19 | XA20 | XA46 |

The PNP output's maximum 1 V residual at 16 mA plus the separate 1 V wiring allowance leaves **at least 5.276 mA** calculated AQY LED current at 21.6 V. The maximum load remains below 8.12 mA, inside that residual-voltage reference point. Add **six × 15 mA = 90 mA** sensor quiescent current to the field load; this published consumption includes the sensor's built-in indicator. No extra field indicators are selected. The retrieved catalog does not establish a worst-case output-off leakage bound: verify an unblocked slot produces AQY LED current below 0.1 mA at the actual temperature/supply before commissioning. Do not infer a guaranteed off margin from the powered-on calculation. [Panasonic catalog](https://industry.panasonic.com/ac/e_download/fasys/sensor/micro/catalog/pm-254565_e_cata.pdf?f_cd=402226&via=ok), [selected sensor record](../hardware/PIN-SENSORS.md).

Both endpoint indications cannot legitimately be true together. Combine the **correct slide endpoint plus its matching pin** for engagement; inactive pins can extend in free air. Sensor flags must correspond to full pin travel. A fouled or blocked optical slot can falsely indicate an endpoint: guarded placement, inspection and the opposing independent sensor/travel checks are required. This installation has no safety performance claim. The selected sensor is a procurement candidate; observed backorder/price data do not establish availability or delivered cost.

The final four channels are electrically defined **only for verified isolated dry contacts**. The actual VFD and kit have not been identified; do not connect a24 V/5 V/PNP/NPN signal directly to this loop, and do not jumper a missing feedback. A drive's “run command accepted” is not necessarily running or standstill feedback. The exact meanings, thresholds, delay and fault behavior must be documented. Existing PG7 IR,PG8 toolsetter andPF10 presence also retain their separate unresolved isolation interfaces. They are not fabricated contacts on this expander.

## Three isolated command channels

For PE13,PE14 and PD10 use separate identical stages:

`GPIO ->1k -> SN74LVC1G17DBVR pin2`, with 10k from pin 2 to LOGIC0. Buffer pin 5 = 3V3, pin 3 = LOGIC0, pin 1 = NC;100 nF across 5–3. Pin 4 ->154 Ω1%0.25 W ->AQY212GS LED1;LED2 = LOGIC0;22k acrossLED1–2. Output AQY pin 4 = AUX24_SAFE through0.25 A control fuse;AQY pin 3 = relay A1;relay A2 = FIELD0. Fit 1N4007 directly across each relay coil, cathode at A1. PD10 is J14 pin 2 through the board's 100 Ω resistor; J14 pin 1 is LOGIC0; the buffer pull-down still provides an off state. Each PhotoMOS drives **only one ≤40 mA relay coil**, never a solenoid. [TI pinout](https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf), [Finder contacts/coil/socket](https://cdn.findernet.com/app/uploads/S40EN.pdf).

| Command | Relay and socket | Contact wiring |
|---|---|---|
|PE13, active HIGH releases both rack pins|K_RACK_RELEASE, 40.52.9.024.0000 / 95.05|AUX24_SAFE -> 11, NO 14 branches through independent 1 A fuses to XA31 and XA33|
|PE14, active HIGH releases shutter catch|K_SHUTTER_RELEASE, 40.52.9.024.0000 / 95.05|AUX24_SAFE -> 11, NO 14 ->independent 1 A fuse -> XA35|
|PD10, active HIGH permits original run-arm chain|K_ATC_GATE, 40.52.9.024.5000 gold / 95.05|Existing XW34 -> XA39 -> 11; NO 14 -> XA40 -> existing PERMIT|

**Remove the old direct XW34–PERMIT link when inserting K_ATC_GATE; never leave a parallel bypass.** This places the added contact upstream of both K_RUN_ARM's pickup/hold branches and its tool-request pole. Losing the ATC gate drops run-arm as well as selected-tool permission. K_REQUEST remains independently supplied as in the baseline, so a held-high run request cannot re-arm. Existing PG6 readiness is upstream and does not prove this added relay contact closed. The additional contact is ordinary control, not a monitored safety relay; a welded contact is not detected here.

**Relay timing handoff:** K_ATC_GATE opening drops K_RUN_ARM on every conversion. After restoring the gate, keep PG2 LOW for a measured, qualified release-to-rearm interval covering both K_ATC_GATE closing and K_RUN_ARM pickup. The future M6 adapter must enforce this before the first spindle request or toolpath action. The offline TOOL permission is immediate and does not simulate relay pickup; PG6 is not gate/run-arm feedback. Do not bypass the request-release interlock to cure a timing race.

XA31/32 = park solenoid+/return; 33/34 = deployed solenoid+/return; 35/36 = shutter solenoid+/return. XA32/34/36 = FIELD0. Each coil is Delta **DSOL-1151-24C** with its own local **1N5408**, cathode at positive, anode at return. Separate coil branches avoid interpreting a shared fuse as individual protection. The relay sees up to 1 A combined design allocation for the two rack coils; shutter allocation 0.5 A. Unused relay poles 21/22/24 are insulated and unconnected. XA29/30 = C24V/FIELD0 input-board supply; XA37/38 = AUX24_SAFE/FIELD0 actuator feed. All field terminals may use Phoenix PT 2,5/3209510 with appropriate end plates and rail restraints, consistent with the earlier panel selection.

The Delta sheet specifies 24 V, 7.5 W, 100% duty, 76.8 Ω±10% at 25°C but also lists 0.4 A. Use at least 0.4 A per coil; this candidate budgets 0.5 A each. [Hardware source and qualification](../hardware/LOCK-ACTUATOR.md) records that discrepancy and the unqualified pull force. A 0°C copper-resistance screen gives about 0.424 A at 26.4 V, but it is not a guaranteed cold-winding limit. The 1 A fuses are candidate branch protection; verify DC interrupt rating, actual supply fault current, wire ampacity and coil data. Design allocation for all three coils, three relay coils, 14 input loads and six sensor quiescent loads is about 1.824 A on 24 V, excluding both stepper motor supplies and the actual kit. Flyback diodes slow spring return; measured de-energize/engage time is required. [Vishay 1N5408](https://www.vishay.com/docs/88516/1n5400.pdf).

The same independently sensed catch must engage at either stopped shutter detent. Before parked run permission, the model explicitly waits in CAPTURE_SHUTTER_CLOSED for extended/not-retracted feedback; simply seeing the closed endpoint is insufficient.

## Motor and firmware boundary

Wire each verified winding pair to its corresponding S5/S6 A1/A2 and B1/B2 terminals, with strain relief and shield bonding at cabinet PE. Identify pairs by the delivered motor's drawing and resistance measurement; the old 17E19S1684MB sheet and newer MB4 variants have different documented lead colors, so this document does not guess a color translation. Never connect/disconnect a motor while energized. No external stepper driver is added.

S5/S6 share SPI with existing axes. The future scheduler must serialize configuration/register transactions, keep S7/S8 chip-selects and enables inactive, use 75 mΩ per auxiliary channel and stop pulses on failed health/readback. The current firmware's board initialization intentionally sets S5/S6 disabled: this candidate is not runnable by wiring alone. Independent watchdog/fault responses and the actual motor-power stop arrangement remain untested. A 200 mm nominal pulse count or a limit switch is not a proven mechanical travel boundary.

## Additional component count for the large-machine candidate

- 1 MCP23017-E/SP; 14 AQY212GS input channels; 3 AQY212GS output channels; 3 SN74LVC1G17DBVR buffers.
- 2 Finder40.52.9.024.0000, 1 Finder40.52.9.024.5000, 3 Finder95.05 sockets; 3 Delta release coils; 3 local 1N5408 and 3 relay 1N4007 diodes.
- 4 selected mechanical endpoint switches, 6 PM-U25-P pin sensors, and 4 unselected external dry-contact interfaces; the existing IR/toolsetter/presence interfaces are additional.
- 46 new XA terminal positions, 3 individual 1 A coil fuse branches plus separately protected control/input feeds; the exact fuse/holder SKUs and final harness remain open.

This count does not include the actual magazine, its cover electronics, or the two separately selected screw motors. No delivered-price total or hardware qualification follows from the arithmetic screen.
