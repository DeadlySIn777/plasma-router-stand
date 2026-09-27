"""Check current report bindings and exact active exports; publish one acceptance index."""
from pathlib import Path
import json,hashlib,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 current=HERE/'verification.json';old=json.loads(current.read_text())
 if 'checks' in old:(HERE/'geometry-verification.json').write_text(current.read_text(),encoding='utf-8')
 reports=[HERE/'geometry-verification.json',HERE/'structure-check.json',HERE/'supplement-check.json',HERE/'panel-transfer-check.json',HERE/'routes/spoil/spoil-transfer-check.json',HERE/'routes/beam/beam-path-check.json']
 bindings={};issues=[];records=[]
 for p in reports:
  r=json.loads(p.read_text());sources=r.get('new_variant_source_sha256',r.get('source_sha256',{}))
  for k,v in sources.items():
   q=ROOT/k
   if not q.is_file() or sha(q)!=v:issues.append({'report':p.name,'stale_source':k})
   if k in bindings and bindings[k]!=v:issues.append({'conflicting_source':k})
   bindings[k]=v
  # The geometry report binds exchange files; other scopes bind their sources.
  for k,v in r.get('artifact_sha256',{}).items():
   if not (ROOT/k).is_file() or sha(ROOT/k)!=v:issues.append({'report':p.name,'stale_artifact':k})
  passed=r.get('passed',False)
  if not passed:issues.append({'report_failed':p.name})
  records.append({'report':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'passed':passed})
 certificate=json.loads((HERE/'annotation-equivalence.json').read_text())
 geometry=json.loads((HERE/'geometry-verification.json').read_text())
 # Fresh exports bind their own bytes. A run which intentionally preserved the
 # earlier STEP files must additionally validate the migration certificate.
 if any(r.get('existing_geometry_preserved') for r in geometry.get('context_exports',[])):
  if not certificate.get('passed') or certificate.get('new_build_sha256')!=sha(HERE/'build.py') or certificate.get('differences') or len(certificate.get('states',[]))!=3 or any(r.get('bodies')!=270 or r.get('world_and_local_differences')!=0 for r in certificate.get('states',[])):
   issues.append({'annotation_equivalence_certificate':'invalid or stale'})
  for k,v in certificate.get('preserved_step_sha256',{}).items():
   if not (ROOT/k).is_file() or sha(ROOT/k)!=v:issues.append({'preserved_step_changed':k})
  if certificate.get('new_dxf_sha256')!=sha(HERE/'output/dxf/SM_BASE_STRIP_1.dxf'):issues.append({'annotation_dxf':'changed after correction'})
 ops=json.loads((HERE/'output/part-operations.json').read_text());inventory={}
 for folder,ext,predicate in [('parts','.step',lambda r:not r['individual_export_guarded']),('dxf','.dxf',lambda r:not r['individual_export_guarded'] and r['manufacturing_flat'])]:
  expected={r['part_number']+ext for r in ops if predicate(r)};actual={p.name for p in (HERE/'output'/folder).glob('*'+ext)}
  inventory[folder]={'expected':len(expected),'actual':len(actual),'missing':sorted(expected-actual),'stale':sorted(actual-expected)}
  if expected!=actual:issues.append({'inventory':folder,**inventory[folder]})
 for p in [Path(__file__),HERE/'README.md']:
  bindings[p.relative_to(ROOT).as_posix()]=sha(p)
 artifact_paths=reports+[HERE/'annotation-equivalence.json']+list((HERE/'output').glob('*.json'))+list((HERE/'output').glob('*.csv'))+[p for f in ('step','parts','dxf') for p in (HERE/'output'/f).glob('*') if p.is_file()]
 g=json.loads((HERE/'geometry-verification.json').read_text());pan=json.loads((HERE/'panel-transfer-check.json').read_text());sp=json.loads((HERE/'routes/spoil/spoil-transfer-check.json').read_text());be=json.loads((HERE/'routes/beam/beam-path-check.json').read_text())
 r={'passed':not issues,'status':'MODELED CARRIER AND BOUNDED RIGID-PART CHECKS; NOT OPERATIONAL ATC RELEASE','source_sha256':bindings,'artifact_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in artifact_paths},'reports':records,'inventory':inventory,'mechanism_parts':270,'full_context_bodies':1940,'counts':{'carrier_translations':len(g['checks']['carrier_translation']['records']),'moving_axis_swept_envelopes':g['checks']['full_800x1000x200_parked_swept_box_screen']['axis_parts'],'pin_configurations':13,'panel_segments':sum(len(p['segments']) for p in pan['panels']),'spoilboard_segments':sum(len(p['phases']) for p in sp['records']),'beam_segments':sum(len(p['phases']) for p in be['records'])},'issues':issues,'open_release_items':['Exact selected magazine body, pocket and attachment CAD, cover and loaded-tool projections.','Selected Z200 module dimensions, mounting, retention, actual nut datum and full machine stiffness.','Small dust-cover mechanism and flexible cable/hose routing: automatic profile disabled.','Return spring catalog/actual force, Delta blind thread and clevis depths, hot solenoid pull/friction and sensor commissioning.','Real loaded-pocket repeatability and reaction forces; assumed150N/19Nm screens are not system qualification.','Rigid spoil/panel/beam paths proved only under explicit staged restraint/tool/fastener preconditions; hands, loose hardware transfer and flexible leads excluded.']}
 current.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':r['passed'],'counts':r['counts'],'inventory':inventory,'issues':issues},indent=2));return 0 if r['passed'] else 2
if __name__=='__main__':sys.exit(main())

