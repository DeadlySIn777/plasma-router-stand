"""Nominal axial coil service proof with mechanically removable rear caps.

The source housing omits undocumented internal coil details and cable terminals.
Their delivered arrangement remains a hold; this verifies the shown external body.
"""
from pathlib import Path
import sys,json,hashlib,copy,os
import mechanism as m
from verify import bb,overlap
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def part_id(p):return getattr(p,'id',getattr(p,'name','?'))
def enclosure(shape,vec):
 b=bb(shape);lo=[b.xmin+min(0,vec[0]),b.ymin+min(0,vec[1]),b.zmin+min(0,vec[2])];sz=[b.xlen+abs(vec[0]),b.ylen+abs(vec[1]),b.zlen+abs(vec[2])]
 return m.box(*sz).translate(tuple(lo))
def check(env,fixed):
 out=[]
 bounds=bb(env)
 if bounds.xmin < -1e-6 or bounds.ymin < -1e-6 or bounds.xmax > 1950+1e-6 or bounds.ymax > 2950+1e-6:out.append({'fixed':'1950 x 2950 machine footprint','outside_footprint':True})
 for p in fixed:
  if overlap(bb(env),bb(p.shape)):
   v=env.intersect(p.shape).Volume()
   if v>.02:out.append({'fixed':part_id(p),'volume_mm3':v})
 return out

def run():
 original=m.build(200,0,False,False);context=m.context();paths=[]
 context.append(m.Part('CONDITIONAL_LOADED_MAGAZINE',m.box(160,600,120).translate((1665,400,819.75)),'allocation','allocation only',(.75,.25,.62)))
 context.append(m.Part('CONDITIONAL_LOADED_TOOLS',m.box(25,500,24).translate((1732.5,450,789.4)),'allocation','allocation only',(.75,.25,.62)))
 # Each coil is independently serviced with the other two fully installed.
 for prefix,dx in [('DOCK0_',70.),('DOCK1_',-70.),('CATCH_',55.)]:
  live=[copy.copy(p) for p in original];sgn=1 if dx>0 else-1
  if prefix=='CATCH_':
   cover_ids={'CATCH_SERVICE_CAP','CATCH_CAP_DOWNSTAND'}
   fixed=[p for p in live if p.id not in cover_ids and not p.id.startswith('CATCH_CAP_BOLT_')]+context
   for cap in [p for p in live if p.id in cover_ids]:
    env=enclosure(cap.shape,(0,0,60));paths.append({'part':cap.id,'operation':'Remove four M4x6 cover screws; manually lift the welded cover and downstand together.','translation_mm':[0,0,60],'collisions':check(env,fixed)})
   live=[p for p in live if p.id not in cover_ids and not p.id.startswith('CATCH_CAP_BOLT_')]
  for j in range(2):
   bolt=next(p for p in live if p.id==prefix+'END_CAP_BOLT_'+str(j));b=bb(bolt.shape);cy=(b.ymin+b.ymax)/2;cz=(b.zmin+b.zmax)/2
   # Shaft and head have different radii. Both translate away from the cap;
   # this avoids treating a shaft in a real clearance hole as a solid head box.
   bearing=b.xmax-3 if sgn>0 else b.xmin+3
   if sgn>0:
    env=m.pose(m.cyl(1.5,24),(bearing-10,cy,cz),(1,0,0),(0,1,0)).fuse(m.pose(m.cyl(2.75,17),(bearing,cy,cz),(1,0,0),(0,1,0)))
   else:
    env=m.pose(m.cyl(1.5,24),(bearing+10,cy,cz),(-1,0,0),(0,1,0)).fuse(m.pose(m.cyl(2.75,17),(bearing,cy,cz),(-1,0,0),(0,1,0)))
   paths.append({'part':bolt.id,'operation':'Unscrew M3x10 and withdraw axially. Threads represented at nominal major diameter.','translation_mm':[14*sgn,0,0],'collisions':check(env,[p for p in live if p.id!=bolt.id]+context)})
   live=[p for p in live if p.id!=bolt.id]
  cap=next(p for p in live if p.id==prefix+'BODY_END_REAR')
  # A cap is a 4 mm constant section. Its bounding enclosure is conservative;
  # the upper-ear recesses are intentionally not subtracted.
  vec=(50*sgn,0,0);env=enclosure(cap.shape,vec)
  paths.append({'part':cap.id,'operation':'Withdraw removable rear cap; support it by hand.','translation_mm':list(vec),'collisions':check(env,[p for p in live if p.id!=cap.id]+context)})
  cap.shape=cap.shape.translate(vec)
  if prefix=='CATCH_':
   env=enclosure(cap.shape,(0,0,60));paths.append({'part':cap.id,'operation':'Lift detached cap through open service cover.','translation_mm':[0,0,60],'collisions':check(env,[p for p in live if p.id!=cap.id]+context)})
  live=[p for p in live if p.id!=cap.id]
  coil=next(p for p in live if p.id==prefix+'SOLENOID');b=bb(coil.shape);env=enclosure(coil.shape,(dx,0,0))
  # The fixed plunger remains linked. The initial 35 mm coaxial housing bore
  # remains empty throughout withdrawal away from the plunger: later housings
  # start farther away, so the initial bore cannot be filled by translated metal.
  # This is a constant-profile proof, not a blanket plunger collision exclusion.
  front=b.xmin if sgn>0 else b.xmax
  bore=m.pose(m.cyl(5.65,35.1),(front-.1*sgn,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2),(sgn,0,0),(0,1,0))
  env=env.cut(bore)
  paths.append({'part':coil.id,'operation':'Disconnect field leads and withdraw coil body axially; side keeper and guided plunger remain installed.','translation_mm':[dx,0,0],'collisions':check(env,[p for p in live if p.id!=coil.id]+context)})
  coil.shape=coil.shape.translate((dx,0,0))
  if prefix=='CATCH_':
   env=enclosure(coil.shape,(0,0,60));paths.append({'part':coil.id,'operation':'Lift fully detached coil through open service cover.','translation_mm':[0,0,60],'collisions':check(env,[p for p in live if p.id!=coil.id]+context)})
  else:
   env=enclosure(coil.shape,(0,0,-20));paths.append({'part':coil.id,'operation':'Lower detached coil 20 mm into the accessible under-module space.','translation_mm':[0,0,-20],'collisions':check(env,[p for p in live if p.id!=coil.id]+context)})
  for item in paths:
   if 'passed' not in item:item['passed']=not item['collisions']
 return {'builder':'large-mechanism','passed':all(x['passed'] for x in paths),'coil_count':3,'machine_footprint_mm':[1950,2950],'conditional_parked_magazine_envelope_mm':[160,600,120],'paths':paths,'method':'Continuous conservative enclosing solids, refined only by the constant coaxial purchased-housing bore; exact positive-volume intersections against all other installed mechanism and baseline context parts. Each coil is serviced independently.','limits':'External nominal body routes only. Isolate actuator power; mechanically support the shutter and secure the slide. Disconnect leads and allow coil cooling. Actual terminals, cable boots, proprietary internal plunger retention, hand/tool space, tolerances and hot surfaces require delivered-part inspection. Swaged linkage pins are not removed for the shown body service. Detached caps/coils are manually supported; no nonexistent fixture is assumed. Reverse paths restore the shown components.'}

if __name__=='__main__':
 files=[OUT/x for x in ('mechanism.py','hood.py','locks.py','catch.py','retention.py','verify.py','service_check.py','README.md')]+[ROOT/'variants/48x96/layout.py']+list((OUT.parent/'hardware').glob('*.py'))+list((OUT.parent/'hardware').glob('*.json'))+list((OUT.parent/'hardware').glob('*.md'))
 before={p.relative_to(ROOT).as_posix():digest(p) for p in files}
 r=run();r['source_sha256']=before;r['sources_unchanged']=all(digest(ROOT/k)==v for k,v in before.items());r['passed']=r['passed'] and r['sources_unchanged'];(OUT/'service-verification.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2),flush=True);os._exit(0)
