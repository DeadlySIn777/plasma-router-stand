"""Check GM1 Rev L's rotary variant from fresh source CAD: the rotary on the front of the frame and a tube in its chuck.

Tube (module and dock out, plasma head on the Z): a Ø60 x 1200 tube along Y at X575 from the chuck at the back (Y1383 in the
jaws) forward to Y183, torch axis on the tube at Y200, Y575 and Y1073.6 (the torch's Y range is 73.6..1073.6): the tip on the
tube top (touch-off) may meet nothing but the tube, and 4 mm over it (cut height) nothing. At Z0 the torch beside the tube (X465 and X685, Y575: 110 mm off the axis, the head being 117 mm
wide): clear. A Ø100 tube at the cut height:
clear, and its touch-off within the Z stroke. A 1500 mm tube runs out of the front over the low front cross tubes: clear.
Plasma: Rev L's nine corner poses and Rev K's three plasma poses with the rotary fitted, no tube: clear.
Router: the nine corner poses with the module in and the dock parked, plus the dock deployed at the rear stop, with the
rotary fitted: clear. The chuck face stays at least 10 mm behind the bed module's rear edge (and 15 behind the BT30 dock's parked tray).
Hoist: Rev J's sampled module-and-sling path (70 mm up, then out of the front window) with the dock deployed and the rotary
fitted at the back, at three hook heights: clear.
Heights: the biggest tube's underside stays 50 mm over the slats and 60 mm over the pan walls.
This is a sampled static interference check, not a motion, cut or stiffness test.
"""
from pathlib import Path
import itertools
import json
import os
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
REVL = HERE.parent / 'RevL-ENGINEERING'
REVK = HERE.parent / 'RevK-ENGINEERING'
LEGACY = HERE.parent / 'RevE-ENGINEERING'
for path in (str(LEGACY), str(REVK), str(REVL), str(HERE)):
    if path not in sys.path:
        sys.path.insert(0, path)

OUT = HERE.parent / 'RevL-ROTARY-CAD' / 'revl-rotary-checks.json'
Z_TOP = 300.0
CORNERS = list(itertools.product((275.0, 1275.0), (175.0, 975.0), (0.0, Z_TOP))) + [(775.0, 575.0, 150.0)]
TORCH_Y_OFFSET = 201.4
TUBE_TORCH_Y = (200.0, 575.0, 1073.6)     # near the free end, mid-tube, nearest the chuck
BESIDE_X = (465.0, 685.0)    # 110 mm either side of the tube axis: the plasma head is 117 mm wide
STANDOFF = 4.0
BIG_D = 100.0
LONG_L = 1500.0
FORWARD_L = 1520.0
SLAT_TOP = 850.0
PAN_WALL_TOP = 835.0
TORCH = 'K_TORCH_PT31'


def main():
    from cad_helpers import bbox, validate
    import build_revj as rev_j
    import build_revk
    import build_revl
    import build_revl_rotary
    import atc_revl
    import ballast_revl
    import plasma_drop
    import rotary_revl as rotary
    import verify_revk
    import z300
    import revj_handling_check as hoist

    start = time.monotonic()
    before = build_revl_rotary.source_hashes()
    report = {'scope': __doc__.strip(), 'revision': 'GM1 Rev L working design, rotary variant', 'status': 'RUNNING'}
    base, base_details = build_revk.build_model(with_motion=False)
    fill = ballast_revl.apply(base)
    info = rotary.extend_model(base)
    axis_z = info['axis_xz_mm'][1]
    module_rear = max(bbox(p.shape)[4] for p in base.parts if p.id.startswith('MOD_'))
    n_rotary = sum(p.id.startswith(rotary.PREFIX) for p in base.parts)
    report['rev_k_fixed_part_count'] = len(base.parts)

    def pose(travel, gy, hx, z, tube=None):
        m = verify_revk.clone(base)
        t = rotary.add_tube(m, axis_z, *tube)[1] if tube else None
        atc = atc_revl.extend_router_model(m, travel)
        z300.add_motion(m, gantry_y=gy, head_x=hx, z_lift=z)
        return m, atc, t

    def plasma(m, allowed=()):
        p, head = plasma_drop.plasma_head_model(rev_j.plasma_layout(m))
        r = validate(p)
        reach, left = verify_revk.classify(p, r['unresolved_intersections'])
        expected = [c for c in left if frozenset((c['a'], c['b'])) in allowed]
        left = [c for c in left if frozenset((c['a'], c['b'])) not in allowed]
        return p, head, r, reach, expected, left

    # the tip at z 0, from the model
    m0, _, _ = pose(atc_revl.TRAVEL, TUBE_TORCH_Y[1] + TORCH_Y_OFFSET, rotary.AXIS_X, 0.0)
    _, head0, _, _, _, _ = plasma(m0)
    tip0 = head0['tip_z_mm']
    touch = {d: round(axis_z + d / 2 - tip0, 3) for d in (rotary.TUBE_D, BIG_D)}
    print('tip at z0', tip0, 'axis', axis_z, 'touch z_lift', touch, flush=True)

    tube_rows = []
    allowed = {frozenset((TORCH, rotary.PREFIX + 'TUBE_ALLOCATION'))}
    for ty, (z, label) in itertools.product(TUBE_TORCH_Y, ((touch[rotary.TUBE_D], 'tip on the tube top'),
                                                           (touch[rotary.TUBE_D] + STANDOFF, 'cut height, 4 mm over the tube'))):
        m, _, t = pose(atc_revl.TRAVEL, ty + TORCH_Y_OFFSET, rotary.AXIS_X, z, (rotary.TUBE_L, rotary.TUBE_D))
        p, head, r, reach, expected, left = plasma(m, allowed if z == touch[rotary.TUBE_D] else set())
        row = {'torch_y': ty, 'gantry_y': round(ty + TORCH_Y_OFFSET, 3), 'head_x': rotary.AXIS_X, 'z_lift': z, 'label': label,
               'tip_z_mm': head['tip_z_mm'], 'tube_top_z_mm': t['top_z_mm'], 'tip_over_tube_mm': round(head['tip_z_mm'] - t['top_z_mm'], 3),
               'parts': r['part_count'], 'tube_contacts': expected, 'slat_contacts': reach, 'unresolved': left,
               'invalid_local': verify_revk.solids_ok(p)}
        row['passed'] = not left and not reach and not row['invalid_local'] and abs(row['tip_over_tube_mm'] - (0.0 if z == touch[rotary.TUBE_D] else STANDOFF)) < 1e-6
        tube_rows.append(row)
        print('tube', ty, label, 'tip over tube', row['tip_over_tube_mm'], 'clashes', len(left), flush=True)
    beside_rows = []
    for bx in BESIDE_X:
        m, _, t = pose(atc_revl.TRAVEL, TUBE_TORCH_Y[1] + TORCH_Y_OFFSET, bx, 0.0, (rotary.TUBE_L, rotary.TUBE_D))
        p, head, r, reach, expected, left = plasma(m)
        row = {'head_x': bx, 'gantry_y': round(TUBE_TORCH_Y[1] + TORCH_Y_OFFSET, 3), 'z_lift': 0.0, 'tip_z_mm': head['tip_z_mm'], 'parts': r['part_count'],
               'slat_contacts': reach, 'unresolved': left, 'invalid_local': verify_revk.solids_ok(p)}
        row['passed'] = not left and not row['invalid_local'] and all(0 < c['tip_below_slat_top_mm'] <= verify_revk.FLOAT_TRAVEL - .5 for c in reach)
        beside_rows.append(row)
        print('beside the tube', bx, 'clashes', len(left), 'slat contacts', len(reach), flush=True)
    m, _, t_big = pose(atc_revl.TRAVEL, TUBE_TORCH_Y[1] + TORCH_Y_OFFSET, rotary.AXIS_X, touch[BIG_D] + STANDOFF, (rotary.TUBE_L, BIG_D))
    p, head, r, reach, expected, left = plasma(m)
    big_row = {'tube_d': BIG_D, 'z_lift': touch[BIG_D] + STANDOFF, 'tip_z_mm': head['tip_z_mm'], 'tube_top_z_mm': t_big['top_z_mm'],
               'tube_bottom_z_mm': t_big['bottom_z_mm'], 'parts': r['part_count'], 'unresolved': left, 'slat_contacts': reach,
               'invalid_local': verify_revk.solids_ok(p)}
    big_row['passed'] = not left and not reach and not big_row['invalid_local']
    print('big tube', 'clashes', len(left), flush=True)
    m, _, t_long = pose(atc_revl.TRAVEL, TUBE_TORCH_Y[0] + TORCH_Y_OFFSET, rotary.AXIS_X, touch[rotary.TUBE_D] + STANDOFF, (LONG_L, rotary.TUBE_D))
    p, head, r, reach, expected, left = plasma(m)
    long_row = {'tube_length': LONG_L, 'tube_y_mm': t_long['y_mm'], 'z_lift': touch[rotary.TUBE_D] + STANDOFF, 'parts': r['part_count'],
                'unresolved': left, 'slat_contacts': reach, 'invalid_local': verify_revk.solids_ok(p)}
    long_row['passed'] = not left and not reach and not long_row['invalid_local']
    print('long tube', 'clashes', len(left), flush=True)

    plasma_rows, reach_rows = [], []
    for gy, hx, z, *label in [c + ('corner or centre',) for c in CORNERS] + [tuple(x) for x in build_revl.__dict__.get('PLASMA_EXTRA', [])] + [
            (571.5 + TORCH_Y_OFFSET, 575.0, 0.0, 'torch over slat 8, bottom of Z'),
            (660.0 + TORCH_Y_OFFSET, 955.0, 0.0, 'level-sensor band at the plasma limit X955, bottom of Z'),
            (660.0 + TORCH_Y_OFFSET, 975.0, Z_TOP, 'level-sensor band at full X, top of Z')]:
        m, _, _ = pose(atc_revl.TRAVEL, gy, hx, z)
        p, head, r, reach, expected, left = plasma(m)
        row = {'gantry_y': round(gy, 3), 'head_x': hx, 'z_lift': z, 'label': label[0], 'parts': r['part_count'], 'tip_z_mm': head['tip_z_mm'],
               'reach_contacts': reach, 'unresolved': left, 'invalid_local': verify_revk.solids_ok(p),
               'rotary_parts_present': sum(q.id.startswith(rotary.PREFIX) for q in p.parts)}
        row['passed'] = not left and not row['invalid_local'] and row['rotary_parts_present'] == n_rotary
        plasma_rows.append(row)
        reach_rows += reach
        print('plasma', round(gy, 1), hx, z, label[0], 'tip', head['tip_z_mm'], 'clashes', len(left), flush=True)

    router_rows = []
    for gy, hx, z in CORNERS:
        m, _, _ = pose(atc_revl.TRAVEL, gy, hx, z)
        r = validate(m)
        row = {'gantry_y': gy, 'head_x': hx, 'z_lift': z, 'dock': 'parked', 'parts': r['part_count'], 'unresolved': r['unresolved_intersections'],
               'invalid_local': verify_revk.solids_ok(m)}
        row['passed'] = not row['unresolved'] and not row['invalid_local']
        router_rows.append(row)
        print('router', gy, hx, z, 'clashes', len(row['unresolved']), flush=True)
    m_dep, atc_dep, _ = pose(0.0, 1275.0, 575.0, Z_TOP)
    r = validate(m_dep)
    deployed_row = {'gantry_y': 1275.0, 'head_x': 575.0, 'z_lift': Z_TOP, 'dock': 'deployed', 'parts': r['part_count'],
                    'unresolved': r['unresolved_intersections'], 'invalid_local': verify_revk.solids_ok(m_dep)}
    deployed_row['passed'] = not deployed_row['unresolved'] and not deployed_row['invalid_local']
    print('router, dock deployed', 'clashes', len(deployed_row['unresolved']), flush=True)

    details = dict(base_details)
    details['bed'] = build_revl.module_with_dock(base_details['bed'], atc_dep)
    hoist.FORWARD = FORWARD_L
    hoist_cases = [hoist.Checker(m_dep, details, rise).run() for rise in hoist.HOOK_RISES]

    big_bottom = axis_z - BIG_D / 2
    checks = {
        'Ø60 tube: tip on the tube top at Y100, Y575 and Y1073.6 meets nothing else; 4 mm over it, clear': all(r['passed'] for r in tube_rows),
        'torch at Z0 110 mm either side of the tube (X465 and X685): clear of the tube, tip within the float on a slat': all(r['passed'] for r in beside_rows),
        'Ø100 tube at the cut height: clear, and its touch-off within the Z stroke': big_row['passed'] and touch[BIG_D] + STANDOFF <= Z_TOP,
        '1500 mm tube out of the front over the low front cross tubes, torch at Y200: clear': long_row['passed'],
        'plasma corners and Rev K poses with the rotary fitted, no tube: clear': all(r['passed'] for r in plasma_rows) and all(
            0 < c['tip_below_slat_top_mm'] <= verify_revk.FLOAT_TRAVEL - .5 for c in reach_rows),
        'router corners with the module in and the rotary fitted: clear; dock deployed at the rear stop: clear': all(
            r['passed'] for r in router_rows) and deployed_row['passed'],
        'chuck face at least 10 mm behind the bed module\'s rear edge and 15 mm behind the BT30 dock\'s parked tray (Y1365)': rotary.CHUCK_FACE_Y - module_rear >= 10 and rotary.CHUCK_FACE_Y - 1365.0 >= 15,
        'the shortest tube end the torch can reach is under 320 mm from the jaws': info['shortest_reach_from_jaws_mm'] <= 320,
        'a Ø100 tube stays 50 mm over the slats and 60 mm over the pan walls': big_bottom - SLAT_TOP >= 50 and big_bottom - PAN_WALL_TOP >= 60,
        'hoist path clear at every hook height with the dock deployed and the rotary fitted': all(c['result'].startswith('PASS') for c in hoist_cases)}
    after = build_revl_rotary.source_hashes()
    report.update(status='PASS' if all(checks.values()) and before == after else 'FAIL', checks=checks, rotary=info,
                  torch_tip_at_z0_mm=tip0, touch_z_lift_mm=touch, tube_poses=tube_rows, beside_tube_poses=beside_rows, big_tube_pose=big_row,
                  long_tube_pose=long_row, plasma_poses=plasma_rows, router_poses=router_rows + [deployed_row],
                  module_rear_y_mm=round(module_rear, 3), chuck_clearance_to_module_mm=round(rotary.CHUCK_FACE_Y - module_rear, 3),
                  big_tube_over_slats_mm=round(big_bottom - SLAT_TOP, 3), hoist_forward_mm=FORWARD_L, hoist_cases=hoist_cases,
                  frame_fill_ports=len(fill['ports']), sources_unchanged_during_run=before == after, source_sha256=before,
                  elapsed_seconds=round(time.monotonic() - start, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
    print('REV L ROTARY CHECKS', report['status'], json.dumps(checks), flush=True)
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
