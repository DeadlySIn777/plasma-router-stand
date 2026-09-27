"""Source-bound nominal geometry screens; physical and supplier holds are separate."""
from pathlib import Path
import sys,hashlib,json,math,os,time
import mechanism as m
import cadquery as cq
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bb(s):return s.BoundingBox()
def overlap(a,b,t=1e-6):return all(min(getattr(a,k+'max'),getattr(b,k+'max'))-max(getattr(a,k+'min'),getattr(b,k+'min'))>t for k in ('x','y','z'))
def box_bounds(b):return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def hits(a,b,selftest=False):
 out=[]
 for i,p in enumerate(a):
  pa=bb(p.shape)
  for j,q in enumerate(b):
   if selftest and j<=i:continue
   if not overlap(pa,bb(q.shape)):continue
   v=p.shape.intersect(q.shape).Volume()
   if v>.02:out.append({'a':p.id,'b':getattr(q,'id',getattr(q,'name','?')),'volume_mm3':v})
 return out

def sweep_box(part,axis,travel):
 if part.id=='CARRIAGE' and axis==0:
  return m.box(160+travel,600,12.7).translate((1465,400,760.7)).fuse(m.box(40+travel,70,12.7).translate((1525,1000,760.7)))
 if part.id=='SHUTTER_LIFT_ARM' and axis==2:
  return m.box(40,97,8+travel).translate((1670,338,942)).fuse(m.box(15,20,8+travel).translate((1655,415,942)))
 b=bb(part.shape);lo=[b.xmin,b.ymin,b.zmin];hi=[b.xmax,b.ymax,b.zmax];hi[axis]+=travel
 return m.box(*[hi[i]-lo[i] for i in range(3)]).translate(tuple(lo))

def enclosure_sweep(parts,groups,axis,travel,exceptions):
 moving=[p for p in parts if p.group in groups];fixed=[p for p in parts if p.group not in groups];out=[];tested=0
 for p in moving:
  swept=sweep_box(p,axis,travel)
  for q in fixed:
   if not overlap(bb(swept),bb(q.shape)):continue
   if exceptions(p,q):continue
   v=swept.intersect(q.shape).Volume();tested+=1
   if v>.02:out.append({'moving':p.id,'fixed':q.id,'conservative_box_overlap_mm3':v})
 return {'method':'Continuous translated AABB enclosure against exact stationary solids; any positive result requires refinement, not automatic collision claim.','parts':len(moving),'tested_pairs':tested,'unresolved_pairs':out,'passed':not out}

def main():
 sources=[OUT/x for x in ('mechanism.py','hood.py','locks.py','catch.py','retention.py','verify.py','service_check.py','export.py','README.md') if (OUT/x).exists()]
 sources += list((OUT.parent/'hardware').glob('*.py'))+list((OUT.parent/'hardware').glob('*.json'))+list((OUT.parent/'hardware').glob('*.md'))+[ROOT/'variants/48x96/layout.py']
 before={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sources}
 report={'builder':'large-mechanism','status':'Development mechanism, not fabrication/machine release','source_sha256':before,'states':[]}
 context=m.context()
 for name,args in [('parked',(200,0,False,False)),('deployed',(0,164,False,False)),('travel',(100,164,True,False)),('shutter_travel',(200,82,False,True)),('pins_midstroke',(200,0,3.,3.))]:
  parts=m.build(*args);item={'name':name,'parts':len(parts),'all_valid_single_solids':all(p.shape.isValid() and len(p.shape.Solids())==1 for p in parts),'internal':hits(parts,parts,True),'machine_context':hits(parts,context)};item['passed']=item['all_valid_single_solids'] and not item['internal'] and not item['machine_context'];report['states'].append(item);print(name,item['passed'],flush=True)
 # Full200mm slide, dockpins released and shutter open. Raceway and screw proof uses their full constant profile below.
 p=m.build(0,164,True,False)
 def slide_ex(a,b):return b.id.startswith(('MGNR12_','RAIL_SCREW_')) or b.id=='SLIDE_MOTOR'
 report['slide_sweep']=enclosure_sweep(p,{'slide','slide_fasteners'},0,200,slide_ex)
 # Exact analytical continuous drive/race profile checks, not a blanket contact allowance.
 profiles=[]
 for i,y in enumerate((430.,970.)):profiles.append(('rail'+str(i),m.box(500,12,8).translate((1430,y-6,747.7))))
 profiles.append(('screw',m.pose(m.cyl(4,400),(1450,1045,797.4),(1,0,0),(0,1,0))))
 prof=[]
 for a in p:
  if a.group not in ('slide','slide_fasteners'):continue
  for name,shape in profiles:
   if overlap(bb(a.shape),bb(shape)):
    v=a.shape.intersect(shape).Volume()
    if v>.02:prof.append({'part':a.id,'profile':name,'volume_mm3':v})
 report['constant_profile_checks']={'passed':not prof,'collisions':prof,'meaning':'Rail rectangle also contains rail screw heads at bearing heights; full straight screw major cylinder is constant along travel. Motor body lies before moving nut bracket.'}
 # Shutter box enclosures can overestimate the L-shaped arm; report those transparently.
 p=m.build(200,0,False,True)
 report['shutter_sweep']=enclosure_sweep(p,{'shutter','shutter_fasteners'},2,164,lambda a,b:b.id=='SHUTTER_MOTOR')
 # Constant vertical drive cylinder proves sliding nut/flange bolts clear along entire164mm stroke.
 screw=m.cyl(4,400,1690,350,800);sc=[]
 for a in p:
  if a.group in ('shutter','shutter_fasteners') and overlap(bb(a.shape),bb(screw)):
   v=a.shape.intersect(screw).Volume()
   if v>.02:sc.append({'part':a.id,'volume_mm3':v})
 report['vertical_screw_profile']={'passed':not sc,'collisions':sc}
 # Full Y gantry bridge/towers/carriage bounds, and full deck routing head allocation.
 parked=m.build(200,0,False,False);envs=[('bridge',m.box(1850.8,2950,250.8).translate((75,0,1150))),('right_tower',m.box(50.8,2950,175).translate((1849.6,0,975))),('left_tower',m.box(50.8,2950,175).translate((49.6,0,975))),('right_carriage',m.box(75,2950,42).translate((1837.5,0,933))),('left_carriage',m.box(75,2950,42).translate((37.5,0,933))),('deck_router_head',m.box(1445.4,2665.4,410).translate((67.3,117.3,930)))]
 gh=[]
 for name,shape in envs:
  for a in parked:
   if overlap(bb(shape),bb(a.shape)):
    v=shape.intersect(a.shape).Volume()
    if v>.02:gh.append({'envelope':name,'part':a.id,'volume_mm3':v})
 report['gantry_deck_head_sweep']={'passed':not gh,'collisions':gh,'head_axis_range_mm':{'x':[117.3,1462.7],'y':[162.3,2737.7]},'head_half_width_mm':50,'head_half_depth_mm':45,'head_z_mm':[930,1340],'limit':'Full deck routing range preserved. Low-Z movement into ATC bay is excluded and requires its separate tool-change handshake.'}
 # Service cap: removefourM4capbolts, thenlift60mm. Retainedtappedtabsstayfixed.
 cover_ids={'CATCH_SERVICE_CAP','CATCH_CAP_DOWNSTAND'};ch=[]
 for cap in [p for p in parked if p.id in cover_ids]:
  capenv=sweep_box(cap,2,60)
  for p in parked+context:
   if getattr(p,'id','') in cover_ids or getattr(p,'id','').startswith('CATCH_CAP_BOLT_'):continue
   if overlap(bb(capenv),bb(p.shape)):
    v=capenv.intersect(p.shape).Volume()
    if v>.02:ch.append({'moving':cap.id,'part':getattr(p,'id',getattr(p,'name','?')),'volume_mm3':v})
 report['cap_service_path']={'passed':not ch,'lift_mm':60,'removed_fasteners':4,'cover_parts':sorted(cover_ids),'collisions':ch}
 # Conditionalloaded-tool envelopes: manufacturerinterface is NOT drilled.
 loaded=[]
 for state,args in [('parked',(200,0,False,False)),('change',(0,164,False,False))]:
  pp=m.build(*args);dx=args[0]
  # Bodyallocation160x600,120tall sitsaboveadaptertop. CentraltoollineØ25travels24mmbelowunderside.
  body=m.box(160,600,120).translate((1465+dx,400,819.75));tools=m.box(25,500,24).translate((1532.5+dx,450,789.4));ls=[]
  for p in pp:
   for n,vv in [('body',body),('tool_drop',tools)]:
    if overlap(bb(vv),bb(p.shape)):
     vol=vv.intersect(p.shape).Volume()
     if vol>.02:ls.append({'allocation':n,'part':p.id,'volume_mm3':vol})
  loaded.append({'state':state,'collisions':ls,'passed':not ls})
 report['conditional_loaded_allocations']={'states':loaded,'passed':all(x['passed'] for x in loaded),'hold':'Actualmagazine maynotfittheseallocations; supplierdrawing/pocket pitch/endcaps/cover and actualloaded tools remainrequired.'}
 E=69000.;b=38.1;h=50.8;t=3.175;Iz=(h*b**3-(h-2*t)*(b-2*t)**3)/12;Iy=(b*h**3-(b-2*t)*(h-2*t)**3)/12
 report['load_screen']={'working_torque_Nm':19,'dynamic_multiplier':2,'screen_torque_Nm':38,'guide_y_spacing_mm':540,'in_plane_couple_N':38000/540,'tube_vertical_I_mm4':Iy,'tube_inplane_I_mm4':Iz,'cantilever_mm':304.2,'separate_vertical_screen_per_tube_N':250,'vertical_end_deflection_mm':250*304.2**3/(3*E*Iy),'inplane_lateral_250N_end_deflection_mm':250*304.2**3/(3*E*Iz),'pin_screen_N':500,'pin_single_shear_MPa':500/(math.pi*6**2/4),'receiver_projected_bearing_MPa':500/(6*4),'limitation':'Elastic member-only screens, not joint/frame/rail/tool-loop qualification. Torque about verticalZ is in-plane reaction, not tube longitudinal torsion. Weld HAZ, clamp preload and measured pocket alignment remain required.'}
 report['dimensions']={'slide_stroke_mm':200,'shutter_stroke_mm':164,'guide_length_mm':350,'guide_block_envelope_max_mm':45.8,'two_block_spacing_mm':80,'end_margin_mm':(350-200-80-45.8)/2,'shutter_nut_screw_end_margin_mm':10,'bonnet_to_bridge_mm':8,'hood_to_right_carriage_mm':7.5,'stock_mm':[1219.2,2438.4]}
 expected_parts={p.id+'.step' for p in parked};expected_flat=set()
 for p in parked:
  if hasattr(p,'frame'):
   local=p.shape.moved(p.frame.inverse)
   if abs(bb(local).zlen-p.thickness)<.01:expected_flat.add(p.id+'.dxf')
 actual_parts={p.name for p in (OUT/'parts').glob('*.step')};actual_flat={p.name for p in (OUT/'flat').glob('*.dxf')}
 inventory=json.loads((OUT/'parts-inventory.json').read_text(encoding='utf-8'));inventory_ids=[r['id'] for r in inventory]
 report['export_inventory']={'passed':actual_parts==expected_parts and actual_flat==expected_flat and len(inventory_ids)==len(set(inventory_ids))==len(parked) and set(inventory_ids)=={p.id for p in parked},'parts_expected':len(expected_parts),'flat_expected':len(expected_flat),'missing_parts':sorted(expected_parts-actual_parts),'extra_parts':sorted(actual_parts-expected_parts),'missing_flat':sorted(expected_flat-actual_flat),'extra_flat':sorted(actual_flat-expected_flat)}
 service=json.loads((OUT/'service-verification.json').read_text(encoding='utf-8'))
 service_bound=bool(service.get('source_sha256')) and all((ROOT/k).is_file() and sha(ROOT/k)==v for k,v in service.get('source_sha256',{}).items())
 report['coil_service_proof']={'passed':service.get('passed') is True and service.get('sources_unchanged') is True and service_bound and service.get('coil_count')==3 and len(service.get('paths',[]))==18 and all(x.get('passed') is True for x in service.get('paths',[])),'source_current':service_bound,'report':'service-verification.json','paths':len(service.get('paths',[]))}
 after={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sources};report['sources_unchanged']=before==after
 report['passed']=all(x['passed'] for x in report['states']) and all(report[k]['passed'] for k in ('slide_sweep','shutter_sweep','constant_profile_checks','vertical_screw_profile','gantry_deck_head_sweep','cap_service_path','conditional_loaded_allocations','export_inventory','coil_service_proof')) and report['sources_unchanged']
 report['artifact_sha256']={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in OUT.rglob('*') if p.is_file() and (p.suffix.lower() in ('.step','.dxf','.csv') or p.name in ('parts-inventory.json','export-summary.json','service-verification.json'))}
 (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:report[k] for k in ('passed','slide_sweep','shutter_sweep','constant_profile_checks','gantry_deck_head_sweep')},indent=2),flush=True)
if __name__=='__main__':
 main();sys.stdout.flush();os._exit(0)
