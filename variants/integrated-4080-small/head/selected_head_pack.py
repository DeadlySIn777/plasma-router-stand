"""Selected shared-router/plasma dock takeoff and nonoverlapping owned-stock nest."""
from pathlib import Path
import csv,json,os,sys
import cadquery as cq
import quick_dock as Q
import plasma_quick_dock as P
import owner_head as H

HERE=H.HERE;OUT=HERE/'output/selected-head-pack'

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
    rows=[
        ('Owned router clamp/boot/actuator/spindle/VFD',1,'OWNED','Existing working owner head; no replacement clamp/actuator',0,'Owner assembly registration and exact spindle nose remain fitting gates'),
        ('Shared receiver',1,'OWNED_HALF_SHEET','146x132x12.7 finished; source-defined upper dock and transfer-fit raised output',0,'Included exact nest; unused50mm tail removed for front-bay bed arc; no duplicate stock credit'),
        ('Router removable plate',1,'OWNED_HALF_SHEET','146x175x12.7 full-thickness billet interface',0,'Included exact nest; source clamp unchanged'),
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
    I=146*12.7**3/12;E=69000.;L=90.
    screen=[dict(force_N=F,loaded_projection_below_nominal_reference_mm=P,
        ideal_tool_displacement_mm=F/(E*I)*(L**3/3+(122+P)*L**2+(122+P)**2*L))
        for F in(25,50,100)for P in(15,50)]
    report=dict(study='SELECTED_ROUTER_PLASMA_SHARED_HEAD_STOCK_AND_TAKEOFF',source_sha256=start,
        ownership_basis='One owner-reported304.8x304.8x12.7sheet allocated exclusively to these10rectangles; actual alloy/thickness/flatness remain verified before machining. Old83-part allocations are superseded for this sheet, not additional free stock.',
        stock_mm=[304.8,304.8,12.7],outer_margin_mm=2,minimum_profile_gap_mm=4,
        machining_basis='Full-sheet contours to finished nominal perimeters with cutter diameter≤4mm and adequate tabs/fixture. No additional per-part saw/facing allowance is included; this is not a saw-cut blank nest.',
        allocation=placements,all_nonoverlap_pair_checks=nest,outputs=outputs,
        quarter_three_eighth_sheet_additional_allocation='Only one30x12.7ledge requested here; parent must reconcile with all other3/8allocations',
        unpriced_requirement_CSV=dict(file=bom.relative_to(HERE).as_posix(),sha256=H.sha(bom)),
        retained_plasma_takeoff=dict(file=path.relative_to(HERE).as_posix(),sha256=H.sha(path),rows=len(stack),source_file=takeoff.relative_to(H.ROOT).as_posix(),source_sha256=H.sha(takeoff)),
        integral_switch_plunger_nonadditive_crosswalk=plunger_crosswalk,
        ideal_head_plate_screen=dict(E_MPa=E,gross_I_mm4=I,uniform_section_mm=[146,12.7],
            assumed_fixed_section='Continuous ideal clamp atM6rowZ1182',
            bottom_source_clamp_mount_Z_mm=1092,nominal_spindle_lower_reference_Z_mm=970,
            cases=screen,formula='F/(E*I)*(L^3/3+a*L^2+a^2*L),L90,a122+toolprojection',
            limitations='Gross section idealization only; excludes holes, true finite bolted supports, receiver bending, source clamp, rails, spindle bearings and everyotherframe/bedjoint. No complete-machine rigidity or stock-alloy qualification.'),
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
