"""Generate/check the selected-slide carrier, guarded park and manual cover path."""
from pathlib import Path
from itertools import combinations,product
import csv,hashlib,json,math,os,sys
import actual_atc as A
cq=A.cq;HERE=A.HERE;ROOT=A.ROOT;OUT=HERE/'output'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def asbox(b):return A.box(*b[:3],*(b[k+3]-b[k]for k in range(3)))
def overlap(a,b):return all(min(a[k+3],b[k+3])-max(a[k],b[k])>1e-6 for k in range(3))
def joined(a,b):return[min(a[k],b[k])for k in range(3)]+[max(a[k+3],b[k+3])for k in range(3)]

def family_metadata(meta):
    """Tier-independent installation references do not assert Basic contents."""
    meta=dict(meta);meta['manufacturing_specs']={n:dict(r)for n,r in meta['manufacturing_specs'].items()}
    for n,r in meta['manufacturing_specs'].items():
        if not n.startswith('ATC_VENDOR_RAPIDCHANGE_4_HOUSING_'):continue
        r.update(ownership='new-kit-family-geometry-reference',
            stock='Datedmanufacturerfourpocket60mmfamilyinstallationgeometryreference;notaseparatepurchase',
            notes='OriginalunscaledmanufacturerSTEP;FAQsharesER11/16/20externalgeometryexceptsockets. EndcaphousingsmaynotbesuppliedwithBasic. Actualtier/boxcontents,IR/internalnutplanes/receivedrevisionremainheld. Thisgeometryreferenceisnonadditive,newquantity0;onechosenkitiscountedseparately.')
    meta['kit_contents_selected_and_verified']=False
    meta['installation_geometry_is_exact_basic_kit_contents']=False
    return meta

def static(parts):
    hits=[];tests=0
    invalid=[n for n,s,c in parts if not s.isValid()or len(s.Solids())!=1]
    for (n,s,c),(m,t,d)in combinations(parts,2):
        if not overlap(A.bounds(s),A.bounds(t)):continue
        tests+=1;v=abs(s.intersect(t).Volume())
        if v>.02:hits.append(dict(a=n,b=m,volume_mm3=v))
    return dict(exact_pairs=tests,unexpected=hits,invalid=invalid,passed=not hits and not invalid)

def boxes_against(enclosures,obstacles):
    tests=0;pairs=0;hits=[]
    obs=[(n,s,A.bounds(s))for n,s,c in obstacles]
    for n,b in enclosures:
        for m,t,bt in obs:
            pairs+=1
            if not overlap(b,bt):continue
            tests+=1;v=abs(asbox(b).intersect(t).Volume())
            if v>.02:hits.append(dict(enclosure=n,obstacle=m,volume_mm3=v))
    return dict(enclosure_count=len(enclosures),candidate_pairs=pairs,exact_pairs=tests,unexpected=hits,passed=not hits)

def rotation_bounds(b,a0,a1):
    out=[float('inf')]*3+[float('-inf')]*3;cx,cz=575.,A.HOOD_ROTATE_CENTRE_Z
    aa,bb=math.radians(a0),math.radians(a1)
    def extrema(v,w):
        ts=[aa,bb];t=math.atan2(w,v)
        for k in range(-3,4):
            q=t+k*math.pi
            if aa<=q<=bb:ts.append(q)
        return[min(v*math.cos(t)+w*math.sin(t)for t in ts),max(v*math.cos(t)+w*math.sin(t)for t in ts)]
    for x,z in product((b[0],b[3]),(b[2],b[5])):
        lo,hi=extrema(x-cx,z-cz);out[0]=min(out[0],cx+lo);out[3]=max(out[3],cx+hi)
        lo,hi=extrema(z-cz,-(x-cx));out[2]=min(out[2],cz+lo);out[5]=max(out[5],cz+hi)
    out[1],out[4]=b[1],b[4]
    return out

def cover_cells():
    cells=[];proof={}
    for n,s,c in A._hood_native(released=True):
        b=A.bounds(s);cuts=None;axis=None
        if n=='ATC_COVER_FRONT':cuts=[275,342,809,875];axis=0
        elif n=='ATC_COVER_REAR_WITH_ARM_RELIEFS':cuts=[275,466,496,654,684,875];axis=0
        elif n=='ATC_COVER_SIDE_L':cuts=[b[1],1310,1321,b[4]];axis=1
        elif n=='ATC_COVER_SIDE_R':cuts=[b[1],1321,b[4]];axis=1
        elif n.startswith('ATC_COVER_FOLDED_HANDLE_'):cuts=[b[1],b[1]+6,b[4]-6,b[4]];axis=1
        pieces=[]
        if cuts:
            for i,(v,w)in enumerate(zip(cuts,cuts[1:])):
                clip=b.copy();clip[axis]=v;clip[axis+3]=w
                q=s.intersect(asbox(clip))
                if q.Volume()>.0001:pieces.append((n+'__'+str(i),A.bounds(q)))
        else:pieces=[(n,b)]
        union=cq.Compound.makeCompound([asbox(q)for _,q in pieces])
        missing=abs(s.cut(union).Volume());proof[n]=dict(missing_material_outside_cells_mm3=missing,passed=missing<.001)
        cells+=pieces
    assert all(q['passed']for q in proof.values())
    return cells,proof

def transform_cell(b,stage,t):
    s=asbox(b)
    s=s.translate((0,0,500*(t if stage==0 else 1)))
    if stage>=1:s=s.rotate((575,A.BODY_Y+233,A.HOOD_ROTATE_CENTRE_Z),(575,A.BODY_Y+234,A.HOOD_ROTATE_CENTRE_Z),90*(t if stage==1 else 1))
    if stage>=2:s=s.translate((-390*(t if stage==2 else 1),70*(t if stage==2 else 1),0))
    if stage>=3:s=s.translate((0,0,-A.HOOD_LOWER_DISTANCE*(t if stage==3 else 1)))
    if stage>=4:s=s.translate((90*t,0,0))
    return A.bounds(s)

def hood_path_proof(obstacles):
    removed=[n for n,_,_ in obstacles if n.startswith('ATC_COVER_KEEPER_')]
    obstacles=[q for q in obstacles if q[0]not in removed]
    cells,containment=cover_cells();enclosures=[];release_tests=[]
    # Exact axial Minkowski solids for the two circular thumbscrews. A
    # square bounding box would falsely cover material outside the M4 tap.
    for side,xc in(('L',264.),('R',886.)):
        swept=A.cyl(4,14,(xc,1288.,1041.55)).fuse(A.cyl(7,12,(xc,1288.,1047.55))).clean()
        rows=[]
        for n,s,c in obstacles:
            if overlap(A.bounds(swept),A.bounds(s)):
                v=abs(swept.intersect(s).Volume())
                if v>.02:rows.append(dict(obstacle=n,volume_mm3=v))
        release_tests.append(dict(side=side,unexpected=rows,passed=not rows))
    for stage in range(5):
        for n,b in cells:
            if stage==1:
                lifted=[*b[:2],b[2]+500,*b[3:5],b[5]+500]
                for angle in range(0,90,5):enclosures.append((f'rotate_{n}_{angle}',rotation_bounds(lifted,angle,angle+5)))
            else:enclosures.append((f'stage{stage}_{n}',joined(transform_cell(b,stage,0),transform_cell(b,stage,1))))
    result=boxes_against(enclosures,obstacles)
    result.update(source_cell_containment=containment,axial_clamp_release=release_tests,
        manually_removed_and_refitted_parts=removed+['ATC_COVER_REMOVABLE_M4x6_L','ATC_COVER_REMOVABLE_M4x6_R'],
        removed_fastener_stow_scope='Removedkeepers/twoshortM4bolts heldinownedtoolstorage; nofullrouteinsideanunmodeledstorageboxclaimed',
        paths=['Remove both retainedstorageLkeepers intoownedtoolstorage','Remove twoM4x6hoodtabbolts with8mmverticalrelease; keepinownedtoolstorage','Lift cover500mm','Rotate90deg aboutY','Shift390mmleft/70mmrear',f'Lower{A.HOOD_LOWER_DISTANCE}mm','Insert90mmright ontohooks,then refitbothLkeepers/Rclips'],
        whole_path_bounds_mm=[min(b[k]for _,b in enclosures)for k in range(3)]+[max(b[k+3]for _,b in enclosures)for k in range(3)])
    result['in_plan_footprint']=result['whole_path_bounds_mm'][0]>=-50 and result['whole_path_bounds_mm'][3]<=1200 and result['whole_path_bounds_mm'][1]>=0 and result['whole_path_bounds_mm'][4]<=1600
    result['passed']=result['passed']and all(q['passed']for q in release_tests)and result['in_plan_footprint']
    return result

def save_assembly(parts,path):
    asm=cq.Assembly(name=path.stem)
    for n,s,c in parts:A.add_assembly_part(asm,n,s,c)
    asm.save(str(path))
    back=cq.importers.importStep(str(path)).val()
    expected=sum(s.Volume()for _,s,_ in parts)
    return dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),components=len(parts),
        valid=back.isValid()and len(back.Solids())==len(parts)and abs(back.Volume()-expected)<max(.1,expected*1e-7),
        solids=len(back.Solids()),volume_error_mm3=abs(back.Volume()-expected),bounds_mm=A.bounds(back))

def run():
    OUT.mkdir(exist_ok=True);(OUT/'custom-step').mkdir(exist_ok=True)
    sources=[Path(__file__),Path(A.__file__),Path(A.source_frame.__file__),A.BASE/'params.py',*sorted((HERE/'sources').glob('*'))]
    hashes=lambda:{p.relative_to(ROOT).as_posix():sha(p)for p in sources}
    start=hashes();checks={};parts={}
    for label,t,h in [('WOOD_DEPLOYED',0.,'stored'),('PLASMA_PARKED',200.,'fitted'),('TRANSIT',100.,'stored')]:
        q=A.actual_atc_parts(t,pins_withdrawn=label=='TRANSIT',hood=h)
        parts[label]=q;checks[label]=static(q)
        print(label,'static',checks[label]['passed'],checks[label]['unexpected'],flush=True)
    moving=A.actual_atc_parts(0,pins_withdrawn=True,hood='stored');meta=A.atc_metadata(0,True,'stored')
    rack=[q for q in moving if meta['classified_parts'][q[0]]=='carrier']+A.acceptance_parts(0)
    fixed=[q for q in moving if meta['classified_parts'][q[0]]!='carrier']
    envelopes=[];material_cover={}
    for n,s,c in rack:
        b=A.bounds(s);cells=[(n,b)]
        if n.startswith('ATC_CROSSCARRIER_END_PLATE_'):
            cells=[];cut_z=A.CARRIER_BOTTOM
            split_x=290 if n.endswith('_L')else 860
            for label,lo,hi,xlo,xhi in(('lower_left',b[2],cut_z,b[0],split_x),
                    ('lower_right',b[2],cut_z,split_x,b[3]),('upper',cut_z,b[5],b[0],b[3])):
                clip=b.copy();clip[2]=lo;clip[5]=hi;clip[0]=xlo;clip[3]=xhi
                q=s.intersect(asbox(clip))
                if q.Volume()>.0001:cells.append((n+'__'+label,A.bounds(q)))
            cover_union=cq.Compound.makeCompound([asbox(bb)for _,bb in cells])
            missing=abs(s.cut(cover_union).Volume())
            material_cover[n]=dict(missing_material_mm3=missing,passed=missing<.001,cells=[bb for _,bb in cells])
        for label,b in cells:
            end=b.copy();end[1]+=200;end[4]+=200;envelopes.append((label,joined(b,end)))
    travel=boxes_against(envelopes,fixed)
    travel['source_material_cover']=material_cover
    travel['passed']=travel['passed']and all(q['passed']for q in material_cover.values())
    print('ATC200travel',travel['passed'],travel['unexpected'],flush=True)
    parked=A.actual_atc_parts(200,hood='removed')+A.acceptance_parts(200)
    cover=hood_path_proof(parked)
    print('hood path',cover['passed'],cover['unexpected'],cover['axial_clamp_release'],flush=True)
    # The existing bed study's exact continuous bound is an input contract;
    # root must revalidate it when combining this factory with the real bed.
    allpark=A.actual_atc_parts(200,hood='fitted')+A.acceptance_parts(200)
    bedmax=1182.8457;bedgap=min(A.bounds(s)[1]-bedmax for n,s,c in allpark)
    exports={}
    for label in('WOOD_DEPLOYED','PLASMA_PARKED'):
        tool_capacity=[q for q in A.acceptance_parts(0 if label=='WOOD_DEPLOYED' else 200)if q[0].startswith('ATC_RETAINED_ER11_')]
        exports[label]=save_assembly(parts[label]+tool_capacity,OUT/(label+'.step'))
    specs=family_metadata(A.atc_metadata(200,False,'fitted'))['manufacturing_specs'];custom=[]
    for n,s,c in parts['PLASMA_PARKED']:
        if specs[n]['ownership']!='new':continue
        if n.startswith(('ATC_ARM_M6','ATC_VENDOR_M6','ATC_CENTRE_M6','ATC_END_M6','ATC_ENDPOINT_SHOULDER','ATC_PIN_','ATC_COVER_M4','ATC_COVER_REMOVABLE_M4','ATC_COVER_KEEPER')):continue
        b=A.bounds(s);local=s.translate(tuple(-v for v in b[:3]));path=OUT/'custom-step'/(n+'.step')
        cq.exporters.export(local,str(path));back=cq.importers.importStep(str(path)).val()
        custom.append(dict(id=n,step=path.relative_to(HERE).as_posix(),sha256=sha(path),source_world_min_corner_mm=b[:3],
            valid=back.isValid()and len(back.Solids())==1 and abs(back.Volume()-local.Volume())<.05,
            local_bounds_mm=A.bounds(local),stock=specs[n]['stock'],notes=specs[n]['notes']))
    rows=[]
    for n,s,c in parts['PLASMA_PARKED']:
        q=specs[n]
        rows.append(dict(id=n,quantity=1,unit='part',ownership=q['ownership'],section_or_finished_stock=q['stock'],notes=q['notes']))
    # Unmodeled internalTnuts/vendor-side screws remain explicit requirements,
    # not magically free hardware or invented attachment solids.
    for n,qty,spec,notes in[
        ('ATC_END_M8x20',8,'M8x20socket +M8washer1.6','Endcore nominal6.8 tappedM8; actual engagement12.05 with6.35plate+1.6washer; noM6inoversizecore'),
        ('ATC_HEADER_AND_DOCK_M6x16',16,'M6x16socket+washer+compatibleTnut','8header/drop and8dock/base; nominal8.05projection after6.35+1.6grip'),
        ('ATC_CARRIER_M6_TNUT',10,'M6Tnut for actual4080die','4end+2centre+4directreararm; externalgrip bolts modeled; source die/cavity/engagement held'),
        ('ATC_BASE_M4x12',4,'M4x12 +compatibleN-M4channelnut','Supplier underside nut contour/depth unverified; custom baseplate hole axes ±10 are drawing-derived'),
        ('ATC_OEM_CARRIAGE_M6_SET',4,'M6 fixing set, length/depthunreleased','Source4-M6 count established; axes/lengthmustcome from actualcarriage'),
        ('ATC_COVER_HANGER_M6x16',2,'M6x16socket+washer+compatibleTnut','Two source-defined custom6.6holes atX352/372,Z932.8 into crossbearer rear slot'),
        ('ATC_COVER_KEEPER_RCLIP',2,'Matched4mmkeeperpinretainer','Retain the two captiveLkeepers'),
        ('RAPIDCHANGE_4_ER11_KIT',1,'RapidChange4pocketER11kit;Basicbudgetcase','Unowned. Original60mmfamilyinstallationhousing/endcaps,pocketXY/mountaxesrecovered. BasicexcludesIR/dustcover;datedfamilyendcapsarenotassertedasBasicboxcontents. InternalER11/nutengagement,cables,receivedrevision/tierremainheld. Fourfamilygeometryreferencesarenonpurchases;onechosenkitcountedhere.'),
        ('ATC_ENDPOINT_CAPTURE_STATE_SENSING',1,'Controllercompatibleendpoint/bothcaptureseat/interlockset','No removablepins. Confirmendpoint,bothseats,energizedaxis andspindlestop; sensorordercodes/mounts/IOisolationheld'),
        ('ATC_TOOLSETTER_AND_IR_INTERFACE',1,'Requiredtoolsetterandunpricedtool/nutstate-detectioninterfacehold','Basic400hasnoIR. BindqualifiedProIRorexternaldetectionandcontrollerIObeforeunattendedautomaticoperation;actualsensor/ordercountsremainheld. Do notcountthisasasecondkitorassumeownedtoolsetter. Theknown50toolsetterpriceisnotapriceforthiswholeinterface.')]:
        rows.append(dict(id=n,quantity=qty,unit='set'if' set'in spec.lower()or n.endswith('SET')else'part',ownership='new-or-verify-owned'if'INTERFACE'in n else'new',section_or_finished_stock=spec,notes=notes))
    with(OUT/'atc-takeoff.csv').open('w',newline='',encoding='utf-8')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (OUT/'custom-part-index.json').write_text(json.dumps(custom,indent=2)+'\n',encoding='utf-8')
    I=134000.;L=520.;E=69000.;load=100.;armL=A.BEAM_CENTRE-(A.BODY_Y+30);armI=28*25.4**3/12
    armdef=(load/2)*armL**3/(3*E*armI);beamdef=load*L**3/(48*E*I)
    hoodmass=sum(s.Volume()*7.85e-6 for n,s,c in A._hood_native())
    torque=20.;lever=50.;sideforce=torque*1000/lever
    guideI=20*6.35**3/12;guideH=12.55
    report=dict(study='SELECTED311_SLIDE_PASSIVE_CAPTURE_AND_MANUFACTURER_HOUSING_INTEGRATION',source_sha256=start,
        metadata=family_metadata(A.atc_metadata()),static_checks=checks,continuous200_translation=travel,
        full_cover_changeover=cover,
        bed_tilt_contract=dict(continuous_bed_max_Y_mm=bedmax,minimum_ATC_parked_Y_gap_mm=bedgap,all_ATC_fixed_and_parked_material_behind_bed=bedgap>=5,
            scope='Uses current integratedbed1182.8457 input; rootassembly must bind/check actualbedfactory.'),
        ideal_stiffness_screen=dict(force_N=load,crossbeam_support_span_mm=L,profile_I_weak_min_mm4=I,
            profile_only_bending_mm=beamdef,each_loaded_arm_tip_mm=armdef,scalar_sum_mm=beamdef+armdef,
            arm_cantilever_mm=armL,qualified=False,excluded='Actualprofilemodifiedholes, pad/endcap/socket, joints,seats,screw/rail/module, thermal and dynamic compliance'),
        passive_capture_fit=dict(no_removable_endpoint_bolts=True,nominal_vertical_gap_mm=.15,
            left_nominal_total_X_clearance_mm=.15,finished_gap_acceptance_mm=[.10,.20],right_outer_float_mm=1.2,
            finish_after_welding=True,full_translation_and_material_containment_checked=travel['passed'],
            powered_axial_hold_required=True,selected_axis_axial_force_verified=False,powerloss_axial_lock=False),
        conditional_guide_wall_screen=dict(torque_case_Nm=torque,effective_yaw_contact_lever_mm=lever,
            contact_force_N=sideforce,assumed_loaded_wall_width_mm=20,wall_thickness_mm=6.35,wall_height_mm=guideH,
            E_MPa=200000.,wall_only_elastic_deflection_mm=sideforce*guideH**3/(3*200000*guideI),
            nominal_wall_bending_stress_MPa=6*sideforce*guideH/(20*6.35**2),qualified=False,
            excludes='Impacttransients/contact/welds/slip, actualmaterials/finish and poweredaxialhold. A chosen20Nm case is not measured vendorreactiondata.'),
        manufacturer_housing=dict(file='sources/'+A.VENDOR_HOUSING_SOURCE.name,sha256=sha(A.VENDOR_HOUSING_SOURCE),
            unscaled_original_solids=4,source_XYZ_mm=[271.2,60,80.8],world_pocket_X_mm=list(A.POCKET_X),
            world_pocket_Y_mm=A.BODY_Y+30,world_body_bottom_Z_mm=A.MAG_BASE,
            mounting_X_mm=list(A.MOUNT_X),mounting_Y_mm=[A.BODY_Y+10,A.BODY_Y+50],
            through_mm=6.35,counterbore_mm=11,counterbore_depth_mm=7,
            source_geometry_recovered=True,actual_received_revision_verified=False,
            internal_ER11_socket_nut_IR_datums_in_source=False,
            exact_Basic_kit_contents_asserted=False,
            export_method='Original local definitions with explicit assemblylocations; no bakedtranslationofmanufacturertrimcurves'),
        new_joint_dimensions=dict(body_M6x55_engagement_mm=10.8,body_tip_reserve_mm=1.9,
            body_head_recess_mm=1.,front_pad_M6x30_engagement_mm=10.7,front_pad_tip_reserve_mm=2.,
            rear_arm_M6x30_internal_projection_mm=10.7,rear_actual_Tnut_fit_verified=False,
            cover_M4x6_engagement_mm=4.1,cover_tip_reserve_mm=2.25),
        cover_finished_reference_mass_kg=hoodmass,
        exported_assemblies=exports,custom_parts=custom,
        output_sha256={'output/atc-takeoff.csv':sha(OUT/'atc-takeoff.csv'),'output/custom-part-index.json':sha(OUT/'custom-part-index.json')},
        actual_vendor_interfaces_completed=False,physical_slide_carriage_height_measured=False,
        actual_RapidChange_variant_height_verified=False,conservative_family_height_allocation_mm=120,actual_head_boot_registration_verified=False,
        final_automatic_M6_sequence_generated=False,complete_delivered_budget_verified=False,
        scope='Nominalmechanicalcarrier,passivecapture/coverandunscaledmanufacturerhousingintegration. Recoveredexternalmount/pocketaxesareactualsourcegeometry;internalER11socket/nut/IR/receivedrevisionandselectedslide4-M6sourcefitremainheld. Noenergizedtest/firmware/configuration/fullmachinerelease.',
        fabrication_release=False,operating_release=False)
    report['source_consistent_during_build']=start==hashes()
    report['passed']=report['source_consistent_during_build']and all(q['passed']for q in checks.values())and travel['passed']and cover['passed']and bedgap>=5 and all(q['valid']for q in exports.values())and all(q['valid']for q in custom)
    (OUT/'atc-integration-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],static=[q['passed']for q in checks.values()],travel=travel['passed'],cover=cover['passed'],bedgap=bedgap,covermass=hoodmass,customparts=len(custom),armbeamdefl=beamdef+armdef)),flush=True)
    return 0 if report['passed']else 2

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
