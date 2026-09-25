"""Regenerate motion-validation.json: five sampled motion-subsystem configurations.

Recreates the original motion-only screen (the one-off generator script was not
retained): for each configuration, a fresh model containing only the rail-cap
blanks and the make_motion output is validated for solid validity and
positive-volume intersections, and every part's local blank is volume-checked
against its placed world solid (a rigid transform preserves volume).
"""
from pathlib import Path
import hashlib,json,sys,os
import cadquery as cq
from cad_helpers import *
import geometry_base as base

ROOT=Path(__file__).resolve().parent

STATES=[(1275,575,100,'router'),(275,175,0,'router'),(275,975,100,'router'),(1275,175,100,'router'),(1275,975,0,'router')]

def normalized_add(m,p):
    bb=bbox(p.shape);local=p.shape.translate(tuple(-x for x in bb[:3]))
    return m.add(p.id,local,origin=bb[:3],group=p.group,material=p.material,pn=p.id,color=p.color)

def main():
    from motion_details import make_motion
    states=[];mismatches=[]
    for gy,hx,zl,tool in STATES:
        m=Model()
        for p in base.fixed:
            if p.group=='rail_cap':normalized_add(m,p)
        make_motion(m,gantry_y=float(gy),head_x=float(hx),z_lift=float(zl),tool=tool)
        r=validate(m)
        states.append({'configuration':{'gantry_y':gy,'beam_center_y':gy+80,'head_x':hx,'z_lift':zl,'tool':tool},
                       'parts':r['part_count'],'clashes':r['unresolved_intersections']})
        for p in m.parts:
            dv=abs(p.shape.Volume()-p.local.Volume())
            if dv>max(.05,p.shape.Volume()*1e-7):
                mismatches.append({'state':[gy,hx,zl],'id':p.id,'volume_delta_mm3':round(dv,5)})
        print('state',gy,hx,zl,'parts',r['part_count'],'clashes',len(r['unresolved_intersections']),flush=True)
    report={'source_file':'motion_details.py',
            'source_sha256':hashlib.sha256((ROOT/'motion_details.py').read_bytes()).hexdigest(),
            'states':states,'local_world_geometry_mismatches':mismatches,
            'switch_actuation_handling':'For a roller on the 0.63-slope cam ramp, roller top is lowered by R*(sqrt(1+slope^2)-1), in addition to the cam underside at its center. Flat-land position follows the underside without intersection. The small lever and internal switch mechanism are not modeled. No positive overlap is permitted merely because a part is a switch.',
            'scope':'Five configurations of the motion subsystem only. No claim of continuous swept-volume clearance or complete machine strength/commissioning.'}
    (ROOT/'motion-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    ok=not mismatches and not any(s['clashes'] for s in states)
    print('MOTION-STATES',('PASS' if ok else 'FAIL'),flush=True)
    return 0 if ok else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
