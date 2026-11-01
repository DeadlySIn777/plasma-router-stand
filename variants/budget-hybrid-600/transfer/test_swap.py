"""Check the four transfers at the proposed elevated rack; dimensions in mm."""
import hashlib, math, os, sys, json
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import build_candidate as design
from motion_context import _bare_motion, _install_plasma
from check_process_bed import limits, overlap
from frame import box
from collections import Counter
def descriptors(items):return [(n,s,limits(s)) for n,s,_ in items]
def run():
    fixed,dry,old=design.pieces()
    park=list(_bare_motion(275.,575.,100.))
    structure=descriptors(fixed+park)
    local=[(n,s.translate((0,-103.4,-920.7)),c) for n,s,c in dry if n.startswith('bridge_0_')]
    def pos(y,z,a):
        return [(n,s.rotate((0,0,0),(1,0,0),a).translate((0,y,z)),c) for n,s,c in local]
    broad=Counter()
    def state(points):
        return [((n,s),limits(s)) for n,s,c in points]
    def check(frame,env,bad,label,i):
        for (n,s),bb in state(frame):
            for nm,ob,b2 in env:
                if overlap(bb,b2):
                    # AABBs with true shape overlap may include holes or diagonal straps.
                    if s.intersect(ob).Volume()>.05:bad[(i,label,nm)]+=1
    bad=Counter();frames=0
    starts=[];slots=[];seat_z=[]
    def validate_pose(calculated,expected,index):
        assert len(calculated)==len(expected)
        actual={name:s for name,s,_ in expected}
        for name,shape,_ in calculated:
            counterpart=actual[name.replace('bridge_0_',f'bridge_{index}_')]
            assert max(abs(a-b) for a,b in zip(limits(shape),limits(counterpart)))<1e-5
            assert shape.cut(counterpart).Volume()<.05 and counterpart.cut(shape).Volume()<.05
    for i in range(4):
        dry_i=[p for p in dry if p[0].startswith(f'bridge_{i}_')]
        wet_i=[p for p in old if p[0].startswith(f'bridge_{i}_')]
        b=limits(dry_i[0][1]);w=limits(wet_i[0][1])
        starts.append(b[1]-22.);slots.append(w[4]);seat_z.append(w[2]-22.)
        validate_pose(pos(starts[i],b[2],0.),dry_i,i)
        validate_pose(pos(slots[i],seat_z[i],90.),wet_i,i)
    sequence=[3,2,1,0]  # load rear slot first
    for i in sequence:
        other=[]
        for j in range(4):
            if j!=i:other.extend(pos(slots[j],seat_z[j],90.) if j>i else pos(starts[j],920.7,0.))
        env=structure+descriptors(other)
        # Angle is about the front end of the carrier's local coordinate frame.
        keys=[(starts[i],920.7,0),(starts[i],980.,0.),(980.,980.,0.),
              (980.,980.,90.),(slots[i],980.,90.),(slots[i],seat_z[i],90.)]
        for label,(f,t) in enumerate(zip(keys,keys[1:])):
            prev=None
            steps=max(1,math.ceil(max(abs(t[0]-f[0])/30,abs(t[1]-f[1])/12,abs(t[2]-f[2])/3)))
            for j in range(steps+1):
                p=[x+(q-x)*j/steps for x,q in zip(f,t)]
                moved=pos(*p)
                check(moved,env,bad,label,i);frames+=1
                curr=state(moved)
                if prev is not None:
                    sag=245*(1-math.cos(math.radians(abs(t[2]-f[2])/steps)/2))
                    for ((n,_),a),((_,_),b) in zip(prev,curr):
                        bb=tuple(min(a[h],b[h])-(sag if h else 0.) for h in range(3))+tuple(
                            max(a[h+3],b[h+3])+(sag if h else 0.) for h in range(3))
                        for ob,_,q in env:
                            if overlap(bb,q): broad[(i,label,n,ob)]+=1
                prev=curr
    print('path',frames,bad,flush=True)
    # Compare endpoints and pose-critical ranges throughout rear travel. Preserve full ring/component IDs.
    checks={}
    assert len([p for p in old if p[0].startswith('locked_storage_M5_')]) == 4
    stored=old+[p for p in fixed if p[0].startswith('rack_')]
    def hot(y,x,z):return dict((n,s) for n,s,c in _install_plasma(_bare_motion(y,x,z)))
    # Rear approach checks: geometry moves linearly in X/Y/Z. Test independent endpoint bounding boxes.
    ref=hot(1275.,575.,50.); alt=hot(1265.,565.,40.)
    refenv={n:limits(s) for n,s in ref.items()}
    def shifted(y,x,z):
        env=[]
        for n,s in ref.items():
            b=refenv[n];a=altboxes[n];dx=(x-575) if abs(b[0]-a[0]-10)<.001 else 0
            dy=(y-1275) if abs(b[1]-a[1]-10)<.001 else 0
            dz=(z-50) if abs(b[2]-a[2]-10)<.001 else 0
            bb=tuple(v+d for v,d in zip(b,(dx,dy,dz,dx,dy,dz)))
            env.append((n,s,(dx,dy,dz),bb))
        return env
    stored_env=descriptors(stored)
    # Enclose the complete Cartesian operating range per solid. Translations are inferred
    # from the actual two generator poses; non-translation between those poses invalidates the test.
    altboxes={n:limits(s) for n,s in alt.items()}
    for n,b in refenv.items():
        a=altboxes[n]
        for i in range(3):
            assert abs((b[i+3]-a[i+3])-(b[i]-a[i]))<.0001 and min(abs(b[i]-a[i]),abs((b[i]-a[i])-10.))<.0001,(n,i)
    hot_bounds={}
    dims=[]
    for n,s,_,a in shifted(275.,175.,0.):
        hot_bounds[n]=a[:3]
    for n,s,_,b in shifted(1240.,975.,100.):
        bounds=(*hot_bounds[n],*b[3:])
        for sn,ss,sb in stored_env:
            if overlap(bounds,sb):dims.append((n,sn))
    print('continuous candidates',dims[:30], 'transfer broad', list(broad)[:25],flush=True)
    for y in (1240.,1250.,1256.9,1275.):
        hits=set()
        for x in (175.,575.,975.):
            for z in (0.,100.):
                env=shifted(y,x,z)
                for n,s,shift,b in env:
                    for sn,ss,sb in stored_env:
                        if overlap(b,sb) and ss.intersect(s.translate(shift)).Volume()>.05:hits.add((n,sn))
        checks[str(y)]=sorted(hits)
        print('machine',y,checks[str(y)][:12],flush=True)
    report={'test':'elevated storage, final CAD','sampled_poses':frames,'sweep_bbox_candidates':[[*k,v] for k,v in broad.items()],'continuous_full_xyz_hot_rack_candidates':dims,'interferences':[list(k)+[v] for k,v in bad.items()],'hot_rear_samples':checks}
    assert not bad and not dims
    assert all(label==0 and nm.startswith('locator_') and n=='bridge_0_crossrail_1' for i,label,n,nm in broad)
    assert not checks['1240.0'] and checks['1250.0']
    report.update(park_xyz_mm={'head_x':575,'gantry_y':275,'lift_z':100},slots_y_mm=slots,
                  seated_origin_z_mm=seat_z,continuous_hot_range={'head_x':[175,975],'gantry_y':[275,1240],'lift_z':[0,100]},
                  limits='Rigid modeled bodies only. Unmodeled hand/tool/lead, wear, compliance and keeper envelope excluded.',
                  source_sha256={path.name:hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in (Path(__file__),HERE.parent/'build_candidate.py',design.BASE/'motion_context.py',design.BASE/'frame.py')})
    (HERE/'transfer-evidence.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':
    try:run();code=0
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)

