"""Joint stock-neutral nesting of NEW 1.9 mm steel blanks; no prices.

Combines bed, hatch, shields, braces and ATC before assigning sheet stock.
Other thicknesses/RHS/bars remain separate material, never free offcuts.
"""
from pathlib import Path
import csv,hashlib,json,math,re
import params as P

HERE=Path(__file__).resolve().parent;OUT=HERE/'review'
TRIM,KERF=5.,3.

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def collect():
    rows=[]
    def add(source,n,qty,w,h,t):
        if abs(float(t)-1.9)>1e-5:return
        for i in range(int(qty)):
            rows.append(dict(id=f'{source}:{n}:{i+1}',source=source,w=float(w),h=float(h)))
    b=json.loads((OUT/'bed-manufacturing-check.json').read_text())
    for r in b['steel_blanks']:add('BED',r['id'],r['quantity'],r['flat_length_mm'],r['flat_width_mm'],r['thickness_mm'])
    s=json.loads((OUT/'shield-manufacturing.json').read_text())
    for n,q,w,h,t,*_ in s['parts']:add('SHIELD',n,q,w,h,t)
    a=json.loads((OUT/'atc-manufacturing.json').read_text())
    assert 'steel_blanks' in a,'ATC flat blank takeoff is required; never price it as omitted.'
    for r in a['steel_blanks']:add('ATC',r['id'],r['quantity'],r['flat_length_mm'],r['flat_width_mm'],r['thickness_mm'])
    with (OUT/'frame-fabrication.csv').open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            if r['category']!='Tension strap':continue
            dims=[float(x) for x in re.findall(r'\d+(?:\.\d+)?',r['finished_blank_or_allowance_mm'])]
            add('FRAME',r['id'],r['quantity'],*dims[:3])
    assert len({r['id'] for r in rows})==len(rows)
    return rows

def intersect(a,b):
    return min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0])>1e-7 and min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1])>1e-7

def split_free(free,used):
    fresh=[];px,py,pw,ph=used
    for r in free:
        if not intersect(r,used):fresh.append(r);continue
        x,y,w,h=r
        if px>x:fresh.append((x,y,px-x,h))
        if px+pw<x+w:fresh.append((px+pw,y,x+w-px-pw,h))
        if py>y:fresh.append((x,y,w,py-y))
        if py+ph<y+h:fresh.append((x,py+ph,w,y+h-py-ph))
    unique=list(dict.fromkeys(r for r in fresh if r[2]>.01 and r[3]>.01))
    return [r for i,r in enumerate(unique) if not any(i!=j and s[0]<=r[0]+1e-7 and s[1]<=r[1]+1e-7 and s[0]+s[2]>=r[0]+r[2]-1e-7 and s[1]+s[3]>=r[1]+r[3]-1e-7 for j,s in enumerate(unique))]

def nest(rows,L,W,order):
    sorters={'area':lambda r:(-r['w']*r['h'],-max(r['w'],r['h'])),
             'length':lambda r:(-max(r['w'],r['h']),-r['w']*r['h']),
             'width':lambda r:(-min(r['w'],r['h']),-r['w']*r['h'])}
    sheets=[]
    for r in sorted(rows,key=sorters[order]):
        candidates=[]
        for si,s in enumerate(sheets):
            for x,y,w,h in s['free']:
                for rw,rh,rot in ((r['w'],r['h'],False),(r['h'],r['w'],True)):
                    pw,ph=rw+KERF,rh+KERF
                    if pw<=w+1e-6 and ph<=h+1e-6:
                        candidates.append(((min(w-pw,h-ph),max(w-pw,h-ph),si,y,x),si,x,y,pw,ph,rot))
        if not candidates:
            sheets.append({'free':[(TRIM,TRIM,L-2*TRIM,W-2*TRIM)],'placements':[]})
            si=len(sheets)-1
            opts=[(rw+KERF,rh+KERF,rot) for rw,rh,rot in ((r['w'],r['h'],False),(r['h'],r['w'],True)) if rw+KERF<=L-2*TRIM and rh+KERF<=W-2*TRIM]
            if not opts:raise ValueError(('Blank does not fit stock',r,L,W))
            pw,ph,rot=min(opts,key=lambda p:(min(L-2*TRIM-p[0],W-2*TRIM-p[1]),max(L-2*TRIM-p[0],W-2*TRIM-p[1])))
            chosen=(None,si,TRIM,TRIM,pw,ph,rot)
        else:chosen=min(candidates,key=lambda c:c[0])
        _,si,x,y,pw,ph,rot=chosen
        sheets[si]['placements'].append(dict(**r,x=x,y=y,cut_w=pw-KERF,cut_h=ph-KERF,rotated=rot))
        sheets[si]['free']=split_free(sheets[si]['free'],(x,y,pw,ph))
    for s in sheets:
        for i,a in enumerate(s['placements']):
            assert a['x']>=TRIM and a['y']>=TRIM and a['x']+a['cut_w']+KERF<=L-TRIM+1e-6 and a['y']+a['cut_h']+KERF<=W-TRIM+1e-6
            for b in s['placements'][i+1:]:
                assert not intersect((a['x'],a['y'],a['cut_w']+KERF,a['cut_h']+KERF),(b['x'],b['y'],b['cut_w']+KERF,b['cut_h']+KERF))
    return sheets

def run():
    files=['steel_nesting.py','params.py','review/bed-manufacturing-check.json','review/shield-manufacturing.json',
           'review/atc-manufacturing.json','review/frame-fabrication.csv']
    source={n:sha(HERE/n) for n in files};rows=collect();area=sum(r['w']*r['h'] for r in rows)
    options={}
    for label,L,W in [('4x8',2438.4,1219.2),('4x10',3048.,1219.2),('5x10',3048.,1524.)]:
        trials=[(nest(rows,L,W,order),order) for order in ('area','length','width')]
        sheets,order=min(trials,key=lambda t:(len(t[0]),len(t[0][-1]['placements'])))
        options[label]={'nominal_sheet_mm':[L,W],'sheet_count':len(sheets),'gross_stock_area_m2':len(sheets)*L*W/1e6,
            'area_lower_bound_sheets':math.ceil(area/((L-2*TRIM)*(W-2*TRIM))),
            'strategy':order,'sheets':sheets}
        with (OUT/f'steel-cuts-{label}.csv').open('w',newline='',encoding='utf-8') as f:
            fields=['sheet','id','source','x','y','cut_w','cut_h','rotated']
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for i,s in enumerate(sheets,1):
                for p in s['placements']:w.writerow(dict(sheet=i,**{k:p[k] for k in fields[1:]}))
    result={'revision':P.REVISION,'passed':source=={n:sha(HERE/n) for n in files},'blank_count':len(rows),
        'gross_blank_area_m2':area/1e6,'thickness_mm':1.9,'trim_each_edge_mm':TRIM,'separation_kerf_mm':KERF,
        'options':options,'source_sha256':source,'pricing_performed':False,'fabrication_release':False,
        'scope':'Conservative rectangular-blank nesting with90degree rotation,3mm separation and5mm edge trim. These are feasible illustrative stock options, not a vendor quote or a proof of global optimum. Confirm real sheet size, kerf, bend development and material grade. Other gauges, RHS, bars and purchased modified washers remain separate new material. No unlisted offcut is assumed free.'}
    (OUT/'steel-nesting.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'blank_count':len(rows),'gross_blank_area_m2':area/1e6,'stock_options':{k:v['sheet_count'] for k,v in options.items()},'passed':result['passed']},indent=2))
    return result

if __name__=='__main__':
    import sys
    sys.exit(0 if run()['passed'] else 1)
