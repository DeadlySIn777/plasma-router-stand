"""Reconcile current artifacts and make a clearly labeled engineering archive.

This is an artifact-integrity check. It never turns successful file checks into
a mechanical design approval or a claim of machine commissioning.
"""
from pathlib import Path
import hashlib, json, zipfile

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[2]
CONTROLS=PROJECT/'RevE-ENGINEERING/controls'
BUDGET=PROJECT/'outputs/reve-30510'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    checks=[]
    validations=[]
    manifest=read(HERE/'engineering-manifest.json')
    current_count=manifest['geometry_checks']['solid_count']
    module_count=len(read(HERE/'bed-configurations.json')['module_part_ids'])
    for f in sorted(HERE.glob('*-validation.json')):
        v=read(f)
        if 'step_readback' not in v: continue
        step=HERE/'step'/v['step_readback']['file']
        ok=step.exists() and sha(step)==v['step_readback'].get('sha256')
        checks.append({'check':f'{step.name}: STEP readback and current file hash', 'passed':bool(ok and v['step_readback'].get('passed'))})
        checks.append({'check':f'{step.name}: no unresolved static intersections','passed':not v.get('unresolved_intersections',[])})
        # PLASMA_SETUP legitimately excludes the hoisted one-piece module.
        expected=current_count-module_count if 'PLASMA' in step.name else current_count
        checks.append({'check':f'{step.name}: current mechanical component count','passed':v.get('part_count')==expected})
        validations.append({'file':step.name,'solids':v.get('part_count'), 'clashes':len(v.get('unresolved_intersections',[]))})
    motion=manifest.get('motion',{})
    checks.append({'check':'Motion definition included in assembly manifest','passed':bool(motion)})
    motion_report=read(HERE/'motion-validation.json') if (HERE/'motion-validation.json').exists() else {}
    travel=motion_report.get('states',[])
    checks.append({'check':'Sampled motion configurations free of unresolved intersections','passed':bool(travel) and all(not t.get('clashes',[]) for t in travel)})
    checks.append({'check':'Motion report source hash and local/world geometry agree','passed':motion_report.get('source_sha256')==sha(HERE/'motion_details.py') and not motion_report.get('local_world_geometry_mismatches',[])})
    swap=read(HERE/'swap-path-checks.json') if (HERE/'swap-path-checks.json').exists() else {}
    checks.append({'check':'Sampled one-piece module hoist path report passed','passed':swap.get('status')=='PASS SAMPLED PATH' and not swap.get('failures',[])})
    geometry_sources=['bed_details.py','build_reve_engineering.py','cad_helpers.py','controls_packaging.py',
        'frame_details.py','geometry_base.py','motion_details.py','sensor_mounts.py',
        'tool_parking.py','water_accessories.py','water_system.py','swap-path-checks.py']
    source_hashes=swap.get('source_modules_sha256_at_build',{})
    stale_sources=[name for name in geometry_sources if not (HERE/name).exists() or sha(HERE/name)!=source_hashes.get(name)]
    checks.append({'check':'Hoist report matches current geometry and checker source hashes','passed':not stale_sources})
    nesting=read(HERE/'nesting/sheet-nesting.json')
    checks.append({'check':'Nesting quantity, edge, DXF audit checks','passed':all(nesting.get('verification',{}).values())})
    control=read(CONTROLS/'verification.json')
    checks.append({'check':'Controller static/compiled-image checks','passed':all(x.get('pass',False) for x in control['checks'])})
    water=read(HERE/'water-verification.json')
    checks.append({'check':'Water logic/inventory analytical screen','passed':water['status'].startswith('PASS')})
    pdf_report=read(PROJECT/'output/pdf/concept-pdf-check.json')
    current_pdf=PROJECT/'output/pdf/plasma-router-stand-concept.pdf'
    checks.append({'check':'Current concept PDF content checks and file hash','passed':pdf_report.get('text_checks_pass') and pdf_report.get('paragraph_bounds_pass') and pdf_report.get('sha256')==sha(current_pdf)})
    checks.append({'check':'All eight current concept PDF pages visually reviewed','passed':pdf_report.get('pages')==8 and pdf_report.get('visual_review_passed') is True})
    cost=read(BUDGET/'budget-data.json')
    goods=round(sum(r['goods_usd'] for r in cost['rows']),2)
    known_ship=round(sum(r['amount_usd'] or 0 for r in cost['shipping']),2)
    total=round(goods+known_ship,2)
    checks.append({'check':'Source-priced scope and grouped shipping reconcile','passed':total==cost['summary']['priced_scope_before_tax_usd']})
    checks.append({'check':'Unknown complete delivered total remains blank','passed':cost['summary']['complete_delivered_total_usd'] is None and bool(cost['unpriced'])})
    audit=read(BUDGET/'actual-cost/audit-data.json')
    checks.append({'check':'Price register matches current research files','passed':all(sha(BUDGET/'actual-cost'/name)==digest for name,digest in audit['input_hashes'].items())})
    holds=motion.get('holds',[])
    cabinet=manifest.get('controls_packaging',{})
    report={'status':'ENGINEERING PACKAGE — NOT A PURCHASE OR MANUFACTURING RELEASE',
            'file_integrity_checks':checks,'assembly_exports':validations,'motion_design_holds':holds,
            'stale_swap_sources':stale_sources,
            'additional_tool_clearance_hold':'Upper float guards begin at X978, only 3 mm beyond nominal maximum head-axis X975. Final torch body and mount offsets must clear guards at Y600/660/720. Nominal 800 mm X stroke is not a verified 800 mm plasma cutting width.',
            'water_electrical_release_items':read(HERE/'water-bom.json')['release_items'],
            'controls_packaging_holds':cabinet.get('unreleased_interfaces',[]),
            'controls_service_access':cabinet.get('service'),
            'priced_scope_before_tax_usd':total,'priced_goods_usd':goods,'known_shipping_usd':known_ship,'actual_delivered_quote_usd':None,
            'physical_commissioning':'Not performed; normal subsequent work, separate from missing design data.',
            'fusion_opened':False}
    (HERE/'package-review.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    lines=['# Rev F package status','',
        '**Not released for ordering or fabrication. Fusion has not been opened.**', '',
        'Rev F replaces the six-cassette bed with a ONE-PIECE hoisted module: welded steel ladder on the receiver ledgers, two machine-surfaced 12.7 mm MDF layers, ten cut-only full-length 20100 strips, four lift ears and four M8 drawdowns. Mode change is four bolts and the owner overhead winch. The engineering files below are current working deliverables. Successful solid checks and compiled firmware do not resolve the missing component interfaces.', '',
        '| Evidence | Current result |','|---|---|']
    for c in checks:lines.append(f"| {c['check']} | {'PASS' if c['passed'] else 'OPEN / FAIL'} |")
    lines+=['','## Cost', '',f"The current **priced portion is ${total:,.2f} USD before tax**: ${goods:,.2f} in sourced goods and ${known_ship:,.2f} in known or advertised shipping. This is a partial register, not the complete build price. {len(cost['unpriced'])} required scope entries still need a price or design decision, and other vendor shipping remains unquoted.",'',
            '[Current workbook](../../../outputs/reve-30510/CNC-plasma-RevE-budget.xlsx) now separates priced items, remaining requirements and alternatives. The former $7,663.82 estimate is superseded: its allowances and $300 shipping reserve were not actual quotes. Owner fabrication labor remains $0. The unsupported $200 skin allowance is removed. The audit also found understated billet stock and omitted small-stock requirements, so no simple subtraction is presented as a finished total.', '',
            '[Actual-cost findings and source register](../../../outputs/reve-30510/actual-cost/REAL-COST.md). The 80/20 beam and 16 T-nuts were configured together: $193.01 goods + $61.30 UPS Ground + $17.80 estimated tax = $272.11 to ZIP 30510. No order was placed. No cheaper rod-end or welded-bracket redesign has been adopted or credited as complete.', '',
            '## Remaining motion design work','']
    lines += ['- '+h for h in holds] or ['- Complete motion manifest has not yet been generated.']
    lines += ['','## Remaining electrical and procurement definition','',
        '- Identify the existing Amazon plasma power source and use its documented trigger, start type and arc-sensing interface. The supplied AG-60 torch-body link does not identify the power source. See PLASMA-COMPATIBILITY.md.',
        '- Complete shared selector/contact blocks, bed/guard confirmation, isolated interfaces and physical panel layout. Water-circuit relays, suppression, branch fuses and terminal allocation are now specified in WATER-ELECTRICAL-REVIEW.md; timer DC contact suitability and pump starting-current/fuse instructions remain open.',
        '- Obtain actual material, purchased-hardware and delivery prices. Custom cutting, finishing and machining are owner-performed; their operations remain in the drawings with no outside-shop labor budget. No supplier inquiry or purchase has been sent.',
        '- Resolve guarded supplier interfaces and final full-travel clearances before manufacturing. Final process-specific CAM needs the fabricator’s machine, tooling and postprocessor.',
        '- Check the actual torch body against the upper float guards: their X978 edge is only 3 mm beyond the nominal X975 maximum head axis. Final torch offset and usable plasma cutting area remain unresolved.',
        '- Complete the cabinet VFD heat rejection, isolation hardware, panel layout, cable-chain anchors, way covers and cable bend envelopes. A purchased enclosure reserve is not a completed panel layout; transfer-drill its back-panel pattern onto the cage rails.',
        '- Prototype-verify the Rev F bed fastening: MDF screw pull-out with the selected screws, TEK engagement in the 3.048 crossmember wall, and a first hoist with the module weighed and the sling geometry checked.', '',
        'Cabinet service: RESOLVED by the Rev F relocation. The enclosure stands upright in the front bay under the water table, door forward through the open front window, on a bolt-on cage under pan bearers 1 and 2. Routine electrical service requires no draining and no pan or bed removal; the old horizontal above-tank placement and its blocked lid are deleted.', '',
        '## Package navigation','',
        '- [Design, efficiency and control priorities](DESIGN-EFFICIENCY-REVIEW.md)',
        '- [Manufacturing handoff](MANUFACTURING-HANDOFF.md)',
        '- [Cut list](cutlist.csv)',
        '- [Tube cut plan](TUBE-CUT-PLAN.md)',
        '- [Flat-part nesting](nesting/sheet-nesting.json)',
        '- [Metal suppliers, posted prices and delivery gaps](METAL-SOURCING.md)',
        '- [Water control and operator sequence](WATER-CONTROL.md)',
        '- [Water electrical components and terminal allocation](WATER-ELECTRICAL-REVIEW.md)',
        '- [Fabrication operations and drawing limitations](FABRICATION-OPERATIONS.md)',
        '- [Plasma cutter and torch compatibility](PLASMA-COMPATIBILITY.md)',
        '- [Kraken firmware and pin map](../../../RevE-ENGINEERING/controls/README.md)',
        '- [Controller commissioning](../../../RevE-ENGINEERING/controls/COMMISSIONING.md)',
        '- [Supplier dimensions register](../module-mounting-field-register.md)',
        '- [Unsent supplier drawing requests](../SUPPLIER-DATA-REQUESTS-DRAFT.md)', '',
        'Prototype load, wet-transfer, electrical and cutting tests are subsequent commissioning steps. They are not claimed complete and are not substitutes for finishing the missing design dimensions.']
    (HERE/'PACKAGE-STATUS.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    first='''# CNC / plasma machine — Rev F

The current engineering package is in [Rev F](output/release-review/RevE-ENGINEERING/PACKAGE-STATUS.md) (directory name retained from Rev E). Rev F replaces the six-cassette bed with a one-piece hoisted module: a welded steel ladder riding the receiver ledgers, two machine-surfaced 12.7 mm MDF layers, and ten full-length cut-only 20100 strips. Mode change is four M8 bolts and the owner's overhead winch out the open front window. No purchase or manufacturing release has been issued, and Fusion has not been opened.

- [Current cost workbook](outputs/reve-30510/CNC-plasma-RevE-budget.xlsx)
- [Current Rev F concept PDF](output/pdf/plasma-router-stand-concept.pdf)
- [Design and efficiency review](output/release-review/RevE-ENGINEERING/DESIGN-EFFICIENCY-REVIEW.md)
- [Actual-price audit and remaining requirements](outputs/reve-30510/actual-cost/REAL-COST.md)
- [Manufacturing handoff](output/release-review/RevE-ENGINEERING/MANUFACTURING-HANDOFF.md)
- [Sampled module hoist review](output/release-review/RevE-ENGINEERING/SWAP-REVIEW.md)
- [Kraken onboard-driver firmware](RevE-ENGINEERING/controls/README.md)
- [Current cut list](output/release-review/RevE-ENGINEERING/cutlist.csv)

The Rev C superseded PDF, Rev C workbook and Rev D study files are historical records. The stable plasma-router-stand-concept.pdf filename contains the current Rev F design brief. Pricing remains in the workbook; the extrusion purchase is unchanged (five B0BXNWK99C two-packs) but each 1220 mm bar now takes ONE cut to 1197 instead of three cuts to 397, and the cassette anchor hardware, tie bars, storage racks and staging trays are deleted from scope.
'''
    (PROJECT/'README-FIRST.md').write_text(first,encoding='utf8')
    roots=[HERE,PROJECT/'output/release-review/sources']
    chosen=[PROJECT/'README-FIRST.md']
    chosen += [PROJECT/'output/pdf/plasma-router-stand-concept.pdf',PROJECT/'output/pdf/concept-pdf-check.json',PROJECT/'build_concept_current.py']
    cutlist=read(HERE/'cutlist.json')
    current_parts={p['part_number'] for p in cutlist if not p['individual_export_guarded']}
    current_nests={v['file'] for g in nesting['groups'] for v in g['layouts']}
    def current_file(p):
        if p.parent in {HERE/'parts',HERE/'dxf'}:
            return p.stem in current_parts
        if p.parent==HERE/'nesting' and p.suffix.lower()=='.dxf':
            return p.name in current_nests
        return True
    for base in roots:
        chosen += [p for p in base.rglob('*') if p.is_file() and p.suffix.lower() in {'.py','.json','.csv','.md','.dxf','.step','.svg','.png','.jpg','.pdf'} and '__pycache__' not in p.parts and current_file(p)]
    chosen += [p for p in BUDGET.iterdir() if p.suffix.lower() in {'.xlsx','.json','.mjs'} and 'superseded' not in p.name and 'estimate-history' not in p.name]
    chosen += [p for p in (BUDGET/'actual-cost').iterdir() if p.suffix.lower() in {'.json','.md','.py'}]
    chosen += [p for p in CONTROLS.iterdir() if p.name in {'README.md','COMMISSIONING.md','verification.json','source-manifest.json','Kraken-V1.1-controls-engineering.zip'}]
    chosen += [PROJECT/'output/release-review'/n for n in ['module-mounting-field-register.json','module-mounting-field-register.md','SUPPLIER-DATA-REQUESTS-DRAFT.md']]
    chosen=sorted(set(p for p in chosen if p.exists() and p.name!='archive-manifest.json'))
    archive_manifest=[{'path':p.relative_to(PROJECT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in chosen]
    archive=PROJECT/'outputs/RevE-ENGINEERING-review-package.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in chosen:z.write(p,p.relative_to(PROJECT).as_posix())
        z.writestr('archive-manifest.json',json.dumps(archive_manifest,indent=2))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print(json.dumps({'archive':str(archive),'files':len(chosen),'checks':checks,'cost':total},indent=2))

if __name__=='__main__':main()
