# Floating head and seated-head inputs

The head now has two defined low-voltage input channels: **an isolated NC float input to PE11**, and **three series NO presence contacts driving a normally-off output across XH:5/6**. These are the four switches already counted in the mechanical head, not four additional switches. This schematic supersedes the earlier motion document's provisional 5 V loop. The frozen CAD metadata remains historical; it does not define this electrical revision.

The [machine-readable schematic](head-interface.json) defines each connection, value, component and terminal. [The checker](verify_head_interface.py) evaluates the actual connection graph, tolerances and finite-delay interaction with the existing relay circuit. [Its report](head-interface-verification.json) is schematic evidence, not a powered-board test. No cutter trigger, raw arc voltage, new motor driver or safety-rated stop is included.

## Presence loop and the existing tool-permission circuit

Use **U_HEAD, Panasonic AQY212GS**. Its LED is pins 1 positive / 2 negative; the normally-open bidirectional output is pins 3/4. Three **Omron D2HW-C203MR** contacts use black COM and blue NO. All three must close with the release plate seated.

```text
Existing fused C, 24 V
  -> R_HEAD 3.32k -> XHEAD:3
  -> S_HEAD_L black / blue -> XHEAD:4
  -> panel link -> XHEAD:5 -> S_HEAD_R black / blue -> XHEAD:6
  -> panel link -> XHEAD:7 -> S_HEAD_T black / blue -> XHEAD:8
  -> U_HEAD pin1 LED pin2 -> XW:2 field 0 V

Existing XH:5 (DOOR_SAFE) -> U_HEAD pin4 / pin3 -> XH:6 (HEAD_SAFE)
HEAD_SAFE -> R_BLEED 100k -> XW:2
```

R_HEAD is **3.32 kohm, 1%, 0.6 W** and sits inside the panel before any outgoing field wire. A **22 kohm, 1%** resistor shunts U_HEAD pins 1/2. Fit a **1N4148 anti-parallel** across those same pins, cathode to pin 1. Do not bridge the presence contacts or feed the LED from HEAD_SAFE: it is powered from C, independently of its output. Opening any contact, any conductor in this loop, or its field supply removes the LED drive and then the XH:5/6 closure. The controller does not create this permission.

HEAD_SAFE feeds **IF_READY plus K_RUN_ARM and the selected tool relay**. K_REQUEST has its own supply and is not on this output. Including resistor tolerances, the IF_READY maximum is 26.737 mA. Allow at most **40 mA per relay coil**, including the actual cold-coil condition. With the 100 kohm bleed, normal demand is about **107.01 mA**; even energizing both tool coils gives about **147.01 mA**, without making that abnormal state acceptable. The output allocation is **150 mA maximum, with no additional loads**. At the catalogue 0.7 ohm reference resistance this implies 0.105 V drop and 15.75 mW output dissipation. Retain a diode directly across each downstream coil, cathode to A1, and verify field-supply/transient voltage. The device has no short-circuit protection.

The 100 kohm bleed bounds the nominal off-state output to 0.102 V with all loads disconnected and 1 microamp catalogue leakage. A shorted PhotoMOS or bridged/welded switch can mask a release; this circuit is an ordinary operating permissive, not a monitored safety function. It does not replace the independent stop circuit.

## Float input and controller connection

Use **S_FLOAT, Omron D2HW-C202MR**, black COM / red NC, and **U_PROBE, a second AQY212GS**. The NC contact must be closed at the float's normal lower stop and open when its cam trips.

```text
C -> R_PROBE 3.32k -> XHEAD:1 -> S_FLOAT black / red -> XHEAD:2
  -> U_PROBE pin1 LED pin2 -> XW:2 field 0 V
22k and reverse 1N4148 across U_PROBE pins1/2, as above

Controller 3V3 -> R_PULLUP 4.7k -> PE11 / EXP2 pin4
PE11 -> R_SERIES 330 ohm -> U_PROBE pin4 / pin3 -> LOGIC_0
PE11 -> C_PROBE 4.7nF -> LOGIC_0
```

R_PROBE also sits before its outgoing wire. Mount the **4.7 kohm pull-up, 330 ohm series resistor and 4.7 nF, 5%, C0G/NP0 capacitor at the controller header**, so a disconnected receiver cable still leaves PE11 pulled high. The [BTT schematic](https://github.com/bigtreetech/BIGTREETECH-Kraken) identifies J22 SWD pin 1 as controller 3.3 V and pin 3 as controller ground; verify these labels on the actual V1.1 board. J_PROBE:1 is PE11, :2 controller ground and :3 controller 3.3 V. EXP2 pin 4 is signal only. Do not use an EXP +5 V supply or connect field 0 V to controller ground. This passive isolated output needs no separate receiver supply.

| Condition | Float LED / isolated contact | PE11 | Meaning |
|---|---|---|---|
| Float normal, field supply healthy | On / closed | LOW | Not triggered |
| Float trips | Off / open | HIGH | Triggered |
| Float wire or field supply opens | Off / open | HIGH | Fault/triggered; probing must not start |
| Receiver-to-controller signal cable opens | Irrelevant | HIGH through header-side pull-up | Fault/triggered |
| Contact, cable or receiver output shorts | May remain closed | May remain LOW | Undetected fault; test physically before use |
| Controller power lost | Undefined logic | No valid controller state | No probe-status claim |

The current vendored grblHAL driver reads raw GPIO and XORs the probe inversion bit. For this healthy-LOW/open-HIGH circuit, the primary probe's **$6 bit 0 is zero**; preserve any other probe bits. Confirm the live status before movement. Disable any internal pull-down; an internal pull-up may remain enabled and is included in the low-level screen. A probe command must begin untriggered, stop on opening, and return to untriggered after retract. No firmware was flashed by these checks.

In router mode the assembled head remains wired in its parking cradle, so its presence loop can remain healthy. **Its parked float is not a spindle touchplate. Router Z zero is manual in this design.** Do not run a router probing macro against this float input. During tool conversion use SETUP and BED UNCONFIRMED; opening the separated head removes tool permission.

## Ratings, calculations and timing limits

The [Panasonic product data](https://industry.panasonic.com/ap/en/products/control/relay/photomos/number/aqy212gs) recommends 5–30 mA LED drive and a maximum 48 V load. Its [catalogue](https://industry.panasonic.com/ac/cdn/e/control/relay/photomos/catalog/semi_eng_gu1a_aqy21_gs.pdf) supplies the pinout and reference resistance/leakage. The 5 ms turn-on and 0.5 ms turn-off maxima are specified at **25 C, 5 mA LED drive, 100 mA load and 10 V**. They are model inputs, not qualified delays at this probe's much smaller load or the actual 24 V relay load.

Calculations use field 21.6–26.4 V, 1 V allowed wiring/contact drop, 1.5 V LED maximum and a conservative 2% effective resistance envelope around the selected 1% parts. This covers initial tolerance plus a bounded allowance for temperature/drift; actual panel temperature still needs verification. Each channel drives at least about **5.57 mA**, with a conservative zero-forward-voltage upper bound of **8.12 mA**. A short on a field loop after its resistor remains limited by that resistor, whose maximum power is about **0.214 W**. This does not qualify a bypass short on the supply or semiconductor output.

The [Omron D2HW data](https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2hw.pdf) specifies gold contacts, a 5 V / 1 mA minimum circuit load, and 1 A resistive at 24 V. These limits support the chosen low-current field loop. They do not establish a contact-bounce or installed trip-delay bound. [Vishay MRS25 data](https://www.vishay.com/docs/28724/mrs16m25.pdf) supports the selected 0.6 W, 1% series, 50 ppm/K resistance family. Anti-parallel diode ratings are from [Vishay 1N4148](https://www.vishay.com/docs/81857/1n4148.pdf).

At logic supply 3.0–3.6 V, including an enabled 30 kohm internal pull-up, the screen gives healthy PE11 below **0.30 V** and open PE11 above **2.99 V**. It allows 1 microamp each for pad and receiver leakage. These exceed the conservative CMOS margins from [STM32H723 Table 51](https://www.st.com/resource/en/datasheet/stm32h723zg.pdf). The RC screen includes capacitor tolerance plus an explicit **1 nF maximum extra local capacitance**. It adds under 0.1 ms to the catalogue off delay, giving a reference travel under 0.001 mm at the initial **1 mm/s** probing speed. This excludes switch motion/bounce, firmware latency, deceleration and machine compliance; it is not a stop-distance claim.

The checker exercises both modes across nine relay pickup/dropout combinations. Each presence contact, a field cable open and field-power loss is held for **300 ms**, including the PhotoMOS delay, then recovered with a held run request. Both tool outputs must drop, PG6 permission must disappear, and the request must return low before restarting. Arbitrarily short pulses are not guaranteed to latch; the existing relay model already records that limit. A shorted presence output is deliberately demonstrated as a masking counterexample.

## Terminals, quantity and commissioning record

XHEAD is **eight Phoenix Contact PT 2,5 / 3209510** DIN feed-through blocks, one D-ST 2,5 / 3030417 end cover and two CLIPFIX 35-5 / 3022276 end brackets. There are no common bridges. Use one correctly prepared conductor per entry. Panel links 4→5 and 6→7 complete the series string. The [primary terminal data](https://www.phoenixcontact.com/en-gb/products/feed-through-terminal-block-pt-25-3209510?type=pdf) covers connection ranges and accessories. For the D2HW's fine stranded leads, use the approved ferrule/release-tool method for the actual lead cross-section; do not force bare fine strands into a direct-insertion connection. Mark 1/2 FLOAT NC, 3/4 LEFT NO, 5/6 RIGHT NO, 7/8 TOP NO. Keep these wires twisted in pairs and physically separated from motor/VFD/torch conductors; any shield terminates at cabinet PE, not the MCU signal return. Final harness routing remains to be drawn and checked.

The [selected controls schedule](selected-components.json) now contains **three AQY212GS total**: the existing run channel and these two added channels. Its four Omron switches cross-reference the already-counted mechanical parts. The seven head resistors, two diodes, one capacitor and field terminal parts are additional electrical inventory. No price, stock, delivery or complete-panel BOM is claimed.

Before connecting a real tool: record actual coil current and interface temperature; verify C supply/coil transients; measure LOW/HIGH and both channels' response with the real loads; open every field conductor; lift each presence cam separately; trip/retract the float; disconnect receiver signal/ground; verify cold boot, reset and controller-power loss; then verify 300 ms fault/recovery with run held and released. Perform the signal tests with motion/tool power disabled first. Record observed switch/receiver/controller latency before selecting a probing feed. The PCB layout, physical control station, full panel protection/stop/brake implementation and EMI behavior remain unfinished engineering work, not measured conclusions of this document.

Reproduce with Python:

```powershell
python output/design-finish-2026-09-26/controls/verify_head_interface.py
```
