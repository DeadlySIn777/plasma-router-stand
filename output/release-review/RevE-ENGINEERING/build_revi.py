"""Rev I: structural, service and motion completion on the frozen Rev H base."""
from pathlib import Path
import hashlib,importlib,json,os,sys,time
import build_revh as previous
from cad_helpers import export

SOURCE=Path(__file__).resolve().parent
OUT=SOURCE.parent/'RevI-CAD'
EXTENSIONS=('structure_finish','service_finish','motion_finish')


def build_model(with_motion=True,gantry_y=1275,head_x=575,z_lift=100):
    model,baseline=previous.build_model(with_motion=with_motion,gantry_y=gantry_y,head_x=head_x,z_lift=z_lift)
    details={'revision':'I','status':'INTEGRATED ENGINEERING REVIEW - PHYSICAL INTERFACES AND COMMISSIONING REMAIN',
             'baseline_rev_h_metadata':baseline,
             'baseline_metadata_scope':'Historical base; current extension definitions and procedures supersede changed details.',
             'architecture_assumption':'Current design uses manual small panels, beams and separate spoilboards stored inside the chassis. This is an engineering choice under the footprint constraint, not a claim of automatic bed handling or an owner-selected effort preference.'}
    for name in EXTENSIONS:
        if name=='motion_finish' and not with_motion:continue
        module=importlib.import_module(name)
        details[name]=module.extend_router_model(model)
    # Historical holds describe mechanisms absent in G/H. Retain the measured
    # release gates, but do not call the new modeled mechanism nonexistent or
    # treat a design choice as an unrequested permission gate.
    model.holds[:]=[h for h in model.holds if not h.startswith('Manual panel conversion is the working architecture, pending')]
    model.holds[:]=[
        'The floating/breakaway hardware is modeled; actual torch barrel, nozzle datum, insert bore, lead/tether, release force and operating compatibility still require qualification.'
        if h.startswith('The owned torch barrel/clamping zone') else h for h in model.holds]
    return model,details


def stored_model(source):
    stored=previous.stored_model(source)
    for name in EXTENSIONS:
        module=importlib.import_module(name)
        if hasattr(module,'extend_stored_model'):module.extend_stored_model(stored,source)
    return stored


def plasma_hardware_model(stored,**kwargs):
    from motion_finish import plasma_hardware_model as make_plasma
    return make_plasma(stored,**kwargs)


def write_mesh(model,name):
    old=previous.OUT
    try:previous.OUT=OUT;previous.write_mesh(model,name)
    finally:previous.OUT=old


def main():
    started=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    router,details=build_model();stored=stored_model(router)
    plasma,details['plasma_hardware_review']=plasma_hardware_model(stored)
    states={}
    for name,model,individual in [('RevI_ROUTER',router,True),('RevI_BED_STORED',stored,False),('RevI_PLASMA_HARDWARE',plasma,False)]:
        print(name,len(model.parts),'parts',flush=True)
        result=export(model,OUT,name,individual=individual)
        states[name]={'part_count':result['part_count'],'step_readback':result['step_readback'],
                      'unresolved_intersections':result['unresolved_intersections']}
        print(name,'clashes',len(result['unresolved_intersections']),flush=True)
        if result['unresolved_intersections']:print(json.dumps(result['unresolved_intersections'],indent=2),flush=True)
        write_mesh(model,name)
    after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    details.update(state_checks=states,source_sha256=after,
                   sources_changed_during_build={n:v for n,v in before.items() if after.get(n)!=v},
                   holds=sorted(set(router.holds)),elapsed_seconds=round(time.monotonic()-started,2))
    details['integrated_geometry_pass']=(not details['sources_changed_during_build'] and all(
        not s['unresolved_intersections'] and s['step_readback']['passed'] for s in states.values()))
    (OUT/'engineering-manifest.json').write_text(json.dumps(details,indent=2)+'\n',encoding='utf-8')
    print('INTEGRATED_GEOMETRY_PASS',details['integrated_geometry_pass'],flush=True)
    return 0 if details['integrated_geometry_pass'] else 2


if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
