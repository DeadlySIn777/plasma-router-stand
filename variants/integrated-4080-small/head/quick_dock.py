"""Whole-owner-head removable dock, reusing the prior defined two-screw seat.

This optional attachment avoids dismantling the owner's working spindle/boot
assembly. Its supplier output attachment remains a transfer-fit interface.
"""
from functools import lru_cache
import csv,json,os,sys
import cadquery as cq
import owner_head as H
import common_dock_source as D

HERE=H.HERE;OUT=HERE/'output/quick-dock'
RECEIVER_REAR_Y=679.6
BASE_Z=1142.
PLATE_WIDTH=146.
HEAD_FRONT_Y=25.4
HEAD_FORWARD_SHIFT=3.175
RELEASE_WITHDRAWAL=12.8

def release_parts(withdrawal=0.):
    if not 0<=withdrawal<=RELEASE_WITHDRAWAL:raise ValueError('Captive stroke0..12.8mm')
    out=[]
    for x in(-28,28):
        tag='L'if x<0 else'R'
        cage=D.box(12.7,2,16,(x-6.35,44.2,32)).cut(D.cy(6.6,4,(x,43.2,40)))
        for dx in(-6.35,5.25):cage=cage.fuse(D.box(1.1,18.8,16,(x+dx,HEAD_FRONT_Y,32)))
        for z in(26,48):cage=cage.fuse(D.box(12.7,3,6,(x-6.35,HEAD_FRONT_Y,z)))
        for z in(29,51):cage=cage.cut(D.cy(3.4,5,(x,HEAD_FRONT_Y-1,z)))
        out.append(dict(id='CD_CAPTIVE_CAGE_'+tag,shape=cage.clean(),move='head'))
        out.append(dict(id='CD_RELEASE_SCREW_'+tag,shape=D.socket_screw_y(6,25,(x,.4+withdrawal,40)),move='head'))
        for z in(29,51):
            out.append(dict(id=f'CD_CAGE_FIX_{tag}_{z}',shape=D.socket_screw_y(3,10,(x,18.4,z)),move='head'))
    return out

def local_parts(withdrawal=0.,separation=0.):
    fixed,meta=D.common_dock();release=release_parts(withdrawal)
    old=fixed[0]['shape'];envelope=D.box(80,12.7,110,(-40,0,0))
    # The raised gantry places the output hold atZ1120..1170 at zero lift.
    # Keep its full50mm mounting contact, but remove the unnecessary lower
    # tail. The former1070mm lower edge hit the bed around16deg changeover.
    # All upper dock features and the owner's installed head stay unchanged.
    receiver=D.box(PLATE_WIDTH,12.7,132,(-PLATE_WIDTH/2,0,-22)).cut(envelope.cut(old))
    fixed[0]={**fixed[0],'shape':receiver.clean(),'notes':'New146x132x12.7 receiver, lowerZ1120 at zero lift. Full nominal raised-output contact retained; original upper dock features unchanged. Supplieroutput remains transfer-drilled.'}
    head=D.box(PLATE_WIDTH,12.7,175,(-PLATE_WIDTH/2,12.7,-65))
    head=head.cut(D.box(30.6,14.7,13,(-15.3,11.7,57)))
    for x in(-28,28):
        head=head.cut(D.cy(6.6,14.7,(x,11.7,40)))
        for z in(29,51):head=head.cut(D.cy(3,8,(x,17.4,z)))
    head=head.cut(D.cy(5.2,14.7,(-30,11.7,85)))
    slot=D.cy(5.2,14.7,(28.5,11.7,85)).fuse(D.cy(5.2,14.7,(31.5,11.7,85))).fuse(D.box(3,14.7,5.2,(28.5,11.7,82.4)))
    head=head.cut(slot)
    for x in(-25,25):
        for z in(-50,-20):head=head.cut(D.cy(5,14.7,(x,11.7,z)))
    moving=[dict(id='OWNER_ROUTER_HEAD_PLATE',shape=head.clean(),move='head',group='custom',
        material='Aluminium12.7billet',notes='146x175x12.7full-thickness; commonfeatureXZpositions retained, M6x25release12.8stroke, fourM5through-taps50x30.')]
    moving+=release
    clamp,boot=H.source_owner_local()
    moving.extend([dict(id='OWNER_65MM_CLAMP',shape=clamp.translate((0,HEAD_FORWARD_SHIFT,0)),move='head'),dict(id='OWNER_POWERED_SHIELD_BOOT_BODY',shape=boot.translate((0,HEAD_FORWARD_SHIFT,0)),move='head')])
    for i,x in enumerate((-25,25),1):
        for k,z in enumerate((-50,-20),1):
            tag=f'{i}_{k}'
            spacer=D.washer_y(10,5.5,6,(x,HEAD_FRONT_Y,z))
            seat=28.225+HEAD_FORWARD_SHIFT+H.WALL
            washer=D.washer_y(10,5.3,1,(x,seat,z))
            # Local +Y is forward; this source screw model has its head on+Y.
            screw=D.socket_screw_y(5,25,(x,seat+1-25,z))
            moving.extend([dict(id='OWNER_CLAMP_SPACER_'+tag,shape=spacer,move='head'),
                dict(id='OWNER_CLAMP_M5_SPREADER_'+tag,shape=washer,move='head'),
                dict(id='OWNER_CLAMP_M5X25_'+tag,shape=screw,move='head')])
    if separation:
        moving=[{**p,'shape':p['shape'].translate((0,separation,0))}for p in moving]
    meta.update(receiver_blank_mm=[PLATE_WIDTH,132,12.7],receiver_local_Z_bounds_mm=[-22,110],
        head_blank_mm=[PLATE_WIDTH,175,12.7],head_full_thickness_mm=12.7,
        head_width_mm=PLATE_WIDTH,head_default_height_mm=175,
        head_cage_bounds_by_center='Xcentre±6.35,Y25.4..46.2,Z26..54',
        nominal_head_section_I_ratio_to80x9p525=PLATE_WIDTH/80*pow(12.7/9.525,3),
        clamp_screw_thread_engagement_mm=25-H.WALL-6-1,
        clamp_screw_tip_reserve_mm=12.7-(25-H.WALL-6-1),
        head_removal_does_not_require_spindle_or_boot_disassembly=True,
        nominal_spindle_axis_Y_at_guide775_mm=RECEIVER_REAR_Y-70.72705925132-HEAD_FORWARD_SHIFT,
        release_centres_local_XZ_mm=[[-28,40],[28,40]],release_thread_engagement_mm=12.3,
        release_rear_tip_reserve_mm=.4,release_withdrawal_mm=RELEASE_WITHDRAWAL,
        release_withdrawn_tip_clearance_mm=.5,head_front_Y_mm=HEAD_FRONT_Y,
        cage_internal_front_Y_mm=44.2,cage_screw_retention_qualified=False,
        spindle_and_boot_mating_registration_not_measured=True)
    meta.pop('release_tip_reserve_mm',None)
    return fixed+moving,meta

def actual_head_dock_parts(gantry_y=775.,head_x=575.,z_lift=0.,boot_lift=0.,*,
                           boot_registration_z_mm=None,include_boot=True,
                           withdrawal=0.,separation=0.):
    assert 175<=head_x<=975 and 275<=gantry_y<=1275 and 0<=z_lift<=250
    if boot_registration_z_mm is None and boot_lift:
        raise ValueError('Existing working boot registration is not encoded.')
    assert 0<=boot_lift<=50
    local,meta=local_parts(withdrawal,separation)
    out=[]
    for p in local:
        n=p['id'];s=p['shape']
        if n=='OWNER_POWERED_SHIELD_BOOT_BODY':
            if not include_boot:continue
            s=s.translate((0,0,boot_lift+(boot_registration_z_mm or 0)))
        s=s.rotate((0,0,0),(0,0,1),180).translate((head_x,RECEIVER_REAR_Y+gantry_y-775,BASE_Z+z_lift))
        color=H.BOOT_COLOR if n=='OWNER_POWERED_SHIELD_BOOT_BODY'else H.DARK if ('SCREW'in n or'M5X'in n or'SPREADER'in n)else H.AL
        out.append((n,s,color))
    return out

def verify_and_export():
    OUT.mkdir(exist_ok=True)
    paths=[__file__,D.__file__,*H.sources()]
    start={str(H.Path(p).relative_to(H.ROOT)).replace('\\','/'):H.sha(p)for p in paths}
    local,meta=local_parts();hits=[];part_checks=[]
    for i,a in enumerate(local):
        sa=a['shape'];part_checks.append(dict(id=a['id'],valid=sa.isValid(),solids=len(sa.Solids())))
        for b in local[i+1:]:
            sb=b['shape']
            if H.S.overlap(H.bounds(sa),H.bounds(sb)):
                v=abs(sa.intersect(sb).Volume())
                if v>.02:hits.append(dict(a=a['id'],b=b['id'],volume_mm3=v))
    fixed=[p for p in local if p.get('move')!='head'];moving=[p for p in local if p.get('move')=='head']
    # Remove the two retained M6 screws by their defined11mm before translating
    # the complete head. The constant XZ profile makes+Y18 a continuous sweep.
    poses=[]
    for d in(0.,1.,8.,18.):
        parts,_=local_parts(withdrawal=RELEASE_WITHDRAWAL,separation=d);positive=[]
        fixedp=[p for p in parts if p.get('move')!='head'];movingp=[p for p in parts if p.get('move')=='head']
        for a in movingp:
            for b in fixedp:
                if H.S.overlap(H.bounds(a['shape']),H.bounds(b['shape'])):
                    v=abs(a['shape'].intersect(b['shape']).Volume())
                    if v>.02:positive.append(dict(a=a['id'],b=b['id'],volume_mm3=v))
        poses.append(dict(separation_mm=d,intersections=positive))
    seated_released,_=local_parts(withdrawal=RELEASE_WITHDRAWAL,separation=0)
    removal_covers=[];broad=0
    for a in seated_released:
        if a.get('move')!='head' or a['id']=='OWNER_POWERED_SHIELD_BOOT_BODY':continue
        b=H.bounds(a['shape'])
        sweep=[*b[:3],b[3],b[4]+18,b[5]]
        for q in fixed:
            if not H.S.overlap(sweep,H.bounds(q['shape'])):broad+=1;continue
            if a['id']=='OWNER_ROUTER_HEAD_PLATE'and q['id']=='CD_RECEIVER':
                ab=H.bounds(a['shape']);qb=H.bounds(q['shape'])
                proof=dict(passed=ab[1]>=qb[4]-1e-7,
                    minimum_normal_plane_gap_mm=ab[1]-qb[4],
                    method='Entire moving plate is on/forward of receiver front planeY12.7 and translates only+Y; zero designed mating-plane gap cannot produce positive-volume interference.')
            elif a['id']=='OWNER_ROUTER_HEAD_PLATE'and q['id']=='CD_GRAVITY_LEDGE':
                qb=H.bounds(q['shape'])
                swept_ledge=D.box(qb[3]-qb[0],qb[4]-qb[1]+18,qb[5]-qb[2],(qb[0],qb[1]-18,qb[2]))
                v=abs(a['shape'].intersect(swept_ledge).Volume())
                proof=dict(passed=v<.02,conservative_complete_ledge_prism_intersection_mm3=v,
                    ledge_XZ_bounds_mm=[qb[0],qb[2],qb[3],qb[5]],
                    head_window_XZ_bounds_mm=[-15.3,57,15.3,70],
                    intended_gravity_bearing_contact_Z_mm=70,
                    method='Complete fixed ledge bounding prism extruded through negativeY0..18; exact intersection with finished moving head is zero. Designed bearing-face tangency is retained; no positive-volume exemption.')
            else:proof=H.S.translation_cover_proof(a['shape'],q['shape'],[0,0,0],[0,18,0])
            removal_covers.append(dict(moving=a['id'],fixed=q['id'],**proof))
    continuous=dict(passed=all(q['passed']for q in removal_covers),broad_pairs_clear=broad,
        exact_cover_pairs=len(removal_covers),proofs=removal_covers,
        scope='Known clamp/complete head dock after12.8mm release-screw withdrawal, then continuous+Y0..18mm. Boot pose, hose/actuator and hand support remain separately unregistered/unqualified.')
    import build_head
    common=[p for p in H.C.motion_parts(False,775,575,125)if p[0]!='TOOL_ADAPTER_110'and not p[0].startswith(H.REMOVED_PREFIXES)]
    known_travel=build_head.head_relative_proof(actual_head_dock_parts(z_lift=125,include_boot=False),common,z_working_travel=250)
    exports={}
    for name,rows in [('OWNER_ROUTER_QUICK_DOCK_REFERENCE',local),
                      ('OWNER_ROUTER_QUICK_DOCK_KNOWN_CLAMP',[p for p in local if p['id']!='OWNER_POWERED_SHIELD_BOOT_BODY'])]:
        parts=actual_head_dock_parts(include_boot=name.endswith('REFERENCE'))
        asm=cq.Assembly(name=name)
        for n,s,c in parts:asm.add(s,name=n,color=cq.Color(*c))
        path=OUT/(name+'.step');asm.save(str(path));back=cq.importers.importStep(str(path)).val()
        exports[name]=dict(file=path.relative_to(H.HERE).as_posix(),sha256=H.sha(path),valid=back.isValid(),
            solids=len(back.Solids()),expected_solids=len(parts),volume_error_mm3=abs(back.Volume()-sum(s.Volume()for n,s,c in parts)))
    for p in local:
        if p['id']not in('CD_RECEIVER','OWNER_ROUTER_HEAD_PLATE'):continue
        s=p['shape'];b=H.bounds(s);path=OUT/(p['id']+'.step')
        cq.exporters.export(s.translate(tuple(-v for v in b[:3])),str(path))
        exports[p['id']]=dict(file=path.relative_to(H.HERE).as_posix(),sha256=H.sha(path),local_source_bounds_mm=b)
    report=dict(study='WHOLE_OWNER_HEAD_TWO_SCREW_GRAVITY_DOCK',metadata=meta,
        source_sha256=start,parts=part_checks,unexpected_static_intersections=hits,
        exact_removal_checkpoints=poses,continuous_removal_proof=continuous,
        continuous_known_clamp_removal_proved=continuous['passed'],
        known_clamp_dock_full_relative_travel=known_travel,
        exports=exports,source_consistent_during_check=start=={str(H.Path(p).relative_to(H.ROOT)).replace('\\','/'):H.sha(p)for p in paths},
        existing_working_boot_registration_known=False,
        assessed_working_Z_mm=250,controller_limits_or_settings_applied=False,
        complete_head_machine_integration=False,physical_handling_qualified=False,
        fabrication_release=False,operating_release=False)
    report['known_dock_static_and_removal_checkpoints_passed']=not hits and all(p['valid']and p['solids']==1 for p in part_checks)and all(not p['intersections']for p in poses)and continuous['passed']and known_travel['passed']and report['source_consistent_during_check']
    (OUT/'quick-dock-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['known_dock_static_and_removal_checkpoints_passed'],hits=hits,poses=poses)),flush=True)
    return 0 if report['known_dock_static_and_removal_checkpoints_passed']else 1

if __name__=='__main__':
    try:code=verify_and_export()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
