"""Bind changed tool obstacles to existing complete-machine path proofs.

Disjoint exact enclosing boxes establish that newly installed tool solids cannot
intersect the recorded motions. This supplements, never replaces, the underlying
full-obstacle proofs. Small hardware motions, fingers, cables and torch are out
of scope, as in those proofs.
"""
from pathlib import Path
import hashlib,json,math,os,sys
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
sys.path[:0]=[str(SOURCE),str(BASE/'structure')]
import cadquery as cq
import build_revi as builder
import bed_cassettes as bc
from cad_helpers import bbox
from check_reinforced_paths import transform,swept_box
from check_transfer_staging import router_tool_id


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sources():
    paths=list(SOURCE.glob('*.py'))+[Path(__file__),OUT/'check_transfer_staging.py',
      BASE/'structure/check_reinforced_paths.py',BASE/'structure/check_temp_fixture_transfer.py',
      BASE/'verify_revi_routes.py',ROOT/'output/cad-repair-2026-09-25/check_spoil_transfer.py',
      ROOT/'output/cad-repair-2026-09-25/verify_revg_beam_path.py']
    return {str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths}


def source_mismatches(d,key):
    issues=[];hashes=d.get(key,{})
    if not hashes:return ['Missing '+key]
    for name,value in hashes.items():
        p=Path(name)
        if not p.is_absolute():p=SOURCE/p if p.parent==Path('.') else ROOT/p
        if not p.exists() or sha(p)!=value:issues.append(str(p))
    return issues


def enclosing_gap(a,b):
    # Positive separation on one axis proves disjointness of the whole boxes.
    return max(max(b[i]-a[i+3],a[i]-b[i+3]) for i in range(3))


def normal_beam_sweeps(router):
    result=[]
    for i,by in enumerate(bc.BEAM_Y):
        ids=[p.id for p in router.parts if bc._PLACEMENTS.get(p.id,('',-1))[:2]==('beam',i)]
        shape=cq.Compound.makeCompound([router.find(n).shape for n in ids])
        ops=[('lift_clear_of_seats',('T',(0,0,80))),
          ('move_lifted_beam_to_front',('T',(0,78.8-(by-25.4),0))),
          ('rotate_on_side_above_front',('R',(113,78.8,922),(114,78.8,922),90))]
        if i==0:ops.extend([
          ('raise_for_temporary_park_approach',('T',(0,0,18.8))),
          ('move_above_second_beam',('T',(0,439.1,0))),
          ('lower_onto_second_beam',('T',(0,0,-20))),
          ('lift_from_temporary_park',('T',(0,0,20))),
          ('return_on_side_to_front_portal',('T',(0,-439.1,0))),
          ('lower_in_open_front_portal',('T',(0,0,-352.8))),
          ('move_into_rear_lower_rack',('T',(0,90,0))),
          ('lower_onto_rear_shelf',('T',(0,0,-3)))])
        elif i==1:ops.append(('lower_onto_front_shelf',('T',(0,0,-337))))
        elif i==2:ops.extend([('lower_above_front_lower_beam',('T',(0,0,-277.2))),
          ('move_above_rear_lower_beam',('T',(0,90,0))),('lower_onto_rear_stacking_pads',('T',(0,0,-3)))])
        else:ops.append(('lower_onto_front_stacking_pads',('T',(0,0,-280.2))))
        segments=[]
        for name,op in ops:
            segments.append({'name':name,'swept_bounds_mm':swept_box(shape,op)})
            shape=transform(shape,op)
        expected=cq.Compound.makeCompound([bc.transformed_to_storage(router.find(n)) for n in ids])
        error=shape.cut(expected).Volume()+expected.cut(shape).Volume()
        result.append({'beam':i+1,'segments':segments,'final_symmetric_difference_mm3':error})
    return result


def main():
    before=sources();reports={};identities={};bindings=[]
    definitions={
      'spoil':('routes/spoil-transfer-check.json','complete_source_sha256','integrated_passed'),
      'panel':('routes/panel-path-check.json','complete_source_sha256','integrated_passed'),
      'beam':('routes/beam-path-check.json','complete_source_sha256','integrated_passed'),
      'restraint':('structure/reinforced-restraint-paths.json','source_sha256','pass'),
      'fixture':('structure/temporary-fixture-transfer.json','source_sha256','pass'),
      'staging':('motion/transfer-staging-verification.json','source_sha256','passed')}
    for key,(name,hashkey,passkey) in definitions.items():
        path=BASE/name;data=json.loads(path.read_text(encoding='utf-8'));reports[key]=data
        identities[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path)
        mismatches=source_mismatches(data,hashkey)
        bindings.append({'report':name,'passed':data.get(passkey) is True and not mismatches,'source_mismatches':mismatches})
    router,_=builder.build_model();stored=builder.stored_model(router)
    plasma,_=builder.plasma_hardware_model(stored)
    installed_router={p.id:bbox(p.shape) for p in router.parts if router_tool_id(p.id)}
    # Include every changed solid, not merely a prefix-selected visible body.
    changed_head={}
    parked_by_id={p.id:p for p in stored.parts}
    for p in plasma.parts:
        old=parked_by_id.get(p.id)
        same=old is not None and p.shape.wrapped.IsSame(old.shape.wrapped)
        changed=not same and (old is None or max(abs(a-b) for a,b in zip(bbox(old.shape),bbox(p.shape)))>1e-7 or p.shape.cut(old.shape).Volume()+old.shape.cut(p.shape).Volume()>1e-5)
        if changed:
            changed_head[p.id]=bbox(p.shape)
    checks=[]
    def compare(label,segments,obstacles):
        rows=[]
        for name,bounds in segments:
            gaps={ident:enclosing_gap(bounds,b) for ident,b in obstacles.items()}
            bad={n:g for n,g in gaps.items() if g<=1e-7}
            rows.append({'segment':name,'swept_bounds_mm':bounds,'obstacle_count':len(obstacles),
                         'minimum_axis_separation_mm':min(gaps.values()),'unresolved_enclosing_boxes':bad,'passed':not bad})
        checks.append({'phase':label,'segments':rows,'passed':all(r['passed'] for r in rows)})
    panel_segments=[('panel'+str(p['panel'])+'/'+s['name'],s['swept_enclosing_bounds_mm'])
        for p in reports['panel']['panels'] if p['panel'] in (2,3,4,5,6) for s in p['segments']]
    compare('Panels6..2 stored while router remains mounted',panel_segments,installed_router)
    early_prefixes=('stage_top_bar_','stage_bare_rod_','close_spoil_guard_','restore_bare_rod_')
    early=[(p['name']+'/'+str(i+1),s['result']['swept_bounding_box_mm'])
        for p in reports['restraint']['paths'] if p['name'].startswith(early_prefixes)
        for i,s in enumerate(p['segments'])]
    compare('Earlier rack/guard preparation with mounted router',early,installed_router)
    # The normal board proof already uses build_revi's mounted router. Keep an
    # explicit current-source link instead of pretending a changed-obstacle test.
    checks.append({'phase':'All six spoilboard routes already use mounted-router builder',
       'passed':bindings[0]['passed'] and reports['spoil'].get('builder')=='build_revi.build_model',
       'basis':'Source-bound check_spoil_transfer.main obtains its model directly from the injected build_revi builder and never calls store_router_tool; prepare_handling_model only moves rack restraints.'})
    beams=normal_beam_sweeps(router)
    for beam,original in zip(beams,reports['beam']['records']):
        names=[s['name'] for s in beam['segments']]
        assert beam['beam']==original['beam'] and names==list(original['phases']),('Different prescribed beam route',beam['beam'])
    compare('Normal four-beam storage with installed plasma head',[(str(b['beam'])+'/'+s['name'],s['swept_bounds_mm']) for b in beams for s in b['segments']],changed_head)
    later=[(p['name']+'/'+str(i+1),s['result']['swept_bounding_box_mm'])
        for p in reports['restraint']['paths'] if p['name'].startswith(('install_panel_top_bar_','insert_temporary_box_'))
        for i,s in enumerate(p['segments'])]
    later.extend((p['name']+'/'+str(i+1),s['result']['swept_bounding_box_mm'])
        for p in reports['fixture']['paths'] for i,s in enumerate(p['segments']))
    compare('Later rack and temporary-fixture paths with installed plasma head',later,changed_head)
    report={'builder':'build_revi','scope':__doc__,'source_sha256':before,'evidence_report_sha256':identities,
       'evidence_bindings':bindings,'changed_obstacles':{'mounted_router':installed_router,'installed_head_and_relocated_mounting_hardware':changed_head},
       'checks':checks,'reconstructed_beam_paths':beams,
       'explicit_limits':['Only named nominal rigid parts and recorded prescribed paths are covered; no hands, leads, hoses, actual torch or tolerance/strength claim.',
          'Removing old parked obstacles cannot introduce an intersection; all newly located installed solids are checked. Underlying full-obstacle path reports must independently pass with current sources.',
          'Revised panel1 rear-table route, router removal and split-head exchange have separate full-obstacle reports; those are not replaced here.',
          'Fastener handling and gate/pin insertion remain excluded wherever excluded by the underlying reports.']}
    report['sources_unchanged']=before==sources()
    report['reports_unchanged']=all((ROOT/n).is_file() and sha(ROOT/n)==value for n,value in identities.items())
    report['passed']=report['sources_unchanged'] and report['reports_unchanged'] and all(b['passed'] for b in bindings) and all(c['passed'] for c in checks) and all(b['final_symmetric_difference_mm3']<1e-5 for b in beams)
    (OUT/'conversion-prerequisites.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('CONVERSION_PREREQUISITES',report['passed'],flush=True)
    for c in checks:
        print(c['phase'],c['passed'],flush=True)
        if not c['passed']:print([r for r in c.get('segments',[]) if not r['passed']],flush=True)
    for b in bindings:
        if not b['passed']:print('EVIDENCE',b,flush=True)
    return 0 if report['passed'] else 2


if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
