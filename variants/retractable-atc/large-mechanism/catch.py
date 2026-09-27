"""Spring-applied shutter catch: static geometry only, no guaranteed arrest distance."""
import cadquery as cq
from retention import retain

def extend(e):
    add=e['add'];plate=e['plate'];bolt=e['bolt'];nut=e['nut'];box=e['box'];cyl=e['cyl'];pose=e['pose'];hw=e['hw'];parts=e['parts'];ALU=e['ALU'];STEEL=e['STEEL'];BLACK=e['BLACK'];sh=e['shutter'];s=(6. if e['catch_release'] else 0.) if isinstance(e['catch_release'],bool) else float(e['catch_release'])
    # 10 mm-pitch lower windows plus a dedicated164mm-travel openwindow.
    centers=[791+10*i for i in range(17)]+[955.]
    ladder=box(3,20,190).translate((1655,690,775+sh))
    for z in centers:ladder=ladder.cut(box(5,8,7).translate((1654,696,z-3.5+sh)))
    add('SHUTTER_RATCHET_LADDER',ladder,'shutter','S235 steel',STEEL,'Welded ladder; 10mm nominal pitch plus dedicated open window. Solenoid delay/rebound can exceed one pitch: dynamic arrest unqualified.')
    for p in parts:
        if p.id=='SHUTTER':
            for z in centers:p.shape=p.shape.cut(box(4,8,7).translate((1652,696,z-3.5+sh)))
    # Reinforcement loads the existing roof posts, not the thin cover sheet.
    beam=box(20,604,20).cut(box(16,606,16).translate((2,-1,2))).translate((1808,398,946))
    add('CATCH_LONGITUDINAL_BEAM',beam,'fixed','6061-T6',ALU,'20x20x2 tube welded to both corner angles; roof sheet has matching clearance cutout.')
    for p in parts:
        if p.id=='HOOD_ROOF':p.shape=p.shape.cut(box(22,606,4).translate((1807,397,959)))
    plate('CATCH_ROOF_CAP',24,608,2,(1806,396,966),material='5052 aluminum')
    for p in parts:
        if p.id=='CATCH_ROOF_CAP':
            for yy in (663.,717.):p.shape=p.shape.cut(box(22,22,4).translate((1807,yy-1,965)))
    for tag,y in [('F',663.),('R',717.)]:
        beam=box(148,20,10).cut(box(150,16,6).translate((-1,2,2))).translate((1660,y,972))
        add('CATCH_CROSS_BEAM_'+tag,beam,'fixed','6061-T6',ALU,'20x10x2 cantilever welded to post on longitudinal beam.')
        plate('CATCH_BEAM_POST_'+tag,20,20,6,(1808,y,966))
    plate('CATCH_UPPER_BRIDGE',91,74,6,(1659,663,982))
    # Guided structural pin is distinct from the coil plunger.
    plate('CATCH_GUIDE_HANGER',24,20,19,(1658,690,963),[(6,10,4.5),(18,10,4.5)],note='Weld upper face to bridge; guide block bolted underneath.')
    block=box(9,20,16).translate((1660,690,947)).cut(pose(cyl(3.02,11),(1659,700,955),(1,0,0),(0,1,0)))
    for y in (694.,706.):block=block.cut(cyl(2.25,18,1664.5,y,946))
    add('CATCH_GUIDE',block,'fixed','bronze',(.8,.6,.2),'Ø6.04 guide; actual pin takes shutter reaction.')
    # Guide screw holes continue into hanger with two nominalM4taps.
    for j,y in enumerate((694.,706.)):
        for p in parts:
            if p.id=='CATCH_GUIDE_HANGER':p.shape=p.shape.cut(cyl(2,10,1664.5,y,962))
        bolt('CATCH_GUIDE_BOLT_'+str(j),4,24,(1664.5,y,947))
    shaft=pose(cyl(3,21),(1654+s,700,955),(1,0,0),(0,1,0)).fuse(pose(cyl(5,6),(1669+s,700,955),(1,0,0),(0,1,0)))
    #45degree lower-nose lead permits upward ratcheting; upperedge retains downwardload.
    wedge=cq.Workplane('XY').polyline([(1653,951),(1657,951),(1653,955)]).close().extrude(12).val()
    wedge=pose(wedge,(s,706,0),(0,-1,0),(1,0,0));shaft=shaft.cut(wedge)
    tail=box(7.2,4,7).translate((1675+s,698,951.5)).cut(pose(cyl(1.65,6),(1680.4364+s,697,955),(0,1,0),(1,0,0)))
    add('CATCH_PIN',shaft.fuse(tail),'catch_moving','ground steel',STEEL,'Pin4mm engagement and2mm released clearance; bevel is one-way lead. Load/impact proof required.')
    add('CATCH_CLEVIS_PIN',pose(cyl(1.6,12),(1680.4364+s,694,955),(0,1,0),(1,0,0)),'catch_moving','steel',STEEL)
    add('CATCH_SOLENOID',pose(hw.delta_housing(),(1700,700,955),(-1,0,0),(0,1,0)),'fixed','Delta DSOL-1151-24C',BLACK)
    add('CATCH_PLUNGER',pose(hw.delta_plunger(False).translate((0,0,-s)),(1700,700,955),(-1,0,0),(0,1,0)),'catch_moving','Delta plunger',STEEL)
    # Fabricated body saddle has an open terminal side; delivery mustconfirmbootclearance.
    for j,x in enumerate((1704.,1740.)):
        saddle=box(6,36.956,4).translate((x,681.522,938.5032)).fuse(box(6,4,29).translate((x,714.478,942.5032))).fuse(box(6,36.956,4).translate((x,681.522,967.4968))).fuse(box(6,8,0.5032).translate((x,714.478,971.4968)))
        add('CATCH_BODY_STRAP_'+str(j),saddle,'fixed','6061-T6',ALU,'Body strap welded to aluminum crossbeam underside; delivered terminal layout, clamp fit and coil cooling remain held.')
    for p in parts:
        if p.id=='HOOD_ROOF':p.shape=p.shape.cut(box(112,42,4).translate((1695,680,959))).cut(box(110,38,4).translate((1657,680,959))).cut(box(6,22,4).translate((1653,689,959))).cut(box(25,16,4).translate((1672,742,959)))
    retain(e,'CATCH_',1700,700,955,'6061-T6')
    # Return leaf lies in XY, clamped atY746; slotted tip surrounds the pin tail.
    pts=[(-10,1673)]
    for j in range(17):
        u=40*j/16;d=(2+s)*(3*40*u*u-u**3)/(2*40**3);pts.append((u,1673+d))
    pts.append((50,1675+s));outline=pts+[(u,x+.25) for u,x in reversed(pts)]
    leaf=cq.Workplane('XY').polyline(outline).close().extrude(10).val()
    # localX→−Y,localY→+X,extrusion→+Z
    leaf=pose(leaf,(0,745,950),(0,0,1),(0,-1,0)).cut(box(12,4.5,7.5).translate((1673+s,697.75,951.25))).cut(pose(cyl(1.7,5),(1671,750,955),(1,0,0),(0,1,0)))
    add('CATCH_RETURN_LEAF',leaf,'catch_moving','301 full-hard spring steel',STEEL,'40mm working leaf,6mm flat tip,0.25x10 section; ideal<1N. Fatigue and hot-coil release margin held.')
    plate('CATCH_SPRING_ROOT',10,15,23,(1673.25,745,950),[(5,5,3.,8.,'bottom')],normal=(1,0,0),xdir=(0,1,0),note='M3 blind tap8mm from left face; welded through riser tab to rear crossbeam.')
    plate('CATCH_SPRING_TAB',9.25,18,15,(1687,737,965),note='Welded to root top and rear crossbeam edge.')
    plate('CATCH_SPRING_CLAMP',10,10,2,(1671,745,950),[(5,5,3.4)],normal=(1,0,0),xdir=(0,1,0),material='S235 steel')
    bolt('CATCH_SPRING_CLAMP_BOLT',3,10,(1671,750,955),(1,0,0),(0,1,0))
    # Noncontact catch feedback: opposed slot openings detect actual pin flags.
    flag=box(2,70,2).translate((1673+s,630,954))
    for yy in (630.,650.):flag=flag.fuse(box(2,2,19).translate((1673+s,yy-1,955)))
    for p in parts:
        if p.id=='CATCH_PIN':p.shape=p.shape.fuse(flag).clean()
    for tag,cy,eng in [('ENGAGED',650.,True),('RELEASED',630.,False)]:
        sensor=box(13.4,16,6).cut(box(6,5.6,8).translate((3.7,10.5,-1)))
        for x in (2.7,10.7):sensor=sensor.cut(cyl(1.6,8,x,2.5,-1))
        org=(1660 if eng else 1694,cy-6.7,976 if eng else 970);nor=(0,0,-1) if eng else(0,0,1)
        add('CATCH_SENSOR_'+tag,pose(sensor,org,nor,(0,1,0)),'fixed','Panasonic PM-U25-P',BLACK,'Opposed U slots detect actual guidedpin, not coilcommand.')
        mx=1662.5 if eng else 1691.5
        for j,yy in enumerate((cy-4,cy+4)):
            bolt('CATCH_SENSOR_BOLT_'+tag+str(j),3,12,(mx,yy,970));nut('CATCH_SENSOR_NUT_'+tag+str(j),3,5.5,2.4,(mx,yy,979))
    plate('CATCH_SENSOR_BACKPLATE',45,45,3,(1660,618,976),[(x-1660,y-618,3.4) for x,y in ((1662.5,646),(1662.5,654),(1691.5,626),(1691.5,634))],material='S235 steel',note='Steel sensor backplate and return angle; bolted through aluminum crossbeam with compression sleeves and isolation compound.')
    for p in parts:
        if p.id=='CATCH_SENSOR_BACKPLATE':p.shape=p.shape.fuse(box(45,4,18).translate((1660,659,971)))
    for j,x in enumerate((1680.,1698.)):
        hole=pose(cyl(2.25,27),(x,658,977),(0,1,0),(1,0,0))
        for p in parts:
            if p.id in ('CATCH_SENSOR_BACKPLATE','CATCH_CROSS_BEAM_F'):p.shape=p.shape.cut(hole)
            if p.id=='CATCH_SENSOR_BACKPLATE':p.shape=p.shape.cut(pose(cyl(4,5),(x,654,977),(0,1,0),(1,0,0)))
        add('CATCH_SENSOR_SLEEVE_'+str(j),pose(cyl(2.75,16).cut(cyl(2.25,18,z=-1)),(x,665,977),(0,1,0),(1,0,0)),'fixed','aluminum',ALU)
        bolt('CATCH_SENSOR_MOUNT_BOLT_'+str(j),4,30,(x,659,977),(0,1,0),(1,0,0));nut('CATCH_SENSOR_MOUNT_NUT_'+str(j),4,7,3.2,(x,683,977),(0,1,0),(1,0,0))
    for p in parts:
        if p.id=='HOOD_ROOF':
            for yy in (630.,650.):p.shape=p.shape.cut(box(10,4,4).translate((1672,yy-2,959)))
        if p.id in ('SHUTTER','SHUTTER_LIFT_ARM','SHUTTER_ARM_RETURN'):p.material='S235 steel';p.note+=' Steel shutter/arm weldment matches the steel ratchet ladder.'
    for yy in (693.5,706.):add('CATCH_CLEVIS_RETAINER_'+str(yy),pose(cyl(2.4,.5),(1680.4364+s,yy,955),(0,1,0),(1,0,0)),'catch_moving','steel',STEEL,'Swaged retaining head, installed after assembly.')
    # Removable top, with actual tappedAltabs and fourM4fasteners.
    holes=[]
    for tag,wall_y,tab_y in [('F',610.,618.),('R',774.,768.)]:
        base=box(99,2,28).translate((1659,wall_y,962))
        for x in (1665.,1752.):
            tab=box(12,12,6).translate((x-6,tab_y-6,984)).cut(cyl(2,8,x,tab_y,983))
            base=base.fuse(tab);holes.append((x-1659,tab_y-610,4.5))
        add('CATCH_CAP_BASE_'+tag,base,'fixed','5052/6061 aluminum',ALU,'Fixed front/rear service-cover bracket with 6 mm tapped tabs. Weld bottom to hood roof; M4 nominal-major bores.')
    plate('CATCH_SERVICE_CAP',101,166,2,(1659,610,990),holes,material='5052 aluminum',note='Remove four M4x6 screws and lift 60 mm together with the welded right downstand.')
    plate('CATCH_CAP_DOWNSTAND',166,8,2,(1758,610,982),normal=(1,0,0),xdir=(0,1,0),material='5052 aluminum',note='Weld upper edge to removable service cap at Z990; this wall leaves with the cover to clear axial coil extraction.')
    for j,(x,y) in enumerate(( (x,y) for x in (1665.,1752.) for y in (618.,768.))):bolt('CATCH_CAP_BOLT_'+str(j),4,6,(x,y,992),(0,0,-1))
