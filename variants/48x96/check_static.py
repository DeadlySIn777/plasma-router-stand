"""Independent exact intersections of fabricated layout solids; not a motion proof."""
from pathlib import Path
import hashlib,json,os,sys,time
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from layout import Parameters,build,bounds
OUT=Path(__file__).resolve().parent

def volume(a,b):
    op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.Build()
    if not op.IsDone():raise RuntimeError('Boolean common failed')
    result=op.Shape();return 0. if result.IsNull() else cq.Shape.cast(result).Volume()

def main():
    begin=time.monotonic();files=(OUT/'layout.py',Path(__file__))
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files};states={}
    for state in ('router','plasma_layout'):
        allparts,_=build(Parameters(),state)
        parts=[p for p in allparts if p.material!='allocation only'];bbs=[bounds(p.shape) for p in parts]
        hits=[];candidates=0
        for i,a in enumerate(parts):
            aa=bbs[i]
            for j in range(i+1,len(parts)):
                bb=bbs[j]
                if not all(min(aa[k+3],bb[k+3])-max(aa[k],bb[k])>1e-5 for k in range(3)):continue
                candidates+=1;b=parts[j];v=volume(a.shape,b.shape)
                if v>.02:hits.append({'a':a.name,'b':b.name,'volume_mm3':v})
        states[state]={'fabricated_parts':len(parts),'excluded_allocation_parts':len(allparts)-len(parts),'broadphase_candidates':candidates,'unexpected_intersections':hits,'passed':not hits}
        print(state,len(parts),'fabricated solids;',len(hits),'unexpected intersections',flush=True)
        if hits:print(json.dumps(hits,indent=2),flush=True)
    after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    result={'passed':all(s['passed'] for s in states.values()) and before==after,'source_sha256':after,'sources_unchanged':before==after,
            'states':states,'elapsed_seconds':time.monotonic()-begin,
            'scope':'Exact positive-volume tests afterAABB broadphase. Zero-volume bearing/weld contacts need no blanket allowance. Unselected axis/ATC allocations are excluded and remain unresolved interfaces. No path/strength/handling claim.'}
    (OUT/'static-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return 0 if result['passed'] else 2
if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
