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
TOP=960.8;PROFILE_BOTTOM=TOP-20.;HDPE_LAYER_COUNT=1;HDPE_THICKNESS=12.7
HDPE_BOTTOM=PROFILE_BOTTOM-HDPE_LAYER_COUNT*HDPE_THICKNESS
HDPE_LENGTH=1200.
ASSEMBLY_Z_SHIFT=7.;WORK_TOP=TOP+ASSEMBLY_Z_SHIFT
CROSS_HEIGHT=80.;CROSS_WIDTH=40.;CROSS_BOTTOM=HDPE_BOTTOM-CROSS_HEIGHT;CROSS_CENTRES=(110.,395.,780.,1140.)
CROSS_X0,CROSS_LENGTH=85.,980.
PAN_LOWERING_MM=26.
COLUMN_LENGTH=CROSS_HEIGHT+HDPE_LAYER_COUNT*HDPE_THICKNESS
PROFILE_BRIDGE_WASHER_OD=18.;PROFILE_BRIDGE_WASHER_ID=6.4;PROFILE_BRIDGE_WASHER_T=1.6
PROFILE_SCREW_STOCK_LENGTH=100.;PROFILE_SCREW_FINISHED_LENGTH=99.3
PIVOT=(-100.,TOP)
GAS_ROOT=(-70.,768.);GAS_MOVING=(365.,905.4)
STAY_ROOT=(-40.,743.);STAY_MOVING=(395.,852.4)
GAS_FORCE=667.;GAS_MIN,GAS_MAX=445.,700.
GAS_AXES=(59.15,1090.85)
STAY_AXES=(54.,1096.)
STAY_PIN_HEAD_X=44.55;STAY_PIN_HEAD_LENGTH=2.5
STAY_PIN_SHOULDER_X=66.2;STAY_PIN_END_X=75.4
STAY_PIN_COTTER_X=72.4
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
 # First/last anchors move inward so the vertical sleeve bores do not
 # intersect either upright4080end-core fixing/tap. All remain real slots.
 return[(cy,X0+100*i+dx)for cy in CROSS_CENTRES for i in range(10)for dx in((50,90)if i==0 else(10,50)if i==9 else(30,70))]

@lru_cache(None)
def deck_local_parts():
 p=[];anchors=anchor_rows();ref=(395.,545.)
 for i,zz in enumerate([HDPE_BOTTOM+k*HDPE_THICKNESS for k in range(HDPE_LAYER_COUNT)],1):
  s=box(X0,Y0+.4,zz,W,HDPE_LENGTH,HDPE_THICKNESS)
  cuts=[cyl(13.2 if(cy,x)==ref else 22.,14.7,(x,cy,zz-1))for cy,x in anchors]
  s=s.cut(cq.Compound.makeCompound(cuts)).clean()
  p.append(item(f'FULL_HDPE_{i}',s,'HDPE',True,'One1000x1200x12.7fullcut-area-coveringrectanglefrom48x48insheet;80roundthroughholesonly.19.6rearprofileoverhang,metalcolumnpreloadbypassesplastic.'))
 prof=profile_section(L).rotate((0,0,0),(1,0,0),90).translate((0,L,0))
 for i in range(10):p.append(item(f'UNCUT_20100_{i+1:02}',prof.translate((X0+100*i,Y0,PROFILE_BOTTOM)),'aluminum',True,'Uncut1220 length, profile axis Y. End-load compatible M5 nuts before assembly.'))
 for j,cy in enumerate(CROSS_CENTRES,1):
  s=F.bar(CROSS_X0,cy-CROSS_WIDTH/2,CROSS_BOTTOM,'X',CROSS_LENGTH,flat=False)
  s=s.cut(cq.Compound.makeCompound([cyl(13.1,CROSS_HEIGHT+2,(x,cy,CROSS_BOTTOM-1))for c,x in anchors if c==cy])).clean()
  if j in(1,2,4):
   for xx,d in((85.,(1,0,0)),(1065.,(-1,0,0))):
    for zz in(CROSS_BOTTOM+20,CROSS_BOTTOM+60):s=s.cut(cyl(8.,22,(xx,cy,zz),d))
  p.append(item(f'BED_4080_CROSS_{j}',s,'aluminum',True,'980mm4080upright40Yx80Z;20D13.1verticalsleevebores. First/lastanchorsshifted40mmfromends;actualsupplierstrong-axis/modifiedligamentpropertiesrequirequalification.'))
 for side in('L','R'):
  cap=box(78.65,1120,CROSS_BOTTOM,6.35,40,80.)
  for zz in(CROSS_BOTTOM+20,CROSS_BOTTOM+60):cap=cap.cut(cyl(8.5,8.35,(77.65,1140,zz),(1,0,0)))
  p.append(item('BED_REAR_END_CAP_'+side,_mirror(cap.clean(),side),'steel',True,'6.35endplate, two8.5through fixingholes into rear4080end cores. Carries closed-mode side drawdowns through metal only.'))
  zz=CROSS_BOTTOM+60
  washer=ring(16,8.5,1.6,(77.05,1140,zz),(1,0,0))
  bolt=cyl(8,20,(77.05,1140,zz),(1,0,0)).fuse(cyl(13,8,(69.05,1140,zz),(1,0,0))).clean()
  p.extend([item('BED_REAR_UPPER_WASHER_'+side,_mirror(washer,side),'steel',True,'PermanentupperendcapM8washer;12.05nominalcoreengagementwithM8x20.'),item('BED_REAR_UPPER_M8x20_'+side,_mirror(bolt,side),'steel',True,'Permanentupperendcapbolt;lowersidedrawdownremovedfortilt,butthisboltremainswithbed.')])
 for k,(cy,x)in enumerate(anchors,1):
  p.append(item(f'BED_COLUMN_{k:02}',ring(12.7,6.35,COLUMN_LENGTH,(x,cy,CROSS_BOTTOM)),'aluminum',True,'Straightcompressiontube12.7OD6.35IDx92.7nominal;fitactualsingleHDPEstack. Metalcolumnbypassesplasticpreload.'))
  washer_bottom=CROSS_BOTTOM-PROFILE_BRIDGE_WASHER_T
  washer=ring(PROFILE_BRIDGE_WASHER_OD,PROFILE_BRIDGE_WASHER_ID,PROFILE_BRIDGE_WASHER_T,(x,cy,washer_bottom))
  p.append(item(f'BED_CROSS_BRIDGE_WASHER_{k:02}',washer,'steel',True,'SteelM6DIN9021/ISO7093largewasher18OD6.4IDx1.6bridges13.1crossbarbore. Seatsbothsquarecolumnendandcrossbarunderside;positivelycapturesthecrossbar. Keepwashercentredandverifybothseats.'))
  screw=cyl(5,PROFILE_SCREW_FINISHED_LENGTH,(x,cy,washer_bottom)).fuse(cyl(8.5,5,(x,cy,washer_bottom-5))).clean()
  p.append(item(f'BED_M5_FINISHED_{k:02}',screw,'steel',True,'M5x100stockfinished99.3+/-0.1underhead,endchamfer<=0.4. Underheadon18ODbridgewasher;full2.7nominalnutengagement,1.0tip/1.1cavityreserve. Fitactualdie/nut/preload.'))
  nut=box(x-4,cy-4,PROFILE_BOTTOM+1.3,8,8,2.7).cut(cyl(5,4.7,(x,cy,PROFILE_BOTTOM+.3))).clean()
  p.append(item(f'BED_M5_BOTTOM_NUT_{k:02}',nut,'steel',True,'Recovered8x8x2.7 nominal slot-nut envelope, end-loaded. Actual selected nut and lip capacity remain a supplier fit acceptance item.'))
 return tuple(p)

def _mirror(s,side):return s if side=='L'else s.mirror('YZ',(575,0,0))

def slotted_nut(thread,af,height,body,slot_width,point):
 nx,cy,zz=point
 pts=[(af/math.sqrt(3)*math.cos(math.radians(30+60*k)),af/math.sqrt(3)*math.sin(math.radians(30+60*k)))for k in range(6)]
 nut=plane_plate(pts,height,origin=point,normal=(1,0,0),xdir=(0,1,0))
 nut=nut.cut(cyl(thread,height+2,(nx-1,cy,zz),(1,0,0)))
 for aa in(0,60,120):
  gap=box(nx+body,cy-af,zz-slot_width/2,height-body+1,2*af,slot_width)
  nut=nut.cut(gap.rotate((0,cy,zz),(1,cy,zz),aa))
 return nut.clean()

def installed_cotter(diameter,point,loop_plane='XY'):
 """Conservative formed split-pin material envelope, cross-hole axis Y."""
 x,cy,zz=point;s=diameter/1.6
 start=-7*s
 # Bent-tail centreline lengths from the under-loop tangent are <=14/16mm.
 # The old scalable tail shape exceeded the stated stock length for M8.
 branch,tail_y,tail_z=(5.4,6.6,1.7)if diameter==1.6 else(6.,7.5,1.)
 shank=cyl(diameter,branch-start,(x,cy+start,zz),(0,1,0))
 loop=ring(4*s,2*s,.8*s,(x,cy-8.5*s,zz-.4*s))
 if loop_plane=='YZ':loop=loop.rotate((x,cy,zz),(x,cy+1,zz),90)
 tails=[line_cylinder(.8*s,(x,cy+branch-.1,zz),(x,cy+tail_y,zz+dz))for dz in(-tail_z,tail_z)]
 return shank.fuse(loop,*tails).clean()

def hinge_pin_parts(side):
 """Inboard headed12mm hinges withdraw toward the clear front-bed centre.

 The front post/base blocks an outboard-fed headed pin. Reverse the head and
 retain outside with a plain washer/cotter; no inaccessible wrench is needed.
 """
 cy,zz=PIVOT;tip=51.15;shoulder=75.2;cross=54.35
 pin=cyl(18,3,(shoulder,cy,zz),(1,0,0)).fuse(cyl(12,shoulder-tip,(tip,cy,zz),(1,0,0)))
 pin=pin.cut(cyl(2.2,16,(cross,cy-8,zz),(0,1,0))).clean()
 washer=ring(18,12.2,1.6,(55.45,cy,zz),(1,0,0))
 cotter=installed_cotter(2,(cross,cy,zz),loop_plane='YZ')
 thickness=1.85 if side=='L'else 1.35
 shim=ring(18,12.2,thickness,(63.5,cy,zz),(1,0,0))
 specs=(('PIN',pin,'Turned12mmplainhingepin:18headx3facinginboard,12smoothshaft24.05;27.05overall,D2.2throughcrosshole23.85fromouterheadface. Pull26mminboardintosupportedfrontbedbayforremoval;nooutboard-fedpinorwrenchrequired.'),
  ('RETAINER_WASHER',washer,'Customsteel18OD12.2IDx1.6retainingwasheroutsidefixedcheek. Retainedby2x16cotter;madefromsamepinbar,notM8purchasedhardware.'),
  ('RETAINER_COTTER',cotter,'DIN94/ISO1234splitpin2x16,headloopandtailsformedinYZplanetoclearwasher;replaceafterremoval. RemovefromfrontYdirectionbeforewithdrawingpin.'),
  ('AXIAL_SHIM',shim,f'Steel18OD12.2IDx{thickness}axialspacer. Leftnominalclearance0.125,right0.625betweenfixedcheekandmovingarm. Fitmetalshimstomeasuredassemblyandthermalfloat.'))
 return[item(f'BED_HINGE_{tag}_{side}',_mirror(s,side),'steel',False,note)for tag,s,note in specs]

def full_open_pin_parts(side,station,normal):
 """A removable headed10mm pin, independent of gas force, fully retained."""
 # Local X is the through-pin axis; local Y maps to global X for accessible
 # inboard/outboard cotter access. The outer tube occupies localX-10..10.
 head=-13.1;land=-10.1;shoulder=10.2;end=19.4;cross=16.4
 pin=cyl(16,3,(head,0,0),(1,0,0)).fuse(cyl(10,shoulder-land,(land,0,0),(1,0,0)),cyl(6,end-shoulder,(shoulder,0,0),(1,0,0)))
 pin=pin.cut(cyl(1.8,8,(cross,-4,0),(0,1,0))).clean()
 washer=ring(12,6.4,1.6,(shoulder,0,0),(1,0,0))
 nut=slotted_nut(6,10,6,3.5,2,(shoulder+1.6,0,0))
 cotter=installed_cotter(1.6,(cross,0,0))
 n=cq.Vector(*normal).normalized();o=cq.Vector(*station)
 # Cotter heads face the accessible outside of each side, above the Y rails;
 # mirroring the right transverse axis avoids trapping its loop by the arm.
 z=n.cross(cq.Vector(1 if side=='L'else-1,0,0))
 tf=cq.Location(cq.Plane(origin=o,xDir=n,normal=z))
 specs=(('POSITIVE_PIN',pin,'Turned10mmsmoothfull-openpin,16headx3,20.3bearingland,M6x1x9.2end;32.5overall. Passesbothwallsofbothstaytubes. Noimpactratinginferred.'),
  ('RETAINER_WASHER',washer,'M6DIN125washer12OD6.4IDx1.6;seats on lock-pin shoulder.'),
  ('RETAINER_CASTLE_NUT',nut,'M6x1DIN937AF10/h6/body3.5/slots2min;nutandcotter positivelycapturefull-openpin.'),
  ('RETAINER_COTTER',cotter,'NewDIN94/ISO1234splitpin1.6x14,installedformedtailenvelope;replaceeachremoval.'))
 return[item(f'BED_FULL_OPEN_{tag}_{side}',s.moved(tf),'steel',False,note)for tag,s,note in specs]

def stay_pivot_parts(tag,point,side,move=False):
 """Captured pivots; the outboard head is recessed, never an external clip.

 The reduced M6 thread, nut and split pin only retain the joint axially.
 The unthreaded 10 mm land carries both clevis/eye bearing interfaces.
 The washer bottoms on the pin shoulder, retaining 0.2 mm nominal axial float.
 """
 cy,zz=point;p=[]
 pin=cyl(14,STAY_PIN_HEAD_LENGTH,(STAY_PIN_HEAD_X,cy,zz),(1,0,0))
 pin=pin.fuse(cyl(10,STAY_PIN_SHOULDER_X-(STAY_PIN_HEAD_X+STAY_PIN_HEAD_LENGTH),(STAY_PIN_HEAD_X+STAY_PIN_HEAD_LENGTH,cy,zz),(1,0,0)),
              cyl(6,STAY_PIN_END_X-STAY_PIN_SHOULDER_X,(STAY_PIN_SHOULDER_X,cy,zz),(1,0,0)))
 pin=pin.cut(cyl(1.8,8,(STAY_PIN_COTTER_X,cy-4,zz),(0,1,0))).clean()
 washer=ring(12,6.4,1.6,(STAY_PIN_SHOULDER_X,cy,zz),(1,0,0))
 # DIN937 M6: AF10, height6, full body3.5, slots >=2 wide.
 # Sharp hex corners conservatively enclose the published minimum E11.05.
 nx=STAY_PIN_SHOULDER_X+1.6
 nut=slotted_nut(6,10,6,3.5,2,(nx,cy,zz))
 # Installed split-pin material envelope. The D1.6 central section fits the
 # D1.8 drilling. Use a new DIN94 1.6x14 split pin after every disassembly.
 cotter=installed_cotter(1.6,(STAY_PIN_COTTER_X,cy,zz))
 specs=(('PIN',pin,'Turned C45/4140 steel pivot:14headx2.5,10smoothbearingland19.15,M6x1retentionthread9.2;overall30.85. Outerhead recessed0.1;D1.8crosshole at27.85fromouterface. See dedicated pivot drawing for fits. Material/load rating needs qualification.'),
        ('WASHER',washer,'M6DIN125washer12OD6.4IDx1.6;seats on pin shoulder and leaves0.2nominal clevis axial float.'),
        ('CASTLE_NUT',nut.clean(),'M6x1DIN937slottednut:AF10,h6,3.5body,slots2minimum. Positive retention by installed split pin, never torque against moving clevis.'),
        ('COTTER',cotter,'DIN94 1.6x14 split pin, installed/bent-tail material envelope;replace after removal. Both tails retained within inboard gap.'))
 for part,shape,note in specs:p.append(item(f'BED_STAY_PIVOT_{part}_{tag}_{side}',_mirror(shape,side),'steel',move,note))
 return p

def fixed_receiver_parts():
 p=[];t=3.175
 for side in('L','R'):
  # Use ordinary angle stock, trimming the vertical leg to31.75mm.
  flange=box(72.,170,CROSS_BOTTOM-t,54.,1050,t)
  web=box(72.,170,CROSS_BOTTOM,t,1050,31.75)
  # Local clearance for the moving assist clevis, replaced by an integral
  # lower reinforcement web. No unsupported slit through the bearing flange.
  web=web.cut(box(71.,355,CROSS_BOTTOM-1,t+2,100,34.))
  # The inboard retained-pin thread crosses the flange height during lift.
  # Widen the existing assist notch to X76.0, leaving0.6mm to its X75.4 tip;
  # the reinforced lower web starts at76.2 and the crossbar bearing atX85.
  flange=flange.cut(box(71.,355,CROSS_BOTTOM-t-1,5.,100,t+2))
  reinforcement=box(76.2,345,CROSS_BOTTOM-35,t,120,35.)
  s=flange.fuse(web,reinforcement).clean()
  # Closed-mode bridge washers project below the crossbar. These22mm holes
  # clear their18mmOD, including reasonable lateral assembly float; the
  # receiver bearing remains around each local access hole.
  for cy in CROSS_CENTRES:s=s.cut(cyl(22.,t+2,(125.,cy,CROSS_BOTTOM-t-1)))
  for cy in(100.,630.,1180.):
   for xx in(96.,116.):
     for yy in(cy-20,cy+20):
      s=s.cut(cyl(5.5,t+2,(xx,yy,CROSS_BOTTOM-t-1)))
      s=s.cut(cq.Solid.makeCone(2.75,5.,2.75,cq.Vector(xx,yy,CROSS_BOTTOM-2.75)))
  s=s.cut(cyl(8.5,5.175,(71.,1140,CROSS_BOTTOM+20),(1,0,0)))
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
  p.extend(hinge_pin_parts(side))
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
    ears=ring(24,10.2,5.,(44.45,cy,zz),(1,0,0)).fuse(ring(24,10.2,3.175,(62.825,cy,zz),(1,0,0)))
    stems=box(44.45,cy-6,zz-20,5.,12,18.2).fuse(box(62.825,cy-6,zz-20,3.175,12,18.2))
    plate=plate.fuse(floor,ears,stems).cut(cyl(10.2,42.2,(24.8,cy,zz),(1,0,0))).clean()
    plate=plate.cut(cyl(14.2,2.6,(44.45,cy,zz),(1,0,0))).clean()
    # Independent gas-column/stud clearance through the rear capture bracket;
    # the two stationary anchor sets are not overlapping fictitious solids.
    for yy in(-120.,-80.):
     for z in(GAS_ROOT[1]-20,GAS_ROOT[1]+20):plate=plate.cut(cyl(13.1,9.,(24.8,yy,z),(1,0,0)))
    plate=plate.cut(cyl(8.5,9.,(24.8,GAS_ROOT[0],GAS_ROOT[1]),(1,0,0)))
   p.append(item(f'BED_{tag}_ROOT_MOUNT_{side}',_mirror(plate.clean(),side),'steel',False,'6.35mm anchorplate;4M6post mounts atY−120/−80,Zanchor±20. Gas uses14.9standoffs; capture directpost. Cantilever web transfers anchor load within its plane. Uppercontacthardware kept separate.'))
   if tag=='CAPTURE':p.extend(stay_pivot_parts('LOWER',STAY_ROOT,side))
   if tag=='GAS':
    stud=cyl(8,27.1,(27.05,cy,zz),(1,0,0))
    p.append(item(f'BED_GAS_ROOT_BALL_STUD_{side}',_mirror(stud,side),'steel',False,'10mmballstudM8x20thread plus7.1mmexposedneck; ballcentre12.1mmfromface. Actualballstudnecksetsfittedspacer, not a claimed supplied-kit bracket.'))
 return p

def closed_drawdowns():
 p=[]
 for side in('L','R'):
  for i,yy in enumerate((1140.,),1):
   zz=CROSS_BOTTOM+20
   washer=ring(16,8.5,1.6,(70.4,yy,zz),(1,0,0))
   spacer=ring(12.7,8.5,3.475,(75.175,yy,zz),(1,0,0))
   screw=cyl(8,35,(70.4,yy,zz),(1,0,0)).fuse(cyl(13,8,(62.4,yy,zz),(1,0,0)))
   for tag,shape in(('WASHER',washer),('SPACER',spacer),('M8x35',screw)):
    p.append(item(f'BED_CLOSED_{tag}_{side}_{i}',_mirror(shape.clean(),side),'steel',False,'Closed-modelowercorelock:oneM8drawdownpersideplusfronttwohinges. Removebothrearlocksetsfortilt. Upperendcapboltstayswithbed;20.4nominalcoreengagement,actualjointcapacityheld.'))
 return p

def deck_brackets():
 p=[]
 for side in('L','R'):
  # Hinge arm connects front crossbar to the top-plane pivot without HDPE cuts.
  plate=plane_plate([(0,0),(270,0),(270,128),(0,128)],9.525,
      origin=(65.475,-127,852.8),normal=(1,0,0),xdir=(0,1,0))
  plate=plate.cut(cyl(12.1,11.525,(64.475,-100,TOP),(1,0,0)))
  spacer=box(75.,90,CROSS_BOTTOM,10.,40,80.)
  for k,zz in enumerate((CROSS_BOTTOM+20,CROSS_BOTTOM+60),1):
   plate=plate.cut(cyl(8.5,11.525,(64.475,110,zz),(1,0,0))).cut(cyl(14.2,4.6,(65.475,110,zz),(1,0,0)))
   spacer=spacer.cut(cyl(8.5,12,(74.,110,zz),(1,0,0)))
   bolt=cyl(8,35,(70.075,110,zz),(1,0,0)).fuse(cyl(14,4.4,(65.675,110,zz),(1,0,0)))
   p.append(item(f'BED_HINGE_M8x35_BUTTON_{side}_{k}',_mirror(bolt.clean(),side),'steel',True,'Recessed14ODx4.4buttonhead;35underhead,20.075nominalend-coreengagement. Inwardshiftedcolumnborescleartheseaxes.'))
  p.append(item(f'BED_HINGE_MOVING_SIDEPLATE_{side}',_mirror(plate.clean(),side),'aluminum',True,'270x128x9.525sidearm;existinghingeaxisretained. EndboltsY110/Z868.1,908.1local. Owned3/8blankrequiresupdateduniqueglobalnest.'))
  p.append(item(f'BED_HINGE_SPACER_{side}',_mirror(spacer.clean(),side),'aluminum',True,'Existing80x40x10blankrotated40Yx80Z;2D8.5corebores.Noowned9.525stockcredit.'))
  # Shared gas/stay mounting bracket on the395mm crossbar end.
  web=box(78.65,380,CROSS_BOTTOM+10,6.35,50,60.)
  upper=box(44.45,355,909.05,34.2,75,6.35).cut(box(46.15,354,906.5,26,56,12))
  top_ear=box(72.3,355,895.4,6.35,20,20.)
  sz=STAY_MOVING[1]
  lower_ear=ring(24,10.2,3.175,(62.825,395,sz),(1,0,0)).fuse(box(62.825,405.4,sz,3.175,10,909.05-sz))
  far_ear=ring(24,10.2,5.,(44.45,395,sz),(1,0,0)).fuse(box(44.45,405.4,sz,5.,10,909.05-sz))
  s=web.fuse(upper,top_ear,lower_ear,far_ear).clean()
  for zz in(CROSS_BOTTOM+20,CROSS_BOTTOM+60):
   s=s.cut(cyl(8.5,8.35,(77.65,395,zz),(1,0,0)))
   s=s.cut(cyl(14.,9.,(69.65,395,zz),(1,0,0)))
   bolt=cyl(8,25,(78.65,395,zz),(1,0,0)).fuse(cyl(13,8,(70.65,395,zz),(1,0,0))).clean()
   p.append(item(f'BED_ASSIST_M8x25_{side}_{zz:g}',_mirror(bolt,side),'steel',True,'Actualendcoreboltgeometry;18.65nominalengagement. Gasandstayconnectionsmovedclearofsocketheads.'))
  s=s.cut(cyl(8.5,21.,(71.25,*GAS_MOVING),(1,0,0)))
  s=s.cut(cyl(13.2,1.15,(71.15,*GAS_MOVING),(1,0,0)))
  s=s.cut(cyl(10.2,24.,(43.45,395,sz),(1,0,0)))
  s=s.cut(cyl(14.2,2.6,(44.45,395,sz),(1,0,0))).clean()
  p.append(item(f'BED_ASSIST_C_BRACKET_{side}',_mirror(s,side),'steel',True,'Fabricated6.35steel bracket;2M8x25end-core bolts, top10mmgasballstud and lowerstayclevis. Ballstud axesX preserve spherical articulation inYZ. Ordinary welded stock; weld capacity acceptance required.'))
  p.extend(stay_pivot_parts('UPPER',STAY_MOVING,side,True))
  stud=cyl(8,27.1,(64.15,*GAS_MOVING),(1,0,0))
  spacer=ring(12.7,8.5,1.05,(71.25,*GAS_MOVING),(1,0,0))
  washer=ring(16,8.4,1.6,(78.65,*GAS_MOVING),(1,0,0))
  pts=[(13/math.sqrt(3)*math.cos(math.radians(30+60*k)),13/math.sqrt(3)*math.sin(math.radians(30+60*k)))for k in range(6)]
  nut=plane_plate(pts,8,origin=(80.25,*GAS_MOVING),normal=(1,0,0),xdir=(0,1,0)).cut(cyl(8,10,(79.25,*GAS_MOVING),(1,0,0))).clean()
  for tag,shape,note in(('UPPER_STUD',stud,'IncludedM8x20/7.1neck10mmballstudreference;actualsupplierfitheld.'),('UPPER_SPACER',spacer,'1.05metalspacerfits6.35gasearandnominal12.1face-to-ballstudgeometry.'),('UPPER_WASHER',washer,'M8flatwasher16OD8.4IDx1.6.'),('UPPER_NUT',nut,'M8DIN985nylocnutAF13/h8nominal;actualstudthread/lockengagementheld.')):
   p.append(item(f'BED_GAS_{tag}_{side}',_mirror(shape,side),'steel',True,note))
 return p

def gas_and_stays(angle=0.):
 p=[];t=math.radians(angle)
 for side,x in zip(('L','R'),GAS_AXES):
  gm=yzpoint(GAS_MOVING,angle);a=(x,*GAS_ROOT);b=(x,*gm);v=cq.Vector(*b)-cq.Vector(*a);u=v.normalized();ln=v.Length
  p.append(item(f'BED_GAS_ROD_{side}',line_cylinder(10,a,tuple(cq.Vector(*a)+u*(ln-220))),'steel',False,'28in150lb/667Ncandidatepair;compressed<=445/expanded>=700required.10rod/24bodyacceptanceenvelopes,notOEMCAD.'))
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
  if angle==90.:p.extend(full_open_pin_parts(side,station.toTuple(),normal.toTuple()))
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
 return dict(bed_footprint_mm=[X0,Y0,W,L],workplane_Z_mm=WORK_TOP,layer_thicknesses_mm=[HDPE_THICKNESS]*HDPE_LAYER_COUNT,
  profile_quantity=10,uncut_profile_length_mm=1220,HDPE_finished_size_mm=[1000,HDPE_LENGTH,HDPE_THICKNESS],
  HDPE_operations='One1000x1200x12.7layer,80roundthroughholesonly;front0.4/rear19.6profileoverhang.Coversfullcuttingarea,nocompositestiffnesscredit.',
  support_crossmember_centres_Y_mm=list(CROSS_CENTRES),crossmember_quantity=4,crossmember_4080_cut_mm=CROSS_LENGTH,
  crossmember_orientation='40Yx80Zstrong-axisupright;actualsupplieranddrilled-sectionpropertiesunqualified',
  sleeve_quantity=80,sleeve_dimensions_mm=dict(OD=12.7,ID=6.35,length=COLUMN_LENGTH),
  profile_fasteners='80M5x100stockfinished99.3underhead+80steelM6DIN9021bridgewashers18OD6.4IDx1.6+M5thinbottomslotnuts',
  profile_fastener_retention=dict(crossbar_bore_mm=13.1,bridge_washer_mm=[18,6.4,1.6],
   screw_stock_length_mm=PROFILE_SCREW_STOCK_LENGTH,screw_finished_underhead_length_mm=PROFILE_SCREW_FINISHED_LENGTH,screw_finish_tolerance_mm=.1,
   nominal_nut_thread_engagement_mm=2.7,nominal_tip_beyond_nut_mm=1.,nominal_tip_to_cavity_ceiling_mm=1.1,
   receiver_washer_access_hole_mm=22,nominal_washer_radial_bore_bridge_mm=2.45,
   lower_slot_ceiling_is_nominal_supplier_section=True,preload_or_slot_capacity_qualified=False),
  hinge_axis_Y_Z_mm=[PIVOT[0],PIVOT[1]+ASSEMBLY_Z_SHIFT],assembly_Z_shift_mm=ASSEMBLY_Z_SHIFT,operating_angle_deg=[0,90],gas_force_nominal_N_each=GAS_FORCE,
  gas_required_eye_acceptance_mm=dict(maximum_compressed=GAS_MIN,minimum_expanded=GAS_MAX),gas_product_ASIN=None,
  gas_selected_listing='28in150lb/667Neachnewpaircandidate;rootprocurementmustselectactualvariant/length/force. Do notsubstituteold200lbpair.',
  receiver_material='formed/trimmedsteel angle54x31.75x3.175,L1050x2,Y170..1220,localassistwindow/reinforcement;16flushM5CSmountsets atmid/reararms. Frontsupport is thehinge.',
  closed_retention='2M8x35lowercorelocks+2washers+2spacers;2permanentupperM8x20endcapbolts/washers. Front2hinges+rear2locksfourcornerrestraint;actualcapacityqualifiedseparately.',
  frame_change_required='Pan/slats/bearerslower26;dryreceiverseatsandarmslower27.3frompreviousflatstack. Workplane967.8unchanged. FrontbarY110;hingearms270x128requireupdatedowned3/8nest. GasupperY365/stayupperZ852.4local;actualgas/handlingqualificationrequired.',
  permanent_machine_plan_bounds_mm=[-50.,-160.,1200.,1600.],
  head_prerequisite='Remove entire installed removable head/tool assembly, retain commonZ, park gantryY1275/Zmax; ATC fullyparked.',
  gas_is_anti_drop_device=False,transition_fall_control_qualified=False,full_open_uses_independent_positive_pins=True,
  stay_pivot_retention=dict(quantity=4,outer_clevis_thickness_mm=5,outer_counterbore_mm=[14.2,2.6],
   pin=dict(head_mm=[14,2.5],bearing_mm=[10,19.15],thread='M6x1x9.2',overall_mm=30.85,cotter_crossdrill_mm=1.8),
   washer='M6DIN125,12OD6.4IDx1.6',nut='M6DIN937,AF10,height6',cotter='DIN94,1.6x14,replace after removal',
   outer_head_recess_mm=.1,nominal_axial_float_mm=.2,thread_end_to_receiver_reinforcement_nominal_mm=.8,
   shaft_surface='10.00/-0.02..-0.05 steel bearing land; all sharp edges deburred; threads excluded from shear planes',
   source='https://www.aspenfasteners.com/content/pdf/Metric_DIN_937_spec.pdf',load_capacity_qualified=False),
  hinge_pin_retention=dict(quantity=2,head_mm=[18,3],smooth_shaft_mm=[12,24.05],thread=None,overall_mm=27.05,
   crossdrill_mm=2.2,crossdrill_from_outer_head_face_mm=23.85,washer='Customsteel18OD12.2IDx1.6',nut=None,cotter='DIN94,2x16',
   head_faces='inboard',service_withdrawal_mm=26,service_side='inboardintoemptyfrontbedbay;cotterandwasherremovedfirst',
   axial_shims_mm=dict(left=1.85,right=1.35),nominal_cheek_gap_mm=dict(left=.125,right=.625),load_capacity_qualified=False),
  full_open_pin_retention=dict(quantity=2,head_mm=[16,3],bearing_mm=[10,20.3],thread='M6x1x9.2',overall_mm=32.5,
   crossdrill_mm=1.8,washer='M6DIN125,12OD6.4IDx1.6',nut='M6DIN937,AF10,height6',cotter='DIN94,1.6x14',
   installed_at_angle_deg=90,load_capacity_qualified=False),
  fabrication_release=False)
