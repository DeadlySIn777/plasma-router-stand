"""Matching plasma module for the same fixed owner-head gravity receiver.

The existing drop/float/breakaway stack and nozzle allocation keep their exact
reference-world pose. Only the custom upper drop fixing bores change, with a
new front U-splice joining it to the removable common head plate.
"""
from functools import lru_cache
import csv,json,os,sys
import cadquery as cq
import quick_dock as Q
import owner_head as H
import common_dock_source as D
import build_head as B

HERE=H.HERE;OUT=HERE/'output/plasma-quick-dock'
UPPER_X=(530.,620.);LOW_Z=(1092.,1118.);HIGH_Z=(1160.,1186.)

def world(s):return s.rotate((0,0,0),(0,0,1),180).translate((575,Q.RECEIVER_REAR_Y,Q.BASE_Z))
def host_holes(s,zrows):
    for x in UPPER_X:
        for z in zrows:
            s=s.cut(H.cyl(6.6,14.7,(x,667.9,z),(0,-1,0)))
            s=s.cut(H.cyl(10.5,6.1,(x,666.9,z),(0,-1,0)))
    return s.clean()

@lru_cache(maxsize=1)
def reference_module():
    prior=H.C.motion_parts(True,775,575,0)
    source={n:(s,c)for n,s,c in prior}
    source_drop=next((n,s,c)for n,s,c in prior if n.startswith('XR_PLASMA_DROP_'))
    retained=[(n,s,c)for n,s,c in prior if n.startswith(('I_HEAD_','XR_DROP_M6x16_LOWER_'))]
    local,meta=Q.local_parts(stiffener=False)
    head=next(p['shape']for p in local if p['id']=='OWNER_ROUTER_HEAD_PLATE')
    head=head.intersect(D.box(Q.PLATE_WIDTH,14.7,110,(-Q.PLATE_WIDTH/2,11.7,0)))
    head=host_holes(world(head),HIGH_Z)
    drop=host_holes(source_drop[1],LOW_Z)
    splice=D.box(110,12.7,114,(520,641.5,1082))
    notch=D.box(70,14.7,31,(540,640.5,1166)).fuse(D.box(76,14.7,28,(537,640.5,1169)))
    for x in(540,610):notch=notch.fuse(H.cyl(6,14.7,(x,640.5,1169)))
    splice=splice.cut(notch)
    bolts=[]
    for side,x in enumerate(UPPER_X,1):
        for row,z in enumerate((*LOW_Z,*HIGH_Z),1):
            splice=splice.cut(H.cyl(6,14.7,(x,640.5,z)))
            shank=H.cyl(6,16,(x,660.8,z),(0,-1,0))
            screw=shank.fuse(H.cyl(10,6,(x,660.8,z))).clean()
            bolts.append((f'PLASMA_SPLICE_M6X16_{side}_{row}',screw,H.DARK))
    custom=[('PLASMA_REMOVABLE_HEAD_PLATE',head,H.AL),
        ('PLASMA_U_SPLICE_PLATE',splice.clean(),H.AL),(source_drop[0],drop,source_drop[2]),*bolts]
    return tuple(custom+retained)

def plasma_head_dock_parts(gantry_y=775.,head_x=575.,z_lift=0.,*,withdrawal=0.,separation=0.):
    common=[p for p in Q.actual_head_dock_parts(gantry_y,head_x,z_lift,include_boot=False,
        withdrawal=withdrawal,separation=separation)if p[0].startswith('CD_')]
    shift=(head_x-575,gantry_y-775-separation,z_lift)
    return common+[(n,s.translate(shift),c)for n,s,c in reference_module()]

def integrate_motion(plasma,gantry_y=775.,head_x=575.,z_lift=0.,**kwargs):
    assert 0<=z_lift<=250
    source=H.C.motion_parts(plasma,gantry_y,head_x,min(z_lift,200))
    if z_lift>200:
        source=[(n,s.translate((0,0,z_lift-200))if H.S.cls(n)=='Y_X_Z_tool'else s,c)for n,s,c in source]
    common=[p for p in source
        if p[0]!='TOOL_ADAPTER_110'and not p[0].startswith(H.REMOVED_PREFIXES)
        and not p[0].startswith(('I_HEAD_','XR_DROP_','XR_PLASMA_DROP_'))]
    if plasma:return common+plasma_head_dock_parts(gantry_y,head_x,z_lift,**kwargs)
    return common+Q.actual_head_dock_parts(gantry_y,head_x,z_lift,**kwargs)

def run():
    OUT.mkdir(exist_ok=True)
    paths=[__file__,Q.__file__,D.__file__,*H.sources()]
    hashes=lambda:{str(H.Path(p).relative_to(H.ROOT)).replace('\\','/'):H.sha(p)for p in paths}
    start=hashes();parts=plasma_head_dock_parts();lookup={n:s for n,s,c in parts}
    prior=H.C.motion_parts(True,775,575,0);old={n:s for n,s,c in prior}
    new_ids=[n for n in lookup if n.startswith(('CD_','PLASMA_','XR_PLASMA_DROP_'))]
    new=[p for p in parts if p[0]in new_ids];retained=[p for p in parts if p[0]not in new_ids]
    pairs=[]
    for i,(n,s,c)in enumerate(new):
        for nf,sf,cf in new[i+1:]+retained:
            if not H.S.overlap(H.bounds(s),H.bounds(sf)):continue
            v=abs(s.intersect(sf).Volume())
            if v>.02:pairs.append(dict(a=n,b=nf,volume_mm3=v))
    exact_unchanged={n:dict(symdiff_mm3=s.cut(old[n]).Volume()+old[n].cut(s).Volume(),
        bbox_error_mm=max(abs(a-b)for a,b in zip(H.bounds(s),H.bounds(old[n]))))for n,s,c in retained}
    mount=[]
    for x in UPPER_X:
        for z in(*LOW_Z,*HIGH_Z):
            host=lookup['PLASMA_REMOVABLE_HEAD_PLATE']if z in HIGH_Z else next(s for n,s,c in parts if n.startswith('XR_PLASMA_DROP_'))
            ring=H.cyl(10,.05,(x,660.75,z)).cut(H.cyl(6.6,.15,(x,660.7,z)))
            shell=H.cyl(9,9.4,(x,644.8,z)).cut(H.cyl(6,11.4,(x,643.8,z)))
            mount.append(dict(X=x,Z=z,full_head_seat_missing_mm3=ring.cut(host).Volume(),
                D9_thread_landing_missing_mm3=shell.cut(lookup['PLASMA_U_SPLICE_PLATE']).Volume(),
                thread_engagement_mm=9.4,splice_tip_reserve_mm=3.3,
                host_web_mm=6.6,host_rear_counterbore_depth_mm=6.1,head_rear_flush_reserve_mm=.1))
    local,meta=Q.local_parts()
    fixed_ids={p['id']for p in local if p.get('move')!='head'}
    fixed=[p for p in parts if p[0]in fixed_ids]
    released=plasma_head_dock_parts(withdrawal=Q.RELEASE_WITHDRAWAL)
    moving=[p for p in released if p[0]not in fixed_ids]
    proof=[];broad=0
    for n,s,c in moving:
        b=H.bounds(s);sweep=[b[0],b[1]-18,b[2],b[3],b[4],b[5]]
        for nf,sf,cf in fixed:
            if not H.S.overlap(sweep,H.bounds(sf)):broad+=1;continue
            if nf=='CD_RECEIVER':
                gap=H.bounds(sf)[1]-b[4]
                p=dict(passed=gap>=-1e-7,normal_gap_mm=gap,
                    method='All moving material is on/forward of the fixed receiver planeY666.9 and moves only−Y; designed plane contact cannot create positive volume.')
            elif n=='PLASMA_REMOVABLE_HEAD_PLATE'and nf=='CD_GRAVITY_LEDGE':
                fb=H.bounds(sf);obstacle=D.box(fb[3]-fb[0],fb[4]-fb[1]+18,fb[5]-fb[2],(fb[0],fb[1],fb[2]))
                v=abs(s.intersect(obstacle).Volume())
                p=dict(passed=v<.02,conservative_ledge_prism_intersection_mm3=v,
                    method='Complete fixed ledge bounding prism extruded by opposite18mm; zero exact positive material, designed gravity-seat tangency retained.')
            else:p=H.S.translation_cover_proof(s,sf,[0,-18,0],[0,0,0])
            proof.append(dict(moving=n,fixed=nf,**p))
    common=[p for p in H.C.motion_parts(True,775,575,125)if p[0]!='TOOL_ADAPTER_110'
        and not p[0].startswith(('I_HEAD_','XR_DROP_','XR_PLASMA_DROP_'))]
    relative=B.head_relative_proof(plasma_head_dock_parts(z_lift=125),common,z_working_travel=250)
    exports={}
    assembly=cq.Assembly(name='SHARED_RECEIVER_COMPLETE_PLASMA_MODULE')
    for n,s,c in parts:assembly.add(s,name=n,color=cq.Color(*c))
    path=OUT/'SHARED_RECEIVER_COMPLETE_PLASMA_MODULE.step';assembly.save(str(path))
    back=cq.importers.importStep(str(path)).val()
    exports['assembly']=dict(file=path.relative_to(HERE).as_posix(),sha256=H.sha(path),valid=back.isValid(),
        solids=len(back.Solids()),expected_solids=sum(len(s.Solids())for n,s,c in parts),
        volume_error_mm3=abs(back.Volume()-sum(s.Volume()for n,s,c in parts)))
    for n in('PLASMA_REMOVABLE_HEAD_PLATE','PLASMA_U_SPLICE_PLATE'):
        s=lookup[n];b=H.bounds(s);path=OUT/(n+'.step')
        cq.exporters.export(s.translate(tuple(-x for x in b[:3])),str(path))
        exports[n]=dict(file=path.relative_to(HERE).as_posix(),sha256=H.sha(path),source_world_min_corner_mm=b[:3],bounds_mm=H.bounds(s))
    drop_id=next(n for n in lookup if n.startswith('XR_PLASMA_DROP_'));s=lookup[drop_id];b=H.bounds(s)
    path=OUT/'XR_PLASMA_DROP_SHARED_DOCK_CLEARANCE_BORES.step';cq.exporters.export(s.translate(tuple(-x for x in b[:3])),str(path))
    exports[drop_id]=dict(file=path.relative_to(HERE).as_posix(),sha256=H.sha(path),source_world_min_corner_mm=b[:3],
        added_material_mm3=s.cut(old[drop_id]).Volume(),removed_material_mm3=old[drop_id].cut(s).Volume())
    report=dict(study='COMMON_FIXED_RECEIVER_WITH_REMOVABLE_PLASMA_MODULE',source_sha256=start,
        shared_receiver_world_geometry_identical_to_router=True,
        source_stack_preserved_world_pose=exact_unchanged,
        old_drop_change='Only four upper customM6attachmentbores become6.6clearance and10.5rear counterbores6.1deep; all otherdrop/float/headgeometryandtorchheightunchanged.',
        new_part_intersections=pairs,matched_eight_M6_mount_checks=mount,
        removal=dict(broad_pairs_clear=broad,proofs=proof,passed=all(p['passed']for p in proof)),
        working250_relative_proof=relative,exports=exports,
        assessed_working_Z_mm=250,controller_limits_or_settings_applied=False,
        part_validity=[dict(id=n,valid=s.isValid(),solids=len(s.Solids()))for n,s,c in parts],
        full_float_breakaway_or_actual_torch_motion_qualified=False,
        source_consistent_during_check=start==hashes(),fabrication_release=False,operating_release=False)
    report['known_shared_plasma_interface_passed']=not pairs and all(q['symdiff_mm3']<.05 and q['bbox_error_mm']<1e-5 for q in exact_unchanged.values())and all(abs(v)<.02 for q in mount for k,v in q.items()if k.endswith('_missing_mm3'))and report['removal']['passed']and relative['passed']and back.isValid()and report['source_consistent_during_check']
    (OUT/'plasma-dock-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['known_shared_plasma_interface_passed'],new_intersections=pairs,
        unchanged_stack_parts=len(exact_unchanged),removal=report['removal']['passed'],relative=relative['passed'],mounts=mount)),flush=True)
    return 0 if report['known_shared_plasma_interface_passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
