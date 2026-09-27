"""Check GM1 Rev K from fresh source CAD: router poses, plasma poses, the hoist path and the water fixes.

Router: the eight X/Y/Z travel corners and the centre, with the bed module, the
parked plasma head and every Rev K addition in place.
Plasma: the same nine poses with the module out, the router tool stored and the
Rev I head, drop bracket and the owner's torch (seller dimensions) on the Z adapter,
plus three plasma-only poses:
  - torch over slat 8 at the bottom of Z: the tip must reach below the slat top by
    no more than the 6 mm float travel (the only contact accepted in this check);
  - the level-sensor band (Y558..765) at the plasma limit X955, bottom of Z: must clear;
  - the level-sensor band at full X (975), top of Z: must clear.
Hoist: Rev J's sampled module-and-sling path (revj_handling_check.Checker), run
against the Rev K fixed parts at three hook heights.
This is a sampled static interference check, not a motion, stiffness or cut test.
"""
from pathlib import Path
import copy
import hashlib
import itertools
import json
import os
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / 'RevE-ENGINEERING'
for path in (str(LEGACY), str(HERE)):
    if path not in sys.path:
        sys.path.insert(0, path)

OUT = HERE.parent / 'RevK-CAD' / 'revk-checks.json'
CORNERS = list(itertools.product((275.0, 1275.0), (175.0, 975.0), (0.0, 100.0))) + [(775.0, 575.0, 50.0)]
TORCH_Y_OFFSET = 201.4          # torch axis Y = gantry Y - 201.4 (adapter face 108.1 + bracket 12.7 + clamp axis 80.6)
SLAT_8_CENTRE_Y = 571.5
PLASMA_EXTRA = [(SLAT_8_CENTRE_Y + TORCH_Y_OFFSET, 575.0, 0.0, 'torch over slat 8, bottom of Z'),
                (660.0 + TORCH_Y_OFFSET, 955.0, 0.0, 'level-sensor band at the plasma limit X955, bottom of Z'),
                (660.0 + TORCH_Y_OFFSET, 975.0, 100.0, 'level-sensor band at full X, top of Z')]
SLAT_TOP_Z, FLOAT_TRAVEL = 850.0, 6.0


def clone(source):
    from cad_helpers import Model
    m = Model()
    m.allowed_intersections = source.allowed_intersections.copy()
    m.holds = list(source.holds)
    for p in source.parts:
        q = copy.copy(p)
        q.notes = list(p.notes)
        q.flat = copy.deepcopy(p.flat)
        m.parts.append(q)
    return m


def solids_ok(model):
    bad = []
    for p in model.parts:
        if not p.local.isValid() or len(p.local.Solids()) != 1 or p.local.Volume() <= 0:
            bad.append(p.id)
        elif abs(p.shape.Volume() - p.local.Volume()) > max(.05, p.shape.Volume() * 1e-7):
            bad.append(p.id + ' (local/world volume)')
    return bad


def classify(model, clashes):
    """Accept only the torch tip dipping into a slat top by at most the float travel."""
    from cad_helpers import bbox
    reach, left = [], []
    for c in clashes:
        pair = {c['a'], c['b']}
        slat = next((i for i in pair if i.startswith('WP_SLAT_')), None)
        if 'K_TORCH_PT31' in pair and slat:
            common = model.find('K_TORCH_PT31').shape.intersect(model.find(slat).shape)
            b = bbox(common)
            depth = SLAT_TOP_Z - b[2]
            if b[5] <= SLAT_TOP_Z + 1e-6 and depth <= FLOAT_TRAVEL - .5:
                reach.append({**c, 'slat': slat, 'tip_below_slat_top_mm': round(depth, 3)})
                continue
        left.append(c)
    return reach, left


def main():
    from cad_helpers import validate
    import build_revk
    import build_revj as rev_j
    import plasma_drop
    import revj_handling_check as hoist

    start = time.monotonic()
    before = build_revk.source_hashes()
    report = {'scope': __doc__.strip(), 'revision': 'GM1 Rev K working design', 'status': 'RUNNING'}
    fixed, details = build_revk.build_model(with_motion=False)
    report['fixed_part_count'] = len(fixed.parts)
    router_rows, plasma_rows, reach_rows = [], [], []
    inventory = {}
    for gy, hx, z in CORNERS:
        m = clone(fixed)
        rev_j.add_motion(m, gantry_y=gy, head_x=hx, z_lift=z)
        r = validate(m)
        row = {'gantry_y': gy, 'head_x': hx, 'z_lift': z, 'parts': r['part_count'],
               'unresolved': r['unresolved_intersections'], 'invalid_local': solids_ok(m)}
        row['passed'] = not row['unresolved'] and not row['invalid_local']
        ids = [p.id for p in m.parts]
        inventory.setdefault('router', ids)
        row['inventory_stable'] = ids == inventory['router']
        router_rows.append(row)
        print('router', gy, hx, z, 'clashes', len(row['unresolved']), 'invalid', len(row['invalid_local']), flush=True)
    for gy, hx, z, *label in [c + ('corner or centre',) for c in CORNERS] + PLASMA_EXTRA:
        m = clone(fixed)
        rev_j.add_motion(m, gantry_y=gy, head_x=hx, z_lift=z)
        p, head = plasma_drop.plasma_head_model(rev_j.plasma_layout(m))
        r = validate(p)
        reach, left = classify(p, r['unresolved_intersections'])
        row = {'gantry_y': round(gy, 3), 'head_x': hx, 'z_lift': z, 'label': label[0], 'parts': r['part_count'],
               'tip_z_mm': head['tip_z_mm'], 'torch_axis_xy_mm': head['torch_axis_xy_mm'],
               'reach_contacts': reach, 'unresolved': left, 'invalid_local': solids_ok(p)}
        row['passed'] = not left and not row['invalid_local']
        ids = [q.id for q in p.parts]
        inventory.setdefault('plasma', ids)
        row['inventory_stable'] = ids == inventory['plasma']
        plasma_rows.append(row)
        reach_rows += reach
        print('plasma', round(gy, 1), hx, z, label[0], 'tip', head['tip_z_mm'], 'reach', len(reach), 'clashes', len(left), flush=True)
    model, details_m = build_revk.build_model(with_motion=True)
    hoist_cases = [hoist.Checker(model, details_m, rise).run() for rise in hoist.HOOK_RISES]
    water = details['revk_water']
    service = details['revk_service']['suction_strainer']['rev_k_route']
    cabinet = details['revk_cabinet']
    screen_gap = model.find('K_DRAIN_SCREEN').shape.distance(model.find('WP_DRAIN_NECK').shape)
    import revk_water
    tank_gap = revk_water.TANK_DRAIN['z'] - revk_water.TANK_DRAIN['hole'] / 2 - revk_water.WALL['origin'][2]
    checks = {
        'refill air gap >= 31.6 mm': water['refill_spout']['air_gap_mm'] >= 31.6,
        'drain screen clear of the drain neck wall': screen_gap > 0,
        'manual tank drain hole bottom within 5 mm of the tank floor': 0 < tank_gap <= 5,
        'suction line only rises': service['rises_monotonically'],
        'cabinet has 24 or more cable entries': cabinet['entry_count'] >= 24,
        'drip lip clears the box top': cabinet['door_drip_lip']['clearance_mm'] >= 2,
        'every router pose clear': all(r['passed'] and r['inventory_stable'] for r in router_rows),
        'every plasma pose clear': all(r['passed'] and r['inventory_stable'] for r in plasma_rows),
        'torch reaches below the slat top within the float travel': bool(reach_rows) and all(
            0 < c['tip_below_slat_top_mm'] <= FLOAT_TRAVEL - .5 for c in reach_rows),
        'hoist path clear at every hook height': all(c['result'].startswith('PASS') for c in hoist_cases)}
    after = build_revk.source_hashes()
    report.update(status='PASS' if all(checks.values()) and before == after else 'FAIL', checks=checks,
                  router_poses=router_rows, plasma_poses=plasma_rows, hoist_cases=hoist_cases,
                  drain_screen_gap_to_neck_mm=round(screen_gap, 3), tank_drain_hole_above_floor_mm=round(tank_gap, 3),
                  sources_unchanged_during_run=before == after,
                  source_sha256=before, elapsed_seconds=round(time.monotonic() - start, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
    print('REV K CHECKS', report['status'], json.dumps(checks), flush=True)
    return 0 if report['status'] == 'PASS' else 2


if __name__ == '__main__':
    try:
        code = main()
    except Exception:
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
