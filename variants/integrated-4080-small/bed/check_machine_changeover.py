"""Continuous rigid-deck changeover against the final actual machine context.

Telescoping assist is explicitly sampled. This does not assert fall-arrest or
operation qualification. The independent local bed proof remains unchanged.
"""
from pathlib import Path
import hashlib,json,os,sys,math,types
import cadquery as cq
import integrated_bed as B
import build_bed as V

HERE=Path(__file__).resolve().parent;ROOT=B.ROOT;OUT=HERE/'output'
sys.path.insert(0,str(HERE.parent))
import assembly as A
import integrated_utilities as U

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sources():
 # Bind the imported primary CAD bytes as well as the Python factories.
 # The manufacturer housing is an actual fixed obstacle in this proof;
 # changing its STEP must invalidate the result even if Python is unchanged.
 result={Path(__file__),HERE/'output/bed-local-check.json',Path(A.A.VENDOR_HOUSING_SOURCE),Path(A.H.CLAMP),Path(A.H.BOOT)}
 queue=list(sys.modules.values());seen=set()
 while queue:
  m=queue.pop()
  if id(m) in seen:continue
  seen.add(id(m))
  name=getattr(m,'__file__',None)
  if name:
   p=Path(name)
   if p.suffix=='.py'and p.is_relative_to(ROOT):
    result.add(p)
    queue.extend(v for v in vars(m).values()if isinstance(v,types.ModuleType))
 return sorted(result)
def digest(paths):return{p.relative_to(ROOT).as_posix():sha(p)for p in paths}

def continuous_pair(s,obstacle,a,b,depth=0):
 bb=V.swept_box(s,a,b)
 if not V.overlap(bb,B.bounds(obstacle)):return(True,1,0,None)
 mid=(a+b)/2
 at=s.rotate((0,B.PIVOT[0],B.PIVOT[1]+B.ASSEMBLY_Z_SHIFT),(1,B.PIVOT[0],B.PIVOT[1]+B.ASSEMBLY_Z_SHIFT),mid)
 displacement=2*V.radial_bound(s)*math.sin(math.radians((b-a)/4))
 gap=at.distance(obstacle)
 if gap>displacement+1e-6:return(True,0,1,None)
 volume=abs(at.intersect(obstacle).Volume())
 if volume>.02:return(False,0,1,dict(angle_deg=mid,intersection_mm3=volume,kind='exact_intersection'))
 if depth>=12 or b-a<.002:return(False,0,1,dict(angle_deg=mid,intersection_mm3=volume,kind='unresolved_enclosure'))
 left=continuous_pair(s,obstacle,a,mid,depth+1)
 if not left[0]:return left
 right=continuous_pair(s,obstacle,mid,b,depth+1)
 return(right[0],left[1]+right[1],left[2]+right[2],right[3])

def hinge_pin_service(external):
 """Exact axial-cylinder covers prove both inboard removal/insertion paths.

 Filling the cross drilling adds material conservatively. The coaxial land
 and head each translate continuously along their own X axis, so elongating
 each cylinder by the26mmstroke exactly covers its complete sweep.
 """
 closed=B.bed_parts(0);results=[]
 for side in('L','R'):
  sweep=B.cyl(12,24.05+26,(51.15,*B.PIVOT),(1,0,0)).fuse(B.cyl(18,3+26,(75.2,*B.PIVOT),(1,0,0))).clean()
  sweep=B._mirror(sweep,side).translate((0,0,B.ASSEMBLY_Z_SHIFT))
  removed={f'BED_HINGE_PIN_{side}',f'BED_HINGE_RETAINER_WASHER_{side}',f'BED_HINGE_RETAINER_COTTER_{side}'}
  obstacles=external+[(p['id'],p['shape'],p['color'])for p in closed if p['id']not in removed]
  result=V.exact_pairs([dict(id=f'HINGE_PIN_SERVICE_SWEEP_{side}',shape=sweep)],obstacles)
  # Outside washer comes off before the plain pin moves. A coaxial annular
  # extrusion exactly covers its full6mmoutward translation and retains
  # the actual pin as an obstacle, including the cross-drilled running land.
  washer=B.ring(18,12.2,7.6,(49.45,*B.PIVOT),(1,0,0))
  washer=B._mirror(washer,side).translate((0,0,B.ASSEMBLY_Z_SHIFT))
  washer_obstacles=external+[(p['id'],p['shape'],p['color'])for p in closed if p['id']not in{f'BED_HINGE_RETAINER_WASHER_{side}',f'BED_HINGE_RETAINER_COTTER_{side}'}]
  washer_result=V.exact_pairs([dict(id=f'HINGE_WASHER_SERVICE_SWEEP_{side}',shape=washer)],washer_obstacles)
  # Straighten the sacrificial cotter legs before removal. Its D2 central
  # material then pulls through the actual D2.2 cross-hole along-frontY.
  # The head-loop box stays outside the shaft and conservatively encloses
  # every position of the YZ-oriented loop during the20mm withdrawal.
  cy,zz=B.PIVOT
  cotter=B.cyl(2,36.75,(54.35,cy-28.75,zz),(0,1,0)).fuse(B.box(53.85,cy-33.125,zz-2.5,1.,25.,5.)).clean()
  cotter=B._mirror(cotter,side).translate((0,0,B.ASSEMBLY_Z_SHIFT))
  cotter_obstacles=external+[(p['id'],p['shape'],p['color'])for p in closed if p['id']!=f'BED_HINGE_RETAINER_COTTER_{side}']
  cotter_result=V.exact_pairs([dict(id=f'HINGE_COTTER_SERVICE_SWEEP_{side}',shape=cotter)],cotter_obstacles)
  results.append(dict(side=side,withdrawal_mm=26,direction='inboard',swept_bounds_mm=B.bounds(sweep),
    removed_before_withdrawal=[f'BED_HINGE_RETAINER_COTTER_{side}',f'BED_HINGE_RETAINER_WASHER_{side}'],
    washer_withdrawal=dict(stroke_mm=6,direction='outward',**washer_result),
    straightened_cotter_withdrawal=dict(stroke_mm=20,direction='front-negativeY',bent_tails_straightened_first=True,**cotter_result),
    **result))
 return dict(passed=all(q['passed']and q['washer_withdrawal']['passed']and q['straightened_cotter_withdrawal']['passed']for q in results),continuous_material_cover=True,paths=results,
  prerequisites='Closeddeckexternallysupportedandunloaded;headremoved,motionlockedinqualifiedrearpark. Unbend/removeanddiscardcotter,removeouterwasher,thenwithdrawpin26mminboard. Capturetheaxialshim. Installationisthereversepathwithanewcotter. Thisisgeometryonly,notsupport/liftqualification.')

def run():
 paths=sources();start=digest(paths)
 (OUT/'bed-machine-changeover-live-witnesses.json').write_text('[]\n',encoding='utf-8')
 local=json.loads((OUT/'bed-local-check.json').read_text(encoding='utf-8'))
 assert local['passed']and local['source_consistent_during_build']
 for n,h in local['source_sha256'].items():assert sha(ROOT/n)==h,n
 park=dict(gantry_y=1275.,head_x=975.,z_lift=250.,module_removed=True,spindle_context=False)
 motion=A.integrated_motion(False,**park)
 frame=A.M.frame_parts();wet=U.utility_parts(guards_fitted=False)
 atc=A.A.actual_atc_parts(200.,hood='fitted',include_allocations=True)
 external=frame+wet+motion+atc
 invalid=[n for n,s,_ in external if not s.isValid()or not s.Solids()or s.Volume()<=0]
 assert not invalid,invalid
 static={name:V.exact_pairs(B.bed_parts(a),external)for name,a in(('closed',0.),('upright',90.))}
 print('MACHINE_STATIC',[(k,r['passed'],r['unexpected'])for k,r in static.items()],flush=True)
 service=hinge_pin_service(external)
 print('HINGE_PIN_SERVICE',service['passed'],[(q['side'],q['unexpected'])for q in service['paths']],flush=True)
 moving=[p for p in B.bed_parts(0)if p['moving_bed']]
 fixed=[(n,s,B.bounds(s))for n,s,_ in external]
 failures=[];pairs=boxes=distances=0
 for p in moving:
  for lo in range(0,90,5):
   bb=V.swept_box(p['shape'],lo,lo+5)
   for n,s,fb in fixed:
    pairs+=1
    if not V.overlap(bb,fb):boxes+=1;continue
    okay,nb,nd,witness=continuous_pair(p['shape'],s,lo,lo+5);boxes+=nb;distances+=nd
    if not okay:
     failure=dict(moving=p['id'],fixed=n,angle_range_deg=[lo,lo+5],witness=witness)
     failures.append(failure);print('MACHINE_WITNESS',json.dumps(failure),flush=True)
     (OUT/'bed-machine-changeover-live-witnesses.json').write_text(json.dumps(failures,indent=2)+'\n',encoding='utf-8')
  if p['id'].startswith(('FULL_','BED_4080','BED_HINGE_MOVING','BED_ASSIST')):print('MACHINE_ROTATION',p['id'],len(failures),flush=True)
 assist=[]
 for angle in range(0,91,10):
  ps=[p for p in B.bed_parts(float(angle))if p['id'].startswith(('BED_GAS','BED_CAPTURE','BED_FULL_OPEN'))]
  q=V.exact_pairs(ps,external)
  assist.append(dict(angle_deg=angle,**q));print('MACHINE_ASSIST',angle,q['passed'],q['unexpected'],flush=True)
 source_current=paths==sources() and start==digest(paths)
 allboxes=[V.swept_box(p['shape'],0,90)for p in moving]
 envelope=[min(b[k]for b in allboxes)for k in range(3)]+[max(b[k+3]for b in allboxes)for k in range(3)]
 report=dict(study='FULL_BED_CHANGEOVER_ACTUAL_FIXED_DOCK_FRAME_ATC_AND_UTILITIES',source_sha256=start,
  source_consistent_during_check=source_current,
  source_paths_added_during_check=[p.relative_to(ROOT).as_posix()for p in set(sources())-set(paths)],
  local_evidence=dict(file='output/bed-local-check.json',sha256=sha(OUT/'bed-local-check.json'),passed=True),
  machine_park=park,ATC=dict(deployment_mm=200,hood='fitted',capacity_envelopes_included=True),
  utilities=dict(guards_fitted=False,stored_screen_racks_included=True,actual_rerouted_gravity_hose_included=True),
  external_component_count=len(external),static=static,
  front_hinge_pin_service=service,
  continuous_rigid_bed=dict(passed=not failures,rigid_parts=len(moving),interval_deg=5,enumerated_pairs=pairs,
    AABB_certificates=boxes,exact_distance_certificates=distances,unresolved=failures,swept_enclosing_bounds_mm=envelope,
    proof='Continuous trigonometric corner bounds on every material-part AABB; exact distance at interval midpoint exceeds angular displacement bound, or adaptive subdivision. No finite pose sampling is called a rigid-bed path proof.'),
  telescoping_assist=dict(sampled_poses=assist,continuous_motion_proved=False,scope='Ten exact finite poses only, inherited local internal checks remain source bound.'),
  whole_head_removed=True,fabrication_release=False,lift_operation_release=False,
  status_scope='Nominal boundary geometry and source fidelity. Actual gas dimensions/force, catch/impact control, joint/material strength and physical handling remain separate acceptance gates.')
 report['passed']=source_current and all(r['passed']for r in static.values())and service['passed']and not failures and all(r['passed']for r in assist)
 (OUT/'bed-machine-changeover-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=report['passed'],source_current=source_current,external_count=len(external),pairs=pairs,unresolved=failures,envelope=envelope)),flush=True)
 return 0 if report['passed']else 1

if __name__=='__main__':
 try:code=run()
 except Exception:
  import traceback;traceback.print_exc();code=2
 sys.stdout.flush();sys.stderr.flush();os._exit(code)
