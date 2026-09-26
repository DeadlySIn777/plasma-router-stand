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
rows=[]; gaps=[]; options=[]; shipments=[]; superseded=[]
tubeplan=read(HERE.parents[2]/'output/release-review/RevH-CAD/tube-cut-plan.json')
assert tubeplan['stock_qty']==6 and len(tubeplan['bars'][5]['cuts'])==2 and all(c['part'].startswith('MOD_CROSSMEMBER') for c in tubeplan['bars'][5]['cuts']), 'Rev H tube plan changed: review the MET01 / MET-GAP-23 text'
def add(id,group,item,qty,unit,price,url,notes='',vendor='',shipping=None,basis='Posted price'):
    rows.append(dict(id=id,category=group,item=item,quantity=qty,unit=unit,unit_usd=price,
        goods_usd=money(Decimal(str(qty))*Decimal(str(price))),url=url,notes=notes,
        vendor=vendor_name(vendor or urlparse(url or '').netloc),shipping_usd=shipping,basis=basis))
def gap(id,item,details,quantity='',url=''):
    gaps.append(dict(id=id,item=item,quantity=str(quantity),required_work=details,url=url,unit_usd=None))
for r in core['rows']:
    if r.get('superseded'):
        superseded.append(dict(id=r['id'],item=r['item'],quantity=r['quantity'],unit_usd=r['unit_usd'],goods_usd=money(Decimal(str(r['quantity']))*Decimal(str(r['unit_usd']))),url=r['url'],reason=r['superseded'],revision='G'));continue
    oldr=byold.get(r['id'],{})
    add(r['id'],oldr.get('category','Controls'),oldr.get('item',r['item']),r['quantity'],oldr.get('unit','each'),r['unit_usd'],r['url'],r['notes'],r['vendor'],r['shipping_usd'],'Live offer 24 Sep')
    if r.get('owner_order_status'): rows[-1]['owner_order_status']=r['owner_order_status']
coreids={r['id'] for r in rows}
# Earlier same-day researched exact offers retained; related-SKU benchmarks excluded.
for id in ['H10','E10','W-AUX-RELAYS','W-DRAIN-TIMER','W-MOTOR-RELAYS']:
    r=byold[id]
    add(id,r['category'],r['item'],r['quantity'],r['unit'],r['unit_usd'],r['url'],r['notes']+' Earlier same-day offer retained; freight not yet quoted.',shipping=None)
for r in metal['published_stock_candidates']:
    if r.get('superseded'):
        superseded.append(dict(id=r['id'],item=r['item'],quantity=r['quantity'],unit_usd=r['unit_usd'],goods_usd=r['goods_usd'],url=r['url'],reason=r['superseded'],revision='G'));continue
    group=byold[r['replaces_or_contributes_to']]['category']
    add(r['id'],group,r['item'],r['quantity'],'stock piece',r['unit_usd'],r['url'],r['allocation']+' '+r['status'],shipping=None)
    if r.get('shipping_usd') is not None:
        shipments.append(dict(id='SHIP-'+r['id'],vendor=vendor_name(urlparse(r['url']).netloc),ids=[r['id']],amount_usd=r['shipping_usd'],tax_usd=None,basis=r['status']))
for i,r in enumerate(metal['quote_only_raw_stock_schedule'],1):
    # Numbered by schedule position so a retired row never renumbers the rows after it.
    if r.get('superseded'):
        superseded.append(dict(id=f'MET-GAP-{i}',item=r['item'],quantity=r['quantity'],unit_usd=None,goods_usd=None,url='',reason=r['superseded'],revision='H'));continue
    gap(f'MET-GAP-{i}',r['item'],r['size']+'. '+r['required_for'],r['quantity'])
for r in metal.get('additional_retail_offers',[]):
    options.append(dict(id=r['id'],item=r['item'],quantity=r['quantity'],unit_price=r['unit_usd'],currency='USD',extended=r['goods_usd'],url=r['url'],reason=r['price_evidence']+' '+r['fulfillment_status']+' '+r['allocation']))
for r in hardware['offers']:
    if r['id']=='T1': continue # exact same 80/20 hardware already included
    comp=r.get('compatibility','')
    if r.get('superseded_by_rev_g') or r.get('superseded_by_rev_h'):
        rev='H' if r.get('superseded_by_rev_h') else 'G'
        superseded.append(dict(id='HW-'+r['id'],item=r['item'],quantity=r['buy_quantity'],unit_usd=r['unit_usd'],goods_usd=r['goods_usd'],url=r['url'],reason=r.get('superseded_by_rev_h') or r['superseded_by_rev_g'],revision=rev));continue
    selected=(r['id'] in ['N1','N3','N4','N5'] or r.get('accepted_current_design',False))
    if selected:
        add('HW-'+r['id'],'Standard hardware',r['item'],r['buy_quantity'],('pack of '+str(r['pack_size'])) if r.get('pack_size',1)>1 else 'each',r['unit_usd'],r['url'],comp,r['vendor'])
    else:
        options.append(dict(id='HW-'+r['id'],item=r['item'],quantity=r['buy_quantity'],unit_price=r.get('unit_usd'),currency='USD',extended=r.get('goods_usd'),url=r.get('url',''),reason=comp))
for r in hardware['audits']:
    if r['budget_id'] in ['H01','H05','H10','H11']: continue
    gap('HW-GAP-'+r['budget_id'],r.get('item') or byold[r['budget_id']]['item'],r['finding'])
options.append(dict(id='OWN-AL-12',item='Owner aluminum: one 12 x 12 x 1/2 in plate and one 12 x 12 x 3/8 in plate (quantity assumed)',quantity=2,unit_price=0,currency='USD',extended=0,url='User-reported stock, 24 September 2026',reason='Acquisition cost $0 for existing pieces. Alloy and usable finished thickness unverified. The 1/2 in plate can replace MET08 Z-carrier stock, conditionally avoiding $58.74; MET08 remains in current subtotal until qualified. Other small parts fit but already use paid-stock offcuts, so no extra saving. The 3/8 in plate is unallocated; no redesign saving assumed. See OWNED-ALUMINUM-FIT.md.'))
for r in controls['rows']:
    if r.get('superseded'):
        superseded.append(dict(id=r['id'],item=r['item'],quantity=r['qty'],unit_usd=r['unitprice'],goods_usd=r.get('extended'),url=r.get('source',''),reason=r['superseded'],revision='G'));continue
    if r.get('status')=='candidate_not_adopted' or r.get('currency','USD')!='USD':
        options.append(dict(id=r['id'],item=r['item'],quantity=r['qty'],unit_price=r['unitprice'],currency=r.get('currency','USD'),extended=r.get('extended'),url=r.get('source',''),reason=r['fitproof']+' '+' '.join(r.get('openitems',[]))))
    elif r.get('unitprice') is not None and r['unitprice']>0:
        add(r['id'],'Controls and water wiring',r['item'],r['qty'],'pack / each',r['unitprice'],r.get('source',''),r['fitproof']+' '+' '.join(r.get('openitems',[])),r.get('shipping',{}).get('vendor_group',''))
    elif r.get('unitprice') is None:
        gap(r['id'],r['item'],r['fitproof']+' '+' '.join(r.get('openitems',[])),r['qty'],r.get('source',''))
# Scope not fully represented in subordinate price audits.
for id,details in [
 ('E08','Arc-voltage sensing for the Rodent route (owner decision 26 Sep 2026): no external THC box. The owned Mesa THCAD-300 feeds grblHAL internal THC, which needs the ten-resistor -10 conversion, an external high-voltage divider for an HF-start cutter, and the unfinished THCAD counter firmware. Parts unpriced; cutter start method and sensing connections unverified.'),
 ('E11','Exact bed/guard/head confirming mechanisms and switch actuation remain to be selected; price cannot be completed from a generic switch allowance.'),
 ('E22','Spindle VFD control for the Rodent route: RS485 Modbus link from the Rodent to the spindle-kit VFD. Confirm the VFD RS485 terminals and protocol, cable and termination, and define fail-off behavior on link loss.'),
 ('MET-DATUM','Rail datum raw-stock cleanup allowance needs confirmation; the nominal 5/16in offer may need thicker stock to produce a flat finished datum.')]:
    gap(id,byold.get(id,{}).get('item',id),details)
gap('H-GALV','Hot-dip galvanizing, Rev H bed module','About 32 kg of steel: rails, crossmembers, end plates, caps, lugs and sleeves welded as one module. Vent and drain holes as agreed with the galvanizer; a minimum lot charge usually governs. Unquoted.',1)
for s in core['shipping_groups']:
    shipments.append(dict(id='SHIP-8020',vendor=s['vendor'],ids=s['ids'],amount_usd=s['shipping_usd'],tax_usd=s['tax_estimate_usd'],basis=s['basis']))
nuttygoods=money(sum(r['goods_usd'] for r in rows if r['vendor']=='Nutty'))
nuttyship=0 if nuttygoods>=100 else 10.95
nuttybasis=('Goods are above $100 and qualify for free shipping.' if nuttyship==0 else f'Goods ${nuttygoods:,.2f} are below the $100 free-shipping threshold, so the published $10.95 flat rate applies unless the unpriced Rev H stainless fasteners are added to this order.')
shipments.append(dict(id='SHIP-NUTTY',vendor='Nutty',ids=[r['id'] for r in rows if r['vendor']=='Nutty'],amount_usd=nuttyship,tax_usd=None,basis='Published US48 eligible-merchandise policy; one order. '+nuttybasis+' Each line rounded to cents; checkout may round fractions of a cent differently. Stock and tax not confirmed.'))
for vendor in ['Amazon','BIQU','AutomationDirect']:
    if not any(r['vendor']==vendor for r in rows): continue
    shipments.append(dict(id='SHIP-'+vendor,vendor=vendor,ids=[r['id'] for r in rows if r['vendor']==vendor],amount_usd=0,tax_usd=None,basis=('Amazon product pages advertise free delivery to30510; eligible items grouped over35USD.' if vendor=='Amazon' else 'Store advertises free shipping above threshold; combined listed order exceeds threshold. Not a ZIP-specific checkout quote.')))
pricedvendors={r['vendor'] for r in rows}
met01=next(r for r in rows if r['id']=='MET01')
comparison_path=HERE/'tube-comparison-findings.json'
if comparison_path.exists():
    for i,r in enumerate(read(comparison_path)['offers']):
        if r['supplier']=='BlueSky Supplies': continue
        options.append(dict(id='TUBE-ALT-'+str(i),item=r['supplier']+': '+r['spec'],quantity=r['quantity'],unit_price=r['price_per_stick'],currency='USD',extended=r['goods_subtotal'],url=r['url'],reason=r.get('availability','')+'. '+r['qualification']+f" Delivery to 30510 is unquoted. Existing ${met01['goods_usd']:,.2f} tube reference is not a lowest-price buying recommendation; no delivered saving adopted."))
marketplace_path=HERE/'marketplace-findings.json'
if marketplace_path.exists():
    mp=read(marketplace_path)
    if mp.get('five_24ft_fit'):
        options.append(dict(id='FB-SYLVANIA',item='Marketplace Sylvania: 2 x 2 x 24 ft tube, seller describes 1/8 in wall',quantity=5,unit_price=115,currency='USD',extended=575,url='https://www.facebook.com/marketplace/item/1367277908682890/',reason='Seller advertises $115 each and 28 available; pickup in Sylvania GA. The recorded five-bar cut proof was made for the Rev E 36-blank schedule; the current Rev H 32-blank schedule has not been re-proved for 24 ft bars, so the quantity shown is that superseded proof. Grade, actual wall (.120 versus nominal1/8), rust/coating, straightness, quantity and collection cost unverified. Conditional option only; no adopted savings.'))
covered={s['vendor'] for s in shipments}
for v in sorted(pricedvendors-covered):
    shipments.append(dict(id='SHIP-UNKNOWN-'+str(len(shipments)),vendor=v,ids=[r['id'] for r in rows if r['vendor']==v],amount_usd=None,tax_usd=None,basis='Not quoted. Blank does not mean free.'))
assert len({r['id'] for r in rows})==len(rows)
sup_g=[r for r in superseded if r['revision']=='G']; sup_h=[r for r in superseded if r['revision']=='H']
goods=money(sum(Decimal(str(r['goods_usd'])) for r in rows))
knownship=money(sum(Decimal(str(s['amount_usd'])) for s in shipments if s['amount_usd'] is not None))
amazon=money(sum(Decimal(str(r['goods_usd'])) for r in rows if r['vendor']=='Amazon'))
summary=dict(date='2026-09-24',currency='USD',destination='Alto GA30510',status='PARTIAL PRICE AUDIT — COMPLETE BUILD TOTAL UNRESOLVED',
    design_revision='GM1 Rev H working design (bed re-baselined 26 Sep 2026)',
    goods_subtotal_usd=goods,known_shipping_subtotal_usd=knownship,priced_scope_before_tax_usd=money(goods+knownship),
    amazon_goods_with_advertised_free_delivery_usd=amazon,complete_delivered_total_usd=None,purchase_release=False,
    owner_fabrication_labor_usd=0,priced_rows=len(rows),unpriced_scope_rows=len(gaps),unquoted_vendor_shipping_groups=sum(s['amount_usd'] is None for s in shipments),
    prior_estimate_with_owner_labor_usd=old['summary']['planning_total_before_tax'],unsupported_skin_allowance_removed_usd=200,
    prior_estimate_is_current=False,reason='The old estimate underpriced raw billets and omitted exact small-stock purchases; its remaining allowances and shipping reserve cannot be called actual cost.',
    orders_placed_by_agent=0,owner_reported_orders=[r['id'] for r in rows if r.get('owner_order_status')],quoted_8020_order_including_estimated_tax_usd=272.11,
    exclusions=['Sales taxes and possible tariffs beyond the isolated80/20cart estimate','Unpriced required scope and unquoted shipping','Dust/fume extraction and air treatment if not already owned','Replacement cutter/torch if existing unit is incompatible','Fabrication tooling not confirmed owned','Paid CAD/CAM licenses'])
categories=[]
for c in dict.fromkeys(r['category'] for r in rows): categories.append(dict(category=c,goods_usd=money(sum(r['goods_usd'] for r in rows if r['category']==c))))
data=dict(summary=summary,rows=rows,shipping=shipments,unpriced=gaps,alternatives=options,categories=categories,
    superseded_offers=superseded,
    bracket_redesign_not_adopted=metal['unadopted_plate_bracket_option'],previous_estimate=old,
    input_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*-findings.json')})
(HERE/'audit-data.json').write_text(json.dumps(data,indent=2),encoding='utf8')
# Main machine-readable budget no longer treats unpriced requirements as allowances.
(BUDGET/'budget-data.json').write_text(json.dumps({k:data[k] for k in ['summary','rows','shipping','unpriced','alternatives','categories']},indent=2),encoding='utf8')
lines=['# GM1 — Garcia Mechanical Table: actual-price audit','',
    f"**Recorded priced scope: ${goods:,.2f} goods + ${knownship:,.2f} known/advertised shipping = ${summary['priced_scope_before_tax_usd']:,.2f} USD before tax.**",'',
    '**The complete delivered build price is still unknown. This is not a purchase or manufacturing release.** The remaining required items are not included as zero-dollar purchases. The earlier $7,663.82 estimate is superseded; it contained allowances, omitted stock details and an arbitrary shipping reserve.', '',
    'The owner performs fabrication, machining, cutting and finishing: outside-shop labor is **$0**. This audit does not assume unconfirmed tools, stock or consumables are already owned. No orders or supplier messages were sent. Fusion remains unopened.', '',
    '## Prices that can be traced to offers','',
    '| Priced portion | Goods, before tax |','|---|---:|']
for c in categories: lines.append(f"| {c['category']} | ${c['goods_usd']:,.2f} |")
lines += ['',f"The current register contains **{len(rows)} priced lines**, **{len(gaps)} remaining scope entries** and a vendor-level shipping register. Every price is linked to a product or supplier. Line quantities are rounded to cents; seller checkout can differ by a cent on fractional-cent fasteners.", '',
    f"Amazon items total **${amazon:,.2f}**, with advertised free delivery to ZIP 30510 under the recorded order conditions. This includes two 1,000 mm Y modules, one 800 mm X module, the 100 mm Z, the two HGR20 rail kits, five extrusion packs, spindle kit, power supplies, cabinet, cable chains and listed Amazon water components. These are source prices, not proof that all mounting and electrical interfaces are finished.", '',
    'The [80/20 beam](https://8020.net/40-8080.html) and [16 matching M8 nuts](https://8020.net/40-3915.html) were configured together in a ZIP-30510 cart: **$193.01 goods + $61.30 UPS Ground + $17.80 estimated tax = $272.11**. The temporary cart was cleared after recording the estimate. This tax amount applies only to that cart, not to all suppliers.', '',
    ('Nutty hardware is combined into one order above its $100 advertised free-shipping threshold.' if nuttyship==0 else f'Nutty hardware is combined into one order of ${nuttygoods:,.2f}, below its $100 free-shipping threshold, so the $10.95 flat rate is included; adding the unpriced Rev H stainless fasteners to this order may remove it.')+' No duplicate delivery charge is added for each fastener row. Other blank freight cells remain unknown.', '',
    *(['**Ordered by the owner:** '+'; '.join(f"{r['id']} {r['item']}, {r['owner_order_status']}" for r in rows if r.get('owner_order_status'))+'. Listed prices stay in this register until the price paid is recorded. See the [drive-module receiving check](../../../output/receiving/MOTION-MODULES.md).', ''] if any(r.get('owner_order_status') for r in rows) else []),
    '## Corrections to the old estimate','',
    f'- Recorded the owner\'s 12 x 12 inch aluminum pieces, provisionally one at 1/2 inch and one at 3/8 inch. The 1/2 inch piece geometrically fits the Z carrier and smaller pieces. Qualifying its alloy and usable finished thickness can avoid MET08 ($58.74), giving ${summary["priced_scope_before_tax_usd"]-58.74:,.2f} for the current incomplete priced scope. No credit is applied before qualification, and no duplicate offcut savings are counted. See [owned aluminum allocation](OWNED-ALUMINUM-FIT.md).',
    f'- The ${met01["goods_usd"]:,.2f} square-tube line is a high retail reference, not a lowest-price buying recommendation. Bobco posts ${97.5*met01["quantity"]:,.2f} for {met01["quantity"]} matching 20-foot A500 Grade B bars, but advertises Los Angeles pickup; Georgia delivery is unquoted. Looper\'s and YAGI comparisons have further specification/availability limits. Nearby SteelMart Gainesville and Sabel Winder require quotations. See [tube comparisons](TUBE-PRICE-COMPARISON.md).',
    '- A [Sylvania Marketplace listing](https://www.facebook.com/marketplace/item/1367277908682890/) advertises 24-foot 2 x 2 tubing for $115 each. Its recorded cut proof (five bars, $575) was made for the Rev E 36-blank schedule and has not been redone for the Rev H 32 blanks. No budget substitution is adopted until the cut proof, actual wall/grade/condition and collection are checked. See [Marketplace findings](MARKETPLACE-TUBING.md).',
    '- Removed the unsupported $200 decorative-skin allowance: no separate appearance panels existed in the current CAD.',
    f'- Rev H needs {tubeplan["part_count"]} square-tube blanks (RevH-CAD/tube-cut-plan.json). Five full 20-foot bars (MET01) take {sum(len(b["cuts"]) for b in tubeplan["bars"][:5])} of them, and one 8 ft length (MET-GAP-23) takes the last two module crossmembers; the plan as written would buy a {tubeplan["stock_qty"]}th full bar instead. The smallest remainder on the full bars is {min(b["offcut_mm"] for b in tubeplan["bars"][:5]):g} mm beyond modeled kerfs and trim; do not assume undersize or damaged stock will fit.',
    '- Kept two 4 × 8 sheets for the .120-inch water assembly. The stale third nesting DXF is excluded from the current package.',
    '- Replaced the $150 adapter-stock allowance with explicit raw-stock purchases. The unchanged billet geometry requires $813.33 of sourced aluminum stock before freight. The old allowance understated this cost. An equivalent OnlineMetals 2 x 2 x 12 inch blank replaces the prior BuyMetal source and reduces goods cost by $31.35 without a geometry change.',
    '- Counted fabricated plugs, supports and clamps as raw stock plus owner work. No shop labor is added a second time.',
    '- Kept price evidence separate from compatibility. Backorders, timer contact checks, hose restrictions and unresolved interfaces are visible rather than being assumed complete.', '',
    '## Rev H re-baseline, 26 September 2026','',
    "GM1 Rev H replaces the Rev G bed with the owner's one-piece, hoist-lifted, waterproof module (`output/release-review/RevH-CAD/`). The rest of the machine is unchanged. "+f"The bed rows now follow the Rev H cut list. {len(sup_h)} Rev G bed items left the register and stay as dated evidence (`superseded_offers`, revision H): "+', '.join(r['id']+(f" ${r['goods_usd']:,.2f}" if r['goods_usd'] is not None else ' (was unpriced)') for r in sup_h)+'. N1 is now 48 stainless square nuts, and B01 stays at five two-packs (nine 1,197 mm profiles plus one spare bar).', '',
    'New unpriced Rev H scope:', '',
    '- 3/4 in HDPE sheet (MET-GAP-20)',
    '- 3 mm stainless for the bolt tray (MET-GAP-21)',
    '- 3/8 x 4 in bar for the lift lugs (MET-GAP-22)',
    '- one 8 ft 2 x 2 tube (MET-GAP-23)',
    '- galvanizing (H-GALV)',
    '- the stainless module hardware (HW-GAP-H06, H07, H08)', '',
    'The owner\'s overhead beam, trolley, hoist, sling, shackles and module stand stay outside the register. Part-by-part changes are in [REVH-PROCUREMENT-DELTA.md](REVH-PROCUREMENT-DELTA.md).', '',
    '`check_revg_stock_fit.py --cad RevH-CAD` (`revh-stock-fit.json`) packs the Rev H flat parts onto the registered sizes. Every sheet and plate row covers its parts, including the 6 mm plate that was short for Rev G. The one exception is the 3/8 in plate, which would need 12 x 36 in with the lugs; the lugs therefore get their own bar. **The lower subtotal is NOT a cheaper build**, because the new Rev H items are unpriced.', '',
    '## Rev G reconciliation, 26 September 2026 (bed rows since re-baselined to Rev H)','',
    f"Quantities were reconciled with the Rev G cut list (`output/release-review/RevG-CAD/cutlist.json`) and the owner's controller decision. {len(sup_g)} offers are no longer priced and are kept as dated evidence in `audit-data.json` (`superseded_offers`): "+', '.join(f"{r['id']} ${r['goods_usd']:,.2f}" for r in sup_g)+'. The controller items went because the owner chose BTT Rodent + grblHAL on 26 September 2026 (the owner already owns a Kraken); the Rodent board itself is unpriced (CA-RODENT). At Rev G, MET01 was five 20 ft tubes (30 blanks), MET02 three 8 ft bars (the controls cage raised the 1 x 1 tube list to 7,730 mm), square nuts 96, spoilboard screws 25 and M8x80 drawdowns 10 (Nutty minimums).', '',
    '`check_revg_stock_fit.py` packs the actual Rev G flat parts onto each registered sheet and plate size (`revg-stock-fit.json`). Every existing row covers its parts except the 6 mm plate, where two tool cradles do not fit; the 3/4 in MDF spoilboards now need only a half sheet. Two thicknesses had no row at all: 2 mm steel rack guides and 3/8 in aluminum panel ties. Those, the extra 6 mm plate, the sleeve round bar and the 30 x 30 x 3 rack-fork tube are listed as remaining scope, as are the Rev G screws, washers and locator pins without an offer. The lower subtotal is therefore NOT a cheaper Rev G build.', '',
    '**The Excel workbook has not been regenerated.** `build_budget.mjs` needs the private `@oai/artifact-tool` runtime, which is not in this repository. Until it is rebuilt, `budget-data.json`, `audit-data.json` and this page are current; the workbook still shows Rev E quantities.', '',
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
