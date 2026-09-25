import json
from pathlib import Path
from urllib.request import urlopen

base = Path(__file__).resolve().parent
url = 'https://baomain.com/products/baomain-ah3-3-24v.js'
product = json.load(urlopen(url))
variant = next(v for v in product['variants'] if v['sku'] == 'AH3-3-24V-3Min')
assert variant['available'] and variant['price'] == 1079
evidence = {'source': url, 'observed_local_date': '2026-09-24', 'product': product['title'], 'variant': variant}
(base.parent / 'sources/Baomain-AH3-3-24V-3Min-offer.json').write_text(json.dumps(evidence, indent=2), encoding='utf8')
path = base / 'water-bom.json'
bom = json.loads(path.read_text(encoding='utf8'))
timer = next(x for x in bom['items'] if x['id'] == 'W-DRAIN-TIMER')
timer.update(description='BAOMAIN AH3-3-24V-3Min power-on-delay timer with socket, 24 VDC, 3-minute range', unit_usd=10.79, extended_usd=10.79,
             price_status='Observed manufacturer offer; exact 3Min variant available', url='https://baomain.com/products/baomain-ah3-3-24v?variant=42107472478393',
             shipping_status='Unquoted to Alto GA 30510; covered by planning reserve, not treated as free',
             notes=['Set nominally to 75 seconds, then measure and adjust to at least 60 seconds.',
                    'Three-minute range replaces the unselected six-minute-range allowance. Same control function; one timed contact plus one instantaneous contact.',
                    'Verify printed terminal diagram and timer DC contact suitability for selected low-power relay coil.'])
timer.pop('allowance_usd', None)
bom['summary'].update(observed_goods_usd=234.51, unquoted_goods_allowance_usd=174, planning_subtotal_before_tax_usd=428.51, planning_increase_usd=68.51)
bom['release_items'] = [x for x in bom['release_items'] if not x.startswith('Select exact0-6minute')]
bom['release_items'].append('Verify selected AH3-3-24V-3Min terminal diagram, low-power DC contact duty and calibrated minimum 60-second dwell')
path.write_text(json.dumps(bom, indent=2), encoding='utf8')
p=base/'WATER-CONTROL.md'
txt=p.read_text(encoding='utf8')
old='For T_DRAIN, select a24VDC power-on-delay timer with a0-6 minute range, nominally set to75 seconds and wet-calibrated to at least60 seconds. Its exactSKU remains a procurement hold in the BOM.'
new='T_DRAIN is the **BAOMAIN AH3-3-24V-3Min**, 24 VDC, three-minute range with socket, [manufacturer variant 42107472478393](https://baomain.com/products/baomain-ah3-3-24v?variant=42107472478393). Its observed price is $10.79; shipping to Alto remains unquoted. Set it nominally to 75 seconds and calibrate to at least 60 seconds. This replaces the unselected six-minute-range allowance; verify the delivered terminal diagram and the contact duty of the selected low-power coil.'
assert old in txt or new in txt
txt=txt.replace(old,new)
txt=txt.replace('The component prices below were read with Amazon delivery set to Alto, GA 30510;', 'Amazon prices were read with delivery set to Alto, GA 30510; the drain timer uses the manufacturer offer with unquoted shipping;')
txt=txt.replace('requires minimum level, bed-clear, no active transfer, and drain-close delay complete.', 'requires minimum level, no high-high condition, bed-clear, no active transfer, and drain-close delay complete.')
p.write_text(txt,encoding='utf8')
print(json.dumps(bom['summary'],indent=2))
