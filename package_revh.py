"""Check the current Rev H inventory and regenerate its material layouts.

Run after the assembly exporter completes. This does not publish to GitHub,
copy workspace mirrors, or change any historical CAD package.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
CAD=ROOT/'output/release-review/RevH-CAD'
EVIDENCE=ROOT/'output/design-completion-2026-09-26'
sys.path.insert(0,str(SOURCE))


def main():
    manifest=json.loads((CAD/'engineering-manifest.json').read_text(encoding='utf-8'))
    assert manifest['integrated_geometry_pass']
    for name,digest in manifest['source_sha256'].items():
        assert hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()==digest, name
    rows=json.loads((CAD/'cutlist.json').read_text(encoding='utf-8-sig'))
    operations=json.loads((CAD/'part-operations.json').read_text(encoding='utf-8'))
    validation=json.loads((CAD/'RevH_ROUTER-validation.json').read_text(encoding='utf-8'))
    panel_mass=[0.0]*6
    panel_members=[[] for _ in range(6)]
    for part in validation['parts']:
        if part['group']!='bed_panel':
            continue
        match=re.match(r'(?:G_PANEL_|H_NUT_STRIP_(?:SET_)?)([1-6])_',part['id'])
        assert match, 'Unassigned panel part: '+part['id']
        material=part['material'].lower()
        density=(7.85e-6 if 'steel' in material else 2.7e-6
                 if 'alum' in material or '6063' in material else None)
        assert density is not None, 'Unclassified panel material: '+part['material']
        index=int(match.group(1))-1
        panel_mass[index]+=part['volume_mm3']*density
        panel_members[index].append(part['id'])
    assert all(panel_members)
    assert {r['part_number'] for r in rows}=={r['part_number'] for r in operations}
    expected_parts={r['part_number']+'.step' for r in rows if not r['individual_export_guarded']}
    expected_flats={r['part_number']+'.dxf' for r in operations
                    if r['manufacturing_flat'] and not r['individual_export_guarded']}
    assert expected_parts=={p.name for p in (CAD/'parts').glob('*.step')}, 'Missing or stale individual STEP files'
    assert expected_flats=={p.name for p in (CAD/'dxf').glob('*.dxf')}, 'Missing or stale flat DXFs'
    import plan_tube_cuts
    plan_tube_cuts.ROOT=CAD
    plan_tube_cuts.main()
    plan=json.loads((CAD/'tube-cut-plan.json').read_text(encoding='utf-8'))
    assert plan['part_count']==30 and abs(plan['net_length_mm']-29472)<.01
    # A scrap shopping reference is not a direction to buy full retail bars.
    path=CAD/'TUBE-CUT-PLAN.md'
    text=path.read_text(encoding='utf-8').replace(
        'Buy 5 full 20-foot bars for 30 modeled blanks.',
        'Reference nest: 5 full 20-foot bars supply the 30 modeled blanks.\n\nThe owner is sourcing scrap. Use actual sound lengths and remaining wall thickness before assigning cuts; this full-bar nest does not predict scrap yield or price.')
    path.write_text(text,encoding='utf-8')
    import nest_flat_parts
    nest_flat_parts.ROOT=CAD
    nest_flat_parts.OUT=CAD/'nesting'
    nest_flat_parts.main()
    report={
        'revision':'Rev H',
        'source_hashes_current':True,
        'assembly_parts':sum(r['quantity'] for r in rows),
        'part_numbers':len(rows),
        'individual_step_files':len(expected_parts),
        'flat_dxf_files':len(expected_flats),
        'no_missing_or_stale_individual_files':True,
        'tube_blanks':plan['part_count'],
        'tube_net_length_mm':plan['net_length_mm'],
        'full_20ft_reference_bar_count':plan['stock_qty'],
        'panel_dry_mass_estimate_kg':[round(v,3) for v in panel_mass],
        'panel_mass_basis':'Exported nominal part volumes; steel 7850 and aluminum 2700 kg/m3. Includes captive strips/retainers, excludes separate spoilboards/work. Weigh actual panels; this is not a handling load rating.',
        'panel_component_ids':panel_members,
        'scope':'Inventory/layout check only. Not a fabrication or procurement release; no current delivered price.',
    }
    (EVIDENCE/'package-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
