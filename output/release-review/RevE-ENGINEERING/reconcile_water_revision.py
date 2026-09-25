"""Update water procurement metadata to the current shallow-tank design."""
from pathlib import Path
import json

here = Path(__file__).parent
p = here / 'water-bom.json'
b = json.loads(p.read_text(encoding='utf8'))
b['reservoir_gross_litres'] = 135
b['reservoir_internal_mm'] = [900, 600, 250]
b['reservoir_low_trip_above_floor_mm'] = 55
b['reservoir_pickup_axis_above_floor_mm'] = 25
b['reservoir_overflow_crest_above_floor_mm'] = 242
selection = json.loads((here/'electrical-selection.json').read_text(encoding='utf8'))
for item in b['items']:
    if item['id'] == 'W-AUX-RELAYS':
        item.update(description='Finder 40.52.9.024.0000 DPDT 24 VDC relay with 95.05 DIN socket',
            quantity=6, unit_usd=14.87, extended_usd=89.22, shipping_usd=None,
            price_status='Observed distributor relay plus associated socket',
            shipping_status='Shipping to 30510 unquoted',
            url='https://www.digikey.com/en/products/detail/finder-relays-inc/40-52-9-024-0000/10055849')
        item.pop('allowance_usd',None)
        item['used_quantity'] = 6
        item['spare_quantity'] = 0
        item['notes'] = [
            'K_ARM, K_FILL, K_DRAIN, K_MIN, K_EMPTY, K_READY. Published nominal coil current 27 mA; IEC terminal allocation in WATER-ELECTRICAL-REVIEW.md.',
            'K_ARM requires release of the FILL button before restarting after loss of FILL_ALLOWED.',
            'No pump load is switched by these auxiliary contacts; controller-interface wetting current remains a design item.'
        ]
    elif item['id'] == 'W-MOTOR-RELAYS':
        item.update(description='Carlo Gavazzi RM1D060D20 DC solid-state pump switch',
            quantity=2, unit_usd=66.50, extended_usd=133.00, shipping_usd=None,
            price_status='Observed distributor exact MPN', shipping_status='Shipping to 30510 unquoted',
            url='https://www.digikey.com/en/products/detail/carlo-gavazzi-inc/RM1D060D20/13277978',
            notes=['Two series devices, 20 A continuous subject to thermal conditions, 30 A for 1 second repetitive overload.',
                   'Required motor flyback diode, heat-dissipating mounting and measured pump inrush verification. Not a service isolator.'])
        item.pop('allowance_usd',None)
    elif item['id'] == 'W-BRANCH-WIRING':
        item['allowance_usd']=45
        item['description']='Specified branch fuse holders/fuses, MBR20100CTG, ten 1N4007-E3/54, terminals, cable and glands'
        item['notes']=['Exact small-parts quantities in electrical-selection.json; unquoted $45 lot allowance supersedes $22 placeholder.',
                       'No duplicate main E-stop, enclosure, DIN rail, contactor or controller isolation charge. Pump fuse starts at 10 A conductor protection; actual pump instruction and inrush still require checking.']
    elif item['id'] == 'W-WATER-BUTTONS':
        item['description'] = 'Guarded momentary FILL with linked NO+NC contacts, NC STOP, guarded AUTO/DRAIN override and labels'
b['release_items'] = [
    'Complete shared selector/contact-block and isolation-interface selection and physical panel layout using the defined terminal allocation.',
    'Confirm AH3-3 DC contact suitability or substitute a documented timer; terminal mapping is now sourced.',
    'Verify pump fuse instructions, actual inrush waveform, SSR thermal mounting, supply recovery and suppression heating.',
    'Define B_CLEAR/B_LOCK keyed confirmation or sensing contacts and their mounting; do not claim automatic fastener-preload verification.',
    'Verify selected fittings, hose pressure ratings, adjustable assembly lengths and shipping.',
    'Measure actual fabricated volume and verify the visible overflow vessel; conservative modeled internal-solid displacement 0.592 L is below the 1 L reserve.',
    'Subsequent commissioning: wet-calibrate floats; test overflow, all-return, stop chain, held-button restart prevention and thermal performance.',
    'Calibrate the three-minute drain timer to at least 60 seconds; verify short interruption and held-button behavior.'
]
b['summary']['observed_goods_usd']=round(sum(i.get('extended_usd',0) for i in b['items']),2)
b['summary']['unquoted_goods_allowance_usd']=round(sum(i.get('allowance_usd',0) for i in b['items']),2)
b['summary']['planning_subtotal_before_tax_usd']=round(b['summary']['observed_goods_usd']+b['summary']['unquoted_goods_allowance_usd']+b['summary']['unquoted_shipping_reserve_usd'],2)
b['summary']['planning_increase_usd']=round(b['summary']['planning_subtotal_before_tax_usd']-b['summary']['previous_allowance_usd'],2)
selection['status']='Selected in master water BOM; terminal allocation documented, shared interfaces and physical acceptance remain open'
selection['remaining_release_items']=[x for x in selection['remaining_release_items'] if not x.startswith('Master BOM')]
selection['remaining_release_items'].insert(0,'Complete physical panel-layout adoption of the selected devices')
(here/'electrical-selection.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf8')
p.write_text(json.dumps(b, indent=2) + '\n', encoding='utf8')
print(json.dumps(b['summary'],indent=2))
