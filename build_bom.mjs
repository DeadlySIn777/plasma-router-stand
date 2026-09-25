import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const here=path.dirname(fileURLToPath(import.meta.url));
const out=path.join(here,'outputs','alto-30510');
await fs.mkdir(out,{recursive:true});
const root=path.join(here,'output','bom');
const metals=JSON.parse(await fs.readFile(path.join(root,'metals_research.json'),'utf8'));
const stock=JSON.parse(await fs.readFile(path.join(root,'cut_stock_check.json'),'utf8'));
const wb=Workbook.create();
const summary=wb.worksheets.add('Budget');
const parts=wb.worksheets.add('Parts');
const ship=wb.worksheets.add('Shipping');
const cuts=wb.worksheets.add('Metal quotes');
const rows=[];
const amazon=asin=>'https://www.amazon.com/dp/'+asin;
const local='https://steelmartatlanta.com/steelmart-gainesville-ga/';
const carr='https://www.carrlane.com/product/locating-pins/locating-pins';
function add(id,scope,cat,item,qty,unit,price,basis,group,status,url,notes){
 rows.push({id,scope,cat,item,qty,unit,price,basis,group,status,url,notes});
}
const A=(id,cat,item,qty,price,asin,notes)=>add(id,'Common',cat,item,qty,'each',price,'Amazon offer','Amazon checked','Verify at checkout',amazon(asin),notes);
const L=(id,cat,item,qty,unit,price,notes)=>add(id,'Common',cat,item,qty,unit,price,'Allowance','Local metal','Quote required',local,notes);
const U=(id,cat,item,qty,unit,price,notes,url='')=>add(id,'Common',cat,item,qty,unit,price,'Allowance','Amazon unselected','Select exact part',url,notes);
A('M01','Motion','KHMOS HMS40 X, 800 mm stroke / 10 mm lead',1,236,'B0C7GQTRRX','User-selected ASIN. NEMA23 motor included. Free delivery displayed for Alto 30510. Do not assume promotional driver/switch inclusion.');
A('M02','Motion','KHMOS HMS40 Y, 1000 mm stroke / 10 mm lead',2,260,'B0C7GN24S1','Two independent Y drives for gantry squaring. Four units shown available at research time; availability can change.');
A('M03','Motion','RATTMMOTOR ZBX80 Z, 100 mm / SFU1605',1,112,'B09MVYGLNQ','Motor included. Current selected new offer supersedes the earlier $105 other-seller starting price. Coupon not deducted.');
L('S01','Frame and finish','2 x 2 x .120-inch steel tube, 20-foot bars',5,'bar',100,'Local allowance $500. Public raw-stock comparisons: $403 Looper, $487.50 Bobco, $1,011.50 Online Metals. See Metal quotes; freight is separate.');
L('S02','Router deck','1 x 1 x .083-inch panel tube, 60-inch blanks',9,'blank',15.58,'Local quote allowance anchored to Online Metals $15.58 per 60-inch piece. Use 12 cuts at 497 and 18 at 346.2 mm. US-stock adjustment is explicit.');
L('S03','Frame and finish','1-1/4 x 1-1/4 x 1/8-inch brace angle, 20 feet',1,'bar',30,'Near-size replacement for 30 x 30 x 3 mm angle. Five centerline lengths total 4.829 m. Final miters/attachment lengths to detail.');
L('S04','Frame and finish','Rail cap strips, 1450 x 100 x 5/16-inch',2,'blank',60,'Allowance for steel cut blanks. Final rail plane requires straightening/machining or shimming. Cap is 0.0625 mm thinner than the 8 mm concept.');
L('S05','Pan and slats','11-gauge steel sheet, 4 x 8 feet',2,'sheet',180,'One sheet allocation for pan; one for 19 slats plus spare stock. Raw-sheet benchmark $173.60 each. Confirm measured gauge; pan/slats need fabrication.');
L('S06','Frame and finish','Steel small-plate stock and cut blanks',1,'lot',140,'6 foot plates; 8 beam end diaphragms; 6 pan-bearer plates; pads, gussets, receiver plates, tube caps. Outlines/holes and any thickness substitutions need detailing.');
L('S07','Router deck','6061-T651 aluminum 5/16-inch plate, 48 x 48 inches',1,'sheet',600,'Local allowance $600, not a quote. Online Metals published $759.54 for this sheet. Six 497 x 397 blanks nest 2 x 3. Flatness/finish must be specified.');
L('S08','Frame and finish','5052 aluminum skin sheet, about .080 inch, 4 x 8 feet',1,'sheet',300,'Local allowance. Outside skins/lift-off covers only; raw-stock comparisons $254.64 for 4 x 10 ft at Looper and $510 for 4 x 8 ft at BCI.');
L('S09','Frame and finish','Internal rack supports, liners and wet-zone shields',1,'lot',160,'Front storage cabinet supports/liners only; reservoir cradle and leak tray are in W05. Light skins do not support the stored 100–110 kg deck. Preserve 1005 x 550 x 680 mm clear storage.');
L('S10','Motion','Gantry/head adapter plate material',1,'lot',90,'Aluminum stock for saddles, cheeks, gussets, two head plates and steel locating seats. Hole patterns and spindle/torch clearance remain to be finalized.');
add('S11','Common','Motion','80/20 standard 40-8080, 1200 mm cut',1,'each',151.73,'Posted price','80/20','Check payload and moment','https://8020.net/40-8080.html','Price = 1200 x $0.1231 + $4.01 cut. Standard section is about 7.64 kg; include that mass in dual-Y and X assembly checks.');
U('S12','Router deck','3/4-inch MDF, one 4 x 8-foot sheet',1,'sheet',55,'Local-store allowance; six panels plus spares. Actual nominal 19.05 mm. Surface after assembly. Delivery allowance is on Shipping.','https://www.homedepot.com/p/309177124');
U('S13','Frame and finish','Dry sand, 50-pound bags',3,'bag',12,'68 kg purchased covers the approximately 58 kg stationary-frame fill. Fill only after welding; provide access to each separate cavity.');
U('S14','Frame and finish','Primer, graphite finish and finishing consumables',1,'lot',100,'DIY paint allowance. Professional powder coating and user fabrication labor are excluded.');
L('S15','Frame and finish','Cutting, pan bending and datum-machining service',1,'lot',300,'Provisional outside-service allowance: stock cutting, pan bending and rail-cap datum finishing. Beam-seat finishing is only in H08. User welding labor/consumables excluded. Quote each service and delivery separately.');
add('H01','Common','Frame and finish','Carr Lane CLM-16-SLF M16 leveling feet',6,'each',23.72,'Posted price','Carr Lane','Check fit and stock','https://www.carrlane.com/product/leveling-feet/stud-leveling-feet/stud-leveling-feet/stud-leveling-feet-steel-zinc-plated/clm-16-slf','6 feet, load through reinforced base plates/thread blocks. Published foot capacity is not a machine load rating.');
U('H02','Frame and finish','M16 threaded blocks, jam nuts and base fastening',6,'set',8,'Do not rely on threads cut into the 0.120-inch tube wall. Plate stock is already in S06.');
add('H03','Common','Router deck','10 mm round locating pin, CLM-100-RP',10,'each',6.11,'Posted price','Carr Lane','Fit and stock pending','https://www.carrlane.com/product/locating-pins/locating-pins/round-diamond-pins/round-pins/clm-100-rp','Six panel pins plus four beam pins as a budget candidate; beam interfaces may need a different size. Price page also displays a status error.');
add('H04','Common','Router deck','10 mm diamond locating pin, CLM-100-DPY',10,'each',11.55,'Posted price','Carr Lane','Fit and stock pending','https://www.carrlane.com/product/locating-pins/locating-pins/round-diamond-pins/diamond-pins/clm-100-dpy','One per round-pin pair. Locate and orient the relief correctly; final bushing and receiver drawings pending.');
U('H05','Router deck','Hardened locating bushings',20,'each',7,'12 for panels and 8 for beams. Match pin fits and required engagement; price allowance.',carr);
U('H06','Router deck','Panel datum pads plus auxiliary supports',6,'set',15,'Per panel: 3 primary pads + 1 preset auxiliary support. Includes 18 pads and 6 auxiliary supports total; hardware allowance.');
U('H07','Router deck','Captive M8 panel drawdowns, sleeves and access plugs',24,'set',8,'Four per panel, clamping through metal sleeves. Length/grade/plain neck and threaded engagement need final detail. Full set allowance, no duplicate screws.');
U('H08','Router deck','Beam riser and docking seat finishing/hardware',8,'set',15,'Eight 30 mm riser feet and eight fixed contact seats. Raw plate stock is in S06; only beam-seat finishing/hardware is here, excluded from S15. Exact riser construction unresolved.');
U('H09','Router deck','Captive beam clamps and receivers',8,'set',12,'Two per paired beam. Structural drawdown clamps, not light door latches. Exact clamp selection pending.');
U('H10','Router deck','Folding/recessed panel handles',12,'each',5,'Two per panel. Verify rated load, attachment and folded storage clearance.');
U('H11','Router deck','Deck assembly and MDF retention fasteners',1,'lot',40,'Allow 48 frame-to-Al and 36 recessed MDF screws, plus washers/inserts. Separate from 24 panel drawdowns.');
U('H12','Frame and finish','Lift-off cover latches, hooks and parking studs',1,'lot',45,'Four captive latches, four lower hooks and four parking studs, nominal. Keep covers within existing footprint when parked.');
U('H13','Frame and finish','Sand-port closures, datum covers and seals',1,'lot',45,'Final port count follows sealed cavity drawing. No sand in removable crossbeams, panel frames or moving gantry.');
U('H14','Motion','Rail mounting hardware, T-nuts and shim pack',1,'lot',60,'Exact HMS mounting pattern and 80/20 slot fasteners to verify. Includes initial rail-plane adjustment materials.');
add('E01','Common','Controls','Kraken onboard TMC2160 channels, included in E07',4,'channel',0,'Included','None','No external drivers','https://global.bttwiki.com/Kraken.html','Use S1-S4 for X/Y1/Y2/Z. Eight drivers included with Kraken; no separate DM556T purchase. Confirm actual motor current and cooling before setting current.');
A('E02','Controls','MEAN WELL LRS-350-36 motor supply',1,36.07,'B071HSNP83','36 V / 350 W candidate for Kraken HV motor input only, never DCIN. Board DCIN uses 24 V from E03. Final current, acceleration and regeneration margin need load test.');
A('E03','Controls','MEAN WELL LRS-150-24 auxiliary supply',1,23.50,'B018RE4CWW','24 V / 150 W candidate for sensors, interlocks and water controls. Pump start-current capacity must be checked if pump option chosen.');
add('E04','Common','Controls','Separate 5 V logic supply, no longer selected',0,'each',11.53,'Amazon offer','None','Not required in proposed route',amazon('B019GUOV40'),'Kraken has a regulated 5 V host-power output. Verify cable/power budget for CB1+Pi4B. Zero quantity and no freight; do not buy a second host supply by default.');
A('E05','Controls','VEVOR steel electrical enclosure 20 x 16 x 8 in',1,84.90,'B0924BN1P5','One unit shown available. Verify backplate, gland entries and actual usable space. Keep VFD wiring segregated; may require separate VFD enclosure.');
A('E06','Controls','Enclosed cable chain 25 x 50 mm, R55, 1 metre',2,29.99,'B0DSPK5X4V','Candidate X/Y carriers. Confirm cable fill, bend radius and travel-end geometry; add metal spark shields separately.');
add('E07','Common','Controls','BIGTREETECH Kraken V1.1 with 8 integrated drivers',1,'each',129.99,'Posted price','BIQU','Preferred hardware; firmware open','https://biqu.equipment/products/kraken-for-voron-phoenix','Official price; Amazon V1.1 ASIN B0F7RQY6Z4 unavailable. S1-S4 max 4.7 A for V1.1, not the V1.0 8 A claim. HV24-60 V and DCIN12/24 V are separate. Does not accept CB1 directly.');
U('E08','Controls','Plasma height-control interface, unresolved provision',1,'set',79,'Inherited interface budget only, not a selected THC solution. THCAD2 is no longer assumed compatible. Firmware, isolated arc feedback and actual cutter remain unresolved; required development is unpriced.');
U('E09','Controls','Additional isolated I/O, unresolved provision',1,'set',79,'Replaces the Mesa 7I84U selection. Input count, isolation and firmware support must be designed for Kraken or Manta; board GPIO is not automatically 24 V tolerant.');
U('E10','Controls','Axis home/limit sensors with brackets',6,'each',8,'Four independent homes including Y1/Y2; two spare/end-limit candidates. Final circuit and combined limit scheme pending.');
U('E11','Controls','Docking/head identification sensors and targets',16,'each',6,'Budget: 8 beam-clamp channels, 6 deck-presence channels, 2 head-ID channels. Engagement sensing does not prove clamp preload.');
U('E12','Controls','E-stop, reset and mode-control station',1,'set',40,'Latching NC E-stop, deliberate reset and mode selector. Exact hardware and wiring pending.');
U('E13','Controls','Contactors, interlock relay and branch protection',1,'lot',160,'Supply isolation, fuses, EMC filter and machine interlock relay only. Dedicated water output/HH/LL relays are in W06. Final electrical design required.');
U('E14','Controls','Shielded motor/IO cable, grounding and connectors',1,'lot',150,'Provisional lengths: about 25–30 m motor cable, 25–30 m signal cable. VFD cable already in spindle kit. Final wire gauges/routes determine purchase.');
U('E15','Controls','DIN rail, terminals, glands and ferrules',1,'lot',65,'Allowance for complete cabinet termination and service labeling.');
U('E16','Controls','Cabinet cooling and segregated VFD housing',1,'lot',75,'Filter fan/vents and separate VFD mounting allowance. Final thermal and space check pending.');
U('E17','Controls','Host USB/Ethernet cables and strain reliefs',1,'lot',18,'CB1/Pi4B to Kraken USB data link, host network cable and restraints. Kraken Ethernet motion control is not assumed.');
add('E18','Common','Controls','CNC firmware and live plasma THC integration',1,'project',0,'Unpriced','None','Development not priced','https://global.bttwiki.com/Kraken.html','Stock Klipper/Marlin support is established; ready plasma THC is not. No verified Kraken grblHAL map. Zero records no software license purchase, not zero development cost or completed integration.');
add('E19','Common','Controls','BIGTREETECH CB1 V2.2 host module',1,'each',32.99,'User screenshot','Amazon screenshot','Cart price; checkout pending','https://github.com/bigtreetech/CB1','User screenshot price $32.99 and Prime free-delivery badge. Exact ASIN and delivery ZIP are not visible. Kraken needs the separate Pi4B carrier E20; Manta accepts CB1 directly.');
add('E20','Common','Controls','BIGTREETECH Pi4B V1.0 carrier only',1,'each',28.98,'Posted price','BIQU','Kraken host carrier','https://biqu.equipment/products/pi4b-adapter-v1-0?variant=39919128969314','Carrier-only price; CB1 is already in E19. Connect the host to Kraken by USB. Omit carrier if Manta alternative is selected.');
U('E21','Controls','Host microSD media, heatsink and fan',1,'set',25,'CB1 storage, firmware microSD and host cooling allowance. No display included; reuse a network browser device for a Klipper UI.');
U('E22','Controls','Isolated VFD speed and run interface',1,'set',35,'Replaces the analog spindle output previously provided by Mesa. Match VFD PWM-to-0-10 V or documented serial interface and run contact. Exact module and firmware remain to be selected.');
A('R01','Router head','Zhong Hua Jiang 110 V / 1.5 kW spindle kit, ER11',1,309.99,'B0BF5R3LNC','Latest user ASIN controls: ER11, 65 mm, 2.7 kg. Includes VFD, clamp, wires, wrenches and 1/4, 1/8, 1/16-inch collets. No second VFD/clamp charge.');
U('R02','Router head','Dust shoe and extraction hose',1,'set',65,'Choose for the actual 65 mm spindle/tool length. Shop dust extractor is a separate prerequisite if unavailable; see X04.');
U('R03','Router head','Starter cutters, surfacing tool and workholding',1,'lot',90,'ER11 shank compatibility, low-profile clamps and screw-down fixtures. No 1/2-inch-shank bits.');
U('R04','Router head','Touch plate / tool-height probe',1,'each',25,'Verify isolated input and controller configuration.');
U('R05','Router head','Z anti-drop support/brake provision',1,'set',70,'Ball screw can backdrive. Exact counterbalance/brake depends on head mass and mounting clearance.');
U('P01','Plasma interface','Torch floating touch-off / breakaway mount',1,'set',90,'Mounting the owned straight torch does not provide touch-off or THC. Rigid indexed router mount remains separate.');
U('P02','Plasma interface','Isolated torch-start / arc interface and cable',1,'set',85,'Torch-start isolation and cutter cabling/accessories only; sensing hardware provision is E08. Actual cutter and HF immunity unresolved. Neither printer board is a direct plasma-voltage interface.');
U('P03','Plasma interface','Torch lead support, shield and work-return lug',1,'set',40,'Keep torch cable drag off the Z. Protect modules and provide dedicated work-return path.');
U('W01','Water common','Cleanable liquid level sensors',5,'channel',25,'Allowance only: pan low/normal/HH and tank LL/HH. The 100 mm pan and 10 mm normal-to-overflow band require actual hysteresis/position checks.');
U('W02','Water common','Sensor guards, brackets and bosses',1,'lot',45,'Mounting pockets must be accessible and keep slag away. Independent overflow remains separate.');
U('W03','Water common','1.5-inch water transfer and overflow hose',10,'foot',5,'Preliminary length. Separate continuously falling drain/overflow routes with cleanouts. Actual hose media, heat and pressure ratings to select.');
U('W04','Water common','Bulkheads, cleanouts, unions, clamps and basket',1,'lot',130,'Includes coarse pan catch and independent overflow fittings. Raw pan sheet in S05. Final thread sizes and counts depend on selected water option.');
U('W05','Water common','Reservoir supports, leak tray and heat shield',1,'lot',70,'Rear reservoir bay only: cradle, leak tray and shield materials. Front storage supports/liners are in S09. Support full water weight without consuming the front bed-storage space.');
U('W06','Water common','Water-control relays, tubing and fittings',1,'lot',50,'Dedicated water output and independent HH/LL trip relays, plus small control fittings. Excluded from E13; main DIN terminals are in E15. No automatic machining restart.');
add('Q01','Air option','Water chamber','Purpose-designed low-pressure displacement chamber',1,'assembly',700,'Allowance','Air fabrication','Pressure and fit quote','','Not the vented tank with its lid sealed. Reserve >=125 L usable return capacity in the rear bay. Pressure rating, reinforcement, cleanout and relief sizing need supplier engineering.');
add('Q02','Air option','Air controls','Low-pressure regulator, gauge and relief package',1,'set',150,'Allowance','Air components','Select matched ratings','','Regulator range and relief capacity must suit the rated chamber and restricted inlet. About 0.9 psi ideal static head is not an operating setpoint or vessel rating.');
add('Q03','Air option','Air controls','Air isolation, restrictor, exhaust and connections',1,'set',75,'Allowance','Air components','Valve models pending','','Use known fail states and manual vent. Existing solenoids are owned but voltage, ports and minimum operating pressure need verification.');
add('Q04','Air option','Air controls','Solenoid replacement contingency',1,'set',60,'Allowance','Air components','Conditional allowance','','Reserve only until owned valves prove suitable; set quantity to zero once compatible parts are assigned. Venturi is not required for positive-pressure fill/gravity drain.');
add('D01','Pump option','Water reservoir','Vented 157.5 L gross reservoir with baffle/cleanout',1,'assembly',350,'Allowance','Pump fabrication','Tank fit quote','https://www.tank-mart.com/fabricated-tanks/','900 x 500 x 350 mm INTERNAL concept; actual outside envelope and minimum125 L usable capacity need a custom quote. Never pressurize this tank.');
add('D02','Pump option','Water valve','U.S. Solid JFMSV90024 1-inch motorized valve',1,'each',207.99,'Posted price','US Solid','Dirty-water validation','https://ussolid.com/products/1-in-brass-motorized-ball-valve-fast-2-second-12-24-v-dc-24-v-ac-5-wire-auto-return-normally-closed-full-port-ip68-manual-override','12–24 VDC; full-port brass; manual override; open and closed feedback; normally closed on power loss. Chemical/fines compatibility unresolved.');
add('D03','Pump option','Water pump','Whale Gulper 320 BP2054, 24 V',1,'each',204.19,'Posted price','Neobits','Confirm indexed price','https://www.neobits.com/whale_bp2054_gulper_320_24v_retail_each__p24302101.html','Indexed seller price; confirm current offer/stock at checkout. Clarified-water refill candidate, not raw abrasive slurry. Head/flow, motor starting current and shipping remain unverified.');
add('D04','Pump option','Water plumbing','1-inch pump hose, strainer and air-gap return',1,'set',65,'Allowance','Pump components','Select exact fittings','','Suction/discharge length, service unions and clarified pickup. Separate from gravity return/overflow.');
add('O01','Owned','Existing equipment','12 CFM compressor',1,'each',0,'Owned','None','Verify rated delivery','','User-reported. Verify delivered CFM at required pressure. No new compressor is included in either water-option total.');
add('O02','Owned','Existing equipment','CV-15HS venturi vacuum generator',1,'each',0,'Owned','None','Confirm manufacturer','https://shop.convum.com/products/200100006','CONVUM reference:100 L/min air at0.5 MPa;63 L/min suction. User brand not confirmed. Reserve for sealed vacuum fixtures; no dirty-water flow through generator.');
add('O03','Owned','Existing equipment','Existing solenoid valves',1,'lot',0,'Owned','None','Voltage/ports unknown','','Counted as owned. Exact quantity/model/coil voltage and minimum pressure not provided; Q04 is conditional replacement allowance.');
add('O04','Owned','Existing equipment','Existing AG60/SG55-style straight torch',1,'each',0,'Owned','None','Exact model pending',amazon('B07B8CWGB5'),'User has something similar. Reference is a torch body, not complete THC or proof of cutter compatibility. No replacement torch is charged.');
add('X01','Optional','Plasma replacement','Bestarc BTC500XP 11GEN non-HF CNC cutter',1,'each',399.99,'Posted price','Optional Bestarc','Replacement proposal','https://www.bestarc.com/products/btc500xp-11gen-cnc-plasma-cutter','Optional comparison only. Non-HF, CNC control ports; 1:1 arc output is raw voltage. Owned AG60-style head is not assumed compatible. Free shipping advertised, checkout pending.');
add('X02','Optional','Plasma replacement','IPTM60 20-foot machine torch',1,'each',159,'Posted price','Optional Bestarc','Verify cutter connection','https://www.bestarc.com/products/btc500xp-11gen-cnc-plasma-cutter','Optional with compatible non-HF cutter; separately sold. Do not add unless replacing the current torch/cutter arrangement.');
add('X03','Optional','Shop equipment','Separate host PC, no longer selected',0,'set',250,'Allowance','None','CB1 host budgeted in E19','','CB1+carrier replaces the previous LinuxCNC host proposal. A network browser device is assumed available; a local monitor/control screen remains unpriced if wanted.');
add('X04','Optional','Shop equipment','Wood dust extractor and fine filtration',1,'set',250,'Allowance','Optional equipment','Needed if none available','','Separate from R02 shoe/hose. Not a plasma fume extractor.');
add('X05','Optional','Shop equipment','Plasma fume extraction and clean dry air treatment',1,'set',350,'Allowance','Optional equipment','Shop-dependent quote','','Provisional allowance only; actual airflow, duct route and filtration require shop-specific selection. Water pan does not replace fume management.');
add('C01','Manta alternative','Controls','BIGTREETECH Manta M5P V1.0',1,'each',59.99,'User screenshot','Manta alternative','Alternative, excluded from totals','https://github.com/bigtreetech/Manta-M5P','User screenshot price. Substitute for E07 Kraken and omit E20 Pi4B. Keep E19 CB1. Four separate channels; the two Motor3 connectors are one shared driver. Live plasma THC remains unresolved.');
add('C02','Manta alternative','Controls','TMC5160T Pro plug-in SPI modules, four-pack',1,'pack',66.84,'Posted price','Manta alternative','Alternative, excluded from totals','https://biqu.equipment/products/tmc5160-pro-v1-0?variant=40301980647522','Four modules fit on the motherboard; no external driver boxes. Standard StepStick format, not EZ or the large Plus modules. Exact module current/cooling and motor ratings must be matched.');

const groups=[
 ['Amazon checked','Common','Amazon selected offers',0,null,'Alto 30510 delivery shown','Free delivery; small items require qualifying Amazon basket. No Prime-only or coupon discounts counted.'],
 ['5V seller','Common','Former 5 V supply, not selected',0,null,'No purchase','Separate 5 V supply has zero quantity; former $2.44 delivery removed.'],
 ['Amazon unselected','Common','Amazon first, exact SKUs pending',null,75,'Allowance','Freight reserve for unselected hardware; not a carrier quote. MDF/sand may be bought locally.'],
 ['Local metal','Common','SteelMart Gainesville quote route',null,250,'Quote required','Delivery/unloading must be quoted for Alto. Raw stock/cutting/service allowances are in Parts; delivery here only.'],
 ['80/20','Common','80/20 direct',null,40,'Quote required','1200 mm standard extrusion; actual parcel shipping at checkout.'],
 ['Carr Lane','Common','Carr Lane or distributor',null,30,'Quote required','Consolidated feet/pins order; stock and shipment terms pending.'],
 ['BIQU','Common','BIQU official store',null,25,'Advertised free; unverified','Kraken+Pi4B: store advertises free shipping $59+, but Alto checkout is unverified. Reserve retained pending destination quote.'],
 ['Amazon screenshot','Common','User Amazon cart, CB1',null,10,'Screenshot Prime badge','CB1 price and Prime free shipping are shown by user; exact ASIN/destination not visible. Reserve pending checkout confirmation.'],
 ['Manta alternative','Alternative','Amazon screenshot + BIQU',null,0,'Excluded alternative','Parts C01-C02 are mutually exclusive with Kraken/carrier. Shipping for this alternate is unquoted; zero reserve here is not free delivery.'],
 ['Air fabrication','Air option','Pressure-chamber fabricator',null,100,'Quote required','Separate pressure-qualified fabrication/fit quote. Not part of the vented-reservoir quote.'],
 ['Air components','Air option','Amazon first, exact parts pending',null,35,'Allowance','Regulator/relief, restrictor and any replacement valves. Existing parts have no new freight.'],
 ['Pump fabrication','Pump option','Vented tank fabricator',null,80,'Quote required','Tank freight reserve; not delivery promise.'],
 ['US Solid','Pump option','U.S. Solid direct',null,20,'Quote required','Shipping amount not verified. Do not assume a free-shipping badge applies.'],
 ['Neobits','Pump option','Neobits BP2054 pump',null,25,'Quote required','Stock and shipping require checkout.'],
 ['Pump components','Pump option','Amazon first',null,15,'Allowance','Pump hose/fittings shipping reserve.'],
 ['Optional Bestarc','Optional','Bestarc direct',null,30,'Advertised free; unverified','Free shipping advertised but not destination-validated; retain reserve until checkout.'],
 ['Optional equipment','Optional','Unselected shop suppliers',null,100,'Allowance','Dust/fume equipment and air treatment: exact basket unknown. Separate host PC quantity is zero.'],
 ['None','Owned','Already owned / free software',0,null,'No shipment','Owned equipment is not a new purchase.']
];
const end=rows.length+5;
const vals=rows.map(r=>[r.id,r.scope,r.cat,r.item,r.qty,r.unit,r.price,r.basis,null,r.group,r.status,null,r.url,r.notes]);
parts.getRange('A5:N'+end).values=[['ID','Scope','Assembly','Part / purchase size','Qty','Unit','Unit USD','Price basis','Goods USD','Shipment group','Selection status','','Source URL','Fit / inclusion / price notes'],...vals];
parts.getRange('I6').formulas=[['=E6*G6']];
parts.getRange('I6:I'+end).fillDown();
rows.forEach((r,i)=>{if(r.url)parts.getRange('M'+(i+6)).values=[[r.url]];});
parts.getRange('A2').values=[['Bill of materials']];
parts.getRange('A3').values=[['Rev C geometry with explicit US-stock adjustments. Prices checked September 24, 2026. USD. Tax excluded.']];
parts.freezePanes.freezeRows(5);parts.freezePanes.freezeColumns(4);
parts.tables.add('A5:K'+end,true,'PartsList');
parts.getRange('G6:G'+end).format.font={color:'#1565C0'};
parts.getRange('G6:I'+end).setNumberFormat('$#,##0.00;($#,##0.00);$0.00');

ship.getRange('A2').values=[['Shipping to Alto, GA 30510']];
ship.getRange('A3').values=[['Quoted shipping and reserves are separate. Unknown freight is never silently treated as free.']];
ship.getRange('A5:J'+(5+groups.length)).values=[['Shipment group','Scope','Supplier','Goods USD','Quoted ship USD','Ship reserve USD','Ship used USD','Budget incl. ship','Shipping basis','Conditions'],...groups.map(g=>[g[0],g[1],g[2],null,g[3],g[4],null,null,g[5],g[6]])];
for(let i=0;i<groups.length;i++){
 const n=i+6;
 ship.getRange('D'+n).formulas=[['=SUMIFS(Parts!$I$6:$I$'+end+',Parts!$J$6:$J$'+end+',A'+n+')']];
 ship.getRange('G'+n).formulas=[['=IF(ISNUMBER(E'+n+'),E'+n+',F'+n+')']];
 ship.getRange('H'+n).formulas=[['=D'+n+'+G'+n]];
}
ship.getRange('D6:H'+(5+groups.length)).setNumberFormat('$#,##0.00;($#,##0.00);$0.00');
ship.getRange('E6:F'+(5+groups.length)).format.font={color:'#1565C0'};
ship.freezePanes.freezeRows(5);
ship.tables.add('A5:J'+(5+groups.length),true,'ShipmentList');

summary.getRange('A2').values=[['CNC / plasma table purchase budget']];
summary.getRange('A3').values=[['Alto, Georgia 30510 • USD • September 24, 2026 • estimates include shipping reserves, exclude sales tax']];
summary.getRange('A5:F5').values=[['Common build','Observed prices USD','Allowances USD','Goods USD','', 'Notes']];
const cats=[...new Set(rows.filter(r=>r.scope==='Common').map(r=>r.cat))];
cats.forEach((cat,i)=>{
 const n=i+6;
 summary.getRange('A'+n).values=[[cat]];
 summary.getRange('B'+n).formulas=[['=SUMIFS(Parts!$I$6:$I$'+end+',Parts!$C$6:$C$'+end+',A'+n+',Parts!$B$6:$B$'+end+',"Common",Parts!$H$6:$H$'+end+',"Amazon offer")+SUMIFS(Parts!$I$6:$I$'+end+',Parts!$C$6:$C$'+end+',A'+n+',Parts!$B$6:$B$'+end+',"Common",Parts!$H$6:$H$'+end+',"Posted price")+SUMIFS(Parts!$I$6:$I$'+end+',Parts!$C$6:$C$'+end+',A'+n+',Parts!$B$6:$B$'+end+',"Common",Parts!$H$6:$H$'+end+',"Out of stock")']];
 summary.getRange('C'+n).formulas=[['=SUMIFS(Parts!$I$6:$I$'+end+',Parts!$C$6:$C$'+end+',A'+n+',Parts!$B$6:$B$'+end+',"Common",Parts!$H$6:$H$'+end+',"Allowance")']];
 const observed=summary.getRange('B'+n).formulas[0][0];
 summary.getRange('B'+n).formulas=[[observed+'+SUMIFS(Parts!$I$6:$I$'+end+',Parts!$C$6:$C$'+end+',A'+n+',Parts!$B$6:$B$'+end+',"Common",Parts!$H$6:$H$'+end+',"User screenshot")']];
 summary.getRange('D'+n).formulas=[['=SUM(B'+n+':C'+n+')']];
});
const totalrow=6+cats.length;
summary.getRange('A'+totalrow).values=[['Common goods subtotal']];
summary.getRange('B'+totalrow+':D'+totalrow).formulas=[['=SUM(B6:B'+(totalrow-1)+')','=SUM(C6:C'+(totalrow-1)+')','=SUM(D6:D'+(totalrow-1)+')']];
const head=totalrow+3;
summary.getRange('A'+head+':D'+head).values=[['Build route','Goods USD','Shipping USD','Planning total USD']];
for(const [scope,offset,label] of [['Air option',1,'Common + pneumatic water'],['Pump option',2,'Common + electric pump water']]){
 const n=head+offset;
 summary.getRange('A'+n).values=[[label]];
 summary.getRange('B'+n).formulas=[['=D'+totalrow+'+SUMIFS(Parts!$I$6:$I$'+end+',Parts!$B$6:$B$'+end+',"'+scope+'")']];
 summary.getRange('C'+n).formulas=[['=SUMIFS(Shipping!$G$6:$G$'+(5+groups.length)+',Shipping!$B$6:$B$'+(5+groups.length)+',"Common")+SUMIFS(Shipping!$G$6:$G$'+(5+groups.length)+',Shipping!$B$6:$B$'+(5+groups.length)+',"'+scope+'")']];
 summary.getRange('D'+n).formulas=[['=SUM(B'+n+':C'+n+')']];
}
summary.getRange('A'+(head+4)).values=[['Shipping actually shown to Alto']];
summary.getRange('A'+(head+3)).values=[['Verified Amazon basket with shipping']];
summary.getRange('D'+(head+3)).formulas=[['=SUM(Shipping!H6:H7)']];
summary.getRange('D'+(head+4)).formulas=[['=SUM(Shipping!E6:E7)']];
summary.getRange('A'+(head+5)).values=[['Replacement / required shop equipment']];
summary.getRange('D'+(head+5)).formulas=[['=SUMIFS(Shipping!$H$6:$H$'+(5+groups.length)+',Shipping!$B$6:$B$'+(5+groups.length)+',"Optional")']];
summary.getRange('A'+(head+7)).values=[['Both build-route totals are estimates, not fully quoted delivered prices.']];
summary.getRange('A'+(head+8)).values=[['CB1 host is included. Browser device assumed available; extraction and any replacement cutter remain separate.']];
summary.getRange('A'+(head+9)).values=[['DIY welding and assembly labor, tax, fabrication tools and shop electrical installation are excluded.']];
summary.getRange('A'+(head+10)).values=[['Air route: pressure-qualified chamber and suitable controls must be engineered/quoted; do not pressurize the vented tank.']];
summary.getRange('A'+(head+11)).values=[['Pump route: vented tank, motorized drain and pump remain the Rev C baseline; sludge/media compatibility is pending.']];
summary.getRange('A'+(head+12)).values=[['CNC release open: Kraken/Manta live THC firmware is unpriced/unverified; cutter, motor ratings, geometry and I/O also require checks.']];
summary.getRange('F6').values=[['Exact Amazon motion set: $868 with free delivery shown to Alto; no motors added twice.']];
summary.getRange('F8').values=[['Spindle ASIN B0BF5R3LNC is ER11 at $309.99. VFD, clamp and cable are included.']];
summary.getRange('F10').values=[['Main steel purchase: 5 x 20 ft. Verified nesting covers 29 parts with 3 mm kerf and 10 mm trim/bar.']];
summary.getRange('F12').values=[['Owned: 12 CFM compressor, CV-15HS vacuum generator, solenoids and a similar straight torch.']];
summary.getRange('F14').values=[['Kraken V1.1 + CB1 + Pi4B: $191.96 hardware. Manta + CB1 + four plug-in drivers: $159.82 alternative. Firmware/THC is unresolved; no external motor drivers.']];
summary.getRange('F16').values=[['Pneumatic chamber estimate includes an unquoted $700 fabrication allowance. A compressor-driven diaphragm pump is another option; see the procurement brief.']];
summary.getRange('B6:D'+(head+5)).setNumberFormat('$#,##0.00;($#,##0.00);$0.00');

cuts.getRange('A2').values=[['Metal cut list and competing price references']];
cuts.getRange('A3').values=[['Request one consolidated local quote. Comparison rows below are alternatives; do not add them to the Parts total.']];
const takeoff=[
 ['Top Y supports','2 x 2 x .120 steel tube',2,1450,'mm','Fixed frame'],
 ['Receiver ledgers','2 x 2 x .120 steel tube',2,1450,'mm','Fixed frame'],
 ['Legs','2 x 2 x .120 steel tube',6,949.2,'mm','Fixed frame'],
 ['Lower side ties','2 x 2 x .120 steel tube',4,648.8,'mm','Fixed frame'],
 ['End ties','2 x 2 x .120 steel tube',4,1048.4,'mm','Fixed frame'],
 ['Pan bearer tubes','2 x 2 x .120 steel tube',3,1032.4,'mm','Before end plates/fit clearance'],
 ['Paired bridge blanks','2 x 2 x .120 steel tube',8,1032,'mm','8 blanks make 4 beam assemblies'],
 ['Panel long members','1 x 1 x .083 steel tube',12,497,'mm','US-stock procurement adjustment'],
 ['Panel inner members','1 x 1 x .083 steel tube',18,346.2,'mm','397 minus 2 x 25.4; replaces 347 mm'],
 ['Front side braces','1-1/4 x 1-1/4 x 1/8 angle',2,907.331,'mm','Centerline only; final miters/ends pending'],
 ['Rear side braces','1-1/4 x 1-1/4 x 1/8 angle',2,904.060,'mm','Centerline only; final miters/ends pending'],
 ['Rear brace','1-1/4 x 1-1/4 x 1/8 angle',1,1206.493,'mm','Centerline only; final miters/ends pending'],
 ['Rail cap plates','Steel, 1450 x 100 x 7.9375 mm',2,null,'blank','Measured thickness and final rail datum matter'],
 ['Al deck plates','6061-T651, 497 x 397 x 7.9375 mm',6,null,'blank','One 48 x 48-inch plate; 2 x 3 nesting'],
 ['MDF panels','497 x 397 x nominal19.05 mm',6,null,'blank','Measure then surface in position'],
 ['Beam diaphragms','101.6 x 50.8 x 6 mm steel',8,null,'blank','Keep exact6 mm or shorten tube if using1/4-inch plates'],
 ['Foot plates','80 x 80 x 12 mm steel',6,null,'blank','Foot hardware and thickness substitutions need detail'],
 ['Slats','880 x 75 x approximately3 mm steel',19,null,'blank','Measure sheet gauge; adjust comb-slot clearance'],
 ['Pan','920 x 1200 x100 outside, sloped floor',1,null,'assembly','About1% slope, cleanout and leak test; no brake pattern released'],
 ['Gantry beam','80/20 standard40-8080',1,1200,'mm','Moving mass about7.64 kg for extrusion alone']
];
cuts.getRange('A5:G'+(5+takeoff.length)).values=[['Part','Material / blank size','Qty','Cut mm','Net mm','Unit','Fabrication note'],...takeoff.map(x=>[x[0],x[1],x[2],x[3],null,x[4],x[5]])];
takeoff.forEach((x,i)=>{if(x[3]!==null)cuts.getRange('E'+(i+6)).formulas=[['=C'+(i+6)+'*D'+(i+6)]];});
let rn=takeoff.length+8;
cuts.getRange('A'+rn).values=[['Five-bar nesting: 6096 mm stock; 3 mm kerf per part; 10 mm total trim per bar']];
rn+=2;
cuts.getRange('A'+rn+':D'+rn).values=[['Bar','Finished cuts in mm','Net mm','Remainder mm']];
stock.main_20ft.bars.forEach((b,i)=>{cuts.getRange('A'+(rn+i+1)+':D'+(rn+i+1)).values=[[i+1,b.cuts_mm.join(' + '),b.net_mm,b.offcut_after_trim_kerf_mm]];});
rn+=8;
cuts.getRange('A'+rn).values=[['US-stock adjustments']];
const changes=[
 'Panel frame25.4 + Al7.9375 + MDF19.05 =52.3875 mm. Raw deck top becomes973.1875 mm before skim, using920.8 mm beam top.',
 'Rail cap5/16-inch =7.9375 mm,0.0625 below original8 mm. Establish actual rail plane with measured pads/shims.',
 'Keep 6 mm beam end plates, or with 1/4-inch plates use1031.3 mm tube blanks to preserve1044 mm overall. Do not mix both dimensions.',
 'If pan-bearer end plates become5/16-inch, tube nominal becomes1032.525 mm before fit clearance. Current1032.4 assumes8 mm plates.',
 'Do not claim sheet gauge is exactly3 mm. Size slat combs and water clearances from measured stock.',
 'Local alternatives: SteelMart Gainesville; Metal Supermarkets Buford; Cherokee Steel Monroe. Freight/cuts/tax must be separate on quotes.'
];
changes.forEach((s,i)=>cuts.getRange('A'+(rn+i+1)).values=[[s]]);
rn+=changes.length+3;
cuts.getRange('A'+rn).values=[['Published supplier comparisons — alternatives only, shipping unquoted']];
rn+=2;
cuts.getRange('A'+rn+':H'+rn).values=[['Supplier','Stock / purchase description','Qty','Unit USD','Goods USD','Match','Delivery / source notes','Source URL']];
metals.price_options.filter(x=>x.unit_price_usd!==null).forEach((p,i)=>{
 const n=rn+i+1;
 cuts.getRange('A'+n+':H'+n).values=[[p.supplier,p.description,p.purchase_quantity,p.unit_price_usd,null,p.match,p.notes,p.url]];
 cuts.getRange('E'+n).formulas=[['=C'+n+'*D'+n]];
 cuts.getRange('H'+n).values=[[p.url]];
});
const cutend=rn+metals.price_options.filter(x=>x.unit_price_usd!==null).length;
cuts.getRange('D'+(rn+1)+':E'+cutend).setNumberFormat('$#,##0.00');
cuts.freezePanes.freezeRows(5);

const C={ink:'#26323E',navy:'#253B50',pale:'#EEF2F5',amber:'#FFF1D4',red:'#FCE5E3',blue:'#1565C0'};
function base(s,range){
 s.showGridLines=false;
 const r=s.getRange(range);
 r.format.font={name:'Arial',size:10,color:C.ink};
 r.format.verticalAlignment='center';
 r.format.rowHeight=24;
 s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:C.ink};
 s.getRange('A2').format.rowHeight=32;
 s.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:'#5B6570'};
}
base(summary,'A1:I'+(head+14));base(parts,'A1:N'+end);base(ship,'A1:J'+(5+groups.length));base(cuts,'A1:H'+cutend);
function widths(s,ws){Object.entries(ws).forEach(([c,w])=>s.getRange(c+'1:'+c+'3').format.columnWidthPx=w);}
function hdr(s,r){s.getRange(r).format={fill:C.navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true,horizontalAlignment:'center',verticalAlignment:'center'};}
widths(summary,{A:270,B:145,C:130,D:155,E:24,F:510,G:30,H:30,I:30});
widths(parts,{A:55,B:105,C:145,D:350,E:48,F:64,G:96,H:110,I:105,J:135,K:160,L:20,M:510,N:570});
widths(ship,{A:145,B:100,C:230,D:110,E:110,F:110,G:110,H:125,I:180,J:530});
widths(cuts,{A:180,B:440,C:60,D:95,E:105,F:155,G:470,H:580});
hdr(summary,'A5:D5');hdr(summary,'A'+head+':D'+head);hdr(parts,'A5:K5');hdr(parts,'M5:N5');hdr(ship,'A5:J5');hdr(cuts,'A5:G5');hdr(cuts,'A'+rn+':H'+rn);
summary.getRange('F6:F16').format.wrapText=true;summary.getRange('F6:F16').format.rowHeight=38;
summary.getRange('A'+totalrow+':D'+totalrow).format.fill=C.pale;
summary.getRange('A'+totalrow+':D'+totalrow).format.font={bold:true};
summary.getRange('A'+(head+1)+':D'+(head+2)).format.rowHeight=34;
summary.getRange('D'+(head+1)+':D'+(head+2)).format={fill:C.amber,font:{bold:true,size:12}};
summary.getRange('A'+(head+7)+':A'+(head+12)).format.rowHeight=28;
parts.getRange('A6:N'+end).format.wrapText=true;parts.getRange('A6:N'+end).format.rowHeight=60;
parts.getRange('E6:F'+end).format.horizontalAlignment='center';
parts.getRange('M6:M'+end).format.font={name:'Arial',size:10,color:'#1565C0'};
parts.getRange('A6:K'+end).conditionalFormats.addCustom('=$H6="Allowance"',{fill:'#FFF7E6'});
parts.getRange('K6:K'+end).conditionalFormats.addCustom('=$H6="Out of stock"',{fill:C.red,font:{bold:true,color:'#A52720'}});
ship.getRange('A6:J'+(5+groups.length)).format.wrapText=true;ship.getRange('A6:J'+(5+groups.length)).format.rowHeight=58;
ship.getRange('E6:E'+(5+groups.length)).conditionalFormats.addCustom('=NOT(ISNUMBER(E6))',{fill:C.amber});
cuts.getRange('A6:H'+cutend).format.rowHeight=42;
cuts.getRange('C6:C'+(5+takeoff.length)).format.horizontalAlignment='center';
cuts.getRange('F6:F'+(5+takeoff.length)).format.horizontalAlignment='center';
cuts.getRange('B6:B'+(5+takeoff.length)).format.wrapText=true;cuts.getRange('G6:G'+cutend).format.wrapText=true;
cuts.getRange('A'+(rn+1)+':H'+cutend).format.wrapText=true;cuts.getRange('A'+(rn+1)+':H'+cutend).format.rowHeight=72;
cuts.getRange('H'+(rn+1)+':H'+cutend).format.font={color:'#1565C0'};
summary.tabColor=C.navy;parts.tabColor='#A6B5C1';ship.tabColor='#A6B5C1';

// Independent arithmetic and a representative input-change check.
const sum=(scope)=>rows.filter(r=>r.scope===scope).reduce((a,r)=>a+r.qty*r.price,0);
const freight=(scope)=>groups.filter(g=>g[1]===scope).reduce((a,g)=>a+(g[3]??g[4]??0),0);
const expected={
 common_goods:sum('Common'),air_goods:sum('Air option'),pump_goods:sum('Pump option'),
 common_shipping_budget:freight('Common'),air_shipping_budget:freight('Air option'),pump_shipping_budget:freight('Pump option'),
 air_total:sum('Common')+sum('Air option')+freight('Common')+freight('Air option'),
 pump_total:sum('Common')+sum('Pump option')+freight('Common')+freight('Pump option'),
 motion_delivered_before_tax:868,parts_count:rows.length
};
wb.recalculate();
const orig=parts.getRange('E6').values[0][0];
const before=summary.getRange('D'+(head+1)).values[0][0];
parts.getRange('E6').values=[[orig+1]];
const after=summary.getRange('D'+(head+1)).values[0][0];
if(Math.abs((after-before)-236)>0.001)throw new Error('Quantity change did not propagate');
parts.getRange('E6').values=[[orig]];
// Blank freight preserves the reserve; a real zero is accepted.
const testRow=8; const restore=ship.getRange('E'+testRow).values[0][0];
const reserve=ship.getRange('F'+testRow).values[0][0];
ship.getRange('E'+testRow).values=[[0]];
if(ship.getRange('G'+testRow).values[0][0]!==0)throw new Error('Zero freight not preserved');
ship.getRange('E'+testRow).values=[[restore]];
wb.recalculate();
if(Math.abs(ship.getRange('G'+testRow).values[0][0]-reserve)>0.001)throw new Error('Freight reserve failed');
const actualAir=summary.getRange('D'+(head+1)).values[0][0];
const actualPump=summary.getRange('D'+(head+2)).values[0][0];
if(Math.abs(actualAir-expected.air_total)>0.01||Math.abs(actualPump-expected.pump_total)>0.01)throw new Error('Summary reconciliation failed');
console.log(JSON.stringify(expected));
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},summary:'Final formula errors'});
console.log(errors.ndjson);
const inspect=await wb.inspect({kind:'table',range:'Budget!A'+head+':D'+(head+5),include:'values,formulas',tableMaxRows:7,tableMaxCols:4,maxChars:3500});
console.log(inspect.ndjson);
await fs.writeFile(path.join(out,'budget-checks.json'),JSON.stringify(expected,null,2));
const renders=[
 ['Budget','A1:F'+(head+5),'budget-preview.png'],
 ['Parts','A1:K15','parts-preview.png'],
 ['Parts','M5:N13','sources-preview.png'],
 ['Parts','A38:K49','controller-preview.png'],
 ['Parts','M38:N49','controller-notes-preview.png'],
 ['Shipping','A1:J13','shipping-preview.png'],
 ['Metal quotes','A1:G25','cuts-preview.png'],
 ['Metal quotes','A'+rn+':H'+Math.min(rn+7,cutend),'metal-prices-preview.png']
];
for(const [s,r,n]of renders){
 const p=await wb.render({sheetName:s,range:r,scale:1,format:'png'});
 await fs.writeFile(path.join(out,n),new Uint8Array(await p.arrayBuffer()));
}
const book=await SpreadsheetFile.exportXlsx(wb);
await book.save(path.join(out,'CNC-plasma-BOM-Alto.xlsx'));
await fs.writeFile(path.join(out,'bom-data.json'),JSON.stringify({rows,groups,expected},null,2));
console.log('SAVED '+path.join(out,'CNC-plasma-BOM-Alto.xlsx'));
