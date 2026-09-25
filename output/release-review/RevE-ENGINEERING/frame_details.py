"""Frame joints, bracing, screw feet, pan supports and tank support structure."""
import math
import cadquery as cq
from cad_helpers import *

def hexpart(af,h,bore=0):
    r=af/math.sqrt(3);pts=[(r*math.cos(k*math.pi/3),r*math.sin(k*math.pi/3)) for k in range(6)]
    return plate(pts,h,[(0,0,bore)] if bore else [])

def edit_global(m,id,tool,note):
    p=m.find(id);p.shape=p.shape.cut(tool).clean();bb=bbox(p.shape)
    p.local=p.shape.translate(tuple(-x for x in bb[:3]));p.notes.append(note)

def diagonal(a,b,width=25.4,wall=2.1082,across=(1,0,0)):
    d=cq.Vector(*b)-cq.Vector(*a);L=d.Length
    plane=cq.Plane(origin=a,xDir=across,normal=d.normalized())
    return cq.Workplane(plane).rect(width,width).rect(width-2*wall,width-2*wall).extrude(L).val(),L

def make_frame(m):
    # Six-millimeter cap rise clears the independent Y-guide blocks during swaps.
    for side,x in enumerate((0,1099.2),1):
        cap=next(p for p in m.parts if p.group=='rail_cap' and abs(bbox(p.shape)[0]-(x-24.6))<1)
        cap.shape=cap.shape.translate((0,0,6))
        cap.notes.append('Raised6mm:underside1056/top1063.9375;continuousmachinedspacerunderrailcap.')
        m.add_plate(f'CAP_SPACER_{side}',50.8,1450,6,origin=(x,0,1050),pn='CAP_SPACER',group='rail_cap',
                    notes=['Finish-machine6mmfrom1/4instock;capfastenerpatterncoordinatedwithmotionmodule.'])
    # Six complete custom jack-foot assemblies; nominal leg bottom staysZ50.
    for side,x in enumerate((0,1099.2),1):
        for station,y in enumerate((0,699.6,1399.2),1):
            cx,cy=x+25.4,y+25.4;pre=f'FT_{side}_{station}_'
            floor=plate(rect(80,80),12.7,[(13,13,9),(67,13,9),(13,67,9),(67,67,9)])
            floor=floor.cut(cyl(32,2).translate((40,40,10.7))).clean()
            m.add(pre+'PAD',floor,origin=(cx-40,cy-40,0),pn='FT_PAD',group='feet',material='A36steel1/2in',
                  flat={'outline':rect(80,80),'thickness_mm':12.7,'holes':[(13,13,9),(67,13,9),(13,67,9),(67,67,9)],'slots':[],'internal':[],
                        'operations':[{'type':'circle','x':40,'y':40,'diameter':32,'layer':'MILL_POCKET_TOP_DEPTH_2'}],
                        'machining_notes':['Mill central32mm diameter recess2mm deep FROM TOP.','Pocket layer is NOT a through-cut.']},
                  notes=['MilltopØ32×2deepjack-headseat. FourØ9optionalanchorholes;flooranchorchoiceis site-specific.'])
            m.add_plate(pre+'LEG_CLOSURE',50.8,50.8,6,holes=[(25.4,25.4,17)],origin=(x,y,44),pn='FT_LEG_CLOSURE',group='feet',
                        notes=['WeldM16nutaboveclosurebeforeclosingleg. Continuous3mmfilletclosure-to-leg.'])
            m.add(pre+'UPPER_NUT',hexpart(24,13,16),origin=(cx,cy,50),pn='STD_M16_NUT',group='feet',material='M16grade8nut24AF×13',purchased=True,color=HARDWARE)
            m.add(pre+'JAM_NUT',hexpart(24,13,16),origin=(cx,cy,31),pn='STD_M16_NUT',group='feet',material='M16grade8nut24AF×13',purchased=True,color=HARDWARE)
            jack=hexpart(24,10).fuse(cyl(16,100).translate((0,0,10))).clean()
            m.add(pre+'JACK',jack,origin=(cx,cy,10.7),pn='STD_M16x100_HEX',group='feet',material='M16x100fullythreadedclass8.8',purchased=True,color=HARDWARE,
                  notes=['Jackheadrestsrecessedonthefloorpad.±8mmlevelingrange;retightenjamnutandrecheckthreadengagement. No casters.'])

    # Five actual25.4square-tube diagonals;outboard sidebraces do not cross storage.
    brace_endpoints=[]
    for side,cx,gx in [('L',-15.7,-3),('R',1165.7,1150)]:
        for j,(ay,by,lower_corner,upper_corner) in enumerate(((75.8,674.6,25.4,725),(775.4,1374.2,725,1424.6)),1):
            a=(cx,ay,285);b=(cx,by,974.2);sh,L=diagonal(a,b)
            bb=bbox(sh)
            m.add(f'FB_SIDE_{side}_{j}',sh.translate(tuple(-v for v in bb[:3])),origin=bb[:3],pn=f'FB_SIDE_{side}_{j}',group='bracing',material='A5001x1x.083tube',length=L,
                  notes=['Square-endnominalbrace;25.4×25.4×2.1082section. Weldinnerfaceto3mmgussets,3mmfilletsminimum50mmaccessibleedges.'])
            brace_endpoints.append([a,b])
            for end,cy,z,sgn in [('LOW',lower_corner,250,1),('HIGH',upper_corner,999.2,-1)]:
                outline=[(0,0),(160*sgn,0),(0,160*sgn)]
                m.add_plate(f'FB_GUSSET_{side}_{j}_{end}',160,160,3,outline=outline,origin=(gx,cy,z),u=(0,1,0),v=(0,0,1),
                            pn='FB_TRIANGLE_160_'+str(sgn),group='bracing',notes=['160mmlegsprovide>50mmbraceoverlap;3mmcontinuousfilletwheregussetoverlapsleg/rail.'])
    a=(75.8,1383.5,285);b=(1074.2,1383.5,974.2);sh,L=diagonal(a,b,across=(0,1,0));bb=bbox(sh)
    m.add('FB_REAR',sh.translate(tuple(-v for v in bb[:3])),origin=bb[:3],group='bracing',material='A5001x1x.083tube',length=L,
          notes=['ReardiagonalinsideframeatY1370.8..1396.2,clearofreservoir.'])
    for label,cx,z,sgn in [('LOW',25.4,250,1),('HIGH',1124.6,999.2,-1)]:
        outline=[(25.4,0),(160,0),(0,160),(0,30.8),(25.4,30.8)] if label=='LOW' else [(0,0),(-160,0),(0,-160)]
        m.add_plate('FB_REAR_GUSSET_'+label,160,160,3,outline=outline,origin=(cx,1399.2,z),u=(1,0,0),v=(0,0,1),
                    pn='FB_REAR_GUSSET_'+label,group='bracing',notes=['Lowergussetnotches25.4×30.8aroundexistinglowersiderail.'])

    # Three bolted pan-bearers, withtappedhangersratherthaninaccessibleouter nuts.
    for i,y in enumerate((175,675,1150),1):
        cy=y+25.4
        s=tube(1016.4)
        # Pan hold-downs onfirst/rearbearer:topwallholesandweldnutsbelow.
        if i in (1,3):
            s=s.cut(cq.Compound.makeCompound([cyl(6.6,5).translate((x-66.8,25.4,46.8)) for x in (108,1042)])).clean()
        m.add(f'PAN_BEARER_{i}',s,origin=(66.8,y,679.2),pn='PAN_BEARER_'+str(i),group='pan_support',material='A5002x2x.120tube',length=1016.4,
              notes=['Finishedtubeendsweldto8mmendplates;boltedinside8mmhangers. TopZ730.'])
        for side in (1,2):
            hanger_x=50.8 if side==1 else 1091.2
            end_x=58.8 if side==1 else 1083.2
            holes=[(dy,zz,8) for dy in (20,60) for zz in (15,105)]
            hp=m.add_plate(f'PB_HANGER_{i}_{side}',80,144.2,8,holes=holes,origin=(hanger_x,cy-40,645),u=(0,1,0),v=(0,0,1),pn='PB_HANGER',group='pan_support',
                        notes=['4×M8through-tapped:predrill6.8;CADusesnominalthreadenvelope. Weldtopedgeunderledgerwith3mmfilletsbothaccessible sides.'])
            hp.flat['holes']=[(dy,zz,6.8) for dy,zz,d in holes]
            hp.flat['machining_notes']=['4 holes:DRILL6.8 THEN TAP M8x1.25 THROUGH.','STEP8mm bores are nominal thread envelopes;DXF6.8mm is the manufacturing pilot.']
            m.add_plate(f'PB_END_{i}_{side}',80,130,8,holes=[(dy,zz,9) for dy in(20,60)for zz in(15,105)],origin=(end_x,cy-40,645),u=(0,1,0),v=(0,0,1),pn='PB_END',group='pan_support',
                        notes=['Weldtubetoendplate3mmfillets;matchfixturetobothhangerfacesbeforewelding.'])
            for j,(yy,zz) in enumerate([(cy+dy,z) for dy in(-20,20)for z in(660,750)],1):
                normal=1 if side==1 else-1
                bstart=52.4 if side==1 else 1097.6
                bolt=cyl(8,16).fuse(cyl(13,8).translate((0,0,16))).clean()
                m.add(f'PB_BOLT_{i}_{side}_{j}',bolt,origin=(bstart,yy,zz),u=(0,1,0),v=(0,0,normal),pn='STD_M8x16_SOCKET',group='fasteners',material='M8x16class8.8',purchased=True,color=HARDWARE)
                wx=66.8 if side==1 else 1083.2
                m.add(f'PB_WASHER_{i}_{side}_{j}',pipe(1.6,16,8.4),origin=(wx,yy,zz),u=(0,1,0),v=(0,0,normal),pn='STD_M8_WASHER',group='fasteners',material='M8flatwasher16×8.4×1.6',purchased=True,color=HARDWARE)
        if i in (1,3):
            for j,x in enumerate((108,1042),1):
                m.add(f'PB_PAN_NUT_{i}_{j}',hexpart(10,5,6),origin=(x,cy,721.952),pn='STD_M6_WELDNUT',group='fasteners',material='M6weldnut',purchased=True,color=HARDWARE)

    # Tank load is carried into rearlegs through an additional welded2x2shelf frame.
    for side,x in enumerate((0,1099.2),1):
        s=place(tube(648.8),(x,750.4,124.2),u=(0,1,0),v=(1,0,0))
        # Abovebasisnormal−Zrequirescorrectplacing; use directaxis-alignedtubeinstead.
        s=box(50.8,648.8,50.8).cut(box(44.704,650.8,44.704).translate((3.048,-1,3.048))).clean()
        m.add(f'TS_OUTER_TIE_{side}',s,origin=(x,750.4,124.2),pn='TS_OUTER_TIE',group='tank_support',material='A5002x2x.120tube',length=648.8,
              notes=['Weldendsdirectlytomiddle/rearlegfaces. TopZ175.'])
    for i,y in enumerate((800,1020,1175),1):
        m.add(f'TS_CROSS_{i}',tube(1048.4),origin=(50.8,y,124.2),pn='TS_CROSS',group='tank_support',material='A5002x2x.120tube',length=1048.4,
              notes=['Continuous3mmendfillets;reservoirfloorrestsontop. RearcleanoutneckatY1260isclear.'])

    # End closures for independently sealed stationary ballast compartments.
    for typ,x,z in [('TOP_L',0,999.2),('TOP_R',1099.2,999.2),('LEDGER_L',50.8,789.2),('LEDGER_R',1048.4,789.2)]:
        for label,y in [('FRONT',0),('REAR',1453.048)]:
            m.add_plate(f'SAND_ENDCAP_{typ}_{label}',50.8,50.8,3.048,origin=(x,y,z),u=(1,0,0),v=(0,0,1),pn='SAND_ENDCAP_2IN',group='ballast',
                        notes=['Continuouslyweldclosurebeforeballastfilling. Neverweldwithsand/waterincompartment.'])

    # One serviceportperstationarytube. Portis a custommachinedM20×1.5bung/plug,
    #threadenvelopesnominal;predrill18.5andtap. Portsarenotpressurefittings.
    ports=[]
    for side,x in enumerate((0,1099.2),1):
        for station,y in enumerate((0,699.6,1399.2),1):
            # Outer face is clear of stored-beam transport and side gussets.
            face=0 if side==1 else 1150;normal=-1 if side==1 else 1
            ports.append((f'MF_LEG_{side}_{station}',(face,y+25.4,800),(0,1,0),(0,0,normal)))
    # Horizontalmembershaveportsontheaccessibleupperface;railsarefilledbefore cap/moduleinstallation.
    for p in list(m.parts):
        if p.group!='main_frame' or 'LEG' in p.id:continue
        bb=bbox(p.shape);cx=(bb[0]+bb[3])/2;cy=(bb[1]+bb[4])/2
        if 'END_FRONT' in p.id:
            ports.append((p.id,(cx,0,(bb[2]+bb[5])/2),(1,0,0),(0,0,1)))
        elif 'TOP_Y' in p.id:
            # Outerwallserviceaccessavoidsrailcap;fillandweigh,donotassumeperfectpacking.
            left=bb[0]<100;face=bb[0] if left else bb[3];normal=-1 if left else 1
            ports.append((p.id,(face,1250,(bb[2]+bb[5])/2),(0,1,0),(0,0,normal)))
        elif 'RECEIVER_LEDGER' in p.id:
            # Rev F: the bed-module rails occupy the ledger tops Y30..1320. The
            # fill port moves behind the rail span, still forward of the rear legs.
            ports.append((p.id,(cx,1370,bb[5]),(1,0,0),(0,1,0)))
        else:ports.append((p.id,(cx,cy,bb[5]),(1,0,0),(0,1,0)))
    for i,(target,origin,u,v) in enumerate(ports,1):
        n=cq.Vector(*u).cross(cq.Vector(*v))
        tool=place(cyl(30,12).translate((0,0,-6)),origin,u,v)
        edit_global(m,target,tool,'Sandserviceport:Ø30weldbung,M20×1.5removableplug. Fillonlyafterallwelding/coating;weightactualdryballast.')
        bung=pipe(10,30,20)
        p0=tuple(origin[k]-n.toTuple()[k]*3.048 for k in range(3))
        m.add(f'SAND_BUNG_{i}',bung,origin=p0,u=u,v=v,pn='SAND_M20_BUNG',group='ballast',material='Machinedmildsteel',
              notes=['OD30×10;M20×1.5female,predrill18.5beforetap;nominalthreadenvelopeinSTEP. Continuouswatertightweldtotube.'])
        plug=cyl(20,10).fuse(cyl(28,6).translate((0,0,10))).cut(hexpart(6,4).translate((0,0,12))).clean()
        m.add(f'SAND_PLUG_{i}',plug,origin=p0,u=u,v=v,pn='SAND_M20_PLUG',group='ballast',material='CustomM20×1.5steelplug',
              notes=['Turn20mmthread×10long,28mmhead×6,6mmhexsocket4deep;sealwasherorremovabledustsealant.'])
    return {'feet_count':6,'level_adjustment_mm':8,'pan_bearer_cut_mm':1016.4,
            'pan_bearer_M8_count':24,'additional_tank_support_tube_m':4.4428,
            'brace_tube':'25.4×25.4×2.1082','side_brace_structural_x_mm':[-28.4,1178.4],
            'gusset_legs_mm':160,'sand_ports':len(ports),'ballast_note':'Stationaryframeonly;actualmassdeterminedbyweighingfill. No sand inbedbeams/cassettes/gantry.'}
