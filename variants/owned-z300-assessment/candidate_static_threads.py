"""Exact same-class custom-involved intersections and specific thread records.

This enumerates every co-moving pair involving a custom motion part. Only
explicit source-declared mating thread IDs receive nominal-thread dispositions.
The three seat spigots additionally have exact annulus correspondence tests.
"""
from pathlib import Path
import csv,json,math,os,sys
import candidate_motion_factory as C
import z300_fit_study as S
import custom_joint_repair as R
import front_stop_repair as F
from motion_finish import make_head

HERE=Path(__file__).resolve().parent

def run():
    paths=[Path(__file__),Path(C.__file__),Path(F.__file__),*R.sources()]
    hashes=lambda:{p.relative_to(S.ROOT).as_posix():S.sha(p)for p in dict.fromkeys(paths)}
    start=hashes()
    custom={r['id']for r in csv.DictReader((S.BASE/'motion-fabrication.csv').open(encoding='utf-8-sig'))if r['category'].startswith('CUSTOM')}
    model,_=make_head();permitted=model.allowed_intersections
    result=dict(study='CANDIDATE_SAME_CLASS_CUSTOM_INTERSECTION_ENUMERATION',source_sha256=start,states={},
        scope='All pairs within each declared motion class involving at least one custom part, at the reference pose. Rigid common-class translations preserve these intersections; independent source-law roller motion is covered by the separate internal continuous checker. This does not declare all purchased internal envelopes physically clear.',
        nominal_thread_rule='Exact pair lookup from make_head().allowed_intersections, restricted to a reason describing a thread/spigot/tapped mating, plus exactly four XR_DROP_M6x16_LOWER_i to I_HEAD_BACKPLATE mounting threads from _add_plasma. Every remaining positive pair is unresolved. Recorded intended thread-envelope material overlap is not proof of actual tap form, engagement or screw-tip clearance.',
        fabrication_release=False,physical_thread_fit_qualified=False)
    for hot in(False,True):
        label='PLASMA'if hot else'WOOD'
        original={n:s for n,s,_ in S.M.motion_parts(hot,775,575,100)}
        parts=C.motion_parts(hot,775,575,100);lookup={n:s for n,s,_ in parts}
        boxes={n:S.bounds(s)for n,s,_ in parts}
        state=dict(exact_pairs=0,nominal_thread_dispositions=[],unresolved=[],seat_spigot_annulus_checks=[])
        for i,(n,s,_)in enumerate(parts):
            for nf,sf,_ in parts[i+1:]:
                if C.part_motion_class(n)!=C.part_motion_class(nf)or not(n in custom or nf in custom)or not S.overlap(boxes[n],boxes[nf]):continue
                state['exact_pairs']+=1;intersection=s.intersect(sf);volume=intersection.Volume()
                if volume<=.05:continue
                reason=permitted.get(frozenset((n,nf)));kind='SOURCE_EXACT_HEAD_THREAD_PAIR'
                if reason and not any(w in reason.lower()for w in('thread','spigot','tapped')):reason=None
                lower_pairs={frozenset(('I_HEAD_BACKPLATE',f'XR_DROP_M6x16_LOWER_{j}'))for j in range(1,5)}
                if frozenset((n,nf))in lower_pairs:
                    reason='Exactly numbered lower custom M6 mounting screw into the existing D5 pilot of I_HEAD_BACKPLATE, per _add_plasma and MOUNT_PATTERN.';kind='EXACT_CUSTOM_BACKPLATE_M6_MOUNT_THREAD'
                row=dict(a=n,b=nf,volume_mm3=volume,intersection_bounds_mm=S.bounds(intersection),
                    inherited_baseline_volume_mm3=original[n].intersect(original[nf]).Volume(),
                    actual_thread_fit_qualified=False)
                if reason:
                    row.update(disposition=kind,source_reason=reason)
                    state['nominal_thread_dispositions'].append(row)
                else:state['unresolved'].append(row)
        if hot:
            adapter=lookup['TOOL_ADAPTER_110'];ox,oy,oz,*_=S.bounds(adapter)
            lower=(ox,oy-12.7,oz-S.M.PLASMA_DROP)
            for kind,x,y in(('CONE',10,40),('V',100,40),('FLAT',55,90)):
                local=F.cyl(4,6,(x,y,28)).cut(F.cyl(3.3,8,(x,y,27)))
                reference=S.M.place(local,lower,u=(1,0,0),v=(0,0,1))
                actual=lookup['I_HEAD_FLOAT_CARRIAGE'].intersect(lookup['I_HEAD_SEAT_'+kind])
                difference=actual.cut(reference).Volume()+reference.cut(actual).Volume()
                q=dict(seat='I_HEAD_SEAT_'+kind,carriage='I_HEAD_FLOAT_CARRIAGE',
                    spigot_major_diameter_mm=4,modeled_pilot_diameter_mm=3.3,engaged_length_mm=6,
                    analytic_nominal_thread_annulus_mm3=math.pi*(2**2-1.65**2)*6,
                    actual_intersection_mm3=actual.Volume(),exact_annulus_symmetric_difference_mm3=difference,
                    passed=difference<1e-7,
                    interpretation='The entire positive intersection is exactly the intended integral M4 spigot/pilot annulus. Cone/V/flat contact geometry contributes no positive intersection with the carriage. This does not qualify contact polish, preload or actual thread fit.')
                state['seat_spigot_annulus_checks'].append(q)
        state['same_class_custom_clear_except_specific_nominal_threads']=not state['unresolved']and all(q['passed']for q in state['seat_spigot_annulus_checks'])
        result['states'][label]=state
        print(label,'static custom exactpairs',state['exact_pairs'],'specific thread records',len(state['nominal_thread_dispositions']),'unresolved',len(state['unresolved']),flush=True)
    result['source_consistent_during_check']=start==hashes()
    result['passed']=result['source_consistent_during_check']and all(s['same_class_custom_clear_except_specific_nominal_threads']for s in result['states'].values())
    (HERE/'output/candidate-static-thread-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return 0 if result['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
