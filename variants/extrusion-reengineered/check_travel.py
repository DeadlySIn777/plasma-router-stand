"""Nominal rigid-axis travel against the XR1 frame/bed; no tool or cable invention."""
from itertools import product
from pathlib import Path
import hashlib,json,os,sys
import re
import params as P
import cadquery as cq
from build import bounds,overlap,clashes
from frame import frame_parts
from bed import bed_parts
from motion import motion_parts,part_motion_class

HERE=Path(__file__).resolve().parent

def run():
    sources=[HERE/n for n in ('params.py','frame.py','bed.py','motion.py','check_travel.py')]
    start_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    states={};poses=[(575.,775.,P.Z_TRAVEL/2),*product((575-P.X_TRAVEL/2,575+P.X_TRAVEL/2),(775-P.Y_TRAVEL/2,775+P.Y_TRAVEL/2),(0.,P.Z_TRAVEL))]
    # Build each nominal pose once, with the two installed tools sharing the
    # same owned motion solids. This preserves actual generated corner poses
    # without rebuilding all eight cached wood configurations for plasma.
    bodies={False:[],True:[]}
    for x,y,z in poses:
        for hot in (False,True):bodies[hot].append(motion_parts(hot,gantry_y=y,head_x=x,z_lift=z))
    for hot in (False,True):
        label='PLASMA' if hot else 'WOOD'
        fixed=frame_parts()+bed_parts(hot);sweeps={};center={};references={};hits=[];tested=0
        internal_hits=[];nominal_threads=[];internal_tested=0
        for ix,(x,y,z) in enumerate(poses):
            parts=bodies[hot][ix]
            r=clashes(parts,fixed);tested+=r['exact_pairs']
            hits.extend(dict(pose=[x,y,z],**h) for h in r['positive_intersections'])
            classes={}
            for part in parts:classes.setdefault(part_motion_class(part[0]),[]).append(part)
            keys=list(classes)
            for ci,ca in enumerate(keys):
                for cb in keys[ci+1:]:
                    rr=clashes(classes[ca],classes[cb]);internal_tested+=rr['exact_pairs']
                    for h in rr['positive_intersections']:
                        names={h['a'],h['b']};nominal=False
                        for axis in ('Y_L','Y_R','X'):
                            if f'HMS_{axis}_BODY' in names and any(re.fullmatch(f'HMS_{axis}_SHOE_BOLT_[1-4]',n) for n in names):
                                nominal=h['volume_mm3']<=31.5
                        record=dict(pose=[x,y,z],**h)
                        (nominal_threads if nominal else internal_hits).append(record)
            for n,s,_ in parts:
                b=bounds(s)
                if ix==0:center[n]=b;sweeps[n]=b.copy();references[n]=s
                else:
                    for k in range(3):sweeps[n][k]=min(sweeps[n][k],b[k]);sweeps[n][k+3]=max(sweeps[n][k+3],b[k+3])
            print(label,'travel pose',x,y,z,'hits',len(hits),flush=True)
        candidates=[];mindistance=None
        for n,b in sweeps.items():
            if all(abs(x-y)<1e-5 for x,y in zip(b,center[n])):continue
            for nf,sf,_ in fixed:
                bf=bounds(sf)
                if overlap(b,bf):candidates.append([n,nf])
                distance=sum(max(0.,b[k]-bf[k+3],bf[k]-b[k+3])**2 for k in range(3))**.5
                if mindistance is None or distance<mindistance[0]:mindistance=[distance,n,nf]
        # A moving solid A+T intersects fixed B iff A intersects B-T. For an
        # axis-aligned box B and translation box T, B-T is exactly another box.
        # The two solid ledger rectangles conservatively contain its real holes.
        unresolved=[];resolved=[]
        fixed_lookup={n:s for n,s,_ in fixed}
        for n,nf in candidates:
            if not (hot and nf.startswith('DRY_LEDGER_') and part_motion_class(n)=='Y_X_Z_tool'):
                unresolved.append([n,nf]);continue
            s=fixed_lookup[nf];bb=bounds(s);t=6.35
            def box(b):return cq.Solid.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],cq.Vector(*b[:3]))
            shelf=bb.copy();shelf[5]=bb[2]+t
            web=bb.copy();web[2]=bb[2]+t
            if '_L_' in nf:web[3]=bb[0]+t
            else:web[0]=bb[3]-t
            envelopes=[shelf,web]
            outside=s.cut(box(shelf).fuse(box(web))).Volume()
            volumes=[];distances=[]
            for b in envelopes:
                expanded=[b[k]-q for k,q in enumerate((P.X_TRAVEL/2,P.Y_TRAVEL/2,P.Z_TRAVEL/2))]+[b[k+3]+q for k,q in enumerate((P.X_TRAVEL/2,P.Y_TRAVEL/2,P.Z_TRAVEL/2))]
                obstacle=box(expanded)
                volumes.append(references[n].intersect(obstacle).Volume())
                distances.append(references[n].distance(obstacle))
            proof={'motion':n,'ledger':nf,'ledger_outside_envelopes_mm3':outside,
                   'expanded_box_intersections_mm3':volumes,'expanded_box_distances_mm':distances}
            if outside<1e-6 and max(volumes)<1e-6 and min(distances)>.01:resolved.append(proof)
            else:unresolved.append([n,nf])
        states[label]={'exact_checks':tested,'sample_intersections':hits,
            'moving_swept_AABB_candidates':unresolved,'conservative_AABB_pairs_resolved_by_exact_translation_proof':resolved,'minimum_swept_bound_gap_mm':mindistance,
            'relative_motion_exact_checks':internal_tested,'relative_motion_sample_intersections':internal_hits,
            'nominal_HMS_shoe_fastener_body_intersections':nominal_threads,
            'nominal_fastener_disposition':'Only BODY vs its own SHOE_BOLT_1..4, max31.5mm3, are separated as inherited nominal carriage-thread envelopes. Actual carriage thread depth and screw-tip clearance remain supplier holds; this is not physical collision clearance.',
            'rigid_translation_clear':not hits and not unresolved,
            'relative_motion_samples_clear_except_nominal_threads':not internal_hits}
    r={'revision':'XR1','poses_X_Yguide_Zlift_mm':poses,'states':states,
       'scope':'Exact external and different-motion-class intersections at center and 8 corners; external union bounds prove clearance for independent pure translations only when candidate list is empty. Internal relative-motion checks are sampled, not a continuous swept-solid proof. Switch/cam compliance and flexible cables are not modeled.',
       'excluded':['actual cutting tool','actual torch nozzle','workpiece and clamps','flexible hoses/cables','conversion trajectory'],
       'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
       'release':False}
    r['source_consistent_during_check']=start_hashes==r['source_sha256']
    (HERE/'review'/'travel-check.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    return 0 if r['source_consistent_during_check'] and all(s['rigid_translation_clear'] and s['relative_motion_samples_clear_except_nominal_threads'] for s in states.values()) else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
