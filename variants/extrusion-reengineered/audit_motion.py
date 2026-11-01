"""Reproduce XR1 motion interface evidence; optionally regenerate its takeoff.

Run with the repository's CadQuery Python environment from any directory:
    python variants/extrusion-reengineered/audit_motion.py
    python variants/extrusion-reengineered/audit_motion.py --manifest

No STEP/DXF exports, purchases, prices or geometry-source mutations occur.
The main build/check_travel scripts separately rebuild actual travel poses.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import csv
import hashlib
import json
import os
import sys

import motion
import params as P
from frame import frame_parts
from cad_helpers import Model, bbox
from motion_details import make_motion
from motion_completion import apply_completion
from motion_finish import make_head

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = HERE / 'interface-audit.json'
MANIFEST = HERE / 'motion-fabrication.csv'
NEW_FIXED = ('XR_SADDLE_', 'XR_STOP_')
NEW_BRACKETS = ('GANTRY_END_BRACKET_', 'Y_LINK_SUPPORT_')
FIELDS = ['id', 'category', 'quantity', 'part_number',
          'minimum_blank_or_local_envelope_mm', 'material',
          'ownership_credit', 'notes']
CUSTOM = 'CUSTOM_MANUFACTURE_VERIFY_OWNED'
STANDARD = 'STANDARD_FASTENER_VERIFY_OWNED'
PURCHASED = 'PURCHASED_INTERFACE_VERIFY_OWNED'


def dimensions(shape):
    b = bbox(shape)
    return [round(b[k+3]-b[k], 6) for k in range(3)]


def overlap(a, b):
    return all(min(a[k+3], b[k+3])-max(a[k], b[k]) > 1e-5
               for k in range(3))


def exact_pairs(a, b):
    """All cross-list candidates, with no broad mating/thread exclusions."""
    ba = {n:bbox(s) for n,s,_ in a}
    bb = {n:bbox(s) for n,s,_ in b}
    hits, count = [], 0
    for n,s,_ in a:
        for k,t,_ in b:
            if not overlap(ba[n], bb[k]):
                continue
            count += 1
            volume = s.intersect(t).Volume()
            if volume > .05:
                hits.append(dict(a=n, b=k, volume_mm3=round(volume, 5)))
    return dict(exact_pairs=count, hits=hits)


def nominal_hms_thread(a, b, volume):
    """Only the source hms() permit for each module's own four shoe screws."""
    if volume > 31.5:
        return False
    for axis in ('Y_L', 'Y_R', 'X'):
        body = f'HMS_{axis}_BODY'
        screws = {f'HMS_{axis}_SHOE_BOLT_{i}' for i in range(1, 5)}
        if (a == body and b in screws) or (b == body and a in screws):
            return True
    return False


def cross_class_check(parts):
    bounds = {n:bbox(s) for n,s,_ in parts}
    raw, count = [], 0
    for i,(n,s,_) in enumerate(parts):
        for k,t,_ in parts[i+1:]:
            if motion.part_motion_class(n) == motion.part_motion_class(k):
                continue
            if not overlap(bounds[n], bounds[k]):
                continue
            count += 1
            volume = s.intersect(t).Volume()
            if volume <= .05:
                continue
            permit = None
            if nominal_hms_thread(n, k, volume):
                permit = ('HMS carriage thread enters the conservative module-body '
                          'envelope; specific frozen motion_details.hms() permit.')
            raw.append(dict(a=n, b=k, volume_mm3=round(volume, 5),
                            specific_source_permit=permit))
    return dict(exact_pairs=count, raw_positive_pairs=raw,
                unpermitted_pairs=[r for r in raw if not r['specific_source_permit']])


def targeted_poses():
    x0, x1 = 575-P.X_TRAVEL/2, 575+P.X_TRAVEL/2
    y0, y1 = 775-P.Y_TRAVEL/2, 775+P.Y_TRAVEL/2
    middle = P.Z_TRAVEL/2
    return [(y0,575,middle), (775,575,middle), (y1,575,middle),
            (y0,x0,0), (y0,x1,P.Z_TRAVEL), (775,x0,P.Z_TRAVEL),
            (775,x1,0), (y1,x0,P.Z_TRAVEL), (y1,x1,0)]


def targeted_fixed_vs_moving(parts):
    """Supplementary rigid-translation checks of the new fixed mounts.

    Class signatures are separately checked by the actual pose travel audit.
    No virtual translation is applied to a component classified stationary.
    """
    fixed = [(n,s,bbox(s)) for n,s,_ in parts if n.startswith(NEW_FIXED)]
    moving = [(n,s,bbox(s),motion.part_motion_class(n))
              for n,s,_ in parts if not motion.is_stationary(n)]
    records = []
    for gy,hx,zl in targeted_poses():
        hits, count = [], 0
        for n,s,b in fixed:
            for k,t,q,cls in moving:
                dx = hx-575 if cls in ('Y_X_head', 'Y_X_Z_tool') else 0
                dz = zl-P.Z_TRAVEL/2 if cls == 'Y_X_Z_tool' else 0
                delta = (dx, gy-775, dz)
                dest = [q[i]+delta[i % 3] for i in range(6)]
                if not overlap(b, dest):
                    continue
                count += 1
                volume = s.intersect(t.translate(delta)).Volume()
                if volume > .05:
                    hits.append(dict(a=n, b=k, volume_mm3=round(volume, 5)))
        records.append(dict(gantry_y=gy, head_x=hx, z_lift=zl,
                            exact_pairs=count, hits=hits))
    return records


def source_metadata():
    """Call geometry builders only, never the inherited release/export scripts."""
    model = Model()
    make_motion(model, gantry_y=775, head_x=575,
                z_lift=P.Z_TRAVEL/2, tool='router')
    apply_completion(model, replacement_brake_motor=False)
    head, _ = make_head(float_lift=0, breakaway_offset=0, torch=None)
    return {p.id:p for p in model.parts+head.parts}


def owned_catalogue_motion(part):
    # The user confirmed these purchased modules, guides, drives and spindle.
    # A custom bracket, fastener, rod end or floating-head component does not
    # acquire ownership merely because its parent group says "motion".
    if part.id == 'TOOL_SPINDLE_65x259':
        return True
    return (part.group == 'motion_purchased' and
            (part.id.startswith(('Y_RAIL_', 'Y_BLOCK_', 'X_RAIL_', 'X_BLOCK_',
                                 'HMS_Y_', 'HMS_X_', 'ZBX80_')) or
             part.id == 'GANTRY_8080'))


def row(ident, category, pn, size, material, notes, quantity=1):
    return dict(id=ident, category=category, quantity=quantity, part_number=pn,
                minimum_blank_or_local_envelope_mm=json.dumps(size),
                material=material,
                ownership_credit=('NONE until actual ownership or a complete '
                                  'nonoverlapping owned-stock nest is verified'),
                notes=notes)


def fabrication_rows(wood, plasma):
    """Regenerate the complete motion fabrication ledger without old CSV input."""
    metadata = source_metadata()
    selected = {n:(s,c) for n,s,c in wood+plasma}
    rows = []
    for name,(shape,_) in selected.items():
        if name in metadata:
            p = metadata[name]
            if p.purchased:
                if owned_catalogue_motion(p):
                    continue
                if p.part_number.startswith(('INCLUDED_', 'I_SWITCH_PLUNGER_')):
                    continue
                hardware = (p.group == 'motion_fasteners' or
                            any(t in p.part_number for t in
                                ('STD_', 'TNUT', 'WASHER', 'SHIM_')))
                category = STANDARD if hardware else PURCHASED
            else:
                category = CUSTOM
            note = ' | '.join(p.notes)
            if name.startswith('GANTRY_END_BRACKET_'):
                note += (' | XR1 selected integral billet: 150x80x82.7 finished '
                         'envelope; web8mm outward; raw billet needs machining '
                         'allowance and is not from the owned thin sheets.')
            elif name.endswith('_CLEVIS'):
                note += (' | XR1 selected integral40x48x32 billet; no ear/base '
                         'edge joint; raw stock needs machining allowance.')
            elif name.startswith('Y_SHOE_'):
                note += (' | XR1: translate8mm outward; link window49x7.35 '
                         'replaces33x7.35; supplier interfaces remain held.')
            elif name == 'X_GUIDE_FACE':
                note += (' | XR1: inherited long aluminum guide-face plate '
                         'unchanged; no assumed owned-sheet credit.')
            rows.append(row(name, category, p.part_number, dimensions(p.local),
                            p.material, note))
            continue

        material = 'Aluminum alloy/temper verification required'
        category, size = CUSTOM, dimensions(shape)
        note = 'XR1 candidate; actual manufactured joint/load proof held.'
        if '_PAD_' in name:
            size = [70,60,12.7]
            note += (' Two underside7.5x4mm M4 head pockets; six pads receive '
                     'owned-stock credit only through the complete cut nest.')
        elif '_SIDE_60' in name:
            size = [60,80,9.525]
        elif name.startswith('Y_LINK_SUPPORT_FLANGE_'):
            size = [99.8,48,6.35]
        elif name.startswith('Y_LINK_SUPPORT_WEB_'):
            size = [48,40,12.7]
        elif name.startswith('XR_PLASMA_DROP_'):
            size = [110,motion.PLASMA_DROP+70,12.7]
            note += (' Lower rear counterbores10.5x6; upperM6 taps. Real '
                     'torch grip and nozzle remain unmeasured.')
        elif name.startswith('XR_STOP_CARRIER_'):
            material = 'Uncoated low-carbon steel welded assembly,6/6.35mm nominal'
            note += (' FOUR cut pieces, not a deep billet: matching stop-base '
                     'landing6.35 thick, max43.3x71FRONT/43.3x50REAR; '
                     'sideleg6x36x55FRONT/6x36x42REAR; '
                     'floor6x30.2x55FRONT/6x30.2x42REAR; '
                     'tower6x25x48.5875. Weld detail/capacity remains held.')
        elif '_SPACER_6p4_' in name:
            size = [12,12,6.4]
            note += ' Solid compression spacer OD12/ID6.6/length6.4.'
        else:
            category, size = STANDARD, []
            material = 'Steel hardware; grade/coating/thread verification required'
            if 'EXTERNAL_GRIP' in name:
                note += (' CAD shows external grip/head only; in-slot thread '
                         'and T-nut geometry are interface holds.')
        rows.append(row(name, category, name, size, material, note))

    rows += [
        row('XR_MODULE_BOTTOM_M4_SLIDING_NUTS', STANDARD,
            'XR_MODULE_BOTTOM_M4_SLIDING_NUTS', [],
            'Steel hardware; exact HMS40 nut shape held',
            'TwoM4 bottom nuts per saddle; supplied count/cavity/engagement unverified.',12),
        row('XR_FRAME_M6_SLOT_NUTS', STANDARD, 'XR_FRAME_M6_SLOT_NUTS', [],
            'Steel hardware;40series8mm-slot fit held',
            '24saddle+8stop-carrier nuts; screw length follows real nut/root clearance.',32),
        row('XR_Y_RAIL_M5_FIXINGS', 'REQUIRED_HARDWARE_INTERFACE_HOLD',
            'XR_Y_RAIL_M5_FIXINGS', [], 'M5-compatible rail screws and slot nuts',
            'REQUIRED QUANTITY UNRESOLVED, NOT ZERO: use every inspected real '
            'HGR20 fixing hole. No invented factory pitch/end datum. A complete '
            'costable BOM requires this count or verified supplied hardware.',0),
    ]
    assert len({r['id'] for r in rows}) == len(rows), 'Duplicate manifest IDs'
    return rows


def run(write_manifest=False):
    report = motion.interface_metadata()
    for path in (Path(__file__), HERE/'frame.py'):
        report['source_sha256'][path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    wood = motion.motion_parts(False, z_lift=P.Z_TRAVEL/2)
    plasma = motion.motion_parts(True, z_lift=P.Z_TRAVEL/2)
    report['selective_billet'] = dict(
        gantry_end_brackets=2, gantry_finished_envelope_mm=[150,80,82.7],
        clevises=6, clevis_finished_envelope_mm=[40,48,32], gussets=0,
        long_guide_face_modified=False)
    report['targeted_kinematic_method'] = (
        'Supplementary rigidXYZ translations of centre solids using '
        'part_motion_class; no flexible cable or switch-roller simulation. '
        'The main check_travel.py rebuilds actual centre/corner poses. '
        'New integral brackets are analytically rigidY.')
    report['solid_checks'] = {
        label:dict(count=len(parts), invalid_ids=[n for n,s,_ in parts
            if not s.isValid() or len(s.Solids()) != 1 or s.Volume() <= 0])
        for label,parts in [('WOOD',wood),('PLASMA',plasma)]}
    report['targeted_new_stationary_vs_moving'] = targeted_fixed_vs_moving(wood)
    report['targeted_plasma_new_stationary_vs_moving'] = targeted_fixed_vs_moving(plasma)
    report['new_stationary_mounts_vs_frame'] = exact_pairs(
        [p for p in wood if p[0].startswith(NEW_FIXED)], frame_parts())
    report['new_gantry_and_link_brackets_vs_other_motion'] = exact_pairs(
        [p for p in wood if p[0].startswith(NEW_BRACKETS)],
        [p for p in wood if not p[0].startswith(NEW_BRACKETS)])
    report['cross_motion_class_center_current'] = cross_class_check(wood)
    if write_manifest:
        rows = fabrication_rows(wood, plasma)
        with MANIFEST.open('w', newline='', encoding='utf-8-sig') as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        report['manufacturing_manifest_rows'] = len(rows)
        report['manufacturing_row_categories'] = dict(Counter(r['category'] for r in rows))
        report['manufacturing_manifest_sha256'] = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    else:
        report['manufacturing_manifest_generation'] = 'Use --manifest to regenerate from geometry metadata.'
    current = {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
               for name in report['source_sha256']}
    report['source_unchanged_during_check'] = current == report['source_sha256']
    report['release'] = False
    report['limits'] = [
        'Supplier fits, actual rail fixing count, threads/pullout and physical stock remain held.',
        'No whole-machine stiffness, cutting accuracy or actual tool/torch clearance follows from these checks.',
        'Unknown rail holes, in-slot threads and nut solids are explicitly absent; required inventory is not zero.',
        'Budget and ownership are not inferred from CAD parts or the manifest.',
    ]
    failed = (any(r['invalid_ids'] for r in report['solid_checks'].values()) or
              any(r['hits'] for key in ('targeted_new_stationary_vs_moving',
                                       'targeted_plasma_new_stationary_vs_moving')
                  for r in report[key]) or
              report['new_stationary_mounts_vs_frame']['hits'] or
              report['new_gantry_and_link_brackets_vs_other_motion']['hits'] or
              report['cross_motion_class_center_current']['unpermitted_pairs'] or
              not report['source_unchanged_during_check'])
    report['targeted_checks_passed'] = not bool(failed)
    AUDIT.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(
        solids=report['solid_checks'], passed=report['targeted_checks_passed'],
        cross_class_raw=len(report['cross_motion_class_center_current']['raw_positive_pairs']),
        cross_class_unpermitted=len(report['cross_motion_class_center_current']['unpermitted_pairs']),
        manifest_rows=report.get('manufacturing_manifest_rows'))), flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', action='store_true',
                        help='Regenerate motion-fabrication.csv from current/source metadata.')
    options = parser.parse_args()
    try:
        code = run(options.manifest)
    except Exception:
        import traceback
        traceback.print_exc()
        code = 2
    sys.stdout.flush()
    sys.stderr.flush()
    # Match this repository's OCCT lifecycle workaround.
    os._exit(code)
