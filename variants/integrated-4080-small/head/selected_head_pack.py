"""Selected shared-router/plasma dock takeoff and nonoverlapping owned-stock nest."""
from pathlib import Path
import csv,json,os,sys,math
import cadquery as cq
import ezdxf
import quick_dock as Q
import plasma_quick_dock as P
import owner_head as H

HERE=H.HERE;OUT=HERE/'output/selected-head-pack'

def coupled_rib_section():
    """Ideal homogeneous gross section; bolt slip/torsion remain unqualified."""
    rectangles=[dict(w=146.,d=12.7,x=0.,y=19.05),
        dict(w=Q.RIB_THICKNESS,d=Q.RIB_DEPTH,x=Q.RIB_X+Q.RIB_THICKNESS/2,y=Q.HEAD_FRONT_Y+Q.RIB_DEPTH/2)]
    area=sum(r['w']*r['d']for r in rectangles)
    cx=sum(r['w']*r['d']*r['x']for r in rectangles)/area
    cy=sum(r['w']*r['d']*r['y']for r in rectangles)/area
    ixx=sum(r['w']*r['d']**3/12+r['w']*r['d']*(r['y']-cy)**2 for r in rectangles)
    iyy=sum(r['d']*r['w']**3/12+r['w']*r['d']*(r['x']-cx)**2 for r in rectangles)
    ixy=sum(r['w']*r['d']*(r['x']-cx)*(r['y']-cy)for r in rectangles)
    effective=ixx-ixy**2/iyy
    return dict(area_mm2=area,centroid_XY_mm=[cx,cy],Ixx_mm4=ixx,Iyy_mm4=iyy,Ixy_mm4=ixy,
        effective_I_for_My_zero_mm4=effective,formula='Ieffective=Ixx-Ixy^2/Iyy; includes unsymmetric bending coupling',
        gross_ratio_to_flat_plate=effective/(146*12.7**3/12),full_composite_action_or_torsion_qualified=False)

def rib_connection_screen(section):
    a=Q.RIB_THICKNESS*Q.RIB_DEPTH;cx,cy=section['centroid_XY_mm']
    q=a*(Q.HEAD_FRONT_Y+Q.RIB_DEPTH/2-cy)-section['Ixy_mm4']/section['Iyy_mm4']*a*(Q.RIB_X+Q.RIB_THICKNESS/2-cx)
    flow=100*q/section['effective_I_for_My_zero_mm4'];n=flow*262
    thread_area=math.pi*3.545*.5*16.4
    return dict(force_N=100,tool_lever_from_support_mm=262,
        unsymmetric_first_moment_Qeffective_mm3=q,longitudinal_shear_flow_N_per_mm=flow,
        maximum_rib_axial_resultant_N=n,worst_single_locator_or_bolt_transfer_N=n,
        friction_only_screen=dict(assumed_friction_coefficient=.1,bolt_count=3,
            required_preload_per_bolt_N=n/(3*.1),example_preload_per_bolt_N=3000,
            nominal_three_bolt_friction_N=900,preload_or_friction_qualified=False),
        M4_thread_screen=dict(nominal_engagement_mm=16.4,pitch_diameter_mm=3.545,
            assumed_effective_shear_area_mm2=thread_area,
            required_allowable_internal_thread_shear_MPa_at3000N=3000/thread_area,
            formula='Ashear=0.5*pi*dp*Le is a simplified nominal thread-strip screen; actual flank geometry, alloy and preload require qualification'),
        positive_dowel_screen=dict(quantity=2,diameter_mm=4,length_mm=20,rib_embed_mm=7.3,
            head_embed_mm=12.7,centres_local_Z_mm=list(Q.RIB_PIN_Z),centre_spacing_mm=60,
            required_allowable_pin_shear_MPa_single_pin=n/(math.pi*4**2/4),
            required_allowable_rib_bearing_MPa_single_pin=n/(4*7.3),
            required_allowable_head_bearing_MPa_single_pin=n/(4*12.7),
            nominal_fit_requirement='Matchedlightpressinhead;measured0..0.005mmdiametralclearanceinrib;rearflush;verifyreceivedgrade,engagementandload-slip.',
            physical_fit_or_capacity_qualified=False),
        qualification='Positive dowels avoid relying solely on unmeasured friction. Fully composite action, joint microslip and <=0.02mm loaded compliance are not proved by nominal bore/pin cylinders. Load test the assembled head; this is not a machine-rigidity release.')

def net_section_rib_screen():
    """Hole-aware unsymmetric Euler beam screen over the actual90mm span.

    Cylinder intersections at each Z are rectangular in X/Y. Removed bore
    material is not replaced with a fictitiously bonded steel screw/dowel.
    """
    base=[(146.,12.7,0.,19.05,1),(Q.RIB_THICKNESS,Q.RIB_DEPTH,Q.RIB_X+Q.RIB_THICKNESS/2,Q.HEAD_FRONT_Y+Q.RIB_DEPTH/2,1)]
    holes=[]
    for x in(-25,25):
        for z in(-50,-20):holes.append((x,z,2.5,12.7,25.4))
    for x in(-28,28):
        holes.append((x,40,3.3,12.7,25.4))
        for z in(29,51):holes.append((x,z,1.5,17.4,25.4))
    x=Q.RIB_X+Q.RIB_THICKNESS/2
    for z in Q.RIB_FIX_Z:
        holes.extend([(x,z,3.8,12.7,16.8),(x,z,2.25,16.8,25.4),(x,z,2,25.4,45.4)])
    for z in Q.RIB_PIN_Z:holes.extend([(x,z,2,12.7,25.4),(x,z,2,25.4,34.4)])
    def effective(z):
        rr=base+[(2*math.sqrt(r*r-(z-zz)**2),y1-y0,x,(y0+y1)/2,-1)
            for x,zz,r,y0,y1 in holes if abs(z-zz)<r]
        area=sum(w*d*sign for w,d,x,y,sign in rr)
        cx=sum(w*d*sign*x for w,d,x,y,sign in rr)/area;cy=sum(w*d*sign*y for w,d,x,y,sign in rr)/area
        ix=sum(sign*(w*d**3/12+w*d*(y-cy)**2)for w,d,x,y,sign in rr)
        iy=sum(sign*(d*w**3/12+w*d*(x-cx)**2)for w,d,x,y,sign in rr)
        ixy=sum(sign*w*d*(x-cx)*(y-cy)for w,d,x,y,sign in rr)
        return ix-ixy**2/iy
    def integrate(step,F,P):
        n=round(90/step);step=90/n
        vals=[F*((-50+i*step)-(-172-P))**2/(69000*effective(-50+i*step))for i in range(n+1)]
        return step*(sum(vals)-.5*(vals[0]+vals[-1]))
    cases=[dict(force_N=f,tool_projection_mm=p,ideal_fully_composite_displacement_mm=integrate(.05,f,p))for f in(25,50,100)for p in(15,50)]
    fine=integrate(.01,100,50);coarse=cases[-1]['ideal_fully_composite_displacement_mm']
    minimum_I=min(effective(-50+i*.05)for i in range(1801))
    conservative=100/(69000*minimum_I)*(90**3/3+172*90**2+172**2*90)
    return dict(E_MPa=69000,support_local_Z_mm=40,lower_clamp_row_local_Z_mm=-50,
        nominal_lower_tool_reference_local_Z_mm=-172,section_step_mm=.05,
        minimum_effective_net_I_mm4=minimum_I,
        uniform_minimum_section_ideal_bending_100N_P50_mm=conservative,
        remaining_from_0p15_plate_target_mm=.15-conservative,
        integration='Integral F*(z-ztool)^2/(E*Ieffective(z)) dz; unsymmetric hole-aware section at each station',
        cases=cases,refinement_100N_P50_0p01mm=fine,refinement_delta_mm=abs(fine-coarse),
        modeled_removed_bores=holes,
        limitations='Includes nominal clamp/release/cage/rib screw and dowel bores across the90mm span. Still assumes full composite action and ideal continuous fixed support; excludes shear deformation, torsion, bolt slip, nonlinear contact and actual alloy qualification.')

def rib_drill_drawings():
    records=[]
    for name,w,h,centres,notes in[
        ('OWNER_ROUTER_SIDE_RIB_DRILLING',Q.RIB_THICKNESS,Q.RIB_HEIGHT,
            [(Q.RIB_THICKNESS/2,z-Q.RIB_Z0)for z in Q.RIB_FIX_Z],
            ['RIB - QTY1 - 9.525 THICK X,20 DEPTH Y,110 HEIGHT Z; ALL mm',
             'FACE VIEW X/Z FROM REAR; THREE M4x0.7 THROUGH TAPS ALONG Y',
             'DRILL3.3 THEN TAP THROUGH20; HOLE X4.7625; Z10,55,100 FROM BOTTOM',
             'ALSO TWO MATCH-REAMED D4 DOWEL BORES DEPTH9 AT Z25,85; PIN EMBED7.3',
             'OWNER3/8 SHEET RAW20x110 AT276,2; GLOBAL NEST RECONCILIATION REQUIRED']),
        ('OWNER_ROUTER_HEAD_RIB_ADDITIONAL_BORES',146.,175.,
            [(Q.RIB_X+Q.RIB_THICKNESS/2+73,z+65)for z in Q.RIB_FIX_Z],
            ['ADDITIONAL THREE BORES ONLY - EXISTING HEAD FEATURES FOLLOW STEP',
             'REAR FACE VIEW X/Z; LOCAL CORNER X-73,Z-65; ALL mm',
             'HOLES X137.7625; Z15,60,105 FROM BOTTOM; DRILL4.5 THROUGH12.7',
             'REAR COUNTERBORE7.6 x4.1; M4x25 SOCKET HEAD7x4 RECESSED0.1',
             'RIB THREAD ENGAGEMENT16.4; TIP RECESSED3.6; ACTUAL SCREW/TAP FIT VERIFY',
             'TWO MATCHED D4 DOWEL BORES THROUGH AT X137.7625/Z30,90; HEAD LIGHTPRESS FIT'])]:
        doc=ezdxf.new('R2010',units=ezdxf.units.MM);ms=doc.modelspace()
        for layer,color in [('OUTLINE',7),('BORE_CENTRES',1),('NOTES',7)]:doc.layers.new(layer,dxfattribs={'color':color})
        ms.add_lwpolyline([(0,0),(w,0),(w,h),(0,h)],close=True,dxfattribs={'layer':'OUTLINE'})
        for x,z in centres:ms.add_circle((x,z),1.65 if 'SIDE_RIB_DRILLING'in name else 2.25,dxfattribs={'layer':'BORE_CENTRES'})
        for z in Q.RIB_PIN_Z:ms.add_circle((w/2 if 'SIDE_RIB_DRILLING'in name else Q.RIB_X+Q.RIB_THICKNESS/2+73,z-Q.RIB_Z0 if 'SIDE_RIB_DRILLING'in name else z+65),2,dxfattribs={'layer':'BORE_CENTRES'})
        for i,t in enumerate(notes):ms.add_text(t,dxfattribs={'height':2,'layer':'NOTES'}).set_placement((0,h+8+5*(len(notes)-i)))
        path=OUT/(name+'.dxf');doc.saveas(path);back=ezdxf.readfile(path)
        assert not back.audit().errors and back.units==ezdxf.units.MM
        records.append(dict(file=path.relative_to(HERE).as_posix(),sha256=H.sha(path),units='mm',role='ADDITIONAL_RIB_DRILLING',readback_passed=True))
    return records

def run():
    OUT.mkdir(exist_ok=True)
    source=[Path(__file__),Path(Q.__file__),Path(P.__file__),*H.sources(),
        HERE/'output/quick-dock/quick-dock-check.json',HERE/'output/plasma-quick-dock/plasma-dock-check.json']
    hashes=lambda:{str(p.relative_to(H.ROOT)).replace('\\','/'):H.sha(p)for p in source}
    start=hashes()
    q=json.loads(source[-2].read_text(encoding='utf-8'));p=json.loads(source[-1].read_text(encoding='utf-8'))
    assert q['known_dock_static_and_removal_checkpoints_passed']and q['source_consistent_during_check']
    assert p['known_shared_plasma_interface_passed']and p['source_consistent_during_check']
    for proof in(q,p):
        for n,h in proof['source_sha256'].items():assert H.sha(H.ROOT/n)==h,n
    placements=[
        dict(id='OWNER_ROUTER_HEAD_PLATE',raw_plane=[2,2,146,175],sheet_thickness_axis='partY',finished_thickness_mm=12.7),
        dict(id='CD_RECEIVER',raw_plane=[152,2,146,132],sheet_thickness_axis='partY',finished_thickness_mm=12.7),
        dict(id='PLASMA_REMOVABLE_HEAD_PLATE',raw_plane=[2,188,146,110],sheet_thickness_axis='partY',finished_thickness_mm=12.7),
        dict(id='PLASMA_U_SPLICE_PLATE',raw_plane=[152,188,110,114],sheet_thickness_axis='partY',finished_thickness_mm=12.7),
        dict(id='CD_CAPTIVE_CAGE_L',raw_plane=[266,188,20.8,28],sheet_thickness_axis='partX',finished_thickness_mm=12.7),
        dict(id='CD_CAPTIVE_CAGE_R',raw_plane=[266,220,20.8,28],sheet_thickness_axis='partX',finished_thickness_mm=12.7),
        *[dict(id=f'OWNER_CLAMP_SPACER_{i}_{j}',raw_plane=[266+(i-1)*16,252+(j-1)*16,12,12],
            sheet_thickness_axis='partY',finished_thickness_mm=6.,face_down_from_owned12p7=True)for i in(1,2)for j in(1,2)]]
    nest=[]
    for a in placements:
        x,y,w,h=a['raw_plane'];assert x>=2 and y>=2 and x+w<=302.8 and y+h<=302.8,a
        for b in placements:
            if a['id']>=b['id']:continue
            xx,yy,ww,hh=b['raw_plane']
            dx=max(x-(xx+ww),xx-(x+w),0);dy=max(y-(yy+hh),yy-(y+h),0)
            assert dx>=4-1e-7 or dy>=4-1e-7,(a,b,dx,dy)
            nest.append(dict(a=a['id'],b=b['id'],axis_gap_mm=max(dx,dy)))
    local,meta=Q.local_parts();shapes={a['id']:a['shape']for a in local}
    shapes.update({n:s for n,s,c in P.reference_module()})
    outputs={}
    for row in placements:
        n=row['id'];s=shapes[n];b=H.bounds(s);part=OUT/(n+'.step')
        localshape=s.translate(tuple(-v for v in b[:3]));cq.exporters.export(localshape,str(part))
        back=cq.importers.importStep(str(part)).val()
        assert back.isValid()and len(back.Solids())==1 and abs(back.Volume()-s.Volume())<.05,n
        outputs[n]=dict(file=part.relative_to(HERE).as_posix(),sha256=H.sha(part),
            source_min_corner=b[:3],bounding_dimensions_mm=[b[k+3]-b[k]for k in range(3)])
    n='OWNER_ROUTER_SIDE_RIB';s=shapes[n];b=H.bounds(s);part=OUT/(n+'.step')
    cq.exporters.export(s.translate(tuple(-v for v in b[:3])),str(part));back=cq.importers.importStep(str(part)).val()
    assert back.isValid()and len(back.Solids())==1 and abs(back.Volume()-s.Volume())<.05
    outputs[n]=dict(file=part.relative_to(HERE).as_posix(),sha256=H.sha(part),source_min_corner=b[:3],
        bounding_dimensions_mm=[b[k+3]-b[k]for k in range(3)])
    rib_drawings=rib_drill_drawings()
    rows=[
        ('Owned router clamp/boot/actuator/spindle/VFD',1,'OWNED','Existing working owner head; no replacement clamp/actuator',0,'Owner assembly registration and exact spindle nose remain fitting gates'),
        ('Shared receiver',1,'OWNED_HALF_SHEET','146x132x12.7 finished; source-defined upper dock and transfer-fit raised output',0,'Included exact nest; unused50mm tail removed for front-bay bed arc; no duplicate stock credit'),
        ('Router removable plate',1,'OWNED_HALF_SHEET','146x175x12.7 full-thickness billet interface',0,'Included exact nest; source clamp unchanged'),
        ('Router side stiffener',1,'OWNER_3P8_ALLOCATION_REQUIRED','OWNER_ROUTER_SIDE_RIB:9.525x20x110;threeM4x0.7through-taps;raw20x110at276,2',None,'Requires exclusive parent3/8sheet allocation; fits right strip with4mm gap from moving sideplates. No extra half-sheet credit.'),
        ('Router rib M4x25 screws',3,'NEW_UNLESS_VERIFIED_OWNED','M4x25DIN912sockethead7ODx4;16.4nominalribengagement/3.6tipreserve;rear7.6x4.1counterbore',3,'New actual rated screws; composite joint stiffness/preload/received aluminum alloy require qualification'),
        ('Router rib ground dowels',2,'NEW_UNLESS_VERIFIED_OWNED','Groundsteel4x20dowel;rearflush;12.7head/7.3ribembed;matchedlightpresshead/0..0.005mmribclearance',2,'Positive longitudinal shear transfer; actual steel grade, fit, bearing capacity and loaded slip must be verified'),
        ('Plasma removable plate',1,'OWNED_HALF_SHEET','146x110x12.7 common seat and four upper splice bores',0,'Included exact nest'),
        ('Plasma U-splice',1,'OWNED_HALF_SHEET','110x114x12.7; R3 internal bottom corners',0,'Included exact nest;8M6through-taps'),
        ('Captive screw cages',2,'OWNED_HALF_SHEET','20.8x28 footprint;12.7 through-width blank',0,'Included exact nest;retain only released screws, not head load'),
        ('Equal owner clamp spacers',4,'OWNED_HALF_SHEET','10OD5.5ID6long; face from allocated12x12x12.7blanks',0,'Included exact nest; actual parallel/square faces verified on fabrication'),
        ('Positive gravity ledge',1,'OWNER_3P8_ALLOCATION_REQUIRED','30x12.7footprint x9.525thick',None,'Requires parent combined3/8sheet nest; no duplicate credit'),
        ('Shoulder locators',2,'NEW_STEEL_OR_VERIFIED_OWNED','M4x8 threaded anchor and5diameterx8shoulder',2,'Custom locator/tolerance and actual mating fit unqualified'),
        ('Captive release screws M6x25',2,'NEW_UNLESS_VERIFIED_OWNED','10ODx6head;12.3nominalengagement,.4rearreserve;12.8withdraw',2,'Fit model checked; joint strength/preload held'),
        ('Cage fixing screws M3x10',4,'NEW_UNLESS_VERIFIED_OWNED','3mmcagefoot+7mmheadplateengagement',4,'Actual selected screw and tap fit'),
        ('Gravity ledge M4x20 screws',2,'NEW_UNLESS_VERIFIED_OWNED','9.475mm nominal receiver engagement',2,'Source inherited defined hardware'),
        ('Gravity ledge M4 washers',2,'NEW_UNLESS_VERIFIED_OWNED','9OD4.3ID1thick',2,'Count once shared receiver'),
        ('Owner clamp M5x25 screws',4,'NEW_UNLESS_VERIFIED_OWNED','10.998mmheadplatethreadengagement;1.702rearreserve',4,'Standard8.5ODx5head; source counterbore unchanged'),
        ('Owner clamp M5 spreader washers',4,'NEW_UNLESS_VERIFIED_OWNED','10OD5.3ID1thicksteel',4,'Full head bearing; exact partial original seat coverage retained, strength/preload unqualified'),
        ('Plasma splice M6x16 screws',8,'NEW_UNLESS_VERIFIED_OWNED','6.6hostweb+9.4spliceengagement;3.3tipreserve;headsflush.1',8,'Replaces4old upperdrop bolts with8new matched interface bolts; do not add both sets'),
        ('Existing custom plasma drop plate',1,'NOT_PROVEN_OWNED','110x218x12.7; only upper fixing holes revised',1,'NOT included in owned-half nest; purchase raw plate unless actual ownedstock is separately allocated'),
        ('Retained plasma float/breakaway stack',1,'SOURCE_TAKEOFF_NOT_PROVEN_OWNED','107 unchanged modeled components plus actual torch/tether interfaces',None,'Use retained-plasma-source-requirements.csv; this reference is not an additive new assembly price')]
    bom=OUT/'selected-head-requirements.csv'
    with bom.open('w',newline='',encoding='utf-8')as f:
        w=csv.writer(f);w.writerow(['item','quantity','ownership','specification','new_requirement_quantity','qualification']);w.writerows(rows)
    takeoff=H.ROOT/'variants/extrusion-reengineered/motion-fabrication.csv'
    with takeoff.open(encoding='utf-8-sig',newline='')as f:source_rows=list(csv.DictReader(f))
    stack=[r for r in source_rows if r['id'].startswith(('I_HEAD_','XR_DROP_M6x16_LOWER_'))]
    stack_ids={r['id']for r in stack}
    retained_ids=set(p['source_stack_preserved_world_pose'])
    plunger_crosswalk={n:n.removesuffix('_PIN')+'_CASE'for n in sorted(retained_ids-stack_ids)}
    assert len(plunger_crosswalk)==4 and all(n.endswith('_PIN')and case in stack_ids for n,case in plunger_crosswalk.items())
    path=OUT/'retained-plasma-source-requirements.csv'
    with path.open('w',newline='',encoding='utf-8')as f:
        w=csv.DictWriter(f,fieldnames=list(source_rows[0]));w.writeheader();w.writerows(stack)
    flat_I=146*12.7**3/12;section=coupled_rib_section();I=section['effective_I_for_My_zero_mm4'];E=69000.;L=90.
    screen=[dict(force_N=F,loaded_projection_below_nominal_reference_mm=P,
        ideal_tool_displacement_mm=F/(E*I)*(L**3/3+(122+P)*L**2+(122+P)**2*L))
        for F in(25,50,100)for P in(15,50)]
    report=dict(study='SELECTED_ROUTER_PLASMA_SHARED_HEAD_STOCK_AND_TAKEOFF',source_sha256=start,
        ownership_basis='One owner-reported304.8x304.8x12.7sheet allocated exclusively to these10rectangles; actual alloy/thickness/flatness remain verified before machining. Old83-part allocations are superseded for this sheet, not additional free stock.',
        stock_mm=[304.8,304.8,12.7],outer_margin_mm=2,minimum_profile_gap_mm=4,
        machining_basis='Full-sheet contours to finished nominal perimeters with cutter diameter≤4mm and adequate tabs/fixture. No additional per-part saw/facing allowance is included; this is not a saw-cut blank nest.',
        allocation=placements,all_nonoverlap_pair_checks=nest,outputs=outputs,
        quarter_three_eighth_sheet_additional_allocation='Gravityledge30x12.7 at2,250 plus side-rib20x110 at276,2; parent must reconcile both with the two270x120bed sideplates. One actual3/8sheet, no duplicate credits.',
        additional_three_eighth_allocation=[dict(id='OWNER_ROUTER_SIDE_RIB',raw_plane=[276,2,20,110],finished_thickness_mm=9.525)],
        stiffener_drill_drawings=rib_drawings,stiffener_boot_registration_independent_clearance=meta['one_sided_stiffener'],
        stiffener_connection_screen=rib_connection_screen(section),
        stiffener_net_section_screen=net_section_rib_screen(),
        unpriced_requirement_CSV=dict(file=bom.relative_to(HERE).as_posix(),sha256=H.sha(bom)),
        retained_plasma_takeoff=dict(file=path.relative_to(HERE).as_posix(),sha256=H.sha(path),rows=len(stack),source_file=takeoff.relative_to(H.ROOT).as_posix(),source_sha256=H.sha(takeoff)),
        integral_switch_plunger_nonadditive_crosswalk=plunger_crosswalk,
        ideal_head_plate_screen=dict(E_MPa=E,gross_I_mm4=I,unreinforced_gross_I_mm4=flat_I,coupled_section=section,
            assumed_fixed_section='Continuous ideal clamp atM6rowZ1182',
            bottom_source_clamp_mount_Z_mm=1092,nominal_spindle_lower_reference_Z_mm=970,
            cases=screen,formula='F/(E*I)*(L^3/3+a*L^2+a^2*L),L90,a122+toolprojection',
            unreinforced_100N_P50_mm=100/(E*flat_I)*(L**3/3+172*L**2+172**2*L),
            limitations='Ideal fully composite gross rib/plate section and continuous fixed line only. Coupled bending included; bolt slip, asymmetric-section shear-center/torsion, holes, actual preload/alloy, receiver/clamp/rails/spindle and every other joint excluded. The computed improvement is not a physical stiffness guarantee or complete-machine rigidity qualification.'),
        no_owned_material_credit_for_Z_carrier_or_plasma_drop=True,
        source_consistent_during_check=start==hashes(),costs_or_shipping_not_fabricated=True,
        complete_working_boot_registration=False,physical_strength_qualified=False,
        fabrication_release=False,operating_release=False)
    report['stock_nest_and_takeoff_passed']=report['source_consistent_during_check']
    (OUT/'selected-head-pack-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['stock_nest_and_takeoff_passed'],allocated_blanks=len(placements),retained_stack_takeoff_rows=len(stack),outputs=len(outputs))),flush=True)
    return 0

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
