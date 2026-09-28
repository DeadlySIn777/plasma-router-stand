"""GM1 Rev L, BT30 variant: Rev L with a 3.2 kW BT30 ATC spindle and a fork rack (bt30_revl.py).

Rev L's sources (`../RevL-ENGINEERING`, `../RevK-ENGINEERING`, `../RevE-ENGINEERING`) are used unchanged;
this folder holds only the BT30 differences. Exports to ../RevL-BT30-CAD:
  RevLBT30_ROUTER       dock parked, gantry at the rear stop, head X575, Z fully up, a holder in the spindle (assembly STEP)
  RevLBT30_PLASMA       module and dock out, the spindle in its cradle, the plasma head and torch on the adapter (assembly STEP)
  RevLBT30_BED_MODULE   the module with the dock deployed, as lifted for a bed change
  RevLBT30_DOCK         the dock alone, deployed (assembly STEP)
  RevLBT30_NEW_PARTS    what differs from Rev L: the head (adapter, clamp, screws, spindle and holder envelopes), the carrier
                        and rack, and the parking cradles: cut list, part STEP files and DXF
  previews              router, tool change (spindle down on pocket 3, X530), plasma, bed module, dock close-up
Unknown purchased interfaces stay guarded; no manufacturing release is implied.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
import time

HERE = Path(__file__).resolve().parent
REVL = HERE.parent / 'RevL-ENGINEERING'
REVK = HERE.parent / 'RevK-ENGINEERING'
LEGACY = HERE.parent / 'RevE-ENGINEERING'
for path in (str(LEGACY), str(REVK), str(REVL), str(HERE)):
    if path not in sys.path:
        sys.path.insert(0, path)

from cad_helpers import export  # noqa: E402
import build_revj as rev_j  # noqa: E402
import build_revk  # noqa: E402
import build_revl  # noqa: E402
import atc_revl  # noqa: E402
import ballast_revl  # noqa: E402
import z300  # noqa: E402
import bt30_revl as bt30  # noqa: E402

OUT = HERE.parent / 'RevL-BT30-CAD'
MACHINE = rev_j.MACHINE
POCKET_GANTRY_Y = bt30.POCKET_Y + bt30.TOOL_AXIS_OFFSET      # 1253.6, as Rev L: the axis and the pocket moved together
NEW_IDS = ('TOOL_ADAPTER_110', 'TOOL_SPINDLE_CLAMP', bt30.SPINDLE_ID, 'TOOL_HOLDER_HELD_ALLOCATION', 'MOD_ATC_CARRIER', 'MOD_ATC_UPSTAND_REAR',
           'MOD_ATC_RACK_BAR')
NEW_PREFIXES = ('TOOL_CLAMP_MOUNT_', 'TOOL_CLAMP_PINCH_', 'BT30_PARK_', 'MOD_ATC_BAR_SCREW_', 'MOD_ATC_FORK_',
                'MOD_ATC_STORED_HOLDER_')


def source_hashes():
    own = {f'{p.parent.name}/{p.name}': hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob('*.py'))}
    return {**build_revl.source_hashes(), **own}


def is_new(part):
    return part.id in NEW_IDS or part.id.startswith(NEW_PREFIXES)


def build_model(with_motion=True, gantry_y=1275.0, head_x=575.0, z_lift=z300.STROKE, atc_travel=atc_revl.TRAVEL, held_tool=True):
    model, details = build_revk.build_model(with_motion=False)
    details['frame_fill'] = ballast_revl.apply(model)
    details['tool_parking'] = dict(details.get('tool_parking', {}), **bt30.replace_cradle(model),
                                   handling='BT30 spindle (about 15 kg) parked in two 140 mm cradles on the reservoir lid, its clamp '
                                            'halves and screws in the hardware bin, the drawdowns in the Rev J bolt tray.')
    details['atc'] = bt30.extend_router_model(model, travel=atc_travel)
    if with_motion:
        details['motion'], details['motion_completion'] = bt30.add_motion(model, gantry_y, head_x, z_lift, held_tool)
    build_revk.purchased_material(model)
    details['bed_rev_j'] = details['bed']
    details['bed'] = build_revl.module_with_dock(details['bed'], details['atc'])
    model.holds.append('Z slide: the 300 mm ZBX80 is drawn from its listing drawing (body 419). Measure the delivered body, '
                       'carriage, end blocks and base slots before the drop adapter and the carrier bolting are made.')
    model.holds.extend(bt30.HOLDS)
    details['machine'] = MACHINE
    details['revision'] = 'L working design, BT30 variant: Rev L with a 3.2 kW BT30 ATC spindle and a fork rack on the dock'
    details['status'] = 'WORKING CAD - NOT A FABRICATION RELEASE'
    details['bt30'] = {'spindle_envelope_mm': [bt30.SPINDLE_D, bt30.SPINDLE_L], 'spindle_mass_kg_assumed': bt30.SPINDLE_KG,
                       'spindle_listing': 'Amazon B0HJ89DJL6 (title only; the listing could not be read)',
                       'holder': 'BT30-ER32-60 class, allocation', 'tool_axis_forward_of_rev_l_mm': round(bt30.TOOL_Y_SHIFT, 3),
                       'tool_axis_y_limits_mm': bt30.TOOL_AXIS_Y_LIMITS, 'pocket_line_y_deployed_mm': bt30.POCKET_Y,
                       'pocket_x_mm': list(bt30.POCKET_X), 'gauge_line_z_mm': bt30.GAUGE_Z, 'rack_top_z_mm': bt30.RACK_TOP,
                       'stored_tool_bottom_z_mm': bt30.STORED_BOTTOM, 'stock_allowance_mm': round(bt30.STOCK_ALLOWANCE, 3),
                       'z_engage_mm': round(bt30.Z_ENGAGE, 3), 'z_dock_min_mm': round(bt30.Z_DOCK_MIN, 3),
                       'stored_cutter_max_below_nut_mm': bt30.STORED_CUTTER, 'held_cutter_rule_mm': bt30.HELD_CUTTER}
    return model, details


def plasma_model(router_model, **head):
    import plasma_drop
    stored = bt30.plasma_layout(router_model)
    model, details = plasma_drop.plasma_head_model(stored, **head)
    build_revk.purchased_material(model)
    return model, details


def main():
    start = time.monotonic()
    before = source_hashes()
    OUT.mkdir(parents=True, exist_ok=True)
    rev_j.OUT = OUT
    model, details = build_model()
    print('Rev L BT30 router:', len(model.parts), 'components', flush=True)
    router = export(model, OUT, 'RevLBT30_ROUTER', individual=False)
    rev_j.write_mesh(model, 'RevLBT30_ROUTER')
    new = build_revl.sub_model(model, lambda i: is_new(model.find(i)))
    parts = export(new, OUT, 'RevLBT30_NEW_PARTS', individual=True)
    plasma, details['plasma_head'] = plasma_model(model)
    print('Rev L BT30 plasma:', len(plasma.parts), 'components', flush=True)
    parked = export(plasma, OUT, 'RevLBT30_PLASMA', individual=False)
    rev_j.write_mesh(plasma, 'RevLBT30_PLASMA')
    change, change_details = build_model(gantry_y=POCKET_GANTRY_Y, head_x=bt30.POCKET_X[2], z_lift=bt30.Z_ENGAGE, atc_travel=0.0, held_tool=False)
    rev_j.write_mesh(change, 'RevLBT30_TOOL_CHANGE')
    rev_j.write_mesh(build_revl.sub_model(change, lambda i: build_revl.near_dock(change.find(i))), 'RevLBT30_DOCK_DETAIL')
    lift, lift_details = build_model(atc_travel=0.0)
    module = rev_j.module_only(lift)
    alone = export(module, OUT, 'RevLBT30_BED_MODULE', individual=False)
    rev_j.write_mesh(module, 'RevLBT30_BED_MODULE')
    dock = build_revl.sub_model(lift, lambda i: i.startswith(atc_revl.PREFIX))
    dock_r = export(dock, OUT, 'RevLBT30_DOCK', individual=False)
    details['tool_change_pose'] = {'gantry_y': POCKET_GANTRY_Y, 'head_x': bt30.POCKET_X[2], 'z_lift': bt30.Z_ENGAGE, 'held_tool': False,
                                   'note': 'spindle nose at the gauge line of the holder in pocket 3',
                                   'atc': change_details['atc'], 'part_count': len(change.parts)}
    details['bed_change_module'] = {'bed': lift_details['bed'], 'atc': lift_details['atc'], 'part_count': len(module.parts)}
    details['state_checks'] = {
        key: {'part_count': r['part_count'], 'step_readback': r['step_readback'],
              'unresolved_intersections': r['unresolved_intersections']}
        for key, r in [('router_dock_parked', router), ('new_parts', parts), ('plasma', parked),
                       ('bed_module_dock_deployed', alone), ('dock_deployed', dock_r)]}
    details['holds'] = sorted(set(model.holds) | set(plasma.holds))
    after = source_hashes()
    details['source_sha256'] = after
    details['sources_changed_during_build'] = {k: v for k, v in before.items() if after.get(k) != v}
    details['elapsed_seconds'] = round(time.monotonic() - start, 2)
    clashes = [len(r['unresolved_intersections']) for r in (router, parts, parked, alone, dock_r)]
    details['integrated_geometry_pass'] = not any(clashes) and not details['sources_changed_during_build']
    (OUT / 'engineering-manifest.json').write_text(json.dumps(details, indent=2, default=str) + '\n', encoding='utf-8')
    print('Exported; unresolved clashes (router, new parts, plasma, module, dock):', clashes, flush=True)
    return 0 if details['integrated_geometry_pass'] else 2


if __name__ == '__main__':
    try:
        code = main()
    except Exception:
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
