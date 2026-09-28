"""GM1 Rev L, rotary variant: Rev L (ER11) with the tube-notching rotary axis on the front of the frame (rotary_revl.py).

Rev L's sources (`../RevL-ENGINEERING`, `../RevK-ENGINEERING`, `../RevE-ENGINEERING`) are used unchanged; this folder
holds only the rotary. Exports to ../RevL-ROTARY-CAD:
  RevLROT_ROUTER      router mode with the rotary fitted: dock parked, gantry at the rear stop, head X575, Z up (assembly STEP)
  RevLROT_PLASMA      module and dock out, a Ø60 tube in the chuck, the torch 4 mm over its top at Y575 (assembly STEP)
  RevLROT_NEW_PARTS   the bracket (cross tube, stubs, shelf plate) and the two allocations: cut list, part STEP and DXF
  previews            router, plasma with the tube (two views), the shelf close-up
The rotary and the chuck are allocations; no manufacturing release is implied.
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

from cad_helpers import bbox, export  # noqa: E402
import build_revj as rev_j  # noqa: E402
import build_revk  # noqa: E402
import build_revl  # noqa: E402
import atc_revl  # noqa: E402
import ballast_revl  # noqa: E402
import z300  # noqa: E402
import rotary_revl as rotary  # noqa: E402

OUT = HERE.parent / 'RevL-ROTARY-CAD'
MACHINE = rev_j.MACHINE
TUBE_GANTRY_Y = 575.0 + 201.4          # torch axis on the tube at Y575
CUT_STANDOFF = 4.0                     # torch tip over the tube top in the plasma export


def source_hashes():
    own = {f'{p.parent.name}/{p.name}': hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob('*.py'))}
    return {**build_revl.source_hashes(), **own}


def build_model(with_motion=True, gantry_y=1275.0, head_x=575.0, z_lift=z300.STROKE, atc_travel=atc_revl.TRAVEL, tube_length=None,
                tube_d=rotary.TUBE_D):
    """Rev L with the rotary on the frame. A tube in the chuck only makes sense with the module out (plasma)."""
    model, details = build_revk.build_model(with_motion=False)
    details['frame_fill'] = ballast_revl.apply(model)
    details['rotary'] = rotary.extend_model(model, tube_length, tube_d)
    details['atc'] = atc_revl.extend_router_model(model, travel=atc_travel)
    if with_motion:
        details['motion'], details['motion_completion'] = z300.add_motion(model, gantry_y, head_x, z_lift)
    build_revk.purchased_material(model)
    details['bed_rev_j'] = details['bed']
    details['bed'] = build_revl.module_with_dock(details['bed'], details['atc'])
    details['rotary']['bracket_and_unit_mass_kg'] = rotary.mass_kg(model)
    details['machine'] = MACHINE
    details['revision'] = 'L working design, rotary variant: Rev L with a tube-notching rotary axis on the front of the frame'
    details['status'] = 'WORKING CAD - NOT A FABRICATION RELEASE'
    return model, details


def plasma_model(router_model, **head):
    import plasma_drop
    stored = rev_j.plasma_layout(router_model)
    model, details = plasma_drop.plasma_head_model(stored, **head)
    build_revk.purchased_material(model)
    return model, details


def near_shelf(part):
    """The shelf close-up: the bracket, the rotary, the tube's first metre and the front legs, without the pan wall."""
    b = bbox(part.shape)
    return b[1] < 60 and b[4] > -300 and b[0] < 1160 and b[3] > -10 and b[5] > 700


def main():
    start = time.monotonic()
    before = source_hashes()
    OUT.mkdir(parents=True, exist_ok=True)
    rev_j.OUT = OUT
    model, details = build_model()
    print('Rev L rotary router:', len(model.parts), 'components', flush=True)
    router = export(model, OUT, 'RevLROT_ROUTER', individual=False)
    rev_j.write_mesh(model, 'RevLROT_ROUTER')
    new = build_revl.sub_model(model, lambda i: i.startswith(rotary.PREFIX))
    parts = export(new, OUT, 'RevLROT_NEW_PARTS', individual=True)
    # plasma with the tube: find the tip at z 0, then set the torch 4 mm over the tube top
    probe, probe_details = build_model(gantry_y=TUBE_GANTRY_Y, head_x=rotary.AXIS_X, z_lift=0.0, tube_length=rotary.TUBE_L)
    _, head0 = plasma_model(probe)
    tube_top = probe_details['rotary']['tube']['top_z_mm']
    z_cut = round(tube_top + CUT_STANDOFF - head0['tip_z_mm'], 3)
    with_tube, tube_details = build_model(gantry_y=TUBE_GANTRY_Y, head_x=rotary.AXIS_X, z_lift=z_cut, tube_length=rotary.TUBE_L)
    plasma, details['plasma_head'] = plasma_model(with_tube)
    print('Rev L rotary plasma:', len(plasma.parts), 'components, torch tip', details['plasma_head']['tip_z_mm'], 'over the tube top', tube_top, flush=True)
    parked = export(plasma, OUT, 'RevLROT_PLASMA', individual=False)
    rev_j.write_mesh(plasma, 'RevLROT_PLASMA')
    rev_j.write_mesh(build_revl.sub_model(plasma, lambda i: near_shelf(plasma.find(i))), 'RevLROT_SHELF_DETAIL')
    details['rotary']['tube'] = tube_details['rotary']['tube']
    details['tube_pose'] = {'gantry_y': TUBE_GANTRY_Y, 'head_x': rotary.AXIS_X, 'z_lift': z_cut, 'torch_tip_z_mm': details['plasma_head']['tip_z_mm'],
                            'tip_z_at_z_lift_0_mm': head0['tip_z_mm'], 'standoff_mm': CUT_STANDOFF, 'part_count': len(plasma.parts)}
    details['state_checks'] = {
        key: {'part_count': r['part_count'], 'step_readback': r['step_readback'], 'unresolved_intersections': r['unresolved_intersections']}
        for key, r in [('router_rotary_fitted', router), ('new_parts', parts), ('plasma_with_tube', parked)]}
    details['holds'] = sorted(set(model.holds) | set(plasma.holds))
    after = source_hashes()
    details['source_sha256'] = after
    details['sources_changed_during_build'] = {k: v for k, v in before.items() if after.get(k) != v}
    details['elapsed_seconds'] = round(time.monotonic() - start, 2)
    clashes = [len(r['unresolved_intersections']) for r in (router, parts, parked)]
    details['integrated_geometry_pass'] = not any(clashes) and not details['sources_changed_during_build']
    (OUT / 'engineering-manifest.json').write_text(json.dumps(details, indent=2, default=str) + '\n', encoding='utf-8')
    print('Exported; unresolved clashes (router, new parts, plasma):', clashes, flush=True)
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
