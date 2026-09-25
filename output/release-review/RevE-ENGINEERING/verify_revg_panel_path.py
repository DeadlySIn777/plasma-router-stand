"""Conservative ordered paths for six router panels; not whole-bed conversion.

Precondition: source gantry is parked; router spindle/clamps are in their modeled
storage locations; all spoilboards, spoilboard screws/top-slot nuts and16panel-clamp sets have
already been removed and stored. Their own handling paths are NOT proved here.
All four beams and their draw bolts remain installed throughout these paths.
"""
from pathlib import Path
import hashlib,json,os,sys,time,traceback

SOURCE=Path(__file__).resolve().parent
OUT=SOURCE.parents[1]/'cad-repair-2026-09-25'/'motion'/'revg-panel-path.json'


def hashes():
    return {name:hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() for name in (
        'verify_revg_panel_path.py','sweep_checks.py','build_revg.py','build_reve_engineering.py',
        'bed_cassettes.py','motion_details.py','cad_helpers.py','frame_details.py',
        'controls_packaging.py','sensor_mounts.py','tool_parking.py','water_system.py','water_accessories.py')}


def main():
    from build_revg import build_model,store_router_tool
    import bed_cassettes as bed
    from cad_helpers import bbox
    from sweep_checks import translation_segment,rotation_segment
    started=time.monotonic();source_hashes=hashes()
    model,_=build_model()
    # Reference the original machine, before any handling/storage transform;
    # an erroneous storage placement must never enlarge the allowed footprint.
    bounds=[bbox(p.shape) for p in model.parts]
    footprint=[min(bb[0] for bb in bounds),min(bb[1] for bb in bounds),
               max(bb[3] for bb in bounds),max(bb[4] for bb in bounds)]
    model=store_router_tool(model)
    for part in model.parts:
        rec=bed._PLACEMENTS.get(part.id)
        if rec and rec[0] in ('spoil','spoil_bolt','spoil_nut','clamp'):
            part.shape=bed.transformed_to_storage(part)
    report={'scope':__doc__,'status':'RUNNING','sources_sha256':source_hashes,
            'reference_machine_footprint_xy_mm':footprint,'panel_order':[6,5,4,3,2,1],
            'panels':[],'caveats':['This does not prove beam extraction or the full conversion sequence.',
                'No hands, fingers, retained loose-nut behavior, cable handling or manufacturing tolerance envelope is represented.',
                'CLEAR excludes positive-volume interference above1e-6 mm3 for represented nominal solids; zero-gap contact is not a clearance allowance.']}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    def save():
        report['elapsed_seconds']=round(time.monotonic()-started,2)
        OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    save()
    for index in (5,4,3,2,1,0):
        parts=[p for p in model.parts if bed._PLACEMENTS.get(p.id,('',-1))[0:2]==('panel',index)]
        moving={p.id:p.shape for p in parts}
        fixed={p.id:p.shape for p in model.parts if p.id not in moving}
        datum=bed._PLACEMENTS[parts[0].id][2]
        panel={'panel':index+1,'moving_parts':list(moving),'segments':[]}
        def record(name,result):
            b=result['swept_enclosing_bounds_mm']
            margins=[b[0]-footprint[0],b[1]-footprint[1],footprint[2]-b[3],footprint[3]-b[4]]
            result['footprint_margin_xy_mm']=margins
            result['footprint_proved']=min(margins)>=0
            panel['segments'].append({'name':name,**result})
            print('Panel',index+1,name,result['status'],'candidates',len(result['candidates']),
                  'footprint',result['footprint_proved'],flush=True)
        def translate(name,delta):
            nonlocal moving
            result=translation_segment(moving,fixed,delta)
            record(name,result)
            moving={ident:shape.translate(delta) for ident,shape in moving.items()}
        translate('lift60',(0,0,60))
        translate('translate_to_front_rotation_datum',(325-datum[0],20-datum[1],0))
        axis_origin=(325,20,980.8)
        result=rotation_segment(moving,fixed,axis_origin,'X',0,90,max_step_deg=2)
        record('rotate90_about_X',result)
        moving={ident:shape.rotate(axis_origin,(326,20,980.8),90) for ident,shape in moving.items()}
        translate('lower_front_drop_lane',(0,0,205-980.8))
        translate('slide_rearward_to_storage_slot',(0,bed.PANEL_STORE_Y[index],0))
        translate('lower30_into_slot',(0,0,-30))
        final_deltas=[]
        for part in parts:
            expected=bed.transformed_to_storage(part)
            eb=bbox(expected);ab=bbox(moving[part.id])
            error=max(abs(a-b) for a,b in zip(eb,ab))
            assert error<1e-6,(part.id,error)
            final_deltas.append(error)
            part.shape=moving[part.id]
        panel['final_storage_max_bounds_error_mm']=max(final_deltas)
        panel['path_proved']=all(s['status']=='CLEAR' and s['footprint_proved'] for s in panel['segments'])
        report['panels'].append(panel);save()
    after=hashes()
    report['sources_changed_during_run']={name:{'before':value,'after':after[name]}
        for name,value in source_hashes.items() if value!=after[name]}
    report['all_panel_paths_proved']=all(p['path_proved'] for p in report['panels'])
    report['status']='STALE' if report['sources_changed_during_run'] else (
        'CLEAR' if report['all_panel_paths_proved'] else 'CANDIDATE_NOT_PROVEN')
    save();print('Panel path:',report['status'],report['elapsed_seconds'],'seconds',flush=True)
    return 0 if report['status']=='CLEAR' else 2


if __name__=='__main__':
    try:code=main()
    except Exception:traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
