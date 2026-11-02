"""Source-current manifest and explicit nominal-thread table for motion checks."""
from pathlib import Path
import csv,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=HERE/'output'
NAMES=('candidate-internal-continuous-check.json','candidate-external-sweep-check.json',
       'candidate-static-thread-check.json','front-stop-repair/front-stop-repair-check.json',
       'front-stop-repair/front-stop-base-reference-check.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    checks={};failures=[]
    for name in NAMES:
        path=OUT/name;data=json.loads(path.read_text());bad=[]
        for n,h in data['source_sha256'].items():
            q=ROOT/n
            if not q.is_file()or sha(q)!=h:bad.append(n)
        for q in data.get('outputs',{}).values():
            if isinstance(q,dict)and q.get('file'):
                p=HERE/q['file']
                if not p.is_file()or sha(p)!=q['sha256']:bad.append(q['file'])
        passed=data['passed']and data['source_consistent_during_check']and not bad
        checks[name]=dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),
            passed=passed,source_hashes_current=not bad,source_errors=bad)
        if not passed:failures.append(name)
    data=json.loads((OUT/'candidate-static-thread-check.json').read_text())
    path=OUT/'specific-nominal-thread-dispositions.csv'
    rows=[dict(mode=mode,**r)for mode,s in data['states'].items()for r in s['nominal_thread_dispositions']]
    fields=('mode','a','b','volume_mm3','inherited_baseline_volume_mm3','disposition','source_reason','actual_thread_fit_qualified')
    with path.open('w',newline='',encoding='utf-8')as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    report=dict(study='SOURCE_CURRENT_CANDIDATE_MOTION_EVIDENCE_MANIFEST',checks=checks,
        source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
            (HERE/'MOTION-PROOF.md').relative_to(ROOT).as_posix():sha(HERE/'MOTION-PROOF.md')},
        specific_thread_table=dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),rows=len(rows)),
        domain_X_Yguide_Zlift_mm=[[175,975],[275,1275],[0,200]],physical_module_catalogue_stroke_mm=300,
        passed=not failures,failures=failures,fabrication_release=False,operating_release=False,
        scope='Only the scoped nominal geometry checks linked here pass. Actual hardware interfaces, retention, loads, rigidity and final installed head/ATC setup remain distinct release gates.')
    (OUT/'candidate-motion-evidence-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],failures=failures,thread_table_rows=len(rows)),indent=2))
    return 0 if report['passed']else 1
if __name__=='__main__':raise SystemExit(run())
