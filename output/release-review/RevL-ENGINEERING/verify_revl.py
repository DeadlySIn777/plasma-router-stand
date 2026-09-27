"""Check GM1 Rev L from fresh source CAD: the 300 mm Z, the dock on the bed module, and the bed lift.

Router: the eight X/Y/Z travel corners (Z 0 and 300) and the centre, dock parked.
Plasma: the same nine poses with the module (and dock) out and Rev K's head and torch on the
Z adapter, plus Rev K's three plasma-only poses (the top-of-Z one now at Z 300).
Dock travel: the carrier at 0..200 mm in 20 mm steps with the gantry at the rear stop, the head
at X975 and Z fully up (the pose the dock moves in).
Tool change: dock deployed, spindle axis on the pocket line (Y1100) at X345, X575 and X805:
  - Z fully up (300) and 5 mm above the magazine allocation (176): must clear;
  - nut at the magazine support plane (Z 90): the spindle may only meet the magazine allocation,
    the saddles and the stored-cutter allocation (the supplier's pocket interface); nothing else.
Forbidden approach: with the dock deployed, the Z body's lower end block cannot pass over the
magazine. A pose with the spindle in front of the magazine must clash; the tool-change sequence
therefore reaches the pockets from the rear stop.
Stock allowance: 50 mm over the HDPE must be clear of the deployed dock.
Hoist: Rev J's sampled module-and-sling path with the dock deployed on the module (heavier, centre
of mass further back), head X575, Z fully up, at three hook heights, run 100 mm further forward.
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
APPROACH_Z = 176.0            # spindle bottom 5.65 mm above the 80 mm magazine allocation
ENGAGE_Z = 90.0               # nut at the magazine support plane (Z1050)
FORWARD_L = 1520.0            # the dock's rear (Y1449) must also leave the frame
ENGAGE_OK = ('MOD_ATC_MAGAZINE_ALLOCATION', 'MOD_ATC_SADDLE_', 'MOD_ATC_STORED_TOOLS_ALLOCATION')


def main():
    from cad_helpers import box, intersection_volume, validate
    import build_revj as rev_j
    import build_revk
    import build_revl
    import atc_revl
    import plasma_drop
    import verify_revk
    import z300
    import revj_handling_check as hoist

    start = time.monotonic()
    before = build_revl.source_hashes()
    report = {'scope': __doc__.strip(), 'revision': 'GM1 Rev L working design', 'status': 'RUNNING'}
    base, base_details = build_revk.build_model(with_motion=False)
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
    for travel in [20.0 * i for i in range(11)]:
        m, atc = pose(travel, 1275.0, build_revl.DOCK_X, Z_TOP)
        row, _ = row_of(m, travel_mm=travel, gantry_y=1275.0, head_x=build_revl.DOCK_X, z_lift=Z_TOP)
        row['passed'] = not row['unresolved'] and not row['invalid_local']
        travel_rows.append(row)
        print('dock travel', travel, 'clashes', len(row['unresolved']), flush=True)

    change_rows = []
    for hx, z in itertools.product(POCKET_X, (Z_TOP, APPROACH_Z, ENGAGE_Z)):
        m, atc = pose(0.0, build_revl.POCKET_GANTRY_Y, hx, z)
        row, _ = row_of(m, gantry_y=build_revl.POCKET_GANTRY_Y, head_x=hx, z_lift=z, dock='deployed')
        expected, other = [], []
        for c in row['unresolved']:
            pair = (c['a'], c['b'])
            if z == ENGAGE_Z and 'TOOL_SPINDLE_65x259' in pair and any(i.startswith(ENGAGE_OK) for i in pair):
                expected.append(c)
            else:
                other.append(c)
        row.update(pocket_interface_contacts=expected, unresolved=other)
        row['passed'] = not other and not row['invalid_local']
        change_rows.append(row)
        print('tool change', hx, z, 'interface', len(expected), 'clashes', len(other), flush=True)

    m, _ = pose(0.0, 1150.0, 575.0, Z_TOP)
    forbidden, _ = row_of(m, gantry_y=1150.0, head_x=575.0, z_lift=Z_TOP, dock='deployed')
    zbody = [c for c in forbidden['unresolved'] if any(i.startswith('ZBX80_') for i in (c['a'], c['b']))]
    forbidden['z_body_clashes_with_dock'] = zbody
    forbidden['meaning'] = 'Expected: the Z body cannot pass over the deployed magazine; approach the pockets from the rear stop.'
    print('forbidden approach: z-body clashes', len(zbody), flush=True)

    m, atc_dep = pose(0.0, 1275.0, 575.0, Z_TOP)
    stock = box(800, 1000, 50).translate((175, 130, 958.8))
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
        'dock travel clear at the rear stop with the head at X975': all(r['passed'] for r in travel_rows),
        'tool-change poses clear; only the pocket interface is touched': all(r['passed'] for r in change_rows),
        'the Z body cannot pass over the deployed magazine (forbidden approach clashes)': bool(zbody),
        'deployed dock clear of a 50 mm stock and clamp allowance': not stock_hits,
        'RapidChange 90 mm: spindle nut at full Z at least 90 mm above the magazine plane': nut_top - atc_revl.MAG >= 90,
        'hoist path clear at every hook height with the dock deployed': all(c['result'].startswith('PASS') for c in hoist_cases)}
    after = build_revl.source_hashes()
    report.update(status='PASS' if all(checks.values()) and before == after else 'FAIL', checks=checks,
                  router_poses=router_rows, plasma_poses=plasma_rows, dock_travel=travel_rows,
                  tool_change_poses=change_rows, forbidden_approach=forbidden, stock_allowance_hits=stock_hits,
                  nut_above_magazine_plane_at_full_z_mm=round(nut_top - atc_revl.MAG, 2),
                  bed_with_dock={k: details['bed'][k] for k in ('module_mass_estimate_kg', 'module_cg_mm', 'module_without_dock')},
                  hoist_forward_mm=FORWARD_L, hoist_cases=hoist_cases,
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
