"""Build a four-page concept review from the actual Rev G CAD package.

Writes a review copy only. Publish to the stable concept PDF after all rendered
pages have been visually inspected; historical drawings are not inputs.
"""
from pathlib import Path
import hashlib
import json
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
ENG=ROOT/'output/release-review/RevG-CAD'
OUT=ROOT/'output/cad-repair-2026-09-25/pdf'
PDF=OUT/'plasma-router-stand-concept-revg-review.pdf'
W,H=landscape(A4)
INK='#17323B'; MUTED='#586C75'; TEAL='#007F83'; PALE='#EAF4F3'
LINE='#CCD9DD'; LIGHT='#F4F7F8'; AMBER='#95621C'; AMBER_BG='#FFF3DC'

for name,file in [('Segoe','segoeui.ttf'),('SegoeBold','segoeuib.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Segoe',normal='Segoe',bold='SegoeBold',italic='Segoe',boldItalic='SegoeBold')


class Brief:
    def __init__(self,manifest):
        self.manifest=manifest
        self.checks=[]
        self.page_number=0
        self.c=canvas.Canvas(str(PDF),pagesize=(W,H),pageCompression=1)
        self.c.setTitle('CNC + plasma stand | Rev G corrected working CAD')
        self.c.setAuthor('Prepared for Gluis')
        self.c.setSubject('Manual panel conversion, actual CAD geometry, measured repairs and remaining release requirements')

    def box(self,x,y,w,h,fill,stroke=None,radius=0):
        c=self.c;c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke or fill))
        if radius:c.roundRect(x,y,w,h,radius,fill=1,stroke=bool(stroke))
        else:c.rect(x,y,w,h,fill=1,stroke=bool(stroke))

    def text(self,x,y,text,size=10,bold=False,color=INK):
        self.c.setFont('SegoeBold' if bold else 'Segoe',size)
        self.c.setFillColor(HexColor(color));self.c.drawString(x,y,str(text))

    def para(self,x,top,w,text,size=10,color=INK,leading=None,bold=False):
        style=ParagraphStyle('p',fontName='SegoeBold' if bold else 'Segoe',fontSize=size,
                             leading=leading or size*1.4,textColor=HexColor(color))
        p=Paragraph(text,style);_,height=p.wrap(w,H)
        bottom=top-height
        assert bottom>=37,(self.page_number,text[:60],bottom)
        p.drawOn(self.c,x,bottom)
        self.checks.append({'page':self.page_number,'kind':'paragraph','top':top,'bottom':bottom,'width':w})
        return bottom

    def block(self,x,top,w,label,text,size=10):
        self.text(x,top,label,12,True)
        return self.para(x,top-11,w,text,size)-21

    def table(self,x,top,w,rows,ratios=(.45,.55),size=9.5):
        style=ParagraphStyle('cell',fontName='Segoe',fontSize=size,leading=size*1.3,textColor=HexColor(INK))
        bold=ParagraphStyle('label',parent=style,fontName='SegoeBold')
        cells=[[Paragraph(str(a),bold),Paragraph(str(b),style)] for a,b in rows]
        table=Table(cells,colWidths=[w*r/sum(ratios) for r in ratios])
        table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,0),(-1,-1),[HexColor(LIGHT),white]),
            ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
            ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('LINEBELOW',(0,-1),(-1,-1),.6,HexColor(LINE))]))
        _,height=table.wrap(w,H)
        assert top-height>=39,(self.page_number,'table',top-height)
        table.drawOn(self.c,x,top-height)
        self.checks.append({'page':self.page_number,'kind':'table','top':top,'bottom':top-height})
        return top-height

    def model(self,name,x,y,w,h):
        path=ENG/'previews'/name
        reader=ImageReader(str(path));iw,ih=reader.getSize()
        # Preview title/footer are repeated in the document's own typography.
        # Clip them inside the PDF; the geometry pixels are unchanged.
        crop_top=100;crop_bottom=90
        scale=min(w/iw,h/(ih-crop_top-crop_bottom))
        dw=iw*scale;dh=ih*scale
        dx=x+(w-dw)/2;dy=y+(h-(ih-crop_top-crop_bottom)*scale)/2-crop_bottom*scale
        self.c.saveState();pathclip=self.c.beginPath();pathclip.rect(x,y,w,h);self.c.clipPath(pathclip,stroke=0,fill=0)
        self.c.drawImage(reader,dx,dy,width=dw,height=dh,mask='auto')
        self.c.restoreState()

    def page(self,number,title,subtitle):
        self.page_number=number
        self.box(0,0,W,H,'#FFFFFF')
        self.text(32,H-27,'WORKSHOP / CNC + PLASMA',9,True,TEAL)
        self.c.setFont('Segoe',8.5);self.c.setFillColor(HexColor(MUTED));self.c.drawRightString(W-32,H-27,'REV G / 25 SEP 2026')
        self.text(32,H-61,title,25,True)
        self.para(32,H-72,W-64,subtitle,10,MUTED)
        self.c.setStrokeColor(HexColor(LINE));self.c.setLineWidth(.6);self.c.line(32,30,W-32,30)
        self.text(32,17,'WORKING DESIGN / DIMENSIONS IN mm / NOT RELEASED FOR ORDERING OR FABRICATION',7.3,color=MUTED)
        self.c.drawRightString(W-32,17,f'{number} / 4')

    def finish_page(self):self.c.showPage()


def numeric(value,digits=1):
    return f'{value:.{digits}f}'.rstrip('0').rstrip('.') if isinstance(value,(int,float)) else str(value)


def build(manifest):
    doc=Brief(manifest)
    bed=manifest['bed']
    checks=manifest['state_checks']
    frame=json.loads((ROOT/'output/cad-repair-2026-09-25/frame/verification.json').read_text(encoding='utf-8'))
    motion=json.loads((ROOT/'output/cad-repair-2026-09-25/motion/revg-full-machine-poses.json').read_text(encoding='utf-8'))
    panels=json.loads((ROOT/'output/cad-repair-2026-09-25/motion/revg-panel-path.json').read_text(encoding='utf-8'))
    assert motion['current_source_run_valid'] and motion['all_sampled_poses_clear']
    assert panels['all_panel_paths_proved'] and not panels['sources_changed_during_run']
    doc.page(1,'A machine built around the work.','Actual Rev G CAD: a steel chassis, a removable router bed and a fixed water pan. The design is corrected, with remaining interfaces identified.')
    doc.box(32,112,492,365,LIGHT,radius=6)
    doc.model('RevG_ROUTER.png',34,115,488,359)
    doc.text(47,98,'ROUTER BED INSTALLED',9,True,TEAL)
    doc.para(47,87,475,'The image is rendered from the exported CAD. Amber geometry represents purchased-part envelopes; appearance does not establish a verified supplier interface.',8.5,MUTED)
    x=548;y=469;w=W-x-32
    y=doc.block(x,y,w,'800 X / 1000 Y / 100 Z','Required nominal axis travel. The usable tool-and-workpiece envelope still depends on the final cutting tool, clamps and purchased motion interfaces.')
    y=doc.block(x,y,w,'A shorter path for cutting loads','The removable bed seats on dedicated supports in the steel chassis. The water pan remains a separate process component.')
    y=doc.block(x,y,w,'Parts stored in the stand','Six separate panels, four removable beams and separate spoilboards replace the earlier one-piece hoisted bed. The manual handling method is a working assumption pending your preference.')
    doc.box(x,58,w,78,AMBER_BG,radius=4)
    doc.para(x+12,124,w-24,'<b>Review the design before ordering.</b><br/>This brief replaces the previous hoisted-bed concept. It does not establish a finished machine or a revised build price.',9,AMBER)
    doc.finish_page()

    doc.page(2,'Change the bed. Keep the footprint.','Manual conversion: 52 screws / clamp assemblies removed, plus 24 loose nuts retrieved. This is a budget-oriented design assumption, with no quick-change or automatic-handling claim.')
    doc.box(32,222,378,257,LIGHT,radius=5);doc.model('RevG_BED_STORED.png',34,224,374,253)
    doc.box(430,222,380,257,LIGHT,radius=5);doc.model('RevG_BED_STORED_front.png',432,224,376,253)
    doc.text(43,207,'STORED CONFIGURATION / ISOMETRIC',9,True,TEAL)
    doc.text(442,207,'STORED CONFIGURATION / FRONT',9,True,TEAL)
    doc.para(32,190,W-64,'<b>Scope:</b> bed and router tools are stored; a verified plasma torch, floating head and breakaway are still missing. Empty the front and left racks by reinstalling the bed before opening the controls cabinet.',9.5,MUTED)
    for x,label,body in [
        (32,'01 / Boards and loose nuts','With the machine isolated and tool removed, take out 24 board screws. Store boards in order 4, 3, 2, 1, 6, 5. Retrieve all 24 loose top-slot nuts before rotating the panels.'),
        (298,'02 / Panels and front seats','Remove 16 clamp assemblies and store six panels, rear slots first. The beam-1 parking pose on beam 2 permits removal of two front seats and their four screws; parking restraint remains unresolved.'),
        (564,'03 / Beams and reinstallation','Release eight beam screws and store four beams in the specified order. Reverse to reinstall, remap the front seats and re-probe work zero. Physical restraint and hand access still require verification.')]:
        doc.block(x,138,245,label,body,9.5)
    doc.finish_page()

    doc.page(3,'Geometry that can be checked.','Dimensions below describe the current model. Nominal shape checks, supplier measurements and structural qualification are separate pieces of evidence.')
    panel_dims=' x '.join(numeric(v,3) for v in bed['panel_envelope_mm'])
    deck_dims=' x '.join(numeric(v) for v in bed['bare_deck_mm'][:2])
    masses=bed['panel_mass_kg'];beam_masses=bed['beam_mass_kg']
    rows=[['Assembled deck',deck_dims+' overall X x Y; includes panel gaps'],
          ['Removable panels',f"{bed['panels']} at {panel_dims}; panel + ties / hardware envelope"],
          ['Panel dry mass',f'{max(masses):.2f} kg each estimated; weigh finished panels'],
          ['Removable beams',f"{bed['beams']} at 924 long, 50.8 square x 3.048 wall tube; {max(beam_masses):.2f} kg estimated each"],
          ['Working surfaces',f"Bare T-slot Z{numeric(bed['workplane_z_mm'])}; finished spoilboard Z{numeric(bed['finished_spoilboard_z_mm'])}"],
          ['Separate spoilboards',f"Six pieces: {bed['rough_spoilboard_thickness_mm']} rough to {bed['finished_spoilboard_thickness_mm']} finished. Only the reachable pieces are skimmed."],
          ['Removable retention',f"{bed['panel_clamp_M6']} M6 clamps / {bed['beam_drawdown_M8']} M8 beam screws / {bed['spoilboard_M5']} M5 board screws / 4 M8 front-seat screws"],
          ['Plasma slat support','Central 810 mm remains at Z850; 35 x 22 end reliefs clear the bed supports']]
    doc.text(32,475,'BED AND MATERIAL DEFINITION',10,True,TEAL)
    bottom=doc.table(32,461,400,rows,size=9.2)
    doc.para(32,bottom-14,400,'<b>Stock count:</b> 5 two-packs = 10 bars. At three 397 mm lengths per bar, 1191 mm is assigned to finished pieces; 29 mm remains for saw kerfs and end trim. Confirm stock length and profile before cutting.',9.3,MUTED)
    x=457;w=W-x-32;y=475
    y=doc.block(x,y,w,'Drilled cabinet stringers','Two actual 6 mm bores now pass through both walls of each stringer. Their axes are local X12.7 and Y12.6 / 486.8. The screw-to-stringer collision exceptions were removed.',9.5)
    y=doc.block(x,y,w,'A defined drip shield','A two-piece welded steel roof and front lip, four cage tabs and four M5 fasteners replace the undefined bent sheet. The roof falls 1% toward the front. Its sampled withdrawal path clears the nominal enclosure.',9.5)
    gap=frame['pan_empty']['distance_at_lowest_slot_play_mm']
    y=doc.block(x,y,w,'Room below the drained-level guard',f'PAN_EMPTY has {gap:.2f} mm nominal pan-floor clearance at its lowest slot-play position. The drawing requires at least 8 mm actual clearance after welding. Its real water trip and drain delay still need wet testing.',9.5)
    y=doc.block(x,y,w,'Matching adapter machining geometry','The two non-through adapter slots now retain their vertical orientation in DXF. The drawing-to-solid comparison passes. The purchased Z-carriage mating interface remains guarded.',9.5)
    doc.finish_page()

    doc.page(4,'What is verified. What closes the design.','Use the corrected CAD to resolve the remaining interfaces and load cases. A clean geometric model alone is not a fabrication release.')
    state_rows=[['Router state',f"{checks['router']['part_count']} components; {len(checks['router']['unresolved_intersections'])} unresolved static overlaps"],
                ['Stored-bed state',f"{checks['bed_stored_layout']['part_count']} components; {len(checks['bed_stored_layout']['unresolved_intersections'])} unresolved static overlaps"],
                ['STEP readback','Both state exports reimported successfully; solid counts and total volumes checked'],
                ['Motion samples',f"{motion['completed_pose_count']} full-machine router poses clear; corners and center, without actual cutter / cable envelopes"],
                ['Large-part paths','36 panel, 25 beam and 60 spoilboard continuous segments checked, including previously stored parts'],
                ['Drip shield service','24 forward positions + 11 lowering positions checked against the frame / enclosure reserve']]
    doc.text(32,475,'EVIDENCE IN THIS REVISION',10,True,TEAL)
    bottom=doc.table(32,460,359,state_rows,ratios=(.38,.62),size=9.2)
    bottom=doc.para(32,bottom-15,359,'<b>Path clearance is not restraint.</b> Stored parts and beam 1 in its temporary parking pose have no qualified anti-slide / anti-tip retention. Small hardware, front-seat and tool transfers, fingers, operator reach, cables and actual tooling remain outside these checks.',9.3,MUTED)
    doc.para(32,bottom-15,359,'<b>Current package:</b> output/release-review/RevG-CAD<br/><b>Repair evidence:</b> output/cad-repair-2026-09-25<br/><b>Project:</b> <link href="https://github.com/DeadlySIn777/plasma-router-stand" color="#007F83">github.com/DeadlySIn777/plasma-router-stand</link>',8.6,MUTED)
    x=422;w=W-x-32;y=475
    for label,body in [
        ('Purchased motion and tools','Verify actuator/guide interfaces, Z-carriage mounting and retention, tool projection and the owned torch. The Z drawing assigns 70 mm transverse spacing to the smaller 5 mm holes; thread and along-travel pitch remain unverified.'),
        ('Rigidity and repeatability','Set a tool-to-work deflection target and cutting load cases. Qualify frame, beam, seat, fastener and foot behavior together; do not credit sand as added elastic stiffness.'),
        ('Process and service hardware','Complete the selected drain valve, fittings, hoses, refill outlet, tank service path and enclosure door/cable/thermal arrangement. Verify wet operation and electrical interlocks using the actual equipment.'),
        ('Handling, stock and cost','Confirm manual handling and design positive restraint. Twenty-four aluminum ties are required; one 12 x 12-inch plate does not supply them all. Verify owned quantity/alloy and recost the bill of materials. No new build total is asserted.')]:
        y=doc.block(x,y,w,label,body,9.5)
    doc.finish_page()
    doc.c.save()
    reader=PdfReader(str(PDF))
    assert len(reader.pages)==4
    extracted='\n'.join(p.extract_text() or '' for p in reader.pages)
    assert all(word in extracted for word in ['REV G','397','PAN_EMPTY','NOT RELEASED'])
    (OUT/'extracted-text.txt').write_text(extracted,encoding='utf-8')
    inputs=[ENG/'engineering-manifest.json',ROOT/'output/cad-repair-2026-09-25/frame/verification.json',
            ROOT/'output/cad-repair-2026-09-25/bed-architecture.md',ROOT/'output/cad-repair-2026-09-25/beam-path-check.json',
            ROOT/'output/cad-repair-2026-09-25/spoil-transfer-check.json',ROOT/'output/cad-repair-2026-09-25/motion/revg-full-machine-poses.json',
            ROOT/'output/cad-repair-2026-09-25/motion/revg-panel-path.json']
    inputs.extend(ENG/'previews'/name for name in ['RevG_ROUTER.png','RevG_BED_STORED.png','RevG_BED_STORED_front.png'])
    (OUT/'build-verification.json').write_text(json.dumps({'pdf':str(PDF),'pages':4,'layout_checks':doc.checks,
        'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'visual_review':'REQUIRED BEFORE PUBLISHING'},indent=2)+'\n',encoding='utf-8')
    print(PDF)


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ENG/'engineering-manifest.json').read_text(encoding='utf-8'))
    for state in manifest['state_checks'].values():
        assert not state['unresolved_intersections'],state
        assert state['step_readback']['passed'],state
    build(manifest)
