import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(dir,'../..');
const eng=path.join(root,'output/release-review/RevE-ENGINEERING');
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const purchases=await read(path.join(eng,'verified-purchases.json'));
const water=await read(path.join(eng,'water-bom.json'));
const old=await read(path.join(root,'outputs/alto-30510/bom-data.json'));
const tube=await read(path.join(eng,'tube-cut-plan.json'));
const rows=[];
function add(id,cat,item,qty,unit,price,basis,ship=null,url='',notes=''){
  rows.push({id,category:cat,item,quantity:qty,unit,unit_usd:price,basis,shipping_usd:ship,url,notes});
}
for(const p of purchases.items.filter(p=>p.id!=='W01')) {
  add(p.id,p.id.startsWith('M')?'Motion':p.id==='B01'?'Router bed':'Router head',p.item,p.qty,p.id==='B01'?'pack':'each',p.unit_price,'Observed',p.shipping,p.url,
    p.id==='M05'?'Both X rails and all four blocks used; no spare X rail.':p.use||p.included||p.interface_status||'Advertised offer to Alto 30510; no order placed.');
}
const metal='https://steelmartatlanta.com/steelmart-gainesville-ga/';
add('S01','Chassis','2 x 2 x .120 inch steel tube, full 20-foot bars',tube.stock_qty,'bar',100,'Allowance',null,metal,'Local quote target only. Public online alternatives are $155.15/bar at BlueSky or $200.75/bar at OnlineMetals, both before unquoted freight. See METAL-SOURCING.md. Quantity from current CAD tube-cut plan; cutting unquoted.');
add('S02','Chassis','1 x 1 x .083 inch brace tube, 20-foot bar',1,'bar',40,'Allowance',null,metal,'Final brace takeoff in CAD cut list; do not substitute the old angle-brace schedule.');
add('S03','Chassis','Rail datum-cap steel blanks',2,'blank',60,'Allowance',null,metal,'Finish dimensions and machining per motion CAD.');
add('S04','Chassis','Steel flat parts, foot pads, seats and gussets',1,'lot',160,'Allowance',null,metal,'Cut blanks only; not a requirement to buy every illustrated full nesting sheet.');
add('S05','Water metal','0.120 inch steel sheet, 4 x 8 feet',2,'sheet',180,'Allowance',null,metal,'Pan, slats and vented reservoir nested together; use final thickness-specific DXFs.');
add('S06','Chassis','Appearance skins and removable access covers',1,'lot',200,'Allowance',null,metal,'Finish/access-cover provision; final cut dimensions and material remain unquoted.');
add('S07','Motion','80/20 standard 40-8080, 1200 mm cut',1,'each',151.73,'Observed',null,'https://8020.net/40-8080.html','Posted goods price: 1200 x $0.1231 + $4.01 cut. Freight unknown.');
add('S08','Motion','Gantry, guide and head adapter plate stock',1,'lot',150,'Allowance',null,metal,'Includes dual-X-guide face plate; machining is a separate allowance.');
add('S09','Router bed','1 x 1/4 inch aluminum flat bar, twelve 500 mm ties',1,'lot',45,'Allowance',null,metal,'6 m finished total plus kerfs; order cut blanks or suitable bar lengths.');
add('S10','Router bed','3/4 inch MDF, one 4 x 8 foot sheet',1,'sheet',55,'Allowance',null,'https://www.homedepot.com/p/309177124','Six removable spoilboards plus spare stock. Surface after alignment.');
add('S11','Chassis','Dry sand, 50-pound bags',3,'bag',12,'Allowance',null,'','Stationary frame members only; weigh actual fill.');
add('S12','Chassis','Primer, graphite finish and finishing consumables',1,'lot',100,'Allowance');
add('H01','Chassis','M16 foot adjustment screws, jam nuts and small hardware',1,'lot',45,'Allowance',null,'','Custom steel foot pads already counted in S04.');
add('H02','Chassis','Sand-port plugs and seals',1,'lot',45,'Allowance');
add('H03','Chassis','Cover fasteners, storage liners and retaining hardware',1,'lot',75,'Allowance');
add('H04','Motion','Motion shoulder screws, race shims, jam nuts and mounting screws',1,'lot',165,'Allowance',null,'','Replaces the former $100 all-hardware allowance: $50 linkage pins/shims, $75 ordinary modeled motion screws, $40 unresolved rail/HMS mounting hardware. Rod ends and 8080 T-nuts are separately priced.');
add('H09','Motion','SKF SA6C right-hand rod end',3,'each',49.32,'Benchmark',null,'https://www.sp-spareparts.com/en/p/sal6-c-skf','Related exact-SKU retail benchmark on SAL6C page, not a direct checkout offer. Matches the frozen CAD ball width; cheap wider rod ends are not interchangeable without redesign.');
add('H10','Motion','SKF SAL6C left-hand rod end',3,'each',46.27,'Observed',null,'https://www.sp-spareparts.com/en/p/sal6-c-skf','Three floating-drive links each require one RH and one LH end. Freight unquoted.');
add('H11','Motion','80/20 40-3915 M8 T-nut',16,'each',2.58,'Observed',null,'https://8020.net/40-3915.html','Manufacturer custom-quantity unit price; already excluded from H04 to avoid duplicate hardware pricing.');
add('H05','Router bed','Nutty XMSQNT5 M5 x 0.8 A2 thin square nuts, DIN 562',260,'each',0.076,'Observed',10.95,'https://www.nutty.com/m5-x-8-stainless-metric-square-nut-thin/','240 used: 120 ties, 60 anchors, 60 spoilboard fasteners; 20 spare. Posted 100–499 price and $10.95 US48 flat shipping policy: https://www.nutty.com/shipping-returns/ . Receipt check 8 x 8 x 2.7 mm maximum to DIN 562; do not substitute DIN 557. Stock/dispatch date not confirmed.');
add('H06','Router bed','M5 tie screws, 60 anchors, jam nuts and DIN 7349 heavy washers',1,'lot',80,'Allowance',null,'https://www.norelemusa.com/en-us/Product-Overview/Flexible-standard-component-system/07000/Nuts-screws-washers-securing-elements/Washers-DIN-7349-for-bolts-with-heavy-duty-clamping-bodies/p/agid.28087','120 tie screws; 60 anchor studs, 120 jam nuts and 60 retaining washers. Washer07305-05-050: 15 mm OD, 5.3 mm ID, 2 mm thick. Thin DIN 9021 washers are superseded.');
add('H07','Router bed','16 M8 beam drawdowns, nuts and compression sleeves',1,'lot',45,'Allowance');
add('H08','Router bed','MDF retention, handles and ordinary work clamps',1,'lot',70,'Allowance');
add('W-METAL-EXTRA','Water metal','EPDM cover gasket, stainless sensor brackets and welded pipe fittings',1,'lot',85,'Allowance',null,'','Does not duplicate flexible hoses and threaded adapters in the water-control BOM.');
for(const w of water.items){
  add(w.id,'Water controls',w.description,w.quantity,'pack / lot',w.unit_usd??w.allowance_usd/w.quantity,
    w.unit_usd===undefined?'Allowance':'Observed',w.shipping_usd,w.url||'',(w.notes||[]).join(' ')+' '+(w.shipping_status||''));
}
function prior(id,overrides={}){
  const p=old.rows.find(x=>x.id===id);
  const v={...p,...overrides};
  add(v.id,v.cat==='Controls'?'Controls':v.cat,v.item,v.qty,v.unit,v.price,
    ['Amazon offer','Posted price'].includes(v.basis)?'Observed':v.basis==='User screenshot'?'Screenshot':'Allowance',
    v.shipping??(v.basis==='Amazon offer'?0:null),v.url,v.notes||'');
}
for(const id of ['E02','E05','E06','E07','E09','E12','E13','E14','E15','E16','E17','E19','E20','E21','E22'])prior(id);
add('E10','Controls','Omron D2VW-01L2-1MS sealed gold-contact roller home switch',4,'each',14.09,'Observed',null,'https://www.mouser.com/ProductDetail/Omron-Electronics/D2VW-01L2-1MS?qs=ImaqFqjHA4nlTsHd7%252BPS7w%3D%3D','Replaces old $48 switch allowance. Three XY switches modeled; fourth Z mounting awaits supplier dimensions. Page warns of possible 10% tariff; actual charge unquoted.');
add('E03','Controls','MEAN WELL LRS-350-24, shared 24 V / 14.6 A supply',1,'each',31.40,'Observed',0,'https://www.amazon.com/dp/B013ETVO12','Counted once; reserve at least 8 A for water system. Replaces earlier LRS-150-24.');
add('E08','Controls','External UP/DOWN/ARC-OK torch-height controller',1,'each',220,'Allowance',null,'https://www.poscope.com/product/plasmasenscompact/','Candidate PlasmaSens Compact; exact cutter compatibility, USD checkout and shipping unresolved. This is not an external stepper driver.');
add('E11','Controls','Bed, guard and head permissive mechanisms and switches',1,'lot',50,'Allowance',null,'','Mechanism not yet fully detailed; this is not a claim that one switch verifies every bed fastener.');
for(const id of ['R02','R03','R04','R05','P01','P02','P03'])prior(id);
add('F01','Fabrication','DIY welding, cutting and assembly consumables',1,'lot',175,'Allowance',null,'','User performs assembly; not a paid shop-fabrication quotation.');
add('F02','Fabrication','Owner-performed rail datum finishing and flat-part cutting',1,'lot',0,'Owner work',null,'','User is the fabricator. No outside-shop labor included; former $250 allowance removed. Required datum finishing and cutting remain fabrication operations. Materials and consumables are priced separately.');
add('F03','Fabrication','Owner-performed motion coupler, clevis, shoe, clamp and stop machining',1,'lot',0,'Owner work',null,'','User is the fabricator. No outside-shop labor included; former $900 allowance removed. Three couplers, six clevises, three shoes, three supports, two beam feet, two clamp halves, stops/cams, tapping and counterbores still require fabrication. Raw stock is in S08.');
add('SHIP','Shipping reserve','Unquoted metal, controls and miscellaneous delivery reserve',1,'lot',300,'Reserve',null,'','Includes the $20 water shipping reserve. It is not an actual carrier or checkout quote.');
const currentNotes={
  E09:'Isolated field-input provision for the selected Kraken V1.1 grblHAL pin map. GPIO is 3.3 V logic; exact field isolation, signal polarity and wetting current remain to be designed.',
  E13:'Common supply isolation, fuses, EMC filter and tool interlocks only. Dedicated water SSRs, auxiliary relays and branch parts are separately counted under Water controls.',
  E21:'CB1 storage, controller firmware microSD and host cooling allowance. The selected controller firmware is grblHAL. No display included; compatible host sender setup remains to be commissioned.',
  E22:'Isolated 5 kHz PWM-to-0–10 V and run-contact interface provision for the selected Kraken firmware. Exact interface module, VFD terminals and parameters remain unselected.',
  R02:'Choose dust shoe and hose for actual 65 mm spindle and tool length. Shop extractor is excluded if not already owned.',
  R03:'ER11-compatible starter cutter set and surfacing cutter only. Workholding hardware is counted in H08; no duplicate clamps. No 1/2-inch-shank bits.'
};
for(const r of rows)if(currentNotes[r.id])r.notes=currentNotes[r.id];
rows.find(r=>r.id==='R03').item='Starter cutters and surfacing tool';
const categories=[...new Set(rows.map(r=>r.category))];
const total=rows.reduce((s,r)=>s+r.quantity*r.unit_usd+(r.shipping_usd??0),0);
const observed=rows.filter(r=>r.basis==='Observed').reduce((s,r)=>s+r.quantity*r.unit_usd+(r.shipping_usd??0),0);
const summary={currency:'USD',destination:'Alto GA 30510',date:'2026-09-24',revision:'RevE engineering estimate',planning_total_before_tax:Math.round(total*100)/100,observed_goods_and_advertised_shipping:Math.round(observed*100)/100,delivered_quote:null,release:false,
  exclusions:['Sales tax and any import tariff','Owner fabrication/machining labor and any separately commissioned outside-shop work','Dust/fume extraction and air treatment if not already owned','Replacement plasma cutter or machine torch if existing equipment is incompatible','Unselected Z brake/counterbalance and unresolved tool-interface parts beyond allowances','Paid CAD/CAM licenses'],
  owner_fabrication_correction:{previous_planning_total_before_tax:8813.82,removed_outside_machining_allowance:900,removed_outside_finishing_cutting_allowance:250,total_removed:1150,reason:'User performs fabrication; labor is not an external cash purchase. Stock and consumables remain counted.'},
  owned:['12 CFM compressor','CV-15HS vacuum generator (not used as a liquid pump)','Existing plasma cutter and torch, identity/compatibility unconfirmed','Existing solenoids, no cost credit until verified'],
  categories:categories.map(c=>({name:c,total:Math.round(rows.filter(r=>r.category===c).reduce((s,r)=>s+r.quantity*r.unit_usd+(r.shipping_usd??0),0)*100)/100}))};
await fs.mkdir(dir,{recursive:true});
await fs.writeFile(path.join(dir,'budget-data.json'),JSON.stringify({summary,rows},null,2));
const wb=Workbook.create();
const s=wb.worksheets.add('Build total');
const p=wb.worksheets.add('Parts and sources');
for(const sh of [s,p]){sh.showGridLines=false;sh.getRange('A1:M120').format.font.name='Aptos';sh.getRange('A1:M120').format.font.size=11;}
const last=rows.length+6;
p.getRange('A1:M1').merge();p.getRange('A1').values=[['RevE | Parts, price evidence and allowances']];
p.getRange('A2:M2').merge();p.getRange('A2').values=[['USD • Alto, GA 30510 • observed September 24, 2026 • planning estimate, no purchasing release']];
p.getRange('A3:M4').merge();p.getRange('A3').values=[['Blank delivery charges are unquoted, not free. The $300 reserve covers unquoted delivery in the estimate. Observed offers are not completed checkout quotes. Quantities remain tied to the engineering CAD revision.']];
p.getRange('A6:M6').values=[['ID','Category','Item / specification','Qty','Unit','Unit $','Price basis','Known ship $','Goods $','Planning line $','Shipping status','Source','Fit / scope notes']];
p.getRange(`A7:M${last}`).values=rows.map(r=>[r.id,r.category,r.item,r.quantity,r.unit,r.unit_usd,r.basis,r.shipping_usd,null,null,r.basis==='Owner work'?'Not applicable':r.shipping_usd===0?'Advertised free':r.shipping_usd===null?'Unquoted':'Posted flat rate',r.url||(r.basis==='Owner work'?'User performs fabrication':'Allowance; no supplier quote'),r.notes]);
p.getRange(`I7:J${last}`).formulas=rows.map((r,i)=>[`=D${i+7}*F${i+7}`,`=I${i+7}+IF(ISNUMBER(H${i+7}),H${i+7},0)`]);
p.getRange(`F7:J${last}`).setNumberFormat('$#,##0.00;[Red]($#,##0.00);$0.00');
for(let i=0;i<rows.length;i++)if(rows[i].unit_usd>0&&rows[i].unit_usd<1)p.getRange(`F${i+7}`).setNumberFormat('$0.000');
p.getRange(`A7:M${last}`).format.rowHeight=90;p.getRange(`A7:M${last}`).format.wrapText=true;p.getRange(`A6:M${last}`).format.verticalAlignment='center';
const widths={A:85,B:125,C:360,D:45,E:80,F:85,G:90,H:100,I:90,J:100,K:110,L:280,M:440};
for(const [c,w]of Object.entries(widths))p.getRange(`${c}:${c}`).format.columnWidthPx=w;
p.freezePanes.freezeRows(6);p.tables.add(`A6:M${last}`,true,'PurchasePlan');
s.getRange('A1:F1').merge();s.getRange('A1').values=[['CNC + plasma | RevE build estimate']];
s.getRange('A2:F2').merge();s.getRange('A2').values=[['800 × 1000 × 100 mm nominal travel • Alto, Georgia 30510 • USD']];
s.getRange('A4:D4').merge();s.getRange('A4').values=[['PLANNING TOTAL, BEFORE TAX']];s.getRange('E4:F4').merge();s.getRange('E4').formulas=[[`=SUM('Parts and sources'!J7:J${last})`]];
s.getRange('A5:F6').merge();s.getRange('A5').values=[['Owner performs fabrication: $1,150 in outside-shop allowances removed. Includes $300 shipping reserve and unquoted materials / hardware. Final delivered cost remains unresolved.']];
s.getRange('A8:D8').merge();s.getRange('A8').values=[['Observed goods + displayed delivery']];s.getRange('E8:F8').merge();s.getRange('E8').formulas=[[`=SUMIF('Parts and sources'!G7:G${last},"Observed",'Parts and sources'!J7:J${last})`]];
s.getRange('A9:D9').merge();s.getRange('A9').values=[['Allowances, benchmarks, screenshots and reserve']];s.getRange('E9:F9').merge();s.getRange('E9').formulas=[['=E4-E8']];
s.getRange('A11:D11').merge();s.getRange('A11').values=[['Included scope']];s.getRange('E11:F11').merge();s.getRange('E11').values=[['Planning $']];
for(let i=0;i<categories.length;i++){let n=12+i;s.getRange(`A${n}:D${n}`).merge();s.getRange(`A${n}`).values=[[categories[i]]];s.getRange(`E${n}:F${n}`).merge();s.getRange(`E${n}`).formulas=[[`=SUMIF('Parts and sources'!B7:B${last},A${n},'Parts and sources'!J7:J${last})`]];}
let n=13+categories.length;
for(const [title,body]of [
  ['Bed quantity','Five packs of 20100 extrusion = ten 1220 mm sticks = thirty 397 mm strips. Six cassettes make a nominal 1003 × 1197 mm deck.'],
  ['Controller','Kraken V1.1 uses four onboard drivers. No external stepper-driver boxes are added. Host hardware remains budgeted; reuse of a suitable PC could remove the host allowance.'],
  ['Owned equipment','Compressor and existing cutter/torch are not repurchased. Exact cutter compatibility is still unresolved. CV-15HS is a vacuum generator, not a water pump.'],
  ['Excluded costs',summary.exclusions.join('; ')+'.'],
  ['Status','Engineering design in progress. This workbook supersedes the old $9,114 workbook and the coarse $5,745 estimate; it is not a purchasing authorization or manufacturing release.']
]){s.getRange(`A${n}:F${n}`).merge();s.getRange(`A${n}`).values=[[title]];s.getRange(`A${n}`).format.font.bold=true;s.getRange(`A${n+1}:F${n+2}`).merge();s.getRange(`A${n+1}`).values=[[body]];n+=4;}
s.getRange(`A1:F${n}`).format.wrapText=true;s.getRange(`A1:F${n}`).format.rowHeight=23;s.getRange('A:F').format.columnWidthPx=130;
s.getRange('A36:F37').format.rowHeight=34;
for(const sh of [s,p]){sh.getRange(sh===s?'A1:F1':'A1:M1').format.fill='#173A43';sh.getRange(sh===s?'A1:F1':'A1:M1').format.font.color='#FFFFFF';sh.getRange('A1').format.font.size=20;sh.getRange('A1').format.rowHeight=38;}
s.getRange('A4:F4').format.fill='#DCEDEA';s.getRange('A4:F4').format.font.bold=true;s.getRange('E4').format.font.size=22;s.getRange('A4:F4').format.rowHeight=40;
s.getRange(`E4:F${12+categories.length}`).setNumberFormat('$#,##0.00');s.getRange('A11:F11').format.fill='#173A43';s.getRange('A11:F11').format.font.color='#FFFFFF';
p.getRange('A6:M6').format.fill='#173A43';p.getRange('A6:M6').format.font.color='#FFFFFF';p.getRange('A6:M6').format.rowHeight=44;p.getRange('A6:M6').format.wrapText=true;
await wb.recalculate();
const inspected=await wb.inspect({kind:'region',sheetId:'Build total',range:'A4:F9',maxChars:3000});
await fs.writeFile(path.join(dir,'workbook-check.json'),JSON.stringify({expected:summary,inspection:inspected},null,2));
const totalCell=s.getRange('E4').values[0][0];if(Math.abs(Number(totalCell)-summary.planning_total_before_tax)>0.005)throw Error('Workbook total mismatch '+totalCell);
const errs=rows.flatMap((r,i)=>p.getRange(`I${i+7}:J${i+7}`).values.flat()).filter(v=>typeof v==='string'&&v.startsWith('#'));if(errs.length)throw Error('Formula errors '+errs);
for(const [sheetName,range,file]of [['Build total',`A1:F${n-2}`,'summary-preview.png'],['Parts and sources','A6:K19','parts-preview.png']]){
  const preview=await wb.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(path.join(dir,file),new Uint8Array(await preview.arrayBuffer()));
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(dir,'CNC-plasma-RevE-budget.xlsx'));
console.log(JSON.stringify({summary,rows:rows.length,xlsx:path.join(dir,'CNC-plasma-RevE-budget.xlsx')},null,2));
