"""Check GM1 Rev L from fresh source CAD: the 300 mm Z, the dock on the bed module, and the bed lift.

Router: the eight X/Y/Z travel corners (Z 0 and 300) and the centre, dock parked.
Plasma: the same nine poses with the module (and dock) out and Rev K's head and torch on the
Z adapter, plus Rev K's three plasma-only poses (the top-of-Z one now at Z 300).
Dock travel: the carrier at 0..200 mm in 20 mm steps with the gantry at the rear stop and Z fully up,
with the head at X175, X575 and X975: the Z body now clears the magazine and its lid, so the dock may
move with the head anywhere (Z up).
Tool change: dock deployed, spindle axis on the pocket line (Y1100) at X345, X575 and X805:
  - Z fully up (300) and 5.65 mm above the lid allocation (about 178): must clear;
  - nut at the magazine support plane (Z 90): the spindle may only meet the magazine and lid
    allocations, the saddles and the stored-cutter allocation (the supplier's pocket interface).
Over the magazine: with the dock deployed and Z up, the gantry drives forward over the magazine
(gantry Y1275 down to 1150 at head X575, and Y1150 at X345 and X805): all clear. In Rev L before the
raise this pose clashed and the changer depended on the head being parked at X975 first.
Z rule: the only remaining collision is the spindle itself, low over the magazine. The dock may move,
and the gantry may cross the deployed magazine, only with the spindle nose (plus a 40 mm tool) above
the lid: z_lift at least Z_DOCK_MIN. The M14 interlock enforces this with the Z top switch.
Stock allowance: 40 mm over the HDPE must be clear of the deployed dock (50 before the magazine was lowered 10 mm
to fit its lid under the gantry).
Tool setter: on the dock's wing at X896, pocket line Y1100 (deployed), inside the tool travel; the head over it with Z up,
and with a 40 mm tool on the button (z_lift 151.35, the nut 40 mm above it): both clear.
Work light: the LED bar under the gantry beam's rear slot is at least 15 mm above the parked lid allocation, and the
gantry crosses the parked dock (Y1200 and Y1180, Z up) with the bar over the lid: clear.
Hoist: Rev J's sampled module-and-sling path with the dock deployed on the module (heavier, centre
of mass further back), head X575, Z fully up, at three hook heights, run 100 mm further forward.
Frame fill: every pose above carries the moved fill ports (ballast_revl.py). One port per frame tube,
none facing down in its fill attitude, and each tube at least 90 % full in that attitude by the sampled
estimate, for epoxy sand (frame tilted 15 degrees) and for dry sand (tube near vertical).
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
REVK = HERE.parent / 'RevK-ENGINEERING'
LEGACY = HERE.parent / 'RevE-ENGINEERING'
for path in (str(LEGACY), str(REVK), str(HERE)):
    if path not in sys.path:
        sys.path.insert(0, path)

OUT = HERE.parent / 'RevL-CAD' / 'revl-checks.json'
Z_TOP = 300.0
CORNERS = list(itertools.product((275.0, 1275.0), (175.0, 975.0), (0.0, Z_TOP))) + [(775.0, 575.0, 150.0)]
TORCH_Y_OFFSET = 201.4
PLASMA_EXTRA = [(571.5 + TORCH_Y_OFFSET, 575.0, 0.0, 'torch over slat 8, bottom of Z'),
                (660.0 + TORCH_Y_OFFSET, 955.0, 0.0, 'level-sensor band at the plasma limit X955, bottom of Z'),
                (660.0 + TORCH_Y_OFFSET, 975.0, Z_TOP, 'level-sensor band at full X, top of Z')]
POCKET_X = (345.0, 575.0, 805.0)
APPROACH_Z = None             # set in main: spindle bottom 5.65 mm above the lid allocation
ENGAGE_Z = None               # set in main: nut at the magazine support plane
FORWARD_L = 1520.0            # the dock's rear (Y1449) must also leave the frame
ENGAGE_OK = ('MOD_ATC_MAGAZINE_ALLOCATION', 'MOD_ATC_MAGAZINE_COVER_ALLOCATION', 'MOD_ATC_SADDLE_',
             'MOD_ATC_STORED_TOOLS_ALLOCATION')
TRAVEL_HEAD_X = (175.0, 575.0, 975.0)
TOOL_BELOW_NUT = 40.0         # a cutter in the spindle while the dock moves
CLEAR = 15.0
Z_DOCK_MIN = None             # set from the model: the lowest z_lift at which the dock may move


def main():
    from cad_helpers import bbox, box, intersection_volume, validate
    import build_revj as rev_j
    import build_revk
    import build_revl
    import atc_revl
    import ballast_revl
    import plasma_drop
    import verify_revk
    import z300
    import revj_handling_check as hoist

    global APPROACH_Z, ENGAGE_Z
    ENGAGE_Z = atc_revl.MAG - 960.0
    APPROACH_Z = atc_revl.COVER_TOP + 5.65 - 960.0
    start = time.monotonic()
    before = build_revl.source_hashes()
    report = {'scope': __doc__.strip(), 'revision': 'GM1 Rev L working design', 'status': 'RUNNING'}
    base, base_details = build_revk.build_model(with_motion=False)
    fill = ballast_revl.apply(base)
    report['rev_k_fixed_part_count'] = len(base.parts)

    def pose(travel, gy, hx, z):
        m = verify_revk.clone(base)
        atc = atc_revl.extend_router_model(m, travel)
        z300.add_motion(m, gantry_y=gy, head_x=hx, z_lift=z)
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
    for gy, hx, z, *label in [c + ('corner or centre',) for c in CORNERS] + PLASMA_EXTRA:
        m, _ = pose(atc_revl.TRAVEL, gy, hx, z)
        p, head = plasma_drop.plasma_head_model(rev_j.plasma_layout(m))
        r = validate(p)
        reach, left = verify_revk.classify(p, r['unresolved_intersections'])
        row = {'gantry_y': round(gy, 3), 'head_x': hx, 'z_lift': z, 'label': label[0], 'parts': r['part_count'],
               'tip_z_mm': head['tip_z_mm'], 'torch_axis_xy_mm': head['torch_axis_xy_mm'], 'reach_contacts': reach,
               'unresolved': left, 'invalid_local': verify_revk.solids_ok(p),
               'dock_parts_present': sum(q.id.startswith(atc_revl.PREFIX) for q in p.parts)}
        row['passed'] = not left and not row['invalid_local'] and row['dock_parts_present'] == 0
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
    for hx, z in itertools.product(POCKET_X, (Z_TOP, APPROACH_Z, ENGAGE_Z)):
        m, atc = pose(0.0, build_revl.POCKET_GANTRY_Y, hx, z)
        row, _ = row_of(m, gantry_y=build_revl.POCKET_GANTRY_Y, head_x=hx, z_lift=z, dock='deployed')
        expected, other = [], []
        for c in row['unresolved']:
            pair = (c['a'], c['b'])
            if z == ENGAGE_Z and ('TOOL_SPINDLE_65x259' in pair or 'TOOL_SPLIT_CLAMP_FRONT' in pair) and any(i.startswith(ENGAGE_OK) for i in pair):
                expected.append(c)
            else:
                other.append(c)
        row.update(pocket_interface_contacts=expected, unresolved=other)
        row['passed'] = not other and not row['invalid_local']
        change_rows.append(row)
        print('tool change', hx, z, 'interface', len(expected), 'clashes', len(other), flush=True)

    over_rows = []
    for gy, hx in [(1150.0, 575.0), (1200.0, 575.0), (1230.0, 575.0), (1150.0, 345.0), (1150.0, 805.0)]:
        m, _ = pose(0.0, gy, hx, Z_TOP)
        row, _ = row_of(m, gantry_y=gy, head_x=hx, z_lift=Z_TOP, dock='deployed')
        row['passed'] = not row['unresolved'] and not row['invalid_local']
        over_rows.append(row)
        print('over the deployed magazine', gy, hx, 'clashes', len(row['unresolved']), flush=True)
    cross_rows = []
    for gy in (1200.0, 1180.0):
        mc, _ = pose(atc_revl.TRAVEL, gy, 575.0, Z_TOP)
        row, _ = row_of(mc, gantry_y=gy, head_x=575.0, z_lift=Z_TOP, dock='parked')
        row['passed'] = not row['unresolved'] and not row['invalid_local']
        cross_rows.append(row)
        print('over the parked dock', gy, 'clashes', len(row['unresolved']), flush=True)
    light_bottom = bbox(mc.find('GANTRY_WORK_LIGHT').shape)[2]
    setter_z = atc_revl.SETTER_TOP - (960.0 - TOOL_BELOW_NUT)
    setter_rows = []
    for z, label in ((Z_TOP, 'over the setter, Z up'), (setter_z, 'a 40 mm tool on the setter button')):
        ms, _ = pose(0.0, build_revl.POCKET_GANTRY_Y, atc_revl.SETTER_X, z)
        row, _ = row_of(ms, gantry_y=build_revl.POCKET_GANTRY_Y, head_x=atc_revl.SETTER_X, z_lift=z, dock='deployed', step=label)
        nose = bbox(ms.find('TOOL_SPINDLE_65x259').shape)[2]
        row.update(spindle_nose_z_mm=round(nose, 3), nose_above_button_mm=round(nose - atc_revl.SETTER_TOP, 3))
        row['passed'] = not row['unresolved'] and not row['invalid_local']
        setter_rows.append(row)
        print('tool setter', label, 'nose', round(nose, 2), 'clashes', len(row['unresolved']), flush=True)
    setter_xy = (atc_revl.SETTER_X, atc_revl.POCKET_Y)
    body_bottom = min(bbox(p.shape)[2] for p in m.parts if p.id.startswith('ZBX80_'))
    lid_top = atc_revl.COVER_TOP
    z_dock_min = lid_top + TOOL_BELOW_NUT + CLEAR - 960.0
    global Z_DOCK_MIN
    Z_DOCK_MIN = z_dock_min
    print('Z body bottom', body_bottom, 'lid top', lid_top, 'dock moves at z >=', z_dock_min, flush=True)

    m, atc_dep = pose(0.0, 1275.0, 575.0, Z_TOP)
    stock = box(800, 1000, 40).translate((175, 130, 958.8))
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

    nut_top = 960.0 + Z_TOP
    checks = {
        'every router pose clear (dock parked, Z 0..300)': all(r['passed'] and r['inventory_stable'] for r in router_rows),
        'every plasma pose clear, module and dock out': all(r['passed'] for r in plasma_rows),
        'torch reaches below the slat top within the float travel': bool(reach_rows) and all(
            0 < c['tip_below_slat_top_mm'] <= verify_revk.FLOAT_TRAVEL - .5 for c in reach_rows),
        'dock travel clear at the rear stop with the head at X175, X575 and X975': all(r['passed'] for r in travel_rows),
        'tool-change poses clear; only the pocket interface is touched': all(r['passed'] for r in change_rows),
        'the Z body clears the magazine and its lid by at least 15 mm': body_bottom - lid_top >= CLEAR,
        'gantry over the deployed magazine with Z up: clear': all(r['passed'] for r in over_rows),
        'the dock can move with Z at least 65 mm below the top (a 40 mm tool clears the lid by 15 mm)': z_dock_min <= Z_TOP - 65,
        'deployed dock clear of a 40 mm stock and clamp allowance': not stock_hits,
        'RapidChange 90 mm: spindle nut at full Z at least 90 mm above the magazine lid': nut_top - lid_top >= 90,
        'tool setter inside the tool travel, on the pocket line; head over it clear, and a 40 mm tool on the button with the nut 40 mm above it': (
            175.0 <= setter_xy[0] <= 975.0 and 121.4 <= setter_xy[1] <= 1121.4 and all(r['passed'] for r in setter_rows)
            and abs(setter_rows[1]['nose_above_button_mm'] - TOOL_BELOW_NUT) < 1e-6),
        'work light under the beam at least 15 mm above the parked lid; gantry crossing the parked dock with Z up: clear': (
            light_bottom - lid_top >= CLEAR and all(r['passed'] for r in cross_rows)),
        'hoist path clear at every hook height with the dock deployed': all(c['result'].startswith('PASS') for c in hoist_cases),
        'frame fill: one port per frame tube': sorted(p['tube'] for p in fill['ports']) == sorted(
            p.id for p in base.parts if p.group == 'main_frame') and len(fill['ports']) == 18,
        'frame fill: no port faces down in its fill attitude': not any(
            e[k]['port_faces_down'] for e in fill['estimates'] for k in ('epoxy', 'dry_sand')),
        'frame fill: every tube at least 90 % full, epoxy (15 degree tilt) and dry sand (near vertical)': all(
            e[k]['filled_fraction'] >= 0.90 for e in fill['estimates'] for k in ('epoxy', 'dry_sand'))}
    after = build_revl.source_hashes()
    report.update(status='PASS' if all(checks.values()) and before == after else 'FAIL', checks=checks,
                  router_poses=router_rows, plasma_poses=plasma_rows, dock_travel=travel_rows,
                  tool_change_poses=change_rows, over_deployed_magazine=over_rows, gantry_over_parked_dock=cross_rows,
                  tool_setter_poses=setter_rows, tool_setter=dict(atc_dep['tool_setter'], touch_z_lift_mm=round(setter_z, 3)),
                  work_light_bottom_z_mm=round(light_bottom, 3), work_light_over_parked_lid_mm=round(light_bottom - lid_top, 3),
                  stock_allowance_hits=stock_hits,
                  z_body_bottom_mm=body_bottom, lid_top_mm=lid_top, z_body_clearance_over_lid_mm=round(body_bottom - lid_top, 2),
                  dock_moves_at_z_lift_at_least_mm=round(z_dock_min, 2),
                  nut_above_magazine_plane_at_full_z_mm=round(nut_top - atc_revl.MAG, 2),
                  nut_above_lid_at_full_z_mm=round(nut_top - lid_top, 2),
                  bed_with_dock={k: details['bed'][k] for k in ('module_mass_estimate_kg', 'module_cg_mm', 'module_without_dock')},
                  hoist_forward_mm=FORWARD_L, hoist_cases=hoist_cases, frame_fill=fill,
                  sources_unchanged_during_run=before == after, source_sha256=before,
                  elapsed_seconds=round(time.monotonic() - start, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
    print('REV L CHECKS', report['status'], json.dumps(checks), flush=True)
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
