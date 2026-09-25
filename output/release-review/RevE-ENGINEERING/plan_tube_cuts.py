"""Nest modeled 2x2 square tubes into full 20ft bars, including saw loss."""
from pathlib import Path
from functools import lru_cache
import json, math

ROOT=Path(__file__).resolve().parent
BAR=6096.0
TRIM=10.0
KERF=3.0

def main():
    rows=json.loads((ROOT/'cutlist.json').read_text(encoding='utf-8-sig'))
    pieces=[]
    for row in rows:
        length=row.get('length_mm')
        if length is None: continue
        b=row['bounds_local_mm']
        dims=sorted(b[i+3]-b[i] for i in range(3))
        if abs(dims[0]-50.8)>1e-3 or abs(dims[1]-50.8)>1e-3: continue
        if 'steel' not in row['material'].lower() and 'a500' not in row['material'].lower():continue
        for i in range(row['quantity']):pieces.append({'part':row['part_number'],'copy':i+1,'length_mm':round(length,3)})
    assert pieces,'No tube pieces found'
    pieces.sort(key=lambda p:p['length_mm'],reverse=True)
    cap=round((BAR-TRIM)*1000)
    weights=[round((p['length_mm']+KERF)*1000) for p in pieces]
    assert max(weights)<=cap
    best=[];remaining=[]
    for i,w in enumerate(weights):
        suitable=[j for j,r in enumerate(remaining) if r>=w]
        if suitable:
            j=min(suitable,key=lambda j:remaining[j]);remaining[j]-=w;best[j].append(i)
        else:best.append([i]);remaining.append(cap-w)
    lower=math.ceil(sum(weights)/cap)
    # Group equal lengths so exact pattern search is not swamped by permutations
    # of identical blanks. Every bin must leave no more than the total spare.
    kinds=sorted(set(weights),reverse=True)
    counts=tuple(weights.count(w) for w in kinds)
    @lru_cache(None)
    def grouped_plan(left,bins):
        total=sum(c*w for c,w in zip(left,kinds))
        if not total:return ()
        if not bins or total>bins*cap:return None
        if bins==1:return (left,) if total<=cap else None
        first=next(i for i,c in enumerate(left) if c)
        minimum=max(0,total-(bins-1)*cap)
        patterns=[]
        def enumerate_patterns(i,used,pattern):
            if i==len(kinds):
                if used>=minimum:patterns.append((cap-used,tuple(pattern)))
                return
            for n in range(min(left[i],(cap-used)//kinds[i]),-1,-1):
                if i==first and n==0:continue
                enumerate_patterns(i+1,used+n*kinds[i],pattern+[n])
        enumerate_patterns(0,0,[])
        for _,pattern in sorted(patterns):
            rest=tuple(a-b for a,b in zip(left,pattern))
            tail=grouped_plan(rest,bins-1)
            if tail is not None:return (pattern,)+tail
        return None
    grouped=grouped_plan(counts,lower)
    if grouped is not None:
        indices={w:[i for i,v in enumerate(weights) if v==w] for w in kinds}
        best=[[indices[w].pop() for w,n in zip(kinds,pattern) for _ in range(n)] for pattern in grouped]
    for count in range(lower,len(best)):
        rem=[cap]*count;plan=[[] for _ in range(count)];nodes=0
        def recurse(i):
            nonlocal nodes
            nodes+=1
            if nodes>500000:return False
            if i==len(weights):return True
            seen=set();w=weights[i]
            for j in sorted(range(count),key=lambda j:rem[j]):
                if rem[j]<w or rem[j] in seen:continue
                before=rem[j];seen.add(before);rem[j]-=w;plan[j].append(i)
                if recurse(i+1):return True
                rem[j]=before;plan[j].pop()
                if before==cap:break
            return False
        if recurse(0):best=plan;break
    bars=[]
    for i,indices in enumerate(best,1):
        cuts=[pieces[j] for j in indices]
        net=sum(p['length_mm'] for p in cuts)
        offcut=BAR-TRIM-net-KERF*len(cuts)
        assert offcut>=-1e-6
        bars.append({'bar':i,'cuts':cuts,'net_mm':round(net,3),'offcut_mm':round(offcut,3)})
    assert sorted(j for a in best for j in a)==list(range(len(pieces)))
    report={'stock':'2x2x0.120in weldable square steel tube','bar_length_mm':BAR,'trim_per_bar_mm':TRIM,
            'kerf_per_cut_mm':KERF,'stock_qty':len(best),'part_count':len(pieces),'net_length_mm':round(sum(p['length_mm'] for p in pieces),3),
            'verification':'Every matching modeled tube counted exactly once; no stock overrun. Actual stock must retain a full 20 feet of usable length.',
            'scope':'Square-tube blank cutting only. Holes, weld preparation, end facing and non-2x2 stock follow individual part drawings.',
            'bars':bars}
    (ROOT/'tube-cut-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# 2 x 2 x 0.120 inch tube cutting plan','',f"Buy {len(best)} full 20-foot bars for {len(pieces)} modeled blanks.",
           'Allow 10 mm trim per bar and 3 mm per cut. Do not first halve the bars: that changes the nesting.','',
           '| Bar | Finished blank lengths (mm) | Remaining after trim and kerfs (mm) |','|---|---|---:|']
    for b in bars:lines.append(f"| {b['bar']} | "+', '.join(f"{p['length_mm']:g}" for p in b['cuts'])+f" | {b['offcut_mm']:g} |")
    lines.extend(['','The JSON schedule preserves each part number and copy. This plan only covers tubes represented in the current assembly cut list.'])
    (ROOT/'TUBE-CUT-PLAN.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='bars'},indent=2))

if __name__=='__main__': main()
