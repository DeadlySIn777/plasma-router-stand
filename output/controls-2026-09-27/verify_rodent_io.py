"""GM1 BTT Rodent I/O allocation: record it and check it against the board and the draft map.

Writes rodent-io.json. The board facts come from BTT's Rodent manual (v1.03) and
V1.0.2 schematic and from grblHAL's btt_rodent_map.h; each fact names its source.
The checks are bookkeeping (one function per pin, input-only pins used as
inputs, map and table agree). Nothing here has been wired, compiled or flashed.
"""
from pathlib import Path
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
MAP = OUT / 'gm1_rodent_map.h'

SOURCES = {
    'BTT-MANUAL': 'BIGTREETECH Rodent V1.x User Manual, revision v1.03 (11 Aug 2025): feature list, V1.0 and V1.1 pin diagrams, '
                  'interface pages. https://github.com/bigtreetech/Rodent',
    'BTT-SCH': 'BIGTREETECH Rodent V1.0.2 schematic (FluidNC, 14 Oct 2024), sheet 2 (ESP32, endstops, probe, spindle headers, '
               'V-MOS, I2C) and sheet 3 (RS485, 0-10 V). https://github.com/bigtreetech/Rodent/tree/master/Hardware',
    'GRBLHAL-MAP': 'grblHAL ESP32 main/boards/btt_rodent_map.h. https://github.com/grblHAL/ESP32/blob/master/main/boards/btt_rodent_map.h',
    'GRBLHAL-ESP32': 'grblHAL ESP32 main/CMakeLists.txt, my_machine.h, driver.c and driver.h (plugin list, BOARD_BTT_RODENT '
                     '"untested", PROBE2/TOOLSETTER, MCP3221/MCP23017 options). https://github.com/grblHAL/ESP32',
    'GRBLHAL-MCP23017': 'grblHAL Plugins_misc mcp23017.c (2026): 8 in + 8 out, 16 out or 16 in; input interrupts need an '
                        'I2C strobe interrupt pin. https://github.com/grblHAL/Plugins_misc/blob/master/mcp23017.c',
    'GRBLHAL-PLASMA': 'grblHAL plasma plugin README ($350-$369), copy at output/release-review/grblHAL_Plugin_plasma_README.md',
}

FACTS = [
    ('Power input 24-56 V DC at 10 A through one VCC terminal. The only other supply is the USB jumper, which is for flashing '
     'with no external power. Removing VCC therefore restarts the controller.', 'BTT-MANUAL p4, p6-7'),
    ('Four onboard TMC2160 drivers. V1.1 marks RSENSE 75 mOhm; BTT\'s rodent.yaml uses 0.022, so set driver current from the '
     'actual board\'s resistor.', 'BTT-MANUAL p4, p7'),
    ('Five opto-isolated endstop inputs and one opto-isolated probe input. SW_VCC and VProbe jumpers select 5 V, 12 V or VCC; '
     'VCC is prohibited above 24 V, so a 48 V board uses 12 V.', 'BTT-MANUAL p4, p8-11'),
    ('Endstop GPIOs: X-MAX 35, Y-MAX 34, Z-MAX 33, E0-MAX 32, E1-MAX 39 on V1.1 and 37 on V1.0.', 'BTT-MANUAL p6-7; BTT-SCH sheet 2 (SW5 = GPIO37)'),
    ('Endstop circuit: EL357N LED fed from SW_VCC through 1 kOhm 0.6 W; a contact between signal (pin 1) and GND (pin 2) lights it; '
     'the transistor pulls the GPIO low through 1 kOhm against a 10 kOhm pull-up.', 'BTT-SCH sheet 2'),
    ('Probe circuit: pin 3 VProbe through a 1 A PTC, pin 2 GND, pin 1 signal through 1 kOhm to an EL357N LED; J44 adds a 10 kOhm pull-up '
     '(NPN mode). The transistor is an emitter follower into GPIO36 with 1 kOhm to GND, so LED on reads HIGH.', 'BTT-SCH sheet 2'),
    ('Spindle headers CN51/CN52/CN53: pin 1 +5 V through 100 Ohm, pin 2 GND, pin 3 to GPIO25/GPIO15/GPIO14 through 100 Ohm, with '
     '0.1 uF from pin 3 to GND. There is no level shifting, so they take 3.3 V logic only.', 'BTT-SCH sheet 2; BTT-MANUAL p7'),
    ('GPIO15 is also RS485 TX (transceiver DI) and GPIO14 is RS485 DE/RE, with a 10 kOhm pull-down. The RS485 pair has a fixed '
     '120 Ohm terminator. The grblHAL Modbus map uses both pins.', 'BTT-SCH sheets 2-3; GRBLHAL-MAP'),
    ('SP-PWM: GPIO13 (10 kOhm pull-down) through a 10 kOhm / 0.22 uF filter to an LM358 on 12 V. Gain is set by the VR20K pot; '
     'the output passes 1 kOhm to J47 "0_10V_Out". It is not isolated.', 'BTT-SCH sheet 3; BTT-MANUAL p14-15'),
    ('V-MOS outputs: low-side MOSFETs on GPIO12 (HB), GPIO2 (HE1) and GPIO4 (HE0), each with a 100 kOhm gate pull-down, '
     'supplied from a separate 12-36 V V-MOS input.', 'BTT-MANUAL p4, p13; BTT-SCH sheet 2'),
    ('OLED header: GPIO27 SDA, GPIO26 SCL, GND and +5 V. The board\'s I2C pull-ups are 10 kOhm to +5 V.', 'BTT-SCH sheet 2; BTT-MANUAL p7'),
    ('grblHAL map: CONTROL_ENABLE 0 (no E-stop, feed-hold, cycle-start or door input); probe on AUXINPUT0 GPIO36; spindle enable GPIO25, '
     'PWM GPIO13, direction GPIO15 only without Modbus; flood GPIO2, mist GPIO4. It does not use GPIO39/37 or GPIO12.', 'GRBLHAL-MAP'),
    ('The grblHAL ESP32 build lists no plasma plugin source. It does carry the MCP3221 ADC and MCP23017 expander plugins, and the '
     'Rodent is marked "untested".', 'GRBLHAL-ESP32'),
    ('The MCP23017 plugin reports input changes by interrupt only through an I2C strobe pin, which the Rodent does not have. Its '
     'inputs are therefore polled status, not real-time signals.', 'GRBLHAL-MCP23017'),
    ('The plasma plugin needs a digital arc-OK port ($367). Voltage-controlled THC (mode 1) also needs an analog arc-voltage port ($366).',
     'GRBLHAL-PLASMA'),
]

INPUT_ONLY = {34, 35, 36, 37, 38, 39}
STRAPPING = {0: 'boot mode: must be high at reset', 2: 'must be low/floating to enter download mode',
             5: 'SDIO timing', 12: 'flash voltage: must be low at reset (100 kOhm gate pull-down holds it)',
             15: 'boot log / SDIO timing; either level boots normally'}

# One row per pin function. rt = real-time signal handled by the ESP32 itself.
ALLOCATION = [
    dict(signal='X home / limit', connector='X-MAX', gpio=35, direction='in', rt=True, map_define='X_LIMIT_PIN',
         wiring='NC switch between pin 1 (signal) and pin 2 (GND); SW_VCC jumper 12 V.', healthy='closed: GPIO low; trip or open wire: high ($5 inverts)'),
    dict(signal='Y1 home / limit', connector='Y-MAX', gpio=34, direction='in', rt=True, map_define='Y_LIMIT_PIN',
         wiring='As X.', healthy='As X'),
    dict(signal='Y2 home / limit (ganged Y, auto-squaring)', connector='E0-MAX', gpio=32, direction='in', rt=True, map_define='M3_LIMIT_PIN',
         wiring='As X.', healthy='As X'),
    dict(signal='Z home / limit', connector='Z-MAX', gpio=33, direction='in', rt=True, map_define='Z_LIMIT_PIN',
         wiring='As X. M14: the Z top switch has a second, NO, contact (or a second switch beside it) wired into the dock motor '
                'feed in the cabinet (LS_ZTOP 13-14); it is not a Rodent input.', healthy='As X'),
    dict(signal='Plasma float (probe)', connector='Probe', gpio=36, direction='in', rt=True, map_define='AUXINPUT0_PIN',
         wiring='Rev I U_PROBE PhotoMOS output (pins 3/4) between probe pin 3 (VProbe, jumper 12 V) and pin 1 (signal). J44 not fitted. '
                'Router Z zero stays manual, as in Rev I, so no router probe shares this input.',
         healthy='float seated: PhotoMOS closed, LED on, GPIO36 high; trip, open wire or lost field supply: low ($6 so low = triggered)'),
    dict(signal='GM1 door input: tool requested but not armed', connector='E1-MAX', gpio=39, v10_gpio=37, direction='in', rt=True,
         map_define='AUXINPUT1_PIN',
         wiring='Dry contacts K_REQ_A 41-42 (NC) in parallel with K_RUN_ARM 53-54 (NO), between pin 1 and pin 2. They carry the 12 V '
                'SW_VCC loop, about 11 mA.',
         healthy='closed: GPIO low. Open only while the Rodent requests a tool that is not armed; grblHAL SAFETY_DOOR then feed-holds '
                 'and stops the spindle ($14 so high = open).'),
    dict(signal='Arc OK', connector='Sp-Direction (CN52)', gpio=15, direction='in', rt=True, map_define='AUXINPUT2_PIN',
         wiring='Dry output of an isolated DC current switch on the work lead, between pin 3 and pin 2. 4.7 kOhm pull-up to 3.3 V on the '
                'interface board. The header is 3.3 V only: never bring the header +5 V or field 24 V to pin 3.',
         healthy='arc on: closed, GPIO low (plasma $367 port, invert as needed)'),
    dict(signal='THCAD-300 frequency (arc voltage)', connector='Sp-Feedback (CN53)', gpio=14, direction='in', rt=True, map_define='THCAD_PIN',
         wiring='THCAD output through an SN74LVC1G17 on 3.3 V (interface board) into pin 3. The pin 3 capacitor is 0.1 uF, so use the '
                'THCAD /64 or /128 divider and check for flat tops on both half-cycles with a scope.',
         healthy='frequency rises with arc voltage; the new ESP32 capture driver turns it into the analog port for plasma $366'),
    dict(signal='Run request (spindle or torch)', connector='Sp-Enable (CN51)', gpio=25, direction='out', rt=True, map_define='AUXOUTPUT0_PIN',
         wiring='Pin 3 into Rev I\'s run interface (10 kOhm pull-down, SN74LVC1G17 on 3.3 V, 154 Ohm, AQY212GS U_RUN). The U_RUN output '
                'is IF_RUN:13-14 and drives K_REQ_A and K_REQ_B.',
         healthy='high: request. Low during reset and boot, and whenever the Rodent is unpowered.'),
    dict(signal='Spindle speed', connector='SP-PWM (J47)', gpio=13, direction='out', rt=False, map_define='AUXOUTPUT1_PIN',
         wiring='J47 0-10 V output into an isolated 0-10 V signal conditioner, then the VFD analog input. Set $33 = 5000 Hz, because the '
                'onboard 10 kOhm / 0.22 uF filter ripples at low PWM frequencies. Trim VR20K for 10.0 V at 100 %. '
                'Rev I\'s C41S needs a raw PWM pin, which the Rodent does not have.',
         healthy='speed only; the VFD runs only with its FWD terminal closed by the GM1 panel'),
    dict(signal='Router mist solenoid', connector='V-MOS HE0', gpio=4, direction='out', rt=False, map_define='AUXOUTPUT3_PIN',
         wiring='24 V solenoid on the V-MOS output. Feed V-MOS input from a controller-side 48-to-24 V DC-DC after the E-stop '
                'contactors, never from the field 24 V, so mist also stops at every E-stop.', healthy='M7 on, M9 off'),
    dict(signal='Spindle direction (K_DIR coil)', connector='V-MOS HE1', gpio=2, direction='out', rt=False, map_define='AUXOUTPUT2_PIN',
         wiring='24 V coil of the force-guided K_DIR (G7SA-2A2B) on the V-MOS output, fed like the mist from the 48-to-24 V DC-DC after '
                'the E-stop contactors. grblHAL SPINDLE_DIRECTION_PIN: M4 energizes K_DIR, which turns the VFD run command from FWD to '
                'REV (controls M12). The RapidChange tool changer unloads tools in reverse.',
         healthy='M3: off (FWD). M4: on (REV). Set before the run request; K_DIR 23-24 reports it on MCP23017 GPA7.'),
    dict(signal='Status expander MCP23017', connector='OLED header', gpio=(27, 26), direction='i2c', rt=False, map_define=('I2C_SDA', 'I2C_SCL'),
         wiring='MCP23017 on +5 V (the board pull-ups are to +5 V). GPA0-3 read dry contacts K_READY 13-14, K_PERMIT 33-34, '
                'K_RDY_R 21-24 and K_RDY_P 21-24, and GPA7 K_DIR 23-24, each with a 470 Ohm pull-up to 5 V (about 10 mA wetting '
                'current). Tool changer (Rev L, controls M13): GPA4 dock deployed and GPA5 dock parked (M8 PNP sensors through '
                'optocouplers), GPA6 reserved for the RapidChange IR check; GPB0 dock run and GPB1 dock direction (ULN2803A to '
                'K_DOCK_RUN and K_DOCK_DIR), GPB2 reserved for the magazine cover.',
         healthy='polled: operator status, and the tool-change macro (M64/M65 outputs, M66 waits on inputs); no real-time use'),
]

NOT_USED = [
    (12, 'V-MOS HB (strapping pin; left unused)'),
    (16, 'RS485 RX: RS485 is not used on GM1'),
    (0, 'SD card CS (SD card kept)'),
]


def parse_map():
    defines = {}
    for line in MAP.read_text(encoding='utf-8').splitlines():
        m = re.match(r'#define\s+(\w+)\s+GPIO_NUM_(\d+)', line.strip())
        if m:
            defines[m.group(1)] = int(m.group(2))
    return defines


def main():
    checks = []

    def check(name, ok, **ev):
        checks.append({'check': name, 'passed': bool(ok), **ev})
        assert ok, (name, ev)

    defines = parse_map()
    pins = []
    for row in ALLOCATION:
        gp = row['gpio'] if isinstance(row['gpio'], tuple) else (row['gpio'],)
        md = row['map_define'] if isinstance(row['map_define'], tuple) else (row['map_define'],)
        for g, d in zip(gp, md):
            pins.append(g)
            check(f'Map agrees with the table: {d}', defines.get(d) == g, table=g, map=defines.get(d))
        if row['direction'] == 'out':
            check(f'Output not on an input-only pin: {row["signal"]}', not set(gp) & INPUT_ONLY)
    check('Each GPIO has one function', len(pins) == len(set(pins)), pins=sorted(pins))
    rt_inputs = [r['signal'] for r in ALLOCATION if r['rt'] and r['direction'] == 'in']
    check('All eight real-time inputs are allocated (four limits, probe, door, arc OK, THCAD)', len(rt_inputs) == 8, inputs=rt_inputs)
    map_text = MAP.read_text(encoding='utf-8')
    check('The map refuses to build with Modbus enabled', '#if MODBUS_ENABLE' in map_text and '#error' in map_text)
    check('No map pin is also listed as unused', not {g for g, _ in NOT_USED} & set(pins))
    strapping_used = {g: STRAPPING[g] for g in pins if g in STRAPPING}
    check('Strapping pins used only where their reset level is safe', set(strapping_used) <= {2, 15}, used=strapping_used)
    check('Spindle direction output exists for M4 (RapidChange unload) on V-MOS HE1',
          '#define SPINDLE_DIRECTION_PIN   AUXOUTPUT2_PIN' in map_text and defines.get('AUXOUTPUT2_PIN') == 2)
    check('No flood coolant is mapped onto the direction output', 'COOLANT_FLOOD_PIN' not in map_text)
    doc = {
        'title': 'GM1 BTT Rodent I/O allocation',
        'status': 'Allocation from BTT and grblHAL primary sources. Not wired, compiled or flashed. Confirm the board version: '
                  'V1.1 puts E1-MAX on GPIO39, V1.0 on GPIO37.',
        'sources': SOURCES,
        'board_facts': [{'fact': f, 'source': s} for f, s in FACTS],
        'demand_vs_supply': {
            'real_time_inputs_needed': 8,
            'why_not_nine': 'The E-stop needs no controller input: the safety relay removes the Rodent\'s 48 V, so the board '
                            'restarts, and grblHAL requires homing after power-up.',
            'opto_inputs_on_board': 6,
            'header_gpios_freed_by_dropping_rs485': [14, 15],
            'cost_of_dropping_rs485': 'No spindle-speed or fault feedback from the VFD. Speed goes by isolated 0-10 V; run goes by the '
                                      'FWD terminal, so no serial command can start the spindle (review major finding).'},
        'allocation': ALLOCATION,
        'unused': [{'gpio': g, 'note': n} for g, n in NOT_USED],
        'strapping_pins_used': strapping_used,
        'side_effects': [
            'The RS485 transceiver stays on GPIO14/15. While the THCAD signal holds GPIO14 high, the transceiver drives its 120 Ohm '
            'terminator: about 10 mA average extra on the 3.3 V rail, and edges on the unused RS485 terminal. Leave that terminal '
            'unconnected. Check board temperature and noise at commissioning. Lifting R8 (180 Ohm, DE/RE) removes the effect; it is '
            'a board modification.',
            'The board I2C pull-ups go to +5 V, so the ESP32 SDA/SCL pins see 5 V through 10 kOhm (BTT design). The MCP23017 runs on '
            '+5 V to match.'],
        'firmware_work': [
            'Board map: gm1_rodent_map.h (draft, not compiled).',
            'Add the plasma plugin to the ESP32 CMakeLists.txt and set PLASMA_ENABLE.',
            'New ESP32 THCAD driver: MCPWM capture (or PCNT with a gate timer) on GPIO14. Convert period to voltage with $361/$362 '
            'and present it as an analog aux port for $366, following the unfinished thcad2.c pattern for RP2040/STM32F4.',
            'MCP23017_ENABLE 1 (8 in, 8 out) for the status inputs and the tool-changer I/O; expose its pins as aux ports for '
            'M62-M66 so the RapidChange macros can run the dock and wait on its sensors.',
            'Spindle direction on GPIO2 (V-MOS HE1): build with SPINDLE_DIR in DRIVER_SPINDLE_ENABLE.',
            'RapidChange grblHAL macros: set the pocket coordinates, and approach the pockets from the rear stop with the head at '
            'X975 while the dock moves (Rev L), never from the front with the dock out.',
            'Settings: $5, $6 and $14 input polarity per the table; homing required after power-up; $33 = 5000; driver current '
            'from the actual sense resistor.',
            'Bench tests before any cutter connection: signal generator on CN53, arc-OK and door inputs toggled by hand, probe '
            'trip and open-wire, and the E-stop restart.'],
        'owner_inputs': [
            'Rodent board version (V1.0 or V1.1).',
            'VFD model: FWD/COM input type, analog input range and impedance, and whether it has STO.',
            'CUT-50 start circuit and a current switch for arc OK sized to its work lead.',
            'Confirm the THC route: firmware on the Rodent (this plan) rather than an external box, as recorded on 25 September.']}
    doc['checks'] = checks
    doc['result'] = 'PASS' if all(c['passed'] for c in checks) else 'FAIL'
    doc['source_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__), MAP)}
    (OUT / 'rodent-io.json').write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8')
    print(doc['result'], len(checks), 'checks')


if __name__ == '__main__':
    main()
