"""Rev E supported motion structure, mm.

HMS40 axes provide thrust only. HGR20 guides carry gantry and tool moments.
Purchased geometry is a conservative envelope wherever a supplier has not
published its section or mating detail. Those interfaces remain guarded.
"""
import math
import cadquery as cq
from cad_helpers import *

CAP_TOP = 1063.9375
GANTRY_BOTTOM = 1155.0
Y_GUIDE_CENTER = 1033.0
HOLD = 'INTERFACE HOLD - INDIVIDUAL EXPORT GUARDED'
ENV = 'PURCHASED CLEARANCE ENVELOPE - NOT MATERIAL MASS'

def socket(d, length, head_d=None, head_h=None):
    hd = head_d or {3:5.5,4:7,5:8.5,6:10,8:13}[d]
    hh = head_h or d
    return cyl(d,length).fuse(cyl(hd,hh).translate((0,0,length))).clean()

def bolt(m, ident, d, length, origin, u=(1,0,0), v=(0,1,0), pn=None):
    return m.add(ident,socket(d,length),origin=origin,u=u,v=v,
        pn=pn or f'STD_M{d}x{length:g}_SOCKET',group='motion_fasteners',
        material=f'M{d} class 8.8 socket screw, nominal threads',purchased=True,
        color=HARDWARE)

def hexring(af,h,bore):
    r=af/math.sqrt(3)
    return plate([(r*math.cos(k*math.pi/3),r*math.sin(k*math.pi/3)) for k in range(6)],h,[(0,0,bore)])

def cut_world(m,ident,tool,note):
    p=m.find(ident);p.shape=p.shape.cut(tool).clean()
    # Most mating holes here are perpendicular to local Z, so creator updates
    # flat operations separately; assembly solid remains the primary3D detail.
    p.notes.append(note)

def sensor(m,name,origin,u,v,roller_top):
    """D2VW micro-load switch envelope; mounting and roller datums sourced."""
    # u along body, v across body, normal up. Body holes are transverse.
    normal=cq.Vector(*u).cross(cq.Vector(*v)).toTuple()
    body=box(33,10.3,15.9)
    for xx,zz in((2.8,2.8),(25,13.1)):
        body=body.cut(place(cyl(3.1,12),(xx,-1,zz),u=(1,0,0),v=(0,0,-1))).clean()
    envelope(m,name+'_BODY',body,origin,u=u,v=v,pn='OMRON_D2VW-01L2-1M',group='limit_switches',
        material='Omron sealed gold-contact roller microswitch',
        notes=['D2VW-01L2-1M,SPDT with300 mm molded lead. Body33×10.3×15.9; mounting holes22.2×10.3 diagonal,Ø3.1.',
               'Use COM black and NC red; insulate unused NO blue.24 V isolated input at5 mA; do not connect24 V to Kraken pins.',
               'M3 mounting torque0.39–0.59 N·m. Roller operating position20.7±1.2 above bodybase; PT4 max,OT1.6 min. Cam continues on flat land.'])
    pt=tuple(origin[k]+u[k]*34+v[k]*2.75 for k in range(3));pt=(pt[0],pt[1],roller_top-2.4)
    roller=place(cyl(4.8,4.8),pt,u=(0,0,1),v=u)
    bb=bbox(roller)
    envelope(m,name+'_ROLLER',roller.translate(tuple(-x for x in bb[:3])),bb[:3],pn='INCLUDED_D2VW_ROLLER',
        group='limit_switches',material='Included roller envelope, not a separate purchase',
        notes=['Roller body only; small moving lever is omitted. Position follows the modeled cam without penetrating it.'])

def make_y_stops(m,gantry_y):
    """Separate Y1/Y2 NC home/limit pairs and low-speed crash buffers."""
    for side,left in [('L',True),('R',False)]:
        # Build on left; right is reflected through machine midplane.
        def xf(s):return s if left else s.mirror('YZ',(575,0,0))
        for end,front in [('FRONT',True),('REAR',False)]:
            y0,y1=(80,151) if front else(1400,1450)
            base=box(20.3,y1-y0,6.35).translate((57.5,y0,CAP_TOP))
            ext_y,ext_d=(80,40) if front else(1422,28)
            base=base.fuse(box(23,ext_d,6.35).translate((77.8,ext_y,CAP_TOP))).clean()
            post_y=113.65 if front else 1430
            post=box(15.8,6.35,50).translate((85,post_y,CAP_TOP+6.35))
            sy=109 if front else 1400
            back=box(3,42 if front else 45,50).translate((74.8,sy,CAP_TOP+6.35))
            stop=base.fuse(post).fuse(back).clean() if front else base.fuse(post).clean()
            # The post and back are connected through the single base plate.
            capscrew_y=(90,140) if front else(1410,1442)
            for gy in capscrew_y:
                stop=stop.cut(cyl(6.6,8).translate((66.5,gy,CAP_TOP-1))).clean()
                capid='RAIL_CAP_1_BLANK' if left else'RAIL_CAP_2_BLANK'
                if any(p.id==capid for p in m.parts):
                    gx=66.5 if left else 1083.5
                    cp=m.find(capid);old=bbox(cp.shape)
                    cp.shape=cp.shape.cut(cyl(6.6,10).translate((gx,gy,1055))).clean()
                    cp.local=cp.shape.translate(tuple(-x for x in old[:3]))
                    cp.notes.append('Y stop/switch bracket: Ø6.6 holes at X66.5/1083.5, Y90/140/1410/1442; within inboard cap overhang, clear of spacer.')
            # Switch body fixed on outboard face of this upright.
            switch_o=(74.8,109,1100) if front else(64.5,1441,1100)
            su=(0,1,0) if front else(0,-1,0)
            sv=(-1,0,0) if front else(1,0,0)
            for j,(al,zz) in enumerate(((2.8,2.8),(25,13.1)) if front else (),1):
                gy=switch_o[1]+su[1]*al;gz=1100+zz
                stop=stop.cut(place(cyl(3,5),(73.8,gy,gz),u=(0,1,0),v=(0,0,1))).clean()
                gx=78.5 if left else 1071.5
                bolt(m,f'Y_LIMIT_{side}_{end}_SCREW_{j}',3,14,(gx,gy,gz),u=(0,1,0),v=(0,0,-1 if left else 1),pn='STD_M3x14_SOCKET')
            # Compressible pad is retained by two flush M4 socket screws.
            py=120 if front else 1422
            pad=box(15.8,8,30).translate((85,py,1080))
            for j,gz in enumerate((1087,1103),1):
                # Drill axis from front or back of pad toward steel post.
                inward=-1 if front else 1
                face=128 if front else 1422
                hole=place(cyl(4.5,10),(92.9,face-inward,gz),u=(1,0,0),v=(0,0,-inward))
                pad=pad.cut(hole).clean()
                cb=place(cyl(8,4),(92.9,face,gz),u=(1,0,0),v=(0,0,-inward))
                pad=pad.cut(cb).clean()
                tap=place(cyl(4,8),(92.9,120 if front else 1430,gz),u=(1,0,0),v=(0,0,-inward))
                stop=stop.cut(tap).clean()
                # Under-head at4 mm below buffer face; screw runs from steel outward.
                start_y=face+inward*16
                gx=92.9 if left else 1057.1
                bolt(m,f'Y_BUFFER_{side}_{end}_SCREW_{j}',4,12,(gx,start_y,gz),u=(1,0,0),v=(0,0,inward))
            for ident,sh,mat in [('BRACKET',stop,'Welded A36 steel6.35 base/post,3 switch upright'),('BUFFER',pad,'EPDM70A rubber8 mm')]:
                sh=xf(sh);bb=bbox(sh)
                m.add(f'Y_STOP_{side}_{end}_{ident}',sh.translate(tuple(-x for x in bb[:3])),origin=bb[:3],
                    pn=f'Y_STOP_{side}_{end}_{ident}',group='motion_stops',material=mat,
                    notes=['Mechanical contact atY carriage268/1282;2 mm software margin to electrical trip273/1277,then5 mm to buffer.',
                           'Weld steel bracket continuously3 mm fillets along base/post. Switch holesØ2.5 pilot,tapM3×0.5 through3. Buffer holesØ3.3 pilot,tapM4×0.7 through6.35.',
                           'Low-speed commissioning crash buffer only. At600 mm/min and20 mm/s² stopping distance2.5 mm before latency; higher feeds need measured stop-distance verification.'])
            for j,gy in enumerate(capscrew_y,1):
                gx=66.5 if left else 1083.5
                bolt(m,f'Y_STOP_{side}_{end}_CAP_{j}',6,25,(gx,gy,1045.2875))
                m.add(f'Y_STOP_{side}_{end}_NUT_{j}',hexring(10,5,6),origin=(gx,gy,1051),
                    pn='STD_M6_NUT',group='motion_fasteners',material='M6 class8 steel nut',purchased=True,color=HARDWARE)
            # Roller follows cam; NC opening datum is set during commissioning.
            roller_y=143 if front else 1407
            leading=gantry_y-140 if front else gantry_y+140
            inside=(roller_y-leading) if front else(leading-roller_y)
            under=1127-6.3*max(0,min(inside,10))/10
            tangent_allowance=2.4*(math.sqrt(1+.63**2)-1) if 0<inside<12.4 else 0
            rtop=min(1124.7,under-tangent_allowance) if 0<=inside<=30 else 1124.7
            if front and not left:
                switch_o=(1150-switch_o[0],switch_o[1],switch_o[2]);sv=tuple(-x if i==0 else x for i,x in enumerate(sv))
                # Reflection reverses handedness; body rises after explicit shape reflection below.
                before=len(m.parts)
                sensor(m,f'Y_LIMIT_{side}_{end}',(74.8,109,1100) if front else(64.5,1441,1100),su,(-1,0,0) if front else(1,0,0),rtop)
                for p in m.parts[before:]:p.shape=xf(p.shape)
            elif front:sensor(m,f'Y_LIMIT_{side}_{end}',switch_o,su,sv,rtop)
        # Moving cam tabs, one at each end of the Y side shoe.
        for end,front in [('FRONT',True)]:
            cy=gantry_y-140 if front else gantry_y+110
            points=[(0,1127),(10,1120.7),(30,1120.7),(30,1129),(0,1129)] if front else[(0,1120.7),(20,1120.7),(30,1127),(30,1129),(0,1129)]
            cam=cq.Workplane('YZ',origin=(62,cy,0)).polyline(points).close().extrude(26.8).val()
            cam=cam.fuse(box(3,30,20).translate((85.8,cy,1100.7))).clean()
            for j,dy in enumerate((8,23),1):
                gy=cy+dy;gz=1110.7
                cam=cam.cut(place(cyl(4.5,5),(84.8,gy,gz),u=(0,1,0),v=(0,0,1))).clean()
                sx=88.8 if left else 1048.5
                sp=m.find('Y_SHOE_'+side)
                tap=place(cyl(4,8),(88.8,gy,gz),u=(0,1,0),v=(0,0,1))
                if not left:tap=tap.mirror('YZ',(575,0,0))
                sp.shape=sp.shape.cut(tap).clean()
                sp.local=sp.local.cut(cyl(4,8).translate((gy-(gantry_y-140),gz-1011,0 if left else 4.7))).clean()
                # Flat drill side is documented, not represented as through-cut pilot.
                sp.flat.setdefault('operations',[]).append({'type':'circle','x':gy-(gantry_y-140),'y':gz-1011,'diameter':3.3,'layer':'DRILL_M4_PILOT_DEPTH_9'})
                sp.flat.setdefault('machining_notes',[]).append('Cam holes:Ø3.3 pilot9 deep,TAP M4×0.7 depth8 from outboard face;M4×10 engagement7.')
                gx=95.8 if left else 1054.2
                bolt(m,f'Y_CAM_{side}_{end}_SCREW_{j}',4,10,(gx,gy,gz),u=(0,1,0),v=(0,0,-1 if left else 1))
            cam=xf(cam);bb=bbox(cam)
            m.add(f'Y_CAM_{side}_{end}',cam.translate(tuple(-v for v in bb[:3])),origin=bb[:3],pn=f'Y_CAM_{side}_{end}',
                group='motion_stops',material='Machined A36 steel cam and3 mm attachment web',
                notes=['10 mm ramp reduces underside from1127 to1120.7, followed by20 mm flat land. Cam is a switch actuator, not a hard stop.',
                       'TwoM4×10 screws into8 mm-deep threads; adjust switch trip with bracket before final pinning.'])

def envelope(m,ident,shape,origin,**kw):
    return m.add(ident,shape,origin=origin,group=kw.pop('group','motion_purchased'),
        purchased=True,release=ENV,color=PURCHASED,**kw)

def make_x_stops(m,head_x,face_y):
    for label,left in [('LEFT',True),('RIGHT',False)]:
        def xf(s):return s if left else s.mirror('YZ',(575,0,0))
        stop=box(20,45,26).translate((10,face_y-45,1239))
        for j,x in enumerate((15,25),1):
            hole=place(cyl(6.6,47),(x,face_y+1,1245),u=(1,0,0),v=(0,0,1))
            stop=stop.cut(hole).clean()
            gx=x if left else 1150-x
            bolt(m,f'X_STOP_{label}_BOLT_{j}',6,55,(gx,face_y+10,1245),u=(1,0,0),v=(0,0,1))
            fp=m.find('X_GUIDE_FACE')
            tap=place(cyl(6,10),(gx,face_y,1245),u=(1,0,0),v=(0,0,-1))
            fp.shape=fp.shape.cut(tap).clean()
            fp.local=fp.local.cut(cyl(6,10).translate((gx+25,102,2.7))).clean()
            fp.flat.setdefault('operations',[]).append({'type':'circle','x':gx+25,'y':102,'diameter':5,'layer':'DRILL_M6_PILOT_DEPTH_12'})
            fp.flat.setdefault('machining_notes',[]).append('X stop mounts:Ø5 pilot12 deep,TAP M6×1 depth10 fromfront face. M6×55 engages10 after45 mm stop block.')
        pad=box(8,14,20).translate((30,face_y-43,1245))
        for j,z in enumerate((1252,1260),1):
            h=place(cyl(4.5,10),(39,face_y-36,z),u=(0,1,0),v=(0,0,-1));pad=pad.cut(h).clean()
            cb=place(cyl(8,4),(38,face_y-36,z),u=(0,1,0),v=(0,0,-1));pad=pad.cut(cb).clean()
            tap=place(cyl(4,10),(30,face_y-36,z),u=(0,1,0),v=(0,0,-1));stop=stop.cut(tap).clean()
            gx=22 if left else 1128
            bolt(m,f'X_BUFFER_{label}_BOLT_{j}',4,12,(gx,face_y-36,z),u=(0,1,0),v=(0,0,1 if left else-1))
        if left:
            arm=box(16,12.4,5).translate((12,face_y-52.4,1265))
            back=box(45,3,18).translate((12,face_y-52.4,1270))
            stop=stop.fuse(arm).fuse(back).clean()
            for j,(x,z) in enumerate(((21.8,1272.8),(44,1283.1)),1):
                stop=stop.cut(place(cyl(3,5),(x,face_y-53.4,z),u=(1,0,0),v=(0,0,-1))).clean()
                bolt(m,f'X_HOME_SCREW_{j}',3,14,(x,face_y-48.7,z),u=(1,0,0),v=(0,0,1),pn='STD_M3x14_SOCKET')
            inside=53-(head_x-130)
            under=1297-6.3*max(0,min(inside,10))/10
            tangent_allowance=2.4*(math.sqrt(1+.63**2)-1) if 0<inside<12.4 else 0
            roller_top=min(1294.7,under-tangent_allowance) if 0<=inside<=30 else 1294.7
            sensor(m,'X_HOME',(19,face_y-62.7,1270),(1,0,0),(0,1,0),roller_top)
        for suffix,sh,mat in [('BODY',stop,'Machined A36 steel stop block; left switch bracket welded3 mm fillets'),('BUFFER',pad,'EPDM70A rubber8')]:
            sh=xf(sh);bb=bbox(sh)
            m.add(f'X_STOP_{label}_{suffix}',sh.translate(tuple(-x for x in bb[:3])),origin=bb[:3],pn=f'X_STOP_{label}_{suffix}',
                group='motion_stops',material=mat,
                notes=['Hard contact atheadX168/982. Normal soft travel175..975; home trip173 adjusted atlow speed.',
                       'Block20×45×26,2×Ø6.6 through45. Buffer screw threads:M4×0.7 depth10,Ø3.3 pilot11 frominner side.',
                       'Left switch bracket holes:Ø2.5 pilot,TAP M3×0.5 through3;switch screw torque0.39–0.59 N·m.'])
    # Home cam attached to front of X carriage, clear of the Z module.
    cx=head_x-130;front_y=face_y-42.7
    poly=[(0,1297),(10,1290.7),(30,1290.7),(30,1299),(0,1299)]
    cam=cq.Workplane('XZ',origin=(cx,front_y,0)).polyline(poly).close().extrude(20).val()
    cam=cam.fuse(box(30,3,20).translate((cx,front_y-3,1270.7))).clean()
    for j,dx in enumerate((8,23),1):
        gx=cx+dx;gz=1280.7
        cam=cam.cut(place(cyl(4.5,5),(gx,front_y+1,gz),u=(1,0,0),v=(0,0,1))).clean()
        p=m.find('Z_CARRIER');tap=place(cyl(4,8),(gx,front_y,gz),u=(1,0,0),v=(0,0,-1));p.shape=p.shape.cut(tap).clean()
        p.local=p.local.cut(cyl(4,8).translate((dx,gz-1143,4.7))).clean()
        p.flat.setdefault('operations',[]).append({'type':'circle','x':dx,'y':gz-1143,'diameter':3.3,'layer':'DRILL_CAM_M4_PILOT_DEPTH_9'})
        p.flat.setdefault('machining_notes',[]).append('X home cam:Ø3.3 pilot9 deep,TAP M4×0.7 depth8 fromfront face;M4×10 engagement7.')
        cb=place(cyl(8,2.2),(gx,front_y-3,gz),u=(1,0,0),v=(0,0,-1));cam=cam.cut(cb).clean()
        m.add(f'X_HOME_CAM_BOLT_{j}',socket(4,8,7.6,2.2),origin=(gx,front_y+7.2,gz),u=(1,0,0),v=(0,0,1),
              pn='ISO7380_M4x8_BUTTON',group='motion_fasteners',material='M4×8 button-head screw7.6×2.2',purchased=True,color=HARDWARE,
              notes=['Cam web counterboreØ8×2.2 deep leaves0.8 mm;7.2 mm thread engagement. Cam carries only microswitch operating force.'])
    bb=bbox(cam);m.add('X_HOME_CAM',cam.translate(tuple(-v for v in bb[:3])),origin=bb[:3],pn='X_HOME_CAM',
        group='motion_stops',material='A36 steel machined cam',notes=['30×20 ramp cam,10 mm ramp followed by20 mm land. TwoØ4.5 attachment holes.'])

def hgr(m,ident,length,origin,u,v):
    # Railway end-hole pattern is deliberately not inferred from contradictory
    # P40/E20/1500 seller drawing. Factory holes transfer to custom datum bars.
    return envelope(m,ident,box(length,20,17.5),origin,u=u,v=v,
        pn='PURCHASED_HGR20_'+str(length),material='iMetrx steel guide rail',
        notes=['Sourced section: width20, height17.5. Hole D9.5 counterbore8.5 deep, through6.',
               'Factory hole pitch and end datum HOLD: drawing P40/E20 does not close on1500. No invented rail screw coordinates.',
               'Cut Y rail to1420 using abrasive-rated process, deburr; verify usable factory end holes before final cut.'])

def hgh(m,ident,origin,u,v):
    # Local X along rail, Y across rail, Z outward from rail mounting plane.
    # Relief removes the conservative rail envelope; actual raceway contacts
    # are internal purchased geometry, not fabricated from this representation.
    s=box(77.5,44,30).cut(box(79.5,20,17.5).translate((-1,12,0))).clean()
    holes=[(x,y,5) for x in (20.75,56.75) for y in (6,38)]
    s=s.cut(cq.Compound.makeCompound([cyl(5,6).translate((x,y,24)) for x,y,_ in holes])).clean()
    return envelope(m,ident,s,origin,u=u,v=v,pn='PURCHASED_HGH20CA',
        material='iMetrx HGH20CA block',notes=['Published77.5×44×30 envelope; output4×M5 depth6, along36×across32.',
        'Envelope omits bearing internals and seals. Source rating is iMetrx, not a HIWIN certification.'])

def hms(m,ident,stroke,body_origin,along,across,carriage_center,shoe_t=6.35):
    """Module datum at nonmotor end, with along pointing toward inline motor."""
    length=stroke+125
    # End-cap max envelope is carried through body, with carriage top separate.
    # This deliberately overstates body volume. It is never used for mass.
    body=envelope(m,ident+'_BODY',box(length,42,60),body_origin,u=along,v=across,
        pn=f'PURCHASED_HMS40_{stroke}',material='KHMOS HMS40 drive-only module',
        notes=['Published body length S+125, end section42×60. Internal voids/rails not represented.',
               'Selected screw lead10 mm. Assembly endpoint datum and base nut cavity require supplier confirmation.'])
    mot_org=tuple(body_origin[k]+along[k]*(stroke+145)+across[k]*(21-28.5) for k in range(3))
    envelope(m,ident+'_MOTOR',box(56,57,57),mot_org,u=along,v=across,
        pn='HMS40_M57_MOTOR',material='HMS40 inline57×56 stepper motor',
        notes=['Motor current/torque-speed/cable outlet not published in the recovered drawing.'])
    bracket_org=tuple(body_origin[k]+along[k]*length+across[k]*(21-30) for k in range(3))
    envelope(m,ident+'_MOTOR_BRACKET',box(20,60,75),bracket_org,u=along,v=across,
        pn='HMS40_MOTOR_BRACKET',material='KHMOS bracket clearance envelope',
        notes=['75 mm maximum bracket height; connector clearance remains HOLD.'])
    normal=cq.Vector(*along).cross(cq.Vector(*across)).toTuple()
    co=tuple(body_origin[k]+along[k]*(carriage_center-32.5)+across[k]*(-3)+normal[k]*60 for k in range(3))
    cart=box(65,48,5.5)
    holes=[(x,y,4) for x in (16,46) for y in (9,39)]
    cart=cart.cut(cq.Compound.makeCompound([cyl(4,7).translate((x,y,-1)) for x,y,_ in holes])).clean()
    carriage=envelope(m,ident+'_CARRIAGE_TOP',cart,co,u=along,v=across,
        pn='HMS40_CARRIAGE_INTERFACE',material='KHMOS sourced top mating envelope',
        notes=['Output plane65.5 above base. Published4×M4 depth10 at30×30; along offsets16/46, transverse9/39.',
               'Only exposed envelope above body max is separate; not a 5.5 mm actual carriage thickness.'])
    shoe_origin=tuple(co[k]+normal[k]*5.5 for k in range(3))
    shoe=plate(rect(65,48),shoe_t,[(x,y,4.5) for x,y,_ in holes])
    shoe=shoe.cut(cq.Compound.makeCompound([cyl(4,shoe_t+2).translate((32.5,y,-1)) for y in(5,43)])).clean()
    shoe=shoe.cut(cq.Compound.makeCompound([cyl(8,shoe_t-2).translate((x,y,2)) for x,y,_ in holes])).clean()
    sh=m.add(ident+'_SHOE',shoe,origin=shoe_origin,u=along,v=across,pn='HMS40_DRIVE_SHOE_'+str(shoe_t).replace('.','p'),
        group='motion_adapters',material='6061-T6 aluminum '+str(shoe_t),
        flat={'outline':rect(65,48),'thickness_mm':shoe_t,'holes':[(x,y,4.5) for x,y,_ in holes]+[(32.5,y,3.3) for y in(5,43)],'slots':[],'internal':[],
              'operations':[{'type':'circle','x':x,'y':y,'diameter':8,'layer':'MILL_COUNTERBORE_DEPTH_'+str(shoe_t-2).replace('.','p')} for x,y,_ in holes],
              'machining_notes':[f'Four counterbores diameter8, depth{shoe_t-2:g} from top face. Remaining web2.00. M4x10 engagement8 mm in sourced purchased threads.',
                                 'TwoØ3.3 pilot holes at(32.5,5)/(32.5,43):TAP M4×0.7 THROUGH for clevis mounts;6 mm minimum thread engagement.']},
        notes=[f'4×Ø4.5 through, Ø8 counterbore{shoe_t-2:g} deep. M4×10 seats on2 mm web,8 mm thread engagement.',
               'Drive-only shoe; do not transfer router overturning moment through HMS40.'])
    for i,(x,y,_) in enumerate(holes,1):
        bo=tuple(shoe_origin[k]+along[k]*x+across[k]*y-normal[k]*8 for k in range(3))
        b=bolt(m,ident+f'_SHOE_BOLT_{i}',4,10,bo,along,across)
        # Thread engagement enters the conservative main-body envelope as the
        # actual module carriage extends below its exposed top cap.
        m.permit(b.id,body.id,'Published M4 carriage thread lies inside the conservative purchased module body envelope.')
    return {'body':body.id,'shoe':sh.id,'shoe_top':tuple(shoe_origin[k]+normal[k]*shoe_t for k in range(3))}

def clevis_link(m,prefix,a,b):
    """SKF SA6C/SAL6C pair, custom RH/LH coupler and shoulder-bolt clevises."""
    direction=(cq.Vector(*b)-cq.Vector(*a));L=direction.Length;assert abs(L-80)<.001
    u=direction.normalized().toTuple();v=(-u[1],u[0],0)
    for label,point,sgn in [('A',a,1),('B',b,-1)]:
        # Lower foot40×48 accepts two M4 screws outside the22 mm eye.
        # Upper ear and integral back wall are machined from one billet.
        lower=box(40,48,6)
        ear1=box(28,6,26).translate((6,14.5,6))
        ear2=box(28,6,26).translate((6,27.5,6))
        clevis=lower.fuse(ear1).fuse(ear2).clean()
        clevis=clevis.cut(place(cyl(6,21),(20,13.5,19),u=(0,0,1),v=(1,0,0))).clean()
        for yy in(5,43):clevis=clevis.cut(cyl(4.5,8).translate((20,yy,-1))).clean()
        org=tuple(point[k]-u[k]*20-v[k]*24+(0,0,-19)[k] for k in range(3))
        m.add(prefix+f'_{label}_CLEVIS',clevis,origin=org,u=u,v=v,pn='MOTION_CLEVIS_BILLET',
            group='motion_links',material='6061-T6 machined billet40×48×32',
            notes=['Mill7 mm gap between6 mm side ears. Pin axis19 mm above mounting sole. Ream common pin bore6H7 through both ears in one setup.',
                   'TwoØ4.5 base holes at(20,5)/(20,43); mount withM4×12 into6 mm minimum M4×0.7 engagement.'])
        shoulder=cyl(6,20).fuse(cyl(10,5).translate((0,0,20))).fuse(cyl(5,10).translate((0,0,-10))).clean()
        pinorg=tuple(point[k]-v[k]*9.5 for k in range(3))
        m.add(prefix+f'_{label}_PIN',shoulder,origin=pinorg,u=(0,0,1),v=u,
            pn='ISO7379_D6_L20_M5',group='motion_fasteners',material='ISO7379 shoulder screw6×20,M5',purchased=True,color=HARDWARE,
            notes=['Smooth6 mm shoulder crosses both ears and inner race. M5 prevailing-torque nut retains; do not run threaded shank in bearing.'])
        for j,dd in enumerate((-3.5,3),1):
            po=tuple(point[k]+v[k]*dd for k in range(3))
            m.add(prefix+f'_{label}_RACE_SPACER_{j}',pipe(.5,10,6.1),origin=po,u=(0,0,1),v=u,
                pn='SHIM_6p1x10x0p5',group='motion_fasteners',material='Hardened bearing spacer',purchased=True,color=HARDWARE)
        m.add(prefix+f'_{label}_TOP_WASHER',pipe(1,12,6.4),origin=tuple(point[k]+v[k]*9.5 for k in range(3)),u=(0,0,1),v=u,
            pn='WASHER_6p4x12x1',group='motion_fasteners',material='Hardened steel washer',purchased=True,color=HARDWARE)
        m.add(prefix+f'_{label}_NUT_WASHER',pipe(1,10,5.3),origin=tuple(point[k]-v[k]*10.5 for k in range(3)),u=(0,0,1),v=u,
            pn='WASHER_5p3x10x1',group='motion_fasteners',material='Steel washer',purchased=True,color=HARDWARE)
        m.add(prefix+f'_{label}_LOCKNUT',hexring(8,5,5),origin=tuple(point[k]-v[k]*15.5 for k in range(3)),u=(0,0,1),v=u,
            pn='M5_PREVAILING_NUT',group='motion_fasteners',material='M5 prevailing torque locknut',purchased=True,color=HARDWARE)
        for j,yy in enumerate((-19,19),1):
            p=(point[0]+v[0]*yy,point[1]+v[1]*yy,point[2]-25)
            bolt(m,prefix+f'_{label}_MOUNT_{j}',4,12,p)
        direction=tuple(sgn*x for x in u)
        shaft=cq.Workplane(cq.Plane(origin=tuple(point[k]+direction[k]*10 for k in range(3)),normal=direction)).circle(3).extrude(26).val()
        rod=place(pipe(6,22,6),tuple(point[k]-v[k]*3 for k in range(3)),u=(0,0,1),v=u)
        bb=bbox(rod)
        envelope(m,prefix+f'_{label}_ROD_END',rod.translate(tuple(-x for x in bb[:3])),bb[:3],
            pn='SKF_SA6C' if label=='A' else'SKF_SAL6C',material='SKF steel/PTFE spherical rod end',
            notes=['SKF SA6C RH /SAL6C LH, bore6, eye22 maximum, inner width6, center-to-thread-end36, M6×1, thread16.',
                   'SKF catalog dynamic3.6 kN/static8.15 kN and13 degree tilt. Design thrust250 N; rating ratio14.4 dynamic before fatigue/application factors.'])
        bb=bbox(shaft)
        envelope(m,prefix+f'_{label}_ROD_SHANK',shaft.translate(tuple(-x for x in bb[:3])),bb[:3],
            pn='INCLUDED_SKF_ROD_END_SHANK',material='Included shank envelope; NOT a separate purchased item',
            notes=['Clearance representation split from rod-end head to avoid Boolean tangency artifacts; included in SKF SA6C/SAL6C assembly.'])
        m.permit(prefix+f'_{label}_ROD_END',prefix+f'_{label}_ROD_SHANK','Overlapping conservative head/shank envelopes describe one purchased SKF rod end, not two fabricated bodies.')
    axis_u=(0,0,1);axis_v=v
    # axis_u×axis_v points opposite u; use explicit plane for axial sections.
    cp=tuple(a[k]+u[k]*26 for k in range(3))
    plane=cq.Plane(origin=cp,xDir=(0,0,1),normal=u)
    coupler=hexring(12,28,6).moved(plane.location)
    bb=bbox(coupler)
    m.add(prefix+'_COUPLER',coupler.translate(tuple(-x for x in bb[:3])),origin=bb[:3],pn='LINK_COUPLER_M6_RHLH_28',
        group='motion_links',material='1215 steel12AF hex,28 long',
        notes=['DrillØ5 through. TapM6×1 RH fromone end andLH fromother end, each12 deep. MarkLH end withcircumferential groove.',
               'Set80 mm eye centers:10 mm thread engagement each end,8 mm internalgap. Never reduce engagement below9 mm.'])
    for label,dist in [('RH',21),('LH',54)]:
        p=tuple(a[k]+u[k]*dist for k in range(3));sh=hexring(10,5,6).moved(cq.Plane(origin=p,xDir=(0,0,1),normal=u).location);bb=bbox(sh)
        m.add(prefix+'_JAM_'+label,sh.translate(tuple(-x for x in bb[:3])),origin=bb[:3],pn='M6_'+label+'_JAM_NUT',
            group='motion_fasteners',material='M6×1 '+label+' steel jamnut10AF×5',purchased=True,color=HARDWARE,
            notes=['Hold coupler while tightening both jamnuts. Witness-mark after homing/squaring.'])

def make_motion(m,gantry_y=1275.0,head_x=575.0,z_lift=100.0,tool='router'):
    assert 275<=gantry_y<=1275 and 175<=head_x<=975 and 0<=z_lift<=100
    beam_y=gantry_y+80
    # Side rail bars weld to inside faces of the upper2in chassis rails.
    for side,left in [('L',True),('R',False)]:
        bx=50.8 if left else 1091.2
        m.add('Y_DATUM_'+side,box(8,1450,45),origin=(bx,0,1010.5),pn='Y_DATUM_BAR',
            group='motion_datums',material='Machined steel8×45 bar',length=1450,
            release=HOLD,notes=['Weld to upper chassis inner face before finish-machining. Rail seat flatness target0.05/1000; parallelism target0.05 overtravel.',
            'Rail fastening holes are transfer-drilled from actual purchased rail; hole locations remain a supplier hold. Do not flame-cut the rail seat.'])
        rail_origin=(58.8,15,1023) if left else (1091.2,15,1043)
        rail_u=(0,1,0);rail_v=(0,0,1) if left else (0,0,-1)
        hgr(m,'Y_RAIL_'+side,1420,rail_origin,rail_u,rail_v)
        output_x=88.8 if left else 1061.2
        shoe_x=88.8 if left else 1048.5
        # Local plate X is Y travel; local Y is vertical. Plate normal points+X.
        holes=[(140+dy+dx,zz-1011,5.5) for dy in(-90,90) for dx in(-18,18) for zz in(1017,1049)]
        # Beam end shoe bolts: y at beam center±25, top down24/54.
        for yy in(beam_y-25,beam_y+25):
            holes.extend([(yy-(gantry_y-140),1142.3-1011-dz,6.6) for dz in(24,54)])
        m.add_plate('Y_SHOE_'+side,280,131.3,12.7,holes=holes,origin=(shoe_x,gantry_y-140,1011),
            u=(0,1,0),v=(0,0,1),pn='Y_SHOE_'+side,group='motion_adapters',material='6061-T6 aluminum12.7',
            notes=['Loweredge1011 clears in-footprint beam transfer. EightM5 screws connect two guide blocks;4M6 connect end-foot bracket.',
                   'Y block centers180 apart. Raised gantry beam center80 mm behind Y guide midpoint.'])
        for bi,cy in enumerate((gantry_y-90,gantry_y+90),1):
            org=(58.8,cy-38.75,1011) if left else (1091.2,cy-38.75,1055)
            hgh(m,f'Y_BLOCK_{side}_{bi}',org,rail_u,rail_v)
            for j,(yy,zz) in enumerate([(cy+dy,zz) for dy in(-18,18) for zz in(1017,1049)],1):
                # Bolt head lies inside;18 mm under-head gives5.3 mm engagement.
                normal=1 if left else-1
                start=output_x-normal*5.3
                bolt(m,f'Y_BLOCK_BOLT_{side}_{bi}_{j}',5,18,(start,yy,zz),
                     u=(0,1,0),v=(0,0,normal))
        # An integral machined end bracket transfers the beam into the side shoe.
        # Horizontal flange spans both underside slots, vertical web beside shoe.
        x0=-25 if left else 1025
        flange_x=(25,100) if left else (50,125)
        flange=plate(rect(150,80),12.7,[(xx,yy,8.5) for xx in flange_x for yy in(20,60)])
        flange=flange.cut(cq.Compound.makeCompound([cyl(13.5,8).translate((xx,yy,0)) for xx in flange_x for yy in(20,60)])).clean()
        web=box(12.7,80,70).translate(((126.5 if left else 10.8),0,-70))
        part=flange.fuse(web).clean()
        for yy in(15,65):
            for zz in(-24,-54):
                toolhole=place(cyl(6,15),(x0+(126.5 if left else 10.8)-1,beam_y-40+yy,1142.3+zz),u=(0,1,0),v=(0,0,1))
                part=part.cut(toolhole.translate((-x0,-(beam_y-40),-1142.3))).clean()
        m.add('GANTRY_END_BRACKET_'+side,part,origin=(x0,beam_y-40,1142.3),
            pn='GANTRY_END_BRACKET_'+side,group='motion_adapters',material='6061-T6 machined billet',
            notes=['Integral12.7 thick horizontal flange and70 mm downstand. No welded aluminum joint.',
                   '4M8 underside T-slot fasteners. FourM6 threaded downstand holes,5.0 pilot; thread representation nominal.'])
        for j,(yy,zz) in enumerate([(yy,1142.3-dz) for yy in(beam_y-25,beam_y+25) for dz in(24,54)],1):
            normal=1 if left else-1
            # Screws pass the12.7 side shoe and engage9.3 into bracket web.
            start=(110.8 if left else 1039.2)
            b=bolt(m,f'GANTRY_WEB_BOLT_{side}_{j}',6,22,(start,yy,zz),u=(0,1,0),v=(0,0,-normal))
        # Y module sits on raised rail cap, centered over the chassis tube.
        center_x=25.4 if left else 1124.6
        # u=+Y, v=-X yields up; base across42 centered on tube.
        r=hms(m,'HMS_Y_'+side,1000,(center_x-21,1220,CAP_TOP),(0,-1,0),(1,0,0),1220-(gantry_y-117))
        # Link support is on the inner shoe; it has a relieved approach to the module.
        wx=6.4 if left else 1040.5;ww=103.1;webx=101.5 if left else 1040.5
        wz=CAP_TOP+65.5
        support=box(ww,32,6.35).fuse(box(8,32,40).translate((webx-wx,0,-40))).clean()
        # Horizontal cantilever passes a clearance window in the Y side plate.
        window=box(15,33,7.35)
        cut_world(m,'Y_SHOE_'+side,window.translate((shoe_x-1,gantry_y-53.5,wz-.5)),
                  '33×7.35 clearance window for thrust-link flange,0.5 mm all-round clearance.')
        sp=m.find('Y_SHOE_'+side)
        local_window=rect(33,7.35)
        wxlocal=86.5;wzlocal=wz-.5-1011
        poly=[(x+wxlocal,z+wzlocal) for x,z in local_window]
        sp.flat['internal'].append(poly)
        sp.local=sp.local.cut(plate(poly,15).translate((0,0,-1))).clean()
        for xx in(center_x-19,center_x+19):support=support.cut(cyl(4,8).translate((xx-wx,16,-1))).clean()
        for yy in(8,24):
            for dz in(10,28):
                toolhole=place(cyl(6,10),(webx-wx-1,yy,-dz),u=(0,1,0),v=(0,0,1))
                support=support.cut(toolhole).clean()
                gy=gantry_y-53+yy;gz=wz-dz
                hole=place(cyl(6.6,15),(shoe_x-1,gy,gz),u=(0,1,0),v=(0,0,1))
                cut_world(m,'Y_SHOE_'+side,hole,'Additional fourØ6.6 link-bracket mounting holes; see3D and matching flat coordinates.')
                sp=m.find('Y_SHOE_'+side)
                sp.local=sp.local.cut(cyl(6.6,15).translate((gy-(gantry_y-140),gz-1011,-1))).clean()
                sp.flat['holes'].append((gy-(gantry_y-140),gz-1011,6.6))
                start=108.8 if left else 1041.2
                bolt(m,f'Y_LINK_BRACKET_{side}_{yy}_{dz}',6,20,(start,gy,gz),u=(0,1,0),v=(0,0,-1 if left else 1))
        m.add('Y_LINK_SUPPORT_'+side,support,origin=(wx,gantry_y-53,wz),pn='Y_LINK_SUPPORT_'+side,
            group='motion_links',material='6061-T6 machined integral bracket',
            notes=['103.1×32×6.35 horizontal flange with8×32×40 downstand. FourØ5.0 pilot holes cross downstand; tapM6×1 through8 mm.',
                   'TwoØ3.3 pilots on horizontal flange:tapM4×0.7 through. M4×12 clevis screws engage6 mm. FourM6×20 shoe screws engage7.3 mm.'])
        clevis_link(m,'Y_LINK_'+side,(center_x,gantry_y-117,1154.7875),(center_x,gantry_y-37,1154.7875))

    # Beam outer envelope is used for collisions only. Published Ix rather than
    # fictitious solid-bar inertia is used by the independent stiffness check.
    beam=envelope(m,'GANTRY_8080',box(1200,80,80),(-25,beam_y-40,GANTRY_BOTTOM),
        pn='8020_40-8080_1200',material='80/20 40-8080 aluminum purchased profile',
        notes=['Actual profile1200×80×80, eight slots at20/60 face offsets. Outer clearance envelope; cavities/T-slots omitted.',
               'Manufacturer Ix=Iy171.6341 cm4, mass6.428 kg/m; do not use envelope volume for mass or inertia.'])
    for side,x0 in [('L',-25),('R',1025)]:
        flange_x=(25,100) if side=='L' else (50,125)
        for j,(x,y) in enumerate([(x0+xx,beam_y+dy) for xx in flange_x for dy in(-20,20)],1):
            b=bolt(m,f'GANTRY_UNDERSIDE_BOLT_{side}_{j}',8,16,(x,y,1166.3),u=(1,0,0),v=(0,-1,0))
            m.permit(b.id,beam.id,'Fastener enters omitted purchased T-slot cavity; M8×16 projects11.3 mm past beam face.')
            nut=envelope(m,f'GANTRY_TNUT_{side}_{j}',plate(rect(22,13.7),5.9,[(11,6.85,8)]),
                (x-11,y-6.85,1159.32),pn='8020_40-3915_M8_TNUT',material='80/20 40-3915 M8×1.25 T-nut',
                notes=['Manufacturer22×13.7×5.9 maximum rectangular envelope; body seating4.32 mm below profile face.',
                       'M8×16 projects11.3 mm:5.9 mm nut fully engaged,1.08 mm tail projection; nominal root clearance3.55 mm.'])
            m.permit(nut.id,beam.id,'Selected T-nut sits inside the omitted purchased T-slot cavity.')
    face_y=beam_y-52.7
    face_z=1143.0
    faceholes=[(xx,zz,8.5) for xx in(75,375,675,1125) for zz in(32,72)]
    face=m.add_plate('X_GUIDE_FACE',1200,112,12.7,holes=faceholes,
        origin=(-25,beam_y-40,face_z),u=(1,0,0),v=(0,0,1),pn='X_GUIDE_FACE',
        group='motion_datums',material='6061-T6 aluminum12.7',release=HOLD,
        notes=['M8 beam-slot attachment coordinates are defined; HGR20 factory holes must be transferred after the actual rail pattern is confirmed.',
               'Face spansZ1143..1255; rails centeredZ1165/1225. Mill both rail seats coplanar0.03 before assembling.'])
    face.local=face.local.cut(cq.Compound.makeCompound([cyl(13.5,8).translate((xx,zz,4.7)) for xx,zz,_ in faceholes])).clean()
    face.shape=place(face.local,(-25,beam_y-40,face_z),(1,0,0),(0,0,1))
    face.flat['operations']=[{'type':'circle','x':xx,'y':zz,'diameter':13.5,'layer':'MILL_COUNTERBORE_DEPTH_8'} for xx,zz,_ in faceholes]
    face.flat['machining_notes']=['Eight diameter13.5 counterbores8 deep from front face. Diameter8.5 through. M8x16 into80/20 40-3915 T-nuts; screw projects11.3 mm past beam face.']
    for j,(xx,zz,_) in enumerate(faceholes,1):
        b=bolt(m,'X_FACE_BOLT_'+str(j),8,16,(-25+xx,beam_y-28.7,face_z+zz),u=(1,0,0),v=(0,0,1))
        m.permit(b.id,beam.id,'M8 thread enters omitted T-slot and nut of the purchased beam envelope.')
        nut=envelope(m,'X_FACE_TNUT_'+str(j),plate(rect(22,13.7),5.9,[(11,6.85,8)]),
            (-25+xx-11,beam_y-35.68,face_z+zz+6.85),u=(1,0,0),v=(0,0,-1),
            pn='8020_40-3915_M8_TNUT',material='80/20 40-3915 M8×1.25 T-nut',
            notes=['Selected manufacturer T-nut. 5.9 mm engagement,1.08 mm screw projection beyond nut.'])
        m.permit(nut.id,beam.id,'Selected T-nut sits inside the omitted purchased T-slot cavity.')
    head_y=face_y-30
    head_z=1143.0
    head_top=GANTRY_BOTTOM+80+65.5+12.7
    headholes=[]
    for ri,cz in enumerate((1165,1225),1):
        hgr(m,'X_RAIL_'+str(ri),1200,(-25,face_y,cz-10),(1,0,0),(0,0,1))
        for bi,cx in enumerate((head_x-80,head_x+80),1):
            hgh(m,f'X_BLOCK_{ri}_{bi}',(cx-38.75,face_y,cz-22),(1,0,0),(0,0,1))
            for j,(xx,zz) in enumerate([(cx+dx,cz+dz) for dx in(-18,18) for dz in(-16,16)],1):
                headholes.append((xx-(head_x-130),zz-head_z,5.5))
                bolt(m,f'X_BLOCK_BOLT_{ri}_{bi}_{j}',5,18,(xx,head_y+5.3,zz),u=(1,0,0),v=(0,0,1))
    m.add_plate('Z_CARRIER',260,head_top-head_z,12.7,holes=headholes,
        origin=(head_x-130,head_y,head_z),u=(1,0,0),v=(0,0,1),pn='Z_CARRIER',
        group='motion_adapters',material='6061-T6 aluminum12.7',release=HOLD,
        notes=['16M5 connect four X guide blocks. Z module fixing holes are NOT invented: bottom slot coordinates/engagement and complete output-height drawing remain HOLD.',
               'The Z module base mounting must be positively fastened before machining or commissioning.'])
    hms(m,'HMS_X',800,(40,beam_y-21,GANTRY_BOTTOM+80),(1,0,0),(0,1,0),head_x-80-40,shoe_t=19.05)
    outline=[(0,0),(156,0),(156,30),(96,30),(96,120.8),(60,120.8),(60,30),(0,30)]
    xsupport=plate(outline,6.35).fuse(box(156,8,30).translate((0,12.7,-30))).clean()
    for yy in(76.4,114.4):xsupport=xsupport.cut(cyl(4,8).translate((78,yy,-1))).clean()
    for xx in(18,138):
        for zz in(-12,-28):
            hole=place(cyl(6,10),(xx,11.7,zz),u=(1,0,0),v=(0,0,-1))
            xsupport=xsupport.cut(hole).clean()
            gx=head_x-78+xx;gz=head_top+zz
            hole=place(cyl(6.6,15),(gx,head_y+1,gz),u=(1,0,0),v=(0,0,1))
            cut_world(m,'Z_CARRIER',hole,'Four additionalØ6.6 link-bridge mounting holes; matching flat coordinates included.')
            sp=m.find('Z_CARRIER');sp.local=sp.local.cut(cyl(6.6,15).translate((gx-(head_x-130),gz-head_z,-1))).clean()
            sp.flat['holes'].append((gx-(head_x-130),gz-head_z,6.6))
            bolt(m,f'X_LINK_BRIDGE_BOLT_{xx}_{zz}',6,20,(gx,head_y+7.3,gz),u=(1,0,0),v=(0,0,1))
    m.add('X_LINK_SUPPORT',xsupport,origin=(head_x-78,head_y-12.7,head_top),
        pn='X_LINK_SUPPORT',group='motion_links',material='6061-T6 machined integral bracket',
        notes=['156 mm front flange narrows to36 mm at rear;120.8 projection,6.35 thick. Integral156×8×30 downstand. FourØ5 pilots cross downstand;tapM6×1 through8.',
               'TwoØ3.3 upper pilots:tapM4×0.7 through6.35. Bridge transfers thrust to X carrier with4M6×20,7.3 mm engagement.'])
    clevis_link(m,'X_LINK',(head_x-80,beam_y,head_top+25.35),(head_x,beam_y,head_top+25.35))

    # Z supplier mounting stack is deliberately a bounded placement assumption,
    # visibly guarded. There is no fake output hole pattern or fake brake.
    zbase_y=head_y-12.7
    envelope(m,'ZBX80_BASE',box(80,20,219),(head_x-40,zbase_y-20,1040),
        pn='RATTMOTOR_ZBX80_100',material='RATTMMOTOR ZBX80 base envelope',
        notes=['Owner-supplied listing drawing (25 Sep 2026): body 219 long x 80 wide with 12 mm end blocks, 330 overall including the NEMA23 (57 sq) motor; matches this envelope.',
               'Exact base-slot fastening interface remains HOLD; base fastening is measure-on-receipt.'])
    for label,z,height in [('BOTTOM',1040,67),('TOP',1247,78)]:
        envelope(m,'ZBX80_END_'+label,box(80,height,12),(head_x-40,zbase_y-height,z),
            pn='ZBX80_END_'+label,material='ZBX80 sourced endplate envelope')
        m.permit('ZBX80_END_'+label,'ZBX80_BASE','Purchased module endplate and extrusion represented with overlapping external envelopes, not separate material solids.')
    envelope(m,'ZBX80_MOTOR',box(57,57,56),(head_x-28.5,zbase_y-67,1314),
        pn='ZBX80_MOTOR',material='ZBX80 stepper motor envelope',
        notes=['57×57×56 motor; intervening coupling/bracket clearance reserved. Motor cable outlet HOLD.'])
    envelope(m,'ZBX80_COUPLER_GUARD',box(80,78,55),(head_x-40,zbase_y-78,1259),
        pn='ZBX80_UPPER_CLEARANCE',material='ZBX80 motor bracket/coupler clearance envelope',
        notes=['330 mm full module envelope fromZ1040 to1370. Connector projection not included.'])
    out_z=1080+z_lift
    output_y=zbase_y-80
    envelope(m,'ZBX80_OUTPUT_HOLD',box(90,35,50),(head_x-45,output_y,out_z),
        pn='ZBX80_OUTPUT_INTERFACE_HOLD',material='ZBX80 partial sourced carriage envelope',
        notes=['Exact-ASIN seller top view: carriage plate90 across x50 along travel; the70 mm transverse dimension connects the smallerØ5 holes. Gallery8 identifies four small output fixing holes. The largerØ7 bores are not established as usable tool-mount holes.',
               'Along-travel hole pitch, tapped-vs-through, and the mounting-plane-to-output height are NOT dimensioned in that drawing: the adapter uses vertical slots and the 80 mm output stack stays an assumption until the unit is measured.'])
    adapter=m.add_plate('TOOL_ADAPTER_110',110,110,12.7,
        slots=[(20,45,30,7,90),(90,45,30,7,90)],origin=(head_x-55,output_y,out_z-10),
        u=(1,0,0),v=(0,0,1),pn='TOOL_ADAPTER_110',group='removable_tool',
        material='6061-T6 aluminum12.7',release='PROVISIONAL - INDIVIDUAL EXPORT GUARDED UNTIL CARRIAGE DRAWING',
        notes=['Provisional adapter: two vertical 7 x 30 slots on 70 mm transverse centers. Their approximately24 mm center travel for a6 mm shank does not verify carriage hole spacing, bolt count or a15-45 mm longitudinal pitch.',
               'Front-face11 x30 counter-slots,6.6 deep, are provisional geometry; the actual carriage screw/head/washer stack remains unselected.',
               'No carriage fasteners are modeled: the listing identifies fourØ5 fixing holes but omits their thread and along-travel spacing. The former two M6 x16 candidates have been removed. A trueØ7 plain bore cannot be tappedM6.',
               'Interface load path and fastening capacity remain HOLD. Do not manufacture this adapter or select its carriage fasteners from this model.',
               'Shared spindle/torch clamp pattern: four Ø6.6 at X±45, Z+12/+38 from the output datum, Ø10.5 counterbore 6 deep on the carriage-side face.'])
    cslot=cq.Compound.makeCompound([cq.Workplane('XY').center(sx,45).slot2D(30,11,90).extrude(7.6).translate((0,0,6.1)).val() for sx in (20,90)])
    adapter.local=adapter.local.cut(cslot).clean()
    adapter.shape=place(adapter.local,(head_x-55,output_y,out_z-10),(1,0,0),(0,0,1))
    adapter.flat.setdefault('operations',[]).extend({'type':'slot','x':sx,'y':45,'length':30,'width':11,'angle':90,'depth_mm':6.6,'face':'front','layer':'MILL_FRONT_COUNTERSLOT_DEPTH_6_6'} for sx in (20,90))
    adapter.flat.setdefault('machining_notes',[]).append('PROVISIONAL: front-face counter-slots11 wide x6.6 deep; dimensions match the STEP but actual carriage fastening is unresolved. Individual fabrication export is guarded.')
    if tool=='router':
        # This full259 mm envelope prevents the earlier180 mm spindle error.
        spindle_y=output_y-12.7-45.5
        envelope(m,'TOOL_SPINDLE_65x259',cyl(65,259),(head_x,spindle_y,960+z_lift),
            pn='SPINDLE_B0BF5R3LNC',group='removable_tool',material='1.5 kW110V ER11 air-cooled spindle',
            notes=['Exact selected diameter65, overall259, mass2.7 kg. Router tip/body reference here is a clearance assumption pending collet/tool drawing.',
                   'Custom split clamp is defined independently of the supplied kit clamp. Only Z-output adapter remains guarded. Remove entire tool before bed swap.'])
        # Custom two-piece clamp replaces the unspecified supplied clamp holes.
        # Both halves are finish-bored together with a0.50 mm split shim.
        clamp_back=output_y-12.7
        bore=cyl(65,42).translate((head_x,spindle_y,out_z+4))
        rear=box(110,45.25,40).translate((head_x-55,clamp_back-45.25,out_z+5)).cut(bore).clean()
        front=box(110,44.75,40).translate((head_x-55,clamp_back-90.5,out_z+5)).cut(bore).clean()
        for x in(head_x-45,head_x+45):
            for z in(out_z+12,out_z+38):
                tap=place(cyl(6,15),(x,clamp_back,z),u=(1,0,0),v=(0,0,1))
                rear=rear.cut(tap).clean()
                adapter_hole=place(cyl(6.6,15),(x,output_y+1,z),u=(1,0,0),v=(0,0,1))
                cut_world(m,'TOOL_ADAPTER_110',adapter_hole,'FourØ6.6 through holes for the shared spindle/torch clamp, atX±45/Z+12,+38 relative to output datum, outboard of the carriage slots.')
                ip=m.find('TOOL_ADAPTER_110')
                ip.local=ip.local.cut(cyl(6.6,15).translate((x-(head_x-55),z-(out_z-10),-1))).clean()
                ip.flat['holes'].append((x-(head_x-55),z-(out_z-10),6.6))
                cb=place(cyl(10.5,6),(x,output_y,z),u=(1,0,0),v=(0,0,1))
                cut_world(m,'TOOL_ADAPTER_110',cb,'Ø10.5 counterbore6 deep from rear/output mating face, keeping heads flush.')
                ip.local=ip.local.cut(cyl(10.5,6).translate((x-(head_x-55),z-(out_z-10),0))).clean()
                ip.flat.setdefault('operations',[]).append({'type':'circle','x':x-(head_x-55),'y':z-(out_z-10),'diameter':10.5,'layer':'MILL_REAR_COUNTERBORE_DEPTH_6'})
                bo=bolt(m,f'TOOL_CLAMP_MOUNT_{int(x-head_x)}_{int(z-out_z)}',6,20,(x,output_y-26,z),u=(1,0,0),v=(0,0,-1))
                bo.group='removable_tool'
        for j,x in enumerate((head_x-47,head_x+47),1):
            z=out_z+25
            rear=rear.cut(place(cyl(6,15),(x,clamp_back-45.25,z),u=(1,0,0),v=(0,0,-1))).clean()
            front=front.cut(place(cyl(6.6,46),(x,clamp_back-91,z),u=(1,0,0),v=(0,0,-1))).clean()
            bo=bolt(m,'TOOL_CLAMP_PINCH_'+str(j),6,60,(x,clamp_back-30.5,z),u=(1,0,0),v=(0,0,1));bo.group='removable_tool'
        for name,sh in [('REAR',rear),('FRONT',front)]:
            bb=bbox(sh)
            m.add('TOOL_SPLIT_CLAMP_'+name,sh.translate(tuple(-v for v in bb[:3])),origin=bb[:3],
                pn='SPINDLE_SPLIT_CLAMP_'+name,group='removable_tool',material='6061-T6 aluminum billet',
                notes=['Width110, height40, assembled depth90.5; split gap0.50. BoreØ65.00/+0.03 with the split shim installed and both pinch bolts snug.',
                       'Rear:four blindM6×1 holes atX±45, Ø5 pilot17 deep, tap15 deep; mount screwsM6×20 engage13.3 through6.7 mm adapter web.',
                       'Pinch screws2×M6×60 atX±47. Rear split face:Ø5 pilot17 deep,tapM6×1 depth15. Front halfØ6.6 through; nominal engagement14.75.',
                       'Deburr bore edges0.3 maximum. Initial pinch torque3 N·m, verify spindle housing is retained without local deformation. Remove tool before bed swap.',
                       'The plasma torch split clamp (boreØ28 for the AG-60 straight body) shares this mount pattern; see TORCH_CLAMP parked parts.'])
    make_y_stops(m,gantry_y)
    make_x_stops(m,head_x,face_y)
    holds=[
        'Z slide: exact-ASIN drawing gives body219x80, end blocks12 and carriage90x50;70 mm transverse spacing belongs to the smallerØ5 fixing holes, not the largerØ7 bores. Output mounting-plane height, along-travel hole pitch/thread/depth and base-slot fastening remain unresolved. No carriage fasteners are modeled; the tool has no released attachment load path and TOOL_ADAPTER_110 individual export is guarded.',
        'HGR20: seller P40/E20/1500 hole dimensions conflict. Actual factory holes must be verified before rail cutting or custom datum drilling.',
        'HMS40: base nut cavity and endpoint datum not published. Rail caps require a verified base clamp/nut design; motor current and torque-speed curves missing.',
        'Z power-loss retention: no selected normally-engaged brake/counterbalance. A ballscrew must not be assumed self-locking. Do not enable a suspended tool until retention is designed and tested.',
        'Head projection uses an explicit80 mm Z stack assumption. Final tool sweep and claimed usable1000 Y must be recalculated when supplier datum is recovered.',
        'X/Y physical stops and three home switches are modeled. Z home bracket and travel stops depend on the unresolved Z supplier endpoint/output geometry. Cable-chain anchors, way covers and spindle/torch cable bend envelopes still require final integration.'
    ]
    m.holds.extend(holds)
    return {'configuration':{'gantry_y':gantry_y,'beam_center_y':beam_y,'head_x':head_x,'z_lift':z_lift,'tool':tool},
        'travel_mm':{'X':800,'Y':1000,'Z':100},'guide_midpoint_y_limits':[275,1275],
        'x_head_limits':[175,975],'gantry_beam_z':[1155,1235],
        'y_guide_center_z':1033,'y_block_spacing':180,'x_block_spacing':160,
        'Y_rail_count_length':[2,1420],'X_rail_count_length':[2,1200],
        'guide_blocks_count':8,'tool_axis_y_nominal_limits':[121.4,1121.4],
        'readiness':'DETAILED STRUCTURAL MOTION LAYOUT WITH EXPLICIT SUPPLIER/CONNECTION HOLDS',
        'holds':holds,'scope_note':'No unverified purchased bolt hole was invented. Geometry checks cannot close the listed missing interfaces.'}
