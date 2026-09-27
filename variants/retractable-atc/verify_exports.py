"""Independent readback of the delivered mechanism STEP/DXF files.

Does not import either mechanism generator. This checks exchange integrity,
units and report bindings, not collision freedom or fabrication readiness.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import sys

import cadquery as cq
import ezdxf
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def drawing_features(path, drawing):
    """Compare declared circular machining features with the actual local STEP.

    Does not recreate a plate from generator metadata. Circular STEP bores are
    inspected independently, including a check for holes missing from the DXF.
    Noncircular profiles and exact operation depths are outside this screen.
    """
    step_path = path.parent.parent / 'parts' / (path.stem + '.step')
    if not step_path.is_file():
        return {'passed': False, 'error': 'DXF has no matching local part STEP'}
    digest = sha(step_path)
    shape = cq.importers.importStep(str(step_path)).val()
    solids = shape.Solids()
    if len(solids) != 1:
        return {'passed': False, 'error': 'Expected one local fabrication solid'}
    solid = solids[0]
    bounds = solid.BoundingBox()
    circles = [(float(e.dxf.center.x), float(e.dxf.center.y),
                float(e.dxf.radius), e.dxf.layer)
               for e in drawing.modelspace() if e.dxftype() == 'CIRCLE']
    cylinders = []
    for face in solid.Faces():
        surface = BRepAdaptor_Surface(face.wrapped)
        if surface.GetType() != GeomAbs_Cylinder:
            continue
        cylinder = surface.Cylinder()
        direction = cylinder.Axis().Direction()
        if abs(abs(direction.Z())-1) > 1e-6:
            continue
        point = cylinder.Location()
        cylinders.append((point.X(), point.Y(), cylinder.Radius(),
                          surface.LastUParameter()-surface.FirstUParameter()))
    def same(a, b):
        return all(abs(a[k]-b[k]) < 1e-4 for k in range(3))
    def empty_through(x, y):
        return all(not solid.isInside(cq.Vector(x, y, z), 1e-6)
                   for z in (bounds.zmin+1e-4, (bounds.zmin+bounds.zmax)/2,
                             bounds.zmax-1e-4))
    failures = []
    for circle in circles:
        if not any(same(circle, cylinder) for cylinder in cylinders):
            failures.append({'kind': 'DXF_circle_without_matching_STEP_cylinder',
                             'circle': circle})
        if circle[3] == 'CUT_HOLES' and not empty_through(*circle[:2]):
            failures.append({'kind': 'DXF_through_hole_contains_STEP_material',
                             'circle': circle})
    # Full cylindrical surfaces with an empty center identify circular bores.
    # A counterbore and its through hole can share a center at different radii.
    for cylinder in cylinders:
        if cylinder[3] < 2*math.pi-1e-5 or not empty_through(*cylinder[:2]):
            continue
        if not any(same(cylinder, circle) for circle in circles):
            failures.append({'kind': 'STEP_bore_missing_from_DXF',
                             'cylinder': cylinder[:3]})
    return {'passed': not failures and sha(step_path) == digest,
            'part_step': str(step_path.relative_to(ROOT)).replace('\\', '/'),
            'part_step_sha256': digest, 'DXF_circles': len(circles),
            'STEP_axial_cylinders': len(cylinders), 'failures': failures,
            'scope': 'Circular locations/radii and declared through-hole centers; excludes complete contour/depth/thread qualification'}


def main():
    checks = []
    sources = {str(Path(__file__).resolve().relative_to(ROOT)).replace('\\', '/'): sha(Path(__file__))}
    artifacts = {}
    for machine in ('small-mechanism', 'large-mechanism'):
        folder = HERE / machine
        files = sorted(p for p in folder.rglob('*') if p.suffix.lower() in ('.step', '.stp', '.dxf'))
        checks.append({'name': 'exchange_files_present', 'machine': machine,
                       'passed': bool(files), 'count': len(files)})
        for path in files:
            rel = str(path.relative_to(ROOT)).replace('\\', '/')
            digest = sha(path)
            item = {'name': 'independent_readback', 'file': rel, 'sha256': digest}
            try:
                if path.suffix.lower() in ('.step', '.stp'):
                    part = cq.importers.importStep(str(path)).val()
                    solids = part.Solids()
                    volumes = [s.Volume() for s in solids]
                    bounds = part.BoundingBox()
                    xyz = [bounds.xmin, bounds.ymin, bounds.zmin,
                           bounds.xmax, bounds.ymax, bounds.zmax]
                    item.update(solids=len(solids), bounds_mm=xyz,
                                volume_sum_mm3=sum(volumes),
                                all_solids_valid=all(s.isValid() for s in solids))
                    item['passed'] = (bool(solids) and item['all_solids_valid'] and
                                      all(math.isfinite(v) and v > 0 for v in volumes) and
                                      all(math.isfinite(v) for v in xyz))
                else:
                    drawing = ezdxf.readfile(path)
                    audit = drawing.audit()
                    item.update(units_code=int(drawing.header.get('$INSUNITS', 0)),
                                model_entities=len(drawing.modelspace()),
                                audit_errors=len(audit.errors),
                                audit_fixes=len(audit.fixes))
                    # A readback that silently repairs a file is not the same
                    # thing as a clean delivered manufacturing drawing.
                    item['passed'] = (item['units_code'] == 4 and
                                      item['model_entities'] > 0 and
                                      not audit.errors and not audit.fixes)
                    feature_check = drawing_features(path, drawing)
                    item['circular_feature_check'] = feature_check
                    item['passed'] = item['passed'] and feature_check['passed']
            except Exception as error:
                item.update(passed=False, error=f'{type(error).__name__}: {error}')
            item['unchanged_during_readback'] = sha(path) == digest
            item['passed'] = item['passed'] and item['unchanged_during_readback']
            checks.append(item)
            artifacts[rel] = digest
    report = {
        'passed': all(x['passed'] for x in checks),
        'scope': 'Independent STEP validity/volume/bounds, DXF units/structure, and circular machining-feature correspondence on both mechanisms',
        'does_not_establish': ['Assembly collision freedom', 'Manufacturing tolerances',
                               'Loaded tool compatibility', 'Physical rigidity',
                               'Fabrication release', 'Controller operation'],
        'source_sha256': sources,
        'artifact_sha256': artifacts,
        'checks': checks,
    }
    (HERE / 'export-verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'passed': report['passed'], 'files': len(artifacts),
                      'failures': [x for x in checks if not x['passed']]}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    result = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(result)
