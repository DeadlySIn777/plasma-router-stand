"""Export verified bed configurations and actual-solid preview meshes.

Rev F states: RevE_ROUTER (module installed) and RevE_PLASMA_SETUP (module
hoisted clear and absent; drawdowns in the internal tray). Run after
build_reve_engineering.py and the hoist-path checker. No G-code.
"""
from pathlib import Path
import copy,json,math,sys,os,time
import numpy as np
import cadquery as cq
from cad_helpers import *
from build_reve_engineering import build_model,ROOT

def mesh_export(m,name):
    vertices=[];triangles=[];colors=[];offset=0
    for p in m.parts:
        vv,tt=p.shape.tessellate(.7,.25)
        v=np.array([q.toTuple() for q in vv],np.float32);f=np.asarray(tt,np.int32)
        if not len(f):continue
        vertices.append(v);triangles.append(f+offset);offset+=len(v)
        col=np.asarray(p.color)*255
        if p.group in('main_frame','bracing','rail_cap','controls_shield'):col=np.array([65,77,83])
        colors.append(np.tile(col.astype(np.uint8),(len(f),1)))
    dest=ROOT/'previews';dest.mkdir(exist_ok=True)
    np.savez_compressed(dest/(name+'.npz'),vertices=np.concatenate(vertices),triangles=np.concatenate(triangles),colors=np.concatenate(colors))

def plasma_model(source):
    """Module absent: it hangs on the owner winch outside the machine. The four
    drawdowns transfer to the internal tray; the spindle parks in its cradle."""
    m=Model();m.allowed_intersections=source.allowed_intersections.copy();m.holds=list(source.holds)
    bolts=0
    for part in source.parts:
        if part.id.startswith('MOD_'):continue
        p=copy.copy(part);p.notes=list(part.notes)
        if p.id=='TOOL_SPINDLE_65x259':
            p.shape=place(p.local,(760.5,1080,599.7),u=(0,1,0),v=(0,0,1))
            p.id='STORED_SPINDLE_65x259';p.group='stored_tool';m.parts.append(p);continue
        if p.id.startswith('BED_M8_'):
            p.shape=place(p.local,(830+30*bolts,731,442.644),u=(1,0,0),v=(0,0,-1))
            bolts+=1
            p.group='stored_hardware';m.parts.append(p);continue
        m.parts.append(p)
    return m

def water_visual(m):
    y0,y1=108.048,1301.952;z0=738;level=820
    shape=place(plate([(0,735+.01*(1305-y0)+3.048*math.sqrt(1.0001)-z0),(y1-y0,735+.01*(1305-y1)+3.048*math.sqrt(1.0001)-z0),(y1-y0,level-z0),(0,level-z0)],913.904),
                (118.048,y0,z0),u=(0,1,0),v=(0,0,1))
    bb=bbox(shape);tools=[]
    for p in m.parts:
        b=bbox(p.shape)
        if all(min(bb[k+3],b[k+3])-max(bb[k],b[k])>1e-5 for k in range(3)):tools.append(p.shape)
    shape=shape.cut(cq.Compound.makeCompound(tools)).clean()
    # Normal liquid is below the overflow lip; the overflow bore contains air,
    # not an isolated water column. Remove that disconnected display volume.
    shape=shape.cut(cyl(48.3,900).translate((180,1270,0))).clean()
    m.add('DISPLAY_PAN_WATER_AT_Z820',shape,group='fluid_display',material='Water volume visualization only',purchased=True,color=(.32,.55,.60),
          release='FLUID DISPLAY - NOT A FABRICATED OR PURCHASED PART',notes=['Normal water plane Z820. Volume is cut around the represented immersed solids. This does not replace fill/overflow commissioning.'])
    return shape.Volume()/1e6

def main():
    source,details=build_model()
    reports={}
    print('Export RevE_ROUTER',len(source.parts),flush=True)
    if '--resume' in sys.argv and (ROOT/'RevE_ROUTER-validation.json').exists() and (ROOT/'previews'/'RevE_ROUTER.npz').exists():
        reports['RevE_ROUTER']=json.loads((ROOT/'RevE_ROUTER-validation.json').read_text())
    else:
        reports['RevE_ROUTER']=export(source,ROOT,'RevE_ROUTER',individual=False);mesh_export(source,'RevE_ROUTER')
    plasma=plasma_model(source)
    print('Export RevE_PLASMA_SETUP',len(plasma.parts),flush=True)
    reports['RevE_PLASMA_SETUP']=export(plasma,ROOT,'RevE_PLASMA_SETUP',individual=False)
    # Water is a display layer, never a fabricated STEP component. Coincident
    # liquid/steel faces are unsuitable inputs to a solid interference certificate.
    waterlitres=water_visual(plasma)
    mesh_export(plasma,'RevE_PLASMA_SETUP')
    # Show water mechanics without upper motion or the module obscuring them.
    section=Model()
    section.parts=[p for p in source.parts if p.group in('water_pan','reservoir','pan_support','slats','slat_support','catch_basket','float_mount','float_guard','float_sensor','pump_mount','pump','vent','controls_support','controls_envelope','controls_shield','tool_parking','hardware_storage','overflow_catch','tank_support')]
    mesh_export(section,'RevE_WATER_CUTAWAY')
    summary={name:{'part_count':r['part_count'],'step_readback':r['step_readback'],'unresolved_intersections':r['unresolved_intersections']} for name,r in reports.items()}
    summary['normal_pan_water_model_litres']=waterlitres
    liquid=box(900,600,242).translate((125,715,178.048));lb=bbox(liquid);immersed=[]
    for p in source.parts:
        b=bbox(p.shape)
        if all(min(lb[k+3],b[k+3])-max(lb[k],b[k])>1e-5 for k in range(3)):
            vol=p.shape.intersect(liquid).Volume()
            if vol>.02:immersed.append({'id':p.id,'litres':vol/1e6})
    summary['tank_displacement_at_overflow_litres']=sum(p['litres'] for p in immersed)
    summary['tank_displacement_components']=immersed
    assert summary['tank_displacement_at_overflow_litres']<1,'Tank displacement exceeds reserved1L.'
    summary['limits']=['Plasma setup depicts the water/slat bed with the one-piece module hoisted clear; the module itself is outside the machine and not in that STEP.',
                       'The blue water volume appears only in previews; mechanical STEP and interference checks exclude fluid display geometry.',
                       'Spindle is parked in its internal cradle. Retained tool-clamp geometry remains on the Z head.',
                       'All purchased interface and Z retention holds in the engineering manifest remain applicable.']
    (ROOT/'state-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)
    return 0 if not any(r['unresolved_intersections'] for r in reports.values()) else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
