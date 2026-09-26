"""Rebuild, static test, and continuous hatch paths for the water extension."""
from pathlib import Path
import hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
sys.path.insert(0,str(SOURCE))
from build_revg import build_model,stored_model
from water_completion import extend_router_model,hatch_service_model,HATCHES,LID_TOP
from cad_helpers import validate,bbox,plate
from sweep_checks import translation_segment,rotation_segment

def main():
    integrated='--integrated' in sys.argv
    all_source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    start=time.monotonic()
    if integrated:
        from build_revh import build_model as builder,stored_model as storer
        m,all_details=builder();details=all_details['water_completion']
        before={p.id for p in m.parts if not p.id.startswith(('H_WT_','H_REFILL_','H_DRAIN_'))}
    else:
        storer=stored_model;m,_=build_model();before={p.id for p in m.parts};details=extend_router_model(m)
    report={'source_sha256':all_source_hashes['water_completion.py'],'all_sources_sha256':all_source_hashes,'integrated':integrated,'definition':details,'state_checks':{},'paths':[]}
    for name,model in [('router_closed',m),('bed_stored_closed',storer(m)),('service_open',hatch_service_model(storer(m)))]:
        r=validate(model)
        report['state_checks'][name]={'count':r['part_count'],'clashes':r['unresolved_intersections'],'all_solids_valid':True}
        print(name,r['part_count'],'clashes',len(r['unresolved_intersections']),flush=True)
    report['new_ids']=[p.id for p in m.parts if p.id not in before]
    report['changed_existing_ids']=['WT_LID','WP_FLOOR','WT_CLEANOUT_NECK']
    flats=[]
    for p in m.parts:
        if p.flat and (p.id not in before or p.id in report['changed_existing_ids']):
            f=p.flat;rebuild=plate(f['outline'],f['thickness_mm'],f['holes'],f['slots'],f['internal'])
            delta=abs(rebuild.Volume()-p.local.Volume())
            assert delta<1e-6,(p.id,delta)
            flats.append({'id':p.id,'volume_delta_mm3':delta})
    report['flat_local_consistency']=flats
    # Both covers are moved sequentially; the first parked cover remains a
    # collision obstacle for the second. All gaskets/pockets/pump/tools remain.
    current={p.id:p.shape for p in storer(m).parts if not any(p.id.startswith('H_WT_'+h['tag']+'_BOLT_') for h in HATCHES)}
    for h in HATCHES:
        names=['H_WT_'+h['tag']+'_COVER','H_WT_'+h['tag']+'_PULL_TAB'];moving={name:current.pop(name) for name in names};fixed=current.copy()
        x,y,w,d=h['cover'];axis=(x,h['park_y'],LID_TOP+2+50)
        route={'hatch':h['tag'],'segments':[]}
        def trans(label,delta):
            nonlocal moving
            r=translation_segment(moving,fixed,delta);route['segments'].append({'name':label,**r})
            moving={n:s.translate(delta) for n,s in moving.items()}
        trans('lift50',(0,0,50));trans('move_to_pocket_plane',(0,h['park_y']-y,0))
        r=rotation_segment(moving,fixed,axis,'X',0,90,max_step_deg=1)
        route['segments'].append({'name':'rotate_upright',**r})
        moving={n:s.rotate(axis,(x+1,axis[1],axis[2]),90) for n,s in moving.items()}
        trans('lower_into40mm_pockets',(0,0,-49))
        current.update(moving)
        report['paths'].append(route)
        print(h['tag'],[(s['name'],s['status'],len(s['candidates'])) for s in route['segments']],flush=True)
    # Cover is hand-held after withdrawal; no unmodeled catch vessel or storage
    # support is implied. Fasteners are conventionally removed first.
    current={name:s for name,s in current.items() if not name.startswith(('H_WT_WASHOUT_BOLT_','H_WT_WASHOUT_WASHER_','H_WT_WASHOUT_NUT_'))}
    name='H_WT_WASHOUT_COVER';moving={name:current.pop(name)}
    route={'hatch':'EMPTY_TANK_WASHOUT_COVER','segments':[]}
    for label,delta in [('lower20_after_removing_four_fasteners',(0,0,-20)),('withdraw_forward80_handheld',(0,-80,0))]:
        r=translation_segment(moving,current,delta);route['segments'].append({'name':label,**r})
        moving={n:s.translate(delta) for n,s in moving.items()}
    report['paths'].append(route)
    print('WASHOUT',[(s['name'],s['status'],len(s['candidates'])) for s in route['segments']],flush=True)
    for route in report['paths']:
        for segment in route['segments']:
            b=segment['swept_enclosing_bounds_mm']
            segment['within_chassis_plan_0_1150_0_1450']=b[0]>=0 and b[1]>=0 and b[3]<=1150 and b[4]<=1450
    report['scope_limits']=['Twelve hatch fasteners are removed before the hatch proof; screw handling and loose storage are not proven.',
        'Nominal rigid path bound, no human hand/brush envelope, manufacturing tolerances, gasket adhesion or wet cleaning test.',
        'Purchased valve/union blocks remain placement reserves and cannot close FW01 by themselves.',
        'No actual cabinet door/thermal/wiring design is introduced.']
    report['elapsed_seconds']=time.monotonic()-start
    final_source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    report['sources_changed_during_run']={name:sha for name,sha in all_source_hashes.items() if final_source_hashes.get(name)!=sha}
    report['passed']=all(not v['clashes'] for v in report['state_checks'].values()) and all(s['status']=='CLEAR' and s['within_chassis_plan_0_1150_0_1450'] for h in report['paths'] for s in h['segments']) and (not integrated or not report['sources_changed_during_run'])
    filename='integrated-verification.json' if integrated else 'verification.json'
    Path(__file__).with_name(filename).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return 0 if report['passed'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
