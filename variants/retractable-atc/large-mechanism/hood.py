"""Fabricated hood and independent powered shutter. Not a plasma enclosure."""
import math

def extend(e):
    add=e['add'];plate=e['plate'];bolt=e['bolt'];nut=e['nut'];box=e['box'];cyl=e['cyl'];pose=e['pose'];hw=e['hw'];parts=e['parts'];sh=e['shutter'];STEEL=e['STEEL'];ALU=e['ALU'];POLY=e['POLY'];BLACK=e['BLACK']
    # Welded porches tie the cover to the two continuous rail bars.
    for tag,y,h in [('F',374,31),('R',995,31)]:
        holes=[(x-1640,yy-y,4.,8.,'top') for x in (1813.,1823.) for yy in ([388.] if tag=='F' else [1012.])]
        holes += [(x-1640,yy-y,5.,9.,'top') for x in (1649.,1659.) for yy in ([389.] if tag=='F' else [1011.])]
        if tag=='F':holes += [(1712-1640,390-y,6.,10.,'top'),(1724-1640,390-y,6.,10.,'top')]
        plate('HOOD_PORCH_'+tag,190,h,12.7,(1640,y,735),holes,note='Weld edge to rail bar before rail-plane machining; M4/M5/M6 blind taps as modeled.')
    for tag,y in [('F',382.),('R',1002.)]:
        plate('HOOD_POST_FOOT_'+tag,20,16,6,(1808,y,747.7),[(5,6 if tag=='F' else 10,4.5),(15,6 if tag=='F' else 10,4.5)],cb=[(5,6 if tag=='F' else 10,7.5,4),(15,6 if tag=='F' else 10,7.5,4)])
        for j,x in enumerate((1813.,1823.)):bolt(f'HOOD_POST_BOLT_{tag}_{j}',4,8,(x,y+(6 if tag=='F' else 10),749.7),(0,0,-1))
        # Open angle posts and roof cleats; welds carry cover loads into foot plates.
        add('HOOD_POST_'+tag,box(20,2,204.3).fuse(box(2,16,204.3)).translate((1808,y,753.7)),'fixed','6061-T6',ALU,'20x16x2 fabricated angle, welded foot/roof cleat.')
        plate('HOOD_ROOF_CLEAT_'+tag,20,16,2,(1808,y,958),[(5,8,4.5),(15,8,4.5)])
    # Cover shell is a welded sheet fabrication; edges meet, never overlap.
    plate('HOOD_RIGHT',638,160,2,(1828,382,800),normal=(1,0,0),xdir=(0,1,0),material='5052 aluminum',note='Weld to front/rear sheets; not a plasma shield.')
    plate('HOOD_REAR',167,160,2,(1661,1020,800),normal=(0,-1,0),xdir=(1,0,0),material='5052 aluminum')
    front=plate('HOOD_FRONT',167,160,2,(1661,382,800),normal=(0,-1,0),xdir=(1,0,0),material='5052 aluminum')
    # Moving lift arm passes through an open slot, protected by raised bonnet.
    for p in parts:
        if p.id=='HOOD_FRONT':p.shape=p.shape.cut(box(41,4,21).translate((1669.5,379,940))).cut(box(10,4,37).translate((1713,379,799))).cut(box(66,4,10).translate((1657,379,834)))
    roofholes=[(x-1655,y-380,4.5) for x in (1813.,1823.) for y in (390.,1010.)]
    plate('HOOD_ROOF',175,640,2,(1655,380,960),roofholes,material='5052 aluminum')
    roofcuts=[(1654,379,10,20,),(1654,1001,10,20),(1669.5,379,41,56.5),(1654,414.5,16,21)]
    for p in parts:
        if p.id=='HOOD_ROOF':
            for x,y,w,h in roofcuts:p.shape=p.shape.cut(box(w,h,4).translate((x,y,959)))
    for j,(x,y) in enumerate(( (x,y) for x in (1813.,1823.) for y in (390.,1010.))):
        bolt('ROOF_BOLT_'+str(j),4,12,(x,y,962),(0,0,-1));nut('ROOF_NUT_'+str(j),4,7,3.2,(x,y,954.8))
        for p in parts:
            if p.id.startswith('HOOD_POST_') and p.id in ('HOOD_POST_F','HOOD_POST_R'):p.shape=p.shape.cut(cyl(4.5,5,x,y,953.8))
    # Paired guides have 0.5 mm running gap per shutter face, a rear support, and real fasteners.
    for tag,y,b in [('F',380.,374.),('R',1002.,1020.)]:
        gz=790 if tag=='F' else 835; bz=755.7 if tag=='F' else 843.;zs=(810.,900.,1030.,1120.) if tag=='F' else(860.,900.,1030.,1120.)
        if tag=='F':
            plate('SHUTTER_GUIDE_FOOT_'+tag,18,26,8,(1645,374,747.7),[(4,15,5.5),(14,15,5.5)])
            for j,x in enumerate((1649.,1659.)):bolt(f'GUIDE_FOOT_BOLT_{tag}_{j}',5,16,(x,389,755.7),(0,0,-1))
        else:
            for p in parts:
                if p.id=='HOOD_PORCH_R':p.shape=p.shape.fuse(box(38,100,12.7).translate((1638,995,735))).clean();p.note+=' Integral rear guide porch projects toY1095, avoiding complete nut/carriage lug sweep.'
            plate('REAR_GUIDE_RISER',18,8,87.3,(1645,1080,747.7),note='Weld foot and upper cantilever, full-width contact.')
            plate('REAR_GUIDE_CANTILEVER',18,68,8,(1645,1020,835),note='Weld to rear riser and guide back; underside above nut-carrier sweep.')
        # Both backs are placed with local Y upward; positive thickness faces inward.
        normal=(0,1,0) if tag=='F' else(0,-1,0);origin=(1645,374 if tag=='F' else 1026,755.7)
        # local x is -X for +Y normal, to keep local y = +Z. Use reversed x origins.
        origin=(1663,374,bz) if tag=='F' else(1645,1026,bz);xd=(-1,0,0) if tag=='F' else(1,0,0)
        holeback=[(1663-x if tag=='F' else x-1645,z-bz,3.4) for x in (1650.25,1657.75) for z in zs]
        plate('SHUTTER_GUIDE_BACK_'+tag,18,1140-bz,6,origin,holeback,normal,xd)
        for side,x in [('L',1648.),('R',1655.5)]:
            # Bore from guide back through first6.5mm only. POM needs tapped insert qualification.
            g=box(4.5,18,1140-gz).translate((x,y,gz))
            for z in zs:
                g=g.cut(pose(cyl(1.5,6.5),(x+2.25,y if tag=='F' else y+18,z),normal,xd))
            add(f'SHUTTER_GIB_{tag}_{side}',g,'fixed','POM',POLY,'Blind M3 nominal taps 6.5 mm; verify polymer creep and thread retention.')
            for j,z in enumerate(zs):
                bolt(f'GIB_BOLT_{tag}_{side}_{j}',3,12,(x+2.25,374 if tag=='F' else 1026,z),normal,xd)
        for p in parts:
            if p.id==f'SHUTTER_GIB_{tag}_R':p.shape=p.shape.fuse(box(3,5,1140-gz).translate((1652.5,380 if tag=='F' else 1015,gz))).clean();p.note='Machine guide and edge stop from one POM blank; blind M3 taps 6.5 mm.'
    plate('SHUTTER',629.5,160,2,(1653,385.25,800+sh),normal=(1,0,0),xdir=(0,1,0),group='shutter',material='5052 aluminum',note='Two mm sheet, 164 mm lift. Independent of manufacturer magazine cover.')
    # Lift motor, welded column and nut arm. It is not self-locking.
    plate('SHUTTER_DRIVE_FOOT',24,70,8,(1706,330,747.7),[(6,60,6.6),(18,60,6.6)],cb=[(6,60,11,6),(18,60,11,6)])
    for j,x in enumerate((1712.,1724.)):bolt('SHUTTER_DRIVE_FOOT_BOLT_'+str(j),6,10,(x,390,749.7),(0,0,-1))
    plate('SHUTTER_DRIVE_COLUMN',70,79.3,8,(1714,330,755.7),normal=(1,0,0),xdir=(0,1,0),note='Weld foot and motor shelf, jig pilot after welding.')
    mh=[(32+dx,32+dy,3.4) for dx in (-15.5,15.5) for dy in (-15.5,15.5)]+[(32,32,22.2)]
    plate('SHUTTER_MOTOR_SHELF',64,64,8,(1658,318,835),mh)
    for p in parts:
        if p.id=='SHUTTER_MOTOR_SHELF':p.shape=p.shape.cut(box(6,9,10).translate((1657.5,373.5,834)))
    add('SHUTTER_MOTOR',pose(hw.slide_motor(),(1690,350,835)),'fixed','purchased stepper',BLACK)
    for j,(dx,dy) in enumerate(((-15.5,-15.5),(-15.5,15.5),(15.5,-15.5),(15.5,15.5))):bolt('SHUTTER_MOTOR_BOLT_'+str(j),3,12,(1690+dx,350+dy,843),(0,0,-1))
    nh=[(20,12,8.8)]+[(20+9.525*math.cos(math.radians(a)),12+9.525*math.sin(math.radians(a)),3.4) for a in (0,120,240)]
    plate('SHUTTER_LIFT_ARM',57,97,8,(1653,338,942+sh),[(x+17,y,d) for x,y,d in nh],group='shutter',outline=[(17,0),(57,0),(57,97),(2,97),(2,77),(17,77)],note='Weld vertical return flange to shutter; arm-to-sheet joint needs fatigue qualification.')
    plate('SHUTTER_ARM_RETURN',20,30,3,(1655,415,912+sh),normal=(1,0,0),xdir=(0,1,0),group='shutter',material='5052 aluminum',note='Weld along shutter and lift-arm edges.')
    add('SHUTTER_NUT',hw.slide_nut().translate((1690,350,950+sh)),'shutter','purchased POM nut',POLY)
    for j,a in enumerate((0,120,240)):
        x=1690+9.525*math.cos(math.radians(a));y=350+9.525*math.sin(math.radians(a))
        bolt('SHUTTER_NUT_BOLT_'+str(j),3,16,(x,y,942+sh),group='shutter_fasteners');nut('SHUTTER_NUT_NUT_'+str(j),3,5.5,2.4,(x,y,953.81+sh),group='shutter_fasteners')
    # Raised bonnet clears screw tip and moving arm; open-sided sheet weldment.
    add('SHUTTER_BONNET',box(2,107,178).translate((1713,334,962)).fuse(box(63,2,178).translate((1650,334,962))).fuse(box(57,2,178).translate((1656,439,962))).fuse(box(65,107,2).translate((1650,334,1140))),'fixed','5052 aluminum',ALU,'Weld sheet seams and attach to reinforced roof; no plasma protection qualification.')

    # Structural hard stops at both ends; motor and guide endcaps are not stops.
    for j,y in enumerate((440.,980.)):
        add('SLIDE_CHANGE_STOP_'+str(j),box(12,10,20).translate((1453,y,747.7)).fuse(box(15,10,8).translate((1465,y,747.7))),'fixed','6061-T6',ALU,'Weld to railbar; machine deployed faceX1465 after alignment. Optionalsetup shim is measured, not assumed.')
        add('SLIDE_PARK_STOP_'+str(j),box(5,10,20).translate((1825,y,747.7)).fuse(box(15,10,8).translate((1810,y,747.7))),'fixed','6061-T6',ALU,'Weld to railbar; machine parked faceX1825. Verify reaction and welds during proofload.')
