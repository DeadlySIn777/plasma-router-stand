"""Independent combined Rev I geometry and current-export verification.

This is static rigid-solid verification, not fabrication release, continuous
tool motion, actual workpiece/cable clearance, rigidity or brake qualification.
The same build_revi API used by the exporter generates each complete pose.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import math
import os
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
OUTPUT=Path(__file__).resolve().parent
CAD=ROOT/'output/release-review/RevI-CAD'
sys.path.insert(0,str(SOURCE))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def imported_hashes():
    paths={Path(__file__).resolve()}
    for module in list(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.parent==SOURCE and path.suffix=='.py':paths.add(path)
    return {str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(paths)}


def local_checks(model):
    """One solid, nonzero volume and rigid-transform volume/area preservation."""
    invalid=[];mismatches=[];seen=set();duplicates=[]
    for p in model.parts:
        if p.id in seen:duplicates.append(p.id)
        seen.add(p.id)
        vl=p.local.Volume();vw=p.shape.Volume()
        al=p.local.Area();aw=p.shape.Area()
        if not p.local.isValid() or len(p.local.Solids())!=1 or vl<=0:
            invalid.append({'id':p.id,'solid_count':len(p.local.Solids()),'volume_mm3':vl})
        vt=max(.05,vw*1e-7);at=max(.05,aw*1e-7)
        if abs(vl-vw)>vt or abs(al-aw)>at:
            mismatches.append({'id':p.id,'part_number':p.part_number,
                'volume_delta_mm3':abs(vl-vw),'volume_tolerance_mm3':vt,
                'area_delta_mm2':abs(al-aw),'area_tolerance_mm2':at})
    return {'invalid_local':invalid,'local_world_volume_or_area_mismatches':mismatches,
            'duplicate_component_ids':duplicates,'passed':not(invalid or mismatches or duplicates)}


def shared_part_checks(model):
    """A part-number export uses one local solid, so duplicates must be congruent.

    Purchased/guarded bodies are reported separately; they are not exported
    fabrication parts. Real differences in released fabricated geometry fail.
    A local coordinate rotation is acceptable only with a proven rigid match.
    Each boolean difference uses the actual local solid, not its picture.
    """
    from cad_helpers import bbox,intersection_volume,place
    groups={}
    for p in model.parts:groups.setdefault(p.part_number,[]).append(p)
    checks=[];bad=[];guarded=[];reoriented=[]
    def rigid_match(reference,candidate,tolerance):
        """Prove congruence over all 24 proper axis-aligned rotations, no mirror.

        Older link solids store their already oriented geometry as local data.
        In that case equal volume or dimensions alone are insufficient. Align
        each valid rotation by its minimum bounds and compare Boolean volume.
        """
        axes=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
        rb=bbox(reference);rv=reference.Volume()
        for u in axes:
            for v in axes:
                if sum(a*b for a,b in zip(u,v))!=0:continue
                rotated=place(candidate,(0,0,0),u=u,v=v);bb=bbox(rotated)
                if any(abs((rb[k+3]-rb[k])-(bb[k+3]-bb[k]))>1e-6 for k in range(3)):continue
                translation=tuple(rb[k]-bb[k] for k in range(3))
                aligned=rotated.translate(translation)
                difference=max(0,rv+candidate.Volume()-2*intersection_volume(reference,aligned))
                if difference<=tolerance:
                    return {'local_x_direction':u,'local_y_direction':v,
                            'translation_mm':translation,'symmetric_difference_mm3':difference}
        return None
    def drawing_geometry(part):
        if part.flat is None:return None
        data={k:part.flat.get(k,[]) for k in ('outline','holes','slots','internal','operations')}
        data['thickness_mm']=part.flat.get('thickness_mm')
        # Drill/operation order is not geometry; outer contour order is.
        for key in ('holes','slots','operations'):
            data[key]=sorted(data[key],key=lambda item:json.dumps(item,sort_keys=True))
        return data
    for pn,parts in groups.items():
        if len(parts)<2:continue
        first=parts[0];b0=bbox(first.local);v0=first.local.Volume()
        for p in parts[1:]:
            b=bbox(p.local);v=p.local.Volume();tolerance=max(.05,max(v0,v)*1e-7)
            delta=abs(v0-v);bd=max(abs(a-c) for a,c in zip(b0,b))
            intersection=None
            if delta<=tolerance and bd<=1e-6:
                intersection=intersection_volume(first.local,p.local)
                difference=max(0,v0+v-2*intersection)
            else:difference=None
            flat_diff=drawing_geometry(first)!=drawing_geometry(p)
            mismatch=delta>tolerance or bd>1e-6 or flat_diff or (difference is not None and difference>tolerance)
            transform=None
            if mismatch and not flat_diff and delta<=tolerance:
                transform=rigid_match(first.local,p.local,tolerance)
                if transform:
                    mismatch=False
                    reoriented.append({'part_number':pn,'reference_id':first.id,
                                       'compared_id':p.id,**transform})
            rec={'part_number':pn,'reference_id':first.id,'compared_id':p.id,
                 'local_volume_delta_mm3':delta,'max_local_bound_delta_mm':bd,
                 'symmetric_difference_mm3':difference,'tolerance_mm3':tolerance,
                 'manufacturing_flat_geometry_mismatch':flat_diff,
                 'individual_export_guarded':any(x.purchased or 'GUARDED' in x.release for x in (first,p))}
            if mismatch:
                if rec['individual_export_guarded']:guarded.append(rec)
                else:bad.append(rec)
            checks.append({'part_number':pn,'compared_id':p.id,'passed':not mismatch})
    return {'compared_duplicate_instances':len(checks),'fabrication_geometry_mismatches':bad,
            'guarded_or_purchased_geometry_mismatches':guarded,
            'proven_coordinate_only_differences':reoriented,
            'passed':not bad,'scope':'Boolean local-geometry congruence and manufacturing drawing equality. Rigid axis rotations/translations are explicitly proven; reflections are not allowed. Does not establish machining allowances or purchased part identity.'}


def assembly_check(model,label,*,shared=False):
    from cad_helpers import validate
    validated=validate(model)
    result={'label':label,'part_count':len(model.parts),
        'all_world_shapes_valid_single_solids':True,
        'total_solid_volume_mm3':sum(p.shape.Volume() for p in model.parts),
        'unresolved_intersections':validated['unresolved_intersections'],
        'documented_intersections':validated['documented_intersections'],
        'local_integrity':local_checks(model)}
    if shared:result['shared_part_numbers']=shared_part_checks(model)
    result['passed']=(not result['unresolved_intersections'] and result['local_integrity']['passed']
                      and (not shared or result['shared_part_numbers']['passed']))
    print(label,'parts',result['part_count'],'clashes',len(result['unresolved_intersections']),
          'local mismatches',len(result['local_integrity']['local_world_volume_or_area_mismatches']),
          'passed',result['passed'],flush=True)
    return result


def stored_inventory_check(router,stored):
    a={p.id:p for p in router.parts};b={p.id:p for p in stored.parts}
    from cad_helpers import bbox,intersection_volume
    missing=sorted(set(a)-set(b));added=sorted(set(b)-set(a));changed=[]
    for ident in sorted(set(a)&set(b)):
        pa,pb=a[ident],b[ident]
        va,vb=pa.local.Volume(),pb.local.Volume();tol=max(.05,max(va,vb)*1e-7)
        if pa.part_number!=pb.part_number or abs(va-vb)>tol or max(abs(x-y) for x,y in zip(bbox(pa.local),bbox(pb.local)))>1e-6:
            changed.append({'id':ident,'router_pn':pa.part_number,'stored_pn':pb.part_number,'local_volume_delta_mm3':abs(va-vb)})
    return {'missing_in_stored':missing,'added_in_stored':added,'changed_local_parts':changed,
            'passed':not(missing or added or changed),
            'scope':'Both states should contain the same physical inventory and local fabrication definitions. World pose can differ.'}


def read_steps(models,source_hashes):
    """Do not parse incomplete export files while the root exporter is running."""
    import cadquery as cq
    manifest_path=CAD/'engineering-manifest.json'
    if not manifest_path.exists():
        return {'status':'NOT_AVAILABLE','reason':'No completed Rev I engineering manifest exists; run --steps-only after export.'}
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest_sources=manifest.get('source_sha256',{})
    source_mismatch=[]
    for path,digest in source_hashes.items():
        if str(Path(path).parent).replace('\\','/')=='output/release-review/RevE-ENGINEERING':
            if manifest_sources.get(Path(path).name)!=digest:
                source_mismatch.append({'source':path,'fresh_hash':digest,'manifest_hash':manifest_sources.get(Path(path).name)})
    if source_mismatch:
        return {'status':'STALE','source_mismatches':source_mismatch,'reason':'STEP export manifest does not match this fresh builder; no current STEP claim made.'}
    records=[]
    for name,model in models.items():
        path=CAD/'step'/(name+'.step')
        if not path.exists():
            records.append({'name':name,'passed':False,'reason':'STEP file missing'});continue
        first_hash=sha(path)
        shape=cq.importers.importStep(str(path)).val()
        final_hash=sha(path)
        expected=sum(p.shape.Volume() for p in model.parts)
        tolerance=max(.2,expected*1e-7)
        record={'name':name,'sha256':final_hash,'stable_during_read':first_hash==final_hash,
                'valid':shape.isValid(),'solid_count':len(shape.Solids()),'expected_solid_count':len(model.parts),
                'volume_delta_mm3':abs(shape.Volume()-expected),'volume_tolerance_mm3':tolerance,
                'manifest_hash':manifest.get('state_checks',{}).get(name,{}).get('step_readback',{}).get('sha256')}
        record['passed']=(record['valid'] and record['stable_during_read']
                          and record['solid_count']==record['expected_solid_count']
                          and record['volume_delta_mm3']<=tolerance
                          and record['sha256']==record['manifest_hash'])
        records.append(record)
        print('STEP',name,'passed',record['passed'],flush=True)
    return {'status':'PASS' if all(r['passed'] for r in records) else 'FAIL','states':records}


def main(steps_only=False):
    from build_revi import build_model,stored_model,plasma_hardware_model
    begin=time.monotonic()
    before={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in SOURCE.glob('*.py')}
    before[str(Path(__file__).resolve().relative_to(ROOT)).replace('\\','/')]=sha(__file__)
    path=OUTPUT/('step-verification.json' if steps_only else 'verification.json')
    report={'revision':'Rev I integrated completion','scope':__doc__,'status':'RUNNING',
            'states':{},'poses':[],'plasma_hardware_poses':[],'source_initial_sha256':before}
    def write():
        report['elapsed_seconds']=round(time.monotonic()-begin,2)
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    write()
    try:
        router,details=build_model();stored=stored_model(router);plasma,_=plasma_hardware_model(stored)
        report['architecture_assumption']=details.get('architecture_assumption')
        report['holds']=sorted(set(router.holds))
        if not steps_only:
            report['states']['RevI_ROUTER']=assembly_check(router,'RevI_ROUTER',shared=True);write()
            report['states']['RevI_BED_STORED']=assembly_check(stored,'RevI_BED_STORED');write()
            report['states']['RevI_PLASMA_HARDWARE']=assembly_check(plasma,'RevI_PLASMA_HARDWARE');write()
            report['stored_inventory_integrity']=stored_inventory_check(router,stored);write()
            for gy,hx,z in list(itertools.product((275,1275),(175,975),(0,100)))+[(775,575,50)]:
                m,_=build_model(gantry_y=gy,head_x=hx,z_lift=z)
                result=assembly_check(m,f'router pose Y{gy} X{hx} Z{z}')
                result['configuration']={'gantry_y':gy,'head_x':hx,'z_lift':z}
                report['poses'].append(result);write()
                pm,_=plasma_hardware_model(stored_model(m))
                presult=assembly_check(pm,f'plasma hardware pose Y{gy} X{hx} Z{z}')
                presult['configuration']={'gantry_y':gy,'head_x':hx,'z_lift':z,'actual_torch_present':False}
                report['plasma_hardware_poses'].append(presult);write()
        current=imported_hashes()
        report['source_imported_sha256']=current
        report['sources_changed_during_run']={p:{'before':before.get(p),'after':v} for p,v in current.items() if before.get(p)!=v}
        report['step_readback']=read_steps({'RevI_ROUTER':router,'RevI_BED_STORED':stored,'RevI_PLASMA_HARDWARE':plasma},current);write()
        final=imported_hashes()
        report['sources_changed_during_run'].update({p:{'before':before.get(p),'after':v} for p,v in final.items() if before.get(p)!=v})
        geometry_passed=(steps_only or (all(r['passed'] for r in report['states'].values())
                         and report['stored_inventory_integrity']['passed']
                         and len(report['poses'])==9 and all(r['passed'] for r in report['poses'])
                         and len(report['plasma_hardware_poses'])==9 and all(r['passed'] for r in report['plasma_hardware_poses'])))
        current_sources=not report['sources_changed_during_run']
        step_status=report['step_readback']['status']
        report['geometry_passed']=geometry_passed if not steps_only else None
        report['status']=('STALE' if not current_sources else 'FAIL' if not geometry_passed or step_status=='FAIL'
                          else 'STEP_EXPORT_STALE' if step_status=='STALE'
                          else 'STEP_EXPORT_PENDING' if step_status=='NOT_AVAILABLE'
                          else 'PASS')
        write();print('REVI_VERIFICATION',report['status'],report['elapsed_seconds'],'seconds',flush=True)
        return 0 if report['status'] in ('PASS','STEP_EXPORT_PENDING') else 2
    except Exception as error:
        report['status']='ERROR';report['error']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
        write();raise


def acceptance_index():
    """Current Rev I evidence index, including head, structure and controls."""
    from final_acceptance import main as join_current_evidence
    return join_current_evidence()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--steps-only',action='store_true',help='Fresh default/stored builders and current STEP readback only.')
    mode.add_argument('--acceptance-index',action='store_true',help='Join current source-matching geometry/path/export proofs without rerunning CAD.')
    args=parser.parse_args()
    try:code=acceptance_index() if args.acceptance_index else main(args.steps_only)
    except Exception:traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
