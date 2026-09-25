# Kraken V1.1 hybrid motion controller — engineering implementation

This folder contains an actual compiled grblHAL STM32H7 board port for the Kraken V1.1, with X/Y1/Y2/Z on its four S1–S4 integrated TMC2160 channels. It has independent dual-Y homing and the upstream plasma plugin's live Z step injection. No external stepper drivers are used. The binary passed the static and compiled-image checks recorded in `verification.json`; it has **not** been booted or electrically tested on a Kraken. This is a prototype commissioning build, not a claim of completed machine acceptance.

## Delivered files

- `firmware/kraken-v11-hybrid.bin` and `.elf`: the single combined firmware image.
- `grblhal-h7/boards/my_machine_map.h`: board pin allocation.
- `grblhal-h7/Src/kraken_board.c`: unused S5–S8 driver enable/CS idle states.
- `grblhal-h7/kraken.ini`: reproducible PlatformIO environments.
- `build.ps1`, `verify_port.py`, `build-hybrid.log`, `verification.json`: build and checks.
- `source-manifest.json`, `patches/`: pinned upstream revisions and local changes.
- `COMMISSIONING.md`: ordered physical acceptance procedure and mode settings.

The selected image supports both router and plasma. Plasma mode `$350=0` disables the plasma motion hooks on controller boot; `$350=2` enables external Arc OK / UP / DOWN THC. A cold controller reset is required after changing this setting. Tool power must be inhibited throughout switching. The hardware mode selector must independently connect the enable request to only the selected tool. Mode changes are not performed inside a running job.

## Exact motor allocation

| Function | Kraken socket | STEP | DIR | EN (active low) | CS | Limit input |
|---|---|---|---|---|---|---|
| X, 800 mm | S1 | PC14 | PC13 | PE6 | PD6 | PC15 |
| Y1, 1,000 mm | S2 | PE5 | PE4 | PE3 | PD5 | PF0 |
| Y2, independent home switch | S3 | PE2 | PE1 | PE0 | PD4 | PF1 |
| Z, 100 mm | S4 | PB9 | PB8 | PB7 | PD3 | PF2 |

S3 is grblHAL motor M3 ganged to Y; it is not a fourth G-code coordinate. SPI is SCK PC6, MISO PC7, MOSI PC8. S5–S8 remain unused, disabled, and deselected. No sensorless homing is used: remove the corresponding DIAG-to-endstop jumpers according to BTT's manual and use physical switches.

**Only Kraken V1.1 is covered.** Its S1–S4 sense resistors are 0.050 ohm; the library parameter is **50 milliohms**. Kraken V1.0 uses 0.022 ohm on these channels and must not use this image. S5–S8 have another sense value and must not be substituted into the map. BTT's official example uses the `tmc5160` register interface for the board's TMC2160 chips; this port uses grblHAL's corresponding SPI implementation. Physical SPI register readback remains an acceptance test.

Default motor current is **500 mA RMS per logical axis**, including both Y drivers. This is a low-energy unloaded commissioning value, not a cutting setting. The Z listing gives 3 A/phase but does not establish how that number maps to a sine RMS driver setting. The X/Y motor current specification remains to be obtained. Do not set 3 A RMS merely because a listing says 3 A/phase. Validate motor/vendor definitions, then thermal-test the chosen current.

## External connector allocation

| Signal | Physical connector | MCU pin | Electrical interface |
|---|---|---|---|
| Arc OK | EXP1 pin 8 | PD12 | isolated 3.3 V-compatible logic |
| THC DOWN | EXP1 pin 7 | PD13 | isolated 3.3 V-compatible logic |
| THC UP | EXP1 pin 6 | PD14 | isolated 3.3 V-compatible logic |
| E-stop chain status | EXP1 pin 2 | PG4 | isolated status from independent hardware stop circuit |
| Feed hold | EXP1 pin 3 | PG3 | isolated/button logic |
| Cycle start | EXP1 pin 1 | PG5 | isolated/button logic |
| Floating head / router tool probe | EXP2 pin 4 | PE11 | selected probe circuit, isolated logic |
| Machine permissive / breakaway / door | EXP2 pin 7 | PG6 | isolated series permissive-chain status; hardware also removes tool permission |
| Torch / VFD run request | EXP1 pin 4 | PG2 | logic to normally-off isolated output circuit and keyed tool selector |
| VFD speed request | BLTouch SERVO signal | PE9 | 5 kHz PWM to isolated PWM-to-0–10 V converter |

EXP headers expose MCU logic. Their separate 5 V supply pin does **not** make the signals 5 V inputs. Do not connect 24 V sensors, VFD terminals, torch triggers, arc voltage, or plasma work return directly to these pins. All interface signal levels, isolation ratings, default states, and connector orientation must match the final interface schematic. Do not use a heater/fan MOSFET output as a logic substitute.

The mapped free aux input ports are intended as Arc OK=0, DOWN=1, UP=2. Confirm these physical-to-logical mappings using `$PINS` on the actual controller before assigning `$367/$368/$369`. The static test also checks that all 12 interrupt inputs have distinct EXTI line numbers; this avoids an STM32 port-selection collision.

This firmware route uses a separate **arc-voltage-sensing THC with isolated Arc OK, UP and DOWN signals**, not a separate motor driver. Kraken still controls every motor and applies the real-time Z correction. The exact cutter-facing voltage/trigger interface must be supplied by a compatible external THC/interface, following the cutter's documented CNC connection. This build does not decode THCAD frequency and does not accept raw arc voltage. No voltage-reading or anti-void capability is implied by UP/DOWN mode; velocity anti-dive is implemented by the plasma plugin.

The controller's E-stop input is a status/reporting path. The physical E-stop and breakaway chain must independently remove tool permission. Firmware, USB, an SBC, or a GPIO is not the sole stop mechanism. PG2 needs an external normally-off interface so reset, loss of power, and an unplugged controller cannot command a tool.

**Water/bed permissive reservation:** PG6 / EXP2 pin 7 is reserved for the isolated combined machine-permissive status (bed locked, appropriate water state, breakaway and door chain), presented as the safety-door input. The same hardwired chain must gate tool permission independently. The separate relay/float-switch controller owns fill, drain and router-ready logic; Kraken firmware does not run or supervise the water-transfer sequence. If separate diagnostics are desired, add them outside this reserved combined stop/permissive input.

## Build and source

The build uses PlatformIO 6.2.0, `ststm32@20.0.0`, STM32CubeH7 1.12.1, and ARM GCC 7.2.1. Runtime packages are inside this folder's `.platformio`; the Python 3.12 venv is `.venv`. Run `./build.ps1` from PowerShell. It builds only `kraken_v11_hybrid`, then verifies the output. It does not flash any hardware.

For a fresh checkout, create a Python 3.12 venv at `.venv`, install `platformio==6.2.0`, clone the source recursively at the revisions in `source-manifest.json`, and apply the included patches / board files. The existing local source already contains them. The linker file reserves 128 KiB for the BTT bootloader and the last 128 KiB for settings. The H723VG-named upstream linker file has the same 1 MiB flash / memory layout needed here; the actual selected MCU is H723ZG. The linked vector is `0x08020000`; the binary is not a bootloader image.

One small plasma-plugin fix is included: a stored retry count of zero is clamped to one before decrementing, the setting accepts 1–255, and the default is one initial attempt with no automatic re-strike. In this implementation `$360=1`, not zero, means one attempt. Existing nonzero NVS settings are not silently rewritten. All source changes and the plugin patch are delivered, with original licenses retained.

Primary references:

- [BTT Kraken documentation](https://global.bttwiki.com/Kraken.html)
- [BTT Kraken repository, manual and schematic](https://github.com/bigtreetech/BIGTREETECH-Kraken)
- [BTT official pin configuration](https://github.com/bigtreetech/BIGTREETECH-Kraken/blob/master/Firmware/generic-bigtreetech-kraken.cfg)
- [grblHAL STM32H7 driver](https://github.com/dresco/STM32H7xx)
- [grblHAL plasma plugin and mode definitions](https://github.com/grblHAL/Plugin_plasma)
