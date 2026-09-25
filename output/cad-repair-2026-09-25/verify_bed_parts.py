"""Read-only consistency audit of Rev G bed part numbers and local solids."""
from pathlib import Path
import hashlib,json,sys,os,itertools,time
from collections import defaultdict
SOURCE=Path(__file__).resolve().parents[1]/'release-review'/'RevE-ENGINEERING'
sys.path.insert(0,str(SOURCE))
from build_revg import build_model,stored_model
from cad_helpers import bbox,place,intersection_volume

AXES=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
BASES=[(u,v) for u in AXES for v in AXES if sum(a*b for a,b in zip(u,v))==0]

def rigid_equal(target,source):
    tv,sv=target.Volume(),source.Volume();tol=max(.02,tv*1e-8)
    if abs(tv-sv)>tol:return {'equal':False,'reason':'volume','delta_mm3':abs(tv-sv)}
    if target.wrapped.IsSame(source.wrapped):return {'equal':True,'identity':True}
    tb=bbox(target);tc=target.Center().toTuple()
    for u,v in BASES:
        rot=place(source,(0,0,0),u=u,v=v);rc=rot.Center().toTuple()
        rot=rot.translate(tuple(a-b for a,b in zip(tc,rc)))
        if max(abs(a-b) for a,b in zip(tb,bbox(rot)))>1e-4:continue
        symmetric=max(0,tv+sv-2*intersection_volume(target,rot))
        if symmetric<=tol:return {'equal':True,'u':u,'v':v,'symmetric_difference_mm3':symmetric}
    return {'equal':False,'reason':'no proper orthogonal rigid match','target_bounds':tb,'source_bounds':bbox(source)}

def main():
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    m,_=build_model();stored=stored_model(m)
    touched=lambda p:p.id.startswith('G_') or p.id.startswith('WP_SLAT_') or p.id.startswith('MF_RECEIVER_LEDGER_')
    parts=[p for p in m.parts if touched(p)]
    groups=defaultdict(list)
    for p in m.parts:groups[p.part_number].append(p)
    selected={p.part_number for p in parts}
    conflicts=[];flat_conflicts=[];checks=0
    for pn in sorted(selected):
        group=groups[pn];first=group[0]
        for other in group[1:]:
            checks+=1
            r=rigid_equal(first.local,other.local)
            if not r['equal']:conflicts.append({'part_number':pn,'first':first.id,'other':other.id,'check':r})
            if first.flat!=other.flat:
                flat_conflicts.append({'part_number':pn,'first':first.id,'other':other.id,'first_flat':first.flat,'other_flat':other.flat})
    print('PART NUMBERS',len(selected),'local comparisons',checks,'geometry conflicts',len(conflicts),'flat conflicts',len(flat_conflicts),flush=True)
    world_failures=[]
    for state,model in [('installed',m),('stored',stored)]:
        for p in model.parts:
            if not touched(p):continue
            r=rigid_equal(p.shape,p.local)
            if not r['equal']:world_failures.append({'state':state,'id':p.id,'part_number':p.part_number,'check':r})
        print('WORLD LOCAL',state,'failures',len(world_failures),flush=True)
    ledgers=[{'id':p.id,'part_number':p.part_number,'local_volume_mm3':p.local.Volume(),'local_bounds':bbox(p.local),'flat':p.flat,'notes':p.notes} for p in parts if p.id.startswith('MF_RECEIVER_LEDGER_')]
    after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    result={'source_sha256':before,'sources_unchanged':before==after,'scope':'All G_ bed parts, all revised WP_SLAT_ parts and the two modified receiver ledgers; all shared-PN instances included even when their IDs are outside that prefix.',
            'method':'Compare actual B-rep symmetric volume after all24 proper orthogonal rotations and translation. Reject reflections. Flat metadata compared exactly within each shared PN. Compare each selected local solid to its installed and stored world solid.',
            'selected_components':len(parts),'selected_part_numbers':len(selected),'shared_pn_comparisons':checks,
            'part_number_geometry_conflicts':conflicts,'part_number_flat_conflicts':flat_conflicts,'local_world_geometry_failures':world_failures,'receiver_ledgers':ledgers}
    result['pass']=before==after and not(conflicts or flat_conflicts or world_failures)
    Path(__file__).with_name('bed-part-consistency.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['pass'],flush=True)
    return 0 if result['pass'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
