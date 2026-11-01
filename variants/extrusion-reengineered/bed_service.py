"""XR2 cold-service scenes and explicitly staged pan/tote replacement geometry."""
from math import sqrt,pi
import cadquery as cq
import params as P
from bed import *
from frame import frame_parts
from motion import motion_parts

def bare_motion():
    return [q for q in motion_parts(False,1275.,575.,P.Z_TRAVEL)
            if not q[0].startswith(('TOOL_SPINDLE_','TOOL_SPLIT_CLAMP_','TOOL_CLAMP_'))]

def accessories():
    from shields import shield_parts
    p=shield_parts(False);missing=[]
    try:
        from atc import atc_parts
        p+=atc_parts(False,deployed=False)
    except (ImportError,SyntaxError) as e:missing.append('atc.py unavailable/in-progress: '+str(e))
    return p,missing

def pan_moving():
    # Combs stay welded to the pan. Slats lift out independently before handling.
    return [q for q in pan_parts() if q[0].startswith(('HOT_PAN_','HOT_COMB_',
       'DRAIN_SMOOTH_','INDEPENDENT_OPEN_OVERFLOW_','PAN_OVERFLOW_WELDED_'))]+[
       q for q in pan_retainers() if q[0].startswith('PAN_WELDED_EAR_')]

def pan_pose(stage):
    p=pan_moving();out=[]
    for n,s,c in p:
        if stage>=1:s=s.translate((0,0,70))
        if stage>=2:s=s.translate((0,-70,0))
        if stage>=3:s=s.rotate((0,100,882),(1,100,882),90)
        if stage>=4:s=s.translate((0,200,0))
        if stage>=5:s=s.translate((0,0,-792))
        out.append((n,s,c))
    return out

def replacement_fixed():
    # HGRrails/blocks, screw modules and gantry remain assembled and supported.
    f=[q for q in frame_parts() if q[0] not in ('XR_EX_DRY_ARM_L_1','XR_EX_DRY_ARM_R_1')]
    f+=bare_motion()+storage_parts(False)
    f+=[q for q in pan_parts() if q[0].startswith('PAN_FRAME_SHIM_PACK_')]
    f+=[q for q in pan_retainers() if not q[0].startswith(('PAN_WELDED_EAR_',
          'PAN_KEEPER_')) or q[0].endswith('_BOSS')]
    for i in range(4):f+=cassette_parts(i,'stored')
    a,m=accessories()
    # Entirebolt-onATCmagazine/railmodule is removedforrarepantote replacement.
    # HGRmotion guides andsupportedgantry remainin f.
    return f,m

def tote_assembly():
    return [q for q in water_envelopes() if q[0].startswith(('WATER_RED20GAL_',
       'WATER_REMOVABLE_LID_','RECEIVER_HATCH_'))]

def temporary_pan_supports():
    out=[]
    for i,x in enumerate((140.,935.)):
        out.append((f'SERVICE_DUNNAGE_{i}',box(x,235,0,75,70,20),PLY))
    # Adjustable clamp-head safety props: service tooling, not assumed owned.
    for i,x in enumerate((128.95,1021.05)):
        a=cq.Vector(x,100,20);b=cq.Vector(x,235,850);v=b-a
        tube=cq.Solid.makeCylinder(8,v.Length,a,v.normalized())
        foot=box(x-30,75,0,60,50,20)
        tube=tube.cut(box(x-10,235,0,20,20,1200))
        head=box(x-20,235,830,40,3,40)
        out.append((f'SERVICE_CLAMP_HEAD_PROP_{i}_MIN500N_TOOLING',
                    fuse([tube,foot,head]),AL))
    return out

def coiled_hose():
    original=next(s for n,s,c in water_envelopes() if n.startswith('WATER_25MM_GRAVITY_HOSE_'))
    length=original.Volume()/(pi*(17**2-12.5**2))
    pitch,r=20.,150.;height=length*pitch/sqrt((2*pi*r)**2+pitch**2)
    wire=cq.Wire.makeHelix(pitch,height,r,center=cq.Vector(350,480,20))
    plane=cq.Plane(origin=wire.startPoint(),normal=wire.tangentAt(0))
    s=cq.Solid.sweep(cq.Workplane(plane).circle(17).val(),
        [cq.Workplane(plane).circle(12.5).val()],wire,True,True)
    return [('SERVICE_DISCONNECTED_HOSE_COIL_R150',s,(.22,.27,.30))]

def service_scene(stage='hatch_open'):
    if stage=='hatch_open':
        moving=[q[0] for q in receiver_hatch_parts(False)]
        p=[q for q in bed_parts(True) if q[0] not in moving]
        p+=receiver_hatch_parts(True)+frame_parts()+bare_motion()+accessories()[0]
        return p
    if stage=='pan_parked':
        p=replacement_fixed()[0]+pan_pose(5)+temporary_pan_supports()+coiled_hose()
        p+=tote_assembly()
        return p
    raise ValueError(stage)
