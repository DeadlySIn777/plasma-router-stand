"""Generate both named STEP assemblies, a chassis-only STEP, and review evidence."""
from pathlib import Path
import csv, json, hashlib, sys, os
from functools import lru_cache
import cadquery as cq
from frame import frame_parts, bolted_datums, wet_support_option
from motion_context import motion_parts
from process_bed import bed_parts

HERE=Path(__file__).resolve().parent; OUT=HERE/'review'; OUT.mkdir(exist_ok=True)
def dump(p,data): p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as fp:
        w=csv.DictWriter(fp,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def cutplan():
    schedule=[]
    for k in 'LR':
        for pos in ('MOTION','PAN'):schedule.append([1500,[(f'EX_{k}_Y_{pos}',1450)]])
    up=[f'EX_{k}_UPRIGHT_{i}' for k in 'LR' for i in (1,2,3)]
    legs=[f'EX_{k}_LEG_{i}' for k in 'LR' for i in (1,2,3)]
    for i in range(3):
        schedule.append([1500,[(f'EX_X_PAN_{i+1}',1048.4),(up[i*2],176.5),(up[i*2+1],176.5)]])
    schedule.append([1500,[(k,730) for k in legs[:2]]])
    for k in legs[2:]:schedule.append([1000,[(k,730)]])
    rows=[]; names=set()
    for i,(stock,pieces) in enumerate(schedule,1):
        residue=round(stock-4-sum(length+3 for _,length in pieces),3)
        assert residue>=0
        for ID,length in pieces:
            assert ID not in names; names.add(ID)
            rows.append(dict(stock_bar=i,stock_mm=stock,finish_mm=length,part_ID=ID,kerf_per_cut_mm=3,
                    ends_allowance_per_bar_mm=4,offcut_after_all_parts_on_bar_mm=residue))
    return rows
def export(path,parts):
    a=cq.Assembly(name=path.stem)
    for n,s,c in parts:a.add(s,name=n,color=cq.Color(*c))
    a.save(str(path))
    read=cq.importers.importStep(str(path)).val(); expected=sum(len(s.Solids()) for _,s,_ in parts)
    actual=len(read.Solids())
    assert actual==expected,(path,expected,actual)
    b=read.BoundingBox(); return dict(named_components=len(parts),STEP_solid_count=actual,
                world_bounds_mm=[round(i,3) for i in (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)])
def clashes(A,B,same=False):
    refs={id(s):s.BoundingBox() for _,s,_ in A+B}; out=[]; count=0
    for i,(a,sa,_) in enumerate(A):
        for j,(b,sb,_) in enumerate(B):
            if same and j<=i:continue
            ba,bb=refs[id(sa)],refs[id(sb)]
            if min(ba.xmax,bb.xmax)-max(ba.xmin,bb.xmin)<1e-4 or min(ba.ymax,bb.ymax)-max(ba.ymin,bb.ymin)<1e-4 or min(ba.zmax,bb.zmax)-max(ba.zmin,bb.zmin)<1e-4: continue
            count+=1
            vol=sa.intersect(sb).Volume()
            if vol>.05:out.append(dict(a=a,b=b,volume_mm3=round(vol,4)))
    return {'exact_intersections_after_bounds_filter':count,'interferences_gt_0p05_mm3':out}
def run(geometry_only=False):
    f=frame_parts(); rows=cutplan()
    assert {n for n,_,_ in f if n.startswith('EX_')}=={r['part_ID'] for r in rows}
    for p in rows:
        s=next(s for n,s,c in f if n==p['part_ID']); bb=s.BoundingBox()
        assert abs(max(bb.xlen,bb.ylen,bb.zlen)-p['finish_mm'])<1e-4
    write_csv(HERE/'stock-and-cuts.csv',rows)
    addcuts=[dict(stock_bar=12+i,stock_mm=1000,finish_mm=730,part_ID=f'OPT_CENTER_LEG_{i}',
        kerf_per_cut_mm=3,ends_allowance_per_bar_mm=4,offcut_after_all_parts_on_bar_mm=263) for i in (1,2,3)]
    write_csv(HERE/'extra-pack-9-feet.csv',addcuts+[dict(stock_bar=16,stock_mm=1000,
        finish_mm='',part_ID='UNCUT_SPARE',kerf_per_cut_mm=0,ends_allowance_per_bar_mm=0,offcut_after_all_parts_on_bar_mm=1000)])
    checks={'frame_self':clashes(f,f,True)}; report={}; assys={}
    for mode,hot in [('WOOD',False),('PLASMA',True)]:
        b=bed_parts(hot); m=bolted_datums(motion_parts(hot))
        parts=f+b+m; assys[mode]=parts
        assert len(parts)==len({n for n,s,c in parts})
        checks[mode]={key:clashes(x,y) for key,x,y in [('frame_vs_bed',f,b),('frame_vs_motion',f,m),('bed_vs_motion',b,m)]}
        assert all(s.isValid() and len(s.Solids())>0 for n,s,c in parts)
        print(mode,{k:len(v['interferences_gt_0p05_mm3']) for k,v in checks[mode].items()},flush=True)
    opt=wet_support_option()
    for row in addcuts:
        piece=next(s for n,s,c in opt if n==row['part_ID'])
        assert abs(piece.BoundingBox().zlen-row['finish_mm'])<1e-4
    checks['OPTION']={'self':clashes(opt,opt,True),'frame':clashes(opt,f)}
    for mode,parts in assys.items():
        checks['OPTION'][mode]=clashes(opt,parts[len(f):])
    dump(OUT/'interface-checks.json',checks)
    if geometry_only: return 0
    # Primary dual-process exchange uses the recommended wet-load supports.
    # The six-foot frame is exported separately to preserve the base-price option.
    assys={mode:items+opt for mode,items in assys.items()}
    for mode,parts in [('FRAME',f),('FRAME_9_FEET',f+opt),*assys.items()]:
        report[mode]=export(OUT/f'{mode}.step',parts)
        print(mode,report[mode],flush=True)
    write_csv(OUT/'component-index.csv',[
        dict(mode=mode,id=n,geometric_solids=len(s.Solids())) for mode,parts in assys.items() for n,s,c in parts])
    from preview import draw
    draw(assys,f+opt,OUT)
    residual=checks['frame_self']['interferences_gt_0p05_mm3']+[
        hit for mode in (*assys,'OPTION') for group in checks[mode].values() for hit in group['interferences_gt_0p05_mm3']]
    dump(OUT/'build-check.json',dict(assemblies=report,cutlist_19_matches_CAD=True,
        source_sha256={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('build.py','frame.py','preview.py','motion_context.py','process_bed.py')},
        six_foot_extrusion_parts=len(rows),six_foot_stock_bars=len({r['stock_bar'] for r in rows}),
        default_hybrid_step_extrusion_parts=len(rows)+3,default_hybrid_step_stock_bars=16,
        total_frame_extrusion_finished_mm=round(sum(r['finish_mm'] for r in rows),2),
        boundary_clashes_remaining=len(residual),machining_or_plasma_release=False,
        limitations='Mid-travel displayed poses only. No blanket inheritance of other variant tests. See individual handling and head checks, and assembly holds.'))
    return int(bool(residual))
if __name__=='__main__':
    try: code=run('--geometry-only' in sys.argv)
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
