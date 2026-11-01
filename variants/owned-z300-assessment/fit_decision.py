"""Separate the selected nominal fit decision from nonselected optional studies."""
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=HERE/'output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    path=OUT/'z300-fit-study.json';data=json.loads(path.read_text(encoding='utf-8'))
    current=all((ROOT/n).is_file() and sha(ROOT/n)==h for n,h in data['source_sha256'].items())
    selected=data['cases']['Z300_STOCK_EXISTING_CARRIER']
    brake=data['cases']['Z300_OPTIONAL_BRAKE']
    rejected=data['cases']['Z300_OPTIONAL_EXTENDED_CARRIER']
    contact_path=OUT/'extension-contact-disposition.json'
    contact=json.loads(contact_path.read_text(encoding='utf-8'))
    contact_current=all((ROOT/n).is_file() and sha(ROOT/n)==h for n,h in contact['source_sha256'].items())
    exact_material=contact['optional_carrier_exact_STEP_material']
    carrier_comparison={**data['carrier_comparison'],
        'raw_render_bound_mass_proxy_kg':data['carrier_comparison']['optional_added_nominal_Al_kg'],
        'optional_added_nominal_Al_kg':exact_material['optional_added_nominal_Al_kg'],
        'optional_added_exact_STEP_material_mm3':exact_material['added_material_volume_mm3'],
        'mass_basis':'Exact imported STEP carrier material addition at nominal2700kg/m3; raw render-bound proxy retained only for traceability.'}
    primary_names=('Z200_STOCK','Z300_STOCK_EXISTING_CARRIER','Z300_OPTIONAL_BRAKE')
    outputs={data['outputs'][n]['file']:data['outputs'][n]['sha256']for n in primary_names}
    pic=data['comparison_image'];outputs[pic['file']]=pic['sha256']
    file_match=all((HERE/n).is_file() and sha(HERE/n)==h for n,h in outputs.items())
    unexpected=[]
    for mode,m in rejected['modes'].items():
        for s in m['whole_changed_part_samples']:
            for group in ('cross','changed_self'):
                unexpected.extend(dict(mode=mode,pose=s['pose_X_Yguide_Zlift_mm'],**r)for r in s[group]['unexpected'])
    result=dict(
        decision='RETAIN_EXISTING_CARRIER_FOR_NOMINAL_OWNED_300_MM_FIT_STUDY',
        passed=bool(data['source_consistent_during_check'] and current and contact_current and exact_material['verified'] and selected['passed'] and file_match and all(data['outputs'][n]['valid']for n in primary_names)),
        primary_bulk_fit_pass=selected['passed'],
        optional_unowned_brake_bulk_fit_pass=brake['passed'],
        proposed_gantry_raise_mm=0,
        assessed_working_travel_mm=200,owned_catalog_stroke_mm=300,
        full_300_mm_operating_domain_qualified=False,
        actual_mounting_support_capacity_verified=False,
        actual_stage_mass_kg=None,
        carrier_comparison=carrier_comparison,
        height_comparison_mm=data['height_comparison_mm'],
        nonselected_optional_extension=dict(raw_whole_part_screen_pass=rejected['passed'],invalid_parts=rejected['invalid'],
            unexpected_sample_count=len(unexpected),first_unexpected_samples=unexpected[:4],
            contact_was_preexisting=contact['unchanged_overlap'],
            added_material_contact_mm3=contact['added_material_overlap_mm3'],
            new_collision_demonstrated=not contact['unchanged_overlap'],
            selected=False,reason='Unnecessary larger carrier. The raw whole-part screen flags a real inherited custom-part clash; exact comparison proves the300mm overlay did not cause it. The separate carrier relief/support repair is required before fabrication. No larger carrier is required by this bulk-fit study.'),
        source_consistent_during_check=current and contact_current and data['source_consistent_during_check'],
        source_sha256={str(path.relative_to(ROOT)).replace('\\','/'):sha(path),
            str(contact_path.relative_to(ROOT)).replace('\\','/'):sha(contact_path),
            str(Path(__file__).resolve().relative_to(ROOT)).replace('\\','/'):sha(Path(__file__))},
        study_source_sha256=data['source_sha256'],
        output_sha256=outputs,
        scope='Nominal incremental material/bulk clearance on frozen XR2 over the existing200mm working box. Existing carrier blank retained; no whole-gantry raise, new OEM holes or inferred support rating. This does not clear the inherited custom-part interference; a separate repair is required. Actual received geometry, mass, mounting, rigidity, retention and commissioning remain open.',
        fabrication_release=False,physical_rigidity_qualified=False)
    target=OUT/'z300-fit-decision.json';target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k]for k in ('passed','primary_bulk_fit_pass','optional_unowned_brake_bulk_fit_pass','source_consistent_during_check')},indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(run())
