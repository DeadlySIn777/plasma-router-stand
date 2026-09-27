"""Two automatic endpoint pins; 45-degree translating fork cams, not motor holding."""
import math
import cadquery as cq
from retention import retain

def extend(e):
    add=e['add'];plate=e['plate'];bolt=e['bolt'];box=e['box'];cyl=e['cyl'];pose=e['pose'];hw=e['hw'];parts=e['parts'];ALU=e['ALU'];STEEL=e['STEEL'];POLY=e['POLY'];BLACK=e['BLACK']
    s=(6. if e['dock_release'] else 0.) if isinstance(e['dock_release'],bool) else float(e['dock_release'])
    nut=e['nut']
    mh=[(x-1520,y-455,5.5) for x,y in ((1530,500),(1630,500),(1730,500),(1770,545))]+[(30,15,6.5),(230,75,6.5)]
    plate('LOCK_STEEL_SUBPLATE',259.2,95,4,(1520,455,731),mh,material='S235 steel',note='Bolted steel lock module; thin isolating compound between steel and aluminum; weld internals before bolting.')
    for j,(x,y) in enumerate(((1530,500),(1630,500),(1730,500),(1770,545))):
        bolt('LOCK_MODULE_BOLT_'+str(j),5,25,(x,y,747.7),(0,0,-1));nut('LOCK_MODULE_NUT_'+str(j),5,8,4,(x,y,727))
    for index,pinx in enumerate((1550.,1750.)):
        first=len(parts);name=f'DOCK{index}_';off=pinx-1580
        # Model the first lock locally at its actual position, then mirror/translate the second.
        hole=[(15,10,12.),(0,10,4.5),(30,10,4.5)]
        plate(name+'GUIDE_CAP',40,20,11,(1560,460,747.7),[(20,10,12.),(5,10,4.5),(35,10,4.5)],cb=[(5,10,7.5,4),(35,10,7.5,4)],material='S235 steel')
        for j,x in enumerate((1565.,1595.)):bolt(name+'CAP_BOLT_'+str(j),4,14,(x,470,754.7),(0,0,-1))
        guide=cyl(6,23.7,1580,470,735).cut(cyl(3.02,26,1580,470,734))
        add(name+'GUIDE_BUSH',guide,'fixed','bronze',(.8,.6,.2),'OD12 press fit, ream6.04 after installation; sliding dry-film lubrication.')
        pin=cyl(3,64.7,1580,470,700-s).fuse(cyl(5,8,1580,470,707-s)).fuse(cyl(4,3,1580,470,722-s))
        add(name+'EXTENSION_STOP',cyl(4.5,6,1580,470,725).cut(cyl(3.2,8,1580,470,724)),'fixed','steel',STEEL,'Welded tube stop bears on integral8mm collar at s=0, setting2mm leaf preload and6mm maximum airgap.')
        follower=pose(cyl(2,18),(1580,461,715-s),(0,1,0),(1,0,0))
        pin=pin.cut(pose(cyl(2.05,20),(1580,460,715-s),(0,1,0),(1,0,0)))
        add(name+'PIN',pin,'dock_moving','ground steel',STEEL,'Ø6 shaft;4mm engagement,2mm released clearance; integral follower collar.')
        add(name+'FOLLOWER',follower,'dock_moving','hardened steel',STEEL,'Ø4 cross pin; end retention by welded/swaged thin heads after serviceable assembly.')
        for yy in (460.5,479.):add(name+'FOLLOWER_HEAD_'+str(yy),pose(cyl(2.7,.5),(1580,yy,715-s),(0,1,0),(1,0,0)),'dock_moving','steel',STEEL)
        for tag,y in [('F',461.),('R',475.)]:
            # True45degree slot: follower atfixedX descends exactly6mm as cam moves+6X.
            local=box(44,34,4)
            slot=cq.Workplane('XY').center(15,20).slot2D(math.sqrt(800)+4.4,4.4,45).extrude(6).val().translate((0,0,-1))
            local=local.cut(slot)
            if tag=='R':local=local.cut(box(18,9,6).translate((3,-1,-1)))
            shape=pose(local,(1565+s,y+4,695),(0,-1,0),(1,0,0))
            add(name+'CAM_'+tag,shape,'dock_moving','S235 steel',STEEL,'44x34x4; slot center1580/715,45deg between1570/705 and1590/725.',local,4)
        add(name+'CAM_BRIDGE',box(20,10,12).translate((1594+s,465,706)),'dock_moving','steel',STEEL,'Weld across fork plates; jig slot alignment.')
        tongue=box(8.2,4,7).translate((1614+s,468,706.5)).cut(pose(cyl(1.65,6),(1620.4364+s,467,710),(0,1,0),(1,0,0)))
        add(name+'CLEVIS_TONGUE',tongue,'dock_moving','steel',STEEL,'4mm tongue fits sourced4.826mm fork; assembled axial clearance must be inspected.')
        add(name+'CLEVIS_PIN',pose(cyl(1.6,12),(1620.4364+s,464,710),(0,1,0),(1,0,0)),'dock_moving','steel',STEEL)
        for yy in (463.5,476.):add(name+'CLEVIS_RETAINER_'+str(yy),pose(cyl(2.4,.5),(1620.4364+s,yy,710),(0,1,0),(1,0,0)),'dock_moving','steel',STEEL,'Swaged retaining head; pin installed before swaging.')
        # Welded guide cage is attached to bridge underside;0.2mm side/vertical running clearance.
        for yy in (458.8,479.2):
            plate(name+'CAM_HANGER_'+str(yy),20,39.8,2,(1595,yy+2,691.2),normal=(0,-1,0),xdir=(1,0,0),material='S235 steel',note='Weld top edge to lock bridge; slot cage is open for cam service.')
        for zz in (692.8,729.2):
            for yy in (460.8,475.):add(name+'CAM_GIB_'+str((zz,yy)),box(20,4.2,1.8 if zz>700 else 2).translate((1595,yy,zz)),'fixed','bronze',(.8,.6,.2),'Braze bronze wear strip to cage;20mm support length.')
        # Two narrow clamps react coil body; mounting thread depth is intentionally not invented.
        front=1640.
        add(name+'SOLENOID',pose(hw.delta_housing(),(front,470,710),(-1,0,0),(0,1,0)),'fixed','Delta DSOL-1151-24C',BLACK)
        add(name+'PLUNGER',pose(hw.delta_plunger(False).translate((0,0,-s)),(front,470,710),(-1,0,0),(0,1,0)).cut(pose(cyl(1.65,14),(1620.4364+s,463,710),(0,1,0),(1,0,0))),'dock_moving','Delta plunger',STEEL)
        for j,x in enumerate((1644.,1680.)):
            # Strap is open toward the terminal wall; isolated terminal boots remain a delivery requirement.
            strap=box(6,36.956,4).translate((x,451.522,693.5032)).fuse(box(6,4,29).translate((x,484.478,697.5032))).fuse(box(6,36.956,4).translate((x,451.522,722.4968)))
            strap=strap.fuse(box(6,4,4.5032).translate((x,484.478,726.4968)))
            add(name+'BODY_STRAP_'+str(j),strap,'fixed','steel',STEEL,'Fabricated clamp welded to bridge; clamp preload/coil cooling and terminal location require delivered-part confirmation.')
        retain(e,name,1640,470,710,'S235 steel')
        # Fabricated leaf spring avoids an unsourced coil spring;<1N ideal maximumforce.
        L=40.;delta=2+s;pts=[(-10,702)]
        for j in range(17):
            xx=L*j/16;defl=delta*(3*L*xx*xx-xx**3)/(2*L**3);pts.append((xx,702-defl))
        pts.append((46,702-delta))
        outline=pts+[(x,z-.25) for x,z in reversed(pts)]
        leaf=cq.Workplane('XY').polyline(outline).close().extrude(10).val()
        leaf=pose(leaf,(1585,513,0),(-1,0,0),(0,-1,0)).cut(cyl(1.7,4,1580,518,699))
        add(name+'RETURN_LEAF',leaf,'dock_moving','301 full-hard spring steel',STEEL,'40x10x0.25 working cantilever plus6 flat contact tip and10 clamp tail;2mm preload+6travel. Ideal0.236..0.942N,362MPa. Curved analytic shape approximates local compliant contact; temper/fatigue held.')
        plate(name+'SPRING_ROOT',10,10,29,(1575,513,702),[(5,5,3.,8.,'bottom')],material='S235 steel',note='Weld upper face to lock module; leaf clamped below with M3.')
        plate(name+'SPRING_CLAMP',10,10,2,(1575,513,699.75),[(5,5,3.4)],material='S235 steel')
        bolt(name+'SPRING_CLAMP_BOLT',3,10,(1580,518,699.75))
        if index:plate(name+'SPRING_EXTENSION',20,33,4,(1570,490,731),material='S235 steel',note='Weld extension to main steel module edge.')
        # Opposed U-slot orientations detect the actual pin, without spring-contact force.
        flag=box(56,2,2).translate((1524,469,702-s))
        for fx in (1525.,1540.):flag=flag.fuse(box(2,19,2).translate((fx-1,470,702-s)))
        for p in parts[first:]:
            if p.id==name+'PIN':p.shape=p.shape.fuse(flag).clean();p.note+=' Welded1mm-web endpoint flag; jig after grinding bearing section.'
        for tag,cx,up,z0 in [('ENGAGED',1540.,False,717.),('RELEASED',1525.,True,683.)]:
            sb=box(13.4,16,6).cut(box(6,5.6,8).translate((3.7,10.5,-1)))
            for hx in (2.7,10.7):sb=sb.cut(cyl(1.6,8,hx,2.5,-1))
            # local x maps worldX; localY is +Z for upright, -Z for inverted.
            nor=(0,-1,0) if up else(0,1,0);ori=(cx-6.7,491 if up else 485,z0)
            add(name+'SENSOR_'+tag,pose(sb,ori,nor,(1,0,0)),'fixed','Panasonic PM-U25-P',BLACK,'Sourced U-slot body; cable route and fouling qualification remain open.')
            mz=z0+(2.5 if up else-2.5)
            plate(name+'SENSOR_BRACKET_'+tag,15,727-(mz-4),3,(cx-7.5,494,mz-4),[(3.5,4,3.4),(11.5,4,3.4)],normal=(0,-1,0),xdir=(1,0,0),material='S235 steel',note='Weld top to module underside/extension. Actual sensor mounting holes8mm pitch.')
            for j,xx in enumerate((cx-4,cx+4)):
                bolt(name+'SENSOR_BOLT_'+tag+str(j),3,12,(xx,485,mz),(0,1,0),(1,0,0));nut(name+'SENSOR_NUT_'+tag+str(j),3,5.5,2.4,(xx,494,mz),(0,1,0),(1,0,0))
        plate(name+'SENSOR_BRIDGE',35,12,4,(1516,487,727),material='S235 steel',note='Weld edge to underside lock subplate; sensor backplates join beneath.')
        # Both pins clear the ledger; park coil is offset60mm inY to avoid the deploycoil.
        for p in parts[first:]:
            if index and not (p.id==name+'PIN' or 'SENSOR' in p.id or any(k in p.id for k in ('RETURN_LEAF','SPRING_ROOT','SPRING_EXTENSION','SPRING_CLAMP'))):
                p.shape=p.shape.mirror('YZ',(1580,0,0)).translate((off,60,0))
            else:p.shape=p.shape.translate((off,60 if index else 0,0))
