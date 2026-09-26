"""Render the Rev I concept review from current CAD and verification evidence."""
from pathlib import Path
import hashlib
import json
from reportlab.lib.colors import HexColor
from pypdf import PdfReader
import build_concept_revg as layout

ROOT=Path(__file__).resolve().parent
ENG=ROOT/'output/release-review/RevI-CAD'
OUT=ROOT/'output/design-finish-2026-09-26/pdf'
PDF=OUT/'plasma-router-stand-concept-revi-review.pdf'
layout.ENG=ENG
layout.PDF=PDF
W,H=layout.W,layout.H


class Brief(layout.Brief):
    def __init__(self,manifest):
        super().__init__(manifest)
        self.c.setTitle('CNC + plasma stand | Rev I design completion work')
        self.c.setSubject('Actual CAD, in-frame storage, water servicing and outstanding physical interfaces')

    def page(self,number,title,subtitle):
        self.page_number=number
        self.box(0,0,W,H,'#FFFFFF')
        self.text(32,H-27,'WORKSHOP / CNC + PLASMA',9,True,layout.TEAL)
        self.c.setFont('Segoe',8.5)
        self.c.setFillColor(HexColor(layout.MUTED))
        self.c.drawRightString(W-32,H-27,'REV I / 26 SEP 2026')
        self.text(32,H-61,title,25,True)
        self.para(32,H-72,W-64,subtitle,10,layout.MUTED)
        self.c.setStrokeColor(HexColor(layout.LINE))
        self.c.setLineWidth(.6)
        self.c.line(32,30,W-32,30)
        self.text(32,17,'WORKING DESIGN / DIMENSIONS IN mm / NOT A FABRICATION OR OPERATION RELEASE',7.3,color=layout.MUTED)
        self.c.drawRightString(W-32,17,f'{number} / 4')


def build(manifest):
    doc=Brief(manifest)
    doc.page(1,'Refining the machine you will build.',
             'Actual Rev I CAD. The Y modules are ordered; the X and Z purchase is planned for Monday. The chassis remains based on 2-inch square tube.')
    doc.box(32,112,492,365,layout.LIGHT,radius=6)
    doc.model('RevI_ROUTER.png',34,115,488,359)
    doc.text(47,98,'ROUTER BED INSTALLED',9,True,layout.TEAL)
    doc.para(47,87,475,'Rendered from exported geometry. Amber parts represent purchased-component envelopes; several mating dimensions still require measurement.',8.5,layout.MUTED)
    x=548;w=W-x-32;y=469
    for label,body in [
        ('800 X / 1000 Y / 100 Z','Nominal travel. Both selected HMS40 X/Y listings specify 10 mm lead: 10 mm movement per screw revolution. This is not screw diameter.'),
        ('2 x 2-inch steel chassis','Current model wall: 0.120 inch (3.048 mm). Scrap lengths, wall and condition are still unknown. Sand can add stationary mass; it does not supply structural stiffness.'),
        ('What this revision changes','Stronger storage retainers, a guided float/breakaway head, supported plumbing, service access and actual control circuits replace several unresolved details.')]:
        y=doc.block(x,y,w,label,body,9.8)
    doc.box(x,57,w,71,layout.AMBER_BG,radius=4)
    doc.para(x+12,117,w-24,'<b>Design review, not finished machinery.</b><br/>The head mechanism is modeled. Actual torch and module interfaces, whole-machine rigidity and electrical qualification remain open.',9,layout.AMBER)
    doc.finish_page()

    doc.page(2,'Conversion stays inside the frame.',
             'Manual panel-and-beam conversion preserves the floor footprint. It retains 52 primary release fasteners plus restraint and tool-exchange steps.')
    doc.box(32,222,378,257,layout.LIGHT,radius=5)
    doc.model('RevI_BED_STORED.png',34,224,374,253)
    doc.box(430,222,380,257,layout.LIGHT,radius=5)
    doc.model('RevI_HEAD_DETAIL.png',432,224,376,253)
    doc.text(43,207,'STORED BED / ISOMETRIC',9,True,layout.TEAL)
    doc.text(442,207,'FLOAT / BREAKAWAY DETAIL / UNBORED INSERT',9,True,layout.TEAL)
    doc.para(32,190,W-64,'<b>Scope:</b> the stored view contains the bed and removed router tools. The head hardware view has no invented torch. Clear the front storage racks before servicing the controls cabinet.',9.5,layout.MUTED)
    for x,label,body in [
        (32,'01 / Captive hardware','Twelve nut strips retain the spoilboard hardware. Thin slot lips cannot accept ordinary torque-table preload: the actual extrusion needs the specified coupon test before release.'),
        (298,'02 / Defined storage','The two storage rods grow from 10 to 14 mm with 40 mm receiver engagement, thicker seats and a revised clearance path. The 100 N single-rod bump screen now has a 2.25 yield reserve.'),
        (564,'03 / Supported tool exchange','One rear panel stays clamped as a work surface. Park the router through the open front bay, then split and transfer the head. Restore the front beam before storing the last panel. Follow the detailed sequence.')]:
        doc.block(x,138,245,label,body,9.5)
    doc.finish_page()

    doc.page(3,'Dimensions, materials and interfaces.',
             'The steel stock lengths remain unchanged. Service openings and fabricated hardware are modeled; unknown supplier interfaces remain explicitly guarded.')
    rows=[
        ('Bare bed','1003 x 1211 overall; larger than nominal cutting travel'),
        ('Six removable panels','500 x 397 each; separate reachable spoilboards'),
        ('Extrusion stock','10 bars at 1220 = five two-packs; 3 x 397 per bar'),
        ('2 x 2 tube blanks','30 blanks / 29,472 mm / 96.69 ft net'),
        ('Tube lengths and quantities','4 x 1450; 7 x 1048.4; 3 x 1016.4; 6 x 949.2; 4 x 924; 6 x 648.8'),
        ('Nominal wall','3.048 mm; do not silently substitute thinner scrap'),
        ('Water storage','Vented reservoir; gravity drain and electric refill'),
        ('Refill discharge','Air gap above the pan; verify at least 25 mm as built')]
    doc.text(32,475,'BED, STOCK AND WATER',10,True,layout.TEAL)
    bottom=doc.table(32,461,388,rows,ratios=(.38,.62),size=9.2)
    doc.para(32,bottom-14,388,'Net tube length excludes saw loss and other profiles, plate and sheet. Five full 20-ft lengths have a documented nest; random scrap must be nested from its actual usable lengths. No new material price is asserted.',9.2,layout.MUTED)
    x=447;w=W-x-32;y=475
    for label,body in [
        ('Supported drain and basket service','A reducer, valve allocation and removable flanged tail replace generic blocks. The tail parks internally, allowing the basket to lift. Exact threaded make-up remains a receipt fit.'),
        ('Pressure and suction paths','Supported Parker hose routes use 80 mm bends and a separate strainer carrier. Enlarged hose sweeps check 2 mm radial allowance. Pump orientation and tray bores now match the routing.'),
        ('Rigidity has a stated target','Known bed members account for about 0.135 mm at 100 N against a proposed 0.20 mm tool-to-work target. Actual motion, joint and tool compliance cannot be assigned zero.'),
        ('One control baseline','Kraken V1.1 retains onboard drivers. Terminal wiring, timers, run isolation and restart prevention are defined. The C41S speed converter uses a 200 Hz commissioning setting.')]:
        y=doc.block(x,y,w,label,body,9.5)
    doc.finish_page()

    doc.page(4,'Evidence and the remaining work.',
             'The checks cover explicit geometry, routes and circuit behavior. Physical supplier fit, cutting rigidity and control commissioning remain separate release conditions.')
    checks=manifest['state_checks']
    rows=[]
    for key,label in [('RevI_ROUTER','Router state'),('RevI_BED_STORED','Stored state'),('RevI_PLASMA_HARDWARE','Head hardware state')]:
        s=checks[key]
        rows.append((label,f"{s['part_count']} components; {len(s['unresolved_intersections'])} unresolved nominal overlaps"))
    rows += [('STEP readback','All three assemblies reimported; matching solid counts and volumes'),
             ('Source identity','Build manifest records exact source hashes and no changes during generation'),
             ('Check scope','18 router/head poses, named handling/service paths and 450 bounded circuit checks; see the linked evidence'),
             ('Limits','Member/joint screens are conditional; full rigidity, physical interfaces and electrical operation are not qualified')]
    doc.text(32,475,'CHECKED ARTIFACTS',10,True,layout.TEAL)
    bottom=doc.table(32,460,359,rows,ratios=(.35,.65),size=9.4)
    bottom=doc.para(32,bottom-17,359,'<b>Current package:</b> output/release-review/RevI-CAD<br/><b>Completion evidence:</b> output/design-finish-2026-09-26<br/><b>Rebuild:</b> build_revi.py in the legacy-named source directory.',9.2,layout.MUTED)
    doc.para(32,bottom-16,359,'<link href="https://github.com/DeadlySIn777/plasma-router-stand" color="#007F83">Public project: github.com/DeadlySIn777/plasma-router-stand</link>',9,layout.MUTED)
    x=422;w=W-x-32;y=475
    for label,body in [
        ('Y arrival and X/Z order','Measure base slots/nuts, carriage hole pattern, height and stroke datums. The Z listing alone does not resolve its output mounting or prove the optional brake motor will fit.'),
        ('Actual plasma assembly','The mechanism now has defined guides, stops, locators, magnets and switch cams. VIV ARC CUT-50 version, torch bore, start interface, lead routing and force/stop tests remain required.'),
        ('Rigid structure with the actual stock','Confirm remaining scrap wall and usable lengths. Qualify the complete frame, bed, gantry, mounts, joints and feet against explicit loads and a tool-to-work deflection target.'),
        ('Operation and procurement','Complete physical panel layout, stop/power/brake integration, measured hose ends and live interlock tests. Revised quantities supersede historical budgets; no current delivered total is asserted.')]:
        y=doc.block(x,y,w,label,body,9.5)
    doc.finish_page()
    doc.c.save()
    reader=PdfReader(str(PDF))
    assert len(reader.pages)==4
    text='\n'.join(page.extract_text() or '' for page in reader.pages)
    assert all(s in text for s in ['REV I','397','10 mm','96.69','NOT A FABRICATION'])
    (OUT/'extracted-text.txt').write_text(text,encoding='utf-8')
    inputs=[Path(__file__).resolve(),ROOT/'build_concept_revg.py',ENG/'engineering-manifest.json']+[ENG/'previews'/p for p in (
        'RevI_ROUTER.png','RevI_BED_STORED.png','RevI_PLASMA_HARDWARE.png','RevI_HEAD_DETAIL.png')]
    (OUT/'build-verification.json').write_text(json.dumps({
        'pdf':str(PDF),'pages':4,'layout_checks':doc.checks,
        'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),
        'visual_review':'REQUIRED BEFORE PUBLISHING'},indent=2)+'\n',encoding='utf-8')
    print(PDF)


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ENG/'engineering-manifest.json').read_text(encoding='utf-8'))
    assert manifest['integrated_geometry_pass']
    build(manifest)
