"""Static solids, exact flat regeneration, and continuous service-route checks."""
from pathlib import Path
import hashlib,importlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
sys.path.insert(0,str(SOURCE))
from cad_helpers import validate,plate,bbox,intersection_volume,pipe
from sweep_checks import translation_segment,rotation_segment
from water_completion import HATCHES,LID_TOP,hatch_service_model
import service_finish as service

def strainer_paths(stored):
    current={p.id:p.shape for p in stored.parts if not p.id.startswith('I_STRAINER_TOP_BOLT_')}
    routes=[]
    for i in (1,2):
        k='I_STRAINER_TOP_'+str(i);moving={k:current.pop(k)};route={'name':'STRAINER_TOP_'+str(i),'segments':[]}
        r=translation_segment(moving,current,(0,0,20));route['segments'].append(r);moving={k:s.translate((0,0,20)) for k,s in moving.items()}
        cy=895.5 if i==1 else 965.5;axis=(1088.5,cy,640)
        r=rotation_segment(moving,current,axis,'Z',0,90,max_step_deg=1);route['segments'].append(r)
        moving={k:s.rotate(axis,(axis[0],axis[1],641),90) for k,s in moving.items()}
        # The carrier's own free25mm strip holds both bridges, independently
        # of loose bed/tool fasteners in the separate hardware bin.
        for delta in ((-73.5,0,0),(0,934.5-cy,0),(0,0,-140 if i==1 else -137)):
            r=translation_segment(moving,current,delta);route['segments'].append(r);moving={k:s.translate(delta) for k,s in moving.items()}
        current.update(moving);routes.append(route)
    k='I_BUY_STRAINER';moving={k:current.pop(k)};r=translation_segment(moving,current,(0,0,120))
    routes.append({'name':'STRAINER_LIFT','segments':[r]})
    return routes

def main():
    verifier_sha_before=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    name=sys.argv[sys.argv.index('--builder')+1] if '--builder' in sys.argv else 'build_revh'
    module=importlib.import_module(name)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    m,details=module.build_model()
    if not any(p.id=='I_DRAIN_TAIL' for p in m.parts):details=service.extend_router_model(m)
    stored=module.stored_model(m)
    report={'builder':name,'source_hashes':hashes,'states':{},'paths':[],'definition':details,'verifier_file':str(Path(__file__).relative_to(ROOT)),'verifier_sha256_before':verifier_sha_before}
    if '--strainer-only' in sys.argv:
        report['paths']=strainer_paths(stored)
        report['scope']='Focused continuous strainer service paths; no static states or other service paths repeated.'
        report['verifier_sha256_after']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        final={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
        report['source_changes']={k:v for k,v in final.items() if hashes.get(k)!=v}
        report['passed']=all(s['status']=='CLEAR' for p in report['paths'] for s in p['segments']) and not report['source_changes'] and report['verifier_sha256_after']==verifier_sha_before
        Path(__file__).with_name('strainer-focused-'+name+'.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print('FOCUSED',report['passed'],[(p['name'],[(s['status'],len(s['candidates'])) for s in p['segments']]) for p in report['paths']],flush=True)
        return 0 if report['passed'] else 2
    for label,model in [('router',m),('stored',stored),('tail_parked',service.tail_service_model(stored)),('hatches_open',hatch_service_model(stored))]:
        r=validate(model);report['states'][label]={'part_count':r['part_count'],'unresolved':r['unresolved_intersections']}
        print(label,r['part_count'],'clashes',len(r['unresolved_intersections']),flush=True)
    flats=[]
    for p in m.parts:
        if (p.id.startswith(('I_DRAIN_','I_SUCTION_','I_REFILL_','I_STRAINER_','I_HOSE_','I_CABINET_','I_CAB_')) or p.id=='PUMP_TRAY') and p.flat:
            f=p.flat;s=plate(f['outline'],f['thickness_mm'],f['holes'],f['slots'],f['internal'])
            dv=abs(s.Volume()-p.local.Volume());assert dv<1e-6,(p.id,dv)
            flats.append({'id':p.id,'volume_delta_mm3':dv})
    report['flat_checks']=flats
    current={p.id:p.shape for p in stored.parts if not any(p.id.startswith('H_WT_'+h['tag']+'_BOLT_') for h in HATCHES)}
    for h in HATCHES:
        moving={k:current.pop(k) for k in ['H_WT_'+h['tag']+'_COVER','H_WT_'+h['tag']+'_PULL_TAB']};fixed=current.copy()
        route={'name':h['tag']+'_HATCH','segments':[]};x,y,w,d=h['cover'];axis=(x,h['park_y'],LID_TOP+52)
        for label,delta in [('lift',(0,0,50)),('front',(0,h['park_y']-y,0))]:
            r=translation_segment(moving,fixed,delta);route['segments'].append({'name':label,**r});moving={k:s.translate(delta) for k,s in moving.items()}
        r=rotation_segment(moving,fixed,axis,'X',0,90,max_step_deg=1);route['segments'].append({'name':'swing',**r})
        moving={k:s.rotate(axis,(x+1,axis[1],axis[2]),90) for k,s in moving.items()}
        r=translation_segment(moving,fixed,(0,0,-49));route['segments'].append({'name':'seat',**r});moving={k:s.translate((0,0,-49)) for k,s in moving.items()}
        current.update(moving);report['paths'].append(route)
        print(route['name'],[(s['name'],s['status'],len(s['candidates'])) for s in route['segments']],flush=True)
    # Empty pan/tank, all four spool fasteners already removed. The gasket
    # follows the loose tail, avoiding an unsupported assumption of adhesion.
    current={p.id:p.shape for p in stored.parts if not p.id.startswith(('I_DRAIN_BOLT_','I_DRAIN_NUT_','I_DRAIN_WASHER_'))}
    moving={k:current.pop(k) for k in ('I_DRAIN_TAIL','I_DRAIN_TAIL_FLANGE','I_DRAIN_TAIL_GASKET')}
    route={'name':'GRAVITY_TAIL_TO_PARK','segments':[]}
    for label,delta in [('unseat',(0,0,-6)),('forward',(0,-90,0)),('raise',(0,0,40)),('right',(140,0,0)),('rearward',(0,90,0)),('seat',(0,0,-47.904))]:
        r=translation_segment(moving,current,delta)
        # The AABB encloses empty corners outside the round tail. For this
        # coaxial downward insertion, an exact swept annulus is available.
        # Test that continuous solid against every candidate, never omit a pair.
        if label=='seat' and r['candidates']:
            remaining=[];proofs=[]
            for c in r['candidates']:
                if c['moving']=='I_DRAIN_TAIL':
                    b=bbox(moving[c['moving']]);sweep=pipe(b[5]-b[2]-delta[2],33.4,26.6).translate(((b[0]+b[3])/2,(b[1]+b[4])/2,b[2]+delta[2]))
                    v=intersection_volume(sweep,current[c['fixed']]);proofs.append({'pair':[c['moving'],c['fixed']],'method':'Exact continuous coaxial translation swept annulus','intersection_mm3':v})
                    if v>1e-6:remaining.append(c)
                else:remaining.append(c)
            r['analytic_sweep_refinements']=proofs;r['candidates']=remaining
            if not remaining:r['status']='CLEAR'
        route['segments'].append({'name':label,**r});moving={k:s.translate(delta) for k,s in moving.items()}
    current.update(moving);report['paths'].append(route)
    print(route['name'],[(s['name'],s['status'],len(s['candidates'])) for s in route['segments']],flush=True)
    # Basket and cover move together after the tail is parked. Raise until its
    # bottom clears the lid; hand-held service stance is not a new cutting pose.
    moving={p.id:current.pop(p.id) for p in stored.parts if p.group=='catch_basket'}
    r=translation_segment(moving,current,(0,0,103));report['paths'].append({'name':'BASKET_LIFT_AFTER_TAIL_PARK','segments':[r]})
    print('BASKET',r['status'],len(r['candidates']),flush=True)
    # Fixed carrier legs remain; remove bolts/top bridges, then lift the whole
    # bought strainer120mm. Hoses are disconnected at their field-fit unions.
    service_paths=strainer_paths(stored);report['paths'].extend(service_paths)
    print('STRAINER',[(p['name'],[s['status'] for s in p['segments']]) for p in service_paths],flush=True)
    # Radius-preserving solid routes enlarged2mm radially bound small routing
    # tolerance and include the hollow hose's core conservatively.
    tolerance=[]
    for k,points,arcs in [('I_REFILL_PRESSURE_HOSE',service.PRESSURE_POINTS,service.PRESSURE_ARCS),('I_SUCTION_HOSE',service.SUCTION_POINTS,service.SUCTION_ARCS)]:
        inflated,_=service._route(points,arcs,diameter=19.9,inside=0);a=bbox(inflated);hits=[]
        for p in stored.parts:
            if p.id==k:continue
            b=bbox(p.shape)
            if all(min(a[j+3],b[j+3])-max(a[j],b[j])>1e-6 for j in range(3)):
                v=intersection_volume(inflated,p.shape)
                if v>1e-6:hits.append({'id':p.id,'intersection_mm3':v})
        tolerance.append({'hose':k,'radial_allowance_mm':2,'intersections':hits})
    report['hose_tolerance_checks']=tolerance
    # Gland plates lower12mm in the empty front bay, electrically isolated;
    # cables must first be disconnected/unthreaded. No cable loop is assumed.
    for tag in ('MAINS','SIGNAL'):
        omitted=[p.id for p in m.parts if p.id.startswith('I_CAB_GLAND_'+tag+'_BOLT_') or p.id.startswith('I_CAB_GLAND_'+tag+'_NUT_')]
        names=['I_CAB_GLAND_'+tag,'I_CAB_GLAND_GASKET_'+tag]
        fixed={p.id:p.shape for p in m.parts if p.id not in omitted+names};moving={k:m.find(k).shape for k in names}
        r=translation_segment(moving,fixed,(0,0,-12));report['paths'].append({'name':tag+'_GLAND_SERVICE','segments':[r]})
    for p in report['paths']:
        for s in p['segments']:
            b=s['swept_enclosing_bounds_mm'];s['within_machine_plan']=b[0]>=0 and b[1]>=0 and b[3]<=1150 and b[4]<=1450
    final={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    report['source_changes']={k:v for k,v in final.items() if hashes.get(k)!=v}
    report['verifier_sha256_after']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['verifier_changed_during_run']=report['verifier_sha256_after']!=verifier_sha_before
    report['limits']=['Purchased allocations do not establish omitted product shape or port fit.','No human hand envelope or tolerance/deformation allowance in nominal positive-volume path proof.','Hose paths are nominal radius-preserving routing definitions; field connections, movement/flex and 2mm tolerance sweep must be separately accepted.','No cabinet hinge/lock/thermal certification.']
    report['passed']=not any(s['unresolved'] for s in report['states'].values()) and all(s['status']=='CLEAR' and s['within_machine_plan'] for p in report['paths'] for s in p['segments']) and not report['source_changes'] and not any(t['intersections'] for t in tolerance) and not report['verifier_changed_during_run']
    target=Path(__file__).with_name('verification-'+name+'.json');target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT',report['passed'],target,flush=True)
    return 0 if report['passed'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
