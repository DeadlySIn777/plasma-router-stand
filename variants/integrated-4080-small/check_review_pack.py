"""Reconcile the review packet without converting scoped passes to a release."""
from pathlib import Path
import hashlib,json
from decimal import Decimal
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SPECS=[
 ('output/assembly-check.json','passed'),
 ('output/integration-clearance-check.json','passed'),
 ('output/frame-gantry-check.json','passed'),
 ('output/gantry-joint/gantry-joint-check.json','passed'),
 ('head/output/quick-dock/quick-dock-check.json','known_dock_static_and_removal_checkpoints_passed'),
 ('head/output/plasma-quick-dock/plasma-dock-check.json','known_shared_plasma_interface_passed'),
 ('head/output/selected-head-pack/selected-head-pack-check.json','stock_nest_and_takeoff_passed'),
 ('atc/output/atc-integration-check.json','passed'),
 ('atc/output/er11-retained-capacity-check.json','passed'),
 ('bed/output/stay-pivot-retention-check.json','passed'),
 ('bed/output/profile-fastener-retention-check.json','passed'),
 ('bed/output/bed-handling-reach-screen.json','source_consistent'),
 ('bed/output/bed-local-check.json','passed'),
 ('bed/output/bed-machine-changeover-check.json','passed'),
 ('bed/output/pan-front-structure-screen.json','passed_without_composite_credit'),
 ('utilities/output/utility-check.json','passed_static_geometry'),
 ('utilities/output/lowered-wet-fabrication-check.json','passed_local_fabrication_geometry'),
 ('utilities/output/guide-handling-check.json','passed'),
 ('output/front-stop-bed-clearance/front-stop-bed-clearance-check.json','passed'),
 ('manufacturing/manufacturing-check.json','passed'),
 ('manufacturing/procurement-check.json','requirements_reconciled'),
 ('manufacturing/cart-coverage-check.json','source_and_cart_arithmetic_passed')]

SPECS.append(('optimization/comparison.json','passed'))
SPECS.append(('../../output/pdf/integrated-4080-review-qa.json','visual_layout_passed'))

def run():
 records=[];stale=[]
 for name,key in SPECS:
  p=HERE/name;j=json.loads(p.read_text(encoding='utf-8-sig'));current=[]
  for n,h in j.get('source_sha256',j.get('source_bindings',{})).items():
   if isinstance(h,dict):n,h=h['file'],h['sha256']
   candidates=[ROOT/Path(n),HERE/Path(n),p.parent/Path(n),p.parent.parent/Path(n)]
   source=next((x for x in candidates if x.is_file()),None)
   passed=source is not None and sha(source)==h
   row=dict(source=n,passed=passed);current.append(row)
   if not passed:stale.append(dict(report=name,source=n))
  output_hashes=dict(j.get('output_sha256',j.get('artifact_sha256',{})))
  if 'pdf_sha256'in j:
   output_hashes[j['pdf']]=j['pdf_sha256']
   output_hashes.update(j['render_sha256'])
  for n,h in output_hashes.items():
   candidates=[ROOT/Path(n),HERE/Path(n),p.parent/Path(n),p.parent.parent/Path(n)]
   artifact=next((x for x in candidates if x.is_file()),None)
   passed=artifact is not None and sha(artifact)==h
   current.append(dict(artifact=n,passed=passed))
   if not passed:stale.append(dict(report=name,artifact=n))
  consistency=[v for k,v in j.items()if k.startswith('source_consistent')]
  records.append(dict(report=name,sha256=sha(p),status_key=key,
   passed=bool(j[key])and all(consistency)and all(x['passed']for x in current),source_checks=len(current)))
 budget=json.loads((HERE/'manufacturing/price-and-budget-register.json').read_text())
 assert budget['budget_gate']=='FAIL'and budget['complete_delivered_total_USD']is None
 core=sum(Decimal(r['extended_USD']) for r in budget['rows']if r['id']in('20100_BED','HDPE_RAW','RAPIDCHANGE_BASIC4'))
 assert core==Decimal(budget['three_core_goods_basis_USD'])
 assembly=json.loads((HERE/'output/assembly-check.json').read_text())
 artifacts={}
 for mode in('WOOD','PLASMA','CHANGEOVER'):
  for ext in('step','png'):
   p=HERE/'output'/f'INTEGRATED_4080_SMALL_{mode}.{ext}'
   assert p.is_file()
   expected=assembly['assemblies'][mode]['sha256']if ext=='step'else assembly['assemblies'][mode]['preview']['sha256']
   assert sha(p)==expected,(mode,ext,'Artifact differs from verified assembly')
   artifacts[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
 p=ROOT/'output/pdf/plasma-router-stand-integrated-4080-review.pdf';assert p.is_file()
 artifacts[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
 result=dict(review_packet_reconciled=all(r['passed']for r in records)and not stale,
  reports=records,stale_sources=stale,artifacts=artifacts,
  source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
  requirements_complete=False,budget_cap_USD=1000,delivered_budget_verified=False,
  current_three_core_goods_basis_USD=float(core),complete_delivered_total_USD=None,
  fabrication_release=False,CAM_release=False,operating_release=False,
  limitations='Source-bound review evidence only. Actual received vendor interfaces, working boot registration, full rigidity, physical retention/handling qualification, controls and complete delivered cost remain open. Nominal retention geometry passes; a reconciled packet is not a completed machine.')
 (HERE/'output/review-pack-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(review_packet_reconciled=result['review_packet_reconciled'],stale=stale,
  failed=[r['report']for r in records if not r['passed']],requirements_complete=False,budget='FAIL')))
 return 0 if result['review_packet_reconciled']else 1

if __name__=='__main__':raise SystemExit(run())
