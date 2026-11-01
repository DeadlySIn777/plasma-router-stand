"""Separate custom-part repair candidate on the frozen XR2/owned-Z300 study.

No frozen source or earlier fit report is rewritten. Nominal thread bores are
major-diameter representations, not tap-drill instructions. Supplier mounting
interfaces and assembled stiffness remain unqualified.
"""
from pathlib import Path
import hashlib,json,os,sys,math
import z300_fit_study as S

cq=S.cq;M=S.M;P=S.P
HERE=Path(__file__).resolve().parent;OUT=HERE/'output'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cylinder(radius,length,origin,axis=(0,1,0)):
    return cq.Solid.makeCylinder(radius,length,cq.Vector(*origin),cq.Vector(*axis))
def sources():
    files=[Path(__file__),Path(S.__file__),S.BASE/'motion.py',S.BASE/'params.py',
        HERE/'owned-hardware-evidence.json',S.BASE/'motion-fabrication.csv',
        S.BASE/'frame.py',S.BASE/'bed.py',S.BASE/'shields.py',S.BASE/'atc.py',
        S.BASE/'build.py',S.BASE/'material_cover.py']
    files.extend(S.ROOT/n for n in M.interface_metadata()['source_sha256'])
    return list(dict.fromkeys(files))
def single_export(shape,path):
    origin=S.bounds(shape)[:3]
    local=shape.translate(tuple(-x for x in origin))
    cq.exporters.export(local,str(path))
    back=cq.importers.importStep(str(path)).val()
    error=abs(back.Volume()-local.Volume())
    return dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),
        source_world_min_corner_mm=origin,local_axes='World-aligned X/Y/Z; translated minimum corner is0,0,0; millimetres.',
        valid=back.isValid()and len(back.Solids())==1 and error<max(.01,local.Volume()*1e-7),
        solid_count=len(back.Solids()),roundtrip_volume_error_mm3=error)

def _repair_geometry(parts):
    """Pure pose-derived geometry; preserve all input IDs, poses and colors."""
    lookup={n:s for n,s,c in parts}
    carrier,support=lookup['Z_CARRIER'],lookup['X_LINK_SUPPORT']
    cb=S.bounds(carrier);sb=S.bounds(support)
    interference=carrier.intersect(support);ib=S.bounds(interference)
    assert abs(interference.Volume()-156*12.7*6.35)<1e-5,'Unexpected source interface'
    floor=ib[2];top=ib[5]+.2;end_centres=(ib[0]-.2,ib[3]+.2)
    width=top-floor;length=end_centres[1]-end_centres[0]+width
    centre=((end_centres[0]+end_centres[1])/2,(floor+top)/2)
    tool=cq.Workplane('XZ',origin=(centre[0],cb[4]+.1,centre[1])).slot2D(length,width).extrude(cb[4]-cb[1]+.2).val()
    relieved=carrier.cut(tool).clean()
    front=cb[4];depth=8.;extension=7.
    extension_box=[ib[0],front,sb[2]-extension,ib[3],front+depth,sb[2]]
    # Rebuild the complete downstand, rather than fusing onto two open partial
    # hole edges. The0.1mm construction overlap is inside existing flange
    # material; it adds no finished material outside the defined37mm web.
    flange=support.intersect(S.box([sb[0]-1,sb[1]-1,floor,sb[3]+1,sb[4]+1,sb[5]+1]))
    web=S.box([ib[0],front,sb[2]-extension,ib[3],front+depth,floor+.1])
    taps=[]
    for n,s,c in parts:
        if n.startswith('X_LINK_BRIDGE_BOLT_'):
            b=S.bounds(s);x=(b[0]+b[3])/2;z=(b[2]+b[5])/2
            taps.append(cylinder(3.,depth+2,(x,front-1,z)))
    assert len(taps)==4
    revised=flange.fuse(web).cut(cq.Compound.makeCompound(taps)).clean()
    result=[(n,relieved if n=='Z_CARRIER'else revised if n=='X_LINK_SUPPORT'else s,c)for n,s,c in parts]
    return result,dict(carrier=carrier,support=support,relieved=relieved,revised=revised,
        cb=cb,sb=sb,interference=interference,ib=ib,floor=floor,top=top,end_centres=end_centres,
        width=width,length=length,centre=centre,tool=tool,front=front,depth=depth,
        extension=extension,extension_box=extension_box)

def apply_repairs(parts):
    """Return repaired motion tuples; input must already contain the chosen Z.

    Only Z_CARRIER and X_LINK_SUPPORT change. This function does not apply a
    300mm overlay, stretch an actuator or change its assessed operating range.
    It performs no file writes and is valid at translated reference poses.
    """
    return _repair_geometry(parts)[0]

def run():
    paths=sources();hashes=lambda:{p.relative_to(S.ROOT).as_posix():sha(p)for p in paths}
    start=hashes()
    original=M.motion_parts(False,775.,575.,0.)
    stock=S.overlay(original,extended_carrier=False)
    repaired,setup=_repair_geometry(stock)
    carrier,support=setup['carrier'],setup['support'];cb,sb=setup['cb'],setup['sb']
    interference,ib=setup['interference'],setup['ib']
    assert abs(interference.Volume()-156*12.7*6.35)<1e-5
    assert max(abs(a-b)for a,b in zip(ib,[497.,759.6,1313.2,653.,772.3,1319.55]))<1e-6
    floor,top=setup['floor'],setup['top'];end_centres=setup['end_centres']
    width,length,centre=setup['width'],setup['length'],setup['centre']
    tool,relieved,revised=setup['tool'],setup['relieved'],setup['revised']

    # The lower tap row was only2mm above a30mm downstand edge. Extend the
    # integral billet by7mm, leaving all four established axes and bolt stacks.
    downstand_front=setup['front'];downstand_depth=setup['depth'];extension=setup['extension']
    extension_box=setup['extension_box']
    bolt_records=[];tap_records=[]
    for n,s,c in stock:
        if not n.startswith('X_LINK_BRIDGE_BOLT_'):continue
        bb=S.bounds(s);x=(bb[0]+bb[3])/2;z=(bb[2]+bb[5])/2
        seat=cylinder(6.,cb[4]-cb[1],(x,cb[1],z)).cut(cylinder(3.3,cb[4]-cb[1]+2,(x,cb[1]-1,z)))
        bolt_records.append(dict(id=n,axis_X_Z_mm=[x,z],
            D12_carrier_seat_missing_material_mm3=seat.cut(relieved).Volume(),
            D10_head_top_to_relief_floor_mm=floor-z-5,
            clearance_bore_edge_to_relief_floor_mm=floor-z-3.3,
            unchanged_nominal_carrier_grip_mm=cb[4]-cb[1],
            unchanged_nominal_support_thread_engagement_mm=bb[4]-downstand_front,
            unchanged_nominal_screw_tip_reserve_mm=downstand_front+downstand_depth-bb[4]))
        edges=[x-ib[0]-3,ib[3]-x-3,z-(sb[2]-extension)-3,floor-z-3]
        tap_records.append(dict(axis_X_Z_mm=[x,z],major_diameter_mm=6,
            old_lower_edge_ligament_mm=z-sb[2]-3,new_lower_edge_ligament_mm=z-(sb[2]-extension)-3,
            minimum_outer_major_diameter_ligament_mm=min(edges)))
    # Recheck every complete tap bore and a1mm annular material shell only
    # after all cuts, so adjacent cuts cannot invalidate an earlier check.
    for r in tap_records:
        x,z=r['axis_X_Z_mm']
        bore=cylinder(3.,downstand_depth,(x,downstand_front,z))
        annulus=cylinder(4.,downstand_depth,(x,downstand_front,z)).cut(cylinder(3.,downstand_depth+2,(x,downstand_front-1,z)))
        r['nominal_tap_bore_intersection_mm3']=bore.intersect(revised).Volume()
        r['D8_annular_shell_missing_material_mm3']=annulus.cut(revised).Volume()

    patch=cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(x,y,floor)for x,y in
        [(ib[0],ib[1]),(ib[3],ib[1]),(ib[3],ib[4]),(ib[0],ib[4]),(ib[0],ib[1])]]))
    def contact_area(s):
        return sum(f.intersect(patch).Area()for f in s.Faces()
            if f.geomType()=='PLANE'and abs(S.bounds(f)[2]-floor)<1e-6 and abs(S.bounds(f)[5]-floor)<1e-6)
    ca,sa=contact_area(relieved),contact_area(revised)
    removed_below=carrier.cut(relieved).intersect(S.box([cb[0]-1,cb[1]-1,cb[2]-1,cb[3]+1,cb[4]+1,floor])).Volume()
    additions=revised.cut(support)
    candidates=[('X_LINK_SUPPORT',additions,(.6,.7,.7))]
    others=[p for p in stock if p[0]not in('Z_CARRIER','X_LINK_SUPPORT')]
    own_bolts=[p for p in others if p[0].startswith('X_LINK_BRIDGE_BOLT_')]
    relative=S.relative_proof(candidates,[p for p in others if p not in own_bolts])
    # These four specific source-defined M6 screws and this support share the
    # same rigid XY class. Their modeled major-diameter cylinders meet the
    # nominal thread bores; positive0.01mm clearance would be the wrong test.
    # Require exact nonpenetration and an unchanged relative transform instead.
    nominal_threads=[]
    for n,s,c in own_bolts:
        volume=additions.intersect(s).Volume();whole_volume=revised.intersect(s).Volume()
        same=S.FACTORS[S.cls(n)]==S.FACTORS[S.cls('X_LINK_SUPPORT')]
        nominal_threads.append(dict(fastener=n,support='X_LINK_SUPPORT',same_rigid_motion_class=same,
            added_material_intersection_mm3=volume,whole_support_intersection_mm3=whole_volume,
            passed=same and volume<1e-7 and whole_volume<1e-7,
            scope='Source-defined co-moving nominal M6 major-diameter thread interface. This is exact geometric nonpenetration, not physical thread fit, a tap-drill size or rated engagement.'))
    relative['nominal_co_moving_M6_thread_interfaces']=nominal_threads
    relative['passed']=relative['passed']and len(nominal_threads)==4 and all(r['passed']for r in nominal_threads)
    # Carrier is unchanged below the original ledge and has material removed
    # only; include it in the exact new-support material check, without waiver.
    local=S.exact_pairs(candidates,[('Z_CARRIER',relieved,(.6,.7,.7)),*others])
    changed_whole=[('Z_CARRIER',relieved,(.6,.7,.7)),('X_LINK_SUPPORT',revised,(.6,.7,.7))]
    whole_static=S.exact_pairs(changed_whole,others)
    external={}
    for hot in(False,True):
        fixed=S.frame_parts()+S.bed_parts(hot)+S.accessory_parts(hot)
        external['PLASMA'if hot else'WOOD']=S.external_proof(candidates,fixed)
    tb=S.bounds(tool);left=tb[0]-cb[0];right=cb[3]-tb[3]
    checks=dict(original_custom_interference_identified=interference.Volume()>0,
        carrier_valid_one_solid=relieved.isValid()and len(relieved.Solids())==1,
        support_valid_integral_one_solid=revised.isValid()and len(revised.Solids())==1,
        original_support_material_preserved=support.cut(revised).Volume()<1e-7,
        carrier_outer_blank_unchanged=max(abs(a-b)for a,b in zip(S.bounds(relieved),cb))<1e-6,
        carrier_no_added_material=relieved.cut(carrier).Volume()<1e-7,
        original_lower_carrier_material_unchanged=removed_below<1e-7,
        zero_positive_custom_part_overlap=relieved.intersect(revised).Volume()<1e-7,
        full_positive_bearing_patch=abs(ca-156*12.7)<1e-5 and abs(sa-156*12.7)<1e-5,
        four_complete_carrier_head_seats=len(bolt_records)==4 and all(r['D12_carrier_seat_missing_material_mm3']<1e-7 for r in bolt_records),
        four_complete_tap_bores_and_shells=len(tap_records)==4 and all(r['nominal_tap_bore_intersection_mm3']<1e-7 and r['D8_annular_shell_missing_material_mm3']<1e-7 and r['minimum_outer_major_diameter_ligament_mm']>=6-1e-6 for r in tap_records),
        new_material_static_clear=not local['unexpected'],new_material_relative_sweep_clear=relative['passed'],
        whole_changed_custom_parts_static_clear=not whole_static['unexpected'],
        new_material_external_sweeps_clear=all(r['passed']for r in external.values()))

    repaired=[(n,relieved if n=='Z_CARRIER'else revised if n=='X_LINK_SUPPORT'else s,c)for n,s,c in stock]
    head=[p for p in repaired if p[0]=='Z_CARRIER'or p[0]=='X_LINK_SUPPORT'or p[0].startswith(('ZBX80_','Z300_','TOOL_','X_LINK_BRIDGE_BOLT_'))]
    outputs={'carrier':single_export(relieved,OUT/'Z_CARRIER_RELIEVED_CANDIDATE.step'),
        'support':single_export(revised,OUT/'X_LINK_SUPPORT_D37_CANDIDATE.step'),
        'stock_300_head':S.export(head,'Z300_STOCK_HEAD_REPAIRED_CUSTOM_JOINT.step')}
    current=hashes();report=dict(study='SEPARATE_CUSTOM_JOINT_REPAIR_CANDIDATE',source_sha256=current,
        source_consistent_during_check=start==current,
        passed=start==current and all(checks.values())and all(r['valid']for r in outputs.values()),
        check_scope='Custom solid interference, bearing/fastener geometry, incremental added-support material clearance and STEP fidelity only; not assembled strength or supplier fit.',
        checks=checks,pose_X_Yguide_Zlift_mm=[575,775,0],original_interference_mm3=interference.Volume(),
        original_interference_bounds_mm=ib,original_carrier_bounds_mm=cb,repaired_carrier_bounds_mm=S.bounds(relieved),
        carrier_relief=dict(face_axes='X across plate, Z up plate; thickness along worldY',
            overall_slot_length_mm=length,slot_height_mm=width,end_radius_mm=width/2,
            end_centres_world_X_mm=list(end_centres),floor_world_Z_mm=floor,top_world_Z_mm=top,
            centre_from_carrier_min_X_Z_mm=[centre[0]-cb[0],centre[1]-cb[2]],tool_bounds_mm=tb,
            bearing_contact_area_carrier_mm2=ca,bearing_contact_area_support_mm2=sa,
            support_intersection_after_repair_mm3=relieved.intersect(revised).Volume(),removed_original_lower_material_mm3=removed_below),
        revised_support=dict(original_downstand_height_mm=30,new_downstand_height_mm=37,
            original_bottom_Z_mm=sb[2],new_bottom_Z_mm=sb[2]-extension,top_Z_mm=floor,
            added_strip_envelope_mm=extension_box,added_material_volume_mm3=additions.Volume(),
            unchanged_nominal_thread_depth_mm=8,raw_stock_status='NEW_OR_VERIFIED_EXISTING_BILLET_REQUIRED; NO OWNED_STOCK_CREDIT',
            finished_bounding_blank_mm=[156,120.8,43.35],cleanup_allowance_included=False,
            original_finished_bounding_blank_mm=[156,120.8,36.35]),
        M6_carrier_seats_and_unchanged_stacks=bolt_records,M6_nominal_tap_geometry=tap_records,
        whole_changed_custom_parts_static=whole_static,
        added_material_static=local,added_material_relative=relative,added_material_external=external,
        structural_geometry_only=dict(continuous_side_web_widths_mm=[left,right],
            minimum_combined_side_web_area_mm2=(left+right)*12.7,
            isolated_minimum_weak_axis_section_ratio=(left+right)/260,
            isolated_minimum_inplane_section_ratio=1-(length/260)**3,
            qualification='Geometric net-section ratios for a homogeneous rectangular plate only; no strength, joint stiffness, fatigue, modal or full tool-loop qualification.'),
        outputs=outputs,frozen_XR2_modified=False,earlier_fit_study_modified=False,
        supplier_mounting_interfaces_verified=False,fabrication_release=False,
        remaining=['Verify actual300mm module fastening rows avoid the relief and have adequate edge distances and support span.',
            'Verify actual billet alloy/temper, nominal thread pilot5.0/tapM6x1 process, thread tolerances/usable depth and tightening.',
            'Set a machining and assembly tolerance stack for the exact bearing floor and0.20mm top clearance; no collision tolerance is substituted.',
            'Qualify the two side-web load paths, local stress concentrations, carrier bending, support flange/downstand and complete tool-loop stiffness.'])
    (OUT/'custom-joint-repair-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],checks=checks,contact_areas=[ca,sa],outputs=outputs),indent=2),flush=True)
    return 0 if report['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
