"""Corrected Rev G working CAD, exported separately from historical Rev E/F.

The bed change is manual and remains a design assumption pending owner choice.
Unknown purchased interfaces are guarded; no manufacturing readiness is implied.
"""
from pathlib import Path
import copy
import hashlib
import json
import os
import sys
import time

import cadquery as cq
import numpy as np

from cad_helpers import Model, bbox, export, place
from build_reve_engineering import build_model as build_legacy_frame

SOURCE = Path(__file__).resolve().parent
OUT = SOURCE.parent / 'RevG-CAD'


def build_model(with_motion=True):
    from bed_cassettes import make_bed
    model, details = build_legacy_frame(
        bed_builder=make_bed, with_motion=with_motion,
        legacy_tool_parking=False)
    model.holds.extend([
        'Manual panel conversion is the working architecture, pending the owner preference requested on 25 September 2026.',
        'The owned torch barrel/clamping zone, nozzle datum and lead connection are not measured. No compatible torch mount, floating head or breakaway assembly is released.',
        'This revision corrects nominal CAD geometry. Full frame/tool/work stiffness, joint capacities, purchased interfaces and physical commissioning remain separate release requirements.',
    ])
    details['revision'] = 'G working repair'
    details['status'] = 'CORRECTED WORKING CAD — NOT A FABRICATION RELEASE'
    details['architecture_assumption'] = 'Manual small panels, beams and separate spoilboards; all stored in the machine. Owner preference pending.'
    details['tool_parking']['handling'] = (
        'Spindle rests in the existing internal cradle. Removed clamps and small '
        'fasteners use the lid/tray in the bed-stored layout. Exact lead routes remain open.')
    return model, details


def clone_model(source):
    model = Model()
    model.holds = list(source.holds)
    model.allowed_intersections = source.allowed_intersections.copy()
    for part in source.parts:
        copied = copy.copy(part)
        copied.notes = list(part.notes)
        copied.flat = copy.deepcopy(part.flat)
        model.parts.append(copied)
    return model


def store_router_tool(source):
    """Geometric storage layout; spindle disconnected and clamp removed first.

    The bare adapter remains at the Z carriage. There is deliberately no invented
    torch, so this state is named BED_STORED rather than operational plasma.
    """
    model = clone_model(source)
    hardware_index = 0
    for part in model.parts:
        if part.id == 'TOOL_SPINDLE_65x259':
            part.shape = place(part.local, (760.5,1080,599.7), u=(0,1,0), v=(0,0,1))
            part.group = 'stored_tool'
        elif part.id in ('TOOL_SPLIT_CLAMP_REAR', 'TOOL_SPLIT_CLAMP_FRONT'):
            y = 1180 if part.id.endswith('REAR') else 1230
            part.shape = place(part.local, (300,y,433.096))
            part.group = 'stored_tool'
        elif part.id.startswith(('TOOL_CLAMP_MOUNT_', 'TOOL_CLAMP_PINCH_')):
            # Two long pinch screws lie along X; four small mount screws stand
            # in the existing shallow tray. The model includes their heads.
            if part.id.startswith('TOOL_CLAMP_PINCH_'):
                index = int(part.id.rsplit('_',1)[1])
                part.shape = place(part.local, (815,767+18*index,441.144), u=(0,1,0), v=(0,0,1))
            else:
                part.shape = place(part.local, (910+18*hardware_index,742,436.144), u=(1,0,0), v=(0,1,0))
                hardware_index += 1
            part.group = 'stored_hardware'
    return model


def stored_model(source):
    from bed_cassettes import stored_bed_model
    return store_router_tool(stored_bed_model(source))


def write_mesh(model, name):
    dest = OUT/'previews'
    dest.mkdir(parents=True,exist_ok=True)
    vertices, triangles, colors = [], [], []
    offset = 0
    for part in model.parts:
        points, faces = part.shape.tessellate(.7,.25)
        v = np.array([p.toTuple() for p in points], dtype=np.float32)
        f = np.asarray(faces,dtype=np.int32)
        if not len(f):
            continue
        vertices.append(v)
        triangles.append(f+offset)
        offset += len(v)
        rgb = np.asarray(part.color)*255
        if part.group in ('main_frame','bracing','rail_cap','controls_shield'):
            rgb = np.array([65,77,83])
        colors.append(np.tile(rgb.astype(np.uint8),(len(f),1)))
    np.savez_compressed(dest/(name+'.npz'),vertices=np.concatenate(vertices),
                        triangles=np.concatenate(triangles),colors=np.concatenate(colors))


def main():
    start = time.monotonic()
    OUT.mkdir(parents=True,exist_ok=True)
    model, details = build_model()
    print('Rev G router:',len(model.parts),'components',flush=True)
    router = export(model,OUT,'RevG_ROUTER',individual=True)
    write_mesh(model,'RevG_ROUTER')
    stored = stored_model(model)
    print('Rev G bed stored:',len(stored.parts),'components',flush=True)
    parked = export(stored,OUT,'RevG_BED_STORED',individual=False)
    write_mesh(stored,'RevG_BED_STORED')
    # Show actual panel storage and receiver details without moving motion parts
    # out of the way and falsely treating the exploded view as an assembly.
    section = Model()
    section.parts = [p for p in stored.parts if p.group not in (
        'motion_purchased','gantry','gantry_hardware','removable_tool','rail_cap')
        and not p.id.startswith(('HMS','Y_','X_','ZBX','GANTRY','TOOL_ADAPTER'))]
    write_mesh(section,'RevG_STORAGE_DETAIL')
    details['state_checks'] = {
        key:{'part_count':result['part_count'], 'step_readback':result['step_readback'],
             'unresolved_intersections':result['unresolved_intersections']}
        for key,result in [('router',router),('bed_stored_layout',parked)]}
    details['holds'] = sorted(set(model.holds))
    details['bed_stored_state_scope'] = (
        'Router bed and tools stored inside the frame. The actual plasma tool '
        'is still missing; this is a storage/layout configuration, not an operational plasma assembly.')
    details['source_sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in SOURCE.glob('*.py')}
    details['elapsed_seconds'] = round(time.monotonic()-start,2)
    (OUT/'engineering-manifest.json').write_text(json.dumps(details,indent=2)+'\n',encoding='utf-8')
    print('Exported both states;', 'router clashes',len(router['unresolved_intersections']),
          'stored clashes',len(parked['unresolved_intersections']),flush=True)
    return 0 if not router['unresolved_intersections'] and not parked['unresolved_intersections'] else 2


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
