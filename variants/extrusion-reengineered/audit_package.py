"""Bind XR1 review artifacts to the current source and expose incomplete checks."""
from pathlib import Path
import hashlib,json,sys
import params as P

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'review'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    required=['build-check.json','travel-check.json','frame-self-check.json',
              'structure-screen.json','owned-stock-check.json','profile-nesting.json',
              'bed-screen.json','transfer-check.json','water-check.json',
              'bed-fabrication-metadata.json','frame-fabrication-metadata.json',
              'custom-parts-check.json','release-register.json','cam-reference-check.json',
              'shield-check.json','shield-manufacturing.json','service-check.json',
              'bed-manufacturing-check.json','atc-check.json','atc-manufacturing.json',
              'detail-views.json','steel-nesting.json','internal-continuous-check.json','atc-stiffness.json','atc-capacity-field-check.json','atc-tab-update-check.json']
    errors=[];reports={};stale=[]
    for n in required:
        p=OUT/n
        if not p.exists():errors.append('Missing '+n);continue
        reports[n]=json.loads(p.read_text(encoding='utf-8'))
    interface=HERE/'interface-audit.json'
    if interface.exists():reports['interface-audit.json']=json.loads(interface.read_text(encoding='utf-8'))
    else:errors.append('Missing interface-audit.json')
    for name,data in reports.items():
        hashes={**data.get('source_sha256',{}),**data.get('motion_source_closure_sha256',{})}
        for key,value in hashes.items():
            p=HERE/key
            if not p.exists():p=ROOT/key
            if not p.exists() or sha(p)!=value:stale.append({'report':name,'source':key})
    checks={}
    b=reports.get('build-check.json',{})
    checks['display_pose_external_intersections_clear']=b.get('display_pose_external_clash_free') is True
    checks['build_source_consistent']=b.get('source_consistent_during_build') is True
    for label,row in b.get('assemblies',{}).items():
        p=OUT/f'{P.REVISION}_{label}.step'
        checks[f'{label}_STEP_matches_roundtrip_report']=p.exists() and sha(p)==row.get('sha256')
    t=reports.get('travel-check.json',{}).get('states',{})
    checks['travel_source_consistent']=reports.get('travel-check.json',{}).get('source_consistent_during_check') is True
    checks['both_modes_external_rigid_sweeps_clear']=len(t)==2 and all(v.get('rigid_translation_clear') for v in t.values())
    checks['relative_motion_samples_clear_except_documented_threads']=len(t)==2 and all(v.get('relative_motion_samples_clear_except_nominal_threads') for v in t.values())
    internal=reports.get('internal-continuous-check.json',{})
    checks['relative_motion_continuous_with_cam_bounds']=set(internal.get('states',{}))=={'WOOD','PLASMA'} and internal.get('passed') is True and internal.get('source_consistent_during_check') is True
    f=reports.get('frame-self-check.json',{})
    checks['frame_self_clear']=f.get('parts')==b.get('assemblies',{}).get('FRAME',{}).get('components') and not f.get('invalid_parts',[True]) and not f.get('positive_intersections',[True])
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
    checks['bed_takeoff_uses_current_ownership_and_manufacturing']=all(
        (OUT/name).exists() and sha(OUT/name)==bed_meta.get(key)
        for name,key in [('owned-stock-check.json','owned_stock_report_sha256'),
                         ('bed-manufacturing-check.json','manufacturing_report_sha256')])
    motion_meta=reports.get('interface-audit.json',{})
    motion_csv=HERE/'motion-fabrication.csv'
    checks['motion_takeoff_matches_audit']=motion_csv.exists() and sha(motion_csv)==motion_meta.get('manufacturing_manifest_sha256')
    checks['targeted_motion_checks_passed']=motion_meta.get('targeted_checks_passed') is True and motion_meta.get('source_unchanged_during_check') is True
    custom=reports.get('custom-parts-check.json',{})
    checks['custom_STEP_roundtrips']=custom.get('passed') is True
    checks['custom_STEP_files_match_report']=bool(custom.get('parts')) and all((HERE/r['step']).is_file() and sha(HERE/r['step'])==r.get('step_sha256') for r in custom.get('parts',[]))
    checks['custom_reference_DXFs_match_report']=all((HERE/r['midsection_reference_dxf']).is_file() and sha(HERE/r['midsection_reference_dxf'])==r.get('midsection_reference_sha256') and r.get('midsection_reference_transform') for r in custom.get('parts',[]) if r.get('midsection_reference_dxf'))
    cam=reports.get('cam-reference-check.json',{})
    checks['CAM_reference_source_and_files']=cam.get('passed') is True and bool(cam.get('output_sha256')) and all((HERE/n).is_file() and sha(HERE/n)==h for n,h in cam.get('output_sha256',{}).items())
    checks['shield_self_frame_bed_motion_service']=reports.get('shield-check.json',{}).get('passed') is True
    def outputs_match(items):
        return bool(items) and all((HERE/str(n).replace('\\','/')).is_file() and sha(HERE/str(n).replace('\\','/'))==h for n,h in items.items())
    shield_files=reports.get('shield-manufacturing.json',{}).get('manufacturing_files',[])
    checks['shield_flat_and_STEP_files']=outputs_match({r['file']:r['sha256'] for r in shield_files})
    bed_mfg=reports.get('bed-manufacturing-check.json',{})
    checks['bed_joinery_and_flat_profiles']=bed_mfg.get('passed') is True and outputs_match(bed_mfg.get('output_sha256',{}))
    svc=reports.get('service-check.json',{})
    checks['receiver_hatch_and_replacement_service']=svc.get('passed') is True and svc.get('source_consistent_during_check') is True
    water=reports.get('water-check.json',{})
    checks['water_uses_current_service_evidence']=(OUT/'service-check.json').exists() and sha(OUT/'service-check.json')==water.get('service_report_sha256')
    atc=reports.get('atc-check.json',{})
    checks['ATC_mechanism_geometry']=atc.get('mechanism_geometry_pass') is True
    checks['ATC_source_consistent']=atc.get('source_consistent_during_check') is True
    checks['ATC_selected_Z_clearance_case']=atc.get('selectedZ_clearance_case_pass') is True
    atc_capacity=reports.get('atc-capacity-field-check.json',{})
    checks['parked_ATC_capacity_and_tool_vs_full_cutting_field']=atc_capacity.get('passed') is True and atc_capacity.get('source_consistent_during_check') is True
    atc_stiffness=reports.get('atc-stiffness.json',{})
    checks['ATC_pocket_field_component_screen']=atc_stiffness.get('passed') is True and atc_stiffness.get('source_consistent_during_check') is True
    tab=reports.get('atc-tab-update-check.json',{})
    checks['ATC_motor_tab_clearance_update']=tab.get('passed') is True and tab.get('source_consistent_during_check') is True
    atc_mfg=reports.get('atc-manufacturing.json',{})
    checks['ATC_manufacturing_files']=atc_mfg.get('passed') is True and atc_mfg.get('source_unchanged') is True and outputs_match(atc_mfg.get('output_sha256',{}))
    detail=reports.get('detail-views.json',{})
    checks['detail_views_current']=detail.get('rendered') is True and outputs_match({r['file']:r['sha256'] for r in detail.get('views',{}).values()})
    checks['joint_steel_blank_nest']=reports.get('steel-nesting.json',{}).get('passed') is True
    artifacts={p.relative_to(HERE).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)}
               for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='package-check.json'}
    result={'revision':P.REVISION,'digital_checks':checks,'missing':errors,'stale_sources':stale,
            'digital_review_pass':not errors and all(checks.values()),
            'artifacts':artifacts,'pricing_performed':False,'fabrication_release':False,
            'remaining_release_gates':['Exact magazine CAD/pocket/nut planes and final mating bolt pattern',
              'ZXHT80-200 base/output fixing details and brake-motor shaft/flange/coupler compatibility',
              'Actual extrusion die/slot, owned motion/guide/tool/torch geometry and delivered screw leads',
              'Material/glue/fastener properties, actual joint capacities and machining setup verification',
              'Assembled stiffness, dry foot contact/CG, retention and dynamic tests',
              'Physical water-flow, receiver capacity/load and protected-storage thermal tests',
              'Actual conversion and rare-service handling/support qualification',
              'Verified spindle/VFD/controller/cutter interfaces and loaded ATC operation',
              'Complete delivered quote against the1000USD cap; pricing remains paused'],
            'scope':'Digital checks are limited to their report scopes. This index is not a claim of complete machine qualification or a verified delivered budget.'}
    pdfs=[ROOT/'output'/'pdf'/name for name in
          (f'plasma-router-stand-{P.REVISION}-review.pdf',
           'plasma-router-stand-concept.pdf','plasma-router-stand-concept-before-XR2.pdf')]
    result['related_root_artifacts']={pdf.relative_to(ROOT).as_posix():{'bytes':pdf.stat().st_size,'sha256':sha(pdf)} for pdf in pdfs if pdf.exists()}
    (OUT/'package-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'digital_review_pass':result['digital_review_pass'],'failed':[n for n,v in checks.items() if not v],'missing':errors,'stale':stale},indent=2))
    return 0 if result['digital_review_pass'] else 1

if __name__=='__main__':sys.exit(run())
