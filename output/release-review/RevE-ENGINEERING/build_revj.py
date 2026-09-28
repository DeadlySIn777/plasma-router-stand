"""GM1 Rev J working CAD: one-piece hoisted router bed module.

Rev J is the owner's one-piece bed (`bed_revj.py`, first published in this
branch as "Rev H") combined with the other session's Rev H water-service and
Z-adapter work from the base branch:
  water_revj.py         Rev H hatches, washout and drain reserves (water_completion.py)
                        with the refill spout moved clear of the module
  motion_completion.py  Rev H Z-adapter transfer blank and braked-motor candidate
The Rev H six-panel bed and its storage restraints (bed_completion.py) are not used.

Exports three states to ../RevJ-CAD:
  RevJ_ROUTER         module installed, router head (full cut list and DXF)
  RevJ_PLASMA_LAYOUT  module out of the machine, spindle and bolts stored
  RevJ_BED_MODULE     the lifted module alone (what the hoist carries)
Unknown purchased interfaces stay guarded; no manufacturing readiness is implied.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
import time

import numpy as np

from cad_helpers import Model, export, place
from build_reve_engineering import build_model as build_legacy_frame
from build_revg import clone_model, store_router_tool

SOURCE = Path(__file__).resolve().parent
OUT = SOURCE.parent / 'RevJ-CAD'
MACHINE = 'GM1 — Garcia Mechanical Table'


def add_motion(model, gantry_y=1275.0, head_x=575.0, z_lift=100.0):
    """Router motion at one pose, then the Rev H Z-adapter blank and braked-motor candidate."""
    from motion_details import make_motion
    import motion_completion
    motion = make_motion(model, gantry_y=gantry_y, head_x=head_x, z_lift=z_lift, tool='router')
    completion = motion_completion.extend_router_model(model)
    motion['holds'] = completion['active_motion_holds']
    return motion, completion


def build_model(with_motion=True, gantry_y=1275.0, head_x=575.0, z_lift=100.0):
    from bed_revj import make_bed
    import water_revj
    model, details = build_legacy_frame(bed_builder=make_bed, with_motion=False, legacy_tool_parking=False)
    details['water_completion'] = water_revj.extend_router_model(model)
    if with_motion:
        details['motion'], details['motion_completion'] = add_motion(model, gantry_y, head_x, z_lift)
    model.holds.extend([
        'Rev J one-piece module: owner hoist, beam, trolley and sling ratings, and the module stand, are owner scope and not modeled.',
        'The owned torch barrel/clamping zone, nozzle datum and lead connection are not measured. No compatible torch mount, floating head or breakaway assembly is released.',
        'This revision is nominal CAD geometry. Frame/tool/work stiffness, joint capacities, purchased interfaces and physical commissioning remain separate release requirements.',
    ])
    for part in model.parts:
        if part.id == 'HW_BOLT_BIN_FLOOR':
            part.notes = ['Holds the removed spindle-clamp screws and the four lift shackles. The six Rev J drawdowns use their own tray on the reservoir lid.']
    details['machine'] = MACHINE
    details['revision'] = 'J working design: one-piece bed module with the Rev H water service and Z adapter'
    details['revision_note'] = ('First published in this branch as Rev H. Renamed Rev J on 26 September 2026 because the base '
                                'branch carries a different Rev H (six-panel bed); Rev I is skipped. Rev J adds that Rev H water '
                                'service and Z-adapter work, moves the refill spout clear of the module and sets the module end '
                                'crossmembers and deck 15 mm rearward.')
    details['status'] = 'WORKING CAD — NOT A FABRICATION RELEASE'
    details['architecture_assumption'] = details['bed']['architecture_assumption']
    details['tool_parking']['handling'] = (
        'Spindle rests in the existing internal cradle; its clamp screws and the lift shackles go in the existing '
        'hardware bin, the six drawdowns in the Rev J bolt tray. Exact lead routes remain open.')
    return model, details


def plasma_layout(source):
    """Module out of the machine, drawdowns in their tray, router tool stored."""
    from bed_revj import bolt_tray_positions
    model = clone_model(source)
    model.parts = [p for p in model.parts if not p.id.startswith('MOD_')]
    labels = [f'{side}_{station}' for side in 'LR' for station in (1, 2, 3)]
    for (x0, y, z), label in zip(bolt_tray_positions(), labels):
        bolt = model.find('BED_M10_' + label)
        washer = model.find('BED_M10_WASHER_' + label)
        bolt.shape = place(bolt.local, (x0, y, z), u=(0, 1, 0), v=(0, 0, 1))
        washer.shape = place(washer.local, (x0 + 78, y, z), u=(0, 1, 0), v=(0, 0, 1))
        for part in (bolt, washer):
            part.group = 'stored_hardware'
            part.notes = list(part.notes) + ['Stored in the Rev J bolt tray while the module is out of the machine.']
    return store_router_tool(model)


def module_only(source):
    model = clone_model(source)
    model.parts = [p for p in model.parts if p.id.startswith('MOD_')]
    model.allowed_intersections = {k: v for k, v in model.allowed_intersections.items()
                                   if all(i.startswith('MOD_') for i in k)}
    return model


def write_mesh(model, name):
    dest = OUT / 'previews'
    dest.mkdir(parents=True, exist_ok=True)
    vertices, triangles, colors = [], [], []
    offset = 0
    for part in model.parts:
        points, faces = part.shape.tessellate(.7, .25)
        v = np.array([p.toTuple() for p in points], dtype=np.float32)
        f = np.asarray(faces, dtype=np.int32)
        if not len(f):
            continue
        vertices.append(v)
        triangles.append(f + offset)
        offset += len(v)
        rgb = np.asarray(part.color) * 255
        if part.group in ('main_frame', 'bracing', 'rail_cap', 'controls_shield'):
            rgb = np.array([65, 77, 83])
        colors.append(np.tile(rgb.astype(np.uint8), (len(f), 1)))
    np.savez_compressed(dest / (name + '.npz'), vertices=np.concatenate(vertices),
                        triangles=np.concatenate(triangles), colors=np.concatenate(colors))


def main():
    start = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=True)
    model, details = build_model()
    print('Rev J router:', len(model.parts), 'components', flush=True)
    router = export(model, OUT, 'RevJ_ROUTER', individual=True)
    write_mesh(model, 'RevJ_ROUTER')
    plasma = plasma_layout(model)
    print('Rev J plasma layout:', len(plasma.parts), 'components', flush=True)
    parked = export(plasma, OUT, 'RevJ_PLASMA_LAYOUT', individual=False)
    write_mesh(plasma, 'RevJ_PLASMA_LAYOUT')
    module = module_only(model)
    print('Rev J bed module:', len(module.parts), 'components', flush=True)
    alone = export(module, OUT, 'RevJ_BED_MODULE', individual=False)
    write_mesh(module, 'RevJ_BED_MODULE')
    details['state_checks'] = {
        key: {'part_count': result['part_count'], 'step_readback': result['step_readback'],
              'unresolved_intersections': result['unresolved_intersections']}
        for key, result in [('router', router), ('plasma_layout_module_out', parked), ('bed_module_alone', alone)]}
    details['holds'] = sorted(set(model.holds))
    details['plasma_layout_scope'] = (
        'Bed module outside the machine; spindle, clamp hardware and drawdowns stored inside. The actual plasma '
        'torch and head are still missing, so this is a layout state, not an operational plasma assembly.')
    details['source_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCE.glob('*.py'))}
    details['elapsed_seconds'] = round(time.monotonic() - start, 2)
    (OUT / 'engineering-manifest.json').write_text(json.dumps(details, indent=2) + '\n', encoding='utf-8')
    clashes = [len(r['unresolved_intersections']) for r in (router, parked, alone)]
    print('Exported three states; unresolved clashes (router, plasma, module):', clashes, flush=True)
    return 0 if not any(clashes) else 2


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
