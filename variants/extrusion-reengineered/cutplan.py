"""Stock-neutral profile nesting; no vendor, stock availability or price assumed."""
from pathlib import Path
import csv,json,os,sys,hashlib
from frame import frame_parts

HERE=Path(__file__).resolve().parent
KERF,END_TRIM=3.,4.

def pieces():
    out=[]
    for n,s,_ in frame_parts():
        if not n.startswith('XR_EX_'):continue
        b=s.BoundingBox()
        axis='X' if ('DRY_ARM' in n or 'PAN_X' in n) else 'Y' if ('HEADER' in n or 'FOOTBASE' in n) else 'Z'
        out.append({'id':n,'length_mm':getattr(b,axis.lower()+'len'),'axis':axis})
    assert len(out)==19
    assert abs(sum(p['length_mm'] for p in out)-12357.4)<1e-4
    return sorted(out,key=lambda p:(-p['length_mm'],p['id']))

def nest(items,short=True):
    bins=[]
    for p in items:
        needed=p['length_mm']+KERF
        choices=[b for b in bins if b['remaining_mm']+1e-6>=needed]
        if choices:b=min(choices,key=lambda b:b['remaining_mm'])
        else:
            length=(1500. if p['length_mm']>996 else 1000.) if short else (3000. if p['length_mm']>996 else 1000.)
            b={'bar':len(bins)+1,'stock_mm':length,'remaining_mm':length-END_TRIM,'pieces':[]};bins.append(b)
        b['pieces'].append(p);b['remaining_mm']-=needed
        assert b['remaining_mm']>=-1e-5
    return bins

def run():
    items=pieces();data={}
    for label in ('short_stock','long_stock'):
        bins=nest(items,label=='short_stock')
        data[label]={'bars':bins,'total_stock_mm':sum(b['stock_mm'] for b in bins),
                     'note':'Illustrative raw-length nesting only; length availability, pack rounding, end damage and actual saw kerf require confirmation.'}
        with (HERE/'review'/f'profile-cuts-{label}.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(['bar','stock_mm','part_id','finish_mm','kerf_mm','trim_per_bar_mm','remaining_after_all_cuts_mm'])
            for b in bins:
                for p in b['pieces']:w.writerow([b['bar'],b['stock_mm'],p['id'],round(p['length_mm'],4),KERF,END_TRIM,round(b['remaining_mm'],4)])
    report={'cut_count':len(items),'finished_mm':sum(p['length_mm'] for p in items),'kerf_mm':KERF,
            'end_trim_per_bar_mm':END_TRIM,'options':data,'passed':True,'release':False,
            'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/n for n in ('params.py','frame.py','cutplan.py')]}}
    (HERE/'review'/'profile-nesting.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print({k:v['total_stock_mm'] for k,v in data.items()},flush=True)

if __name__=='__main__':
    try:run();code=0
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
