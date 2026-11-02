"""Export/check the exact owner clamp integration and explicit boot registration."""
from pathlib import Path
import csv,json,os,sys
import cadquery as cq
import owner_head as H

HERE=H.HERE;ROOT=H.ROOT;OUT=HERE/'output'

def no_overlap(a,b):
    if not H.S.overlap(H.bounds(a),H.bounds(b)):return 0.
    return abs(a.intersect(b).Volume())

def export(parts,path):
    asm=cq.Assembly(name=path.stem)
    for n,s,c in parts:asm.add(s,name=n,color=cq.Color(*c))
    asm.save(str(path));back=cq.importers.importStep(str(path)).val()
    expected=sum(s.Volume()for _,s,_ in parts)
    return dict(file=path.relative_to(HERE).as_posix(),sha256=H.sha(path),
        valid=back.isValid(),solid_count=len(back.Solids()),expected_solid_count=sum(len(s.Solids())for _,s,_ in parts),
        volume_error_mm3=abs(back.Volume()-expected),bounds_mm=H.bounds(back),
        preserved_source_entity_graph=False,geometry_is_rigidly_transformed_owner_solids=True)

def head_relative_proof(parts,obstacles,z_working_travel=200.):
    """Exact continuous translation-cover proof for the known rigid head."""
    results=[];broad=0
    for n,s,c in parts:
        for nf,sf,cf in obstacles:
            ff=H.S.FACTORS[H.S.cls(nf)]
            span=(400.,500.,z_working_travel/2)
            lo=[-(1-ff[k])*span[k]for k in range(3)]
            hi=[(1-ff[k])*span[k]for k in range(3)]
            if nf in H.S.FOLLOWERS:hi[2]+=3.17657258
            b=H.bounds(s);sweep=[b[k]+lo[k]for k in range(3)]+[b[k+3]+hi[k]for k in range(3)]
            if not H.S.overlap(sweep,H.bounds(sf)):broad+=1;continue
            q=H.S.translation_cover_proof(s,sf,lo,hi)
            results.append(dict(head_part=n,obstacle=nf,**q))
    return dict(passed=all(r['passed']for r in results),working_Z_travel_mm=z_working_travel,
        broad_pairs_clear=broad,exact_cover_pairs=len(results),results=results)

def run():
    OUT.mkdir(exist_ok=True)
    hashes=lambda:{p.relative_to(ROOT).as_posix():H.sha(p)for p in H.sources()}
    start=hashes();known=H.actual_head_parts(include_boot=False);illustrated=H.actual_head_parts()
    invalid=[n for n,s,c in illustrated if not s.isValid()or len(s.Solids())!=1]
    overlaps=[]
    for i,(n,s,c)in enumerate(illustrated):
        for nf,sf,cf in illustrated[i+1:]:
            v=no_overlap(s,sf)
            if v>.02:overlaps.append(dict(a=n,b=nf,volume_mm3=v))
    adapter=known[0][1];clamp=known[1][1];lookup={n:s for n,s,c in known};joints=[]
    for i,dx in enumerate(H.MOUNT_X):
        for k,z in enumerate(H.MOUNT_Z):
            x=575+dx;mount=H.ADAPTER_FRONT_Y_AT_REFERENCE-H.SPACER_LENGTH
            seat=mount-H.WALL
            # 0.05 mm thin material sections immediately inside each mating face.
            ring=lambda d,inside,y:H.cyl(d,.05,(x,y,z)).cut(H.cyl(inside,.15,(x,y-.05,z)))
            a=ring(10,5.5,H.ADAPTER_FRONT_Y_AT_REFERENCE)
            b=ring(10,5.5,mount-.05)
            washer=lookup[f'OWNER_CLAMP_M5_SPREADER_{i+1}_{k+1}']
            c=ring(8.5,5.3,seat-1)
            washer_seat=ring(10,5.3,seat)
            missing=washer_seat.cut(clamp).Volume()
            shell=H.cyl(9,25-H.WALL-H.SPACER_LENGTH-1,(x,H.ADAPTER_FRONT_Y_AT_REFERENCE,z)).cut(
                H.cyl(5,14.7,(x,H.ADAPTER_FRONT_Y_AT_REFERENCE-1,z)))
            joints.append(dict(X=x,Z=z,adapter_spacer_seat_missing_mm3=a.cut(adapter).Volume(),
                clamp_spacer_seat_missing_mm3=b.cut(clamp).Volume(),
                bolt_head_on_spreader_missing_mm3=c.cut(washer).Volume(),
                spreader_contact_fraction=1-missing/washer_seat.Volume(),
                spreader_contact_missing_mm3=missing,
                D9_thread_landing_shell_missing_mm3=shell.cut(adapter).Volume()))
    # Contact area is evidence for the subsequent strength/preload check, not
    # an invented fit tolerance. The spreader supports the entire screwhead;
    # its own partial bearing on the original seat remains explicitly held.
    joint_ok=all(abs(v)<.02 for r in joints for k,v in r.items()if k.endswith('_mm3')and k!='spreader_contact_missing_mm3')
    local=adapter.translate((-520,-666.9,-1070))
    partpath=OUT/'OWNER_CLAMP_ADAPTER110_WITH_M5_ROWS.step';cq.exporters.export(local,str(partpath))
    back=cq.importers.importStep(str(partpath)).val()
    part=dict(file=partpath.relative_to(HERE).as_posix(),sha256=H.sha(partpath),valid=back.isValid(),
        bounds_mm=H.bounds(back),solid_count=len(back.Solids()),volume_error_mm3=abs(back.Volume()-local.Volume()))
    known_export=export(known,OUT/'EXACT_OWNER_CLAMP_ON_Z_ADAPTER.step')
    reference_export=export(illustrated,OUT/'OWNER_HEAD_WITH_UNREGISTERED_BOOT_REFERENCE.step')
    common=[p for p in H.C.motion_parts(False,775,575,100)if p[0]!='TOOL_ADAPTER_110'and not p[0].startswith(H.REMOVED_PREFIXES)]
    relative=head_relative_proof(H.actual_head_parts(z_lift=100,include_boot=False),common)
    # Original body dimensions are verified from the unchanged imported owner solid.
    source_clamp=cq.importers.importStep(str(H.CLAMP)).val()
    source_boot=cq.importers.importStep(str(H.BOOT)).val()
    preservation=dict(clamp_faces=[len(source_clamp.Faces()),len(clamp.Faces())],
        clamp_volume_error_mm3=abs(source_clamp.Volume()-clamp.Volume()),
        boot_faces=[len(source_boot.Faces()),len(illustrated[-1][1].Faces())],
        boot_volume_error_mm3=abs(source_boot.Volume()-illustrated[-1][1].Volume()),
        original_files_modified=False)
    meta=H.metadata()
    with(OUT/'head-requirements.csv').open('w',newline='',encoding='utf-8')as f:
        w=csv.writer(f);w.writerow(['item','qty','ownership','specification','new_purchase_quantity','qualification'])
        w.writerows([
            ['Original65mmclamp complete with existing pinch hardware',1,'OWNED','Exact supplied STEP; no relief or split-clamp substitution',0,'Original working owner assembly preserved'],
            ['Original whole boot and existing actuator arrangement',1,'OWNED','PegelongB0D6BCQCVR50mm; preserve boot/brush groove/working assembly',0,'Installed machine registration remains unencoded'],
            ['Spindle/VFD kit',1,'OWNED','ZhongHuaJiang65mm1.5kWER11 B0BF5R3LNC',0,'Exact nose/collet/gripping datums not in supplied body STEP'],
            ['Removable adapter finished blank',1,'NEW_OR_REALLOCATE_OWNED_STOCK','110x110x12.7mm; retain existing features and add4M5x0.8custom taps',1,'No owned material credit until parent nonoverlapping nest'],
            ['Equal spacer rings',4,'NEW_OR_REALLOCATE_OWNED_STOCK','10OD5.5ID6longmm; equal length and square ends',4,'Could be cut from suitable available tube/round stock; no source assumed'],
            ['M5x25 socket head',4,'NEW_UNLESS_VERIFIED_OWNED','Nominal8.5ODx5head,25underhead;10.998mmengagement',4,'Actual fastener grade/thread fit/load qualification'],
            ['Steel M5 spreaderwasher',4,'NEW_UNLESS_VERIFIED_OWNED','10OD5.3ID1thick200HVsteel;fits source10.5counterbore',4,'Full screwhead bearing; washer source-seat contact96.996% for3 and86.963% for1; actual bridge/preload capacity remains held']])
    import ezdxf
    coordinates=[(575+dx-520,z-1070)for dx in H.MOUNT_X for z in H.MOUNT_Z]
    doc=ezdxf.new('R2010');doc.units=4
    doc.layers.new('REFERENCE_OUTLINE');doc.layers.new('NEW_4P2_PILOTS')
    space=doc.modelspace()
    space.add_lwpolyline([(0,0),(110,0),(110,110),(0,110)],close=True,dxfattribs={'layer':'REFERENCE_OUTLINE'})
    for x,z in coordinates:space.add_circle((x,z),2.1,dxfattribs={'layer':'NEW_4P2_PILOTS'})
    dxf=OUT/'ADAPTER_FOUR_NEW_M5_PILOTS_OPERATION_ONLY.dxf';doc.saveas(dxf)
    readback=ezdxf.readfile(dxf)
    actual=[(round(e.dxf.center.x,8),round(e.dxf.center.y,8),round(e.dxf.radius*2,8))for e in readback.modelspace().query('CIRCLE[layer=="NEW_4P2_PILOTS"]')]
    expected=[(x,z,4.2)for x,z in coordinates]
    assert sorted(actual)==sorted(expected)
    csvpath=OUT/'adapter-new-hole-coordinates.csv'
    with csvpath.open('w',newline='',encoding='utf-8')as f:
        w=csv.writer(f);w.writerow(['X_from_left_mm','Z_from_lower_mm','pilot_diameter_mm','thread','operation_scope'])
        w.writerows([[x,z,4.2,'M5x0.8','New custom adapter operations only; retain all other STEP features; OEM output transfer-drilled']for x,z in coordinates])
    report=dict(study='ACTUAL_OWNER_CLAMP_CUSTOM_ADAPTER_INTEGRATION',metadata=meta,
        source_sha256=start,invalid_parts=invalid,illustrated_registration_static_overlaps=overlaps,
        exact_four_mount_seat_and_landing_checks=joints,known_adapter_joint_passed=joint_ok,
        spreader_qualification='The complete8.5mm screwhead is supported by a10mm steelwasher. Washer/clamp contact is96.996% for three and86.963% for one: all have the5.3-to5.5inner-bore lip, and the fourth retains an outer source-seat interruption. Contactfraction is reported without an invented acceptance threshold. Actual preload, steelgrade and washerbridge capacity remain unqualified.',
        washer_bridge_or_bearing_strength_qualified=False,
        source_geometry_preservation=preservation,
        known_clamp_adapter_relative_continuous_motion=relative,
        adapter_STEP=part,known_head_STEP=known_export,unregistered_boot_reference_STEP=reference_export,
        new_tap_operation_DXF=dict(file=dxf.relative_to(HERE).as_posix(),sha256=H.sha(dxf),
            passed=sorted(actual)==sorted(expected),readback_holes=actual,outer_layer_is_reference_only=True),
        new_tap_coordinate_CSV=dict(file=csvpath.relative_to(HERE).as_posix(),sha256=H.sha(csvpath)),
        boot_home_registration_known=False,full_working_boot_50mm_proved=False,
        missing_installed_datums=['Working boot home relative to the unmodified clamp','Spindle collet/nose datum relative to clamp grip','Actual received Z output mounting pattern/depth and thickness'],
        owner_identity_questions_already_answered=['Clamp matches original-uncutSTEP','Whole boot moves50mm','PegelongB0D6BCQCVR','Existing assembly already works'],
        conservative_boot_handling='Factory refuses nonzero boot_lift without an explicit registration. Include the exact boot at its labeled reference pose, or use a measured registration; never treat the earlier inferred joint as qualified.',
        complete_head_machine_integration=False,fabrication_release=False,operating_release=False)
    report['source_consistent_during_check']=start==hashes()
    report['known_clamp_adapter_integration_passed']=(not invalid and not overlaps and joint_ok and relative['passed']and part['valid']and known_export['valid']and reference_export['valid']and report['source_consistent_during_check'])
    report['inspection_and_export_completed']=True
    (OUT/'head-integration-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(known_clamp_adapter_integration_passed=report['known_clamp_adapter_integration_passed'],joints=joints,
        continuous_relative=relative['passed'],boot_registered=False,invalid=invalid,overlaps=overlaps)),flush=True)
    return 0 if report['known_clamp_adapter_integration_passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
