"""Check candidate CAD against axis extremes and dry deck rise. This does not move hardware."""
from itertools import product
import json, sys
from build_candidate import pieces, OUT, bolted_datums
from motion_context import _bare_motion, _install_plasma
from check_work_envelope import extents, overlap, gap
from cad_helpers import intersection_volume

def check():
    fixed,dry,wet=pieces()
    results={}
    cache={}
    for label,deck,hot,min_z in [('wood',dry,False,30.),('plasma',wet,True,0.)]:
        obstacles=extents(fixed+deck); combined={}; center={}; hits=[]
        max_y=1240. if hot else 1275.
        poses=[(575.,775.,50.),*product((175.,975.),(275.,max_y),(min_z,100.))]
        for idx,(x,y,z) in enumerate(poses):
            pos=(x,y,z)
            if pos not in cache: cache[pos]=_bare_motion(y,x,z)
            bare=cache[pos]
            body=_install_plasma(bare) if hot else list(bare)
            for name,shape,b in extents(bolted_datums(body)):
                if idx==0: center[name]=b.copy();combined[name]=b.copy()
                sw=combined[name]
                for k in range(3):
                    sw[k]=min(b[k],sw[k]);sw[k+3]=max(b[k+3],sw[k+3])
                for ob,solid,bb in obstacles:
                    if overlap(b,bb):
                        vol=intersection_volume(shape,solid)
                        if vol>.05:hits.append([pos,name,ob,round(vol,4)])
        closest=None;bound_candidates=[]
        for name,bb in combined.items():
            if not any(abs(a-b)>1e-5 for a,b in zip(center[name],bb)):continue
            if name.endswith('_ROLLER') and name.startswith(('X_HOME','Y_LIMIT')):
                bb=bb.copy();bb[2]-=8;bb[5]+=8
            for ob,_,bounds in obstacles:
                if overlap(bb,bounds): bound_candidates.append([name,ob])
                rec=(round(gap(bb,bounds),4),name,ob)
                if closest is None or rec<closest: closest=rec
        results[label]={'poses':poses,'geometry_review_limits_only':{'min_z_lift_mm':min_z,'max_y_gantry_mm':max_y},
                        'moving_swept_AABB_overlaps':bound_candidates,
                        'exact_pose_intersections_over_0p05_mm3':hits,'nearest_moving_AABB':closest}
    (OUT/'travel.json').write_text(json.dumps(results,indent=2))
    print({k:(len(v['moving_swept_AABB_overlaps']),len(v['exact_pose_intersections_over_0p05_mm3']),v['nearest_moving_AABB']) for k,v in results.items()})
if __name__=='__main__':check()
