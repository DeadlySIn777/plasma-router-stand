"""Rev J water-service check: static states, hatch and washout paths, refill spout.

Rebuilds GM1 Rev J (`build_revj.py`) and repeats the Rev H water-service proof
(output/design-completion-2026-09-26/water/verify_water_completion.py) on it:
closed router and plasma-layout states, the upright hatch service state, the
eight hatch-cover path segments and the two washout-cover segments. The hatch
paths run in the plasma layout, the fullest cabinet state: spindle, clamps and
screws stored, and the six M10 drawdowns in the bolt tray. It also records the
relocated refill spout's air gap and its nearest gaps to the bed module, slats
and pan bearer. Nominal rigid-solid checks only: no hands, brushes, hoses,
gasket behavior or wet test.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import traceback

SOURCE = Path(__file__).resolve().parent
OUT = SOURCE.parent / 'RevJ-CAD' / 'water-service-check.json'


def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCE.glob('*.py'))}


def main():
    from build_revj import build_model, plasma_layout
    from water_completion import HATCHES, LID_TOP, hatch_service_model
    from cad_helpers import bbox, plate, validate
    from sweep_checks import rotation_segment, translation_segment
    import water_revj

    before = hashes()
    start = time.monotonic()
    model, details = build_model()
    plasma = plasma_layout(model)
    report = {'scope': __doc__.strip(), 'revision': details['revision'], 'definition': details['water_completion'],
              'state_checks': {}, 'paths': []}
    for name, state in [('router_closed', model), ('plasma_layout_closed', plasma),
                        ('service_open_plasma_layout', hatch_service_model(plasma))]:
        r = validate(state)
        report['state_checks'][name] = {'count': r['part_count'], 'clashes': r['unresolved_intersections']}
        print(name, r['part_count'], 'clashes', len(r['unresolved_intersections']), flush=True)

    changed = ['WT_LID', 'WP_FLOOR', 'WT_CLEANOUT_NECK']
    flats = []
    for p in model.parts:
        if p.flat and (p.id.startswith(('H_WT_', 'J_REFILL_')) or p.id in changed):
            f = p.flat
            rebuilt = plate(f['outline'], f['thickness_mm'], f['holes'], f['slots'], f['internal'])
            delta = abs(rebuilt.Volume() - p.local.Volume())
            assert delta < 1e-6, (p.id, delta)
            flats.append({'id': p.id, 'volume_delta_mm3': delta})
    report['changed_existing_ids'] = changed
    report['flat_local_consistency'] = flats

    # Hatch covers, one after the other; the first parked cover stays as an
    # obstacle for the second. Their twelve screws are removed first.
    current = {p.id: p.shape for p in plasma.parts
               if not any(p.id.startswith('H_WT_' + h['tag'] + '_BOLT_') for h in HATCHES)}
    for h in HATCHES:
        names = ['H_WT_' + h['tag'] + '_COVER', 'H_WT_' + h['tag'] + '_PULL_TAB']
        moving = {n: current.pop(n) for n in names}
        fixed = current.copy()
        x, y, w, d = h['cover']
        axis = (x, h['park_y'], LID_TOP + 2 + 50)
        route = {'hatch': h['tag'], 'segments': []}

        def trans(label, delta):
            nonlocal moving
            r = translation_segment(moving, fixed, delta)
            route['segments'].append({'name': label, **r})
            moving = {n: s.translate(delta) for n, s in moving.items()}
        trans('lift50', (0, 0, 50))
        trans('move_to_pocket_plane', (0, h['park_y'] - y, 0))
        r = rotation_segment(moving, fixed, axis, 'X', 0, 90, max_step_deg=1)
        route['segments'].append({'name': 'rotate_upright', **r})
        moving = {n: s.rotate(axis, (x + 1, axis[1], axis[2]), 90) for n, s in moving.items()}
        trans('lower_into40mm_pockets', (0, 0, -49))
        current.update(moving)
        report['paths'].append(route)
        print(h['tag'], [(s['name'], s['status'], len(s['candidates'])) for s in route['segments']], flush=True)
    # Empty-tank washout cover, hand-held after its four fastener sets are removed.
    current = {n: s for n, s in current.items() if not n.startswith(('H_WT_WASHOUT_BOLT_', 'H_WT_WASHOUT_WASHER_', 'H_WT_WASHOUT_NUT_'))}
    moving = {'H_WT_WASHOUT_COVER': current.pop('H_WT_WASHOUT_COVER')}
    route = {'hatch': 'EMPTY_TANK_WASHOUT_COVER', 'segments': []}
    for label, delta in [('lower20_after_removing_four_fasteners', (0, 0, -20)), ('withdraw_forward80_handheld', (0, -80, 0))]:
        r = translation_segment(moving, current, delta)
        route['segments'].append({'name': label, **r})
        moving = {n: s.translate(delta) for n, s in moving.items()}
    report['paths'].append(route)
    print('WASHOUT', [(s['name'], s['status'], len(s['candidates'])) for s in route['segments']], flush=True)
    for route in report['paths']:
        for segment in route['segments']:
            b = segment['swept_enclosing_bounds_mm']
            segment['within_chassis_plan_0_1150_0_1450'] = b[0] >= 0 and b[1] >= 0 and b[3] <= 1150 and b[4] <= 1450

    # Refill spout: air gap and the gaps that set its position.
    shapes = {p.id: p.shape for p in model.parts}
    spout = shapes['J_REFILL_MITER_SPOUT']
    sb = bbox(spout)
    outlet_low = min(v.Z for v in spout.Vertices() if abs(v.X - water_revj.HEAD_X) < water_revj.PIPE_OD)
    report['refill_spout'] = {
        'bounds_mm': [round(v, 3) for v in sb],
        'outlet_low_edge_z_mm': round(outlet_low, 3),
        'air_gap_above_pan_rim_mm': round(outlet_low - water_revj.PAN_RIM_Z, 3),
        'nearest_gaps_mm': {other: round(spout.distance(shapes[other]), 2) for other in
                            ('MOD_XM_4', 'MOD_XM_3', 'MOD_STRIP_3', 'WP_SLAT_18', 'WP_SLAT_19', 'PAN_BEARER_3', 'WP_CRADLE_WEB_3_2')},
        'connection_reserve_gap_to_pan_bearer_3_mm': round(shapes['J_REFILL_CONNECTION_RESERVE'].distance(shapes['PAN_BEARER_3']), 2),
        'rear_tool_reach': 'Tool centre travel ends at Y1121.4; the spout starts at Y%.2f.' % sb[1]}
    print('spout', json.dumps(report['refill_spout']), flush=True)

    report['scope_limits'] = ['The twelve hatch screws and four washout fastener sets are removed before the paths; their handling and storage are not proven.',
                              'Nominal rigid path bounds: no hand or brush envelope, manufacturing tolerance, gasket adhesion or wet cleaning test.',
                              'Purchased valve, union and hose-connection blocks are placement reserves only.',
                              'No cabinet door, thermal or wiring design is introduced.']
    after = hashes()
    report['source_sha256'] = before
    report['sources_changed_during_run'] = {n: h for n, h in before.items() if after.get(n) != h}
    report['elapsed_seconds'] = round(time.monotonic() - start, 1)
    gaps = report['refill_spout']['nearest_gaps_mm']
    report['passed'] = (all(not v['clashes'] for v in report['state_checks'].values())
                        and all(s['status'] == 'CLEAR' and s['within_chassis_plan_0_1150_0_1450'] for r in report['paths'] for s in r['segments'])
                        and report['refill_spout']['air_gap_above_pan_rim_mm'] >= 25 and min(gaps.values()) > 0
                        and not report['sources_changed_during_run'])
    report['result'] = 'PASS' if report['passed'] else 'FAIL'
    OUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('RESULT', report['result'], report['elapsed_seconds'], 's', flush=True)
    return 0 if report['passed'] else 2


if __name__ == '__main__':
    try:
        code = main()
    except Exception:
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
