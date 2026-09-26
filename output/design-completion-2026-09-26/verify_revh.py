"""Independent combined Rev H geometry and current-export verification.

This is static rigid-solid verification, not fabrication release, continuous
tool motion, actual workpiece/cable clearance, rigidity or brake qualification.
The same build_revh API used by the exporter generates each complete pose.
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
CAD=ROOT/'output/release-review/RevH-CAD'
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
        return {'status':'NOT_AVAILABLE','reason':'No completed Rev H engineering manifest exists; run --steps-only after export.'}
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
    from build_revh import build_model,stored_model
    begin=time.monotonic()
    before={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in SOURCE.glob('*.py')}
    before[str(Path(__file__).resolve().relative_to(ROOT)).replace('\\','/')]=sha(__file__)
    path=OUTPUT/('step-verification.json' if steps_only else 'verification.json')
    report={'revision':'Rev H integrated completion','scope':__doc__,'status':'RUNNING',
            'states':{},'poses':[],'source_initial_sha256':before}
    def write():
        report['elapsed_seconds']=round(time.monotonic()-begin,2)
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    write()
    try:
        router,details=build_model();stored=stored_model(router)
        report['architecture_assumption']=details.get('architecture_assumption')
        report['holds']=sorted(set(router.holds))
        if not steps_only:
            report['states']['RevH_ROUTER']=assembly_check(router,'RevH_ROUTER',shared=True);write()
            report['states']['RevH_BED_STORED']=assembly_check(stored,'RevH_BED_STORED');write()
            report['stored_inventory_integrity']=stored_inventory_check(router,stored);write()
            for gy,hx,z in list(itertools.product((275,1275),(175,975),(0,100)))+[(775,575,50)]:
                m,_=build_model(gantry_y=gy,head_x=hx,z_lift=z)
                result=assembly_check(m,f'router pose Y{gy} X{hx} Z{z}')
                result['configuration']={'gantry_y':gy,'head_x':hx,'z_lift':z}
                report['poses'].append(result);write()
        current=imported_hashes()
        report['source_imported_sha256']=current
        report['sources_changed_during_run']={p:{'before':before.get(p),'after':v} for p,v in current.items() if before.get(p)!=v}
        report['step_readback']=read_steps({'RevH_ROUTER':router,'RevH_BED_STORED':stored},current);write()
        final=imported_hashes()
        report['sources_changed_during_run'].update({p:{'before':before.get(p),'after':v} for p,v in final.items() if before.get(p)!=v})
        geometry_passed=(steps_only or (all(r['passed'] for r in report['states'].values())
                         and report['stored_inventory_integrity']['passed']
                         and len(report['poses'])==9 and all(r['passed'] for r in report['poses'])))
        current_sources=not report['sources_changed_during_run']
        step_status=report['step_readback']['status']
        report['geometry_passed']=geometry_passed if not steps_only else None
        report['status']=('STALE' if not current_sources else 'FAIL' if not geometry_passed or step_status=='FAIL'
                          else 'STEP_EXPORT_STALE' if step_status=='STALE'
                          else 'STEP_EXPORT_PENDING' if step_status=='NOT_AVAILABLE'
                          else 'PASS')
        write();print('REVH_VERIFICATION',report['status'],report['elapsed_seconds'],'seconds',flush=True)
        return 0 if report['status'] in ('PASS','STEP_EXPORT_PENDING') else 2
    except Exception as error:
        report['status']='ERROR';report['error']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
        write();raise


def acceptance_index():
    """Join current source-matching proof records; do not rewrite older results."""
    checks=[]
    definitions=[
        ('Integrated solids, shared parts and nine poses',OUTPUT/'verification.json','source_imported_sha256',
         lambda r:r.get('geometry_passed') is True and not r.get('sources_changed_during_run') and len(r.get('poses',[]))==9),
        ('Independent final STEP readback',OUTPUT/'step-verification.json','source_imported_sha256',
         lambda r:r.get('status')=='PASS' and r.get('step_readback',{}).get('status')=='PASS' and not r.get('sources_changed_during_run')),
        ('Six spoilboard continuous routes',OUTPUT/'routes/spoil-transfer-check.json','complete_source_sha256',
         lambda r:r.get('integrated_passed') is True and len(r.get('records',[]))==6),
        ('Six panel continuous routes',OUTPUT/'routes/panel-path-check.json','complete_source_sha256',
         lambda r:r.get('integrated_passed') is True and len(r.get('panels',[]))==6),
        ('Four beam continuous routes',OUTPUT/'routes/beam-path-check.json','complete_source_sha256',
         lambda r:r.get('integrated_passed') is True and len(r.get('records',[]))==4),
        ('Added restraint and temporary capture paths',OUTPUT/'bed/restraint-paths.json','source_sha256',
         lambda r:r.get('pass') is True and r.get('sources_unchanged') is True),
        ('Integrated hatch and washout service paths',OUTPUT/'water/integrated-verification.json','all_sources_sha256',
         lambda r:r.get('passed') is True and r.get('integrated') is True and not r.get('sources_changed_during_run')),
        ('Final assembly exports',CAD/'engineering-manifest.json','source_sha256',
         lambda r:r.get('integrated_geometry_pass') is True and not r.get('sources_changed_during_build')),
    ]
    for label,path,hash_key,predicate in definitions:
        rec={'check':label,'report':str(path.relative_to(ROOT)).replace('\\','/')}
        if not path.exists():
            rec.update(status='MISSING',passed=False);checks.append(rec);continue
        data=json.loads(path.read_text(encoding='utf-8'));recorded=data.get(hash_key,{})
        mismatches=[]
        if not isinstance(recorded,dict) or not recorded:
            mismatches.append({'reason':'Missing source hash map'})
        else:
            for filename,digest in recorded.items():
                file=Path(filename)
                file=(SOURCE/file if file.parent==Path('.') else ROOT/file) if not file.is_absolute() else file
                current=sha(file) if file.exists() else None
                if current!=digest:mismatches.append({'file':str(file),'recorded':digest,'current':current})
            # Every proof must record all integrated builder/extension sources.
            names={Path(name).name for name in recorded}
            for name in ('build_revh.py','bed_completion.py','water_completion.py','motion_completion.py'):
                if name not in names:mismatches.append({'reason':'Integrated source missing','file':name})
        passed=bool(predicate(data)) and not mismatches
        rec.update(status='PASS' if passed else 'STALE' if mismatches else 'FAIL',
                   passed=passed,report_sha256=sha(path),source_mismatches=mismatches)
        checks.append(rec)
    # Bind the final acceptance record to the bytes currently available to open.
    step_path=OUTPUT/'step-verification.json'
    if step_path.exists():
        step=json.loads(step_path.read_text(encoding='utf-8'))
        for state in step.get('step_readback',{}).get('states',[]):
            path=CAD/'step'/(state['name']+'.step')
            current=sha(path) if path.exists() else None
            passed=bool(current) and current==state.get('sha256')
            checks.append({'check':'Current '+state['name']+' STEP bytes','report':str(path.relative_to(ROOT)).replace('\\','/'),
                           'status':'PASS' if passed else 'STALE','passed':passed,
                           'current_sha256':current,'verified_sha256':state.get('sha256')})
    result={'status':'PASS' if checks and all(r['passed'] for r in checks) else 'NOT_CURRENT_OR_NOT_PASSING',
            'scope':'Recorded nominal CAD geometry and named continuous paths, with source-matching independent STEP readback. This is not a fabrication, operational-plasma, structural, controls or physical-safety release.',
            'checks':checks,'current_extension_sha256':{n:sha(SOURCE/n) for n in ('build_revh.py','bed_completion.py','water_completion.py','motion_completion.py')},
            'index_generator_sha256':sha(__file__),
            'diagnostic_history':'diagnostic-before-final-freeze contains superseded diagnostic reports. A historical STEP_EXPORT_STALE/PENDING status in verification.json is superseded only for export readback by the current passing step-verification.json; its geometry/source findings are not rewritten.'}
    (OUTPUT/'acceptance-index.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    lines=['# Rev H CAD verification index','',f"**Recorded checks: {result['status']}.** {result['scope']}",'',
           '| Check | Current result |','|---|---|']
    for rec in checks:
        relative=os.path.relpath(ROOT/rec['report'],OUTPUT).replace('\\','/')
        lines.append(f"| [{rec['check']}]({relative}) | {rec['status']} |")
    lines.extend(['',result['diagnostic_history'],'',
        'Current results do not close purchased-interface measurements, coupling/brake fit and response, the unfinished floating/breakaway plasma head, flexible cable/hoses, rigidity or physical commissioning. Read each linked report for its exact exclusions.',
        '', '[Complete hashes and provenance](acceptance-index.json).',''])
    (OUTPUT/'ACCEPTANCE.md').write_text('\n'.join(lines),encoding='utf-8')
    print('REVH_ACCEPTANCE_INDEX',result['status'],flush=True)
    return 0 if result['status']=='PASS' else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--steps-only',action='store_true',help='Fresh default/stored builders and current STEP readback only.')
    mode.add_argument('--acceptance-index',action='store_true',help='Join current source-matching geometry/path/export proofs without rerunning CAD.')
    args=parser.parse_args()
    try:code=acceptance_index() if args.acceptance_index else main(args.steps_only)
    except Exception:traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
