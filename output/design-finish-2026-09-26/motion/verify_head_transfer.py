"""Continuous, inventory-preserving split-head route through the internal front gap.

This is manual handling without a torch, supply lead or tether fitted. Small
fastener unscrewing/access is excluded; their resulting tray poses are modeled.
"""
from pathlib import Path
import hashlib, importlib.util, json, math, sys
import cadquery as cq
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(OUT))
from cad_helpers import bbox,validate,intersection_volume
import motion_finish as mf
import build_revg as bg
import bed_cassettes as bc
from check_transfer_staging import build_staging_model

def run(builder='build_revi'):
    import verify_motion_finish as vm
    started=vm.source_hashes();identity=vm.proof_identity()
    checkfiles=[Path(__file__),OUT/'check_transfer_staging.py']
    bindings={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in checkfiles}
    mod=__import__(builder);router,_=mod.build_model();stored=mod.stored_model(router)
    target,_=mf.plasma_hardware_model(stored)
    model=build_staging_model(router)
    head,meta=mf.make_head();released,_=mf.make_head(breakaway_offset=8)
    headids=[p.id for p in head.parts]
    byid={p.id:p for p in model.parts};fixed={p.id:p.shape for p in model.parts}
    solver=vm.continuous();records=[];footprints=[];states=[];current={};support_checks=[]
    support=cq.Compound.makeCompound([p.shape for p in model.parts if bc._PLACEMENTS.get(p.id,('',-1))[:2]==('panel',0)])
    support_bounds=bbox(support);table_y=support_bounds[1];table_z=support_bounds[5]
    stage_screen=(430,table_y+184.4,table_z-12)
    stage_front=(320,table_y+104.4,table_z+110.85)
    stage_insert=(310,table_y+214.4,table_z+80.35)
    stage_rear=(180,table_y+123.9,table_z+80.35)
    def support_check(label):
        group=compound();patch=group.translate((0,0,-.01)).intersect(support)
        points=sorted(set((round(v.Center().x,6),round(v.Center().y,6)) for v in patch.Vertices()))
        def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
        lower=[];upper=[]
        for p in points:
            while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
            lower.append(p)
        for p in reversed(points):
            while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
            upper.append(p)
        hull=lower[:-1]+upper[:-1]
        total=0;weighted=[0.,0.,0.]
        for ident,s in current.items():
            material=byid[ident].material.lower()
            density=1400 if any(t in material for t in ('polymer','acetal','insulating')) else 1700 if 'switch' in material else 2700 if any(t in material for t in ('aluminium','aluminum','6061')) else 7850
            mass=s.Volume()*density/1e9;center=s.Center();total+=mass
            for k,v in enumerate((center.x,center.y,center.z)):weighted[k]+=mass*v
        center=[v/total for v in weighted]
        margins=[cross(a,hull[(i+1)%len(hull)],center)/math.dist(a,hull[(i+1)%len(hull)]) for i,a in enumerate(hull)] if len(hull)>=3 else [-1]
        rec={'group':label,'contact_area_screen_mm2':patch.Volume()/.01,'support_hull_xy_mm':hull,'mass_screen_kg':total,'center_of_mass_xyz_mm':center,'minimum_gravity_projection_margin_mm':min(margins),'passed':patch.Volume()>.01 and min(margins)>1}
        support_checks.append(rec);print('SUPPORT',label,rec['passed'],round(min(margins),3),flush=True)
    def state(label):
        for ident,shape in fixed.items():byid[ident].shape=shape
        r=validate(model);states.append({'name':label,'parts':r['part_count'],'clashes':r['unresolved_intersections']})
        print('STATE',label,len(r['unresolved_intersections']),flush=True)
        if r['unresolved_intersections']:print(json.dumps(r['unresolved_intersections']),flush=True)
    # Socket heads rest flat down on the actual hardware-tray floor. These are
    # explicit intermediate locations, not parts silently removed from inventory.
    small=['I_HEAD_CLAMP_PINCH_15','I_HEAD_CLAMP_PINCH_95','I_HEAD_SPLASH_5','I_HEAD_SPLASH_105']
    for ident,x in zip(small,(885,903,921,939)):
        part=head.find(ident);s=part.local.rotate((0,0,0),(1,0,0),180)
        bb=bbox(s);fixed[ident]=s.translate((x,787,436.144-bb[2]))
    for i in (1,2):fixed['I_PARK_BOLT_'+str(i)]=target.find('I_PARK_BOLT_'+str(i)).shape
    state('staging_with_removed_fasteners_in_tray')

    def take(ids):
        nonlocal current
        current={ident:fixed.pop(ident) for ident in ids}
    def compound():return cq.Compound.makeCompound(list(current.values()))
    def apply(label,shape_at,part_at,speed,curve=0,exclude=()):
        r=solver(shape_at,{i:s for i,s in fixed.items() if i not in exclude},speed,curve)
        rec={'name':label,**r}
        if exclude:rec['analytic_contact_exclusions']=list(exclude)
        records.append(rec)
        # Every translation has exact endpoint bounds. Rotation additionally
        # gets a rigorous circular projected bound in the turn() wrapper.
        for ident,s in list(current.items()):current[ident]=part_at(s,1)
        print(label,r['status'],r['failures'][:4],flush=True)
    def shift(label,d,exclude=()):
        s=compound();b0=bbox(s);f=lambda t:s.translate(tuple(v*t for v in d))
        b1=bbox(f(1));xy=[min(b0[0],b1[0]),min(b0[1],b1[1]),max(b0[3],b1[3]),max(b0[4],b1[4])]
        footprints.append({'name':label,'xy_swept_bounds_mm':xy,'passed':xy[0]>=-1e-6 and xy[1]>=-1e-6 and xy[2]<=1150+1e-6 and xy[3]<=1450+1e-6})
        apply(label,f,lambda p,t:p.translate(tuple(v*t for v in d)),math.dist((0,0,0),d),exclude=exclude)
    def turn(label,pivot,degrees):
        s=compound();bb=bbox(s);r=max(math.hypot(y-pivot[1],z-pivot[2]) for y in (bb[1],bb[4]) for z in (bb[2],bb[5]))
        axis=(pivot[0]+1,pivot[1],pivot[2]);f=lambda t:s.rotate(pivot,axis,degrees*t)
        # Exact extrema for all corners' Y projections over this angular arc.
        vals=[];a,b=sorted((0,math.radians(degrees)))
        for y in (bb[1]-pivot[1],bb[4]-pivot[1]):
            for z in (bb[2]-pivot[2],bb[5]-pivot[2]):
                angles=[a,b];base=math.atan2(-z,y)
                angles += [base+k*math.pi for k in range(-4,5) if a<=base+k*math.pi<=b]
                vals += [pivot[1]+y*math.cos(t)-z*math.sin(t) for t in angles]
        xy=[bb[0],min(vals),bb[3],max(vals)]
        footprints.append({'name':label,'xy_swept_bounds_mm':xy,'passed':xy[0]>=-1e-6 and xy[1]>=-1e-6 and xy[2]<=1150+1e-6 and xy[3]<=1450+1e-6})
        apply(label,f,lambda p,t:p.rotate(pivot,axis,degrees*t),r*abs(math.radians(degrees)),r*math.radians(degrees)**2)
    def park(label):
        fixed.update(current);current.clear();state(label)
    def route_to_board(label,ids,lift,front_y,stage_origin,stage_angle=0):
        take(ids);origin=list(mf.PARK)
        shift(label+'_lift',(0,0,lift),exclude=('I_HEAD_CLAMP_REAR',) if label=='rear_insert' else ());origin[2]+=lift
        shift(label+'_rear_lane',(0,500-origin[1],0));origin[1]=500
        shift(label+'_right_lane',(865-origin[0],0,0));origin[0]=865
        shift(label+'_front_lane',(0,front_y-origin[1],0));origin[1]=front_y
        if label!='screen':turn(label+'_stand',origin,90)
        shift(label+'_raise',(0,0,1170-origin[2]));origin[2]=1170
        shift(label+'_over_board',(stage_origin[0]-origin[0],stage_origin[1]-origin[1],0));origin[:2]=stage_origin[:2]
        angle=stage_angle-(0 if label=='screen' else 90)
        if angle:turn(label+'_lay_on_board',origin,angle)
        shift(label+'_lower_to_board',(0,0,stage_origin[2]-origin[2]))
        support_check(label);park(label+'_staged')

    front=['I_HEAD_CLAMP_FRONT','I_HEAD_INSERT_FRONT']
    rearinsert=['I_HEAD_INSERT_REAR']
    screen=['I_HEAD_SPLASH_SCREEN','I_HEAD_SPLASH_TAB_5','I_HEAD_SPLASH_TAB_105']
    rear=[x for x in meta['detachable_ids'] if x not in small+front+rearinsert+screen]
    base=[x for x in headids if x not in meta['detachable_ids']]
    # First unload the cap and loose insert. Manually retain the insert while
    # carrying; its semicircular register contains it when cap lies face down.
    route_to_board('screen',screen,10,40,stage_screen,90)
    route_to_board('front_cap',front,20,163,stage_front,180)
    route_to_board('rear_insert',rearinsert,35,133,stage_insert,180)
    # Opening the three kinematic contacts is proven by the separate mechanism
    # report; switch plungers extend as release moves away. They are not fixed
    # obstacles with impossible uncompressed lengths during this initial move.
    take(rear)
    pin_ids=[x for x in base if x.startswith('I_HEAD_PRESENCE_') and x.endswith('_PIN')]
    contact_ids=['I_HEAD_SEAT_CONE','I_HEAD_SEAT_V','I_HEAD_SEAT_FLAT','I_HEAD_FLOAT_CAM']+pin_ids
    shift('rear_release_initial_8',(0,0,8),exclude=contact_ids)
    for ident in pin_ids:fixed[ident]=released.find(ident).shape.translate(mf.PARK)
    fixed.update(current);current.clear()
    # It is now8mm off the original location; route helper assumes PARK, so
    # undo that bookkeeping by explicit parameters while keeping real shapes.
    take(rear);origin=[550,745,450.096]
    for name,d in [('rear_lift',(0,0,42)),('rear_rear_lane',(0,-245,0)),('rear_right_lane',(315,0,0)),('rear_front_lane',(0,-367,0))]:
        shift(name,d);origin=[a+b for a,b in zip(origin,d)]
    turn('rear_stand',origin,90);shift('rear_raise',(0,0,1170-origin[2]));origin[2]=1170
    shift('rear_over_board',(stage_rear[0]-origin[0],stage_rear[1]-origin[1],0));origin[:2]=stage_rear[:2]
    turn('rear_lay_on_board',origin,90)
    rear_z=stage_rear[2]
    shift('rear_lower_to_board',(0,0,rear_z-1170));support_check('rear');park('rear_staged_clamp_face_down')
    # Finally the thin guide/backplate assembly fits the54.2mm inner front gap.
    take(base);origin=[550,745,442.096]
    for name,d in [('base_lift',(0,0,50)),('base_rear_lane',(0,-245,0)),('base_right_lane',(315,0,0)),('base_front_lane',(0,-397,0))]:
        shift(name,d);origin=[a+b for a,b in zip(origin,d)]
    turn('base_stand',origin,90)
    ab=bbox(stored.find('TOOL_ADAPTER_110').shape);work=ab[:3]
    shift('base_raise',(0,0,work[2]-origin[2]));origin[2]=work[2]
    shift('base_align_x',(work[0]-origin[0],0,0));origin[0]=work[0]
    shift('base_approach_adapter',(0,work[1]-origin[1],0));park('base_at_adapter_before_four_mount_screws')
    for i in range(1,5):fixed['I_TOOL_MOUNT_'+str(i)]=target.find('I_TOOL_MOUNT_'+str(i)).shape
    # Mount screws' nominal thread engagements are permitted by target model.
    model.allowed_intersections.update(target.allowed_intersections)
    state('base_fixed_with_four_mount_screws')

    stages=[('rear',rear,stage_rear,180),('screen',screen,stage_screen,90),('rear_insert',rearinsert,stage_insert,180),('front_cap',front,stage_front,180)]
    for label,ids,at,angle in stages:
        take(ids);origin=list(at)
        shift(label+'_retrieve_up',(0,0,1300-origin[2]));origin[2]=1300
        if angle!=90:turn(label+'_orient_for_install',origin,90-angle)
        # Approach at100mm in front of the working plane before lowering to
        # the exact assembly height; then close on the custom head interface.
        shift(label+'_align_work_x',(work[0]-origin[0],0,0));origin[0]=work[0]
        shift(label+'_align_work_y',(0,work[1]-100-origin[1],0));origin[1]=work[1]-100
        shift(label+'_lower_for_install',(0,0,work[2]-origin[2]));origin[2]=work[2]
        if label=='rear':
            shift('rear_approach_to_release8',(0,92,0))
            # Closed seat/pin contact proof is reversible normal release.
            shift('rear_close_kinematic_coupling',(0,8,0),exclude=contact_ids)
            for ident in pin_ids:fixed[ident]=target.find(ident).shape
        else:shift(label+'_close_to_installed',(0,100,0),exclude=('I_HEAD_CLAMP_REAR',) if label=='rear_insert' else ())
        park(label+'_installed')
    for ident in small:fixed[ident]=target.find(ident).shape
    state('all_head_parts_installed_before_staging_restored')
    final_errors=[]
    for ident in headids+small+['I_TOOL_MOUNT_'+str(i) for i in range(1,5)]+['I_PARK_BOLT_1','I_PARK_BOLT_2']:
        actual=fixed[ident];expected=target.find(ident).shape
        overlap=intersection_volume(actual,expected)
        delta=max(abs(actual.Volume()-overlap),abs(expected.Volume()-overlap))
        final_errors.append({'part':ident,'boolean_difference_mm3':delta,'passed':delta<.001})
    result={'source_sha256':{**started,**bindings},'source_unchanged':started==vm.source_hashes() and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in bindings.items()),
      'builder':builder,'states':states,'head_transfer_segments':records,'footprint_checks':footprints,'final_part_checks':final_errors,'staging_support_checks':support_checks,
      'preparation_dependency':'check_transfer_staging.py: panel1 remains available and is relocated onto installed crossbeams as an internal table, then beam1 enters front/lower slot. All six spoilboards remain stored. Restoration is separately checked with the installed head retained as obstacle.',
      'staging_panel_bounds_mm':support_bounds,
      'staging_support':'Actual panel1 restrained by existing clamp sets. Rear assembly and front cap rest on broad machined clamp faces. Insert lies split-face-down; screen rests flat with tabs upward. Contact patches are intersected with actual extrusion geometry using0.01mm downward screening penetration; mass-weighted gravity projections must be inside the support hull by>1mm. This is a static placement screen, not a shock/friction/capacity qualification.',
      'small_hardware_scope':'Unscrewing, hand/finger access and individual small-fastener transfer are excluded. Four removed head screws have explicit head-down tray poses; two parking screws move to their final tray positions. All ten are restored/accounted in final geometry.',
      'actual_tool_scope':'No torch, supply lead or tether is installed. Routing of those items requires measured interfaces and disconnected transfer. These rigid manual paths do not qualify a powered/automatic swap or human lift capacity.',
      'contact_scope':'Three monotonic kinematic seats, the cam and morphing presence plungers use separate mechanism exact contact/swept-box proofs during the two8mm normal release/reseat segments. The rear half-insert withdraws normally through the open semicircular rear clamp: every point remaining inside rear-clamp W<=80.35 moves toward circle centerW80.6, so its squared radial coordinate decreases until it leaves the body. Thus it cannot enter the rear-clamp solid; reverse insertion is the same path. All other obstacles remain in rigid proofs.'}
    result['passed']=result['source_unchanged'] and not any(s['clashes'] for s in states) and all(r['status']=='CLEAR' for r in records) and all(r['passed'] for r in footprints+final_errors+support_checks)
    vm.finish_identity(result,identity)
    (OUT/'integrated-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('INTEGRATED',result['passed'],flush=True)
    return result
