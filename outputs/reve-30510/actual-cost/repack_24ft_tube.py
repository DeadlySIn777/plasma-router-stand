"""Repack the frozen 36 tube blanks into five 24 ft bars; no CAD changes."""
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
SRC = OUT.parents[2] / 'output/release-review/RevE-ENGINEERING/tube-cut-plan.json'
source = json.loads(SRC.read_text())
parts = [p.copy() for bar in source['bars'] for p in bar['cuts']]
counts = Counter(round(p['length_mm'] * 10) for p in parts)
lengths = sorted(counts, reverse=True)
amounts = tuple(counts[x] for x in lengths)
costs = [x + 30 for x in lengths]  # 3 mm kerf for every separated blank
capacity = 73152 - 100  # 24 ft exactly, less 10 mm total end trim
patterns = []

def enumerate_patterns(i, pattern, used):
    if i == len(lengths):
        if used >= sum(n*c for n, c in zip(amounts, costs)) - 4 * capacity:
            patterns.append((tuple(pattern), used))
        return
    for n in range(min(amounts[i], (capacity-used)//costs[i])+1):
        enumerate_patterns(i+1, pattern+[n], used+n*costs[i])

enumerate_patterns(0, [], 0)
# Prefer roughly equal leftovers over a bar with no cleanup margin.
target = sum(n*c for n, c in zip(amounts, costs)) / 5
patterns.sort(key=lambda p: abs(p[1]-target))

@lru_cache(None)
def solve(remaining, bins):
    required = sum(n*c for n, c in zip(remaining, costs))
    if required > bins*capacity:
        return None
    if bins == 1:
        return (remaining,) if required <= capacity else None
    first = next((i for i, n in enumerate(remaining) if n), None)
    if first is None:
        return ()
    for pattern, used in patterns:
        if not pattern[first] or any(p > n for p, n in zip(pattern, remaining)):
            continue
        tail = solve(tuple(n-p for n, p in zip(remaining, pattern)), bins-1)
        if tail is not None:
            return (pattern,) + tail
    return None

solution = solve(amounts, 5)
assert solution is not None, 'Five-bar packing not found'
pool = defaultdict(list)
for p in parts:
    pool[round(p['length_mm']*10)].append(p)
bars = []
for i, pattern in enumerate(solution, 1):
    cuts = []
    for length, n in zip(lengths, pattern):
        cuts.extend(pool[length].pop() for _ in range(n))
    net = round(sum(p['length_mm'] for p in cuts), 3)
    kerf = len(cuts)*3
    remaining = round(7315.2-10-kerf-net, 3)
    bars.append(dict(bar=i, cuts=cuts, net_mm=net, kerf_total_mm=kerf,
                     end_trim_total_mm=10, offcut_mm=remaining))
original_ids = Counter((p['part'],p['copy'],p['length_mm']) for p in parts)
packed_ids = Counter((p['part'],p['copy'],p['length_mm']) for b in bars for p in b['cuts'])
assert original_ids == packed_ids
assert len(bars) == 5 and len(parts) == 36
assert all(b['offcut_mm'] >= 0 for b in bars)
result = dict(
    source=str(SRC), source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
    calculation_date='2026-09-24', stock='2 x 2 inch square steel tube; existing model wall 0.120 inch',
    candidate_advertised_wall='1/8 inch, seller claim; grade and actual measured wall unverified',
    stock_qty=5, bar_length_mm=7315.2, kerf_per_cut_mm=3.0, trim_per_bar_mm=10.0,
    part_count=len(parts), net_length_mm=round(sum(p['length_mm'] for p in parts), 3),
    five_24ft_fit=True, min_offcut_mm=min(b['offcut_mm'] for b in bars),
    total_offcut_mm=round(sum(b['offcut_mm'] for b in bars),3),
    candidate_goods_usd=575.0, prior_six_20ft_goods_usd=930.9,
    candidate_goods_difference_usd=355.9,
    verification='All 36 source blanks assigned exactly once. All five bars fit with 3 mm kerf per blank and 10 mm total end trim per bar.',
    limitations='Blank-length feasibility only. Seller claims and usable lengths must be verified. Weathering/straightness/coating/grade are unqualified. Wall is advertised 1/8 inch, not verified 0.120 inch; qualify against design before substitution. Pickup, tax, inspection and cleanup are not priced. No CAD or purchase total changed.',
    bars=bars)
(OUT/'marketplace-24ft-cut-proof.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('five_24ft_fit','stock_qty','part_count','net_length_mm','min_offcut_mm','total_offcut_mm','candidate_goods_usd','candidate_goods_difference_usd')},indent=2))
