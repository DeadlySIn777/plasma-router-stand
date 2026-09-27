"""GM1 Rev L working CAD: Rev K with the 300 mm Z slide and a RapidChange dock on the bed module.

Rev L is Rev K (`../RevK-ENGINEERING/build_revk.py`, used unchanged) plus:
  z300.py       the ZBX80 with a 300 mm stroke (lower datum kept, body grows upward)
  atc_revl.py   a retracting magazine carrier that rides on the one-piece bed module
  ballast_revl.py  the frame's fill ports moved to each tube's high end (epoxy or dry sand)
The sources live in this folder, so the Rev K and shared RevE-ENGINEERING inventories are unchanged.
Exports to ../RevL-CAD:
  RevL_ROUTER       dock parked, gantry at the rear stop, head X575, Z fully up (assembly STEP)
  RevL_BED_MODULE   the module with the dock deployed, as lifted for a bed change
  RevL_DOCK         the dock alone, deployed (assembly STEP)
  RevL_NEW_PARTS    the dock's parts, the 300 mm Z body and the frame tubes, caps and fill ports whose
                    ports moved: cut list, part STEP files and DXF
  previews          router (dock parked), tool change (dock deployed), bed module, dock close-up
The plasma state is Rev K's with the longer Z; verify_revl.py checks it and it is not re-exported.
Unknown purchased interfaces stay guarded; no manufacturing release is implied.
"""
from pathlib import Path
import copy
import hashlib
import json
import os
import sys
import time

HERE = Path(__file__).resolve().parent
REVK = HERE.parent / 'RevK-ENGINEERING'
LEGACY = HERE.parent / 'RevE-ENGINEERING'
for path in (str(LEGACY), str(REVK), str(HERE)):
    if path not in sys.path:
        sys.path.insert(0, path)

from cad_helpers import Model, bbox, export  # noqa: E402
import build_revj as rev_j  # noqa: E402
import build_revk  # noqa: E402
import atc_revl  # noqa: E402
import ballast_revl  # noqa: E402
import z300  # noqa: E402

OUT = HERE.parent / 'RevL-CAD'
MACHINE = rev_j.MACHINE
POCKET_GANTRY_Y = atc_revl.POCKET_Y + 153.6      # spindle axis Y = gantry Y - 153.6
DOCK_X = 975.0                                   # head X while the dock moves: Z body clear of the magazine


def source_hashes():
    files = sorted(HERE.glob('*.py')) + sorted(REVK.glob('*.py')) + sorted(LEGACY.glob('*.py'))
    return {f'{p.parent.name}/{p.name}': hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def module_with_dock(bed, atc):
    """Rev J module mass and centre of mass, plus the dock in its modeled position."""
    m0, c0 = bed['module_mass_estimate_kg'], bed['module_cg_mm']
    m1, c1 = atc['mass_kg'], atc['cg_mm']
    total = m0 + m1
    cg = [round((m0 * c0[i] + m1 * c1[i]) / total, 1) for i in range(3)]
    result = copy.deepcopy(bed)
    result.update(module_mass_estimate_kg=round(total, 1), module_cg_mm=cg,
                  module_without_dock={'mass_kg': m0, 'cg_mm': c0},
                  dock_state_for_mass=atc['travel_state'])
    return result


def build_model(with_motion=True, gantry_y=1275.0, head_x=575.0, z_lift=z300.STROKE, atc_travel=atc_revl.TRAVEL):
    model, details = build_revk.build_model(with_motion=False)
    details['frame_fill'] = ballast_revl.apply(model)
    details['atc'] = atc_revl.extend_router_model(model, travel=atc_travel)
    if with_motion:
        details['motion'], details['motion_completion'] = z300.add_motion(model, gantry_y, head_x, z_lift)
    build_revk.purchased_material(model)
    details['bed_rev_j'] = details['bed']
    details['bed'] = module_with_dock(details['bed'], details['atc'])
    model.holds.append('Z slide: the 300 mm ZBX80 is drawn from the 100 mm listing drawing (body = stroke + 119). '
                       'Measure the delivered body, carriage and end blocks before the adapter and stops are made.')
    details['machine'] = MACHINE
    details['revision'] = 'L working design: Rev K with a 300 mm Z and a RapidChange dock on the bed module'
    details['status'] = 'WORKING CAD - NOT A FABRICATION RELEASE'
    return model, details


def plasma_model(router_model, **head):
    return build_revk.plasma_model(router_model, **head)


def sub_model(source, keep):
    m = Model()
    m.parts = [copy.copy(p) for p in source.parts if keep(p.id)]
    ids = {p.id for p in m.parts}
    m.allowed_intersections = {k: v for k, v in source.allowed_intersections.items() if all(i in ids for i in k)}
    return m


def is_fill_part(part):
    """The frame tubes, ported end caps, bungs and plugs that Rev L's fill-port change touches."""
    return part.group == 'main_frame' or part.id.startswith(('SAND_BUNG_', 'SAND_PLUG_')) or \
        part.part_number == ballast_revl.CAP_PN


def near_dock(part):
    b = bbox(part.shape)
    return b[4] > 1000 and b[1] < 1460 and b[5] > 900 and b[2] < 1320 and b[3] > 200 and b[0] < 960


def main():
    start = time.monotonic()
    before = source_hashes()
    OUT.mkdir(parents=True, exist_ok=True)
    rev_j.OUT = OUT
    model, details = build_model()
    print('Rev L router:', len(model.parts), 'components', flush=True)
    router = export(model, OUT, 'RevL_ROUTER', individual=False)
    rev_j.write_mesh(model, 'RevL_ROUTER')
    new = sub_model(model, lambda i: i.startswith(atc_revl.PREFIX) or i == 'ZBX80_BASE' or is_fill_part(model.find(i)))
    parts = export(new, OUT, 'RevL_NEW_PARTS', individual=True)
    change, change_details = build_model(gantry_y=POCKET_GANTRY_Y, head_x=575.0, atc_travel=0.0)
    rev_j.write_mesh(change, 'RevL_TOOL_CHANGE')
    rev_j.write_mesh(sub_model(change, lambda i: near_dock(change.find(i))), 'RevL_DOCK_DETAIL')
    lift, lift_details = build_model(atc_travel=0.0)
    module = rev_j.module_only(lift)
    alone = export(module, OUT, 'RevL_BED_MODULE', individual=False)
    rev_j.write_mesh(module, 'RevL_BED_MODULE')
    dock = sub_model(lift, lambda i: i.startswith(atc_revl.PREFIX))
    dock_r = export(dock, OUT, 'RevL_DOCK', individual=False)
    details['tool_change_pose'] = {'gantry_y': POCKET_GANTRY_Y, 'head_x': 575.0, 'z_lift': z300.STROKE,
                                   'atc': change_details['atc'], 'part_count': len(change.parts)}
    details['bed_change_module'] = {'bed': lift_details['bed'], 'atc': lift_details['atc'], 'part_count': len(module.parts)}
    details['state_checks'] = {
        key: {'part_count': r['part_count'], 'step_readback': r['step_readback'],
              'unresolved_intersections': r['unresolved_intersections']}
        for key, r in [('router_dock_parked', router), ('new_parts', parts), ('bed_module_dock_deployed', alone),
                       ('dock_deployed', dock_r)]}
    details['holds'] = sorted(set(model.holds))
    after = source_hashes()
    details['source_sha256'] = after
    details['sources_changed_during_build'] = {k: v for k, v in before.items() if after.get(k) != v}
    details['elapsed_seconds'] = round(time.monotonic() - start, 2)
    clashes = [len(r['unresolved_intersections']) for r in (router, parts, alone, dock_r)]
    details['integrated_geometry_pass'] = not any(clashes) and not details['sources_changed_during_build']
    (OUT / 'engineering-manifest.json').write_text(json.dumps(details, indent=2, default=str) + '\n', encoding='utf-8')
    print('Exported; unresolved clashes (router, new parts, module, dock):', clashes, flush=True)
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
