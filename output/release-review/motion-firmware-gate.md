# Motion and plasma firmware release gate

**Historical review. The missing Kraken implementation described below has now been built.** See [Rev E controls](../../RevE-ENGINEERING/controls/README.md) and its verification record. The custom Kraken V1.1 hybrid image compiles with onboard X/Y1/Y2/Z drivers, independent Y homing, router PWM and external Arc OK/UP/DOWN plasma step injection. Forty-eight static/image checks pass. Physical boot, SPI current control, motion and live-arc testing remain commissioning work. The exact owned cutter and its isolated CNC interface are still unidentified. Manta M5P was not substituted or developed for this revision.

The following text preserves the findings before that implementation was completed.

Reviewed 2026-09-24. Scope: BIGTREETECH Manta M5P V1.0 or Kraken, four onboard motor-driver channels for X/Y1/Y2/Z, automatic dual-Y homing, router operation, and live arc-voltage plasma THC. External stepper drivers are excluded by the user.

## Decision

**HOLD both choices for procurement as a validated complete CNC router/plasma controller.** Both can provide ordinary motion using supported firmware. No exact-board firmware and isolated plasma-interface combination has been verified that meets the complete requirement. This is a validation gap, not a claim that either board is physically incapable of CNC motion or cannot be developed further.

Kraken remains the stronger hardware candidate if the project accepts firmware development and validation. Its eight integrated TMC2160 drivers satisfy the requested onboard-driver arrangement. That does not make its firmware a plasma controller. No external up/down THC box or Klipper macro has been accepted as an equivalent to coordinated real-time THC.

## Pinned primary evidence

GitHub repository heads below were obtained directly through the GitHub API on the review date. Relevant source files were retrieved by full commit SHA and saved beside this report.

1. **Kraken / grblHAL** — `dresco/STM32H7xx` at `bfe5d4f6ec271cc9929336244c3b1c8e55d1d040` (2026-06-30). `driver.json` and the entire recursive repository tree have no Kraken board mapping. Existing H723 processor support does not imply an interchangeable board pinout. The tree does contain `boards/btt_manta_m8p_v2_map.h`; this is Manta **M8P V2**, not the selected M5P. `Inc/my_machine.h` labels the plasma option unfinished.
   - https://github.com/dresco/STM32H7xx/blob/bfe5d4f6ec271cc9929336244c3b1c8e55d1d040/driver.json
   - https://github.com/dresco/STM32H7xx/tree/bfe5d4f6ec271cc9929336244c3b1c8e55d1d040/boards
   - https://github.com/dresco/STM32H7xx/blob/bfe5d4f6ec271cc9929336244c3b1c8e55d1d040/Inc/my_machine.h

2. **Manta M5P / grblHAL** — `djwmarcx/STM32G0xx` at `804c4f4d8b83fe5276bb55c7bad7870aa0f83399` (2026-07-25). The README describes testing on an SKR Mini E3 V3.0 and explicitly says Manta M5P would need its own board map. This is not a released M5P configuration.
   - https://github.com/djwmarcx/STM32G0xx/blob/804c4f4d8b83fe5276bb55c7bad7870aa0f83399/README.md
   - https://github.com/djwmarcx/STM32G0xx/blob/804c4f4d8b83fe5276bb55c7bad7870aa0f83399/driver.json

3. **Klipper-plasma is not a drop-in remedy** — actual default branch `plasma`, commit `d9be1f5f31ad64efc9a701aa91f1c21781bf8a47` (2020-11-03). Its STM32 processor choices are F103/F207/F405/F407/F446/F042/F070. They exclude M5P's G0B1 and Kraken's H723. Porting or rebasing would be required. This review checked the default plasma branch, not merely its older upstream master branch.
   - https://github.com/proto3/klipper-plasma/blob/d9be1f5f31ad64efc9a701aa91f1c21781bf8a47/src/stm32/Kconfig
   - https://klipper-plasma.readthedocs.io/en/latest/introduction.html

4. **Ordinary Klipper motion is distinct from THC** — current mainline Klipper head checked: `ce7002bedf37e938bb483572949f3703ac6476cb` (2026-09-19). BTT publishes configurations for both exact boards. Cartesian multi-rail implementation supports numbered additional steppers with their own endstop inputs; two Y motors must use distinct drivers and switches. The stock configuration reference does not document a live arc-voltage THC module.
   - https://github.com/Klipper3d/klipper/blob/ce7002bedf37e938bb483572949f3703ac6476cb/klippy/kinematics/cartesian.py
   - https://github.com/Klipper3d/klipper/blob/ce7002bedf37e938bb483572949f3703ac6476cb/klippy/stepper.py
   - https://www.klipper3d.org/Config_Reference.html
   - https://github.com/bigtreetech/BIGTREETECH-Kraken/blob/master/Firmware/generic-bigtreetech-kraken.cfg
   - https://github.com/bigtreetech/Manta-M5P/blob/master/Firmware/Klipper/generic-bigtreetech-manta-m5p.cfg

5. **grblHAL plasma plugin exists, but is not proof of exact-board readiness** — current plugin head `d2f91b5887db6550ddec0fc0229cd87ec0af1a56` (2026-09-02). Its README labels it under development. It documents arc-voltage and external-up/down modes, Arc OK, and velocity anti-dive. A working board mapping, suitable auxiliary inputs, driver resources, and end-to-end verification are still required.
   - https://github.com/grblHAL/Plugin_plasma/blob/d2f91b5887db6550ddec0fc0229cd87ec0af1a56/README.md

6. **Remora does not establish a supported Kraken route** — checked `scottalford75/Remora` head `09d7e2416da40a46681cb9ddb21cca04242d0fe4` (2026-01-26). Its repository describes LPC176x/STM32F4 boards. The public request for Kraken/H723 support is open. Do not treat the existence of LinuxCNC or Remora on other boards as proof of this board's compatibility.
   - https://github.com/scottalford75/Remora/tree/09d7e2416da40a46681cb9ddb21cca04242d0fe4
   - https://github.com/scottalford75/Remora/issues/68

7. **FluidNC alternative caution** — the project's plasma documentation, updated 2026-08-01, explicitly says controller-side up/down THC is not supported and describes a separate THC intercepting Z instead. Its anti-dive section is marked unsupported. This does not resolve the all-onboard-driver requirement with a new ESP32 board.
   - https://github.com/bdring/fluidnc-wiki-content/blob/main/development/plasma.md

## Hardware and isolation gate

Kraken V1.0 and V1.1 have different S1-S4 sense resistors and manufacturer maximum-current ratings; the actual revision must be fixed before generating driver configuration. Exact motor current and cooling remain to be matched. Its HV driver supply and main logic supply are different inputs.

Neither the driver count nor a low-voltage ADC/endstop connector establishes suitability for plasma arc voltage. The final design still needs the exact plasma source, supported arc-voltage pickup/divider, rated galvanic isolation, isolated torch-start and Arc OK interfaces, a hardware stop chain, defined power-up/power-loss behavior, and a verified firmware input allocation. Direct torch voltage into thermistor/ADC pins is not an accepted interface. Pilot arc does not identify the ignition method or establish an isolated CNC port.

- https://global.bttwiki.com/Kraken.html
- https://github.com/bigtreetech/Manta-M5P

## Smallest alternative worth evaluating

If the user allows a different motherboard while preserving onboard plug-in drivers, **Manta M8P V2 + suitable onboard TMC5160 modules** is a close architectural candidate because an exact H723 grblHAL mapping already exists. **It is not released by this review as a validated plasma purchase.** The plugin and isolated I/O must still be implemented and tested as an exact configuration. Scylla is another mapped integrated-driver board, but merely changing to it does not prove the plasma chain either.

No board-only substitution has been represented as a guaranteed complete solution. The shortest honest path retaining Kraken is a bounded firmware/interface engineering project followed by validation. The procurement release remains held until that gap is closed or the controller constraint changes.
