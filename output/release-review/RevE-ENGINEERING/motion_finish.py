"""Rev I removable float/breakaway head; no invented purchased torch interface.

Head coordinates: X transverse, Y up, Z forward. Standalone parts and flats use
the same machining definitions. Unknown owner torch and Z carriage connections
remain explicit inputs. A complete head is parked in the router assembly; a
hardware-only plasma setup can be made without asserting an installed torch.
"""
from dataclasses import dataclass
import copy, math
import cadquery as cq
from cad_helpers import Model, box, cyl, plate, rect, place, bbox, ALU, STEEL, PURCHASED, HARDWARE

PREFIX='I_HEAD_'
PARK=(550.,745.,442.096)
GUARDED='MEASURED INTERFACE REQUIRED - INDIVIDUAL EXPORT GUARDED'
SOURCES={
 'bearing':'https://www.igus.com/product/drylin_RJ4JP_01',
 'bearing_dimensions':'https://igus.partcommunity.com/3d-cad-models/rj4jp-01-linear-bearings-igus?info=igus%2Fdrylin_lineargleitlager%2Fr_runde_wellen_schnell_leise%2Frj4jp_01.prj',
 'switch':'https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2hw.pdf',
 'magnet':'https://www.supermagnete.de/eng/data_sheet_CSN-20.pdf',
 'socket_m3':'https://www.accu.co.uk/api/product-datasheet?id=642039',
 'socket_m4':'https://www.accu.co.uk/api/product-datasheet?id=151797',
 'countersunk_m4':'https://www.accu.co.uk/countersunk-socket-head-screws/251236-SSK-M4-16-A2-R360',
}

@dataclass(frozen=True)
class TorchMeasurements:
    barrel_diameter_mm:float
    straight_grip_length_mm:float
    barrel_roundness_mm:float
    evidence_id:str

def measured_bore(record):
    if record is None:return None
    if not record.evidence_id or not 20<=record.barrel_diameter_mm<=40:
        raise ValueError('Evidence and measured 20..40 mm barrel required')
    if record.straight_grip_length_mm<40 or not 0<=record.barrel_roundness_mm<=.10:
        raise ValueError('Need 40 mm straight grip and <=0.10 mm roundness')
    return record.barrel_diameter_mm+.10

def axis_y(s):return s.rotate((0,0,0),(1,0,0),-90)
def annulus(d,di,l):return cyl(d,l).cut(cyl(di,l)).clean()
def drilling(s,d,start,length,axis='z'):
    tool=cyl(d,length)
    if axis=='y':tool=axis_y(tool)
    return s.cut(tool.translate(start)).clean()

def make_head(float_lift=0., breakaway_offset=0., torch=None):
    """Fabricated head with complete mechanical interfaces, default blank insert.

    Float is 0..6 mm; normal separation is 0..8 mm. These are two distinct
    mechanisms. Work-mode acceptance still requires switch/force/torch tests.
    """
    if not 0<=float_lift<=6 or not 0<=breakaway_offset<=8:raise ValueError('Travel outside modeled mechanism')
    bore=measured_bore(torch)
    m=Model(); moving=[]; detachable=[]
    def add(name,s,origin=(0,0,0),pn=None,notes=(),moving_part=False,detached=False,**kw):
        ident=PREFIX+name
        p=m.add(ident,s,origin,pn=pn or ident,group='plasma_head_hardware',notes=notes,**kw)
        if moving_part or detached:moving.append(ident)
        if detached:detachable.append(ident)
        return p
    def flat(name,w,h,t,holes=(),origin=(0,0,0),**kw):
        data=dict(outline=rect(w,h),thickness_mm=t,holes=list(holes),slots=[],internal=[])
        return add(name,plate(rect(w,h),t,holes),origin,flat=data,**kw)
    def screw(name,d,L,x,y,z,axis='z',head=True,thread_target=None,moving_part=False,detached=False):
        # Local plain screw envelope: thread engagement is the sole permitted
        # positive overlap, explicitly assigned to the tapped component.
        s=cyl(d,L)
        if head:s=s.fuse(cyl({3:5.5,4:7.0,5:8.5,6:10.2}[d],d).translate((0,0,L))).clean()
        if axis=='y':s=axis_y(s)
        p=add(name,s,(x,y,z),pn=f'I_STD_M{d:g}x{L:g}_{axis}_'+('SOCKET' if head else 'STUD'),
              purchased=True,material='Steel ISO4762 socket screw, nominal thread envelope',color=HARDWARE,
              notes=['Specified unknurled socket heads: M3 diameter5.5/height3; M4 diameter7/height4. Enlarged knurled heads require new clearance check.',SOURCES['socket_m3'] if d==3 else SOURCES['socket_m4']],
              moving_part=moving_part,detached=detached)
        if thread_target:m.permit(p.id,PREFIX+thread_target,'Nominal screw thread engagement in tapped hole; pilot solid has thread minor diameter.')
        return p

    # Tool-side pattern is a designed custom interface, not a claimed ZBX80 pitch.
    back_holes=[(x,y,5.) for x in (10.,100.) for y in (22.,48.)]
    back=flat('BACKPLATE',110,130,9.525,back_holes,material='6061-T6 aluminium 3/8 in',color=ALU,
        notes=['Four M6x1 tapped holes on custom 90 x 26 mm tool-side pattern. Minor diameter5 modeled; tap through.',
               'This plate bolts to Rev H custom adapter from its rear. It does not establish the purchased Z output fixing pattern.',
               'Rod and stop tapped coordinates are defined in the local STEP. Crossbars are matched and jig-bored.'])
    # Crossbar screws enter from front, below and above the float mechanism.
    for x in (45,65):
        for y in (6,124):
            back.local=drilling(back.local,3.3,(x,y,0),9.525)
            back.flat['holes'].append((x,y,3.3))
    for x in (49,61):
        back.local=drilling(back.local,3.3,(x,55,0),9.525);back.flat['holes'].append((x,55,3.3))
    back.shape=back.local
    for x,y in ((105,112),(105,17.5)):
        back.local=drilling(back.local,5.5,(x,y,0),9.525)
        back.flat['holes'].append((x,y,5.5))
    back.shape=back.local
    for k,yy in enumerate((0,118),1):
        bar=box(110,12,25)
        for x in (25,85):
            # Rod socket lies at head Z22 => local12.475.
            y0=6 if k==1 else -1
            bar=drilling(bar,8,(x,y0,12.475),7,'y')
            bar=drilling(bar,4.5,(x,-1,12.475),14,'y')
            for x in (45,65):bar=drilling(bar,4.5,(x,6,-1),27)
        p=add('CROSSBAR_'+str(k),bar,(0,yy,9.525),material='6061-T6 aluminium',color=ALU,
            notes=['Ø8 H7 matched rod sockets depth6; nominal geometry shown. Ø4.5 coaxial end-screw access.',
                   'Two Ø4.5 front mounting holes. M4x30 screws engage5mm into tapped backplate. Jig bore both rod centers together.'])
        for x in (45,65):screw(f'BAR_{k}_{x}',4,30,x,yy+6,4.525,thread_target='BACKPLATE')
    # End-tapped rods; actual Ø8 h6 ground stock and straightness are acceptance items.
    rod=axis_y(cyl(8,118))
    rod=drilling(rod,3.3,(0,0,0),12,'y');rod=drilling(rod,3.3,(0,106,0),12,'y')
    for x in (25,85):
        add('ROD_'+str(x),rod,(x,6,22),pn='I_HEAD_ROD_8x118_M4_ENDS',material='Ground stainless shaft Ø8 h6',color=HARDWARE,
            notes=['Finish length118.0; axial M4x0.7 blind tap each end, usable depth10, pilot12. Hardened stock requires machinable ends or ground shaft made to drawing.'])
        # Top screw's shaft runs upward, head above top crossbar; lower reverses.
        screw('ROD_TOP_'+str(x),4,16,x,114,22,axis='y',thread_target='ROD_'+str(x))
        bottom=screw('ROD_BOTTOM_'+str(x),4,16,x,0,22,axis='y',thread_target='ROD_'+str(x))
        bottom.shape=bottom.shape.rotate((x,8,22),(x+1,8,22),180)
        bottom.local=bottom.local.rotate((0,8,0),(1,8,0),180)

    carriage=box(110,72,22)
    for x in (25,85):carriage=drilling(carriage,15,(x,-1,10),74,'y')
    # Captured metal stop: 14 mm slot around 8 mm fixed block gives exact6 float.
    carriage=carriage.cut(box(24,14,16).translate((43,17,-1))).clean()
    cp=add('FLOAT_CARRIAGE',carriage,(0,28,12),material='6061-T6 aluminium',color=ALU,moving_part=True,
           notes=['Two Ø15 slip-fit bearing housings. Bearing retention comes from bolted end caps, never crush-fit preload.',
                  'Internal pocket X43..67 / Y45..59 / Z11..27 captures the fixed8mm tall stop: metal lower/upper travel limits0 and6.',
                  'Ream housings and jig align with ground shafts. Verify gravity return over full travel after wiring/lead installation.'])
    # Four dry running manufacturer-dimensioned bushings, captured between caps.
    for x in (25,85):
        for y in (28,75.85):
            bearing=axis_y(annulus(15,8.04,24))
            add(f'BUSH_{x}_{y}',bearing,(x,y,22),pn='IGUS_RJ4JP_01_08',material='igus J4 polymer bearing',
                purchased=True,color=PURCHASED,moving_part=True,
                notes=['Manufacturer nominal ID8 / OD15 / length24. Internal clearance shown0.04; installed fit must be checked.',SOURCES['bearing_dimensions']])
        spacer=axis_y(annulus(14.8,9,23.85))
        add('BUSH_SPACER_'+str(x),spacer,(x,52,22),pn='I_HEAD_BUSH_SPACER_23p85',material='Acetal bearing spacer',moving_part=True,
            notes=['OD14.8 / ID9 / length23.85. Combined nominal bushing/spacer stack71.85 leaves0.15mm axial clearance between caps72mm apart. Verify actual0.10..0.20mm clearance after assembly.'])
    for k,yy in enumerate((26,100),1):
        # End cap local XY = width x depth, thickness along the guide direction.
        holes=[(x,10,8.8) for x in (25,85)]+[(x,z,3.4) for x in (7,103) for z in (5,17)]
        cap=plate(rect(110,22),2,holes)
        p=add('BEARING_CAP_'+str(k),cap,material='304 stainless 2mm',color=STEEL,moving_part=True,
            flat=dict(outline=rect(110,22),thickness_mm=2,holes=holes,slots=[],internal=[]))
        p.shape=place(cap,(0,yy+2,12),u=(1,0,0),v=(0,0,1))
        for x in (7,103):
            for z in (17,29):
                if k==2:
                    cp.local=drilling(cp.local,2.5,(x,64,z-12),8,'y')
                    screw(f'CAP_{k}_{x}_{z}',3,8,x,94,z,axis='y',thread_target='FLOAT_CARRIAGE',moving_part=True)
                else:
                    cp.local=drilling(cp.local,2.5,(x,0,z-12),8,'y')
                    p=screw(f'CAP_{k}_{x}_{z}',3,8,x,20,z,axis='y',thread_target='FLOAT_CARRIAGE',moving_part=True)
                    p.shape=p.shape.rotate((x,27,z),(x+1,27,z),180)
                    p.local=p.local.rotate((0,7,0),(1,7,0),180)
    cp.shape=cp.local.translate((0,28,12))
    stop=box(20,8,15.475)
    for x in (4,16):
        stop=drilling(stop,4.5,(x,4,-1),18)
        stop=drilling(stop,7.5,(x,4,11.475),4)
    add('FLOAT_STOP',stop,(45,51,9.525),material='6061-T6 aluminium',color=ALU,
        notes=['Rigid captured block controls both float travel ends; fit before carriage. No spring is needed to carry a falling head: the closed slot retains it.',
               'Replaceable0.2mm stop shims may be fitted only with corresponding travel and probe offset recalibration. Nominal definition has no shim.'])
    for x in (49,61):screw('STOP_'+str(x),4,16,x,55,5,thread_target='BACKPLATE')

    # Three kinematic seats: cone / V / flat, never three overconstraining cones.
    c=36+3*math.sqrt(2)
    for kind,x,y in [('CONE',10,40),('V',100,40),('FLAT',55,90)]:
        if kind=='CONE':
            seat=cyl(10,6).cut(cq.Solid.makeCone(0,4,4).translate((0,0,2))).clean()
        elif kind=='V':
            seat=box(20,12,6).translate((-10,-6,0))
            tool=cq.Workplane('YZ').polyline([(-4,6),(0,2),(4,6),(4,7),(-4,7)]).close().extrude(22,both=True).val()
            seat=seat.cut(tool).clean()
        else:seat=cyl(10,c-3-34)
        # Integral M4 threaded spigot is an explicit custom turned/machined part.
        seat=seat.fuse(cyl(4,6).translate((0,0,-6))).clean()
        add('SEAT_'+kind,seat,(x,y,34),material='Hardened steel contact insert',color=HARDWARE,moving_part=True,
            notes=['M4x0.7 integral6mm spigot into float body; fixture-machine contact height after assembly.',
                   'Cone90deg / V90deg / flat establishes a six-constraint coupling. Harden/contact polish; inspect contact blue before force tests.'])
        cp.local=drilling(cp.local,3.3,(x,y-28,15),7)
        m.permit(PREFIX+'SEAT_'+kind,cp.id,'Integral M4 seat thread in matching tapped float body.')
        sphere=cq.Solid.makeSphere(3,angleDegrees1=-90,angleDegrees2=90).intersect(box(8,8,3).translate((-4,-4,-3)))
        button=sphere.fuse(cyl(3.8,44-c)).clean()
        # Solid threaded pilot through fullbutton shank.
        button=button.cut(cyl(2.5,6).translate((0,0,-.1))).clean()
        add('BUTTON_'+kind,button,(x,y,c),pn='I_HEAD_BALL_BUTTON_R3',material='Hardened spherical steel contact R3',
            color=HARDWARE,detached=True,notes=['Custom R3 hemispherical contact, Ø3.8 shank; M3 internal fixing thread. All three identical.'])
    # Release plate supports magnets, locator buttons and clamp; 1/4in steel.
    release_holes=[(x,y-15,3.4) for x,y in [(10,40),(100,40),(55,90)]]
    release_holes += [(x,y-15,4.5) for x in (25,85) for y in (35,55)]
    rp=flat('RELEASE_PLATE',110,97,6.35,release_holes,origin=(0,15,44),material='Low carbon steel 1/4in',color=STEEL,detached=True,
        notes=['Steel back face is the magnet target. Three kinematic locator buttons fasten from the front.',
               'Keep mating face uncoated/flat; corrosion film and swarf change both retention and repeatability. Clean before seating.'])
    rp.flat['outline']=[(0,0),(110,0),(110,97),(28,97),(28,84.5),(0,84.5)]
    rp.local=plate(rp.flat['outline'],6.35,release_holes)
    for kind,x,y in [('CONE',10,40),('V',100,40),('FLAT',55,90)]:
        rp.local=drilling(rp.local,6.0,(x,y-15,3.35),3)
        rp.flat.setdefault('operations',[]).append(dict(type='circle',x=x,y=y-15,diameter=6.0,layer='MILL_FRONT_CB_DEPTH_3'))
        screw('BUTTON_SCREW_'+kind,3,7,x,y,40.35,thread_target='BUTTON_'+kind,detached=True)
    for j,(x,y) in enumerate(((17,88),(93,90),(55,40)),1):
        spacer=annulus(20.5,4.5,3.8)
        add('MAGNET_SPACER_'+str(j),spacer,(x,y,34),pn='I_HEAD_MAGNET_SPACER_3p8',material='Aluminium',moving_part=True,
            notes=['3.8 mm nominal spacer leaves0.2mm magnet-to-target gap. Force qualification requires actual gap, coating and measured lead load.'])
        magnet=annulus(20,4.5,6).cut(cq.Solid.makeCone(2.25,4.73,2.48).translate((0,0,3.52))).clean()
        add('MAGNET_'+str(j),magnet,(x,y,37.8),pn='SUPERMAGNETE_CSN_20',material='Purchased N38 magnet in Q235 cup',purchased=True,color=PURCHASED,moving_part=True,
            notes=['Manufacturer20x6mm, bore4.5 / countersink9.46x2.48;87.3N nominal direct steel pull,80C maximum.',SOURCES['magnet'],
                   'The catalog direct-contact pull is NOT the release force at this0.2mm gap. Set and record actual force after assembly.'])
        screw_s=cyl(4,13.52).fuse(cq.Solid.makeCone(2,4.48,2.48).translate((0,0,13.52))).clean()
        add('MAGNET_SCREW_'+str(j),screw_s,(x,y,27.8),pn='I_STD_M4x16_CSK',material='M4 countersunk steel screw',purchased=True,color=HARDWARE,moving_part=True,
            notes=['ISO10642 M4x16 overall length, head diameter8.96 and height2.48;90deg conservative cone envelope. Supplier countersink diameter9.46 leaves0.25mm radial clearance.',SOURCES['countersunk_m4']])
        cp.local=drilling(cp.local,3.3,(x,y-28,15.8),6.2)
        m.permit(PREFIX+'MAGNET_SCREW_'+str(j),cp.id,'M4 screw engages6.2mm in tapped carriage.')
    cp.shape=cp.local.translate((0,28,12))

    # Split clamp; insert default is a real blank with no fictional owner torch.
    clamp_axis=(55,25,80.6)
    for side,start,depth in [('REAR',50.35,30),('FRONT',80.85,30)]:
        s=box(90,40,depth).translate((10,25,start))
        s=s.cut(axis_y(cyl(48,42)).translate((55,24,80.6))).clean()
        if side=='REAR':
            for x in (25,85):
                for y in (35,55):s=drilling(s,3.3,(x,y,50.35),14)
        for x in (15,95):s=drilling(s,3.3 if side=='REAR' else 4.5,(x,45,start+18 if side=='REAR' else start),12 if side=='REAR' else depth)
        # Shape local is translated back to its rectangular blank origin.
        local=s.translate((-10,-25,-start))
        add('CLAMP_'+side,local,(10,25,start),material='6061-T6 aluminium',color=ALU,detached=True,
            notes=['FinishØ48 bore across matched assembled halves with0.5mm spacer in split. Rear half attaches through steel release plate.',
                   'FourM4 rear attachment taps depth12 usable; twoM4 pinch screws. Pinch torque must be set by actual torch allowable clamp load.'])
    for x in (25,85):
        for y in (35,55):
            # Rear-access counterbore keeps heads out of magnetic coupling gap.
            rp.local=drilling(rp.local,8,(x,y-15,0),4)
            rp.flat.setdefault('operations',[]).append(dict(type='circle',x=x,y=y-15,diameter=8,layer='MILL_REAR_CB_DEPTH_4'))
            sc=screw(f'CLAMP_MOUNT_{x}_{y}',4,14,x,y,34,thread_target='CLAMP_REAR',detached=True)
            sc.shape=sc.shape.rotate((x,y,48),(x,y+1,48),180)
            sc.local=sc.local.rotate((0,0,14),(0,1,14),180)
    rp.shape=rp.local.translate((0,15,44))
    for x in (15,95):screw('CLAMP_PINCH_'+str(x),4,40,x,45,70.85,thread_target='CLAMP_REAR',detached=True)
    insert=axis_y(cyl(48,40)).translate((55,25,80.6))
    if bore:insert=insert.cut(axis_y(cyl(bore,42)).translate((55,24,80.6))).clean()
    for side,z in [('REAR',50.6),('FRONT',80.85)]:
        half=insert.intersect(box(60,40,29.75).translate((25,25,z))).clean()
        add('INSERT_'+side,half.translate((-25,-25,-z)),(25,25,z),material='Machinable insulating insert blank; grade/temperature verify',color=(.2,.23,.27),detached=True,
            release=GUARDED if bore is None else 'MEASURED TORCH INSERT - THERMAL/CLAMP LOAD ACCEPTANCE REQUIRED',
            notes=['Default is an unbored physical split blank, not an assumed torch diameter.',
                   'Bore only from explicit diameter/roundness/40mm straight-zone record. Actual torch thermal limits and allowed clamp force remain required.'])

    # Removable dross/splash screen below the clamp. Its aperture is clearance,
    # not an assumed torch locating bore. Two welded tabs use actual screws.
    shield=plate(rect(110,60.5),1.5,[(55,30.25,50)])
    sp=add('SPLASH_SCREEN',shield,material='304 stainless 1.5mm',color=STEEL,detached=True,
        flat=dict(outline=rect(110,60.5),thickness_mm=1.5,holes=[(55,30.25,50)],slots=[],internal=[]),
        notes=['Flat110x60.5x1.5 screen, Ø50 clearance opening. Weld two separate10x10x1.5 tabs; no unspecified bends.',
               'Does not replace thermal qualification: magnet maximum80C and actual insert/lead temperatures must be measured. No aluminum-water plasma cutting is authorized by this model.'])
    sp.shape=place(shield,(0,13.5,50.35),u=(1,0,0),v=(0,0,1))
    for x in (5,105):
        flat('SPLASH_TAB_'+str(x),10,10,1.5,[(5,6,3.4)],origin=(x-5,13.5,50.35),
             material='304 stainless 1.5mm',color=STEEL,detached=True,
             notes=['Bottom10mm edge welded to screen rear upper edge; local hole at5,6.'])
        rp.local=drilling(rp.local,2.5,(x,4.5,0),6.35)
        rp.flat['holes'].append((x,4.5,2.5))
        screw('SPLASH_'+str(x),3,6,x,19.5,45.85,thread_target='RELEASE_PLATE',detached=True)
    rp.shape=rp.local.translate((0,15,44))

    # Float switch fits over the left end of the top crossbar. The release
    # plate has a matching upper corner relief; no outboard width is added.
    cam=cq.Workplane('YZ').polyline([(99.5,45.6),(110.05,45.6),(111.55,47.1),(120,47.1),(120,50),(99.5,50)]).close().extrude(22).val()
    cam=cam.fuse(box(7,11.5,4).translate((0,88,34))).fuse(box(7,3.5,16).translate((0,99.5,34))).clean()
    cam=cam.cut(cyl(21.5,6).translate((17,88,33.5))).clean()
    cam=drilling(cam,3.4,(2.65,99,39.5),5,'y')
    for y in (91,96.5):cam=drilling(cam,3.4,(3,y,33),6)
    add('FLOAT_CAM',cam.translate((0,-88,-34)),(0,88,34),material='Acetal cam',moving_part=True,
        notes=['Pin mount datum39.5; conservative2.2mm pin has lowest contact edge atY111.55. Ramp crosses real switch range at1.0..1.65mm float.',
               'Dwell maintains6.1mm normal position from the datum through remaining travel; TTPmax5.1 leaves1mm mechanical reserve.',
               'Probe initially at1mm/s and calibrate actual offset and stopping distance. Cam clears a defined corner relief in the release plate.'])
    for y in (91,96.5):
        cp.local=drilling(cp.local,2.5,(3,y-28,15),7)
        screw('CAM_'+str(y),3,10,3,y,28,thread_target='FLOAT_CARRIAGE',moving_part=True)
    cp.shape=cp.local.translate((0,28,12))

    def switch(name,x,face_y,reference_z,kind,plunger_normal,*,moving_part,reverse=False,bracket_x=None,bracket_w=26,relief=None,upper_mount=False):
        # Case dimensions and mating dimensions are from Omron's M3 pin-plunger
        # drawing. Cosmetic outline is a conservative rectangular envelope.
        sx=(lambda a:18.5-a) if reverse else (lambda a:a)
        case=box(18.5,5.3,6.5)
        case=drilling(case,3.3,(sx(15.65),-.1,3.5),5.5,'y')
        post=axis_y(cyl(3,1.5)).translate((sx(2.65),-1.5,3.5))
        case=case.fuse(post).fuse(axis_y(cyl(3,1.5)).translate((sx(2.65),5.3,3.5))).clean()
        add(name+'_CASE',case,(x,face_y,reference_z-3.5),pn='OMRON_D2HW_C20'+('2MR' if kind=='NC' else '3MR')+('_REVERSE' if reverse else ''),
            material='Omron sealed switch mating envelope',purchased=True,color=PURCHASED,moving_part=moving_part,
            notes=[SOURCES['switch'],'18.5x5.3x6.5 conservative case; M3mount centers13mm. Locating postØ3 projects1.5.',
                   'Pin-plunger operating position6.4±0.2 from mount datum; FPmax7.2 / TTPmax5.1. IP67 body, protect unsealed lead ends.'])
        pin=cyl(2.2,plunger_normal-3.0)
        add(name+'_PIN',pin,(x+sx(2.65),face_y+2.65,reference_z+3.0),pn='I_SWITCH_PLUNGER_'+name,
            purchased=True,material='Switch plunger kinematic envelope',moving_part=moving_part)
        bx=x-2.65 if bracket_x is None else bracket_x
        if upper_mount:
            base_z=reference_z-4.2;by=face_y+5.3
            bracket=box(bracket_w,14,2).fuse(box(bracket_w,6,8)).clean()
            for xx,d in ((x+sx(2.65),3.05),(x+sx(15.65),2.5)):
                bracket=drilling(bracket,d,(xx-bx,0,4.2),6,'y')
            for xx in (bx+3,bx+bracket_w-3):bracket=drilling(bracket,3.4,(xx-bx,10,-1),4)
            add(name+'_BRACKET',bracket,(bx,by,base_z),material='6061-T6 aluminium machined L bracket',color=ALU,
                notes=['Upper mounting face faces the switch.13mm M3/post centers; foot supports from upper guide crossbar front.'])
            sc=screw(name+'_M3',3,10,x+sx(15.65),face_y,reference_z,axis='y',thread_target=name+'_BRACKET')
            sc.shape=sc.shape.rotate((x+sx(15.65),face_y+5,reference_z),(x+sx(15.65)+1,face_y+5,reference_z),180)
            sc.local=sc.local.rotate((0,5,0),(1,5,0),180)
            bar=m.find(PREFIX+'CROSSBAR_2')
            for j,xx in enumerate((bx+3,bx+bracket_w-3)):
                yy=by+10;gap=base_z-34.525
                add(name+'_FOOT_SPACER_'+str(j),annulus(6,3.4,gap),(xx,yy,34.525),material='Aluminium spacer')
                screw(name+'_FOOT_'+str(j),3,8,xx,yy,base_z-6,thread_target='CROSSBAR_2')
                bar.local=drilling(bar.local,2.5,(xx,yy-118,19),6)
            bar.shape=bar.local.translate((0,118,9.525))
            return
        bracket=box(bracket_w,14,2).fuse(box(bracket_w,6,8).translate((0,8,0))).clean()
        for u in (x+sx(2.65)-bx,x+sx(15.65)-bx):bracket=drilling(bracket,3.05 if abs(u-(x+sx(2.65)-bx))<.01 else 2.5,(u,8,reference_z-(reference_z-4.2)),6,'y')
        anchor_x=(bx+3,bx+bracket_w-3)
        base_z=reference_z-4.2
        for xx in anchor_x:bracket=drilling(bracket,3.4,(xx-bx,4,-1),4)
        if relief:
            rx,ry=relief;bracket=drilling(bracket,12,(rx-bx,ry-(face_y-14),-1),4)
        add(name+'_BRACKET',bracket,(bx,face_y-14,base_z),material='6061-T6 aluminium machined L bracket',color=ALU,moving_part=moving_part,
            notes=['6mm thick upright tappedM3; Ø3.05 locating pocket and screw centers13.0. TwoM3 feet fasten into supporting plate/body.',
                   'Locating post pocket is clearance in this envelope; fit switch and set trip using measured shim stack, then record installed actuation.'])
        screw(name+'_M3',3,10,x+sx(15.65),face_y-4.7,reference_z,axis='y',thread_target=name+'_BRACKET',moving_part=moving_part)
        for j,xx in enumerate(anchor_x):
            yy=face_y-10
            target='FLOAT_CARRIAGE' if moving_part else 'BACKPLATE'
            # Shoulder spacer makes bracket foot sit exactly on its support.
            supporting_z=34 if moving_part else 9.525
            gap=base_z-supporting_z
            if gap>1e-6:
                add(name+'_FOOT_SPACER_'+str(j),annulus(6,3.4,gap),(xx,yy,supporting_z),material='Aluminium spacer',moving_part=moving_part)
            length=6 if moving_part else 10
            screw(name+'_FOOT_'+str(j),3,length,xx,yy,base_z+2-length,thread_target=target,moving_part=moving_part)
            targetp=cp if moving_part else back
            localx=xx;localy=yy-28 if moving_part else yy
            targetp.local=drilling(targetp.local,2.5,(localx,localy,0),22 if moving_part else 9.525)
            if targetp.flat:targetp.flat['holes'].append((localx,localy,2.5))
    switch('FLOAT_SWITCH',0,110,39.5,'NC',7.2 if float_lift<.4 else 7.6-min(float_lift,1.5),moving_part=False,bracket_x=0,upper_mount=True)
    for name,x,y,reverse,bx,bw,relief in [('PRESENCE_LEFT',0,69,False,0,26,None),
                                         ('PRESENCE_RIGHT',91.5,69,False,84,26,None),
                                         ('PRESENCE_TOP',52.35,103,False,44,36,(55,90))]:
        switch(name,x,y,38.2,'NO',min(7.2,5.8+breakaway_offset),moving_part=True,reverse=reverse,bracket_x=bx,bracket_w=bw,relief=relief)
    back.shape=back.local;cp.shape=cp.local.translate((0,28,12))

    # Lead saddle is on the fixed upper crossbar, within the110mm head width.
    lead=box(32,12,15).translate((76,118,34.525))
    lead=lead.cut(box(26,8,9).translate((79,120,40.525))).clean()
    for xx in (84,100):lead=drilling(lead,3.4,(xx,124,33.5),8)
    add('LEAD_SADDLE',lead.translate((-76,-118,-34.525)),(76,118,34.525),material='Aluminium fixed lead saddle',color=ALU,
        notes=['Open saddle accepts reusable insulated strap up to20mm wide. Fixed upper-crossbar attachment takes supply-lead drag off floating carriage.',
               'Actual lead OD, minimum bend radius, slack loop and strap selection remain measurement inputs. No unmeasured cable is modeled.'])
    topbar=m.find(PREFIX+'CROSSBAR_2')
    for xx in (84,100):
        topbar.local=drilling(topbar.local,2.5,(xx,6,19),6)
        screw('LEAD_'+str(xx),3,10,xx,124,30.525,thread_target='CROSSBAR_2')
    topbar.shape=topbar.local.translate((0,118,9.525))
    # Eyes are bolted; an actual rated nonconductive tether remains required.
    for name,x,y,z,detached in [('FIXED',55,122,34.525,False),('RELEASE',104,100,50.35,True)]:
        eye=box(16,12,12)
        eye=drilling(eye,4.5,(3,6,-1),14)
        eye=eye.cut(axis_y(cyl(4,14)).translate((12,-1,8))).clean()
        if not detached:eye=eye.rotate((0,0,0),(0,0,1),90).translate((12,0,0))
        add('TETHER_EYE_'+name,eye,(x-3,y-6,z) if detached else (x-6,y-3,z),material='6061-T6 aluminium eye block',color=ALU,detached=detached,
            notes=['Separate4mm tether passage and4.5mm screw clearance. Fit rated nonconductive tether with enough slack for6mm float/8mm normal release; qualify arrest load.'])
        if detached:
            rp.local=drilling(rp.local,3.3,(x,y-15,0),6.35);rp.flat['holes'].append((x,y-15,3.3))
        else:topbar.local=drilling(topbar.local,3.3,(x,y-118,19),6)
        screw('TETHER_'+name,4,16,x,y,z-4,thread_target='RELEASE_PLATE' if detached else 'CROSSBAR_2',detached=detached)
    topbar.shape=topbar.local.translate((0,118,9.525));rp.shape=rp.local.translate((0,15,44))
    # Apply mechanism translations after all local shapes are finalized.
    for p in m.parts:
        if p.id in moving:p.shape=p.shape.translate((0,float_lift,0))
        if p.id in detachable:p.shape=p.shape.translate((0,0,breakaway_offset))
    meta=dict(status='COMPLETE MECHANISM GEOMETRY / MEASURED TORCH AND INSTALLATION ACCEPTANCE REQUIRED',
        float_travel_mm=6,probe_switch_crossing_mm=[1,1.65],probe_speed_mm_s=1,
        breakaway_catalog_normal_pull_sum_n=261.9,breakaway_actual_force_n=None,
        magnet_gap_mm=.2,torch_bore_mm=bore,actual_torch_present=False,
        working_tool_axis_from_adapter_mm=[55,None,80.6],
        moving_ids=moving,detachable_ids=detachable,sources=SOURCES,
        switch_logic={'float':'D2HW-C202MR NC opens on touch-off',
          'head_present':'Three D2HW-C203MR NO contacts in series; all close only when seated. Isolated5V/5mA suggested; controller interface must be designed.',
          'safety':'Switch contacts are detection only, not a rated safety system.'})
    m.holds=['Actual torch barrel, straight grip, nozzle stand-off, lead OD/bend radius and thermal limits require owner measurements.',
        'Head is not an operating plasma tool until clamp bore, seated-force/release-force, return, detection, stopping and tether tests pass.',
        'Purchased Z output fixing, brake motor pilot/coupling and loss-of-power timing remain the separately recorded Rev H interface holds.']
    return m,meta

def _copy_into(target,head,origin,working=False):
    for p in head.parts:
        q=copy.copy(p);q.notes=list(p.notes);q.flat=copy.deepcopy(p.flat)
        q.shape=place(p.shape,origin,u=(1,0,0),v=(0,0,1)) if working else p.shape.translate(origin)
        target.parts.append(q)
    target.allowed_intersections.update(head.allowed_intersections)
    target.holds.extend(head.holds)

def extend_router_model(m):
    head,meta=make_head()
    m.holds[:]=[('Rev I supplies nominal fabricated floating and breakaway mechanisms. Actual torch/clamp dimensions, installed retention/release forces, tether, lead routing and electrical commissioning remain unqualified.' if h.startswith('The owned torch barrel/clamping zone') else h) for h in m.holds]
    _copy_into(m,head,PARK)
    # Three pads support the head's rear plate without loading float bearings.
    # Two outboard screws retain it; feet are welded onto the existing lid.
    for i,(x,y) in enumerate(((105,112),(105,17.5),(20,65)),1):
        foot=plate(rect(40,30),6.35,[(20,15,4.2)] if i<3 else [])
        m.add('I_HEAD_PARK_FOOT_'+str(i),foot,(PARK[0]+x-20,PARK[1]+y-15,433.096),
            group='tool_storage',material='Low carbon steel 1/4in',
            notes=['Four10mm-long3mm fillet welds at separated corners onto equipment lid. Coat and leak-test after fabrication.',
                   'M5x0.8 through tap in first two feet; bottom screw tip remains0.525mm above lid. Third foot is a support only.'],
            flat=dict(outline=rect(40,30),thickness_mm=6.35,holes=[(20,15,4.2)] if i<3 else [],slots=[],internal=[]))
        pad=annulus(12,5.5,2.65) if i<3 else cyl(12,2.65)
        m.add('I_HEAD_PARK_PAD_'+str(i),pad,(PARK[0]+x,PARK[1]+y,439.446),group='tool_storage',
            material='Machined steel support pad',notes=['Machine3mm stock to2.65mm. Two small edge welds retain pad to its foot; keep weld below the top datum. Confirm support coplanarity and screw tip clearance after welding.'])
        if i<3:
            bolt=cyl(5,18).fuse(cyl(8.5,5).translate((0,0,18))).clean()
            m.add('I_PARK_BOLT_'+str(i),bolt,(PARK[0]+x,PARK[1]+y,433.621),pn='I_STD_M5x18_SOCKET',
                group='tool_storage',material='M5x18 steel socket screw',purchased=True,color=HARDWARE)
            m.permit('I_PARK_BOLT_'+str(i),'I_HEAD_PARK_FOOT_'+str(i),'M5 parking screw engages5.825mm in tapped steel foot.')
    # Dedicated short screws fit the9.525mm new backplate without protruding into
    # the moving carriage. Router's longer screws stay with the router clamp.
    for i in range(4):
        bolt=cyl(6,16).fuse(cyl(10.2,6).translate((0,0,16))).clean()
        m.add('I_TOOL_MOUNT_'+str(i+1),bolt,(920+18*i,770,436.144),pn='I_STD_M6x16_SOCKET',
            group='stored_hardware',material='M6x16 steel socket screw',purchased=True,color=HARDWARE,
            notes=['New plasma-head mount screw:16mm under-head length,9.3mm engagement after6.7mm adapter web. Do not substitute the router20mm screw.'])
    meta['parking_origin_mm']=PARK
    meta['parking_status']='Three lid-welded support feet and two outboardM5 retainers; explicit transfer path verification in motion evidence.'
    return meta

def extend_stored_model(stored,source):
    return {'head':'Remains in the same parking bay; no second transform.'}

def plasma_hardware_model(stored, *, float_lift=0., breakaway_offset=0., torch=None):
    """Exchange guarded head hardware into work position; actual torch absent."""
    import build_revg
    result=build_revg.clone_model(stored)
    result.parts=[p for p in result.parts if not (p.id.startswith(PREFIX) and not p.id.startswith('I_HEAD_PARK_'))]
    # Caller supplies bed-stored model whose router tool is already parked.
    adapter=result.find('TOOL_ADAPTER_110');bb=bbox(adapter.shape)
    head,details=make_head(float_lift,breakaway_offset,torch)
    _copy_into(result,head,(bb[0],bb[1],bb[2]),working=True)
    for i,(x,y) in enumerate([(x,y) for x in (10,100) for y in (22,48)],1):
        p=result.find('I_TOOL_MOUNT_'+str(i))
        at_head=place(p.local,(x,y,9.3),u=(1,0,0),v=(0,-1,0))
        p.shape=place(at_head,(bb[0],bb[1],bb[2]),u=(1,0,0),v=(0,0,1))
        p.group='plasma_head_hardware'
        result.permit(p.id,PREFIX+'BACKPLATE','M6x16 mount screw engages9.3mm in tapped custom head plate.')
    for i in (1,2):
        p=result.find('I_PARK_BOLT_'+str(i))
        p.shape=p.local.translate((907+20*i,807,436.144))
        p.group='stored_hardware'
    details['status']='PLASMA HEAD HARDWARE REVIEW; NO ACTUAL TORCH OR ENERGIZED OPERATION QUALIFIED'
    return result,details
