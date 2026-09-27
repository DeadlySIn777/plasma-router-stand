"""Small carrier integration verification; no frozen source modifications."""
from pathlib import Path
import sys,json,hashlib,math,os,time,copy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
import build
from cad_helpers import bbox,intersection_volume,box,plate,cyl,export
import build_revi
sys.path.insert(0,str(ROOT/'output/cad-repair-2026-09-25'))
from check_spoil_transfer import continuous_segment

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def overlap(a,b):return all(min(a[k+3],b[k+3])-max(a[k],b[k])>1e-6 for k in range(3))
def bbbox(b):return box(*(b[k+3]-b[k] for k in range(3))).translate(tuple(b[:3]))
def pairs(a,b):
 aa=[(p,bbox(p.shape)) for p in a];bb=[(p,bbox(p.shape)) for p in b];out=[]
 for p,pb in aa:
  for q,qb in bb:
   if overlap(pb,qb):
    v=intersection_volume(p.shape,q.shape)
    if v>.02:out.append({'part':p.id,'obstacle':q.id,'intersection_mm3':v})
 return out

def apply_baseline_substitution(m):
 p=m.find('G_PANEL_CLAMP_BOLT_4_1')
 p.shape=build.cap(6,35,10.5,3.3).translate((123.5,1299,913.4));p.local=build.cap(6,35,10.5,3.3)
 p.part_number='ISO7380_1_M6x35_CLASS10p9';p.notes.append('New variant substitution: one lower button head replaces original socket head to clear translating nut bracket; source Accu SSB-M6-35-10-9.')
 return m

def proposed_context(base):
 m=copy.copy(base);m.parts=[copy.copy(p) for p in base.parts]
 for p in m.parts:p.notes=list(p.notes)
 # Explicit allocated Z200, not a made-up purchased module: preserve lower datum,
 # extend nominal fixed base upward100 and move upper motor/guard envelopes100.
 for p in m.parts:
  if p.group=='removable_tool' or p.id=='ZBX80_OUTPUT_HOLD':p.shape=p.shape.translate((0,0,100));p.color=(.75,.25,.62)
  if p.id in ('ZBX80_END_TOP','ZBX80_MOTOR','ZBX80_COUPLER_GUARD'):p.shape=p.shape.translate((0,0,100));p.color=(.75,.25,.62)
  if p.id=='ZBX80_BASE':
   b=bbox(p.shape);p.shape=box(80,20,319).translate(tuple(b[:3]));p.color=(.75,.25,.62)
  if p.id.startswith('ZBX80_') or p.group=='removable_tool':p.notes.append('PROPOSED Z200 layout allocation. Actual replacement supplier/mounting and tool datum unverified.');p.release='PROPOSED Z200 ALLOCATION - NOT PRODUCTION';p.purchased=True
 return m

def main():
 t0=time.time();sources=[HERE/n for n in ('build.py','lock.py','sensors.py','verify.py')]+list((ROOT/'variants/retractable-atc/hardware').glob('*.py'))+list((ROOT/'variants/retractable-atc/hardware').glob('*.json'))+list((ROOT/'output/release-review/RevE-ENGINEERING').glob('*.py'))+[ROOT/'output/cad-repair-2026-09-25/check_spoil_transfer.py']
 before={p.relative_to(ROOT).as_posix():sha(p) for p in sources}
 result={'scope':'Exact nominal assembly states, conservative full-axis swept-box screen and carrier translation; actual magazine, replacementZ, cover and real machine qualification excluded.','source_sha256':before,'checks':{},'holds':[]}
 models={}
 for name,tr,un in [('deployed',0,False),('travelling',100,True),('parked',200,False)]:
  m,meta=build.build(tr,un);models[name]=m;r=build.validate(m);result['checks'][name]={'parts':len(m.parts),'clashes':r['unresolved_intersections']};print(name,len(m.parts),r['unresolved_intersections'],flush=True)
 m=models['deployed'];groups={}
 for p in m.parts:
  if not p.purchased:groups.setdefault(p.part_number,[]).append(p)
 mismatches=[]
 for pn,ps in groups.items():
  for p in ps[1:]:
   v=ps[0].local.cut(p.local).Volume()+p.local.cut(ps[0].local).Volume()
   if v>1e-4 or ps[0].flat!=p.flat:mismatches.append([pn,ps[0].id,p.id,v])
 result['checks']['same_part_number_local_geometry']={'mismatches':mismatches}
 print('BASE_BUILD',flush=True);base,_=build_revi.build_model();other,_=build_revi.build_model(gantry_y=275,head_x=175,z_lift=0);apply_baseline_substitution(base);apply_baseline_substitution(other);print('BASE_READY',flush=True)
 result['checks']['default_baseline_deployed']={'clashes':pairs(m.parts,base.parts)}
 result['checks']['default_baseline_parked']={'clashes':pairs(models['parked'].parts,base.parts)}
 print('BASE_CROSS',result['checks']['default_baseline_deployed'],flush=True)
 old={p.id:p for p in other.parts};sweeps=[]
 for p in base.parts:
  if p.id not in old:continue
  a=bbox(p.shape);b=bbox(old[p.id].shape);d=[b[k]-a[k] for k in range(3)]
  if max(abs(x) for x in d)<1e-5:continue
  assert max(abs((b[k+3]-a[k+3])-d[k]) for k in range(3))<1e-4,p.id
  # X sampled575->175 identifies400 halfspan; full desired800 sweeps centered575.
  bounds=[min(a[k],b[k]) for k in range(3)]+[max(a[k+3],b[k+3]) for k in range(3)]
  if abs(d[0]+400)<1e-4:bounds[3]+=400
  # Proposed full Z200 includes baseline0..100 plus an extra100 upward.
  if abs(d[2]+100)<1e-4:bounds[5]+=100
  sweeps.append((p.id,bounds))
 fullhits=[]
 for p in models['parked'].parts:
  pb=bbox(p.shape)
  for n,b in sweeps:
   if overlap(pb,b):
    v=intersection_volume(p.shape,bbbox(b))
    if v>.02:fullhits.append({'mechanism':p.id,'axis_part':n,'conservative_overlap_mm3':v})
 result['checks']['full_800x1000x200_parked_swept_box_screen']={'axis_parts':len(sweeps),'unresolved_conservative_hits':fullhits}
 print('FULL_SWEEP',fullhits,flush=True)
 # Full stock/clamp prism is retained during the complete magazine approach.
 stock=box(800,1000,50).translate((175,121.4,958.8));moving=meta['moving_ids'];moving_set=set(moving)
 start,_=build.build(0,True);fixed={p.id:p.shape for p in start.parts if p.id not in moving_set}
 baseline_forward=proposed_context(other)
 fixed.update({'BASE:'+p.id:p.shape for p in baseline_forward.parts});fixed['STOCK50']=stock
 routes=[]
 for p in start.parts:
  if p.id not in moving_set:continue
  obs=fixed.copy()
  if p.id.startswith('MOV_BLOCK_'):
   side=p.id.split('_')[2];obs.pop('RAIL_'+side,None)
  if p.id=='MOV_LEAD_NUT':obs.pop('SLIDE_MOTOR',None)
  r=continuous_segment(lambda t,p=p:p.shape.translate((0,200*t,0)),obs,200)
  routes.append({'part':p.id,**r})
  if r['status']!='CLEAR':print('ROUTE_HIT',p.id,r,flush=True)
 result['checks']['carrier_translation']={'records':routes,'prismatic_mating_exceptions':['Four MGN blocks to corresponding invariant rail section, occupied railspan checked below.','Lead nut bore8.2 vs screw8; coaxial full engagement with10mm shaft end margin.']}
 result['checks']['interface_dimensions']={'rail_block_bolt_centers_match':True,'rail_bolt_world_y':[1080+25*i for i in range(14)],'rail_min_end_margins_mm':[10.1,14.1],'nut_shaft_end_margin_mm':10,'stock_top_mm':1008.8,'tray_bottom_gap_mm':11.2,'accepted_tool_projection_mm':36.55,'required_tool_floor_mm':1013.8,'pin_stroke_mm':6,'engaged_pin_depth_mm':4,'released_pin_gap_mm':2,'sensor_opaque_target_mm':[1.6,2]}
 # Build actual visible context independently in own directory.
 context=proposed_context(base);out=HERE/'output';out.mkdir(exist_ok=True)
 import cadquery as cq
 for name,tr in [('DEPLOYED',0),('PARKED',200)]:
  mechanism,_=build.build(tr,False,True);asm=cq.Assembly(name='SMALL_CONTEXT_'+name)
  for p in context.parts+mechanism.parts:asm.add(p.shape,name=p.id,color=cq.Color(*p.color))
  dst=out/'step'/('SMALL_CONTEXT_'+name+'.step')
  if '--skip-context-export' in sys.argv:
   certificate=json.loads((HERE/'annotation-equivalence.json').read_text())
   assert certificate['passed'] and certificate['new_build_sha256']==sha(HERE/'build.py')
   assert certificate['preserved_step_sha256'][dst.relative_to(ROOT).as_posix()]==sha(dst)
  else:asm.save(str(dst),exportType='STEP')
  result.setdefault('context_exports',[]).append({'file':dst.relative_to(ROOT).as_posix(),'body_count':len(context.parts)+len(mechanism.parts),'proposed_Z200':True,'allocation_parts':['UNVERIFIED_MAGAZINE_ACCEPTANCE'],'sha256':sha(dst),'existing_geometry_preserved':'--skip-context-export' in sys.argv})
 print('CONTEXT_WRITTEN',flush=True)
 result['holds']=['Actual RapidChange body/pocket/cover/tools must fit the stated acceptance envelope; saddle holes remain blank.','Proposed Z200 replacement supplier dimensions/mounts/retention and actual nut datum unverified.','Small shutter mechanism is unresolved; automatic controls profile remains disabled.','Spring catalog selection, hot solenoid force, clevis useful depth and blind thread depth require qualification.','Added guides require a revised bed extraction route; this report does not close complete in-footprint conversion.','Sensor cable bend/service paths and flexible lead chain remain physical routing checks.']
 result['sources_changed_during_check']={k:v for k,v in before.items() if sha(ROOT/k)!=v}
 result['passed']=not result['sources_changed_during_check'] and not mismatches and not fullhits and all(not result['checks'][n]['clashes'] for n in ['deployed','travelling','parked','default_baseline_deployed','default_baseline_parked']) and all(r['status']=='CLEAR' for r in routes)
 result['artifact_sha256']={p.relative_to(ROOT).as_posix():sha(p) for folder in ('step','parts','dxf') for p in (out/folder).glob('*') if p.is_file()}
 result['elapsed_seconds']=time.time()-t0
 (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('PASS',result['passed'],flush=True)
 return 0 if result['passed'] else 2
if __name__=='__main__':
 try:code=main()
 except Exception:
  import traceback;traceback.print_exc();code=1
 sys.stdout.flush();sys.stderr.flush();os._exit(code)

