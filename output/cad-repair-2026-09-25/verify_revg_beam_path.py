"""Continuous ordered transfer proof for the four Rev G bed crossbeams.

Boards, panels, panel clamps and the router tool are already stored. Beam bolts
and front seats are transferred as explicit state changes; their small-part
handling paths, fingers and operator reach are NOT verified here.
"""
from pathlib import Path
import hashlib,json,math,os,sys
SOURCE=Path(__file__).resolve().parents[1]/'release-review'/'RevE-ENGINEERING'
sys.path.insert(0,str(SOURCE))
import cadquery as cq
from cad_helpers import bbox,intersection_volume
from build_revg import build_model,store_router_tool
import bed_cassettes as bc
from check_spoil_transfer import continuous_segment

def hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}

def main():
    initial_hashes=hashes()
    source,details=build_model();source=store_router_tool(source)
    fixed={p.id:p.shape for p in source.parts}
    for p in source.parts:
        kind=bc._PLACEMENTS.get(p.id,('',))[0]
        if kind and kind not in ('beam','beam_bolt','front_seat','front_seat_bolt'):
            fixed[p.id]=bc.transformed_to_storage(p)
    records=[];temporary={};all_poses=[]
    for i in range(4):
        moving=[p for p in source.parts if bc._PLACEMENTS.get(p.id,('',-1))[:2]==('beam',i)]
        datum=bc._PLACEMENTS[moving[0].id][2]
        local_parts={p.id:p.shape.translate(tuple(-v for v in datum)) for p in moving}
        local=cq.Compound.makeCompound(list(local_parts.values()))
        installed=cq.Compound.makeCompound([p.shape for p in moving])
        for p in moving:fixed.pop(p.id)
        for p in source.parts:
            record=bc._PLACEMENTS.get(p.id,('',-1))
            if record[0]=='beam_bolt' and record[1]//2==i:
                fixed[p.id]=bc.transformed_to_storage(p)
        phases=[]
        def run(name,fn,speed,curve=0):
            result=continuous_segment(fn,fixed,speed,curve)
            phases.append((name,result))
            all_poses.extend(bbox(fn(t)) for t in (0,.25,.5,.75,1))
            if result['status']!='CLEAR':
                print(json.dumps({'beam':i+1,'phase':name,'failures':result['failures']}),flush=True)
            return fn(1)
        lifted=run('lift_clear_of_seats',lambda t:installed.translate((0,0,80*t)),80)
        front_flat=run('move_lifted_beam_to_front',lambda t:lifted.translate((0,(78.8-datum[1])*t,0)),abs(78.8-datum[1]))
        bb=bbox(local);radius=max(math.hypot(y,z) for y in (bb[1],bb[4]) for z in (bb[2],bb[5]))
        side_fn=lambda t:local.rotate((0,0,0),(1,0,0),90*t).translate((113,78.8,922))
        side=run('rotate_on_side_above_front',side_fn,radius*math.pi/2,radius*(math.pi/2)**2)
        if i==0:
            raised=run('raise_for_temporary_park_approach',lambda t:side.translate((0,0,18.8*t)),18.8)
            over_second=run('move_above_second_beam',lambda t:raised.translate((0,(517.9-78.8)*t,0)),517.9-78.8)
            parked=run('lower_onto_second_beam',lambda t:over_second.translate((0,0,-20*t)),20)
            temporary={'bounds_mm':bbox(parked),'nominal_uniform_steel_center_of_volume_mm':list(parked.Center().toTuple()),
                       'support_contact_nominal_xy_mm':[113,453.1,1037,489.9],
                       'status':'Nominal static resting contact only; no lateral restraint or human-access qualification.'}
            # The assembly is resting independently on beam 2 before the front
            # seat fasteners and plates leave their working locations.
            for p in source.parts:
                if bc._PLACEMENTS.get(p.id,('',))[0] in ('front_seat','front_seat_bolt'):
                    fixed[p.id]=bc.transformed_to_storage(p)
            up=run('lift_from_temporary_park',lambda t:parked.translate((0,0,20*t)),20)
            at_front=run('return_on_side_to_front_portal',lambda t:up.translate((0,(78.8-517.9)*t,0)),517.9-78.8)
            down=run('lower_in_open_front_portal',lambda t:at_front.translate((0,0,(588-940.8)*t)),940.8-588)
            rear=run('move_into_rear_lower_rack',lambda t:down.translate((0,90*t,0)),90)
            final=run('lower_onto_rear_shelf',lambda t:rear.translate((0,0,-3*t)),3)
        elif i==1:
            final=run('lower_onto_front_shelf',lambda t:side.translate((0,0,(585-922)*t)),922-585)
        elif i==2:
            down=run('lower_above_front_lower_beam',lambda t:side.translate((0,0,(644.8-922)*t)),922-644.8)
            rear=run('move_above_rear_lower_beam',lambda t:down.translate((0,90*t,0)),90)
            final=run('lower_onto_rear_stacking_pads',lambda t:rear.translate((0,0,-3*t)),3)
        else:
            final=run('lower_onto_front_stacking_pads',lambda t:side.translate((0,0,(641.8-922)*t)),922-641.8)
        fy,z=bc.BEAM_STORE[i]
        deltas=[]
        for p in moving:
            final_shape=local_parts[p.id].rotate((0,0,0),(1,0,0),90).translate((113,fy+78.8,z))
            official=bc.transformed_to_storage(p)
            deltas.append(max(abs(a-b) for a,b in zip(bbox(final_shape),bbox(official))))
            fixed[p.id]=final_shape
        final_expected=cq.Compound.makeCompound([fixed[p.id] for p in moving])
        final_delta=max(abs(a-b) for a,b in zip(bbox(final),bbox(final_expected)))
        records.append({'beam':i+1,'moving_components':len(moving),'phases':dict(phases),'stored_bounds_mm':bbox(final),'final_geometry_bounds_delta_mm':max([final_delta]+deltas)})
        print(json.dumps({'beam':i+1,'phases':{k:v['status'] for k,v in phases},'final_delta':final_delta}),flush=True)
    final_hashes=hashes()
    # The lift and frontward linear moves stay between their end coordinates.
    # During each X rotation the local Y/Z bounds are nonnegative, so Y stays
    # >=78.8-max_local_Z=0 and <=78.8+max_local_Y=135.6. X is unchanged.
    result={'scope':'Ordered geometry of beams 1,2,3,4 after all panels/boards/clamps and router tool are already stored. Small-part transfers, fingers, operator reach and temporary-park lateral restraint are excluded.',
            'source_sha256':initial_hashes,'sources_unchanged_during_check':initial_hashes==final_hashes,
            'method':'Exact B-rep midpoint minimum distance plus a conservative maximum point displacement; adaptive continuous subdivision, including already stored beams as obstacles.',
            'model_parts':len(source.parts),'temporary_park':temporary,'records':records,
            'analytic_xy_envelope_mm':[113,0,1037,1330.4],
            'footprint':'All prescribed geometry stays inside nominal frame X0..1150,Y0..1450; X never changes, quarter-turn Y bounds remain0..135.6, other XY moves are linear between contained endpoints.',
            'sampled_bounds_mm':[min(b[k] for b in all_poses) for k in range(3)]+[max(b[k+3] for b in all_poses) for k in range(3)]}
    result['pass']=initial_hashes==final_hashes and all(v['status']=='CLEAR' for r in records for v in r['phases'].values()) and max(r['final_geometry_bounds_delta_mm'] for r in records)<1e-5
    Path(__file__).with_name('beam-path-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['pass'],flush=True)
    return 0 if result['pass'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
