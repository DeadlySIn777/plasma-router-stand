# ATC control integration for the new variants

**Design reservations, not working ATC firmware.** The existing Rev I controller
and circuit files remain unchanged. This directory identifies the required
changes so a modeled magazine cannot be mistaken for an operational tool changer.

## What changes from Rev I

The present Kraken router/hybrid build selects `SPINDLE_PWM0_NODIR`, has no
direction pin, and uses PE11 for the removable plasma head's float input.
The C41S speed interface holds REV low and leaves its relay outputs unused;
the separate hardware run-permission circuit owns spindle start. Router Z zero
is manual. Those are concrete compatibility gaps, not solved by attaching a rack.

The ATC variant requires a direction-capable spindle configuration, a separate
fixed router toolsetter, magazine status inputs, the selected cover interface,
and a filesystem-backed M6 integration. Retain hardware mode selection,
release-to-rearm logic and the independent run relay. A reverse command must
never bypass run permission or permit a plasma-mode spindle command.

## Reserved connections

| Function | Proposed Kraken V1.1 connection | Qualification still required |
|---|---|---|
| Spindle direction | PD15, EXP1 pin 5 | Isolated interface and actual VFD forward/reverse truth table |
| Fixed router toolsetter | PG8, EXP2 pin 3 | Sensor circuit, polarity and explicit firmware probe selection |
| ATC infrared status | PG7, EXP2 pin 5 | Exact kit sensor voltage, polarity and behavior |
| Cover command | PE12, EXP2 pin 2 | Logic reservation only; actual cover/controller protocol, no servo PWM claim |
| Removable dock present | PF10, S7 stop input | Confirm board connector and isolate any S7 DIAG jumper path |

The [reservation check](pin-reservation-check.json) parses the existing source
map, board idle outputs and official connector aliases. It checks GPIO reuse
and STM32 external-interrupt line conflicts for the new inputs. PE12 cannot also
serve an EXP2 LCD/SD SPI connection. The onboard TF card has a separate SPI
connection in the Kraken schematic; its support has not been implemented here.
Raw MCU logic pins cannot accept a 24 V sensor or a VFD terminal directly.

The dock-present input proves only the intended sensor state. It does not prove
that the pins are seated, clamps are tight, the correct rack is installed or
the saved pocket coordinates are valid. Establish a rack identity/reference
check before enabling M6 after removal. Keep the toolsetter referenced to a
metal datum, with the sensor and cable protected during plasma conversion.

## Firmware and spindle qualification

The manufacturer publishes [grblHAL macros](https://github.com/greilick-industries/rcatc-scripts-grblhal).
Its documented integration needs core 20240506 or newer, SD file access and
RS274 expression support. Configuration, cover, tool-change and measurement
macros must agree with the actual rack coordinates and input/output numbering.
The macros' T98 workaround for unloading is distinct from M6 T0. Copying macro
files alone does not supply the missing board interfaces. No runnable M6 file
or firmware image is issued with this design allocation.

The [RapidChange requirements](https://rapidchangeatc.com/faq/) include reverse
rotation, custom M6 and programmable low speed. The actual spindle/VFD must
demonstrate stable operation in the specified change cycle; do not infer this
from its 24,000 rpm nameplate. Before reversal, command stop and verify the
required stopped condition using the actual drive's supported interface.
Do not copy another VFD brand's parameter numbers. Retain the Rev I C41S
200 Hz PWM calibration requirement if that speed converter is retained.
Direction may use a separate isolated drive interface; merely toggling the
C41S REV input while leaving its relays unwired supplies no VFD reverse path.

Cold-start mode selection, tool-power inhibition, dock removal, a failed
toolsetter, a blocked/clear IR sequence fault, controller restart, feed hold
inside a change, and interrupted threading all need explicit recovery behavior.
Software must not resume a machining block after an unverified tool change.
These requirements are open integration work, not a tested safety controller.

## Small machine and 4x8 machine

Both use the same functional interface plan. This does not qualify one set of
motor currents, steps/mm, accelerations or travel limits for both machines.
The small screw modules and the long machine's proposed rack drives require
separate calibration and torque/speed checks. Keeping onboard Kraken drivers
is a design preference; the larger gantry's motor selection remains open.

## Evidence and reproduction

- [Machine-readable reservations](pin-reservations.json)
- [Static verification](verify_reservations.py): `python verify_reservations.py`
- [Official Kraken pin source](https://github.com/bigtreetech/BIGTREETECH-Kraken/blob/master/Firmware/generic-bigtreetech-kraken.cfg)
- [Official Kraken board documentation](https://global.bttwiki.com/Kraken.html)
- [Baseline run circuit](../../../output/design-finish-2026-09-26/controls/RUN-INTERFACE.md)
- [Baseline speed interface](../../../output/design-finish-2026-09-26/controls/SPEED-INTERFACE.md)

The static report binds its source hashes. It does not compile new firmware,
validate an electrical harness, test sensor timing or operate the machine.
