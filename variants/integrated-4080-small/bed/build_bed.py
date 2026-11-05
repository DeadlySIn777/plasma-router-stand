"""Build, export and bound-check the continuous full-bed revision.

Passing means nominal geometry/analysis scope passed, never lift approval.
"""
from pathlib import Path
from itertools import combinations
import csv,hashlib,importlib.util,json,math,os,sys
import cadquery as cq
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
import integrated_bed as B

HERE=Path(__file__).resolve().parent;ROOT=B.ROOT;OUT=HERE/'output'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,n):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def overlap(a,b,tol=1e-7):return all(min(a[k+3],b[k+3])>max(a[k],b[k])+tol for k in range(3))
def exact_pairs(parts,other=None,allow_vendor=False):
 records=[];tests=0;contacts=0
 ps=[(p['id'],p['shape'],B.bounds(p['shape']))for p in parts]
 qs=ps if other is None else[(p[0],p[1],B.bounds(p[1]))for p in other]
 pairs=((a,b)for i,a in enumerate(ps)for b in(ps[i+1:]if other is None else qs))
 for(a,sa,ba),(b,sb,bb)in pairs:
  if not overlap(ba,bb):continue
  tests+=1;v=abs(sa.intersect(sb).Volume())
  if v>.02:
   vendor=any({a,b}=={f'BED_GAS_ROD_{side}',f'BED_GAS_10MM_BALL_{side}_LOWER'}for side in('L','R'))
   if allow_vendor and vendor:contacts+=1
   else:records.append(dict(a=a,b=b,volume_mm3=v))
 return dict(exact_pairs=tests,registered_vendor_joint_overlaps=contacts,unexpected=records,passed=not records)

def trig_range(c,s,a,b):
 lo,hi=map(math.radians,(a,b));angles=[lo,hi];base=math.atan2(s,c)
 for k in range(-3,4):
  q=base+k*math.pi
  if lo<=q<=hi:angles.append(q)
 vals=[c*math.cos(q)+s*math.sin(q)for q in angles]
 return min(vals),max(vals)
def swept_box(s,a,b):
 box=B.bounds(s);yy=[];zz=[]
 for y in(box[1],box[4]):
  for z in(box[2],box[5]):
   dy,dz=y-B.PIVOT[0],z-(B.PIVOT[1]+B.ASSEMBLY_Z_SHIFT)
   r=trig_range(dy,-dz,a,b);yy.extend(v+B.PIVOT[0]for v in r)
   r=trig_range(dz,dy,a,b);zz.extend(v+B.PIVOT[1]+B.ASSEMBLY_Z_SHIFT for v in r)
 return[box[0],min(yy),min(zz),box[3],max(yy),max(zz)]
def radial_bound(s):
 b=B.bounds(s);return max(math.hypot(y-B.PIVOT[0],z-(B.PIVOT[1]+B.ASSEMBLY_Z_SHIFT))for y in(b[1],b[4])for z in(b[2],b[5]))
def continuous_pair(s,obstacle,a,b,depth=0):
 bb=swept_box(s,a,b)
 if not overlap(bb,B.bounds(obstacle)):return(True,1,0)
 mid=(a+b)/2;at=s.rotate((0,B.PIVOT[0],B.PIVOT[1]+B.ASSEMBLY_Z_SHIFT),(1,B.PIVOT[0],B.PIVOT[1]+B.ASSEMBLY_Z_SHIFT),mid)
 displacement=2*radial_bound(s)*math.sin(math.radians((b-a)/4))
 gap=at.distance(obstacle)
 if gap>displacement+1e-6:return(True,0,1)
 if depth>=12 or b-a<.002:
  v=at.intersect(obstacle).Volume()
  return(False,0,1) # An unresolved enclosure is not declared clear.
 l=continuous_pair(s,obstacle,a,mid,depth+1);r=continuous_pair(s,obstacle,mid,b,depth+1)
 return(l[0]and r[0],l[1]+r[1],l[2]+r[2])

def export_step(parts,path):
 a=cq.Assembly(name=path.stem)
 for p in parts:a.add(p['shape'],name=p['id'],color=cq.Color(*p['color']))
 a.save(str(path));back=cq.importers.importStep(str(path)).val()
 expected=sum(len(p['shape'].Solids())for p in parts);vol=sum(p['shape'].Volume()for p in parts)
 return dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),components=len(parts),solids=len(back.Solids()),
  valid=back.isValid()and len(back.Solids())==expected and abs(back.Volume()-vol)<max(.5,vol*1e-7),
  volume_error_mm3=abs(back.Volume()-vol),bounds_mm=B.bounds(back))

def analyze():
 section=B.profile_section(1.);g=GProp_GProps();BRepGProp.VolumeProperties_s(section.wrapped,g)
 area=section.Volume();ix=g.MatrixOfInertia().Value(1,1)-area/12
 ps=[p for p in B.bed_parts(0)if p['moving_bed']]
 #4080envelopes omit their true cavities: never infer their mass from display.
 known=[];base_mass=0.;weighted=[0.,0.,0.]
 for p in ps:
  if p['id'].startswith('BED_4080_CROSS_'):continue
  rho={'HDPE':.95e-6,'aluminum':2.7e-6,'steel':7.85e-6}[p['material']]
  mass=p['shape'].Volume()*rho;c=p['shape'].Center();xyz=(c.x,c.y,c.z)
  base_mass+=mass
  for k in range(3):weighted[k]+=mass*xyz[k]
  known.append(dict(id=p['id'],mass_kg=mass))
 rows=[]
 for secarea in(785.,1000.,1200.):
  cmass=4*.98*secarea*.0027;total=base_mass+cmass
  cy=sum(B.CROSS_CENTRES)/4;cz=B.CROSS_BOTTOM+20+B.ASSEMBLY_Z_SHIFT
  cg=[(weighted[k]+cmass*v)/total for k,v in enumerate((575.,cy,cz))]
  cases=[]
  for ratio in(0.,.5,1.,1.3):
   samples=[]
   for a in range(91):
    theta=math.radians(a);gm=B.yzpoint(B.GAS_MOVING,a);sm=B.yzpoint(B.STAY_MOVING,a)
    gl=math.dist(B.GAS_ROOT,gm);sl=math.dist(B.STAY_ROOT,sm)
    rg=(gm[0]-B.PIVOT[0],gm[1]-B.PIVOT[1]);ug=((gm[0]-B.GAS_ROOT[0])/gl,(gm[1]-B.GAS_ROOT[1])/gl)
    gas_moment=2*B.GAS_FORCE*ratio*(rg[0]*ug[1]-rg[1]*ug[0])/1000
    rgy=(cg[1]-B.PIVOT[0])*math.cos(theta)-(cg[2]-B.PIVOT[1]-B.ASSEMBLY_Z_SHIFT)*math.sin(theta)
    gravity=total*9.80665*rgy/1000
    stayr=(sm[0]-B.PIVOT[0],sm[1]-B.PIVOT[1]);stayu=((sm[0]-B.STAY_ROOT[0])/sl,(sm[1]-B.STAY_ROOT[1])/sl)
    staylever=abs(stayr[0]*stayu[1]-stayr[1]*stayu[0])/1000
    residual=gravity-gas_moment
    #Human force normal to the plane, applied at the rear bed edge, not
    #a fixed vertical pull whose leverage vanishes near90degrees.
    samples.append(dict(angle_deg=a,gas_length_mm=gl,stay_length_mm=sl,gravity_moment_Nm=gravity,
      gas_assist_moment_Nm=gas_moment,normal_twohand_handle_force_N=residual/((B.Y0+B.L-B.PIVOT[0])/1000),
      static_each_stay_force_N=residual/(2*staylever)))
   cases.append(dict(gas_force_ratio=ratio,maximum_absolute_handle_force_N=max(abs(r['normal_twohand_handle_force_N'])for r in samples),
       maximum_absolute_static_each_stay_force_N=max(abs(r['static_each_stay_force_N'])for r in samples),samples=samples))
  rows.append(dict(profile4080_material_area_assumption_mm2=secarea,moving_mass_kg=total,CG_world_mm=cg,cases=cases))
 #Ideal serial compliance screen, no HDPE/composite stiffness credit.
 E=69000.;Icross=134000.;F=100.;span=939.
 dprofile=F*400**3/(48*E*ix);dcross=F*span**3/(48*E*Icross)
 #Uniform formedsteel receiver section; localized patched zone is separate.
 w,t,h=54.,3.175,31.75;A1=w*t;A2=t*h;zc=(A1*t/2+A2*(t+h/2))/(A1+A2)
 Iledger=w*t**3/12+A1*(zc-t/2)**2+t*h**3/12+A2*(t+h/2-zc)**2
 dledger=max((F/2)*550**3/(48*200000*Iledger),(F/2)*235**3/(3*200000*Iledger))
 return dict(section20100=dict(area_mm2=area,I_vertical_mm4=ix,profile_quantity=10,length_each_mm=1220),
  moving_known_mass_excluding4080_kg=base_mass,mass_and_force_cases=rows,
  gas_eyelength_range_mm=[min(r['gas_length_mm']for r in rows[0]['cases'][0]['samples']),max(r['gas_length_mm']for r in rows[0]['cases'][0]['samples'])],
  gas_required_acceptance_mm=dict(compressed_max=450,extended_min=700),gas_compressed_published=False,gas_is_holding_device=False,force_model='889N nominal constant force conditional on200lblabel;0,0.5,1,1.3 factors are sensitivity assumptions, not manufacturer tolerance data.',
  workbed_compliance_screen=dict(force_N=100,profile_span_mm=400,profile_deflection_mm=dprofile,cross_span_mm=span,
    required4080_I_weak_mm4=Icross,cross_deflection_mm=dcross,ledger_I_mm4=Iledger,ledger_deflection_mm=dledger,
    sum_ideal_components_mm=dprofile+dcross+dledger,target_mm=.3,passed=dprofile+dcross+dledger<.3,
    exclusions=['Actual profile section and drilled-ligament compliance','Joint slip/twist, slot lips and anchors','Formed angle patch/weld local behavior','Machine gantry/Z/tool loop','Dynamics and thermal creep']),
  stay_static_design_basis=dict(outer_mm=[20,20,2,390],inner_mm=[15,15,1.5,375],positive_pin_mm=10,
    pin_shear_area_double_mm2=2*math.pi*10**2/4,inner_two_wall_bearing_area_mm2=2*1.5*10,
    impact_capacity_qualified=False,index_catch_impact_rating_assigned=False,
    note='Static force only. Full-open retained pin passes both tube walls; gas assist never substitutes for positive support. The proposed spring-index row is NOT a proved fall-arrest system.'))

def run():
 OUT.mkdir(exist_ok=True)
 local_only='--local' in sys.argv
 mech=None if local_only else load(HERE.parent/'mechanical.py','bed_current_integrated_mechanical')
 atc=None if local_only else load(HERE.parent/'atc/actual_atc.py','bed_current_integrated_atc')
 sys.path.insert(0,str(B.BASE));import bed as legacy_bed
 sources=[Path(__file__),Path(B.__file__),Path(legacy_bed.__file__),Path(B.F.__file__)]+([]if local_only else[Path(mech.__file__),Path(atc.__file__)])
 hashes=lambda:{p.relative_to(ROOT).as_posix():sha(p)for p in sources};start=hashes()
 closed=B.bed_parts(0);opened=B.bed_parts(90)
 selfchecks={name:exact_pairs(parts,allow_vendor=True)for name,parts in(('wood',closed),('open',opened))}
 print('SELF',[(k,v['passed'],v['unexpected'])for k,v in selfchecks.items()],flush=True)
 frame=[]if local_only else mech.frame_parts();pan=[p for p in legacy_bed.pan_parts()if not(p[0].startswith('PAN_FRAME_SHIM_PACK_')and p[0].endswith('_100_VERIFY_ACTUAL'))]
 retained=[]if local_only else[p for p in mech.motion_parts(False,1275,575,200)if not p[0].startswith(('TOOL_','I_HEAD_','XR_PLASMA_DROP_','XR_DROP_'))]
 accessories=[]if local_only else atc.actual_atc_parts(200,hood='stored',include_allocations=True)
 external=frame+pan+retained+accessories
 statics={name:exact_pairs(parts,external)for name,parts in(('wood',closed),('open',opened))}
 print('EXTERNAL',[(k,v['passed'],v['unexpected'])for k,v in statics.items()],flush=True)
 if not all(q['passed']for q in[ *selfchecks.values(),*statics.values()]):
  diagnostic=dict(study='BED_CURRENT_COLLISION_WITNESSES',static_self=selfchecks,static_external=statics,
    source_sha256=start,source_consistent_during_check=start==hashes(),passed=False,
    complete_path_proof=False,exports_produced=False,fabrication_release=False)
  (OUT/'bed-collision-witnesses.json').write_text(json.dumps(diagnostic,indent=2)+'\n',encoding='utf-8')
  return 1
 #Rigid deck path, continuous bounding-box rotation plus exact-distance
 #Lipschitz certificates when boxes alone are insufficient.
 moving=[p for p in closed if p['moving_bed']]
 fixed=external+[(p['id'],p['shape'],p['color'])for p in closed if not p['moving_bed']and p['id'].startswith(('BED_RECEIVER_','BED_FRONT_SEAT','BED_HINGE_FIXED','BED_HINGE_PIN','BED_HINGE_RETAINER_','BED_HINGE_AXIAL_SHIM_','BED_GAS_ROOT_','BED_CAPTURE_ROOT_','BED_STAY_PIVOT_'))]
 partitions=[];partitioned=[]
 for n,s,c in fixed:
  if not n.startswith('BED_RECEIVER_ANGLE_'):partitioned.append((n,s,c));continue
  side=n[-1];canonical=B._mirror(s,side);bb=B.bounds(canonical);pieces=[]
  for i,(lo,hi)in enumerate(((72.,75.175),(75.175,79.375),(79.375,126.)),1):
   clip=B.box(lo,bb[1]-1,bb[2]-1,hi-lo,bb[4]-bb[1]+2,bb[5]-bb[2]+2)
   q=canonical.intersect(clip)
   if q.Volume()>1e-7:
    pieces.append(q);partitioned.append((n+f'__EXACT_X_PART_{i}',B._mirror(q,side),c))
  compound=cq.Compound.makeCompound(pieces)
  error=abs(sum(q.Volume()for q in pieces)-canonical.Volume())
  missing=canonical.cut(compound).Volume()+sum(q.cut(canonical).Volume()for q in pieces)
  assert error<.05 and missing<.05,(n,error,missing)
  partitions.append(dict(id=n,volume_sum_error_mm3=error,material_symmetric_difference_mm3=missing,
      meaning='Exact spatial partition separating the verticalweb from the bearingflange; no discarded geometry and no contact exemption.'))
 fixed=partitioned
 failures=[];pair_count=0;aabb=0;distance=0
 fixedb=[(n,s,B.bounds(s))for n,s,_ in fixed]
 for p in moving:
  for lo in range(0,90,5):
   bb=swept_box(p['shape'],lo,lo+5)
   for n,s,b in fixedb:
    pair_count+=1
    if not overlap(bb,b):aabb+=1;continue
    good,na,nd=continuous_pair(p['shape'],s,lo,lo+5);aabb+=na;distance+=nd
    if not good:failures.append(dict(moving=p['id'],fixed=n,angle_range_deg=[lo,lo+5]))
  print('ROTATION',p['id'],'unresolved',len(failures),flush=True)if p['id'].startswith(('FULL_','BED_4080','BED_ASSIST','BED_HINGE_MOVING'))else None
 #Gas and stays deform by telescoping: explicitly finite sampled pose
 #checks, not mislabeled as a rigid continuous proof.
 assist_rows=[]
 for angle in range(0,91,10):
  parts=B.bed_parts(float(angle));assist=[p for p in parts if p['id'].startswith(('BED_GAS','BED_CAPTURE','BED_FULL_OPEN'))]
  rigid=[(p['id'],p['shape'],p['color'])for p in parts if p['moving_bed']or p['id'].startswith(('BED_RECEIVER','BED_FRONT_SEAT','BED_HINGE_FIXED','BED_HINGE_PIN','BED_HINGE_RETAINER_','BED_HINGE_AXIAL_SHIM_','BED_STAY_PIVOT_'))]
  result=exact_pairs(assist,external+rigid)
  assist_rows.append(dict(angle_deg=angle,**result))
  print('ASSIST',angle,result['passed'],result['unexpected'],flush=True)
 exports={name:export_step(parts,OUT/('FULL_BED_'+name.upper()+'.step'))for name,parts in(('wood',closed),('upright',opened))}
 custom={}
 for p in[*closed,*[q for q in opened if q['id'].startswith('BED_FULL_OPEN_POSITIVE_PIN_')]]:
  if p['id'].startswith(('BED_HINGE_FIXED_','BED_HINGE_MOVING_SIDEPLATE_','BED_HINGE_SPACER_','BED_HINGE_PIN_','BED_HINGE_AXIAL_SHIM_','BED_HINGE_RETAINER_WASHER_','BED_ASSIST_','BED_RECEIVER','BED_FRONT_SEAT','BED_REAR_END_CAP','BED_GAS_ROOT_MOUNT','BED_CAPTURE_ROOT_MOUNT','BED_STAY_PIVOT_PIN_','BED_FULL_OPEN_POSITIVE_PIN_')):
   b=B.bounds(p['shape']);local=p['shape'].translate(tuple(-v for v in b[:3]));path=OUT/(p['id']+'.step')
   cq.exporters.export(local,str(path));back=cq.importers.importStep(str(path)).val()
   custom[p['id']]=dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),world_min_mm=b[:3],valid=back.isValid()and len(back.Solids())==1)
 drill=[]
 for layer in(1,2):
  for cy,x in B.anchor_rows():drill.append(dict(part=f'FULL_HDPE_{layer}',X_from_left_mm=x-B.X0,Y_from_front_mm=cy-(B.Y0+.4),diameter_mm=13.2 if(cy,x)==(395.,545.)else 22.,operation='Round through-drill only'))
 with(OUT/'HDPE-DRILL.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(drill[0]));w.writeheader();w.writerows(drill)
 report=dict(study='INTEGRATED_FULL_HDPE_20100_BED',local_bed_and_pan_only=local_only,metadata=B.metadata(),source_sha256=start,
  static_self=selfchecks,static_external=statics,
  continuous_rigid_deck=dict(passed=not failures,base_interval_deg=5,enumerated_pairs=pair_count,AABB_certificates=aabb,exact_distance_certificates=distance,exact_receiver_material_partitions=partitions,unresolved=failures),
  telescoping_assist_sampled_poses=assist_rows,telescoping_assist_continuously_qualified=False,
  analysis=analyze(),exports=exports,custom_parts=custom,
  source_consistent_during_build=start==hashes(),fabrication_release=False,lift_operation_release=False,
  open_gates=['Actual complete gas body/socket/bracket dimensions and load ratings','Impact-qualified transition catch or controlled lifting process','Actual final mass, handle forces, pin/hinge/weld/core/nut capacity and full fitting','Existing working head installed registration and complete service routes are root package interfaces'],
  ownership=dict(HDPE_proven_owned=False,profiles20100_proven_owned=False,raw_aluminum_credit_taken=False))
 report['passed']=report['source_consistent_during_build']and all(q['passed']for q in selfchecks.values())and all(q['passed']for q in statics.values())and not failures and all(q['passed']for q in assist_rows)and all(q['valid']for q in exports.values())and all(q['valid']for q in custom.values())
 (OUT/('bed-local-check.json'if local_only else'bed-integration-check.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=report['passed'],source_current=report['source_consistent_during_build'],continuous_failures=len(failures),moving_masses=[r['moving_mass_kg']for r in report['analysis']['mass_and_force_cases']],ideal_deflection=report['analysis']['workbed_compliance_screen']['sum_ideal_components_mm'])),flush=True)
 return 0 if report['passed']else 1

if __name__=='__main__':
 try:code=run()
 except Exception:
  import traceback;traceback.print_exc();code=2
 sys.stdout.flush();sys.stderr.flush();os._exit(code)
