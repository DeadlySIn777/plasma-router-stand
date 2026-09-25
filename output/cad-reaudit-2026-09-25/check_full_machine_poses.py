"""Nine fresh full-machine router poses; no source CAD or exports overwritten.

All eight nominal travel-box corners plus center. These are sampled static
checks of represented solids; no cutter, workpiece, hose or cable sweep is
invented, and no operational plasma configuration exists in the source model.
"""
from pathlib import Path
import copy
import hashlib
import itertools
import json
import os
import sys
import time

OUT=Path(__file__).resolve().parent
CAD=OUT.parents[1]/'output/release-review/RevE-ENGINEERING'
sys.path.insert(0,str(CAD))


def main():
    from cad_helpers import Model, validate
    import motion_details
    from build_reve_engineering import build_model
    original=motion_details.make_motion
    try:
        motion_details.make_motion=lambda m: {'audit_only':'motion deferred'}
        fixed,_=build_model()
    finally:
        motion_details.make_motion=original
    print('Built fixed assembly',len(fixed.parts),'parts',flush=True)
    report={'scope':__doc__,'sources_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
        for p in CAD.glob('*.py')},'states':[]}
    start=time.monotonic()
    for gy,hx,z in list(itertools.product((275,1275),(175,975),(0,100)))+[(775,575,50)]:
        m=Model()
        m.allowed_intersections=fixed.allowed_intersections.copy()
        m.holds=list(fixed.holds)
        for p in fixed.parts:
            q=copy.copy(p)
            q.notes=list(p.notes)
            q.flat=copy.deepcopy(p.flat)
            m.parts.append(q)
        original(m,gantry_y=gy,head_x=hx,z_lift=z,tool='router')
        result=validate(m)
        record={'gantry_y':gy,'head_x':hx,'z_lift':z,'tool':'router',
                'part_count':result['part_count'],'broadphase_pairs':result['broadphase_pairs'],
                'unresolved_intersections':result['unresolved_intersections'],
                'documented_intersections':result['documented_intersections']}
        report['states'].append(record)
        report['elapsed_seconds']=round(time.monotonic()-start,2)
        (OUT/'full-machine-poses.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print('Full-machine pose',gy,hx,z,'unresolved',len(record['unresolved_intersections']),flush=True)
    report['all_sampled_poses_clear']=not any(s['unresolved_intersections'] for s in report['states'])
    (OUT/'full-machine-poses.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Complete',len(report['states']),'poses;',report['elapsed_seconds'],'seconds',flush=True)


if __name__=='__main__':
    code=0
    try:main()
    except Exception:
        import traceback
        traceback.print_exc()
        code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
