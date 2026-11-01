"""Build reproducible XR1 review assemblies. Geometry evidence is not strength certification."""
from pathlib import Path
import csv, hashlib, json, os, sys
import cadquery as cq
import params as P
from frame import frame_parts
from bed import bed_parts
from motion import motion_parts

HERE=Path(__file__).resolve().parent
OUT=HERE/'review'

def bounds(s):
    b=s.BoundingBox()
    return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def overlap(a,b):
    return all(min(a[i+3],b[i+3])-max(a[i],b[i])>1e-5 for i in range(3))

def clashes(a,b,same=False):
    out=[]; tested=0
    ba=[bounds(s) for _,s,_ in a]; bb=[bounds(s) for _,s,_ in b]
    for i,(na,sa,_) in enumerate(a):
        for j,(nb,sb,_) in enumerate(b):
            if same and j<=i:continue
            if not overlap(ba[i],bb[j]):continue
            tested+=1
            v=sa.intersect(sb).Volume()
            if v>.05:out.append({'a':na,'b':nb,'volume_mm3':round(v,5)})
    return {'exact_pairs':tested,'positive_intersections':out}

def export(path,parts):
    assembly=cq.Assembly(name=path.stem)
    for n,s,c in parts:assembly.add(s,name=n,color=cq.Color(*c))
    assembly.save(str(path))
    imported=cq.importers.importStep(str(path)).val()
    expected=sum(len(s.Solids()) for _,s,_ in parts)
    assert imported.isValid() and len(imported.Solids())==expected,(path,expected,len(imported.Solids()))
    return {'components':len(parts),'solids':expected,'bounds_mm':bounds(imported),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def run():
    OUT.mkdir(exist_ok=True)
    sources=[HERE/n for n in ('params.py','frame.py','bed.py','motion.py','build.py','preview.py')]+[HERE/'requirements.json']
    start_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    frame=frame_parts(); report={'revision':P.REVISION,'assemblies':{},'interfaces':{}}
    report['interfaces']['frame_self']=clashes(frame,frame,True)
    assemblies={'FRAME':frame}
    for label,hot in [('WOOD',False),('PLASMA',True)]:
        bed=bed_parts(hot); motion=motion_parts(hot)
        parts=frame+bed+motion
        assert len({n for n,_,_ in parts})==len(parts),'Duplicate component IDs'
        bad=[n for n,s,_ in parts if not s.isValid() or not len(s.Solids()) or s.Volume()<=0]
        assert not bad,bad
        assemblies[label]=parts
        report['interfaces'][label]={k:clashes(a,b) for k,a,b in
            [('frame_bed',frame,bed),('frame_motion',frame,motion),('bed_motion',bed,motion)]}
        print(label,{k:len(v['positive_intersections']) for k,v in report['interfaces'][label].items()},flush=True)
    for label,parts in assemblies.items():
        report['assemblies'][label]=export(OUT/f'XR1_{label}.step',parts)
        print('Exported',label,report['assemblies'][label]['solids'],flush=True)
    report['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    report['source_consistent_during_build']=start_hashes==report['source_sha256']
    report['release']=False
    all_checks=[report['interfaces']['frame_self']]+[group for mode in ('WOOD','PLASMA') for group in report['interfaces'][mode].values()]
    report['display_pose_external_clash_free']=all(not c['positive_intersections'] for c in all_checks)
    report['scope']='Valid solids, STEP round-trip and exact external-group intersections at the display pose. Separate travel, structure, bed and water evidence is required.'
    (OUT/'build-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with (OUT/'components.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['assembly','id','solid_count','bbox_mm'])
        for label,parts in assemblies.items():
            for n,s,_ in parts:w.writerow([label,n,len(s.Solids()),json.dumps(bounds(s))])
    from preview import draw
    draw(assemblies,OUT)
    return 0 if report['display_pose_external_clash_free'] and report['source_consistent_during_build'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
