"""Join the base Rev H index with the separate temporary fixture transfer proof."""
from pathlib import Path
import json
import os
import verify_revh as base


def main():
    base.acceptance_index()
    path=base.OUTPUT/'bed/temporary-fixture-transfer.json'
    rec={'check':'Two temporary C-body tray-to-beam routes',
         'report':str(path.relative_to(base.ROOT)).replace('\\','/')}
    mismatches=[]
    if path.exists():
        data=json.loads(path.read_text(encoding='utf-8'))
        source_hashes=data.get('source_sha256',{})
        if not source_hashes:mismatches.append({'reason':'Missing source hashes'})
        for name,digest in source_hashes.items():
            source=Path(name)
            source=source if source.is_absolute() else base.ROOT/source
            current=base.sha(source) if source.exists() else None
            if current!=digest:mismatches.append({'file':name,'recorded':digest,'current':current})
        names={Path(name).name for name in source_hashes}
        for name in ('build_revh.py','bed_completion.py','water_completion.py','motion_completion.py'):
            if name not in names:mismatches.append({'reason':'Integrated source missing','file':name})
        passed=(data.get('pass') is True and data.get('sources_unchanged') is True
                and len(data.get('paths',[]))==2 and not mismatches)
        rec.update(status='PASS' if passed else 'STALE' if mismatches else 'FAIL',
                   passed=passed,report_sha256=base.sha(path),source_mismatches=mismatches)
    else:
        rec.update(status='MISSING',passed=False)
    json_path=base.OUTPUT/'acceptance-index.json'
    result=json.loads(json_path.read_text(encoding='utf-8'))
    result['checks'].insert(6,rec)
    result['status']='PASS' if all(r['passed'] for r in result['checks']) else 'NOT_CURRENT_OR_NOT_PASSING'
    result['supplemental_index_generator_sha256']=base.sha(__file__)
    json_path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    lines=['# Rev H CAD verification index','',
           f"**Recorded checks: {result['status']}.** {result['scope']}",'',
           '| Check | Current result |','|---|---|']
    for item in result['checks']:
        relative=os.path.relpath(base.ROOT/item['report'],base.OUTPUT).replace('\\','/')
        lines.append(f"| [{item['check']}]({relative}) | {item['status']} |")
    lines.extend(['',result['diagnostic_history'],'',
        'Current results do not close purchased-interface measurements, coupling/brake fit and response, the unfinished floating/breakaway plasma head, flexible cable/hoses, rigidity or physical commissioning. Read each linked report for its exact exclusions.',
        '', '[Complete hashes and provenance](acceptance-index.json).',''])
    (base.OUTPUT/'ACCEPTANCE.md').write_text('\n'.join(lines),encoding='utf-8')
    print('FINAL_REVH_INDEX',result['status'],flush=True)
    return 0 if result['status']=='PASS' else 2


if __name__=='__main__':
    raise SystemExit(main())
