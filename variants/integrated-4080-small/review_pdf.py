"""Render the current review, using actual assembly previews and bound reports."""
from pathlib import Path
import hashlib,json,re,sys
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE/'manufacturing'))
from budget_model import current_budget
OUT=ROOT/'output/pdf/plasma-router-stand-integrated-4080-review.pdf'
W,H=792,612
INK=colors.HexColor('#173443');MUTED=colors.HexColor('#48616d')
BLUE=colors.HexColor('#236a89');PALE=colors.HexColor('#edf3f5')
RED=colors.HexColor('#963d35')
STYLE=ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14,textColor=INK)

def readable(text):
    text=text.replace('mm4','mm^4')
    text=re.sub(r'(?<=[a-z])(?=[0-9$])',' ',text)
    text=re.sub(r'(?<=\d)(mm|kg|N|lb)\b',r' \1',text)
    text=re.sub(r'([,:;])(?=[A-Za-z0-9$])',r'\1 ',text)
    return re.sub(r'\bI(?=\d)','I ',text)

def para(c,text,x,top,width,size=10,leading=14,color=INK):
    style=ParagraphStyle('p',parent=STYLE,fontSize=size,leading=leading,textColor=color)
    p=Paragraph(readable(text),style);_,height=p.wrap(width,1000);p.drawOn(c,x,top-height);return top-height

def header(c,title,subtitle,page):
    c.setFillColor(INK);c.rect(0,H-9,W,9,fill=1,stroke=0)
    c.setFont('Helvetica-Bold',22);c.drawString(40,565,title)
    para(c,subtitle,40,547,712,10,14,MUTED)
    c.setStrokeColor(colors.HexColor('#c8d5dc'));c.line(40,43,752,43)
    c.setFont('Helvetica',8);c.setFillColor(MUTED)
    c.drawString(40,29,'6 November 2026 revision | Review only - fabrication, CAM and operating releases remain open')
    c.drawRightString(752,29,f'{page} / 3')

def photo(c,path,x,y,w,h):
    im=ImageReader(str(path));iw,ih=im.getSize();s=min(w/iw,h/ih)
    dw,dh=iw*s,ih*s;c.drawImage(im,x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    assembly=json.loads((HERE/'output/assembly-check.json').read_text())
    assert assembly['passed']and assembly['source_consistent_during_build']
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    for n,h in assembly['source_sha256'].items():assert sha(ROOT/n)==h,n
    for mode,row in assembly['assemblies'].items():
        assert row['passed']and row.get('adaptive_volume_tolerance')==1e-8,mode
        assert sha(HERE/row['file'])==row['sha256'],mode
        assert sha(HERE/row['preview']['file'])==row['preview']['sha256'],mode
    # A valid display assembly cannot substitute for a passed transition proof.
    for name in('bed/output/bed-machine-changeover-check.json',
                'output/integration-clearance-check.json',
                'utilities/output/guide-handling-check.json'):
        report=json.loads((HERE/name).read_text())
        assert report['passed'],name
        for n,h in report['source_sha256'].items():assert sha(ROOT/n)==h,(name,n)
    budget=current_budget()
    assert budget['three_core_goods_basis_USD']=='934.83'
    c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('Integrated 4080 small table - current review')
    c.setAuthor('Plasma-router-stand project')
    header(c,'Integrated 4080 small table','Original owner head | Full HDPE / 20100 bed | Retractable ATC | 800 X / 1000 Y / 250 working Z',1)
    c.setFillColor(colors.HexColor('#fae9e5'));c.roundRect(40,502,712,23,5,fill=1,stroke=0)
    para(c,'<b>CURRENT ENGINEERING REVIEW - Supplier, control and delivered-budget gates remain.</b>',51,519,690,10,13,RED)
    for label,mode,x in(('WOOD / CARVING','WOOD',40),('PLASMA / BED UPRIGHT','PLASMA',410)):
        c.setFillColor(PALE);c.roundRect(x,143,342,345,7,fill=1,stroke=0)
        c.setFillColor(INK);c.setFont('Helvetica-Bold',12);c.drawString(x+14,467,label)
        photo(c,HERE/'output'/f'INTEGRATED_4080_SMALL_{mode}.png',x+8,183,326,273)
        caption=('Ten finished tracks, one HDPE layer, upright crossbars and removable billet head.'if mode=='WOOD'else
                 'Bed parks in the front bay; covered magazine parks in the rear bay.')
        para(c,caption,x+14,171,314,9,12)
    para(c,'Rendered from the exported solid assemblies, including the original manufacturer magazine housing. Purple tool/spindle volumes are capacity context. The original owner boot remains at an unregistered reference pose.',40,120,712,10,14)
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
    rect(75,-100,1000,112.7,colors.HexColor('#d99b86'))
    for y in(110,395,780,1140):
        c.setStrokeColor(colors.HexColor('#677e87'));c.setLineWidth(1)
        c.line(fx(85),fy(y),fx(1065),fy(y))
    for y in(300,630,1180):
        c.setStrokeColor(colors.HexColor('#9b805c'));c.setLineWidth(2)
        c.line(fx(32.15),fy(y),fx(1117.85),fy(y))
    c.setStrokeColor(BLUE);c.setLineWidth(1.8);c.setDash(5,3)
    c.rect(fx(175),fy(105.697941),800*scale,1000*scale,fill=0,stroke=1);c.setDash()
    rect(553,1230,44,311,colors.HexColor('#91a5af'))
    rect(439.4,1270,271.2,60,colors.HexColor('#c6b6d7'))
    c.setFont('Helvetica',9);c.setFillColor(MUTED)
    c.drawCentredString(fx(575),fy(1600)+12,'REAR / ATC BAY')
    c.drawCentredString(fx(575),fy(-160)-18,'FRONT / BED PARKING BAY')
    c.drawCentredString(fx(575),fy(580),'800 x 1000 tool field')
    c.saveState();c.translate(fx(-45),fy(720));c.rotate(90)
    c.drawCentredString(0,0,'1760 mm continuous headers');c.restoreState()
    top=510
    top=para(c,'<b>Defined geometry</b>',390,top,358,13,17)-10
    for text in[
        'Bed: ten finished1220 mm tracks; one1000 x1200 x12.7 mm HDPE layer. Four980 mm 4080 crossbars stand80Z x40Y at Y110/395/780/1140. Surface Z967.8.',
        'Hinge: Y-100, Z967.8. Upright track/crossbar envelope Y-100 to12.7; highest point approximately Z2247.8. Nominal deck mass49.25-53.64 kg.',
        'Frame: six posts and paired1250 mm 4080 beams; continuous1200 x112 x6.35 mm steel rail face, fitted lands and four upper ties. Actual rail pattern is transfer-fit.',
        'Head: unchanged original clamp/boot; removable billet dock and owned-stock rib. Ideal local bending0.093 mm at100 N; joint slip and torsion are unqualified.',
        'ATC: 200 mm slide; tool rows Y1100 /1300. Original manufacturer housing and pocket XY axes; slide-driven passive capture docks replace manual endpoint fasteners.',
        'Front stops: cutting contact geometry is unchanged. Complete modules park 400 mm rearward, with guides stored and head removed, before bed tilt.'
    ]:top=para(c,text,390,top,358,9.5,13)-7
    top-=2;top=para(c,'<b>Analysis limits</b>',390,top,358,13,17)-9
    for text in[
        'The100 N bed component screen is0.156 mm versus0.296 mm previously, using assumed I536000 mm4; at50% retained I it is0.203 mm. No HDPE composite action or full-machine stiffness is credited.',
        'Pan/slats/drain are26 mm lower; slat top Z852. The ideal full-brim pan screen is1.156 mm. Actual sections, drilled ligaments, welds, joint slip, thermal effects and safe handling remain unqualified.',
        'Each of two gas springs is a150 lb /667 N candidate: compressed eye length at most445 mm, expanded at least700 mm. Received force curves, Z retention and interlocks require qualification.'
    ]:top=para(c,text,390,top,358,9,12)-8
    assert top>58,top
    c.showPage()

    header(c,'Cost and release status','5 November 2026 source observations. Owned equipment excluded; shared tracks counted once; unknown charges remain unknown.',3)
    y=506;c.setFillColor(PALE);c.rect(40,y-27,712,29,fill=1,stroke=0)
    c.setFillColor(INK);c.setFont('Helvetica-Bold',11)
    c.drawString(51,y-17,'Currently sourced required goods');c.drawRightString(739,y-17,'USD, before unknown charges')
    rows=[('Two actual four-profile1500 mm packs; cut eight to1220','$259.98','https://www.amazon.com/dp/B0DY7JYQCJ'),
          ('One actual two-profile1220 mm pack; retain both lengths','$82.99','https://www.amazon.com/dp/B0DY7GCFRV'),
          ('US Plastic42707: one48 x48 x1/2-inch HDPE sheet','$191.86','https://www.usplastic.com/catalog/item.aspx?itemid=127310'),
          ('RapidChange four-pocket ER11 Basic magazine','$400.00','https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/')]
    y-=51
    for label,amount,url in rows:
        c.setFont('Helvetica',10);c.setFillColor(BLUE);c.drawString(51,y,readable(label))
        c.linkURL(url,(51,y-3,610,y+12),relative=0,thickness=0)
        c.setFillColor(INK);c.drawRightString(739,y,amount)
        c.setStrokeColor(colors.HexColor('#d9e2e6'));c.line(40,y-10,752,y-10);y-=28
    c.setFillColor(RED);c.setFont('Helvetica-Bold',13)
    c.drawString(51,y,'Core goods');c.drawRightString(739,y,'$934.83')
    top=para(c,'<b>Core plus already-staged hardware: $1046.91.</b> Adding the required$50 tool setter gives$1096.91, before any4080 frame, pan, remaining parts, freight or tax. The$1000 delivered cap fails. Core goods alone save$90.87 against the prior selected-source case.',40,y-22,712,10,13,RED)-14
    left=right=top
    left=para(c,'<b>Partial carts and delivery</b>',40,left,340,12,16)-6
    left=para(c,'16 variants /33 packs /538 pieces: $455.05 goods, including the same$342.97 tracks. AliExpress:13 variants,$78.32. Amazon:3 variants,$376.73. No order placed; remaining BOM items are unstaged.',40,left,340,9.5,12)-10
    left=para(c,'Long1500 mm stock: <b>December9-24</b> final cart estimate, superseding November. Selected Amazon lines show free Prime to30510. Ali exact Alto address is unconfirmed. HDPE/ATC freight and all tax are unknown.',40,left,340,9.5,12)-12
    left=para(c,'<b>Owned cost exclusions</b>',40,left,340,12,16)-6
    left=para(c,'Owned motion, guides, drives/controller, spindle/VFD, working head, enclosure, cutter/torch, compressor and selected slide are excluded. Two aluminum squares have14 exclusive blank allocations. Bed materials and ATC have no ownership credit.',40,left,340,9.5,12)-6
    right=para(c,'<b>Physical and operating gates</b>',410,right,342,12,16)-6
    gates=[
        'Register boot home, spindle nose and actual ER11 nut/socket engagement. Confirm received kit revision, state sensing, rail and slide patterns.',
        'Qualify actual extrusion/drilled sections, slot nuts, welds, joint slip, full rigidity, power-loss Z retention and controlled bed handling.',
        'Verify receiver water/temperature/overflow, two150 lb-each struts, valve/fittings, module shielding, VFD reverse/stop, isolated plasma control and interlocks.',
        'Finish the delivered quotation and remaining selections. Valid exported solids and nominal clearance do not establish fabrication or operating release.'
    ]
    for i,text in enumerate(gates,1):right=para(c,f'<b>{i}.</b> {text}',410,right,342,9.5,12)-9
    assert min(left,right)>68,(left,right)
    c.setFont('Helvetica',8);c.setFillColor(BLUE)
    c.drawString(40,57,'Current source, checks, stock and status: public project / variants / integrated-4080-small')
    c.linkURL('https://github.com/DeadlySIn777/plasma-router-stand/tree/codex/initial-import/variants/integrated-4080-small',(40,54,752,68),relative=0,thickness=0)
    c.save();print(str(OUT))

if __name__=='__main__':main()
