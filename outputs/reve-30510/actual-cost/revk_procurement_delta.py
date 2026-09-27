"""What GM1 Rev K adds to the Rev J shopping list, computed from the two cut lists.

Compares output/release-review/RevJ-CAD/cutlist.json with RevK-CAD/cutlist.json
part number by part number, and lists the GM1 controls parts
(output/controls-2026-09-27/gm1-components.json, "added"). Writes
revk-procurement-delta.json. Nothing here is priced: the Rev K and controls items
are new scope, recorded unpriced until offers are linked. Stdlib only.
"""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
CAD = PROJECT / 'output/release-review'
CONTROLS = PROJECT / 'output/controls-2026-09-27/gm1-components.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def rows(rev):
    return {r['part_number']: r for r in load(CAD / f'Rev{rev}-CAD' / 'cutlist.json')}


def kind(row):
    if 'PURCHASED' in (row['status'] or '') or row['part_number'].startswith(('BUY_', 'STD_', 'OWNER_', 'I_STD_', 'K_STD_', 'IGUS_', 'OMRON_', 'SUPERMAGNETE_')):
        return 'purchased'
    if row.get('length_mm') and 'tube' in (row['material'] or '').lower():
        return 'tube'
    if row.get('thickness_mm'):
        return 'flat'
    return 'machined or other'


def describe(row):
    b = row['bounds_local_mm']
    dims = sorted(round(b[i + 3] - b[i], 2) for i in range(3))
    return {'part_number': row['part_number'], 'quantity': row['quantity'], 'material': row['material'],
            'kind': kind(row), 'length_mm': row.get('length_mm'), 'thickness_mm': row.get('thickness_mm'),
            'envelope_mm': dims, 'status': row['status']}


def main():
    j, k = rows('J'), rows('K')
    removed = [describe(j[p]) for p in sorted(j) if p not in k]
    added = [describe(k[p]) for p in sorted(k) if p not in j]
    changed = [{'part_number': p, 'rev_j_quantity': j[p]['quantity'], 'rev_k_quantity': k[p]['quantity'], 'material': k[p]['material']}
               for p in sorted(j) if p in k and j[p]['quantity'] != k[p]['quantity']]
    by_kind = defaultdict(lambda: {'removed_rows': 0, 'removed_pieces': 0, 'added_rows': 0, 'added_pieces': 0})
    for r in removed:
        by_kind[r['kind']]['removed_rows'] += 1
        by_kind[r['kind']]['removed_pieces'] += r['quantity']
    for r in added:
        by_kind[r['kind']]['added_rows'] += 1
        by_kind[r['kind']]['added_pieces'] += r['quantity']
    flats = defaultdict(list)
    for r in added:
        if r['kind'] == 'flat':
            flats[f"{r['material']} | {r['thickness_mm']:g} mm"].append({'part_number': r['part_number'], 'quantity': r['quantity'],
                                                                         'envelope_mm': r['envelope_mm']})
    controls = load(CONTROLS)
    report = {'scope': __doc__.strip(),
              'source_sha256': {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in
                                (('RevJ-CAD/cutlist.json', CAD / 'RevJ-CAD/cutlist.json'),
                                 ('RevK-CAD/cutlist.json', CAD / 'RevK-CAD/cutlist.json'),
                                 ('controls-2026-09-27/gm1-components.json', CONTROLS))},
              'summary_by_kind': dict(by_kind), 'removed_part_numbers': removed, 'added_part_numbers': added,
              'quantity_changes': changed, 'added_flat_parts_by_stock': dict(flats),
              'controls_parts_added': controls['added'], 'controls_parts_retired': controls['retired_from_rev_i'],
              'priced': False}
    (HERE / 'revk-procurement-delta.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'summary_by_kind': report['summary_by_kind'], 'quantity_changes': changed,
                      'removed': [r['part_number'] for r in removed]}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
