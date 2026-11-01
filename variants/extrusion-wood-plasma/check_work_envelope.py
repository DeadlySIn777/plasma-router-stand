"""Axis-aligned swept-bound check against the new frame and actual mode bed.

The independent axes translate; the table describes travel of the nominal rigid
solids with tool exchange complete. MDF/backers and stored carriers use the correct
mode. No cutter, workpiece, flexible leads, human handling or ATC asserted.
"""
from itertools import product
from pathlib import Path
import hashlib,json,math,os,sys
from motion_context import HERE,ROOT,POSE,_bare_motion,_install_plasma,bbox
from frame import frame_parts,bolted_datums,wet_support_option
from process_bed import bed_parts
from cad_helpers import intersection_volume


def extents(parts):
    return [(n,s,bbox(s)) for n,s,_ in parts]


def gap(a,b):
    return math.sqrt(sum(max(0.,a[j]-b[j+3],b[j]-a[j+3])**2 for j in range(3)))


def overlap(a,b):
    return all(min(a[k+3],b[k+3])-max(a[k],b[k])>1e-5 for k in range(3))


def check():
    fixed=[extents(frame_parts()+wet_support_option()+bed_parts(mode)) for mode in (False,True)]
    # Only change the datum holes once, since these members do not move.
    datum_replacements=bolted_datums([p for p in _bare_motion(**POSE) if p[0] in ('Y_DATUM_L','Y_DATUM_R')])
    swept=[{},{}]; center=[{},{}]; sample_hits=[[],[]]; finite_pairs=[0,0]
    poses=[(575.,775.,50.),*product((175.,975.),(275.,1275.),(0.,100.)),(175.,775.,0.),(975.,775.,0.)]
    for ix,p in enumerate(poses):
        x,y,z=p; bare=_bare_motion(y,x,z)
        for mode,body in ((0,bare),(1,_install_plasma(bare))):
            for n,s,b in extents([v for v in body if v[0] not in ('Y_DATUM_R','Y_DATUM_L')]+datum_replacements):
                if ix==0:
                    swept[mode][n]=b.copy();center[mode][n]=b.copy()
                sw=swept[mode][n]
                for j in range(3):sw[j]=min(sw[j],b[j]);sw[j+3]=max(sw[j+3],b[j+3])
                for name,shape,fbox in fixed[mode]:
                    if not overlap(b,fbox):continue
                    finite_pairs[mode]+=1
                    v=intersection_volume(s,shape)
                    if v>.02:
                        sample_hits[mode].append({'pose':p,'motion':n,'obstacle':name,'mm3':round(v,5)})
        print('Checked external collisions',p,'hits so far',list(map(len,sample_hits)),flush=True)
    report={}
    for mode,label in enumerate(('wood','plasma')):
        unresolved=[]; nearest=[]; ig=[]; nearest_head=[]; nearest_rack=[]; fixed_candidates=[]
        for n,b in swept[mode].items():
            # Cams can displace a fixed limit microswitch roller between sampled
            # states. Expand its swept support conservatively (roller radius 2.4,
            # cam rise 6.3); these rollers remain a long way above the external bed.
            if n.endswith('_ROLLER') and (n.startswith('X_HOME') or n.startswith('Y_LIMIT')):
                b=b.copy();b[2]-=8;b[5]+=8
            moving=any(abs(a-c)>1e-5 for a,c in zip(b,center[mode][n]))
            for nm,_,f in fixed[mode]:
                if not moving:
                    if overlap(b,f):fixed_candidates.append((n,nm))
                    continue
                if overlap(b,f):unresolved.append((n,nm))
                record=(round(gap(b,f),5),n,nm)
                nearest.append(record)
                if (n.startswith(('I_HEAD_','WP_')) if mode else n.startswith('TOOL_SPINDLE_')):nearest_head.append(record)
                if nm.startswith('RACK_') or nm.startswith('BED_bridge_') and 'parked' in nm:nearest_rack.append(record)
        report[label]={'fixed_frame_bed_objects':len(fixed[mode]),'motion_objects':len(swept[mode]),
            'finite_shape_positive_overlap_checks':finite_pairs[mode],'fixed_mount_BB_overlap_pairs':fixed_candidates,
            'sampled_positive_intersection_mm3':sample_hits[mode],
            'moving_swept_AABB_positive_overlap_pairs':unresolved,
            'smallest_moving_vs_external_AABB_clearance_mm':min(nearest),
            'smallest_working_head_vs_external_AABB_clearance_mm':min(nearest_head),
            'smallest_moving_vs_rack_or_stored_panels_AABB_clearance_mm':min(nearest_rack)}
    sources=[HERE/n for n in ('check_work_envelope.py','motion_context.py','process_bed.py','frame.py')]
    report={'scope':'Nominal as-modeled whole XYZ rigid motion vs actual external frame and complete bed for each operating state. Swept axis-aligned boxes are conservative clearance bounds for pure translation; switches widened for cam/roll excursion. Separately checks all stationary interfaces with nominal solids at sample poses.',
            'assumptions':'Independent translational axes over stated ranges; float seated and breakaway seated. No rotation of main bodies or flexible leads. Installed mode only, not bed conversion. Identically fixed reference faces can intentionally touch.',
            'poses_X_Yguide_Zlift':poses,'states':report,'passed':all(not v['moving_swept_AABB_positive_overlap_pairs'] and not v['sampled_positive_intersection_mm3'] for v in report.values()),
            'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (HERE/'motion-detail'/'external-envelope.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for k,v in report['states'].items():print(k,{n:r for n,r in v.items() if 'fixed_mount' not in n},flush=True)
    return 0 if report['passed'] else 1


if __name__=='__main__':
    try:code=check()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
