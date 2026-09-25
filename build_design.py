from pathlib import Path
import math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
PDF = OUT / 'plasma-router-stand-concept.pdf'
W,H = landscape(A3)
C = canvas.Canvas(str(PDF), pagesize=(W,H))
C.setTitle('KHMOS / RATTMMOTOR CNC stand | Sand-filled 2-inch chassis | Concept B')
C.setAuthor('Prepared for Gluis')
INK='#182E3B'; MUTED='#536B79'; LINE='#BAC8CE'; PAPER='#F5F7F7'
STEEL='#3C5360'; LIGHT='#76909E'; RAIL='#26A3A6'; ALU='#CBD7DC'; GOLD='#DF9C3D'
RED='#B9583E'

def col(v): return HexColor(v) if isinstance(v,str) else v
def text(x,y,s,size=11,color=INK,bold=False):
    C.setFillColor(col(color)); C.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
    C.drawString(x,y,str(s))
def right(x,y,s,size=11,color=INK,bold=False):
    C.setFillColor(col(color)); C.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
    C.drawRightString(x,y,str(s))
def line(x1,y1,x2,y2,color=LINE,width=0.7,dash=None):
    C.setStrokeColor(col(color)); C.setLineWidth(width); C.setDash(dash or [])
    C.line(x1,y1,x2,y2); C.setDash([])
def rect(x,y,w,h,fill=None,stroke=LINE,width=.7):
    C.setLineWidth(width)
    if fill: C.setFillColor(col(fill))
    if stroke: C.setStrokeColor(col(stroke))
    C.rect(x,y,w,h,fill=int(fill is not None),stroke=int(stroke is not None))
def poly(points,fill,stroke=INK,width=.45):
    p=C.beginPath(); p.moveTo(*points[0])
    for a in points[1:]: p.lineTo(*a)
    p.close(); C.setFillColor(col(fill)); C.setLineWidth(width)
    if stroke: C.setStrokeColor(col(stroke))
    C.drawPath(p,fill=1,stroke=bool(stroke))
def para(x,y,w,s,size=11,color=INK,leading=None):
    style=ParagraphStyle('p',fontName='Helvetica',fontSize=size,leading=leading or size*1.4,textColor=col(color))
    p=Paragraph(s,style); _,h=p.wrap(w,1000); p.drawOn(C,x,y-h); return y-h
def heading(x,y,k,title):
    text(x,y,k,10,RAIL,True); text(x,y-24,title,20,INK,True)
def bullet_block(x,y,w,items,size=11):
    for s in items:
        text(x,y-10,'-',size,RAIL,True)
        y=para(x+14,y,w-14,s,size)-10
    return y
def tag(x,y,n):
    C.setFillColor(col(INK)); C.circle(x,y,10,fill=1,stroke=0)
    C.setFillColor(white); C.setFont('Helvetica-Bold',10); C.drawCentredString(x,y-3,str(n))
def dim(x1,y1,x2,y2,label,offset=0):
    dx=x2-x1; dy=y2-y1; length=math.hypot(dx,dy)
    nx,ny=-dy/length,dx/length
    a=(x1+nx*offset,y1+ny*offset); b=(x2+nx*offset,y2+ny*offset)
    line(x1,y1,a[0]+nx*4,a[1]+ny*4,MUTED,.5)
    line(x2,y2,b[0]+nx*4,b[1]+ny*4,MUTED,.5)
    line(*a,*b,MUTED,.55)
    ux,uy=dx/length,dy/length
    for p,sgn in [(a,1),(b,-1)]:
        for q in [-1,1]:
            line(*p,p[0]+sgn*ux*5+nx*q*2,p[1]+sgn*uy*5+ny*q*2,MUTED,.6)
    mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
    if abs(dy)>abs(dx):
        C.saveState(); C.translate(mx-5,my); C.rotate(90)
        C.setFillColor(white); sw=stringWidth(label,'Helvetica',9)
        C.rect(-sw/2-3,-2,sw+6,12,fill=1,stroke=0)
        C.setFillColor(col(INK)); C.setFont('Helvetica',9); C.drawCentredString(0,0,label); C.restoreState()
    else:
        sw=stringWidth(label,'Helvetica',9); rect(mx-sw/2-3,my-2,sw+6,12,white,None)
        C.setFillColor(col(INK)); C.setFont('Helvetica',9); C.drawCentredString(mx,my,label)

def page(n,title,subtitle):
    rect(0,0,W,H,white,None)
    text(40,H-38,'WORKSHOP / MACHINE DESIGN',10,RAIL,True)
    right(W-40,H-38,'CONCEPT B  |  24 SEP 2026',10,MUTED)
    text(40,H-75,title,27,INK,True)
    text(40,H-98,subtitle,11,MUTED)
    line(40,H-113,W-40,H-113,LINE)
    line(40,43,W-40,43,LINE)
    text(40,26,'ALL DIMENSIONS mm  /  DO NOT SCALE  /  PROPOSED GEOMETRY - NOT RELEASED FOR FABRICATION',8,MUTED)
    right(W-40,26,f'{n} / 4',9,MUTED)

# Accurate spatial concept; vendor details deliberately schematic.
boxes=[]; rods=[]
def box(x,y,z,dx,dy,dz,color): boxes.append((x,y,z,dx,dy,dz,color))
def rod(a,b,width,color): rods.append((a,b,width,color))
T=50.8
RX=1150-T
RY=1450-T
Y_CENTERS=[T/2,1450/2,1450-T/2]
def model():
    # Six feet/legs, exact 2-inch tube; top of main steel at930.
    for x in [0,RX]:
        for y in [0,(1450-T)/2,RY]:
            box(x-15,y-15,0,80,80,12,STEEL)
            box(x+16,y+16,12,18,18,38,ALU)
            box(x,y,50,T,T,829.2,STEEL)
    for x in [0,RX]:
        box(x,0,879.2,T,1450,T,STEEL)
        for y in [T,750.4]: box(x,y,230,T,648.8,T,STEEL)
        box(x-24.6,0,930,100,1450,8,LIGHT)
        # HMS40 approximate envelopes; replace from supplier drawing before drilling.
        box(x+5.4,225,940,40,1125,40,RAIL)
        box(x-3.1,1350,940,57,75,57,STEEL)
        box(x+20,240,981,10,1095,10,ALU)
    for y in [0,RY]:
        box(T,y,230,1048.4,T,T,STEEL)
        box(T,y,679.2,1048.4,T,T,STEEL)
    for y in [175,675,1175]:
        box(T,y,679.2,1048.4,T,T,LIGHT)
        for x in [44.8,RX]: box(x,y-15,679.2,6,80,200,LIGHT)
    # Rear and both side diagonal braces, left side crossed for visible stiffness.
    for x in [25.4,1124.6]:
        rod((x,75,290),(x,674,829),28,LIGHT)
        rod((x,775,290),(x,1375,829),28,LIGHT)
    rod((75,1424.6,290),(1075,1424.6,829),28,LIGHT)
    # Water pan external1000x1200x100; slats project15 above lip.
    box(75,75,735,1000,1200,3,ALU)
    box(75,75,738,3,1200,97,ALU)
    box(1072,75,738,3,1200,97,ALU)
    box(78,75,738,994,3,97,ALU)
    box(78,1272,738,994,3,97,ALU)
    for y in range(120,1240,60): box(95,y,775,960,3,75,LIGHT)
    # Adjustable shields, fixed to stand only, clear of moving saddle.
    for x in [63,1084]: box(x,155,850,3,1175,60,LIGHT)
    yy=775; xx=655
    for x in [25.4,1124.6]:
        box(x-35,yy-45,980,70,90,15,ALU)
        box(x-50,yy-60,995,100,120,12,GOLD)
        box(x-6,yy-30,1007,12,110,113,GOLD)
    box(-25,yy+10,1007,1200,80,80,ALU)
    box(125,yy-30,1027,925,40,40,RAIL)
    box(1050,yy-38,1020,75,57,57,STEEL)
    box(xx-45,yy-45,1007,90,15,70,ALU)
    # ZBX80 body219mm, overall330 incl motor; mounting offset remains provisional.
    box(xx-40,yy-83,900,80,38,219,LIGHT)
    box(xx-28.5,yy-81,1174,57,57,56,STEEL)
    box(xx-10,yy-65,1119,20,20,55,ALU)
    box(xx-38,yy-94,915,76,11,130,GOLD)
    # Router shown as a generic ER17 candidate, not the unverified spindle model.
    box(xx-36,yy-136,900,72,72,180,STEEL)
    box(xx-7,yy-108,850,14,16,50,GOLD)
model()

def shade(color,f):
    c=col(color); return Color(min(1,c.red*f),min(1,c.green*f),min(1,c.blue*f))
def iso(ox,oy,s):
    def p(q):
        x,y,z=q; return ox+s*(.8*x+.6*y), oy+s*(-.36*x+.48*y+.9*z)
    items=[]
    for x,y,z,dx,dy,dz,color in boxes:
        pts=[(x,y,z),(x+dx,y,z),(x+dx,y+dy,z),(x,y+dy,z),(x,y,z+dz),(x+dx,y,z+dz),(x+dx,y+dy,z+dz),(x,y+dy,z+dz)]
        faces=[([0,1,5,4],.85),([1,2,6,5],1),([4,5,6,7],1.12)]
        for inds,f in faces:
            qs=[pts[i] for i in inds]
            def lerp(a,b,t): return tuple(v+(w-v)*t for v,w in zip(a,b))
            def depth(v): return .54*v[0]-.72*v[1]+.6*v[2]
            # Split long faces so a face-average depth does not hide the rails.
            n=max(1,math.ceil(math.dist(qs[0],qs[1])/85))
            m=max(1,math.ceil(math.dist(qs[0],qs[3])/85))
            def uv(u,v): return lerp(lerp(qs[0],qs[1],u),lerp(qs[3],qs[2],u),v)
            for i in range(n):
                for j in range(m):
                    q=[uv(i/n,j/m),uv((i+1)/n,j/m),uv((i+1)/n,(j+1)/m),uv(i/n,(j+1)/m)]
                    items.append((sum(depth(v) for v in q)/4,'f',q,shade(color,f)))
            for a,b in zip(qs,qs[1:]+qs[:1]):
                num=max(1,math.ceil(math.dist(a,b)/70))
                for i in range(num):
                    q=[lerp(a,b,i/num),lerp(a,b,(i+1)/num)]
                    items.append((sum(depth(v) for v in q)/2+.1,'e',q,INK))
    for a,b,width,color in rods:
        dep=sum(.54*v[0]-.72*v[1]+.6*v[2] for v in [a,b])/2
        items.append((dep,'r',[a,b],(width,color)))
    for _,kind,qs,color in sorted(items,key=lambda q:q[0]):
        if kind=='f': poly([p(q) for q in qs],color,color,.22)
        elif kind=='e': pass
        else: line(*p(qs[0]),*p(qs[1]),color[1],color[0]*s)
    return p

def plan(x,y,s):
    def rr(a,b,w,h,fill,stroke=INK): rect(x+a*s,y+b*s,w*s,h*s,fill,stroke,.5)
    rr(0,0,1150,1450,None)
    for a in [0,RX]:
        rr(a,0,T,1450,STEEL)
        rr(a+5.4,225,40,1125,RAIL)
        rr(a-3.1,1350,57,75,STEEL)
        rr(a-9.6,730,70,90,ALU)
    rr(75,75,1000,1200,'#E7EEF0')
    for yy in range(120,1240,60): line(x+95*s,y+yy*s,x+1055*s,y+yy*s,LINE,.6)
    C.setDash([4,3]); C.setStrokeColor(col(GOLD)); C.setLineWidth(1.2)
    C.rect(x+185*s,y+185*s,780*s,980*s,fill=0,stroke=1); C.setDash([])
    rr(-25,785,1200,80,ALU)
    rr(125,745,925,40,RAIL)
    rr(1050,737,75,57,STEEL)
    rr(615,692,80,53,LIGHT)
    C.setFillColor(col(GOLD)); C.circle(x+655*s,y+675*s,5,fill=1,stroke=0)
    for a in [25.4,1124.6]: line(x+a*s,y,x+a*s,y+1450*s,MUTED,.5,[5,3])
    dim(x,y,x+1150*s,y,'1150 steel width',-28)
    dim(x,y,x,y+1450*s,'1450 steel length',28)
    dim(x+25.4*s,y+1450*s,x+1124.6*s,y+1450*s,'1099.2 Y rail centers',22)

def front(x,y,s):
    def rr(a,b,w,h,fill,stroke=INK): rect(x+a*s,y+b*s,w*s,h*s,fill,stroke,.5)
    line(x-40*s,y,x+1220*s,y,LINE,.6)
    for a in [0,RX]:
        rr(a,50,T,829.2,STEEL); rr(a,879.2,T,T,STEEL)
        rr(a-24.6,930,100,8,LIGHT); rr(a+5.4,940,40,40,RAIL)
        rr(a-9.6,980,70,15,ALU); rr(a-24.6,995,100,12,GOLD)
        rr(a+19.4,1007,12,113,GOLD); rr(a-15,0,80,12,STEEL)
    rr(T,230,1048.4,T,STEEL); rr(T,679.2,1048.4,T,LIGHT)
    rr(75,735,1000,100,ALU)
    for a in [95,300,510,720,930,1052]: rr(a,775,3,75,LIGHT)
    rr(-25,1007,1200,80,ALU); rr(125,1027,925,40,RAIL)
    rr(1050,1020,75,57,STEEL)
    rr(615,900,80,219,LIGHT); rr(645,1119,20,55,ALU); rr(626.5,1174,57,56,STEEL)
    rr(619,900,72,180,STEEL); rr(648,850,14,50,GOLD)
    line(x-25*s,y+850*s,x+1180*s,y+850*s,GOLD,.7,[4,2])
    dim(x+1150*s,y,x+1150*s,y+930*s,'930 steel rail-support top',-30)
    dim(x,y,x,y+850*s,'850 nominal slat top',30)
    dim(x-25*s,y+1087*s,x+1175*s,y+1087*s,'1200 bridge blank',22)


exec((ROOT / 'pages.py').read_text(), globals())
