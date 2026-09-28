"""What GM1 Rev J changes in the shopping list, computed from the two cut lists.

Compares output/release-review/RevG-CAD/cutlist.json with RevJ-CAD/cutlist.json
part number by part number, then the two tube plans and the two stock-fit
reports (check_revg_stock_fit.py with --cad). Writes revj-procurement-delta.json.
Stdlib only.
"""
from pathlib import Path
from collections import defaultdict
import hashlib, json, sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
CAD = PROJECT / 'output/release-review'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def rows(rev):
    return {r['part_number']: r for r in load(CAD / f'Rev{rev}-CAD' / 'cutlist.json')}


def kind(row):
    if 'PURCHASED' in row['status']:
        return 'purchased'
    if row.get('length_mm') and 'tube' in row['material'].lower():
        return 'tube'
    if row.get('thickness_mm'):
        return 'flat'
    return 'machined or other'


def describe(row):
    b = row['bounds_local_mm']
    dims = sorted(round(b[i + 3] - b[i], 2) for i in range(3))
    return {'part_number': row['part_number'], 'quantity': row['quantity'], 'material': row['material'],
            'kind': kind(row), 'length_mm': row.get('length_mm'), 'thickness_mm': row.get('thickness_mm'),
            'envelope_mm': dims}


def main():
    g, h = rows('G'), rows('J')
    removed = [describe(g[p]) for p in sorted(g) if p not in h]
    added = [describe(h[p]) for p in sorted(h) if p not in g]
    changed = [{'part_number': p, 'rev_g_quantity': g[p]['quantity'], 'rev_j_quantity': h[p]['quantity'], 'material': h[p]['material']}
               for p in sorted(g) if p in h and g[p]['quantity'] != h[p]['quantity']]
    by_kind = defaultdict(lambda: {'removed_rows': 0, 'removed_pieces': 0, 'added_rows': 0, 'added_pieces': 0})
    for r in removed:
        by_kind[r['kind']]['removed_rows'] += 1; by_kind[r['kind']]['removed_pieces'] += r['quantity']
    for r in added:
        by_kind[r['kind']]['added_rows'] += 1; by_kind[r['kind']]['added_pieces'] += r['quantity']
    tube = {}
    for rev in 'GJ':
        plan = load(CAD / f'Rev{rev}-CAD' / 'tube-cut-plan.json')
        tube[f'rev_{rev.lower()}'] = {'bars_20ft': plan['stock_qty'], 'pieces': plan['part_count'], 'net_length_mm': plan['net_length_mm'],
                                      'offcuts_mm': [b['offcut_mm'] for b in plan['bars']]}
    fit = {}
    for rev, name in (('g', 'revg-stock-fit.json'), ('j', 'revj-stock-fit.json')):
        report = load(HERE / name)
        fit[f'rev_{rev}'] = [{'material': r['material'], 'thickness_mm': r['thickness_mm'], 'row': r['row'], 'parts': r['parts'],
                              'result': r['result'], 'options': r.get('options')} for r in report['groups']]
    report = {'scope': __doc__.strip(),
              'source_sha256': {f'Rev{rev}-CAD/cutlist.json': hashlib.sha256((CAD / f'Rev{rev}-CAD' / 'cutlist.json').read_bytes()).hexdigest()
                                for rev in 'GJ'},
              'summary_by_kind': dict(by_kind), 'removed_part_numbers': removed, 'added_part_numbers': added,
              'quantity_changes': changed, 'tube_2x2_plan': tube, 'stock_fit': fit}
    (HERE / 'revj-procurement-delta.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'summary_by_kind': report['summary_by_kind'], 'quantity_changes': changed, 'tube_2x2_plan': tube}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
