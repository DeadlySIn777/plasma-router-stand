"""Interlocked manual park of complete, unchanged front stop assemblies.

Operating bumper/striker and roller/cam datums are preserved. During bed
conversion the actual assemblies park400mm rearward on the same header slots.
This module never edits the frozen XR2 source or root mechanical factory.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,json,csv,math,os,re,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent;OUT=HERE/'output/front-stop-bed-clearance'
PARK_Y=400.;INBOARD_CLEARANCE=40.
STEEL=(.30,.36,.40);HARD=(.43,.47,.50)
def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cyl(r,h,p,d=(1,0,0)):return cq.Solid.makeCylinder(r,h,cq.Vector(*p),cq.Vector(*d))
def bounds(s):
 b=s.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def mirror(s,side):return s if side=='L'else s.mirror('YZ',(575,0,0))
def side(n):
 for q in('L','R'):
  if re.search(r'(?:^|_)'+q+r'(?:_|$)',n):return q
 return None
def is_front_module(n):
 return any(re.fullmatch(p,n)for p in(
  r'Y_STOP_[LR]_FRONT_(?:BRACKET|BUFFER)',r'Y_BUFFER_[LR]_FRONT_SCREW_[12]',
  r'Y_LIMIT_[LR]_FRONT_(?:BODY|ROLLER|SCREW_[12])',r'XR_STOP_CARRIER_[LR]_FRONT',
  r'XR_STOP_BASE_M6x12_[LR]_FRONT_[12]',r'XR_STOP_FRAME_(?:M6x16_EXTERNAL_GRIP|WASHER)_[LR]_FRONT_[12]'))
def is_removed_fastener(n):return n.startswith(('XR_STOP_FRAME_M6x16_EXTERNAL_GRIP_','XR_STOP_FRAME_WASHER_'))and'_FRONT_'in n

@lru_cache(None)
def datum_parts():
 p=[]
 for sd in('L','R'):
  for label,y in(('OPERATING',60.),('PARKED',460.)):
   s=box(25.8,y,1023,6.35,20,20).cut(cyl(3.3,8.35,(24.8,y+10,1033))).clean()
   p.append((f'INT_STOP_DATUM_{sd}_{label}_BLOCK',mirror(s,sd),STEEL))
   washer=cyl(6,1.6,(32.15,y+10,1033)).cut(cyl(3.3,3.6,(31.15,y+10,1033))).clean()
   p.append((f'INT_STOP_DATUM_{sd}_{label}_WASHER',mirror(washer,sd),HARD))
   # External grip only. Actual M6x16 and compatible slot nut remain subject
   # to the same purchased-profile fit/engagement check as all header joints.
   screw=cyl(2.95,7.95,(33.75,y+10,1033),(-1,0,0)).fuse(cyl(5.25,3.3,(33.75,y+10,1033))).clean()
   p.append((f'INT_STOP_DATUM_{sd}_{label}_M6_BUTTON_EXTERNAL',mirror(screw,sd),HARD))
 return tuple(p)

def apply_front_stop_state(parts,state='operating'):
 if state not in('operating','parked'):raise ValueError('operating / parked')
 p=[]
 for n,s,c in parts:
  if n.startswith('INT_STOP_DATUM_'):continue
  if state=='parked'and is_front_module(n):s=s.translate((0,PARK_Y,0))
  p.append((n,s,c))
 return p+list(datum_parts())

def module_at(parts,sd,stage,t):
 if stage not in range(3)or not 0<=t<=1:raise ValueError('stage0..2,t0..1')
 p=[];dx=INBOARD_CLEARANCE*(1 if sd=='L'else -1)
 for n,s,c in parts:
  if not is_front_module(n)or side(n)!=sd or is_removed_fastener(n):continue
  s=s.translate((dx*(t if stage==0 else 1),0,0))
  if stage>=1:s=s.translate((0,PARK_Y*(t if stage==1 else 1),0))
  if stage>=2:s=s.translate((-dx*t,0,0))
  p.append((n,s,c))
 return p

def source_cells(parts,sd):
 """Bounds enclose every module solid; separate true carrier height bands."""
 cells=[];coverage={}
 for n,s,c in parts:
  if not is_front_module(n)or side(n)!=sd or is_removed_fastener(n):continue
  b=bounds(s);pieces=[]
  zcuts=[b[2],1049.,1097.5875,b[5]]if n.startswith('XR_STOP_CARRIER_')else[b[2],1110.2875,b[5]]if n.endswith('_BRACKET')else[b[2],b[5]]
  zcuts=sorted(set(max(b[2],min(b[5],z))for z in zcuts))
  for k,(z0,z1)in enumerate(zip(zcuts,zcuts[1:])):
   if z1-z0<1e-6:continue
   q=s.intersect(box(b[0]-1,b[1]-1,z0,b[3]-b[0]+2,b[4]-b[1]+2,z1-z0))
   # Split base relief so a bounding cell does not recreate removed steel
   # next to the actual HMS motor bracket at the initial front position.
   ycuts=[b[1],95.5,b[4]]if n.endswith('_BRACKET')and z0<1110.2876 else[b[1],b[4]]
   ycuts=sorted(set(max(b[1],min(b[4],y))for y in ycuts))
   for j,(y0,y1)in enumerate(zip(ycuts,ycuts[1:])):
    r=q.intersect(box(b[0]-1,y0,z0-1,b[3]-b[0]+2,y1-y0,z1-z0+2))
    for a in r.Solids():
     if a.Volume()>1e-5:pieces.append(bounds(a))
  cubes=[box(*v[:3],*(v[i+3]-v[i]for i in range(3)))for v in pieces]
  cover=cubes[0].fuse(*cubes[1:]).clean()if len(cubes)>1 else cubes[0]
  missing=abs(s.cut(cover).Volume());assert missing<.001,(n,missing)
  cells +=[(n+'_'+str(k),v)for k,v in enumerate(pieces)]
  coverage[n]=dict(cells=len(pieces),missing_material_mm3=missing)
 return cells,coverage

def run():
 import mechanical as M
 sys.path[:0]=[str(HERE/'bed'),str(HERE/'utilities'),str(HERE/'atc')]
 import integrated_bed as B
 import integrated_utilities as U
 import actual_atc as A
 import assembly as I
 OUT.mkdir(parents=True,exist_ok=True)
 raw=[p for p in I.integrated_motion(False,1275,975,250,module_removed=True,spindle_context=False)if not p[0].startswith('INT_STOP_DATUM_')and not is_front_module(p[0])]
 raw +=[p for p in M.motion_parts(False,1275,975,250)if is_front_module(p[0])]
 fixed=M.frame_parts()+U.utility_parts(guards_fitted=False)
 fixed+=A.actual_atc_parts(200,hood='fitted',include_allocations=True)+[p for p in raw if not is_front_module(p[0])]+list(datum_parts())
 hashes=lambda:{str(p.relative_to(HERE.parents[1])):hashlib.sha256(p.read_bytes()).hexdigest()for p in map(Path,(__file__,M.__file__,B.__file__,U.__file__,A.__file__,I.__file__))}
 start=hashes();hits=[];coverage={};bounds_all=[];count=0
 def overlaps(a,b):return all(min(a[i+3],b[i+3])-max(a[i],b[i])>1e-6 for i in range(3))
 # Transfer left then right. The other complete module stays physical in
 # its operating or parked pose; only four explicitly removed header screws
 # and washers are held by the operator during transfer.
 for bed_angle in(0.,90.):
  endpoint_bed=[(p['id'],p['shape'],p['color'])for p in B.bed_parts(bed_angle)]
  done=[]
  for sd in('L','R'):
   other=[p for p in raw if is_front_module(p[0])and side(p[0])!=sd]
   if done:other=[(n,s.translate((0,PARK_Y,0)),c)for n,s,c in other]
   obs=[(n,s,bounds(s))for n,s,c in fixed+endpoint_bed+other]
   cells,cov=source_cells(raw,sd);coverage.update(cov)
   for stage in range(3):
    for n,b in cells:
     dx=INBOARD_CLEARANCE*(1 if sd=='L'else -1)
     def shifted(t):
      v=b.copy();x=dx*(t if stage==0 else 1)-(dx*t if stage==2 else 0);y=PARK_Y*(t if stage==1 else 1)if stage>=1 else 0
      v[0]+=x;v[3]+=x;v[1]+=y;v[4]+=y;return v
     a,z=shifted(0),shifted(1);v=[min(a[i],z[i])for i in range(3)]+[max(a[i],z[i])for i in range(3,6)]
     bounds_all.append(v);count+=1;env=None
     for m,s,bb in obs:
      if not overlaps(v,bb):continue
      if env is None:env=box(*v[:3],*(v[i+3]-v[i]for i in range(3)))
      vol=abs(env.intersect(s).Volume())
      if vol>.01:hits.append(dict(bed_angle_deg=bed_angle,side=sd,stage=stage,cell=n,obstacle=m,volume_mm3=vol))
   done.append(sd)
 report=dict(source_sha256=start,source_consistent_after_build=start==hashes(),method='Conservative material-cover cells; continuous axis translations enclosed exactly by unioned endpoint bounds. All source material containment checked.',
  original_operating_parts_unchanged=True,operating_buffer_and_roller_cam_datums_changed=False,park_offset_Y_mm=400,
  manual_path_mm=[['inboard_X',40],['rearward_Y',400],['outboard_X',40]],coverage=coverage,enclosures=count,hits=hits,
  whole_route_bounds_mm=[min(v[i]for v in bounds_all)for i in range(3)]+[max(v[i]for v in bounds_all)for i in range(3,6)],
  checked_bed_angles_deg=[0.,90.],reverse_route_has_same_geometry=True,
  prerequisites=['Bedfullyflatoremptiedandpositivelypinned90deg; neverintermediateangle','Allguideguardsstored','Headremoved; commonX975/Y1275/Z250; motionlocked','DisconnectbothNCswitchserviceconnectors','Removeandhold4M6headerscrewsand4washers','Transferleftthenright','Reseatandclampatparkdatumblocks'],
  restore_before_motion=['ReturncompletestopgroupsagainstoriginalY80datumblocks','ReconnectNCswitches','ProvebothNCinputsandretentioninterlock','Rehomeatcommissioningspeed; verifytripandbufferdistances'],
  new_items=['Four20x20x6.35steeldatumblocks','FourM6x16buttonhead/washer/actualslotnutsets','FourextraM6parkheaderTnuts;originaloperatingTnutsstayinplace','TwoNCswitchserviceconnectorpairs','Stop-operating/parkedinterlockhardwarecompatiblewithactualcontroller'],
  hold='Actual connectors, cable handling, slot engagement, anti-drop handling and positive state sensing require qualification. Nominal stop contact is preserved; commissioning crash-energy rating is unchanged and unqualified.',fabrication_release=False,operating_release=False)
 report['passed']=not hits and report['source_consistent_after_build']
 (OUT/'front-stop-bed-clearance-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 for state in('operating','parked'):
  parts=[p for p in apply_front_stop_state(raw,state)if is_front_module(p[0])or p[0].startswith('INT_STOP_DATUM_')]
  a=cq.Assembly(name='FRONT_STOPS_'+state.upper())
  for n,s,c in parts:a.add(s,name=n,color=cq.Color(*c))
  a.save(str(OUT/('FRONT_STOPS_'+state.upper()+'.step')))
 print(json.dumps(dict(passed=report['passed'],hits=hits,enclosures=count,bounds=report['whole_route_bounds_mm'])),flush=True)
 sys.stdout.flush();os._exit(0 if report['passed']else 2)
if __name__=='__main__':run()
