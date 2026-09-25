from pathlib import Path
import math, json, sys
from PIL import Image, ImageDraw, ImageFont
from render_cad import render_scene

ROOT=Path(__file__).resolve().parent
exec((ROOT/'build_design.py').read_text().split('# Accurate spatial concept;')[0],globals())
C.setTitle('CNC / plasma stand | Integrated bed and water system | Revision C')
OUTIMG=ROOT/'output'/'bed-system'; OUTIMG.mkdir(parents=True,exist_ok=True)
GRAPH='#34454F'; SKIN='#263842'; EDGE='#516774'; MDF='#C9A16C'; ORANGE='#ECA23E'
T=50.8

def page(n,title,subtitle):
    rect(0,0,W,H,white,None)
    text(40,H-38,'WORKSHOP / INTEGRATED MACHINE DESIGN',10,RAIL,True)
    right(W-40,H-38,'REVISION C  |  24 SEP 2026',10,MUTED)
    text(40,H-75,title,26,INK,True)
    text(40,H-98,subtitle,10.5,MUTED)
    line(40,H-113,W-40,H-113,LINE)
    line(40,43,W-40,43,LINE)
    text(40,26,'DIMENSIONS mm / CONCEPT GEOMETRY / VERIFY INTERFACES AND LOADS BEFORE FABRICATION',8,MUTED)
    right(W-40,26,f'{n} / 6',9,MUTED)

def scene(mode):
    boxes=[]; rods=[]
    def b(x,y,z,dx,dy,dz,c): boxes.append((x,y,z,dx,dy,dz,c))
    def r(a,bb,w,c): rods.append((a,bb,w,c))
    def beam(y,z):
        for yy in [y-50.8,y]: b(59,yy,z,1032,50.8,50.8,GRAPH)
        for x in [53,1091]: b(x,y-50.8,z,6,101.6,50.8,ALU)
        for x in [59,1051]: b(x,y-45,z-30,40,90,30,ALU)
        # Receiver clamps shown schematically, outside useful cut area.
        for x in [67,1065]: b(x,y-18,z+51,18,36,7,ORANGE)
    def panel(x,y,z,explode=0):
        for yy in [y,y+372]: b(x,yy,z,497,25,25,GRAPH)
        for xx in [x,x+236,x+472]: b(xx,y+25,z,25,347,25,GRAPH)
        b(x,y,z+25+explode,497,397,8,ALU)
        b(x,y,z+33+2*explode,497,397,19,MDF)
        # Flush removable access plugs, below these are metal clamping sleeves.
        for dx,dy in [(32,32),(465,32),(32,365),(465,365)]:
            b(x+dx-6,y+dy-6,z+51.8+2*explode,12,12,.4,EDGE)
    # Main chassis - six legs, integral upper rail supports.
    for x in [0,1099.2]:
        for y in [0,699.6,1399.2]:
            b(x-15,y-15,0,80,80,12,GRAPH); b(x+16,y+16,12,18,18,38,ALU)
            b(x,y,50,T,T,949.2,GRAPH)
        b(x,0,999.2,T,1450,T,GRAPH)
        for y in [50.8,750.4]: b(x,y,230,T,648.8,T,GRAPH)
        b(x-24.6,0,1050,100,1450,8,ALU)
    b(50.8,0,50,1048.4,T,T,GRAPH)
    b(50.8,1399.2,230,1048.4,T,T,GRAPH)
    for y in [0,1399.2]: b(50.8,y,679.2,1048.4,T,T,GRAPH)
    # Independent, fixed router receiver ledgers tied to all six legs.
    for x in [50.8,1048.4]: b(x,0,789.2,T,1450,T,GRAPH)
    # Independent pan bearers, below the routing load path.
    for y in [175,675,1175]: b(50.8,y,679.2,1048.4,T,T,EDGE)
    for x in [25.4,1124.6]:
        r((x,80,290),(x,675,975),30,EDGE)
        r((x,780,290),(x,1370,975),30,EDGE)
    r((75,1425,290),(1075,1425,965),30,EDGE)
    # Narrowed fixed water pan; lowest floor735, rim835, slats850.
    b(115,75,735,920,1200,3,ALU)
    for x in [115,1032]: b(x,75,738,3,1200,97,ALU)
    for y in [75,1272]: b(118,y,738,914,3,97,ALU)
    for y in range(120,1240,60): b(135,y,775,880,3,75,EDGE)
    # Reservoir within rear half of chassis; all capacity figures use interior dims.
    b(110,800,175,930,530,380,ALU)
    b(104,794,552,942,542,10,GRAPH)
    r((995,1120,735),(995,1120,592),32,RAIL)
    b(977,1102,641,36,36,55,GRAPH); b(985,1092,662,65,56,43,ORANGE)
    r((995,1120,592),(965,1110,570),32,RAIL)
    r((115,1160,820),(160,1200,570),24,RAIL)
    # Closed front storage cabinet. Cutaway exposes its entirely internal storage.
    b(65,55,125,1020,700,5,EDGE)
    b(65,55,130,5,700,575,GRAPH); b(1080,55,130,5,700,575,GRAPH)
    b(65,750,130,1020,5,575,GRAPH)
    if mode not in ['cutaway','exploded']:
        b(70,51,132,503,4,566,GRAPH); b(578,57,132,502,4,566,GRAPH)
        for x in [524,596]: b(x,42,390,12,14,115,ALU)
        for x in [88,550,595,1063]:
            for zc in [155,673]: b(x,45,zc,8,6,8,ORANGE)
    if mode=='cutaway':
        # Front covers park on retained side studs within the existing rail overhang.
        b(-8,80,205,4,503,566,GRAPH)
        b(1154,80,205,4,503,566,GRAPH)
        # Stow panels first, then angled beams in front, reverse for assembly.
        for x in [130,623]:
            for y in [525,580,635]:
                b(x,y,150,397,25,497,GRAPH)
                b(x,y+25,150,397,8,497,ALU)
                b(x,y+33,150,397,19,497,MDF)
        ang=math.radians(25)
        for y in [110,220,330,440]:
            for yy in [y-25.4,y+25.4]:
                r((85,yy,185),(85+1044*math.cos(ang),yy,185+1044*math.sin(ang)),50.8,GRAPH)
    # Designed removable skins: conceal bracing, preserve access to pads and wiring.
    if mode not in ['cutaway','exploded']:
        for x in [-2,1150]:
            b(x,62,288,2,615,498,GRAPH); b(x,772,288,2,615,498,GRAPH)
            for yy in [610,1320]: b(x-1,yy,560,4,35,90,ALU)
    # Front service/status console, indicative not final electrical layout.
    b(792,3,739,304,36,76,GRAPH)
    b(811,-1,756,110,5,42,ALU)
    b(946,-8,756,26,12,26,ORANGE)
    b(1000,-7,752,35,13,35,RED)
    if mode in ['router','exploded']:
        for y in [75,475,875,1275]: beam(y,870 if mode=='router' else 930)
        for iy,y in enumerate([76.5,476.5,876.5]):
            for ix,x in enumerate([76.5,576.5]):
                panel(x,y,920.8 if mode=='router' else 1110,25 if(mode=='exploded' and ix==0 and iy==0)else 0)
    if mode!='exploded':
        # Exact product identities retained; mounting details remain schematic.
        for x in [0,1099.2]:
            b(x+5.4,225,1060,40,1125,40,RAIL)
            b(x-3.1,1350,1060,57,75,57,GRAPH)
            b(x+20,240,1101,10,1095,7,ALU)
            b(x+52,160,978,3,1190,74,ALU)
        yy=1000 if mode=='router' else 1100; xx=685
        for x in [25.4,1124.6]:
            b(x-35,yy-45,1100,70,90,15,ALU)
            b(x-50,yy-60,1115,100,120,12,ORANGE)
            b(x-6,yy-30,1127,12,110,113,ORANGE)
        b(-25,yy+10,1127,1200,80,80,ALU)
        b(125,yy-30,1147,925,40,40,RAIL);b(1050,yy-38,1140,75,57,57,GRAPH)
        b(xx-45,yy-45,1127,90,15,70,ALU)
        b(xx-40,yy-83,1020.8,80,38,219,ALU)
        b(xx-28.5,yy-81,1294.8,57,57,56,GRAPH)
        b(xx-10,yy-65,1239.8,20,20,55,ALU)
        if mode=='router':
            b(xx-38,yy-94,1035.8,76,11,130,ORANGE)
            b(xx-36,yy-136,1020.8,72,72,180,GRAPH)
            b(xx-7,yy-108,972.8,14,16,48,ORANGE)
        else:
            b(xx-22,yy-95,910,44,12,200,ORANGE)
            b(xx-15,yy-120,885,30,32,155,GRAPH)
            b(xx-6,yy-110,850,12,16,35,ORANGE)
    return boxes,rods

renders={}
for mode in ['router','plasma','exploded','cutaway']:
    path=OUTIMG/f'{mode}.png'
    if '--reuse-images' in sys.argv and path.exists(): continue
    bs,rs=scene(mode)
    renders[mode]=render_scene(bs,rs,path,width=1800,height=1550,background='#F5F7F7',shadow=True)
    print('Rendered',mode,flush=True)

def pic(mode,x,y,w,h): C.drawImage(str(OUTIMG/f'{mode}.png'),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')

exec((ROOT/'bed_system_pages.py').read_text(),globals())
