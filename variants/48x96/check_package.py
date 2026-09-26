"""Independent current-file binding and STEP readback of the development layout."""
from pathlib import Path
import hashlib,json,os,sys
import cadquery as cq
from layout import Parameters,build,bounds

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
STATES=('router','plasma_layout')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source_paths=[OUT/n for n in ('layout.py','check_static.py','render.py','check_package.py')]
    sources={p.relative_to(ROOT).as_posix():sha(p) for p in source_paths}
    names=['README.md','router.step','plasma_layout.step','layout-verification.json','static-verification.json',
           'preview-verification.json','layout-router.png','layout-plasma.png','layout-plan.png','layout-plan.svg']
    artifacts={n:sha(OUT/n) for n in names}
    layout=json.loads((OUT/'layout-verification.json').read_text(encoding='utf-8'))
    static=json.loads((OUT/'static-verification.json').read_text(encoding='utf-8'))
    preview=json.loads((OUT/'preview-verification.json').read_text(encoding='utf-8'))
    checks={'exact_layout_states':set(layout['states'])==set(STATES),
            'exact_static_states':set(static['states'])==set(STATES),
            'reports_sources_unchanged':all(r['sources_unchanged'] for r in (layout,static,preview)),
            'layout_source_binding':set(layout['source_sha256'])=={'layout.py'} and all(sha(OUT/n)==h for n,h in layout['source_sha256'].items()),
            'static_source_binding':set(static['source_sha256'])=={'layout.py','check_static.py'} and all(sha(OUT/n)==h for n,h in static['source_sha256'].items()),
            'preview_source_binding':set(preview['source_sha256'])=={'layout.py','render.py'} and all(sha(OUT/n)==h for n,h in preview['source_sha256'].items()),
            'preview_exact_artifacts':set(preview['artifact_sha256'])=={'layout-router.png','layout-plasma.png','layout-plan.png','layout-plan.svg'},
            'preview_artifact_binding':all(sha(OUT/n)==h for n,h in preview['artifact_sha256'].items()),
            'static_report_passed':static['passed'] is True}
    records={}
    for state in STATES:
        parts,d=build(Parameters(),state)
        expected=cq.Compound.makeCompound([p.shape for p in parts])
        actual=cq.importers.importStep(str(OUT/(state+'.step'))).val()
        bbox_delta=max(abs(a-b) for a,b in zip(bounds(actual),bounds(expected)))
        volume_delta=abs(actual.Volume()-expected.Volume())
        one=layout['states'][state];v=one['verification'];s=static['states'][state]
        physical=[p for p in parts if p.material!='allocation only']
        record={'part_count':len(parts),'step_solids':len(actual.Solids()),'valid':actual.isValid(),
                'bbox_max_delta_mm':bbox_delta,'volume_delta_mm3':volume_delta,
                'part_count_matches':len(parts)==len(actual.Solids())==one['part_count']==one['step_solid_count']==347,
                'volume_matches':volume_delta<max(.2,expected.Volume()*1e-7),'bbox_matches':bbox_delta<1e-5,
                'step_binding_matches':one['step_sha256']==sha(OUT/(state+'.step')),
                'reported_geometry_passes':v['passed'] is True and len(v['checks'])==10 and all(x is True for x in v['checks'].values()),
                'reported_static_passes':s['passed'] is True and s['fabricated_parts']==len(physical)==338 and s['excluded_allocation_parts']==9 and not s['unexpected_intersections'],
                'physical_holds_preserved':v['conversion_paths_verified'] is False and v['whole_machine_strength_qualified'] is False and v['supplier_interfaces_verified'] is False}
        record['passed']=all(record[k] is True for k in ('valid','part_count_matches','volume_matches','bbox_matches','step_binding_matches','reported_geometry_passes','reported_static_passes','physical_holds_preserved'))
        records[state]=record
        print(state,'independent readback',record['passed'],flush=True)
    checks['source_files_unchanged']=all(sha(ROOT/n)==h for n,h in sources.items())
    checks['artifact_files_unchanged']=all(sha(OUT/n)==h for n,h in artifacts.items())
    result={'passed':all(checks.values()) and all(r['passed'] for r in records.values()),
            'scope':'Source-bound development package and independent STEP round trip only; not fabrication, handling, supplier-interface or structural release.',
            'checks':checks,'states':records,'sources_unchanged':checks['source_files_unchanged'],
            'source_sha256':sources,'artifact_sha256':{(OUT/n).relative_to(ROOT).as_posix():h for n,h in artifacts.items()},
            'fabrication_ready':False,'conversion_paths_verified':False,'whole_machine_strength_qualified':False,'supplier_interfaces_verified':False}
    (OUT/'package-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PACKAGE PASS',result['passed'],flush=True)
    return 0 if result['passed'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
