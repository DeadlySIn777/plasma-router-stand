"""Place the small machine's selected motion hardware on the extrusion variant.

Units mm; world coordinates match Rev I. motion_parts(False) is wood, True plasma.
Only frozen geometry-building functions are called. No production generators/exporters.
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import os
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'output' / 'release-review' / 'RevE-ENGINEERING'
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))
from cad_helpers import Model, bbox, place, cyl, plate, rect, write_dxf
from motion_details import make_motion
from motion_completion import apply_completion
from motion_finish import make_head

POSE = {'gantry_y': 775.0, 'head_x': 575.0, 'z_lift': 50.0}
DROP, THICKNESS = 115.0, 12.7
MOUNT_PATTERN = tuple((x,y) for x in (10.,100.) for y in (22.,48.))


def _bare_motion(gantry_y,head_x,z_lift):
    m = Model()
    make_motion(m, gantry_y=gantry_y,head_x=head_x,z_lift=z_lift, tool='router')
    # Same guarded 110 mm output blank as Rev I. Keep the buyer's standard Z motor
    # geometry; neither it nor a candidate brake motor establishes power-off retention.
    apply_completion(m, replacement_brake_motor=False)
    return tuple((p.id, p.shape, tuple(p.color)) for p in m.parts)


@lru_cache(maxsize=1)
def _wood():
    return _bare_motion(**POSE)


@lru_cache(maxsize=1)
def drop_blank():
    # Local XY = across and up, +Z = toward operator/front of machine.
    # Nominal thread-diameter CAD cylinders are not drill/pilot sizes.
    upper = [(x,y+DROP,6.0) for x,y in MOUNT_PATTERN]
    lower = [(x,y,6.6) for x,y in MOUNT_PATTERN]
    outline = rect(110,DROP+70)
    machined = plate(outline,THICKNESS,upper+lower)
    for x,y in MOUNT_PATTERN:
        machined = machined.cut(cyl(10.5,6.1).translate((x,y,-.1))).clean()
    flat = dict(outline=outline,thickness_mm=THICKNESS,holes=lower,slots=[],internal=[],
                operations=([dict(type='circle',x=x,y=y+DROP,diameter=5.0,layer='DRILL_5p0_TAP_M6x1_THRU') for x,y in MOUNT_PATTERN]+
                            [dict(type='circle',x=x,y=y,diameter=10.5,layer='CB_REAR_10p5_DEPTH_6') for x,y in MOUNT_PATTERN]),
                machining_notes=['mm. Local XY across/up; rear face = Z0. Stock 110 x 185 x 12.7 mm.',
                    'Upper: 4x drill 5.0, tap M6x1 through; STEP uses nominal M6 thread envelope.',
                    'Lower: 4x dia 6.6 through, rear counterbore dia 10.5 x 6.0 deep. Deburr both faces.',
                    'Design candidate. Verify stock, torch reach, clearances and clamp/fastener loads before cutting.'])
    return machined,flat


@lru_cache(maxsize=1)
def _local_head():
    head,meta = make_head(float_lift=0.0,breakaway_offset=0.0,torch=None)
    assert not meta['actual_torch_present'] and meta['torch_bore_mm'] is None
    return tuple((p.id,p.shape,tuple(p.color)) for p in head.parts)


def _install_plasma(router):
    # Preserve the common Z-to-head adapter and replace only the installed tool.
    common = [p for p in router if not p[0].startswith(('TOOL_SPINDLE_', 'TOOL_SPLIT_CLAMP_', 'TOOL_CLAMP_'))]
    adapter = next(p[1] for p in common if p[0] == 'TOOL_ADAPTER_110')
    ox,oy,oz,*_ = bbox(adapter)
    def install(shape,origin):
        return place(shape,origin,u=(1,0,0),v=(0,0,1))
    upper=(ox,oy,oz); bracket=(ox,oy,oz-DROP); lower=(ox,oy-THICKNESS,oz-DROP)
    common.append(('WP_PLASMA_DROP_115',install(drop_blank()[0],bracket),(.30,.50,.52)))
    for name,shape,color in _local_head():
        common.append((name,install(shape,lower),color))
    # Same dedicated M6x16 screw size as Rev I. Four secure bracket to common
    # adapter; a second set secures head to bracket. Lower screw recesses face rear.
    screw = cyl(6,16).fuse(cyl(10.2,6).translate((0,0,16))).clean()
    for i,(x,y) in enumerate(MOUNT_PATTERN,1):
        component=place(screw,(x,y,9.3),u=(1,0,0),v=(0,-1,0))
        for st,origin in (('UPPER',upper),('LOWER',lower)):
            common.append((f'WP_DROP_M6x16_{st}_{i}',install(component,origin),(.49,.51,.54)))
    return tuple(common)


@lru_cache(maxsize=1)
def _plasma():
    return _install_plasma(_wood())


def motion_parts(plasma: bool) -> list[tuple[str,cq.Shape,tuple[float,float,float]]]:
    """Return named world-space solids for one mode. Cached shapes are read-only."""
    return list(_plasma() if plasma else _wood())


def motion_evidence():
    """Return inspectable geometry and process limits. No imaginary torch or cutter."""
    from process_bed import SLAT_TOP, PLANE, BACK
    states = {}
    for key, plasma in (('wood',False),('plasma',True)):
        parts = motion_parts(plasma)
        lookup = {name:shape for name,shape,_color in parts}
        assert len(lookup)==len(parts)
        for name,shape,_color in parts:
            assert shape.isValid() and len(shape.Solids()) == 1 and shape.Volume() > 0, name
        assert not any(n.startswith(('I_HEAD_PARK','MF_','RAIL_CAP_','SM_')) for n in lookup)
        assert all(n in lookup for n in ('Y_DATUM_L','Y_DATUM_R','X_RAIL_1','X_RAIL_2',
            'Y_RAIL_L','Y_RAIL_R','HMS_X_BODY','HMS_Y_L_BODY','HMS_Y_R_BODY',
            'ZBX80_BASE','ZBX80_OUTPUT_HOLD','TOOL_ADAPTER_110','GANTRY_8080'))
        assert ('I_HEAD_BACKPLATE' in lookup) == plasma
        assert ('TOOL_SPINDLE_65x259' in lookup) != plasma
        b = bbox(lookup['TOOL_ADAPTER_110'])
        if plasma:
            extent = bbox(cq.Compound.makeCompound([lookup['I_HEAD_INSERT_REAR'],lookup['I_HEAD_INSERT_FRONT']]))
        else:
            extent = bbox(lookup['TOOL_SPINDLE_65x259'])
        axis = [(extent[0]+extent[3])/2,(extent[1]+extent[4])/2]
        # Work axis of split plasma insert is at Ø48 outer cylinder center;
        # its 0.5 mm split removes symmetric material on each side.
        axis = [round(x,4) for x in axis]
        assert all(abs(a-q)<.001 for a,q in zip(axis,(575.,573.6 if plasma else 621.4))), axis
        states[key] = {
            'valid_solid_count':len(parts), 'installed_ids':[name for name,_,_ in parts],
            'pose_axis_center_xy_mm':axis,
            'head_adapter_bounds_mm':[round(x,4) for x in b],
            'reference': 'unbored plasma insert, bottom of straight grip' if plasma else 'spindle envelope lower face, not a tool tip',
            'reference_bounds_at_pose_mm':[round(x,4) for x in extent],
            'reference_bottom_range_over_Z_travel_mm':[round(extent[2]-POSE['z_lift'],4),round(extent[2]-POSE['z_lift']+100,4)],
            'nominal_axis_center_X_limits_mm':[axis[0]-400,axis[0]+400],
            'nominal_axis_center_Y_limits_mm':[round(axis[1]-500,4),round(axis[1]+500,4)],
            'actual_tool_tip_z_mm':None,
        }
    paths = [SOURCE/(name+'.py') for name in ('cad_helpers','motion_details','motion_completion','motion_finish')]+[Path(__file__),HERE/'process_bed.py']
    grip0,grip1=states['plasma']['reference_bottom_range_over_Z_travel_mm']
    target=SLAT_TOP+3+2
    return {'kind':'Nominal motion context; not a manufacturing or operation release', 'display_pose':POSE,
        'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'states':states, 'plasma_drop_mm':DROP, 'plasma_forward_shift_mm':THICKNESS,
        'wood_z_reference':{'board_top_Z_mm':PLANE+BACK,'min_spindle_body_bottom_Z_mm':960.0,
            'reference_gap_mm':round(960-PLANE-BACK,4),'note':'No measured tool protrusion, workpiece, clamp or depth of cut selected.'},
        'plasma_z_example':{'slat_z_mm':SLAT_TOP,'example_sheet_mm':3,'example_standoff_mm':2,
            'target_nozzle_z_mm':target,'needed_grip_bottom_to_nozzle_range_mm':[grip0-target,grip1-target],
            'hypothetical_projection_mm':80,'corresponding_z_lift_mm':target+80-grip0,
            'note':'Fit illustration only; neither a measured torch dimension nor a cut-chart setting.'},
        'limits':['Catalogue-size envelopes, inherited 80 mm Z output stack; no real cutter/collet or plasma nozzle.',
            'The main variant assembly replaces inherited Y datum blanks with bolted bars. The old weld-to-tube method no longer applies. Transfer the actual rail pattern and verify preload/seat flatness.',
            'Delivered HMS40 flange, slot and actual screw lead, rail holes, Z output, power-off retention, stops/soft limits, axis skew and cables require verification.',
            'Actual permitted torch grip, thermal/electrical compatibility, feed lead, tether, CNC start and height interfaces unqualified.',
            'Axis-center rectangle does not establish process reach, collision-free travel, actual wood cut depth or plasma cut capability.']}


def write_evidence():
    evidence = motion_evidence()
    detail=HERE/'motion-detail'; detail.mkdir(exist_ok=True)
    shape,flat=drop_blank()
    step=detail/'WP_PLASMA_DROP_115.step'; cq.exporters.export(shape,str(step))
    proof=cq.importers.importStep(str(step)).val()
    assert proof.isValid() and len(proof.Solids())==1 and abs(proof.Volume()-shape.Volume())<.01
    write_dxf(detail/'WP_PLASMA_DROP_115.dxf',flat)
    (HERE/'motion-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({mode:{k:v for k,v in data.items() if k!='installed_ids'} for mode,data in evidence['states'].items()},indent=2),flush=True)


if __name__ == '__main__':
    # OCCT teardown can fail after Python destroys CAD objects in this runtime.
    try:
        write_evidence(); code=0
    except Exception:
        import traceback; traceback.print_exc(); code=1
    sys.stdout.flush(); sys.stderr.flush(); os._exit(code)
