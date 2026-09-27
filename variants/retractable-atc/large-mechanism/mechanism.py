"""Fabricated large-machine ATC mechanism; supplied magazine interface is gated.

All dimensions mm. CAD mounting interfaces are separate from unselected loaded
magazine allowances. No frozen design is modified by this builder.
"""
from pathlib import Path
import sys,importlib.util,math
from dataclasses import dataclass
import cadquery as cq
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(OUT))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
hw=module('retractable_hardware',OUT.parent/'hardware/hardware.py')
base=module('large_baseline',ROOT/'variants/48x96/layout.py')

STEEL=(.25,.32,.35);ALU=(.68,.72,.75);BLUE=(.23,.45,.57);YELLOW=(.87,.58,.20);BLACK=(.15,.16,.18);POLY=(.83,.84,.78)
def box(x,y,z):return hw.box(x,y,z)
def cyl(r,h,x=0,y=0,z=0):return hw.cyl(r,h,x,y,z)
def pose(s,origin,normal=(0,0,1),xdir=(1,0,0)):return hw.pose(s,origin,normal,xdir)
def bbox(s):return base.bounds(s)

@dataclass
class Part:
    id:str;shape:object;group:str;material:str;color:tuple;note:str='';local:object=None;thickness:float=None

def build(slide=0.,shutter=0.,dock_release=False,catch_release=False):
    """slide0=change,200=park; shutter0=closed,164=open."""
    parts=[]
    def add(id,shape,group,material='6061-T6',color=ALU,note='',local=None,thickness=None):
        parts.append(Part(id,shape.clean(),group,material,color,note,local,thickness));return shape
    def plate(id,w,h,t,origin,holes=(),normal=(0,0,1),xdir=(1,0,0),group='fixed',material='6061-T6',color=ALU,cb=(),outline=None,note=''):
        local=box(w,h,t) if outline is None else cq.Workplane('XY').polyline(outline).close().extrude(t).val()
        for hole in holes:
            x,y,d=hole[:3]
            if len(hole)==3:local=local.cut(cyl(d/2,t+2,x,y,-1))
            else:
                depth,side=hole[3:]
                local=local.cut(cyl(d/2,depth+1,x,y,t-depth if side=='top' else -1))
        for x,y,d,depth in cb:local=local.cut(cyl(d/2,depth+1,x,y,t-depth))
        shape=add(id,pose(local,origin,normal,xdir),group,material,color,note,local,t)
        parts[-1].frame=cq.Plane(origin=origin,xDir=xdir,normal=normal).location
        return shape
    def bolt(id,d,length,origin,normal=(0,0,1),xdir=(1,0,0),group='fixed_fasteners'):
        # Origin is bearing plane; thread extends +normal, head goes -normal.
        head={3:(5.5,3),4:(7,4),5:(8.5,5),6:(10,6),8:(13,8)}[d]
        s=cyl(d/2,length).fuse(cyl(head[0]/2,head[1],z=-head[1]))
        return add(id,pose(s,origin,normal,xdir),group,'steel 8.8',BLACK,f'ISO4762 M{d}x{length}; unthreaded major-diameter representation')
    def washer(id,d,od,t,origin,normal=(0,0,1),xdir=(1,0,0),group='fixed_fasteners'):
        return add(id,pose(cyl(od/2,t).cut(cyl((d+.4)/2,t+2,z=-1)),origin,normal,xdir),group,'steel',STEEL)
    def nut(id,d,af,t,origin,normal=(0,0,1),xdir=(1,0,0),group='fixed_fasteners'):
        r=af/math.sqrt(3);points=[(r*math.cos(math.pi/6+i*math.pi/3),r*math.sin(math.pi/6+i*math.pi/3)) for i in range(6)]
        s=cq.Workplane('XY').polyline(points).close().extrude(t).val().cut(cyl(d/2,t+2,z=-1))
        return add(id,pose(s,origin,normal,xdir),group,'steel 8',STEEL)
    def rhs(id,length,w,h,wall,origin,normal=(0,0,1),xdir=(1,0,0),group='fixed',material='6061-T6'):
        s=box(length,w,h).cut(box(length+2,w-2*wall,h-2*wall).translate((-1,wall,wall)))
        return add(id,pose(s,origin,normal,xdir),group,material,ALU,'Square-cut tube; deburr and match frame jig before drilling.')

    # Bolted side saddles with compression sleeves through the lower chord.
    # Context builder drills these holes in its copy of the baseline, never source.
    for i,y in enumerate((270.,760.),1):
        holes=[(yy,zz,9.) for yy in (15.,55.) for zz in (35.,60.)]
        plate(f'FRAME_INNER_{i}',70,70,12.7,(1836.9,y-35,525),holes,(1,0,0),(0,1,0),material='S235 steel',color=STEEL)
        plate(f'FRAME_OUTER_{i}',70,70,12.7,(1900.4,y-35,525),holes,(1,0,0),(0,1,0),material='S235 steel',color=STEEL)
        for j,(yy,zz,_) in enumerate(holes):
            bolt(f'FRAME_BOLT_{i}_{j}',8,90,(1836.9,y-35+yy,525+zz),(1,0,0),(0,1,0))
            sleeve=cyl(6,44.704).cut(cyl(4.5,46,z=-.5))
            add(f'FRAME_COMPRESSION_SLEEVE_{i}_{j}',pose(sleeve,(1852.648,y-35+yy,525+zz),(1,0,0),(0,1,0)),'fixed','steel',STEEL,'Fit internal sleeve before closing chassis tube; sleeve ends bear inside faces. Access and assembly order must be planned before welding the chord.')
            washer(f'FRAME_WASHER_{i}_{j}',8,16,1.6,(1913.1,y-35+yy,525+zz),(1,0,0),(0,1,0))
            nut(f'FRAME_NUT_{i}_{j}',8,13,6.5,(1914.7,y-35+yy,525+zz),(1,0,0),(0,1,0))
        rhs(f'OUTER_RISER_{i}',76,50.8,25.4,3.175,(1900.4,y+25.4,595),normal=(1,0,0),xdir=(0,0,1),material='S235 steel')
        plate(f'OUTRIGGER_SEAT_{i}',136.6,70,12.7,(1789.2,y-35,671),[(15,20,6.6),(15,50,6.6)],material='S235 steel',color=STEEL,note='Weld to outer riser; dimensioned shim plane supports aluminum frame.')
        plate(f'OUTRIGGER_SHIM_{i}',40,60,.5,(1789.2,y-30,683.7),[(15,15,6.6),(15,45,6.6)],material='steel shim',color=STEEL)
    # Single-level welded aluminum H-frame; its inside edge clears steel diagonals.
    rhs('SUPPORT_LEDGER',810,50.8,50.8,3.175,(1830,235,684.2),xdir=(0,1,0))
    for i,y in enumerate((430.,970.),1):rhs(f'CANTILEVER_{i}',304.2,38.1,50.8,3.175,(1475,y-19.05,684.2))
    for i,y in enumerate((255.,285.,745.,775.)):
        x=1804.2
        for item in parts:
            if item.id=='SUPPORT_LEDGER':item.shape=item.shape.cut(cyl(3.3,53,x,y,683))
        add(f'OUTRIGGER_COMPRESSION_SLEEVE_{i}',cyl(6,44.45,x,y,687.375).cut(cyl(3.3,46,x,y,686.5)),'fixed','6061-T6',ALU)
        bolt(f'OUTRIGGER_BOLT_{i}',6,75,(x,y,735),(0,0,-1))
        washer(f'OUTRIGGER_WASHER_{i}',6,12,1.6,(x,y,669.4))
        nut(f'OUTRIGGER_NUT_{i}',6,10,5,(x,y,664.4))
    frame_mounts=[(x,y+dy) for x in (1490.,1795.) for y in (430.,970.) for dy in (-9.,9.)]
    for k,(x,y) in enumerate(frame_mounts):
        for item in parts:
            if item.id in ('SUPPORT_LEDGER','CANTILEVER_1','CANTILEVER_2'):item.shape=item.shape.cut(cyl(3.3,53,x,y,683))
        add(f'BASE_COMPRESSION_SLEEVE_{k}',cyl(6,44.45,x,y,687.375).cut(cyl(3.3,46,x,y,686.5)),'fixed','6061-T6',ALU)
        washer(f'BASE_WASHER_{k}',6,12,1.6,(x,y,682.6))
        nut(f'BASE_NUT_{k}',6,10,5,(x,y,677.6))
        bolt(f'BASE_BOLT_{k}',6,65,(x,y,741.2),(0,0,-1))
    # Two rail bars, a rear motor tab, and a short lock bridge replace a heavy sheet.
    motor_foot=[(1491.,1020.),(1521.,1020.),(1491.,1050.),(1521.,1050.)]
    for i,y in enumerate((430.,970.)):
        holes=[(15+25*j,25,3.,8,'top') for j in range(14)]
        holes += [(x-1465,yy-(y-25),6.6) for x,yy in frame_mounts if abs(yy-y)<10]
        counter=[(x-1465,yy-(y-25),11.,6.5) for x,yy in frame_mounts if abs(yy-y)<10]
        if i==1:
            holes += [(x-1465,yy-945,5.,9.,'top') for x,yy in motor_foot]
            outline=[(0,0),(365,0),(365,50),(80,50),(80,135),(0,135)]
        else:outline=None
        plate(f'RAIL_BAR_{i}',365,50,12.7,(1465,y-25,735),holes,cb=counter,outline=outline,note='M3 rail taps 8 mm; rear motor-foot M5 taps 9 mm; M6 counterbores 6.5 mm; rear tab welded/gusseted before final rail-plane machining if fabricated from separate stock.')
    lock_holes=[]
    for pinx,piny in ((1550.,470.),(1750.,530.)):
        lock_holes += [(pinx-1520,piny-455,12.),(pinx-1520-15,piny-455,4.,8,'top'),(pinx-1520+15,piny-455,4.,8,'top')]
    lock_holes += [(x-1520,y-455,5.5) for x,y in ((1530,500),(1630,500),(1730,500),(1770,545))]
    plate('LOCK_BRIDGE',260,95,12.7,(1520,455,735),lock_holes,note='6061 bracket welded to front rail bar; isolated bolted steel lock subplate underneath. Finish bores after welding.')
    # Rails and four blocks, with real mounting holes and real socket screw sizes.
    for i,y in enumerate((430.,970.)):
        add(f'MGNR12_{i}',hw.rail_350().translate((1470,y,747.7)),'fixed','purchased HIWIN reference',STEEL,'350mm cut:14holes,first10,last15; verify supplied rail end datum.')
        for j in range(14):bolt(f'RAIL_SCREW_{i}_{j}',3,10,(1480+25*j,y,751.2),(0,0,-1))
        for j,x in enumerate((1505.+slide,1585.+slide)):
            add(f'MGN12H_{i}_{j}',hw.mgn12h_block().translate((x,y,747.7)),'slide','purchased HIWIN reference',STEEL)
    # Carriage plate with narrow rear drive lug and actual bearing screw holes.
    moving_holes=[];counter=[]
    for x in (1505.,1585.):
        for y in (430.,970.):
            for dx in (-10,10):
                for dy in (-10,10):moving_holes.append((x+dx-1465,y+dy-400,3.4));counter.append((x+dx-1465,y+dy-400,6.,3.5))
    for x in (1495.,1515.,1575.,1595.):
        for y in (490.,700.,910.):moving_holes.append((x-1465,y-400,5.5))
    moving_holes += [(85.,70.,12.),(85.,130.,12.)]
    moving_holes += [(x-1465,y-400,5.,9.,'top') for x in (1530.,1560.) for y in (1010.,1052.)]
    outline=[(0,0),(160,0),(160,600),(100,600),(100,670),(60,670),(60,600),(0,600)]
    plate('CARRIAGE',160,670,12.7,(1465+slide,400,760.7),moving_holes,group='slide',cb=counter,outline=outline,note='M5 nut-foot taps 9 mm from top; nominal major-diameter cavities. M3 head counterbores 3.5 mm leave 0.7 mm nominal bolt-bottom clearance.')
    for i,(x,y,_) in enumerate(moving_holes[:16]):bolt(f'BLOCK_SCREW_{i}',3,12,(1465+slide+x,400+y,769.9),(0,0,-1),group='slide_fasteners')
    for piny in (470.,530.):add('CARRIAGE_LOCK_BUSH_'+str(piny),cyl(6,12.7,1550+slide,piny,760.7).cut(cyl(3.02,14,1550+slide,piny,760.1)),'slide','bearing bronze',YELLOW,'Press fit outer12; ream ID6.04; endpoint pin enters4mm from underside.')
    # Raised adapter strips preserve a central opening and24mm tool drop space.
    for side,x in (('L',1485.),('R',1565.)):
        for j,y in enumerate((490.,700.,910.)):
            plate(f'ADAPTER_STAND_{side}_{j}',40,30,40,(x+slide,y-15,773.4),[(10,15,5,15,'top'),(30,15,5,15,'top'),(10,15,5,15,'bottom'),(30,15,5,15,'bottom')],group='slide',note='M5 blind taps15mm at each end, separated by10mm solid web; nominal major-diameter thread cavities.')
            for k,xx in enumerate((x+10,x+30)):
                bolt(f'STAND_LOWER_{side}_{j}_{k}',5,25,(xx+slide,y,760.7),group='slide_fasteners')
                bolt(f'STAND_UPPER_{side}_{j}_{k}',5,12,(xx+slide,y,814.75),(0,0,-1),group='slide_fasteners')
        strip_holes=[(xx,y-400,5.5) for xx in (10,30) for y in (490.,700.,910.)]
        plate(f'MAGAZINE_ADAPTER_BLANK_{side}',40,600,6.35,(x+slide,400,813.4),strip_holes,group='slide',cb=[(xx,y-400,9.,5.) for xx in (10,30) for y in (490.,700.,910.)],note='M5x12 heads sit flush in9mm counterbores5mm deep; structural fastening modeled; manufacturer magazine mounting pattern intentionally undrilled. Central40mm gap preserves tool path.')
    # Main drive: current supplier alias supplies the verified motor/nut interfaces.
    motor_origin=(1500.,1045.,797.4)
    add('SLIDE_MOTOR',pose(hw.slide_motor(),motor_origin,(1,0,0),(0,1,0)),'fixed','purchased stepper',BLACK)
    plate('MOTOR_FOOT',44,64,8,(1484,1013,747.7),[(7,7,5.5),(37,7,5.5),(7,37,5.5),(37,37,5.5)])
    mh=[(32+dy,41.7+dz,3.4) for dy in (-15.5,15.5) for dz in (-15.5,15.5)]+[(32,41.7,22.2)]
    plate('MOTOR_UPRIGHT',64,75.7,8,(1500,1013,755.7),mh,(1,0,0),(0,1,0),note='Weld to motor foot after jigging31mm pattern; post-weld inspect pilot and screw axis.')
    for i,(x,y) in enumerate(motor_foot):bolt(f'MOTOR_FOOT_BOLT_{i}',5,16,(x,y,755.7),(0,0,-1))
    for i,(dy,dz) in enumerate(((-15.5,-15.5),(-15.5,15.5),(15.5,-15.5),(15.5,15.5))):
        bolt(f'MOTOR_FACE_BOLT_{i}',3,12,(1508,1045+dy,797.4+dz),(-1,0,0),(0,1,0))
    foot_holes=[(5,5,5.5),(35,5,5.5),(5,47,5.5),(35,47,5.5)]
    plate('NUT_CARRIER_FOOT',40,60,8,(1525+slide,1005,773.4),foot_holes,group='slide')
    nh=[(20,16,8.8)]
    for angle in (0,120,240):nh.append((20+9.525*math.cos(math.radians(angle)),16+9.525*math.sin(math.radians(angle)),3.4))
    plate('NUT_CARRIER_UPRIGHT',40,42,8,(1537+slide,1025,781.4),nh,(1,0,0),(0,1,0),group='slide',note='Weld to nut foot before final three-hole nut pattern inspection.')
    add('SLIDE_NUT',pose(hw.slide_nut(),(1545+slide,1045,797.4),(1,0,0),(0,1,0)),'slide','purchased POM nut',POLY)
    for i,(x,y) in enumerate([(1530,1010),(1560,1010),(1530,1052),(1560,1052)]):bolt(f'NUT_FOOT_BOLT_{i}',5,16,(x+slide,y,781.4),(0,0,-1),group='slide_fasteners')
    for i,angle in enumerate((0,120,240)):
        yy=1045+9.525*math.cos(math.radians(angle));zz=797.4+9.525*math.sin(math.radians(angle))
        bolt(f'NUT_FLANGE_BOLT_{i}',3,16,(1537+slide,yy,zz),(1,0,0),(0,1,0),'slide_fasteners')
        nut(f'NUT_FLANGE_NUT_{i}',3,5.5,2.4,(1548.81+slide,yy,zz),(1,0,0),(0,1,0),'slide_fasteners')
    locks=module('large_locks',OUT/'locks.py')
    locks.extend(dict(locals(),box=box,cyl=cyl,pose=pose,hw=hw,STEEL=STEEL,ALU=ALU,POLY=POLY,BLACK=BLACK))
    hood=module('large_hood',OUT/'hood.py')
    hood.extend(dict(locals(),box=box,cyl=cyl,pose=pose,hw=hw,STEEL=STEEL,ALU=ALU,POLY=POLY,BLACK=BLACK))
    catch=module('large_catch',OUT/'catch.py')
    catch.extend(dict(locals(),box=box,cyl=cyl,pose=pose,hw=hw,STEEL=STEEL,ALU=ALU,POLY=POLY,BLACK=BLACK))
    for p in parts:
        if p.id in ('HOOD_FRONT','HOOD_ROOF') and len(p.shape.Solids())>1:
            p.shape=max(p.shape.Solids(),key=lambda x:x.Volume());p.note+=' Drive/service cutouts intentionally remove unsupported isolated sheet islands; openings are not sealed.'
    return parts

def context():
    """Current large-machine bodies with explicit new sleeve holes in the copy."""
    parts,_=base.build(base.Parameters(),'router')
    parts=[p for p in parts if p.name!='ATC_MAGAZINE']
    for p in parts:
        if p.name=='SIDE_R_LOWER_1':
            for y in (250.,290.,740.,780.):
                for z in (560.,585.):p.shape=p.shape.cut(pose(cyl(4.5,54),(1848,y,z),(1,0,0),(0,1,0)))
    return parts
