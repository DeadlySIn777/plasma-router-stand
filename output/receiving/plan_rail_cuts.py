"""Plan where to cut each iMetrx HGR20 Y rail (1500 -> 1420 mm) from its measured factory holes.

Reads hgr20-receiving-register.json in this folder and writes rail-cut-plan.json.
A rail with measured holes gets a cut plan; a rail without them is reported as
waiting for measurement, and three plausible factory patterns are planned as
scenarios to show why the cut cannot be fixed before the rails are measured.

Rules for a cut plan, all in mm along the rail from end A:
  * every kept hole centre is at least E_MIN from its new rail end, so the end
    keeps solid rail around the counterbore;
  * no rail end overhangs its last kept hole by more than one pitch (E_MAX = P);
  * a removed hole's counterbore must lie wholly in the offcut, never cut in half
    on the kept rail end (centre at least D/2 + REMOVED_CLEAR from the cut face);
  * among valid cuts, take the one with the largest smallest margin to these
    limits, then the most even end distances, then the most even offcuts.
The saw kerf falls on the offcut side of each marked cut face.
"""
from pathlib import Path
import json, math, sys

HERE = Path(__file__).resolve().parent
REGISTER = HERE / 'hgr20-receiving-register.json'
OUT = HERE / 'rail-cut-plan.json'

E_MIN = 10.0            # hole centre to rail end; D/2 = 4.75 plus about 5 mm of solid rail
REMOVED_CLEAR = 1.0     # removed counterbore edge to kept end face
COUNTERBORE_D = 9.5     # seller table D; replaced by the measured value when present
STEP = 0.5
ROBUST_MARGIN = 2.0     # smallest margin considered robust to marking and measuring error


def hole_centres(m):
    """Hole centres from end A: an explicit list wins, otherwise first hole + pitch x count."""
    if m.get('hole_centres_from_end_A_mm'):
        return sorted(float(h) for h in m['hole_centres_from_end_A_mm'])
    needed = ('first_hole_from_end_A_mm', 'pitch_mm', 'hole_count')
    if all(m.get(k) is not None for k in needed):
        return [m['first_hole_from_end_A_mm'] + i * m['pitch_mm'] for i in range(int(m['hole_count']))]
    return None


def plan(length, holes, target, pitch, cb_d=COUNTERBORE_D, e_min=E_MIN):
    remove = length - target
    if remove < 0:
        raise ValueError(f'rail {length} mm is shorter than the {target} mm target')
    e_max = pitch
    clear = cb_d / 2 + REMOVED_CLEAR
    candidates = []
    for k in range(int(round(remove / STEP)) + 1):
        a = k * STEP
        b = remove - a
        end_face = length - b
        kept = [h for h in holes if a < h < end_face]
        removed = [h for h in holes if not a < h < end_face]
        if len(kept) < 2:
            continue
        e1, e2 = kept[0] - a, end_face - kept[-1]
        margins = [e1 - e_min, e2 - e_min, e_max - e1, e_max - e2]
        margins += [min(abs(h - a), abs(h - end_face)) - clear for h in removed]
        worst = min(margins)
        if worst < 0:
            continue
        candidates.append({'cut_from_end_A_mm': round(a, 2), 'cut_from_end_B_mm': round(b, 2),
                           'end_distance_A_mm': round(e1, 2), 'end_distance_B_mm': round(e2, 2),
                           'kept_holes': len(kept), 'smallest_margin_mm': round(worst, 2)})
    if not candidates:
        return {'status': 'NO VALID CUT', 'reason': 'Every cut position either leaves a hole too near an end, overhangs more than one pitch, or splits a counterbore. Check the measurements; if they are right, discuss a shorter or offset rail with the design owner.'}
    best = max(candidates, key=lambda c: (c['smallest_margin_mm'],
                                          -abs(c['end_distance_A_mm'] - c['end_distance_B_mm']),
                                          -abs(c['cut_from_end_A_mm'] - c['cut_from_end_B_mm'])))
    best = dict(best)
    best['status'] = 'OK' if best['smallest_margin_mm'] >= ROBUST_MARGIN else 'VALID BUT TIGHT: re-measure before cutting'
    best['valid_cut_from_end_A_ranges_mm'] = ranges([c['cut_from_end_A_mm'] for c in candidates])
    return best


def ranges(values):
    out = []
    for v in values:
        if out and abs(v - out[-1][1] - STEP) < 1e-9:
            out[-1][1] = v
        else:
            out.append([v, v])
    return out


def main():
    reg = json.loads(REGISTER.read_text(encoding='utf-8'))
    target = reg['y_rail_target_length_mm']
    results = {'register': REGISTER.name, 'y_rail_target_length_mm': target,
               'rules': {'e_min_mm': E_MIN, 'e_max': 'one measured pitch',
                         'removed_counterbore_clearance_mm': REMOVED_CLEAR,
                         'robust_margin_mm': ROBUST_MARGIN, 'search_step_mm': STEP},
               'rails': [], 'scenarios_before_measurement': []}
    waiting = 0
    for rail in reg['rails']:
        if rail['target_length_mm'] == rail['nominal_length_mm']:
            results['rails'].append({'id': rail['id'], 'use': rail['use'], 'status': 'NO CUT: used at supplied length; measure end distances for transfer drilling'})
            continue
        m = rail['measured']
        holes = hole_centres(m)
        length = m.get('length_mm')
        if not holes or not length:
            waiting += 1
            results['rails'].append({'id': rail['id'], 'use': rail['use'], 'status': 'WAITING FOR MEASUREMENT'})
            continue
        pitch = m.get('pitch_mm') or (holes[-1] - holes[0]) / (len(holes) - 1)
        p = plan(length, holes, rail['target_length_mm'], pitch, m.get('counterbore_diameter_mm') or COUNTERBORE_D)
        results['rails'].append({'id': rail['id'], 'use': rail['use'], 'measured_length_mm': length,
                                 'pitch_used_mm': round(pitch, 3), **p})
    # Plausible factory patterns on a 1500 mm rail: the same cut rule gives different answers.
    for name, first, pitch in (('Pitch 60, symmetric 30 mm ends (common HGR20 pattern)', 30, 60),
                               ('Pitch 40, symmetric 30 mm ends (seller table pitch)', 30, 40),
                               ('Pitch 40, 20 mm at end A (seller table E) and 40 mm at end B', 20, 40)):
        holes = [first + i * pitch for i in range(int((1500 - first) // pitch) + 1) if first + i * pitch < 1500]
        results['scenarios_before_measurement'].append({'scenario': name, **plan(1500, holes, target, pitch)})
    results['status'] = ('WAITING FOR MEASUREMENTS: do not cut the Y rails yet' if waiting
                         else 'PLANNED FROM MEASUREMENTS: mark, re-check against the rail, then cut')
    OUT.write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': results['status'],
                      'scenarios': [(s['scenario'], s.get('cut_from_end_A_mm'), s.get('cut_from_end_B_mm'),
                                     s.get('end_distance_A_mm'), s.get('end_distance_B_mm'), s.get('smallest_margin_mm'))
                                    for s in results['scenarios_before_measurement']]}, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
