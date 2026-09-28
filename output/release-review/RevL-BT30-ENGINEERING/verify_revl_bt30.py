"""Check GM1 Rev L's BT30 variant from fresh source CAD: the BT30 head, the fork rack on the dock, and the bed lift.

Router: the eight X/Y/Z travel corners (Z 0 and 300) and the centre, dock parked, a holder in the spindle.
Plasma: the same nine poses with the module (and dock) out, the BT30 spindle in its cradle on the reservoir lid, the
clamp and its screws in the bin, and Rev K's head and torch on the thicker adapter (torch axis Y = gantry Y - 207.75),
plus Rev K's three plasma-only poses.
Dock travel: the carrier at 0..200 mm in 20 mm steps, gantry at the rear stop, Z fully up, head at X175, X575 and X975.
Tool change, at pockets 1, 3 and 6 (X350, X530, X800), spindle axis on the pocket line (Y1073.65 deployed):
  - Z fully up with a holder in the spindle, all pockets full: clear;
  - engage: spindle nose at the gauge line (Z 37.7), no holder in the spindle, all pockets full: only the spindle
    envelope may meet that pocket's holder (the taper inside the nose);
  - sliding in: holder in the spindle 35 mm in front of the pocket line at the engage height, that pocket empty: only
    the held holder may meet that pocket's fork (the lips entering the flange groove);
  - approach: holder in the spindle 70 mm in front of the pocket line at the engage height, that pocket empty: clear.
Over the rack: dock deployed, Z up, gantry Y1150..1230 at X575 and Y1150 at X350 and X800: clear.
Sweep: the pull-stud tops of the stored holders sit under the gantry's lowest members (Z1143) by at least 8 mm with the
dock parked, and the Z body clears them by at least 15 mm.
Z rule: the dock may move, and the gantry may cross the deployed rack, only with a held tool (holder plus a 40 mm
cutter) 15 mm above the stud tops: z_lift at least Z_DOCK_MIN, at least 30 mm below the top (the M14 top-switch interlock).
Stock allowance: 8.5 mm over the HDPE must be clear of the deployed dock.
Tool setter: on the dock's wing at X896, pocket line Y1073.65 (deployed), inside the tool travel; the head over it with Z up
and the held holder's cutter allocation on the button (z_lift 151.35): nothing but that touch.
Work light: the LED bar under the gantry beam counts among the gantry's lowest members (sweep rule above), and the gantry
crosses the parked rack (Y1200 and Y1180, Z up) with the bar over the studs: clear.
Hoist: Rev J's sampled module-and-sling path with the dock deployed on the module, at three hook heights.
Frame fill: as Rev L (the ports moved by ballast_revl.py).
This is a sampled static interference check, not a motion, stiffness or cut test.
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

OUT = HERE.parent / 'RevL-BT30-CAD' / 'revl-bt30-checks.json'
Z_TOP = 300.0
X_MIN, X_MAX = 175.0, 975.0
CORNERS = list(itertools.product((275.0, 1275.0), (X_MIN, X_MAX), (0.0, Z_TOP))) + [(775.0, 575.0, 150.0)]
TEST_POCKETS = (1, 3, 6)
TRAVEL_HEAD_X = (X_MIN, 575.0, X_MAX)
FORWARD_L = 1520.0
CLEAR = 15.0
SWEEP_CLEAR = 8.0
STOCK = 8.5


def main():
    from cad_helpers import bbox, box, intersection_volume, validate
    import build_revk
    import build_revl
    import build_revl_bt30
    import atc_revl
    import ballast_revl
    import bt30_revl as bt30
    import plasma_drop
    import verify_revk
    import revj_handling_check as hoist

    torch_y_offset = verify_revk.TORCH_Y_OFFSET + bt30.ADAPTER_T - 12.7
    plasma_extra = [(verify_revk.SLAT_8_CENTRE_Y + torch_y_offset, 575.0, 0.0, 'torch over slat 8, bottom of Z'),
                    (660.0 + torch_y_offset, 955.0, 0.0, 'level-sensor band at the plasma limit X955, bottom of Z'),
                    (660.0 + torch_y_offset, X_MAX, Z_TOP, 'level-sensor band at full X, top of Z')]
    pocket_gy = build_revl_bt30.POCKET_GANTRY_Y
    engage = bt30.Z_ENGAGE
    start = time.monotonic()
    before = build_revl_bt30.source_hashes()
    report = {'scope': __doc__.strip(), 'revision': 'GM1 Rev L working design, BT30 variant', 'status': 'RUNNING'}
    base, base_details = build_revk.build_model(with_motion=False)
    fill = ballast_revl.apply(base)
    parking = bt30.replace_cradle(base)
    report['rev_k_fixed_part_count'] = len(base.parts)

    def pose(travel, gy, hx, z, held=True, empty=()):
        m = verify_revk.clone(base)
        atc = bt30.extend_router_model(m, travel, empty)
        bt30.add_motion(m, gantry_y=gy, head_x=hx, z_lift=z, held_tool=held)
        return m, atc

    def row_of(m, **kw):
        r = validate(m)
        row = dict(kw, parts=r['part_count'], unresolved=r['unresolved_intersections'], invalid_local=verify_revk.solids_ok(m))
        return row, r

    router_rows, inventory = [], {}
    for gy, hx, z in CORNERS:
        m, _ = pose(atc_revl.TRAVEL, gy, hx, z)
        row, _ = row_of(m, gantry_y=gy, head_x=hx, z_lift=z, dock='parked')
        row['passed'] = not row['unresolved'] and not row['invalid_local']
        ids = [p.id for p in m.parts]
        inventory.setdefault('router', ids)
        row['inventory_stable'] = ids == inventory['router']
        router_rows.append(row)
        print('router', gy, hx, z, 'clashes', len(row['unresolved']), flush=True)

    plasma_rows, reach_rows = [], []
    for gy, hx, z, *label in [c + ('corner or centre',) for c in CORNERS] + plasma_extra:
        m, _ = pose(atc_revl.TRAVEL, gy, hx, z)
        p, head = plasma_drop.plasma_head_model(bt30.plasma_layout(m))
        r = validate(p)
        reach, left = verify_revk.classify(p, r['unresolved_intersections'])
        spindle = [q for q in p.parts if q.id == bt30.SPINDLE_ID]
        row = {'gantry_y': round(gy, 3), 'head_x': hx, 'z_lift': z, 'label': label[0], 'parts': r['part_count'],
               'tip_z_mm': head['tip_z_mm'], 'torch_axis_xy_mm': head['torch_axis_xy_mm'], 'reach_contacts': reach,
               'unresolved': left, 'invalid_local': verify_revk.solids_ok(p),
               'dock_parts_present': sum(q.id.startswith(atc_revl.PREFIX) for q in p.parts),
               'spindle_parked': len(spindle) == 1 and spindle[0].group == 'stored_tool',
               'held_holder_present': any(q.id == 'TOOL_HOLDER_HELD_ALLOCATION' for q in p.parts)}
        row['passed'] = (not left and not row['invalid_local'] and row['dock_parts_present'] == 0 and row['spindle_parked']
                         and not row['held_holder_present'])
        plasma_rows.append(row)
        reach_rows += reach
        print('plasma', round(gy, 1), hx, z, label[0], 'tip', head['tip_z_mm'], 'clashes', len(left), flush=True)

    travel_rows = []
    for hx in TRAVEL_HEAD_X:
        for travel in [20.0 * i for i in range(11)]:
            m, atc = pose(travel, 1275.0, hx, Z_TOP)
            row, _ = row_of(m, travel_mm=travel, gantry_y=1275.0, head_x=hx, z_lift=Z_TOP)
            row['passed'] = not row['unresolved'] and not row['invalid_local']
            travel_rows.append(row)
            print('dock travel', travel, 'head', hx, 'clashes', len(row['unresolved']), flush=True)

    change_rows = []
    for k in TEST_POCKETS:
        px = bt30.POCKET_X[k - 1]
        stored, fork = f'{atc_revl.PREFIX}STORED_HOLDER_{k}', f'{atc_revl.PREFIX}FORK_{k}'
        steps = [('top, holder in the spindle, all pockets full', pocket_gy, Z_TOP, True, (), set()),
                 ('engage: nose at the gauge line, no holder in the spindle', pocket_gy, engage, False, (),
                  {frozenset((bt30.SPINDLE_ID, stored))}),
                 ('sliding in: held holder 35 mm ahead of the pocket line, pocket empty', pocket_gy - 35.0, engage, True, (k,),
                  {frozenset(('TOOL_HOLDER_HELD_ALLOCATION', fork))}),
                 ('approach: held holder 70 mm ahead of the pocket line, pocket empty', pocket_gy - 70.0, engage, True, (k,), set())]
        for label, gy, z, held, empty, allowed in steps:
            m, atc = pose(0.0, gy, px, z, held, empty)
            row, _ = row_of(m, pocket=k, step=label, gantry_y=gy, head_x=px, z_lift=z, held_tool=held, dock='deployed')
            expected, other = [], []
            for c in row['unresolved']:
                (expected if frozenset((c['a'], c['b'])) in allowed else other).append(c)
            row.update(pocket_interface_contacts=expected, unresolved=other, interface_complete=len(expected) == len(allowed))
            row['passed'] = not other and not row['invalid_local'] and row['interface_complete']
            change_rows.append(row)
            print('tool change', k, label.split(':')[0], 'interface', len(expected), 'clashes', len(other), flush=True)

    over_rows = []
    for gy, hx in [(1150.0, 575.0), (1200.0, 575.0), (1230.0, 575.0), (1150.0, bt30.POCKET_X[0]), (1150.0, bt30.POCKET_X[-1])]:
        m, _ = pose(0.0, gy, hx, Z_TOP)
        row, _ = row_of(m, gantry_y=gy, head_x=hx, z_lift=Z_TOP, dock='deployed')
        row['passed'] = not row['unresolved'] and not row['invalid_local']
        over_rows.append(row)
        print('over the deployed rack', gy, hx, 'clashes', len(row['unresolved']), flush=True)
    body_bottom = min(bbox(p.shape)[2] for p in m.parts if p.id.startswith('ZBX80_'))
    rack_top = max(bbox(p.shape)[5] for p in m.parts if p.id.startswith(atc_revl.PREFIX + 'STORED_HOLDER_'))
    stored_bottom = min(bbox(p.shape)[2] for p in m.parts if p.id.startswith(atc_revl.PREFIX + 'STORED_HOLDER_'))
    m_parked, _ = pose(atc_revl.TRAVEL, 1275.0, 575.0, Z_TOP)
    gantry_low = min(bbox(p.shape)[2] for p in m_parked.parts
                     if p.id.startswith(('Z_CARRIER', 'X_BLOCK_', 'X_GUIDE_FACE', 'X_RAIL_', 'GANTRY_8080', 'GANTRY_WORK_LIGHT')) and 'BOLT' not in p.id)
    light_bottom = bbox(m_parked.find('GANTRY_WORK_LIGHT').shape)[2]
    cross_rows = []
    for gy in (1200.0, 1180.0):
        mc, _ = pose(atc_revl.TRAVEL, gy, 575.0, Z_TOP)
        row, _ = row_of(mc, gantry_y=gy, head_x=575.0, z_lift=Z_TOP, dock='parked')
        row['passed'] = not row['unresolved'] and not row['invalid_local']
        cross_rows.append(row)
        print('over the parked rack', gy, 'clashes', len(row['unresolved']), flush=True)
    setter_z = atc_revl.SETTER_TOP - 920.0
    setter_rows = []
    touch = frozenset(('TOOL_HOLDER_HELD_ALLOCATION', atc_revl.PREFIX + 'TOOL_SETTER'))
    for z, label in ((Z_TOP, 'over the setter, Z up'), (setter_z, 'held holder\'s cutter allocation on the setter button')):
        ms, _ = pose(0.0, pocket_gy, atc_revl.SETTER_X, z)
        row, _ = row_of(ms, gantry_y=pocket_gy, head_x=atc_revl.SETTER_X, z_lift=z, dock='deployed', step=label)
        other = [c for c in row['unresolved'] if frozenset((c['a'], c['b'])) != touch]
        held_bottom = bbox(ms.find('TOOL_HOLDER_HELD_ALLOCATION').shape)[2]
        row.update(unresolved=other, held_allocation_bottom_z_mm=round(held_bottom, 3),
                   held_bottom_above_button_mm=round(held_bottom - atc_revl.SETTER_TOP, 3))
        row['passed'] = not other and not row['invalid_local']
        setter_rows.append(row)
        print('tool setter', label, 'held bottom', round(held_bottom, 2), 'clashes', len(other), flush=True)
    setter_xy = (atc_revl.SETTER_X, bt30.POCKET_Y)
    z_dock_min = rack_top + bt30.HELD_CUTTER + CLEAR - 920.0
    print('Z body bottom', body_bottom, 'rack top', rack_top, 'gantry low', gantry_low, 'dock moves at z >=', z_dock_min, flush=True)

    m, atc_dep = pose(0.0, 1275.0, 575.0, Z_TOP)
    stock = box(800, 1000, STOCK).translate((175, 130, 958.8))
    stock_hits = []
    for p in m.parts:
        if p.id.startswith(atc_revl.PREFIX):
            v = intersection_volume(p.shape, stock)
            if v > .02:
                stock_hits.append({'part': p.id, 'intersection_mm3': round(v, 3)})
    print('stock allowance hits', len(stock_hits), flush=True)

    details = dict(base_details)
    details['bed'] = build_revl.module_with_dock(base_details['bed'], atc_dep)
    hoist.FORWARD = FORWARD_L
    hoist_cases = [hoist.Checker(m, details, rise).run() for rise in hoist.HOOK_RISES]

    held_bottom_top = 960.0 + Z_TOP
    checks = {
        'every router pose clear (dock parked, Z 0..300, holder in the spindle)': all(r['passed'] and r['inventory_stable'] for r in router_rows),
        'every plasma pose clear: module and dock out, spindle in its cradle, clamp in the bin': all(r['passed'] for r in plasma_rows),
        'torch reaches below the slat top within the float travel': bool(reach_rows) and all(
            0 < c['tip_below_slat_top_mm'] <= verify_revk.FLOAT_TRAVEL - .5 for c in reach_rows),
        'dock travel clear at the rear stop with the head at X175, X575 and X975': all(r['passed'] for r in travel_rows),
        'tool-change poses clear; only the pocket interface is touched, and it is touched': all(r['passed'] for r in change_rows),
        'the Z body clears the stored holders by at least 15 mm': body_bottom - rack_top >= CLEAR,
        'stored holders under the gantry\'s lowest members by at least 8 mm (dock parked or crossed)': gantry_low - rack_top >= SWEEP_CLEAR,
        'gantry over the deployed rack with Z up: clear': all(r['passed'] for r in over_rows),
        'the dock can move with Z at least 30 mm below the top (held holder and a 40 mm cutter clear the studs by 15)': z_dock_min <= Z_TOP - 30,
        'deployed dock clear of an 8.5 mm stock allowance over the HDPE': not stock_hits,
        'held holder nose at full Z at least 100 mm above the stored studs': held_bottom_top - rack_top >= 100,
        'tool setter inside the tool travel, on the pocket line; head over it clear, and the held cutter allocation on the button': (
            X_MIN <= setter_xy[0] <= X_MAX and 121.4 <= setter_xy[1] <= 1121.4 and all(r['passed'] for r in setter_rows)
            and abs(setter_rows[1]['held_bottom_above_button_mm']) < 1e-6),
        'work light under the beam at least 15 mm above the stored studs; gantry crossing the parked rack with Z up: clear': (
            light_bottom - rack_top >= CLEAR and all(r['passed'] for r in cross_rows)),
        'hoist path clear at every hook height with the dock deployed': all(c['result'].startswith('PASS') for c in hoist_cases),
        'frame fill: one port per frame tube': sorted(p['tube'] for p in fill['ports']) == sorted(
            p.id for p in base.parts if p.group == 'main_frame') and len(fill['ports']) == 18,
        'frame fill: no port faces down in its fill attitude': not any(
            e[k]['port_faces_down'] for e in fill['estimates'] for k in ('epoxy', 'dry_sand')),
        'frame fill: every tube at least 90 % full, epoxy (15 degree tilt) and dry sand (near vertical)': all(
            e[k]['filled_fraction'] >= 0.90 for e in fill['estimates'] for k in ('epoxy', 'dry_sand'))}
    after = build_revl_bt30.source_hashes()
    report.update(status='PASS' if all(checks.values()) and before == after else 'FAIL', checks=checks,
                  router_poses=router_rows, plasma_poses=plasma_rows, dock_travel=travel_rows,
                  tool_change_poses=change_rows, over_deployed_rack=over_rows, gantry_over_parked_rack=cross_rows,
                  tool_setter_poses=setter_rows, tool_setter=dict(atc_dep['tool_setter'], touch_z_lift_mm=round(setter_z, 3)),
                  work_light_bottom_z_mm=round(light_bottom, 3), work_light_over_studs_mm=round(light_bottom - rack_top, 3),
                  stock_allowance_hits=stock_hits,
                  z_body_bottom_mm=body_bottom, rack_top_mm=rack_top, stored_holder_bottom_mm=round(stored_bottom, 3),
                  stock_allowance_mm=round(stored_bottom - 958.8, 3), gantry_lowest_member_z_mm=gantry_low,
                  z_body_clearance_over_rack_mm=round(body_bottom - rack_top, 3), rack_under_gantry_mm=round(gantry_low - rack_top, 3),
                  dock_moves_at_z_lift_at_least_mm=round(z_dock_min, 3), z_engage_mm=round(engage, 3),
                  held_nose_above_rack_at_full_z_mm=round(held_bottom_top - rack_top, 3), torch_y_offset_mm=round(torch_y_offset, 3),
                  spindle_parking=parking, pocket_x_mm=list(bt30.POCKET_X), pocket_gantry_y_mm=pocket_gy,
                  bed_with_dock={k: details['bed'][k] for k in ('module_mass_estimate_kg', 'module_cg_mm', 'module_without_dock')},
                  hoist_forward_mm=FORWARD_L, hoist_cases=hoist_cases, frame_fill=fill,
                  sources_unchanged_during_run=before == after, source_sha256=before,
                  elapsed_seconds=round(time.monotonic() - start, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
    print('REV L BT30 CHECKS', report['status'], json.dumps(checks), flush=True)
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
