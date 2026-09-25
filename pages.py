page(1,'Sand-filled steel chassis. Screw-driven axes.','Your selected KHMOS HMS40 X/Y modules + RATTMMOTOR ZBX80 Z  |  1000 Y x 800 X x 100 Z travel')
rect(38,104,760,600,PAPER,None)
p=iso(103,238,.29)
for n,q in [(1,(0,650,930)),(2,(1125,775,1020)),(3,(620,800,1087)),(4,(870,180,790)),(5,(1125,725,250))]: tag(*p(q),n)
text(58,87,'2 x 2 x 0.120 in STEEL  /  SIX LEGS  /  NO SEPARATE UPPER FRAME',10,MUTED,True)
text(58,69,'Router silhouette is provisional; the pan is shown to expose the bed-support layout.',9,MUTED)
xx=830; yy=H-149
heading(xx,yy,'01 / YOUR HARDWARE','Built around these parts')
yy-=58
for n,title,body in [
    (1,'Two 1000 mm Y modules','KHMOS HMS40, 10 mm lead. Each axis sits on a continuous shim-adjustable cap over a supported side beam.'),
    (2,'Short gantry adapters','12 mm aluminum saddles and gusseted cheeks connect the two Y carriages to the bridge. Hole patterns follow the actual modules.'),
    (3,'One 800 mm X module','Your HMS40 sits against an 8080 extrusion, 1200 long. The RATTMMOTOR 100 mm ballscrew slide carries the interchangeable head.'),
    (4,'Rigid, interchangeable beds','Three steel bearers take a dry router-bed cassette or a removable water pan. The routing bed does not rest on plasma slats.'),
    (5,'Sand-filled stationary chassis','2-inch square tube, 0.120-inch wall. Center legs shorten both rail-support spans; braces control sway. Six leveling feet.')]:
    tag(xx+10,yy-4,n); text(xx+28,yy,title,12,INK,True)
    yy=para(xx+28,yy-12,285,body,10.5)-21
rect(830,85,318,88,'#F9EEE7',None)
text(844,152,'DESIGNED FOR CNC ROUTING',10,RED,True)
para(844,140,290,'The stand and rigid bed are included. Final rail holes, spindle clamp and operating limits require the exact spindle and mounting drawings; this is not a ready-to-cut machine release.',10)
C.showPage()

page(2,'The stand, rail spacing and tool envelope','Chassis only: 1150 x 1450 (45.3 x 57.1 in); caps, bridge, feet and motors enlarge the machine envelope  |  Tube: 2 x 2 x 0.120 in')
text(78,696,'PLAN / X across, Y front to rear',12,INK,True)
plan(99,221,.29)
text(498,696,'FRONT / router head and Z mounting provisional',12,INK,True)
front(554,295,.31)
text(498,258,'HEIGHT STACK - FINAL TOOL-STACK CHECK REQUIRED',10,RAIL,True)
rows=[('850','Nominal work / slat plane'),('930','Top of chassis rail-support tubes'),('938','Top of 8 mm mounting strips, before shimming'),('~995','Y carriage top shown schematically'),('1007 / 1087','8080 bridge bottom / top in this layout')]
for i,(a,b) in enumerate(rows):
    y=237-i*24; text(500,y,a,11,INK,True); text(604,y,b,10.5,MUTED)
rect(65,74,391,110,PAPER,None)
text(80,163,'TRAVEL AND CUTTING AREA',11,INK,True)
para(80,151,358,'Travel: X 800 / Y 1000 / Z 100.<br/>Dashed target: 780 x 980, after reserving 10 mm at each end. This is not a verified cutting envelope. Tool offset, end switches and guards must be checked through the complete sweep.',10)
para(500,98,632,'Pan outside: 1000 x 1200 x 100, positioned at x = 75 to 1075 and y = 75 to 1275. A nominal 100 mm forward tool offset places the Y travel midpoint at 775 and the tool midpoint at 675. Module placement and bed height adjust to the actual head.',10)
C.showPage()

page(3,'Mount the axes. Brace the frame. Swap the bed.','Keep the spindle plate rigid and the torch floating/breakaway mount separate  |  Fill only the stationary chassis with sand')
heading(50,693,'A / Y SUPPORT SECTION','Rail -> cap -> chassis')
bx=83; by=409; sc=1.7
rect(bx,by,86.36,86.36,STEEL,INK)
rect(bx+5.18,by+5.18,76,76,white,INK)
rect(bx-41.82,by+110,170,13.6,LIGHT,INK)
rect(bx+9.18,by+145,68,68,RAIL,INK)
rect(bx-11.8,by+220,110,20,ALU,INK)
line(bx+43.18,by-10,bx+43.18,by+260,MUTED,.6,[4,3])
for y,t in [(by+229,'Carriage: use actual holes'),(by+177,'HMS40 module'),(by+116,'100 x 8 cap + shims'),(by+41,'2 x 2 x 0.120 in tube')]:
    line(bx+134,y,260,y,MUTED,.5); text(268,y-3,t,9.5)
text(50,377,'Exploded schematic; gaps are not installed spacing.',9,MUTED)
para(50,354,352,'Support each module at its specified mounting points along the full length. Attach caps with bolted tabs or through-bolts with crush sleeves. Seal penetrations against sand loss. Drill the caps only from the verified supplier pattern.',10.5)

heading(437,693,'B / GANTRY END','Wide, gusseted adapter')
rect(477,423,156,21,GOLD,INK)
rect(544,444,20,150,GOLD,INK)
poly([(486,444),(544,444),(544,526)],GOLD,INK)
rect(564,457,118,118,ALU,INK)
for cy in [477,554]:
    C.setFillColor(col(STEEL)); C.circle(554,cy,4,fill=1,stroke=0)
dim(484,401,633,401,'~100 x 120 saddle blank')
text(453,365,'12 mm aluminum plates + 6 mm gussets.',10,INK)
para(437,341,320,'Use an 8080 bridge, 1200 long, supported at both ends. Keep the Z backplate close to the X carriage and supported over a broad area. Adapter and head plates remain un-drilled until the actual modules, clamp and fastener depths are checked.',10.5)

heading(805,693,'C / BED CASSETTES','Dry routing / wet plasma')
rect(821,544,282,9,LIGHT,INK); rect(833,553,258,55,ALU,INK)
for x in [849,881,913,945,977,1009,1041,1073]: rect(x,574,3,42,LIGHT,INK)
text(821,635,'Plasma: steel pan + replaceable slats',11,INK,True)
rect(821,401,282,9,LIGHT,INK); rect(833,410,258,42,STEEL,INK); rect(833,452,258,14,GOLD,INK)
text(821,489,'Wood: rigid cassette + surfaced spoilboard',11,INK,True)
para(805,363,326,'Three cross-bearers carry either bed. Use a bolted steel grid under an 18-25 mm spoilboard, with cross-ribs at about 250 mm centers. Fix the grid to all three bearers. Set the work plane with positive hole locations, then surface the spoilboard.',10.5)

line(50,257,1140,257,LINE)
text(50,234,'FABRICATION AND ALIGNMENT',11,RAIL,True)
items=[
 ('1  Weld and cap','Tack square, check diagonals, fit side/rear braces, alternate welds and cool. Add accessible fill and drain plugs to each enclosed tube cavity.'),
 ('2  Fill and level','Finish all welding before adding clean, completely dry sand. Main tubes hold about 29 L / 47 kg. Level all six feet without jacking the center legs into the rail plane.'),
 ('3  Align and mount','Shim caps coplanar; align one reference Y and then the other parallel. Fit the bridge without forcing the carriages. Use independent Y homing switches.'),
 ('4  Prove the tool sweep','Set Z/head height and bed level using actual tooling. Check travel, spindle/torch clearance, dust shoe and cable bends before final drilling and powered operation.')]
for i,(a,b) in enumerate(items):
    x=50+i*278; text(x,211,a,11,INK,True); para(x,196,254,b,10)
C.showPage()

page(4,'Material schedule and the CNC completion checks','Preliminary cut schedule for the chosen geometry  |  Exact rail and spindle interfaces remain pending')
text(50,696,'CHASSIS AND MOUNTING MATERIAL',12,INK,True)
tx=50; ty=674; widths=[35,104,219,279]
headers=['Qty','Length / size','Part','Material / note']
rows=[
 ['2','1450','Top side beams','2 x 2 x 0.120 in steel tube'],
 ['6','829.2','Legs','Same tube; nominal 50 foot allowance'],
 ['4','648.8','Lower side ties','Same tube; fit between six legs'],
 ['4','1048.4','End ties: 2 low + 2 high','Same tube; upper ties top at 730'],
 ['3','1032.4*','Removable bed bearers','Same tube + 8 mm end plates'],
 ['5','Fit on assembly','Four side / one rear brace','30 x 30 x 3 angle; allow ~4.5 m'],
 ['2','1450 x 100 x 8','Rail mounting caps','Steel; holes pending'],
 ['1','1200','Gantry backing beam','8080 extrusion; supplier I / mass needed'],
 ['2 + 2','100 x 120 / 110 x 113','Saddles / upright cheeks','12 mm aluminum blanks; holes pending'],
 ['4','~80 x 80 triangles','Gantry gussets','6 mm aluminum; fit connections'],
 ['6','~80 x 200 x 6','Bed hanger blanks','Steel; positive height-location holes'],
 ['1','1000 x 1200 x 100','Pan outside envelope','2-3 mm steel; drain + leak test'],
 ['19','~960 x 75 x 3','Replaceable slat blanks','Steel; combs set top at 850'],
 ['6','Select for total load','Leveling feet','Cap feet / locknuts / fill plugs extra'],
 ['1 set','Fit cassette','Woodworking bed','Steel grid + 18-25 mm spoilboard']]
xx=tx
for wi,he in zip(widths,headers): rect(xx,ty-22,wi,22,INK,None);text(xx+5,ty-15,he,9,white,True);xx+=wi
ty-=22
for ri,row in enumerate(rows):
    xx=tx
    for wi,cell in zip(widths,row):
        rect(xx,ty-27,wi,27,PAPER if ri%2==0 else white,None)
        text(xx+5,ty-17,cell,8.6,INK);xx+=wi
    ty-=27
para(50,ty-12,634,'*1032.4 + two 8 mm end plates = 1048.4 clear span; leave fitting clearance as required. Welded chassis: 14.664 m of tube; about 67 kg steel + 47 kg sand. Add about 3.10 m for bearers, plus stock allowance. Estimates exclude caps, beds, motion and fluids.',9.5,MUTED)
text(50,169,'EXACT PARTS / PRIMARY SOURCES',10,RAIL,True)
sources=[
 ('2 x Y: HMS40, 1000 mm stroke / 10 mm lead - B0C7GN24S1','https://www.amazon.com/dp/B0C7GN24S1'),
 ('1 x X: HMS40, 800 mm stroke / 10 mm lead - B0C7GQTRRX','https://www.amazon.com/dp/B0C7GQTRRX'),
 ('1 x Z: RATTMMOTOR ZBX80, 100 mm - B09MVYGLNQ','https://www.amazon.com/dp/B09MVYGLNQ'),
 ('KHMOS HMS40 maker data: loads, moments and nominal envelope','https://www.khmos.com/high-performance-easy-access/hms40')]
for i,(lab,url) in enumerate(sources):
    yy=149-i*19; text(50,yy,lab,9.2,RAIL); C.linkURL(url,(50,yy-2,692,yy+11),relative=0)
text(50,66,'Sources checked 24 Sep 2026. Nominal dimensions and interfaces require supplier confirmation.',8.5,MUTED)

rx=738
text(rx,696,'TO FINISH THE CNC BUILD',12,INK,True)
y=675
for title,body in [
 ('Use the selected screw modules','HMS40 is a ballscrew axis. The maker graphic gives stroke + 200 overall: about 1200 for Y and 1000 for X, including the motor. End allocations in this sketch are schematic.'),
 ('Keep the router head close','HMS40 maker data for 10 mm lead: 20 kg horizontal; moments MY 13 / MP 12 / MR 15 N.m. An 8 kg head at 100 mm offset already adds 7.85 N.m from gravity. Check combined moments and wall-mount data, not payload alone.'),
 ('Finish the spindle and Z interface','The selected ZBX80 has 100 mm travel, 80 mm width and about 330 mm overall length. ER17 does not identify the spindle diameter or length. Finalize the rigid plate and clamp after that model is known.'),
 ('Allow the proper controls','Four motion drivers: X, Y-left, Y-right and Z; independent Y homing, travel limits, E-stop, spindle/VFD interface and protected wiring. Plasma additionally needs torch firing, touch-off and suitable height control.'),
 ('Hold position and verify rigidity','Provide an appropriate brake/counterbalance against Z backdrive. Measure tool-to-bed movement under known forces at maximum reach, verify homing/squareness, then establish wood feeds and depths by test cuts.'),
 ('Sand and bed loads are additional mass','Sand receives no bending-stiffness credit. A 60 mm fill in a 1.0 x 1.2 m pan adds about 72 kg water. Size the hangers, connections and feet for the entire machine, stock and fluids.')]:
    text(rx,y,title,11,INK,True); y=para(rx,y-11,400,body,10.1)-17
para(rx,97,400,'Remove the wood cassette and accumulated dust before plasma work. Keep leads supported, fit spark shields to the stand, and keep screw/guide protection clear through full travel.',9.7,MUTED)
C.save()
print(PDF)
assert abs((2*1450+6*829.2+4*648.8+4*1048.4)-14664)<1e-8
assert abs(1150-2*50.8-1048.4)<1e-8
assert abs(1124.6-25.4-1099.2)<1e-8
assert 775-100 == (75+1275)/2
assert abs(50+829.2+50.8-930)<1e-8
