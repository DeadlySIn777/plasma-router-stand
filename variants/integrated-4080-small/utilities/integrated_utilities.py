"""Integrated wet utilities and removable two-level guide screens.

Manufacturer valve dimensions are rounded bounding data, not an exact BRep.
The receiver is atmospheric. No cabinet from the former cassette bed is used.
"""
from pathlib import Path
from functools import lru_cache
import importlib.util,sys,math
import cadquery as cq
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
BASE=ROOT/'variants/extrusion-reengineered'
if str(BASE) not in sys.path:sys.path.insert(0,str(BASE))
import bed as O
import shields as SH
sys.path.insert(0,str(HERE.parent/'bed'))
import integrated_bed as B
sys.path.insert(0,str(HERE.parent))
import mechanical as M
PAN_DROP=M.PAN_LOWERING_MM
STEEL=(.31,.36,.40); FAST=(.48,.51,.53); PIPE=(.22,.27,.30)
def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cyl(r,h,p,d=(0,0,1)):return cq.Solid.makeCylinder(r,h,cq.Vector(*p),cq.Vector(*d))
def mirror(s,side):return s if side=='L' else s.mirror('YZ',(575,0,0))
def bb(s):
 b=s.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def screw(p,d,length,axis=(1,0,0),head=3.):
 return cyl((d-.1)/2,length,p,axis).fuse(cyl(d*.9,head,p,tuple(-q for q in axis))).clean()
def add(p,n,s,c=STEEL):p.append((n,s.clean(),c))

def pan_retainers():
 """Move the removed front-bearer station to real middle bearer cy630."""
 p=[]
 for n,s,c in O.pan_retainers():
  front=n.endswith(('_FL','_FR'))or any(q in n for q in('_FL_','_FR_'))
  if not front:p.append((n,s.translate((0,0,-PAN_DROP)),c));continue
  if 'FRAME_EAR' in n:s=s.translate((0,530,0))
  elif n.endswith('_BOSS'):
   x=116. if '_FL_' in n else 1034.
   s=cyl(7,18.18,(x,680,812.5)).cut(cyl(3,18.38,(x,680,812.4)))
  else:s=s.translate((0,530,3.18))
  n=n.replace('_FL_','_ML_').replace('_FR_','_MR_')
  if n.endswith('_FL'):n=n[:-3]+'_ML'
  if n.endswith('_FR'):n=n[:-3]+'_MR'
  p.append((n,s.translate((0,0,-PAN_DROP)),c))
 return p

@lru_cache(None)
def drain_parts():
 p=[];zc=826.48-PAN_DROP
 pts=[(128,180,zc),(102,154,zc),(102,75,zc),(102,45,796.48-PAN_DROP),(102,45,750-PAN_DROP)]
 mids={0:(128-26/math.sqrt(2),154+26/math.sqrt(2),zc),
       2:(102,75-30/math.sqrt(2),796.48-PAN_DROP+30/math.sqrt(2))}
 add(p,'U_DRAIN_WELDED_OD28_ID24_FORWARD_DOWN',O.swept_pipe(pts,mids,14,12))
 # Rounded published package: 81.28 flow length,76.2 motor width,
 # 109.22 overall transverse height. Axis is vertical, actuator toward +X.
 body=cyl(20,81.28,(102,45,668.72)).cut(cyl(12.446,81.48,(102,45,668.62)))
 add(p,'U_VALVE_USS_MSV00009_BODY_DIMENSION_ENVELOPE',body.translate((0,0,-PAN_DROP)),(.64,.66,.67))
 motor=box(122,6.9,671.26,69.22,76.2,76.2)
 add(p,'U_VALVE_9_24V_NC_ACTUATOR_DIMENSION_ENVELOPE',motor.translate((0,0,-PAN_DROP)),(.17,.21,.27))
 # Never rises. The delayed lateral offset remains outboard of the stay corridor.
 t=math.acos(.88);dy=100*math.sin(t)
 pts=[(102,45,668.72-PAN_DROP),(102,45,630),(102,145,530),(102,500,530),
      (90,500+dy,530),(78,500+2*dy,530),(78,700,530),
      (178,800,530),(300,800,530),(400,800,430),(400,800,410)]
 mids={1:(102,145-100/math.sqrt(2),630-100/math.sqrt(2)),
       3:(2+100*math.cos(t/2),500+100*math.sin(t/2),530),
       4:(178-100*math.cos(t/2),500+2*dy-100*math.sin(t/2),530),
       6:(178-100/math.sqrt(2),700+100/math.sqrt(2),530),
       8:(300+100/math.sqrt(2),800,430+100/math.sqrt(2))}
 add(p,'U_GRAVITY_HOSE_25ID_R100_DELAYED_X_OFFSET',O.swept_pipe(pts,mids,17,12.5),PIPE)
 return tuple(p)

def lowered_overflow_return():
 """Lower pan interface only; retain receiver outlet Z410 and19mm airgap."""
 rim=O.P.PAN_RIM-PAN_DROP
 wall=box(1056,878,465,20,44,rim-465).cut(box(1055.9,879.9,464.9,18.2,40.2,rim-464.8))
 points=[cq.Vector(900,878,462),cq.Vector(1076,878,465),cq.Vector(1076,878,466.9),cq.Vector(900,878,463.9)]
 base=cq.Solid.extrudeLinear(cq.Wire.makePolygon(points+[points[0]]),[],cq.Vector(0,44,0))
 pieces=[wall,base,box(898.1,878,410,1.9,44,53.9)]
 for y in(878.,920.1):
  pp=[cq.Vector(900,y,462),cq.Vector(1076,y,465),cq.Vector(1076,y,477),cq.Vector(900,y,474)]
  pieces.append(cq.Solid.extrudeLinear(cq.Wire.makePolygon(pp+[pp[0]]),[],cq.Vector(0,1.9,0)))
 pieces +=[O.overflow_bent_bracket(y).translate((0,0,-PAN_DROP))for y in(866.,922.)]
 return O.fuse(pieces)

def retained_wet_parts():
 p=[]
 for n,s,c in O.pan_parts():
  if n=='DRAIN_SMOOTH_OD28_ID24_NPT_ADAPTER_HOLD':continue
  if n.startswith('PAN_FRAME_SHIM_PACK_')and '_100_'in n:continue
  p.append((n,s.translate((0,0,-PAN_DROP)),c))
 # Actual additional front pan bearer cy300, not the removed cy100 beam.
 for x in(140.,575.,1010.):
  s=O.yz(x-12.5,25,[(290.,806.5),(310.,806.5),
      (310.,O.pan_floor_z(310.)-1.9),(290.,O.pan_floor_z(290.)-1.9)])
  add(p,f'PAN_FRAME_SHIM_PACK_{int(x)}_300_VERIFY_ACTUAL',s.translate((0,0,-PAN_DROP)),O.AL)
 p+=pan_retainers()
 bad=('WATER_DRAIN_','WATER_1IN_','WATER_VALVE_HANDLE_','WATER_DOWN_ELBOW_','WATER_25MM_GRAVITY_HOSE_')
 for n,s,c in O.water_envelopes():
  if n.startswith(bad):continue
  if n=='OVERFLOW_WELDED_OPEN_RETURN_AIRGAP19':s=lowered_overflow_return()
  elif n.startswith('OVERFLOW_REMOVABLE_SUPPORT_'):s=s.translate((0,0,-PAN_DROP))
  p.append((n,s,c))
 p+=[x for x in SH.shield_parts(False)if x[0].startswith(('SH_RECEIVER_',))]
 return p

GUIDE_SECTIONS=((15.,487.,180.),(489.,961.,650.),(963.,1435.,1180.))
@lru_cache(None)
def guide_screen(side,index):
 lo,hi,cy=GUIDE_SECTIONS[index]
 screen=box(75.,lo,1013.,1.9,hi-lo,94.3)
 clip=box(25.8,cy-30,1013,1.9,60,30).fuse(
     box(27.7,cy-30,1013,47.3,60,1.9),box(73.1,cy-30,1014.9,1.9,60,32.85)).clean()
 for yy in(cy-20,cy+20):clip=clip.cut(cyl(3.3,3.9,(24.8,yy,1033),(1,0,0)))
 return mirror(screen.fuse(clip).clean(),side)

def guide_primitives(side,index):
 """Conservative exterior material boxes; omitted bores only add material."""
 lo,hi,cy=GUIDE_SECTIONS[index]
 return[mirror(s,side)for s in(
  box(75,lo,1013,1.9,hi-lo,94.3),box(25.8,cy-30,1013,1.9,60,30),
  box(27.7,cy-30,1013,47.3,60,1.9),box(73.1,cy-30,1014.9,1.9,60,32.85))]

def guide_handling_pose(side,index,stage,t,shape=None,upright=False):
 """Nine in-plan manual stages, all head tooling removed and bed flat/empty.

 Rear section first slides250forward outside the ATC/common-Z field. Each section
 crosses the center below the gantry, turns acrossX, goes ahead of the bed,
 lowers to200, goes behind the low front crossbar, then reaches its rack.
 """
 lo,hi,clipcy=GUIDE_SECTIONS[index];cy=(lo+hi)/2;front_y=75. if upright else -65.
 dy0=-250. if index==2 else 0.;dx=500. if side=='L'else -500.
 ang=90. if side=='L'else -90.;level=(80.,280.,480.)[index]
 s=guide_screen(side,index)if shape is None else shape
 ops=[('tr',(0,dy0,0)),('tr',(dx,0,0)),('rot',(ang,575,cy+dy0)),
      ('tr',(0,front_y-(cy+dy0),0)),('tr',(0,0,200-1013)),('tr',(0,336-front_y,0)),
      ('tr',(0,0,level-200)),('rot',(-ang,575,336)),
      ('tr',((-395.8 if side=='L'else 395.8),0,0))]
 for k,(typ,v)in enumerate(ops):
  if k>stage:break
  f=t if k==stage else 1.
  if typ=='tr':s=s.translate(tuple(a*f for a in v))
  else:
   a,x,y=v;s=s.rotate((x,y,0),(x,y,1),a*f)
 return s

@lru_cache(None)
def guide_rack_parts():
 p=[]
 for side in('L','R'):
  rack=box(125.8,200,70,1.9,160,656.5-PAN_DROP).fuse(
      box(127.7,200,70,18.1,1.9,656.5-PAN_DROP),box(127.7,358.1,70,18.1,1.9,656.5-PAN_DROP),
      box(127.7,280,724.6-PAN_DROP,40,40,1.9)).clean()
  for xx in(140.,160.):
   rack=rack.cut(cyl(3.3,3.9,(xx,300,723.6-PAN_DROP)))
   add(p,f'U_GUIDE_RACK_M6_EXTERNAL_{side}_{int(xx)}',mirror(screw((xx,300,724.6-PAN_DROP),6,1.9,(0,0,1),3.3),side),FAST)
  for i,(lo,hi,cy)in enumerate(GUIDE_SECTIONS):
   level=(80.,280.,480.)[i]
   rack=rack.fuse(box(127.7,280,level-1.9,72.3,40,1.9)).clean()
   for j,yy in enumerate((336+cy-(lo+hi)/2-20,336+cy-(lo+hi)/2+20),1):
    rack=rack.cut(cyl(3.3,3.9,(124.8,yy,level+20),(1,0,0)))
    nut=box(120.8,yy-5,level+15,5,10,10).cut(cyl(3,7,(119.8,yy,level+20),(1,0,0)))
    add(p,f'U_GUIDE_RACK_M6_WELDNUT_{side}_{i+1}_{j}',mirror(nut,side),FAST)
  add(p,'U_GUIDE_FIXED_UNDER_PAN_RACK_'+side,mirror(rack.clean(),side))
 return tuple(p)

def guide_parts(fitted=True):
 p=list(guide_rack_parts())
 for side in('L','R'):
  for i,(lo,hi,cy)in enumerate(GUIDE_SECTIONS):
   s=guide_screen(side,i)if fitted else guide_handling_pose(side,i,8,1.)
   add(p,f'U_GUIDE_REMOVABLE_SCREEN_{side}_{i+1}',s)
   for j,yy in enumerate((cy-20,cy+20),1):
    screw_shape=screw((27.7,yy,1033),6,1.9,(-1,0,0),3.3)
    if fitted:screw_shape=mirror(screw_shape,side)
    else:
     yy=336+yy-(lo+hi)/2;level=(80.,280.,480.)[i]
     screw_shape=mirror(screw((131.9,yy,level+20),6,12,(-1,0,0),3.3),side)
    add(p,f'U_GUIDE_REUSED_M6_EXTERNAL_{side}_{i+1}_{j}',screw_shape,FAST)
 return p

def utility_parts(*,guards_fitted=True,patches_fitted=None):
 # patches_fitted is retained as an alias for early root changeover callers.
 if patches_fitted is not None:guards_fitted=patches_fitted
 return retained_wet_parts()+list(drain_parts())+guide_parts(guards_fitted)

def metadata():
 return dict(valve_model='USS-MSV00009 / JFMSV00009',valve_unit_price_USD=50.42,shipping_USD=None,
  pan_lowering_mm=PAN_DROP,plasma_slat_top_Z_mm=O.P.SLAT_TOP-PAN_DROP,wood_workplane_Z_unchanged_mm=967.8,
  receiver_outlet_Z_mm=410,receiver_lid_Z_mm=391,overflow_airgap_mm=19,
  valve_package_published_in=dict(port_length=3.2,motor_width=3.,total_height=4.3,bore=.98),
  valve_is_exact_supplier_solid=False,voltage='9–24VAC/DC,2wire auto-return NC',charge_seconds_minimum=60,
  actuator_ambient_C=[-10,40],medium_C=[0,90],max_power_W=5,actuation_seconds=[6,8],
  reservoir_atmospheric=True,compressed_air_connection=False,receiver_usable_capacity_requirement_L=65,
  receiver_listing_is_liquid_rating=False,return_airgap_mm=19.,drain_path_centerline_never_rises=True,
  drain_thread_union_orientation_support_qualified=False,guide_screen_X_mm=[75.,76.9],guide_screen_Z_mm=[1013.,1107.3],
  guide_section_quantity=6,guide_section_sheet_mm=[472.,94.3,1.9],guide_section_gap_mm=2.,
  guide_section_removed_before_bed_tilt=True,guide_screen_handling_path_qualified=False,
  guide_is_direct_splash_screen_not_complete_module_enclosure=True,manufacturer_wiper_bellows_selection_held=True,
  pan_retention_front_station_moved_Y_mm=530.,pan_retention_local_floor_delta_mm=3.18,
  old_cassette_cabinet_included=False,fabrication_release=False,operating_release=False)
