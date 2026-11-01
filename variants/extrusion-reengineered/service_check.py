"""Cold hatch access and staged pan/tote replacement collision evidence."""
from pathlib import Path
from math import sqrt,pi,sin,cos,atan2,radians
import hashlib,json,os,sys
import cadquery as cq
import params as P
import bed as B
import bed_service as S
from build import clashes,bounds
HERE=Path(__file__).resolve().parent
OUT=HERE/'review'

def union_bounds(parts):
    b=[bounds(s) for _,s,_ in parts]
    return [min(q[i] for q in b) for i in range(3)]+[max(q[i] for q in b) for i in range(3,6)]

def bboxshape(b):return B.box(*b[:3],*(b[i+3]-b[i] for i in range(3)))

def mergebox(a,b):return [min(a[i],b[i]) for i in range(3)]+[max(a[i],b[i]) for i in range(3,6)]

def check_sweep(label,b,obstacles):
    r=clashes([(label,bboxshape(b),B.AL)],obstacles)
    r.update(label=label,bounds_mm=b,within_plan=b[0]>=-1e-5 and b[3]<=1150+1e-5 and b[1]>=-1e-5 and b[4]<=1450+1e-5)
    r['passed']=not r['positive_intersections'] and r['within_plan'];return r

def rotation_enclosure(shape,py,pz,lo=-pi/2,hi=0.):
    b=bounds(shape);yr=[];zr=[]
    def extrema(A,C):
        ts=[lo,hi];t=atan2(C,A)
        ts += [t+k*pi for k in range(-3,4) if lo<=t+k*pi<=hi]
        vs=[A*cos(q)+C*sin(q) for q in ts];return min(vs),max(vs)
    for y in (b[1]-py,b[4]-py):
        for z in (b[2]-pz,b[5]-pz):yr.append(extrema(y,-z));zr.append(extrema(z,y))
    return [b[0],py+min(v[0] for v in yr),pz+min(v[0] for v in zr),
       b[3],py+max(v[1] for v in yr),pz+max(v[1] for v in zr)]

def run():
    OUT.mkdir(exist_ok=True)
    files=[HERE/n for n in ('params.py','bed.py','frame.py','motion.py','build.py','bed_service.py','service_check.py','shields.py','atc.py','reservoir-interface.json') if (HERE/n).exists()]
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    acc,missing=S.accessories();frame=S.frame_parts();motion=S.bare_motion()
    hatch_ids={n for n,s,c in B.receiver_hatch_parts(False)}
    bed=B.bed_parts(True)
    external=[q for q in bed if q[0] not in hatch_ids]+frame+motion+acc
    # Full continuous enclosure over0..90degrees, including ear and knuckle radius.
    closed_cover=next(q[1] for q in B.receiver_hatch_parts(False) if q[0].startswith('RECEIVER_HATCH_COVER_'))
    env=rotation_enclosure(closed_cover,B.HATCH_AXIS_Y,B.HATCH_AXIS_Z)
    hatch_external=check_sweep('HATCH_CONTINUOUS_ENCLOSURE',env,external)
    openparts=B.receiver_hatch_parts(True)
    open_self=clashes(openparts,openparts,True)
    hinge_fixed=[q for q in B.receiver_hatch_parts(False) if not q[0].startswith((
       'RECEIVER_HATCH_COVER_','RECEIVER_HATCH_M4x16_KNOB_',
       'RECEIVER_HATCH_OPEN_INDEX_PIN_','RECEIVER_HATCH_INDEX_R_CLIP_'))]
    cover=next(s for n,s,c in B.receiver_hatch_parts(False) if n.startswith('RECEIVER_HATCH_COVER_'))
    hinge_checks=[]
    for angle in (0,.01,.05,.1,.2,1,5,15,30,45,60,75,89,90):
        moved=cover.rotate((0,B.HATCH_AXIS_Y,B.HATCH_AXIS_Z),(1,B.HATCH_AXIS_Y,B.HATCH_AXIS_Z),-angle)
        hinge_checks.append({'angle_deg':angle,**clashes([('MOVING_HATCH',moved,B.HOT)],hinge_fixed)})
    # Reachability proof: distance to a convex inset entry rectangle is convex;
    # maximum over the entire floor-centre rectangle occurs at a corner.
    brush=[];maxreach=0.;scene=S.service_scene('hatch_open')
    for x in (253.,897.):
        for y in (734.,1136.):
            a=cq.Vector(x,y,34.);e=cq.Vector(min(max(x,320.),830.),min(max(y,890.),1080.),394.)
            v=e-a;length=v.Length;maxreach=max(maxreach,length)
            rod=cq.Solid.makeCylinder(5.,450.,a,v.normalized())
            head=B.box(x-30,y-30,4,60,60,60)
            hit=clashes([('BRUSH_HANDLE',rod,B.AL),('BRUSH_HEAD',head,B.AL)],scene)
            brush.append({'floor_head_centre_mm':[x,y,34.],'entry_mm':list(e.toTuple()),'required_handle_to_entry_mm':length,**hit})
    # Rare replacement only: power isolated,alltoolsremoved,allslatsremoved;
    # remove heatshields/ledgers/frontarms, NOT HGRrails; disconnect wet union.
    fixed,missing2=S.replacement_fixed()
    tote=S.tote_assembly()
    coil=S.coiled_hose()
    fixed_with_tote=fixed+tote+coil+[q for q in S.temporary_pan_supports() if q[0].startswith('SERVICE_DUNNAGE_')]
    pan_checks=[]
    def trig_extrema(A,C,lo,hi):
        ts=[lo,hi];t=atan2(C,A)
        ts += [t+k*pi for k in range(-3,4) if lo<=t+k*pi<=hi]
        vs=[A*cos(t)+C*sin(t) for t in ts];return min(vs),max(vs)
    for stage in (1,2,3,4,5):
        checks=[];aa=S.pan_pose(stage-1);bb=S.pan_pose(stage)
        if stage==3:
            for (n,s,c) in aa:
                z=bounds(s);ys=(z[1]-100,z[4]-100);zs=(z[2]-882,z[5]-882)
                for angle in range(90):
                    lo,hi=radians(angle),radians(angle+1)
                    yr=[trig_extrema(y,-zz,lo,hi) for y in ys for zz in zs]
                    zr=[trig_extrema(zz,y,lo,hi) for y in ys for zz in zs]
                    env=[z[0],100+min(v[0] for v in yr),882+min(v[0] for v in zr),
                         z[3],100+max(v[1] for v in yr),882+max(v[1] for v in zr)]
                    checks.append(check_sweep(n+f'_ROTATION_{angle}_{angle+1}',env,fixed_with_tote))
        else:
            for qa,qb in zip(aa,bb):
                obs=fixed_with_tote
                if stage==1:
                    # The panunderside and nine shimtops are the same analytic
                    # slope at t0; positive verticaltranslation only separates.
                    obs=[q for q in obs if not q[0].startswith('PAN_FRAME_SHIM_PACK_')]
                checks.append(check_sweep(qa[0]+'_LINEAR',mergebox(bounds(qa[1]),bounds(qb[1])),obs))
        pan_checks.append({'stage':stage,'continuous_subenclosures':len(checks),
           'exact_pairs':sum(q['exact_pairs'] for q in checks),
           'bounds_mm':[min(q['bounds_mm'][i] for q in checks) for i in range(3)]+[max(q['bounds_mm'][i] for q in checks) for i in range(3,6)],
           'positive_intersections':[v for q in checks for v in q['positive_intersections']],
           'passed':all(q['passed'] for q in checks),
           'initial_shim_contact_proof':stage==1})
    parked=S.pan_pose(5);supports=S.temporary_pan_supports()
    support_contacts=clashes(parked,supports)
    fixed_after=fixed+parked+supports+coil
    tb=union_bounds(tote);forward=[v for v in tb];forward[1]-=44.;forward[4]-=44.
    lifted=forward.copy();lifted[2]+=820.;lifted[5]+=820.
    tote_checks=[check_sweep('EMPTY_TOTE_FORWARD44',mergebox(tb,forward),fixed_after),
       check_sweep('EMPTY_TOTE_VERTICAL_HANDOFF820',mergebox(forward,lifted),fixed_after)]
    uniontool=check_sweep('DISCONNECT_UNION_TOOL_ACCESS',[50,185,790,125,320,875],
       [q for q in bed+frame+acc if not q[0].startswith(('WATER_','RECEIVER_HATCH_','DRAIN_SMOOTH_'))])
    all_self={}
    for hot in (False,True):
        pp=B.bed_parts(hot);r=clashes(pp,pp,True)
        r['invalid_ids']=[n for n,s,c in pp if not s.isValid() or s.Volume()<=0]
        r['passed']=not r['positive_intersections'] and not r['invalid_ids'];all_self['PLASMA' if hot else'WOOD']=r
    result={'revision':P.REVISION,'release':False,'prices_included':False,'source_sha256':hashes,
      'positive_volume_threshold_mm3':.05,'missing_accessories':missing+missing2,
      'routine_hatch':{'continuous_external':hatch_external,'open_self':open_self,
       'hinge_exact_checkpoints':hinge_checks,
       'continuous_hinge_geometry_proof':[
         'Fixed/movingindexears have disjointXintervals with0.6mm axialgap; their bores align at90deg.',
         'Mainpins r1.95 stayinside rotating/stationaryr2.2 coaxial bores at allangles.',
         'Fixedleaf has rotationalclearance for movingbarrel and full ear trajectory; cover has cylindricalclearance for fixedbarrel.',
         'Cover bottomneverbelow394; carrierangles end394. Knuckleminimum394 and neckminimum394.95.',
         'Forfirst0.2deg,flange radialshift<.016mm versus.1mm counterboreclearance; thereafter frontlatchpoints riseabove .8mm rivnutflanges.'
       ],'full_open_Z_max_mm':max(bounds(q[1])[5] for q in openparts),'continuous_sweep_Z_max_mm':env[5],'shield_Z_min_mm':700.,'nominal_vertical_gap_mm':700.-max(bounds(q[1])[5] for q in openparts),
       'latches_and_index_pins_removed_before_swing':True,'positive_open_lock':'Two4mm indexpins reinsertedat90deg.',
       'brush_reach':{'opening_mm':list(B.HATCH_OPENING),'handle_length_mm':450.,'head_mm':[60,60,60],
          'maximum_entry_reach_mm':maxreach,'convex_full_floor_reach':maxreach<450,'corner_collision_checks':brush}},
      'rare_pan_tote_replacement':{'pan_continuous_checks':pan_checks,'pan_support_intersections':support_contacts,
         'empty_tote_checks':tote_checks,'union_access':uniontool,
         'pan_moving_steel_mass_kg':sum(s.Volume()*1e-9*7850 for _,s,_ in S.pan_moving()),
         'pan_max_handling_height_mm':max(r['bounds_mm'][5] for r in pan_checks),
         'parked_pan_bounds_mm':union_bounds(parked),
         'steps':['Drainpan,letcool,removebothcomplete toolmodules and parkcommonZ at fullretract.',
           'Remove slats;combs remainwelded. Removeheatshields/clips,Alledgers,TWOfrontledgerarms;removeALLbolt-onATCsubassemblies:rail/drive/lockcarrier AND independentlymountedhood/supports,aftertoolsout/airbled/electricaldisconnected. Undo theirseparateframebolts;doNOTremoveHGRrails/blocks.',
           'Uncouple valve/returnhose at wetstubunion,releasehoseclips,coilR150under cabinet. Undo2overflowM4nuts and slideassembly17mmrightoffstuds before lifting/storing.',
           'Remove4keeperbolts/caps/shoulders. Twopeople controlpan throughout lift70,shift70forward,rotateupright,shift200rearward andloweronto20mmdunnage.',
           'Clamp two minimum500N adjustable safetyprops to parkedpanrim and verifylatching/restraint before handlersrelease.',
           'Move EMPTY closedreceiver44mmforward toY656..1126;liftthroughvacatedbay to820mm baseheight for handoff. Reverseforreplacement.',
           'Handoff then carryingouttheemptytote is rare disassemblyservice, not the zero-outside-space cassette-swap operation.'
         ],'removed_parts_not_assumed_owned':['2minimum500Nclamp-headsafetyprops','2dunnage75x70x20','union/cliptools'],
         'physical_holds':['Confirm actual empty masses,handles,operatorreach and two-personpanhandling; noownedhoist is assumed.',
          'Verify≥1.92m free overhead handlingheight and rated restraint/tool compatibility;CADnonintersection is not an ergonomicrating.',
          'Prove temporaryprop headclamp/slip resistance and fullfloorcontact before releasinghumancontrol.',
          'Receivedtote geometry/rimbearing,usablecapacityandthermal/liquidcompatibility mustmeet stated interfaceenvelopes.']},
      'mode_self':all_self}
    result['source_consistent_during_check']=all(hashlib.sha256((HERE/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
    result['passed']=not result['missing_accessories'] and result['source_consistent_during_check'] and hatch_external['passed'] and not open_self['positive_intersections'] and all(not r['positive_intersections'] for r in hinge_checks+brush) and maxreach<450 and all(r['passed'] for r in pan_checks+tote_checks+[uniontool]) and not support_contacts['positive_intersections'] and all(r['passed'] for r in all_self.values())
    (OUT/'service-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':result['passed'],'source_consistent':result['source_consistent_during_check'],
      'missing':result['missing_accessories'],'hatch_clear':hatch_external['passed'],
      'hatch_open_max_Z_mm':result['routine_hatch']['full_open_Z_max_mm'],
      'pan_stages_clear':[q['passed'] for q in pan_checks],
      'tote_stages_clear':[q['passed'] for q in tote_checks],
      'union_clear':uniontool['passed'],'brush_max_reach_mm':maxreach,
      'self_positives':{k:len(v['positive_intersections']) for k,v in all_self.items()}},indent=2),flush=True)
    return 0 if result['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
