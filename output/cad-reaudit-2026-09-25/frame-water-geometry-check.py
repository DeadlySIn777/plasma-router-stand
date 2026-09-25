from pathlib import Path
import sys, json, hashlib, math, os
ROOT=Path(__file__).resolve().parent.parent/'release-review'/'RevE-ENGINEERING'
OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT))
from cad_helpers import *
from build_reve_engineering import normalized_add
import geometry_base as base
from frame_details import make_frame
from water_system import make_water
from water_accessories import make_water_accessories
from sensor_mounts import make_sensor_mounts
from controls_packaging import make_controls_packaging
from tool_parking import make_tool_parking
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
m=Model()
for p in base.fixed:
    if p.group in ('main_frame','rail_cap'):
        q=normalized_add(m,p)
        if q.id=='MF_END_FRONT_UPPER':q.shape=q.shape.translate((0,0,100.8-679.2))
details={}
for name,fn in [('frame',make_frame),('water',make_water),('water_accessories',make_water_accessories),('sensors',make_sensor_mounts),('tool_parking',make_tool_parking),('cabinet',make_controls_packaging)]:
    details[name]=fn(m)
    print(name,len(m.parts),flush=True)
def distance(a,b):
    r=BRepExtrema_DistShapeShape(a.wrapped,b.wrapped)
    r.Perform()
    assert r.IsDone()
    return r.Value()
record={'status':'Independent targeted nominal geometry checks only; no design modifications','part_count':len(m.parts),'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')},'invalid':[],'measurements':{},'service_probes':{}}
for p in m.parts:
    if not p.shape.isValid() or len(p.shape.Solids())!=1:record['invalid'].append(p.id)
for a,b in [('FLOAT_PAN_EMPTY_GUARD_FLOOR','WP_FLOOR'),('WT_CLEANOUT_NECK','TS_CROSS_3'),('WP_OVERFLOW_STANDPIPE','WT_LID'),('WT_EMERGENCY_OVERFLOW','OVERFLOW_CATCH_FLOOR'),('BUY_CONTROL_ENCLOSURE_RESERVE','PAN_BEARER_1'),('BUY_CONTROL_ENCLOSURE_RESERVE','MF_END_FRONT_UPPER')]:
    aa=m.find(a).shape;bb=m.find(b).shape
    record['measurements'][a+' / '+b]={'distance_mm':distance(aa,bb),'intersection_mm3':intersection_volume(aa,bb),'a_bounds':bbox(aa),'b_bounds':bbox(bb)}
floor=m.find('WP_FLOOR').shape
for a in ['WP_DRAIN_NECK','WP_OVERFLOW_STANDPIPE']:
    record['measurements'][a+' / panfloor']={'distance_mm':distance(m.find(a).shape,floor),'intersection_mm3':intersection_volume(m.find(a).shape,floor)}
# Collision probes of named, simple service motions; a collision rejects only
# that tested motion, not every possible hand-service route.
tests=[('bare_lid_rear_100', ['WT_LID'], (0,100,0)),('bare_lid_rear_60_lift15',['WT_LID'], (0,60,15)),('basket_lift100',[p.id for p in m.parts if p.group=='catch_basket'], (0,0,100))]
for name,ids,t in tests:
    moved=cq.Compound.makeCompound([m.find(x).shape for x in ids]).translate(t)
    bb=bbox(moved);clashes=[]
    for p in m.parts:
        if p.id in ids or p.id.startswith('WT_LID_BOLT') or p.id.startswith('PUMP_') or p.id.startswith('TOOL_PARK_') or p.group in ('hardware_storage','pump'):continue
        aa=bbox(p.shape)
        if not all(min(aa[k+3],bb[k+3])-max(aa[k],bb[k])>1e-5 for k in range(3)):continue
        vol=intersection_volume(moved,p.shape)
        if vol>.02:clashes.append({'id':p.id,'volume_mm3':vol})
    record['service_probes'][name]={'translation_mm':t,'moving_ids':ids,'clashes':clashes}
record['parts']=[{'id':p.id,'bounds':bbox(p.shape),'volume_mm3':p.shape.Volume()} for p in m.parts]
record['cage_hole_evidence']={'stringer_1_volume_mm3':m.find('CAB_STRINGER_1').shape.Volume(),'unperforated_tube_volume_mm3':(25.4**2-(25.4-2*2.1082)**2)*499.2,'screw_intersection_mm3':intersection_volume(m.find('CAB_STRINGER_1').shape,m.find('CAB_TEK_1_1').shape),'comment':'The stringer volume equals a plain tube; the claimed predrilled clearance holes are not cut in the solid.'}
record['cabinet_nominal_projection_margins_mm']={'door_top_to_bearer_bottom':679.2-673,'door_bottom_to_lowered_front_tie':165-151.6,'washer_gap_behind_cage_rail':1.0}
(OUT/'frame-water-geometry-evidence.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ('source_sha256','parts')},indent=2),flush=True)
# Match the project's CadQuery exporter process-exit convention. The local
# Windows CAD runtime returns code 1 during interpreter teardown after writing
# complete evidence; avoid that destructor phase once assertions are complete.
sys.stdout.flush();sys.stderr.flush();os._exit(0)
