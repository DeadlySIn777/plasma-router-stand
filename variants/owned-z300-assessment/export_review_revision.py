"""Export the review candidate with both custom-joint and front-stop repairs.

This does not represent the unintegrated owner head or full HDPE/20100 bed.
Earlier exported proposals and their source/report files remain unchanged.
"""
from pathlib import Path
import csv,json,os,sys
import cadquery as cq
import export_candidate_assembly as E
import candidate_motion_factory as C
import front_stop_repair as F

S=E.S;R=E.R;HERE=E.HERE;ROOT=E.ROOT
OUT=HERE/'output/proposal-assemblies-v2'
PREFIX='Z300_WORK200_JOINT_AND_STOP_REPAIRED_REVIEW'

def run():
    evidence=[HERE/'output/z300-fit-decision.json',HERE/'output/custom-joint-repair-check.json',
              HERE/'output/front-stop-repair/front-stop-repair-check.json',
              HERE/'output/candidate-path-service-check.json',
              HERE/'output/candidate-external-sweep-check.json',
              HERE/'output/candidate-internal-continuous-check.json']
    upstream=[]
    for p in evidence:
        j=json.loads(p.read_text(encoding='utf-8'))
        assert j.get('passed'),p
        assert not E.check_sources(j),(p,E.check_sources(j))
        upstream.append(dict(file=p.relative_to(HERE).as_posix(),sha256=E.sha(p),passed=True))
    paths=list(dict.fromkeys([Path(__file__),Path(E.__file__),Path(C.__file__),Path(F.__file__),
                *R.sources(),*evidence,HERE/'output/owned-head-inspection.json']))
    hashes=lambda:{p.relative_to(ROOT).as_posix():E.sha(p)for p in paths}
    start=hashes();OUT.mkdir(parents=True,exist_ok=True)
    repair=json.loads(evidence[2].read_text(encoding='utf-8'))
    refs={n:cq.importers.importStep(str(HERE/q['file'])).val().translate(tuple(q['source_world_min_corner_mm']))
          for n,q in repair['outputs'].items()}
    report=dict(study='REVIEW_REVISION_WITH_CUSTOM_JOINT_AND_FRONT_STOP_REPAIRS',
        source_sha256=start,upstream_evidence=upstream,
        catalogue_module_stroke_mm=300,assessed_working_stroke_mm=200,
        pose_X_Yguide_Zlift_mm=[575,775,50],gantry_raise_mm=0,
        owned_clamp_boot_assembly_integrated=False,owner_HDPE_20100_bed_integrated=False,
        selected_for_fabrication=False,fabrication_release=False,operating_release=False,
        note='Nominal current proposal only. Source-valid scoped geometry proofs do not close the recovered owner head/bed requirements or actual supplier, strength and operating interfaces.',
        assemblies={},geometry_checks={})
    frame=S.frame_parts();assemblies={}
    for hot in (False,True):
        label='PLASMA'if hot else'WOOD'
        bed=S.bed_parts(hot);motion=C.motion_parts(hot,775,575,50);accessories=S.accessory_parts(hot)
        lookup={n:s for n,s,_ in motion}
        correspondence={n:lookup[n].cut(ref).Volume()+ref.cut(lookup[n]).Volume()for n,ref in refs.items()}
        custom_overlap=lookup['Z_CARRIER'].intersect(lookup['X_LINK_SUPPORT']).Volume()
        stop_overlaps={side:lookup[f'Y_STOP_{side}_FRONT_BRACKET'].intersect(lookup[f'HMS_Y_{side}_MOTOR_BRACKET']).Volume()for side in('L','R')}
        interfaces={k:S.exact_pairs(a,b)for k,a,b in[
            ('frame_bed',frame,bed),('frame_motion',frame,motion),('bed_motion',bed,motion),
            ('accessory_frame',accessories,frame),('accessory_bed',accessories,bed),('accessory_motion',accessories,motion)]}
        pieces=frame+bed+motion+accessories
        assert len(set(n for n,_,_ in pieces))==len(pieces)
        invalid=[n for n,s,_ in pieces if not s.isValid()or not s.Solids()or s.Volume()<=0]
        passed=not invalid and custom_overlap<1e-7 and all(v<1e-7 for v in stop_overlaps.values())and all(v<.05 for v in correspondence.values())and all(not g['unexpected']for g in interfaces.values())
        report['geometry_checks'][label]=dict(passed=passed,invalid_parts=invalid,
            front_stop_STEP_symmetric_difference_mm3=correspondence,
            custom_joint_overlap_mm3=custom_overlap,front_stop_motor_overlaps_mm3=stop_overlaps,
            six_external_group_display_checks=interfaces)
        assert passed,label
        assemblies[label]=pieces
        print(label,'review geometry checked',len(pieces),flush=True)
    for label,parts in assemblies.items():
        report['assemblies'][label]=E.export_step(parts,OUT/(PREFIX+'_'+label+'.step'))
        print(label,'STEP readback',report['assemblies'][label]['valid_STEP_readback'],flush=True)
    from preview import legacy
    for label,parts in assemblies.items():
        path=OUT/(PREFIX+'_'+label+'.png')
        legacy.render(parts,back=label=='PLASMA',w=1500,h=1250).save(path)
        report['assemblies'][label]['preview']=dict(file=path.relative_to(HERE).as_posix(),sha256=E.sha(path))
    csvpath=OUT/'proposal-components.csv'
    with csvpath.open('w',newline='',encoding='utf-8')as f:
        w=csv.writer(f);w.writerow(['assembly_identifier','component_id','solid_count'])
        for label,parts in assemblies.items():
            for n,s,_ in parts:w.writerow([PREFIX+'_'+label,n,len(s.Solids())])
    report['components_csv']=dict(file=csvpath.relative_to(HERE).as_posix(),sha256=E.sha(csvpath))
    report['source_consistent_during_build']=start==hashes()
    report['passed']=report['source_consistent_during_build']and all(q['passed']for q in report['geometry_checks'].values())and all(q['valid_STEP_readback']for q in report['assemblies'].values())
    (OUT/'candidate-assembly-v2-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],assemblies={k:dict(components=v['components'],solids=v['solid_count'])for k,v in report['assemblies'].items()})),flush=True)
    return 0 if report['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
