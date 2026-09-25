"""Rebuild the frame/water subset and verify FW02/FW03/FW05 repairs, without exporting release files."""
from pathlib import Path
import hashlib
import json
import math
import os
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent/'release-review'/'RevE-ENGINEERING'
sys.path.insert(0,str(ROOT))
from cad_helpers import *
from build_reve_engineering import normalized_add
import geometry_base as base
from frame_details import make_frame
from water_system import make_water
from water_accessories import make_water_accessories
from sensor_mounts import make_sensor_mounts, PAN_EMPTY_MIN_AS_BUILT_GAP
from controls_packaging import make_controls_packaging, TUBE, TWALL, STR_LEN, STR_HOLE_D, STR_HOLE_Y, CAP_V
from tool_parking import make_tool_parking
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

def distance(a,b):
    check=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped)
    check.Perform()
    assert check.IsDone()
    return check.Value()

def nearby_clashes(a, parts):
    bounds=bbox(a)
    result=[]
    for p in parts:
        other=bbox(p.shape)
        if not all(min(bounds[k+3],other[k+3])-max(bounds[k],other[k])>1e-5 for k in range(3)):
            continue
        volume=intersection_volume(a,p.shape)
        if volume>0.02:
            result.append({'id':p.id,'volume_mm3':volume})
    return result

def run():
    model=Model()
    for p in base.fixed:
        if p.group in ('main_frame','rail_cap'):
            q=normalized_add(model,p)
            if q.id=='MF_END_FRONT_UPPER':
                q.shape=q.shape.translate((0,0,100.8-679.2))
    details={}
    for name,fn in [('frame',make_frame),('water',make_water),('water_accessories',make_water_accessories),('sensors',make_sensor_mounts),('tool_parking',make_tool_parking),('cabinet',make_controls_packaging)]:
        details[name]=fn(model)
        print(name,len(model.parts),flush=True)

    evidence={'scope':'FW02 cabinet stringer bores, FW03 welded drip-shield definition and FW05 PAN_EMPTY floor clearance. Purchased interfaces and full-machine motion are not qualified by this check.',
              'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['controls_packaging.py','sensor_mounts.py','water_system.py']},
              'design_details':{key:details[key] for key in ['sensors','cabinet']},'stringers':[]}
    validation=validate(model)
    assert not validation['unresolved_intersections'],validation['unresolved_intersections']
    evidence['subset_validation']={key:validation[key] for key in ['part_count','broadphase_pairs','unresolved_intersections','documented_intersections']}
    original_volume=(TUBE**2-(TUBE-2*TWALL)**2)*STR_LEN
    expected_removed=2*2*TWALL*math.pi*(STR_HOLE_D/2)**2
    for index in (1,2):
        p=model.find('CAB_STRINGER_'+str(index))
        assert abs(p.local.Volume()-p.shape.Volume())<1e-6
        removed=original_volume-p.local.Volume()
        assert abs(removed-expected_removed)<1e-5,(removed,expected_removed)
        for y in STR_HOLE_Y:
            probe=cyl(STR_HOLE_D-0.001,TUBE+2).translate((TUBE/2,y,-1))
            assert intersection_volume(p.local,probe)<1e-6
        intersections=[]
        for hole in (1,2):
            screw=model.find(f'CAB_TEK_{index}_{hole}')
            volume=intersection_volume(p.shape,screw.shape)
            assert volume<1e-6
            assert frozenset((p.id,screw.id)) not in model.allowed_intersections
            intersections.append(volume)
        output=OUT/(p.id+'.step')
        cq.exporters.export(p.local,str(output))
        reread=cq.importers.importStep(str(output)).val()
        assert reread.isValid() and len(reread.Solids())==1
        assert abs(reread.Volume()-p.local.Volume())<1e-5
        evidence['stringers'].append({'id':p.id,'local_volume_mm3':p.local.Volume(),'removed_volume_mm3':removed,'expected_removed_volume_mm3':expected_removed,'screw_intersections_mm3':intersections,'step_readback_valid':True})

    guard=model.find('FLOAT_PAN_EMPTY_GUARD_FLOOR').shape
    floor=model.find('WP_FLOOR').shape
    nominal=distance(guard,floor)
    worst=distance(guard.translate((0,0,-0.3)),floor)
    assert nominal>10.6 and worst>PAN_EMPTY_MIN_AS_BUILT_GAP
    evidence['pan_empty']={'nominal_guard_floor_distance_mm':nominal,'distance_at_lowest_slot_play_mm':worst,'minimum_as_built_gap_mm':PAN_EMPTY_MIN_AS_BUILT_GAP,'remaining_fabrication_variation_allowance_mm':worst-PAN_EMPTY_MIN_AS_BUILT_GAP,'guard_bounds_mm':bbox(guard),'adjustment_pose_clashes':{}}
    prefix='FLOAT_PAN_EMPTY_'
    moving=[p for p in model.parts if p.id.startswith(prefix) and p.id!=prefix+'BACKRAIL' and not p.id.startswith(prefix+'STANDOFF_')]
    fixed=[p for p in model.parts if p not in moving]
    # Both slot end positions plus physical bottom play. Translation is parallel
    # to the straight rail slots; intermediate 2 mm positions are also sampled.
    for z in [-0.3]+list(range(0,21,2))+[20.3]:
        moved=cq.Compound.makeCompound([p.shape for p in moving]).translate((0,0,z))
        clashes=nearby_clashes(moved,fixed)
        assert not clashes,(z,clashes)
        evidence['pan_empty']['adjustment_pose_clashes'][str(z)]=clashes

    rail=model.find('FLOAT_PAN_EMPTY_BACKRAIL')
    write_dxf(OUT/'FLOAT_BACKRAIL_PAN_EMPTY.dxf',rail.flat)
    cq.exporters.export(rail.local,str(OUT/'FLOAT_BACKRAIL_PAN_EMPTY.step'))
    evidence['pan_empty']['restricted_backrail_flat']=rail.flat
    roof=model.find('CAB_DRIP_CAP')
    lip=model.find('CAB_DRIP_FRONT_LIP')
    weldment=roof.shape.fuse(lip.shape).clean()
    assert weldment.isValid() and len(weldment.Solids())==1
    cabinet=model.find('BUY_CONTROL_ENCLOSURE_RESERVE').shape
    cap_evidence={'weldment_single_valid_solid':True,'roof_bounds_mm':bbox(roof.shape),'nominal_enclosure_gap_mm':distance(weldment,cabinet),'tab_contact_distances_mm':{},'withdrawal_poses':{}}
    for p in model.parts:
        if p.id.startswith('CAB_CAP_TAB_'):
            gap=distance(roof.shape,p.shape)
            assert gap<1e-6
            cap_evidence['tab_contact_distances_mm'][p.id]=gap
    # Cap is lowered into the front bay after clearing the nominal enclosure.
    # Removal direction lies in the roof plane, so its plane does not move into
    # the cabinet roof and no rear lip exists to catch the enclosure back edge.
    cap_fixed=[p for p in model.parts if p.id not in ['CAB_DRIP_CAP','CAB_DRIP_FRONT_LIP'] and not p.id.startswith('CAB_CAP_BOLT_') and not p.id.startswith('CAB_CAP_NUT_')]
    for travel in range(0,231,10):
        translation=tuple(-travel*c for c in CAP_V)
        moved=weldment.translate(translation)
        clashes=nearby_clashes(moved,cap_fixed)
        assert not clashes,(travel,clashes)
        cap_evidence['withdrawal_poses'][str(travel)]={'translation_mm':translation,'clashes':clashes,'bounds_mm':bbox(moved)}
    cap_front=weldment.translate(tuple(-230*c for c in CAP_V))
    assert bbox(cap_front)[4]<bbox(cabinet)[1]-10
    cap_evidence['lowering_poses']={}
    for drop in range(0,101,10):
        moved=cap_front.translate((0,0,-drop))
        clashes=nearby_clashes(moved,cap_fixed)
        assert not clashes,(drop,clashes)
        cap_evidence['lowering_poses'][str(drop)]={'clashes':clashes,'bounds_mm':bbox(moved)}
    for p in [roof,lip]+[p for p in model.parts if p.id.startswith('CAB_CAP_TAB_') and p.id.endswith('_1')]:
        cq.exporters.export(p.local,str(OUT/(p.part_number+'.step')))
        reread=cq.importers.importStep(str(OUT/(p.part_number+'.step'))).val()
        assert reread.isValid() and len(reread.Solids())==1
        assert abs(reread.Volume()-p.local.Volume())<1e-5
        write_dxf(OUT/(p.part_number+'.dxf'),p.flat)
    evidence['drip_shield']=cap_evidence
    evidence['remaining_holds']=['PAN_EMPTY exact reed trip and post-trip drainage must be wet-tested; no bone-dry claim.','FW03 nominal manufactured geometry is defined, but selected enclosure projection and fabrication tolerances need verification together with FW08 door/cable/thermal integration.','FW01 plumbing service routes, FW04 tank service and FW07 whole-frame rigidity remain open.']
    (OUT/'verification.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'parts':len(model.parts),'unresolved_intersections':len(validation['unresolved_intersections']),'guard_gap_mm':nominal,'guard_gap_lowest_mm':worst,'stringers_verified':len(evidence['stringers']),'cap_withdrawal_poses':len(cap_evidence['withdrawal_poses']),'nominal_cap_enclosure_gap_mm':cap_evidence['nominal_enclosure_gap_mm']},indent=2),flush=True)

if __name__=='__main__':
    try:
        run()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.stdout.flush();sys.stderr.flush();os._exit(1)
    sys.stdout.flush();sys.stderr.flush();os._exit(0)
