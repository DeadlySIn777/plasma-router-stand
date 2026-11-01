"""Four-page XR2 review built from current CAD and source-bound evidence."""
from pathlib import Path
import json,textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
import params as P

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REVIEW=HERE/'review'
OUT=ROOT/'output'/'pdf'/f'plasma-router-stand-{P.REVISION}-review.pdf'
FONT='XRBody';BOLD='XRBold'
pdfmetrics.registerFont(TTFont(FONT,'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont(BOLD,'C:/Windows/Fonts/segoeuib.ttf'))
W,H=landscape(A4);INK=colors.HexColor('#16343f');MUT=colors.HexColor('#4c6570')
BG=colors.HexColor('#f3f6f7');TEAL=colors.HexColor('#176469')

def run():
    load=lambda n:json.loads((REVIEW/n).read_text(encoding='utf-8'))
    build=load('build-check.json');water=load('water-check.json');bed=load('bed-screen.json')
    transfer=load('transfer-check.json');package=load('package-check.json')
    service=load('service-check.json');details=load('detail-views.json')
    atc_case=load('atc-check.json')['selected_Z_clearance_case']
    atc_stiffness=load('atc-stiffness.json')
    custom=load('custom-parts-check.json');bm=load('bed-manufacturing-check.json')
    profiles=load('profile-nesting.json');owned=load('owned-stock-check.json')
    atc=details['ATC_metadata']
    OUT.parent.mkdir(exist_ok=True,parents=True)
    c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle(P.REVISION+' - 4080 wood / plasma / ATC design review')
    c.setAuthor('Plasma-router-stand project')
    def text(x,y,s,size=11,bold=False,color=INK):
        c.setFillColor(color);c.setFont(BOLD if bold else FONT,size);c.drawString(x,y,s)
    def lines(x,y,s,width=94,size=10.5,leading=16):
        for line in textwrap.wrap(s,width=width):text(x,y,line,size);y-=leading
        return y
    def page(n,title,subtitle):
        c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0)
        text(32,H-35,P.REVISION+'  /  DESIGN AND VERIFICATION',12,True,TEAL)
        text(32,H-69,title,24,True)
        text(33,H-91,subtitle,10,False,MUT)
        c.setStrokeColor(colors.HexColor('#cedadd'));c.line(32,39,W-32,39)
        text(32,23,'01 November 2026  |  Millimetres unless stated  |  Physical release gates remain',8,False,MUT)
        text(W-60,23,f'{n} / 4',8,False,MUT)

    page(1,'4080 table. Independent beds. Retractable ATC.',
         f'Current small machine: {P.X_TRAVEL:,.0f} X / {P.Y_TRAVEL:,.0f} Y / {P.Z_TRAVEL:,.0f} Z nominal travel. New Z hardware is required.')
    c.drawImage(str(REVIEW/'overview.png'),27,82,width=W-54,height=414,preserveAspectRatio=True,anchor='c',mask='auto')
    text(33,57,'Actual generated CAD. Owned electronics enclosure stays excluded; the red box is the water receiver.',9.5,True)
    c.showPage()

    page(2,'Structure, workholding and water',
         'Pan loads and router loads have separate bearing paths. Component calculations remain conditional.')
    y=H-127
    count=sum(len(s['parts']) for s in owned['sheets'])
    rows=[('Frame',f"{profiles['finished_mm']/1000:.4f} m finished 4080; {profiles['cut_count']} cuts"),
          ('Supports','Six posts; rear bases; eight main feet'),
          ('Dry carriers','Four 932 x 257 x 70.8'),
          ('Wear field','770 x 960 enclosing outline; keep-outs apply'),
          ('Box construction','12.7 skins / 39.05 core / 6.35 wear'),
          ('Hot pan','894 x 1096 outside; 1.9 nominal plain steel'),
          ('Slats','Eight 880 x 40 x 1.9; center-keyed / free ends'),
          ('Owned aluminum',f'Two 304.8-square blanks; {count} nested blanks')]
    for a,b in rows:
        text(34,y,a,10.5,True);y=lines(34,y-17,b,width=49,size=10,leading=14)-12
    right=435;yy=H-127
    text(right,yy,'WATER VOLUMES',11,True,TEAL);yy-=26
    v=water['liquid_volumes_L_after_comb_slat_displacement']
    for label,key in [('Operating level','operating'),('Overflow starts','overflow_invert'),
                      ('Brim','brim'),('Gravity-drain residue','drained_residual')]:
        text(right,yy,label,10);text(W-106,yy,f'{v[key]:.2f} L',10,True);yy-=21
    yy=lines(right,yy-3,'Require 65 L measured usable receiver capacity. The nominal 20-gallon storage label does not verify its liquid load, useful volume or temperature suitability.',width=55,size=10,leading=15)-17
    text(right,yy,'100 N VERTICAL SENSITIVITY',11,True,TEAL);yy-=22
    a,b=bed['combined_vertical_service_sensitivities']
    yy=lines(right,yy,f"Selected material case: {a['known_ideal_component_subtotal_mm']:.3f} mm bed + ledger + upper-beam subtotal against a 0.30 mm framework/bed target. Weaker plywood case: {b['known_ideal_component_subtotal_mm']:.3f} mm, exceeding the target before omitted joints.",width=55,size=10,leading=15)-10
    yy=lines(right,yy,'Half-lap integration is a nominal composite-beam sensitivity. Local notch/glue transfer, joints and actual tool-loop compliance are unqualified; this is not assembled-frame FEA.',width=55,size=10,leading=15)
    assert yy>60,yy
    text(34,65,'Section properties, plywood direction, adhesive quality and actual joint preload are conditions of the estimates.',9.5,True)
    c.showPage()

    page(3,'Service access and manufacturable parts',
         'Routine cleaning stays in place. Rare receiver replacement has a separate reversible disassembly sequence.')
    c.drawImage(str(REVIEW/'receiver-service.png'),32,203,width=382,height=282,preserveAspectRatio=True,anchor='c',mask='auto')
    text(35,185,'OPEN / LOCKED CLEAN-OUT HATCH',11,True,TEAL)
    y=lines(35,165,'Conservative reservoir envelope and modeled service hardware. Surrounding machine remains in the collision check. Metal cross-angles and rim feet support the hatch independently of the cut plastic lid.',width=54,size=10,leading=15)
    gap=700-details['receiver_hatch_open_max_z_mm']
    y=lines(35,y-8,f"Open assembly incl. locks Z{details['receiver_hatch_open_max_z_mm']:.1f}; roof Z700: {gap:.1f} mm allowance before support/thermal effects.",width=54,size=10,leading=15)
    right=440;yy=H-127
    text(right,yy,'CONVERSION AND MAINTENANCE',11,True,TEAL);yy-=23
    for s in [
        f"{len(transfer['segments'])} complete cassette-transfer segment enclosures are checked inside the plan.",
        'Remove the complete installed tool module, cassette clamps and plasma-only ledger armors; retain Z and park the ATC before conversion.',
        'A 450 mm cleaning brush reaches the receiver floor through the framed hatch. Two index pins hold the cover open.',
        'Rare tank replacement removes the bolt-on ATC module and specified guards/ledgers; HGR motion rails stay installed. Temporary supports and two-person handling require physical qualification.']:
        yy=lines(right,yy,s,width=54,size=10,leading=15)-9
    text(right,yy,'FABRICATION FILES',11,True,TEAL);yy-=22
    yy=lines(right,yy,f"{custom['custom_step_count']} custom frame/motion STEP files with read-back checks; {custom['plate_section_reference_count']} labeled plate cross-section DXFs; {len(bm['flat_parts'])} bed/steel profile DXFs. Shield and ATC schedules add their own files.",width=54,size=10,leading=15)-10
    yy=lines(right,yy,'Reference plate sections do not replace counterbore, countersink, tap, edge-drilling or bend instructions. No production G-code is supplied.',width=54,size=10,leading=15)
    assert min(y,yy)>52,(y,yy)
    c.showPage()

    page(4,'Full-bed ATC and the 200 mm Z redesign',
         'Nominal spindle reference, not a measured nut plane. Magazine dimensions are an acceptance specification.')
    c.drawImage(str(REVIEW/'atc-deployed.png'),30,248,width=384,height=233,preserveAspectRatio=True,anchor='c',mask='auto')
    yy=232
    text(35,yy,'ATC MECHANISM / DEPLOYED',11,True,TEAL);yy-=22
    facts=[f"{atc['stroke_mm']:.0f} mm carrier stroke; {atc['guide_length_mm']:.0f} mm guides.",
           f"Magazine base Z{atc['magazine_base_Z_mm']:.2f}; stock + clamps <= {atc['stock_plus_clamp_height_mm']:.0f}.",
           f"Retained projection below base <= {atc['max_tool_projection_below_magazine_base_mm']:.2f}.",
           f"50 mm tool projection: flyover {atc_case['loaded_P50_overflight_gap_mm']:.2f}; minimum 5.",
           f"Worst pocket beam: {atc_stiffness['worst_pocket_beam_deflection_mm']:.3f} mm, excluding joints."]
    for s in facts:yy=lines(35,yy,s,width=54,size=10,leading=15)-7
    right=440;y=H-126
    passed=package['digital_review_pass']
    text(right,y,'DIGITAL REVIEW: '+('PASS WITHIN REPORT SCOPES' if passed else 'OPEN FINDINGS'),10.5,True,TEAL);y-=25
    gates=[
        'Match the selected ZXHT80-200 mounting/output, shaft/coupler and power-off retention interfaces. The brake-motor provision is conditional on actual fit and dynamic testing.',
        'Verify the real magazine envelope, pocket/nut plane, bolt pattern, retained tools, spindle reverse/control and loaded docking repeatability. No successful M6 cycle is asserted.',
        'Confirm the actual extrusion, nuts, fasteners, guide alignment and screw lead. Measure assembled framework/bed and complete spindle-to-work compliance separately.',
        'Cold-test drain/overflow and receiver capacity, then qualify guard/storage temperatures. Trial conversion and rare service with final hoses, tooling and measured masses.']
    for s in gates:y=lines(right,y,s,width=54,size=10,leading=15)-10
    y=lines(right,y,'The measurement worksheet separates these real interfaces and tests from modeled geometry. This revision does not qualify steel milling.',width=54,size=10,leading=15)
    assert min(yy,y)>77,(yy,y)
    text(35,65,'USD 1,000 remains the complete-build constraint. Replacement Z and ATC hardware are not assumed owned.',9.5,True)
    text(35,49,'No new pricing or cart changes. Sources: current CAD/check reports and preserved primary supplier drawings.',8.5,False,MUT)
    text(650,49,'RapidChange setup FAQ',8.5,False,TEAL)
    c.linkURL('https://rapidchangeatc.com/faq/',(648,46,810,59),relative=0,thickness=0)
    c.save()
    pdf=PdfReader(str(OUT));assert len(pdf.pages)==4
    assert all((p.extract_text() or '').strip() for p in pdf.pages)
    print(OUT)

if __name__=='__main__':run()
