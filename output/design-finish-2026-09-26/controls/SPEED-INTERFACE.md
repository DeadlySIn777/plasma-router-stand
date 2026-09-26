# Isolated spindle-speed converter

Select **CNC4PC C41S Rev 1.1** for the design baseline. Its manufacturer specifies
an isolated 0–10 V output, 200 Hz recommended PWM, 2–5 V active-high input with
10 mA minimum on-state current, 5 V / 300 mA power and a 105 × 75 × 22 mm envelope.
The earlier unspecified 5 kHz converter is superseded. The verified current
firmware exposes PWM frequency as **$33**; set it to **200 Hz** during isolated
commissioning and verify the actual PE9 waveform. No board has been connected,
programmed or operated as part of this change.

Sources: [manufacturer manual](https://cnc4pc2.s3.us-east-2.amazonaws.com/files/c41s-r1.1_user_manual_v1.pdf),
[official product family](https://www.cnc4pc.com/shop/category/integration-electronics-spindle-control-436),
and the checked-in grblHAL `grbl/config.h` definition of `Setting_PWMFreq`.

## Controller-side connection

Use a second **SN74LVC1G17DBVR** buffer with the same controller-side 3.3 V
supply and return as Kraken. Pin 5 receives 3.3 V; pin 3 is controller return;
pin 1 is unused. Place 100 nF between pins 5/3. Connect PE9 through 1 kohm to
pin 2, with a 10 kohm pull-down at pin 2. Pin 4 drives the C41S PWM input. Keep
this wiring short inside the enclosure. The buffer, rather than the MCU,
supplies the module input current.

The buffer guarantees at least 2.3 V high at 24 mA with a 3 V supply. Acceptance
requires the delivered C41S input to draw **10–20 mA** at the actual driven
high level; its manual gives a minimum rather than a worst-case maximum.
Measure that current and the high/low waveform into the actual load before
connecting the drive. This is a concrete interface acceptance limit, not an
invented input-resistance value. Validate default-low behavior during reset,
power sequencing and an unplugged controller.

Use only the **C41S input RJ45** for this harness; its printed-page 6 drawing
identifies the following pins. It is not an Ethernet network connection.

| Input RJ45 pin | Connection |
|---|---|
| 1 GND | Controller return |
| 4 REV | Controller return; no reverse command |
| 5 PWM | Buffered PE9 |
| 7 5 V | Fused controller-domain 5 V supply |
| 2, 3, 6, 8 | Unconnected |

Allocate at least 350 mA on the controller's 5 V power branch. Kraken's official
5 V rail limit is 5 A shared with its other loads; this is not 5 A per connector.
Use its documented USB-A power output through a power-only lead and a separate
500 mA branch fuse, then verify voltage and total rail load. Do not also feed
the C41S screw power terminals or join this supply to VFD analog common.
[Kraken primary power limits](https://global.bttwiki.com/Kraken.html).

## Drive-side connection and settings

Use only output RJ45 pin 2, analog 0–10 V, and pin 1, isolated analog common.
All other output RJ45 conductors are omitted from the harness. Remove unused
relay-common jumpers and leave C41S relay contacts unwired; the independent
K_VFD_RUN circuit owns the run command. Select US mode with REV held low.
Do not infer the VFD's AI/ACM names or programming parameters from another
brand. The exact delivered VFD manual must identify the voltage input, common,
input impedance, forward-run contact and frequency scaling.

With the VFD disconnected, measure 0, 25, 50, 75 and 100% duty commands;
nominal output targets are 0, 2.5, 5, 7.5 and 10 V after calibration. Repeat
with the documented equivalent VFD input load, verify the response and absence
of run permission on reset, then check the actual drive at low energy. A
nonzero analog output must never substitute for the hardware run permission.

The chosen module is now identified and its frequency/pin/power requirements
are recorded. Delivered-board input current, calibration, noise response,
panel location/thermal clearance and the actual VFD connection remain
commissioning/interface inputs. This is not a fabricated interface PCB or
a claim that any converter can accept raw plasma arc voltage.
