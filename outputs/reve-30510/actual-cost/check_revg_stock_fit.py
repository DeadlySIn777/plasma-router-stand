"""Check that the sheet, plate and bar stock in the cost register covers a revision's flat parts.

Packs the actual DXF outlines (RevG-CAD/dxf by default, CUT_OUTER extents) onto each
purchased or requested stock size with the project's own MaxRects packer
(nest_flat_parts.py: 10 mm edge margin, 6 mm part spacing, rotations allowed),
then compares the pieces needed with the quantity in metal-findings.json.
Writes revg-stock-fit.json (or --out). Rectangular envelopes only: final
kerf-compensated nesting and grain/flatness choices remain the fabricator's.

Run with the CAD Python environment (needs ezdxf):  python check_revg_stock_fit.py
Rev J:  python check_revg_stock_fit.py --cad RevJ-CAD --out revj-stock-fit.json
"""
from pathlib import Path
from collections import defaultdict
import argparse, hashlib, json, math, sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
REVG = PROJECT / 'output/release-review/RevG-CAD'
ENG = PROJECT / 'output/release-review/RevE-ENGINEERING'
sys.path.insert(0, str(ENG))
import ezdxf
from ezdxf import bbox as dxf_bbox
import nest_flat_parts as nf

IN = 25.4
# (material group, finished thickness) -> stock row in metal-findings.json.
# 'exclude' lists parts the register already cuts from other stock.
STOCK = {
    ('carbon_steel', 6):     {'row': 'MET13', 'size_in': (24, 48), 'exclude': ['CAP_SPACER'],
                              'note': 'CAP_SPACER is cut from the MET05 flat bars.'},
    ('carbon_steel', 8):     {'row': 'MET14', 'size_in': (12, 24), 'also_try_in': [(12, 36), (24, 24)]},
    ('carbon_steel', 12.7):  {'row': 'MET15', 'size_in': (12, 12)},
    ('carbon_steel', 3.048): {'row': 'MET-GAP-1', 'size_in': (48, 96)},
    ('carbon_steel', 3):     {'row': 'MET-GAP-2', 'size_in': (36, 48)},
    ('carbon_steel', 1.5):   {'row': 'MET-GAP-3', 'size_in': (24, 24)},
    ('stainless_confirm_grade', 1):     {'row': 'MET-GAP-4', 'size_in': (12, 12)},
    ('stainless_confirm_grade', 1.5):   {'row': 'MET-GAP-5', 'size_in': (24, 36)},
    ('stainless_confirm_grade', 2):     {'row': 'MET-GAP-6', 'size_in': (12, 12)},
    ('stainless_confirm_grade', 3.048): {'row': 'MET-GAP-7', 'size_in': (12, 12)},
    ('stainless_confirm_grade', 6):     {'row': 'MET-GAP-8', 'size_in': (12, 12)},
    ('MDF_18_mm_finished', 18):         {'row': 'MET-GAP-14', 'size_in': (48, 96), 'also_try_in': [(48, 48)]},
    # Rev J: HDPE top plates, 3/8 in lift lugs (same raw plate as the 8 mm parts), stainless bolt tray.
    ('HDPE_sheet_3_4_in_finish_18_0', 18): {'row': None, 'size_in': (48, 48), 'also_try_in': [(24, 48), (48, 96)],
                              'note': 'Rev J top plates, 3/4 in HDPE finished 18.0 in place.'},
    ('carbon_steel', 9.525): {'row': 'MET14', 'size_in': (12, 24), 'merge_into': ('carbon_steel', 8),
                              'note': 'Rev J lift lugs are cut from the same 3/8 in plate as the 8 mm parts; packed together.'},
    ('stainless_confirm_grade', 3): {'row': None, 'size_in': (12, 12), 'also_try_in': [(12, 24)],
                              'note': 'Rev J bolt tray; 3 mm or 11 ga (3.048) sheet.'},
    # Not covered by any row before this check; sizes are suggestions to test.
    ('carbon_steel', 2):     {'row': None, 'size_in': (12, 24), 'also_try_in': [(12, 12), (24, 24)]},
    ('aluminum_confirm_alloy', 9.525): {'row': None, 'size_in': (12, 12), 'also_try_in': [(12, 24), (24, 24)],
                              'note': 'Plate option; a 3/8 x 1 in flat bar is checked separately below.'},
}
SEEDS = 180


def register_quantities():
    metal = json.loads((HERE / 'metal-findings.json').read_text(encoding='utf-8-sig'))
    qty = {r['id']: r['quantity'] for r in metal['published_stock_candidates']}
    for i, r in enumerate(metal['quote_only_raw_stock_schedule'], 1):
        qty[f'MET-GAP-{i}'] = r['quantity']
    return qty


NOT_SHEET = ('tube', 'pipe', 'billet', 'bar', 'rod', 'rubber', 'epdm', 'plug', 'sleeve')


def flat_items(cad):
    """DXF extents where a flat export exists; otherwise model bounds for parts whose
    smallest dimension equals a sheet thickness of their material (small guards,
    cradles, bosses and spacers that the CAD does not export as DXF)."""
    rows = json.loads((cad / 'cutlist.json').read_text(encoding='utf-8-sig'))
    sheet_t = defaultdict(set)
    for group, t in STOCK:
        sheet_t[group].add(t)
    groups = defaultdict(list)
    for row in rows:
        pn = row['part_number']; src = cad / 'dxf' / (pn + '.dxf')
        if row.get('individual_export_guarded'):
            continue
        group = nf.material_group(row)
        if src.exists():
            doc = ezdxf.readfile(src)
            outer = [e for e in doc.modelspace() if e.dxf.layer == 'CUT_OUTER']
            ext = dxf_bbox.extents(outer)
            w, h = ext.extmax.x - ext.extmin.x, ext.extmax.y - ext.extmin.y
            key, basis = (group, row['thickness_mm']), 'dxf'
        else:
            if any(word in row['material'].lower() for word in NOT_SHEET):
                continue
            b = row['bounds_local_mm']
            t, w, h = sorted((b[3] - b[0], b[4] - b[1], b[5] - b[2]))
            match = [s for s in sheet_t[group] if abs(s - t) < 0.05]
            if not match:
                continue
            key, basis = (group, match[0]), 'model bounds, no DXF'
        for n in range(row['quantity']):
            groups[key].append({'part_number': pn, 'copy': n + 1, 'w': w, 'h': h, 'basis': basis})
    return groups


def pieces_needed(items, size_mm):
    nf.STOCK = size_mm
    usable = (size_mm[0] - 2 * nf.EDGE) * (size_mm[1] - 2 * nf.EDGE)
    for p in items:
        if min(p['w'], p['h']) + nf.GAP > min(size_mm) - 2 * nf.EDGE + nf.GAP or \
           max(p['w'], p['h']) + nf.GAP > max(size_mm) - 2 * nf.EDGE + nf.GAP:
            return None
    best = min((nf.pack(items, m) for m in ('area', 'long', 'perimeter')), key=len)
    lower = math.ceil(sum(p['w'] * p['h'] for p in items) / usable)
    for seed in range(SEEDS):
        if len(best) <= lower:
            break
        trial = nf.pack(items, ('area', 'long', 'perimeter')[seed % 3], seed)
        if len(trial) < len(best):
            best = trial
    return len(best)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cad', default='RevG-CAD', help='CAD package folder under output/release-review')
    parser.add_argument('--out', default='revg-stock-fit.json')
    args = parser.parse_args()
    cad = PROJECT / 'output/release-review' / args.cad
    qty = register_quantities()
    groups = flat_items(cad)
    for key, spec in STOCK.items():
        if spec.get('merge_into') and key in groups:
            groups.setdefault(spec['merge_into'], []).extend(groups.pop(key))
    results = []
    for key, spec in sorted(STOCK.items(), key=lambda kv: str(kv[0])):
        if spec.get('merge_into'):
            continue
        items = [p for p in groups.get(key, []) if p['part_number'] not in spec.get('exclude', [])]
        if not items:
            results.append({'material': key[0], 'thickness_mm': key[1], 'row': spec['row'], 'parts': 0,
                            'result': f'NO {args.cad} PARTS IN THIS GROUP'})
            continue
        options = []
        for size_in in [spec['size_in']] + spec.get('also_try_in', []):
            size_mm = (size_in[0] * IN, size_in[1] * IN)
            options.append({'stock_in': list(size_in), 'pieces_needed': pieces_needed(items, size_mm)})
        need = options[0]['pieces_needed']
        have = qty.get(spec['row']) if spec['row'] else None
        if spec['row'] is None:
            result = 'NEW REQUIREMENT: no stock row covers these parts'
        elif need is None:
            result = 'PART DOES NOT FIT THE REGISTERED STOCK SIZE'
        else:
            result = 'COVERED' if need <= have else f'SHORT: needs {need}, register has {have}'
        results.append({'material': key[0], 'thickness_mm': key[1], 'row': spec['row'], 'register_quantity': have,
                        'parts': len(items), 'part_numbers': sorted({p['part_number'] for p in items}),
                        'placed_from_model_bounds': sorted({p['part_number'] for p in items if p['basis'] != 'dxf'}),
                        'blank_area_m2': round(sum(p['w'] * p['h'] for p in items) / 1e6, 4),
                        'options': options, 'result': result, **({'note': spec['note']} if spec.get('note') else {})})
    # Panel ties as flat bar: 250 mm long, 20 mm finished width from 1 in (25.4) bar, 3 mm kerf, 10 mm trim.
    ties = sum(len([p for p in v if p['part_number'].startswith('G_PANEL_TIE')]) for v in groups.values())
    per_bar = int((72 * IN - 10 + 3) // (250 + 3))
    if ties:
        results.append({'material': 'aluminum 3/8 x 1 in flat bar, 72 in', 'thickness_mm': 9.525, 'row': None,
                        'parts': ties, 'ties_per_72in_bar': per_bar, 'bars_needed': math.ceil(ties / per_bar),
                        'result': 'NEW REQUIREMENT: bar option for the 250 x 20 x 9.525 panel ties (machine 25.4 width to 20)'})
    report = {'cad_package': args.cad, 'source_cutlist_sha256': hashlib.sha256((cad / 'cutlist.json').read_bytes()).hexdigest(),
              'packer': 'nest_flat_parts.pack, 10 mm edge, 6 mm spacing, rectangular DXF extents',
              'groups': results}
    (HERE / args.out).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    for r in results:
        print(f"{r['material'][:30]:30} {r['thickness_mm']!s:6} {str(r['row']):10} parts={r['parts']:3} {r['result']}  {r.get('options', '')}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
