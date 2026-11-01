"""Check only new drop/head integration; no inherited source or model writes."""
from itertools import product
from pathlib import Path
import hashlib
import json
import os
import sys

from motion_context import (HERE, POSE, ROOT, SOURCE, THICKNESS, _bare_motion,
                            _install_plasma, bbox, drop_blank)
from cad_helpers import intersection_volume


def check_pose(px,py,pz):
    parts=_install_plasma(_bare_motion(py,px,pz))
    model=[(n,s,bbox(s)) for n,s,_ in parts]
    assert len(model)==394
    checked=0; known=[]; unclassified=[]
    for i,(na,sa,ba) in enumerate(model):
        for nb,sb,bb in model[i+1:]:
            if not (na.startswith(('WP_','I_HEAD_')) or nb.startswith(('WP_','I_HEAD_'))):continue
            if na.startswith('I_HEAD_') and nb.startswith('I_HEAD_'):continue
            if any(min(ba[k+3],bb[k+3])-max(ba[k],bb[k])<1e-5 for k in range(3)):continue
            checked+=1
            v=intersection_volume(sa,sb)
            if v<.02:continue
            if ('I_HEAD_BACKPLATE' in (na,nb) and (na.startswith('WP_DROP_M6x16_LOWER_') or nb.startswith('WP_DROP_M6x16_LOWER_'))):
                known.append((na,nb,round(v,4)))  # existing tapped-bore vs nominal male thread
            else:unclassified.append((na,nb,round(v,4)))
    return {'x':px,'gantry_y':py,'z_lift':pz,'broad_phase_pairs_checked':checked,'known_thread_engagement_mm3':known,'unclassified_intersections_mm3':unclassified}


def main():
    poses=[(POSE['head_x'],POSE['gantry_y'],POSE['z_lift']),*product((175.,975.),(275.,1275.),(0.,100.))]
    records=[]
    for pose in poses:
        entry=check_pose(*pose); records.append(entry)
        print('Pose',pose,entry['broad_phase_pairs_checked'],'pairs,',len(entry['unclassified_intersections_mm3']),'unclassified intersections',flush=True)
    s,_=drop_blank()
    dimensions=bbox(s)
    assert all(abs(a-b)<.001 for a,b in zip(dimensions,(0,0,0,110,185,THICKNESS)))
    result={'scope':'New lowered plasma head and drop hardware vs other selected motion solids, plus new part-to-part interfaces; inherited head-internal and inherited common-common pairs excluded.',
            'numerical_reporting_threshold_mm3':.02,'records':records,'all_passed':not any(r['unclassified_intersections_mm3'] for r in records),
            'blank_mm':[110.,185.,12.7], 'plate_net_volume_mm3':s.Volume(),
            'plate_estimated_mass_kg_at_2700kgm3':s.Volume()*2.7e-6,
            'not_tested':'Continuous motion, flexible torch lead, installed torch/nozzle, fixture stock, driver/hardware access, wear/retention and any new chassis/bed geometry. Whole-variant report covers separate frame/bed checks.',
            'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [SOURCE/'cad_helpers.py',SOURCE/'motion_details.py',SOURCE/'motion_completion.py',SOURCE/'motion_finish.py',HERE/'motion_context.py',Path(__file__)]}}
    (HERE/'motion-detail'/'clearance-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return 0 if result['all_passed'] else 1


if __name__=='__main__':
    # Work around OCCT Python destructor faults during this environment's teardown.
    try:code=main()
    except Exception:
        import traceback; traceback.print_exc(); code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
