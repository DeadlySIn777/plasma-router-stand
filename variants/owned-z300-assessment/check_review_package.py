"""Bind the current review evidence without asserting machine completion."""
from pathlib import Path
import hashlib,importlib.util,json,re
from urllib.parse import unquote

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    reports=[
        ('output/z300-fit-decision.json',ROOT,'passed'),
        ('output/custom-joint-repair-check.json',ROOT,'passed'),
        ('output/front-stop-repair/front-stop-repair-check.json',ROOT,'passed'),
        ('output/front-stop-repair/front-stop-base-reference-check.json',ROOT,'passed'),
        ('output/candidate-internal-continuous-check.json',ROOT,'passed'),
        ('output/candidate-external-sweep-check.json',ROOT,'passed'),
        ('output/candidate-static-thread-check.json',ROOT,'passed'),
        ('output/candidate-motion-evidence-manifest.json',ROOT,'passed'),
        ('output/candidate-path-service-check.json',ROOT,'passed'),
        ('output/proposal-assemblies-v2/candidate-assembly-v2-check.json',ROOT,'passed'),
        ('output/owned-head-inspection.json',HERE,'inspection_completed')]
    failures=[];checks={};bindings=0
    def bind(path,h,label):
        nonlocal bindings
        bindings+=1
        if not path.is_file()or sha(path)!=h:failures.append(dict(report=label,file=str(path.relative_to(ROOT)),reason='missing_or_hash_changed'))
    def find_file_hash_records(value,label):
        if isinstance(value,dict):
            if isinstance(value.get('file'),str)and isinstance(value.get('sha256'),str):
                path=HERE/value['file']
                if not path.is_file():path=ROOT/value['file']
                bind(path,value['sha256'],label)
            for v in value.values():find_file_hash_records(v,label)
        elif isinstance(value,list):
            for v in value:find_file_hash_records(v,label)
    for n,base,flag in reports:
        path=HERE/n;j=json.loads(path.read_text(encoding='utf-8'))
        okay=j.get(flag)is True
        if not okay:failures.append(dict(report=n,reason='required_result_false'))
        for key in('source_consistent_during_check','source_consistent_during_build'):
            if key in j and not j[key]:failures.append(dict(report=n,reason=key+'_false'))
        for key in('source_sha256','study_source_sha256','motion_source_closure_sha256'):
            for source,h in j.get(key,{}).items():bind(base/source,h,n)
        for source,h in j.get('output_sha256',{}).items():
            p=ROOT/source
            if not p.is_file():p=HERE/source
            bind(p,h,n)
        find_file_hash_records(j,n)
        checks[n]=dict(sha256=sha(path),required_flag=flag,result=okay)
    spec=importlib.util.spec_from_file_location('candidate_manufacturing_binding',HERE/'build_manufacturing_pack.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    name='manufacturing/manufacturing-pack-check.json';path=HERE/name
    m=json.loads(path.read_text(encoding='utf-8'))
    assert m['passed']and all(m['checks'].values())
    for key,h in m['source_sha256'].items():bind(module.INPUTS[key],h,name)
    for source,h in m['output_sha256'].items():bind(ROOT/source,h,name)
    bind(HERE/'build_manufacturing_pack.py',m['generator_sha256'],name)
    artifacts=json.loads((HERE/'manufacturing/artifact-hash-checks.json').read_text(encoding='utf-8'))
    for row in artifacts:
        bind(ROOT/row['file'],row['expected_sha256'],'manufacturing/artifact-hash-checks.json')
    checks[name]=dict(sha256=sha(path),required_flag='passed',result=True,counts=m['counts'])
    docs=[HERE/'README.md',HERE/'STATUS.md',HERE/'OWNER-HEAD-INTEGRATION.md',
          HERE/'MOTION-PROOF.md',HERE/'PATH-SERVICE-PROOF.md',HERE/'manufacturing/README.md',ROOT/'README-FIRST.md']
    for path in docs:
        for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if re.match(r'^[a-zA-Z]+:|^#',target):continue
            linked=path.parent/unquote(target.strip('<>').split('#',1)[0])
            if not linked.exists():failures.append(dict(report=path.relative_to(ROOT).as_posix(),file=target,reason='broken_local_document_link'))
    requirements=json.loads((HERE/'candidate-requirements.json').read_text(encoding='utf-8'))
    assert not requirements['design_complete']and not requirements['fabrication_release']
    result=dict(study='CURRENT_REVIEW_EVIDENCE_AND_REQUIREMENTS_BINDING',
        checks=checks,verified_source_or_output_bindings=bindings,
        manufacturing_artifacts_freshly_rechecked=len(artifacts),failures=failures,
        passed=not failures,meaning_of_pass='The listed scoped review evidence remains source/output consistent. This is not machine-design completion or a fabrication/operation release.',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in[Path(__file__),*docs,HERE/'candidate-requirements.json']},
        unresolved_CAD=['Owned clamp and working whole-boot assembly machine integration',
            'Full drill-only HDPE/uncut20100 bed, support, retention and in-footprint conversion',
            'Inherited8080 gantry member versus4080-only preference',
            'Previously selected magazine slide reconciliation and exact ATC interfaces'],
        design_complete=False,fabrication_release=False,operating_release=False,
        full_300_Z_operating_domain_qualified=False,physical_rigidity_qualified=False,
        complete_delivered_budget_verified=False,separate_4x8_completed=False)
    (HERE/'output/current-review-package-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],report_count=len(checks),bindings=bindings,failures=failures,design_complete=False)),flush=True)
    return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
