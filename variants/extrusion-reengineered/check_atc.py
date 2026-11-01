"""Reproduce XR2 ATC legal-state geometry, translation and interface screens.
No physical kit geometry or machine M6 is invented. Run with CadQuery Python.
"""
from pathlib import Path
import json,hashlib,os,sys,itertools,math
from functools import lru_cache
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
import atc,motion,frame,bed,shields,params as P
from cad_helpers import bbox,intersection_volume
HERE=Path(__file__).resolve().parent;D=HERE/'review';D.mkdir(exist_ok=True)
def ov(a,b):return all(min(a[k+3],b[k+3])-max(a[k],b[k])>1e-5 for k in range(3))
def pairs(a,b=None):
 aa=[(n,s,bbox(s))for n,s,c in a];bb=aa if b is None else[(n,s,bbox(s))for n,s,c in b];hits=[];num=0
 for i,(n,s,bs)in enumerate(aa):
  for k,t,bt in(bb[i+1:]if b is None else bb):
   if not ov(bs,bt):continue
   num+=1;v=intersection_volume(s,t)
   if v>.05:hits.append(dict(a=n,b=k,volume_mm3=round(v,6)))
 return dict(exact_pairs=num,hits=hits)
def box(b):return cq.Solid.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],cq.Vector(*b[:3]))
def continuous(moving,obstacle,lo,hi,depth_limit=28):
 todo=[(bbox(obstacle),0)];cells=0;empty=0;cleared=0;contact=0
 while todo:
  b,depth=todo.pop();cells+=1
  material=obstacle.intersect(box(b))
  if material.Volume()<1e-7:empty+=1;continue
  # Keep a conservative cover of actual obstacle material, rather than the
  # empty part of a grid cell straddling an exact fitted stop/contact face.
  # Every material point remains in its cell-intersection bounding box.
  actual=bbox(material)
  expanded=box([actual[k]-hi[k]for k in range(3)]+[actual[k+3]-lo[k]for k in range(3)])
  if moving.distance(expanded)>.01:cleared+=1;continue
  #Exact empty conservative cover proves nonpenetration, including designed
  #bearing/stop surface contact. It does not claim positive running clearance.
  if intersection_volume(moving,expanded)<1e-7:contact+=1;continue
  lengths=[b[k+3]-b[k]for k in range(3)];axis=max(range(3),key=lambda k:lengths[k])
  if depth>=depth_limit:return dict(passed=False,cells=cells,unresolved_cell=b,depth=depth)
  mid=(b[axis]+b[axis+3])/2;a=b.copy();c=b.copy();a[axis+3]=mid;c[axis]=mid;todo.extend(((a,depth+1),(c,depth+1)))
 return dict(passed=True,cells=cells,empty_cells=empty,separated_cells=cleared,zero_volume_contact_cells=contact)
def phase_proof(parts,moving_names,lo,hi,external):
 moving=[p for p in parts if p[0]in moving_names];fixed=[p for p in parts if p[0]not in moving_names]+external;records=[]
 fixed_rows=[(n,s,bbox(s))for n,s,c in fixed]
 for n,s,c in moving:
  b=bbox(s);swept=[b[k]+lo[k]for k in range(3)]+[b[k+3]+hi[k]for k in range(3)]
  for nf,sf,bf in fixed_rows:
   if ov(swept,bf):
    r=continuous(s,sf,lo,hi);records.append(dict(moving=n,fixed=nf,**r))
 return dict(candidate_pairs=len(records),proofs=records,passed=all(r['passed']for r in records))

def prismatic_Z_sweep(shape,stroke):
 """Exact positive-Z sweep for shapes proved to have prismatic Z sections.

 Every boundary must be horizontal/vertical planar or Z-coaxial cylindrical.
 Start material plus all horizontal-face extrusions covers every material
 interval, including changes of section and through bores. No bbox substitute.
 """
 pieces=[shape];horizontal=0
 for face in shape.Faces():
  kind=face.geomType()
  if kind=='PLANE':
   nz=abs(face.normalAt().z)
   if nz>1-1e-8:
    pieces.append(cq.Solid.extrudeLinear(face.outerWire(),face.innerWires(),cq.Vector(0,0,stroke)))
    horizontal+=1
   elif nz>1e-8:raise ValueError('Non-prismatic sloped pin boundary')
  elif kind=='CYLINDER':
   if abs(BRepAdaptor_Surface(face.wrapped).Cylinder().Axis().Direction().Z())<1-1e-8:
    raise ValueError('Non-axial cylinder in pin boundary')
  else:raise ValueError('Unproved pin-boundary type '+kind)
 # Keep the exact union as separately checked members. Fusing coincident
 # coplanar boundaries and unifying same-domain faces is unnecessary and can
 # stall OpenCascade. Every member is tested, so overlap is never subtracted.
 pieces.append(shape.translate((0,0,stroke)))
 assert horizontal and all(s.isValid()for s in pieces)
 return pieces,horizontal

def pin_stack_translation(parts,names,stroke,external):
 fixed=[p for p in parts if p[0]not in names]+external
 fixed_rows=[(n,s,bbox(s))for n,s,c in fixed];records=[];sweeps=[]
 for n,s,c in parts:
  if n not in names:continue
  sweep,nfaces=prismatic_Z_sweep(s,stroke);bs=bbox(cq.Compound.makeCompound(sweep))
  sweeps.append(dict(part=n,horizontal_boundary_faces=nfaces,valid=all(p.isValid()for p in sweep)))
  for nf,sf,bf in fixed_rows:
   if not ov(bs,bf):continue
   volume=sum(p.intersect(sf).Volume()for p in sweep if ov(bbox(p),bf))
   records.append(dict(moving=n,fixed=nf,swept_intersection_mm3=volume,passed=volume<1e-7))
  print('pin sweep',n,'checked',flush=True)
 return dict(passed=all(r['passed']for r in records),candidate_pairs=len(records),proofs=records,
  swept_parts=sweeps,method='Exact prismatic positive-Z sweeps from verified horizontal/vertical planar and Z-coaxial cylindrical boundaries; zero-volume designed bearing contacts permitted.')

def pin_actuation_proof(parts,external):
 """Four translated pin/flag stacks, with separate deforming-part proofs.

 A return spring shortens inside its initial annular envelope. The cylinder
 rod grows inside its final envelope, with its tip meeting a flag underside
 translating at the same rate. Those specific relations replace neither a
 clearance check nor a generic collision exemption.
 """
 unlocked=atc.atc_parts(False,True,unlocked=True)
 a={n:s for n,s,c in parts};b={n:s for n,s,c in unlocked}
 names={n for n in a if atc.atc_motion_class(n)=='ATC_pin_Z'}
 stroke_values=[];translation_checks=[];analytic=[];sensor_checks=[]
 springs={n for n in a if n.endswith('RETURN_SPRING_ENVELOPE')}
 for n in sorted(names):
  shift=bbox(b[n])[2]-bbox(a[n])[2];stroke_values.append(shift)
  expected=a[n].translate((0,0,shift))
  err=expected.cut(b[n]).Volume()+b[n].cut(expected).Volume()
  translation_checks.append(dict(part=n,stroke_mm=shift,symmetric_difference_mm3=err,passed=err<1e-6))
 assert stroke_values,'No moving pin stacks'
 stroke=stroke_values[0]
 for spring in sorted(springs):
  stem=spring.removesuffix('RETURN_SPRING_ENVELOPE')
  sl,su=a[spring],b[spring];bl,bu=bbox(sl),bbox(su)
  cx,cy=(bl[0]+bl[3])/2,(bl[1]+bl[4])/2
  outer=(bl[3]-bl[0])/2;h=bl[5]-bl[2]
  inner=math.sqrt(max(0.,outer*outer-sl.Volume()/(math.pi*h)))
  annulus=atc.cyl(outer*2,h,(cx,cy,bl[2])).cut(atc.cyl(inner*2,h+2,(cx,cy,bl[2]-1)))
  annulus_error=annulus.cut(sl).Volume()+sl.cut(annulus).Volume()
  pin=a[stem+'PIN'];bp=bbox(pin);pin_radius=max(bp[3]-bp[0],bp[4]-bp[1])/2
  washer_l,washer_u=bbox(a[stem+'FLAG_WASHER']),bbox(b[stem+'FLAG_WASHER'])
  cap=bbox(a[stem+'SPRING_CAP'])
  spring_checks=dict(annulus_geometry_error_mm3=annulus_error,
   final_spring_outside_initial_mm3=su.cut(sl).Volume(),inner_radius_mm=inner,
   maximum_pin_radius_mm=pin_radius,radial_gap_mm=inner-pin_radius,
   fixed_top_error_mm=abs(bl[5]-bu[5])+abs(bl[5]-cap[2]),
   moving_bottom_error_mm=abs(bl[2]-washer_l[5])+abs(bu[2]-washer_u[5]),
   shortening_matches_pin_stroke_mm=abs((bu[2]-bl[2])-stroke),
   final_height_mm=bu[5]-bu[2],
   final_spring_outside_translated_initial_mm3=su.cut(sl.translate((0,0,stroke))).Volume(),
   initial_rigid_stack_intersection_mm3=sum(a[n].intersect(sl).Volume() for n in names))
  actuator=stem+'SMC_CJPB6_10_NOMINAL';al,au=a[actuator],b[actuator]
  added=au.cut(al);ba=bbox(added);rod_r=max(ba[3]-ba[0],ba[4]-ba[1])/2
  rcx,rcy=(ba[0]+ba[3])/2,(ba[1]+ba[4])/2
  cylinder=atc.cyl(rod_r*2,ba[5]-ba[2],(rcx,rcy,ba[2]))
  rod_error=added.cut(cylinder).Volume()+cylinder.cut(added).Volume()
  flag=a[stem+'FLAG'];bf=bbox(flag)
  local_flag=flag.intersect(atc.cyl(rod_r*2,bf[5]-bf[2]+2,(rcx,rcy,bf[2]-1)))
  rod_checks=dict(initial_outside_final_mm3=al.cut(au).Volume(),
   added_rod_cylinder_error_mm3=rod_error,added_rod_length_error_mm=abs(ba[5]-ba[2]-stroke),
   added_rod_bottom_error_mm=abs(ba[2]-bbox(al)[5]),
   rod_tip_flag_underside_error_mm=abs(bbox(local_flag)[2]-bbox(al)[5]),
   final_tip_flag_underside_error_mm=abs(bbox(local_flag)[2]+stroke-bbox(au)[5]))
  ok=(annulus_error<1e-6 and spring_checks['final_spring_outside_initial_mm3']<1e-6
   and inner-pin_radius>.01 and spring_checks['fixed_top_error_mm']<1e-6
   and spring_checks['moving_bottom_error_mm']<1e-6 and spring_checks['shortening_matches_pin_stroke_mm']<1e-6
   and spring_checks['final_height_mm']>0
   and spring_checks['final_spring_outside_translated_initial_mm3']<1e-6
   and spring_checks['initial_rigid_stack_intersection_mm3']<1e-6
   and all(v<1e-6 for v in rod_checks.values()))
  analytic.append(dict(spring_part=spring,actuator=actuator,passed=ok,spring_relations=spring_checks,rod_relations=rod_checks))
  for idx in (0,1):
   sensor=stem+'E2E_C03SR8_'+str(idx);bs=bbox(a[sensor])
   face=cq.Vertex.makeVertex((bs[0]+bs[3])/2,bs[4],(bs[2]+bs[5])/2)
   gaps=[a[stem+'FLAG'].distance(face),b[stem+'FLAG'].distance(face)]
   sensor_checks.append(dict(sensor=sensor,engaged_flag_gap_mm=gaps[0],withdrawn_flag_gap_mm=gaps[1],
    geometric_target_pass=gaps[idx]<=.56 and gaps[1-idx]>.8,
    scope='Point at nominal sensing-face centre to opaque steel flag; not an electrical sensor commissioning test.'))
 # Only the specifically proved, monotonically shortening annuli are omitted
 # from this translated-stack calculation. Their radial/axial relations above
 # explicitly prove no penetration throughout the same stroke.
 rigid=[p for p in parts if p[0]not in springs]
 translation=pin_stack_translation(rigid,names,stroke,external)
 passed=(all(abs(v-stroke)<1e-6 for v in stroke_values) and stroke>0
  and all(x['passed']for x in translation_checks+analytic)
  and all(x['geometric_target_pass']for x in sensor_checks) and translation['passed'])
 return dict(passed=passed,stroke_mm=stroke,rigid_stack_translation=translation,
  endpoint_translation_identity=translation_checks,deforming_part_relations=analytic,pin_flag_targets=sensor_checks,
  scope='Continuous nominal pin/flag translation; return-spring annuli shorten inside their initial envelopes and rods grow inside final envelopes with tips tracking flag undersides. Spring force/solid height/rod load and actual sensing remain physical acceptance items.')
def run():
 # These geometry builders are pure. Retain the nine cutting poses across
 # wood gate states and plasma, instead of cycling through an eight-item LRU
 # and rebuilding every full model. This changes no checked geometry/scope.
 motion._wood=lru_cache(maxsize=64)(motion._wood.__wrapped__)
 atc._cached=lru_cache(maxsize=32)(atc._cached.__wrapped__)
 guide_source=Path(atc.guide_source.__file__).resolve()
 assert guide_source==(atc.SOURCE_GUIDE/'hardware.py').resolve(),'Unexpected imported ATC hardware module'
 sources=[HERE/x for x in('atc.py','motion.py','params.py','frame.py','bed.py','shields.py','check_atc.py')]+[guide_source]
 # Frozen motion helpers create actual solids too; include their raw sources,
 # not merely the importing wrapper's hash.
 sources+= [HERE.parents[1]/n for n in motion.interface_metadata()['source_sha256']]
 sources=list(dict.fromkeys(sources))
 hashes=lambda:{str(p.relative_to(HERE.parents[1])):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources}
 start=hashes();checks={};f=frame.frame_parts();beds={h:bed.bed_parts(h)for h in(False,True)};guards={h:shields.shield_parts(h)for h in(False,True)}
 safe=motion.motion_parts(False,700,255,P.Z_TRAVEL)
 spindle_full=bbox(next(s for n,s,c in safe if n=='TOOL_SPINDLE_65x259'))[2]
 interface=atc.interface_metadata()
 reference0=spindle_full-P.Z_TRAVEL;stocktop=P.DRY_TOP+atc.STOCK_HEIGHT
 gap=interface['required_running_gap_mm']
 Pmin,Pmax=interface['loaded_tool_projection_P_mm']
 radius=interface['loaded_tool_radius_mm']
 assert abs(reference0-interface['nominal_spindle_reference_zero'])<1e-6
 R=atc.retained_projection_allowance();kit_top=atc.MAG_BASE+atc.KIT_MAX_HEIGHT
 Hmin=max(0.,Pmax-R);engage_min=atc.MAG_BASE+Hmin-reference0;engage_max=atc.MAG_BASE+atc.KIT_MAX_HEIGHT-reference0
 zclear=stocktop+gap+Pmax-reference0
 stock=[('FULL_DRYBED_40MM_STOCK_CLAMP_CAPACITY',atc.box(109,103.4,P.DRY_TOP,932,1034,atc.STOCK_HEIGHT),(.5,.1,.1))]
 clearance_pass=(R>=0 and spindle_full-Pmax-kit_top>=gap and atc.LOWER_BASE-stocktop>=gap and atc.MAG_BASE-R-stocktop>=gap and spindle_full-atc.MAG_BASE>=90. and 0<=zclear<=P.Z_TRAVEL and 0<=engage_min<=engage_max<=P.Z_TRAVEL)
 clearance=dict(magazine_base_Z_mm=atc.MAG_BASE,kit_height_capacity_mm=atc.KIT_MAX_HEIGHT,kit_top_Z_mm=kit_top,stock_top_Z_mm=stocktop,stock_plus_clamps_mm=atc.STOCK_HEIGHT,spindle_reference_at_zero_Z_mm=reference0,spindle_reference_at_full_Z_mm=spindle_full,reference_is_measured_nut_plane=False,loaded_projection_P_mm=[Pmin,Pmax],max_loaded_projection_for5mm_gap_mm=spindle_full-kit_top-gap,loaded_P50_tip_at_full_Z_mm=spindle_full-Pmax,loaded_P50_overflight_gap_mm=spindle_full-Pmax-kit_top,minimum_P50_safe_Z_lift_mm=zclear,retained_projection_below_base_R_mm=R,retained_tip_to_stock_mm=atc.MAG_BASE-R-stocktop,conditional_nut_seat_height_above_base_H_mm=[Hmin,atc.KIT_MAX_HEIGHT],conditional_reference_datum_engagement_Z_lift_mm=[engage_min,engage_max],actual_nut_plane_offset_mm=None,manufacturer90mm_packaging_margin_mm=spindle_full-atc.MAG_BASE-90.,actual_kit_interface_verified=False)
 def checkpoint():
  (D/'atc-check-progress.json').write_text(json.dumps(dict(source_sha256=start,static_states=checks),indent=2))
 for name,dep,gate,unlock in [('park_closed',False,False,False),('park_open',False,True,False),('deployed_open',True,True,False),('deployed_unlocked',True,True,True),('park_unlocked',False,True,True)]:
  p=atc.atc_parts(False,dep,gate_open=gate,unlocked=unlock)
  checks[name]=dict(invalid=[n for n,s,c in p if not s.isValid()or len(s.Solids())!=1],self=pairs(p),frame=pairs(p,f),bed=pairs(p,beds[False]),shields=pairs(p,guards[False]),safe_head=pairs(p,safe))
  print(name,'hits',sum(len(v.get('hits',[]))for v in checks[name].values()if isinstance(v,dict)),flush=True);checkpoint()
 cut=[]
 for hot in(False,True):
  for gate in((False,)if hot else(False,True)):
   p=atc.atc_parts(hot,gate_open=gate)
   for x,y,z in[(575.,775.,P.Z_TRAVEL/2),*itertools.product((175.,975.),(275.,1275.),(0.,P.Z_TRAVEL))]:cut.append(dict(hot=hot,gate_open=gate,pose=[x,y,z],**pairs(p,motion.motion_parts(hot,y,x,z))))
 transport=[]
 for travel in(0.,50.,100.,150.,200.):
  p=atc.atc_parts(False,travel_mm=travel,gate_open=True,unlocked=True)
  transport.append(dict(travel_mm=travel,self=pairs(p),external=pairs(p,f+beds[False]+guards[False]+safe)))
 gates=[]
 for g in(0.,.25,.5,.75,1.):
  p=atc.atc_parts(False,gate_fraction=g,gate_pin_withdrawn=True)
  gates.append(dict(fraction=g,self=pairs(p),external=pairs(p,f+beds[False]+guards[False]+safe)))
 xp0,yp0,xp1,yp1=atc.POCKET_REGION;pickups=[]
 for x,y,z in itertools.product((xp0,xp1),(yp0,yp1),(engage_min,engage_max,P.Z_TRAVEL)):
  p=atc.atc_parts(False,True);head=motion.motion_parts(False,y+153.6,x,z)
  cutter=atc.cyl(2*radius,Pmax,(x,y,reference0+z-Pmax))
  pickups.append(dict(pose_X_Ytool_Z=[x,y,z],mechanism=pairs(p,head),loaded_cutter=pairs([('REFERENCE_P50_D15_CUTTER',cutter,(1,0,0))],p+stock)))
 pp=atc.atc_parts(False,True,unlocked=True);classes=atc._cached(0.,1.,True)[1];racknames={n for n in classes if classes[n]=='rack'}
 rackproof=phase_proof(pp,racknames,[0,0,0],[0,200,0],f+beds[False]+guards[False]+safe+stock)
 print('rack continuous',rackproof['passed'],flush=True)
 capacity=atc.acceptance_parts(True)
 capacity_static=pairs(capacity,pp+stock)
 capacityproof=phase_proof(capacity,{n for n,s,c in capacity},[0,0,0],[0,200,0],[p for p in pp if p[0]not in racknames]+f+beds[False]+guards[False]+safe+stock)
 print('capacity continuous',capacityproof['passed'],'static hits',capacity_static['hits'],flush=True)
 gp=atc.atc_parts(False,gate_fraction=0.,gate_pin_withdrawn=True);classes=atc._cached(200.,0.,False,True)[1];gatenames={n for n in classes if classes[n]=='gate'}
 gateproof=phase_proof(gp,gatenames,[0,0,-atc.GATE_STROKE],[0,0,0],f+beds[False]+guards[False]+safe+atc.acceptance_parts(False)+stock)
 print('gate continuous',gateproof['passed'],flush=True)
 #The fixedZbody cannot fly over a magazine by retractingoutputZ. Enter via
 #X255 first, then traverseX only after modulefront is behindkitrear.
 deployed=atc.atc_parts(False,True);entry_head=[p for p in safe if not motion.is_stationary(p[0])]
 entrycutter=('ENTRY_P50_D15',atc.cyl(2*radius,Pmax,(255,700-153.6,spindle_full-Pmax)),(1,0,0));entry_head.append(entrycutter)
 entryproof=phase_proof(entry_head,{n for n,s,c in entry_head},[0,0,0],[0,yp0+153.6-700,0],deployed+capacity+stock)
 print('entry continuous',entryproof['passed'],flush=True)
 traverse={}
 atrow=motion.motion_parts(False,yp0+153.6,255,P.Z_TRAVEL)
 for cls in('Y_gantry_or_drive','Y_X_head','Y_X_Z_tool'):
  group=[p for p in atrow if motion.part_motion_class(p[0])==cls]
  if cls=='Y_X_Z_tool':group.append(('OVERFLIGHT_P50_D15',atc.cyl(2*radius,Pmax,(255,yp0,spindle_full-Pmax)),(1,0,0)))
  traverse[cls]=phase_proof(group,{n for n,s,c in group},[0,0,0],[0 if cls=='Y_gantry_or_drive'else xp1-255,yp1-yp0,0],deployed+capacity+stock)
 #Continuous vertical physicalmechanism/stockcheck; actualkitpocketvoidsare
 #unknown, so thefullsuppliercapacitybox is deliberatelynot treated asvoid.
 vertical={}
 pocket_head=motion.motion_parts(False,yp0+153.6,xp0,P.Z_TRAVEL)
 for cls in('Y_gantry_or_drive','Y_X_head','Y_X_Z_tool'):
  group=[p for p in pocket_head if motion.part_motion_class(p[0])==cls]
  if cls=='Y_X_Z_tool':group.append(('POCKET_FIELD_P50_D15',atc.cyl(2*radius,Pmax,(xp0,yp0,spindle_full-Pmax)),(1,0,0)))
  lo=[0,0,engage_min-P.Z_TRAVEL if cls=='Y_X_Z_tool'else 0]
  hi=[0 if cls=='Y_gantry_or_drive'else xp1-xp0,yp1-yp0,0]
  vertical[cls]=phase_proof(group,{n for n,s,c in group},lo,hi,deployed+stock)
 pinproof=pin_actuation_proof(atc.atc_parts(False,True),f+beds[False]+guards[False]+safe+stock)
 # Main travel report covers wood gate open and plasma gate closed. Prove
 # the additional legal parked/closed wood state here over the full XYZ box.
 closed=atc.atc_parts(False,gate_open=False);closed_cut={}
 initial=motion.motion_parts(False,275.,175.,0.)
 for cls in('Y_gantry_or_drive','Y_X_head','Y_X_Z_tool'):
  group=[p for p in initial if motion.part_motion_class(p[0])==cls]
  closed_cut[cls]=phase_proof(group,{n for n,s,c in group},[0,0,0],
   [0 if cls=='Y_gantry_or_drive'else P.X_TRAVEL,P.Y_TRAVEL,P.Z_TRAVEL if cls=='Y_X_Z_tool'else 0],closed)
 end=hashes();static_pass=all(not a['invalid']and all(not v.get('hits')for v in a.values()if isinstance(v,dict))for a in checks.values())
 sample_pass=not any(r['hits']for r in cut)and all(not a['self']['hits']and not a['external']['hits']for a in transport+gates)and not any(a['mechanism']['hits']or a['loaded_cutter']['hits']for a in pickups)
 continuous_pass=all(p['passed']for p in [rackproof,gateproof,capacityproof,entryproof,*traverse.values(),*vertical.values(),pinproof,*closed_cut.values()])
 I=(50.8*25.4**3-44.45*19.05**3)/12;L=924.;M=19000.;beam=M*L*L/(72*math.sqrt(3)*200000*I)
 yaw=dict(applied_Z_torque_Nm=19.,two_sided_pin_span_mm=L,pin_shear_N=M/L,pin_bearing_MPa=(M/L)/(6*4),pin_diametral_clearance_mm=.05,translation_play_mm=.025,pocket_angular_play_mm=.05/L*230,beam_I_vertical_axis_mm4=I,paired_support_point_moment_beam_deflection_mm=beam,screen_only=True,actual_joint_guide_pin_and_spindle_proof_required=True)
 r=dict(revision=P.REVISION,mechanism_geometry_pass=bool(start==end and static_pass and sample_pass and continuous_pass and not capacity_static['hits']),selectedZ_clearance_case_pass=bool(clearance_pass),actual_kit_interface_verified=False,source_sha256=end,source_consistent_during_check=start==end,legal_static_states=checks,cutting_poses=cut,transport_samples=transport,gate_samples=gates,pickup_samples=pickups,continuous_rack_translation=rackproof,continuous_gate_translation=gateproof,capacity_static=capacity_static,continuous_capacity_translation=capacityproof,entry_bypass_X255=entryproof,entry_bypass_XY_head_traverse=traverse,continuous_physical_pickup_XYZ_field=vertical,continuous_parked_closed_wood_XYZ=closed_cut,continuous_pin_actuation=pinproof,selected_Z_clearance_case=clearance,Z_torque_screen=yaw,interface=atc.interface_metadata(),scope='Exactsampledlegalstates;conservativecontinuousnonpenetrationforrack,gate,declaredcapacity,entry,pocketXYZfield,closedwoodXYZandnominalpinactuation.Zero-volumebearing/stopcontactsallowed,notclaimedpositiverunningclearance.Actualvendorpocketvoids/nutdatum/realcutters/cables/airhosesunverified;notanM6programorcollisionproofforactualpocketengagement.',release=False)
 (D/'atc-check.json').write_text(json.dumps(r,indent=2)+'\n');print('ATC',r['mechanism_geometry_pass'],'Zcase',r['selectedZ_clearance_case_pass'],'continuous',continuous_pass,flush=True)
 return 0 if r['mechanism_geometry_pass']and r['selectedZ_clearance_case_pass']else 1
if __name__=='__main__':
 try:code=run()
 except Exception:
  import traceback;traceback.print_exc();code=2
 sys.stdout.flush();sys.stderr.flush();os._exit(code)
