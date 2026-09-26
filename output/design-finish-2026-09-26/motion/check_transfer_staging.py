"""Prove existing panel1/beam1 temporary preparation for split-head transfer.

All paths use the complete selected Rev I model. Small fasteners, human grips,
cleanliness, restraint strength and head-component paths are separate checks.
"""
from pathlib import Path
import hashlib,json,math,os,sys

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
OLD=ROOT/'output/cad-repair-2026-09-25'
sys.path[:0]=[str(SOURCE),str(OLD),str(ROOT/'output/design-finish-2026-09-26/structure')]
import cadquery as cq
import build_revi as builder
import bed_cassettes as bc
import bed_completion as h
from build_revg import clone_model
from cad_helpers import bbox,place,validate,intersection_volume
from check_spoil_transfer import continuous_segment
from check_reinforced_paths import transform,bounds_speed,swept_box

OUT=Path(__file__).with_name('transfer-staging-verification.json')
TABLE_Y=890.5
TABLE_TOP=940.8
TABLE_CLAMPS=(8,9,12,13)


def panel_ids(router):
    return [p.id for p in router.parts if bc._PLACEMENTS.get(p.id,('',-1))[:2]==('panel',0)]


def router_tool_id(ident):
    return ident in ('TOOL_SPINDLE_65x259','TOOL_SPLIT_CLAMP_REAR','TOOL_SPLIT_CLAMP_FRONT') or ident.startswith(('TOOL_CLAMP_MOUNT_','TOOL_CLAMP_PINCH_'))


def hashes():
    paths=list(SOURCE.glob('*.py'))+[Path(__file__),OLD/'check_spoil_transfer.py',
        ROOT/'output/design-finish-2026-09-26/structure/check_reinforced_paths.py']
    return {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def build_conversion_start(router):
    """All boards and panels2..6 stored; panel1 and router remain installed."""
    result=builder.stored_model(router)
    h.prepare_panel_handling_model(result)
    for p in result.parts:
        rec=bc._PLACEMENTS.get(p.id,('',-1));kind=rec[0]
        if kind in ('beam','beam_bolt','front_seat','front_seat_bolt') or rec[:2]==('panel',0) or router_tool_id(p.id):
            p.shape=router.find(p.id).shape
    return result


def place_table(model,router,clamp=True):
    for p in model.parts:
        rec=bc._PLACEMENTS.get(p.id,('',-1))
        if rec[:2]==('panel',0):p.shape=router.find(p.id).shape.translate((0,TABLE_Y-76.5,0))
        elif clamp and rec[0]=='clamp' and rec[1] in TABLE_CLAMPS:p.shape=router.find(p.id).shape
    return model


def build_beam_on_second_model(router,front_seats_stored=True,keepers=True):
    """Exact router-removal phase: table fitted, beam1 on beam2, tool mounted."""
    model=place_table(build_conversion_start(router),router)
    for p in model.parts:
        rec=bc._PLACEMENTS.get(p.id,('',-1))
        if rec[:2]==('beam',0):
            p.shape=router.find(p.id).shape.translate(tuple(-v for v in rec[2])).rotate((0,0,0),(1,0,0),90).translate((113,517.9,920.8))
        elif (rec[0]=='beam_bolt' and rec[1]//2==0) or (front_seats_stored and rec[0] in ('front_seat','front_seat_bolt')):
            p.shape=bc.transformed_to_storage(router.find(p.id))
    if keepers:h.set_temporary_capture(model,True)
    return model


def place_temporary_beam(model,router,lock=True):
    """Put beam1 in empty front/lower slot, with existing single-beam locks."""
    for p in model.parts:
        rec=bc._PLACEMENTS.get(p.id,('',-1))
        if rec[:2]==('beam',0):
            local=router.find(p.id).shape.translate(tuple(-v for v in rec[2]))
            p.shape=local.rotate((0,0,0),(1,0,0),90).translate((113,78.8,585))
        elif rec[0]=='beam_bolt' and rec[1]//2==0 or rec[0] in ('front_seat','front_seat_bolt'):
            p.shape=bc.transformed_to_storage(router.find(p.id))
    if lock:
        for side,x in ((1,123),(2,1027)):
            for stem,z in (('BOLT',513.4),('TOP_WASHER',641.8),('LOW_WASHER',577.4),('NUT',572.4)):
                p=model.find(f'H_STACK_LOCK_{stem}_{side}_1')
                p.shape=place(p.local,(x,25.4,z))
    return model


def build_staging_model(router):
    """Exact head-transfer fixture state, constructed without any CAD edits."""
    result=place_table(build_conversion_start(router),router)
    parked=builder.stored_model(router)
    for p in result.parts:
        if router_tool_id(p.id):p.shape=parked.find(p.id).shape
    return place_temporary_beam(result,router)


def solid_difference(a,b):
    return a.cut(b).Volume()+b.cut(a).Volume()


def main():
    before=hashes();router,_=builder.build_model();start=build_conversion_start(router)
    report={'builder':'build_revi','source_sha256':before,'states':{},'paths':[],
        'scope':__doc__,
        'preconditions':[
            'Machine isolated; no stock or actual torch; gantry parked rear/high; router remains mounted until beam1 is safely captured on beam2.',
            'Six bare boards and panels6..2 follow normal ordered routes into storage. Panel1 is LAST and still installed. All release screws/clamps are already in trays. Four beams and front seats remain installed.',
            'Panel rods remain installed; top bars staged using separately checked restraint paths. Spoilboard guard closed. Stack bolts parked.',
            'Move panel1 into the normal empty rear-left panel5 location on beams3/4 using the listed three-segment path. Fit four existing left clamp sets on beams3/4 before handling head pieces; no additional panel or board is introduced.',
            'Temporary table is clean/dry. Drain pan before conversion. Verify actual support and clamp bearing. This is gravity staging for at most3kg of head parts; no machining or standing rating. Existing qualified panel-clamp procedure applies.',
            'After beam1 rests on beam2, fit both temporary keeper fixtures before removing front seats and transferring router parts. Router-transfer proof is separate. Remove keepers before lifting beam1; their separate routes are checked in structural evidence.',
            'After beam1 reaches the front/lower slot, fit both front-row stack locks using the stated single-beam heights. Small fastener motions and hand access are excluded.',
            'After head transfer, remove those locks, restore beam1/front seats by the reverse route, remove the four table clamps to their normal tray locations, and move panel1 to its normal first rack slot. Restore rack top bars. Only then use the normal four-beam storage sequence.'],
        'temporary_panel':{'panel':1,'xy_mm':[73.5,TABLE_Y,573.5,TABLE_Y+397],'extrusion_bottom_z_mm':920.8,'support_top_z_mm':TABLE_TOP,
            'beam_support_y_mm':[[890.5,910.9],[1273.6,1287.5]],'beam1_temporary_gap_mm':TABLE_Y-489.9,
            'clamp_indices_zero_based':TABLE_CLAMPS,'front_clamp_overlap_mm':10,'rear_clamp_overlap_mm':3.5,
            'max_head_parts_kg':3,'qualification':'Normal rear-bay support and standard clamp bearing. Actual joint/preload qualification remains in structure/JOINTS.md; no new torque or operational load rating.'},
        'temporary_beam_lock':{'centers_xy_mm':[[123,25.4],[1027,25.4]],'bolt_tip_z_mm':513.4,'top_washer_z_mm':641.8,'lower_washer_z_mm':577.4,'nut_z_mm':572.4,
            'hardware':'Existing front-row M6x130 FULL THREAD screws, two washers and nut per side. Rear-row locks remain parked.'}}
    def save():OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def state(name,m):
        v=validate(m);report['states'][name]={'part_count':len(m.parts),'clashes':v['unresolved_intersections']}
        print('STATE',name,len(v['unresolved_intersections']),v['unresolved_intersections'][:3],flush=True);save()
    path_functions={}
    def run(name,shape,fixed,ops):
        records=[];functions=[]
        for label,op in ops:
            if op[0]=='CALLBACK':fn,speed,curve,sweep=op[1:]
            else:
                speed,curve=bounds_speed(shape,op);sweep=swept_box(shape,op)
                fn=lambda t,s=shape,o=op:transform(s,o,t)
            r=continuous_segment(fn,fixed,speed,curve)
            r['start_symmetric_difference_mm3']=solid_difference(fn(0),shape) if op[0]=='CALLBACK' else 0.0
            functions.append((label,fn,speed,curve,sweep))
            r['swept_bounds_mm']=sweep;r['inside_frame_footprint']=sweep[0]>=-1e-6 and sweep[1]>=-1e-6 and sweep[3]<=1150+1e-6 and sweep[4]<=1450+1e-6
            records.append({'name':label,**r});shape=fn(1)
            print(name,label,r['status'],r['failures'][:3],flush=True)
            report['paths']=[p for p in report['paths'] if p['name']!=name]+[{'name':name,'segments':records}];save()
        rec=report['paths'][-1];rec['passed']=all(r['status']=='CLEAR' and r['inside_frame_footprint'] and r['start_symmetric_difference_mm3']<1e-5 for r in records)
        path_functions[name]=functions
        return shape
    def reverse_ops(name):
        return [('reverse_'+label,('CALLBACK',lambda t,f=fn:f(1-t),speed,curve,sweep))
                for label,fn,speed,curve,sweep in reversed(path_functions[name])]
    state('boards_panels2to6_stored_router_and_panel1_installed',start)
    table_ids=panel_ids(router)
    panel=cq.Compound.makeCompound([router.find(i).shape for i in table_ids])
    fixed={p.id:p.shape for p in start.parts if p.id not in table_ids}
    final=run('panel1_to_rear_table',panel,fixed,[('lift_panel1_60',('T',(0,0,60))),
        ('move_panel1_to_rear_bay',('T',(0,TABLE_Y-76.5,0))),('lower_panel1_to_beams3and4',('T',(0,0,-60)))])
    staged_table=place_table(clone_model(start),router)
    table_shape=cq.Compound.makeCompound([staged_table.find(i).shape for i in table_ids])
    report['panel_table_symmetric_difference_mm3']=solid_difference(final,table_shape)
    state('panel1_rear_table_router_still_installed',staged_table)
    # Full compound beam1 includes sleeves, shoes, locators and stacking pads.
    ids=[p.id for p in router.parts if bc._PLACEMENTS.get(p.id,('',-1))[:2]==('beam',0)]
    moving=cq.Compound.makeCompound([router.find(i).shape for i in ids])
    fixed={p.id:p.shape for p in staged_table.parts if p.id not in ids}
    for p in router.parts:
        rec=bc._PLACEMENTS.get(p.id,('',-1))
        if rec[0]=='beam_bolt' and rec[1]//2==0:fixed[p.id]=bc.transformed_to_storage(p)
    ops=[('lift_clear_of_seats',('T',(0,0,80))),('move_lifted_beam_to_front',('T',(0,39.2,0))),
         ('rotate_on_side_above_front',('R',(113,78.8,922),(114,78.8,922),90)),
         ('raise_for_temporary_park_approach',('T',(0,0,18.8))),('move_above_second_beam',('T',(0,439.1,0))),
         ('lower_onto_second_beam',('T',(0,0,-20)))]
    parked=run('beam1_rest_on_beam2',moving,fixed,ops)
    state('router_removal_phase_beam1_captured_on_beam2',build_beam_on_second_model(router))
    router_parked=builder.stored_model(router)
    for p in router.parts:
        if bc._PLACEMENTS.get(p.id,('',))[0] in ('front_seat','front_seat_bolt'):fixed[p.id]=bc.transformed_to_storage(p)
        if router_tool_id(p.id):fixed[p.id]=router_parked.find(p.id).shape
    final=run('beam1_to_front_lower_slot',parked,fixed,[('lift_from_temporary_park',('T',(0,0,20))),
        ('return_on_side_to_front_portal',('T',(0,-439.1,0))),('lower_onto_front_shelf',('T',(0,0,-355.8)))])
    target=build_staging_model(router)
    expected=cq.Compound.makeCompound([target.find(i).shape for i in ids])
    report['beam_final_symmetric_difference_mm3']=solid_difference(final,expected)
    state('panel1_rear_table_beam1_locked_front_lower',target)
    # The head has changed position, so restoration is independently checked
    # against the actual installed hardware, not inferred from reversibility.
    restored,_=builder.plasma_hardware_model(target)
    for p in restored.parts:
        if p.id.startswith('H_STACK_LOCK_'):p.shape=router.find(p.id).shape
    fixed={p.id:p.shape for p in restored.parts if p.id not in ids}
    parked=run('restore_beam1_to_second_beam',expected,fixed,reverse_ops('beam1_to_front_lower_slot'))
    for p in restored.parts:
        if bc._PLACEMENTS.get(p.id,('',))[0] in ('front_seat','front_seat_bolt'):
            p.shape=router.find(p.id).shape;fixed[p.id]=p.shape
    returned=run('restore_beam1_to_seats',parked,fixed,reverse_ops('beam1_rest_on_beam2'))
    report['beam_return_symmetric_difference_mm3']=solid_difference(returned,moving)
    for p in restored.parts:
        rec=bc._PLACEMENTS.get(p.id,('',-1))
        if rec[:2]==('beam',0) or (rec[0]=='beam_bolt' and rec[1]//2==0):p.shape=router.find(p.id).shape
    state('installed_head_beams_restored_panel1_rear_table',restored)
    for p in restored.parts:
        rec=bc._PLACEMENTS.get(p.id,('',-1))
        if rec[0]=='clamp' and rec[1] in TABLE_CLAMPS:p.shape=bc.transformed_to_storage(router.find(p.id))
    fixed={p.id:p.shape for p in restored.parts if p.id not in table_ids}
    returned=run('panel1_table_to_normal_rack_with_head_installed',table_shape,fixed,[
        ('lift_panel1_60',('T',(0,0,60))),('panel1_to_front_rotation_datum',('T',(251.5,20-TABLE_Y,0))),
        ('rotate_panel1_upright',('R',(325,20,980.8),(326,20,980.8),90)),
        ('lower_panel1_in_front',('T',(0,0,-775.8))),('panel1_to_first_slot',('T',(0,7,0))),('lower_panel1_into_slot',('T',(0,0,-30)))])
    expected_panel=cq.Compound.makeCompound([bc.transformed_to_storage(router.find(i)) for i in table_ids])
    report['panel_storage_symmetric_difference_mm3']=solid_difference(returned,expected_panel)
    for p in restored.parts:
        if p.id in table_ids:p.shape=bc.transformed_to_storage(router.find(p.id))
    state('installed_head_boards_panels_stored_beams_installed',restored)
    report['sources_unchanged']=before==hashes()
    report['passed']=report['sources_unchanged'] and not any(s['clashes'] for s in report['states'].values()) and all(p['passed'] for p in report['paths']) and max(report[k] for k in ('panel_table_symmetric_difference_mm3','beam_final_symmetric_difference_mm3','beam_return_symmetric_difference_mm3','panel_storage_symmetric_difference_mm3'))<1e-5
    save();print('TRANSFER_STAGING',report['passed'],flush=True)
    return 0 if report['passed'] else 2


if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
