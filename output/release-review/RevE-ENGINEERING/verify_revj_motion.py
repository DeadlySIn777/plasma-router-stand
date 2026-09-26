"""Check nine nominal full-machine GM1 Rev J router poses from fresh source CAD.

Checks all eight X/Y/Z travel-box corners and the center. Each includes the
fixed chassis, actual frame-raised cap blanks, the Rev J one-piece bed module,
water and packaging geometry.
This is a sampled static interference check; it does not establish continuous
motion, independent-Y skew, actual cutter/workpiece/cable clearance, stiffness,
supplier-interface compatibility or a commissioned operational plasma state.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import itertools
import json
import os
import sys
import time
import traceback

SOURCE=Path(__file__).resolve().parent
DEFAULT_OUTPUT=SOURCE.parent/'RevJ-CAD'/'motion'/'revj-full-machine-poses.json'
STATES=list(itertools.product((275,1275),(175,975),(0,100)))+[(775,575,50)]


def source_hashes():
    """Hash the local generator modules actually imported into this process."""
    paths={Path(__file__).resolve()}
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.parent==SOURCE and path.suffix=='.py':paths.add(path)
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def clone_fixed(source):
    from cad_helpers import Model
    model=Model()
    model.allowed_intersections=source.allowed_intersections.copy()
    model.holds=list(source.holds)
    for part in source.parts:
        copied=copy.copy(part)
        copied.notes=list(part.notes)
        copied.flat=copy.deepcopy(part.flat)
        model.parts.append(copied)
    return model


def write_report(path,report,start):
    report['elapsed_seconds']=round(time.monotonic()-start,2)
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


def main(output=DEFAULT_OUTPUT):
    from cad_helpers import bbox,validate
    from build_revj import build_model
    from motion_details import make_motion

    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    report={'scope':__doc__,'revision':'GM1 Rev J working design','status':'RUNNING',
            'expected_pose_count':len(STATES),'states':[],
            'acceptance':{'all_world_and_local_shapes_valid_single_solids':True,
                          'local_world_volume_tolerance_mm3':'max(0.05, world_volume * 1e-7)',
                          'unresolved_positive_volume_threshold_mm3':0.02,
                          'sources_must_remain_unchanged_during_run':True}}
    write_report(output,report,start)
    try:
        before_build={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
        fixed,details=build_model(with_motion=False)
        assert not any(p.id.startswith(('TOOL_SPINDLE_','ZBX80_','Z_CARRIAGE_BOLT_')) for p in fixed.parts), 'Motion was not deferred'
        after_build=source_hashes()
        report['sources_sha256']={name:before_build.get(name) for name in after_build}
        report['sources_changed_during_build']={name:{'before':before_build.get(name),'after':value}
            for name,value in after_build.items() if before_build.get(name)!=value}
        report['fixed_part_count']=len(fixed.parts)
        report['cap_blanks_before_motion_drilling']=[{'id':p.id,'bounds_mm':bbox(p.shape)}
            for p in fixed.parts if p.id in ('RAIL_CAP_1_BLANK','RAIL_CAP_2_BLANK')]
        assert len(report['cap_blanks_before_motion_drilling'])==2
        report['build_status']=details.get('status')
        report['architecture_assumption']=details.get('architecture_assumption')
        print('Rev J fixed assembly:',len(fixed.parts),'parts',flush=True)
        for gy,hx,z in STATES:
            model=clone_fixed(fixed)
            make_motion(model,gantry_y=gy,head_x=hx,z_lift=z,tool='router')
            result=validate(model)
            ids=[p.id for p in model.parts]
            assert len(ids)==len(set(ids)), 'Duplicate component IDs'
            invalid_local=[]
            mismatches=[]
            for part in model.parts:
                valid=part.local.isValid()
                solids=len(part.local.Solids())
                local_volume=part.local.Volume()
                world_volume=part.shape.Volume()
                if not valid or solids!=1 or local_volume<=0:
                    invalid_local.append({'id':part.id,'valid':valid,'solid_count':solids,
                                          'volume_mm3':local_volume})
                delta=abs(world_volume-local_volume)
                tolerance=max(.05,world_volume*1e-7)
                if delta>tolerance:
                    mismatches.append({'id':part.id,'volume_delta_mm3':delta,
                                       'tolerance_mm3':tolerance})
            record={'configuration':{'gantry_y':gy,'head_x':hx,'z_lift':z,'tool':'router'},
                    'part_count':result['part_count'],
                    'all_world_shapes_valid_single_solids':True,
                    'invalid_local_shapes':invalid_local,
                    'local_world_geometry_mismatches':mismatches,
                    'broadphase_pairs':result['broadphase_pairs'],
                    'unresolved_intersections':result['unresolved_intersections'],
                    'documented_intersections':result['documented_intersections']}
            record['passed']=not(record['unresolved_intersections'] or invalid_local or mismatches)
            report['states'].append(record)
            if len(report['states'])==1:
                report['component_ids']=ids
                report['holds']=sorted(set(model.holds))
            else:
                assert ids==report['component_ids'], 'Pose component inventory changed'
            write_report(output,report,start)
            print('Rev J pose',gy,hx,z,'parts',result['part_count'],
                  'clashes',len(record['unresolved_intersections']),
                  'local-invalid',len(invalid_local),'volume-mismatches',len(mismatches),flush=True)
            if record['unresolved_intersections']:
                print(json.dumps({'configuration':record['configuration'],
                                  'clashes':record['unresolved_intersections']}),flush=True)
        final_hashes=source_hashes()
        report['sources_changed_during_run']={name:{'before':before,'after':final_hashes.get(name)}
            for name,before in report['sources_sha256'].items() if final_hashes.get(name)!=before}
        report['completed_pose_count']=len(report['states'])
        geometry_passed=all(s['passed'] for s in report['states'])
        sources_unchanged=not(report['sources_changed_during_build'] or report['sources_changed_during_run'])
        passed=geometry_passed and sources_unchanged
        report['all_sampled_poses_clear']=geometry_passed
        report['current_source_run_valid']=sources_unchanged
        report['status']='PASS' if passed else ('STALE' if geometry_passed else 'FAIL')
        write_report(output,report,start)
        print('Rev J full-machine motion:',report['status'],len(report['states']),
              'poses;',report['elapsed_seconds'],'seconds',flush=True)
        return 0 if passed else 2
    except Exception as error:
        report['status']='ERROR'
        report['error']={'type':type(error).__name__,'message':str(error),
                         'traceback':traceback.format_exc()}
        write_report(output,report,start)
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    try:code=main(args.output)
    except Exception:
        traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
