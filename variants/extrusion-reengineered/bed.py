"""XR1 removable plywood torsion-box bed, fixed mild-steel pan and closed storage.

Engineering envelopes in mm. No purchasing or fabrication release is implied.
Tracks, threads, glue lines, plasma nozzle, cables and shielding require real parts.
"""
from math import pi, sqrt
from functools import lru_cache
import cadquery as cq
import params as P

AL=(.63,.69,.72); PLY=(.65,.50,.32); MDF=(.73,.62,.43)
HOT=(.29,.36,.40); LIGHT=(.71,.75,.77); PIN=(.25,.31,.34)
PAN_T=1.9
SLAT_T=1.9
SLAT_X0=135.
SLAT_LENGTH=880.
CORE=39.05
BOTTOM=12.7
TOP=12.7
WEAR=6.35
BOX_H=BOTTOM+CORE+TOP
CASSETTE_H=BOX_H+WEAR
WEB=9.
# Seven continuous webs leave no more than45.75mm unsupported top-skin gap.
WEB_CENTRES=(4.5,19.,73.75,128.5,183.25,238.,252.5)
CROSS_CENTRES=tuple(9.+(P.PANEL_WIDTH-18.)*i/7 for i in range(1,7))
TRACK_CENTRES=(19.,238.)
TRACK_X0,TRACK_LENGTH,TRACK_W,TRACK_H=162.,826.,19.,12.7
TRACK_BOLTS=(190.,430.,720.,960.)
SKIM=(190.,960.,141.4,1101.4)
STORE_Y=360.
STORE_LEVELS=(400.,475.8,551.6,627.4)
TRANSFER_FRONT_Y=CASSETTE_H
TRANSFER_FLAT_BOTTOM=970.
TRANSFER_LOW_BOTTOM=400.

def box(x,y,z,dx,dy,dz): return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cyl(x,y,z,r,h,d=(0,0,1)): return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*d))
def fuse(parts): return parts[0].fuse(*parts[1:]).clean()
def cutmany(s,holes):
    return s.cut(fuse(holes)).clean() if holes else s.clean()
def pose_shape(s,y,z,angle=0.):
    return s.rotate((0,0,0),(1,0,0),angle).translate((0,y,z))
def pan_floor_z(y): return P.PAN_FLOOR_FRONT+P.PAN_SLOPE*(y-P.PAN_Y0)
def yz(x,w,points):
    pp=[cq.Vector(x,y,z) for y,z in points]
    return cq.Solid.extrudeLinear(cq.Wire.makePolygon(pp+[pp[0]]),[],cq.Vector(w,0,0))

@lru_cache(None)
def cassette_local_parts(index):
    """Local Y0..257,Z0..70.8, with world X109..1041 preserved."""
    p=[]; add=lambda n,s,c:p.append((f'CAS{index+1}_'+n,s.clean(),c))
    x0,w,l=P.PANEL_X,P.PANEL_WIDTH,P.PANEL_LENGTH
    shells=[box(x0,0,0,w,l,BOTTOM),box(x0,0,BOTTOM+CORE,w,l,TOP)]
    for cy in WEB_CENTRES: shells.append(box(x0,cy-WEB/2,BOTTOM,w,WEB,CORE))
    # Full end walls and six internal diaphragms; glued not merely dry-stacked.
    for cx in (x0+WEB/2,x0+w-WEB/2,*[x0+q for q in CROSS_CENTRES]):
        shells.append(box(cx-WEB/2,0,BOTTOM,WEB,l,CORE))
    crate=fuse(shells)
    holes=[]
    # Lifting grips in low-moment end zones, plus front recessed pulls for shelf insertion.
    for x in (132.,994.): holes.append(box(x,90,-.1,24,70,BOX_H+.2))
    for x in (250.,820.): holes.append(box(x,-.1,22.,80,14.1,20.))
    for cy in TRACK_CENTRES:
        holes.append(box(TRACK_X0-.1,cy-TRACK_W/2-.1,BOX_H-6.35,
                         TRACK_LENGTH+.2,TRACK_W+.2,6.55))
        for x in TRACK_BOLTS:
            holes.append(box(x-10,cy-10,-.1,20,20,9.625))
            holes.append(cyl(x,cy,-.1,4.,BOX_H+1))
    for x in (117.5,1032.5):
        for y in (40.,217.):
            holes.append(box(x-8,y-12.5,-.1,16,25,3.275))
    for x in (117.5,1032.5): holes.append(cyl(x,128.5,-.1,5.,BOX_H+.2))
    add('GLUED_PLY_BOX_12p7_12p7_9_WEB',cutmany(crate,holes),PLY)
    for x in (117.5,1032.5):
        sleeve=cyl(x,128.5,0,5.,BOX_H).cut(cyl(x,128.5,-.1,3.3,BOX_H+.2))
        add(f'CLAMP_COMPRESSION_SLEEVE_{int(x)}_OD10_ID6p6',sleeve,AL)
    for k,cy in enumerate(TRACK_CENTRES,1):
        z=BOX_H-6.35
        track=box(TRACK_X0,cy-TRACK_W/2,z,TRACK_LENGTH,TRACK_W,TRACK_H)
        # Schematic undercut: verify purchased die, lip capacity and nut fit.
        track=track.cut(box(TRACK_X0-.1,cy-6.5,z+3.5,TRACK_LENGTH+.2,13.,7.2))
        track=track.cut(box(TRACK_X0-.1,cy-3.5,z+10.7,TRACK_LENGTH+.2,7.,2.1))
        for j,x in enumerate(TRACK_BOLTS,1):
            track=track.cut(cyl(x,cy,z-.1,2.75,3.7))
            track=track.cut(cq.Solid.makeCone(2.75,4.8,2.05,
                               cq.Vector(x,cy,z+1.45),cq.Vector(0,0,1)))
            block=box(x-10,cy-10,0,20,20,9.525).cut(cyl(x,cy,-.1,2.50,9.8))
            add(f'TRACK{k}_BACKING_BLOCK{j}_AL_STOCK_ALLOCATION_PENDING',block,AL)
            length=z-9.525
            tube=cyl(x,cy,9.525,4.,length).cut(cyl(x,cy,9.425,2.75,length+.2))
            add(f'TRACK{k}_COMPRESSION_TUBE{j}_OD8_ID5p5',tube,AL)
            # M5x60 flathead envelope, blind thread in9.525Al block.
            head_top=z+3.5
            screw=fuse([cyl(x,cy,head_top-60,2.45,57.95),
                cq.Solid.makeCone(2.45,4.75,2.05,cq.Vector(x,cy,head_top-2.05),cq.Vector(0,0,1))])
            add(f'TRACK{k}_M5x60_VERIFY_GRIP_{j}',screw,PIN)
        add(f'TRACK{k}_AL_T_SLOT_DIE_ENVELOPE',track,AL)
    # Three hard datum seats plus a fourth adjustable support. Metal, not MDF,
    # receives repeated docking contact. No pin bore is asserted as a tolerance.
    for x in (117.5,1032.5):
        for y in (40.,217.):
            pad=box(x-8,y-12.5,0,16,25,3.175)
            if y==40.: pad=pad.cut(cyl(x,y,-.1,3.02,3.4))
            add(f'DOCK_PAD_{int(x)}_{int(y)}',pad,AL)
    # All unreachable structural plywood remains6.35 below the wear datum.
    # Only the broad central infill is declared machinable; exposed tracks,
    # panel seams, recessed perimeter and screws are separate CAM keep-outs.
    front=P.PANEL_Y0+index*P.PANEL_PITCH
    ya=max(TRACK_CENTRES[0]+TRACK_W/2,SKIM[2]-front)
    yb=min(TRACK_CENTRES[1]-TRACK_W/2,SKIM[3]-front)
    if yb>ya:
        wear=box(SKIM[0],ya,BOX_H,SKIM[1]-SKIM[0],yb-ya,WEAR)
        for x in (205.,445.,705.,945.):
            for y in (ya+20,yb-20):
                # Recess heads2mm under new wear top. Maximum routine skim1mm.
                wear=wear.cut(cyl(x,y,CASSETTE_H-2.,4.,3.))
                wear=wear.cut(cq.Solid.makeCone(1.75,3.4,1.65,
                         cq.Vector(x,y,CASSETTE_H-3.65),cq.Vector(0,0,1)))
                wear=wear.cut(cyl(x,y,BOX_H-.1,1.75,WEAR+.2))
        add('REPLACEABLE_6p35_MDF_WEAR_KEEP_OUT_SCREWS',wear,MDF)
    return p

def cassette_parts(index,location='installed',angle=None,y=None,z=None):
    if location=='installed': y,z,a=P.PANEL_Y0+index*P.PANEL_PITCH,P.DRY_BOTTOM,0.
    elif location=='stored': y,z,a=STORE_Y,STORE_LEVELS[index],0.
    else: a=0. if angle is None else angle
    return [(n,pose_shape(s,y,z,a),c) for n,s,c in cassette_local_parts(index)]

def transfer_poses(index):
    yi=P.PANEL_Y0+index*P.PANEL_PITCH
    return [
      {'stage':'installed','y':yi,'z':P.DRY_BOTTOM,'angle':0.},
      {'stage':'flat_lift','y':yi,'z':TRANSFER_FLAT_BOTTOM,'angle':0.},
      {'stage':'front_flat','y':TRANSFER_FRONT_Y,'z':TRANSFER_FLAT_BOTTOM,'angle':0.},
      {'stage':'front_upright','y':TRANSFER_FRONT_Y,'z':TRANSFER_FLAT_BOTTOM,'angle':90.},
      {'stage':'lower_front_channel','y':TRANSFER_FRONT_Y,'z':TRANSFER_LOW_BOTTOM,'angle':90.},
      {'stage':'rotate_below_pan','y':TRANSFER_FRONT_Y,'z':TRANSFER_LOW_BOTTOM,'angle':0.},
      {'stage':'raise_in_front_of_case','y':TRANSFER_FRONT_Y,'z':STORE_LEVELS[index]+1.,'angle':0.},
      {'stage':'insert_above_shelf','y':STORE_Y,'z':STORE_LEVELS[index]+1.,'angle':0.},
      {'stage':'seat_on_shelf','y':STORE_Y,'z':STORE_LEVELS[index],'angle':0.}]

@lru_cache(None)
def dock_parts():
    p=[]; add=lambda n,s,c=AL:p.append((n,s.clean(),c))
    t,L=6.35,50.8
    for left in (True,False):
        tag='L' if left else'R'
        x0=75.2 if left else 1024.
        flange=box(x0,80,P.DRY_BOTTOM-t,L,1120,t)
        webx=x0 if left else x0+L-t
        angle=fuse([flange,box(webx,80,P.DRY_BOTTOM,t,1120,L-t)])
        for cy in P.POST_CENTRES_Y:
            for x in ((96.,116.) if left else(1034.,1054.)):
                for y in (cy-20,cy+20):
                    if cy==P.POST_CENTRES_Y[0] and y==cy-20 and x==(116. if left else 1034.):continue
                    angle=angle.cut(cyl(x,y,P.DRY_BOTTOM-t-.1,3.3,t+.2))
                    angle=angle.cut(cq.Solid.makeCone(3.3,6.3,3.,
                                  cq.Vector(x,y,P.DRY_BOTTOM-3.),cq.Vector(0,0,1)))
        for i in range(4):
            yy=P.PANEL_Y0+i*P.PANEL_PITCH+40
            px=117.5 if left else 1032.5
            angle=angle.cut(cyl(px,yy,P.DRY_BOTTOM-4,3.,4.1))
            pin=cyl(px,yy,P.DRY_BOTTOM-4,2.99,6.)
            if not left: pin=pin.intersect(box(px-2.4,yy-4,P.DRY_BOTTOM-4,4.8,8,6))
            add(f'DOCK_{tag}_{i+1}_'+('ROUND' if left else'DIAMOND_X_RELIEF'),pin,PIN)
        for i in range(4):
            yy=P.PANEL_Y0+i*P.PANEL_PITCH+128.5
            angle=angle.cut(cyl(117.5 if left else 1032.5,yy,P.DRY_BOTTOM-t-.1,3.3,t+.2))
        add('DRY_LEDGER_'+tag+'_2x2xQUARTER_AL_UP_WEB',angle)
    return p

@lru_cache(None)
def pan_parts():
    p=[]; add=lambda n,s,c=HOT:p.append((n,s.clean(),c))
    a,b,lo,hi=P.PAN_X0,P.PAN_X1,P.PAN_Y0,P.PAN_Y1
    t=PAN_T
    add('HOT_PAN_PLAIN14GA_FLOOR',yz(a,b-a,[(lo,pan_floor_z(lo)-t),
       (hi,pan_floor_z(hi)-t),(hi,pan_floor_z(hi)),(lo,pan_floor_z(lo))]))
    for tag,x in (('L',a),('R',b-t)):
        wall=yz(x,t,[(lo,pan_floor_z(lo)),(hi,pan_floor_z(hi)),
                                                    (hi,P.PAN_RIM),(lo,P.PAN_RIM)])
        if tag=='L':
            wall=wall.cut(cyl(a-.1,180.,pan_floor_z(180.)+14.,12.,t+.2,(1,0,0)))
        else:
            wall=wall.cut(box(b-t-.1,880.,P.PAN_RIM-11,t+.2,40,8))
        add('HOT_PAN_WALL_'+tag,wall)
    front=yz(a+t,b-a-2*t,[(lo,pan_floor_z(lo)),(lo+t,pan_floor_z(lo+t)),
                                        (lo+t,P.PAN_RIM),(lo,P.PAN_RIM)])
    # Smooth bore is an interface hold. It is not anNPT thread or finished valve.
    add('HOT_PAN_FRONT',front)
    add('HOT_PAN_REAR',yz(a+t,b-a-2*t,[(hi-t,pan_floor_z(hi-t)),(hi,pan_floor_z(hi)),
                                                        (hi,P.PAN_RIM),(hi-t,P.PAN_RIM)]))
    zc=pan_floor_z(180.)+14
    outlet=cyl(a-26,180.,zc,14,26,(1,0,0)).cut(cyl(a-26.1,180.,zc,12,26.2,(1,0,0)))
    add('DRAIN_SMOOTH_OD28_ID24_NPT_ADAPTER_HOLD',outlet,HOT)
    # Right-side independent overflow stays clear of front transfer channel.
    # Its wall opening is cut in the actual wall below; chute remains open to air.
    overflow=box(b,878.,P.PAN_RIM-13,34,44,12).cut(
                 box(b-.1,880.,P.PAN_RIM-11,34.2,40,8))
    add('INDEPENDENT_OPEN_OVERFLOW_40x8',overflow)
    # Three short longitudinal combs support transverse slats, with drainage gaps.
    slat_bottom=P.SLAT_TOP-40.
    slat_ys=tuple(lo+30+(hi-lo-60)*i/7 for i in range(8))
    for j,x in enumerate((140.,575.,1010.)):
        comb=box(x-1.5875,lo+10,pan_floor_z(lo),3.175,hi-lo-20,
                 slat_bottom-pan_floor_z(lo)+15)
        # Follow slope at foot so it never pierces pan floor.
        wedge=yz(x-2,4,[(lo+9,pan_floor_z(lo)+1),(hi-9,pan_floor_z(hi)+1),
                         (hi-9,pan_floor_z(hi)),(lo+9,pan_floor_z(lo))])
        # Remove below the actualslopedfloor for a level, drainage-notched comb.
        below=yz(x-2,4,[(lo+9,pan_floor_z(lo+9)-20),(hi-9,pan_floor_z(hi-9)-20),
                         (hi-9,pan_floor_z(hi-9)),(lo+9,pan_floor_z(lo+9))])
        comb=comb.cut(below)
        for y in slat_ys:
            comb=comb.cut(box(x-3,y-SLAT_T/2-.15,slat_bottom,6,SLAT_T+.3,20))
        for y in range(int(lo)+40,int(hi)-30,120):
            comb=comb.cut(box(x-3,y,pan_floor_z(y)-.1,6,20,8))
        add(f'HOT_COMB_{j+1}_WALL_JOIN_AND_WELD_HOLD',comb)
    for i,y in enumerate(slat_ys,1):
        add(f'HOT_SLAT_{i:02}_880x40x1p9_ONE_SHEET_CANDIDATE',
            box(SLAT_X0,y-SLAT_T/2,slat_bottom,SLAT_LENGTH,SLAT_T,40))
    # Nine small frame-to-floor shim packs replace long milled saddles.
    # Each pack must be assembled/measured on the real frame; no stock ownership credit.
    for cy in P.POST_CENTRES_Y:
        for x in (140.,575.,1010.):
            add(f'PAN_FRAME_SHIM_PACK_{int(x)}_{int(cy)}_VERIFY_ACTUAL',
                yz(x-12.5,25,[(cy-10,P.PAN_BEARER_TOP),(cy+10,P.PAN_BEARER_TOP),
                    (cy+10,pan_floor_z(cy+10)-t),(cy-10,pan_floor_z(cy-10)-t)]),AL)
    # Clipandstand-off geometry protectsAlfromdirectspatter butisnotthermalproof.
    for left,x in ((True,118.),(False,1022.)):
        shadow=box(x,lo,870.,10.,hi-lo,1.9)
        for cy in P.POST_CENTRES_Y:shadow=shadow.cut(box(x-1,cy-41,869,12,82,5))
        if not left:shadow=shadow.cut(box(x-1,877.,869,12,46,5))
        add('HOT_SIDE_SHADOW_'+('L' if left else'R'),shadow)
    return p

@lru_cache(None)
def storage_parts(door_open=False):
    """Floor-supported closed cold cabinet; rear links resist tip, not vertical load.

    Four corner posts leave the full-width front transfer corridor unobstructed.
    Thin skins carry no machining load. All sheet joints need actual fasteners.
    """
    p=[]; add=lambda n,s,c=LIGHT:p.append((n,s.clean(),c))
    t=.8; x0,x1,y0,y1,z0,z1=104.,1046.,350.,627.,378.,710.
    floor=box(x0,y0,z0,x1-x0,y1-y0,t)
    for left in (True,False):
        for front in (True,False):
            xx=x0 if left else x1-22.
            yy=y0 if front else y1-3.
            floor=floor.cut(box(xx-.01,yy-.01,z0-.1,22.02,3.02,1.))
    add('COLD_CASE_FLOOR_NOT_A_WORKBED',floor)
    # 25x25x3 structural Al corner angles bear directly on floor shims.
    for left in (True,False):
        tag='L' if left else'R'; xx=101. if left else 1046.
        for front in (True,False):
            yy=y0 if front else y1-25.
            fy=y0 if front else y1-3.
            fx=104. if left else 1024.
            post=fuse([box(xx,yy,0,3,25,z1),box(fx,fy,0,22,3,z1)])
            if front:
                # Full-width panels pass between the outboard side legs. Retain
                # the return belowfloor/abovepanels; side skin braces the flat segment.
                post=post.cut(box(fx-.01,fy-.01,378.,22.02,3.02,326.))
            # Rivets join the case wall to the outboard column, never to wood.
            for zz in (410.,500.,600.,690.):
                ry=yy+12.5
                post=post.cut(cyl(xx-.1,ry,zz,2.1,3.2,(1,0,0)))
            if not front:
                for zz in (573.,587.):post=post.cut(cyl(xx-.1,610.,zz,2.2,3.2,(1,0,0)))
            add(f'COLD_CASE_FLOOR_COLUMN_{tag}_'+('F' if front else'R')+'_AL25x25x3',post,AL)
    sides=[]
    for left in (True,False):
        tag='L' if left else'R'; x=x0 if left else x1-t
        wall=box(x,y0,z0+t,t,y1-y0-3,z1-z0-t).cut(box(x-.1,y0-.1,704.,t+.2,3.2,6.1))
        for yy in (362.5,614.5):
            for zz in (410.,500.,600.,690.):
                wall=wall.cut(cyl(x-.1,yy,zz,2.1,t+.2,(1,0,0)))
        for yy in (362.5,614.5):
            for zz in (410.,500.,600.,690.):
                rivet=cyl(100.6,yy,zz,1.95,7.,(1,0,0))
                if not left:rivet=rivet.mirror('YZ',(575,0,0))
                add(f'COLD_CASE_COLUMN_{tag}_M4_BLIND_RIVET_{int(yy)}_{int(zz)}_VERIFY_GRIP',rivet,PIN)
        for zz in (573.,587.):wall=wall.cut(cyl(x-.1,610.,zz,2.2,t+.2,(1,0,0)))
        # Separate one-piece angle shelf rails, three flush blind rivets each.
        for i,z in enumerate(STORE_LEVELS):
            vx=x0+t if left else x1-t-1.6
            hx=vx+1.6 if left else vx-18.4
            rail=fuse([box(vx,STORE_Y,z-20,1.6,P.PANEL_LENGTH,20),
                       box(hx,STORE_Y,z-1.6,18.4,P.PANEL_LENGTH,1.6)])
            for yy in (390.,480.,587.):
                wall=wall.cut(cyl(x-.1,yy,z-10,2.1,t+.2,(1,0,0)))
                rail=rail.cut(cyl(vx-.1,yy,z-10,2.1,1.8,(1,0,0)))
                start=100.6 if left else 1042.4
                # Sleeve/body only; compact blind head stays outside X109..1041.
                rivet=cyl(start,yy,z-10,1.95,7.0,(1,0,0))
                add(f'CASE_SHELF_{tag}_{i}_M4_BLIND_RIVET_{int(yy)}_VERIFY_GRIP',rivet,PIN)
            add(f'CASE_SHELF_{tag}_{i}_AL20x20x1p6',rail,AL)
        add('COLD_CASE_SIDE_'+tag,wall)
    add('COLD_CASE_BACK',box(126.,y1-t,z0+t,898.,t,z1-z0-t))
    add('COLD_CASE_ROOF',box(101.,y0,z1,948.,y1-y0,t))
    add('COLD_CASE_SECONDARY_STEEL_ROOF_AIRGAP5_THERMAL_HOLD',box(101.,y0,z1+5,948.,y1-y0,1.9),HOT)
    for xx in (150.,1000.):
        for yy in (365.,610.):
            add(f'COLD_CASE_ROOF_STANDOFF_{int(xx)}_{int(yy)}',
                cyl(xx,yy,z1+t,3.,5-t).cut(cyl(xx,yy,z1+t-.1,1.65,5)),AL)
    dz=-342. if door_open else 0.
    add('COLD_CASE_SLIDING_FRONT_DOOR_'+('OPEN' if door_open else'CLOSED'),
        box(x0,y0-2,z0+dz,x1-x0,t,z1-z0))
    # Two rear anti-tip links to centre post inner faces. Not cabinet suspension.
    for left in (True,False):
        tag='L' if left else'R'
        if left:
            link=fuse([box(50.8,600,565,3,20,30),box(53.8,600,592,47.2,20,3),box(98.,600,565,3,20,30)])
            link=link.cut(cyl(50.7,610,580,3.3,3.2,(1,0,0)))
        else:
            link=fuse([box(1096.2,600,565,3,20,30),box(1049,600,592,47.2,20,3),box(1049.,600,565,3,20,30)])
            link=link.cut(cyl(1096.1,610,580,3.3,3.2,(1,0,0)))
        for zz in (573.,587.):
            hx=97.9 if left else 1048.9
            link=link.cut(cyl(hx,610.,zz,2.2,3.2,(1,0,0)))
            shaft=cyl(98.,610.,zz,1.95,10.,(1,0,0)).fuse(cyl(95.,610.,zz,3.5,3.,(1,0,0)))
            nut=cq.Workplane('YZ').polygon(6,8.083).extrude(3.2).val().translate((104.8,610.,zz))
            nut=nut.cut(cyl(104.7,610.,zz,2.,3.4,(1,0,0)))
            if not left:
                shaft=shaft.mirror('YZ',(575,0,0));nut=nut.mirror('YZ',(575,0,0))
            add(f'COLD_CASE_ANTITIP_{tag}_M4x10_{int(zz)}',shaft,PIN)
            add(f'COLD_CASE_ANTITIP_{tag}_M4_NUT_{int(zz)}',nut,PIN)
        add('COLD_CASE_REAR_ANTI_TIP_LINK_'+tag+'_M6_POST_M4_COLUMN_HOLD',link,AL)
    return p

@lru_cache(None)
def pan_retainers():
    """Four positively captured pan ears; one round, one X-float, two radial-float."""
    out=[]; add=lambda n,s,c=AL:out.append((n,s.clean(),c))
    for front,face,ey in ((True,120.,150.),(False,1160.,1125.)):
        for left,cx in ((True,116.),(False,1034.)):
            key=('F' if front else'R')+('L' if left else'R')
            xx=104. if left else 1022.
            # Bent frame ear outside the wet pan; face joint at back of bearer.
            vy=face if front else face-6
            hy=face if front else ey-15
            hl=ey-face+15 if front else face-hy
            bracket=fuse([box(xx,vy,736.5,24,6,70.),
                          box(xx,hy,806.5,24,hl,6.)])
            for z in (746.5,786.5):
                bracket=bracket.cut(cyl(cx,vy-.1,z,3.3,6.2,(0,1,0)))
            add('PAN_FRAME_EAR_'+key+'_M6_FACE_FIX_HOLD',bracket)
            boss=cyl(cx,ey,812.5,7.,15.).cut(cyl(cx,ey,812.4,3.,15.2))
            shoulder=cyl(cx,ey,827.5,4.,7.).cut(cyl(cx,ey,827.4,3.15,7.2))
            cap=box(cx-10,ey-8,834.5,20,16,3.).cut(cyl(cx,ey,834.4,3.3,3.2))
            add('PAN_KEEPER_'+key+'_BOSS',boss)
            add('PAN_KEEPER_'+key+'_SHOULDER',shoulder)
            add('PAN_KEEPER_'+key+'_CAP_1MM_UPLIFT',cap)
            # Steel ear welds to external dry wall, does not pierce fluid boundary.
            ear=box(xx,ey-15,831.6,24,30,1.9)
            if front and left:
                hole=cyl(cx,ey,831.5,4.3,2.1)
            elif front:
                hole=fuse([cyl(cx-2,ey,831.5,4.3,2.1),
                           cyl(cx+2,ey,831.5,4.3,2.1),
                           box(cx-2,ey-4.3,831.5,4,8.6,2.1)])
            else: hole=cyl(cx,ey,831.5,7.,2.1)
            add('PAN_WELDED_EAR_'+key,ear.cut(hole),HOT)
            # Bolt envelope bears on cap/shoulder, not on the floating ear.
            bolt=fuse([cyl(cx,ey,817.5,2.95,20.),
                       cyl(cx,ey,837.5,5.,6.)])
            add('PAN_KEEPER_'+key+'_M6x20_VERIFY_THREAD',bolt,PIN)
    return out

def swept_pipe(points,midpoints,outer,inner):
    """Circular pipe along tangent-continuous line/arc centreline segments."""
    edges=[]
    for i,(a,b) in enumerate(zip(points,points[1:])):
        if i in midpoints:edges.append(cq.Edge.makeThreePointArc(a,midpoints[i],b))
        else:edges.append(cq.Edge.makeLine(cq.Vector(*a),cq.Vector(*b)))
    path=cq.Wire.assembleEdges(edges)
    tangent=edges[0].tangentAt(0)
    plane=cq.Plane(origin=points[0],normal=tangent)
    ow=cq.Workplane(plane).circle(outer).val()
    iw=cq.Workplane(plane).circle(inner).val()
    return cq.Solid.sweep(ow,[iw],path,True,True).clean()

@lru_cache(None)
def water_envelopes():
    """Vented floor receiver and gravity returns. Hardware dimensions remain holds."""
    out=[];add=lambda n,s,c:out.append((n,s.clean(),c))
    zc=pan_floor_z(180.)+14.
    # Swept 90-degree side adapter and valve turn the outlet rearward.
    elbow=swept_pipe([(102.,180.,zc),(82.,200.,zc)],
                    {0:(87.857864,185.857864,zc)},14.,12.)
    add('WATER_DRAIN_90DEG_ADAPTER_OD28_ID24_THREAD_HOLD',elbow,HOT)
    valve=cyl(82.,200.,zc,19.,54.,(0,1,0)).cut(cyl(82.,199.9,zc,12.,54.2,(0,1,0)))
    add('WATER_1IN_FULL_PORT_VALVE_ENVELOPE_NO_THREAD_RELEASE',valve,(.62,.49,.25))
    add('WATER_VALVE_HANDLE_SERVICE_ENVELOPE',box(78,205,zc+19,8,95,5),PIN)
    elbow=swept_pipe([(82.,254.,zc),(82.,274.,zc-20.)],
                    {0:(82.,268.142136,zc-5.857864)},17.,12.5)
    add('WATER_DOWN_ELBOW_ADAPTER_34_OD_25_ID_HOLD',elbow,(.22,.27,.30))
    # No rising section. 100mm centreline bend radius; verify actual hose minimum.
    pts=[(82.,274.,zc-20.),(82.,274.,630.),(82.,374.,530.),
         (82.,700.,530.),(182.,800.,530.),(300.,800.,530.),
         (400.,800.,430.),(400.,800.,410.)]
    mids={1:(82.,303.289322,559.289322),3:(111.289322,770.710678,530.),
          5:(370.710678,800.,500.710678)}
    add('WATER_25MM_GRAVITY_HOSE_R100_OVER_RIM_AIRGAP21',
        swept_pipe(pts,mids,17.,12.5),(.22,.27,.30))
    # Conservative listing clearance incl handles:712x470x389. Listing is not a liquid rating.
    receiver=box(219,700,0,712,470,389).cut(box(223,704,4,704,462,386))
    add('WATER_RED20GAL_CANDIDATE_712x470x389_REQUIRE_65L_USABLE',receiver,(.65,.09,.08))
    lid=box(219,700,389,712,470,2.)
    for x,y,r in ((400.,800.,25.),(700.,1000.,12.5)):
        lid=lid.cut(cyl(x,y,388.9,r,2.2))
    lid=lid.cut(box(880,875,388.9,40,50,2.2))
    add('WATER_REMOVABLE_LID_RETURN_PORTS_OPEN25MM_VENT_NOT_PRESSURE',lid,LIGHT)
    wall=box(1056,878,465,20,44,P.PAN_RIM-465)
    wall=wall.cut(box(1055.9,879.9,466.9,18.2,40.2,P.PAN_RIM-465))
    overflow_pieces=[wall]
    points=[cq.Vector(900,878,462),cq.Vector(1076,878,465),
            cq.Vector(1076,878,466.9),cq.Vector(900,878,463.9)]
    base=cq.Solid.extrudeLinear(cq.Wire.makePolygon(points+[points[0]]),[],cq.Vector(0,44,0))
    sides=[]
    for y in (878.,920.1):
        pp=[cq.Vector(900,y,462),cq.Vector(1076,y,465),
            cq.Vector(1076,y,477),cq.Vector(900,y,474)]
        sides.append(cq.Solid.extrudeLinear(cq.Wire.makePolygon(pp+[pp[0]]),[],cq.Vector(0,1.9,0)))
    overflow_pieces += [base,*sides,box(900,878,410,1.9,44,64)]
    add('OVERFLOW_WELDED_OPEN_RETURN_AIRGAP21',fuse(overflow_pieces),HOT)
    return out


@lru_cache(None)
def retention_parts():
    """Router-only removable M6 bolts, washers and nuts. Remove before each lift."""
    p=[]
    for i in range(4):
        yy=P.PANEL_Y0+i*P.PANEL_PITCH+128.5
        for x in (117.5,1032.5):
            z=P.DRY_BOTTOM+BOX_H
            bolt=fuse([cyl(x,yy,z-80,2.95,80),cyl(x,yy,z,5.,6.)])
            washer=cyl(x,yy,P.DRY_BOTTOM-6.35-1.6,6.,1.6).cut(
                       cyl(x,yy,P.DRY_BOTTOM-8.,3.3,2.))
            nut=cq.Workplane('XY').polygon(6,11.547).extrude(5.).val().translate(
                       (x,yy,P.DRY_BOTTOM-6.35-1.6-5.)).cut(
                       cyl(x,yy,P.DRY_BOTTOM-14.,3.,7.))
            for tag,s in (('M6x80_SOCKET_REMOVE_BEFORE_LIFT',bolt),
                          ('M6_WASHER_OD12',washer),('M6_HEX_NUT_AF10',nut)):
                p.append((f'CAS{i+1}_CLAMP_{int(x)}_'+tag,s.clean(),PIN))
    return p

def bed_parts(plasma):
    p=pan_parts()+pan_retainers()+water_envelopes()+dock_parts()+storage_parts(False)
    for i in range(4): p+=cassette_parts(i,'stored' if plasma else'installed')
    if not plasma:p+=retention_parts()
    return p

def transfer_fixed_parts():
    return pan_parts()+pan_retainers()+water_envelopes()+dock_parts()+storage_parts(True)

def mass_report():
    densities={PLY:600.,MDF:750.,AL:2700.,LIGHT:2700.,HOT:7850.,PIN:7850.,
               (.62,.49,.25):8500.,(.22,.27,.30):1400.,(.30,.43,.39):950.,(.65,.09,.08):950.}
    def group(parts):
        rows=[];total=0.;mom=[0.,0.,0.]
        for n,s,c in parts:
            density=(950. if n.startswith('WATER_RED20GAL_') else 1200. if n.startswith('WATER_REMOVABLE_LID_') else densities[c])
            mass=s.Volume()*1e-9*density; com=s.Center().toTuple()
            total+=mass
            for j,v in enumerate(com):mom[j]+=mass*v
            rows.append({'name':n,'kg':mass,'centre_mm':list(com)})
        return {'kg':total,'cg_mm':[v/total for v in mom] if total else None,'parts':rows}
    return {'cassette_installed':[group(cassette_parts(i)) for i in range(4)],
            'cassette_stored':[group(cassette_parts(i,'stored')) for i in range(4)],
            'pan_slats_combs':group(pan_parts()),'pan_retainers':group(pan_retainers()),
            'water_envelopes_floor_receiver_not_frame_ballast':group(water_envelopes()),
            'storage_empty':group(storage_parts()),
            'docks':group(dock_parts()),'assumed_density_kg_m3':{'ply':600,'MDF':750,'Al':2700,'steel':7850},'receiver_mass_qualification':'Clearance-shell volume with assumed950kg/m3 body and1200kg/m3 lid; NOT actual tote mass or liquid rating. Receiver and separate floor cabinet are not frame ballast.'}

