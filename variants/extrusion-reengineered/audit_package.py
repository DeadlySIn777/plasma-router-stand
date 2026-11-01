"""Bind XR1 review artifacts to the current source and expose incomplete checks."""
from pathlib import Path
import hashlib,json,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'review'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    required=['build-check.json','travel-check.json','frame-self-check.json',
              'structure-screen.json','owned-stock-check.json','profile-nesting.json',
              'bed-screen.json','transfer-check.json','water-check.json',
              'bed-fabrication-metadata.json','frame-fabrication-metadata.json']
    errors=[];reports={};stale=[]
    for n in required:
        p=OUT/n
        if not p.exists():errors.append('Missing '+n);continue
        reports[n]=json.loads(p.read_text(encoding='utf-8'))
    interface=HERE/'interface-audit.json'
    if interface.exists():reports['interface-audit.json']=json.loads(interface.read_text(encoding='utf-8'))
    else:errors.append('Missing interface-audit.json')
    for name,data in reports.items():
        hashes=data.get('source_sha256',{})
        for key,value in hashes.items():
            p=HERE/key
            if not p.exists():p=ROOT/key
            if not p.exists() or sha(p)!=value:stale.append({'report':name,'source':key})
    checks={}
    b=reports.get('build-check.json',{})
    checks['display_pose_external_intersections_clear']=b.get('display_pose_external_clash_free') is True
    checks['build_source_consistent']=b.get('source_consistent_during_build') is True
    for label,row in b.get('assemblies',{}).items():
        p=OUT/f'XR1_{label}.step'
        checks[f'{label}_STEP_matches_roundtrip_report']=p.exists() and sha(p)==row.get('sha256')
    t=reports.get('travel-check.json',{}).get('states',{})
    checks['travel_source_consistent']=reports.get('travel-check.json',{}).get('source_consistent_during_check') is True
    checks['both_modes_external_rigid_sweeps_clear']=len(t)==2 and all(v.get('rigid_translation_clear') for v in t.values())
    checks['relative_motion_samples_clear_except_documented_threads']=len(t)==2 and all(v.get('relative_motion_samples_clear_except_nominal_threads') for v in t.values())
    f=reports.get('frame-self-check.json',{})
    checks['frame_self_clear']=f.get('parts')==89 and not f.get('invalid_parts',[True]) and not f.get('positive_intersections',[True])
    for name,key in [('owned-stock-check.json','owned_plate_nesting'),('profile-nesting.json','profile_cut_nesting'),('bed-screen.json','conditional_bed_component_screen'),('transfer-check.json','bed_transfer_clear_within_report_scope'),('water-check.json','conditional_water_volume_allowance')]:
        checks[key]=reports.get(name,{}).get('passed') is True
    for n in ['frame-fabrication.csv','bed-fabrication.csv','components.csv','overview.png']:
        checks[n+'_present']=(OUT/n).is_file()
    for n in ['motion-fabrication.csv','INTERFACES.md','BED.md','WATER.md','ATC-INTERFACE.md','AUDIT.md']:
        checks[n+'_present']=(HERE/n).is_file()
    checks['recorded_source_hashes_current']=not stale
    bed_meta=reports.get('bed-fabrication-metadata.json',{})
    bed_csv=OUT/'bed-fabrication.csv'
    checks['bed_takeoff_matches_metadata']=bed_csv.exists() and sha(bed_csv)==bed_meta.get('csv_sha256')
    motion_meta=reports.get('interface-audit.json',{})
    motion_csv=HERE/'motion-fabrication.csv'
    checks['motion_takeoff_matches_audit']=motion_csv.exists() and sha(motion_csv)==motion_meta.get('manufacturing_manifest_sha256')
    checks['targeted_motion_checks_passed']=motion_meta.get('targeted_checks_passed') is True and motion_meta.get('source_unchanged_during_check') is True
    artifacts={p.relative_to(HERE).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)}
               for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='package-check.json'}
    result={'revision':'XR1','digital_checks':checks,'missing':errors,'stale_sources':stale,
            'digital_review_pass':not errors and all(checks.values()),
            'artifacts':artifacts,'pricing_performed':False,'fabrication_release':False,
            'remaining_release_gates':['Actual supplier interfaces and delivered lead',
              'Complete mounted heat shields and reservoir service hatch/removal path',
              'Final eggcrate/flat-pattern machining and bend/joinery details',
              'Extrusion die/slot and joint capacity', 'Measured tool/torch reach and Z retention',
              'Assembled stiffness, foot contact/CG and dynamic tests',
              'Physical water-flow and protected-storage thermal tests',
              'Retractable ATC integration using the actual kit and Z stack'],
            'scope':'Digital checks are limited to their report scopes. This index is not a claim of complete machine qualification or a verified delivered budget.'}
    pdf=ROOT/'output'/'pdf'/'plasma-router-stand-XR1-review.pdf'
    if pdf.exists():result['related_root_artifacts']={pdf.relative_to(ROOT).as_posix():{'bytes':pdf.stat().st_size,'sha256':sha(pdf)}}
    (OUT/'package-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'digital_review_pass':result['digital_review_pass'],'failed':[n for n,v in checks.items() if not v],'missing':errors,'stale':stale},indent=2))
    return 0 if result['digital_review_pass'] else 1

if __name__=='__main__':sys.exit(run())
