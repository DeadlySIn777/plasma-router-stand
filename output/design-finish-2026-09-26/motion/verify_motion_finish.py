"""Independent Rev I head mechanism, fabrication and handling checks."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, os, sys, time
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCE))
import cadquery as cq
from cad_helpers import bbox, validate, export, plate, cyl, box, intersection_volume
import motion_finish as mf

def source_hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}

def proof_identity():
    solver=ROOT/'output/cad-repair-2026-09-25/check_spoil_transfer.py'
    return {'verifier_file':str(Path(__file__).relative_to(ROOT)).replace('\\','/'),
            'verifier_sha256_before':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'continuous_solver_file':str(solver.relative_to(ROOT)).replace('\\','/'),
            'continuous_solver_sha256_before':hashlib.sha256(solver.read_bytes()).hexdigest()}

def finish_identity(result,before):
    after=proof_identity();result.update(before)
    result['verifier_sha256_after']=after['verifier_sha256_before']
    result['verifier_changed_during_run']=before['verifier_sha256_before']!=after['verifier_sha256_before']
    result['continuous_solver_sha256_after']=after['continuous_solver_sha256_before']
    result['continuous_solver_changed_during_run']=before['continuous_solver_sha256_before']!=after['continuous_solver_sha256_before']
    result['passed']=bool(result['passed'] and not result['verifier_changed_during_run'] and not result['continuous_solver_changed_during_run'])
    result.setdefault('source_sha256',{})[before['continuous_solver_file']]=before['continuous_solver_sha256_before']

def continuous():
    p=ROOT/'output/cad-repair-2026-09-25/check_spoil_transfer.py'
    spec=importlib.util.spec_from_file_location('head_continuous_engine',p)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod.continuous_segment

def flat_checks(model):
    result=[]
    for p in model.parts:
        if not p.flat:continue
        f=p.flat;s=plate(f['outline'],f['thickness_mm'],f['holes'],f['slots'],f['internal'])
        for op in f.get('operations',[]):
            depth=float(op['layer'].rsplit('_',1)[1].replace('p','.'))
            z=0 if 'REAR' in op['layer'] else f['thickness_mm']-depth
            s=s.cut(cyl(op['diameter'],depth).translate((op['x'],op['y'],z))).clean()
        difference=abs(s.Volume()-p.local.Volume())
        overlap=intersection_volume(s,p.local)
        delta=max(abs(s.Volume()-overlap),abs(p.local.Volume()-overlap))
        result.append({'part':p.id,'difference_mm3':difference,'boolean_difference_mm3':delta,'passed':delta<.001})
    return result

def mechanism():
    identity=proof_identity()
    started={k:v for k,v in source_hashes().items() if k in ('motion_finish.py','cad_helpers.py')};records=[]
    head,meta=mf.make_head();solver=continuous()
    for f in (0,.4,1,1.4,1.5,3,6):
        for b in (0,8):
            m,d=mf.make_head(f,b);r=validate(m)
            records.append({'float_mm':f,'separation_mm':b,'part_count':r['part_count'],'clashes':r['unresolved_intersections']})
            print('MECHANISM_STATE',f,b,len(r['unresolved_intersections']),flush=True)
    rod_ids={'I_HEAD_ROD_25','I_HEAD_ROD_85'}
    fixed={p.id:p.shape for p in head.parts if p.id not in meta['moving_ids'] and p.id!='I_HEAD_FLOAT_SWITCH_PIN' and p.id not in rod_ids}
    moving=cq.Compound.makeCompound([p.shape for p in head.parts if p.id in meta['moving_ids']])
    # Exact conservative Minkowski sweep for each stationary straight guide:
    # replacing its small end holes with a full cylinder only adds obstacle.
    # Sweeping it backwards6mm is exactly an8mm cylinder of length124.
    rod_sweep_checks=[]
    for x in (25,85):
        swept=mf.axis_y(cyl(8,124)).translate((x,0,22))
        volume=intersection_volume(moving,swept)
        rod_sweep_checks.append({'rod_x_mm':x,'full_swept_obstacle_intersection_mm3':volume,'passed':volume<.00001})
    float_route=solver(lambda t:moving.translate((0,6*t,0)),fixed,6)
    print('FLOAT_ROUTE',float_route['status'],flush=True)
    moving=cq.Compound.makeCompound([p.shape for p in head.parts if p.id in meta['detachable_ids']])
    seats={'I_HEAD_SEAT_CONE','I_HEAD_SEAT_V','I_HEAD_SEAT_FLAT'}
    fixed={p.id:p.shape for p in head.parts if p.id not in meta['detachable_ids'] and p.id not in seats and p.id!='I_HEAD_FLOAT_CAM' and not (p.id.startswith('I_HEAD_PRESENCE_') and p.id.endswith('_PIN'))}
    # The cam and release-plate corner have an exact sliding plane atY99.5.
    # A generic distance bound cannot certify persistent tangency. Enclose the
    # entire cam in two explicit boxes and sweep those boxes8mm backwards.
    # Testing the initial release group against that conservative swept solid
    # proves every outward-normal pose, without dropping this obstacle.
    cam_boxes=[(0,88,34,7,11.5,4),(0,99.5,34,22,20.5,16)]
    cover=cq.Compound.makeCompound([box(w,h,d).translate((x,y,z)) for x,y,z,w,h,d in cam_boxes])
    swept=cq.Compound.makeCompound([box(w,h,d+8).translate((x,y,z-8)) for x,y,z,w,h,d in cam_boxes])
    cam=head.find('I_HEAD_FLOAT_CAM').shape
    cam_cover_residual=cam.cut(cover).Volume()
    cam_sweep_overlap=intersection_volume(moving,swept)
    cam_proof={'cam_cover_residual_mm3':cam_cover_residual,'conservative_swept_box_intersection_mm3':cam_sweep_overlap,'passed':cam_cover_residual<1e-5 and cam_sweep_overlap<1e-5}
    seat_checks=[]
    for ident in seats:
        seat=head.find(ident).shape
        volume=intersection_volume(moving,seat)
        seat_checks.append({'seat':ident,'initial_intersection_mm3':volume,'passed':volume<.00001,
          'continuous_argument':'Cone and V voids open monotonically in+Z, and flat is a half-space stop. Initial detached assembly has no point below the seat base where its threaded shank could enter. Outward+Z translation cannot enter any of these three seat solids. Tilt is not included.'})
    breakaway_route=solver(lambda t:moving.translate((0,0,8*t)),fixed,8)
    print('RELEASE_ROUTE',breakaway_route['status'],flush=True)
    flats=flat_checks(head)
    input_checks=[]
    for diameter in (20,40):
        mh,md=mf.make_head(torch=mf.TorchMeasurements(diameter,40,.05,'VERIFIER SYNTHETIC BOUNDARY - NOT OWNER MEASUREMENT'))
        vr=validate(mh);input_checks.append({'synthetic_diameter_mm':diameter,'insert_bore_mm':md['torch_bore_mm'],'clashes':vr['unresolved_intersections']})
    reject_count=0
    for record in (mf.TorchMeasurements(19,40,.05,'test'),mf.TorchMeasurements(41,40,.05,'test'),mf.TorchMeasurements(30,39,.05,'test'),mf.TorchMeasurements(30,40,.11,'test'),mf.TorchMeasurements(30,40,.05,'')):
        try:mf.measured_bore(record)
        except ValueError:reject_count+=1
    result={'source_sha256':started,'source_unchanged':all(source_hashes().get(k)==v for k,v in started.items()),'scope':'Nominal rigid geometry only. Actual owner torch, lead, thermal behavior, switch response and force calibration are excluded.',
       'static_mechanism_states':records,'float_continuous':float_route,'guide_exact_sweep_checks':rod_sweep_checks,
       'normal_breakaway_continuous':breakaway_route,'seat_monotonic_release_checks':seat_checks,'cam_exact_sweep_check':cam_proof,
       'switch_analytic_clearance':{'float_cam_contact':'At the lowest edge of the conservative2.2mm pin, cam normal=7.6-min(float,1.5). Pin normal=min(7.2,cam). Gap>=0 through0..6; pin remains>=6.1 versusTTPmax5.1.',
          'presence_contact':'Release plane normal=5.8+separation relative switch datum. Pin=min(7.2,plane), gap>=0 for0..8. Three plungers excluded from rigid sweep only because their prescribed normal length changes.',
          'scope':'No electrical latency, hysteresis timing, tilted release or safety integrity qualification.'},
       'flat_solid_checks':flats,'synthetic_boundary_checks':input_checks,'invalid_inputs_rejected':reject_count}
    result['passed']=result['source_unchanged'] and cam_proof['passed'] and not any(r['clashes'] for r in records+input_checks) and all(r['passed'] for r in flats+rod_sweep_checks+seat_checks) and reject_count==5 and all(r['status']=='CLEAR' for r in (float_route,breakaway_route))
    finish_identity(result,identity)
    (OUT/'mechanism-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('MECHANISM',result['passed'],flush=True)
    if result['passed']:
        export(head,OUT/'head-cad','RevI_FLOAT_BREAKAWAY_HEAD_BLANK',individual=True)
    return result

def integrated(builder='build_revh'):
    identity=proof_identity();started=source_hashes();mod=__import__(builder)
    router,details=mod.build_model()
    if not any(p.id=='I_HEAD_BACKPLATE' for p in router.parts):mf.extend_router_model(router)
    stored=mod.stored_model(router)
    plasma,meta=mf.plasma_hardware_model(stored)
    states={}
    for name,model in [('ROUTER',router),('BED_STORED',stored),('PLASMA_HARDWARE',plasma)]:
        r=validate(model);states[name]={'part_count':r['part_count'],'clashes':r['unresolved_intersections']}
        print(name,r['part_count'],len(r['unresolved_intersections']),flush=True)
        if r['unresolved_intersections']:print(json.dumps(r['unresolved_intersections']),flush=True)
    solver=continuous()
    ids=[p.id for p in stored.parts if p.id.startswith(mf.PREFIX) and not p.id.startswith('I_HEAD_PARK_')]
    head=cq.Compound.makeCompound([stored.find(x).shape for x in ids])
    fixed={p.id:p.shape for p in stored.parts if p.id not in ids}
    # Both parking screws have already been removed and stored upright in the
    # existing hardware tray. Their unscrewing/access is outside rigid head path.
    for i in (1,2):fixed['I_PARK_BOLT_'+str(i)]=plasma.find('I_PARK_BOLT_'+str(i)).shape
    records=[];current=head
    def shift(label,delta):
        nonlocal current
        f=lambda t:current.translate(tuple(v*t for v in delta))
        r=solver(f,fixed,math.sqrt(sum(v*v for v in delta)))
        records.append({'name':label,'translation_mm':delta,**r})
        current=current.translate(delta)
        print(label,r['status'],r['failures'][:3],flush=True)
    shift('lift_clear_of_parking_feet',(0,0,50))
    shift('under_pan_to_cabinet_rear',(0,-245,0))
    shift('cross_to_right_of_cabinet',(280,0,0))
    shift('move_to_front_turn_bay',(0,-335,0))
    pivot=(830,165,492.096)
    before=current
    radius=max(math.hypot(y-pivot[1],z-pivot[2]) for x in bbox(before)[::3] for y in (bbox(before)[1],bbox(before)[4]) for z in (bbox(before)[2],bbox(before)[5]))
    rotation=lambda t:before.rotate(pivot,(pivot[0]+1,pivot[1],pivot[2]),90*t)
    r=solver(rotation,fixed,radius*math.pi/2,radius*(math.pi/2)**2)
    records.append({'name':'stand_head_in_front_bay','rotation_degrees':90,**r});current=rotation(1)
    print('stand_head_in_front_bay',r['status'],r['failures'][:3],flush=True)
    adapter=stored.find('TOOL_ADAPTER_110');bb=bbox(adapter.shape)
    shift('raise_head_above_front',(0,0,bb[2]-492.096))
    shift('align_head_transverse',(bb[0]-830,0,0))
    shift('approach_adapter_from_front',(0,bb[1]-165,0))
    expected=cq.Compound.makeCompound([plasma.find(x).shape for x in ids])
    final_error=max(abs(a-b) for a,b in zip(bbox(current),bbox(expected)))
    result={'source_sha256':started,'source_unchanged':started==source_hashes(),'builder':builder,'states':states,'head_transfer_segments':records,'final_bounds_error_mm':final_error,
        'scope':'Rigid complete head in nominal bed-stored layout. Parking bolts pre-removed; torch absent, supply lead disconnected. Human access/grip/weight and rear adapter-fastener access require physical acceptance.',
        'footprint':'Prescribed XY positions and turn stay withinX0..1150/Y0..1450. Head rotation occurs in front bay; no cart or external floor area is used.'}
    result['passed']=result['source_unchanged'] and not any(s['clashes'] for s in states.values()) and all(r['status']=='CLEAR' for r in records) and final_error<1e-5
    finish_identity(result,identity)
    (OUT/'integrated-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('INTEGRATED',result['passed'],flush=True)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--integrated',action='store_true');parser.add_argument('--builder',default='build_revh')
    args=parser.parse_args()
    try:
        if args.integrated:
            from verify_head_transfer import run
            r=run(args.builder)
        else:r=mechanism()
        code=0 if r['passed'] else 2
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
