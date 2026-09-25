"""Machine-readable companion to metals_research.md; USD public observations."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
prices=[]
def price(id, supplier, description, unit, qty, url, match='exact', notes='', shipping=None, observed='direct page'):
    prices.append(dict(id=id,supplier=supplier,description=description,unit_price_usd=unit,
                       purchase_quantity=qty,extended_usd=round(unit*qty,2) if unit is not None and qty is not None else None,
                       url=url,match=match,notes=notes,shipping_usd=shipping,
                       delivery_to_30510='Unquoted/unconfirmed',evidence=observed))

price('tube_local_benchmark','Looper’s Metal Works','2 x 2 11-gauge tube, 20 ft',80.60,5,'https://www.loopersmetalworks.com/metal-products/',
      'confirm actual .120 wall','Oklahoma stock-price benchmark dated2026-09-17; cuts $3 each; not Georgia delivered price.')
price('tube_bobco_benchmark','Bobco','2 x 2 x .120 A500B tube, 20 ft',97.50,5,
      'https://www.bobcometal.com/hot-rolled-steel-square-tube-2-inch-x-0-12.html',
      notes='Los Angeles pickup listing; freight to Georgia unknown.',observed='supplier search-index listing; direct open403')
price('tube_olm20','Online Metals','2 x 2 x .120 A500/A513 tube, 20 ft',202.30,5,
      'https://www.onlinemetals.com/en/buy/carbon-steel/2-x-0-12-carbon-steel-square-tube-a500-a513-hot-rolled/pid/10343',
      notes='Confirm actual supplied ASTM grade; processing and freight extra.')
price('tube_olm12','Online Metals','2 x 2 x .120 A500/A513 tube, 12 ft',100.72,9,
      'https://www.onlinemetals.com/en/buy/carbon-steel/2-x-0-12-carbon-steel-square-tube-a500-a513-hot-rolled/pid/10343',
      notes='Alternative stock nesting, not additional to five20ft bars.')
price('panel_tube_metric','Parker Steel / Metric Metal','25 x 25 x 2 metric square tube cut list',None,1,
      'https://www.metricmetal.com/wp-content/uploads/2024/05/RG-201123-FULL-CATALOG-COMPRESSED.pdf',
      notes='Catalog lists size,1.442kg/m; current stock, length options and price require quote.',observed='official catalog')
price('panel_tube_imperial','Online Metals / A-Z Metals','1 x 1 x .083 tube, 60 inches',15.58,9,
      'https://www.onlinemetals.com/en/buy/carbon-steel/1-inch-x-083-inch-carbon-steel-square-tube-a500-a513/pid/mp-00064364',
      'dimensional substitution','25.4mm external,2.1082mm wall; changes innercuts to346.2mm and stack+.4mm. Page says2business-day ship lead fromMesaAZ; arrival unknown.')
price('brace_angle_imperial','Steel Supply LP','1.25 x 1.25 x .125 angle, 20 ft',24.19,1,
      'https://www.steelsupplylp.com/sku/100002','dimensional substitution',
      '31.75 x31.75 x3.175 differs from30 x30 x3. Freight shipment; page stock messaging ambiguous.')
price('pan_slat_sheet_benchmark','Looper’s Metal Works','11-gauge 4 x 8 ft raw steel sheet',173.60,2,
      'https://www.loopersmetalworks.com/metal-products/','dimensional substitution',
      'Oklahoma benchmark; confirm wall for3mm design. Separate pan/slat nesting. Shearing, bending, welding, fittings and leak test extra.')
price('slat_flat_alternative','Online Metals','3 x 1/8 inch flat bar, 72 inches',18.14,10,
      'https://www.onlinemetals.com/en/buy/carbon-steel/0-125-x-3-carbon-steel-rectangle-bar-commercial-quality-hot-rolled/pid/10007',
      'dimensional substitution','Yields20 x880mm slats including one spare;76.2mm high x3.175 thick requires dimensional adjustment. Alternative to sheet-cut slats.')
price('panel_al_8mm','Online Metals','8mm5754 plate, 24 x36 inches',902.42,3,
      'https://www.onlinemetals.com/en/buy/aluminum/8mm-aluminum-plate-grade-5754/pid/29508',
      'exact thickness; alloy and flatness pending','Three blanks yield two panels each. Public high-cost comparison; obtain local finished-blank quote first.')
price('panel_al_5_16','Online Metals','5/16-inch6061-T651 plate, 48 x48 inches',759.54,1,
      'https://www.onlinemetals.com/en/buy/aluminum/0-3125-aluminum-plate-6061-t651/pid/14480',
      'dimensional substitution','7.9375mm vs8mm; six panels nest2 x3. Latest directly readable759.54 supersedes indexed915.25. Cutting and datum finishing extra.')
price('gantry_8080','80/20','40-8080 standard extrusion, cut1200mm',151.73,1,
      'https://8020.net/40-8080.html',notes='Calculated from0.1231USD/mm plus4.01cut.6063-T6,Ix=Iy171.6341cm4,about7.64kg for1200mm. Shipping,taps/machining extra.')
price('skins_al_bci','BCI Imaging Supplies','.080-inch5052-H32, 48 x96 inches',510.00,1,
      'https://bciimage.com/product/aluminium-sheet-080-5052-h32-0-08-x-48-x-96/',
      '2.032mm near-size stock','For external faces only pending final unfolded shapes. Supplier says oversized shipping requires quote; not free delivery.')
price('skins_al_benchmark','Looper’s Metal Works','.080-inch5052, 4 x10 ft sheet',254.64,1,
      'https://www.loopersmetalworks.com/metal-products/','2.032mm near-size stock',
      'Oklahoma raw material benchmark; fabrication and freight extra; availability to confirm.')
price('mdf','Home Depot','3/4-inch MDF nominal4 x8 ft actual49 x97 inches',None,1,
      'https://www.homedepot.com/p/309177124','19.05mm near-size stock',
      'No price observable; store stock and pickup/delivery price to confirm. One sheet yields six plus spares.')

takeoff=[
 ('top_y_tubes','2 x2 x.120 steel tube',2,[1450]),
 ('receiver_ledgers','2 x2 x.120 steel tube',2,[1450]),
 ('legs','2 x2 x.120 steel tube',6,[949.2]),
 ('lower_side_ties','2 x2 x.120 steel tube',4,[648.8]),
 ('end_ties','2 x2 x.120 steel tube',4,[1048.4]),
 ('pan_bearer_tubes','2 x2 x.120 steel tube',3,[1032.4]),
 ('bridge_tube_blanks','2 x2 x.120 steel tube',8,[1032]),
 ('panel_long_members','25 x25 x2 steel tube',12,[497]),
 ('panel_short_members','25 x25 x2 steel tube',18,[347]),
 ('side_braces_front','30 x30 x3 steel angle',2,[907.331]),
 ('side_braces_rear','30 x30 x3 steel angle',2,[904.060]),
 ('rear_brace','30 x30 x3 steel angle',1,[1206.493]),
 ('rail_caps','steel plate',2,[1450,100,8]),
 ('beam_diaphragms','steel plate',8,[101.6,50.8,6]),
 ('base_plates','steel plate',6,[80,80,12]),
 ('deck_subplates','aluminum; alloy and flatness to specify',6,[497,397,8]),
 ('deck_mdf','MDF',6,[497,397,19]),
 ('gantry_extrusion','documented standard8080 aluminum extrusion',1,[1200]),
 ('slats','steel sheet',19,[880,75,3]),
 ('pan','fabricated3mmsteel; external envelope',1,[920,1200,100]),
 ('reservoir','compatible vented material; internal envelope',1,[900,500,350]),
 ('front_light_covers','1.5–2mm flangedAl; nominalface; thicknessvisual ignored',2,[503,566]),
 ('side_skins','1.5–2mm flangedAl; nominalface',4,[615,498]),
]
unknown=[
 {'id':'pan_bearer_end_plates','qty':6,'material':'8mm steel','status':'outline,bolts,fitclearance unresolved'},
 {'id':'beam_riser_feet','qty':8,'finished_rise_mm':30,'render_envelope_mm':[40,90,30],'status':'finalconstruction/contactpads unresolved; do not assume solid blocks'},
 {'id':'rack_cabinet_supports','qty':1,'clear_space_mm':[1005,550,680],'status':'loadbearingrackcrossmembers separate from light skins; fabricationquote'},
 {'id':'cabinet_liners_shields','qty':1,'status':'unfoldedblanks/area unresolved; no5mmcabinet counted'},
 {'id':'reservoir_fabrication','qty':1,'status':'wallmaterial/thickness,baffles,sump,lid,vent,fittings,shelf unspecified'},
 {'id':'interface_plates_hardware','qty':None,'status':'gantryheadadapters,receiverseats,datum pads,gussets,caps,bungs,locators,clamps and fasteners pending drawings'},
 {'id':'finish_fabrication','qty':1,'status':'cuts,welding,datum finishing,panleaktest,powdercoat/paint remain quote-required'},
 {'id':'shipping_tax','qty':1,'status':'no supplier freight amount to30510 obtained; not zero'}
]
data={'revision':'C','observed_date':'2026-09-24','currency':'USD','destination':'Alto, Georgia30510',
      'status':'Source-backed takeoff and price benchmarks, not released drawings or delivered quotations',
      'amazon_first':'Searched first; no verified exact1200mm standard8080 or497x397x8mmplate price obtained',
      'takeoff':[dict(id=i,material=m,quantity=q,dimensions_mm=d) for i,m,q,d in takeoff],
      'stationary_2in_tube_m':18.284,'total_2in_tube_m':29.6372,'panel_25mm_tube_m':12.210,
      'brace_angle_centerline_m':4.829275925459,'sand_kg_estimate':58,
      'stock_nesting_file':'cut_stock_check.json','price_options':prices,'unpriced_or_unreleased':unknown,
      'regional_suppliers':[
       {'name':'SteelMart Gainesville','url':'https://steelmartatlanta.com/steelmart-gainesville-ga/','address':'455 Industrial Boulevard,GainesvilleGA30501','phone':'770-297-6675','price':'quote required','fulfillment':'willcall,countercuts,deliveryoffered;Altochargeunconfirmed'},
       {'name':'Metal Supermarkets Buford','url':'https://www.metalsupermarkets.com/location/buford/','address':'4908 Golden Parkway,Suite400,BufordGA30518','price':'quote required','fulfillment':'cut-to-size;Corneliainservicearea;Altochargeunconfirmed'},
       {'name':'Cherokee Steel','url':'https://cherokeesteel.com/','address':'196 Leroy Anderson Road,MonroeGA30655','phone':'770-207-4621','price':'quote required','fulfillment':'bandsaw,platesaw,waterjet;freightunconfirmed'}],
      'total_price':None,'total_note':'Alternative rows must not be added together; incomplete fabrication and freight scope.'}
data['procurement_addendum']={
 'title':'US-stock procurement adjustments to Rev C',
 'status':'Procurement adaptation for quoting; original concept drawings unchanged',
 'preferred_quote_route':'Local cut-to-size stock; quote both metric original and US-stock adaptation. No local dollar allowance represented as a supplier quote.',
 'panel_tube':{'section_in':[1,1,.083],'quantity_long':12,'long_cut_mm':497,'quantity_short':18,'short_cut_mm':346.2,'net_length_m':12.1956},
 'panel_subplate_mm':[497,397,7.9375],
 'mdf_nominal_mm':[497,397,19.05],
 'panel_raw_stack_mm':52.3875,'router_top_before_skim_mm':973.1875,
 'rail_cap':{'quantity':2,'nominal_dimensions_mm':[1450,100,7.9375],'cap_datum_delta_mm':-.0625},
 'unknowns':'Actual stock tolerances, finished geometry, bed skim, contact sleeves/clamps and complete tool clearance require verification.',
 'metric_8mm5754_price_role':'Rejected high-price benchmark, excluded from proposed purchasing subtotal',
 'small_tube_stock_options':'Prefer2 x24ft if stocked; or2 x20ft plus a short drop. Do not silently use only2 x20ft:12.1956m finished still exceeds12.192m before kerf.'}
(ROOT/'metals_research.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
print(ROOT/'metals_research.json')
