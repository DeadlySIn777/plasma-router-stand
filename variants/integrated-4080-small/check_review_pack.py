"""Reconcile the review packet without converting scoped passes to a release."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SPECS=[
 ('output/assembly-check.json','passed'),
 ('output/integration-clearance-check.json','passed'),
 ('output/frame-gantry-check.json','passed'),
 ('head/output/quick-dock/quick-dock-check.json','known_dock_static_and_removal_checkpoints_passed'),
 ('head/output/plasma-quick-dock/plasma-dock-check.json','known_shared_plasma_interface_passed'),
 ('head/output/selected-head-pack/selected-head-pack-check.json','stock_nest_and_takeoff_passed'),
 ('atc/output/atc-integration-check.json','passed'),
 ('bed/output/bed-local-check.json','passed'),
 ('bed/output/bed-machine-changeover-check.json','passed'),
 ('bed/output/pan-front-structure-screen.json','passed_without_composite_credit'),
 ('utilities/output/utility-check.json','passed_static_geometry'),
 ('utilities/output/guide-handling-check.json','passed'),
 ('output/front-stop-bed-clearance/front-stop-bed-clearance-check.json','passed'),
 ('manufacturing/manufacturing-check.json','passed')]

def run():
 records=[];stale=[]
 for name,key in SPECS:
  p=HERE/name;j=json.loads(p.read_text(encoding='utf-8-sig'));current=[]
  for n,h in j.get('source_sha256',{}).items():
   if isinstance(h,dict):n,h=h['file'],h['sha256']
   candidates=[ROOT/Path(n),HERE/Path(n),p.parent/Path(n)]
   source=next((x for x in candidates if x.is_file()),None)
   passed=source is not None and sha(source)==h
   row=dict(source=n,passed=passed);current.append(row)
   if not passed:stale.append(dict(report=name,source=n))
  consistency=[v for k,v in j.items()if k.startswith('source_consistent')]
  records.append(dict(report=name,sha256=sha(p),status_key=key,
   passed=bool(j[key])and all(consistency)and all(x['passed']for x in current),source_checks=len(current)))
 budget=json.loads((HERE/'manufacturing/price-and-budget-register.json').read_text())
 assert budget['budget_gate']=='FAIL'and budget['complete_delivered_total_USD']is None
 assert budget['three_core_goods_basis_USD']=='1060.35'
 artifacts={}
 for mode in('WOOD','PLASMA','CHANGEOVER'):
  for ext in('step','png'):
   p=HERE/'output'/f'INTEGRATED_4080_SMALL_{mode}.{ext}'
   assert p.is_file();artifacts[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
 p=ROOT/'output/pdf/plasma-router-stand-integrated-4080-review.pdf';assert p.is_file()
 artifacts[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
 result=dict(review_packet_reconciled=all(r['passed']for r in records)and not stale,
  reports=records,stale_sources=stale,artifacts=artifacts,
  source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
  requirements_complete=False,budget_cap_USD=1000,delivered_budget_verified=False,
  current_three_core_goods_basis_USD=1060.35,complete_delivered_total_USD=None,
  fabrication_release=False,CAM_release=False,operating_release=False,
  limitations='Source-bound review evidence only. Actual vendor interfaces, working boot registration, full rigidity, final pin retention/handling, controls and complete delivered cost remain open. A reconciled packet is not a completed machine.')
 (HERE/'output/review-pack-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(review_packet_reconciled=result['review_packet_reconciled'],stale=stale,
  failed=[r['report']for r in records if not r['passed']],requirements_complete=False,budget='FAIL')))
 return 0 if result['review_packet_reconciled']else 1

if __name__=='__main__':raise SystemExit(run())
