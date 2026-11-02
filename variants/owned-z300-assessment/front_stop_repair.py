"""Candidate-only relief of two inherited front-stop/motor bracket clashes.

The forward base screw is moved from Y90 to105, with both mating holes.
No source XR2 solid, original carrier repair, switch or buffer datum changes.
"""
from pathlib import Path
import hashlib,json,os,sys
import z300_fit_study as S
import custom_joint_repair as R

HERE=Path(__file__).resolve().parent
OUT=HERE/'output'/'front-stop-repair'
CHANGED={f'{prefix}_{side}_FRONT'+suffix for side in('L','R')
         for prefix,suffix in(('Y_STOP','_BRACKET'),('XR_STOP_CARRIER',''),('XR_STOP_BASE_M6x12','_1'))}

def cyl(d,h,o):return S.cq.Solid.makeCylinder(d/2,h,S.cq.Vector(*o))
def canonical(shape,side):return shape if side=='L'else shape.mirror('YZ',(575,0,0))

def apply_repairs(parts):
    """Six named stationary parts change; all other tuple values are retained."""
    replacements={};lookup={n:s for n,s,_ in parts};z=S.M.OLD_BASE
    for side in('L','R'):
        ident=f'Y_STOP_{side}_FRONT_BRACKET'
        old=canonical(lookup[ident],side)
        # New manufacture: close the superseded clearance bore before making
        # a complete through relief. This is not a weld/plug repair procedure.
        revised=old.fuse(cyl(6.6,6.35,(58.5,90,z))).clean()
        relief=S.box([48.5,79,z-1,55.9,95.5,z+7.35])
        revised=revised.cut(relief).cut(cyl(6.6,8.35,(58.5,105,z-1))).clean()
        replacements[ident]=canonical(revised,side)
        ident=f'XR_STOP_CARRIER_{side}_FRONT'
        old=canonical(lookup[ident],side)
        revised=old.fuse(cyl(6.,6.35,(58.5,90,z-6.35))).clean()
        revised=revised.cut(cyl(6.,8.35,(58.5,105,z-7.35))).clean()
        replacements[ident]=canonical(revised,side)
        ident=f'XR_STOP_BASE_M6x12_{side}_FRONT_1'
        replacements[ident]=lookup[ident].translate((0,15,0))
    assert set(replacements)==CHANGED
    return [(n,replacements.get(n,s),c)for n,s,c in parts]

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    paths=[Path(__file__),*R.sources()]
    hashes=lambda:{p.relative_to(S.ROOT).as_posix():S.sha(p)for p in dict.fromkeys(paths)}
    start=hashes()
    old=R.apply_repairs(S.overlay(S.M.motion_parts(False,775,575,100)))
    parts=apply_repairs(old);lookup={n:s for n,s,_ in parts};original={n:s for n,s,_ in old}
    checks={};exports={}
    for side in('L','R'):
        ids=[f'Y_STOP_{side}_FRONT_BRACKET',f'XR_STOP_CARRIER_{side}_FRONT',f'XR_STOP_BASE_M6x12_{side}_FRONT_1']
        bracket,carrier,screw=(lookup[n]for n in ids)
        motor=lookup[f'HMS_Y_{side}_MOTOR_BRACKET']
        x=58.5 if side=='L' else 1091.5;z=S.M.OLD_BASE
        # Entire diameter10 head, diameter6 clearance grip and exact 5.65mm
        # threaded length are seated after relocation. Thread bore is shown at
        # major diameter in the review CAD, not a drilling instruction.
        seat=cyl(10,6.35,(x,105,z)).cut(cyl(6.6,8.35,(x,105,z-1)))
        shell=cyl(9.,5.65,(x,105,z-5.65)).cut(cyl(6.,7.65,(x,105,z-6.65)))
        checks[side]=dict(old_motor_stop_intersection_mm3=original[ids[0]].intersect(motor).Volume(),
            motor_stop_intersection_mm3=bracket.intersect(motor).Volume(),
            motor_stop_gap_mm=bracket.distance(motor),
            moved_screw_motor_gap_mm=screw.distance(motor),
            clearance_grip_intersection_mm3=bracket.intersect(screw).Volume(),
            major_thread_screw_carrier_intersection_mm3=carrier.intersect(screw).Volume(),
            D10_head_seat_missing_material_mm3=seat.cut(bracket).Volume(),
            D9_landing_shell_missing_material_mm3=shell.cut(carrier).Volume(),
            nominal_engagement_mm=5.65,nominal_tip_reserve_mm=.70,
            base_thickness_mm=6.35,clearance_bore_mm=6.6,
            forward_axis_X_Y_mm=[x,105],rear_axis_X_Y_mm=[x,140],
            minimum_clearance_bore_ligament_mm=5.7,
            minimum_new_major_thread_ligament_mm=6.,
            full_head_seat_outer_diameter_mm=10.,
            holes_spacing_mm=35.,mount_capacity_qualified=False)
        for n in ids[:2]:
            shape=lookup[n];b=S.bounds(shape);local=shape.translate(tuple(-q for q in b[:3]));path=OUT/(n+'_REVISED.step')
            S.cq.exporters.export(local,str(path));back=S.cq.importers.importStep(str(path)).val()
            exports[n]=dict(file=path.relative_to(HERE).as_posix(),sha256=S.sha(path),
                source_world_min_corner_mm=b[:3],bounds_local_mm=S.bounds(local),
                valid=back.isValid()and len(back.Solids())==1 and abs(back.Volume()-local.Volume())<.05,
                solid_count=len(back.Solids()))
        checks[side]['passed']=all(checks[side][k]<1e-7 for k in('motor_stop_intersection_mm3','clearance_grip_intersection_mm3','major_thread_screw_carrier_intersection_mm3','D10_head_seat_missing_material_mm3','D9_landing_shell_missing_material_mm3'))and checks[side]['motor_stop_gap_mm']>=.49999
    report=dict(study='CANDIDATE_FRONT_STOP_RELIEF_AND_RELOCATED_MATCHED_FORWARD_MOUNT',
        source_sha256=start,checks=checks,outputs=exports,changed_parts=sorted(CHANGED),
        manufacturing_intent='New custom parts. Superseded Y90 hole is absent in the revised finished solids. Stop clearance D6.6 atY105 and nominal majorD6 carrier tap atY105 replace it. Actual M6x1 pilot/tapping, weld size and stop-load capacity require fabrication/joint qualification.',
        switch_and_buffer_datums_changed=False,frame_mount_axes_changed=False,
        source_consistent_during_check=start==hashes(),fabrication_release=False)
    report['passed']=report['source_consistent_during_check']and all(c['passed']for c in checks.values())and all(c['valid']for c in exports.values())
    (OUT/'front-stop-repair-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],checks=checks),indent=2),flush=True)
    return 0 if report['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
