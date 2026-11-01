"""Three-page XR1 review from the current CAD and audit outputs; no prices."""
from pathlib import Path
import json,textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REVIEW=HERE/'review'
OUT=ROOT/'output'/'pdf'/'plasma-router-stand-XR1-review.pdf'
FONT='XRBody';BOLD='XRBold'
pdfmetrics.registerFont(TTFont(FONT,'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont(BOLD,'C:/Windows/Fonts/segoeuib.ttf'))
W,H=landscape(A4);INK=colors.HexColor('#16343f');MUT=colors.HexColor('#4c6570')
BG=colors.HexColor('#f3f6f7');TEAL=colors.HexColor('#176469')

def run():
    load=lambda n:json.loads((REVIEW/n).read_text(encoding='utf-8'))
    build=load('build-check.json');water=load('water-check.json');bed=load('bed-screen.json')
    transfer=load('transfer-check.json');package=load('package-check.json')
    OUT.parent.mkdir(exist_ok=True,parents=True)
    c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('XR1 - 4080 wood and plasma table design review')
    c.setAuthor('Plasma-router-stand project')
    def text(x,y,s,size=11,bold=False,color=INK):
        c.setFillColor(color);c.setFont(BOLD if bold else FONT,size);c.drawString(x,y,s)
    def lines(x,y,s,width=94,size=10.5,leading=16):
        for line in textwrap.wrap(s,width=width):text(x,y,line,size);y-=leading
        return y
    def page(n,title,subtitle):
        c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0)
        text(32,H-35,'XR1  /  DESIGN REVIEW',12,True,TEAL)
        text(32,H-69,title,25,True)
        text(33,H-91,subtitle,10.5,False,MUT)
        c.setStrokeColor(colors.HexColor('#cedadd'));c.line(32,39,W-32,39)
        text(32,23,'01 November 2026  |  Millimetres unless stated  |  Engineering development',8,False,MUT)
        text(W-60,23,f'{n} / 3',8,False,MUT)
    page(1,'4080 frame. Removable dry bed. Steel plasma pan.','Small machine: 800 X / 1,000 Y / 100 Z nominal travel. Selective billet mounts retained.')
    c.drawImage(str(REVIEW/'overview.png'),27,71,width=W-54,height=430,preserveAspectRatio=True,anchor='c',mask='auto')
    text(33,51,'Current design replaces the earlier cart and frame proposals. No new pricing or shopping.',9.5,True)
    c.showPage()
    page(2,'Geometry and conditional structural targets','The pan supports water and steel stock. Separate ledgers support woodworking loads.')
    left,right=34,432;y=H-126
    rows=[('Frame','12.3574 m finished 4080; 19 cuts'),('Supports','Six posts; short rear bases; eight main feet'),
          ('Dry carriers','Four 932 x 257 x 70.8 cassettes'),('Wear field','770 x 960 enclosing field; track/seam keep-outs'),
          ('Construction','12.7 ply skins; 39.05 core; 6.35 MDF wear'),('Hot pan','894 x 1096 outside; 1.9 nominal plain steel'),
          ('Slats','Eight 880 x 40 x 1.9; replaceable'),('Owned stock','Two 304.8-square Al blanks; 75 nested blanks')]
    for a,b in rows:
        text(left,y,a,10.5,True);y=lines(left,y-17,b,width=48,size=10,leading=14)-12
    text(right,H-126,'WATER VOLUMES',11,True,TEAL)
    v=water['liquid_volumes_L_after_comb_slat_displacement'];yy=H-152
    for label,key in [('Operating level','operating'),('Overflow begins','overflow_invert'),('Full to brim','brim'),('Estimated gravity-drain residue','drained_residual')]:
        text(right,yy,label,10);text(W-108,yy,f'{v[key]:.2f} L',10,True);yy-=22
    yy=lines(right,yy-4,'Selected red 20-gallon tote: allow 712 x 470 x 389 externally. Require 65 L measured usable below the chosen maximum fill mark. Actual liquid load and temperature rating remain unverified.',width=56,size=10,leading=15)-19
    text(right,yy,'100 N VERTICAL SCREEN',11,True,TEAL);yy-=22
    yy=lines(right,yy,'Selected plywood case: approximately 0.230 mm ideal bed + ledger + upper-beam subtotal. The framework/bed target is 0.30 mm, leaving about 0.070 mm for omitted joint/contact and other compliance.',width=56,size=10,leading=15)-12
    yy=lines(right,yy,'Weaker plywood sensitivity is about 0.311 mm and exceeds that target. This is a component calculation, not assembled-frame FEA or demonstrated tool-to-work accuracy.',width=56,size=10,leading=15)
    text(34,65,'Extrusion section, grain direction, glue quality and joint preload are conditions of these results.',10,True)
    c.showPage()
    page(3,'Audit evidence and release gates','A successful CAD check covers its stated scope; it does not qualify the complete machine.')
    good=package['digital_review_pass'];status='DIGITAL REVIEW PASSED WITHIN STATED SCOPES' if good else 'OPEN DIGITAL FINDINGS REMAIN'
    c.setFillColor(colors.HexColor('#d9eae8') if good else colors.HexColor('#f1dddd'));c.roundRect(33,H-140,W-66,31,6,fill=1,stroke=0)
    text(45,H-129,status,12,True,TEAL if good else INK)
    y=H-171
    evidence=[f"STEP round trips: frame {build['assemblies']['FRAME']['solids']} solids; wood {build['assemblies']['WOOD']['solids']}; plasma {build['assemblies']['PLASMA']['solids']}.",
       'Display-pose external intersections and frame/bed self checks are recorded separately.',
       'XYZ external travel uses full translation bounds and exact ledger-envelope proofs; internal relative motion is sampled.',
       f"Bed conversion checks {len(transfer.get('segments',[]))} complete-path segment enclosures within the machine plan.",
       'Owned-aluminum and profile-stock nests include cut gaps; deep billet gantry brackets and clevises are not assumed owned.']
    for s in evidence:y=lines(35,y,s,width=117,size=10,leading=15)-9
    text(35,y-2,'REQUIRED BEFORE FABRICATION / CAM RELEASE',11,True,TEAL);y-=27
    holds=['Verify delivered module mounts, guide geometry, lead, Z retention, actual tool/torch projection and the cutter interface.',
           'Finish mounted heat shields, reservoir hatch/removal access and flat-pattern/half-lap machining details before manufacturing.',
           'Qualify extrusion, fasteners, assembled stiffness and stability; cold-test water flow/capacity and thermally test protected storage.',
           'Integrate the requested retractable ATC using the actual kit and Z stack. It is not installed or qualified in these assemblies.']
    for s in holds:y=lines(35,y,s,width=117,size=10,leading=15)-8
    text(35,65,'USD 1,000 remains the complete-table budget constraint. It is not a verified delivered quote.',10,True)
    c.linkURL('https://github.com/DeadlySIn777/plasma-router-stand',(32,19,500,36),relative=0,thickness=0)
    c.save()
    proof=PdfReader(str(OUT));assert len(proof.pages)==3
    assert 'OPEN DIGITAL' not in '\n'.join(p.extract_text() or '' for p in proof.pages) if good else True
    print(OUT)

if __name__=='__main__':run()
