"""Build the current Rev F design brief from reviewed CAD and engineering records."""
from pathlib import Path
import json, hashlib
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
ENG=ROOT/'output/release-review/RevE-ENGINEERING'
COST=ROOT/'outputs/reve-30510/actual-cost'
OUT=ROOT/'output/pdf'
# Historical Rev F brief. The current plasma-router-stand-concept.pdf is the Rev G
# review copy from build_concept_revg.py; never overwrite it from here.
PDF=OUT/'plasma-router-stand-concept-revf-historical.pdf'
OWN=json.loads((COST/'OWNED-ALUMINUM-INVENTORY.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('Segoe','C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('SegoeBold','C:/Windows/Fonts/segoeuib.ttf'))
pdfmetrics.registerFontFamily('Segoe',normal='Segoe',bold='SegoeBold',italic='Segoe',boldItalic='SegoeBold')
W,H=landscape(A3)
INK='#193640'; MUTED='#58717A'; TEAL='#008B89'; PALE='#E8F2F1'; LINE='#CBD9DD'; AMBER='#A36513'; LIGHT='#F5F8F9'
C=canvas.Canvas(str(PDF),pagesize=(W,H))
C.setTitle('CNC + plasma stand - Rev F one-piece hoisted bed, design and control architecture')
C.setAuthor('Prepared for Gluis')
SWAP=json.loads((ENG/'swap-path-checks.json').read_text(encoding='utf-8'))
ROUTERV=json.loads((ENG/'RevE_ROUTER-validation.json').read_text(encoding='utf-8'))
MANIFEST=json.loads((ENG/'engineering-manifest.json').read_text(encoding='utf-8'))
MODMASS=MANIFEST['bed']['module_mass_estimate_kg']
checks=[]
def color(v):return HexColor(v)
def txt(x,y,t,size=11,bold=False,fill=INK):
    C.setFont('SegoeBold' if bold else 'Segoe',size);C.setFillColor(color(fill));C.drawString(x,y,str(t))
def right(x,y,t,size=10,fill=MUTED):
    C.setFont('Segoe',size);C.setFillColor(color(fill));C.drawRightString(x,y,str(t))
def line(x1,y1,x2,y2,fill=LINE,width=.7):
    C.setStrokeColor(color(fill));C.setLineWidth(width);C.line(x1,y1,x2,y2)
def rect(x,y,w,h,fill=LIGHT,stroke=None):
    C.setFillColor(color(fill));C.setStrokeColor(color(stroke or fill));C.rect(x,y,w,h,fill=1,stroke=bool(stroke))
def para(x,top,w,t,size=11,fill=INK,leading=None):
    st=ParagraphStyle('body',fontName='Segoe',fontSize=size,leading=leading or size*1.42,textColor=color(fill))
    p=Paragraph(t,st);pw,ph=p.wrap(w,H);bottom=top-ph
    assert bottom>=58,(page_number,t[:60],bottom)
    p.drawOn(C,x,bottom);checks.append({'page':page_number,'kind':'paragraph','bottom':round(bottom,2)})
    return bottom
def block(x,top,w,title,body,size=11):
    txt(x,top,title,14,True);return para(x,top-13,w,body,size)-23
def table(x,top,width,heads,rows,ratios=None,size=11):
    ratios=ratios or [1]*len(heads);cw=[width*a/sum(ratios) for a in ratios]
    ps=ParagraphStyle('cell',fontName='Segoe',fontSize=size,leading=size*1.32,textColor=color(INK))
    hs=ParagraphStyle('head',parent=ps,fontName='SegoeBold',textColor=white)
    cells=[[Paragraph(str(v),hs) for v in heads]]+[[Paragraph(str(v),ps) for v in row] for row in rows]
    t=Table(cells,colWidths=cw,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),color(INK)),('ROWBACKGROUNDS',(0,1),(-1,-1),[color(LIGHT),white]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),('LINEBELOW',(0,-1),(-1,-1),.6,color(LINE))]))
    tw,th=t.wrap(width,H);assert top-th>=62,(page_number,'table',top-th)
    t.drawOn(C,x,top-th);return top-th
def image(name,x,y,w,h):
    path=ENG/'previews'/name
    C.drawImage(str(path),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
def note(x,top,w,title,body):
    st=ParagraphStyle('n',fontName='Segoe',fontSize=10.5,leading=14.5,textColor=color(INK))
    p=Paragraph(body,st);_,hh=p.wrap(w-28,H)
    height=hh+53;assert top-height>=58,(page_number,'note',top-height)
    rect(x,top-height,w,height,PALE);txt(x+14,top-23,title,11,True,TEAL);p.drawOn(C,x+14,top-height+14)
    return top-height
def link(label,url):return '<link color="#007F80" href="'+escape(url,{'"':'&quot;'})+'">'+escape(label)+'</link>'
def page(n,title,sub):
    global page_number
    page_number=n
    rect(0,0,W,H,'#FFFFFF')
    txt(36,H-30,'WORKSHOP / CNC + PLASMA',10,True,TEAL)
    right(W-36,H-30,'REV F | 25 SEP 2026 | ONE-PIECE HOISTED BED')
    txt(36,H-70,title,27,True)
    para(36,H-87,W-72,sub,11,MUTED)
    line(36,H-117,W-36,H-117)
    line(36,43,W-36,43)
    txt(36,26,'DIMENSIONS mm UNLESS STATED / ENGINEERING REVIEW / NOT RELEASED FOR ORDERING OR FABRICATION',8,False,MUTED)
    right(W-36,26,f'{n} / 8',9)
def end():C.showPage()

# 1. Current machine, using real CAD previews rather than the superseded Rev C illustration.
page(1,'One machine. Two removable tool systems.','A rigid load path, a one-piece winch-out bed and clear process controls. Current CAD is shown; proposed improvements are labeled separately.')
image('RevE_ROUTER.png',36,85,700,620)
x=765;y=H-146;w=W-x-36
y=block(x,y,w,'800 X / 1000 Y / 100 Z','Nominal motion travel in mm. Actual usable cutting area remains dependent on the final tool and purchased-module interfaces.')
y=block(x,y,w,'Rigid bed support','Ten full-length aluminum T-slot strips lie on a machine-surfaced two-layer MDF sub-bed over a welded steel ladder that bears continuously on the receiver ledgers. The water tray is not the router support.')
y=block(x,y,w,'One-piece mode change','The whole bed is a single module on four M8 drawdowns. It leaves on the owner overhead winch through the open front window; no multi-part unload, no racks, no staged handling.')
y=block(x,y,w,'A deliberate industrial finish','Finish direction: dark frame, natural aluminum datums and one accent color for handles and mode controls. Group cable routes and labels; keep covers removable for inspection.')
table(x,y,w,['Envelope','Current model'],[['Fixed footprint','1206.8 x 1479.2'],['Static height','1370'],['Module mass estimate',f'{MODMASS:g} kg on a 567 kg winch']],[1,1.25],10.5)
note(x,196,w,'CURRENT MODEL / NEXT DESIGN PASS','Amber shows purchased-component envelopes. Finish, covers and diagnostic display are design intentions, not installed hardware. Rigidity and service access take priority over adding exterior skins.')
end()

# 2. Bed geometry and the actual stock count.
page(2,'The one-piece T-slot bed and its working heights','Ten full-length strips, no cross seams, one saw cut per purchased bar. The bare work plane is unchanged from Rev E, so head and motion geometry are untouched.')
px,py,s=87,105,.43
rect(px,py,1000*s,1197*s,'#CFDCDD',INK)
for by in (75,475,875,1275):
    rect(px,py+(by-76.5-19.05)*s if by>76.5 else py,1000*s,min(38.1,38.1)*s,'#BFD2D3')
for k in range(10):
    if k:line(px+k*100*s,py,px+k*100*s,py+1197*s,INK,.55)
    for slot_center in (10,30,50,70,90):
        rect(px+(k*100+slot_center-3.1)*s,py,6.2*s,1197*s,'#789599')
for nx,ny0,ny1 in [(938.5,488.5,678.5),(938.5,1085.5,1155.5)]:
    rect(px+nx*s,py+ny0*s,(1000-nx)*s,(ny1-ny0)*s,'#FFFFFF',AMBER)
rect(px+9,py+1197*s/2-6,206,24,'#CFDCDD')
txt(px+15,py+1197*s/2,'One module, slots run full length',11,True)
line(px,py-17,px+1000*s,py-17,MUTED)
txt(px+125,py-35,'1000 overall X',12,True)
C.saveState();C.translate(px-24,py+160);C.rotate(90);txt(0,0,'1197 overall Y',12,True);C.restoreState()
txt(px,py+1197*s+24,'PLAN / 10 STRIPS / 5 SLOTS PER 100 mm / FLOAT NOTCHES IN AMBER',10,True,TEAL)
txt(px+330,py+1197*s+8,'Rear of machine',9,False,MUTED)
x=590;w=W-x-36;y=H-145
y=table(x,y,w,['Bed element','Quantity and size'],[['One-piece module',f'1 at about {MODMASS:g} kg, four M8 drawdowns'],['20100 extrusion strips','10 at 1197; ONE cut per 1220 bar = five two-packs'],['MDF sub-bed','2 layers at 12.7, machine-surfaced in place'],['Steel ladder','2 rails 2 x 2 x 1290; 4 crossmembers 2 x 1.5 flat'],['Optional spoilboards','2 at 465.6 x 1197 x 19, one MDF sheet']],[1,1.4],10.5)-18
y=table(x,y,w,['Height from floor','Z'],[['Rail top / MDF seat','890.8 / 895.4'],['Strip bottom on surfaced MDF','920.8'],['Bare T-slot surface','940.8'],['Fresh spoilboard top','959.8'],['Plasma slat top','850.0']],[1.5,.6],10.5)-18
y=note(x,y,w,'FLATNESS COMES FROM THE MACHINE','The router surfaces the MDF sub-bed in place before the strips are fitted, so ledger, weld and stock tolerances never reach the aluminum. Bare and head planes are identical to Rev E; the separate head-mounting-position requirement is unchanged.')-12
para(x,y,w,'<b>Count:</b> 5 packs x 2 bars = 10 strips; ONE cut to 1197 leaves 23 mm trim. Rev E needed 30 cuts to 397 with two cross seams.<br/><b>Product:</b> '+link('B0BXNWK99C','https://www.amazon.com/dp/B0BXNWK99C')+' title and dimension image confirm the 100 x 20 20100 section (6.2 slots at 20 pitch, verified against the factory drawing); its 20 x 20 bullet is a listing error. Measure the received profile before cutting.',10.5,MUTED)
end()

# 3. Visible states and qualified hoist sequence.
page(3,'Change modes with four bolts and a winch','The whole bed leaves as one checked module through the open front window on the owner overhead winch. Water handling is automatic in parts; rigging is owner scope.')
image('RevE_ROUTER.png',36,340,555,350)
image('RevE_PLASMA_SETUP.png',600,340,555,350)
left=[('1 / Stop and clear the head','Inhibit machining, remove the mounted spindle or torch to its cradle and park the gantry at the rear datum.'),('2 / Drain and inspect','Use the drain cycle and required dwell. A low-level indication does not mean dry: remove puddles, sludge and loose debris.'),('3 / Rig and unbolt','Hang the 4-leg sling on the four lift ears and take up slack. Remove the four M8 drawdowns to the internal tray.')]
rightblocks=[('4 / Hoist out','Winch up 60 mm, pull the module forward out the front window along the sampled path, then hoist clear and park it on the winch or its stand.'),('5 / Reverse to install','Lower through the front window at handling height, translate rearward, then descend: the two dowels engage on the final drop. Torque the four M8 drawdowns to 12 Nm on clean seats.'),('6 / Make the sequence repeatable','Weigh the finished module before its first hoist and verify sling symmetry. Keep removed bolts in the tray, use the prescribed torque and a guided checklist; recheck the path if any guard, sensor or cable envelope changes.')]
for xx,items in [(36,left),(610,rightblocks)]:
    yy=328
    for title,body in items:yy=block(xx,yy,535,title,body,10.5)
txt(36,66,f'MODEL MASS: one-piece module about {MODMASS:g} kg estimated, on a 567 kg (1250 lb) winch. Sampled hoist path: {SWAP["sample_count"]} poses, {SWAP["boolean_check_count"]} solid intersection checks, zero contacts.',10,False,MUTED)
end()

# 4. Current fixed wet circuit. Keep actual relay behavior separate from proposed diagnostics.
page(4,'Gravity drain. Vented storage. Pump refill.','The compressor and CV-15HS venturi are not connected to the water reservoir. The reservoir remains open to atmosphere.')
image('RevE_WATER_CUTAWAY.png',36,370,590,330)
y=350
y=block(36,y,560,'Fixed pan and replaceable slats','19 loose steel slats, 880 x 75 x 3.048. Normal water is Z820, 30 mm below the Z850 slat tops. The modeled normal pan inventory is 79.616 L.')
y=block(36,y,560,'Reservoir and charge','900 x 600 x 250 internal: 135 L gross. Maximum total circuit water inventory is 115 L, including water in the pan and lines. Maintain the modeled return capacity and independent overflow route.')
note(36,y,560,'REFILL IS AN EFFICIENCY BOTTLENECK','The selected 7 L/min open-flow pump gives an estimated 13-18 minute installed refill. A faster transfer target requires pump/head-loss selection, dirty-water qualification and overflow testing together; no faster performance is claimed.')
x=660;w=W-x-36;y=H-145
for title,body in [('Drain / current logic','ROUTER disables refill and keeps the drain open. Router-water-ready requires drained indication continuously for at least 60 seconds plus bed-lock confirmation. Low water does not mean dry or clean.'),('Refill / current logic','PLASMA allows 10 seconds for valve closure, then requires guarded FILL in SETUP. Normal level stops the pump; independent high-high and tank-low chains interrupt refill. Release and press FILL again after interruption.'),('Feedback boundary','The selected drain valve has no position-feedback output. Closure is timed, not confirmed. Timeout, contradictory-sensor and lack-of-progress diagnostics are proposed additions, not functions of the present relay circuit.'),('Service and capacity','Provide access to the catch basket, filter bowl and level guards. Keep returns downhill, the overflow unvalved, the reservoir vent open and a 25 mm minimum refill air gap above maximum water.')]:y=block(x,y,w,title,body,10.5)
table(x,y,w,['Level datum','Z mm'],[['Minimum operating target','810'],['Normal water','820'],['Overflow crest','825'],['High-high','827'],['Pan rim','835']],[1.4,.6],10.5)
end()

# 5. Owner material: show the exact allocation and separate it from a redesign.
page(5,'Use the aluminum you already have','Provisional inventory: one 12 x 12-inch plate at 1/2-inch thickness and one at 3/8-inch thickness. Alloy and usable finished thickness remain unknown.')
px,py,s=54,157,1.48
rect(px,py,304.8*s,304.8*s,'#EEF3F5',INK)
half=OWN['owned_plates'][0]['proposed_allocations']
names=['Z carrier','Tool adapter','Drive shoe A','Drive shoe B']
fills=['#B7D5D4','#C9DFDE','#E5D6B7','#E5D6B7']
for r,label,fill in zip(half,names,fills):
    xx=px+r['x_mm']*s;yy=py+r['y_mm']*s;ww=r['width_mm']*s;hh=r['height_mm']*s
    rect(xx,yy,ww,hh,fill,INK);txt(xx+8,yy+hh/2,label,11,True)
txt(px,py+304.8*s+20,'1/2-INCH PLATE / 304.8 x 304.8 mm',11,True,TEAL)
para(px,py-20,480,'Bounding rectangles reserve 10 mm edge clearance and 6 mm gaps. Drive shoes are machined down to 6.35 mm. This is a stock layout, not released toolpaths.',10.5,MUTED)
x=570;w=W-x-36;y=H-145
y=block(x,y,w,'Concentrate material where it works','The 260 x 170.2 Z carrier, 110 x 70 tool adapter and two 65 x 48 drive-shoe blanks fit the 1/2-inch plate with the shown margins. Confirm alloy, flatness and usable thickness before selecting machining allowances.')
y=block(x,y,w,'The 3/8-inch piece has a useful role','A preliminary rectangle layout fits flange and web blanks for three thrust-link supports. Those supports currently have integral billet geometry. A bolted or welded plate version needs defined joints, locating features and stiffness checks before adoption.')
y=block(x,y,w,'Machine datums after the weldment settles','Weld, cool and measure the frame before finishing the rail pads. The bed no longer needs a machined receiver plane: the module rails bear directly on the ledgers and the router surfaces the MDF sub-bed in place before the strips are fitted.')
note(x,y,w,'MAKE THE PART FAMILY EASY TO BUILD','Use shared datum references, numbered beam positions and consistent hardware access. A plate-built thrust link is a redesign: define its locating shoulders, fasteners, thread engagement and load path before replacing the current billet geometry.')
end()

# 6. Separate support paths and the actual stiffness screen.
page(6,'Rigidity comes from the complete load path','Keep the cutting forces out of the water tray and small actuator carriages. Sand is stationary ballast; it is not a substitute for section stiffness.')
x=36;w=520;y=H-146
for title,body in [('Workpiece side','Workpiece and spoilboard load the T-slot strips, which run continuously over four crossmembers on a glued two-layer MDF sub-bed. The ladder rails bear the full length of the receiver ledgers into the braced six-leg frame; the MDF adds damping the all-metal bed lacked.'),('Tool side','Spindle and Z load the gantry and independent linear guides. HMS40 modules supply drive force through floating axial links; their small carriages are not the primary supports for router cutting moments.'),('Locate, then clamp','Two diagonal Ø10 dowels locate the module on the ledgers; four M8 drawdowns clamp through welded compression sleeves, all reachable from above outside the deck plan. Clean the ledger tops before every reinstallation.'),('Keep moving mass under control','Fill only stationary frame tubes with dry sand after fabrication and coating. Leave the bed module and the gantry unfilled. Set acceleration from measured moving mass and motor capability.')]:
    y=block(x,y,w,title,body,11)
note(x,y,w,'STIFFNESS IS NOT YET A MACHINE ACCURACY RATING','The elastic screen excludes joint rotation, weldment distortion, gantry torsion, guide preload and tool compliance. Measure bed return repeatability and tool-to-workpiece deflection at center and corner positions before assigning a cutting envelope.')
x=610;w=W-x-36;y=H-146
txt(x,y,'Two support paths meet at the frame',14,True)
for i,(title,body) in enumerate([('WORKPIECE','T-slot strips > surfaced MDF > ladder > ledgers'),('TOOL','Head > Z / X structure > independent Y guides'),('COMMON FRAME','Bracing > short supported feet > floor')]):
    top=y-22-i*88
    rect(x,top-64,w,64,PALE if i!=2 else LIGHT)
    txt(x+14,top-21,title,11,True,TEAL)
    para(x+14,top-29,w-28,body,11)
y-=300
SS=json.loads((ENG/'strength-screen.json').read_text(encoding='utf-8'))
xm100=SS['one_module_crossmember'][0]['deflection_mm'];st100=SS['one_20100_strip'][0]['deflection_mm']
sum100=SS['bed_combined_vertical_screen']['100_N_sum_mm'];sum500=SS['bed_combined_vertical_screen']['500_N_sum_mm']
y=table(x,y,w,['Preliminary member screen','At 100 N'],[['One 2 x 1.5 crossmember, 938.4 mm simple span',f'{xm100:.4f} mm'],['One 20100 strip, one 400 mm bay, simply supported',f'{st100:.4f} mm'],['Conservative sum of these two',f'{sum100:.4f} mm']],[2.5,1],10.5)-20
para(x,y,w,f'The same two-member sum is about {sum500:.2f} mm at 500 N. This deliberately ignores what the Rev F sandwich adds: strip continuity over four supports, load sharing through the glued MDF into neighboring strips and members, and continuous rail bearing on the ledgers - each of which cuts the real number substantially. It is a screen, not predicted machine accuracy or a certified cutting-force limit.',10.5,MUTED)
end()

# 7. Current automation boundary and a clearly identified operator-interface direction.
page(7,'High tech should make the machine easier to run','Current motion and water controls remain separate. A proposed diagnostic panel explains permissions and faults without replacing the independent stop chain.')
x=36;w=540;y=H-146
for title,body in [('Motion / implemented in the compiled port','Kraken V1.1 drives X, Y1, Y2 and Z through four onboard TMC2160 channels. Independent Y homing provides the auto-squaring route. The image is compiled and statically checked; hardware commissioning remains.'),('Tool interfaces / defined architecture','Isolated tool-run and spindle-speed interfaces serve the selected head. External isolated Arc OK / UP / DOWN signals request plasma Z correction. Motor control stays on Kraken. The existing cutter interface remains unidentified.'),('Water / separate hardwired sequence','Float switches, timers and relay logic own drain, guarded refill and water permission. A combined isolated permissive reaches Kraken and independently gates tool permission. The present Kraken image does not supervise each water sensor.'),('Mode change / deliberate setup operation','Stop and park, inhibit tool power, change the bed and head, then apply the correct firmware mode with a cold controller reset. Re-home and verify tool offsets before a job. Bed presence cannot prove clamp preload or cleanliness.')]:
    y=block(x,y,w,title,body,11)
note(x,y,w,'AUTOMATIC DOES NOT MEAN UNATTENDED CONVERSION','The current system automates water transfer and motion functions. Bed movement, cleaning, clamping and configuration confirmation remain manual. No automatic standstill proof or clamp-torque sensing is implemented.')
x=625;w=W-x-36;y=H-146
txt(x,y,'Proposed operator panel / layout study',14,True)
rect(x,y-203,w,180,INK)
txt(x+18,y-54,'SETUP',20,True,'#8BE1D3')
txt(x+18,y-78,'TOOL POWER INHIBITED',11,True,'#FFFFFF')
line(x+18,y-92,x+w-18,y-92,'#597D86')
for i,t in enumerate(['MODE: ROUTER     WATER: DRAINING','BED: CONFIRM REQUIRED     HEAD: CHECK','NEXT: inspect, seat and clamp all bed parts']):
    txt(x+18,y-117-i*24,t,10.5,False,'#FFFFFF')
y-=231
y=block(x,y,w,'Show the reason for every inhibit','Display requested mode, active firmware mode, homed state, transfer state and the first missing permission. Show unknown feedback as unknown. Do not display a valve as closed when only its timer has elapsed.',11)
y=block(x,y,w,'Add useful diagnostics in the next control revision','Provide isolated individual sensor monitoring, transfer timeout and contradictory-state detection. Log the first fault and require deliberate recovery. These functions need additional I/O and software; they are not in the present relay circuit.',11)
note(x,y,w,'KEEP THE PHYSICAL CONTROLS CLEAR','Use labeled SETUP / RUN and ROUTER / PLASMA controls, guarded FILL, STOP and a visible status indicator. A screen may explain state; it must not bypass the hardwired tool-enable and stop circuit. Panel fit and wiring remain open.')
end()

# 8. Current controller and the remaining definition, with actionable references.
page(8,'What is defined, and what still prevents release','Successful model checks are useful evidence. They do not establish supplier fit, complete electrical design, final machining accuracy or physical commissioning.')
x=36;w=540;y=H-145
for title,body in [('Kraken with onboard drivers','Kraken V1.1 uses four onboard TMC2160 channels: X, Y1, Y2 and Z. No external stepper drivers are budgeted. The compiled grblHAL port provides independent dual-Y homing and external isolated UP/DOWN/Arc-OK THC inputs. The owner Mesa THCAD arc-voltage converter and an alternate FluidNC/LinuxCNC route are logged as an open controls decision.'),('What has been checked',f'Both STEP states read back successfully. The model contains {ROUTERV["part_count"]:,} valid solids with no unresolved static intersections. The one-piece module hoist screen examined {SWAP["sample_count"]:,} sampled poses and {SWAP["boolean_check_count"]:,} actual solid-intersection cases with zero contacts.'),('What those checks do not prove','The compiled firmware has not been boot/bench/HF tested. Static and sampled checks do not certify continuous clearance, whole-machine stiffness, rigging behavior or production capability. Weigh the module and pull-test the MDF fastening before the first hoist.'),('Water and process control','Use isolated field interfaces and independent power interruption. Do not connect 24 V field signals to Kraken 3.3 V headers. Exact torch start, arc sensing and HF compatibility depend on the unidentified plasma power source.')]:y=block(x,y,w,title,body,11)
note(x,y,w,'EXISTING PLASMA CUTTER','An AG-60 torch listing does not identify the power source or prove its CNC compatibility. The cutter model/start circuit and actual torch envelope must be established before final wiring and mounting details can be released.')
x=625;w=W-x-36;y=H-145
for title,body in [('Mounting and mechanical details','Close the HMS40 base interface, HGR20 hole pattern, ZBX80 datums and Z power-loss retention. Finish cable chains, way covers, dust-shoe and torch clearances. The upper float guards sit only 3 mm beyond the nominal maximum X head axis.'),('Cabinet and wet-service access','Solved by relocation: the enclosure stands upright in the front bay under the water table, door forward through the open front window, on a bolt-on cage beneath the first two pan bearers. Routine electrical service needs no draining and no pan or bed removal. VFD thermal layout, glands and the internal panel remain open.'),('Efficiency and handling','The Rev F conversion burden is four M8 drawdowns, one sling and the winch button. Owner scope that remains: the overhead winch anchorage or track, sling selection, and a weighed first lift. The sampled path assumes the gantry parked at the rear datum.'),('Fabrication and CAM','Set final joint details, datum machining, tolerances and supplier-specific fasteners. Generate CAM only for the actual fabrication machine, tooling and postprocessor after those dimensions are closed.')]:y=block(x,y,w,title,body,11)
para(x,y,w,'Design references: <b>MECHANICAL-ENGINEERING.md</b>, <b>WATER-CONTROL.md</b>, <b>DESIGN-EFFICIENCY-REVIEW.md</b> and <b>PACKAGE-STATUS.md</b>. Rev F rebuilt and re-verified the bed CAD as the one-piece hoisted module; it still does not release the design for ordering or fabrication.',10.5,MUTED)
end()
C.save()
r=PdfReader(PDF)
assert len(r.pages)==8
text='\n'.join(p.extract_text() or '' for p in r.pages)
for term in ['REV F','Rigidity','High tech','1000 overall X','1197','135 L','115 L','12 x 12','no position-feedback','13-18','four M8','5 SLOTS PER 100','5 packs x 2 bars = 10 strips','ONE cut','listing error','THCAD']:
    assert term in text,term
assert 'cassette' not in text.lower(),'stale cassette copy'
assert 'REV E |' not in text
assert '972.8' not in text and '157.5 L' not in text
assert '$' not in text, 'Prices are outside this design-focused PDF'
assert all(ord(c) not in [0xfffd, 0x00c3, 0x00c2] for c in text), 'Possible text encoding error'
report={'pdf':str(PDF),'pages':len(r.pages),'text_checks_pass':True,'paragraph_bounds_pass':True,'links':sum(len(p.get('/Annots',[])) for p in r.pages),'scope':'Rev F one-piece hoisted bed: design, efficiency and control architecture','sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'cad_geometry_changed':True,'cad_change':'Rev F replaced the six-cassette bed with the one-piece hoisted module; this brief documents the rebuilt and re-verified geometry.','visual_review':'Render and inspect latest pages before delivery'}
(OUT/'concept-pdf-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
