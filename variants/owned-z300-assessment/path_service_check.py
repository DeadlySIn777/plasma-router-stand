"""Source-bound candidate motion replacement in frozen XR2 changeover paths.

Regenerate every continuous path enclosure from the frozen path definitions and
test it against the COMPLETE repaired, stock-motor Z300 retained-motion group.
Unchanged non-motion obstacles and unchanged bed/hinge/water self checks are
inherited only from passing reports whose recorded source hashes still match.
No global factory, filesystem method, source file or baseline report is patched.
"""
from pathlib import Path
from math import atan2, cos, sin, pi, radians
import hashlib, json, os, sys, time
import z300_fit_study as Z
import custom_joint_repair as R
import front_stop_repair as F
import candidate_motion_factory as Factory
import bed as B
import bed_service as BS
import check_transfer as T
import service_check as C
import shields as H

HERE=Path(__file__).resolve().parent
ROOT=Z.ROOT
BASE=Z.BASE
OUT=HERE/'output'/'candidate-path-service-check.json'
REMOVED_TOOL_PREFIXES=('TOOL_SPINDLE_','TOOL_SPLIT_CLAMP_','TOOL_CLAMP_')
PARK=(575.,1275.,200.)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return path.relative_to(ROOT).as_posix()
def source_matches(data,base):
    hashes={**data.get('source_sha256',{}),**data.get('study_source_sha256',{})}
    return {key:dict(expected=value,actual=sha(base/key) if (base/key).is_file() else None)
            for key,value in hashes.items()
            if not (base/key).is_file() or sha(base/key)!=value}

def candidate_bare_motion():
    """Same stated service park and removal list as both frozen checkers."""
    original=Z.M.motion_parts(False,PARK[1],PARK[0],PARK[2])
    owned=Z.overlay(original,stroke=300,brake=False,extended_carrier=False)
    repaired=R.apply_repairs(owned)
    assert [n for n,_,_ in owned]==[n for n,_,_ in repaired]
    changed=[n for (n,s,c),(nr,sr,cr) in zip(owned,repaired) if s is not sr]
    assert set(changed)=={'Z_CARRIER','X_LINK_SUPPORT'}
    assert all(c==cr for (_,_,c),(_,_,cr) in zip(owned,repaired))
    stopped=F.apply_repairs(repaired)
    assert [n for n,_,_ in stopped]==[n for n,_,_ in repaired]
    assert {n for (n,s,c),(nr,sr,cr) in zip(repaired,stopped)if s is not sr}==F.CHANGED
    # Cross-check the local scene adapter against the shared operating factory,
    # without replacing or monkeypatching either function.
    common=Factory.motion_parts(False,PARK[1],PARK[0],PARK[2])
    assert [n for n,_,_ in common]==[n for n,_,_ in stopped]
    for (n,a,_),(nb,b,_)in zip(common,stopped):
        if n in F.CHANGED or n in ('Z_CARRIER','X_LINK_SUPPORT','ZBX80_BASE',
                'ZBX80_END_TOP','ZBX80_COUPLER_GUARD',Z.STOCK_MOTOR):
            assert a.cut(b).Volume()+b.cut(a).Volume()<.05,n
    return [q for q in stopped if not q[0].startswith(REMOVED_TOOL_PREFIXES)]

class MotionChecker:
    def __init__(self,parts):
        self.parts=[(n,s,Z.bounds(s))for n,s,_ in parts]
        self.rows=[]
    def add(self,group,label,shape=None,bounds=None,within_plan=True):
        b=Z.bounds(shape) if bounds is None else list(bounds)
        possible=[];gaps=[]
        for n,s,bb in self.parts:
            # A nonnegative separating-axis gap proves no positive volume.
            gap=max(max(bb[k]-b[k+3],b[k]-bb[k+3])for k in range(3))
            if gap>=-1e-5:gaps.append(gap)
            else:possible.append((n,s,bb))
        hits=[]
        if possible:
            if shape is None:shape=C.bboxshape(b)
            for n,s,_ in possible:
                volume=shape.intersect(s).Volume()
                if volume>.05:hits.append(dict(moving=label,retained_motion=n,volume_mm3=volume))
        inside=(b[0]>=-1e-5 and b[3]<=1150.+1e-5 and b[1]>=-1e-5 and b[4]<=1450.+1e-5)
        self.rows.append(dict(group=group,label=label,continuous_enclosure_bounds_mm=b,
            motion_parts_tested=len(self.parts),separating_axis_clear_pairs=len(gaps),
            minimum_best_separating_axis_gap_mm=min(gaps)if gaps else None,
            exact_pairs=len(possible),positive_intersections=hits,within_plan=inside,
            plan_limit_required=within_plan,passed=not hits and (inside or not within_plan)))
    def summaries(self):
        groups={}
        for q in self.rows:
            v=groups.setdefault(q['group'],dict(continuous_subenclosures=0,exact_pairs=0,
                separating_axis_clear_pairs=0,positive_intersections=[],passed=True))
            for key in ('continuous_subenclosures','exact_pairs','separating_axis_clear_pairs'):
                v[key]+=1 if key=='continuous_subenclosures'else q[key]
            v['positive_intersections']+=q['positive_intersections'];v['passed'] &= q['passed']
        return groups

def regenerate_paths(check):
    # Reverse restoration traverses exactly the same enclosures, 4->1.
    for i in range(4):
        poses=B.transfer_poses(i)
        for a,b in zip(poses,poses[1:]):
            check.add('normal_cassette_transfer',f'CASSETTE_{i+1}_{a["stage"]}_{b["stage"]}',T.swept_enclosure(a,b))
    stages=('closed','front','lowered','leaned','parked')
    for a,b in zip(stages,stages[1:]):
        check.add('normal_cover_transfer',a+'_'+b,bounds=C.mergebox(Z.bounds(B.cabinet_cover(a)),Z.bounds(B.cabinet_cover(b))))
    for i in range(5):
        shape=B.cabinet_cover('parked').translate((0,5*i*__import__('math').tan(radians(8)),5*i))
        check.add('normal_cover_slot_checkpoints',f'SLOT_LIFT_{5*i}',shape)
    cover=next(s for n,s,_ in B.receiver_hatch_parts(False)if n.startswith('RECEIVER_HATCH_COVER_'))
    check.add('routine_hatch', 'HATCH_COMPLETE_CONTINUOUS_SWEEP',bounds=C.rotation_enclosure(cover,B.HATCH_AXIS_Y,B.HATCH_AXIS_Z))
    # Endpoint of convex full-floor brush reach proof; line inside inset entry.
    for x in (253.,897.):
        for y in (734.,1136.):
            a=Z.cq.Vector(x,y,34.);e=Z.cq.Vector(min(max(x,320.),830.),min(max(y,890.),1080.),394.)
            v=e-a
            check.add('routine_brush',f'ROD_{x}_{y}',Z.cq.Solid.makeCylinder(5.,450.,a,v.normalized()))
            check.add('routine_brush',f'HEAD_{x}_{y}',B.box(x-30,y-30,4,60,60,60))
    def extrema(A,D,lo,hi):
        ts=[lo,hi];t=atan2(D,A)
        ts += [t+k*pi for k in range(-3,4)if lo<=t+k*pi<=hi]
        vals=[A*cos(t)+D*sin(t)for t in ts];return min(vals),max(vals)
    for stage in (1,2,3,4,5):
        aa,bb=BS.pan_pose(stage-1),BS.pan_pose(stage)
        if stage==3:
            for n,s,_ in aa:
                b=Z.bounds(s);ys=(b[1]-100,b[4]-100);zs=(b[2]-882,b[5]-882)
                for angle in range(90):
                    lo,hi=radians(angle),radians(angle+1)
                    yr=[extrema(y,-z,lo,hi)for y in ys for z in zs]
                    zr=[extrema(z,y,lo,hi)for y in ys for z in zs]
                    env=[b[0],100+min(v[0]for v in yr),882+min(v[0]for v in zr),
                         b[3],100+max(v[1]for v in yr),882+max(v[1]for v in zr)]
                    check.add('rare_pan_stage_3_rotation',n+f'_{angle}_{angle+1}',bounds=env)
        else:
            for (n,sa,_),(nb,sb,_)in zip(aa,bb):
                assert n==nb
                check.add(f'rare_pan_stage_{stage}',n,bounds=C.mergebox(Z.bounds(sa),Z.bounds(sb)))
    tb=C.union_bounds(BS.tote_assembly());forward=tb.copy();forward[1]-=44.;forward[4]-=44.
    lifted=forward.copy();lifted[2]+=820.;lifted[5]+=820.
    check.add('rare_tote','EMPTY_TOTE_FORWARD44',bounds=C.mergebox(tb,forward))
    check.add('rare_tote','EMPTY_TOTE_VERTICAL_HANDOFF820',bounds=C.mergebox(forward,lifted))
    # Baseline union access excluded the whole motion group; add it explicitly.
    check.add('union_tool_access','UNION_TOOL',bounds=[50,185,790,125,320,875])
    # Original roof proof also omitted motion; check the full candidate group.
    for n,s,_ in H.roof_service_envelopes():check.add('rare_roof_removal',n,s)

def run():
    start_time=time.monotonic()
    upstream={}
    for label,name in (('baseline_transfer','transfer-check.json'),('baseline_service','service-check.json'),
                       ('baseline_water','water-check.json'),('baseline_shields','shield-check.json')):
        path=BASE/'review'/name;data=json.loads(path.read_text(encoding='utf-8'))
        errors=source_matches(data,BASE)
        assert data['passed']and not errors,(label,errors)
        upstream[label]=dict(file=rel(path),sha256=sha(path),passed=True,
            source_hashes_current=True,recorded_source_sha256=data.get('source_sha256',{}))
    extra_output_paths=[]
    for label,name in (('candidate_bulk_fit','z300-fit-decision.json'),('candidate_custom_joint','custom-joint-repair-check.json'),
                       ('candidate_front_stops','front-stop-repair/front-stop-repair-check.json')):
        path=HERE/'output'/name;data=json.loads(path.read_text(encoding='utf-8'))
        errors=source_matches(data,ROOT)
        assert data['passed']and not errors,(label,errors)
        upstream[label]=dict(file=rel(path),sha256=sha(path),passed=True,source_hashes_current=True)
        if label=='candidate_front_stops':
            for item in data['outputs'].values():
                output=HERE/item['file'];assert sha(output)==item['sha256'],str(output)
                extra_output_paths.append(output)
    paths=R.sources()+[Path(__file__),Path(F.__file__),Path(Factory.__file__),BASE/'bed_service.py',BASE/'check_transfer.py',BASE/'service_check.py',
        BASE/'water_check.py',BASE/'reservoir-interface.json']
    paths += [ROOT/v['file']for v in upstream.values()]+extra_output_paths
    paths=list(dict.fromkeys(paths));hashes=lambda:{rel(p):sha(p)for p in paths}
    before=hashes()
    parts=candidate_bare_motion()
    assert all(s.isValid()and s.Volume()>0 for _,s,_ in parts)
    check=MotionChecker(parts);regenerate_paths(check)
    groups=check.summaries();after=hashes()
    baseline_transfer=json.loads((BASE/'review'/'transfer-check.json').read_text())
    baseline_service=json.loads((BASE/'review'/'service-check.json').read_text())
    # Prove path regeneration did not silently revise the transfer definition.
    newsegments=[q for q in check.rows if q['group']=='normal_cassette_transfer']
    baseline_segments=baseline_transfer['segments']
    assert len(newsegments)==len(baseline_segments)
    maxdelta=max(abs(a-b)for q,r in zip(newsegments,baseline_segments)
        for a,b in zip(q['continuous_enclosure_bounds_mm'],r['continuous_enclosure_bounds_mm']))
    baseline_pan_count=sum(q['continuous_subenclosures']for q in baseline_service['rare_pan_tote_replacement']['pan_continuous_checks'])
    candidate_pan_count=sum(v['continuous_subenclosures']for k,v in groups.items()if k.startswith('rare_pan_'))
    assert candidate_pan_count==baseline_pan_count
    correspondence={}
    for old in baseline_service['rare_pan_tote_replacement']['pan_continuous_checks']:
        stage=old['stage'];prefix=f'rare_pan_stage_{stage}'
        rows=[q for q in check.rows if q['group'].startswith(prefix)]
        union=[min(q['continuous_enclosure_bounds_mm'][k]for q in rows)for k in range(3)]+[
            max(q['continuous_enclosure_bounds_mm'][k]for q in rows)for k in range(3,6)]
        correspondence[f'pan_stage_{stage}_aggregate_bounds_max_delta_mm']=max(abs(a-b)for a,b in zip(union,old['bounds_mm']))
    new_tote=[q for q in check.rows if q['group']=='rare_tote']
    for new,old in zip(new_tote,baseline_service['rare_pan_tote_replacement']['empty_tote_checks']):
        correspondence[new['label']+'_bounds_max_delta_mm']=max(abs(a-b)for a,b in zip(new['continuous_enclosure_bounds_mm'],old['bounds_mm']))
    hatch=next(q for q in check.rows if q['group']=='routine_hatch')
    correspondence['hatch_sweep_bounds_max_delta_mm']=max(abs(a-b)for a,b in zip(
        hatch['continuous_enclosure_bounds_mm'],baseline_service['routine_hatch']['continuous_external']['bounds_mm']))
    assert all(delta<1e-7 for delta in correspondence.values()),correspondence
    report=dict(schema='owned-z300-path-service-check/v1',candidate='Z300_STOCK_WORK200_CUSTOM_JOINT_PROPOSAL',
        source_sha256=after,source_consistent_during_check=before==after,
        geometry_factory=dict(base='motion.motion_parts(False,1275,575,200)',
            overlay='z300_fit_study.overlay(stroke=300,brake=False,extended_carrier=False)',
            repairs=['custom_joint_repair.apply_repairs','front_stop_repair.apply_repairs'],
            shared_factory='candidate_motion_factory.motion_parts',shared_factory_symmetric_difference_crosscheck_mm3_limit=.05,
            removed_tool_prefixes=REMOVED_TOOL_PREFIXES,
            monkeypatches=[],full_retained_motion_group_rechecked=True,retained_motion_component_count=len(parts),
            park=dict(head_X_mm=PARK[0],gantry_Y_mm=PARK[1],Z_lift_mm=PARK[2]),
            bounds_mm=C.union_bounds(parts),assessed_working_travel_mm=dict(X=800,Y=1000,Z=200)),
        proof_method='Exact intersections against every regenerated conservative continuous path enclosure. All full candidate retained-motion solids are tested; only unchanged non-motion obstacle/self/volume evidence is inherited with current source hashes. AABB separation is conclusive; any overlap invokes exact OCCT volume. Removed material is not assumed to clear a positive test.',
        upstream_evidence=upstream,source_paths_or_baseline_reports_modified=False,
        inherited_scope=['Cassette pins and initial pad-bore engagement; unchanged docking/storage/frame/bed/accessory obstacles and bed self checks',
            'Cover slot, hatch internal hinge/index/latch proof and convex full-floor brush reach',
            'Pan shims, parked pan dunnage/props, disconnected hose coil and all unchanged replacement obstacles',
            'Atmospheric water route/volume requirements and receiver capacity allowance; physical holds remain'],
        source_route_correspondence=dict(transfer_segment_count=len(newsegments),
            transfer_bounds_maximum_difference_mm=maxdelta,baseline_pan_subenclosures=baseline_pan_count,
            candidate_pan_subenclosures=candidate_pan_count,other_bounds_maximum_differences_mm=correspondence,
            passed=maxdelta<1e-7 and all(delta<1e-7 for delta in correspondence.values())),
        groups=groups,checks=check.rows,positive_volume_threshold_mm3=.05,aabb_tolerance_mm=1e-5,
        normal_conversion=dict(within_machine_plan_mm=[0,0,1150,1450],outside_plan_clearance_required_mm=0,
            remove_cassettes_order=[1,2,3,4],restore_order=[4,3,2,1],
            whole_tool_modules_removed=True,common_Z_retained=True,ATC_parked_and_guide_guards_retained=True,
            reverse_path_same_enclosures=True),
        rare_service=dict(ATC_rail_drive_lock_and_separate_hood_support_removed=True,
            HGR_guides_and_supported_gantry_retained=True,receiver_roof_and_heatshields_removed=True,
            two_people_and_two_minimum_500N_props_required=True,free_overhead_requirement_mm=1920,
            external_tote_handoff_allowed=True),
        physical_and_unqualified=['Actual received module mounting/output datums, mass and screw lead',
            'Stock motor power-off retention; no qualified anti-drop device',
            'Assembly stiffness, preload, fabrication tolerances, lift/hand/handling loads and thermal/fume protection',
            'Actual tote usable capacity/liquid/load/temperature compatibility and wet commissioning',
            'Removal handling and carrying away disconnected accessories; hose/air/cable flexibility',
            'Full 300mm operating travel is not assessed; no controller settings applied'],
        elapsed_seconds=time.monotonic()-start_time,
        fabrication_release=False,operating_release=False)
    report['passed']=before==after and maxdelta<1e-7 and all(v['passed']for v in groups.values())
    OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],source_consistent=before==after,
        output=rel(OUT),groups=groups,elapsed_seconds=report['elapsed_seconds']),indent=2),flush=True)
    return 0 if report['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
