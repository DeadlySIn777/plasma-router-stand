"""Nominal ZBX80-300 packaging overlay on frozen XR2; no OEM holes invented.

This is an incremental bulk-fit study, not a replacement machine revision.
The preferred study retains XR2's existing carrier and its 200 mm working box.
An optional longer carrier and unowned brake motor are compared separately.
"""
from pathlib import Path
from itertools import product,combinations
import hashlib,json,os,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=HERE.parent/'extrusion-reengineered'
sys.path.insert(0,str(BASE))
import cadquery as cq
import motion as M
import params as P
from frame import frame_parts
from bed import bed_parts
from build import accessory_parts,bounds,overlap
from material_cover import translation_cover_proof

OUT=HERE/'output';OUT.mkdir(exist_ok=True)
BODY=419.;STOCK_OVERALL=530.;CATALOG_STROKE=300.;WORKING_STROKE=200.
CENTER=(575.,775.,100.)
OLD_MOTOR='ZBX80_BRAKE_MOTOR_CANDIDATE'
STOCK_MOTOR='Z300_STOCK_MOTOR_NOMINAL'
BRAKE_MOTOR='Z300_OPTIONAL_BRAKE_NOT_OWNED'
MOVED=('ZBX80_BASE','ZBX80_END_TOP','ZBX80_COUPLER_GUARD',OLD_MOTOR)
FACTORS={'stationary':(0,0,0),'Y_gantry_or_drive':(0,1,0),
         'Y_X_head':(1,1,0),'Y_X_Z_tool':(1,1,1)}
FOLLOWERS={'Y_LIMIT_L_FRONT_ROLLER','Y_LIMIT_R_FRONT_ROLLER','X_HOME_ROLLER'}
BASELINE_JOINT_VOLUMES={}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def box(b):return cq.Solid.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],cq.Vector(*b[:3]))
def cls(n):
    return 'Y_X_head' if n in (STOCK_MOTOR,BRAKE_MOTOR) else M.part_motion_class(n)

def overlay(parts,*,stroke=300,brake=False,extended_carrier=False):
    growth=float(stroke)-200
    out=[]
    for n,s,c in parts:
        b=bounds(s)
        if n=='ZBX80_BASE':
            b[5]+=growth;s=box(b)
        elif n in ('ZBX80_END_TOP','ZBX80_COUPLER_GUARD'):
            s=s.translate((0,0,growth))
        elif n==OLD_MOTOR:
            b[2]+=growth;b[5]=b[2]+(88 if brake else 56)
            s=box(b);n=BRAKE_MOTOR if brake else STOCK_MOTOR;c=(.18,.20,.22)
        elif n=='Z_CARRIER' and extended_carrier:
            ext=b.copy();ext[2]=b[5];ext[5]+=100
            s=s.fuse(box(ext)).clean()
        out.append((n,s,c))
    return out

def added_parts(original,new):
    old={n:s for n,s,_ in original};out=[]
    for n,s,c in new:
        key=OLD_MOTOR if n in (STOCK_MOTOR,BRAKE_MOTOR) else n
        if key not in MOVED and key!='Z_CARRIER':continue
        add=s.cut(old[key])
        if add.Volume()>1e-7:out.append((n,add,c))
    return out

def shifted(part,pose):
    n,s,c=part;f=FACTORS[cls(n)]
    return n,s.translate(tuple((pose[k]-CENTER[k])*f[k] for k in range(3))),c

def known_internal(n,nf):
    return {n,nf} in ({'ZBX80_BASE','ZBX80_END_BOTTOM'},
                     {'ZBX80_BASE','ZBX80_END_TOP'})

def exact_pairs(a,b):
    hits=[];nominal=[];count=0
    fixed=[(n,s,bounds(s))for n,s,_ in b]
    for n,s,_ in a:
        bs=bounds(s)
        for nf,sf,bf in fixed:
            if n==nf or not overlap(bs,bf):continue
            count+=1;v=s.intersect(sf).Volume()
            if v>.05:
                r=dict(a=n,b=nf,volume_mm3=v)
                expected=BASELINE_JOINT_VOLUMES.get(frozenset((n,nf)))
                retained_joint=known_internal(n,nf) and expected is not None and abs(v-expected)<.05
                if retained_joint:r['same_as_baseline_volume_mm3']=expected
                (nominal if retained_joint else hits).append(r)
    return dict(exact_pairs=count,unexpected=hits,nominal_stage_envelope_joints=nominal)

def relative_proof(added,obstacles):
    records=[];broad_clear=0
    for n,s,_ in added:
        cf=FACTORS[cls(n)]
        for nf,sf,_ in obstacles:
            ff=FACTORS[cls(nf)]
            span=(P.X_TRAVEL/2,P.Y_TRAVEL/2,WORKING_STROKE/2)
            lo=[-abs(cf[k]-ff[k])*span[k] for k in range(3)]
            hi=[ abs(cf[k]-ff[k])*span[k] for k in range(3)]
            # Follower's complete source-supported extra Z range is already
            # independently checked in XR2; this enlarged box contains it.
            if nf in FOLLOWERS:hi[2]+=3.17657258
            b=bounds(s);sweep=[b[k]+lo[k]for k in range(3)]+[b[k+3]+hi[k]for k in range(3)]
            if not overlap(sweep,bounds(sf)):
                broad_clear+=1;continue
            q=translation_cover_proof(s,sf,lo,hi)
            records.append(dict(moving=n,obstacle=nf,**q))
    return dict(passed=all(r['passed']for r in records),broad_phase_clear_pairs=broad_clear,
        exact_candidate_pairs=len(records),proofs=records)

def external_proof(added,fixed):
    records=[];clear=0
    lo=[-P.X_TRAVEL/2,-P.Y_TRAVEL/2,0.];hi=[P.X_TRAVEL/2,P.Y_TRAVEL/2,0.]
    for n,s,_ in added:
        b=bounds(s);swept=[b[k]+lo[k]for k in range(3)]+[b[k+3]+hi[k]for k in range(3)]
        for nf,sf,_ in fixed:
            if not overlap(swept,bounds(sf)):clear+=1;continue
            q=translation_cover_proof(s,sf,lo,hi)
            records.append(dict(moving=n,fixed=nf,**q))
    return dict(passed=all(r['passed']for r in records),broad_phase_clear_pairs=clear,
        exact_candidate_pairs=len(records),proofs=records)

def export(parts,name):
    path=OUT/name;a=cq.Assembly(name=path.stem)
    for n,s,c in parts:a.add(s,name=n,color=cq.Color(*c))
    a.save(str(path))
    back=cq.importers.importStep(str(path)).val()
    expected=sum(s.Volume() for _,s,_ in parts)
    error=abs(back.Volume()-expected)
    valid=back.isValid() and len(back.Solids())==sum(len(s.Solids())for _,s,_ in parts) and error<max(.1,expected*1e-7)
    return dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),valid=valid,
        solid_count=len(back.Solids()),roundtrip_volume_error_mm3=error)

def head(parts):
    return [p for p in parts if p[0]=='Z_CARRIER' or p[0].startswith(('ZBX80_','Z300_','TOOL_'))]

def draw_comparison(scenes):
    from preview import legacy
    from PIL import Image,ImageDraw
    canvas=Image.new('RGB',(1800,1000),'#f3f6f7');d=ImageDraw.Draw(canvas)
    ink='#17343e';mut='#4b6670';font=legacy.font
    d.text((35,20),'OWNED Z300 / NOMINAL FIT STUDY',font=font(37,True),fill=ink)
    d.text((38,72),'Same camera and scale. Same lower mounting datum and spindle position. No gantry raise.',font=font(22),fill=mut)
    rows=[('200 mm family / stock motor','430 mm package; top Z1470',scenes['Z200_STOCK']),
          ('Owned 300 mm family / stock motor','530 mm package; top Z1570',scenes['Z300_STOCK_EXISTING_CARRIER']),
          ('300 mm / optional brake motor','562 mm conditional package; top Z1602',scenes['Z300_OPTIONAL_BRAKE'])]
    for i,(title,sub,parts) in enumerate(rows):
        left=30+590*i
        d.rounded_rectangle((left,118,left+570,836),radius=12,fill='#e8eff1',outline='#c6d6db',width=2)
        d.text((left+15,137),title,font=font(24,True),fill=ink)
        d.text((left+15,173),sub,font=font(20),fill=mut)
        image=legacy.render(head(parts),w=1400,h=1600)
        # The renderer uses a fixed camera and 1125 mm parallel scale; its
        # crop changes framing only. Apply one common resize, never per-panel fit.
        image=image.resize((round(image.width*1.25),round(image.height*1.25)),Image.Resampling.LANCZOS)
        assert image.width<550 and image.height<600,(image.size,title)
        canvas.paste(image,(left+(570-image.width)//2,805-image.height))
    d.text((39,862),'Existing 270.2 mm carrier retained in all three views. Actual support/nut layout remains unverified.',font=font(22,True),fill=ink)
    d.text((39,904),'Optional 370.2 mm carrier is a separate comparison, not a required purchase; it exceeds a 304.8 mm blank.',font=font(21),fill=mut)
    d.text((39,944),'Bulk fit only. Actual stage mass, delivered interfaces, retention, stiffness and full 300 mm operating travel remain open.',font=font(20),fill=mut)
    path=OUT/'z300-head-comparison.png';canvas.save(path)
    return dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),common_camera_and_scale=True)

def run():
    inputs=[Path(__file__),BASE/'motion.py',BASE/'params.py',BASE/'frame.py',BASE/'bed.py',
        BASE/'shields.py',BASE/'atc.py',BASE/'build.py',BASE/'material_cover.py',BASE/'preview.py',
        BASE.parent/'extrusion-wood-plasma'/'preview.py',BASE/'review/internal-continuous-check.json']
    evidence=HERE/'owned-hardware-evidence.json'
    if evidence.exists():inputs.append(evidence)
    inputs += [ROOT/n for n in M.interface_metadata()['source_sha256']]
    inputs=list(dict.fromkeys(inputs))
    hashes=lambda:{p.relative_to(ROOT).as_posix():sha(p)for p in inputs}
    start=hashes()
    internal=json.loads((BASE/'review/internal-continuous-check.json').read_text())
    assert internal['passed'] and internal['source_consistent_during_check']
    for key,h in internal['source_sha256'].items():assert sha(BASE/key)==h,key
    original=M.motion_parts(False,gantry_y=CENTER[1],head_x=CENTER[0],z_lift=CENTER[2])
    lookup={n:s for n,s,_ in original}
    for n in ('ZBX80_END_BOTTOM','ZBX80_END_TOP'):
        BASELINE_JOINT_VOLUMES[frozenset(('ZBX80_BASE',n))]=lookup['ZBX80_BASE'].intersect(lookup[n]).Volume()
    cases={
        'Z300_STOCK_EXISTING_CARRIER':overlay(original),
        'Z300_OPTIONAL_BRAKE':overlay(original,brake=True),
        'Z300_OPTIONAL_EXTENDED_CARRIER':overlay(original,extended_carrier=True)}
    report={'study':'NOMINAL_OWNED_ZBX80_300_INCREMENTAL_BULK_FIT_ONLY',
        'owned_catalog_stroke_mm':CATALOG_STROKE,'assessed_working_stroke_mm':WORKING_STROKE,
        'actual_delivered_interfaces_verified':False,'gantry_raise_mm':0,
        'nominal_family_dimensions_mm':dict(base=BODY,stock_motor_overall=STOCK_OVERALL,width=80),
        'actual_stage_mass_kg':None,'mass_note':'Do not derive supplier actuator mass from solid envelope volumes.',
        'cases':{},'source_sha256':start,'fabrication_release':False,'physical_rigidity_qualified':False}
    poses=[CENTER,*product((175.,975.),(275.,1275.),(0.,WORKING_STROKE))]
    for case,cold in cases.items():
        changed_names=set(MOVED)-{OLD_MOTOR}
        changed_names.add(BRAKE_MOTOR if 'BRAKE' in case else STOCK_MOTOR)
        if 'EXTENDED' in case:changed_names.add('Z_CARRIER')
        additions=added_parts(original,cold)
        valid=[n for n,s,c in cold if n in changed_names and (not s.isValid()or len(s.Solids())!=1)]
        modes={}
        for hot in (False,True):
            whole=M._add_plasma(cold) if hot else cold
            unchanged=[p for p in whole if p[0]not in changed_names]
            fixed=frame_parts()+bed_parts(hot)+accessory_parts(hot)
            relative=relative_proof(additions,unchanged)
            external=external_proof(additions,fixed)
            samples=[]
            for pose in poses:
                moving=[shifted(p,pose)for p in whole]
                changed=[p for p in moving if p[0]in changed_names]
                rest=[p for p in moving if p[0]not in changed_names]
                cross=exact_pairs(changed,rest+fixed)
                local=exact_pairs(changed,changed)
                samples.append(dict(pose_X_Yguide_Zlift_mm=pose,cross=cross,changed_self=local))
            passed=not valid and relative['passed'] and external['passed'] and all(not s['cross']['unexpected']and not s['changed_self']['unexpected'] for s in samples)
            modes['PLASMA'if hot else'WOOD']=dict(passed=passed,incremental_relative=relative,
                incremental_external=external,whole_changed_part_samples=samples)
            print(case,'PLASMA'if hot else'WOOD','PASS',passed,'newmaterial candidates',relative['exact_candidate_pairs']+external['exact_candidate_pairs'],flush=True)
            if not passed:print('DETAIL',valid,[s for s in samples if s['cross']['unexpected']or s['changed_self']['unexpected']][:1],flush=True)
        report['cases'][case]=dict(changed_parts=sorted(changed_names),invalid=valid,modes=modes,
            passed=all(m['passed']for m in modes.values()))
    # Preserve the actual zero-lift tool setup for common-scale visual comparison.
    zero=M.motion_parts(False,gantry_y=775,head_x=575,z_lift=0)
    scenes={'Z200_STOCK':overlay(zero,stroke=200),
        'Z300_STOCK_EXISTING_CARRIER':overlay(zero),
        'Z300_OPTIONAL_BRAKE':overlay(zero,brake=True),
        'Z300_OPTIONAL_EXTENDED_CARRIER':overlay(zero,extended_carrier=True)}
    exports={name:export(head(parts),name+'.step')for name,parts in scenes.items()}
    picture=draw_comparison(scenes)
    carrier=next(s for n,s,c in zero if n=='Z_CARRIER');cb=bounds(carrier)
    report['carrier_comparison']=dict(existing_height_mm=cb[5]-cb[2],
        stage_base_Z_mm=[1040,1459],existing_carrier_Z_mm=[cb[2],cb[5]],
        axial_support_overlap_mm=min(cb[5],1459)-max(cb[2],1040),
        upper_base_extent_above_carrier_mm=1459-cb[5],
        optional_extended_height_mm=cb[5]-cb[2]+100,
        optional_added_nominal_Al_kg=(cb[3]-cb[0])*(cb[4]-cb[1])*100*2.7e-6,
        optional_extension_required=False,support_capacity_verified=False)
    report['height_comparison_mm']=dict(module_lower_Z=1040,Z200_stock_top=1470,
        current_XR2_Z200_brake_candidate_top=1502,Z300_stock_top=1570,
        Z300_optional_brake_top=1602,stock_to_stock_increase=100,
        owned_stock_vs_XR2_conditional_brake_increase=68)
    report['conditional_full_stroke_arithmetic']=dict(assumed_reference_zero_Z=970,
        reference_at300=1270,loaded_tool_projection=50,kit_top=1110.15,
        loaded_tool_tip_at300=1220,flyover_gap_at300=109.85,
        full300_operating_domain_simulated=False)
    report['method']='Only modified parts and their newly added material are screened. Shared axis translations are canceled for relative proofs, with the complete XR2 cam-follower Z bound. Existing two base/endcap envelope overlaps are recorded separately; nominal manufacturer internals are not qualified. Unchanged XR2 geometry is referenced, not reapproved.'
    report['outputs']=exports;report['comparison_image']=picture
    report['source_consistent_during_check']=start==hashes()
    report['passed']=report['source_consistent_during_check']and all(c['passed']for c in report['cases'].values())and all(e['valid']for e in exports.values())
    report['source_sha256']=hashes()
    (OUT/'z300-fit-study.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'case_passes':{k:v['passed']for k,v in report['cases'].items()},'heights':report['height_comparison_mm']},indent=2),flush=True)
    return 0 if report['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
