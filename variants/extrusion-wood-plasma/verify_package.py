"""Cross-check this variant's reports and local documentation without changing other packages."""
from pathlib import Path
import hashlib,json,math,re,sys,csv
from collections import Counter
H=Path(__file__).resolve().parent; R=H.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    checks=[]
    def ck(k,v):checks.append({'check':k,'pass':bool(v)})
    srcfiles=[p for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='package-review.json']
    for p in srcfiles:
        if p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf8')):
                if target.startswith(('https:','http:','#')):continue
                ck(p.name+': '+target,(p.parent/target.split('#')[0]).is_file())
        if p.suffix=='.json':
            val=obj(p)
            if not isinstance(val,dict):continue
            for rel,h in val.get('source_sha256',{}).items():
                target=R/rel
                if not target.exists():target=p.parent/rel
                if not target.exists():target=H/rel
                ck(p.name+': '+rel,target.is_file() and sha(target)==h)
    calc=obj(H/'review/build-check.json'); bd=obj(H/'bed-check.json'); sc=obj(H/'review/support-screen.json')
    ck('STEP readbacks',len(calc['assemblies'])==4 and all(v['STEP_solid_count']>=v['named_components'] for v in calc['assemblies'].values()))
    ck('frame/bed/motion/interface clashes',calc['boundary_clashes_remaining']==0)
    ck('travel screening',obj(H/'motion-detail/external-envelope.json')['passed'])
    ck('new plasma head checks',obj(H/'motion-detail/clearance-check.json')['all_passed'])
    ck('manual transfer samples',len(bd['manual_transfer']['unexpected'])==0 and bd['manual_transfer']['poses']>0)
    ck('internal bed checks',all(not item['unclassified_intersections'] for item in bd['assembly_internal_pairs'].values()))
    ck('all four pan mounts captured',len(bd['four_captive_pan_mounts'])==4 and all(
        d['free_test_interference_mm3']<0.05 and d['stop_test_interference_mm3']>0.05
        and d['quarter_mm_past_uplift_stop_interference_mm3']>0.05 for d in bd['four_captive_pan_mounts'].values()))
    w=obj(H/'review/water-option.json')
    ck('optional water layout has room for full return',w['full_return_test_headroom_L']>0 and w['max_unintended_clash_mm3']==0)
    ck('support screen uses retained pan mass',math.isclose(bd['all_bed_parts_plus_operating_water_weight_N'],sc['wet_bed_weight_N']))
    ck('the 36 frame profiles are included',len(list((H/'plate-profiles').glob('*.dxf')))==36)
    ck('budget nesting and variants',math.isclose(sc['base_frame_usd'],319.88) and math.isclose(sc['nine_foot_extrusion_usd'],379.78))
    rows=list(csv.DictReader((H/'stock-and-cuts.csv').open(encoding='utf8')))
    bars={int(r['stock_bar']):int(r['stock_mm']) for r in rows}
    ck('pack counts',len(rows)==19 and Counter(bars.values())=={1500:8,1000:4} and calc['default_hybrid_step_extrusion_parts']==22)
    for mode in ('wood','plasma','frame'):
        ck(mode+' preview', (H/'review'/(mode+'-view.png')).stat().st_size>10000)
    fail=[c for c in checks if not c['pass']]
    result={'status':'PASS' if not fail else 'FAIL','scope':'File consistency and declared bounded checks only, not a machine fabrication or operation release.',
        'checks':checks,'files_sha256':{p.relative_to(H).as_posix():sha(p) for p in sorted(srcfiles)}}
    (H/'review/package-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'checks':len(checks),'files':len(srcfiles),'failures':fail},indent=2))
    return int(bool(fail))
if __name__=='__main__':sys.exit(main())
