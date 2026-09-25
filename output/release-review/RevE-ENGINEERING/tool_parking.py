"""Internal spindle cradle and removed-beam hardware tray above the tank."""
import cadquery as cq
from cad_helpers import *
from frame_details import hexpart

def make_tool_parking(m, include_legacy_torch_clamps=True):
    lidtop=433.096;t=3.048;allholes=[]
    for i,x in enumerate((805,975),1):
        m.add_plate(f'TOOL_PARK_BASE_{i}',30,110,t,holes=[(5,10,6.6),(5,100,6.6)],origin=(x-15,1025,lidtop),pn='TOOL_PARK_BASE',group='tool_parking',
            notes=['Spindle is parked horizontally along X, inside the rear bay. Disconnect power before removing it from the head.'])
        h=603-(lidtop+t);cz=600-(lidtop+t)
        s=plate(rect(110,h),6,slots=[(10,130,16,6,90),(100,130,16,6,90)])
        s=s.cut(cyl(65.6,8).translate((55,cz,-1)).fuse(box(65.6,h-cz+1,8).translate((22.2,cz,-1)))).clean()
        m.add(f'TOOL_PARK_CRADLE_{i}',s,origin=(x-3,1025,lidtop+t),u=(0,1,0),v=(0,0,1),pn='TOOL_PARK_CRADLE',group='tool_parking',
            notes=['110mm wide,6mm thick;65.6mm open-top cradle centered at Y1080/Z600. Weld bottom to base with3mm fillets.',
                   'Two6x16mm strap slots at local X10/100,Z130. Use two25mm cam straps to retain the spindle.'])
        for j,y in enumerate((1035,1125),1):
            allholes.append((x-10,y))
            m.add(f'TOOL_PARK_NUT_{i}_{j}',hexpart(10,5,6),origin=(x-10,y,lidtop-t-5),pn='STD_M6_WELDNUT',group='tool_parking',material='M6 weld nut',purchased=True,color=HARDWARE)
            bolt=cyl(6,20).fuse(cyl(10,6).translate((0,0,20))).clean()
            m.add(f'TOOL_PARK_BOLT_{i}_{j}',bolt,origin=(x-10,y,lidtop+t-20),pn='STD_M6x20_SOCKET',group='tool_parking',material='M6x20 socket screw',purchased=True,color=HARDWARE)
    lid=m.find('WT_LID');bb=bbox(lid.shape)
    lid.shape=lid.shape.cut(cq.Compound.makeCompound([cyl(6.6,5).translate((x,y,lidtop-4)) for x,y in allholes])).clean()
    lid.local=lid.shape.translate(tuple(-v for v in bb[:3]));lid.flat['holes'].extend((x-bb[0],y-bb[1],6.6) for x,y in allholes)
    m.add_plate('HW_BOLT_BIN_FLOOR',200,100,t,origin=(800,725,lidtop),group='hardware_storage',notes=['Retains the four removed module drawdown bolts and lift shackles, inside the stand. Tack the tray to the removable reservoir lid.'])
    for name,x in [('L',800),('R',996.952)]:
        m.add_plate('HW_BOLT_BIN_SIDE_'+name,100,26.952,t,origin=(x,725,lidtop+t),u=(0,1,0),v=(0,0,1),pn='HW_BOLT_BIN_SIDE',group='hardware_storage')
    for name,y in [('FRONT',728.048),('REAR',825)]:
        m.add_plate('HW_BOLT_BIN_'+name,193.904,26.952,t,origin=(803.048,y,lidtop+t),u=(1,0,0),v=(0,0,1),pn='HW_BOLT_BIN_END',group='hardware_storage')
    # Plasma torch split clamp (bore Ø28 for the AG-60 straight machine body,
    # M22x1.5 head thread interface) parks flat on the tank lid beside the
    # spindle cradle. It shares the TOOL_ADAPTER_110 mount pattern (X±45).
    for name,py,depth in ([('REAR',1180,45.25),('FRONT',1230,44.75)] if include_legacy_torch_clamps else []):
        half=box(110,depth,40).cut(place(cyl(28,depth+2),(55,depth+1,40),u=(1,0,0),v=(0,0,1))).clean()
        m.add('TORCH_CLAMP_'+name,half,origin=(300,py,lidtop),pn='TORCH_SPLIT_CLAMP_'+name,group='tool_parking',material='6061-T6 aluminum billet',
              release='LEGACY INVALID CLAMP - INDIVIDUAL EXPORT GUARDED',
              notes=['Historical Rev F placeholder only. It has no mounting or pinch holes and is not a usable torch clamp.',
                     'The owned torch barrel diameter, insulated clamping zone, nozzle datum and lead attachment have not been measured. The former 27.9 mm claim is not verified.',
                     'Excluded from the corrected Rev G assembly. Do not fabricate this shape or treat it as a compatible tool interface.'])
    return {'spindle_axis_start_xyz_mm':[760.5,1080,599.7],'spindle_envelope_mm':[65,259],'strap_count':2,
        'hardware_tray_bounds_mm':[800,725,433.096,1000,825,463.096],
        'handling':'The spindle and the four removed drawdowns park inside the footprint. Prove the handheld tool transfer slowly while unpowered; the module hoist sweep does not certify that transfer.'}
