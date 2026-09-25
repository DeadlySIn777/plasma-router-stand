"""Reconcile researched offers without filling missing prices with allowances."""
from pathlib import Path
import json, hashlib
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlparse

HERE=Path(__file__).resolve().parent
BUDGET=HERE.parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def money(x): return float(Decimal(str(x)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def vendor_name(v):
    return {'www.digikey.com':'DigiKey','www.mouser.com':'Mouser','www.onlinemetals.com':'OnlineMetals','store.buymetal.com':'BuyMetal','www.zoro.com':'Zoro','www.jegs.com':'JEGS','www.blueskysupplies.com':'BlueSky Supplies','www.shapirosupply.com':'Shapiro Supply','www.bonanza.com':'Harness Steel / Bonanza','www.sp-spareparts.com':'SP Spareparts','baomain.com':'Baomain'}.get(v,v)
oldpath=BUDGET/'budget-data.estimate-history.json'
if not oldpath.exists(): oldpath.write_bytes((BUDGET/'budget-data.json').read_bytes())
old=read(oldpath); byold={r['id']:r for r in old['rows']}
core=read(HERE/'core-findings.json'); metal=read(HERE/'metal-findings.json')
hardware=read(HERE/'hardware-findings.json'); controls=read(HERE/'controls-findings.json')
rows=[]; gaps=[]; options=[]; shipments=[]
def add(id,group,item,qty,unit,price,url,notes='',vendor='',shipping=None,basis='Posted price'):
    rows.append(dict(id=id,category=group,item=item,quantity=qty,unit=unit,unit_usd=price,
        goods_usd=money(Decimal(str(qty))*Decimal(str(price))),url=url,notes=notes,
        vendor=vendor_name(vendor or urlparse(url or '').netloc),shipping_usd=shipping,basis=basis))
def gap(id,item,details,quantity='',url=''):
    gaps.append(dict(id=id,item=item,quantity=str(quantity),required_work=details,url=url,unit_usd=None))
for r in core['rows']:
    oldr=byold.get(r['id'],{})
    add(r['id'],oldr.get('category','Controls'),oldr.get('item',r['item']),r['quantity'],oldr.get('unit','each'),r['unit_usd'],r['url'],r['notes'],r['vendor'],r['shipping_usd'],'Live offer 24 Sep')
coreids={r['id'] for r in rows}
# Earlier same-day researched exact offers retained; related-SKU benchmarks excluded.
for id in ['H10','E10','W-AUX-RELAYS','W-DRAIN-TIMER','W-MOTOR-RELAYS']:
    r=byold[id]
    add(id,r['category'],r['item'],r['quantity'],r['unit'],r['unit_usd'],r['url'],r['notes']+' Earlier same-day offer retained; freight not yet quoted.',shipping=None)
for r in metal['published_stock_candidates']:
    group=byold[r['replaces_or_contributes_to']]['category']
    add(r['id'],group,r['item'],r['quantity'],'stock piece',r['unit_usd'],r['url'],r['allocation']+' '+r['status'],shipping=None)
    if r.get('shipping_usd') is not None:
        shipments.append(dict(id='SHIP-'+r['id'],vendor=vendor_name(urlparse(r['url']).netloc),ids=[r['id']],amount_usd=r['shipping_usd'],tax_usd=None,basis=r['status']))
for r in metal['quote_only_raw_stock_schedule']:
    gap('MET-GAP-'+str(len(gaps)+1),r['item'],r['size']+'. '+r['required_for'],r['quantity'])
for r in metal.get('additional_retail_offers',[]):
    options.append(dict(id=r['id'],item=r['item'],quantity=r['quantity'],unit_price=r['unit_usd'],currency='USD',extended=r['goods_usd'],url=r['url'],reason=r['price_evidence']+' '+r['fulfillment_status']+' '+r['allocation']))
for r in hardware['offers']:
    if r['id']=='T1': continue # exact same 80/20 hardware already included
    comp=r.get('compatibility','')
    selected=(r['id'] in ['N1','N2','N3','N4','N5','W1'] or r.get('accepted_current_design',False))
    if selected:
        add('HW-'+r['id'],'Standard hardware',r['item'],r['buy_quantity'],('pack of '+str(r['pack_size'])) if r.get('pack_size',1)>1 else 'each',r['unit_usd'],r['url'],comp,r['vendor'])
    else:
        options.append(dict(id='HW-'+r['id'],item=r['item'],quantity=r['buy_quantity'],unit_price=r.get('unit_usd'),currency='USD',extended=r.get('goods_usd'),url=r.get('url',''),reason=comp))
for r in hardware['audits']:
    if r['budget_id'] in ['H01','H05','H10','H11']: continue
    gap('HW-GAP-'+r['budget_id'],byold[r['budget_id']]['item'],r['finding'])
options.append(dict(id='OWN-AL-12',item='Owner aluminum: one 12 x 12 x 1/2 in plate and one 12 x 12 x 3/8 in plate (quantity assumed)',quantity=2,unit_price=0,currency='USD',extended=0,url='User-reported stock, 24 September 2026',reason='Acquisition cost $0 for existing pieces. Alloy and usable finished thickness unverified. The 1/2 in plate can replace MET08 Z-carrier stock, conditionally avoiding $58.74; MET08 remains in current subtotal until qualified. Other small parts fit but already use paid-stock offcuts, so no extra saving. The 3/8 in plate is unallocated; no redesign saving assumed. See OWNED-ALUMINUM-FIT.md.'))
for r in controls['rows']:
    if r.get('status')=='candidate_not_adopted' or r.get('currency','USD')!='USD':
        options.append(dict(id=r['id'],item=r['item'],quantity=r['qty'],unit_price=r['unitprice'],currency=r.get('currency','USD'),extended=r.get('extended'),url=r.get('source',''),reason=r['fitproof']+' '+' '.join(r.get('openitems',[]))))
    elif r.get('unitprice') is not None and r['unitprice']>0:
        add(r['id'],'Controls and water wiring',r['item'],r['qty'],'pack / each',r['unitprice'],r.get('source',''),r['fitproof']+' '+' '.join(r.get('openitems',[])),r.get('shipping',{}).get('vendor_group',''))
    elif r.get('unitprice') is None:
        gap(r['id'],r['item'],r['fitproof']+' '+' '.join(r.get('openitems',[])),r['qty'],r.get('source',''))
# Scope not fully represented in subordinate price audits.
for id,details in [
 ('E08','Selected THC offer is conditional and EUR-denominated; actual cutter starting circuit, isolated sensing, currency conversion and delivery are unresolved.'),
 ('E11','Exact bed/guard/head confirming mechanisms and switch actuation remain to be selected; price cannot be completed from a generic switch allowance.'),
 ('E22','Isolated VFD control candidate requires a complete fail-off interface and 3.3V/5V compatibility check; candidate prices are separate.'),
 ('MET-DATUM','Rail datum raw-stock cleanup allowance needs confirmation; the nominal 5/16in offer may need thicker stock to produce a flat finished datum.')]:
    gap(id,byold.get(id,{}).get('item',id),details)
for s in core['shipping_groups']:
    shipments.append(dict(id='SHIP-8020',vendor=s['vendor'],ids=s['ids'],amount_usd=s['shipping_usd'],tax_usd=s['tax_estimate_usd'],basis=s['basis']))
nuttygoods=money(sum(r['goods_usd'] for r in rows if r['vendor']=='Nutty'))
nuttyship=0 if nuttygoods>=100 else 10.95
shipments.append(dict(id='SHIP-NUTTY',vendor='Nutty',ids=[r['id'] for r in rows if r['vendor']=='Nutty'],amount_usd=nuttyship,tax_usd=None,basis='Published US48 eligible-merchandise policy; one order. Goods are above $100 and qualify for free shipping. Each line rounded to cents; checkout may round fractions of a cent differently. Stock and tax not confirmed.'))
for vendor in ['Amazon','BIQU','AutomationDirect']:
    shipments.append(dict(id='SHIP-'+vendor,vendor=vendor,ids=[r['id'] for r in rows if r['vendor']==vendor],amount_usd=0,tax_usd=None,basis=('Amazon product pages advertise free delivery to30510; eligible items grouped over35USD.' if vendor=='Amazon' else 'Store advertises free shipping above threshold; combined listed order exceeds threshold. Not a ZIP-specific checkout quote.')))
pricedvendors={r['vendor'] for r in rows}
comparison_path=HERE/'tube-comparison-findings.json'
if comparison_path.exists():
    for i,r in enumerate(read(comparison_path)['offers']):
        if r['supplier']=='BlueSky Supplies': continue
        options.append(dict(id='TUBE-ALT-'+str(i),item=r['supplier']+': '+r['spec'],quantity=r['quantity'],unit_price=r['price_per_stick'],currency='USD',extended=r['goods_subtotal'],url=r['url'],reason=r.get('availability','')+'. '+r['qualification']+' Delivery to 30510 is unquoted. Existing $930.90 tube reference is not a lowest-price buying recommendation; no delivered saving adopted.'))
marketplace_path=HERE/'marketplace-findings.json'
if marketplace_path.exists():
    mp=read(marketplace_path)
    if mp.get('five_24ft_fit'):
        options.append(dict(id='FB-SYLVANIA',item='Marketplace Sylvania: 2 x 2 x 24 ft tube, seller describes 1/8 in wall',quantity=5,unit_price=115,currency='USD',extended=575,url='https://www.facebook.com/marketplace/item/1367277908682890/',reason='Seller advertises $115 each and 28 available; pickup in Sylvania GA. Alternate cut plan fits all 36 blanks in five bars with 3mm kerfs and 10mm total trim/bar, minimum offcut73mm. $355.90 goods difference from retail reference. Grade, actual wall (.120 versus nominal1/8), rust/coating, straightness, quantity and collection cost unverified. Conditional option only; no adopted savings.'))
covered={s['vendor'] for s in shipments}
for v in sorted(pricedvendors-covered):
    shipments.append(dict(id='SHIP-UNKNOWN-'+str(len(shipments)),vendor=v,ids=[r['id'] for r in rows if r['vendor']==v],amount_usd=None,tax_usd=None,basis='Not quoted. Blank does not mean free.'))
assert len({r['id'] for r in rows})==len(rows)
goods=money(sum(Decimal(str(r['goods_usd'])) for r in rows))
knownship=money(sum(Decimal(str(s['amount_usd'])) for s in shipments if s['amount_usd'] is not None))
amazon=money(sum(Decimal(str(r['goods_usd'])) for r in rows if r['vendor']=='Amazon'))
summary=dict(date='2026-09-24',currency='USD',destination='Alto GA30510',status='PARTIAL PRICE AUDIT — COMPLETE BUILD TOTAL UNRESOLVED',
    goods_subtotal_usd=goods,known_shipping_subtotal_usd=knownship,priced_scope_before_tax_usd=money(goods+knownship),
    amazon_goods_with_advertised_free_delivery_usd=amazon,complete_delivered_total_usd=None,purchase_release=False,
    owner_fabrication_labor_usd=0,priced_rows=len(rows),unpriced_scope_rows=len(gaps),unquoted_vendor_shipping_groups=sum(s['amount_usd'] is None for s in shipments),
    prior_estimate_with_owner_labor_usd=old['summary']['planning_total_before_tax'],unsupported_skin_allowance_removed_usd=200,
    prior_estimate_is_current=False,reason='The old estimate underpriced raw billets and omitted exact small-stock purchases; its remaining allowances and shipping reserve cannot be called actual cost.',
    orders_placed_by_agent=0,quoted_8020_order_including_estimated_tax_usd=272.11,
    exclusions=['Sales taxes and possible tariffs beyond the isolated80/20cart estimate','Unpriced required scope and unquoted shipping','Dust/fume extraction and air treatment if not already owned','Replacement cutter/torch if existing unit is incompatible','Fabrication tooling not confirmed owned','Paid CAD/CAM licenses'])
categories=[]
for c in dict.fromkeys(r['category'] for r in rows): categories.append(dict(category=c,goods_usd=money(sum(r['goods_usd'] for r in rows if r['category']==c))))
data=dict(summary=summary,rows=rows,shipping=shipments,unpriced=gaps,alternatives=options,categories=categories,
    bracket_redesign_not_adopted=metal['unadopted_plate_bracket_option'],previous_estimate=old,
    input_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*-findings.json')})
(HERE/'audit-data.json').write_text(json.dumps(data,indent=2),encoding='utf8')
# Main machine-readable budget no longer treats unpriced requirements as allowances.
(BUDGET/'budget-data.json').write_text(json.dumps({k:data[k] for k in ['summary','rows','shipping','unpriced','alternatives','categories']},indent=2),encoding='utf8')
lines=['# CNC / plasma actual-price audit','',
    f"**Recorded priced scope: ${goods:,.2f} goods + ${knownship:,.2f} known/advertised shipping = ${summary['priced_scope_before_tax_usd']:,.2f} USD before tax.**",'',
    '**The complete delivered build price is still unknown. This is not a purchase or manufacturing release.** The remaining required items are not included as zero-dollar purchases. The earlier $7,663.82 estimate is superseded; it contained allowances, omitted stock details and an arbitrary shipping reserve.', '',
    'The owner performs fabrication, machining, cutting and finishing: outside-shop labor is **$0**. This audit does not assume unconfirmed tools, stock or consumables are already owned. No orders or supplier messages were sent. Fusion remains unopened.', '',
    '## Prices that can be traced to offers','',
    '| Priced portion | Goods, before tax |','|---|---:|']
for c in categories: lines.append(f"| {c['category']} | ${c['goods_usd']:,.2f} |")
lines += ['',f"The current workbook contains **{len(rows)} priced lines**, **{len(gaps)} remaining scope entries** and a vendor-level shipping register. Every price is linked to a product or supplier. Line quantities are rounded to cents; seller checkout can differ by a cent on fractional-cent fasteners.", '',
    f"Amazon items total **${amazon:,.2f}**, with advertised free delivery to ZIP 30510 under the recorded order conditions. This includes two 1,000 mm Y modules, one 800 mm X module, the 100 mm Z, the two HGR20 rail kits, five extrusion packs, spindle kit, power supplies, cabinet, cable chains, CB1 and listed Amazon water components. These are source prices, not proof that all mounting and electrical interfaces are finished.", '',
    'The [80/20 beam](https://8020.net/40-8080.html) and [16 matching M8 nuts](https://8020.net/40-3915.html) were configured together in a ZIP-30510 cart: **$193.01 goods + $61.30 UPS Ground + $17.80 estimated tax = $272.11**. The temporary cart was cleared after recording the estimate. This tax amount applies only to that cart, not to all suppliers.', '',
    'Nutty hardware is combined into one order above its $100 advertised free-shipping threshold. No duplicate delivery charge is added for each fastener row. Other blank freight cells remain unknown.', '',
    '## Corrections to the old estimate','',
    '- Recorded the owner\'s 12 x 12 inch aluminum pieces, provisionally one at 1/2 inch and one at 3/8 inch. The 1/2 inch piece geometrically fits the Z carrier and smaller pieces. Qualifying its alloy and usable finished thickness can avoid MET08 ($58.74), giving $5,751.50 for the current incomplete priced scope. No credit is applied before qualification, and no duplicate offcut savings are counted. See [owned aluminum allocation](OWNED-ALUMINUM-FIT.md).',
    '- The $930.90 square-tube line is a high retail reference, not a lowest-price buying recommendation. Bobco posts $585.00 for six matching 20-foot A500 Grade B bars, but advertises Los Angeles pickup; Georgia delivery is unquoted. Looper\'s and YAGI comparisons have further specification/availability limits. Nearby SteelMart Gainesville and Sabel Winder require quotations. See [tube comparisons](TUBE-PRICE-COMPARISON.md).',
    '- A [Sylvania Marketplace listing](https://www.facebook.com/marketplace/item/1367277908682890/) advertises 24-foot 2 x 2 tubing for $115 each. The alternate cut proof fits all 36 blanks into five bars, giving $575 goods and a $355.90 difference from the retail reference before pickup/tax/qualification. No budget substitution is adopted until actual wall/grade/condition and collection are checked. See [Marketplace findings](MARKETPLACE-TUBING.md).',
    '- Removed the unsupported $200 decorative-skin allowance: no separate appearance panels existed in the current CAD.',
    '- Retained six full 20-foot chassis tubes because the cut plan needs them. One bar has no surplus beyond its modeled kerfs and trim; do not assume undersize or damaged stock will fit.',
    '- Kept two 4 × 8 sheets for the .120-inch water assembly. The stale third nesting DXF is excluded from the current package.',
    '- Replaced the $150 adapter-stock allowance with explicit raw-stock purchases. The unchanged billet geometry requires $813.33 of sourced aluminum stock before freight. The old allowance understated this cost. An equivalent OnlineMetals 2 x 2 x 12 inch blank replaces the prior BuyMetal source and reduces goods cost by $31.35 without a geometry change.',
    '- Counted fabricated plugs, supports and clamps as raw stock plus owner work. No shop labor is added a second time.',
    '- Kept price evidence separate from compatibility. Backorders, timer contact checks, hose restrictions and unresolved interfaces are visible rather than being assumed complete.', '',
    '## Cost reductions requiring an engineering revision','',
    'Fabricated steel gantry feet and three link brackets could avoid large billets, with a preliminary goods saving of $387.17 before changed stock, shipping and consumables. This is not applied to the current subtotal: welds, post-weld datum finishing, clearances and the roughly 3.1 kg moving-mass increase still need checking.', '',
    'The [VXB rod-end packs](https://vxb.com/products/4-male-rod-end-6mm-pos6-2-right-and-2-left-ha) are $39.98 for two packs with advertised US shipping, compared with $286.77 in SKF offers/benchmark prices. Their 9 mm ball width does not fit the current 7 mm clevis gap. The $246.79 comparison includes a $147.96 right-hand SKF benchmark already excluded from the priced subtotal. Against that subtotal, the possible change is $98.83 before changed pins/spacers, while also resolving the unpriced right-hand ends. Neither saving is credited before changing and checking the clevises, pins and shims.', '',
    'The included spindle-kit clamp may reduce custom clamp work only after its actual hole pattern, envelope and load path are established. No credit is assumed from its mere presence in the kit.', '',
    '## What prevents a real final total and CAD/CAM release','',
    '1. **Supplier dimensions and component selection:** the HMS40 base interface, rail hole pattern, Z mounting dimensions and retention, actual torch envelope, isolated controls and several finishing details remain unresolved. The existing cutter is unidentified; an AG-60 torch listing does not establish the cutter starting circuit or CNC terminals.',
    '2. **Actual metal and delivery quotations:** remaining sheets, round/hex stock, gasket material, freight and taxes lack a delivered quote. The prepared [SteelMart material quote request](STEELMART-QUOTE-REQUEST.md) has not been sent. Supplier contact requires the owner\'s authorization and reply contact details.',
    '3. **Budget-oriented design correction:** the current billet-heavy design and multiple exact metric sheet thicknesses should be simplified before purchasing. These are drawing and joint-design changes, not numerical discounts. Full cabinet service access, tool clearance and final process-specific CAM also remain open.', '',
    'The successful CAD solid/intersection checks and firmware compilation do not close those missing interfaces. Physical commissioning follows a completed design; it cannot substitute for the missing pre-order drawings.', '',
    '## Audit files','',
    '- [Metal quantities, stock sources and unsent RFQ](METAL-AUDIT.md)',
    '- [Prepared SteelMart quotation request — not sent](STEELMART-QUOTE-REQUEST.md)',
    '- [Cost-reduction decisions and stock fit proof](COSTDOWN-DECISION.md)',
    '- [Chassis cost breakdown and owned aluminum](CHASSIS-COST-EXPLAINED.md)',
    '- [Owned aluminum fit and allocation](OWNED-ALUMINUM-FIT.md)',
    '- [Square-tube price comparisons and fulfillment limits](TUBE-PRICE-COMPARISON.md)',
    '- [Georgia supplier quote candidates](TUBE-SUPPLIERS-GEORGIA.md)',
    '- [Verified Marketplace listing details and alternate cutting plan](MARKETPLACE-TUBING.md)',
    '- [Mechanical hardware and conditional alternatives](HARDWARE-AUDIT.md)',
    '- [Controls and plumbing offers](CONTROLS-AUDIT.md)',
    '- [Current machine package status](../../../output/release-review/RevE-ENGINEERING/PACKAGE-STATUS.md)', '',
    'Price evidence recorded September 24, 2026. Sales tax, possible tariffs, unpriced required scope, unquoted freight, any unowned extraction/air treatment, replacement cutter/torch, fabrication tooling and paid software are outside the priced subtotal.']
(HERE/'REAL-COST.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps(summary,indent=2))
