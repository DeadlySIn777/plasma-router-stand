"""Render the current review, using actual assembly previews and bound reports."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=ROOT/'output/pdf/plasma-router-stand-integrated-4080-review.pdf'
W,H=792,612
INK=colors.HexColor('#173443');MUTED=colors.HexColor('#48616d')
BLUE=colors.HexColor('#236a89');PALE=colors.HexColor('#edf3f5')
RED=colors.HexColor('#963d35')
STYLE=ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14,textColor=INK)

def para(c,text,x,top,width,size=10,leading=14,color=INK):
    style=ParagraphStyle('p',parent=STYLE,fontSize=size,leading=leading,textColor=color)
    p=Paragraph(text,style);_,height=p.wrap(width,1000);p.drawOn(c,x,top-height);return top-height

def header(c,title,subtitle,page):
    c.setFillColor(INK);c.rect(0,H-9,W,9,fill=1,stroke=0)
    c.setFont('Helvetica-Bold',22);c.drawString(40,565,title)
    para(c,subtitle,40,547,712,10,14,MUTED)
    c.setStrokeColor(colors.HexColor('#c8d5dc'));c.line(40,43,752,43)
    c.setFont('Helvetica',8);c.setFillColor(MUTED)
    c.drawString(40,29,'1 November 2026 | Review only - fabrication, CAM and operating releases remain open')
    c.drawRightString(752,29,f'{page} / 3')

def photo(c,path,x,y,w,h):
    im=ImageReader(str(path));iw,ih=im.getSize();s=min(w/iw,h/ih)
    dw,dh=iw*s,ih*s;c.drawImage(im,x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    assembly=json.loads((HERE/'output/assembly-check.json').read_text())
    assert assembly['passed']and assembly['source_consistent_during_build']
    c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('Integrated 4080 small table - current review')
    c.setAuthor('Plasma-router-stand project')
    header(c,'Integrated 4080 small table','Original owner head | Full HDPE / 20100 bed | Retractable ATC | 800 X / 1000 Y / 250 working Z',1)
    c.setFillColor(colors.HexColor('#fae9e5'));c.roundRect(40,502,712,23,5,fill=1,stroke=0)
    para(c,'<b>REVIEW MODEL - Budget and actual-interface requirements are not complete.</b>',51,519,690,10,13,RED)
    for label,mode,x in(('WOOD / CARVING','WOOD',40),('PLASMA / BED UPRIGHT','PLASMA',410)):
        c.setFillColor(PALE);c.roundRect(x,143,342,345,7,fill=1,stroke=0)
        c.setFillColor(INK);c.setFont('Helvetica-Bold',12);c.drawString(x+14,467,label)
        photo(c,HERE/'output'/f'INTEGRATED_4080_SMALL_{mode}.png',x+8,183,326,273)
        caption=('Ten uncut tracks, full drill-only HDPE layers and a removable billet head.'if mode=='WOOD'else
                 'Bed parks in the front bay; covered magazine parks in the rear bay.')
        para(c,caption,x+14,171,314,9,12)
    para(c,'The pictures are rendered from the exported solid assemblies. Purple spindle/magazine volumes are capacity context. The owner boot solid is exact supplied geometry at an unregistered reference pose.',40,120,712,10,14)
    para(c,'The current source replaces earlier cassette beds and generic heads. It does not qualify the separate 4x8 design or steel machining.',40,77,712,9,12,MUTED)
    c.showPage()

    header(c,'Layout and load paths','Permanent front parking bay and rear ATC bay keep the bed and guard changes within the machine plan.',2)
    scale=.21;px,py=66,104
    fx=lambda x:px+(x+50)*scale;fy=lambda y:py+(y+160)*scale
    def rect(x,y,w,h,fill,stroke=INK,width=.7):
        c.setFillColor(fill);c.setStrokeColor(stroke);c.setLineWidth(width)
        c.rect(fx(x),fy(y),w*scale,h*scale,fill=1,stroke=1)
    # The diagram uses the same world coordinates as the source factories.
    rect(75,-40,1000,1220,colors.HexColor('#e2edf0'))
    for i in range(1,10):
        c.setStrokeColor(colors.HexColor('#a8bfc9'));c.line(fx(75+i*100),fy(-40),fx(75+i*100),fy(1180))
    rect(-14.2,-160,40,1760,INK);rect(1124.2,-160,40,1760,INK)
    for x in(-14.2,1124.2):
        for y in(-100,630,1180):rect(x,y-40,40,80,colors.HexColor('#537785'))
    rect(75,-100,1000,85.4,colors.HexColor('#d99b86'))
    for y in(300,630,1180):
        c.setStrokeColor(colors.HexColor('#9b805c'));c.setLineWidth(2)
        c.line(fx(32.15),fy(y),fx(1117.85),fy(y))
    c.setStrokeColor(BLUE);c.setLineWidth(1.8);c.setDash(5,3)
    c.rect(fx(175),fy(105.697941),800*scale,1000*scale,fill=0,stroke=1);c.setDash()
    rect(553,1230,44,367,colors.HexColor('#91a5af'))
    rect(315,1270,520,60,colors.HexColor('#c6b6d7'))
    c.setFont('Helvetica',9);c.setFillColor(MUTED)
    c.drawCentredString(fx(575),fy(1600)+12,'REAR / ATC BAY')
    c.drawCentredString(fx(575),fy(-160)-18,'FRONT / BED PARKING BAY')
    c.drawCentredString(fx(575),fy(580),'800 x 1000 tool field')
    c.saveState();c.translate(fx(-45),fy(720));c.rotate(90)
    c.drawCentredString(0,0,'1760 mm continuous headers');c.restoreState()
    top=510
    top=para(c,'<b>Defined geometry</b>',390,top,358,13,17)-10
    for text in[
        'Bed: 1000 x1220 mm; surface Z967.8. Ten uncut 1220 mm 20100 profiles over two 12.7 mm HDPE layers.',
        'Hinge: Y-100, Z967.8. Upright bed Y-100 to -14.6; highest point approximately Z2247.8.',
        'Frame: six posts and paired 1250 mm 4080 gantry beams. Pan supports at Y300 /630 /1180.',
        'Head: original clamp/boot solids; 146 x175 x12.7 mm removable plate and 146 x132 x12.7 mm shared receiver.',
        'ATC: selected 200 mm slide; working tool row Y1100, parked row Y1300. Endpoint pins are manual; actual vendor body/pocket geometry and automatic release remain open.',
        'Front stops: cutting contact geometry is unchanged. Complete modules park 400 mm rearward, with guides stored and head removed, before bed tilt.'
    ]:top=para(c,text,390,top,358,10,14)-9
    top-=2;top=para(c,'<b>Analysis limits</b>',390,top,358,13,17)-9
    for text in[
        'The full-brim pan rib/floor screen is 1.156 mm without composite flange credit. It uses ideal supports and excludes weld distortion and thermal effects.',
        'Member checks are not a full tool-to-work stiffness result. Actual sections, joint slip, guides, Z retention, vibration and safe handling need physical qualification.',
        'All dimensional envelopes and continuous geometry proofs have explicit scopes. No firmware limits or machine settings were applied.'
    ]:top=para(c,text,390,top,358,9,12)-8
    assert top>58,top
    c.showPage()

    header(c,'Cost and release status','Owned equipment is excluded. Unknown delivery charges and new hardware are not counted as zero.',3)
    y=506;c.setFillColor(PALE);c.rect(40,y-27,712,29,fill=1,stroke=0)
    c.setFillColor(INK);c.setFont('Helvetica-Bold',11)
    c.drawString(51,y-17,'Currently sourced required goods');c.drawRightString(739,y-17,'USD, before unknown charges')
    rows=[('Ten 1220 mm 20100 tracks - five two-profile packs','$399.95','https://www.amazon.com/dp/B0BXNWK99C'),
          ('One 48 x96 x1/2-inch HDPE sheet - supplies both layers','$260.40','https://shop.flexpipeinc.com/us_en/d-hdpew-481-2-white-hdpe-plastic-1-2'),
          ('RapidChange four-pocket ER11 Basic magazine','$400.00','https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/')]
    y-=51
    for label,amount,url in rows:
        c.setFont('Helvetica',10);c.setFillColor(BLUE);c.drawString(51,y,label)
        c.linkURL(url,(51,y-3,610,y+12),relative=0,thickness=0)
        c.setFillColor(INK);c.drawRightString(739,y,amount)
        c.setStrokeColor(colors.HexColor('#d9e2e6'));c.line(40,y-12,752,y-12);y-=31
    c.setFillColor(RED);c.setFont('Helvetica-Bold',13)
    c.drawString(51,y,'Core goods extension');c.drawRightString(739,y,'$1,060.35')
    top=para(c,'That is already $60.35 above the entire $1000 cap, before the 4080 frame, pan/slats, other custom stock, gas supports, reservoir/valve, hardware, tool setter, freight or tax. The complete delivered total remains unquoted. Required five-pack availability is not reserved.',40,y-24,712,9.5,12,RED)-12
    top=para(c,'<b>Excluded owned equipment and stock</b>',40,top,712,12,16)-6
    top=para(c,'Motion modules, extra guides, drives/controller, spindle/VFD, existing working clamp/boot/actuator, electronics enclosure, cutter/torch, compressor and CV15HS are excluded from new equipment cost. The one half-inch and one three-eighth-inch aluminum squares have exclusive stock nests. No full-bed HDPE, tracks or RapidChange ownership credit is established.',40,top,712,9.5,12)-12
    top=para(c,'<b>Gates that prevent a final release</b>',40,top,712,12,16)-7
    gates=[
        'Register the existing working boot home/moving joint, spindle nose datum, selected ATC nut/IR/pocket map and exact vendor mating patterns.',
        'Qualify received extrusion sections, slot nuts, modified members, joints, full rigidity, power-loss Z support and controlled bed handling.',
        'Verify water capacity/temperature/overflow, actual strut and valve/fittings, module wipers/bellows, controller interlocks, VFD reverse/stop and isolated plasma control.',
        'Resolve the new-parts delivered budget before ordering. Valid STEP solids and nominal clearance results do not close these requirements.'
    ]
    for i,text in enumerate(gates,1):top=para(c,f'<b>{i}.</b> {text}',40,top,712,9.5,12)-6
    assert top>62,top
    c.setFont('Helvetica',8);c.setFillColor(BLUE)
    c.drawString(40,57,'Current source, checks, stock and status: public project / variants / integrated-4080-small')
    c.linkURL('https://github.com/DeadlySIn777/plasma-router-stand/tree/codex/initial-import/variants/integrated-4080-small',(40,54,752,68),relative=0,thickness=0)
    c.save();print(str(OUT))

if __name__=='__main__':main()
