"""Independently verify bed STEP readbacks with adaptive volume integration.

Reuses unchanged source-bound geometry certificates, regenerates both expected
factories, and preserves the default-quadrature diagnostic. Acceptance remains
strict: valid BReps, exact solid count, bounds1e-5mm and relative volume1e-7.
"""
from pathlib import Path
import hashlib,json,os,sys
import cadquery as cq
import integrated_bed as B

HERE=Path(__file__).resolve().parent;OUT=HERE/'output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 path=OUT/'bed-local-check.json';report=json.loads(path.read_text(encoding='utf-8'))
 diagnostic=OUT/'bed-local-nonadaptive-export-diagnostic.json'
 if not report.get('adaptive_export_verification'):
  diagnostic.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 original=json.loads(diagnostic.read_text(encoding='utf-8'))
 sources=dict(original['source_sha256'])
 sources.update({Path(__file__).relative_to(B.ROOT).as_posix():sha(Path(__file__)),diagnostic.relative_to(B.ROOT).as_posix():sha(diagnostic)})
 for name,h in sources.items():assert sha(B.ROOT/name)==h,name
 assert original['source_consistent_during_build']
 assert all(q['passed']for q in original['static_self'].values())
 assert all(q['passed']for q in original['static_external'].values())
 assert original['continuous_rigid_deck']['passed']and not original['continuous_rigid_deck']['unresolved']
 assert all(q['passed']for q in original['telescoping_assist_sampled_poses'])
 assert all(q['valid']for q in original['custom_parts'].values())
 rows=[]
 for mode,angle in(('wood',0.),('upright',90.)):
  parts=B.bed_parts(angle);expected=cq.Compound.makeCompound([p['shape']for p in parts])
  record=report['exports'][mode];step=HERE/record['file']
  assert sha(step)==original['exports'][mode]['sha256'],step
  back=cq.importers.importStep(str(step)).val()
  expected_count=sum(len(p['shape'].Solids())for p in parts)
  assert expected.isValid()and back.isValid()
  assert len(back.Solids())==expected_count==len(expected.Solids())
  ev=expected.Volume(1e-8);bv=back.Volume(1e-8);error=abs(ev-bv)
  tolerance=max(.5,abs(ev)*1e-7)
  bound_error=max(abs(x-y)for x,y in zip(B.bounds(expected),B.bounds(back)))
  assert error<=tolerance and bound_error<=1e-5,(mode,error,tolerance,bound_error)
  record.update(valid=True,volume_error_mm3=error,expected_adaptive_volume_mm3=ev,
   readback_adaptive_volume_mm3=bv,volume_acceptance_mm3=tolerance,bounds_error_mm=bound_error,
   original_default_volume_error_mm3=original['exports'][mode]['volume_error_mm3'])
  rows.append(dict(mode=mode,solids=expected_count,adaptive_error_mm3=error,bounds_error_mm=bound_error))
 current=all(sha(B.ROOT/name)==h for name,h in sources.items())
 assert current
 report.update(source_sha256=sources,adaptive_export_verification=dict(
  script=Path(__file__).relative_to(B.ROOT).as_posix(),quadrature_tolerance=1e-8,
  volume_acceptance='max(0.5mm3,expected_adaptive_volume*1e-7)',bounds_acceptance_mm=1e-5,
  exact_solid_count_required=True,source_consistent=True,
  original_diagnostic=diagnostic.relative_to(HERE).as_posix(),results=rows),passed=True)
 path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=True,source_current=current,results=rows)),flush=True)
 return 0

if __name__=='__main__':
 try:code=run()
 except Exception:
  import traceback;traceback.print_exc();code=2
 sys.stdout.flush();sys.stderr.flush();os._exit(code)
