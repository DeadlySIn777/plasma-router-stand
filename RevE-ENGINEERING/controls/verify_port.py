"""Static wiring and compiled-image checks; this is not a hardware test."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT / "grblhal-h7"
MAP = REPO / "boards/my_machine_map.h"
text = MAP.read_text()
official = (ROOT / "kraken-official.cfg").read_text()
defs = dict(re.findall(r"^#define[ \t]+(\w+)[ \t]+([^\r\n/]+)", text, re.M))
checks = []

def check(label, condition):
    checks.append({"check": label, "pass": bool(condition)})
    if not condition:
        raise AssertionError(label)

def resolve(key):
    val = defs[key].strip()
    return resolve(val) if val in defs else val

def pin(name):
    return resolve(name + "_PORT").replace("GPIO", "P") + resolve(name + "_PIN")

motor_order = [("X", "S1", "MOTOR_CSX"), ("Y", "S2", "MOTOR_CSY"),
               ("M3", "S3", "MOTOR_CSM3"), ("Z", "S4", "MOTOR_CSZ")]
physical = {}
for name, socket, cs in motor_order:
    # The official file includes commented examples for unused sockets.
    block = official.split("# " + socket + "\n", 1)[1].split("\n# S", 1)[0]
    for name_part, key in [("STEP", "step_pin"), ("DIRECTION", "dir_pin"),
                           ("ENABLE", "enable_pin"), ("LIMIT", "endstop_pin")]:
        match = re.search(r"^#?" + key + r":\s*!?(P[A-G]\d+)", block, re.M)
        check(f"{socket} {name_part} matches official map", match and pin(name + "_" + name_part) == match[1])
        physical[name + "_" + name_part] = pin(name + "_" + name_part)
    physical[cs] = pin(cs)

for name in ["TRINAMIC_MOSI", "TRINAMIC_MISO", "TRINAMIC_SCK"]:
    physical[name] = pin(name)
for i in range(8):
    physical[f"AUXINPUT{i}"] = pin(f"AUXINPUT{i}")
for i in range(2):
    physical[f"AUXOUTPUT{i}"] = pin(f"AUXOUTPUT{i}")

expected_cs = {"MOTOR_CSX": "PD6", "MOTOR_CSY": "PD5", "MOTOR_CSM3": "PD4", "MOTOR_CSZ": "PD3"}
for key, value in expected_cs.items():
    check(f"{key} matches official CS map", physical[key] == value and "cs_pin: " + value in official)

header_aliases = dict(re.findall(r"(EXP[12]_\d+)=(P[A-G]\d+)", official))
header_signals = {"EXP1_8": "AUXINPUT0", "EXP1_7": "AUXINPUT1", "EXP1_6": "AUXINPUT2",
                  "EXP1_2": "AUXINPUT3", "EXP1_3": "AUXINPUT4", "EXP1_1": "AUXINPUT5",
                  "EXP2_4": "AUXINPUT6", "EXP2_7": "AUXINPUT7", "EXP1_4": "AUXOUTPUT0"}
for header, signal in header_signals.items():
    check(f"{signal} equals official {header}", physical[signal] == header_aliases[header])
check("PWM is official BLTouch PE9", pin("SPINDLE_PWM") == "PE9" and "control_pin: PE9" in official)
check("No assigned physical GPIO overlap", len(set(physical.values())) == len(physical))
interrupts = [value for key, value in physical.items() if "LIMIT" in key or key.startswith("AUXINPUT")]
exti = [int(re.search(r"\d+", x)[0]) for x in interrupts]
check("Every interrupt input has a unique EXTI line", len(set(exti)) == len(exti))
check("V1.1 S1-S4 use 50 milliohm sense value", resolve("TRINAMIC_R_SENSE") == "50")
check("S1-S4 exclusively selected", "N_ABC_MOTORS != 1" in text and "!Y_AUTO_SQUARE" in text)
plugin = (REPO / "plasma/thc.c").read_text()
check("Zero stored arc-attempt count is guarded before decrement", "plasma.arc_retries ? plasma.arc_retries : 1" in plugin)
check("Only one initial arc attempt by default", ".arc_retries = 1," in plugin)
check("Arc-attempt setting rejects zero", 'Format_Int8, "#0", "1", "255", Setting_NonCore, &plasma.arc_retries' in plugin)
unused = {"S5_EN": "PG13", "S6_EN": "PG12", "S7_EN": "PB5", "S8_EN": "PG14",
          "S5_CS": "PD2", "S6_CS": "PA15", "S7_CS": "PA9", "S8_CS": "PA10"}
check("Unused driver EN/CS do not conflict with assigned pins", not (set(unused.values()) & set(physical.values())))
check("All unused driver pins appear in official configuration", all(value in official for value in unused.values()))

toolbin = ROOT / ".platformio/packages/toolchain-gccarmnoneeabi/bin"
nm = toolbin / "arm-none-eabi-nm.exe"
objdump = toolbin / "arm-none-eabi-objdump.exe"
build = REPO / ".pio/build/kraken_v11_hybrid"
elf = build / "firmware.elf"
binary = build / "firmware.bin"
check("Hybrid ELF and BIN exist", elf.exists() and binary.exists())
symbols = subprocess.check_output([str(nm), str(elf)], text=True)
for symbol in ["board_init", "plasma_init", "TMC5160_Init", "st2_motor_init", "tmc_spi_init", "stepperOutputStep"]:
    check("ELF links " + symbol, re.search(r"\b" + symbol + r"$", symbols, re.M))
sections = subprocess.check_output([str(objdump), "-h", str(elf)], text=True)
vector = re.search(r"\.isr_vector\s+[0-9a-f]+\s+([0-9a-f]+)", sections)
check("Vector begins after 128KiB bootloader", vector and int(vector[1], 16) == 0x08020000)
check("BIN stays below NVS sector at 0x080E0000", binary.stat().st_size <= 0xC0000)

report = {
    "status": "STATIC_AND_COMPILE_CHECKS_PASSED_NOT_BENCH_TESTED",
    "checks": checks,
    "pin_allocation": physical,
    "exti_lines": exti,
    "binary": str(binary.relative_to(ROOT)),
    "binary_bytes": binary.stat().st_size,
    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "explicitly_not_tested": ["MCU boot", "SPI communication and RMS current", "physical direction and enable polarity",
                              "USB enumeration", "Y auto-squaring", "pulse timing", "live THC response",
                              "E-stop hardware chain", "EMI immunity", "VFD/torch interfaces"]
}
(ROOT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"passed_checks": len(checks), "binary_bytes": binary.stat().st_size,
                  "binary_sha256": report["binary_sha256"]}, indent=2))
