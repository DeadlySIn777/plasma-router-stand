"""XR1 six-post frame. Millimetres; profile envelopes are not vendor die solids.

Only direct-bearing joints are used for gravity loads. The angle envelopes
require formed/purchased one-piece angle; a pair of touching plates is not an
equivalent part. Frame section properties are screened separately.
"""
from functools import lru_cache
from math import hypot
import cadquery as cq
import params as P

DARK=(.16,.20,.23); SILVER=(.65,.71,.74); BLUE=(.18,.39,.48); FOOT=(.30,.33,.35)
TOP_PLATE_Z0=933.
PAN_ANGLE_THICKNESS=6.35
ARM_LENGTH=75.2
ARM_BOTTOM,ARM_TOP=841.65,881.65
ARM_ANGLE_LEG=32.
BRACE_NOMINAL_THICKNESS=1.9

def box(x,y,z,dx,dy,dz):
    return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))

def cyl(r,h,p,d=(0,0,1)):
    return cq.Solid.makeCylinder(r,h,cq.Vector(*p),cq.Vector(*d))

def drilled(s,holes,r=3.3):
    for p,d,h in holes:s=s.cut(cyl(r,h,p,d))
    return s.clean()

@lru_cache(None)
def local4080(length):
    """40X x80Y profile along Z; shallow grooves identify mounting faces only.

    Actual cavities, lip thickness, mass, I and J are not inferred from this
    decorative model. Slot centres follow the selected 20/60 mm drawing.
    """
    s=box(0,0,0,40,80,length)
    for y in (20.,60.):
        for x in (-1.,38.):s=s.cut(box(x,y-4.1,-1,3,8.2,length+2))
        s=s.cut(cyl(3.4,length+2,(20,y,-1)))
    for y in (-1.,78.):s=s.cut(box(15.9,y,-1,8.2,3,length+2))
    return s.clean()

def bar(x,y,z,axis,length,flat=False):
    s=local4080(length)
    if axis in ('Y','X'):
        s=s.rotate((0,0,0),(1,0,0),-90).translate((0,0,80))
        if axis=='X':s=s.rotate((0,0,0),(0,0,1),-90).translate((0,40,0))
    if flat:
        assert axis=='X'
        # Short ledger arm only: 80Y wide,40Z deep. Main beams are80Z.
        s=s.rotate((0,0,0),(1,0,0),90).translate((0,80,0))
    return s.translate((x,y,z))

def strap(a,b,normal,width=30.,thickness=BRACE_NOMINAL_THICKNESS):
    delta=cq.Vector(*b)-cq.Vector(*a); ln=delta.Length
    wp=cq.Workplane(cq.Plane(origin=a,xDir=delta.normalized().toTuple(),normal=normal))
    s=wp.center(ln/2,0).slot2D(ln+width,width).extrude(thickness).val()
    for p in (a,b):
        start=tuple(v+(thickness+1)*n for v,n in zip(p,normal))
        s=s.cut(cyl(3.3,thickness+2,start,tuple(-n for n in normal)))
    return s.clean()

def bearing_angle(x,cy,seat_top,seat_length,leg_height,left):
    """One-piece angle, against inner column face; its seat bears the beam.

    Vertical web ends at seat top, below supported beam. Two bolts into each
    mounting face. Angle bend radius and hole-edge clearance need shop drawing
    qualification; geometry here is a conservative square-corner envelope.
    """
    t=PAN_ANGLE_THICKNESS
    xx=x if left else x-seat_length
    vx=x if left else x-t
    s=box(xx,cy-40,seat_top-t,seat_length,80,t).fuse(
        box(vx,cy-40,seat_top-leg_height,t,80,leg_height)).clean()
    post_z=seat_top-(40. if leg_height==80. else 20.)
    # pan beam has one bottom slot in Y; flat arms have two.
    if leg_height==80.:
        seat_xy=[(x+(35 if left else -35),cy),(x+(65 if left else -65),cy)]
    else:
        seat_xy=[(x+(25 if left else -25),cy-20),(x+(25 if left else -25),cy+20)]
    holes=[((vx-1,yy,post_z),(1,0,0),t+2) for yy in (cy-20,cy+20)]
    holes += [((xx0,yy,seat_top-t-1),(0,0,1),t+2) for xx0,yy in seat_xy]
    return drilled(s,holes)

def front_channel_notch(s,left):
    """Front-corner relief for the upright70.8mm cassette channel.

    Root blank and remaining ledgers are unchanged. Local profile/angle stress,
    lip capacity and manufacturing edge radii require separate qualification.
    """
    x=108. if left else 1018.
    return s.cut(box(x,59.,-1.,24.,13.8,2002.)).clean()

def frame_parts():
    out=[]
    def add(n,s,c=SILVER):out.append((n,s,c))
    def add_foot(side,x,cy,key,into_base=False):
        ft=P.FOOT_PLATE_TOP-P.FOOT_PLATE_BOTTOM
        plate=box(x,cy-40,P.FOOT_PLATE_BOTTOM,40,80,ft)
        rows=(cy-20,cy+20)
        if into_base and cy==1410.:rows=(1390.,1427.)
        plate=drilled(plate,[((x+20,yy,P.FOOT_PLATE_BOTTOM-1),(0,0,1),ft+2) for yy in rows],3.3 if into_base else 4.25)
        # Nominal M8 threaded envelope; drill6.8 and tapM8 in manufacture.
        plate=plate.cut(cyl(4,ft+2,(x+20,cy,P.FOOT_PLATE_BOTTOM-1))).clean()
        add(f'XR_FOOT_PLATE_{side}_{key}',plate,BLUE)
        foot=cyl(25.4,9,(x+20,cy,0)).fuse(cyl(4,P.FOOT_PLATE_TOP-1-9,(x+20,cy,9))).clean()
        nz=P.FOOT_PLATE_BOTTOM-6.8
        nut=cq.Workplane('XY').polygon(6,15.011).extrude(6.8).val().translate((x+20,cy,nz))
        nut=nut.cut(cyl(4,8,(x+20,cy,nz-1))).clean()
        add(f'XR_RATED_FOOT_{side}_{key}_ALLOWANCE',foot,FOOT)
        add(f'XR_FOOT_LOCKNUT_{side}_{key}_ALLOWANCE',nut,FOOT)
    for side,x in (('L',P.LEFT_X),('R',P.RIGHT_X)):
        left=side=='L'; outer=x if left else x+40; sg=-1 if left else 1
        add(f'XR_EX_{side}_HEADER',bar(x,0,P.UPPER_BOTTOM,'Y',P.Y_LENGTH),DARK)
        add(f'XR_EX_{side}_REAR_FOOTBASE',bar(x,1140.,P.FOOT_PLATE_TOP,'Y',300.),DARK)
        for i,cy in enumerate(P.POST_CENTRES_Y,1):
            rear=i==3
            pb=P.FOOT_PLATE_TOP+(80. if rear else 0.)
            add(f'XR_EX_{side}_POST_{i}',bar(x,cy-40,pb,'Z',P.UPPER_BOTTOM-pb),DARK)
            if rear:
                add_foot(side,x,cy,'3A',True);add_foot(side,x,1410.,'3B',True)
                for face,px in (('OUT',outer-6 if left else outer),('IN',x+40 if left else x-6)):
                    baseplate=box(px,1140.,119.5,6,80,80)
                    holes=[((px-1,yy,zz),(1,0,0),8) for yy in (1160.,1200.) for zz in (129.5,179.5)]
                    add(f'XR_REAR_BASE_FISHPLATE_{side}_{face}',drilled(baseplate,holes),BLUE)
            else:add_foot(side,x,cy,str(i))
            px=outer-6 if left else outer
            plate=box(px,cy-40,TOP_PLATE_Z0,6,80,80)
            holes=[((px-1,yy,zz),(1,0,0),8) for yy in (cy-20,cy+20) for zz in (943.,993.)]
            add(f'XR_TOP_FISHPLATE_{side}_{i}',drilled(plate,holes),BLUE)
            inner=P.INNER_LEFT if left else P.INNER_RIGHT
            pan_angle=bearing_angle(inner,cy,P.PAN_BEARER_BOTTOM,80.,80.,left)
            if i==1:pan_angle=front_channel_notch(pan_angle,left)
            add(f'XR_PAN_BEARING_ANGLE_{side}_{i}',pan_angle,BLUE)
            ax=P.INNER_LEFT if left else P.INNER_RIGHT-ARM_LENGTH
            arm=bar(ax,cy-40,ARM_BOTTOM,'X',ARM_LENGTH,flat=True)
            if i==1:arm=front_channel_notch(arm,left)
            add(f'XR_EX_DRY_ARM_{side}_{i}',arm,DARK)
            add(f'XR_DRY_ARM_ANGLE_{side}_{i}',bearing_angle(inner,cy,ARM_BOTTOM,40.,ARM_ANGLE_LEG,left),BLUE)
        # Paired uncoated steel straps; one tension diagonal is credited under
        # each load direction. A3mm spacer separates the crossing straps.
        for bay,(y1,y2,lo,hi) in enumerate(((80.,610.,160.,900.),(650.,1200.,240.,900.)),1):
            for j,(za,zb,offset) in enumerate(((lo,hi,0.),(hi,lo,3.)),1):
                xx=outer+sg*offset
                add(f'XR_SIDE_X_{side}_{bay}_{j}',strap((xx,y1,za),(xx,y2,zb),(sg,0,0)),BLUE)
                if offset:
                    for k,(yy,zz) in enumerate(((y1,za),(y2,zb)),1):
                        sp=cyl(9,3,(outer,yy,zz),(sg,0,0)).cut(cyl(3.3,4,(outer,yy,zz),(sg,0,0)))
                        add(f'XR_SIDE_SPACER_{side}_{bay}_{k}',sp.clean())
    for i,cy in enumerate(P.POST_CENTRES_Y,1):
        add(f'XR_EX_PAN_X_{i}',bar(P.INNER_LEFT,cy-20,P.PAN_BEARER_BOTTOM,'X',P.CROSS_LENGTH),DARK)
    # The front crossing ends atZ375 (strap edge), below theZ400storagefloor.
    # All front transfer space aboveZ400 remains free of transverse frame ties.
    for name,y,normal,lo,hi in (('FRONT',60.,-1,120.,360.),('REAR',1220.,1,175.,900.)):
        for j,(za,zb,offset) in enumerate(((lo,hi,0.),(hi,lo,3.)),1):
            yy=y+normal*offset
            a=(P.LEFT_X+20,yy,za);b=(P.RIGHT_X+20,yy,zb)
            add(f'XR_END_X_{name}_{j}',strap(a,b,(0,normal,0)),BLUE)
            if offset:
                for k,(xx,zz) in enumerate(((a[0],za),(b[0],zb)),1):
                    sp=cyl(9,3,(xx,y,zz),(0,normal,0)).cut(cyl(3.3,4,(xx,y,zz),(0,normal,0)))
                    add(f'XR_END_SPACER_{name}_{k}',sp.clean())
    return out

def design_metadata():
    return {
        'profile_cuts_mm':{'continuous_posts':[P.POST_LENGTH]*4+[P.POST_LENGTH-80]*2,'Y_headers':[P.Y_LENGTH]*2,
                           'pan_X_bearers':[P.CROSS_LENGTH]*3,'flat_ledger_arms':[ARM_LENGTH]*6,'rear_footbases':[300.]*2},
        'finished_profile_length_mm':6*P.POST_LENGTH-160+2*P.Y_LENGTH+3*P.CROSS_LENGTH+6*ARM_LENGTH+600,
        'primary_joint_stations':{'top_fishplates':24,'pan_angles':24,'dry_arm_angles':24,'rear_footbase_fishplates':16},
        'front_transfer_reliefs':{'count':4,'parts':'Two front dry-arm tips and two front pan-angle seats',
            'left_xy_mm':[108,132,59,72.8],'right_xy_mm':[1018,1042,59,72.8],
            'channel_clearance_to70p8_upright_mm':2.,'ledger_attachment_stations':22,
            'omitted_ledger_bolts_xy_mm':[[116,80],[1034,80]],
            'qualification':'Qualify local notch stress, remaining slot lips, contact support, edge radii and3-station front-ledger anti-roll joints. No member property is inferred from the relieved envelope.'},
        'brace_steel':{'width_mm':30,'thickness_mm':BRACE_NOMINAL_THICKNESS,'minimum_screen_thickness_mm':1.8,
                      'count':12,'hole_diameter_mm':6.6,
                      'tension_only':True,'front_highest_nominal_edge_z_mm':375},
        'foot_plates':{'count':8,'blank_mm':[40,80,P.FOOT_PLATE_TOP-P.FOOT_PLATE_BOTTOM],
                       'core_clearance_diameter_mm':8.5,'core_rows_y_from_front_mm':[20,60],
                       'rear_base_clearance_diameter_mm':6.6,'rear_base_rows_y_mm':[[1160,1200],[1390,1427]],
                       'central_adjuster_y_mm':40,'central_adjuster_thread':'M8, nominal CAD diameter8; drill6.8/tapM8',
                       'nominal_thread_engagement_mm':P.FOOT_PLATE_TOP-P.FOOT_PLATE_BOTTOM-1,
                       'qualification':'Verify end-core taps, central M8 thread stripping, adjuster rating, plate bending and floor friction.'},
        'angle_requirement':'One-piece purchased or formed angle. Square-corner CAD envelope; qualify real bend radius, fastener seats and capacities.',
        'profile_model':'Nominal mounting envelope only. Not a section-property or mass model.',
        'release':False}
