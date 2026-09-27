"""Supplement proposed fixedZ200 swept bounds and pin kinematic configurations."""
from pathlib import Path
import json,sys,hashlib,math,os,copy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
import build
from cad_helpers import bbox,box,cyl,intersection_volume,validate

def main():
 m,_=build.build(200,False,True);baseline=ROOT/'output/release-review/RevI-CAD/RevI_ROUTER-validation.json';parts={p['id']:p['bounds_mm'] for p in json.loads(baseline.read_text())['parts']}
 hits=[];bounds={}
 for name in ('ZBX80_BASE','ZBX80_END_TOP','ZBX80_MOTOR','ZBX80_COUPLER_GUARD'):
  b=list(parts[name]);b[5]+=100
  if name!='ZBX80_BASE':b[2]+=100
  b[0]-=400;b[3]+=400;b[1]-=1000;bounds[name]=b
  envelope=box(*(b[k+3]-b[k] for k in range(3))).translate(tuple(b[:3]))
  for p in m.parts:
   pb=bbox(p.shape)
   if all(min(b[k+3],pb[k+3])-max(b[k],pb[k])>1e-6 for k in range(3)):
    vol=intersection_volume(p.shape,envelope)
    if vol>.02:hits.append([name,p.id,vol])
 unlocked,_=build.build(0,True);locked,_=build.build(0,False);states=[];endpoint_errors=[]
 for step in range(13):
  s=step*.5;a=math.degrees(math.atan2(s,20));model=copy.copy(unlocked);model.parts=[copy.copy(p) for p in unlocked.parts]
  for i,py in enumerate((1055.,1430.)):
   mirror=i==1;cy=py+(-6 if mirror else 6)
   for p in model.parts:
    pre=f'LOCK_{i}_'
    if not p.id.startswith(pre):continue
    suffix=p.id[len(pre):]
    if suffix in ('PIN','FOLLOWER','SENSOR_FLAG','FLAG_WASHER','FLAG_NUT'):p.shape=p.shape.translate((0,0,s))
    elif suffix=='CLEVIS_PIN':p.shape=p.shape.translate((-s if mirror else s,0,0))
    elif suffix=='BELLCRANK':p.shape=p.shape.rotate((141 if mirror else 101,cy,982),(141 if mirror else 101,cy+1,982),a if mirror else -a)
    elif suffix=='PLUNGER':
     front=87.4364;shape=cyl(10.9982,17.526+s).rotate((0,0,0),(0,1,0),90).translate((front,cy,962)).cut(box(15,4.826,12).translate((front+2.526+s,cy-2.413,956)))
     hole=cyl(3.2,11).rotate((0,0,0),(1,0,0),90).translate((101+s,cy+5.5,962));shape=shape.cut(hole);p.shape=shape.mirror('YZ',(121,0,0)) if mirror else shape
    elif suffix=='SPRING_ENVELOPE':p.shape=cyl(5,2.7+s).cut(cyl(4.5,2.7+s)).translate((121,py,976.3))
   if step==12:
    for p in model.parts:
     if p.id.startswith(f'LOCK_{i}_'):
      q=locked.find(p.id);error=p.shape.cut(q.shape).Volume()+q.shape.cut(p.shape).Volume()
      if error>1e-4:endpoint_errors.append([p.id,error])
  r=validate(model);states.append({'withdrawal_from_released_mm':s,'bellcrank_degrees':a,'clashes':r['unresolved_intersections']});print('PIN',s,r['unresolved_intersections'],flush=True)
 sources=[Path(__file__),HERE/'build.py',HERE/'lock.py',HERE/'sensors.py',baseline]
 report={'scope':'Continuous conservative swept-box check of proposed extended fixedZ components versus parked mechanism/allocation, plus thirteen exact intermediate pin mechanism configurations. Pin configuration samples are not a continuous collision proof.','fixed_Z200_swept_bounds':bounds,'fixed_Z200_hits':hits,'pin_states':states,'endpoint_geometry_mismatch':endpoint_errors,'pin_kinematics':{'equal_arm_mm':20,'stroke_mm':6,'maximum_radial_slide_mm':math.hypot(20,6)-20,'slot_available_center_travel_mm':6.5-3.4,'minimum_pin_guided_length_mm':11,'spring_free_length_mm':14,'spring_min_compressed_length_mm':2.7,'spring_rate_target_N_mm':.0602,'max_nominal_force_N':.68026,'spring_catalog_and_hot_force_qualified':False},'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
 report['passed']=not hits and not endpoint_errors and all(not r['clashes'] for r in states)
 (HERE/'supplement-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SUPPLEMENT',report['passed'],flush=True);return 0 if report['passed'] else 2
if __name__=='__main__':
 try:code=main()
 except Exception:
  import traceback;traceback.print_exc();code=1
 sys.stdout.flush();sys.stderr.flush();os._exit(code)

