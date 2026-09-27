"""Revised rigid panel sequence with fixed retracting ATC supports installed."""
from pathlib import Path
import sys,json,hashlib,time,os,copy,math
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
import build,verify
import build_revi,build_revg,bed_cassettes as bc,bed_completion
from cad_helpers import bbox
from sweep_checks import translation_segment,rotation_segment

def main():
 sources=[Path(__file__),HERE/'build.py',HERE/'lock.py',HERE/'sensors.py',HERE/'verify.py']+list((ROOT/'output/release-review/RevE-ENGINEERING').glob('*.py'))
 before={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};start=time.time()
 model,_=build_revi.build_model();verify.apply_baseline_substitution(model);bed_completion.prepare_panel_handling_model(model);model=build_revg.store_router_tool(model)
 for p in model.parts:
  rec=bc._PLACEMENTS.get(p.id)
  if rec and rec[0] in ('spoil','spoil_bolt','spoil_nut','clamp'):p.shape=bc.transformed_to_storage(p)
 atc,_=build.build(200,False,True);model.parts.extend(atc.parts)
 report={'scope':'Six rigid bare panel paths after spoilboards and clamp sets have been stored and router tool parked; fixed ATC supports remain installed and carrier parked. Preconditions use frozen RevI phases. This does not prove human access, flexible leads, small fastener transfer, or an installed real magazine.', 'source_sha256':before,'order_one_based':[1,2,3,4,6,5],'assigned_storage_slots_one_based':[6,5,4,3,2,1],'panels':[]}
 out=HERE/'panel-transfer-check.json'
 def save():out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 for ordinal,index in enumerate((0,1,2,3,5,4)):
  slot=5-ordinal;parts=[p for p in model.parts if bc._PLACEMENTS.get(p.id,('',-1))[:2]==('panel',index)];moving={p.id:p.shape for p in parts};fixed={p.id:p.shape for p in model.parts if p.id not in moving};datum=bc._PLACEMENTS[parts[0].id][2];rec={'panel':index+1,'slot':slot+1,'segments':[]}
  def record(name,r):
   b=r['swept_enclosing_bounds_mm']
   if name=='rotate90_about_X':
    ys=[];xs=[]
    for sh in moving.values():
     bb=bbox(sh);xs += [bb[0],bb[3]]
     for y in (bb[1],bb[4]):
      for z in (bb[2],bb[5]):
       A=y-20;B=-(z-980.8);angles=[0,math.pi/2]
       theta=math.atan2(B,A)
       angles += [theta+k*math.pi for k in range(-2,3) if 0<theta+k*math.pi<math.pi/2]
       ys += [20+A*math.cos(t)+B*math.sin(t) for t in angles]
    b=[min(xs),min(ys),0,max(xs),max(ys),0]
    r['analytic_rotation_xy_bounds_mm']=[b[0],b[1],b[3],b[4]]
    r['footprint_method']='Exact quarter-turn extrema of every moving-part AABB corner; collision bounds remain independently conservative.'
   r['footprint_clear']=b[0]>=-1e-5 and b[1]>=-1e-5 and b[3]<=1150+1e-5 and b[4]<=1450+1e-5;rec['segments'].append({'name':name,**r});print(index+1,name,r['status'],len(r['candidates']),flush=True)
  def move(name,d):
   nonlocal moving
   r=translation_segment(moving,fixed,d);record(name,r);moving={n:s.translate(d) for n,s in moving.items()}
  px,py,_=datum
  if index<4:move('lift60',(0,0,60))
  elif index==5:
   move('rear_right_lift20',(0,0,20));move('rear_right_forward407',(0,-407,0));move('raise_after_gussets',(0,0,40));py-=407
  else:
   move('rear_left_lift2',(0,0,2));move('right_into_empty_rear_bay',(110,0,0));px+=110
   move('lift_remaining18',(0,0,18));move('rear_left_forward407',(0,-407,0));move('raise_after_supports',(0,0,40));py-=407
  move('translate_to_front_rotation_datum',(325-px,20-py,0))
  origin=(325,20,980.8);r=rotation_segment(moving,fixed,origin,'X',0,90,max_step_deg=2);record('rotate90_about_X',r);moving={n:s.rotate(origin,(326,20,980.8),90) for n,s in moving.items()}
  move('lower_front_drop_lane',(0,0,205-980.8));move('slide_to_new_deepest_slot',(0,bc.PANEL_STORE_Y[slot],0));move('lower30_into_slot',(0,0,-30))
  for p in parts:p.shape=moving[p.id]
  rec['passed']=all(x['status']=='CLEAR' and x['footprint_clear'] for x in rec['segments']);report['panels'].append(rec);save()
 report['sources_changed_during_check']={k:v for k,v in before.items() if hashlib.sha256((ROOT/k).read_bytes()).hexdigest()!=v};report['passed']=not report['sources_changed_during_check'] and all(p['passed'] for p in report['panels']);report['elapsed_seconds']=time.time()-start;save();print('PANELS_PASS',report['passed'],flush=True)
 return 0 if report['passed'] else 2
if __name__=='__main__':
 try:code=main()
 except Exception:
  import traceback;traceback.print_exc();code=1
 sys.stdout.flush();sys.stderr.flush();os._exit(code)
