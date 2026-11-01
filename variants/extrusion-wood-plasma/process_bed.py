"""Alternate compact carving / steel-sheet plasma bed. All coordinates mm, original small-machine world.

Independent design study; do not use as a cutting file or energized-machine drawing.
The shapes model material with square bends, clearance holes, locators, and supports.
Fastener threads, radii, welds and consumable tooling are not represented.
"""
import functools
import math
import cadquery as cq

STEEL=(.42,.49,.54); PAN=(.25,.35,.40); WARM=(.62,.44,.24)
ZINC=(.59,.67,.69); BRIGHT=(.69,.76,.78); MDF=(.72,.52,.30); DARK=(.20,.25,.29)
def box(x,y,z,w,l,h): return cq.Solid.makeBox(w,l,h,cq.Vector(x,y,z))
def cyl(x,y,z,r,h,d=(0,0,1)): return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*d))
def join(*ss): return ss[0].fuse(*ss[1:]).clean() if len(ss)>1 else ss[0]
def minus(s,holes): return s.cut(cq.Compound.makeCompound(holes)).clean() if holes else s
def yz(x,w,points):
    p=[cq.Vector(x,y,z) for y,z in points]
    return cq.Solid.extrudeLinear(cq.Wire.makePolygon(p+[p[0]]),[],cq.Vector(w,0,0))
def tube_y(x,y,z,w,l,h,t): return box(x,y,z,w,l,h).cut(box(x+t,y-1,z+t,w-2*t,l+2,h-2*t))
def tube_z(x,y,z,w,l,h,t): return box(x,y,z,w,l,h).cut(box(x+t,y+t,z-1,w-2*t,l-2*t,h+2))
def tube_x(x,y,z,w,l,h,t): return box(x,y,z,w,l,h).cut(box(x-1,y+t,z+t,w+2,l-2*t,h-2*t))
def bore6(x,y,z,h):return cyl(x,y,z,3.3,h)
def nut(x,y,z,h=5):
    ring=cq.Workplane('XY').polygon(6,11.55).extrude(h).val().translate((x,y,z))
    return ring.cut(cyl(x,y,z-1,2.5,h+2))
def bolt(x,y,seat,grip=10):
    return join(cyl(x,y,seat-grip,2.95,grip),cyl(x,y,seat,5,3.5))

PY0=64.; PY1=1196.; PX0=128.; PX1=1022.; RIM=907.; SLOPE=.006
SLAT_TOP=911.; WATER=887.; PLANE=946.1; BACK=12.7; PANEL_X=109.; PANEL_W=932.
PANEL_L=257.; PANEL_STEP=259.; FIRST_Y=103.4; STORED_Z=714.; SLOT_Y=(1216.,1262.,1308.,1354.)
SLAT_X=[152+i*47. for i in range(19)]
# Two clamp stations along X, outside drain/overflow and storage support posts.
KEEP_X=(306.,836.)
def top(y):return 845.+SLOPE*(y-PY0)
def panel_y(i):return FIRST_Y+PANEL_STEP*i
def holes_px():return (117.5,1032.5)
def fixt():return [(x,y) for x in (190.,575.,960.) for y in (33.,224.)]

def pan_retainers():
    """Wrap the two outer crossbearers. No new holes in the frame or plasma pan."""
    parts=[];add=lambda n,s,c=STEEL:parts.append((n,s,c))
    for front,cy in ((True,100.),(False,1180.)):
        edge='F' if front else 'R'
        ey=49. if front else 1205.
        for j,cx in enumerate(KEEP_X):
            side='L' if j==0 else 'R'; key=edge+side; px,hx=cx+7.,cx-9.
            y1,y2=(34.,135.) if front else (1145.,1215.)
            bys=(cy-27.,cy+27.)
            up=box(cx-18.,y1,839.5,36.,y2-y1,3.)
            for by in bys:
                up=up.cut(cyl(hx,by,839.0,3.3,4.))
            add('PAN_HOLD_'+key+'_upper_strap',up)
            lower=minus(box(cx-18,cy-34.5,794.5,36,69,5),[bore6(hx,by,794,6) for by in bys])
            # Bolts enter from below and finish below the upper strap face; check actual lengths.
            add('PAN_HOLD_'+key+'_base_strap',lower)
            for k,by in enumerate(bys):
                sh=join(cyl(hx,by,791.5,2.975,50.),cyl(hx,by,785.5,5,6))
                washer=cyl(hx,by,791.5,7,3).cut(cyl(hx,by,791.,3.3,4))
                add(f'PAN_HOLD_{key}_M6x50_{k}',sh,ZINC)
                add(f'PAN_HOLD_{key}_washer_{k}',washer,ZINC)
                # Nominal female/male thread envelopes use the same through diameter here.
                lock=cq.Workplane('XY').polygon(6,11.55).extrude(6).val().translate((hx,by,833.5))
                add(f'PAN_HOLD_{key}_captive_boss_{k}',lock.cut(cyl(hx,by,832.5,3.,8)),ZINC)
            boss=cyl(px,ey,842.5,7.,15.).cut(cyl(px,ey,845.5,3.,13))
            add('PAN_HOLD_'+key+'_boss_14mm',boss)
            sleeve=cyl(px,ey,857.5,4.,7.).cut(cyl(px,ey,856.5,3.15,9.))
            add('PAN_HOLD_'+key+'_shoulder_8mm',sleeve,BRIGHT)
            # 1 mm axial capture clearance: clamp screws bear on sleeves, not sliding pan ears.
            cap=minus(box(px-13,ey-8,864.5,26,16,3),[bore6(px,ey,864,5)])
            add('PAN_HOLD_'+key+'_keeper_cap',cap)
            add('PAN_HOLD_'+key+'_M6x20_keeper',join(cyl(px,ey,847.5,2.95,20.),cyl(px,ey,867.5,5,6)),ZINC)
            start,stop=(34.,64.) if front else (1196.,1215.)
            ear=box(px-16,start,859.5,32.,stop-start,4.)
            if not front: holes=[cyl(px,ey,859.,7.,5.)]  # 3 mm radial float
            elif j==0: holes=[cyl(px,ey,859.,4.3,5.)]
            else:holes=[join(cyl(px-2.,ey,859.,4.3,5.),cyl(px+2.,ey,859.,4.3,5.),box(px-2,ey-4.3,859,4,8.6,5))]
            add('PAN_EAR_'+key+'_welded_to_dry_wall',minus(ear,holes),BRIGHT)
    return parts

@functools.lru_cache(None)
def pan_parts():
    p=[];add=lambda n,s,c=PAN:p.append((n,s,c))
    lo,hi=PY0,PY1; a,b=PX0,PX1
    f=yz(a,b-a,[(lo,top(lo)-2),(hi,top(hi)-2),(hi,top(hi)),(lo,top(lo))])
    add('PAN_sloping_floor_2mm',f)
    for n,x in [('left',a),('right',b-2)]:
        add('PAN_'+n+'_wall',yz(x,2,[(lo,top(lo)),(hi,top(hi)),(hi,RIM),(lo,RIM)]))
    front=yz(a+2,b-a-4,[(lo,top(lo)),(lo+2,top(lo+2)),(lo+2,RIM),(lo,RIM)])
    front=front.cut(cyl(235,lo-1,859,12,4,(0,1,0))).cut(box(855,lo-1,896,40,4,8))
    add('PAN_front_wall_drain_overflow',front)
    rear=yz(a+2,b-a-4,[(hi-2,top(hi-2)),(hi,top(hi)),(hi,RIM),(hi-2,RIM)])
    add('PAN_rear_wall',rear)
    outlet=cyl(235,30,859,14,34,(0,1,0)).cut(cyl(235,29,859,12,36,(0,1,0)))
    add('PAN_gravity_drain_OD28_ID24',outlet,BRIGHT)
    overflow=box(853,30,894,44,34,12).cut(box(855,29,896,40,36,8))
    add('PAN_open_overflow_40x8',overflow,BRIGHT)
    for i,y in enumerate((100.,630.,1180.),1):
        ya,yb=y-16,y+16
        # Inclined face mates the actual floor; two outer saddles make room for wrap clamps.
        shim=yz(a,b-a,[(ya,839.5),(yb,839.5),(yb,top(yb)-2),(ya,top(ya)-2)])
        if i in (1,3):
            shim=minus(shim,[box(cx-19,ya-1,838,38,yb-ya+2,20) for cx in KEEP_X])
        add('PAN_bearing_saddle_%s'%i,shim,STEEL)
    # Comb locations are deliberate inside supports, not the ends of the sheet.
    for i,y in enumerate((94.,630.,1162.),1):
        g=yz(140,870,[(y,top(y)),(y+3,top(y+3)),(y+3,888.),(y,888.)])
        g=minus(g,[box(x-.3,y-1,879.,3.6,5,12.) for x in SLAT_X])
        # Gaps at the base prevent combs damming the pan into closed cells.
        g=minus(g,[box(x,y-1,top(y)-.05,23,5,9) for x in (175,335,495,655,815,965)])
        add('PAN_slotted_comb_%s'%i,g,STEEL)
    for i,x in enumerate(SLAT_X,1):
        add('SLAT_%02d_3x32x1092'%i,box(x,76,879.,3,1092,32.),BRIGHT)
    return p+pan_retainers()

@functools.lru_cache(None)
def frame_interfaces():
    p=[];add=lambda n,s,c=STEEL:p.append((n,s,c))
    for side,lx,px,base,fix in [('L',96.,117.5,54.,(63.,82.)),('R',1024.,1032.5,1024.,(1068.,1087.))]:
        holes=[]; nuts=[]
        for i in range(4):
            y=panel_y(i)
            for end,dy in [('a',24.),('b',233.)]:
                holes.append(bore6(px,y+dy,941.7,4.))
                nuts.append(nut(px,y+dy,937.5))
            holes.append(cyl(px,y+128.5,941.7,3.,4.))
            add('LOC_%s_%s_dowel'%(side,i+1),cyl(px,y+128.5,941.9,3.,6.6),BRIGHT)
        rail=minus(tube_y(lx,84.,914.5,30.,1116.,30.,2.),holes)
        add('CARVE_LEDGER_%s_tube_30x30x2'%side,rail)
        add('CARVE_LEDGER_%s_weldnuts'%side,cq.Compound.makeCompound(nuts),ZINC)
        for num,cy in enumerate((100.,630.,1180.),1):
            foot=minus(box(base,cy-16,839.5,72,32,4),
                       [bore6(x,cy,839,6) for x in fix])
            add('LEDGER_%s_base_%d_slot_bores'%(side,num),foot)
            add('LEDGER_%s_riser_%d'%(side,num),tube_z(lx,cy-15,843.5,30,30,71,2))
        # Continuous cleanable steel side skirt, not a guarantee of guide or operator protection.
        sx=76. if side=='L' else 1072.
        add('SPLASH_%s_outer_steel_skirt'%side,box(sx,68.,879.,2.,1120.,94.),PAN)
        for j,cy in enumerate((100.,630.,1180.),1):
            # Return flanges attach splash skirts to outer riser face.
            a,b=(78.,96.) if side=='L' else (1054.,1072.)
            add('SPLASH_%s_tab_%d'%(side,j),box(a,cy-7,890.,b-a,14,3),PAN)
    return p

@functools.lru_cache(None)
def local_panel():
    # Native part planes: y=0 front edge; all real material z=PLANE-32..PLANE.
    s=box(PANEL_X,0,PLANE-1.6,PANEL_W,PANEL_L,1.6)
    s=join(s,box(132,0,PLANE-32,886,1.6,30.4),
           box(132,PANEL_L-1.6,PLANE-32,886,1.6,30.4),
           box(132,1.6,PLANE-32,886,8.4,1.6),
           box(132,PANEL_L-10,PLANE-32,886,8.4,1.6),
           tube_x(127,PANEL_L/2.-12.7,PLANE-27.,896,25.4,25.4,1.5))
    holes=[bore6(x,y,PLANE-3,5) for x in holes_px() for y in (24.,233.)]
    holes.append(cyl(117.5,128.5,PLANE-3,3.15,5))
    holes.append(join(cyl(1031.5,128.5,PLANE-3,3.15,5),cyl(1033.5,128.5,PLANE-3,3.15,5),box(1031.5,125.35,PLANE-3,2,6.3,5)))
    holes+= [bore6(x,y,PLANE-3,5) for x,y in fixt()]
    s=minus(s,holes)
    # Weld nuts stay with bridge when the job/backer leaves; each pilot bore modeled.
    return join(s,*[nut(x,y,PLANE-1.6-5.) for x,y in fixt()])

def rotate_panel(shape, angle):
    return shape.rotate((0,0,PLANE),(1,0,PLANE),angle)
def stored(shape,i):
    return rotate_panel(shape,90).translate((0,SLOT_Y[i],STORED_Z-PLANE))

@functools.lru_cache(None)
def storage(plasma):
    p=[];add=lambda n,s,c=STEEL:p.append((n,s,c))
    # Rack is bolted to dedicated end hangers. Bottom Y stringers are below stored panel webs;
    # mouse-hole geometry is not an inferred collision exemption. Two wide open upper combs retain lips.
    for side,x in [('L',179.),('R',941.)]:
        add('RACK_'+side+'_bottom_rail',tube_y(x,1210,STORED_Z-25,30,185,25,2))
        arm=tube_y(x,1165,STORED_Z-55,30,230,30,2)
        add('RACK_'+side+'_cantilever',arm)
        add('RACK_'+side+'_hanger',tube_z(x,1165,STORED_Z-25,30,30,799.5-STORED_Z+25,2))
        tab=minus(box(x-16,1167,795.5,16,26,4),[bore6(x-8,1180,795,6)])
        tab2=minus(box(x+30,1167,795.5,16,26,4),[bore6(x+38,1180,795,6)])
        add('RACK_'+side+'_hanger_tabs',cq.Compound.makeCompound([tab,tab2]))
        # Each slot has a rear and front formed guide beyond folded-panel projected width (32 mm).
        for i,sy in enumerate(SLOT_Y,1):
            for tag,gy in [('A',sy-3.),('B',sy+34.)]:
                add('RACK_%s_guide_%d%s'%(side,i,tag),box(x,gy,STORED_Z,30,2,55),DARK)
    add('RACK_back_cross_tie',tube_x(99,1395,STORED_Z-55,953,16,30,2))
    for side,x in [('L',99.),('R',1043.)]:
        add('RACK_'+side+'_rear_upright',box(x,1395,STORED_Z-25,8,16,242.))
        # Fixed slotted steel combs capture the thin metal side tabs high up.
        # The 32 mm deep formed lips end well inboard of the combs.
        add('RACK_'+side+'_upper_spine',box(x,1206,931,8,205,16))
        a=x+8 if side=='L' else x-16
        teeth=box(a,1206,931,16,205,16)
        teeth=minus(teeth,[box(a-1,sy-1.3,930,18,4.2,18) for sy in SLOT_Y])
        add('RACK_'+side+'_comb_teeth',teeth)
    for i,sy in enumerate(SLOT_Y,1):
        hx,hy=1047.,sy+4.
        block=minus(box(1043.,sy,947.,8.,9.,26.),[cyl(hx,hy,963,2.1,11)])
        add('RACK_keeper_pedestal_%d'%i,block)
        tab=minus(box(1028.,sy,973.,24.,8.,3.),[cyl(hx,hy,972,2.65,5)])
        if not plasma:tab=tab.rotate((hx,hy,0),(hx,hy,1),90)
        add('RACK_keeper_%d_%s'%(i,'locked' if plasma else 'open'),tab,WARM)
        add('RACK_keeper_pivot_%d'%i,join(cyl(hx,hy,963.,2.45,13),cyl(hx,hy,976.,4.5,3)),ZINC)
    return p

@functools.lru_cache(None)
def bed_parts(plasma:bool):
    p=pan_parts()+frame_interfaces()+storage(plasma)
    for i in range(4):
        local=local_panel()
        q=stored(local,i) if plasma else local.translate((0,panel_y(i),0))
        p.append(('BED_bridge_%d_%s'%(i+1,'parked' if plasma else 'installed'),q,BRIGHT))
        if not plasma:
            y=panel_y(i)
            # Sacrificial stock backer, no under-table wood storage. Six countersunk hold-down bores.
            m=box(162.,y+1,PLANE,826.,PANEL_L-2,BACK)
            for x,dy in fixt():
                h=cyl(x,y+dy,PLANE-.3,3.3,BACK+1)
                counter=cq.Solid.makeCone(3.3,6.75,3.45,cq.Vector(x,y+dy,PLANE+BACK-3.45))
                m=m.cut(join(h,counter))
            p.append(('JOB_sacrificial_backer_%s_remove_with_stock'%(i+1),m,MDF))
            p.append(('BED_panel_%d_hold_down_bolts'%(i+1),cq.Compound.makeCompound(
                  [bolt(x,y+dy,PLANE,8.) for x in holes_px() for dy in (24.,233.)]),ZINC))
    return p
