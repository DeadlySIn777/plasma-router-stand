"""Check the nominal moving bodies against both complete operating states."""
from pathlib import Path
from itertools import product
import hashlib,json,sys
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('whole_table',HERE/'build.py')
design=importlib.util.module_from_spec(spec);spec.loader.exec_module(design)
from check_work_envelope import extents,overlap,gap
from cad_helpers import intersection_volume

def moving(hot,x,y,z):
    bare=design._bare_motion(y,x,z)
    body=design._install_plasma(bare) if hot else bare
    return [(n,s.translate((0,0,-150)),c) for n,s,c in body if n not in ('Y_DATUM_L','Y_DATUM_R')]

def main():
    fixed,wood,plasma=design.components()
    report={'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'build.py',Path(__file__))}}
    for mode,extra,hot in [('CARVING',wood,False),('PLASMA',plasma,True)]:
        obstacles=extents(fixed+extra); sweeps={}; centers={};hits=[]
        poses=[(575.,775.,50.),*product((175.,975.),(275.,1275.),(0.,100.))]
        for i,(x,y,z) in enumerate(poses):
            for name,s,b in extents(moving(hot,x,y,z)):
                if i==0:centers[name]=b.copy();sweeps[name]=b.copy()
                sw=sweeps[name]
                for k in range(3):sw[k]=min(sw[k],b[k]);sw[k+3]=max(sw[k+3],b[k+3])
                for ob,shape,bb in obstacles:
                    if overlap(b,bb):
                        v=intersection_volume(s,shape)
                        if v>.05:hits.append({'pose':[x,y,z],'moving':name,'obstacle':ob,'mm3':round(v,5)})
        candidates=[];nearest=[]
        for n,b in sweeps.items():
            if not any(abs(a-c)>1e-5 for a,c in zip(b,centers[n])):continue
            if n.endswith('_ROLLER') and n.startswith(('X_HOME','Y_LIMIT')):
                b=b.copy();b[2]-=8;b[5]+=8
            for ob,_,bb in obstacles:
                if overlap(b,bb):candidates.append([n,ob])
                nearest.append((round(gap(b,bb),4),n,ob))
        report[mode]={'limits_X_Yguide_Zlift_mm':[[175,975],[275,1275],[0,100]],
                      'sampled_intersections_gt_0p05_mm3':hits,'moving_swept_AABB_candidates':candidates,'nearest_AABB':min(nearest)}
        print(mode,len(hits),len(candidates),min(nearest),flush=True)
    (design.OUT/'motion-check.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
