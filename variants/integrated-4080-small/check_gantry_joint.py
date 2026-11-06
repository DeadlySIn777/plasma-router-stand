"""Export/check the fitted steel gantry face and four end closure bridges."""
from pathlib import Path
from itertools import combinations
import csv,hashlib,json,math,os,sys
import cadquery as cq
import ezdxf
import gantry_joint as G
import assembly as E

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=HERE/'output/gantry-joint'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writecsv(path,rows):
    with path.open('w',encoding='utf-8',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def draw_dxf(path,outline,circles,text,lines=()):
    """Canonical millimetre DXF, with separate machining/reference layers."""
    doc=ezdxf.new('R2010');doc.units=4;space=doc.modelspace()
    def layer(name):
        if name not in doc.layers:doc.layers.new(name)
        return dict(layer=name)
    def line(p,q,name):space.add_line(p,q,dxfattribs=layer(name))
    for p,q in zip(outline,outline[1:]+outline[:1]):line(p,q,'FINISHED_OUTLINE')
    for x,z,d,name in circles:space.add_circle((x,z),d/2,dxfattribs=layer(name))
    for p,q,name in lines:line(p,q,name)
    for j,t in enumerate(text):space.add_text(t,dxfattribs=dict(height=3.,**layer('NOTES'))).set_placement((0,-8-6*j))
    doc.saveas(path)

def write_drawings(d):
    x0,z0=d['x0'],d['lower_z'];cir=[]
    for x,z in d['retained_M8_axes']:
        cir +=[(x-x0,z-z0,8.5,'M8_CLEARANCE_THROUGH'),(x-x0,z-z0,13.5,'COUNTERBORE_D13p5_DEPTH8')]
    for x,z in d['retained_M6_axes']:cir.append((x-x0,z-z0,5.,'M6_PILOT_D5_TAP_M6x1_THROUGH'))
    for x,z in d['coupler_access_axes']:cir.append((x-x0,z-z0,12.5,'COUPLER_HEAD_ACCESS_THROUGH'))
    draw_dxf(OUT/'GJ_FACE_FRONT.dxf',[(0,0),(1200,0),(1200,112),(0,112)],cir,
        ['FRONT DATUM VIEW X/Z; MILLIMETRES; NOMINAL6.35 STEEL PLUS ATTACHED REAR LANDS',
         '8x M8: D8.5 THROUGH AND D13.5 COUNTERBORE8 FROM FRONT AFTER WELDING',
         '4x M6: D5 PILOT/TAP M6x1 THROUGH; RETAINED SOURCE AXES',
         '10x D12.5 COUPLER ACCESS; END AXES MAKE HALF-ROUND EDGE NOTCHES',
         'HGR20 M5 RAIL PATTERN: TRANSFER ACTUAL OWNED RAILS; DO NOT GUESS PITCH/PHASE',
         'FINISH DATUM FLATNESS0.05 AND REAR LAND COPLANARITY0.05; INSPECT ACTUAL WELDMENT'],
        [((0,20),(1200,20),'RAIL_AXIS_REFERENCE_ONLY'),((0,80),(1200,80),'RAIL_AXIS_REFERENCE_ONLY')])
    draw_dxf(OUT/'GJ_TOP_BRIDGE.dxf',[(0,0),(32,0),(32,80),(0,80)],
        [(16,20,6.6,'THROUGH_D6p6'),(16,60,6.6,'THROUGH_D6p6')],
        ['4x STEEL32x80x6.35; RAW34x82 FROM ALLOCATED NEW HANGER OFFCUTS',
         'M6x20 WITH1.6 WASHER:7.95 EXTERNAL GRIP AND12.05 INTERNAL PROJECTION',
         'ACTUAL T-NUT/CAVITY FIT AND PRELOAD REQUIRE VERIFICATION'])
    draw_dxf(OUT/'GJ_M8_REAR_LAND.dxf',[(0,0),(25,0),(25,25),(0,25)],
        [(12.5,12.5,8.5,'THROUGH_D8p5'),(12.5,12.5,13.5,'RECESS_PART_OF_ASSEMBLED_8mm_COUNTERBORE')],
        ['8x STEEL25x25x6.35 NOMINAL; RAW27x27 FROM ALLOCATED NEW OFFCUTS',
         'ATTACH TO FACE BEFORE FINAL MACHINING; TOTAL DATUM STACK12.7',
         'COUNTERBORE8 FROM ASSEMBLED FRONT LEAVES4.7 BEARING WEB'])
    draw_dxf(OUT/'GJ_M6_UPPER_LAND.dxf',[(0,0),(30,0),(30,20),(0,20)],
        [(10,10,5.,'M6_PILOT_D5_TAP_M6x1'),(20,10,5.,'M6_PILOT_D5_TAP_M6x1')],
        ['2x STEEL30x20x6.35 NOMINAL; RAW32x22 FROM ALLOCATED NEW OFFCUTS',
         'ATTACH BEFORE DRILL/TAP; FULL SOURCE M6 EDGE SEAT; TOTAL STACK12.7'])
    rows=[]
    for typ,axes,dia,operation in(('M8',d['retained_M8_axes'],8.5,'D8.5through;D13.5counterbore8fromfront'),
             ('M6',d['retained_M6_axes'],5.,'D5pilotthrough;tapM6x1through'),
             ('COUPLER',d['coupler_access_axes'],12.5,'D12.5throughaccess;edgeaxesintentionalhalfround')):
        for j,(x,z)in enumerate(axes,1):rows.append(dict(id=f'{typ}_{j}',local_X_mm=x-x0,local_Z_mm=z-z0,
            world_X_mm=x,world_Z_at_reference_mm=z,nominal_drill_mm=dia,operation=operation,datum='Facefrontlowerleft;worldreferenceGY775'))
    writecsv(OUT/'GJ_FACE_DRILL_SCHEDULE.csv',rows)

def write_nest_drawing(nest):
    doc=ezdxf.new('R2010');doc.units=4;m=doc.modelspace()
    for name in('MINIMUM_PARENT_REFERENCE_ONLY','RAW_BLANK_BOUNDARY','LABELS'):
        doc.layers.new(name)
    def rect(x,y,w,h,layer):m.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],close=True,dxfattribs=dict(layer=layer))
    for side,offset in(('L',0),('R',200)):
        rect(offset,0,160,325.85,'MINIMUM_PARENT_REFERENCE_ONLY')
        m.add_text(side+' NEW HANGER SIDE-BAND ALLOCATION',dxfattribs=dict(height=4,layer='LABELS')).set_placement((offset,333))
    for r in nest['placements']:
        x=r['u']+(200 if r['hanger']=='R'else 0);y=r['v']
        rect(x,y,r['w'],r['h'],'RAW_BLANK_BOUNDARY')
        if 'TOP_BRIDGE'in r['id']:name='C'+r['id'].rsplit('_',1)[1]
        elif 'STOP_DATUM'in r['id']:name='D'+r['id'].rsplit('_',1)[1]
        elif 'M8_REAR_LAND'in r['id']:name='B'+r['id'].rsplit('_',1)[1]
        else:name='U'+r['id'].rsplit('_',1)[1]
        m.add_text(name,dxfattribs=dict(height=3,layer='LABELS')).set_placement((x+2,y+3))
    for j,text in enumerate(['MILLIMETRES. LAYOUT ONLY: DO NOT CUT MINIMUM PARENT OUTLINE.',
        'ACTUAL HANGER STEP CONTROLS THE FINAL351.85mm OR OTHER CURRENT HEIGHT.',
        'D1-D4 EXISTING RAW22x22 DATUMS; C1-C4 RAW34x82 TOP BRIDGES.',
        'B1-B8 RAW27x27 M8 LANDS; U1-U2 RAW32x22 UPPER M6 LANDS.',
        'CUT RAW BLANKS BEFORE HANGER OUTLINE. 4mm SEPARATION;1mm NEW-BLANK EDGE CLEANUP.',
        'PARENT STEEL IS AN ALREADY-COUNTED NEW PURCHASE, NOT OWNED OR FREE STOCK.']):
        m.add_text(text,dxfattribs=dict(height=3,layer='LABELS')).set_placement((0,-10-6*j))
    doc.saveas(OUT/'GJ_HANGER_OFFCUT_LAYOUT.dxf')

def run():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'custom-step').mkdir(exist_ok=True)
    sources=list(dict.fromkeys([Path(__file__),Path(G.__file__),Path(E.__file__),Path(E.M.__file__),
        Path(E.M.X.__file__),Path(E.M.X.P.__file__),Path(E.Q.__file__),Path(E.P.__file__),Path(E.Q.D.__file__),*E.H.sources()]))
    hashes=lambda:{p.relative_to(ROOT).as_posix():sha(p)for p in sources};start=hashes()
    G.ENABLED=False
    try:reference=E.integrated_motion(False,775.,575.,125.,spindle_context=False)
    finally:G.ENABLED=True
    d=G.source_datums(reference);parts=G.apply_joint(reference)
    fresh=[p for p in parts if p[0].startswith(G.PREFIX)]
    retained=[p for p in parts if not p[0].startswith(G.PREFIX)]
    invalid=[n for n,s,c in fresh if not s.isValid()or len(s.Solids())!=1]
    hits=[]
    for (n,s,c),(m,t,cc)in combinations(fresh,2):
        if E.S.overlap(G.bounds(s),G.bounds(t)):
            v=abs(s.intersect(t).Volume())
            if v>.02:hits.append(dict(a=n,b=m,volume_mm3=v))
    relative=[]
    for n,s,c in fresh:
        for nf,sf,cf in retained:
            cls=E.motion_class(nf)
            span=[400 if cls in('Y_X_head','Y_X_Z_tool')else 0,500 if cls=='stationary'else 0,125 if cls=='Y_X_Z_tool'else 0]
            b=G.bounds(s);swept=[b[k]-span[k]for k in range(3)]+[b[k+3]+span[k]for k in range(3)]
            if not E.S.overlap(swept,G.bounds(sf)):continue
            if any(span):q=E.S.translation_cover_proof(s,sf,[-v for v in span],span,max_depth=18)
            else:
                v=abs(s.intersect(sf).Volume());q=dict(passed=v<.02,overlap_mm3=v,method='Exactstatic;contacttangencyallowed')
            relative.append(dict(part=n,obstacle=nf,**q))
            if not q['passed']:print('HOLD',n,nf,flush=True)
    nest=G.nest_offcuts(E.M.frame_parts())
    custom=[]
    for n,s,c in fresh:
        if n!=G.FACE_ID and not n.startswith(G.PREFIX+'TOP_BRIDGE_'):continue
        b=G.bounds(s);local=s.translate(tuple(-v for v in b[:3]));path=OUT/'custom-step'/(n+'.step')
        cq.exporters.export(local,str(path));back=cq.importers.importStep(str(path)).val()
        error=abs(back.Volume()-local.Volume());bb=G.bounds(back);expected=[0,0,0]+[b[k+3]-b[k]for k in range(3)]
        ok=back.isValid()and len(back.Solids())==1 and error<.05 and max(abs(x-y)for x,y in zip(bb,expected))<1e-5
        custom.append(dict(id=n,step=path.relative_to(HERE).as_posix(),sha256=sha(path),valid=ok,
            source_world_min_corner_mm=b[:3],finished_dimensions_mm=expected[3:],roundtrip_volume_error_mm3=error,
            raw_stock='Newlong6.35nominalsteelfaceplusattachedoffcutlands'if n==G.FACE_ID else'Raw34x82x6.35allocatednewhanger-sidebandblank',
            fabrication_release=False))
    (OUT/'custom-part-index.json').write_text(json.dumps(custom,indent=2)+'\n',encoding='utf-8')
    rows=[dict(id='GJ_NEW_LONG_FACE_STOCK',quantity=1,unit='blank',role='DISTINCT_REQUIREMENT',
        ownership='new',material='plainsteel',spec='Finished1200x112x6.35nominalface;minimumraw1202x114plusactualthickness/flatnessallowance',
        notes='REPLACESbothnew1200x40x12.7Albars. Newlongstockpurchase,shippingunquoted. Fitnominalplate/landthicknessesandinspectfinished12.7datumstack;donotcountoldAlbarstockagain.'),
        dict(id='GJ_OFFCUT_TOP_BRIDGES',quantity=4,unit='part',role='NONADDITIVE_REFERENCE',ownership='already-counted-new-hanger-stock',material='plainsteel6.35',spec='Finished32x80;raw34x82',notes='Allocatedoncefromleftnewhangerblanksidebands;nofreestock/ownedcredit;newdrilling/finishworkandhardwarestillrequired.'),
        dict(id='GJ_OFFCUT_M8_REAR_LANDS',quantity=8,unit='part',role='NONADDITIVE_REFERENCE',ownership='already-counted-new-hanger-stock',material='plainsteel6.35',spec='Finished25x25;raw27x27',notes='Allocatedoncefromrightnewhangerblankleftsideband;attachtofacebeforefinalcounterbores. Notadditionalrawpurchase.'),
        dict(id='GJ_OFFCUT_M6_UPPER_LANDS',quantity=2,unit='part',role='NONADDITIVE_REFERENCE',ownership='already-counted-new-hanger-stock',material='plainsteel6.35',spec='Finished30x20;raw32x22',notes='Allocatedoncefromrightnewhangerblankrightsideband;supportsfullretainedM6holes. Notadditionalrawpurchase.'),
        dict(id='GJ_TOP_M6x20',quantity=8,unit='each',role='DISTINCT_REQUIREMENT',ownership='new',material='steel',spec='M6x20socketcap;10ODx6head',notes='7.95externalgrip;12.05internalslotprojection;actualnut/cavitydepth>=13.05andnominal5.9engagementverifiedbeforeassembly.'),
        dict(id='GJ_TOP_M6_WASHER',quantity=8,unit='each',role='DISTINCT_REQUIREMENT',ownership='new',material='steel',spec='M6washer12ODx6.6IDx1.6',notes='Oneperclosurebolt;includedin7.95externalgrip.'),
        dict(id='GJ_TOP_M6_TNUT',quantity=8,unit='each',role='INTERFACE_HOLD',ownership='new',material='steel',spec='M6Tnutmatchedtoactual4080slot;nominal5.9mmengagementand>=13.05cavity',notes='Actualsupplierdie/lip/nut/boltprojectionmustmatch;notassumedincludedwithownedmotionorfreehardware.')]
    writecsv(OUT/'gantry-joint-takeoff.csv',rows);write_drawings(d);write_nest_drawing(nest)
    drawing_checks=[]
    for path in sorted(OUT.glob('*.dxf')):
        doc=ezdxf.readfile(path);audit=doc.audit()
        drawing_checks.append(dict(file=path.relative_to(HERE).as_posix(),units_mm=doc.units==4,
            entities=len(doc.modelspace()),audit_errors=len(audit.errors),audit_repairs=len(audit.fixes),
            circles=len(doc.modelspace().query('CIRCLE')),
            passed=doc.units==4 and not audit.errors and not audit.fixes))
    (OUT/'hanger-offcut-nest.json').write_text(json.dumps(nest,indent=2)+'\n',encoding='utf-8')
    old_mass=sum(s.Volume()*2.70e-6 for n,s,c in reference if n in G.REMOVED_IDS)
    new_mass=sum(s.Volume()*7.85e-6 for n,s,c in fresh if n==G.FACE_ID or n.startswith(G.PREFIX+'TOP_BRIDGE_'))
    torque_Nmm=25000.;force=torque_Nmm/(2*40);width=32.;thickness=6.15;length=40.
    inertia=width*thickness**3/12
    report=dict(study='FITTED_STEEL_FACE_AND_END_CLOSURES',source_sha256=start,metadata=G.metadata(d),
        invalid_new_solids=invalid,new_self_intersections=hits,relative_motion_proofs=relative,
        global_tool_loop_or_whole_machine_proved=False,offcut_nesting=nest,custom_parts=custom,
        drawing_readbacks=drawing_checks,
        mass=dict(removed_Al_guidebars_kg=old_mass,new_custom_steel_face_caps_kg=new_mass,
            custom_part_moving_mass_increase_kg=new_mass-old_mass,
            complete_hardware_mass_added_not_in_this_number=True,axis_acceleration_or_motor_capacity_verified=False),
        conditional_cap_component_screen=dict(assumed_tool_force_N=100,assumed_lever_mm=250,torque_Nm=25,
            onecap_per_end_takes_all_end_reaction=True,force_per_cap_N=force,span_mm=length,minimum_screen_thickness_mm=thickness,
            assumed_E_MPa=200000,conservative_cantilever_deflection_mm=force*length**3/(3*200000*inertia),
            nominal_bending_stress_MPa=6*force*length/(width*thickness**2),
            scope='Component-onlycantileverscreen;nojointpreload/actualprofile/weld/counterborebearing/contact/impact/compositetorsionqualification.'),
        rail_holes_not_invented=True,actual_profile_Tnut_and_lip_capacity_qualified=False,
        long_steel_and_new_fasteners_delivered_price_verified=False,fabrication_release=False,operating_release=False)
    report['source_consistent_during_check']=start==hashes()
    report['output_sha256']={p.relative_to(HERE).as_posix():sha(p)for p in OUT.rglob('*')if p.is_file()and p.name!='gantry-joint-check.json'}
    report['passed']=report['source_consistent_during_check']and not invalid and not hits and all(q['passed']for q in relative)and nest['passed']and all(q['valid']for q in custom)and all(q['passed']for q in drawing_checks)
    (OUT/'gantry-joint-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],newparts=len(fresh),proofs=len(relative),failed=[(r['part'],r['obstacle'])for r in relative if not r['passed']],custom_mass_delta_kg=new_mass-old_mass,custom_STEPS=len(custom),nest=nest['passed'])),flush=True)
    return 0 if report['passed']else 2

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
