"""XR2 removable, guarded200mm ATC carrier. The actual magazine is not invented.

atc_parts() returns physical mechanism solids only. acceptance_parts() contains
design-volume checks, not purchased RapidChange geometry or drilled templates.
No firmware, pneumatic valve or M6 operation is commissioned by this module.
"""
from functools import lru_cache
from pathlib import Path
import math
import sys

import cadquery as cq
import params as P
import motion
from cad_helpers import Model, bbox, plate, rect, place

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TRAVEL=200.
GATE_STROKE=161.
RAIL_START,RAIL_LENGTH=1065.,335.
BLOCK_CENTRES=(1100.,1165.)
RAIL_X,RAIL_Z=110.025,1050.
MAG_BASE=1030.15
LOWER_BASE=1003.8
STOCK_HEIGHT=40.
LOADED_TOOL_PROJECTION_P_MM=(15.,50.)
LOADED_TOOL_RADIUS_MM=7.5
SAFE_RUNNING_GAP_MM=5.
NOMINAL_SPINDLE_REFERENCE_ZERO=970.
PIN_STROKE=6.
KIT_MAX_LENGTH,KIT_WIDTH,KIT_MAX_HEIGHT=520.,60.,80.
KIT_BOUNDS=(315.,1082.,MAG_BASE,835.,1142.,MAG_BASE+KIT_MAX_HEIGHT)
POCKET_REGION=(345.,1092.,805.,1121.4)
PARK_GANTRY_Y=700.
STEEL=(.31,.38,.43);AL=(.55,.68,.73);BOUGHT=(.72,.56,.25)
HARD=(.38,.41,.44);SENSOR=(.08,.13,.16)
SOURCE_GUIDE=ROOT/'variants/retractable-atc/hardware'
if str(SOURCE_GUIDE) not in sys.path:sys.path.append(str(SOURCE_GUIDE))
import hardware as guide_source


def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cyl(d,l,p,n=(0,0,1)):return cq.Solid.makeCylinder(d/2,l,cq.Vector(*p),cq.Vector(*n))
def cut(s,tools):
    for t in tools:s=s.cut(t)
    return s.clean()
def reflect(s,left=True):return s if left else s.mirror('YZ',(575,0,0))
def pin_d6_sensor_body():
    # Panasonic PM-U25-P nominal13.4wide,6deep,16high,6wide open slot.
    s=box(0,0,0,13.4,6,16).cut(box(3.7,-1,10.5,6,8,5.6))
    return cut(s,[cyl(3.2,8,(x,-1,2.5),(0,1,0))for x in(2.7,10.7)])


def _build(travel=200.,gate_open=False,unlocked=False,gate_pin_withdrawn=False):
    assert 0<=travel<=TRAVEL
    m=Model();classes={}
    def add(n,s,kind='fixed',material='Low-carbon steel; actual grade/finish to verify',
            purchased=False,notes=(),flat=None,pn=None,color=None):
        if kind=='rack':s=s.translate((0,travel,0))
        elif kind=='gate':s=s.translate((0,0,-GATE_STROKE*float(gate_open)))
        hoodmoving=n.startswith(('ATC_HOOD_','ATC_GATE_','ATC_STEEL_GATE'))and not n.startswith(('ATC_HOOD_STAND_','ATC_HOOD_FRAME_','ATC_HOOD_SUPPORT_RHS'))
        if hoodmoving:s=s.translate((0,12.3,0))
        if n.startswith(('ATC_LOCK_','ATC_STOP_DEPLOY')):s=s.translate((0,0,20))
        p=m.add(n,s,pn=pn or n,group='ATC_'+kind,material=material,
                purchased=purchased,notes=notes,flat=flat,
                color=color or (BOUGHT if purchased else STEEL))
        # Locals are explicit fabrication coordinates, never a claim of vendor CAD.
        b=bbox(s);p.local=s.translate(tuple(-x for x in b[:3]));classes[n]=kind
        return p
    def screw(n,d,L,under,norm,kind='fixed',head=None):
        h=d;hd=head or{3:5.5,4:7,5:8.5,6:10}[d]
        a=tuple(under[i]-norm[i]*L for i in range(3))
        s=cyl(d,L,a,norm).fuse(cyl(hd,h,under,norm)).clean()
        return add(n,s,kind,'Steel socket screw, grade/coating to verify',True,pn=f'M{d}x{L}_SOCKET',color=HARD)
    def sheet(n,outline,t,origin,u=(1,0,0),v=(0,1,0),holes=(),kind='fixed',material='Steel plate',notes=()):
        flat=dict(outline=outline,thickness_mm=t,holes=list(holes),slots=[],internal=[])
        return add(n,place(plate(outline,t,holes),origin,u,v),kind,material,
                   notes=notes,flat=flat)

    # Two rigid rear supports per side. Floors pass below the moving Y blocks;
    # upright maxX99 stays2mm outboard of the guide-guard webX101.
    for side,left in(('L',True),('R',False)):
        bar=box(100.5,1060,1033.5,9.525,342,33)
        for y in [1085+25*i for i in range(13)]:
            bar=bar.cut(cyl(3,10,(101.525,y,1050),(1,0,0)))
        for y in(1094,1106,1294,1306):
            bar=bar.cut(cyl(4,14,(100,y,1052.5)))
        add(f'ATC_BACKBAR_{side}',reflect(bar.clean(),left),notes=[
            '342x33x9.525 steel backbar. Railseat is inner face; inspect straightness after support welding.',
            'Rear guide guard relief accepts this bar as the replacement steel spatter barrier.'])
        for i,y0 in enumerate((1225.,1325.),1):
            leg=cut(box(50.8,y0,983,6.35,40,26),
                    [cyl(6.6,9,(49.8,y0+q,993),(1,0,0))for q in(8,32)])
            floor=box(50.8,y0,1002.65,53.7,40,6.35)
            upright=box(100.5,y0,1009,4,40,24.5)
            cradle=leg.fuse(floor,upright).clean()
            add(f'ATC_REAR_CRADLE_{side}_{i}',reflect(cradle,left),notes=[
                'Fabricated steel:6.35leg/floor and4mm upright; weld to backbar, then inspect rail datum.',
                'Frame attachment2xM6 in lower inner slotZ993. Full actuator loads require a measured joint proof.'])
            for j,q in enumerate((8,32),1):
                grip=cyl(6,7.95,(50.8,y0+q,993),(1,0,0)).fuse(
                    cyl(10,6,(58.75,y0+q,993),(1,0,0)))
                add(f'ATC_FRAME_M6x16_EXTERNAL_{side}_{i}_{j}',reflect(grip.clean(),left),
                    purchased=True,material='Steel M6x16 candidate; in-slot tip/nut omitted',color=HARD,
                    notes=['External grip/head only. Actual slot nut depth and screw projection must be measured.'])
        #335mm cut of a sourced MGN12 rail, retaining E20/P25 and13holes.
        rail=guide_source.rail_350().translate((-15,0,0)).intersect(box(0,-7,-1,335,14,10))
        rail=place(rail,(RAIL_X,RAIL_START,RAIL_Z),u=(0,1,0),v=(0,0,1))
        add(f'ATC_MGNR12_{side}_335',reflect(rail,left),purchased=True,pn='MGNR12_335_E20_P25',
            notes=['Source HIWIN nominal interfaces;335cut,13retained holes, first20/far15. Verify delivered rail revision.'])
        for i,y in enumerate([1085+25*i for i in range(13)]):
            s=cyl(3,12,(101.525,y,1050),(1,0,0)).fuse(cyl(5.5,3,(113.525,y,1050),(1,0,0)))
            add(f'ATC_RAIL_M3x12_{side}_{i}',reflect(s.clean(),left),purchased=True,
                material='Steel M3x12 socket screw',color=HARD)
        wing=box(123.025,1067.1,1036.5,6.35,130.8,27)
        for yy in(1132.,1192.):
            for zz in(1042.,1058.):wing=wing.cut(cyl(4.4,8,(122.025,yy,zz),(1,0,0)))
        for i,cy in enumerate(BLOCK_CENTRES):
            block=place(guide_source.mgn12h_block(),(RAIL_X,cy,RAIL_Z),u=(0,1,0),v=(0,0,1))
            add(f'ATC_MGN12H_{side}_{i}',reflect(block,left),'rack',purchased=True,
                pn='MGN12H',notes=['45.8maximum length,27width,13assemblyheight;M3depth3.5.'])
            for j,(dy,dz) in enumerate(((-10,-10),(-10,10),(10,-10),(10,10))):
                yy,zz=cy+dy,1050+dz
                wing=wing.cut(cyl(3.3,9,(122.025,yy,zz),(1,0,0)))
                wing=wing.cut(cyl(6,1.35,(128.025,yy,zz),(1,0,0)))
                bolt=cyl(3,8,(120.025,yy,zz),(1,0,0)).fuse(cyl(5.5,3,(128.025,yy,zz),(1,0,0)))
                add(f'ATC_BLOCK_M3x8_{side}_{i}_{j}',reflect(bolt.clean(),left),'rack',purchased=True,
                    material='Steel M3x8 socket screw',color=HARD,
                    notes=['5mmgrip at1.35counterbore;3mm nominal block engagement,0.5mm depth reserve.'])
        add(f'ATC_MOVING_WING_{side}',reflect(wing.clean(),left),'rack',material='6.35mm aluminum plate',
            notes=['130.8x27x6.35; eightM3clearance/counterbore holes.'])
        # Steel drop arm stays inside the Y corner but outside the Z-base envelope.
        arm=box(129.375,1128.5,1036.5,7.95,80.5,27).fuse(box(129.375,1172,980.15,7.95,25.4,56.35))
        for yy in(1155.,1175.):
            for zz in(1040.,1060.):arm=arm.cut(cyl(6,2.1,(129.325,yy,zz),(1,0,0)))
        for yy in(1132.,1192.):
            for zz in(1042.,1058.):
                arm=arm.cut(cyl(4,9,(128.825,yy,zz),(1,0,0)))
                bolt=cyl(4,14,(123.025,yy,zz),(1,0,0)).fuse(cyl(7,4,(119.025,yy,zz),(1,0,0)))
                add(f'ATC_ARM_M4x14_{side}_{int(yy)}_{int(zz)}',reflect(bolt.clean(),left),'rack',purchased=True,material='M4x14 socket screw;7.65mm nominal steel engagement')
        add(f'ATC_CARRIER_END_{side}',reflect(arm,left),'rack',notes=[
            'Steel carrier end: four M4x14 through aluminum wing into7.65mm tapped steel; weld to RHS. Stage transport restricted to gantry-front safe pose; actual supplier profiles held.'])
    tube=box(137.325,1172,980.15,875.35,25.4,50.8).cut(
        box(136.325,1175.175,983.325,877.35,19.05,44.45))
    add('ATC_MOVING_RHS_875p35x50p8x25p4',tube.clean(),'rack',notes=['3.175wall steel RHS; rear of full stock at every stroke coordinate.'])
    # Open carrier and removable top bridge. End lands are outside the accepted
    # cutter-centre interval; no fictional magazine holes are added.
    u=[(0,0),(40,0),(40,65),(520,65),(520,0),(560,0),(560,90),(0,90)]
    lower=place(plate(u,6.35),(295,1082,LOWER_BASE))
    top=place(plate(u,6.35),(295,1082,MAG_BASE-6.35))
    clamps=((305.,1097.),(305.,1132.),(845.,1097.),(845.,1132.))
    for x,y in clamps:
        lower=lower.cut(cyl(6,8,(x,y,LOWER_BASE-1)))
        top=top.cut(cyl(6.6,8,(x,y,MAG_BASE-7.35)))
        pad=cut(box(x-10,y-10,1010.15,20,20,13.65),[cyl(6.6,36,(x,y,1009.15))])
        add(f'ATC_HARD_SEAT_{int(x)}_{int(y)}',pad,'rack',notes=[
            'Three ground seats establish the plane; fourth is hard-shim adjusted to bear without lifting the other seats.'])
        screw(f'ATC_DRAWDOWN_M6x25_{int(x)}_{int(y)}',6,25,(x,y,MAG_BASE),(0,0,1),'rack')
    for x,diamond in((325.,False),(825.,True)):
        lower=lower.cut(cyl(4,8,(x,1159,LOWER_BASE-1)))
        top=top.cut(cyl(6.02,8,(x,1159,MAG_BASE-7.35)))
        boss=box(x-10,1149,1010.15,20,20,13.65)
        for yy in(1153.,1165.):
            boss=boss.cut(cyl(4,12,(x,yy,1009.15)))
            lower=lower.cut(cyl(4.4,8,(x,yy,LOWER_BASE-1))).cut(cyl(7.5,4,(x,yy,LOWER_BASE)))
            screw(f'ATC_LOCATOR_RISER_M4x12_{int(x)}_{int(yy)}',4,12,(x,yy,LOWER_BASE+4),(0,0,-1),'rack')
        boss=boss.cut(cyl(4,7,(x,1159,1017.8)))
        add(f'ATC_LOCATOR_RISER_{int(x)}',boss.clean(),'rack',notes=['20x20x13.65 billet riser; two M4x12 underside attachments,5.65mm nominal engagement.'])
        p=cyl(6,9,(x,1159,1023.8))
        if diamond:p=p.intersect(box(x-2.7,1155,1022.8,5.4,8,12))
        p=p.fuse(cyl(4,6,(x,1159,1017.8))).clean()
        add('ATC_LOCATOR_'+('DIAMOND'if diamond else'ROUND'),p,'rack',
            notes=['Nominal6mm shoulder,9mm high,M4stud. Diamond5.4acrossX relieves thermal expansion. Fit/repeatability require measurement.'])
    add('ATC_LOWER_U_CARRIER',lower.clean(),'rack',notes=['6.35steel openU; weld rearland over RHS.'])
    add('ATC_REMOVABLE_MAGAZINE_U_BRIDGE',top.clean(),'rack',material='6061 aluminum6.35',
        notes=['560x90 openU; known locator/clamp holes only. Supplier magazine/endcap mounting pattern deliberately absent.'],
        flat=dict(outline=u,thickness_mm=6.35,holes=[(x-295,y-1082,6.6)for x,y in clamps]+[(30,77,6.02),(530,77,6.02)],slots=[],internal=[]))

    #Rear-only transport drive. Its front is behind TOOL_ADAPTER maxY1179.6;
    #the loop stays inward of the Z-module minimumX1015 at right travel.
    drive_x=1030.;yf,yr=1188.,1429.4
    pitch_r=16*2/(2*math.pi);ro,ri=pitch_r+.7,pitch_r-.7
    def stadium(r):return box(drive_x-r,yf,1076,2*r,yr-yf,6).fuse(cyl(2*r,6,(drive_x,yf,1076)),cyl(2*r,6,(drive_x,yr,1076)))
    belt=stadium(ro).cut(stadium(ri))
    for yy in(yf,yr):belt=belt.cut(cyl(9.7,8,(drive_x,yy,1075)))
    add('ATC_2GT_6MM_OPEN_BELT_ROUTE',belt.clean(),purchased=True,notes=['Nominal502mm path; openbelt cut allowance560mm. Smooth envelope clipped at pulley toothOD; tooth mesh is not represented.'])
    for yy,label in((yf,'IDLER'),(yr,'DRIVE')):
        pulley=cyl(12.4,1,(drive_x,yy,1075)).fuse(cyl(9.7,6,(drive_x,yy,1076)),cyl(12.4,1,(drive_x,yy,1082)))
        if label=='DRIVE':pulley=pulley.fuse(cyl(10,6,(drive_x,yy,1083)))
        pulley=pulley.cut(cyl(7 if label=='IDLER'else 5,26,(drive_x,yy,1067)))
        if label=='DRIVE':pulley=pulley.cut(cyl(3,4,(drive_x+2.5,yy,1086),(1,0,0)))
        add('ATC_16T_'+label,pulley.clean(),purchased=True,notes=['16T/2mmpitch,6belt,max12.4flange. Idler7bore with customacetalbush; drive5bore and M3hubgrub. Verify selected tooth profile.'])
    add('ATC_DRIVE_PULLEY_M3_GRUB',cyl(3,2.5,(drive_x+2.5,yr,1086),(1,0,0)),purchased=True,material='M3flushgrub,tangentto5mmshaft')
    bridge=box(1023.8,1182,1066.5,25.7,12,5).cut(cyl(5.2,8,(drive_x,yf,1065.5))).cut(cyl(9,4,(drive_x,yf,1064)))
    add('ATC_IDLER_BAR_BRIDGE',bridge.clean(),notes=['Welded5mmsteelbridgeonrightbackbartop;frontY1182is2.4behindcommonheadmax1179.6.'])
    axle=cyl(5,25,(drive_x,yf,1068)).fuse(cyl(8.5,3.5,(drive_x,yf,1064.5)))
    add('ATC_IDLER_M5x25_AXLE',axle.clean(),purchased=True,material='M5x25lowhead/shoulder candidate,5mmrunningdiameter')
    add('ATC_IDLER_LOWER_WASHER',cyl(10,1,(drive_x,yf,1071.5)).cut(cyl(5.2,3,(drive_x,yf,1070.5))),purchased=True)
    add('ATC_IDLER_AXIAL_SPACER',cyl(8,2.5,(drive_x,yf,1072.5)).cut(cyl(5.2,4,(drive_x,yf,1071.5))),material='Acetal8OD5.2ID2.5long')
    add('ATC_IDLER_RUNNING_BUSH',cyl(7,8,(drive_x,yf,1075)).cut(cyl(5.02,10,(drive_x,yf,1074))),material='Acetal7OD5.02ID8long;fit/lubricationtestheld')
    add('ATC_IDLER_UPPER_WASHER',cyl(10,1,(drive_x,yf,1083)).cut(cyl(5.2,3,(drive_x,yf,1082))),purchased=True)
    add('ATC_IDLER_M5_NUT',cyl(9.24,4,(drive_x,yf,1084)).cut(cyl(5,6,(drive_x,yf,1083))),purchased=True,material='M5locknut9.24maxcircumdiameter')
    #PrimarycompactNEMA14:35nominalface,52body,0.4Nm,1.5A.
    motor=cut(box(1012.35,1411.75,1015,35.3,35.3,53),[cyl(3,4.5,(drive_x+dx,yr+dy,1063.5))for dx in(-13.,13.)for dy in(-13.,13.)])
    motor=motor.fuse(cyl(22,2,(drive_x,yr,1068)),cyl(5,25,(drive_x,yr,1068))).clean()
    add('ATC_NEMA14_14HS20_1504S',motor,purchased=True,notes=['PrimarymanufacturerPDF35x35x52,0.4Nm,1.5A.Currentprimarydrawings:35.3maxface,53maxbody,5x25maxshaft;26square,22pilot,4M3depth4min. Nominalshaft24/Dflat15. Hardwaretol/torquecapacityheld.'])
    mp=box(1012.35,1411.75,1068,35.3,35.3,6.35).fuse(box(1039.975,1390,1066.5,7.675,21.75,3.175))
    mp=mp.cut(cyl(22.4,9,(drive_x,yr,1067)))
    for i,(dx,dy) in enumerate(((-13.,-13.),(-13.,13.),(13.,-13.),(13.,13.))):
        mp=mp.cut(cyl(3.5,9,(drive_x+dx,yr+dy,1067)))
        screw(f'ATC_MOTOR_M3x10_{i}',3,10,(drive_x+dx,yr+dy,1074.35),(0,0,1))
    for xx in(1016.,1044.):mp=mp.cut(cyl(3,8,(xx,yr,1067.35)))
    add('ATC_MOTOR_WELDED_MOUNT',mp.clean(),notes=['6.35motorplate,welded3.175mmtabtocurrentbackbartop;cantilever9.75mmfrombarendtomotorfront.'])
    #Removable5panelsteelcase,newmale/female standoffs.
    case=box(1008.5,1411,1014,1.9,39,82.35).fuse(box(1049.6,1411,1014,1.9,39,82.35),box(1010.4,1448.1,1014,39.2,1.9,82.35),box(1008.5,1411,1096.35,43,39,1.9))
    front=box(1010.4,1411,1014,39.2,1.85,82.35).cut(box(1011.4,1410,1014,37.2,4,62.35)).cut(box(1023,1410,1074,14,4,10)).cut(box(1038.975,1410,1065.5,9.625,4,7))
    case=case.fuse(front).clean()
    for xx in(1016.,1044.):
        case=case.cut(cyl(3.3,4,(xx,yr,1095.35)))
        post=cyl(6.4,22,(xx,yr,1074.35)).fuse(cyl(3,6,(xx,yr,1068.35))).cut(cyl(3,8,(xx,yr,1089.35)))
        add(f'ATC_DRIVE_STANDOFF_{xx}',post.clean(),purchased=True,material='M3male-female22+6,6.4maxOD')
        screw(f'ATC_DRIVE_CASE_M3x8_{xx}',3,8,(xx,yr,1098.25),(0,0,1))
    add('ATC_DRIVE_STEEL_CASE',case.clean(),notes=['Fivewelded1.9panels,openbottom;remove2M3roof screws. Heat/contaminationtestheld.'])
    grip=box(1012.5,1195.5,1063.5,19.5,13.5,19.5).cut(box(1023.8,1194.5,1069,2,15.5,15))
    grip=grip.cut(cyl(4.4,22,(1016.5,1203,1062.5))).cut(cyl(8,5,(1016.5,1203,1079)))
    grip=grip.cut(cyl(2,10,(1016.5,1207.5,1062.5))).cut(cyl(3,22,(1011,1198.5,1071),(1,0,0)))
    screw('ATC_BELT_GRIP_M4x22',4,22,(1016.5,1203,1079),(0,0,1),'rack')
    add('ATC_BELT_GRIP_D2_PIN',cyl(2,14.5,(1016.5,1207.5,1057.5)),'rack',purchased=True,material='2mmanti-rotationpin;fitheld')
    bolt=cyl(3,16,(1016,1198.5,1071),(1,0,0)).fuse(cyl(5.5,3,(1032,1198.5,1071),(1,0,0)))
    add('ATC_BELT_CLAMP_M3x16',bolt.clean(),'rack',purchased=True)
    add('ATC_MOVING_BELT_GRIP',grip.clean(),'rack',material='6061billet19.5x13.5x19.5',notes=['M4hold-down+2mmdowel;13.5mmgrip,matchedtoothinsertsand50Nslipproofrequired.'])
    for tag,xx,width in(('A',1023.8,(drive_x-ro)-.02-1023.8),('B',(drive_x-ri)+.02,1025.8-(drive_x-ri)-.02)):
        add('ATC_MOVING_BELT_LINER_'+tag,box(xx,1195.5,1076,width,13.5,6),'rack',purchased=True,material='Gripinsertnominalenvelope,matchactual2GTprofile')

    #Spring-engaged endpoint pins. A purchased CJPB6-10 pushes the flag;
    #it never carries rack shear. The right-side belt leaves this corridor clear.
    lug=box(109.5,1090,1094,7.7,20,6).cut(cyl(6.05,8,(113,1100,1093)))
    neck=box(116.2,1090,1063.5,13.175,20,36.5).cut(box(116.0,1089,1063.5,11.2,22,31.5))
    for yy in(1094.,1106.):
        neck=neck.cut(cyl(3.3,18,(136.5,yy,1062.5))).cut(cyl(6,3.5,(136.5,yy,1076.5)))
    dog=lug.fuse(neck).clean()
    dog=dog.cut(cyl(8,8,(113,1100,1093))).cut(cyl(3.6,22,(123.4,1090,1073.2),(0,1,0)))
    for xx in(120.4,124.4):dog=dog.cut(cyl(2,4,(xx,1089,1076.2),(0,1,0)))
    add('ATC_MOVING_LOCK_LUG',dog.clean(),'rack',material='6061 integral billet wing/dogleg',notes=[
        'Integral left wing and dogleg with steel press-fit pin bushing;4mm engaged,2mm withdrawn. Actual load/fit proof held.'])
    for ep in(1100.,1300.):
        tag='DEPLOY'if ep==1100 else'PARK'
        support_y=ep-20 if tag=='DEPLOY'else ep+12
        base=box(108.2,support_y,1066.5,9.8,8,4).fuse(box(108.2,support_y,1046.5,1.8,8,20))
        post=box(112,support_y,1070.5,6,8,11.5)
        cantilever_y=ep-20 if tag=='DEPLOY'else ep-10
        cantilever=box(108,cantilever_y,1082,10,30,6.35)
        cantilever=cantilever.cut(cyl(6.05,9,(113,ep,1081)))
        housing=box(108,ep-10,1088.35,10,20,12).cut(cyl(6.05,14,(113,ep,1087.35)))
        fixed=base.fuse(post,cantilever,housing).clean()
        for xx in(110.5,115.5):fixed=fixed.cut(cyl(3,10,(xx,ep-8 if xx<113 else ep+8,1095)))
        #Cylinders are ahead/behind the complete lug trajectory; no stand clearance cuts.
        add('ATC_LOCK_'+tag+'_FIXED',fixed.clean(),notes=[
            'Fabricated steel pin stand. Bored6.05 guided housing12long; load goes through housing/stop, never cylinder rod.'])
        shift=PIN_STROKE*float(unlocked)
        pin=cyl(6,25,(113,ep,1076+shift)).fuse(cyl(4,8,(113,ep,1101+shift))).clean()
        add('ATC_LOCK_'+tag+'_PIN',pin,notes=['6mm pin,6mm withdrawal,4mm engaged lug thickness; ground fit and actual shear proof required.'])
        flag=box(110,ep-46,1101+shift,6,92,2).fuse(cyl(8,2,(113,ep,1101+shift)))
        flag=flag.fuse(box(110,ep-47,1100+shift,6,2,4))
        flag=flag.cut(cyl(4.2,4,(113,ep,1100+shift)))
        for xx in(110.5,115.5):flag=flag.cut(cyl(3.4,6,(xx,ep-8 if xx<113 else ep+8,1099+shift)))
        add('ATC_LOCK_'+tag+'_FLAG',flag.clean(),material='Opaque2mm steel target/rod push plate')
        nut=cyl(8.083,3,(113,ep,1104+shift)).cut(cyl(4,5,(113,ep,1103+shift)))
        add('ATC_LOCK_'+tag+'_FLAG_M4_NUT',nut.clean(),purchased=True,material='M4hexnut7AF,8.083maxcircumdiameter')
        washer=cyl(12,1,(113,ep,1103+shift)).cut(cyl(4.3,3,(113,ep,1102+shift)))
        add('ATC_LOCK_'+tag+'_FLAG_WASHER',washer.clean(),purchased=True,material='M4largewasher12OD4.3ID1')
        cap=box(107,ep-10,1113,12,20,3).cut(cyl(6.5,5,(113,ep,1112)))
        for xx in(110.5,115.5):cap=cap.cut(cyl(3,5,(xx,ep-8 if xx<113 else ep+8,1112)))
        add('ATC_LOCK_'+tag+'_SPRING_CAP',cap.clean())
        for x in(110.5,115.5):
            add(f'ATC_LOCK_{tag}_CAP_POST_{x}',cyl(3,23,(x,ep-8 if x<113 else ep+8,1096)),purchased=True,material='M3 threaded support and retained nuts')
            add(f'ATC_LOCK_{tag}_CAP_NUT_{x}',cyl(6.351,2.4,(x,ep-8 if x<113 else ep+8,1116)).cut(cyl(3,4,(x,ep-8 if x<113 else ep+8,1115))),purchased=True,material='M3hexnut5.5AF,6.351maxcircumdiameter')
        spring=cyl(9.5,9-shift,(113,ep,1104+shift)).cut(cyl(8.5,11,(113,ep,1103+shift)))
        add('ATC_LOCK_'+tag+'_RETURN_SPRING_ENVELOPE',spring.clean(),purchased=True,
            notes=['Catalog requirement:OD<=9.5,ID>=8.5,free11,installed9,compressed3,solid<=2.5,k<=0.3N/mm,max2.4N. Actual spring selection held.'])
        #Legacy primary CJPB6-10:H9+S25.5=34.5 total retracted. Rod plane1101;
        #panel reference1092. This is a nominal envelope, not a fabricated cylinder.
        cy=ep-40 if tag=='DEPLOY'else ep+40
        actuator=cyl(10,19.5,(113,cy,1072.5)).fuse(cyl(5.6,6,(113,cy,1066.5)),cyl(3,9+shift,(113,cy,1092)))
        #12mm hex across flats,13.856 across corners, oriented flat across X.
        hexnut=cq.Workplane('XY').polygon(6,12/math.cos(math.pi/6)).extrude(2).val().rotate((0,0,0),(0,0,1),30).translate((113,cy,1092))
        actuator=actuator.fuse(hexnut).clean()
        add('ATC_LOCK_'+tag+'_SMC_CJPB6_10_NOMINAL',actuator,purchased=True,
            material='SMC CJPB6-10 single-acting cylinder; new',notes=[
                'Primary legacy CJPB6-10:6bore,10stroke,H9,S25.5,Z34.5,M10x1 panel thread,M3rod. Nominal placement uses6 of10mm stroke; real revision/fittings held.'])
        panel_y=ep-52 if tag=='DEPLOY'else ep+10
        panel=box(107,panel_y,1090,12,42,2).cut(cyl(10.2,4,(113,cy,1089)))
        add('ATC_LOCK_'+tag+'_CYLINDER_PANEL',panel.clean(),notes=['M10x1 cylinder locknut clamps2mm panel; no rod side load allowed.'])
        support=box(108.5,ep-70,1098,9,60,2).cut(cyl(3.5,4,(113,cy,1097)))
        clamp=box(108.5,ep-70,1097,9,6,16)
        for zz in(1102.,1108.):
            clamp=clamp.cut(cyl(3.1,8,(113,ep-71,zz),(0,1,0))).cut(cyl(2,4,(114,ep-67,zz),(1,0,0)))
        add('ATC_LOCK_'+tag+'_SENSOR_SUPPORT',support.fuse(clamp).clean(),notes=['Two3mmactual-pin sensors,0.5mmsettinggap;6mmverticalcentres.'])
        for j,zz in enumerate((1102.,1108.)):
            add(f'ATC_LOCK_{tag}_E2E_C03SR8_{j}',cyl(3,30,(113,ep-77.5,zz),(0,1,0)),purchased=True,pn='E2E-C03SR8-WC-B1',notes=['Primary3mm/0.8range/0.56setting.30mmconservativebodyallocation;deliveredlengthheld.'])
            add(f'ATC_LOCK_{tag}_SENSOR_M2_SET_{j}',cyl(2,3,(114.5,ep-67,zz),(1,0,0)),purchased=True,material='M2x3flushgrub,lowinstallationtorque')
        #Fitted stop extends from the fixed bar without crossing its swept wing.
        #Moving lug end faceY1090/1110; stops contact only at exact endpoints.
        sy=1080. if tag=='DEPLOY'else 1310.
        arm_y=1070. if tag=='DEPLOY'else 1320.
        stop=box(108.5,arm_y,1066.5,8.7,8,4).fuse(box(108.5,arm_y,1046.5,1.5,8,20))
        if tag=='DEPLOY':stop=stop.fuse(box(108.5,1076,1070.5,8.7,14,9))
        else:stop=box(100.5,1397.9,1063.5,22.525,4.1,3).fuse(box(123.025,1397.9,1048,5.85,10,18.5))
        if tag=='DEPLOY':stop=stop.cut(box(118,1060,1070,15,350,20))
        add('ATC_STOP_'+tag,stop.clean(),notes=['Weld/braze to steel backbar, fit end face to actual lug. Low-force approach, not rated crash absorber.'])

    #Actual-stage sensors look up at a steelpatch flush in the rear wing.
    #Both stations lie beyond main toolhead maxY1179.6 and inside ZbaseX135.
    for label,yy in(('DEPLOY',1194.9),('PARK',1394.9)):
        add('ATC_STAGE_E2E_C03SR8_'+label,cyl(3,30,(125,yy,1006)),purchased=True,pn='E2E-C03SR8-WC-B1',notes=['FaceZ1036,0.5mmgaptoferrouswingpatch.30mmbodyallocation,actualdrawingheld.'])
        clamp=box(121.5,yy-3,1009,7,6,6).cut(cyl(3.1,8,(125,yy,1008)))
        mount=box(104.9,yy-3,1002.65,23.6,6,6.35).fuse(box(106,yy-3,1009,4,6,24.5),clamp)
        mount=mount.cut(cyl(3.1,40,(125,yy,1000))).cut(cyl(2,4,(125.5,yy,1012),(1,0,0)))
        add('ATC_STAGE_SENSOR_MOUNT_'+label,mount.clean(),notes=['Weldtoleftbackbarunderside;fixedmaxX128.5andY>=1191.9clearsthecommonhead;clampsbelowmovingarm.'])
        add('ATC_STAGE_SENSOR_M2_SET_'+label,cyl(2,2,(126.5,yy,1012),(1,0,0)),purchased=True,material='M2x2flushgrub')
    wing=m.find('ATC_MOVING_WING_L')
    patch=box(123.025,1191.9,1036.5,6.35,6,1)
    wing.shape=wing.shape.cut(patch.translate((0,travel,0))).cut(cyl(2,4,(127,1194.9+travel,1036.5)))
    patch=patch.cut(cyl(2.2,3,(127,1194.9,1035.5)))
    head=cq.Solid.makeCone(1.9,1,1,cq.Vector(127,1194.9,1036.5),cq.Vector(0,0,1))
    patch=patch.cut(head)
    add('ATC_MOVING_STAGE_STEEL_PATCH',patch.clean(),'rack',material='Steel1mmflushpatch6.35x6')
    add('ATC_STAGE_PATCH_M2x4',head.fuse(cyl(2,3,(127,1194.9,1037.5))).clean(),'rack',purchased=True)

    #Rear steel protective hood; manual gate opened once for a cold wood job.
    #The selected magazine's own servo cover remains a separate supplier interface.
    for side,x in(('L',285.),('R',863.1)):
        sidewall=box(x,1272.0,965.4,1.9,119.9,173.6).cut(box(x-1,1271,978.15,4,116.9,54.8))
        add('ATC_HOOD_'+side,sidewall.clean(),notes=['Crossbeam passage1008.15..1062.95:2mm nominal running gaps. Vented hood, not sealed or thermally qualified.'])
    add('ATC_HOOD_REAR',box(286.9,1390.,965.4,576.2,1.9,173.6))
    add('ATC_HOOD_FLOOR',box(286.9,1272.0,965.4,576.2,118.0,1.9))
    add('ATC_HOOD_ROOF',box(285,1272.1,1139,580,119.8,1.9).cut(box(835,1270,1138,17.4,10,4)))
    gate=box(286.9,1265,965.4,576.2,1.9,173.6)
    add('ATC_STEEL_GATE',gate,'gate',notes=['161mm downward stroke; manual opening before wood ATC use; positively indexed both states.'])
    strap=box(863.1,1265,928,12,1.8,180)
    for zz in(940.,1101.):strap=strap.cut(cyl(6.1,5,(869.1,1264,zz),(0,1,0)))
    add('ATC_GATE_INDEX_STRAP',strap.clean(),'gate',notes=['Two6.1index holes161apart; captive manual6pin holds open/closed.'])
    gatepin=cyl(6,14,(869.1,1258,940),(0,1,0)).fuse(cyl(14,4,(869.1,1254,940),(0,1,0)))
    if gate_pin_withdrawn:gatepin=gatepin.translate((0,-16,0))
    add('ATC_GATE_INDEX_PIN',gatepin.clean(),purchased=True,material='Captive6mm pullpin; fully withdraw before gate movement')
    keeper=box(861.1,1258,930,16,4,20).cut(cyl(6.1,6,(869.1,1257,940),(0,1,0)))
    add('ATC_GATE_PIN_KEEPER',keeper.clean(),notes=['Weld to fixed right guide; captive chain/tether and hand operation.'])
    add('ATC_GATE_HANDLE',box(550,1250,1050,50,15,8),'gate',notes=['Welded steel pullhandle; open only with stationary rack parked.'])
    for name,x,left in(('L',281.,True),('R',873.1,False)):
        channel=box(x,1262,836,7.9,10,305)
        voidx=x+1.9 if left else x-.1
        channel=channel.cut(box(voidx,1263.9,835.9,6.1,6.2,305.2))
        #No cross-channel flag arm: optical target is on the gate inside the guide span.
        channel=channel.cut(box(x-1,1261,978.15,10,12,54.8))
        add('ATC_GATE_GUIDE_'+name,channel.clean(),notes=['Steel Uchannel captures2mm panel/strap edge with running clearance.'])
    for zz in(970.,1100.):add('ATC_GATE_RIGHT_TIE_'+str(int(zz)),box(863.1,1270.1,zz,16,1.9,5))
    #Keeper joins right guide without crossing the spindle rear boundary.
    add('ATC_GATE_KEEPER_SUPPORT',box(877,1260,930,4,4,20))
    #Hood load goes to the rear pan crossbeam, not the precision ATC guides.
    #The rear-face M6rows746.5/786.5 are explicit frame-datum interfaces.
    for x in(315.,835.):
        base=cut(box(x-20,1200,738,40,6.35,56),
                 [cyl(6.6,9,(x,1199,z),(0,1,0))for z in(746.5,786.5)])
        arm=box(x-12.7,1206.35,744,25.4,188.65,25.4).cut(
            box(x-11.1,1205.35,745.6,22.2,190.65,22.2))
        upright=box(x-12.7,1369.6,769.4,25.4,25.4,170.6).cut(
            box(x-11.1,1371.2,768.4,22.2,22.2,172.6))
        stand=base.fuse(arm,upright).clean()
        stand=stand.cut(cyl(11,14,(x,1206.35,746.5),(0,1,0)))
        add('ATC_HOOD_STAND_'+str(int(x)),stand,notes=[
            'Steel25.4RHS1.6wall cantilever and upright,6.35rear-faceplate; weld3mmfillets. Mount to structural beam, not pan wall.'])
        for z in(746.5,786.5):
            screw(f'ATC_HOOD_FRAME_M6x16_{int(x)}_{int(z)}',6,7.95,(x,1207.95,z),(0,1,0))
    cross=box(302.3,1369.6,940,545.4,25.4,25.4).cut(
        box(301.3,1371.2,941.6,547.4,22.2,22.2))
    add('ATC_HOOD_SUPPORT_RHS',cross.clean())
    #Gate opticals face an Ltarget outsidethecarrier, without crossing aguide.
    for label,z0,invert in(('CLOSED',1124.5,True),('OPEN',951.5,False)):
        sen=pin_d6_sensor_body()
        if invert:sen=sen.rotate((6.7,3,8),(7.7,3,8),180)
        sen=place(sen,(866,1262.6,z0),u=(0,-1,0),v=(1,0,0))
        add('ATC_GATE_PM_'+label,sen,purchased=True,pn='PM-U25-P',color=SENSOR)
        row=z0+(13.5 if invert else 2.5)
        mount=box(872,1249.2,row-3,2,13.4,6)
        for yy in(1251.9,1259.9):mount=mount.cut(cyl(3,4,(871,yy,row),(1,0,0)))
        add('ATC_GATE_SENSOR_BRACKET_'+label,mount.clean())
        for j,yy in enumerate((1251.9,1259.9)):
            bolt=cyl(3,8,(866,yy,row),(1,0,0)).fuse(cyl(5.7,1.65,(864.35,yy,row),(1,0,0)))
            add(f'ATC_GATE_SENSOR_M3x8_BUTTON_{label}_{j}',bolt.clean(),purchased=True,material='M3x8ISO7380buttonhead5.7x1.65')
    flag=box(861,1255.2,1125.5,11,1.6,2).fuse(box(861,1255.2,1125.5,2.1,11.7,2))
    add('ATC_GATE_OPAQUE_FLAG',flag.clean(),'gate',material='Opaque2mmsteelLtarget')
    def weld_join(target,children):
        p=m.find(target)
        for child in children:
            c=m.find(child);p.shape=p.shape.fuse(c.shape).clean();p.notes+=c.notes
            m.remove(child);classes.pop(child,None)
        b=bbox(p.shape);p.local=p.shape.translate(tuple(-x for x in b[:3]))
    weld_join('ATC_LOCK_DEPLOY_FIXED',['ATC_STOP_DEPLOY'])
    weld_join('ATC_BACKBAR_L',['ATC_STOP_PARK'])
    #Two-sided positiveYcapture: mirror every fixedlock, flag andsensor.
    originals=[p for p in m.parts if p.id.startswith('ATC_LOCK_')or p.id=='ATC_STOP_DEPLOY']
    for p in originals:
        pp=add('ATC_R_'+p.id[4:],reflect(p.shape,False),purchased=p.purchased,material=p.material,notes=p.notes,pn=p.part_number)
    add('ATC_MOVING_RIGHT_DOG',reflect(dog,False),'rack',material='6061integralrightwingdog')
    weld_join('ATC_MOVING_WING_L',['ATC_MOVING_LOCK_LUG'])
    weld_join('ATC_MOVING_WING_R',['ATC_MOVING_RIGHT_DOG'])
    for side,left in(('L',True),('R',False)):
        bush=cyl(8,6,(113,1100,1074)).cut(cyl(6.05,8,(113,1100,1073))).clean()
        add('ATC_MOVING_PIN_BUSHING_'+side,reflect(bush.translate((0,0,20)),left),'rack',purchased=True,material='Steel8OD6.05ID6long,fitheld')
    q=m.find('ATC_CARRIER_END_R')
    q.shape=q.shape.cut(cyl(4,8,(1016.5,1203+travel,1056.5))).cut(cyl(2,7,(1016.5,1207.5+travel,1056.5)))
    weld_join('ATC_STEEL_GATE',['ATC_GATE_INDEX_STRAP','ATC_GATE_OPAQUE_FLAG'])
    weld_join('ATC_GATE_GUIDE_R',['ATC_GATE_KEEPER_SUPPORT','ATC_GATE_PIN_KEEPER','ATC_GATE_SENSOR_BRACKET_CLOSED','ATC_GATE_SENSOR_BRACKET_OPEN','ATC_GATE_RIGHT_TIE_970','ATC_GATE_RIGHT_TIE_1100'])
    weld_join('ATC_HOOD_R',['ATC_HOOD_ROOF','ATC_GATE_GUIDE_R'])
    weld_join('ATC_HOOD_L',['ATC_GATE_GUIDE_L'])
    q=m.find('ATC_HOOD_R')
    for yy in(1264.2,1272.2):
        for zz in(1138.,954.):q.shape=q.shape.cut(cyl(3,10,(865,yy,zz),(1,0,0)))
    q.shape=q.shape.clean()
    return m,classes


@lru_cache(maxsize=6)
def _cached(travel,gate_open,unlocked,gate_pin_withdrawn=False):return _build(travel,gate_open,unlocked,gate_pin_withdrawn)


def atc_parts(hot=False,deployed=False,travel_mm=None,gate_open=None,unlocked=False,gate_fraction=None,gate_pin_withdrawn=False,pin_fraction=None):
    if hot and (deployed or travel_mm not in(None,200.) or gate_open or unlocked or gate_fraction not in(None,0)or gate_pin_withdrawn or pin_fraction not in(None,0)):
        raise ValueError('Plasma requires ATC parked, gate closed and pins engaged.')
    travel=(0. if deployed else 200.) if travel_mm is None else float(travel_mm)
    gate=(float(bool(deployed) if gate_open is None else bool(gate_open))if gate_fraction is None else float(gate_fraction))
    assert 0<=gate<=1
    pin=float(bool(unlocked)) if pin_fraction is None else float(pin_fraction)
    assert 0<=pin<=1
    model,_=_cached(travel,gate,pin,bool(gate_pin_withdrawn))
    return [(p.id,p.shape,p.color)for p in model.parts]


def atc_motion_class(name):
    kind=_cached(200.,0.,False)[1].get(name,'fixed')
    if kind=='rack':return 'ATC_Y_slide'
    if kind=='gate':return 'ATC_gate_Z'
    if name.startswith(('ATC_LOCK_','ATC_R_LOCK_'))and name.endswith(('_PIN','_FLAG','_FLAG_M4_NUT','_FLAG_WASHER')):return 'ATC_pin_Z'
    return 'stationary'


def retained_projection_allowance():return MAG_BASE-P.DRY_TOP-STOCK_HEIGHT-SAFE_RUNNING_GAP_MM

def acceptance_parts(deployed=True):
    shift=0 if deployed else 200
    a=box(315,1082+shift,MAG_BASE,KIT_MAX_LENGTH,KIT_WIDTH,KIT_MAX_HEIGHT)
    R=retained_projection_allowance()
    tool=box(337.5,1084.5+shift,MAG_BASE-R,475,44.4,R)
    return [('SUPPLIER_KIT_ACCEPTANCE_NOT_A_PART',a,(.8,.18,.6)),
            ('RETAINED_TOOL_PROJECTION_ACCEPTANCE_NOT_A_PART',tool,(.8,.35,.1))]


def interface_metadata():
    return dict(revision=P.REVISION,stroke_mm=TRAVEL,guide_length_mm=RAIL_LENGTH,
        guide_pitch_mm=65.,rail_end_reserves_mm=[12.1,12.1],rail_hole_end_distances_mm=[20.,15.],rail_seat_X_mm=[110.025,1039.975],
        magazine_base_Z_mm=MAG_BASE,carrier_lowest_over_stock_Z_mm=LOWER_BASE,
        stock_plus_clamp_height_mm=STOCK_HEIGHT,stock_top_Z_mm=P.DRY_TOP+STOCK_HEIGHT,
        stock_clearance_mm=LOWER_BASE-P.DRY_TOP-STOCK_HEIGHT,
        max_tool_projection_below_magazine_base_mm=retained_projection_allowance(),
        pocket_centre_acceptance_XY_mm=list(POCKET_REGION),
        actual_pocket_centres=None,actual_magazine_mount_pattern=None,
        actual_kit_interface_verified=False,
        stage_transport_gantry_Y=PARK_GANTRY_Y,loaded_tool_projection_P_mm=list(LOADED_TOOL_PROJECTION_P_MM),loaded_tool_radius_mm=LOADED_TOOL_RADIUS_MM,safe_running_gap_mm=SAFE_RUNNING_GAP_MM,required_running_gap_mm=SAFE_RUNNING_GAP_MM,nominal_spindle_reference_zero=NOMINAL_SPINDLE_REFERENCE_ZERO,pin_stroke_mm=PIN_STROKE,gate_stroke_mm=GATE_STROKE,
        manufacturer_requirements=dict(non_inset_clearance_mm=90,body_width_mm=60,
            ER11_max_tool_OD_mm=15,typical_unrecessed_stickout_mm=24,
            source='https://rapidchangeatc.com/faq/'),
        spindle_reference_is_measured_nut_plane=False,
        original_Z100_packaging_screen_margin_mm=1060-MAG_BASE-90,
        selected_Z200_packaging_screen_margin_mm=NOMINAL_SPINDLE_REFERENCE_ZERO+P.Z_TRAVEL-MAG_BASE-90,
        entry_bypass_head_X_mm=255.,pin_actuation_proof='Endpointchecks only; physicalwithdraw/returnforceanddynamicactuationremaincommissioninggates.',
        current_steel_gate='Manual opening before cold wood job; parked/closed input required for plasma. It is not the vendor servo dust cover.',
        release=False)

