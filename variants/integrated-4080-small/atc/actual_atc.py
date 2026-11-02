"""Selected311mm /200stroke ATC slide on a simple removable pinned carrier.

Only the selected slide's published outer dimensions are represented. The
RapidChange family acceptance volumes are separate from manufactured solids;
actual endcap/pocket geometry is not invented. No generic MGN/belt axis.
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
MODULE_FRONT=1230.;MODULE_OVERALL=311.;TRAVEL=200.;MAG_BASE=1039.15
BED_TOP=967.8;STOCK_PLUS_CLAMP=40.;SAFE_GAP=5.;FRAME_DEPTH=1600.
MODULE_BASE=959.15;CARRIAGE_HEIGHT_ALLOCATION=47.3
CARRIER_BOTTOM=1026.45;ARM_BOTTOM=1013.75
GEOMETRY_RISE=7.;KIT_HEIGHT=120.;HOOD_ROTATE_CENTRE_Z=1590.35;HOOD_LOWER_DISTANCE=1182.35
BEAM_CENTRE=MODULE_FRONT+38.;BODY_Y=1070.
FRAME_INNER_LEFT,FRAME_INNER_RIGHT=25.8,1124.2
PIN_X=(315.,835.);HOOD_STORED_OFFSET_X=-300.;HOOD_STORED_OFFSET_Y=70.

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

def _hood_native(released=False):
    front=cut(box(275,1277,1005.9,600,1.9,165.1),[box(x,1276,1004.9,60,4,13.85)for x in(280.,810.)])
    p=[('ATC_COVER_ROOF',box(275,1277,1171,600,91,1.9),STEEL),
       ('ATC_COVER_FRONT',front,STEEL),
       ('ATC_COVER_SIDE_L',box(275,1278.9,1005.9,1.9,87.2,165.1),STEEL),
       ('ATC_COVER_SIDE_R',box(873.1,1278.9,1005.9,1.9,87.2,165.1),STEEL)]
    rear=box(275,1366.1,1005.9,600,1.9,165.1)
    rear=cut(rear,[box(x,1365.1,1004.9,50,4,26.55)for x in(290.,810.)])
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
    p=[(n,s.cut(cyl(4.5,4,(274 if n.endswith('_L') else 872.1,1310,1020.1),(1,0,0))).clean(),c)
       if n in('ATC_COVER_SIDE_L','ATC_COVER_SIDE_R')else(n,s,c)for n,s,c in p]
    for side,x,direction in(('L',276.9,(1,0,0)),('R',873.1,(-1,0,0))):
        spacer=cyl(10,18.1,(x,1310,1020.1),direction).cut(cyl(4.5,20.1,(x-direction[0],1310,1020.1),direction)).clean()
        p.append(('ATC_COVER_WELDED_CLAMP_SPACER_'+side,spacer,STEEL))
        face=275. if side=='L' else 875.
        shank=cyl(4,25,(face,1310,1020.1),direction)
        head=cyl(12,4,(face-direction[0]*4,1310,1020.1),direction)
        screw=shank.fuse(head).clean()
        if released:screw=screw.translate((-direction[0]*6,0,0))
        p.append(('ATC_COVER_M4x25_THUMB_'+side,screw,HARD))
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
        return [(n,s.translate(((-6 if n.endswith('_L') else 6)*t,0,0))if n.startswith('ATC_COVER_M4x25_THUMB_')else s,c)
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
    return [('ATC_RAPIDCHANGE_KIT_CAPACITY_NOT_VENDOR_CAD',box(315,BODY_Y+deployment,MAG_BASE,520,60,KIT_HEIGHT),ALLOC),
            ('ATC_RETAINED_TOOLS_CAPACITY_NOT_ACTUAL_TOOLS',box(340,BODY_Y+2.5+deployment,1012.8,470,52.4,26.35),ALLOC)]

@lru_cache(None)
def _build(deployment=0.,pins_withdrawn=False,hood='stored'):
    if not 0<=deployment<=TRAVEL:raise ValueError('ATC travel0..200')
    if deployment not in(0.,200.)and not pins_withdrawn:raise ValueError('Withdraw both locating/clamping bolts before motion')
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
    beam=source_frame.bar(275,BEAM_CENTRE-40,mag_base,'X',600,flat=True)
    beam=cut(beam,[cyl(18,42,(x,BEAM_CENTRE,mag_base-1))for x in PIN_X])
    add('ATC_4080_MOVING_CROSSCARRIER',beam,EX,True,stock='4080 x600mm laid80Yx40Z;2xD18vertical pin/head-accessbores',notes='Conditional Iweak>=134000mm4 before local machining; modified section, slot and bolt joint capacities unqualified. Do not replace with a flat unsupported bar.')
    centre=box(530,BEAM_CENTRE-30,carrier_bottom,90,60,12.7)
    for yy in(BEAM_CENTRE-20,BEAM_CENTRE+20):
        centre=cut(centre,[cyl(6.6,14.7,(575,yy,carrier_bottom-1)),cyl(11,3.4,(575,yy,carrier_bottom))])
        # External grip only. The selected4080 must accept10.7mm maximum
        # internal projection and a compatibleM6 nut; no false die is cut.
        b=cyl(6,9.3,(575,yy,1022.85)).fuse(cyl(10.5,3.3,(575,yy,1019.55))).clean()
        add(f'ATC_CENTRE_M6x20_BUTTON_EXTERNAL_GRIP_{yy:g}',b,HARD,True,stock='M6x20button screw; externalgrip9.3, threadprojection10.7 held',notes='Button head3.3 in3.4counterbore. Actual slot lip/nut/cavity fit must permit the declared projection.')
    add('ATC_CARRIAGE_TRANSFER_PLATE',centre,AL,True,stock='90x60x12.7mm6061-T6, custom centre2holes only',notes='Supplier4-M6 mating face remains a transfer-drill blank. No claimed complete attachment to unmeasured OEM carriage.')
    for side,x,pinx,slotx in(('L',275.,315.,285.),('R',815.,835.,865.)):
        endplate=box(x,BEAM_CENTRE-30,carrier_bottom,60,60,12.7)
        holes=[cyl(8,14.7,(pinx,BEAM_CENTRE,carrier_bottom-1))]
        holes += [cyl(6,14.7,(pinx,yy,carrier_bottom-1))for yy in(BEAM_CENTRE-13,BEAM_CENTRE+12)]
        for yy in(BEAM_CENTRE-20,BEAM_CENTRE+20):
            holes.append(cyl(6.6,14.7,(slotx,yy,carrier_bottom-1)))
            for k,zz in enumerate((1016.25,1017.85),1):
                washer=cyl(12,1.6,(slotx,yy,zz)).cut(cyl(6.6,3.6,(slotx,yy,zz-1)))
                add(f'ATC_END_M6_WASHER_{side}_{yy:g}_{k}',washer,HARD,True,stock='M6washer12ODx1.6;8total')
            b=cyl(6,15.9,(slotx,yy,1016.25)).fuse(cyl(10,6,(slotx,yy,1010.25))).clean()
            add(f'ATC_END_M6x25_EXTERNAL_GRIP_{side}_{yy:g}',b,HARD,True,stock='M6x25socket screw; externalgrip15.9+9.1threadprojection held',notes='Actual received slot nut, lip and9.1mm inner projection require fit verification; no slot thread geometry invented.')
        add('ATC_CROSSCARRIER_END_PLATE_'+side,cut(endplate,holes),AL,True,stock='60x60x12.7mm6061-T6',notes='Nominal8mmreamed locatorhole,2M6arm taps,2M6slotfixingclearanceholes. Specify compatible ground pin/H7 bore as actual fit.')
    for side,x,pinx in(('L',295.,315.),('R',815.,835.)):
        arm=box(x,BODY_Y,arm_bottom,40,BEAM_CENTRE+44-BODY_Y,12.7)
        holes=[cyl(8.1,14.7,(pinx,BEAM_CENTRE,arm_bottom-1))]
        for y in(BEAM_CENTRE-13,BEAM_CENTRE+12):
            holes += [cyl(6.6,14.7,(pinx,y,arm_bottom-1)),cyl(10.5,6.1,(pinx,y,arm_bottom))]
        for y in(BODY_Y+15,BODY_Y+50):holes += [cyl(6.6,14.7,(pinx,y,arm_bottom-1)),cyl(10.5,6.1,(pinx,y,arm_bottom))]
        arm=cut(arm,holes)
        ox=295 if side=='L' else 855
        direction=(1,0,0)if side=='L'else(-1,0,0)
        arm=arm.cut(cyl(4,8,(ox,BODY_Y+40,1013.1),direction)).clean()
        add('ATC_FORWARD_ARM_'+side,arm,AL,True,stock=f'40x{BEAM_CENTRE+44-BODY_Y:g}x12.7mm6061-T6',notes='Underside M6 head recesses6.1deep; standardM6x20 finished underhead19mm. Final lowest head1013.85, above1012.8 travel plane.')
        pad=box(305 if side=='L' else 815,BODY_Y,1019.45,30,60,12.7)
        pad=cut(pad,[cyl(6,14.7,(pinx,y,1018.45))for y in(BODY_Y+15,BODY_Y+50)])
        add('ATC_KIT_ENDCAP_TRANSFER_PAD_'+side,pad,AL,True,stock='30x60x12.7mm6061-T6 transfer pad',notes='OEM top mounting pattern deliberately blank. Not a claimed RapidChange flange/pocket drawing. Fit supplied kit/endcap drawing before drill release.')
        for y in(BODY_Y+15,BODY_Y+50,BEAM_CENTRE-13,BEAM_CENTRE+12):
            under=1012.85
            screw=cyl(6,19,(pinx,y,under)).fuse(cyl(10,6,(pinx,y,under-6))).clean()
            add(f'ATC_ARM_M6_FINISHED19_{side}_{y:g}',screw,HARD,True,stock='M6x20 socket screw, finish19mm underhead;8total',notes='Web6.6mm, nominal engagement12.4mm, top reserve0.3mm. Thread/pilot strength still material/process qualification.')
    # Four compact steel U docks: fixed contact seats remove tool-change
    # reaction from motor holding torque. Two reused shoulder bolts clamp
    # whichever endpoint is active. Right precision bore is relieved in X.
    for end,cy in(('DEPLOYED',BEAM_CENTRE),('PARKED',BEAM_CENTRE+200)):
        for side,x,pinx in(('L',285.,315.),('R',815.,835.)):
            base=box(x,cy-30,945.8,50,72,6.35)
            top=box(x,cy-30,1000.4,50,72,6.35)
            if end=='DEPLOYED'and side=='L':top=top.fuse(box(x,cy-36.35,1000.4,6.35,6.35,6.35)).clean()
            legs=[box(xx,cy-30,952.15,6.35,72,48.25)for xx in(x,x+43.65)]
            dock=base.fuse(top,*legs).clean()
            slot=xslot if side=='R'else None
            upper=xslot(8,1.,4.6,(pinx,cy,1002.15))if slot else cyl(8,4.6,(pinx,cy,1002.15))
            lower=xslot(6.6,1.,2.75,(pinx,cy,999.4))if slot else cyl(6.6,2.75,(pinx,cy,999.4))
            dock=cut(dock,[upper,lower])
            # Crossbearer top slots run alongX atYcybearer±20; use two
            # indexed axes per base. These known custom clearance holes
            # do not establish received slot-lip capacity.
            ys=(1260.,1300.)if end=='DEPLOYED'else(1480.,1520.)
            dock=cut(dock,[cyl(6.6,8.35,(pinx,yy,944.8))for yy in ys])
            add(f'ATC_DOCK_{end}_{side}',dock,STEEL,stock='Welded6.35mm steelU:2x50x72 +2x48.25x72;ream after weld',notes='Finaltop1013.75,bottom952.8. Deployedlefttop includes6.35x6.35frontstopoverhang. Left nominal8mmH7 locator/6.6thread clearance; right8mmY-width with1mm extraX relief. Match source steel grade/weld capacity and actual shim/seat preload.')
    for name,x,y in(('DEPLOYED',285.,BEAM_CENTRE-36.35),('PARKED',858.65,BEAM_CENTRE+230)):
        # Faces contact only the crossbar extension beyond the40mm arms.
        stop=box(x,y,1006.75,6.35,6.35,25.4)
        add('ATC_HARD_STOP_'+name,stop,STEEL,stock='6.35x6.35x25.4 steel stop, welded to matching receiver',notes='Not the locating pin. Fit contact face/shim after alignment; motor approaches at reduced speed.')
    if not pins_withdrawn:
        for side,x in(('L',315.),('R',835.)):
            pin=cyl(8,30,(x,BEAM_CENTRE+deployment,1002.15)).fuse(cyl(13,5.5,(x,BEAM_CENTRE+deployment,1032.15)),cyl(6,11,(x,BEAM_CENTRE+deployment,991.15))).clean()
            # Already placed in current state; do not add deployment again.
            add('ATC_ENDPOINT_SHOULDER_BOLT_'+side,pin,HARD,stock='ISO7379 shoulder8x30/M6x11;actual dimensions to match',notes='30mm locating shoulder; receiver bearing4.6mm. M6 nut+washer retain against uplift; manual setup, not an automatic pin release.')
            washer=cyl(12,1.6,(x,BEAM_CENTRE+deployment,998.8)).cut(cyl(6.6,3.6,(x,BEAM_CENTRE+deployment,997.8)))
            nut=cq.Workplane('XY').polygon(6,11.547005).extrude(5).val().translate((x,BEAM_CENTRE+deployment,993.8)).cut(cyl(6,7,(x,BEAM_CENTRE+deployment,992.8)))
            add('ATC_PIN_WASHER_'+side,washer,HARD,stock='M6washer12ODx1.6')
            add('ATC_PIN_NUT_'+side,nut,HARD,stock='M6nut5high;actualgrade/threadretentionqualification')
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
        elif 'SPACER'in n:stock='Steel10ODx4.5IDx18.1weldedspacer;drillroundstock'
        elif 'THUMB'in n:stock='M4x25thumbscrew,12ODx4head;retract6mmforswapping'
        spec[n]=dict(stock=stock,ownership='new',notes='Removable thermal/splash cover;not sealed or thermally qualified. TwoM4clamps engage5mm into arms; withdraw beforelifting.')
    return tuple(p),classes,spec

def actual_atc_parts(deployment=0.,*,pins_withdrawn=False,hood='stored',include_allocations=False):
    parts=list(_build(float(deployment),bool(pins_withdrawn),hood)[0])
    return parts+acceptance_parts(deployment)if include_allocations else parts

def atc_metadata(deployment=0.,pins_withdrawn=False,hood='stored'):
    _,classes,spec=_build(float(deployment),bool(pins_withdrawn),hood)
    return dict(module_body_Y_mm=[MODULE_FRONT,MODULE_FRONT+311],reserved_motor_Y_mm=[MODULE_FRONT+311,MODULE_FRONT+367],
        frame_depth_mm=FRAME_DEPTH,stroke_mm=200,magazine_base_Z_mm=MAG_BASE,
        kit_capacity_XYZ_mm=[520,60,120],selected_kit='RapidChange4pocketER11; exact tier/interfaces unverified',
        pocket_centres=None,actual_kit_mount_pattern=None,
        nominal_pocket_row_Y_mm=BODY_Y+30,
        pocket_centre_acceptance_X_mm=[347.5,802.5],pocket_centre_acceptance_Y_mm=[BODY_Y+5,1105.69794],
        retained_tool_below_base_max_mm=26.35,loaded_tool_projection_mm=[15,50],
        stock_plus_clamp_mm=40,bed_top_Z_mm=BED_TOP,minimum_travel_plane_Z_mm=1012.8,
        lowest_arm_material_Z_mm=ARM_BOTTOM,nominal_spindle_reference_Z0_mm=970,
        P50_flyover_gap_at200lift_mm=-39.15,P50_flyover_gap_at250lift_mm=10.85,minimum_P50_flyover_lift_mm=244.15,
        actual_delivered_motor_dimension_verified=False,actual_carriage_height_verified=False,
        slide_base_channel_nut_fit_verified=False,carriage4M6_pattern_verified=False,
        RapidChange_vendor_CAD_available=False,actual_pockets_nut_IR_servo_datums_verified=False,
        automatic_deploy_pin_release=False,manual_endpoint_clamping=True,
        selected_slide_ownership='Owned motion reported; contents/revision/motor still uninspected',
        kit_owned=False,classified_parts=classes,manufacturing_specs=spec,
        fabrication_release=False,operating_release=False)
