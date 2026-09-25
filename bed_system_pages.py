page(1,'The router bed now has a real docking system.','Fixed wet pan. Four removable bridge beams. Six rigid deck panels. Every part stores inside the chassis.')
pic('router',38,101,756,613)
heading(824,692,'01 / INTEGRATED BED SYSTEM','One finished machine')
y=638
for title,body in [
 ('A structural bridge over the pan','Paired steel beams land on metal receiver seats tied directly to all six chassis legs. No routing load passes through the water tray or slats.'),
 ('Six numbered, rigid deck panels','Each panel has a welded steel frame, an 8 mm aluminum subplate and replaceable MDF. Pins locate it; metal-to-metal clamps hold it down.'),
 ('Guided drain and refill','Fixed plumbing sends water into a vented settling reservoir. No hose disconnection or wet cassette lift is needed for a normal mode change.'),
 ('Everything has a parking place','Lightweight lift-off covers reveal the full-width cabinet. Covers park on side studs within the rail overhang; angled beam slots and numbered panel banks keep the changeover orderly.'),
 ('A deliberate exterior','Graphite skins conceal the braces; removable brushed-metal shields protect the wet zone. Amber marks identify release points and clamps. Service panels remain accessible.')]:
    text(824,y,title,12,INK,True); y=para(824,y-12,318,body,10.5)-19
rect(824,83,318,92,'#EAF2F2',None)
text(838,154,'REVISION C REPLACES REVISION B',10,RAIL,True)
para(838,141,289,'The rail-support height increases from 930 to 1050. Plasma stays at 850; the new router deck starts at 972.8 before surfacing. Separate head mounting references accommodate the two planes.',10)
text(54,79,'Chassis: 1150 W x 1450 D. No swap cart or external bed-storage station.',10,MUTED)
C.showPage()

page(2,'Exactly how the CNC bed fits','The removable deck bridges the fixed pan. Its supports stay clear of plasma sheet loading when removed.')
pic('exploded',40,168,669,548)
text(59,151,'EXPLODED ASSEMBLY - vertical separation is illustrative; gantry hidden.',9,MUTED)
heading(751,691,'02 / SIDE SECTION','Two work planes')
# Diagram uses vertical scale1.05 and a shortened horizontal section.
sx=782; sy=264; ss=1.05
def z(zz): return sy+(zz-700)*ss
rect(sx,z(735),218,3*ss,ALU,INK)
rect(sx,z(738),4,97*ss,ALU,INK);rect(sx+214,z(738),4,97*ss,ALU,INK)
for xx in [sx+25,sx+70,sx+115,sx+160,sx+200]: rect(xx,z(775),3,75*ss,EDGE,INK)
line(sx+5,z(815),sx+213,z(815),RAIL,1,[4,2])
rect(sx-27,z(789.2),25,50.8*ss,GRAPH,INK)
rect(sx+220,z(789.2),25,50.8*ss,GRAPH,INK)
rect(sx-22,z(840),20,30*ss,ALU,INK);rect(sx+220,z(840),20,30*ss,ALU,INK)
rect(sx-25,z(870),269,50.8*ss,GRAPH,INK)
rect(sx-12,z(920.8),244,25*ss,GRAPH,INK)
rect(sx-12,z(945.8),244,8*ss,ALU,INK)
rect(sx-12,z(953.8),244,19*ss,MDF,INK)
for zz,label in [(972.8,'972.8  router, before skim'),(920.8,'920.8  panel datum'),(870,'870  beam underside'),(850,'850  plasma slats'),(815,'815  normal water target'),(735,'735  pan low point')]:
    line(sx+252,z(zz),sx+272,z(zz),MUTED,.5)
    text(sx+276,z(zz)-3,label,8.5,INK)
text(751,235,'20 mm nominal slat-to-beam clearance',11,RAIL,True)
para(751,220,383,'Fixed ledgers stop at 840, below the slats. The removable beams carry their own 30 mm riser feet, so their undersides sit at 870. Verify clearance to warped slats before installing the deck.',10.5)
line(48,126,1140,126,LINE)
para(52,111,522,'LOAD PATH: cutter -> MDF/aluminum panel -> steel panel frame -> paired bridge beam -> hard receiver seats -> six-leg chassis -> floor.',11,INK)
para(630,111,501,'The 100 mm Z stroke does not span both work planes by itself. The torch and router need independently located mounting references, set from their actual tool-tip geometry.',10.5,MUTED)
C.showPage()

page(3,'Rigid contact, repeatable location, captive hardware','Precision is established at the metal contacts; the MDF is replaceable and is surfaced after the complete deck is installed.')
heading(50,692,'A / ONE DECK PANEL','Small enough to handle')
px=73; py=455
rect(px,py,284,20,GRAPH,INK)
rect(px+7,py+54,270,12,ALU,INK)
rect(px+7,py+102,270,28,MDF,INK)
for xx in [px+26,px+243]:
    rect(xx-6,py+44,12,28,ALU,INK)
text(73,620,'19 mm MDF, individually replaceable',10,INK)
text(73,535,'8 mm aluminum subplate',10,INK)
text(73,433,'25 x 25 x 2 steel frame + center rib',10,INK)
para(50,409,336,'Actual panel blank: 497 x 397. Six panels form a 997 x 1197 deck with 3 mm seams. Each completed panel is approximately 10-11 kg. Handles fold flat; numbered corner keys prevent transposition.',10.5)

heading(439,692,'B / LOCATORS AND CLAMPS','Locate first. Pull down second.')
rect(460,486,282,94,'#ECF1F3',INK)
for xx,yy in [(478,502),(724,502),(478,560),(724,560)]:
    C.setFillColor(col(ALU));C.circle(xx,yy,8,fill=1,stroke=1)
C.setFillColor(col(ORANGE)); C.circle(502,530,9,fill=1,stroke=0)
poly([(696,521),(703,530),(696,539),(689,530)],ORANGE,None)
text(470,597,'Round locator',10,INK);text(650,597,'Diamond locator',10,INK)
line(502,540,502,588,MUTED,.7);line(696,540,696,588,MUTED,.7)
text(463,459,'Three datum contacts + one preset support',10,INK)
para(439,435,321,'Use hardened mating inserts, a round locator and a relieved diamond locator. Captive M8 draw-down screws load metal sleeves directly above supports; MDF is not in the clamping stack. Recessed access plugs cover the screw pockets.',10.5)
para(439,325,321,'Clean and inspect the contact pads at each swap. Keep paint, rubber and chips off the datum faces. Final pin fits and screw engagement follow the selected hardware drawings.',10,MUTED)

heading(825,692,'C / REMOVABLE CROSSBEAM','A tied pair of 2-inch tubes')
rect(854,491,90,90,GRAPH,INK);rect(944,491,90,90,GRAPH,INK)
rect(861,498,76,76,white,INK);rect(951,498,76,76,white,INK)
line(944,488,944,584,ORANGE,2)
rect(862,448,32,43,ALU,INK);rect(994,448,32,43,ALU,INK)
text(847,610,'101.6 wide x 50.8 high + 30 riser feet',10,INK)
text(842,419,'1044 finished overall; 1032 tube blanks',10,INK)
para(825,398,316,'Two tubes are connected along their meeting seams and at load-transfer points, with 6 mm end diaphragms. Ground or shimmed contact pads set the datum after welding. End plates alone do not establish equal load sharing.',10.5)
para(825,286,316,'Beam clamps pull the riser feet onto fixed steel seats. Locators carry lateral forces. Clamp engagement sensors support the changeover sequence; they do not prove clamp preload.',10,MUTED)

line(50,220,1140,220,LINE)
text(50,196,'STIFFNESS CHECK / ILLUSTRATIVE, NOT A TEST RESULT',11,RAIL,True)
para(50,179,515,'A tied pair of 2 x 2 x 0.120 tubes, simply supported over about 1 m, deflects approximately 0.023 mm under a 100 N central load if both tubes share that load. One tube carrying it alone gives about 0.047 mm.',10.5)
para(633,179,504,'This calculation excludes joints, panels, gantry and axes. Commission the assembled bed with a known force and an indicator, then repeat at seams and corners. Suggested starting targets: <=0.10 mm bed movement at 100 N and <=0.05 mm height change after a clean re-dock; verify these experimentally.',10.5)
C.showPage()

page(4,'A swap that stays inside the machine footprint','No full-bed lift, no moving water pan and no long drawer. The storage order matches the assembly order.')
pic('cutaway',37,133,687,582)
text(56,116,'CUTAWAY / skins and doors removed only to show storage',9,MUTED)
heading(759,692,'03 / ROUTER CHANGEOVER','A guided sequence')
y=638
steps=[
 ('1','Isolate and remove the torch head','Finish the job and inhibit machining. Remove the torch head cassette; park the bare Z fully up at the rear. Torch retraction alone may not clear the higher deck.'),
 ('2','Run the drain cycle','Verify return capacity, open the drain, monitor low level, then close it. The panel reports drained to low level, not dry. Inspect and clean residual water.'),
 ('3','Dock the four beams','Lift off the light front covers and park them on the stand. Remove beams from their angled slots; seat riser feet, engage locators and tighten captive beam clamps.'),
 ('4','Fit the six panels','The panel banks are now accessible. Fit numbered panels to their keyed locations; clean contacts and tighten the metal draw-downs.'),
 ('5','Fit the router head and probe','With the deck locked, fit the router head at its indexed reference. Connect dust collection, probe the bed and check the tool sweep. New or resurfaced MDF needs a fresh datum.'),
 ('6','Return to plasma in reverse','Stop and remove the router head first. Stow panels, then beams. Clean wood dust; confirm the dry deck is absent before refill. Fit and identify the torch head before enabling plasma.')]
for n,title,body in steps:
    tag(769,y-4,n); text(789,y,title,11.5,INK,True)
    y=para(789,y-12,340,body,10.1)-18
rect(50,59,1090,39,PAPER,None)
para(63,88,1065,'Storage allowance: approximately 1005 W x 550 H x 680 D clear, with the full opening exposed. Beam assemblies park around 25 degrees; two banks of three panels stand behind them. Verify feet, clamps, handles and cover-parking clearance in the mock-up.',10)
C.showPage()

page(5,'Automatic water handling, with a fixed wet system','Normal changes retain every hose connection. Valve, pump, sensors and cleanout are accessible from the rear wet-service bay.')
# Schematic - named components and independent paths.
def node(x,y,w,h,title,sub,fill=PAPER):
    rect(x,y,w,h,fill,LINE);text(x+12,y+h-23,title,12,INK,True);para(x+12,y+h-32,w-24,sub,10)
def arrow(points,color=RAIL,width=1.5):
    for a,b in zip(points,points[1:]): line(*a,*b,color,width)
    a,b=points[-2:];dx=b[0]-a[0];dy=b[1]-a[1];d=math.hypot(dx,dy);ux=dx/d;uy=dy/d
    poly([b,(b[0]-ux*8-uy*3,b[1]-uy*8+ux*3),(b[0]-ux*8+uy*3,b[1]-uy*8-ux*3)],color,None)
node(55,527,362,134,'FIXED PAN','920 x 1200 outside; rim 835; slats 850.<br/>Nominal operating water 815; overflow 825.<br/>Sloped floor: about 1% toward accessible sump.')
node(483,543,242,102,'COARSE CATCH + DRAIN','Removable catch basket/cleanout<br/>1-1.5 in full-port motorized valve<br/>24 V, position feedback, manual override')
node(796,518,345,146,'VENTED SETTLING RESERVOIR','Dirty inlet -> baffle -> clarified pickup.<br/>900 x 500 x 350 internal = 157.5 L gross.<br/>Reserve 125 L usable return capacity.<br/>Proposed total liquid charge 110 L, including lines.')
arrow([(417,592),(483,592)])
arrow([(725,592),(796,592)])
text(428,608,'gravity',9,MUTED)
node(795,368,346,94,'REFILL PUMP','24 V diaphragm candidate; pickup above sludge.<br/>Fused supply; pan high-high and reservoir low-low interrupt pump power independently.')
arrow([(970,518),(970,462)])
arrow([(795,410),(40,410),(40,561),(55,561)])
text(397,423,'Air-gapped return outlet above maximum pan level',10,RAIL)
arrow([(325,661),(325,691),(1091,691),(1091,664)],MUTED,1.2)
text(538,702,'Independent, unvalved overflow return',10,MUTED)
para(55,475,643,'The reservoir remains under the rear half of the machine; the deck cabinet occupies the front. All baffle compartments share a vented headspace. Tank, pan, pipes and trapped water must fit the verified return volume after any power loss.',10.5)
line(50,341,1140,341,LINE)
cols=[
 ('Drain permission','Dedicated changeover only. Machining inhibited; pump off; wet system present; reservoir installed with sufficient capacity. Valve-open feedback and a separate drain timeout are required.'),
 ('Drain completion','Stable pan-low signal, then close valve and verify closed feedback. Inspect puddles and sludge. An actuator end switch proves position, not a leak-tight valve seat or a dry pan.'),
 ('Refill permission','All six panels and four beams absent; dry dust removed; drain closed; overflow clear. Stop at normal level. Pan high-high and reservoir low-low also stop the pump through an independent circuit.'),
 ('Fault and restart','Timeout, no level progress, inconsistent sensors or reservoir high-high latches a fault. Pump stays off after power loss; reconcile levels and valve position before operator restart. No automatic machining start.')]
for i,(title,body) in enumerate(cols):
    x=50+i*278;text(x,315,title,11,INK,True);para(x,300,252,body,10)
rect(50,91,1090,70,'#F9EEE7',None)
para(64,146,1060,'Dirty-water component selection remains open: coarse screening does not remove abrasive fines. The candidate motorized valve and refill pump require confirmation for the actual settled water and additives. Keep the valve, basket, baffles and level switches removable for cleaning. Commission blocked-drain, overflow, independent-trip and interrupted-power cases; measure cycle times instead of promising a drain time.',10.2)
C.showPage()

page(6,'Revision C material basis and completion checks','This replaces the earlier bed concept and 930 mm rail-support height. Exact motor/head interfaces still require their supplier drawings.')
text(50,695,'PRELIMINARY FABRICATION BASIS',12,INK,True)
rows=[
 ('2','1450','Top Y-support tubes','2 x 2 x 0.120 steel'),
 ('6','949.2','Legs','50 foot allowance; steel top 1050'),
 ('4','648.8','Lower side ties','2 x 2 x 0.120 steel'),
 ('4','1048.4','End ties','Front lower tie top 100.8'),
 ('2','1450','Fixed receiver ledgers','2 x 2 tube; top 840'),
 ('3','1032.4 nominal','Fixed pan bearers','2 x 2 + 8 end plates; fit clearance'),
 ('8','1032','Removable beam tube blanks','Pairs; 6 end plates -> 1044 finished'),
 ('8','30 rise','Removable beam feet','Remain with beams; pad faces set datum'),
 ('6','497 x 397 x 52','Complete panel modules','25 steel frame + 8 Al + 19 MDF'),
 ('6 sets','25 x 25 x 2','Panel steel frames','2 x 497 + 3 x 347 per panel'),
 ('1','920 x 1200 x 100','Fixed pan','Floor 735 low point; slats 850'),
 ('1','900 x 500 x 350 inside','Vented reservoir','157.5 L gross; wall/support extra'),
 ('1','1005 x 550 x 680','Cabinet clear space','Lift-off covers; diagonal beam rack'),
 ('1','1200','8080 gantry','Exact section/mass verification pending')]
xx=[50,89,231,431];ww=[39,142,200,264];ty=674
for x,w,h in zip(xx,ww,['Qty','Size / length','Assembly','Material / note']):rect(x,ty-22,w,22,INK,None);text(x+5,ty-15,h,8.8,white,True)
ty-=22
for i,row in enumerate(rows):
    for x,w,cell in zip(xx,ww,row):rect(x,ty-26,w,26,PAPER if i%2==0 else white,None);text(x+5,ty-16,cell,8.5)
    ty-=26
para(50,ty-13,634,'Stationary tube allowance: 18.284 m, approximately 84 kg steel. Dry sand: about 36.5 L / 58 kg at assumed 1.6 kg/L. Braces, caps, pan bearers, skins, beds, feet and stock allowance are additional. Leave sand out of the removable deck parts.',9.8,MUTED)
text(50,199,'PRIMARY REFERENCES / CLICK TO OPEN',10,RAIL,True)
refs=[
 ('Your HMS40 X; matching 1000 mm Y uses B0C7GN24S1','https://www.amazon.com/dp/B0C7GQTRRX'),
 ('Your RATTMMOTOR ZBX80 100 mm Z','https://www.amazon.com/dp/B09MVYGLNQ'),
 ('Carr Lane locating-pin principles','https://www.carrlane.com/product/locating-pins/locating-pins'),
 ('Valworx 24 V valve example - confirm media suitability','https://www.valworx.com/stainless-ball-valve-1-24-vdc'),
 ('Whale Gulper 320 maker guide - refill candidate only','https://whale.navico.com/globalassets/whale/marine/fishbox/resources/gulper_320_installation_guide.pdf'),
 ('SJE low-current water/wastewater level switches','https://www.sjerhombus.com/wp-content/uploads/2023/04/9500137I-ControlSwitchOverview.pdf')]
for i,(label,url) in enumerate(refs):
    yy=180-i*18;text(50,yy,label,9.1,RAIL);C.linkURL(url,(50,yy-2,689,yy+11),relative=0)

rx=744;text(rx,695,'WHAT STILL NEEDS TO BE PROVED',12,INK,True)
y=671
for title,body in [
 ('Whole-machine mass','Stored deck parts and reservoir water stay on the stand. The revised machine can approach roughly 450-550 kg before heavy stock, depending on skins and hardware. Size feet, ledgers, welds, tank shelf and floor supports for the complete load; do not count only the active bed.'),
 ('Head geometry and clearance','Plasma is 850; fresh router deck 972.8. Bridge underside 1127 gives 154.2 nominal clearance above the bare router bed, not usable material thickness. Verify the exact spindle, torch, dust shoe and 100 mm Z with their separate located plates.'),
 ('Motion-system capacity','Retain the chosen HMS40 modules, but check the assembled head and bridge masses, carriage moments and operating speed. A stiffer bed cannot remove compliance in the X carriage, adapters or spindle mounting.'),
 ('Positive mode verification','Confirm all beam/panel states, clamp engagement and head identity before enabling the selected process. Treat these as process interlocks until the electrical architecture is properly reviewed; they are not a certified safety system.'),
 ('Dryness and contamination','Draining does not dry steel. Inspect the pan, protect the underside of deck panels from condensation, and collect router dust at the head. Remove all wood parts and dust before plasma operation; keep the storage cabinet closed.'),
 ('Fabrication release','Mock up storage, beam seating and tool sweep at full scale. Then finalize pin/bushing fits, clamp hardware, connections, cabinet openings, plumbing materials and wiring. Prove clean re-docking and loaded deflection with an indicator.')]:
    text(rx,y,title,11,INK,True);y=para(rx,y-11,391,body,10.2)-19
C.save()
print('PDF:',PDF,flush=True)

# Internal arithmetic checks. These are concept checks, not a structural certification.
assert abs(50+949.2+50.8-1050)<1e-8
assert abs(840+30+50.8+25+8+19-972.8)<1e-8
assert 1032+6+6==1044
assert abs((2*1450+6*949.2+4*648.8+4*1048.4+2*1450)-18284)<1e-8
assert abs(2*497+3-997)<1e-8 and abs(3*397+2*3-1197)<1e-8
assert abs(.9*.5*.35*1000-157.5)<1e-8

design={
 'revision':'C','chassis_mm':[1150,1450,1050],
 'axis_travel_mm':{'X':800,'Y_left':1000,'Y_right':1000,'Z':100},
 'water_pan_external_mm':[920,1200,100],
 'planes_mm':{'pan_low_floor':735,'pan_rim':835,'plasma_slats':850,'fixed_ledger':840,'removable_beam_bottom':870,'panel_datum':920.8,'router_before_skim':972.8,'gantry_underside':1127},
 'deck_panel_mm':[497,397,52],'deck_panel_count':6,
 'bridge_beam_count':4,'bridge_beam_finished_length_mm':1044,
 'reservoir_internal_mm':[900,500,350],'reservoir_gross_L':157.5,'required_usable_return_L':125,'proposed_total_charge_L':110,
 'storage_clear_mm':[1005,550,680],
 'status':'Engineering concept; not released for fabrication',
 'pending':['Exact ER17 spindle and torch geometry','Supplier mounting holes and ratings','Clamp/locator hardware drawings','Fluid media compatibility','Electrical review and physical commissioning']
}
(ROOT/'output'/'bed-system'/'design-parameters.json').write_text(json.dumps(design,indent=2))
