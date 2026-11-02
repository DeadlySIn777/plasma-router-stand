"""Full uncut 20100/drill-only HDPE bed with a real front top-plane hinge.

Nominal engineering geometry. Independent metal sleeves bypass plastic preload.
Gas springs assist handling; paired positively pinned stays support the open bed.
No original owner head geometry or frozen prior design is modified.
"""
from pathlib import Path
from functools import lru_cache
import importlib.util,sys,math
import cadquery as cq

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'variants/extrusion-reengineered'
spec=importlib.util.spec_from_file_location('integrated_bed_frame',BASE/'frame.py')
if str(BASE)not in sys.path:sys.path.insert(0,str(BASE))
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
X0,Y0,W,L=75.,-40.,1000.,1220.
TOP=960.8;PROFILE_BOTTOM=TOP-20.;HDPE_BOTTOM=PROFILE_BOTTOM-25.4
ASSEMBLY_Z_SHIFT=7.;WORK_TOP=TOP+ASSEMBLY_Z_SHIFT
CROSS_BOTTOM=HDPE_BOTTOM-40.;CROSS_CENTRES=(100.,395.,780.,1140.)
CROSS_X0,CROSS_LENGTH=85.,980.
PIVOT=(-100.,TOP)
GAS_ROOT=(-70.,768.);GAS_MOVING=(395.,905.4)
STAY_ROOT=(-40.,743.);STAY_MOVING=(395.,855.4)
GAS_FORCE=889.;GAS_MIN,GAS_MAX=450.,700.
GAS_AXES=(59.15,1090.85)
STAY_AXES=(54.,1096.)
AL=(.65,.70,.74);HDPE=(.16,.48,.57);STEEL=(.25,.31,.34);BLACK=(.12,.15,.17)

def bounds(s):
 b=s.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cyl(d,h,p,direction=(0,0,1)):return cq.Solid.makeCylinder(d/2,h,cq.Vector(*p),cq.Vector(*direction))
def ring(od,id,h,p,direction=(0,0,1)):return cyl(od,h,p,direction).cut(cyl(id,h,p,direction)).clean()
def item(n,s,material,move=False,note=''):
 return dict(id=n,shape=s.clean(),material=material,moving_bed=move,notes=note,color=HDPE if material=='HDPE'else(AL if material=='aluminum'else STEEL))
def rotate(s,a):return s.rotate((0,*PIVOT),(1,*PIVOT),float(a))
def yzpoint(p,a):
 y,z=p;dy,dz=y-PIVOT[0],z-PIVOT[1];t=math.radians(a)
 return(PIVOT[0]+dy*math.cos(t)-dz*math.sin(t),PIVOT[1]+dy*math.sin(t)+dz*math.cos(t))
def line_cylinder(d,a,b):
 v=cq.Vector(*b)-cq.Vector(*a)
 return cyl(d,v.Length,a,v.toTuple())
def tube_between(outer,wall,a,b):
 v=cq.Vector(*b)-cq.Vector(*a)
 plane=cq.Plane(origin=a,xDir=(1,0,0),normal=v.toTuple())
 return cq.Workplane(plane).rect(outer,outer).rect(outer-2*wall,outer-2*wall).extrude(v.Length).val()
def plane_plate(points,thickness,origin=(0,0,0),normal=(0,0,1),xdir=(1,0,0)):
 return cq.Workplane(cq.Plane(origin=origin,xDir=xdir,normal=normal)).polyline(points).close().extrude(thickness).val()

@lru_cache(None)
def profile_section(length=1220.):
 """Recovered nominal supplier 20100 section, with omitted transition radii.

 Geometry copied from prior owner bed_details.profile_20100; unchanged section.
 It does not certify a different Amazon extrusion die or lip/nut capacity.
 """
 s=cq.Workplane('XY').box(100,20,length,centered=False).edges('|Z').fillet(1.5).val();voids=[]
 def cutwire(points):return plane_plate(points,length+2,origin=(0,0,-1))
 for c in(10,30,50,70,90):
  low=[(c-3.1,-.5),(c+3.1,-.5),(c+3.1,1.3),(c+5.5,1.3),(c+5.5,2.9),(c+3.9,6.1),(c-3.9,6.1),(c-5.5,2.9),(c-5.5,1.3),(c-3.1,1.3)]
  voids.extend([cutwire(low),cutwire([(x,20-y)for x,y in low]),cyl(5,length+2,(c,10,-1))])
 for c in(20,40,60,80):
  wire=[(c-2.8,1.8),(c+2.8,1.8),(c+2.8,3.3),(c+6.1,6.7),(c+6.1,13.3),(c+2.8,16.7),(c+2.8,18.2),(c-2.8,18.2),(c-2.8,16.7),(c-6.1,13.3),(c-6.1,6.7),(c-2.8,3.3)]
  voids.append(cutwire(wire))
 left=[(-.5,6.4),(1.3,6.4),(1.3,4.5),(2.9,4.5),(5.7,7.6),(5.7,12.4),(2.9,15.5),(1.3,15.5),(1.3,13.6),(-.5,13.6)]
 voids.extend([cutwire(left),cutwire([(100-x,y)for x,y in left])])
 return s.cut(cq.Compound.makeCompound(voids)).clean()

def anchor_rows():
 return[(cy,x)for cy in CROSS_CENTRES for i in range(10)for x in(X0+100*i+30,X0+100*i+70)]

@lru_cache(None)
def deck_local_parts():
 p=[];anchors=anchor_rows();ref=(395.,545.)
 for i,zz in enumerate((HDPE_BOTTOM,HDPE_BOTTOM+12.7),1):
  s=box(X0,Y0+.4,zz,W,1219.2,12.7)
  cuts=[cyl(13.2 if(cy,x)==ref else 22.,14.7,(x,cy,zz-1))for cy,x in anchors]
  s=s.cut(cq.Compound.makeCompound(cuts)).clean()
  p.append(item(f'FULL_HDPE_{i}',s,'HDPE',True,'1000x1219.2x12.7 full rectangle from48in-wide sheet;80 circular through holes only. Profiles overhang0.4mm each end. No pockets, slots, counterbores or surfacing.'))
 prof=profile_section(L).rotate((0,0,0),(1,0,0),90).translate((0,L,0))
 for i in range(10):p.append(item(f'UNCUT_20100_{i+1:02}',prof.translate((X0+100*i,Y0,PROFILE_BOTTOM)),'aluminum',True,'Uncut1220 length, profile axis Y. End-load compatible M5 nuts before assembly.'))
 for j,cy in enumerate(CROSS_CENTRES,1):
  s=F.bar(CROSS_X0,cy-40,CROSS_BOTTOM,'X',CROSS_LENGTH,flat=True)
  s=s.cut(cq.Compound.makeCompound([cyl(13.1,42,(x,cy,CROSS_BOTTOM-1))for c,x in anchors if c==cy])).clean()
  if j in(1,4):
   for xx,d in((85.,(1,0,0)),(1065.,(-1,0,0))):
    for yy in(cy-20,cy+20):s=s.cut(cyl(8.,22,(xx,yy,895.4),d))
  p.append(item(f'BED_4080_CROSS_{j}',s,'aluminum',True,'980mm4080 laid80Yx40Z;20 sleeve bores13.1 through. Final actual section/lip fit and modified-section capacity require acceptance.'))
 for side in('L','R'):
  cap=box(78.65,1100,875.4,6.35,80,40.)
  for yy in(1120.,1160.):cap=cap.cut(cyl(8.5,8.35,(77.65,yy,895.4),(1,0,0)))
  p.append(item('BED_REAR_END_CAP_'+side,_mirror(cap.clean(),side),'steel',True,'6.35endplate, two8.5through fixingholes into rear4080end cores. Carries closed-mode side drawdowns through metal only.'))
 for k,(cy,x)in enumerate(anchors,1):
  p.append(item(f'BED_COLUMN_{k:02}',ring(12.7,6.35,65.4,(x,cy,CROSS_BOTTOM)),'aluminum',True,'Straight compression tube:12.7ODx6.35ID,65.4 long nominal. Fit length to actual HDPE stack; metal supports profile and bypasses plastic preload.'))
  screw=cyl(5,70,(x,cy,CROSS_BOTTOM)).fuse(cyl(8.5,5,(x,cy,CROSS_BOTTOM-5))).clean()
  p.append(item(f'BED_M5x70_{k:02}',screw,'steel',True,'Underhead directly on square sleeve end.2.7 nominal nut engagement plus0.6 tip; no washer stack. Actual compatible nut/torque must be selected.'))
  nut=box(x-4,cy-4,PROFILE_BOTTOM+1.3,8,8,2.7).cut(cyl(5,4.7,(x,cy,PROFILE_BOTTOM+.3))).clean()
  p.append(item(f'BED_M5_BOTTOM_NUT_{k:02}',nut,'steel',True,'Recovered8x8x2.7 nominal slot-nut envelope, end-loaded. Actual selected nut and lip capacity remain a supplier fit acceptance item.'))
 return tuple(p)

def _mirror(s,side):return s if side=='L'else s.mirror('YZ',(575,0,0))

def fixed_receiver_parts():
 p=[];t=3.175
 for side in('L','R'):
  # Use ordinary angle stock, trimming the vertical leg to31.75mm.
  flange=box(72.,170,CROSS_BOTTOM-t,54.,1050,t)
  web=box(72.,170,CROSS_BOTTOM,t,1050,31.75)
  # Local clearance for the moving assist clevis, replaced by an integral
  # lower reinforcement web. No unsupported slit through the bearing flange.
  web=web.cut(box(71.,355,CROSS_BOTTOM-1,t+2,100,34.))
  flange=flange.cut(box(71.,355,CROSS_BOTTOM-t-1,4.175,100,t+2))
  reinforcement=box(76.2,345,840.4,t,120,35.)
  s=flange.fuse(web,reinforcement).clean()
  for cy in CROSS_CENTRES:s=s.cut(cyl(12.5,t+2,(105.,cy,CROSS_BOTTOM-t-1)))
  for cy in(100.,630.,1180.):
   for xx in(96.,116.):
     for yy in(cy-20,cy+20):
      s=s.cut(cyl(5.5,t+2,(xx,yy,CROSS_BOTTOM-t-1)))
      s=s.cut(cq.Solid.makeCone(2.75,5.,2.75,cq.Vector(xx,yy,CROSS_BOTTOM-2.75)))
  for yy in(1120.,1160.):s=s.cut(cyl(8.5,5.175,(71.,yy,895.4),(1,0,0)))
  p.append(item(f'BED_RECEIVER_ANGLE_{side}',_mirror(s.clean(),side),'steel',False,'1050mm formed/trimmed angle54horizontalx31.75verticalx3.175. Downward loads bear on lowered4080 dry arms; seatZ882.4world. Actual flatness fitted with metal shims only.'))
  pad=box(76.2,60,CROSS_BOTTOM-t,49.8,80,t)
  pad=pad.cut(cyl(12.5,t+2,(105.,100.,CROSS_BOTTOM-t-1)))
  for xx in(96.,116.):
   for yy in(80.,120.):pad=pad.cut(cyl(5.5,t+2,(xx,yy,CROSS_BOTTOM-t-1))).cut(cq.Solid.makeCone(2.75,5.,2.75,cq.Vector(xx,yy,CROSS_BOTTOM-2.75)))
  # Frontwoodload is carried by the actual hinge. Frontdryarms and their
  # loose pads are omitted to keep the gas/stay corridor open.
  # Front top-plane hinge: two stationary6.35 cheeks and one moving cheek.
  # All pin axes are global X; fixed support bolts attach to existing4080header.
  base=box(25.8,-140,930.8,6.35,80,70.)
  for yy in(-120.,-80.):
   for zz in(960.,993.):base=base.cut(cyl(6.6,8.35,(24.8,yy,zz),(1,0,0)))
  cheek=box(57.15,-125,940.8,6.35,50,32.2)
  bridge=box(32.15,-125,940.8,25.,50,6.35)
  fixed=base.fuse(cheek,bridge).cut(cyl(12.1,8.35,(56.15,-100,TOP),(1,0,0))).clean()
  p.append(item(f'BED_HINGE_FIXED_{side}',_mirror(fixed,side),'steel',False,'Welded6.35mm fixed hinge bracket;4M6front-vertical-post fasteners atY−120/−80,Z967/1000world. Paired hinge axisY−100/Z967.8world; actual pin/bushing and weld loads require qualification.'))
  pin=cyl(12,24.2,(54.3,-100,TOP),(1,0,0)).fuse(cyl(18,3,(51.3,-100,TOP),(1,0,0))).clean()
  p.append(item(f'BED_HINGE_PIN_{side}',_mirror(pin,side),'steel',False,'Retained12mm hinge pin. Source model smooth, specify retained steel pin and bushings; no threaded pivot running surface.'))
  for tag,point in(('GAS',GAS_ROOT),('CAPTURE',STAY_ROOT)):
   cy,zz=point;plate=box(40.7 if tag=='GAS'else 25.8,-140,zz-40,6.35,80 if tag=='GAS'else 120,80)
   for yy in(-120.,-80.):
    for z in(zz-20,zz+20):
     plate=plate.cut(cyl(6.6,8.35,((39.7 if tag=='GAS'else 24.8),yy,z),(1,0,0)))
     if tag=='GAS':
      spacer=ring(12.7,6.35,14.9,(25.8,yy,z),(1,0,0))
      p.append(item(f'BED_{tag}_ROOT_SPACER_{side}_{int(yy)}_{int(z)}',_mirror(spacer,side),'aluminum',False,'14.9mm metal standoff to widened frontpost; made from same12.7ODtube stock. M6profile/Tnut attachment selected for actual die.'))
   plate=plate.cut(cyl(8.5 if tag=='GAS'else 10.2,8.35,((39.7 if tag=='GAS'else 24.8),cy,zz),(1,0,0)))
   if tag=='CAPTURE':
    floor=box(32.15,cy-20,zz-19.15,33.85,40,6.35)
    ears=ring(24,10.2,3.175,(44.45,cy,zz),(1,0,0)).fuse(ring(24,10.2,3.175,(62.825,cy,zz),(1,0,0)))
    stems=box(44.45,cy-6,zz-20,3.175,12,18.2).fuse(box(62.825,cy-6,zz-20,3.175,12,18.2))
    plate=plate.fuse(floor,ears,stems).cut(cyl(10.2,42.2,(24.8,cy,zz),(1,0,0))).clean()
    # Independent gas-column/stud clearance through the rear capture bracket;
    # the two stationary anchor sets are not overlapping fictitious solids.
    for yy in(-120.,-80.):
     for z in(GAS_ROOT[1]-20,GAS_ROOT[1]+20):plate=plate.cut(cyl(13.1,9.,(24.8,yy,z),(1,0,0)))
    plate=plate.cut(cyl(8.5,9.,(24.8,GAS_ROOT[0],GAS_ROOT[1]),(1,0,0)))
   p.append(item(f'BED_{tag}_ROOT_MOUNT_{side}',_mirror(plate.clean(),side),'steel',False,'6.35mm anchorplate;4M6post mounts atY−120/−80,Zanchor±20. Gas uses14.9standoffs; capture directpost. Cantilever web transfers anchor load within its plane. Uppercontacthardware kept separate.'))
   if tag=='GAS':
    stud=cyl(8,27.1,(27.05,cy,zz),(1,0,0))
    p.append(item(f'BED_GAS_ROOT_BALL_STUD_{side}',_mirror(stud,side),'steel',False,'10mmballstudM8x20thread plus7.1mmexposedneck; ballcentre12.1mmfromface. Actualballstudnecksetsfittedspacer, not a claimed supplied-kit bracket.'))
 return p

def closed_drawdowns():
 p=[]
 for side in('L','R'):
  for i,yy in enumerate((1120.,1160.),1):
   washer=ring(16,8.5,1.6,(70.4,yy,895.4),(1,0,0))
   spacer=ring(12.7,8.5,3.475,(75.175,yy,895.4),(1,0,0))
   screw=cyl(8,35,(70.4,yy,895.4),(1,0,0)).fuse(cyl(13,8,(62.4,yy,895.4),(1,0,0)))
   for tag,shape in(('WASHER',washer),('SPACER',spacer),('M8x35',screw)):
    p.append(item(f'BED_CLOSED_{tag}_{side}_{i}',_mirror(shape.clean(),side),'steel',False,'Closed-mode retained hardware; withdraw both screws per side and store before tilting. M8nominal major thread bore,20.4mm engagement in rear4080core; actual tap/slot/core capacity held.'))
 return p

def deck_brackets():
 p=[]
 for side in('L','R'):
  # Hinge arm connects front crossbar to the top-plane pivot without HDPE cuts.
  plate=plane_plate([(0,0),(270,0),(270,120),(0,120)],9.525,
      origin=(65.475,-125,860.8),normal=(1,0,0),xdir=(0,1,0))
  plate=plate.cut(cyl(12.1,11.525,(64.475,-100,TOP),(1,0,0)))
  spacer=box(75.,60,875.4,10.,80,40.)
  for yy in(80.,120.):
   plate=plate.cut(cyl(8.5,11.525,(64.475,yy,895.4),(1,0,0))).cut(cyl(14.2,4.6,(65.475,yy,895.4),(1,0,0)))
   spacer=spacer.cut(cyl(8.5,12,(74.,yy,895.4),(1,0,0)))
   bolt=cyl(8,35,(70.075,yy,895.4),(1,0,0)).fuse(cyl(14,4.4,(65.675,yy,895.4),(1,0,0)))
   p.append(item(f'BED_HINGE_M8x35_BUTTON_{side}_{int(yy)}',_mirror(bolt.clean(),side),'steel',True,'Recessed14ODx4.4buttonhead;35underhead,20.075mmnominalend-core engagement. Actual ISO7380head/drive and core tap fit verified before use.'))
  p.append(item(f'BED_HINGE_MOVING_SIDEPLATE_{side}',_mirror(plate.clean(),side),'aluminum',True,'270x120x9.525full-thickness sidearm, pivot150mmforwardofearlierlayout. Two14.2x4.6counterbores and8.5through;12.1pivot bore. No HDPE/profile relief. Owned3/8blank allocation only if globally unique.'))
  p.append(item(f'BED_HINGE_SPACER_{side}',_mirror(spacer.clean(),side),'aluminum',True,'80x40x10new spacer,2D8.5through; not supplied by9.525sheet without machining/newstock.'))
  # Shared gas/stay mounting bracket on the395mm crossbar end.
  web=box(78.65,365,885.4,6.35,60,30.)
  upper=box(44.45,365,909.05,34.2,60,6.35).cut(box(46.15,364,906.5,26,46,12))
  top_ear=box(75.2,375,895.4,3.175,40,20.)
  lower_ear=ring(24,10.2,3.175,(62.825,395,855.4),(1,0,0)).fuse(box(62.825,405.4,855.4,3.175,10,53.65))
  far_ear=ring(24,10.2,3.175,(44.45,395,855.4),(1,0,0)).fuse(box(44.45,405.4,855.4,3.175,10,53.65))
  s=web.fuse(upper,top_ear,lower_ear,far_ear).clean()
  for yy in(375.,415.):s=s.cut(cyl(8.5,8.35,(77.65,yy,895.4),(1,0,0)))
  s=s.cut(cyl(8.5,5.175,(74.2,395,905.4),(1,0,0)))
  s=s.cut(cyl(10.2,24.,(43.45,395,855.4),(1,0,0)))
  p.append(item(f'BED_ASSIST_C_BRACKET_{side}',_mirror(s,side),'steel',True,'Fabricated6.35steel bracket;2M8x25end-core bolts, top10mmgasballstud and lowerstayclevis. Ballstud axesX preserve spherical articulation inYZ. Ordinary welded stock; weld capacity acceptance required.'))
 return p

def gas_and_stays(angle=0.):
 p=[];t=math.radians(angle)
 for side,x in zip(('L','R'),GAS_AXES):
  gm=yzpoint(GAS_MOVING,angle);a=(x,*GAS_ROOT);b=(x,*gm);v=cq.Vector(*b)-cq.Vector(*a);u=v.normalized();ln=v.Length
  p.append(item(f'BED_GAS_ROD_{side}',line_cylinder(10,a,tuple(cq.Vector(*a)+u*(ln-220))),'steel',False,'ARANA28in200lb candidate reference only. Exactcompressedlengthand889Nlabelrequireverification;10rod/24body are acceptance envelopes, not OEMCAD.'))
  start=cq.Vector(*b)-u*220
  p.append(item(f'BED_GAS_BODY_{side}',line_cylinder(24,start.toTuple(),tuple(cq.Vector(*b)-u*15)),'steel',False,'Conservative24mm body envelope, not manufacturer-certified CAD. Cylinder toward moving bed; rod down.'))
  for tag,pt in(('LOWER',a),('UPPER',b)):
   p.append(item(f'BED_GAS_10MM_BALL_{side}_{tag}',cq.Solid.makeSphere(5,cq.Vector(*pt)),'steel',False,'10mm ball connection, stud axisX. Actual socket angular limits, brackets and rod/body envelopes require fit inspection.'))
  x=STAY_AXES[0 if side=='L'else 1]
  sm=yzpoint(STAY_MOVING,angle);a=(x,*STAY_ROOT);b=(x,*sm);v=cq.Vector(*b)-cq.Vector(*a);u=v.normalized();ln=v.Length
  outer_start=cq.Vector(*a)+u*12;outer_end=cq.Vector(*a)+u*402
  inner_end=cq.Vector(*b)-u*12;inner_start=inner_end-u*375
  outer=tube_between(20,2,outer_start.toTuple(),outer_end.toTuple());inner=tube_between(15,1.5,inner_start.toTuple(),inner_end.toTuple())
  # Nominal automatic index row in the inner tube; pin axes perpendicular
  # to tube within theYZplane. Final full-open hole accepts an independentM10pin.
  normal=cq.Vector(0,-u.z,u.y)
  q0=math.dist(STAY_ROOT,STAY_MOVING)-397.
  q90=math.dist(STAY_ROOT,yzpoint(STAY_MOVING,90.))-397.
  count=max(1,int((q90-q0-20)/15)+1)
  for q in([q0+15*k for k in range(count)]+[q90]):
   c=inner_end-u*q
   d=10.2 if abs(q-q90)<1e-5 else 8.5
   inner=inner.cut(cyl(d,26,tuple(c-normal*13),normal.toTuple()))
  station=cq.Vector(*a)+u*385
  outer=outer.cut(cyl(10.2,26,tuple(station-normal*13),normal.toTuple())).clean()
  p.append(item(f'BED_CAPTURE_OUTER_{side}',outer,'steel',False,'20x20x2tube390; joint centres and independent full-open10mm positive pin. Index catch is not assigned an impact rating.'))
  p.append(item(f'BED_CAPTURE_INNER_{side}',inner.clean(),'steel',False,'15x15x1.5tube375; drilled index row, min74mm nominal full-open overlap. Physical safe transition/catch validation remains mandatory.'))
  if angle==90.:
   pin=cyl(10,40,tuple(station-normal*20),normal.toTuple())
   p.append(item(f'BED_FULL_OPEN_POSITIVE_PIN_{side}',pin,'steel',False,'Independent10mm steel through-pin passes both walls of both tubes at90deg. Retained with positive head/clip; no gas-spring holding credit.'))
  for tag,pt in(('LOWER',a),('UPPER',b)):
   eye=ring(24,10.2,6.35,(x-3.175,pt[1],pt[2]),(1,0,0))
   p.append(item(f'BED_CAPTURE_EYE_{side}_{tag}',eye,'steel',False,'Welded eye to telescopic stay;10mm retained pivot in double-shear clevis required.'))
 return p

def bed_parts(angle=0.,include_assist=True):
 if not 0<=float(angle)<=90:raise ValueError('Angle0..90 required')
 moving=[dict(p,shape=rotate(p['shape'],angle))for p in(*deck_local_parts(),*deck_brackets())]
 parts=moving+fixed_receiver_parts()+(gas_and_stays(angle)if include_assist else[])+(closed_drawdowns()if angle==0. else[])
 return[dict(p,shape=p['shape'].translate((0,0,ASSEMBLY_Z_SHIFT)))for p in parts]

def metadata():
 return dict(bed_footprint_mm=[X0,Y0,W,L],workplane_Z_mm=WORK_TOP,layer_thicknesses_mm=[12.7,12.7],
  profile_quantity=10,uncut_profile_length_mm=1220,HDPE_operations='80 ordinary circular through holes per full1000x1219.2 sheet only; profile overhang0.4each end',
  support_crossmember_centres_Y_mm=list(CROSS_CENTRES),crossmember_quantity=4,crossmember_4080_cut_mm=CROSS_LENGTH,
  sleeve_quantity=80,sleeve_dimensions_mm=dict(OD=12.7,ID=6.35,length=65.4),profile_fasteners='80M5x70 direct sleeve seats with compatible bottom-slot nuts',
  hinge_axis_Y_Z_mm=[PIVOT[0],PIVOT[1]+ASSEMBLY_Z_SHIFT],assembly_Z_shift_mm=ASSEMBLY_Z_SHIFT,operating_angle_deg=[0,90],gas_force_nominal_N_each=GAS_FORCE,
  gas_required_eye_acceptance_mm=dict(maximum_compressed=GAS_MIN,minimum_expanded=GAS_MAX),gas_product_ASIN='B08CNGT5Z7',
  gas_selected_listing='ARANA ST280M20028in200lb,4x10mmballstuds; exactcompressed length unconfirmed and force bullet contradictory. Verify200lb889Neach label and dimensions before installation.',
  receiver_material='formed/trimmedsteel angle54x31.75x3.175,L1050x2,Y170..1220,localassistwindow/reinforcement;16flushM5CSmountsets atmid/reararms. Frontsupport is thehinge.',
  closed_retention='4M8x35 side drawdowns,4washers,4spacers,2rearendcaps; front12mmhinges provide repeatable geometry, left axial datum/right thermal float must be fitted.',
  frame_change_required='Frame/Y assemblies±25outboard;1760headers Y−160..1600/frontposts Y−100. Omit oldfirstpanXbearer/frontdryarms andangles; lowerfourremainingdryarms/seats2.425mm. Reararms D12.5headaccess X105/1045,Y1140. Hinge fronts carrywoodbed; pan supports300/630/1180 separatelyscreened. Repack complete frontstop assemblies clear of hinge/assist paths.',
  permanent_machine_plan_bounds_mm=[-50.,-160.,1200.,1600.],
  head_prerequisite='Remove entire installed removable head/tool assembly, retain commonZ, park gantryY1275/Zmax; ATC fullyparked.',
  gas_is_anti_drop_device=False,transition_fall_control_qualified=False,full_open_uses_independent_positive_pins=True,
  fabrication_release=False)
