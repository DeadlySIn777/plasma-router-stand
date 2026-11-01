"""Export full machine proposals using the owned-family Z300 and joint repair.

The actual module's catalogue stroke is300mm; only the inherited200mm working
box has fit-study evidence. These are review assemblies, not machine releases.
The frozen XR2 geometry and the earlier raw fit study remain unchanged.
"""
from pathlib import Path
import csv,hashlib,json,os,sys
import cadquery as cq
import z300_fit_study as S
import custom_joint_repair as R

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=HERE/'output'/'proposal-assemblies'
ASSEMBLY_PREFIX='Z300_STOCK_WORK200_CUSTOM_JOINT_PROPOSAL'
REPAIR_IDS={'Z_CARRIER','X_LINK_SUPPORT'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check_sources(data):
    hashes={**data.get('source_sha256',{}),**data.get('study_source_sha256',{})}
    failures=[]
    for n,h in hashes.items():
        p=ROOT/n
        if not p.is_file()or sha(p)!=h:failures.append(n)
    return failures

def output_paths(data):
    result={}
    for row in data.get('outputs',{}).values():
        if isinstance(row,dict)and row.get('file'):result[row['file']]=row['sha256']
    result.update(data.get('output_sha256',{}))
    return result

def export_step(parts,path):
    expected_count=sum(len(s.Solids())for _,s,_ in parts)
    expected_volume=sum(s.Volume()for _,s,_ in parts)
    boxes=[S.bounds(s)for _,s,_ in parts]
    expected_bounds=[min(b[k]for b in boxes)for k in range(3)]+[max(b[k+3]for b in boxes)for k in range(3)]
    assembly=cq.Assembly(name=path.stem)
    for n,s,c in parts:assembly.add(s,name=n,color=cq.Color(*c))
    assembly.save(str(path))
    imported=cq.importers.importStep(str(path)).val()
    imported_bounds=S.bounds(imported)
    volume_error=abs(imported.Volume()-expected_volume)
    bbox_error=max(abs(a-b)for a,b in zip(imported_bounds,expected_bounds))
    valid=(imported.isValid()and len(imported.Solids())==expected_count and
        volume_error<max(.5,expected_volume*1e-7)and bbox_error<1e-4)
    return dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),
        assembly_identifier=path.stem,components=len(parts),solid_count=expected_count,
        valid_STEP_readback=valid,native_component_volume_sum_mm3=expected_volume,
        imported_component_volume_sum_mm3=imported.Volume(),
        roundtrip_volume_error_mm3=volume_error,roundtrip_bbox_error_mm=bbox_error,
        bounds_mm=imported_bounds,
        volume_scope='Sum of nominal component solids for format fidelity; not physical material mass or a union volume.')

def run():
    assert callable(getattr(R,'apply_repairs',None)),'Wait for frozen repair API before running.'
    repair_path=HERE/'output'/'custom-joint-repair-check.json'
    fit_path=HERE/'output'/'z300-fit-decision.json'
    repair=json.loads(repair_path.read_text(encoding='utf-8'))
    fit=json.loads(fit_path.read_text(encoding='utf-8'))
    assert repair.get('passed')and repair.get('source_consistent_during_check'), 'Repair evidence must pass and be frozen.'
    assert fit.get('passed')and fit.get('source_consistent_during_check'), 'Owned-family bulk-fit decision must pass.'
    upstream_errors={label:check_sources(data)for label,data in [('repair',repair),('bulk_fit',fit)]}
    upstream_outputs={label:[n for n,h in output_paths(data).items()if not(HERE/n).is_file()or sha(HERE/n)!=h]
        for label,data in [('repair',repair),('bulk_fit',fit)]}
    assert not any(upstream_errors.values())and not any(upstream_outputs.values()),(upstream_errors,upstream_outputs)
    paths=[Path(__file__),Path(S.__file__),Path(R.__file__),repair_path,fit_path]
    paths+=R.sources()
    paths+=[HERE/n for n in output_paths(repair)]
    paths=list(dict.fromkeys(paths))
    hashes=lambda:{p.relative_to(ROOT).as_posix():sha(p)for p in paths}
    start=hashes();OUT.mkdir(parents=True,exist_ok=True)
    frame=S.frame_parts();assemblies={};report=dict(
        study='FULL_REVIEW_PROPOSALS_WITH_OWNED_FAMILY_Z300_AND_CUSTOM_JOINT_REPAIR',
        catalogue_module_stroke_mm=300,assessed_working_stroke_mm=200,
        actual_delivered_module_identity_and_interfaces_verified=False,
        optional_brake_installed=False,gantry_raise_mm=0,
        proposal_pose_X_Yguide_Zlift_mm=[575,775,50],
        source_sha256=start,upstream_evidence=dict(
            bulk_fit=dict(file=fit_path.relative_to(HERE).as_posix(),sha256=sha(fit_path),passed=fit['passed']),
            custom_joint_repair=dict(file=repair_path.relative_to(HERE).as_posix(),sha256=sha(repair_path),passed=repair['passed'])),
        assemblies={},interface_checks={},repair_export_correspondence={},
        fabrication_release=False,operating_release=False,physical_rigidity_qualified=False,
        frozen_XR2_modified=False,earlier_raw_fit_study_modified=False)
    repaired_reference={}
    for label in ('carrier','support'):
        r=repair['outputs'][label]
        local=cq.importers.importStep(str(HERE/r['file'])).val()
        repaired_reference['Z_CARRIER'if label=='carrier'else'X_LINK_SUPPORT']=local.translate(tuple(r['source_world_min_corner_mm']))
    for hot in(False,True):
        label='PLASMA'if hot else'WOOD'
        bed=S.bed_parts(hot);accessories=S.accessory_parts(hot)
        original=S.M.motion_parts(hot,775.,575.,50.)
        owned=S.overlay(original,extended_carrier=False)
        repaired=R.apply_repairs(owned)
        assert [n for n,_,_ in repaired]==[n for n,_,_ in owned], 'Repair API must preserve IDs and ordering.'
        source={n:(s,c)for n,s,c in owned};changed=[]
        for n,s,c in repaired:
            if s is not source[n][0]:changed.append(n)
            assert c==source[n][1],n
        assert set(changed)==REPAIR_IDS,changed
        correspondence={}
        for n,s,_ in repaired:
            if n not in REPAIR_IDS:continue
            ref=repaired_reference[n]
            difference=s.cut(ref).Volume()+ref.cut(s).Volume()
            correspondence[n]=dict(symmetric_difference_from_verified_repair_STEP_mm3=difference,passed=difference<.05)
        report['repair_export_correspondence'][label]=correspondence
        pieces=frame+bed+repaired+accessories
        assert len({n for n,_,_ in pieces})==len(pieces), 'Duplicate proposal component IDs.'
        invalid=[n for n,s,_ in pieces if not s.isValid()or not s.Solids()or s.Volume()<=0]
        native_multi=[dict(id=n,solid_count=len(s.Solids()))for n,s,_ in pieces if len(s.Solids())>1]
        interfaces={k:S.exact_pairs(a,b)for k,a,b in
            [('frame_bed',frame,bed),('frame_motion',frame,repaired),('bed_motion',bed,repaired),
             ('accessory_frame',accessories,frame),('accessory_bed',accessories,bed),
             ('accessory_motion',accessories,repaired)]}
        lookup={n:s for n,s,_ in repaired}
        joint_overlap=lookup['Z_CARRIER'].intersect(lookup['X_LINK_SUPPORT']).Volume()
        report['interface_checks'][label]=dict(groups=interfaces,
            repaired_custom_joint_intersection_mm3=joint_overlap,
            invalid_parts=invalid,inherited_multisolid_component_allocations=native_multi,
            passed=not invalid and joint_overlap<1e-7 and all(not g['unexpected']for g in interfaces.values())
                and all(r['passed']for r in correspondence.values()))
        assemblies[label]=pieces
        print(label,'display interfaces clear',report['interface_checks'][label]['passed'],
            'components',len(pieces),'customjoint',joint_overlap,flush=True)
    # Finish all geometry checks and STEP readback before any VTK tessellation.
    for label,pieces in assemblies.items():
        report['assemblies'][label]=export_step(pieces,OUT/(ASSEMBLY_PREFIX+'_'+label+'.step'))
        print('Exported',label,report['assemblies'][label]['solid_count'],flush=True)
    from preview import legacy
    for label,pieces in assemblies.items():
        image=legacy.render(pieces,back=label=='PLASMA',w=1500,h=1250)
        path=OUT/(ASSEMBLY_PREFIX+'_'+label+'.png');image.save(path)
        report['assemblies'][label]['preview']=dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path))
    report['source_consistent_during_build']=start==hashes()
    report['source_sha256']=hashes()
    report['passed']=(report['source_consistent_during_build']and
        all(x['passed']for x in report['interface_checks'].values())and
        all(x['valid_STEP_readback']for x in report['assemblies'].values()))
    report['scope']='Full nominal display assemblies with valid solids and STEP readback, six external group checks at the stated pose, and exact correspondence to the verified two-part repair. Working200 bulk-fit and incremental repair evidence is linked separately. Existing source limits, supplier interfaces, any other inherited internal contacts, flexible routing, actual support/strength and commissioning remain open. No full300 operating domain or machine release is asserted.'
    with(OUT/'proposal-components.csv').open('w',newline='',encoding='utf-8')as f:
        w=csv.writer(f);w.writerow(['assembly_identifier','component_id','solid_count'])
        for label,pieces in assemblies.items():
            for n,s,_ in pieces:w.writerow([ASSEMBLY_PREFIX+'_'+label,n,len(s.Solids())])
    report['components_csv']=dict(file=(OUT/'proposal-components.csv').relative_to(HERE).as_posix(),sha256=sha(OUT/'proposal-components.csv'))
    target=OUT/'candidate-assembly-check.json';target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],source_consistent=report['source_consistent_during_build'],
        assemblies={k:dict(components=v['components'],solids=v['solid_count'],bounds=v['bounds_mm'])for k,v in report['assemblies'].items()}),indent=2),flush=True)
    return 0 if report['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
