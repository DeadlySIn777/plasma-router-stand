"""Rev E integrated mechanical engineering definition. Units mm.

Custom parts are dimensioned for welded steel fabrication and shop-cut/milled
plates. Purchased interfaces and final physical commissioning are independently
identified; this generator does not make machine-specific CAM or G-code.
"""
from pathlib import Path
import json,math,os,sys,time
import cadquery as cq
from cad_helpers import *
import geometry_base as base
from water_system import make_water

ROOT=Path(__file__).resolve().parent
T=50.8;W=3.048

def normalized_add(m,p):
    bb=bbox(p.shape);origin=bb[:3]
    local=p.shape.translate(tuple(-x for x in origin))
    length=max(bb[i+3]-bb[i] for i in range(3)) if 'nominal hollow' in p.geometry_basis else None
    return m.add(p.id,local,origin=origin,group=p.group,material=p.material,pn=p.id,
                 notes=[p.geometry_basis,'Welded structure: nominal square tube corners; stock corner radii are not precision mating datums.'],color=p.color,length=length)

def update_part(m,id,shape,notes=()):
    p=m.find(id);bb=bbox(shape);p.shape=shape;p.local=shape.translate(tuple(-x for x in bb[:3]));p.flat=None;p.notes.extend(notes)

def build_model():
    m=Model()
    for p in base.fixed:
        if p.group in ('main_frame','rail_cap'):
            q=normalized_add(m,p)
            if q.id=='MF_END_FRONT_UPPER':
                q.shape=q.shape.translate((0,0,100.8-679.2))
    # Frame-details module supplies actual feet, bracing, pan-bearer connections,
    # sand fill ports and racks. It is separate to keep geometry independently auditable.
    details={}
    if (ROOT/'frame_details.py').exists():
        from frame_details import make_frame
        details['frame']=make_frame(m)
    details['water']=make_water(m)
    from water_accessories import make_water_accessories
    details['water_accessories']=make_water_accessories(m)
    from sensor_mounts import make_sensor_mounts
    details['sensor_mounts']=make_sensor_mounts(m)
    if (ROOT/'bed_details.py').exists():
        from bed_details import make_bed
        details['bed']=make_bed(m)
    # Rev F: no fixed storage racks. The one-piece bed module leaves on the
    # owner's overhead winch; nothing is parked inside the frame but the tool
    # cradle and the four-drawdown tray.
    details['storage']={'racks':'None. Module is hoisted clear and parked outside the machine on the owner winch/track.',
                        'stored_inside':'Spindle cradle and the four M8 drawdowns in the internal tray.'}
    from tool_parking import make_tool_parking
    details['tool_parking']=make_tool_parking(m)
    from controls_packaging import make_controls_packaging
    details['controls_packaging']=make_controls_packaging(m)
    if (ROOT/'motion_details.py').exists():
        from motion_details import make_motion
        details['motion']=make_motion(m)
    return m,details

def get_swap_geometry():
    """Module solids for the hoist-path checker: MOD_* parts move as one body;
    the four BED_M8 drawdowns are removed to the tray before any motion."""
    m,details=build_model()
    module=[p.shape for p in m.parts if p.id.startswith('MOD_')]
    fixed={p.id:p.shape for p in m.parts if not p.id.startswith(('MOD_','BED_M8_'))}
    removed=[p.id for p in m.parts if p.id.startswith('BED_M8_')]
    return {'fixed':fixed,'module':cq.Compound.makeCompound(module),
            'module_part_ids':[p.id for p in m.parts if p.id.startswith('MOD_')],
            'removed_for_handling':removed,'model':m,'details':details}

def main():
    started=time.monotonic();m,details=build_model()
    print('Built',len(m.parts),'components; validating and exporting',flush=True)
    r=export(m,ROOT,'RevE_ASSEMBLED_ENGINEERING',individual=True)
    details['status']='ENGINEERING DEFINITION - NOT A COMMISSIONED MACHINE'
    details['geometry_checks']={'solid_count':r['part_count'],'step_readback':r['step_readback'],
                                'unresolved_intersections':r['unresolved_intersections']}
    details['elapsed_seconds']=round(time.monotonic()-started,2)
    (ROOT/'engineering-manifest.json').write_text(json.dumps(details,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'parts':r['part_count'],'clashes':r['unresolved_intersections'],'elapsed':details['elapsed_seconds']}),flush=True)
    return 0 if not r['unresolved_intersections'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
