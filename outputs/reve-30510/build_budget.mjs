import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=path.dirname(fileURLToPath(import.meta.url));
const d=JSON.parse(await fs.readFile(path.join(dir,'actual-cost/audit-data.json'),'utf8'));
const wb=Workbook.create();
const s=wb.worksheets.add('Cost status'),p=wb.worksheets.add('Priced items'),u=wb.worksheets.add('Required unpriced'),a=wb.worksheets.add('Options not adopted');
const teal='#173A43',pale='#E5F0ED',amber='#FFF0D0';
for(const sh of [s,p,u,a]){sh.showGridLines=false;sh.getRange('A1:K220').format.font.name='Aptos';sh.getRange('A1:K220').format.font.size=11;sh.getRange('A1:K220').format.verticalAlignment='center';}
function title(sh,last,text,sub){
 sh.getRange(`A1:${last}1`).merge();sh.getRange('A1').values=[[text]];
 sh.getRange(`A1:${last}1`).format.fill=teal;sh.getRange(`A1:${last}1`).format.font.color='#FFFFFF';sh.getRange('A1').format.font.size=21;sh.getRange('A1').format.rowHeight=40;
 sh.getRange(`A2:${last}2`).merge();sh.getRange('A2').values=[[sub]];sh.getRange('A2').format.rowHeight=28;
}
function table(sh,head,last,headers,values,name,widths){
 sh.getRange(`A${head}:${last}${head}`).values=[headers];const end=head+values.length;
 if(values.length)sh.getRange(`A${head+1}:${last}${end}`).values=values;
 sh.tables.add(`A${head}:${last}${end}`,true,name);sh.getRange(`A${head}:${last}${head}`).format.fill=teal;sh.getRange(`A${head}:${last}${head}`).format.font.color='#FFFFFF';sh.getRange(`A${head}:${last}${head}`).format.rowHeight=36;
 sh.getRange(`A${head}:${last}${end}`).format.wrapText=true;sh.getRange(`A${head+1}:${last}${end}`).format.rowHeight=78;
 for(const [c,w]of Object.entries(widths))sh.getRange(`${c}:${c}`).format.columnWidthPx=w;
 sh.freezePanes.freezeRows(head);return end;
}
title(p,'J','RevE | Source-backed prices','USD • recorded 24 September 2026 • prices are not a manufacturing release');
p.getRange('A3:J4').merge();p.getRange('A3').values=[['Every row has a source price. Vendor shipping is counted once on Cost status. Remaining fit, stock and electrical checks are in column J. Required unpriced items and unadopted alternatives are excluded from this subtotal.']];p.getRange('A3:J4').format.wrapText=true;p.getRange('A3:J4').format.rowHeight=26;
const pend=table(p,6,'J',['ID','Category','Exact item / stock','Buy qty','Unit','Unit USD','Goods USD','Vendor','Source','Fit / availability / scope'],d.rows.map(r=>[r.id,r.category,r.item,r.quantity,r.unit,r.unit_usd,null,r.vendor,r.url,r.notes]),'PricedOffers',{A:100,B:145,C:380,D:65,E:90,F:95,G:100,H:165,I:340,J:590});
p.getRange(`G7:G${pend}`).formulas=d.rows.map((r,i)=>[`=ROUND(D${i+7}*F${i+7},2)`]);p.getRange(`F7:G${pend}`).setNumberFormat('$#,##0.00');
for(let i=0;i<d.rows.length;i++)if(d.rows[i].unit_usd<1)p.getRange(`F${i+7}`).setNumberFormat('$0.000');p.getRange(`D7:F${pend}`).format.font.color='#205A9C';
title(u,'E','Required scope with no complete price','Blank prices mean unresolved cost, never zero. These requirements are outside the priced subtotal.');
const uend=table(u,4,'E',['ID','Required item / residual scope','Quantity','Work or quote needed','Source / specification'],d.unpriced.map(r=>[r.id,r.item,r.quantity,r.required_work,r.url]),'UnpricedScope',{A:130,B:360,C:85,D:700,E:360});u.getRange(`A5:E${uend}`).format.rowHeight=96;
title(a,'H','Options not adopted','These offers are not added to the current-design subtotal. Prices may be in different currencies.');
const aend=table(a,4,'H',['ID','Candidate','Buy qty','Unit price','Currency','Goods total','Source','Reason / remaining design work'],d.alternatives.map(r=>[r.id,r.item,r.quantity,r.unit_price,r.currency,null,r.url,r.reason]),'UnadoptedOptions',{A:90,B:385,C:70,D:90,E:75,F:110,G:360,H:680});
a.getRange(`F5:F${aend}`).formulas=d.alternatives.map((r,i)=>[`=IF(ISNUMBER(D${i+5}),ROUND(C${i+5}*D${i+5},2),"")`]);a.getRange(`D5:D${aend}`).setNumberFormat('#,##0.00');a.getRange(`F5:F${aend}`).setNumberFormat('#,##0.00');a.getRange(`A5:H${aend}`).format.rowHeight=116;
for(let i=0;i<d.alternatives.length;i++){const r=d.alternatives[i];if(r.unit_price>0&&r.unit_price<1)a.getRange(`D${i+5}`).setNumberFormat('0.000');if(r.reason.length>600)a.getRange(`A${i+5}:H${i+5}`).format.rowHeight=170;}
title(s,'H','CNC + plasma | Actual price audit','800 × 1000 × 100 mm nominal travel • Alto, GA 30510 • USD • 24 September 2026');
s.getRange('A:H').format.columnWidthPx=115;s.getRange('A1:H100').format.wrapText=true;s.getRange('A3:H100').format.rowHeight=26;
function output(row,label,formula,value){s.getRange(`A${row}:E${row}`).merge();s.getRange(`A${row}`).values=[[label]];s.getRange(`F${row}:H${row}`).merge();if(formula)s.getRange(`F${row}`).formulas=[[formula]];else s.getRange(`F${row}`).values=[[value]];}
output(4,'COMPLETE BUILD, DELIVERED','','NOT ESTABLISHED');s.getRange('A4:H4').format.fill=amber;s.getRange('A4:H4').format.font.bold=true;s.getRange('A4:H4').format.rowHeight=44;
output(6,'Priced goods subtotal',`=SUM('Priced items'!G7:G${pend})`);
const shiphead=34,shipfirst=35,shipend=shiphead+d.shipping.length;
output(7,'Known or advertised shipping',`=SUM(C${shipfirst}:C${shipend})`);output(8,'PRICED SCOPE ONLY — BEFORE TAX','=F6+F7');s.getRange('A8:H8').format.fill=pale;s.getRange('A8:H8').format.font.bold=true;s.getRange('A8:H8').format.rowHeight=38;s.getRange('F8').format.font.size=21;s.getRange('F6:H8').setNumberFormat('$#,##0.00');
s.getRange('A10:H12').merge();s.getRange('A10').values=[[`This is a partial price register, not the whole-machine cost. ${d.summary.unpriced_scope_rows} remaining scope entries and ${d.summary.unquoted_vendor_shipping_groups} vendor delivery groups are unpriced. Those blanks are not included as $0. Your fabrication labor is $0; no outside shop fees or arbitrary shipping reserve are added.`]];s.getRange('A10:H12').format.rowHeight=26;
output(14,'Amazon goods with advertised free delivery',`=SUMIF('Priced items'!H7:H${pend},"Amazon",'Priced items'!G7:G${pend})`);s.getRange('F14:H14').setNumberFormat('$#,##0.00');
s.getRange('A16:E16').merge();s.getRange('A16').values=[['Priced portion by category']];s.getRange('F16:H16').merge();s.getRange('F16').values=[['Goods only']];s.getRange('A16:H16').format.fill=teal;s.getRange('A16:H16').format.font.color='#FFFFFF';
d.categories.forEach((c,i)=>output(17+i,c.category,`=SUMIF('Priced items'!B7:B${pend},A${17+i},'Priced items'!G7:G${pend})`));s.getRange(`F17:H${16+d.categories.length}`).setNumberFormat('$#,##0.00');
s.getRange('A29:H31').merge();s.getRange('A29').values=[['The old $7,663.82 estimate is superseded. It included $4,200 of allowances and a $300 shipping reserve. The audit also found understated billet stock and missing small-stock purchases. A $200 skin allowance had no separate CAD panels and is removed. No cheaper bracket or rod-end redesign has been credited as completed.']];s.getRange('A29:H31').format.fill=amber;s.getRange('A29:H31').format.rowHeight=29;
s.getRange('A33:H33').merge();s.getRange('A33').values=[['Shipping register — one charge per vendor order']];s.getRange('A33').format.font.bold=true;
s.getRange('A34:B34').merge();s.getRange('A34').values=[['Vendor']];s.getRange('C34').values=[['Ship USD']];s.getRange('D34').values=[['Tax shown']];s.getRange('E34:H34').merge();s.getRange('E34').values=[['Evidence / conditions']];s.getRange('A34:H34').format.fill=teal;s.getRange('A34:H34').format.font.color='#FFFFFF';
d.shipping.forEach((r,i)=>{const n=35+i;s.getRange(`A${n}:B${n}`).merge();s.getRange(`A${n}`).values=[[r.vendor]];s.getRange(`C${n}:D${n}`).values=[[r.amount_usd,r.tax_usd]];s.getRange(`E${n}:H${n}`).merge();s.getRange(`E${n}`).values=[[r.basis]];s.getRange(`A${n}:H${n}`).format.rowHeight=r.basis.length>170?82:64;});s.getRange(`C35:D${shipend}`).setNumberFormat('$#,##0.00');
const note=shipend+2;s.getRange(`A${note}:H${note+2}`).merge();s.getRange(`A${note}`).values=[['80/20 cart: $193.01 goods + $61.30 UPS Ground + $17.80 estimated tax = $272.11. This is the only destination-specific vendor cart total captured; no order was placed. Other tax, tariffs and blank freight remain unknown.']];s.getRange(`A${note}:H${note+2}`).format.rowHeight=26;s.freezePanes.freezeRows(4);
await wb.recalculate();const got=Number(s.getRange('F8').values[0][0]);if(Math.abs(got-d.summary.priced_scope_before_tax_usd)>.005)throw Error(`Subtotal mismatch ${got}`);
if(p.getRange(`G7:G${pend}`).values.flat().some(v=>typeof v==='string'&&v.startsWith('#')))throw Error('Formula error in goods');if(s.getRange('F4').values[0][0]!=='NOT ESTABLISHED')throw Error('Unknown final total must stay open');
const originalQty=p.getRange('D8').values[0][0];p.getRange('D8').values=[[originalQty+1]];await wb.recalculate();
if(Math.abs(Number(s.getRange('F8').values[0][0])-got-d.rows[1].unit_usd)>.005)throw Error('Quantity change did not propagate to summary');
p.getRange('D8').values=[[originalQty]];await wb.recalculate();if(Math.abs(Number(s.getRange('F8').values[0][0])-got)>.005)throw Error('Input restoration failed');
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'final formula error scan'});
const formulaErrorPattern=/^#(?:REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!|SPILL!|CALC!)$/;
const directErrors=[];
for(const [sheet,range]of [[s,'A1:H100'],[p,`A1:J${pend}`],[u,`A1:E${uend}`],[a,`A1:H${aend}`]]){for(const [ri,row]of sheet.getRange(range).values.entries())for(const [ci,value]of row.entries())if(typeof value==='string'&&formulaErrorPattern.test(value))directErrors.push({sheet:sheet.name,row:ri+1,column:ci+1,value});}
if(directErrors.length)throw Error(JSON.stringify(directErrors));
const check={summary:d.summary,subtotal_matches:true,quantity_recalculation_restored:true,final_total_not_invented:true,priced_items:d.rows.length,unique_ids:new Set(d.rows.map(r=>r.id)).size,direct_formula_error_count:directErrors.length,formula_scan:errors,inspection:await wb.inspect({kind:'region',sheetId:'Cost status',range:'A4:H14',maxChars:3000})};await fs.writeFile(path.join(dir,'workbook-check.json'),JSON.stringify(check,null,2));
for(const [sheetName,range,file]of [['Cost status','A1:H31','summary-preview.png'],['Cost status','A33:H43','shipping-preview.png'],['Priced items','A6:G18','parts-preview.png'],['Required unpriced','A4:D10','unpriced-preview.png'],['Options not adopted','A4:H9','options-preview.png'],['Options not adopted','A15:H17','owned-stock-preview.png']]){const preview=await wb.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(path.join(dir,file),new Uint8Array(await preview.arrayBuffer()));}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(dir,'CNC-plasma-RevE-budget.xlsx'));console.log(JSON.stringify(check.summary,null,2));
