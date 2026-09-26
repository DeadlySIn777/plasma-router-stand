"""Rev H integration of completion work; no unverified fabrication release."""
from pathlib import Path
import copy,hashlib,importlib,json,os,sys,time
import build_revg as previous
from cad_helpers import export,Model

SOURCE=Path(__file__).resolve().parent
OUT=SOURCE.parent/'RevH-CAD'
EXTENSIONS=('bed_completion','water_completion','motion_completion')


def build_model(with_motion=True, gantry_y=1275, head_x=575, z_lift=100):
    model,baseline=previous.build_model(with_motion=False)
    details={
        'baseline_rev_g_metadata':baseline,
        'baseline_metadata_scope':'Historical input definition only. Its masses and conversion procedure are superseded by the Rev H completion details and handling report.',
        'architecture_assumption':baseline['architecture_assumption'],
    }
    if with_motion:
        from motion_details import make_motion
        details['motion']=make_motion(model, gantry_y=gantry_y, head_x=head_x,
                                     z_lift=z_lift, tool='router')
    for name in EXTENSIONS:
        if name=='motion_completion' and not with_motion:
            continue
        mod=importlib.import_module(name)
        result=mod.extend_router_model(model)
        details[name]=result
    if with_motion:
        details['motion']['holds']=details['motion_completion']['active_motion_holds']
    details['revision']='H completion work'
    details['status']='INTEGRATED DESIGN REVIEW - NOT A FABRICATION RELEASE'
    details['confirmed_inputs']={'Y_modules':'Ordered and on the way; user, 26 September 2026',
        'X_and_Z':'User plans to order Monday, 28 September 2026',
        'frame_stock':'User sourcing 2 x 2 inch steel tube at a junkyard; lengths/wall/grade not yet supplied'}
    return model,details


def stored_model(source):
    stored=previous.stored_model(source)
    for name in EXTENSIONS:
        module=importlib.import_module(name)
        if hasattr(module,'extend_stored_model'):
            module.extend_stored_model(stored,source)
    return stored


def write_mesh(model,name):
    before=previous.OUT
    try:
        previous.OUT=OUT
        previous.write_mesh(model,name)
    finally:previous.OUT=before


def main():
    start=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
    initial_sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    router,details=build_model()
    parked=stored_model(router)
    print('Rev H',len(router.parts),'router parts;',len(parked.parts),'stored parts',flush=True)
    states={}
    for name,model,individual in [('RevH_ROUTER',router,True),('RevH_BED_STORED',parked,False)]:
        result=export(model,OUT,name,individual=individual)
        states[name]={'part_count':result['part_count'],'step_readback':result['step_readback'],
                     'unresolved_intersections':result['unresolved_intersections']}
        print(name,'clashes',len(result['unresolved_intersections']),flush=True)
        if result['unresolved_intersections']:
            print(json.dumps(result['unresolved_intersections'],indent=2),flush=True)
        write_mesh(model,name)
    details['state_checks']=states
    details['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    details['sources_changed_during_build']={k:v for k,v in initial_sources.items() if details['source_sha256'].get(k)!=v}
    details['holds']=sorted(set(router.holds))
    details['elapsed_seconds']=round(time.monotonic()-start,2)
    details['integrated_geometry_pass']=(not details['sources_changed_during_build']
        and not any(s['unresolved_intersections'] for s in states.values())
        and all(s['step_readback']['passed'] for s in states.values()))
    (OUT/'engineering-manifest.json').write_text(json.dumps(details,indent=2)+'\n',encoding='utf-8')
    print('INTEGRATED_GEOMETRY_PASS',details['integrated_geometry_pass'],flush=True)
    return 0 if details['integrated_geometry_pass'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
