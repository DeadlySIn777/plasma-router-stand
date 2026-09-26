"""Independent STEP readback for the shared locator and small ATC dock.

The larger layout has its own two-state readback. These checks confirm exchange
file consistency with the recorded bodies, not manufacturing qualification.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    specs = [
        ('common/location/output/step/common-locator-dock.step',
         'common/location/output/verification.json', 'installed_static'),
        ('common/location/output/protected/step/common-locator-protected.step',
         'common/location/output/verification.json', 'protected_static'),
        ('small-atc/output/step/SMALL_ATC_DOCK_CANDIDATE.step',
         'small-atc/output/fit-report.json', 'dock_internal_static'),
    ]
    checks = []
    for rel, report_rel, key in specs:
        target, record = HERE/rel, HERE/report_rel
        data = json.loads(record.read_text(encoding='utf8'))[key]['parts']
        expected_volume = sum(p['volume_mm3'] for p in data)
        expected_bounds = [min(p['bounds_mm'][k] for p in data) if k<3 else
                           max(p['bounds_mm'][k] for p in data) for k in range(6)]
        step_before, record_before = sha(target), sha(record)
        solid = cq.importers.importStep(str(target)).val()
        bb = solid.BoundingBox()
        actual_bounds = [bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]
        delta = abs(solid.Volume()-expected_volume)
        tolerance = max(.02,expected_volume*1e-7)
        bounds_error = max(abs(a-b) for a,b in zip(expected_bounds,actual_bounds))
        passed = (solid.isValid() and len(solid.Solids()) == len(data)
                  and delta < tolerance and bounds_error < .002
                  and sha(target) == step_before and sha(record) == record_before)
        checks.append({'file':rel, 'report':report_rel, 'passed':passed,
                       'step_sha256':step_before, 'report_sha256':record_before,
                       'solid_count':len(solid.Solids()), 'recorded_body_count':len(data),
                       'volume_difference_mm3':delta, 'volume_tolerance_mm3':tolerance,
                       'maximum_bounds_error_mm':bounds_error})
    result = {'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL',
              'scope':'Independent STEP body count, validity, volume and outer bounds against the recorded candidate model',
              'sources':{str(Path(__file__).relative_to(ROOT)).replace('\\','/'):sha(Path(__file__))},
              'physical_release':False, 'checks':checks}
    (HERE/'exchange-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2),flush=True)
    return 0 if result['status']=='PASS' else 1

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
