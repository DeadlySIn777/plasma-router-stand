"""Reconcile frozen XR2 takeoffs for the owned-Z300 candidate, without prices.

This does not modify CAD, qualify suppliers, or assert fabrication release.
Every input row remains traceable; additive requirements and references are
separate. Run with the repository's plain Python (no CAD generation needed).
"""
from __future__ import annotations
from collections import Counter
import ast
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = HERE.parent / 'extrusion-reengineered'
OUT = HERE / 'manufacturing'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rel(path):
    return Path(path).relative_to(ROOT).as_posix()

def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write_csv(path, rows):
    assert rows
    with Path(path).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')

INPUTS = {
    'frame_takeoff': BASE / 'review/frame-fabrication.csv',
    'frame_manifest': BASE / 'review/frame-fabrication-metadata.json',
    'motion_takeoff': BASE / 'motion-fabrication.csv',
    'bed_takeoff': BASE / 'review/bed-fabrication.csv',
    'bed_manifest': BASE / 'review/bed-manufacturing-check.json',
    'bed_takeoff_manifest': BASE / 'review/bed-fabrication-metadata.json',
    'shield_takeoff': BASE / 'review/shield-fabrication.csv',
    'shield_manifest': BASE / 'review/shield-manufacturing.json',
    'atc_takeoff': BASE / 'review/atc-fabrication.csv',
    'atc_manifest': BASE / 'review/atc-manufacturing.json',
    'owned_stock_nest': BASE / 'review/owned-stock-check.json',
    'custom_index': BASE / 'fabrication/custom-part-index.csv',
    'custom_manifest': BASE / 'review/custom-parts-check.json',
    'profile_nest': BASE / 'review/profile-nesting.json',
    'steel_nest': BASE / 'review/steel-nesting.json',
    'owned_Z_evidence': HERE / 'owned-hardware-evidence.json',
    'custom_repair_manifest': HERE / 'output/custom-joint-repair-check.json',
    'custom_repair_source': HERE / 'custom_joint_repair.py',
    'Z300_overlay_source': HERE / 'z300_fit_study.py',
    'carrier_STEP': HERE / 'output/Z_CARRIER_RELIEVED_CANDIDATE.step',
    'support_STEP': HERE / 'output/X_LINK_SUPPORT_D37_CANDIDATE.step',
    'source_motion_details': ROOT / 'output/release-review/RevE-ENGINEERING/motion_details.py',
    'source_motion_finish': ROOT / 'output/release-review/RevE-ENGINEERING/motion_finish.py',
    'source_motion_integration': BASE / 'motion.py',
    'front_stop_repair_source': HERE / 'front_stop_repair.py',
    'front_stop_repair_manifest': HERE / 'output/front-stop-repair/front-stop-repair-check.json',
    'front_stop_details_source': HERE / 'front_stop_details.py',
    'front_stop_operation_manifest': HERE / 'output/front-stop-repair/front-stop-base-reference-check.json',
    'owner_head_basis': HERE / 'sources/owned-head/recovered-owner-basis.json',
    'owner_working_boot': HERE / 'sources/owned-head/owner-working-boot.json',
    'owner_head_decisions': HERE / 'sources/owned-head/owner-decisions.json',
    'owner_actuator_selection': HERE / 'sources/owned-head/owner-actuator-selection.json',
    'owner_clamp_STEP': HERE / 'sources/owned-head/R10 - original uncut 65 mm spindle clamp.step',
    'owner_boot_STEP': HERE / 'sources/owned-head/Spindle dust boot.step',
    'candidate_requirements': HERE / 'candidate-requirements.json',
    'owner_head_integration_note': HERE / 'OWNER-HEAD-INTEGRATION.md',
}

FIELDS = ['schedule_id', 'source_evidence_id', 'source_file', 'source_row', 'source_item_id',
          'source_category', 'source_quantity', 'source_owned', 'source_procure',
          'requirement_role', 'additive_requirement', 'selected_base', 'quantity', 'unit',
          'ownership_status', 'owned_credit_quantity', 'new_required_quantity',
          'include_in_new_procurement', 'status', 'material_or_spec', 'stock_or_part_spec',
          'covered_by', 'artifacts', 'evidence_and_qualification']

def build():
    OUT.mkdir(exist_ok=True)
    (OUT / 'source-evidence').mkdir(exist_ok=True)
    (OUT / 'custom-step').mkdir(exist_ok=True)
    (OUT / 'operation-reference').mkdir(exist_ok=True)
    start = {key: sha(path) for key, path in INPUTS.items()}
    source_rows = {key: read_csv(INPUTS[key]) for key in
                   ('frame_takeoff', 'motion_takeoff', 'bed_takeoff', 'shield_takeoff', 'atc_takeoff')}
    source_manifests = {key: read_json(INPUTS[key]) for key in
                        ('frame_manifest', 'bed_manifest', 'bed_takeoff_manifest', 'shield_manifest',
                         'atc_manifest', 'owned_stock_nest', 'custom_manifest', 'custom_repair_manifest', 'front_stop_repair_manifest', 'front_stop_operation_manifest')}
    assert len(source_rows['atc_takeoff']) == 344
    assert source_manifests['atc_manifest']['procurement_rows'] == 344
    assert start['atc_manifest'] == 'ac8b22cb76277f8c96f30238b9660eacb7f1d2aad29f47daabb91b134a268329'
    assert source_manifests['custom_repair_manifest']['passed']
    assert source_manifests['front_stop_repair_manifest']['passed']
    assert source_manifests['owned_stock_nest']['passed']
    schedule = []
    ids = set()

    def add(scope, source_key, source_row, source, item_id, category, qty, material, spec,
            role='DISTINCT_REQUIREMENT', additive=True, selected=True, ownership='NOT_CONFIRMED_OWNED',
            credit=0, new=None, status='NOMINAL_UNPRICED_MEASURE_BEFORE_ORDER', covered='', artifacts='', notes='',
            unit='each', source_owned='', source_procure=''):
        sid = scope + ':' + item_id
        assert sid not in ids, sid
        ids.add(sid)
        q = qty
        if new is None:
            new = q - credit if isinstance(q, (int, float)) else ''
        include = bool(additive and selected and new != 0)
        row = dict(zip(FIELDS, [sid, source_key, rel(INPUTS[source_key]) if source_key in INPUTS else source,
            source_row, item_id, category, source.get('quantity', qty) if isinstance(source, dict) else qty,
            source_owned, source_procure, role, additive, selected, q, unit, ownership, credit, new, include,
            status, material, spec, covered, artifacts, notes]))
        if not additive:
            row['new_required_quantity'] = 0
            row['include_in_new_procurement'] = False
        schedule.append(row)
        return row

    # Exact physical source rows plus distinct fastener-set requirements. A
    # station group is not extra steel/aluminum or a second set of adjusters.
    for number, row in enumerate(source_rows['frame_takeoff'], 1):
        item, cat = row['id'], row['category']
        additive = item not in ('RATED_M8_ADJUSTER', 'LEDGER_TO_ARM_M6_BED_SCOPE')
        covered = (';'.join('FRAME:' + r['id'] for r in source_rows['frame_takeoff']
                           if r['id'].startswith('XR_RATED_FOOT_')) if item == 'RATED_M8_ADJUSTER'
                   else 'BED:Ledger fasteners' if item == 'LEDGER_TO_ARM_M6_BED_SCOPE' else '')
        role = 'REFERENCE_STATION_GROUP' if not additive else (
            'FASTENER_SET_REQUIREMENT' if cat == 'Hardware station allowance' else 'FINISHED_STOCK_REQUIREMENT')
        note = row['holes_or_stations'] + ' | ' + row['qualification']
        if cat == 'Hardware station allowance' and additive:
            note += ' | Quantity counts joint sets. Include the listed screw/washer/matching nut once per set; actual length is held.'
        add('FRAME', 'frame_takeoff', number, row, item, cat, int(row['quantity']), row['material'],
            row['finished_blank_or_allowance_mm'], role=role, additive=additive, covered=covered, notes=note,
            unit='joint set' if cat == 'Hardware station allowance' and additive else 'each')

    provisional_clamp = {'TOOL_SPLIT_CLAMP_FRONT', 'TOOL_SPLIT_CLAMP_REAR',
                         'TOOL_CLAMP_MOUNT_-45_12', 'TOOL_CLAMP_MOUNT_-45_38',
                         'TOOL_CLAMP_MOUNT_45_12', 'TOOL_CLAMP_MOUNT_45_38',
                         'TOOL_CLAMP_PINCH_1', 'TOOL_CLAMP_PINCH_2'}
    welded_motion = {r['id'] for r in source_rows['motion_takeoff'] if
                     r['id'].startswith('XR_STOP_CARRIER_') or
                     (r['id'].startswith('Y_STOP_') and r['id'].endswith('_BRACKET')) or
                     r['id'] == 'X_STOP_LEFT_BODY'}
    for number, row in enumerate(source_rows['motion_takeoff'], 1):
        item, cat = row['id'], row['category']
        q = int(row['quantity'])
        kw = {}
        note = row['notes']
        spec, material = row['minimum_blank_or_local_envelope_mm'], row['material']
        part_spec = row['part_number'] + ' | finished/local envelope ' + spec
        if item == 'ZBX80_BASE':
            cat = 'OWNED_Z300_MODULE_CANDIDATE'
            material = 'Owned RATTMMOTOR ZBX80, 300 mm catalog travel, stock motor included'
            part_spec = 'B09MY7XP9L selected child; nominal body 419 x80; overall 530; physical interfaces held'
            kw.update(ownership='OWNER_REPORTED_OWNED_PHYSICAL_IDENTITY_PENDING', credit=1, new=0,
                      role='OWNED_COMPLETE_ASSEMBLY', status='OWNED_QTY1_NO_NEW_Z200_PURCHASE')
            note = ('Supersedes only this frozen takeoff row for a new/unowned 200 mm replacement. '
                    'Quantity is one complete owned 300 mm module, including stock motor, end blocks and output carriage; '
                    'do not buy those envelopes again. Selected candidate working range remains 200 mm. '
                    'Evidence: owned_Z_evidence. The source category/quantity remains in source columns.')
        elif item == 'ZBX80_BRAKE_MOTOR_CANDIDATE':
            kw.update(role='CONDITIONAL_RETENTION_ALTERNATIVE', selected=False,
                      status='OPTIONAL_NEW_UNOWNED_EXCLUDED_FROM_SELECTED_BASE')
            note += ' | No ownership credit. Not mandatory procurement until a compatible qualified power-off retention choice is selected.'
        elif item == 'XR_Y_RAIL_M5_FIXINGS':
            q = ''
            kw.update(role='UNRESOLVED_QUANTITY_REQUIREMENT', new='',
                      status='QUANTITY_HOLD_NOT_ZERO', ownership='SUPPLIED_HARDWARE_COUNT_UNVERIFIED')
            note += ' | Source zero is an unresolved-count marker, never a purchasing zero. Check all owned real rail holes and supplied screws/nuts.'
        elif item in provisional_clamp:
            kw.update(selected=False, role='PROVISIONAL_OWNED_INTERFACE_SUBSTITUTE',
                      status='DO_NOT_ORDER_OR_MACHINE_OWNER_CLAMP_INTEGRATION_HOLD')
            note += ' | Owner supplied an original uncut 65 mm spindle clamp and complete powered 50 mm dust boot, to remain unchanged. This substituted clamp/fastener layout is not the final owned interface.'
        elif item in welded_motion:
            kw.update(additive=False, role='WELDED_ASSEMBLY_REFERENCE', covered='MOTION_STOCK:' + item)
            note += ' | Constituent stock requirements are listed separately; do not purchase the whole bounding box as a billet.'
        if item == 'Z_CARRIER':
            part_spec = '260 x270.2 x12.7 finished blank; through-relief 162.95 x6.55, R3.275 ends'
            note = ('Candidate repaired part replaces the old solid. Preserve 16 M5 guide-block interfaces and four 6.6 clearance bores. '
                    'Carrier local face X/Z center of through-relief is 130/173.475 from minimum corner; thickness is world Y. '
                    'Maintain the specified bearing ledge and full four M6 head seats. No Z300 supplier mounting holes are invented. '
                    'Actual fixing pattern must avoid the relief and prove support span/edge distances. New stock; no owned-sheet credit.')
        elif item == 'X_LINK_SUPPORT':
            part_spec = '156 x120.8 x43.35 finished bounding blank; integral downstand 156 x8 x37'
            note = ('Candidate integral billet replaces the old 30 mm downstand; new downstand 37 mm, lower edge moved down 7 mm while top/bolt axes stay fixed. '
                    'Four specified 5.0 mm pilots, tap M6x1 through 8 mm. STEP cylinders are nominal 6 mm thread-major envelopes, not drill sizes. '
                    'Lower row center-to-edge 9 mm, nominal major-bore ligament 6 mm; nominal engagement 7.3 mm/tip reserve 0.7 mm. '
                    'Two 3.3 mm pilots tap M4x0.7 through 6.35 mm. New unowned billet; add saw/facing cleanup allowance before buying. '
                    'Do not use the old 156x120.8x36.35 blank or add an attached strip. Actual material, thread fit and strength remain held.')
        if item in source_manifests['front_stop_repair_manifest']['outputs']:
            note += (' | Front-stop repair supersedes original geometry: complete 6.35 mm base-corner relief '
                     'left X49.5..55.9,Y80..95.5 (right mirrored). Front mount is now X58.5/1091.5,Y105; '
                     'rear mount stays Y140. Manufacture a new correctly drilled part, not a welded old hole. '
                     'Old Y90 bore absent; new hole center/ligament and 35 mm mount spacing require capacity proof.')
        if item in ('XR_STOP_BASE_M6x12_L_FRONT_1', 'XR_STOP_BASE_M6x12_R_FRONT_1'):
            note += ' | Front-stop candidate moves this unchanged M6x12 screw axis from Y90 to Y105 (+15 mm). Do not drill the old Y90 attachment.'
        r = add('MOTION', 'motion_takeoff', number, row, item, row['category'], q, material, part_spec,
                notes=note, **kw)
        if cat != row['category']:
            r['requirement_role'] = kw.get('role', cat)

    # Welded stop stock is explicit in source geometry/notes, not a deep billet.
    # These are nominal blank requirements, not unverified production cut DXFs.
    for item in sorted(welded_motion):
        front = '_FRONT' in item
        children = []
        if item.startswith('Y_STOP_'):
            children = [('BASE', [43.3, 71 if front else 50, 6.35]), ('POST', [15.8, 50, 6.35])]
            if front:
                children.append(('SWITCH_UPRIGHT', [42, 50, 3]))
        elif item.startswith('XR_STOP_CARRIER_'):
            depth = 55 if front else 42
            children = [('LANDING', [43.3, 71 if front else 50, 6.35]),
                        ('SIDELEG', [36, depth, 6]), ('FLOOR', [30.2, depth, 6]), ('TOWER', [25, 48.5875, 6])]
        elif item == 'X_STOP_LEFT_BODY':
            children = [('BLOCK', [20, 45, 26]), ('ARM', [16, 12.4, 5]), ('SWITCH_BACK', [45, 18, 3])]
        child_ids = []
        for suffix, size in children:
            cid = item + '__' + suffix
            child_ids.append('MOTION_STOCK:' + cid)
            add('MOTION_STOCK', 'source_motion_details' if not item.startswith('XR_') else 'source_motion_integration',
                '', '', cid, 'WELDED_STOP_CONSTITUENT_NOMINAL_BLANK', 1, 'Uncoated low-carbon/A36 steel; actual grade held',
                ' x'.join(str(x) for x in size) + ' mm finished rectangular bounding blank',
                role='STOCK_FOR_WELDED_ASSEMBLY',
                notes='Parent: MOTION:' + item + '. Source-defined constituent, not an additional complete assembly. '
                      'Add saw/facing allowance. Base shaped perimeter and holes use parent STEP; weld procedure, distortion and capacity remain held.')
            if front and suffix in ('BASE', 'LANDING'):
                schedule[-1]['evidence_and_qualification'] += (' | Revised front-stop candidate: old Y90 hole removed, new front fixing Y105; rear Y140. '
                     'Stop BASE also has full-depth relief at left X49.5..55.9/Y80..95.5, right mirror. Landing hole is specified M6 tap, not a clearance bore. '
                     'Use candidate repaired parent STEP and front-stop repair report; no old production profile authorized.')
        parent = next(r for r in schedule if r['schedule_id'] == 'MOTION:' + item)
        parent['covered_by'] = ';'.join(child_ids)

    bed_flat_ids = {r['id'] for r in source_manifests['bed_manifest']['flat_parts']}
    cassette_only = {
        'BOTTOM_SKIN', 'TOP_SKIN', 'Raw structural skin sheet', 'Raw core plywood', 'Raw MDF wear stock',
        'Al T-track', 'Track backing blocks', 'Track compression tubes', 'Track screws',
        'DOCK_PAD_ROUND_BORE', 'DOCK_PAD_PLAIN', 'Dock pads material', 'Dock pad screws',
        'Round locator pins', 'Diamond locator pins', 'Al dry ledgers', 'Ledger fasteners',
        'Cassette clamp sleeves', 'Cassette clamp bolts', 'Cassette lower washers/nuts',
        'M6_D_WASHER_FINISH_VIEW', 'Wear screws', 'Plywood bond adhesive', 'Edge/pocket sealer',
        'COVER_PARKING_BLOCK_SIDE_PROFILE',
    }
    for number, row in enumerate(source_rows['bed_takeoff'], 1):
        item, material = row['item'], row['material']
        kw = {}
        note = row['operation'] + ' | ' + row['notes']
        if item in bed_flat_ids:
            if material == 'structural_plywood':
                kw.update(additive=False, role='FINISHED_PROFILE_REFERENCE',
                          covered='BED:Raw structural skin sheet' if item in ('BOTTOM_SKIN', 'TOP_SKIN') else 'BED:Raw core plywood')
            elif material == 'MDF_finished_from_9p525':
                kw.update(additive=False, role='FINISHED_PROFILE_REFERENCE', covered='BED:Raw MDF wear stock')
            elif material == 'laminated_plywood_stock':
                kw.update(additive=False, role='OFFCUT_PROFILE_REFERENCE', covered='BED:Raw structural skin sheet')
            elif material == 'purchased_Al_angle_operation_view':
                kw.update(additive=False, role='PURCHASED_STOCK_OPERATION_REFERENCE', covered='BED:Hatch carrier angle stock')
        if item == 'Dock pads material':
            kw.update(additive=False, role='OWNED_MATERIAL_REFERENCE', covered='BED:DOCK_PAD_ROUND_BORE;BED:DOCK_PAD_PLAIN')
        elif item == 'Receiver lid':
            kw.update(additive=False, role='INCLUDED_ASSEMBLY_PART_OPERATION_REFERENCE', covered='BED:Receiver')
            note += ' | Matching lid is included in the selected reservoir set, not a second reservoir/lid purchase.'
        elif item == 'Receiver':
            note += ' | One complete reservoir set includes its lid; new/unowned unless physically confirmed. Atmospheric/gravity only. Actual interior usable capacity >=65 L is a release gate.'
        elif item == 'Metal retention/bedding adhesive':
            kw.update(additive=False, role='SHARED_CONSUMABLE_REFERENCE', covered='BED:Hard dock bedding')
            note += ' | One qualified compatible bedding/retention material set must cover pads, rim feet and pins; do not count a second overlapping kit.'
        elif item == 'Hard dock bedding':
            note += ' | Shared material requirement also covers Metal retention/bedding adhesive tasks: pad bondline, receiver rim feet and locator retention; select compatible systems/quantity after cure tests.'
        elif item == 'Unmodeled purchase holds':
            kw.update(additive=False, role='INTERFACE_REGISTER_REFERENCE')
        if item in cassette_only or item.startswith(('WEAR_PAD_PANEL_', 'LONG_WEB_', 'CROSS_WEB_', 'COLD_CASE_', 'CABINET_')) or item.lower().startswith('cabinet '):
            kw.update(selected=False, status='PROPOSAL_ONLY_OWNER_BED_REQUIREMENTS_CONFLICT')
            note += (' | Current plywood/MDF four-cassette proposal is not selected for final fabrication. '
                     'Recovered owner basis calls for ten uncut1220mm20100 members over two full12.7mmHDPE layers with circular drilling only. '
                     'Final bed basis/support/retention is unresolved; do not order these substitute materials as the final bed.')
        q = int(row['quantity'])
        add('BED', 'bed_takeoff', number, row, item, row['status'] + '/' + row['material'], q,
            material, row['stock_mm'], notes=note,
            unit='material lot' if item in ('Raw core plywood', 'Raw MDF wear stock', 'Hard dock bedding',
                                           'Plywood bond adhesive', 'Edge/pocket sealer') else 'each', **kw)

    for number, row in enumerate(source_rows['shield_takeoff'], 1):
        add('SHIELD', 'shield_takeoff', number, row, row['blank_id'], 'FORMED_OR_CUT_SHIELD_BLANK', int(row['quantity']),
            'Uncoated plain steel; actual grade/finish held',
            f"{row['length_mm']} x{row['developed_width_mm']} x{row['thickness_mm']} mm developed blank",
            role='DEVELOPED_STOCK_REQUIREMENT', notes=row['notes'] + ' | Use matching bend/hem instructions and relief profile; do not buy a second finished-panel envelope.')
    for item, q in source_manifests['shield_manifest']['hardware'].items():
        add('SHIELD_HW', 'shield_manifest', 'hardware.' + item, '', item, 'SHIELD_HARDWARE', q,
            'Matching standard hardware, actual profile fit held', item,
            role='HARDWARE_REQUIREMENT', notes='Separate from shield sheet blanks. External-grip conventions do not include unmodeled slot-nut material; count matching listed slot nuts exactly once.')

    # Preserve ALL 344 source rows, including the exact owned/procure flags in
    # separate provenance columns. Source assembly rows remain nonadditive.
    for number, row in enumerate(source_rows['atc_takeoff'], 1):
        additive = row['procure'] == 'True'
        kw = {}
        note = row['notes']
        if row['id'] == 'ATC_MOTOR_DRIVER_CHANNEL':
            kw.update(new='', ownership='OWNER_REPORTED_DRIVES_AVAILABLE_CHANNEL_MATCH_PENDING',
                      status='INTERFACE_HOLD_VERIFY_OWNED_DRIVER_CAPACITY_FIRST')
            note += ' | Latest owner reports drives already owned. This is a channel requirement; determine whether an owned driver satisfies it before adding a new driver. No duplicate purchase or speculative one-channel credit.'
        kw.update(selected=False, status='PROPOSAL_ONLY_RETAINED_ATC_MODULE_ARCHITECTURE_RECONCILIATION')
        note += (' | Current custom rail/belt ATC carrier is a proposal. Earlier owner-selected200mmstroke/311mmoverall module is known; '
                 'reconcile its actual interface/selection before ordering this alternative mechanism. Exact source procure flag remains provenance, not current purchase authorization.')
        atc_scope = 'ATC_REF' if not additive else ('ATC_STOCK' if row['category'] == 'STOCK_FOR_CUSTOM_PART' else
                    'ATC_PURCHASE' if row['category'] == 'PURCHASED_NOMINAL' else 'ATC_INTERFACE')
        add(atc_scope, 'atc_takeoff', number, row, row['id'], row['category'], int(row['quantity']),
            row['material_or_spec'], row['part_number'] + ' | ' + row['finished_size_mm'] + ' | ' + row['stock_type'],
            role='ASSEMBLY_OR_PART_REFERENCE' if not additive else row['category'], additive=additive,
            source_owned=row['owned'], source_procure=row['procure'], artifacts=row['artifacts'], notes=note, **kw)

    atc_decomposition = {entry['id']:entry['constituents'] for entry in source_manifests['atc_manifest']['assembly_decomposition']}
    atc_stock_rows = {r['source_item_id']:r['schedule_id'] for r in schedule if r['source_evidence_id'] == 'atc_takeoff' and r['source_category'] == 'STOCK_FOR_CUSTOM_PART'}
    for reference in [r for r in schedule if r['schedule_id'].startswith('ATC_REF:')]:
        constituents = atc_decomposition.get(reference['source_item_id'], [reference['source_item_id']])
        reference['covered_by'] = ';'.join(atc_stock_rows[item] for item in constituents)
        reference['evidence_and_qualification'] += ' | Stock linkage follows the source manifest decomposition (or one direct blank); do not purchase the parent envelope again.'

    # Material already owned is credited ONCE to exactly the 83 cut blanks in
    # the frozen, nonoverlapping nest. No chips/split thickness/offcut credit.
    nest = source_manifests['owned_stock_nest']
    allocations = {part['id']: (sheet, part) for sheet in nest['sheets'] for part in sheet['parts']}
    assert len(allocations) == 83
    assert 'Z_CARRIER' not in allocations and 'X_LINK_SUPPORT' not in allocations
    mapping = {}
    pads = sorted(r['source_item_id'] for r in schedule if re.fullmatch(r'XR_SADDLE_[LR]_[123]_PAD_70x60x12p7', r['source_item_id']))
    sides = sorted(r['source_item_id'] for r in schedule if re.fullmatch(r'XR_SADDLE_[LR]_[123]_SIDE_60x80x9p525', r['source_item_id']))
    feet = sorted(r['source_item_id'] for r in schedule if r['schedule_id'].startswith('FRAME:XR_FOOT_PLATE_'))
    assert len(pads) == len(sides) == 6 and len(feet) == 8
    for i, item in enumerate(pads, 1): mapping['ACTUATOR_PAD_' + str(i)] = 'MOTION:' + item
    for i, item in enumerate(sides, 1): mapping['ACTUATOR_SIDE_' + str(i)] = 'MOTION:' + item
    for i, item in enumerate(feet, 1): mapping['FOOT_PLATE_' + str(i)] = 'FRAME:' + item
    mapping.update({'PLASMA_DROP': 'MOTION:XR_PLASMA_DROP_148',
                    'LINK_SUPPORT_WEB_1': 'MOTION:Y_LINK_SUPPORT_WEB_L', 'LINK_SUPPORT_WEB_2': 'MOTION:Y_LINK_SUPPORT_WEB_R',
                    'LINK_SUPPORT_FLANGE_1': 'MOTION:Y_LINK_SUPPORT_FLANGE_L', 'LINK_SUPPORT_FLANGE_2': 'MOTION:Y_LINK_SUPPORT_FLANGE_R',
                    'TOP_FISHPLATE_1': 'FRAME:XR_TOP_FISHPLATE_L_1', 'TOP_FISHPLATE_2': 'FRAME:XR_TOP_FISHPLATE_R_1'})
    for i in range(1, 33): mapping['TRACK_BACKING_BLOCK_' + str(i)] = 'BED:Track backing blocks'
    for i in range(1, 17): mapping['DOCK_PAD_' + str(i)] = 'BED:DOCK_PAD_ROUND_BORE' if i <= 8 else 'BED:DOCK_PAD_PLAIN'
    for family in ('CABINET_COVER_THREADED_TAB', 'CABINET_ROOF_THREADED_BLOCK'):
        for i in range(1, 5): mapping[family + '_' + str(i)] = 'BED:' + family
    assert set(mapping) == set(allocations), (set(mapping) ^ set(allocations))
    crosswalk = []
    by_id = {r['schedule_id']: r for r in schedule}
    credits = Counter(mapping.values())
    for aid, target in mapping.items():
        sheet, blank = allocations[aid]
        assert by_id[target]['additive_requirement']
        crosswalk.append(dict(owned_blank_id=aid, stock_sheet_id=sheet['id'], source_evidence_id='owned_stock_nest',
            source_file=rel(INPUTS['owned_stock_nest']), schedule_id=target,
            nest_x_mm=blank['x'], nest_y_mm=blank['y'], blank_width_mm=blank['w'], blank_height_mm=blank['h'],
            source_stock_thickness_mm=sheet['stock_t'], finished_thickness_mm=blank['finish_t'],
            qualification='Nominal nest only; actual size, alloy/temper, damage, flatness and cleanup allowance remain held.'))
    for target, q in credits.items():
        row = by_id[target]
        assert q <= row['quantity']
        row.update(ownership_status='OWNED_83_BLANK_NEST_CONDITIONAL_ALLOY_AND_STOCK_VERIFICATION',
                   owned_credit_quantity=q, new_required_quantity=row['quantity'] - q,
                   include_in_new_procurement=(row['quantity'] != q), status='OWNED_NEST_CREDIT_CONDITIONAL_NO_NEW_MATERIAL_FOR_ALLOCATED_BLANKS')
        row['evidence_and_qualification'] += ' | Owned credit: owned-stock-crosswalk.csv; only explicitly allocated blanks.'

    owner_notes = 'Latest owner instruction in current project: all motion, extra rails, drives, spindle/VFD kit and electronics enclosure already owned. Verify exact received interfaces; assembly ownership does not prove spare fasteners or new ATC subassemblies.'
    owned_components = [
        ('Y_MODULES', 2, 'Existing HMS40-class 1000 mm Y modules, complete assemblies', 'Two Y axes; actual mounting, lead, cable outlets/current held.'),
        ('X_MODULE', 1, 'Existing HMS40-class 800 mm X module, complete assembly', 'Actual output/base interfaces, lead and drive data held.'),
        ('Y_GUIDE_RAILS_BLOCKS', 1, 'Owned Y guide rail/block set; nominal two 1420 mm HGR20 rails/four blocks', 'Physical rail length/hole pitch, block preload and supplied fixing inventory held.'),
        ('X_GUIDE_RAILS_BLOCKS', 1, 'Owned X guide rail/block set; nominal two 1200 mm rails/four blocks', 'Inspect actual section, length, fixing pitch, blocks and supplied hardware.'),
        ('MOTION_DRIVES_CONTROLS', 1, 'Owned motion drivers/controllers, available set', 'Quantity/channel/voltage/current/firmware and integrated-driver capability require inventory; no new controller selected.'),
        ('SPINDLE_VFD_KIT', 1, 'Owned spindle/VFD kit', 'Actual spindle, shaft/nut geometry, reversal/speed and ATC compatibility held.'),
        ('ELECTRONICS_ENCLOSURE', 1, 'Owned electronics enclosure', 'Keep separate from red drain reservoir; actual dimensions/thermal/IP interfaces held.'),
        ('ORIGINAL_65MM_SPINDLE_CLAMP', 1, 'Owned original uncut 65 mm spindle clamp; exact supplied STEP', 'Owner requested preservation unchanged. Exact installed mating pose/fastener grip must be integrated.'),
        ('POWERED_50MM_DUST_BOOT', 1, 'Owned complete working powered 50 mm spindle dust boot; exact supplied STEP; Pegelong B0D6BCQCVR actuator', 'Owner confirms whole boot moves, original clamp unchanged, and existing assembly already works. Preserve it; installed machine attachment/home transform still needs integration. No new actuator purchase.'),
        ('PLASMA_CUTTER_TORCH', 1, 'Owned CUT-50/VIV arc machine and AG60-like torch, owner reported', 'Exact delivered starting circuit/connector/current/torch barrel and isolated CNC/height control interface remain held.'),
        ('AIR_COMPRESSOR', 1, 'Owned nominal 12 CFM air compressor', 'Actual pressure/duty and plasma+ATC simultaneous demand/filtration held.'),
        ('VENTURI_CV15HS', 1, 'Owned CV-15HS vacuum generator', 'Vacuum generator, not a liquid transfer pump; not a pressure-rated drain reservoir substitute.'),
    ]
    for item, q, spec, note in owned_components:
        add('OWNED', 'owner_latest_statement', '', 'Current owner instruction and owned-hardware-evidence.json',
            item, 'OWNER_REPORTED_EXISTING_EQUIPMENT', q, 'Existing complete assembly', spec,
            ownership='OWNER_REPORTED_OWNED_VERIFY_IDENTITY_AND_INTERFACE', credit=q, new=0,
            role='OWNED_COMPLETE_ASSEMBLY', status='OWNED_EXCLUDED_FROM_NEW_PROCUREMENT', notes=owner_notes + ' | ' + note,
            unit='set' if q == 1 and item.endswith(('KIT', 'CONTROLS', 'BLOCKS')) else 'each')

    # Recovered bed basis is an owner requirement, not evidence that the bed
    # material was bought. Purchase quantity stays held until the bases agree.
    for item, q, spec in [
        ('RETAINED_20100_BED', 10, 'Ten uncut1220mm20100 extrusions, nominal1000x1220 assembled bed'),
        ('RETAINED_HDPE_LAYERS', 2, 'Two full12.7mmHDPE layers; ordinary circular through-drilling only, no routed pockets/notches/counterbores or surfacing'),
    ]:
        add('RETAINED_BED', 'candidate_requirements', '', '', item, 'RECOVERED_OWNER_BED_REQUIREMENT', q,
            'Ownership unverified', spec, role='RETAINED_REQUIREMENT_RECONCILIATION', selected=False, new='',
            status='FINAL_BED_DESIGN_AND_PURCHASE_QUANTITY_HELD',
            notes='Current four routed plywood/MDF cassettes do not implement this retained owner basis. Do not credit material as owned or order either incompatible bed until engineering reconciles geometry/support/retention and approved fabrication process.')
    add('RETAINED_ATC', 'candidate_requirements', '', '', 'SELECTED_200MM_MAGAZINE_SLIDE', 'RECOVERED_OWNER_SELECTED_MAGAZINE_MODULE', 1,
        'Ownership unverified; selection known', '200 mm stroke /311 mm overall module; exact received mating interfaces held',
        role='RETAINED_REQUIREMENT_RECONCILIATION', selected=False, new='', status='ATC_ARCHITECTURE_AND_PURCHASE_QUANTITY_HELD',
        notes='Earlier selected module is not an instruction to buy a second slide. Current custom rail/belt mechanism is unselected pending reconciliation. Confirm supplied/owned contents and exact interfaces without guessing a new product.')

    # Required items omitted by the source takeoffs. They are explicit held
    # requirements, not invented vendor selections or free supplied hardware.
    add('SUPPLEMENT', 'source_motion_details', '', '', 'GANTRY_8080', 'INHERITED_GANTRY_STOCK_REQUIREMENT', 1,
        'Al extrusion, actual slot/section held', '1200 mm finished length, nominal 80x80 section',
        role='FINISHED_STOCK_REQUIREMENT',
        notes='make_motion() creates GANTRY_8080 from a 1200x80x80 envelope. Not part of the 19 chassis 4080 cuts. Not confirmed owned. '
              'This inherited gantry member conflicts with an interpretation of all-4080 for every machine member; keep visible until engineering selects/qualifies a final beam. Do not silently substitute 4080.')
    add('SUPPLEMENT', 'source_motion_finish', '', '', 'PLASMA_HEAD_NONCONDUCTIVE_TETHER', 'UNMODELED_REQUIRED_INTERFACE', 1,
        'Rated nonconductive tether and retention terminations', 'Fit owned torch/head mass; slack for 6 mm float and 8 mm normal release',
        role='INTERFACE_REQUIREMENT', notes='motion_finish.py explicitly requires this tether. Two modeled eye blocks are already in motion custom stock; this row is the distinct flexible restraint/terminations. Arrest load and attachment/cable routing held.')
    for item, spec, note in [
        ('Z300_POSITIVE_MOUNTING_SET', 'Actual base/output fasteners, mating nuts and positive retention; quantity not published', 'Do not assume a clearance-envelope contact is a fastened joint; measure received 300 mm module. Do not duplicate manufacturer-supplied contents once inspected.'),
        ('Z_POWER_OFF_RETENTION_SELECTION', 'Qualified retention arrangement; purchase quantity depends on selected method', 'Required safety function is unresolved. Optional new brake motor is separately excluded pending actual compatibility and stopping/holding proof.'),
        ('MACHINE_CABLE_CHAIN_GLAND_EARTH_SET', 'Route-measured complete motion/spindle/plasma cable containment, glands, strain relief and bonding interfaces', 'Existing electronics/drive ownership does not inventory these added frame interfaces. Exact quantities/lengths and plasma EMI/earthing design are held.'),
        ('ACTUAL_TORCH_CLAMP_BORE', 'Machine actual supplied-torch clamp inserts only after measuring approved barrel zone', 'I_HEAD_INSERT parts are blank candidate geometry, not a qualified AG60 bore or torch-start interface.'),
    ]:
        add('HOLD', 'owner_latest_statement', '', 'Current project interface register', item, 'UNRESOLVED_REQUIRED_INTERFACE', '',
            'Actual received interfaces', spec, role='UNRESOLVED_REQUIREMENT', new='', status='QUANTITY_OR_SELECTION_HOLD_NOT_ZERO', notes=note)

    # Repair-specific artifact pointers replace the two bad old part pointers.
    repair = source_manifests['custom_repair_manifest']
    custom_rows = []
    source_custom = read_csv(INPUTS['custom_index'])
    for original in source_custom:
        row = dict(original)
        item = row['id']
        row['source_index'] = rel(INPUTS['custom_index'])
        row['reference_scope'] = 'UNCHANGED_FROZEN_BASELINE_PART'
        row['selected_for_manufacture'] = item not in provisional_clamp
        row['fabrication_release'] = False
        row['operation_reference_dxf'] = ''
        row['operation_reference_dxf_sha256'] = ''
        row['operation_reference_instruction'] = ''
        row['step'] = rel(BASE / row['step'])
        if row['midsection_reference_dxf']:
            row['midsection_reference_dxf'] = rel(BASE / row['midsection_reference_dxf'])
        if item in ('Z_CARRIER', 'X_LINK_SUPPORT'):
            key, source_key = ('carrier', 'carrier_STEP') if item == 'Z_CARRIER' else ('support', 'support_STEP')
            meta = repair['outputs'][key]
            target = OUT / 'custom-step' / INPUTS[source_key].name
            shutil.copyfile(INPUTS[source_key], target)
            assert sha(target) == meta['sha256']
            row.update(step=rel(target), step_sha256=sha(target),
                       world_origin_mm=json.dumps(meta['source_world_min_corner_mm']),
                       world_aligned_size_mm=json.dumps([260., 12.7, 270.2] if key == 'carrier' else [156., 120.8, 43.35]),
                       volume_mm3='', step_roundtrip_valid=meta['valid'],
                       step_roundtrip_volume_error_mm3=meta['roundtrip_volume_error_mm3'],
                       step_roundtrip_bbox_error_mm='', midsection_reference_dxf='', midsection_reference_sha256='',
                       midsection_reference_transform='', reference_scope='OWNED_Z300_REPAIRED_CANDIDATE_SUPERSEDES_OLD_PART',
                       qualification=by_id['MOTION:' + item]['evidence_and_qualification'])
            by_id['MOTION:' + item]['artifacts'] = row['step']
        elif item in provisional_clamp:
            row['reference_scope'] = 'PROVISIONAL_SUBSTITUTE_DO_NOT_MACHINE_OWNER_CLAMP_INTEGRATION_HOLD'
            row['qualification'] += ' | Do not order or machine as final owner clamp. Integrate unchanged supplied original clamp/boot.'
        elif item in source_manifests['front_stop_repair_manifest']['outputs']:
            meta = source_manifests['front_stop_repair_manifest']['outputs'][item]
            original_step = HERE / meta['file']
            target = OUT / 'custom-step' / original_step.name
            shutil.copyfile(original_step, target)
            assert sha(target) == meta['sha256']
            row.update(step=rel(target), step_sha256=sha(target),
                       world_origin_mm=json.dumps(meta['source_world_min_corner_mm']),
                       world_aligned_size_mm=json.dumps([meta['bounds_local_mm'][i+3] - meta['bounds_local_mm'][i] for i in range(3)]),
                       volume_mm3='', step_roundtrip_valid=meta['valid'], step_roundtrip_volume_error_mm3='',
                       step_roundtrip_bbox_error_mm='', midsection_reference_dxf='', midsection_reference_sha256='',
                       midsection_reference_transform='', reference_scope='FRONT_STOP_REPAIR_CANDIDATE_SUPERSEDES_OLD_PART',
                       qualification=by_id['MOTION:' + item]['evidence_and_qualification'])
            by_id['MOTION:' + item]['artifacts'] = row['step']
            operation = source_manifests['front_stop_operation_manifest']['outputs'][item]
            op_source = HERE / operation['file']
            op_target = OUT / 'operation-reference' / op_source.name
            shutil.copyfile(op_source, op_target)
            assert sha(op_target) == operation['sha256']
            row['operation_reference_dxf'] = rel(op_target)
            row['operation_reference_dxf_sha256'] = sha(op_target)
            row['operation_reference_instruction'] = operation['instruction']
            by_id['MOTION:' + item]['artifacts'] += ' | ' + rel(op_target)
        custom_rows.append(row)

    # Confirm every linked generated manufacturing file, not merely manifests.
    artifact_checks = []
    for row in custom_rows:
        for field, hash_field in [('step', 'step_sha256'), ('midsection_reference_dxf', 'midsection_reference_sha256'), ('operation_reference_dxf', 'operation_reference_dxf_sha256')]:
            if row[field]:
                path = ROOT / row[field]
                artifact_checks.append(dict(file=row[field], expected_sha256=row[hash_field], actual_sha256=sha(path),
                                            passed=sha(path) == row[hash_field]))
    for key in ('bed_manifest', 'atc_manifest'):
        for file, expected in source_manifests[key]['output_sha256'].items():
            path = BASE / file.replace('\\', '/')
            actual = sha(path)
            artifact_checks.append(dict(file=rel(path), expected_sha256=expected, actual_sha256=actual, passed=actual == expected))
    for entry in source_manifests['shield_manifest']['manufacturing_files']:
        path = BASE / entry['file'].replace('\\', '/')
        actual = sha(path)
        artifact_checks.append(dict(file=rel(path), expected_sha256=entry['sha256'], actual_sha256=actual, passed=actual == entry['sha256']))
    assert all(entry['passed'] for entry in artifact_checks), 'Stale or modified manufacturing artifact'

    # Check provenance binding: a valid artifact manifest must also describe
    # the current frozen source that produced it, not just valid old files.
    bindings = []
    for manifest_key in ('frame_manifest', 'bed_manifest', 'bed_takeoff_manifest', 'shield_manifest',
                         'atc_manifest', 'custom_manifest'):
        for file, expected in source_manifests[manifest_key].get('source_sha256', {}).items():
            path = BASE / file
            actual = sha(path)
            bindings.append(dict(manifest_evidence_id=manifest_key, file=rel(path.resolve()),
                                 expected_sha256=expected, actual_sha256=actual, passed=actual == expected))
    assert all(entry['passed'] for entry in bindings), 'Stale manufacturing manifest/source binding'

    # Source snapshot copies have deliberately explicit baseline labels. The
    # raw sources retain their original categories/IDs, never act as a second BOM.
    snapshots = {}
    for key in ('frame_takeoff', 'motion_takeoff', 'bed_takeoff', 'shield_takeoff', 'atc_takeoff', 'atc_manifest'):
        path = OUT / 'source-evidence' / ('XR2_SOURCE_ONLY_' + key + INPUTS[key].suffix)
        shutil.copyfile(INPUTS[key], path)
        snapshots[key] = dict(file=rel(path), sha256=sha(path), matches_source=sha(path) == start[key],
                              role='EXACT_BASELINE_SOURCE_EVIDENCE_NOT_AN_ADDITIONAL_PURCHASE_LIST')
    write_csv(OUT / 'consolidated-schedule.csv', schedule)
    write_csv(OUT / 'new-procurement-requirements.csv', [r for r in schedule if r['include_in_new_procurement']])
    write_csv(OUT / 'reference-and-excluded-rows.csv', [r for r in schedule if not r['additive_requirement'] or not r['selected_base']])
    write_csv(OUT / 'owned-stock-crosswalk.csv', crosswalk)
    write_csv(OUT / 'candidate-custom-part-index.csv', custom_rows)
    write_json(OUT / 'artifact-hash-checks.json', artifact_checks)
    write_json(OUT / 'source-manifest-binding-checks.json', bindings)

    # No raw-stock option is additive to its already counted finished blank/cut.
    profile = read_json(INPUTS['profile_nest'])
    steel = read_json(INPUTS['steel_nest'])
    options = dict(role='NONADDITIVE_PURCHASE_PACKAGING_OPTIONS_FOR_EXISTING_REQUIREMENTS',
        prices_included=False, selected_stock_option=None, fabrication_release=False,
        chassis_4080=dict(cut_count=profile['cut_count'], finished_mm=profile['finished_mm'],
                         option_stock_mm={k: sum(b['stock_mm'] for b in v['bars']) for k,v in profile['options'].items()},
                         source=rel(INPUTS['profile_nest']), source_sha256=start['profile_nest'],
                         note='Choose one actual supplier option; no 4080 section/slot properties or cost inferred. Extra inherited gantry beam is separate.'),
        nominal_1p9_steel=dict(blank_count=steel['blank_count'], gross_blank_area_m2=steel['gross_blank_area_m2'],
                              options={k: dict(sheet_count=v['sheet_count'], nominal_sheet_mm=v['nominal_sheet_mm']) for k,v in steel['options'].items()},
                              source=rel(INPUTS['steel_nest']), source_sha256=start['steel_nest'],
                              note='One combined nest covers frame straps + bed + shields + ATC1.9 sheet. Other steel gauges/round stock/billets are separate. Do not add sheets on top of additive blank requirements.'),
        remaining_stock_gates=[
            'Z carrier new stock 260x270.2x12.7 finished; support new integral billet156x120.8x43.35 finished; cleanup allowance held.',
            'Two deep150x80x82.7 gantry billets and six clevis billets are new; not from the owned sheets.',
            'ATC moving wings require two NEW1x3x6in6061 blanks; final fused thickness19.875mm cannot come from6.35mm plate.',
            'Other ATC steel gauges,3.175mm motor tab, angles/round/EPDM/acetal/stainless and adhesive quantities need supplier-compatible stock packaging.',
            '9mm core plywood/9.525 MDF rows are material lots, not an asserted one-sheet retail package; no complete raw-sheet nest claimed.',
            'Owned83blank nest only: verify alloy/temper, actual dimensions, damage, cleanup, weld compatibility. No added owned material credit.',
            'No pricing, tax, shipping, availability or USD1000 delivered-budget claim.'
        ])
    write_json(OUT / 'stock-options-and-gates.json', options)
    ownership = dict(schema=1, latest_owner_statement=owner_notes,
        owned_Z_complete_assembly_quantity=1, new_Z200_purchase_removed=True,
        optional_brake_motor=dict(owned=False, selected_base=False, quantity=1, status='Only selected after qualified retention decision'),
        owned_stock_allocated_blank_count=len(crosswalk), owned_stock_credit_basis='Exact original83blank nest, no new blank allocation',
        spindle_clamp=dict(source_file=rel(INPUTS['owner_clamp_STEP']),
                           sha256='506d12b3f749db3eeec03e133b519fd93e45ff1b6cb80bd8fa568d3fb0dba1cb',
                           ownership='Owner supplied complete clamp, preserve unchanged', status='Pose and mating integration held'),
        dust_boot=dict(source_file=rel(INPUTS['owner_boot_STEP']),
                       sha256='3716855cf25a308de3db696ae827578d7803bfe4665fd1a6535f311a5246a044',
                       ownership='Owner confirms already working whole-moving powered50mm boot, preserve unchanged',
                       actuator='PegelongB0D6BCQCVR50mm12V40N0.6in/s owner-selected',
                       status='Installed machine attachment/home transform and moving clearances require integration; identity/clamp revision/moving-body scope already answered',
                       superseding_evidence=[rel(INPUTS[k]) for k in ('owner_working_boot','owner_head_decisions','owner_actuator_selection')]),
        interpretation='Latest owner assembly ownership overrides older not-ordered notes. It does not grant new material, replacement brake, ATC kit, new fasteners or unmeasured spare-channel credit.',
        prices_included=False, fabrication_release=False)
    write_json(OUT / 'ownership-decisions.json', ownership)

    selected_by_id = {r['schedule_id']: r for r in schedule}
    references_resolve = all(not r['covered_by'] or all(t in selected_by_id for t in r['covered_by'].split(';')) for r in schedule)
    atc = [r for r in schedule if r['source_evidence_id'] == 'atc_takeoff']
    stock_ids = [r['owned_blank_id'] for r in crosswalk]
    checks = dict(
        all_source_rows_retained=all(sum(r['source_evidence_id'] == key for r in schedule) == len(source_rows[key]) for key in source_rows),
        exact_ATC344_rows=len(atc) == 344,
        ATC_source_owned_and_procure_preserved=all(r['source_owned'] == src['owned'] and r['source_procure'] == src['procure'] and r['source_item_id'] == src['id'] for r,src in zip(atc,source_rows['atc_takeoff'])),
        ATC_63_assemblies_nonadditive=sum(not r['additive_requirement'] for r in atc) == 63,
        ATC_reference_rows_link_exact_stock=all(bool(r['covered_by']) for r in atc if not r['additive_requirement']),
        no_unselected_new_brake_in_base=not selected_by_id['MOTION:ZBX80_BRAKE_MOTOR_CANDIDATE']['include_in_new_procurement'],
        owned_Z300_one_no_new_Z200=selected_by_id['MOTION:ZBX80_BASE']['owned_credit_quantity'] == 1 and selected_by_id['MOTION:ZBX80_BASE']['new_required_quantity'] == 0,
        owned_83_exact_no_double_credit=len(stock_ids) == len(set(stock_ids)) == 83 and sum(r['owned_credit_quantity'] for r in schedule if r['ownership_status'].startswith('OWNED_83')) == 83,
        repaired_parts_new_no_owned_credit=all(selected_by_id['MOTION:' + k]['owned_credit_quantity'] == 0 and selected_by_id['MOTION:' + k]['new_required_quantity'] == 1 for k in ('Z_CARRIER','X_LINK_SUPPORT')),
        repaired_index_replaces_both_old_pointers=all('manufacturing/custom-step/' in r['step'] for r in custom_rows if r['id'] in ('Z_CARRIER','X_LINK_SUPPORT')),
        front_stop_index_replaces_four_old_pointers=all('manufacturing/custom-step/' in r['step'] and r['reference_scope'] == 'FRONT_STOP_REPAIR_CANDIDATE_SUPERSEDES_OLD_PART' for r in custom_rows if r['id'] in source_manifests['front_stop_repair_manifest']['outputs']),
        front_stop_four_source_repairs_present=len(source_manifests['front_stop_repair_manifest']['outputs']) == 4,
        no_old_split_clamp_order=all(not selected_by_id['MOTION:' + k]['include_in_new_procurement'] for k in provisional_clamp),
        no_proposal_bed_in_selected_procurement=all(not r['include_in_new_procurement'] for r in schedule if r['status'] == 'PROPOSAL_ONLY_OWNER_BED_REQUIREMENTS_CONFLICT'),
        no_unreconciled_ATC_alternative_order=all(not r['include_in_new_procurement'] and not r['selected_base'] for r in atc),
        eight_main_feet_once=sum(int(r['quantity']) for r in schedule if r['schedule_id'].startswith('FRAME:XR_RATED_FOOT_') and r['additive_requirement']) == 8 and not selected_by_id['FRAME:RATED_M8_ADJUSTER']['additive_requirement'],
        ledger_22_sets_once=not selected_by_id['FRAME:LEDGER_TO_ARM_M6_BED_SCOPE']['additive_requirement'] and selected_by_id['BED:Ledger fasteners']['quantity'] == 22,
        wood_rawstock_not_plus_profiles=all(not r['additive_requirement'] for r in schedule if r['source_evidence_id'] == 'bed_takeoff' and r['source_item_id'] in bed_flat_ids and r['material_or_spec'] in ('structural_plywood','MDF_finished_from_9p525','laminated_plywood_stock')),
        receiver_lid_not_second_purchase=not selected_by_id['BED:Receiver lid']['additive_requirement'],
        references_resolve=references_resolve,
        unknown_rail_fixings_not_zero=selected_by_id['MOTION:XR_Y_RAIL_M5_FIXINGS']['quantity'] == '' and selected_by_id['MOTION:XR_Y_RAIL_M5_FIXINGS']['new_required_quantity'] == '',
        linked_artifact_hashes_match=all(r['passed'] for r in artifact_checks),
        source_manifest_bindings_match=all(r['passed'] for r in bindings),
        source_consistent_during_build=start == {key: sha(path) for key,path in INPUTS.items()},
    )
    evidence = dict(schema=1, path_basis='Repository-relative paths unless explicitly called alternate local project evidence',
        sources={key: dict(file=rel(path), sha256=start[key]) for key,path in INPUTS.items()},
        source_snapshots=snapshots, latest_owner_statement_evidence='Current conversation; privacy-minimized interpretation in ownership-decisions.json',
        source_category_rule='Original source category/quantity/owned/procure remain separate columns; candidate decisions never rewrite source evidence.',
        baseline_modified=False, CAD_modified=False, prices_included=False)
    write_json(OUT / 'evidence-register.json', evidence)
    (OUT / 'README.md').write_text(README, encoding='utf-8')
    report = dict(schema=1, candidate='OWNED_Z300_STOCK_MOTOR_WORK200_REPAIRED_CUSTOM_JOINT',
        status='UNPRICED_REQUIREMENTS_RECONCILED_CAD_REQUIREMENTS_NOT_INTEGRATED_AND_PHYSICAL_RELEASE_HELD',
        CAD_requirements_not_integrated=['Unchanged owned working spindle clamp/powered boot at actual machine attachment/home transform',
                                        'Ten uncut1220mm20100 profiles plus two full drill-only12.7mmHDPE layers and compatible changeover/support',
                                        'Earlier selected200mmstroke/311mmoverall magazine module versus current unselected custom rail/belt proposal'],
        checks=checks, passed=all(checks.values()),
        counts=dict(source_takeoff_rows={key:len(value) for key,value in source_rows.items()},
                    consolidated_rows=len(schedule), additive_requirement_rows=sum(r['additive_requirement'] for r in schedule),
                    nonadditive_reference_rows=sum(not r['additive_requirement'] for r in schedule),
                    new_procurement_requirement_rows=sum(r['include_in_new_procurement'] for r in schedule),
                    unresolved_quantity_rows=sum(r['include_in_new_procurement'] and r['new_required_quantity'] == '' for r in schedule),
                    owned_stock_blank_allocations=len(crosswalk), custom_STEP_index_rows=len(custom_rows),
                    selected_candidate_owned_blank_allocations=sum(r['owned_credit_quantity'] for r in schedule if r['selected_base'] and r['ownership_status'].startswith('OWNED_83')),
                    linked_artifact_checks=len(artifact_checks)),
        source_manifest_binding_checks=len(bindings),
        source_sha256=start,
        output_sha256={rel(path):sha(path) for path in OUT.rglob('*') if path.is_file() and path.name != 'manufacturing-pack-check.json'},
        generator_sha256=sha(Path(__file__)), baseline_modified=False, CAD_modified=False,
        fabrication_release=False, pricing_performed=False, supplier_parts_verified=False,
        limits=['Passed means manifest reconciliation/hash/reference checks only, not a fabricated or operational machine.',
                'The filtered procurement CSV is a view of the consolidated schedule; never add the two together.',
                'Finished blanks/cuts are requirements; raw-stock packaging choices are nonadditive and need cleanup allowance.',
                'Still open CAD work: integrate unchanged owned working head, retained drill-only20100/HDPE bed and earlier selected magazine module; this is not only a measurement gate.',
                'Still held: delivered interfaces, exact ATC kit/spindle compatibility, retention, actual load/rigidity and commissioning acceptance.',
                'Unknown quantities are blank with a HOLD status; no complete cart or delivered price is asserted.'])
    write_json(OUT / 'manufacturing-pack-check.json', report)
    print(json.dumps(dict(passed=report['passed'], counts=report['counts'], checks=checks), indent=2))
    assert report['passed']

README = '''# Owned Z300 candidate — unpriced manufacturing requirements

This pack reconciles the existing frame, motion, wood bed, water pan, guards
and retractable ATC into one candidate requirement schedule. It retains every
source takeoff row, its category and its evidence ID. It is complete as a
traceable requirements register; it is **not released for fabrication, CAM
posting, shopping or a delivered-price claim**. Required unmeasured interfaces
are explicit holds, not zero-quantity purchases.

Read `consolidated-schedule.csv` first. Only rows with `additive_requirement=True`
are distinct requirements. Only `include_in_new_procurement=True` rows feed the
unpriced new-material view, `new-procurement-requirements.csv`. That CSV and
`reference-and-excluded-rows.csv` are filtered views, never additional BOMs.
`selected_base=False` means an alternative/provisional item is excluded from
the selected plan. Empty quantity/new quantity means unresolved, not zero.
Quantities count the stated unit: a joint set includes its listed screw,
washer and nut; a material lot is not a guessed retail package. Source
quantities are retained separately, including the old rail-fixing zero marker.

The frame has 19 chassis 4080 cuts, 12,357.4 mm finished total, eight main feet,
and 22 ledger fastener sets. The old duplicate foot station group and frame
ledger allowance are references. Raw wood sheets/lots replace their finished
profile stock requirements. The selected reservoir includes its lid. Shared
pad/rim/pin retention material is counted once. The inherited 1,200 mm 8080
gantry beam is a separate visible requirement and engineering decision; it is
not hidden inside the chassis 4080 count. An all-4080 gantry substitution is
not approved by this pack.

The four routed plywood/MDF cassettes, their raw materials, locator/clamp
hardware and cassette storage cabinet are **proposal-only, unselected**.
The recovered owner basis is ten uncut 1,220 mm 20100 bed profiles over two
full 12.7 mm HDPE layers, with ordinary circular drilling only. Those bed
materials are not proven owned. Their final mounting/support/retention and
purchase quantities remain held; neither competing bed is a final order
list. See the machine-level `../STATUS.md` and `../candidate-requirements.json`.

The ATC source is exactly 344 rows: 63 nonadditive assembly/part references
and 281 additive source requirements. All remain **proposal-only, unselected**
pending reconciliation with the earlier owner-selected 200 mm-stroke,
311 mm-overall ATC module. The original `owned` and `procure` flags remain
in provenance columns; they are not an instruction to order a competing
custom rail/belt architecture. Its 17 assembly decompositions, deep moving
wing billets, split lock-flag sheet pieces and all source STEP/DXF hashes are
retained. A new driver channel is not silently charged when the owner already
reports drives: that row requires an owned-channel capacity check. The ATC
kit and its actual magazine interfaces remain unselected/unverified.

Owned X/Y motion assemblies, extra guide rails/blocks, drives, spindle/VFD,
electronics enclosure, plasma equipment and compressor are excluded from new
procurement on the latest owner statement. Exact supplied contents, channel
counts and interfaces still need inspection. The selected Z is **one owned
RATTMMOTOR ZBX80, 300 mm catalog-travel module with stock motor**. The prior
new 200 mm replacement is removed. Assessed working Z remains 200 mm; full
300 mm operation and controller limits are not qualified. The optional new,
unowned brake motor is excluded pending a compatible qualified retention
choice; the retention function itself remains mandatory and unresolved.

`owned-stock-crosswalk.csv` assigns exactly the existing 83 nested blanks
once to their target requirements. Only those blanks receive conditional
owned material credit. The two 12-inch sheets still require alloy/temper,
flatness, damage, true dimensions and cleanup verification. The Z carrier,
X-link support, main gantry billets, clevises and deep ATC wings gain no new
owned credit. `stock-options-and-gates.json` records alternative profile/sheet
packaging; do not add raw sheet/bar options on top of the listed blank/cut
requirements. Other gauges and unfinished stock packaging remain unpriced.

Use `candidate-custom-part-index.csv` for the 174 frame/motion custom STEP
references. Unchanged parts point to hash-checked frozen XR2 files. The two
repaired Z-joint parts point only to the clearly named candidate STEP copies here:

- `custom-step/Z_CARRIER_RELIEVED_CANDIDATE.step`: finished blank
  260 x270.2 x12.7 mm. Through relief 162.95 x6.55 mm, R3.275 ends; center
  local face X/Z =130/173.475 mm. Thickness is world Y. Preserve the ledge,
  four full M6 head seats and existing guide interfaces. Z300 mount positions
  must be measured and checked against the relief; no OEM hole pattern is invented.
- `custom-step/X_LINK_SUPPORT_D37_CANDIDATE.step`: integral new billet,
  **156 x120.8 x43.35 mm finished envelope**, with a 37 mm downstand.
  Add saw/facing cleanup allowance before choosing raw billet. Do not use
  the old 36.35 mm envelope or attach an extra strip. Four specified 5.0 mm
  pilots are tapped M6x1 through the 8 mm downstand; nominal STEP thread
  cylinders are 6 mm major envelopes, not tap-drill sizes. Lower-row edge
  distance is 9 mm, nominal radial ligament 6 mm. Material/thread tolerance,
  engagement and load proof remain held. Two upper pilots are 3.3 mm,
  tapped M4x0.7 through 6.35 mm.

Four revised front-stop/bracket STEP files also replace their old pointers.
Their base operation-reference DXFs are under `operation-reference/`: old
Y90 mounting holes are absent; the new front mount is Y105 and the rear
stays Y140, at X58.5/1091.5. The bracket base has the specified full-depth
motor-clearance corner relief. Carrier circles are nominal M6 major-envelope
references: specify a suitable nominal 5 mm pilot and M6x1 tap, not a drilled
6 mm clearance hole. Manufacture new corrected parts; no hole-plug welding
instruction is implied. The reduced 35 mm mounting spacing requires capacity
qualification. The two existing M6x12 front screws move +15 mm in Y.

Old XR2 carrier/support and these four front-stop files/notes are superseded for this candidate.
The source snapshot copies are deliberately labeled SOURCE_ONLY and are not
manufacturing authority for the six repaired custom parts. Other MIDSECTION_REFERENCE
DXFs are checking sections, not complete machining drawings. Counterbores,
edge holes, threads, welds, forming and setup belong to the referenced STEP,
source notes and physical acceptance process. Finished bounding blanks do
not include machining cleanup allowance.

The owner supplied an original uncut 65 mm spindle clamp and a complete
powered 50 mm dust boot to preserve unchanged. The current XR2 split-clamp
substitute and its six fasteners are excluded from ordering/manufacture as
the final interface. Their STEP references are explicitly provisional.
Owned clamp/boot identity is recorded in `ownership-decisions.json`. Later
owner records already confirm the clamp revision, whole-boot moving scope,
working assembly and Pegelong B0D6BCQCVR 50 mm actuator. These are answered
requirements. Installed machine attachment/home registration and moving
clearances remain an integration gate. See `../OWNER-HEAD-INTEGRATION.md`.
No new boot actuator is inferred or purchased.

Welded motion-stop assemblies are nonadditive references with separately
listed source-defined constituent blank requirements. Their parent STEP
contains the shaped perimeters/holes; no production child DXF or qualified
weld procedure is implied. The actual rated nonconductive plasma-head
tether, positive Z300 mounting set, power-off retention selection and final
cable/gland/bonding interfaces are also explicit requirements/holds.

The red reservoir is atmospheric, gravity drained and floor supported. Its
real interior usable capacity/rim/lid, water/temperature compatibility and
service access remain physical gates. A CV-15HS vacuum generator is not a
liquid pump. This pack does not authorize pressurizing the consumer tote.

Reproduce with `python variants/owned-z300-assessment/build_manufacturing_pack.py`.
`manufacturing-pack-check.json` records row/ownership/reference checks,
source consistency and output hashes. `artifact-hash-checks.json` verifies
the linked baseline manufacturing artifacts. These tests establish a
reconciled traceable list, not supplier fit, structural qualification,
physical commissioning, price/tax/shipping or compliance with the USD1,000
delivered budget. Baseline geometry and manufacturing files are unchanged.
'''

if __name__ == '__main__':
    build()
