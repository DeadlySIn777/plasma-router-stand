"""Budget 4040 chassis in mm; nominal envelopes, not vendor die drawings."""
from functools import lru_cache
from math import hypot
import cadquery as cq

DARK=(.18,.22,.25); SILVER=(.64,.71,.74); BLUE=(.18,.40,.49); FOOT=(.29,.32,.35)
def box(x,y,z,dx,dy,dz):
    return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cyl(r,h,p,d=(0,0,1)):
    return cq.Solid.makeCylinder(r,h,cq.Vector(*p),cq.Vector(*d))
def drill(s,centers,r):
    for p,d,h in centers:
        s=s.cut(cyl(r,h,p,d))
    return s.clean()

@lru_cache(None)
def local40(L):
    # The shallow grooves identify a T-slot profile in the STEP. Not a T-nut
    # cavity, a supplier section, or a basis for mass or section properties.
    s=box(0,0,0,40,40,L)
    for a in [box(-1,16,-1,3,8,L+2),box(38,16,-1,3,8,L+2),
              box(16,-1,-1,8,3,L+2),box(16,38,-1,8,3,L+2)]:
        s=s.cut(a)
    return s.cut(cyl(3.4,L+2,(20,20,-1))).clean()
def bar(x,y,z,axis,L):
    s=local40(L)
    if axis=='X': s=s.rotate((0,0,0),(0,1,0),90).translate((0,0,40))
    if axis=='Y': s=s.rotate((0,0,0),(1,0,0),-90).translate((0,0,40))
    return s.translate((x,y,z))

def strap(a,b,width,thick,normal):
    delta=cq.Vector(*b)-cq.Vector(*a); ln=delta.Length; direction=delta.normalized().toTuple()
    # local x along strap; local y sideways; thickness out of its mounting plane
    w=cq.Workplane(cq.Plane(origin=a,xDir=direction,normal=normal))
    s=w.center(ln/2,0).slot2D(ln+width,width).extrude(thick).val()
    d=tuple(-t for t in normal)
    for p in (a,b):
        start=tuple(i+(thick+1)*j for i,j in zip(p,normal))
        s=s.cut(cyl(3.3,thick+2,start,d))
    return s.clean()

def frame_parts():
    out=[]
    def add(n,s,c=SILVER): out.append((n,s,c))
    for si,x in enumerate((10.8,1099.2)):
        k='L' if si==0 else 'R'; mid=x+20; side=x if si==0 else x+40; sign=-1 if si==0 else 1
        add('EX_'+k+'_Y_MOTION',bar(x,0,1016,'Y',1450),DARK)
        add('EX_'+k+'_Y_PAN',bar(x,0,799.5,'Y',1450),DARK)
        for i,y in enumerate((0,705,1410),1):
            cy=y+20
            add(f'EX_{k}_LEG_{i}',bar(x,y,69.5,'Z',730),DARK)
            add(f'EX_{k}_UPRIGHT_{i}',bar(x,y,839.5,'Z',176.5),DARK)
            # Adjustable foot allocation with positive top/foot plate interfaces.
            foot=cyl(33,9,(mid,cy,0)).fuse(cyl(7,54.5,(mid,cy,9)),box(x,y,63.5,40,40,6)).clean()
            add(f'FOOT_{k}_{i}_RATED_PART_ALLOWANCE',foot,FOOT)
            # Two exterior fishplates: direct metal end bearing takes gravity.
            # Offset longitudinal arms permit two nuts in the horizontal slot.
            for nm,z,lv in [('MID',819.5,[-58,-28,32,65]),('TOP',1036,[-67,-32])]:
                xb=side-6 if not si else side; ymin=max(0,cy-52); ymax=min(1450,cy+52)
                rect=box(xb,ymin,z-15,6,ymax-ymin,30)
                upr=box(xb,cy-14,z+min(lv)-13,6,28,max(0,max(lv))-min(lv)+26)
                p=rect.fuse(upr)
                yholes=[v for v in (cy-36,cy+36) if ymin+6<v<ymax-6]+[cy]
                pos=[(v,z) for v in yholes]+[(cy,z+v) for v in lv]
                add(f'JOIN_{k}_{i}_{nm}',drill(p,[((xb-1,yy,zz),(1,0,0),8) for yy,zz in pos],3.3),BLUE)
        # Hot-zone cap is narrower than moving side shoes. Flush hardware
        # before motion hardware; real HMS base fixings remain transfer-matched.
        cx=-23.8 if not si else 1072.2
        cap=box(cx,0,1056,101.6,1450,7.9375)
        for yy in (90,140,1410,1442):
            cap=cap.cut(cyl(3.3,10,((66.5 if not si else 1083.5),yy,1055)))
        for yy in (50,250,450,650,850,1050,1250,1370):
            cap=cap.cut(cyl(3.3,10,(mid,yy,1055)))
            cap=cap.cut(cq.Solid.makeCone(6.5,3.3,3.2,cq.Vector(mid,yy,1063.9375),cq.Vector(0,0,-1)))
        add('CAP_'+k+'_BOLTED',cap.clean())
        # X pairs in both long bays. Stagger middle-post bolt heights to
        # avoid sharing anchors. Credit the tension diagonal only.
        for i,(y1,y2,lo,hi) in enumerate([(20,725,150,710),(725,1430,200,660)],1):
            for j,(za,zb,off) in enumerate([(lo,hi,0),(hi,lo,5)],1):
                xx=side+sign*off
                add(f'BRACE_SIDE_{k}_{i}_{j}',strap((xx,y1,za),(xx,y2,zb),30,4,(sign,0,0)),BLUE)
                if off:
                    for h,(yy,zz) in enumerate(((y1,za),(y2,zb)),1):
                        sp=cyl(10,5,(side,yy,zz),(sign,0,0)).cut(cyl(3.3,6,(side,yy,zz),(sign,0,0)))
                        add(f'BRACE_SIDE_SPACER_{k}_{i}_{h}',sp)
    for i,y in enumerate((80,610,1160),1):
        add(f'EX_X_PAN_{i}',bar(50.8,y,799.5,'X',1048.4),DARK)
        for k in ('L','R'):
            left=k=='L'; xx=10.8 if left else 1043.2
            p=box(xx,y-15,793.15,96,70,6.35)
            cx=30.8 if left else 1119.2
            hole=[(cx,y-3),(cx,y+43)]+[(v,y+20) for v in ((65.8,94.8) if left else (1084.2,1055.2))]
            add(f'BEARING_SHELF_{k}_{i}',drill(p,[((a,b,792),(0,0,1),9) for a,b in hole],3.3))
    # Both diagonals on front and rear transverse planes. One strap is stood
    # off 5 mm; steel spacer washers give solid bearing and separate the cross.
    for k,y,n in [('F',0,-1),('R',1450,1)]:
        for i,(za,zb,standoff) in enumerate([(175,745,0),(745,175,5)],1):
            off=y+n*standoff
            add(f'BRACE_END_{k}_{i}',strap((30.8,off,za),(1119.2,off,zb),30,4,(0,n,0)),BLUE)
            if standoff:
                for j,(xx,zz) in enumerate([(30.8,za),(1119.2,zb)],1):
                    s=cyl(10,5,(xx,y,zz),(0,n,0)).cut(cyl(3.3,6,(xx,y,zz),(0,n,0)))
                    add(f'BRACE_SPACER_{k}_{j}',s)
    return out

def bolted_datums(parts):
    """New flush rail-datum-to-extrusion mounting, not the old weld detail."""
    out=[]
    for name,s,c in parts:
        if name in ('Y_DATUM_L','Y_DATUM_R'):
            left=name.endswith('_L'); x=58.8 if left else 1091.2; sg=-1 if left else 1
            # Flathead envelope flush at rail seat; actual rail holes, required
            # separation & T-nut/thread capacity must be confirmed before drilling.
            for y in (45,205,365,525,685,845,1005,1165,1325,1400):
                s=s.cut(cyl(3.3,10,(x-sg,y,1036),(sg,0,0)))
                s=s.cut(cq.Solid.makeCone(6.5,3.3,3.2,cq.Vector(x,y,1036),cq.Vector(sg,0,0)))
            s=s.clean(); name+='__BOLTED_REDESIGN'
        out.append((name,s,c))
    return out

def wet_support_option():
    """Optional 3 directly bearing center posts; no bolts shared with the pan."""
    out=[]
    for i,y in enumerate((80,610,1160),1):
        out.append((f'OPT_CENTER_LEG_{i}',bar(555,y,69.5,'Z',730),DARK))
        foot=cyl(33,9,(575,y+20,0)).fuse(cyl(7,54.5,(575,y+20,9)),box(555,y,63.5,40,40,6)).clean()
        out.append((f'OPT_FOOT_{i}_RATED_PART_ALLOWANCE',foot,FOOT))
        for j,yy in enumerate((y-6,y+40),1):
            p=box(527,yy,805,96,6,29).fuse(box(562,yy,735,26,6,74)).clean()
            p=drill(p,[((xx,yy-1,zz),(0,1,0),8) for xx,zz in ((540,819.5),(610,819.5),(575,748),(575,779))],3.3)
            out.append((f'OPT_BEARER_CLIP_{i}_{j}',p,BLUE))
    return out
