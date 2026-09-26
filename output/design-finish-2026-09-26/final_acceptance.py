"""Bind Rev I evidence to current source and artifact bytes; not machine release."""
from pathlib import Path
import hashlib,json,os

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
CAD=ROOT/'output/release-review/RevI-CAD'
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
ASSEMBLY_NAMES={'RevI_ROUTER','RevI_BED_STORED','RevI_PLASMA_HARDWARE'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def step_readbacks_passed(report):
    states=report.get('step_readback',{}).get('states',[])
    return (report.get('status')=='PASS' and report.get('step_readback',{}).get('status')=='PASS'
        and len(states)==3 and {s.get('name') for s in states}==ASSEMBLY_NAMES
        and all(s.get('passed') is True for s in states))


def checker_mismatches(data, checker=None, runner=None):
    """Bind optional checker identities to known paths, never a report-chosen file."""
    issues=[]
    for family,target in (('verifier',checker),('checker',checker),('runner',runner)):
        keys=[family+'_sha256'+suffix for suffix in ('','_before','_after')]
        present=[key for key in keys if key in data]
        if not present:continue
        if target is None:
            issues.append('No trusted file mapping for '+family+' identity');continue
        target=Path(target)
        actual=sha(target) if target.is_file() else None
        for key in present:
            if actual is None or data[key]!=actual:
                issues.append({'binding':key,'file':str(target),'expected':data[key],'actual':actual})
        paired=[family+'_sha256_before',family+'_sha256_after']
        if any(key in data for key in paired) and not all(key in data for key in paired):
            issues.append('Incomplete before/after '+family+' identity')
        if all(key in data for key in paired) and data[paired[0]]!=data[paired[1]]:
            issues.append(family+' changed during the recorded run')
        if data.get(family+'_changed_during_run'):
            issues.append(family+' reported a change during the recorded run')
        declared=data.get(family+'_file')
        if declared:
            declared=Path(str(declared).replace('\\','/'))
            if not declared.is_absolute():declared=(target.parent/declared if declared.parent==Path('.') else ROOT/declared)
            if declared.resolve()!=target.resolve():issues.append('Unexpected '+family+' file '+str(declared))
    return issues


def structural_calculation_passed(r):
    """A passing arithmetic screen explicitly leaves machine rigidity unqualified."""
    states=r.get('static_states',{})
    return (r.get('arithmetic_checks_pass') is True and r.get('nominal_geometry_pass') is True
        and r.get('sources_unchanged') is True and r.get('builder')=='build_revi.build_model'
        and set(states)=={'router','stored'} and all(not s.get('unresolved_intersections') for s in states.values())
        and r.get('full_machine_rigidity_qualified') is False
        and bool(r.get('whole_chain_budget',{}).get('unknown_series_compliances')))


def exported_handling_mass_check(calculations, exported):
    """Reconcile exact handling membership/material/volume with current export."""
    issues=[];rows=[]
    parts=exported.get('parts',[]);by_id={p['id']:p for p in parts}
    if len(by_id)!=len(parts):issues.append('Duplicate exported part IDs')
    for kind,count in (('panel',6),('beam',4)):
        assemblies=calculations.get('geometry',{}).get(kind+'_mass_inventory',[])
        if len(assemblies)!=count:issues.append('Missing exact '+kind+' mass inventory')
        assigned=[]
        for assembly in assemblies:
            total=0.0
            for member in assembly.get('parts',[]):
                ident=member['id'];assigned.append(ident);actual=by_id.get(ident)
                if actual is None:issues.append('Missing exported member '+ident);continue
                if actual['material']!=member['material']:issues.append('Changed material '+ident)
                if abs(actual['volume_mm3']-member['volume_mm3'])>0.0001:issues.append('Changed nominal solid volume '+ident)
                total+=actual['volume_mm3']*member['density_kg_per_mm3']
            delta=abs(total-assembly.get('nominal_mass_kg',-1))
            if delta>1e-6:issues.append('Mass sum differs for '+kind+' '+str(assembly['index']))
            rows.append({'kind':kind,'index':assembly['index'],'exported_nominal_mass_kg':total,'difference_kg':delta})
        expected={p['id'] for p in parts if p.get('group')==('bed_panel' if kind=='panel' else 'bed_beam')}
        if set(assigned)!=expected or len(assigned)!=len(set(assigned)):
            issues.append('Exported '+kind+' membership differs from calculator')
    return {'passed':not issues,'differences':issues,'assemblies':rows,
            'scope':'Nominal solid volumes and specified densities only; no measured handling-mass or physical strength qualification.'}


def main():
    checks=[]
    def record(label,path,predicate,hashkey=None,base=SOURCE,required=(),source_files=None,checker=None,runner=None,local_paths=False):
        path=Path(path);rec={'check':label,'report':str(path.relative_to(ROOT)).replace('\\','/')}
        if not path.exists():rec.update(status='MISSING',passed=False);checks.append(rec);return
        data=json.loads(path.read_text(encoding='utf-8'));mismatches=[]
        hashes=data.get(hashkey,{}) if hashkey else {}
        if hashkey and not hashes:mismatches.append('Missing source hashes')
        for name,expected in hashes.items():
            p=Path(str(name).replace('\\','/'))
            if not p.is_absolute():p=((source_files or {}).get(p.name,base/p) if local_paths or p.parent==Path('.') else ROOT/p)
            actual=sha(p) if p.exists() else None
            if actual!=expected:mismatches.append({'file':str(p),'expected':expected,'actual':actual})
        names={Path(str(n).replace('\\','/')).name for n in hashes}
        for name in required:
            if name not in names:mismatches.append('Missing integrated source '+name)
        mismatches.extend(checker_mismatches(data,checker,runner))
        passed=bool(predicate(data)) and not mismatches
        rec.update(status='PASS' if passed else 'STALE' if mismatches else 'FAIL',passed=passed,
                   report_sha256=sha(path),source_mismatches=mismatches)
        checks.append(rec)
    integrated=('build_revi.py','structure_finish.py','service_finish.py','motion_finish.py')
    record('Three assembly states; shared parts; nine router and nine head poses',OUT/'verification.json',
        lambda r:r.get('geometry_passed') and not r.get('sources_changed_during_run') and len(r.get('poses',[]))==9 and len(r.get('plasma_hardware_poses',[]))==9,
        'source_imported_sha256',required=integrated)
    record('Independent current STEP readback',OUT/'step-verification.json',
        step_readbacks_passed,
        'source_imported_sha256',required=integrated)
    for name,label in [('spoil-transfer-check','Six spoilboard routes'),('panel-path-check','Six panel routes'),('beam-path-check','Four support-beam routes')]:
        record(label,OUT/'routes'/(name+'.json'),lambda r:r.get('integrated_passed') and not r.get('complete_sources_changed_during_run'),
               'complete_source_sha256',required=integrated,runner=OUT/'verify_revi_routes.py')
    record('Structural arithmetic and nominal states; full-machine rigidity remains unqualified',OUT/'structure/calculations.json',
        structural_calculation_passed,'source_sha256',required=integrated+('calculate_structure.py',),
        source_files={'calculate_structure.py':OUT/'structure/calculate_structure.py'},checker=OUT/'structure/calculate_structure.py')
    record('Reinforced storage restraint routes',OUT/'structure/reinforced-restraint-paths.json',
        lambda r:r.get('pass') and r.get('sources_unchanged') and r.get('builder')=='build_revi.build_model',
        'source_sha256',required=integrated+('check_reinforced_paths.py','check_spoil_transfer.py'),checker=OUT/'structure/check_reinforced_paths.py')
    record('Temporary keeper-body transfer',OUT/'structure/temporary-fixture-transfer.json',
        lambda r:r.get('pass') and r.get('sources_unchanged') and r.get('builder')=='build_revi.build_model',
        'source_sha256',required=integrated+('check_temp_fixture_transfer.py','check_reinforced_paths.py','check_spoil_transfer.py'),checker=OUT/'structure/check_temp_fixture_transfer.py')
    record('Water servicing, cabinet plates and enlarged hose sweeps',OUT/'service/verification-build_revi.json',
        lambda r:r.get('passed') and r.get('builder')=='build_revi' and not r.get('source_changes'),
        'source_hashes',required=integrated,checker=OUT/'service/verify_service_finish.py')
    record('Float, normal breakaway and head machining definitions',OUT/'motion/mechanism-verification.json',
        lambda r:r.get('passed') and r.get('source_unchanged'),'source_sha256',required=('motion_finish.py','cad_helpers.py'),checker=OUT/'motion/verify_motion_finish.py')
    record('Head fastener envelopes and exact individual export inventory',OUT/'motion/head-package-verification.json',
        lambda r:r.get('passed') and r.get('source_unchanged') and r.get('mechanism_source_matches')
            and r.get('motion_source_sha256')==sha(SOURCE/'motion_finish.py'),
        'file_sha256',base=OUT/'motion/head-cad',checker=OUT/'motion/verify_head_package.py',local_paths=True)
    record('Split-head transfer through the phased machine',OUT/'motion/integrated-verification.json',
        lambda r:r.get('passed') and r.get('source_unchanged') and r.get('builder')=='build_revi',
        'source_sha256',required=integrated,checker=OUT/'motion/verify_motion_finish.py')
    record('Temporary panel/beam preparation and restoration for head transfer',OUT/'motion/transfer-staging-verification.json',
        lambda r:r.get('passed') and r.get('sources_unchanged') and r.get('builder')=='build_revi',
        'source_sha256',base=ROOT,required=integrated+('check_transfer_staging.py',),checker=OUT/'motion/check_transfer_staging.py')
    record('Router tool transfer and its bed-sequence prerequisites',OUT/'motion/router-transfer-verification.json',
        lambda r:r.get('passed') and r.get('sources_unchanged') and r.get('builder')=='build_revi',
        'source_sha256',base=ROOT,required=integrated+('check_router_transfer.py',),checker=OUT/'motion/check_router_transfer.py')
    record('Changed tool obstacles across the full conversion sequence',OUT/'motion/conversion-prerequisites.json',
        lambda r:r.get('passed') and r.get('sources_unchanged') and r.get('reports_unchanged')
            and all(e['passed'] for e in r.get('evidence_bindings',[])),
        'source_sha256',base=ROOT,required=integrated+('check_conversion_prerequisites.py',),checker=OUT/'motion/check_conversion_prerequisites.py')
    record('Conversion prerequisite input-report identities',OUT/'motion/conversion-prerequisites.json',
        lambda r:r.get('passed') and r.get('reports_unchanged'),
        'evidence_report_sha256',base=ROOT)
    record('Water/tool terminal graph and bounded fault sequences',OUT/'controls/verification.json',
        lambda r:r.get('status')=='PASS_WITH_EXPLICIT_LIMITS' and len(r.get('checks',[]))==450
            and all(c['passed'] for c in r['checks']),
        'source_sha256',base=OUT/'controls')
    record('Current generated terminal wiring and reviewed control documents',OUT/'controls/verification.json',
        lambda r:r.get('status')=='PASS_WITH_EXPLICIT_LIMITS',
        'artifact_sha256',base=ROOT)
    record('Normally-off run interface electrical screen',OUT/'controls/run-interface.json',
        lambda r:r.get('status')=='SCHEMATIC_SCREEN_PASS' and len(r.get('checks',{}))==11
            and all(r['checks'].values()),
        'source_sha256',base=OUT/'controls')
    record('Current authored run-interface drawing',OUT/'controls/run-interface.json',
        lambda r:r.get('status')=='SCHEMATIC_SCREEN_PASS',
        'artifact_sha256',base=ROOT)
    record('Isolated head/probe schematic and bounded fault response',OUT/'controls/head-interface-verification.json',
        lambda r:r.get('status')=='PASS_WITH_EXPLICIT_LIMITS' and r.get('passed_checks')==418
            and len(r.get('checks',[]))==418 and r.get('dynamic_cases')==18
            and all(c['passed'] for c in r['checks']),
        'source_sha256',base=ROOT,required=('verify_head_interface.py','head-interface.json','circuit.py','terminal-netlist.json'),
        checker=OUT/'controls/verify_head_interface.py')
    record('Final source-bound assembly exports',CAD/'engineering-manifest.json',
        lambda r:r.get('integrated_geometry_pass') and not r.get('sources_changed_during_build')
            and set(r.get('state_checks',{}))==ASSEMBLY_NAMES,
        'source_sha256',required=integrated)
    record('Part inventory, individual solids and drawing package',OUT/'package-verification.json',
        lambda r:r.get('no_missing_or_stale_individual_files') and r.get('source_hashes_current'),
        'artifact_sha256',base=ROOT)
    record('Head detail rendered from current CAD',OUT/'head-preview-verification.json',
        lambda r:r.get('sources_unchanged') and not r.get('actual_torch_present')
            and sha(CAD/'previews'/r['preview']['file'])==r.get('image_sha256'),
        'source_sha256',base=ROOT)
    record('Concept PDF build inputs',OUT/'pdf/build-verification.json',
        lambda r:r.get('pages')==4 and sha(ROOT/'output/pdf/plasma-router-stand-concept.pdf')==r.get('pdf_sha256'),
        'input_sha256',base=ROOT)
    record('Four-page visual review of the current PDF',OUT/'pdf/visual-review.json',
        lambda r:r.get('passed') and r.get('pages_reviewed')==[1,2,3,4]
            and sha(ROOT/'output/pdf/plasma-router-stand-concept.pdf')==r.get('pdf_sha256'),
        'artifact_sha256',base=ROOT)
    calc=OUT/'structure/calculations.json';exported=CAD/'RevI_ROUTER-validation.json'
    mass_record={'check':'Exported panel/beam inventory and nominal mass reconciliation','report':str(calc.relative_to(ROOT)).replace('\\','/')}
    if calc.exists() and exported.exists():
        result=exported_handling_mass_check(json.loads(calc.read_text(encoding='utf-8')),json.loads(exported.read_text(encoding='utf-8')))
        mass_record.update(result,status='PASS' if result['passed'] else 'FAIL',report_sha256=sha(calc),
                           export_report=str(exported.relative_to(ROOT)).replace('\\','/'),export_report_sha256=sha(exported))
    else:mass_record.update(status='MISSING',passed=False)
    checks.append(mass_record)
    step=OUT/'step-verification.json'
    if step.exists():
        for state in json.loads(step.read_text(encoding='utf-8')).get('step_readback',{}).get('states',[]):
            p=CAD/'step'/(state['name']+'.step');actual=sha(p) if p.exists() else None
            passed=bool(actual) and actual==state['sha256']
            checks.append({'check':'Current '+state['name']+' file','report':str(p.relative_to(ROOT)).replace('\\','/'),
                'status':'PASS' if passed else 'STALE','passed':passed,'sha256':actual})
    result={'status':'PASS' if checks and all(r['passed'] for r in checks) else 'NOT_CURRENT_OR_NOT_PASSING',
        'scope':'Explicit nominal geometry, named handling/service paths, conditional structural arithmetic and bounded circuit-model behavior. This is not a complete fabrication, physical rigidity, electrical safety, HF compatibility or operating-machine release.',
        'checks':checks,'index_generator_sha256':sha(__file__),
        'physical_release':False,
        'not_closed':['Actual motion/torch/valve/strainer/enclosure interfaces','Purchased module and complete tool-to-work rigidity',
            'Actual extrusion-slot preload capacity','Complete populated panel and stop/power/brake integration',
            'Tilted breakaway behavior, force calibration, moving tool leads and physical commissioning']}
    (OUT/'acceptance-index.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    lines=['# Rev I verification index','',f"**Recorded checks: {result['status']}.** {result['scope']}",'',
        '| Check | Result |','|---|---|']
    for rec in checks:
        rel=os.path.relpath(ROOT/rec['report'],OUT).replace('\\','/')
        lines.append(f"| [{rec['check']}]({rel}) | {rec['status']} |")
    lines.extend(['','The initial findings and rejected diagnostic routes are retained as history. Only the source-matching records above support the current package. A PASS here does not mean the machine is ready to fabricate or operate.','',
        '[Open engineering and measured inputs](OPEN-ITEMS.md). [Full hashes](acceptance-index.json).',''])
    (OUT/'ACCEPTANCE.md').write_text('\n'.join(lines),encoding='utf-8')
    print('REVI_ACCEPTANCE',result['status'],len(checks),'records',flush=True)
    for r in checks:
        if not r['passed']:
            mismatches=r.get('source_mismatches',[])
            print(r['check'],r['status'],len(mismatches),'binding differences',mismatches[:3],flush=True)
    return 0 if result['status']=='PASS' else 2


if __name__=='__main__':raise SystemExit(main())
