"""Candidate diagnostic of relative rigid translations between motion classes. Derived from frozen XR2 review/check_internal_continuous.py; rerun with candidate_motion_factory including both custom repairs and front-stop mount relocation.

This does not modify the production travel checker. Positive unresolved cover
cells are failed clearance proofs, not automatically confirmed collisions.
"""
from pathlib import Path
from itertools import product, combinations
import hashlib,json,math,os,re,sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import z300_fit_study as S
import custom_joint_repair as R
import front_stop_repair as F
from candidate_motion_factory import motion_parts,part_motion_class
P=S.P;cq=S.cq;bounds=S.bounds;overlap=S.overlap
interface_metadata=S.M.interface_metadata
from sweep_proof import translation_cover_proof
SOURCE_PATHS=[Path(__file__),HERE/'candidate_motion_factory.py',HERE/'front_stop_repair.py',*R.sources(),S.BASE/'sweep_proof.py',S.BASE/'review/check_internal_continuous.py']
def hashes():return {p.relative_to(S.ROOT).as_posix():S.sha(p)for p in dict.fromkeys(SOURCE_PATHS)}
START=hashes()

FACTORS={'stationary':(0,0,0),'Y_gantry_or_drive':(0,1,0),
         'Y_X_head':(1,1,0),'Y_X_Z_tool':(1,1,1)}
ORDER=list(FACTORS)
CENTER=(575.,775.,P.Z_TRAVEL/2)
HALF=(P.X_TRAVEL/2,P.Y_TRAVEL/2,P.Z_TRAVEL/2)
TOL=.05
ROLLERS={'Y_LIMIT_L_FRONT_ROLLER':('Y_CAM_L_FRONT',1,283.,1127.),
         'Y_LIMIT_R_FRONT_ROLLER':('Y_CAM_R_FRONT',1,283.,1127.),
         'X_HOME_ROLLER':('X_HOME_CAM',0,183.,1297.)}
ROLLER_R=2.4;CAM_SLOPE=.63
TANGENT_ALLOWANCE=ROLLER_R*(math.sqrt(1+CAM_SLOPE**2)-1)

def roller_delta(name,pose):
    _,axis,offset,_=ROLLERS[name];inside=offset-pose[axis]
    tangent=TANGENT_ALLOWANCE if 0<inside<12.4 else 0.
    return min(0.,2.3-CAM_SLOPE*max(0.,min(inside,10.))-tangent)if 0<=inside<=30 else 0.

def roller_extra_range(name):
    _,axis,offset,_=ROLLERS[name];inside_max=offset-(CENTER[axis]-HALF[axis])
    # On this declared soft-travel range, inside spans a negative value to8.
    # The cam law is constant then monotone, before its10/12.4mm transitions.
    assert 0<=inside_max<=10 and offset-(CENTER[axis]+HALF[axis])<0
    return (-max(0.,CAM_SLOPE*inside_max+TANGENT_ALLOWANCE-2.3),0.)

def cam_tangency_proof(name,reference,samples):
    cam,axis,offset,H=ROLLERS[name];roller=reference[name];obstacle=reference[cam]
    rb,cb=bounds(roller),bounds(obstacle);leading=CENTER[axis]-(offset-(143. if axis==1 else 53.))
    u0,u1=cb[axis]-1,cb[axis+3]+1;zmin=cb[2]-100
    poly=[(u0,zmin),(u1,zmin),(u1,H-CAM_SLOPE*(u1-leading)),(u0,H-CAM_SLOPE*(u0-leading))]
    if axis==1:
        below=cq.Workplane('YZ',origin=(rb[0],0,0)).polyline(poly).close().extrude(rb[3]-rb[0]).val()
    else:
        below=cq.Workplane('XZ',origin=(0,rb[4],0)).polyline(poly).close().extrude(rb[4]-rb[1]).val()
    below_volume=obstacle.intersect(below).Volume()
    shape_error=max(abs(rb[5]-(H-2.3)),abs(rb[5]-rb[2]-2*ROLLER_R),abs(rb[axis+3]-rb[axis]-2*ROLLER_R))
    max_sample=max(samples)if samples else None
    return {'roller':name,'cam':cam,'passed':below_volume<1e-7 and shape_error<1e-5 and max_sample is not None and max_sample<1e-7,
       'cam_below_ramp_plane_in_roller_axial_slab_mm3':below_volume,'roller_reference_geometry_error_mm':shape_error,
       'max_sample_actual_positive_intersection_mm3':max_sample,'sample_pose_count':len(samples),
       'additional_Z_range_mm':roller_extra_range(name),'maximum_inside_mm':offset-(CENTER[axis]-HALF[axis]),
       'slope':CAM_SLOPE,'radius_mm':ROLLER_R,'tangent_allowance_mm':TANGENT_ALLOWANCE,
       'minimum_ideal_surface_gap_mm':0.,
       'method':'Exact cam material containment above its ramp plane in the roller axial slab, plus analytic circle/plane separation. For inside0..8, deltaZ=min(0,2.3-0.63*inside-r*(sqrt(1+0.63^2)-1)); perpendicular centre distance is at least radius2.4. For inside<0, the leading cam edge is above the free roller. The extra 10/12.4/30mm source-law transitions lie outside soft travel. Nominal tangency is deliberate zero-volume contact, not a positive-penetration exception.',
       'physical_hold':'The small switch lever, actual operating-force/compliance and trip adjustment are not qualified by the roller-only cam-following envelope.'}

def own_nominal_shoe_thread(a,b):
    names={a,b}
    return any(f'HMS_{axis}_BODY'in names and any(re.fullmatch(f'HMS_{axis}_SHOE_BOLT_[1-4]',n)for n in names)
               for axis in ('Y_L','Y_R','X'))

def mating_guide_axis(block,rail):
    y=re.fullmatch(r'Y_BLOCK_([LR])_[12]',block)
    if y and rail=='Y_RAIL_'+y[1]:return 1
    x=re.fullmatch(r'X_BLOCK_([12])_[12]',block)
    if x and rail=='X_RAIL_'+x[1]:return 0
    return None

def guide_prism_proof(block,rail,tmin,tmax):
    b=bounds(rail)
    def prism(q):return cq.Solid.makeBox(q[3]-q[0],q[4]-q[1],q[5]-q[2],cq.Vector(*q[:3]))
    original=prism(b)
    expanded=[b[i]-tmax[i]for i in range(3)]+[b[i+3]-tmin[i]for i in range(3)]
    swept=prism(expanded)
    outside=rail.cut(original).Volume();volume=block.intersect(swept).Volume()
    return {'passed':outside<1e-7 and volume<1e-7,
            'actual_rail_outside_reference_prism_mm3':outside,
            'swept_rail_prism_bounds_mm':expanded,'translation_min_mm':tmin,'translation_max_mm':tmax,
            'block_intersection_with_full_swept_rail_prism_mm3':volume,
            'minimum_modeled_gap_mm':block.distance(swept),
            'method':'The generated rail is an exact-tested subset of its full reference bounding prism. Expanding that prism by the negative relative translation box contains the complete rail sweep. Zero block intersection therefore proves continuous nonpenetration, including zero modeled bearing-interface running gap. Only exact matched HGR rail/block IDs use this case.',
            'supplier_qualification':False}

def run():
    closure_start=interface_metadata()['source_sha256']
    result={'revision':'OWNED_FAMILY_Z300_WORK200_WITH_CARRIER_AND_FRONT_STOP_REPAIRS','release':False,'source_sha256':START,
            'motion_source_closure_sha256':closure_start,'states':{},
            'center_pose_X_Yguide_Z_mm':CENTER,'class_axis_factors_X_Y_Z':FACTORS,
            'scope':'Corner validation of each named solid as its declared rigid translation, with three explicit source-law cam followers. Continuous relative translation proofs cancel shared axes; conservative independent-Z boxes bound each follower and also test follower pairs within a class. Designed roller/cam tangency is separately proved analytically. Other same-class rigid assembly self-intersections, frame/bed/accessory collisions, flex cables, measured compliance, contact loads and dynamics are outside this diagnostic.',
            'numeric_thresholds':{'translation_bound_mm':1e-5,'shape_sym_difference_mm3':TOL,'intersection_mm3':TOL,'cam_zero_volume_mm3':1e-7,'proof_gap_mm':.01},
            'nominal_thread_rule':'Only HMS_Y_L/Y_R/X_BODY against its own exact HMS_axis_SHOE_BOLT_1..4, max31.5mm3 sampled overlap, can be separated as inherited nominal thread envelopes. This is not proof of actual thread fit or screw depth.'}
    geometry_checked={}
    for hot in(False,True):
        label='PLASMA'if hot else'WOOD'
        reference={n:s for n,s,_ in motion_parts(hot,*[CENTER[i] for i in (1,0,2)])}
        classes={n:part_motion_class(n)for n in reference}
        validation={'parts':len(reference),'class_counts':{k:sum(v==k for v in classes.values())for k in ORDER},
                    'corner_instances':0,'exact_shape_comparisons':0,'shared_geometry_reused':0,
                    'max_bound_error_mm':0.,'max_shape_sym_difference_mm3':0.,'failures':[]}
        nominal_samples={};contact_samples={n:[]for n in ROLLERS}
        poses=[CENTER,*product((CENTER[0]-HALF[0],CENTER[0]+HALF[0]),
                              (CENTER[1]-HALF[1],CENTER[1]+HALF[1]),(0.,P.Z_TRAVEL))]
        for ip,pose in enumerate(poses):
            actual={n:s for n,s,_ in motion_parts(hot,pose[1],pose[0],pose[2])}
            if set(actual)!=set(reference):
                validation['failures'].append({'pose':pose,'missing':sorted(set(reference)-set(actual)),'extra':sorted(set(actual)-set(reference))})
                continue
            if ip:
                for n,s in actual.items():
                    validation['corner_instances']+=1;f=FACTORS[classes[n]]
                    delta=tuple((pose[i]-CENTER[i])*f[i]for i in range(3));expected=reference[n].translate(delta)
                    if n in ROLLERS:expected=expected.translate((0,0,roller_delta(n,pose)-roller_delta(n,CENTER)))
                    b0,b1=bounds(expected),bounds(s);err=max(abs(x-y)for x,y in zip(b0,b1))
                    validation['max_bound_error_mm']=max(validation['max_bound_error_mm'],err)
                    # Reuse requires identical actual AND reference topology
                    # and the same declared translation class in both modes.
                    key=(n,pose)
                    old=geometry_checked.get(key)
                    if old and s.isSame(old[0]) and reference[n].isSame(old[1]) and classes[n]==old[2]:
                        validation['shared_geometry_reused']+=1;diff=0.
                    elif s.isSame(expected):diff=0.
                    else:
                        validation['exact_shape_comparisons']+=1
                        diff=max(0.,s.Volume()+expected.Volume()-2*s.intersect(expected).Volume())
                    geometry_checked[key]=(s,reference[n],classes[n])
                    validation['max_shape_sym_difference_mm3']=max(validation['max_shape_sym_difference_mm3'],diff)
                    if err>1e-5 or diff>TOL:
                        failure={'name':n,'class':classes[n],'pose':pose,'bound_error_mm':err,'shape_sym_difference_mm3':diff}
                        validation['failures'].append(failure)
                        print(label,'CLASS_TRANSLATION_FAILURE',json.dumps(failure),flush=True)
                print(label,'translation corner',ip,'failures',len(validation['failures']),flush=True)
            for axis in('Y_L','Y_R','X'):
                body=f'HMS_{axis}_BODY'
                for j in range(1,5):
                    bolt=f'HMS_{axis}_SHOE_BOLT_{j}'
                    if body in actual and bolt in actual:
                        volume=actual[body].intersect(actual[bolt]).Volume()
                        key=(body,bolt);nominal_samples.setdefault(key,[]).append(volume)
            for name,(cam,_,_,_)in ROLLERS.items():
                contact_samples[name].append(actual[name].intersect(actual[cam]).Volume())
        validation['passed']=not validation['failures']
        state={'translation_validation':validation,'continuous_proofs':[],
               'cam_follower_extra_Z_bounds_mm':{n:roller_extra_range(n)for n in ROLLERS},
               'designed_zero_volume_cam_contacts':[],'nominal_guide_prism_proofs':[],
               'nominal_thread_envelopes':[],'unresolved_pairs':[],
               'cross_class_pairs':0,'same_class_follower_pairs':0,'broadphase_candidates':0}
        if validation['passed']:
            bb={n:bounds(s)for n,s in reference.items()}
            contact_pairs={frozenset((n,v[0])):n for n,v in ROLLERS.items()}
            for ca,cb in [*combinations(ORDER,2),*[(k,k)for k in ORDER]]:
                # Higher class is the moving reference. Signed factors cancel
                # all physical shared axes rather than treating them independent.
                fa,fb=FACTORS[cb],FACTORS[ca]
                base_max=[HALF[i]*abs(fa[i]-fb[i])for i in range(3)];base_min=[-q for q in base_max]
                movers=[n for n in reference if classes[n]==cb]
                obstacles=[n for n in reference if classes[n]==ca]
                for n in movers:
                    for nf in obstacles:
                        if ca==cb:
                            if n>=nf or not(n in ROLLERS or nf in ROLLERS):continue
                            state['same_class_follower_pairs']+=1
                        else:state['cross_class_pairs']+=1
                        tmin=base_min.copy();tmax=base_max.copy()
                        if n in ROLLERS:
                            lo,hi=roller_extra_range(n);tmin[2]+=lo;tmax[2]+=hi
                        if nf in ROLLERS:
                            lo,hi=roller_extra_range(nf);tmin[2]-=hi;tmax[2]-=lo
                        b=bb[n];swept=[b[i]+tmin[i]for i in range(3)]+[b[i+3]+tmax[i]for i in range(3)]
                        if not overlap(swept,bb[nf]):continue
                        state['broadphase_candidates']+=1
                        pair=frozenset((n,nf))
                        if pair in contact_pairs:
                            name=contact_pairs[pair];q=cam_tangency_proof(name,reference,contact_samples[name])
                            state['designed_zero_volume_cam_contacts'].append(q)
                            if not q['passed']:state['unresolved_pairs'].append(q)
                            continue
                        guide_axis=mating_guide_axis(n,nf)
                        if guide_axis is not None:
                            q={'moving':n,'obstacle':nf,**guide_prism_proof(reference[n],reference[nf],tmin,tmax)}
                            state['nominal_guide_prism_proofs'].append(q)
                            if not q['passed']:state['unresolved_pairs'].append(q)
                            continue
                        if own_nominal_shoe_thread(n,nf):
                            sample=nominal_samples.get((nf,n),nominal_samples.get((n,nf),[]))
                            if sample and max(sample)<=31.5:
                                state['nominal_thread_envelopes'].append({'a':n,'b':nf,'sample_pose_count':len(sample),'max_sample_overlap_mm3':max(sample),'thread_fit_qualified':False})
                                continue
                        proof=translation_cover_proof(reference[n],reference[nf],tmin,tmax)
                        record={'moving':n,'moving_class':cb,'obstacle':nf,'obstacle_class':ca,**proof}
                        state['continuous_proofs'].append(record)
                        if not proof['passed']:
                            state['unresolved_pairs'].append(record)
                            print(label,'UNRESOLVED',n,nf,json.dumps(proof['unresolved_cells']),flush=True)
                        if len(state['continuous_proofs'])%25==0:
                            print(label,'relative proofs',len(state['continuous_proofs']),'unresolved',len(state['unresolved_pairs']),flush=True)
        state['continuous_relative_clear_except_nominal_threads']=validation['passed']and not state['unresolved_pairs']
        result['states'][label]=state
        result['end_source_sha256']=hashes()
        result['source_consistent_during_check']=START==result['end_source_sha256']and closure_start==interface_metadata()['source_sha256']
        result['complete']=set(result['states'])=={'WOOD','PLASMA'}
        result['passed']=result['complete']and result['source_consistent_during_check']and all(s['continuous_relative_clear_except_nominal_threads']for s in result['states'].values())
        (HERE/'output/candidate-internal-continuous-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(label,'relative clear',state['continuous_relative_clear_except_nominal_threads'],flush=True)
    return 0 if result['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
