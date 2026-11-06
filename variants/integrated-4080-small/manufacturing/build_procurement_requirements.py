"""Consolidate the current engineering takeoff without inventing supplier prices.

The master is the authority for ownership and quantity. Explicit joint sets are
split into their constituent purchases; reused/included references are excluded.
Ten/25/50/100-piece packs are sizing scenarios, not verified vendor offerings.
This helper does not modify build_pack.py or any of its outputs.
"""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
import argparse, csv, hashlib, json, math, re, sys
from functools import lru_cache

HERE = Path(__file__).resolve().parent
MACHINE = HERE.parent
ROOT = MACHINE.parents[1]
MASTER = HERE / 'detailed-requirements.csv'
INPUTS = {
    'master': MASTER,
    'master_families': HERE / 'stock-and-hardware-families.csv',
    'profile_stock_plan': HERE / '4080-cut-stock-options.json',
    'exclusive_stock_nests': HERE / 'exclusive-stock-nests.json',
    'motion_hardware_geometry': ROOT / 'variants/extrusion-reengineered/motion.py',
    'gantry_hardware_geometry': MACHINE / 'mechanical.py',
    'gantry_joint_geometry': MACHINE / 'gantry_joint.py',
    'gantry_joint_report': MACHINE / 'output/gantry-joint/gantry-joint-check.json',
    'atc_hardware_geometry': MACHINE / 'atc/actual_atc.py',
    'selected_head_geometry': MACHINE / 'head/quick_dock.py',
    'front_stop_geometry': MACHINE / 'front_stop_bed_clearance.py',
    'helper': Path(__file__),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).relative_to(ROOT).as_posix()


def number(s):
    if s is None or str(s).strip() == '':
        return None
    d = Decimal(str(s))
    return int(d) if d == int(d) else float(d)


def norm(s):
    return re.sub(r'\s+', ' ', s.strip())


def screw(d, length=None, head='head selection held', operation=''):
    return dict(category='SCREW', specification=f'M{d} x {length if length is not None else "LENGTH HELD"} {head}',
                thread=f'M{d}', head=head, length_mm=length, operation=operation,
                hold='Actual head selection required.' if 'held' in head else '')


def washer(d, od=None, hole=None, thickness=None):
    dims = f'OD{od if od is not None else "HELD"} ID{hole if hole is not None else "HELD"} t{thickness if thickness is not None else "HELD"}'
    specification = f'Flat washer {dims}' if None not in (od, hole, thickness) else f'M{d} flat washer {dims}'
    return dict(category='WASHER', specification=specification, thread=f'M{d}',
                hold='Unspecified washer dimensions require selection.' if None in (od, hole, thickness) else '')


def nut(d, kind='hex nut', detail='', hold=''):
    return dict(category='NUT', specification=f'M{d} {kind}' + (f'; {detail}' if detail else ''), thread=f'M{d}', hold=hold)


def slotnut(d, profile='actual 4080 8mm slot'):
    return nut(d, 'slot nut', profile, 'Actual selected extrusion die/lip/nut capacity and fit remain required.')


def simple(category, spec, hold='', operation=''):
    return dict(category=category, specification=spec, hold=hold, operation=operation)


def explicit_joint(row):
    """Only documented set contents; never infer a washer merely from a bolt."""
    key = row['id']
    spec = row['specification']
    if key.startswith('FRAME:') and spec == 'M6 +washer +matching slot nut | Length not released':
        return [screw(6), washer(6), slotnut(6)]
    exact = {
        'FRAME:FRONT_MID_FOOT_CORE_M8': [screw(8, head='socket head'), washer(8)],
        'FRAME:FRONT_PAN_HANGER_M6_HEADER': [screw(6), washer(6), slotnut(6)],
        'FRAME:FRONT_PAN_BEAM_M8_ENDCORE': [screw(8, 20, 'socket head'), washer(8)],
        'FRONT_STOP:DATUM_M6X16_ANCHOR_SETS': [screw(6, 16, 'button head'), washer(6, 12, 6.6, 1.6), slotnut(6)],
        'FRONT_STOP:PARKED_MODULE_M6_SLOT_NUTS': [slotnut(6)],
        'BED:BED_RECEIVER_FIXING': [screw(5, 10, 'countersunk head'), slotnut(5)],
        'BED:BED_FIXED_HINGE_FASTENERS': [screw(6), slotnut(6)],
        'BED:BED_ASSIST_ROOT_FASTENERS': [screw(6), slotnut(6)],
        'ATC:ATC_END_M8x20': [screw(8, 20, 'socket head'), washer(8, thickness=1.6)],
        'ATC:ATC_HEADER_AND_DOCK_M6x16': [screw(6, 16, 'socket head'), washer(6), slotnut(6)],
        'ATC:ATC_COVER_HANGER_M6x16': [screw(6, 16, 'socket head'), washer(6), slotnut(6)],
        'ATC:ATC_BASE_M4x12': [screw(4, 12), slotnut(4, 'selected ATC module N-M4 underside channel')],
        'ATC:ATC_OEM_CARRIAGE_M6_SET': [screw(6)],
        'ATC:ATC_CARRIER_M6_TNUT': [slotnut(6)],
        'UTILITIES:U_GUIDE_FRAME_M6_SETS': [screw(6, 12), slotnut(6)],
        'UTILITIES:U_GUIDE_RACK_ANCHOR_SETS': [screw(6), slotnut(6)],
        'UTILITIES:U_GUIDE_RACK_M6_NUTS': [nut(6, 'weld nut', '5mm-high nominal steel nut', 'Weld process, actual nut and grade held.')],
        'WET_BASE:Pan keeper frame fasteners': [screw(6, 16), washer(6), slotnut(6)],
        'WET_BASE:Overflow detachable hardware': [nut(4), washer(4, od=9, thickness=1.6), simple('SPACER', 'OD8 ID4.4 x1 steel spacer')],
        'WET_BASE:Hatch hinge bolts': [screw(4, 16), washer(4, od=9, thickness=1.6), nut(4)],
        'WET_BASE:Hatch latch knobs/rivnuts': [screw(4, 16, 'hand knob'), nut(4, 'rivnut', '3mm grip', 'Actual rivnut tail/seat fit held.')],
        'RECEIVER_ROOF:M6_FRAME_SETS': [screw(6, 16, 'button head'), washer(6), slotnut(6)],
        'RECEIVER_ROOF:M4_ROOF_SETS': [screw(4, 12, 'button head'), washer(4), nut(4)],
        'GANTRY:M6_WASHERS': [washer(6, 12, 6.6, 1.6)],
        'GANTRY:M6_NUTS': [nut(6, detail='5mm nominal height', hold='Actual grade and retention held.')],
        'GANTRY:GJ_TOP_M6x20': [screw(6, 20, 'socket head')],
        'GANTRY:GJ_TOP_M6_WASHER': [washer(6, 12, 6.6, 1.6)],
        'GANTRY:GJ_TOP_M6_TNUT': [slotnut(6, 'actual4080slot; nominal5.9mmthreadengagement and at least13.05mmcavityfor20mmbolt')],
        'HEAD:Captive release screws M6x25': [screw(6, 25, 'socket head')],
        'HEAD:Cage fixing screws M3x10': [screw(3, 10, 'socket head')],
        'HEAD:Gravity ledge M4x20 screws': [screw(4, 20, 'socket head')],
        'HEAD:Gravity ledge M4 washers': [washer(4, 9, 4.3, 1)],
        'HEAD:Owner clamp M5x25 screws': [screw(5, 25, 'socket head')],
        'HEAD:Owner clamp M5 spreader washers': [washer(5, 10, 5.3, 1)],
        'HEAD:Plasma splice M6x16 screws': [screw(6, 16, 'socket head')],
        'HEAD:Router rib M4x25 screws': [screw(4, 25, 'socket head')],
        'HEAD:Router rib ground dowels': [dict(category='GROUND_DOWEL',specification='Ground steel dowel D4 x20mm',
            length_mm=20,hold='Actual steel grade, matched light press fit in head, 0..0.005mm diametral rib clearance, bearing capacity and loaded slip require qualification.',
            operation='Match-ream the head/rib bore pair to actual selected pins; rear flush, 12.7mm head and7.3mm rib engagement.')],
        'BED:BED_BOTTOM_SLOT_NUT_M5': [slotnut(5, '20100 bottom slot; nominal 8x8x2.7')],
        'BED:BED_HINGE_BUTTON_FASTENERS': [screw(8, 35, 'button head')],
        'BED:BED_REAR_CLOSED_BOLTS': [screw(8, 35, 'socket head')],
        'BED:BED_ASSIST_END_FIXINGS': [screw(8, 25)],
        'BED:BED_REAR_CLOSED_WASHERS': [washer(8, 16, 8.5, 1.6)],
        'BED:BED_REAR_UPPER_CAP_BOLTS': [screw(8, 20, 'socket head')],
        'BED:BED_REAR_UPPER_CAP_WASHERS': [washer(8, 16, 8.5, 1.6)],
        'BED:BED_GAS_UPPER_WASHERS': [washer(8, 16, 8.4, 1.6)],
        'BED:BED_GAS_UPPER_NYLOC_NUTS': [nut(8, 'nyloc nut', 'DIN985AF13/h8nominal', 'Verifyactualballstudthread/nylonengagement.')],
        'BED:BED_GAS_UPPER_STUD_SPACER': [simple('SPACER', 'OD12.7 ID8.5 x1.05mm steel spacer', 'Actualballstudneckandmountstackfitheld.')],
        'BED:BED_CROSS_BRIDGE_WASHERS': [washer(6, 18, 6.4, 1.6)],
        'MOTION:XR_MODULE_BOTTOM_M4_SLIDING_NUTS': [slotnut(4, 'owned HMS40 bottom channel; exact supplied contour held')],
        'MOTION:XR_FRAME_M6_SLOT_NUTS': [slotnut(6)],
        'ATC:ATC_COVER_KEEPER_RCLIP': [simple('RETAINER', 'R-clip for 4mm keeper pin', 'Actual matching crosshole/wire fit held.')],
    }
    if key in exact:
        return exact[key]
    if key=='BED:BED_M5X100_FINISH99P3':
        assert '100'in spec and '99.3'in spec,'Bed finished99.3mm screw requires explicitly sourced100mm raw stock.'
        return [screw(5,100,'socket head',
            'Machine each purchased M5x100 socket screw to99.3+/-0.1mm finished underhead length; enddeburr/chamfer<=0.4mm and verify complete usable thread, 18ODbridgewasher stack, full2.7mm nominalslotnutengagement,1.0mmtipreserve and1.1mmcavityreserve.99.3mm is a finished part, not an assumed catalogue length.')]
    # These opaque component IDs are recovered from the bound motion.py factory.
    if re.match(r'MOTION:Y_LINK_SUPPORT_TOP_M5x20_', key):
        return [screw(5, 20, 'countersunk head')]
    if re.match(r'MOTION:XR_SADDLE_[LR]_\d+_MODULE_M4x16_', key):
        return [screw(4, 16, 'socket head')]
    if re.match(r'MOTION:XR_SADDLE_[LR]_\d+_EDGE_M5x25_', key):
        return [screw(5, 25, 'socket head')]
    if re.match(r'MOTION:XR_SADDLE_[LR]_\d+_M6x25_EXTERNAL_GRIP_', key):
        return [screw(6, 25, 'socket head')]
    if re.match(r'MOTION:XR_SADDLE_[LR]_\d+_M6_WASHER_', key) or key.startswith('MOTION:XR_STOP_FRAME_WASHER_'):
        return [washer(6, 12, 6.6, 1.6)]
    if key.startswith('MOTION:XR_STOP_BASE_M6x12_'):
        return [screw(6, 12, 'socket head')]
    if key.startswith('MOTION:XR_STOP_FRAME_M6x16_EXTERNAL_GRIP_'):
        return [screw(6, 16, 'socket head')]
    if key.startswith('FRAME:XR_FOOT_LOCKNUT_'):
        return [nut(8, detail='6.8mm nominal height', hold='Actual selected foot-locknut dimensions and grade held.')]
    if key.startswith('ATC:ATC_END_M6_WASHER_') or key.startswith('ATC:ATC_PIN_WASHER_'):
        return [washer(6, 12, 6.6, 1.6)]
    if key.startswith('ATC:ATC_PIN_NUT_'):
        return [nut(6, detail='5mm nominal height', hold='Actual grade and retention held.')]
    return None


@lru_cache(None)
def profile_plan():
    return json.loads(INPUTS['profile_stock_plan'].read_text())


def profile_atom(row):
    scope, item = row['id'].split(':', 1)
    matches = [c for c in profile_plan()['cuts'] if c['scope']==scope and c['id']==item]
    if row['id']=='BED:BED_CROSS_4080':
        matches = [c for c in profile_plan()['cuts'] if c['scope']=='BED']
        assert len(matches)==number(row['new_quantity'])
    if not matches:
        return None
    lengths = set(c['length_mm'] for c in matches)
    assert len(lengths)==1, (row['id'], matches)
    length = number(next(iter(lengths)))
    return [dict(category='4080_FINISHED_CUT_REQUIREMENT', specification=f'4080 x{length}mm finished',
                 length_mm=length, hold='Use one compatible raw4080stock plan only; actual section, slot/core, cleanup, tapping and modified-section acceptance remain required.')]


def classify(row):
    override = explicit_joint(row)
    if override is not None:
        return override
    spec, key = row['specification'], row['id']
    if row['role'] == 'INTERFACE_HOLD' or row['new_quantity'] == '':
        return [simple('INTERFACE_HOLD', spec, 'Quantity and/or actual selection held; not zero.')]
    profile = profile_atom(row)
    if profile is not None:
        return profile
    if key=='BED:BED_HDPE_FULL_LAYERS':
        return [simple('HDPE_FINISHED_LAYER_REQUIREMENT', spec, 'ONE1000x1200x12.7finishedlayer derives from one nominal48x48inch halfsheet in the bound exclusive-stock nest; rawsheet is nonadditive.80roundthroughholesonly.')]
    # Source-modeled custom blanks are never parsed as bolts merely because
    # their machining notes contain an M6/M8 hole designation.
    if row['artifacts']:
        return [simple('CUSTOM_STOCK_OR_FABRICATION', spec, 'Finished-part requirements; raw size, cleanup, nesting and supplier stock remain to select.')]
    m = re.search(r'ISO7379[_ ](?:D|shoulder)?(\d+)[_x]L?(\d+)[_/]M(\d+)', spec, re.I)
    if m:
        d, length, thread = map(int, m.groups())
        return [dict(category='SHOULDER_SCREW', specification=f'ISO7379 shoulder D{d} x{length}; M{thread} thread', thread=f'M{thread}', hold='Actual shoulder/thread dimensions and grade require selection.')]
    m = re.fullmatch(r'(WASHER|SHIM)_(\d+p?\d*)x(\d+p?\d*)x(\d+p?\d*)', spec)
    if m:
        kind, hole, od, thick = m.groups()
        hole, od, thick = (number(v.replace('p', '.')) for v in (hole, od, thick))
        if kind == 'SHIM':
            return [simple('PRECISION_SHIM', f'ID{hole} OD{od} t{thick} hardened bearing shim', 'Match hardness, flatness and bearing-face application.')]
        return [dict(category='WASHER', specification=f'Flat washer OD{od} ID{hole} t{thick}', hold='')]
    if re.search(r'(?:^|_)M\d+_(?:LH|RH)_JAM_NUT$', spec):
        m = re.search(r'M(\d+)_(LH|RH)_JAM_NUT', spec)
        return [nut(m[1], 'jam nut', m[2] + ' thread; 5mm high nominal', 'Handed thread and grade must match rod end.')]
    if spec == 'M5_PREVAILING_NUT':
        return [nut(5, 'prevailing torque locknut', hold='Actual type and reuse policy to select.')]
    if spec == '8020_40-3915_M8_TNUT':
        return [nut(8, 'slot nut', '80/20 40-3915;22x13.7x5.9 maximum', 'Qualified only if selected extrusion accepts this exact nut.')]
    if spec.startswith('SKF_') or spec.startswith('OMRON_'):
        return [simple('CATALOGUE_COMPONENT', spec, 'Confirm current supplier, included contents and exact variant.')]
    # Metric fasteners with a released size; orientation suffixes do not create
    # separate purchases. Head styles remain distinct.
    m = re.search(r'(?<![A-Za-z0-9])M(\d+)\s*[xX\u00d7]\s*(\d+(?:\.\d+)?)', spec)
    explicit_fastener = bool(re.search(r'(?i)^(?:I_)?STD_|ISO7380|socket|countersunk|thumb|screw|bolt', spec))
    if m and explicit_fastener:
        d, length = int(m[1]), number(m[2])
        head = ('countersunk head' if re.search(r'(?i)CSK|countersunk', spec)
                else 'button head' if re.search(r'(?i)BUTTON|ISO7380', spec)
                else 'thumb screw' if re.search(r'(?i)thumb', spec)
                else 'socket head' if re.search(r'(?i)SOCKET', spec)
                else 'head selection held')
        op = 'Finish underhead length to19mm;8 current ATC arm screws require this operation.' if key.startswith('ATC:ATC_ARM_M6_FINISHED19_') else ''
        return [screw(d, length, head, op)]
    if key == 'WET_BASE:Pan keeper bolts':
        return [screw(6, 20)]
    # Keep source quantity but avoid falsely claiming standardized hardware
    # from a diameter-only pin/washer/cylinder envelope.
    if re.search(r'(?i)pin|retainer|Rclip|retention', key) and re.search(r'(?i)steel|pin|clip', spec):
        return [simple('PIN_OR_RETAINER_SELECTION_HOLD', spec, 'Source count retained; actual pin, retention and complete envelope require selection.')]
    if re.search(r'(?i)4080.*finished', spec) or key in ('BED:BED_CROSS_4080', 'ATC:ATC_FIXED_CROSSBEARERS_4080', 'ATC:ATC_MOVING_CARRIER_4080'):
        return [simple('4080_FINISHED_CUT_REQUIREMENT', spec, 'Choose one compatible raw-stock plan; do not also order finished cuts and raw-bar plan.')]
    if key == 'BED:BED_UNCUT_20100':
        return [simple('20100_PROFILE', spec, 'Tenfinished1220mmtracks. Selectedrawplan8x1500+2x1220issamefamilyandnonadditive;trim8barsby280mmnominalanddeburr. Exactslotdie/nut/lipfit and actualusable1220length required.')]
    return [simple('SOURCE_REQUIREMENT_UNMAPPED', spec, 'Count and specification preserved. Select supplier/stock from source drawing or resolve actual interface before ordering.')]


def family_key(atom, row):
    # Product type, dimensions and source unit govern grouping; human left/right
    # component identifiers and display modes never split the same screw.
    return (atom['category'], norm(atom['specification']),
            'piece' if atom['category'] in ('SCREW', 'SHOULDER_SCREW', 'GROUND_DOWEL', 'NUT', 'WASHER', 'PRECISION_SHIM', 'SPACER', 'RETAINER', '4080_FINISHED_CUT_REQUIREMENT') else row['unit'])


def run():
    start = {name: sha(p) for name, p in INPUTS.items()}
    with MASTER.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)), 'Duplicate master row IDs'
    groups = {}
    coverage = []
    excluded = []
    for r in rows:
        if r['additive'] != 'True' or r['ownership'].startswith('OWNED'):
            excluded.append(dict(source_id=r['id'], reason='NONADDITIVE_REFERENCE' if r['additive'] != 'True' else 'OWNED_EXCLUDED',
                                 source_ownership=r['ownership'], master_new_quantity=r['new_quantity']))
            coverage.append(dict(source_id=r['id'], treatment=excluded[-1]['reason'], procurement_keys=[]))
            continue
        q = number(r['new_quantity'])
        atoms = classify(r)
        keys = []
        for a in atoms:
            key = family_key(a, r)
            if key not in groups:
                groups[key] = dict(category=a['category'], specification=a['specification'], unit=key[2],
                    known_minimum_quantity=0, unresolved_quantity_source_ids=[], source_rows=[], source_specs=[],
                    source_ownerships=[], source_materials=[], source_qualification_notes=[], holds=[], operations=[], thread=a.get('thread', ''), head=a.get('head', ''),
                    length_mm=a.get('length_mm'), sources=[])
            g = groups[key]
            if q is None:
                g['unresolved_quantity_source_ids'].append(r['id'])
            else:
                g['known_minimum_quantity'] += q
            g['source_rows'].append(r['id'])
            g['source_specs'].append(r['specification'])
            g['source_ownerships'].append(r['ownership'])
            g['source_materials'].append(r['material'])
            if r['notes']:
                g['source_qualification_notes'].append(r['notes'])
            g['sources'].append(r['source'])
            if a.get('hold'):
                g['holds'].append(a['hold'])
            if r['role'] == 'INTERFACE_HOLD':
                g['holds'].append('Master marks this row INTERFACE_HOLD.')
            if a.get('operation'):
                g['operations'].append(dict(source_id=r['id'], quantity=q, operation=a['operation']))
            # Retain all source qualification text; it must not disappear when
            # many right/left source instances consolidate into one purchase.
            keys.append(key)
        coverage.append(dict(source_id=r['id'], treatment='EXPLODED_SET' if len(atoms) > 1 else 'DIRECT_REQUIREMENT',
                             master_new_quantity=q, atoms_per_source_unit=len(atoms), procurement_keys=keys))
    families = []
    key_ids = {}
    hardware = {'SCREW', 'SHOULDER_SCREW', 'GROUND_DOWEL', 'NUT', 'WASHER', 'PRECISION_SHIM', 'SPACER', 'RETAINER'}
    for i, (key, g) in enumerate(sorted(groups.items()), 1):
        code = f'P{i:03}'
        key_ids[key] = code
        g['procurement_id'] = code
        g['new_required_quantity'] = None if g['unresolved_quantity_source_ids'] else g['known_minimum_quantity']
        g['quantity_status'] = 'HELD_NOT_ZERO' if g['unresolved_quantity_source_ids'] else 'KNOWN'
        g['supplier_selection_status'] = 'UNSELECTED'
        g['source_rows'] = sorted(set(g['source_rows']))
        for field in ('source_specs', 'source_ownerships', 'source_materials', 'source_qualification_notes', 'sources', 'holds'):
            g[field] = sorted(set(g[field]))
        if g['category'] == 'SCREW' and g['length_mm'] is None:
            g['holds'].append('Known count contains different source joints; select actual screw lengths per joint, not one assumed length.')
        g['pack_sizing_scenarios'] = []
        if g['category'] in hardware and g['new_required_quantity'] is not None:
            for size in (10, 25, 50, 100):
                count = math.ceil(g['new_required_quantity'] / size)
                g['pack_sizing_scenarios'].append(dict(pack_size=size, packs=count,
                    supplied=count*size, spare=count*size-g['new_required_quantity']))
        g['selected_vendor_pack_size'] = None
        g['selected_vendor_pack_count'] = None
        g['goods_USD'] = None
        g['shipping_USD'] = None
        g['tax_USD'] = None
        families.append(g)
    for row in coverage:
        row['procurement_ids'] = [key_ids[tuple(k)] for k in row.pop('procurement_keys')]
    stock = json.loads(INPUTS['profile_stock_plan'].read_text())
    nests = json.loads(INPUTS['exclusive_stock_nests'].read_text())
    stock_plan = dict(role='NONADDITIVE_RAW_STOCK_ALTERNATIVE',
        note='One valid all2000mm plan only. Do not add its13bars to26finished-cut requirements. Pack rounding depends on an actual selected supplier.',
        cut_count=stock['cut_count'], finished_4080_length_mm=stock['finished_length_mm'],
        stock_length_mm=2000, bars=len(stock['options']['2000']['bars']),
        raw_mm=stock['options']['2000']['raw_stock_mm'],
        two_piece_pack_scenario=dict(packs=math.ceil(len(stock['options']['2000']['bars'])/2), pieces=2*math.ceil(len(stock['options']['2000']['bars'])/2)),
        actual_vendor_pack_selected=False)
    profile_families=[g for g in families if g['category']=='4080_FINISHED_CUT_REQUIREMENT']
    profile_quantity=sum(g['new_required_quantity'] for g in profile_families)
    profile_length=sum(g['new_required_quantity']*g['length_mm'] for g in profile_families)
    profile_allocation_reconciles=(profile_quantity==stock['cut_count'] and abs(profile_length-stock['finished_length_mm'])<1e-6)
    assert profile_allocation_reconciles, (profile_quantity,profile_length,stock['cut_count'],stock['finished_length_mm'])
    result = dict(schema_version=1, purpose='Purchase-preparation crosswalk of every current master row; source reconciliation only.',
        scope='Current integrated4080small variant. Source interface and qualification holds survive consolidation.',
        assumptions=['No supplier, price, shipping, tax or ownership inferred.',
          'Pack sizes10/25/50/100are comparison scenarios only; actual variant/package requires supplier selection.',
          'Known screw dimensions are consolidated across orientations. Different heads, washer sizes, handed threads and module-vs-frame slotnuts stay distinct.',
          'Opaque motion saddle/stop fastener dimensions recovered from bound source factory; no new supplier mounting pattern invented.',
          'No inferred spare allowance. Pack scenario spares are arithmetic excess only.',
          'Unmapped source rows retain exact requirement and count; missing count stays null, never zero.'],
        source_bindings={name:dict(file=relative(path), sha256=start[name]) for name,path in INPUTS.items()},
        counts=dict(master_rows=len(rows), active_source_rows=len(rows)-len(excluded), excluded_owned_or_included_rows=len(excluded),
                    procurement_families=len(families), standard_hardware_families=sum(f['category'] in hardware for f in families),
                    quantity_held_families=sum(f['new_required_quantity'] is None for f in families),
                    unmapped_source_families=sum(f['category']=='SOURCE_REQUIREMENT_UNMAPPED' for f in families)),
        raw_4080_stock_plan=stock_plan,
        HDPE_source_raw_stock_nonadditive=nests['HDPE_new_stock'],
        HDPE_raw_order_scenario=dict(role='NONADDITIVE_RAW_STOCK_ALTERNATIVE',quantity=1,unit='48x48inch x1/2inch raw halfsheet',
            finished_layers=1,finished_layer_mm=[1000,1200,12.7],master_row='BED:BED_HDPE_FULL_LAYERS',actual_supplier_selected=False,
            note='One halfsheet supplies ONEfinishedlayer; ordinarycutsand80roundholes. Raw stock is an alternative purchase representation, not extra material.'),
        tracks_raw_order_scenario=dict(role='NONADDITIVE_RAW_STOCK_ALTERNATIVE',finished_quantity=10,finished_length_mm=1220,
            raw_packs=[dict(ASIN='B0DY7JYQCJ',packs=2,pieces_per_pack=4,length_mm=1500),dict(ASIN='B0DY7GCFRV',packs=1,pieces_per_pack=2,length_mm=1220)],
            master_row='BED:BED_UNCUT_20100',note='SameSeekfamilyselectedrawpackplan;8trimmedplus2uncuttracks. Not20tracksandnotadditionaltothe10finishedrequirements. Pricesanddeliveryfollowboundbudget/cartregister.'),
        families=families, source_coverage=coverage, excluded=excluded,
        complete_shipped_cost_USD=None, under_1000_shipped_verified=False,
        fabrication_release=False, CAM_release=False, operating_release=False)
    csvpath = HERE/'procurement-requirements.csv'
    jsonpath = HERE/'procurement-requirements.json'
    fields = ['procurement_id','category','specification','unit','new_required_quantity','known_minimum_quantity','quantity_status',
              'thread','head','length_mm','packs_of_10','packs_of_25','packs_of_50','packs_of_100','pack_basis',
              'supplier_selection_status','selected_vendor_pack_size','selected_vendor_pack_count','source_row_count','source_row_ids','operations','holds']
    with csvpath.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for g in families:
            rr = {k:g.get(k) for k in fields}
            for p in g['pack_sizing_scenarios']:
                rr[f'packs_of_{p["pack_size"]}'] = p['packs']
            rr.update(pack_basis='UNPRICED_SIZING_SCENARIO_ONLY' if g['pack_sizing_scenarios'] else '',
                      source_row_count=len(g['source_rows']),source_row_ids=';'.join(g['source_rows']),
                      operations=json.dumps(g['operations'],ensure_ascii=True) if g['operations'] else '',holds=' | '.join(g['holds']))
            w.writerow(rr)
    jsonpath.write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
    # Reconciliation checks catch lost/duplicated instances and invalid pack math.
    sources_current = {k:sha(v)==start[k] for k,v in INPUTS.items()}
    counted = Counter(c['source_id'] for c in coverage)
    coverage_once = len(coverage)==len(rows) and all(counted[i]==1 for i in ids)
    source_actions = {c['source_id']:c for c in coverage}
    atoms_reconcile = all(len(source_actions[r['id']]['procurement_ids']) == len(classify(r))
        for r in rows if r['additive']=='True' and not r['ownership'].startswith('OWNED'))
    index = {f['procurement_id']:f for f in families}
    no_owned_purchase = all(not o.startswith('OWNED') for f in families for o in f['source_ownerships'])
    pack_math = all(p['supplied']>=g['new_required_quantity'] and p['spare']>=0 and p['packs']==math.ceil(g['new_required_quantity']/p['pack_size'])
                    for g in families for p in g['pack_sizing_scenarios'])
    # A32-instance bound fastener provides a useful anti-one-row-per-part check.
    m5_rows = [r for r in rows if r['specification']=='STD_M5x18_SOCKET' and r['additive']=='True']
    source_family_ids = {p for r in m5_rows for p in source_actions[r['id']]['procurement_ids']}
    size_consolidated = len(source_family_ids)==1 and sum(number(r['new_quantity']) for r in m5_rows)==32
    datum = source_actions['FRONT_STOP:DATUM_M6X16_ANCHOR_SETS']
    explicit_set_three_atoms = len(datum['procurement_ids'])==3 and number(next(r for r in rows if r['id']==datum['source_id'])['new_quantity'])==4
    by_source={r['id']:r for r in rows}
    newbed_screws=by_source['BED:BED_M5X100_FINISH99P3']
    current_bed_and_gantry=(number(newbed_screws['new_quantity'])==80 and
        all(index[p]['length_mm']==100 for p in source_actions[newbed_screws['id']]['procurement_ids'])and
        number(by_source['BED:BED_HDPE_FULL_LAYERS']['new_quantity'])==1 and
        len(nests['HDPE_new_stock']['parts'])==1 and
        all(number(by_source['GANTRY:'+i]['new_quantity'])==8 for i in('GJ_TOP_M6x20','GJ_TOP_M6_WASHER','GJ_TOP_M6_TNUT'))and
        all(by_source['GANTRY:'+i]['additive']=='False'for i in('GJ_OFFCUT_TOP_BRIDGES','GJ_OFFCUT_M8_REAR_LANDS','GJ_OFFCUT_M6_UPPER_LANDS'))and
        not any('INT_GANTRY_GUIDE_BAR_'in r['id']for r in rows))
    check = dict(source_bindings=result['source_bindings'], source_files_current=sources_current,
        source_coverage_once=coverage_once, explicit_atoms_reconcile=atoms_reconcile,
        no_owned_purchase=no_owned_purchase, pack_arithmetic=pack_math,
        all_current_4080_cut_requirements_reconcile=profile_allocation_reconciles,
        thirty_two_M5x18_instances_consolidated=size_consolidated,
        four_datum_joint_sets_expand_to_four_each_screw_washer_slotnut=explicit_set_three_atoms,
        current_single_layer_bed_and_gantry_reconcile=current_bed_and_gantry,
        held_counts_preserved=all(f['new_required_quantity'] is None for f in families if f['unresolved_quantity_source_ids']),
        artifact_sha256={csvpath.name:sha(csvpath),jsonpath.name:sha(jsonpath)},
        requirements_reconciled=all(sources_current.values()) and coverage_once and atoms_reconcile and no_owned_purchase and pack_math and size_consolidated and explicit_set_three_atoms and profile_allocation_reconciles and current_bed_and_gantry,
        supplier_selections_complete=False, complete_shipped_total_USD=None, budget_pass=False,
        fabrication_release=False, CAM_release=False)
    (HERE/'procurement-check.json').write_text(json.dumps(check,indent=2)+'\n',encoding='utf-8')
    assert check['requirements_reconciled'], check
    print(json.dumps(dict(requirements_reconciled=True, **result['counts']),indent=2))


def check_only():
    path = HERE/'procurement-check.json'
    if not path.exists():
        print('No procurement-check.json; run generator first.')
        return 1
    check = json.loads(path.read_text())
    stale = [name for name, b in check['source_bindings'].items() if not (ROOT/b['file']).exists() or sha(ROOT/b['file']) != b['sha256']]
    bad = [name for name, expected in check['artifact_sha256'].items() if not (HERE/name).exists() or sha(HERE/name)!=expected]
    print(json.dumps(dict(requirements_reconciled=check['requirements_reconciled'], stale_source_bindings=stale,
                         changed_outputs=bad, passed=not stale and not bad and check['requirements_reconciled']),indent=2))
    return 1 if stale or bad or not check['requirements_reconciled'] else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check bindings/output hashes without regenerating.')
    args = parser.parse_args()
    if args.check:
        sys.exit(check_only())
    run()
