"""Read-only source/export audit; writes evidence only beside this script.

Requires CadQuery 2.7 and ezdxf 1.4. Run from any directory. No CAD generator
main(), export, machine connection or fabrication action is invoked.
"""
from pathlib import Path
from collections import Counter, defaultdict
import ast
import hashlib
import json
import math
import os
import sys
import tempfile
import time

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[1]
CAD = REPO / 'output/release-review/RevE-ENGINEERING'
sys.path.insert(0, str(CAD))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def inventory():
    extensions = {'.step', '.stp', '.dxf', '.f3d', '.f3z', '.stl', '.3mf'}
    files = []
    for p in sorted(REPO.rglob('*')):
        if p.is_file() and p.suffix.lower() in extensions:
            rel = p.relative_to(REPO).as_posix()
            files.append({'file': rel, 'bytes': p.stat().st_size, 'sha256': sha(p),
                          'scope': 'current_engineering' if p.is_relative_to(CAD)
                          else 'historical_or_other'})
    sources = sorted(CAD.glob('*.py'))
    sources += [REPO / name for name in ('build_design.py', 'build_bed_system.py',
               'build_concept_current.py', 'render_cad.py')]
    syntax = []
    for p in sources:
        try:
            ast.parse(p.read_text(encoding='utf-8-sig'))
            error = None
        except Exception as exc:
            error = repr(exc)
        syntax.append({'file': p.relative_to(REPO).as_posix(), 'sha256': sha(p),
                       'syntax_error': error})
    save('inventory.json', {'files': files, 'counts_by_extension': dict(Counter(
        Path(r['file']).suffix for r in files)), 'sources': syntax,
        'historical_scope': 'Historical STEP files receive fresh import/validity checks in historical-step-checks.json; '
        'the current engineering package receives source-rebuild and configuration checks.'})
    print('Inventory', len(files), 'CAD files;', len(sources), 'Python sources', flush=True)


def dxfs_and_nesting():
    import ezdxf
    from ezdxf import bbox as ebbox
    rows = read(CAD / 'cutlist.json')
    ops = read(CAD / 'part-operations.json')
    flatpns = {p['part_number'] for p in ops if p['manufacturing_flat']
               and not p['individual_export_guarded']}
    actual = {p.stem for p in (CAD / 'dxf').glob('*.dxf')}
    reports = []
    for path in sorted(CAD.rglob('*.dxf')):
        d = ezdxf.readfile(path)
        a = d.audit()
        cut = [e for e in d.modelspace() if e.dxf.layer.startswith('CUT_')]
        ext = ebbox.extents(cut)
        opened = [e.dxf.handle for e in cut if e.dxftype() == 'LWPOLYLINE' and not e.closed]
        reports.append({'file': path.relative_to(CAD).as_posix(), 'units': d.units,
                        'audit_errors': len(a.errors), 'audit_fixes': len(a.fixes),
                        'entities': len(d.modelspace()), 'cut_entities': len(cut),
                        'open_cut_polylines': opened,
                        'cut_bounds': [list(ext.extmin), list(ext.extmax)] if ext.has_data else None})
    n = read(CAD / 'nesting/sheet-nesting.json')
    counts = Counter()
    failures = []
    for g in n['groups']:
        for layout in g['layouts']:
            parts = layout['parts']
            for i, p in enumerate(parts):
                counts[p['part_number']] += 1
                x, y, w, h = [p[k] for k in ('x', 'y', 'placed_w', 'placed_h')]
                edge = n['edge_margin_mm']
                if min(x, y) < edge-1e-6 or x+w > n['stock_mm'][0]-edge+1e-6 or y+h > n['stock_mm'][1]-edge+1e-6:
                    failures.append({'file': layout['file'], 'part': p['part_number'], 'type': 'edge'})
                for q in parts[i+1:]:
                    dx = min(x+w, q['x']+q['placed_w']) - max(x, q['x'])
                    dy = min(y+h, q['y']+q['placed_h']) - max(y, q['y'])
                    if dx > 1e-6 and dy > 1e-6:
                        failures.append({'file': layout['file'], 'parts': [p['part_number'],q['part_number']], 'type': 'rectangle_overlap'})
    expected = {p['part_number']: p['quantity'] for p in rows if p['part_number'] in flatpns}
    mismatches = [{'pn': p, 'expected': expected.get(p, 0), 'nested': counts.get(p, 0)}
                  for p in set(expected)|set(counts) if expected.get(p, 0) != counts.get(p, 0)]
    save('drawing-checks.json', {'dxf_reports': reports, 'missing_current_dxf': sorted(flatpns-actual),
        'unreferenced_current_dxf': sorted(actual-flatpns), 'nesting_quantity_mismatches': mismatches,
        'nesting_rectangle_failures': failures,
        'limits': 'DXF parsing, units, closed polylines and recorded nesting rectangles/quantities only. '
        'No kerf, lead-in, tabs, tooling or process-specific CAM validation. Drawing/source fidelity also requires feature review.'})
    print('DXF', len(reports), 'files; nesting errors', len(failures)+len(mismatches), flush=True)


def model_and_steps():
    import cadquery as cq
    import ezdxf
    from cad_helpers import bbox, validate, intersection_volume, write_dxf
    from build_reve_engineering import build_model
    start = time.monotonic()
    print('Building current model in memory', flush=True)
    m, details = build_model()
    print('Built', len(m.parts), 'components in', round(time.monotonic()-start, 1), 'seconds', flush=True)
    previous = read(CAD / 'RevE_ASSEMBLED_ENGINEERING-validation.json')
    old = {p['id']: p for p in previous['parts']}
    records = []
    diffs = []
    groups = defaultdict(list)
    for p in m.parts:
        groups[p.part_number].append(p)
        v = p.shape.Volume()
        b = bbox(p.shape)
        rec = {'id': p.id, 'part_number': p.part_number, 'group': p.group,
               'purchased': p.purchased, 'release': p.release, 'valid': p.shape.isValid(),
               'solids': len(p.shape.Solids()), 'volume_mm3': v, 'bounds_mm': b,
               'local_world_volume_delta_mm3': abs(v-p.local.Volume())}
        records.append(rec)
        q = old.get(p.id)
        if q is None or abs(q['volume_mm3']-v) > max(.05, v*1e-7) or max(abs(x-y) for x,y in zip(q['bounds_mm'],b)) > 1e-4:
            diffs.append({'id': p.id, 'saved': q, 'fresh': rec})
    save('fresh-model.json', {'runtime': {'python': sys.version, 'cadquery': cq.__version__, 'ezdxf': ezdxf.__version__},
        'part_count': len(m.parts), 'records': records,
        'duplicate_component_ids': [p for p,n in Counter(p.id for p in m.parts).items() if n>1],
        'missing_saved_ids': sorted(set(old)-{p.id for p in m.parts}), 'saved_validation_mismatches': diffs,
        'source_hashes': {p.name: sha(p) for p in CAD.glob('*.py')}, 'details': details})
    # The exported part number must describe every instance, not just parts[0].
    pnconflicts = []
    orientation_equivalent = []
    for pn, parts in groups.items():
        if len(parts) < 2 or parts[0].purchased or 'GUARDED' in parts[0].release:
            continue
        a = parts[0]
        for b in parts[1:]:
            # Different volumes/bounds/centroids are an inexpensive sufficient test.
            av,bv = a.local.Volume(), b.local.Volume()
            ac,bc = a.local.Center().toTuple(), b.local.Center().toTuple()
            ba,bb = bbox(a.local), bbox(b.local)
            metric = max(abs(x-y) for x,y in zip(ba+list(ac),bb+list(bc)))
            if abs(av-bv) > .05 or metric > 1e-4:
                common = intersection_volume(a.local,b.local)
                symmetric = max(0,av+bv-2*common)
                if symmetric > .05:
                    equivalent = None
                    rotations = [(axis,angle) for axis in ((1,0,0),(0,1,0),(0,0,1)) for angle in (90,180,270)]
                    for axis,angle in rotations:
                        rotated = b.local.rotate((0,0,0),axis,angle)
                        rb = bbox(rotated)
                        rotated = rotated.translate(tuple(ba[k]-rb[k] for k in range(3)))
                        if max(abs(x-y) for x,y in zip(bbox(rotated),ba)) > 1e-4:
                            continue
                        diff = max(0,av+bv-2*intersection_volume(a.local,rotated))
                        if diff < .05:
                            equivalent = {'pn':pn,'a':a.id,'b':b.id,'rotation_axis':axis,
                                          'degrees':angle,'symmetric_difference_mm3':diff}
                            break
                    if equivalent:
                        orientation_equivalent.append(equivalent)
                        continue
                    pnconflicts.append({'part_number': pn, 'exported_instance': a.id,
                        'other_instance': b.id, 'symmetric_difference_mm3': symmetric,
                        'volume_delta_mm3': abs(av-bv), 'centroid_a': ac, 'centroid_b': bc,
                        'bounds_a': ba, 'bounds_b': bb})
    save('part-number-checks.json', {'unresolved_geometry_differences': pnconflicts,
        'orientation_equivalent':orientation_equivalent,
        'limits': 'All manufactured shared part numbers screened by volume, bounds and centroid. '
        'Differences checked by Boolean symmetric volume, including quarter-turn rotations about X/Y/Z. '
        'Other rigid transforms may resolve remaining differences. Equal invariants do not prove identical shape.'})
    print('Shared manufactured PN conflicts', len(pnconflicts), flush=True)
    def entity_signature(entity):
        common=[entity.dxftype(),entity.dxf.layer]
        if entity.dxftype()=='CIRCLE':
            return common+[list(entity.dxf.center),entity.dxf.radius]
        if entity.dxftype()=='LWPOLYLINE':
            return common+[entity.closed,[list(v) for v in entity.get_points('xyb')]]
        if entity.dxftype()=='MTEXT':
            return common+[entity.text,list(entity.dxf.insert)]
        return common+['UNSUPPORTED_ENTITY']
    def rounded(value):
        if isinstance(value,float):return round(value,6)
        if isinstance(value,(list,tuple)):return [rounded(v) for v in value]
        return value
    fidelity=[]
    with tempfile.TemporaryDirectory(prefix='cad-audit-dxf-') as scratch:
        for pn,parts in groups.items():
            p=parts[0]
            if p.flat and not p.purchased and 'GUARDED' not in p.release:
                generated=Path(scratch)/(pn+'.dxf')
                write_dxf(generated,p.flat)
                source_doc=ezdxf.readfile(generated)
                saved_doc=ezdxf.readfile(CAD/'dxf'/(pn+'.dxf'))
                a=rounded([entity_signature(e) for e in source_doc.modelspace()])
                b=rounded([entity_signature(e) for e in saved_doc.modelspace()])
                fidelity.append({'part_number':pn,'matches_current_flat_generator':a==b,
                                 'generated_entities':len(a),'saved_entities':len(b)})
    save('dxf-source-fidelity.json',{'checks':fidelity,
        'limits':'Fresh flat-generator entities compared at 1e-6 mm, including machining layers and notes. '
        'This checks freshness, not whether the flat generator describes the solid correctly; MT01 is a known counterexample.'})
    # Fresh static validation preserves documented overlaps for human review.
    print('Fresh assembled collision validation', flush=True)
    fresh = validate(m)
    save('fresh-static-validation.json', fresh)
    print('Static overlaps:', len(fresh['unresolved_intersections']), 'unresolved;', len(fresh['documented_intersections']), 'permitted', flush=True)
    expected_parts = {pn: ps[0] for pn,ps in groups.items()
                      if not ps[0].purchased and 'GUARDED' not in ps[0].release}
    actual = {p.stem: p for p in (CAD/'parts').glob('*.step')}
    partchecks = []
    for i,(pn,path) in enumerate(sorted(actual.items())):
        p = expected_parts.get(pn)
        try:
            s = cq.importers.importStep(str(path)).val()
            rec = {'pn': pn, 'valid': s.isValid(), 'solids': len(s.Solids()),
                   'volume_mm3': s.Volume(), 'current_expected': p is not None}
            if p is not None:
                rec['source_volume_delta_mm3'] = abs(s.Volume()-p.local.Volume())
                rec['source_bounds_max_delta_mm'] = max(abs(x-y) for x,y in zip(bbox(s),bbox(p.local)))
                rec['volume_tolerance_mm3'] = max(.2, p.local.Volume()*1e-7)
            partchecks.append(rec)
        except Exception as exc:
            partchecks.append({'pn': pn, 'error': repr(exc)})
        if (i+1)%40==0:
            print('Individual STEP readbacks',i+1,'/',len(actual),flush=True)
    save('individual-step-checks.json', {'checks':partchecks,
        'missing_expected':sorted(set(expected_parts)-set(actual)),
        'unreferenced':sorted(set(actual)-set(expected_parts)),
        'limits':'Every existing current individual STEP freshly imported and checked. '
        'First-instance source volume/bounds checked; does not prove feature-level congruence.'})
    checks = []
    for path in sorted((CAD/'step').glob('*.step')):
        print('Assembly STEP readback',path.name,flush=True)
        s = cq.importers.importStep(str(path)).val()
        report = read(CAD/(path.stem+'-validation.json'))
        vol = sum(p['volume_mm3'] for p in report['parts'])
        checks.append({'file':path.name, 'valid':s.isValid(), 'solids':len(s.Solids()),
            'expected_solids':report['part_count'], 'sha256':sha(path),
            'hash_matches_saved_report':sha(path)==report['step_readback']['sha256'],
            'volume_delta_vs_saved_parts_mm3':abs(s.Volume()-vol),
            'volume_tolerance_mm3':max(.2,vol*1e-7), 'bounds_mm':bbox(s)})
    save('assembly-step-checks.json', {'checks':checks,'elapsed_seconds':round(time.monotonic()-start,2)})
    historical=[]
    for path in sorted((REPO/'output/release-review/RevD-STUDY/step').glob('*.step')):
        s=cq.importers.importStep(str(path)).val()
        historical.append({'file':path.relative_to(REPO).as_posix(),'valid':s.isValid(),
                           'solids':len(s.Solids()),'volume_mm3':s.Volume(),'sha256':sha(path)})
    save('historical-step-checks.json', {'checks':historical,
        'limits':'Fresh import and solid validity only. These three historical study assemblies are superseded; '
        'they are not included in current-design strength, quantity, mating-interface or motion conclusions.'})
    print('Model/export audit complete in',round(time.monotonic()-start,1),'seconds',flush=True)


if __name__ == '__main__':
    code=0
    try:
        OUT.mkdir(parents=True, exist_ok=True)
        inventory()
        dxfs_and_nesting()
        model_and_steps()
    except Exception:
        import traceback
        traceback.print_exc()
        code=1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
