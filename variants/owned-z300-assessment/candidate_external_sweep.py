"""Complete candidate external domain, with explicitly bound unchanged proofs.

Every candidate/fixed pair is enumerated. Inherited continuous pair proofs are
reused only for exact current baseline topology retained by the candidate and
an enclosing upstream translation box. Changed shapes are proved afresh.
"""
from pathlib import Path
import hashlib,json,os,sys
import candidate_motion_factory as C
import z300_fit_study as S
import custom_joint_repair as R
import front_stop_repair as F
from material_cover import translation_cover_proof

HERE=Path(__file__).resolve().parent
CENTER=(575.,775.,100.);HALF=(400.,500.,100.)
FACTORS=S.FACTORS
UPSTREAM=S.BASE/'review/travel-check.json'

def sources():
    paths=[Path(__file__),Path(C.__file__),Path(F.__file__),*R.sources(),
        S.BASE/'check_travel.py',UPSTREAM,
        S.BASE/'review/internal-continuous-check.json',S.BASE/'review/check_internal_continuous.py']
    return list(dict.fromkeys(paths))

def run():
    hashes=lambda:{p.relative_to(S.ROOT).as_posix():S.sha(p)for p in sources()}
    start=hashes();up=json.loads(UPSTREAM.read_text())
    assert up['source_consistent_during_check']
    assert all(s['rigid_translation_clear']for s in up['states'].values())
    assert up['poses_X_Yguide_Zlift_mm'][0]==list(CENTER)
    for name,h in up['source_sha256'].items():assert S.sha(S.BASE/name)==h,name
    internal=json.loads((S.BASE/'review/internal-continuous-check.json').read_text())
    assert internal['passed']and internal['source_consistent_during_check']
    for name,h in internal['source_sha256'].items():assert S.sha(S.BASE/name)==h,name
    for name,h in internal['motion_source_closure_sha256'].items():assert S.sha(S.ROOT/name)==h,name
    result=dict(study='FULL_CANDIDATE_EXTERNAL_WORKING_DOMAIN',
        physical_catalogue_Z_travel_mm=300,assessed_X_Y_Z_stroke_mm=[800,1000,200],
        domain_X_Yguide_Zlift_mm=[[175,975],[275,1275],[0,200]],
        source_sha256=start,upstream_proof=dict(file=UPSTREAM.relative_to(S.ROOT).as_posix(),sha256=S.sha(UPSTREAM)),
        source_binding='Frozen upstream source hashes and full motion-source closure are verified now. Exact current retained topology and enclosing translation bounds are required per reused pair. These are qualified inherited proofs, not newly rerun upstream tests.',
        states={},fabrication_release=False,operating_release=False,
        scope='Complete nominal external pair enumeration over full working800X/1000Y/200Z in wood and plasma endpoint configurations, including source-law cam roller Z envelopes. Actual cutter/nozzle/workstock/clamps, flexible wiring/hoses, ATC changeover and bed transfer are separate checks.')
    for hot in(False,True):
        label='PLASMA'if hot else'WOOD'
        base={n:s for n,s,_ in S.M.motion_parts(hot,775,575,100)}
        parts=C.motion_parts(hot,775,575,100)
        fixed=S.frame_parts()+S.bed_parts(hot)+S.accessory_parts(hot)
        fb={n:S.bounds(s)for n,s,_ in fixed}
        retained={n:n in base and s.isSame(base[n])for n,s,_ in parts}
        upstream={(q['motion'],q.get('fixed',q.get('ledger'))):q for q in up['states'][label]['conservative_AABB_pairs_resolved_by_exact_translation_proof']}
        state=dict(parts=len(parts),fixed_parts=len(fixed),enumerated_pairs=0,broadphase_clear_pairs=0,
            exact_static_checks=[],reused_continuous_pair_proofs=[],new_continuous_pair_proofs=[],unresolved=[],
            exact_retained_reference_geometry=sorted(n for n,v in retained.items()if v),
            changed_reference_geometry=sorted(n for n,v in retained.items()if not v))
        for n,s,_ in parts:
            b=S.bounds(s);f=FACTORS[C.part_motion_class(n)]
            lo=[-HALF[k]*f[k]for k in range(3)];hi=[HALF[k]*f[k]for k in range(3)]
            if n in S.FOLLOWERS:lo[2]-=3.17657258
            swept=[b[k]+lo[k]for k in range(3)]+[b[k+3]+hi[k]for k in range(3)]
            for nf,sf,_ in fixed:
                state['enumerated_pairs']+=1
                if not S.overlap(swept,fb[nf]):state['broadphase_clear_pairs']+=1;continue
                if not any(f):
                    v=s.intersect(sf).Volume();q=dict(moving=n,fixed=nf,intersection_mm3=v,passed=v<=.05)
                    state['exact_static_checks'].append(q)
                else:
                    prior=upstream.get((n,nf));contains=False
                    if prior and retained[n]:
                        if 'translation_min_mm'in prior:
                            contains=all(prior['translation_min_mm'][k]<=lo[k]+1e-7 and prior['translation_max_mm'][k]>=hi[k]-1e-7 for k in range(3))and prior['passed']
                        elif prior.get('ledger')==nf:
                            contains=all(abs(lo[k])<=HALF[k]+1e-7 and abs(hi[k])<=HALF[k]+1e-7 for k in range(3))and prior['ledger_outside_envelopes_mm3']<1e-6 and max(prior['expanded_box_intersections_mm3'])<1e-6 and min(prior['expanded_box_distances_mm'])>.01
                    if contains:
                        q=dict(moving=n,fixed=nf,passed=True,
                            retained_exact_current_topology=True,
                            translation_min_mm=lo,translation_max_mm=hi,
                            upstream_record=prior)
                        state['reused_continuous_pair_proofs'].append(q)
                    else:
                        q=dict(moving=n,fixed=nf,**translation_cover_proof(s,sf,lo,hi))
                        state['new_continuous_pair_proofs'].append(q)
                if not q['passed']:state['unresolved'].append(q)
        state['passed']=not state['unresolved']
        result['states'][label]=state
        print(label,'external pass',state['passed'],'reused',len(state['reused_continuous_pair_proofs']),
              'new',len(state['new_continuous_pair_proofs']),'static',len(state['exact_static_checks']),flush=True)
    result['source_consistent_during_check']=start==hashes()
    result['complete']=set(result['states'])=={'WOOD','PLASMA'}
    result['passed']=result['source_consistent_during_check']and result['complete']and all(s['passed']for s in result['states'].values())
    (HERE/'output/candidate-external-sweep-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return 0 if result['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
