"""Check reservations against the committed Kraken map, not live hardware.

Run with any Python 3; no firmware or baseline file is changed.
"""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MAP = ROOT / 'RevE-ENGINEERING/controls/source-overlay/boards/my_machine_map.h'
IDLE = ROOT / 'RevE-ENGINEERING/controls/source-overlay/Src/kraken_board.c'
OFFICIAL = ROOT / 'RevE-ENGINEERING/controls/kraken-official.cfg'
INI = ROOT / 'RevE-ENGINEERING/controls/source-overlay/kraken.ini'
SPEC = HERE / 'pin-reservations.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source = MAP.read_text()
    macros = dict(re.findall(r'^#define\s+(\w+)\s+(\w+)', source, re.M))
    def resolve(value):
        seen = set()
        while value in macros and value not in seen:
            seen.add(value)
            value = macros[value]
        return value
    pins = {}
    for name in macros:
        if name.endswith('_PORT') and name[:-5] + '_PIN' in macros:
            port, number = resolve(name), resolve(name[:-5] + '_PIN')
            if re.fullmatch(r'GPIO[A-K]', port) and number.isdigit():
                pins[name[:-5]] = f'P{port[-1]}{number}'
    used = set(pins.values())
    # Board init also drives disabled-channel enables and chip selects.
    idle = IDLE.read_text()
    for port, expr in re.findall(r'output_high\(GPIO([A-K]),\s*([^;]+)\);', idle):
        used.update(f'P{port}{n}' for n in re.findall(r'GPIO_PIN_(\d+)', expr))
    baseline_inputs = {gpio for name, gpio in pins.items()
                       if name.endswith('_LIMIT') or name.startswith('AUXINPUT')}
    official = OFFICIAL.read_text()
    aliases = dict(re.findall(r'(EXP[12]_\d+)=(P[A-K]\d+)', official))
    spec = json.loads(SPEC.read_text())
    checks = []
    def check(name, ok, detail):
        checks.append({'check': name, 'pass': bool(ok), 'detail': detail})
    assigned = set()
    input_lines = {int(re.search(r'\d+', p)[0]) for p in baseline_inputs}
    for row in spec['reservations']:
        gpio = row['gpio']
        check(row['function'] + ':unused_gpio', gpio not in used and gpio not in assigned,
              {'gpio': gpio, 'baseline_users': [n for n, p in pins.items() if p == gpio]})
        assigned.add(gpio)
        if row['connector'].startswith('EXP'):
            check(row['function'] + ':connector', aliases.get(row['connector']) == gpio,
                  {'connector': row['connector'], 'official_gpio': aliases.get(row['connector'])})
        else:
            check(row['function'] + ':connector',
                  row['connector'] == 'S7_STOP' and gpio == 'PF10'
                  and re.search(r'filament_switch_sensor material_2\]\s*#switch_pin: PF10', official),
                  'Official S7 filament/stop input; actual board DIAG jumper still needs verification')
        if row['kind'] == 'input':
            line = int(re.search(r'\d+', gpio)[0])
            check(row['function'] + ':unique_exti', line not in input_lines,
                  {'exti_line': line, 'already_used': sorted(input_lines)})
            input_lines.add(line)
    ini = INI.read_text()
    check('baseline_reverse_gap_recorded', 'SPINDLE0_ENABLE=SPINDLE_PWM0_NODIR' in ini
          and 'SPINDLE_DIRECTION_PIN' not in macros,
          'Baseline router/hybrid configuration has no direction channel; the reservations do not implement it')
    result = {
        'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL',
        'scope': 'Static connector, GPIO and external-interrupt line reservation only',
        'firmware_compiled': False, 'hardware_tested': False, 'physical_release': False,
        'sources': {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
                    for p in [MAP, IDLE, OFFICIAL, INI, SPEC, Path(__file__)]},
        'baseline_assigned_gpio': sorted(used),
        'checks': checks,
        'unresolved': spec['unresolved']
    }
    (HERE / 'pin-reservation-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"{result['status']}: {sum(c['pass'] for c in checks)}/{len(checks)} static reservation checks; not operating ATC firmware")
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
