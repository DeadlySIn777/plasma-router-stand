"""Selected311mm /200stroke ATC slide with passive captured endpoint docks.

The original60mm-width manufacturerhousing STEP supplies the externalbody,
endcaps andpocket/mountaxes. Its internalER11socket/nut/IRplanes remain
calibration/interfaces, distinct from the unmodified installation geometry.
"""
from pathlib import Path
from functools import lru_cache
import sys
import cadquery as cq

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'variants/extrusion-reengineered'
sys.path.insert(0,str(BASE))
import frame as source_frame

AL=(.60,.69,.74);STEEL=(.26,.34,.39);EX=(.16,.20,.23)
VENDOR=(.68,.48,.24);ALLOC=(.64,.35,.72);HARD=(.36,.39,.42)
MODULE_FRONT=1230.;MODULE_OVERALL=311.;TRAVEL=200.;MAG_BASE=1051.85
BED_TOP=967.8;STOCK_PLUS_CLAMP=40.;SAFE_GAP=5.;FRAME_DEPTH=1600.
MODULE_BASE=959.15;CARRIAGE_HEIGHT_ALLOCATION=47.3
CARRIER_BOTTOM=1026.45;ARM_BOTTOM=1013.75
GEOMETRY_RISE=7.;KIT_HEIGHT=107.3;HOOD_ROTATE_CENTRE_Z=1590.35;HOOD_LOWER_DISTANCE=1182.35
BEAM_CENTRE=MODULE_FRONT+38.;BODY_Y=1070.
FRAME_INNER_LEFT,FRAME_INNER_RIGHT=25.8,1124.2
PIN_X=(315.,835.);HOOD_STORED_OFFSET_X=-300.;HOOD_STORED_OFFSET_Y=70.
CAPTURE_Z_GAP=.15
CAPTURE_LEFT_OUTER=255.025
CAPTURE_LEFT_INNER=275.175
CAPTURE_KEY_LEFT=(255.1,275.1)
CAPTURE_KEY_BOTTOM=1006.9
CAPTURE_KEY_TOP=1032.15
VENDOR_HOUSING_SOURCE=HERE/'sources/ER20_4_Standard_20240204.step'
POCKET_X=(507.5,552.5,597.5,642.5)
MOUNT_X=(481.,669.)

def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cyl(d,h,p,n=(0,0,1)):return cq.Solid.makeCylinder(d/2,h,cq.Vector(*p),cq.Vector(*n))
def bounds(s):
    b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def cut(s,tools):
    for q in tools:s=s.cut(q)
    return s.clean()
def xslot(d,extra,h,p):
    x,y,z=p
    return cyl(d,h,(x-extra/2,y,z)).fuse(cyl(d,h,(x+extra/2,y,z)),box(x-extra/2,y-d/2,z,extra,d,h)).clean()

def capture_key(side,cy):
    """Integral lowered tongue with symmetric3x5mm entry chamfers.

    Left totalXfreeplay is .15mm; rightfloats. The lower tongue passes
    beneath the main plate, clearing its M6heads and the inner fixed guide.
    """
    lo,hi=CAPTURE_KEY_LEFT;y0,y1=cy-30,cy+30
    xy=[(lo+3,y0),(hi-3,y0),(hi,y0+5),(hi,y1-5),
        (hi-3,y1),(lo+3,y1),(lo,y1-5),(lo,y0+5)]
    if side=='R':xy=[(1150-x,y)for x,y in reversed(xy)]
    return cq.Workplane('XY').polyline(xy).close().extrude(CAPTURE_KEY_TOP-CAPTURE_KEY_BOTTOM).val().translate((0,0,CAPTURE_KEY_BOTTOM))

@lru_cache(None)
def vendor_housing_parts():
    source=cq.importers.importStep(str(VENDOR_HOUSING_SOURCE)).val()
    assert source.isValid() and len(source.Solids())==4
    return tuple(source.Solids())

def add_assembly_part(asm,name,shape,color):
    """Preserve the OEM's local trim curves through STEP serialization.

    Baking the1000mm translation into the original small corner trim of
    source topcap4 makes an OCC STEP roundtrip selfintersect that wire.
    A real assembly location preserves the untouched local definition.
    """
    if name.startswith('ATC_VENDOR_RAPIDCHANGE_4_HOUSING_'):
        local=vendor_housing_parts()[int(name.rsplit('_',1)[1])-1]
        b0,b1=bounds(local),bounds(shape)
        loc=cq.Location(cq.Vector(*(b1[k]-b0[k]for k in range(3))))
        asm.add(local,name=name,color=cq.Color(*color),loc=loc)
    else:asm.add(shape,name=name,color=cq.Color(*color))

def _hood_native(released=False):
    front=cut(box(275,1277,1005.9,600,1.9,165.1),[box(x,1276,1004.9,60,4,13.85)for x in(280.,810.)])
    p=[('ATC_COVER_ROOF',box(275,1277,1171,600,91,1.9),STEEL),
       ('ATC_COVER_FRONT',front,STEEL),
       ('ATC_COVER_SIDE_L',box(275,1278.9,1005.9,1.9,87.2,165.1),STEEL),
       ('ATC_COVER_SIDE_R',box(873.1,1278.9,1005.9,1.9,87.2,165.1),STEEL)]
    rear=box(275,1366.1,1005.9,600,1.9,165.1)
    rear=cut(rear,[box(x,1365.1,1004.9,30,4,35.25)for x in(466.,654.)])
    p.append(('ATC_COVER_REAR_WITH_ARM_RELIEFS',rear,STEEL))
    # Roof clears the raised common Z carrier. Folded grips lie behind its
    # rear face, below the raised gantry beam; root checks the actual head.
    for side,x in(('L',270.),('R',880.)):
        handle=cyl(6,40,(x,1323,1181.8),(0,1,0))
        for y in(1323.,1363.):
            handle=handle.fuse(box(267. if side=='L' else 872.,y-3,1178.8,11,6,6),
                box(272. if side=='L' else 872.,y-3,1172.9,6,6,11.9))
        p.append(('ATC_COVER_FOLDED_HANDLE_'+side,handle.clean(),HARD))
    p=[(n,s.translate((0,BODY_Y-1082.,0)),c)for n,s,c in p]
    p=[(n,s.cut(box(274,1264,1004,68,4,23.3)).cut(box(809,1264,1004,67,4,10.75)).clean(),c)
       if n=='ATC_COVER_FRONT'else(n,s,c)for n,s,c in p]
    p=[(n,s.cut(box(274,1264,1004,4,46,23.3)).cut(box(274,1309,1004,4,12,10.75)).clean(),c)
       if n=='ATC_COVER_SIDE_L'else(n,s.cut(box(872,1264,1004,4,57,10.75)).clean(),c)
       if n=='ATC_COVER_SIDE_R'else(n,s,c)for n,s,c in p]
    for side,x,xc in(('L',255.,264.),('R',875.,886.)):
        tab=cut(box(x,1278.,1045.65,20,20,1.9),[cyl(4.5,3.9,(xc,1288.,1044.65))])
        p.append(('ATC_COVER_SEAT_TAB_'+side,tab,STEEL))
        if not released:
            screw=cyl(4,6,(xc,1288.,1041.55)).fuse(cyl(7,4,(xc,1288.,1047.55))).clean()
            p.append(('ATC_COVER_REMOVABLE_M4x6_'+side,screw,HARD))
    return p

def hood_parts(state='fitted'):
    if state=='removed':return []
    p=_hood_native(released=state=='stored')
    if state=='fitted':return p
    if state!='stored':raise ValueError('Hood state: fitted / stored / removed')
    return [(n,s.translate((0,0,500)).rotate((575,BODY_Y+233,HOOD_ROTATE_CENTRE_Z),(575,BODY_Y+234,HOOD_ROTATE_CENTRE_Z),90)
             .translate((HOOD_STORED_OFFSET_X,HOOD_STORED_OFFSET_Y,-HOOD_LOWER_DISTANCE)),c)for n,s,c in p]

def hood_parts_at(stage,t):
    """Release clamps then five manual path segments; no outside carry."""
    if stage not in range(6)or not 0<=t<=1:raise ValueError('stage0..5,t0..1')
    if stage==0:
        return [(n,s.translate((0,0,8*t))if n.startswith('ATC_COVER_REMOVABLE_M4x6_')else s,c)
                for n,s,c in _hood_native()]
    stage-=1;p=_hood_native(released=True);out=[]
    for n,s,c in p:
        s=s.translate((0,0,500*(t if stage==0 else 1)))
        if stage>=1:s=s.rotate((575,BODY_Y+233,HOOD_ROTATE_CENTRE_Z),(575,BODY_Y+234,HOOD_ROTATE_CENTRE_Z),90*(t if stage==1 else 1))
        if stage>=2:s=s.translate((-390*(t if stage==2 else 1),70*(t if stage==2 else 1),0))
        if stage>=3:s=s.translate((0,0,-HOOD_LOWER_DISTANCE*(t if stage==3 else 1)))
        if stage>=4:s=s.translate((90*t,0,0))
        out.append((n,s,c))
    return out

def acceptance_parts(deployment=0.):
    if not 0<=deployment<=TRAVEL:raise ValueError('ATC travel0..200')
    return [('ATC_RAPIDCHANGE_KIT_CAPACITY_NOT_VENDOR_CAD',box(315,BODY_Y+deployment,MAG_BASE,520,60,KIT_HEIGHT),ALLOC)]+[
        (f'ATC_RETAINED_ER11_NUT_TOOL_CAPACITY_{j}',cyl(21,26.35,(x,BODY_Y+30+deployment,MAG_BASE-26.35)),ALLOC)
        for j,x in enumerate(POCKET_X,1)]

@lru_cache(None)
def _build(deployment=0.,pins_withdrawn=False,hood='stored'):
    if not 0<=deployment<=TRAVEL:raise ValueError('ATC travel0..200')
    # Compatibility argument only: this revision has no removable pins.
    if hood=='fitted'and deployment!=200.:raise ValueError('Cover fitted only over the parked magazine')
    p=[];classes={};spec={}
    module_base=MODULE_BASE-GEOMETRY_RISE;carrier_bottom=CARRIER_BOTTOM-GEOMETRY_RISE
    arm_bottom=ARM_BOTTOM-GEOMETRY_RISE;mag_base=MAG_BASE-GEOMETRY_RISE
    def add(n,s,color=AL,moving=False,stock='',ownership='new',notes=''):
        if moving:s=s.translate((0,deployment,0))
        p.append((n,s,color));classes[n]='carrier'if moving else'fixed'
        spec[n]=dict(stock=stock,ownership=ownership,notes=notes)
    # Two lowered full-width4080 members and four plate mounts. They belong
    # to this factory/takeoff, so the root frame must not count them again.
    for j,cy in enumerate((1280.,1500.),1):
        bar=source_frame.bar(32.15,cy-40,905.8,'X',1085.7,flat=True)
        for x,norm in((32.15,(1,0,0)),(1117.85,(-1,0,0))):
            for y in(cy-20,cy+20):bar=bar.cut(cyl(8,22,(x,y,925.8),norm))
        for x in(565.,585.):
            yy=1270. if j==1 else 1510.
            bar=bar.cut(cyl(8.5,42,(x,yy,904.8)))
        add(f'ATC_4080_CROSSBEARER_{j}',bar.clean(),EX,stock='4080 x1085.7mm, flat80Yx40Z; core end tapM8; four vertical access bores as indexed',notes='Actual die/core/slot fit and section properties remain supplier gates.')
        for side,x in(('L',25.8),('R',1117.85)):
            plate=box(x,cy-40,905.8,6.35,80,133.2)
            plate=cut(plate,[cyl(d,8.35,(x-1,y,z),(1,0,0))for y in(cy-20,cy+20)for z,d in((925.8,8.5),(1026.,6.6))])
            add(f'ATC_DROP_PLATE_{side}_{j}',plate,stock='80x133.2x6.35 6061-T6 candidate plate',notes='FinalworldM8rowZ932.8, headerM6rowZ1033, top1046 (5mm below movingHGHblock). M8 end fixing and M6/Tnut header face. Actual die/slot/preload held.')
    base=box(535,MODULE_FRONT+8,945.8,80,295,6.35)
    base=cut(base,[cyl(4.5,8.35,(x,y,944.8))for x in(565.,585.)for y in(1270.,1510.)])
    add('ATC_SELECTED_SLIDE_BASE_PLATE',base,stock='80x295x6.35mm6061-T6;4xD4.5 atX±10 and indexedY',notes='N-M4 underside channel axes±10 are inferred from16/24 drawing; actual nut contour/thread depth are supplier-fit holds. Along-channelY positions are this design.')
    # Source-specific outer envelopes, not a claimed OEM detailed solid.
    add('ATC_SELECTED311_MODULE_BASE',box(553,MODULE_FRONT+8,module_base,44,295,20),VENDOR,ownership='owned-motion-reported',notes='Selected drawing311/44/20. Actual underside channels are not invented.')
    add('ATC_SELECTED311_FRONT_END',box(552,MODULE_FRONT,module_base,46,8,50),VENDOR,ownership='owned-motion-reported',notes='46x50 far end from supplied drawing; orientation reversed, motor at rear.')
    add('ATC_SELECTED311_MOTOR_END',box(547,MODULE_FRONT+303,module_base,56,8,65),VENDOR,ownership='owned-motion-reported',notes='56x65 mounting end. No implicit motor included in311 dimension.')
    add('ATC_MOTOR57x57x56_RESERVATION',box(546.5,MODULE_FRONT+311,959.65,57,56,57),VENDOR,ownership='owned-motion-reported',notes='Conservative stock-motor reservation only; actual motor/coupler/revision not inspected. Cable exits up/side; no rear projection allocated beyond1597.')
    add('ATC_SELECTED311_CARRIAGE_ALLOCATION',box(530,BEAM_CENTRE-30,module_base+20,90,60,CARRIAGE_HEIGHT_ALLOCATION),VENDOR,True,ownership='owned-motion-reported',notes='60mm axial length/4-M6 source known. Width90/height47.3 are retained unmeasured envelope allocations; no manufactured OEM-hole pattern invented.')
    beam=source_frame.bar(275,BEAM_CENTRE-40,1039.15-GEOMETRY_RISE,'X',600,flat=True)
    add('ATC_4080_MOVING_CROSSCARRIER',beam,EX,True,stock='4080 x600mm laid80Yx40Z; obsolete pin/head-access bores removed',notes='Conditional Iweak>=134000mm4; actual die, slot and bolt joint capacities unqualified. Do not replace with a flat unsupported bar.')
    centre=box(530,BEAM_CENTRE-30,carrier_bottom,90,60,12.7)
    for yy in(BEAM_CENTRE-20,BEAM_CENTRE+20):
        centre=cut(centre,[cyl(6.6,14.7,(575,yy,carrier_bottom-1)),cyl(11,3.4,(575,yy,carrier_bottom))])
        # External grip only. The selected4080 must accept10.7mm maximum
        # internal projection and a compatibleM6 nut; no false die is cut.
        b=cyl(6,9.3,(575,yy,1022.85)).fuse(cyl(10.5,3.3,(575,yy,1019.55))).clean()
        add(f'ATC_CENTRE_M6x20_BUTTON_EXTERNAL_GRIP_{yy:g}',b,HARD,True,stock='M6x20button screw; externalgrip9.3, threadprojection10.7 held',notes='Button head3.3 in3.4counterbore. Actual slot lip/nut/cavity fit must permit the declared projection.')
    add('ATC_CARRIAGE_TRANSFER_PLATE',centre,AL,True,stock='90x60x12.7mm6061-T6, custom centre2holes only',notes='Supplier4-M6 mating face remains a transfer-drill blank. No claimed complete attachment to unmeasured OEM carriage.')
    for side,x,pinx,slotx in(('L',275.,315.,288.),('R',815.,835.,865.)):
        endplate=box(x,BEAM_CENTRE-30,carrier_bottom,60,60,12.7)
        holes=[]
        for yy in(BEAM_CENTRE-20,BEAM_CENTRE+20):
            holes.append(cyl(6.6,14.7,(slotx,yy,carrier_bottom-1)))
            for k,zz in enumerate((1016.25,1017.85),1):
                washer=cyl(12,1.6,(slotx,yy,zz)).cut(cyl(6.6,3.6,(slotx,yy,zz-1)))
                add(f'ATC_END_M6_WASHER_{side}_{yy:g}_{k}',washer,HARD,True,stock='M6washer12ODx1.6;8total')
            b=cyl(6,15.9,(slotx,yy,1016.25)).fuse(cyl(10,6,(slotx,yy,1010.25))).clean()
            add(f'ATC_END_M6x25_EXTERNAL_GRIP_{side}_{yy:g}',b,HARD,True,stock='M6x25socket screw; externalgrip15.9+9.1threadprojection held',notes='Actual received slot nut, lip and9.1mm inner projection require fit verification; no slot thread geometry invented.')
        land=box(295 if side=='L'else 815,BEAM_CENTRE-30,1006.75,40,60,12.7)
        endplate=cut(endplate,holes).fuse(capture_key(side,BEAM_CENTRE),land).clean()
        add('ATC_CROSSCARRIER_END_PLATE_'+side,endplate,AL,True,
            stock='80x60x25.4mm6061-T6 raw billet; integral lower tongue and40mm-wide underside seat land',
            notes='No endpoint bolt or locator bore. Mainplate12.7mm, integral25.4mm thick bearingland; lowered20mm tongue with3x5mm chamfers. Finish totalleftXguide/verticalgaps .10-.20mm afterwelding/fit. Rightfloats. Newstock; noownedsheetcredit.')
    for side,pinx in zip(('L','R'),MOUNT_X):
        x=pinx-14
        arm=box(x,BODY_Y,arm_bottom,28,BEAM_CENTRE+44-BODY_Y,25.4)
        holes=[]
        for y in(BEAM_CENTRE-20,BEAM_CENTRE+20,BODY_Y+30):
            holes += [cyl(6.6,27.4,(pinx,y,arm_bottom-1)),cyl(10.5,6.1,(pinx,y,arm_bottom))]
        arm=cut(arm,holes)
        add('ATC_FORWARD_ARM_'+side,arm,AL,True,stock=f'28x{BEAM_CENTRE+44-BODY_Y:g}x25.4mm6061-T6billet',notes='Manufacturer mount axes481/669. ThreeM6bores with6.1mm undersideheadrecess. M6x30rear to4080andcentralfrontpad. Deepbilletstrengthensbendingwithoutnewprofile. Noobsoletehoodtap;hoodretainsdirectlyonfixedcapture-rooftabs.')
        pad=box(pinx-14,BODY_Y,1032.15,28,60,12.7)
        pad=cut(pad,[cyl(6,14.7,(pinx,y,1031.15))for y in(BODY_Y+10,BODY_Y+30,BODY_Y+50)])
        add('ATC_KIT_MOUNT_PAD_'+side,pad,AL,True,stock='28x60x12.7mm6061-T6;threeM6tapsinlineat10/30/50mmY',notes='Bodymounts atmanufacturerX+/-94/Y+/-20. Centretap attachespadfrombelow;outertapsacceptM6x55fromOEMcounterbores. Distinctaxespreventopposingscrewoverlap. Bodyengagement10.8mm/tipreserve1.9mm.')
        for y in(BODY_Y+30,BEAM_CENTRE-20,BEAM_CENTRE+20):
            under=arm_bottom+6.1
            rendered_grip=30 if y==BODY_Y+30 else 19.3
            screw=cyl(6,rendered_grip,(pinx,y,under)).fuse(cyl(10,6,(pinx,y,under-6))).clean()
            add(f'ATC_ARM_M6x30_{side}_{y:g}',screw,HARD,True,stock='M6x30socket screw;6total',notes='Underside6.1recess leaves19.3grip:10.7mmengagement/projection. Rearbolts render only19.3externalgrip; actual4080Tnut/cavityfitheld. Frontbolts renderfull30and12.7padleaves2.0mmtipreserve.')
        for y in(BODY_Y+10,BODY_Y+50):
            under=mag_base+44.2
            screw=cyl(6,55,(pinx,y,under-55)).fuse(cyl(10,6,(pinx,y,under))).clean()
            add(f'ATC_VENDOR_M6x55_{side}_{y:g}',screw,HARD,True,stock='M6x55socket screw;4total',notes='ManufacturerSTEPD6.35through/D11counterbore7deep;head10ODx6. Bodygrip44.2leaves10.8padengagement/1.9tipreserve. Verifyreceivedrevision/templatebeforecut.')
    for j,s in enumerate(vendor_housing_parts(),1):
        s=s.translate((575,BODY_Y+30,mag_base))
        add(f'ATC_VENDOR_RAPIDCHANGE_4_HOUSING_{j}',s,VENDOR,True,ownership='new-kit-included-reference',stock='Included datedmanufacturer60mm-width fourpocket housingSTEP;no separatehousingpurchase',notes='OriginalunscaledER20_4_Standard;FAQER11/ER16/ER20externalgeometrysameexceptsockets. Fouroriginalsolidsincludeendcaps/body/top;internalER11sockets,IR,cables,nutengagementplanesabsent. Receivedrevisionheld.')
    # Passive U docks: seats carry downforce; roofs capture uplift/roll;
    # the two-sided left guide constrainsX/yaw; right floats laterally.
    # Opposite endpoint stops permit powered straight-line entry/exit.
    # Axial retention still requires verified energized slide preload.
    for end,cy in(('DEPLOYED',BEAM_CENTRE),('PARKED',BEAM_CENTRE+200)):
        for side,x,pinx in(('L',285.,315.),('R',815.,835.)):
            outer=CAPTURE_LEFT_OUTER-6.35 if side=='L'else 896.1
            xmin=outer if side=='L'else x
            xmax=x+50 if side=='L'else outer+6.35
            base=box(xmin,cy-30,945.8,xmax-xmin,72,6.35)
            top=box(xmin,cy-30,1000.4,xmax-xmin,72,6.35)
            legs=[box(xx,cy-30,952.15,6.35,72,48.25)for xx in(x,x+43.65)]
            legs.append(box(outer,cy-30,952.15,6.35,72,48.25))
            wall=box(outer,cy-30,1006.75,6.35,60,CAPTURE_KEY_TOP+CAPTURE_Z_GAP-1006.75)
            roof_x=outer if side=='L'else 875.1
            roof_end=274.9 if side=='L'else outer+6.35
            roof=box(roof_x,cy-30,CAPTURE_KEY_TOP+CAPTURE_Z_GAP,roof_end-roof_x,60,6.35)
            additions=[wall,roof]
            if side=='L':
                additions.append(box(CAPTURE_LEFT_INNER,cy-30,1006.75,6.35,60,1019.3-1006.75))
            stop_y=cy-36.35 if end=='DEPLOYED'else cy+30
            stop_x=255.1 if side=='L'else 875.1
            additions.append(box(stop_x,stop_y,1000.4,19.8,6.35,CAPTURE_KEY_TOP+CAPTURE_Z_GAP-1000.4))
            dock=base.fuse(top,*legs,*additions).clean()
            if end=='DEPLOYED':
                hood_x=264. if side=='L'else 886.
                dock=dock.cut(cyl(4,8.35,(hood_x,1288.,CAPTURE_KEY_TOP+CAPTURE_Z_GAP-1))).clean()
            # Crossbearer top slots run alongX atYcybearer±20; use two
            # indexed axes per base. These known custom clearance holes
            # do not establish received slot-lip capacity.
            ys=(1260.,1300.)if end=='DEPLOYED'else(1480.,1520.)
            dock=cut(dock,[cyl(6.6,8.35,(pinx,yy,944.8))for yy in ys])
            stock=(f'Welded6.35mm steel:2x{xmax-xmin:g}x72 base/top;3x48.25x72 legs;'
                   f'1x60x{CAPTURE_KEY_TOP+CAPTURE_Z_GAP-1006.75:g} outerwall;'
                   f'1x{roof_end-roof_x:g}x60 roof;1x19.8x{CAPTURE_KEY_TOP+CAPTURE_Z_GAP-1000.4:g} endpointstop')
            if side=='L':stock+=';plus6.35mm steel1x60x12.55 innerguide'
            add(f'ATC_DOCK_{end}_{side}',dock,STEEL,stock=stock,
                notes='Finish seats/guides after welding. Nominal vertical and lower-tongue gap.15mm; left totalXgap.15mm. Fit .10-.20mm gap with indexed thin shims and verify fullstroke. Right key has1.2mm outerXfloat. Front stops deployed/rear stops parked. GeometricZcapture; axial preload depends on energized selectedslide/controller. No selflocking friction or powerloss axial retention claimed.')
    # Compact welded4mm storage hanger. The cover is lowered70mm left of
    # its final hooks, then inserted laterally under the two L keepers.
    hanger=box(322,1320,905.8,40,4,40).fuse(box(322,1324,905.8,40,93,4))
    for yy in(1389.,1409.):
        hanger=hanger.fuse(box(355,yy,703,4,8,202.8),box(343,yy,699,16,8,4))
        hanger=hanger.cut(cyl(4.5,6,(354,yy+4,715),(1,0,0)))
    hanger=cut(hanger,[cyl(6.6,6,(xx,1319,925.8),(0,1,0))for xx in(332.,352.)])
    add('ATC_COVER_STORAGE_HANGER',hanger.translate((20,0,0)),STEEL,stock='Welded4mmsteel40mmwideattachment+arm;two4x8x202.8verticalprongs;two16x8x4shelves',notes='FinaltwoM6holesX352/372,Z932.8 into front1280 crossbearer rear slot. Hook supports upper cover handle; use both L keepers.')
    for yy in(1393.,1413.):
        keeper=cyl(4,24,(340,yy,715),(1,0,0)).fuse(cyl(4,12,(340,yy,703))).clean().translate((20,0,0))
        add(f'ATC_COVER_KEEPER_{yy:g}',keeper,HARD,stock='4mm steelL keeper24x12;retainwithRclip',notes='Remove to service cover; closes anti-uplift/left escape around the stored handle. Actual pin/clip load qualification still held.')
    p=[(n,s.translate((0,0,GEOMETRY_RISE)),c)for n,s,c in p]
    p+=hood_parts(hood)
    for n,_,_ in hood_parts(hood):
        classes[n]='hood'
        stock='1.9mmsteelcover;exactfinishedpanelinindexedSTEP'
        if 'HANDLE'in n:stock='Welded6mmgrip40long +two6mmlegs;twohandles'
        elif 'SEAT_TAB'in n:stock='Welded20x20x1.9steelhoodtab;D4.5clearance;2total'
        elif 'REMOVABLE_M4x6'in n:stock='M4x6socketcapscrew;7ODx4head;2total'
        spec[n]=dict(stock=stock,ownership='new',notes='Thermal/splashcover,notsealed/thermallyqualified. TwoM4x6bolts through1.9tab into6.35fixedroof:4.1mmengagement/2.25mmreserve. Removebothboltsintoownedtoolstoragebeforelifting. No longspacersorarmclamps.')
    return tuple(p),classes,spec

def actual_atc_parts(deployment=0.,*,pins_withdrawn=False,hood='stored',include_allocations=False):
    parts=list(_build(float(deployment),bool(pins_withdrawn),hood)[0])
    return parts+acceptance_parts(deployment)if include_allocations else parts

def atc_metadata(deployment=0.,pins_withdrawn=False,hood='stored'):
    _,classes,spec=_build(float(deployment),bool(pins_withdrawn),hood)
    return dict(module_body_Y_mm=[MODULE_FRONT,MODULE_FRONT+311],reserved_motor_Y_mm=[MODULE_FRONT+311,MODULE_FRONT+367],
        frame_depth_mm=FRAME_DEPTH,stroke_mm=200,magazine_base_Z_mm=MAG_BASE,
        kit_capacity_XYZ_mm=[520,60,120],selected_kit='RapidChange4pocketER11; exact tier/interfaces unverified',
        pocket_centres=[[x,BODY_Y+30,MAG_BASE]for x in POCKET_X],
        pocket_plane_note='XYaxes fromdatedmanufacturerhousing; Zisbodybottomreference,notnutengagementplane',
        actual_kit_mount_pattern=dict(source='ER20_4_Standard_20240204.step',
            world_X_mm=list(MOUNT_X),world_Y_mm=[BODY_Y+10,BODY_Y+50],
            through_diameter_mm=6.35,counterbore_diameter_mm=11.,counterbore_depth_mm=7.),
        nominal_pocket_row_Y_mm=BODY_Y+30,
        pocket_centre_acceptance_X_mm=[347.5,802.5],pocket_centre_acceptance_Y_mm=[BODY_Y+5,1105.69794],
        retained_tool_below_base_max_mm=26.35,loaded_tool_projection_mm=[15,50],
        stock_plus_clamp_mm=40,bed_top_Z_mm=BED_TOP,minimum_travel_plane_Z_mm=1012.8,
        lowest_arm_material_Z_mm=ARM_BOTTOM,nominal_spindle_reference_Z0_mm=970,
        P50_flyover_gap_at200lift_mm=-39.15,P50_flyover_gap_at250lift_mm=10.85,minimum_P50_flyover_lift_mm=244.15,
        actual_delivered_motor_dimension_verified=False,actual_carriage_height_verified=False,
        slide_base_channel_nut_fit_verified=False,carriage4M6_pattern_verified=False,
        RapidChange_vendor_CAD_available=True,manufacturer_external_housing_source_width_mm=60.,
        manufacturer_external_housing_source_size_XYZ_mm=[271.2,60.,80.8],
        source_housing_and_pocket_mount_axes_verified=True,received_current_kit_revision_verified=False,
        actual_pockets_nut_IR_servo_datums_verified=False,
        automatic_deploy_pin_release='NOT_APPLICABLE_PASSIVE_CAPTURE_KEYS',manual_endpoint_clamping=False,
        passive_endpoint_capture_keys=True,endpoint_nominal_vertical_gap_mm=CAPTURE_Z_GAP,
        left_key_nominal_total_X_gap_mm=.15,finish_fit_gap_range_mm=[.10,.20],
        right_key_outer_X_float_mm=1.2,requires_energized_axis_axial_preload=True,
        axis_holding_force_qualified=False,power_loss_axial_lock=False,
        operating_interlocks=['spindle_zero_speed_before_magazine_motion','head_flyover_clearance',
            'wood_mode_and_hood_stored','deployed_endpoint_confirmed','both_capture_seats_confirmed',
            'selected_slide_energized_and_holding','abort_tool_change_on_sensor_or_energy_loss',
            'tool_loaded_unloaded_and_toolsetter_confirmed'],
        selected_slide_ownership='Owned motion reported; contents/revision/motor still uninspected',
        kit_owned=False,classified_parts=classes,manufacturing_specs=spec,
        fabrication_release=False,operating_release=False)
