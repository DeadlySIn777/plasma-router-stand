"""Check the current Rev G artifact package and evidence freshness."""
from pathlib import Path
import ast,hashlib,json
import ezdxf
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
CAD=ROOT/'output/release-review/RevG-CAD'
SOURCE=CAD.parent/'RevE-ENGINEERING'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def source_hashes(values):
    bad=[n for n,h in values.items() if digest(SOURCE/n)!=h]
    assert not bad,('stale source evidence',bad)
def main():
    manifest=read(CAD/'engineering-manifest.json');source_hashes(manifest['source_sha256'])
    for state in manifest['state_checks'].values():
        assert state['part_count']==1283 and not state['unresolved_intersections']
        step=state['step_readback'];assert step['passed'] and digest(CAD/'step'/step['file'])==step['sha256']
    rows=read(CAD/'cutlist.json');ops=read(CAD/'part-operations.json')
    expected={r['part_number'] for r in rows if not r['individual_export_guarded']}
    expected_dxf={r['part_number'] for r in ops if not r['individual_export_guarded'] and r['manufacturing_flat']}
    assert expected=={p.stem for p in (CAD/'parts').glob('*.step')}
    assert expected_dxf=={p.stem for p in (CAD/'dxf').glob('*.dxf')}
    validation=read(CAD/'RevG_ROUTER-validation.json')
    assert {r['part_number'] for r in validation['individual_step_readback']}==expected
    assert all(r['valid'] for r in validation['individual_step_readback'])
    dxf_checks=[]
    for p in sorted((CAD/'dxf').glob('*.dxf')):
        d=ezdxf.readfile(p);audit=d.audit();assert not audit.errors and d.units==4,p
        dxf_checks.append({'file':p.name,'millimeters':True,'audit_errors':0})
    reports={}
    for name in ('motion/revg-full-machine-poses.json','motion/revg-panel-path.json'):
        data=read(HERE/name);assert data['status'] in ('PASS','CLEAR'),name
        source_hashes(data['sources_sha256']);reports[name]=data['status']
    for name in ('beam-path-check.json','bed-part-consistency.json'):
        data=read(HERE/name);assert data['pass'],name;source_hashes(data['source_sha256']);reports[name]='PASS'
    data=read(HERE/'spoil-transfer-check.json');assert data['pass'] and data['source_sha256']==digest(SOURCE/'bed_cassettes.py')
    reports['spoil-transfer-check.json']='PASS'
    data=read(HERE/'nut-evacuation-check.json');assert data['pass'];source_hashes(data['sources_sha256']);reports['nut-evacuation-check.json']='PASS'
    pdf=read(HERE/'pdf/build-verification.json')
    assert digest(ROOT/'output/pdf/plasma-router-stand-concept.pdf')==pdf['published_sha256']==pdf['pdf_sha256']
    for name,h in pdf['input_sha256'].items():assert digest(ROOT/name)==h,('PDF input changed',name)
    syntax=[]
    for p in SOURCE.glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p));syntax.append(p.name)
    artifacts={str(p.relative_to(ROOT)):digest(p) for p in CAD.rglob('*') if p.is_file() and p.suffix not in ('.npz','.log')}
    artifacts['output/pdf/plasma-router-stand-concept.pdf']=pdf['published_sha256']
    result={'status':'PASS','scope':'Artifact integrity, source freshness, expected exported inventory, DXF parsing/units and referenced evidence. Does not issue engineering or fabrication approval.',
        'assemblies':2,'components_per_assembly':1283,'individual_STEP_files':len(expected),'individual_DXF_files':len(expected_dxf),'dxf_checks':dxf_checks,
        'evidence_status':reports,'python_source_syntax_count':len(syntax),'PDF_pages':pdf['pages'],'PDF_visual_review':pdf['visual_review'],'artifact_sha256':artifacts}
    (HERE/'package-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('dxf_checks','artifact_sha256')},indent=2))
if __name__=='__main__':main()
