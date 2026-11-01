"""Complete low-cost welded wood/plasma table, mm. Review geometry."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'extrusion-wood-plasma'
sys.path.insert(0,str(BASE))
from frame import box,cyl,strap
from process_bed import tube_x,tube_y,tube_z
from motion_context import motion_parts, _bare_motion, _install_plasma
import importlib.util
_spec=importlib.util.spec_from_file_location('source_exchange',BASE/'build.py')
_exchange=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_exchange)
clashes,export=_exchange.clashes,_exchange.export
from preview import render,font
from PIL import Image,ImageDraw

OUT=HERE/'review'
LOWER=150.
FLOOR=735.85
SHEET=1.8974
INSIDE=FLOOR+SHEET
SLAT_BOTTOM=INSIDE+12.
SLAT_TOP=SLAT_BOTTOM+40.
WOOD_T=19.05
XRAILS=(33.4,1116.6)
STATIONS=(100.,600.,1100.)
PADS=[121.4+251*i for i in range(4)]
SLATS=[p+o for p in PADS for o in (40.,210.)]
STEEL=(.27,.36,.40); DARK=(.15,.24,.29); HOT=(.47,.53,.55)
AL=(.69,.73,.74); WOOD=(.73,.65,.48); LIGHT=(.75,.77,.73)

def hole(s,r,p,h,d=(0,0,1)):
    return s.cut(cyl(r,h,p,d))

def welded_band(a,b,normal):
    delta=cq.Vector(*b)-cq.Vector(*a)
    plane=cq.Plane(origin=a,xDir=delta.normalized().toTuple(),normal=normal)
    return cq.Workplane(plane).center(delta.Length/2,0).rect(delta.Length+4,19.05).extrude(3.175).val()

def motion(hot):
    # The boxed beams replace the previous full-length guide-datum blanks.
    return [(n,s.translate((0,0,-LOWER)),c) for n,s,c in motion_parts(hot) if n not in ('Y_DATUM_L','Y_DATUM_R')]

def components():
    fixed,wood,plasma=[],[],[]
    def add(n,s,c=STEEL,to=fixed):to.append((n,s.clean(),c))
    for k,x in enumerate(XRAILS):
        name='LR'[k]
        rail=tube_y(x-25.4,0,863.1375,50.8,1450,50.8,1.9)
        # Actual module and guide patterns are transfer drilled after measurement.
        add(name+'_direct_2in_RHS_rail',rail,DARK)
        for i,y in enumerate(STATIONS):
            a=50.8 if i==1 else 31.75
            add(f'{name}_leg_{i}',tube_z(x-a/2,y-a/2,69.5,a,a,793.6375,1.9),STEEL)
            # Fixed fabricated feet use a short tube and a bearing cap.
            add(f'{name}_ground_pad_{i}',box(x-23.5,y-23.5,0,47,47,4.7625),LIGHT)
            add(f'{name}_foot_tube_{i}',tube_z(x-15.875,y-15.875,4.7625,31.75,31.75,59.975,1.9),STEEL)
            p=55. if i==1 else 47.
            add(f'{name}_foot_bearing_cap_{i}',box(x-p/2,y-p/2,64.7375,p,p,4.7625),STEEL)
        # Side X pairs. Both ends weld on the exterior post faces.
        for i,(a,b) in enumerate(zip(STATIONS,STATIONS[1:])):
            for j,(za,zb,n) in enumerate(((150.,775.,-1),(775.,150.,1))):
                xx=x+n*25.4
                add(f'{name}_side_brace_{i}_{j}',welded_band((xx,a,za),(xx,b,zb),(n,0,0)),DARK)
                for end_y,end_z,is_small in ((a,za,i==0),(b,zb,i==1)):
                    if is_small:
                        px=x+15.875 if n>0 else x-25.4
                        add(f'{name}_side_spacer_{i}_{j}',box(px,end_y-7.5,end_z-9.525,9.525,15,19.05))
        # Small stop outstands replace the wide full-length cap.
        for j,y in enumerate((90.,140.,1410.,1442.)):
            xx=58.8 if k==0 else 1072.2
            tab=box(xx,y-10,906.,19,20,7.9375)
            tab=hole(tab,3.3,(66.5 if k==0 else 1083.5,y,903),12)
            add(f'{name}_welded_steel_stop_tab_{j}',tab,STEEL)
    for i,y in enumerate(STATIONS):
        w=50.8 if i==1 else 31.75
        a=XRAILS[0]+w/2;b=XRAILS[1]-w/2
        add(f'pan_crossbeam_{i}',tube_x(a,y-12.7,FLOOR-50.8,b-a,25.4,50.8,1.5))
    for i,(a,b) in enumerate(((112.7,587.3),(612.7,1087.3))):
        add(f'center_backbone_{i}',tube_y(562.3,a,FLOOR-50.8,25.4,b-a,50.8,1.5))
    for i,y in enumerate((100.,1100.)):
        for j,(a,b,n) in enumerate(((200.,680.,-1),(680.,200.,1))):
            yy=y+n*25.4
            add(f'end_brace_{i}_{j}',welded_band((XRAILS[0],yy,a),(XRAILS[1],yy,b),(0,n,0)),DARK)
            py=y+15.875 if n>0 else y-25.4
            for k,(x,z) in enumerate(((XRAILS[0],a),(XRAILS[1],b))):
                add(f'end_spacer_{i}_{j}_{k}',box(x-9.525,py,z-7.5,19.05,9.525,15))
    # Full supported floor has no drain penetration. Drain hose is used when cold.
    add('pan_floor_unbroken_830x1030',box(160,85,FLOOR,830,1030,SHEET),HOT)
    for k,x in enumerate((160.,990.-SHEET)):
        add(f'pan_wall_{k}',box(x,85,INSIDE,SHEET,1030,35-SHEET),HOT)
        # Dry structural lip stands above the water-retaining wall. Flood slots keep
        # the 35 mm water boundary. No liquid capacity is credited above the notch.
        sx=160.-SHEET if k==0 else 990.
        lip=box(sx,95,FLOOR+35,SHEET,1010,25)
        for y in range(120,1090,80):lip=lip.cut(box(sx-1,y,FLOOR+34.9,SHEET+2,30,12))
        add(f'pan_edge_stiffener_{k}',lip,HOT)
    for k,y in enumerate((85.,1115.-SHEET)):
        wall=box(160+SHEET,y,INSIDE,830-2*SHEET,SHEET,35-SHEET)
        if k==0:wall=wall.cut(box(480,y-1,INSIDE+26,80,SHEET+2,12))
        add(f'pan_end_{k}',wall,HOT)
    # Overflow drops ahead of the front crossbeam, then returns beneath it.
    # The receiver stays fully under the steel pan.
    from process_bed import yz
    drop=box(478,65,650,84,20,INSIDE+36-650)
    drop=drop.cut(box(478+SHEET,65+SHEET,650+SHEET,84-2*SHEET,20-2*SHEET,140))
    drop=drop.cut(box(480,83,INSIDE+26,80,4,20))
    drop=drop.cut(box(480,83,650,80,4,13))
    ret=yz(478,84,[(65,650-SHEET),(250,648-SHEET),(250,648),(65,650)])
    for x in (478.,562.-SHEET):
        ret=ret.fuse(yz(x,SHEET,[(65,650),(250,648),(250,660),(65,662)]))
    down=box(478,250,550,84,SHEET,110)
    add('independent_overflow_return',cq.Compound.makeCompound([drop,ret,down]),HOT)
    # Side combs are welded against sidewalls with a short connecting toe.
    for k,x in enumerate((165.,575.,985.)):
        comb=box(x-1.5875,90,INSIDE,3.175,1020,31.75)
        for y in SLATS:comb=comb.cut(box(x-3,y-.3,SLAT_BOTTOM,7,SHEET+.6,22))
        for y in range(103,1080,80):comb=comb.cut(box(x-3,y,INSIDE-.1,7,12,7))
        add(f'comb_{k}',comb,HOT)
        if k in (0,2):
            a=161.8974 if k==0 else 986.5875
            add(f'comb_wall_join_toe_{k}',box(a,90,INSIDE,1.5151,1020,3.175),HOT)
    # The same replaceable steel support grid carries each removable wood pad.
    # All clamps and locators must be checked after the slats are consumed/replaced.
    for j,y in enumerate(SLATS):
        s=box(163,y,SLAT_BOTTOM,824,SHEET,40)
        i=j//2
        for x in (365.,785.):
            s=s.cut(box(x-10,y-.1,SLAT_TOP-3.175,20,SHEET+.2,4))
            tab=hole(box(x-10,y-6,SLAT_TOP-3.175,20,19.05,3.175),2.75,(x,y+6.5,SLAT_TOP-4),6)
            boss=hole(box(x-4.5,y+2,SLAT_TOP-7.675,9,9,4.5),2.5,(x,y+6.5,SLAT_TOP-8),6)
            add(f'pad_weldnut_{j}_{x}',boss,HOT)
            add(f'pad_clamp_tab_{j}_{x}',tab,HOT)
        add(f'slat_{j:02}_40mm',s,HOT)
    for i,y in enumerate(PADS):
        board=box(162,y,SLAT_TOP,826,250,WOOD_T)
        for x,yy in ((365.,y+46.5),(785.,y+46.5),(365.,y+216.5),(785.,y+216.5)):
            board=hole(board,2.75,(x,yy,SLAT_TOP-1),WOOD_T+2)
            cone=cq.Solid.makeCone(5.3,2.75,2.55,cq.Vector(x,yy,SLAT_TOP+WOOD_T),cq.Vector(0,0,-1))
            board=board.cut(cone)
            bolt=cyl(2.45,27.45,(x,yy,SLAT_TOP+WOOD_T-30)).fuse(cone)
            add(f'installed_pad_M5_{i}_{x}_{yy}',bolt,AL,wood)
        add(f'removable_wood_pad_{i}',board,WOOD,wood)
    # Cold storage is a small closed case in the rear bay. The same four bare pads
    # load vertically from above with the gantry parked at its front limit.
    case_x,case_y,case_z=160.,1240.,559.375
    metal=.315
    add('cold_case_floor',box(case_x,case_y,case_z,830,84,metal),LIGHT)
    for k,y in enumerate((case_y,case_y+84-metal)):
        add(f'cold_case_wall_{k}',box(case_x,y,case_z+metal,830,metal,255-metal),LIGHT)
    for k,x in enumerate((case_x-9.525,case_x+830)):
        end=box(x,case_y,case_z,9.525,84,255)
        for yy in (case_y+16,case_y+68):
            end=hole(end,2.5,(x+4.7625,yy,case_z+242),15)
        add(f'cold_case_owned_Al_end_{k}',end,AL)
    # Secondary cover made from one 609.6 mm sheet remnant and an owned Al patch.
    # It is removed for transfer, then resecured using the priced M5 fasteners.
    for suffix,x,l,t,c in [('sheet',case_x-9.525,609.6,metal,LIGHT),('Al_patch',case_x-9.525+609.6,239.45,9.525,AL)]:
        lid=box(x,case_y,case_z+255,l,84,t)
        for xx in (case_x-4.7625,case_x+834.7625):
            if x<xx<x+l:
                for yy in (case_y+16,case_y+68):lid=hole(lid,2.75,(xx,yy,case_z+254),t+2)
        add('cold_case_lid_'+suffix,lid,c,plasma)
    for i,y in enumerate(PADS):
        board=next(s for n,s,c in wood if n==f'removable_wood_pad_{i}')
        local=board.translate((-162,-y,-SLAT_TOP))
        parked=local.rotate((0,0,0),(1,0,0),90).translate((162,case_y+1.5+WOOD_T+i*(WOOD_T+1),case_z+metal))
        add(f'parked_wood_pad_{i}',parked,WOOD,plasma)
    # Directly seated rack arms use the priced beam drops.
    for k,x in enumerate((190.,960.)):
        add(f'case_hanger_{k}',tube_z(x-25.4,1074.6,508.575,50.8,50.8,176.475,1.9))
        add(f'case_arm_{k}',tube_y(x-12.7,1125.4,508.575,25.4,300,50.8,1.5))
    # The commercial 34 L tub is only a conservative fit envelope. Mark actual
    # usable volume at least 30 L and keep it on a full-support floor.
    add('cold_drain_receiver_400x650x300_ENVELOPE',box(320,140,0,400,650,300).cut(box(324,144,4,392,642,297)),(.35,.48,.36))
    return fixed,wood,plasma

def main():
    OUT.mkdir(exist_ok=True)
    fixed,wood,plasma=components()
    report={'CAD_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for label,parts,hot in (('CARVING',wood,False),('PLASMA',plasma,True)):
        allparts=fixed+parts+motion(hot)
        assert all(s.isValid() and len(s.Solids()) for _,s,_ in allparts)
        report[label]={'exchange':export(OUT/(label+'.step'),allparts),
                       'fixed_self':clashes(fixed,fixed,True),'bed_vs_fixed':clashes(parts,fixed),
                       'bed_self':clashes(parts,parts,True),'motion_vs_external':clashes(motion(hot),fixed+parts)}
    (OUT/'geometry.json').write_text(json.dumps(report,indent=2))
    print({mode:{key:len(val.get('interferences_gt_0p05_mm3',[])) for key,val in records.items()}
           for mode,records in report.items() if isinstance(records,dict)},flush=True)
    scene=Image.new('RGB',(1360,770),'#f5f7f7');draw=ImageDraw.Draw(scene)
    draw.text((42,22),'Complete wood and plasma table',font=font(35,True),fill='#183449')
    draw.text((45,76),'Boxed steel rails / six braced legs / structural steel bed / enclosed pad storage',font=font(18),fill='#526771')
    for j,(label,extra,hot) in enumerate((('CARVING',wood,False),('PLASMA',plasma,True))):
        im=render(fixed+extra+motion(hot),back=hot,w=840,h=720);im.thumbnail((620,560))
        scene.paste(im,(40+665*j+(620-im.width)//2,130))
        draw.text((48+665*j,710),label,font=font(24,True),fill='#183449')
    scene.save(OUT/'overview.png')
if __name__=='__main__':main()
