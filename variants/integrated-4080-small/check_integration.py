"""Check current subsystem boundaries; no supplier or operating release.

Independent translation boxes over-approximate the commanded motion domain.
Every unresolved material-cover cell is reported as a hold, never a pass.
Retained subsystem internal joints are checked in their source manifests.
"""
from pathlib import Path
import hashlib,json,os,sys,time
import assembly as E

HERE=Path(__file__).resolve().parent;OUT=HERE/'output';S=E.S
FACTOR={'stationary':(0,0,0),'Y_gantry_or_drive':(0,1,0),'Y_X_head':(1,1,0),'Y_X_Z_tool':(1,1,1)}
CENTER=(775.,575.,125.)
HALF=(400.,500.,125.) # translation vector order is X,Y,Z

def broad(s,lo,hi,sf):
    b=S.bounds(s)
    return S.overlap([b[k]+lo[k]for k in range(3)]+[b[k+3]+hi[k]for k in range(3)],S.bounds(sf))

def compare(movers,obstacles,relative=False):
    rows=[];clear=0
    fixed=[(n,s,E.motion_class(n)if relative else'stationary',S.bounds(s))for n,s,c in obstacles]
    for n,s,c in movers:
        cf=FACTOR[E.motion_class(n)];body_bounds=S.bounds(s)
        for nf,sf,cl,fixed_bounds in fixed:
            ff=FACTOR[cl]
            span=[abs(cf[k]-ff[k])*HALF[k]for k in range(3)]
            lo=[-v for v in span];hi=span
            swept=[body_bounds[k]+lo[k]for k in range(3)]+[body_bounds[k+3]+hi[k]for k in range(3)]
            if not S.overlap(swept,fixed_bounds):clear+=1;continue
            if not any(span):
                volume=abs(s.intersect(sf).Volume())
                q=dict(passed=volume<.05,method='Exact static material intersection; mating tangency allowed.',overlap_mm3=volume)
            else:
                q=S.translation_cover_proof(s,sf,lo,hi,max_depth=18)
            rows.append(dict(moving=n,obstacle=nf,**q))
            if not q['passed']:print('HOLD',n,nf,flush=True)
        if n.startswith(('OWNER_','PLASMA_','CD_','I_HEAD_')):print('CHECKED',n,flush=True)
    return dict(passed=all(r['passed']for r in rows),broad_phase_separated=clear,candidate_pairs=len(rows),proofs=rows)

def is_tool(n):
    return n.startswith(('OWNER_','CD_','PLASMA_','I_HEAD_','XR_DROP_','XR_PLASMA_DROP_','OWNED_SPINDLE_'))

def run():
    OUT.mkdir(exist_ok=True)
    import integrated_utilities as U
    sources=list(dict.fromkeys([Path(__file__),Path(E.__file__),Path(E.M.__file__),
        Path(E.Q.__file__),Path(E.P.__file__),Path(E.A.__file__),Path(E.B.__file__),
        Path(E.Q.D.__file__),Path(E.T.__file__),Path(U.__file__),Path(U.O.__file__),Path(U.SH.__file__),
        Path(E.M.X.__file__),*E.H.sources()]))
    hashes=lambda:{str(p.relative_to(E.ROOT)).replace('\\','/'):E.sha(p)for p in sources}
    start=hashes();cases={}
    frame=E.M.frame_parts();wet=E.wet_parts()
    # WATER_* source IDs describe real tote/lid/plumbing solids, not fluid
    # contents. Keep them. Only an explicitly named fluid allocation could
    # be removed; no such volume is present in the current utility factory.
    for plasma in(False,True):
        name='PLASMA'if plasma else'WOOD'
        motion=E.integrated_motion(plasma,*CENTER)
        tool=[p for p in motion if is_tool(p[0])]
        remainder=[p for p in motion if not is_tool(p[0])]
        fixture=frame+wet+E.bed_parts(90 if plasma else 0)+E.A.actual_atc_parts(200,hood='fitted'if plasma else'stored',include_allocations=True)
        datums=[p for p in motion if p[0].startswith('INT_STOP_DATUM_')]
        other_motion=[p for p in motion if not p[0].startswith('INT_STOP_DATUM_')]
        cases[name]=dict(tool_against_rest_of_motion=compare(tool,remainder,True),
            stop_datums_against_motion=compare(datums,other_motion,True),
            motion_against_fixed_subsystems=compare(motion,fixture))
        print('MODE',name,'DONE',flush=True)
    data=dict(study='CURRENT_INTEGRATED_SUBSYSTEM_BOUNDARIES',source_sha256=start,
        motion_box=dict(X=[175,975],guide_Y=[275,1275],working_Z=[0,250]),
        cases=cases,source_consistent_during_check=start==hashes(),
        exclusions=['Internal joints within each subsystem remain governed by its own current manifest.',
                    'ATC deployment and manual cover/bed changeover are separate interlocked paths.',
                    'Unregistered working boot, spindle nose and actual vendor magazine geometry are not certified by nominal envelopes.',
                    'No stiffness, safe-stop, thread, lifting, EMC or delivered-price qualification.'],
        fabrication_release=False,operating_release=False)
    data['passed']=data['source_consistent_during_check']and all(q['passed']for case in cases.values()for q in case.values())
    data['unresolved_pair_count']=sum(sum(not p['passed']for p in q['proofs'])for case in cases.values()for q in case.values())
    (OUT/'integration-clearance-check.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=data['passed'],unresolved=data['unresolved_pair_count'])),flush=True)
    return 0 if data['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
