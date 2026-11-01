"""Actual pan displacement and reservoir allowance; no invented tote interior."""
from pathlib import Path
import hashlib,json,os,sys
import cadquery as cq
import params as P
from bed import PAN_T,pan_parts,pan_floor_z,yz,water_envelopes

HERE=Path(__file__).resolve().parent
RECEIVER_REQUIRED_USABLE_L=65.
PIPE_ALLOWANCE_L=3.
SLUDGE_ALLOWANCE_L=2.

def fluid_at(z):
    t=PAN_T;x0=P.PAN_X0+t;x1=P.PAN_X1-t;y0=P.PAN_Y0+t;y1=P.PAN_Y1-t
    if z<=pan_floor_z(y0):return None
    if P.PAN_SLOPE>0:y1=min(y1,P.PAN_Y0+(z-P.PAN_FLOOR_FRONT)/P.PAN_SLOPE)
    if y1<=y0:return None
    vertices=[(y0,pan_floor_z(y0)),(y1,pan_floor_z(y1)),(y1,z),(y0,z)]
    # Avoid a duplicate vertex at the triangular low-water limit.
    points=[]
    for v in vertices:
        if not points or sum((a-b)**2 for a,b in zip(v,points[-1]))>1e-12:points.append(v)
    shape=yz(x0,x1-x0,points)
    for n,s,_ in pan_parts():
        if n.startswith(('HOT_COMB_','HOT_SLAT_')):shape=shape.cut(s)
    assert shape.isValid()
    return shape

def run():
    sources=[HERE/n for n in ('params.py','bed.py','water_check.py','reservoir-interface.json')]
    start={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    parts=pan_parts();outlet=next(s for n,s,_ in parts if n.startswith('DRAIN_SMOOTH_'))
    bb=outlet.BoundingBox();centre=(bb.zmin+bb.zmax)/2
    drain_invert=centre-12.
    levels={'operating':P.SLAT_TOP-24.,'overflow_invert':P.PAN_RIM-11.,'brim':P.PAN_RIM,'drained_residual':drain_invert}
    volumes={}
    for name,z in levels.items():
        s=fluid_at(z);volumes[name]=0. if s is None else s.Volume()/1e6
    full_drain=volumes['brim']-volumes['drained_residual']
    worst=full_drain+PIPE_ALLOWANCE_L+SLUDGE_ALLOWANCE_L
    margin=RECEIVER_REQUIRED_USABLE_L-worst
    fluid=fluid_at(levels['brim']);b=fluid.BoundingBox()
    water=water_envelopes()
    receiver=next(s for n,s,_ in water if n.startswith('WATER_RED20GAL_'))
    rb=receiver.BoundingBox()
    lid=next(s for n,s,_ in water if n.startswith('WATER_REMOVABLE_LID_'));lb=lid.BoundingBox()
    result={
      'revision':'XR1','prices_included':False,'release':False,
      'levels_Z_mm':levels,'liquid_volumes_L_after_comb_slat_displacement':volumes,
      'water_box_capacity_requirement':{
          'minimum_measured_usable_L':RECEIVER_REQUIRED_USABLE_L,
          'complete_brim_pan_drain_L':full_drain,'pipe_allowance_L':PIPE_ALLOWANCE_L,
          'sludge_allowance_L':SLUDGE_ALLOWANCE_L,'required_combined_L':worst,
          'margin_L_if_65L_measured_usable':margin,
          'maximum_initial_receiver_water_L_for_this_case':max(0.,margin),
          'selected_listing_nominal_storage_US_gal':20,
          'physical_usable_liquid_capacity_verified':False,
          'critical_limit':'The rectangular CAD receiver is an external clearance envelope, not the real tapered liquid interior. Do not derive capacity or water load rating from its hollow CAD volume.'},
      'receiver_fit_envelope_mm':[rb.xlen,rb.ylen,rb.zlen],
      'geometry_checks':{'capacity_allowance_positive':margin>0,
          'overflow_above_operating_level':levels['overflow_invert']>levels['operating'],
          'rim_above_overflow':P.PAN_RIM>levels['overflow_invert'],
          'receiver_candidate_height_includes_lid_mm':lb.zmax,
          'all_water_solids_valid':all(s.isValid() and s.Volume()>0 for _,s,_ in water)},
      'hydraulic_thermal_holds':[
          'Cold-water leak, complete drain and partial-depth tail-flow test using actual fittings and hose.',
          'Verify actual hose minimum bend radius, supports, valve sweep, continuously falling route and accessible cleanout.',
          'Verify independent overflow capacity exceeds the actual filling rate; geometry alone is not a flow rating.',
          'Confirm usable tote volume, long-term liquid load, temperature and coolant compatibility with the actual delivered product.',
          'Empty receiver before filling the pan; its nominal storage capacity is not spare capacity when already partly full.',
          'Keep vent and top returns unobstructed; no compressor pressure, sealed drain or venturi liquid pumping.',
          'Lid removal/service path remains a physical trial; a full upward hinge sweep is not assumed to fit under the pan.',
          'Qualify hot debris shields, protected wood-storage temperature and cooldown before mixed wood/plasma operation.'
      ],
      'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    result['source_consistent_during_check']=start==result['source_sha256']
    result['passed']=all(result['geometry_checks'][k] for k in ('capacity_allowance_positive','overflow_above_operating_level','rim_above_overflow','all_water_solids_valid')) and result['source_consistent_during_check']
    result['scope']='Geometry/volume requirement check only. A passed flag does not verify the tote liquid rating, measured usable capacity, gravity/overflow flow or thermal protection.'
    (HERE/'review'/'water-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'volumes_L':volumes,'receiver_margin_L_if_verified':margin,'passed':result['passed']},indent=2),flush=True)
    return 0 if result['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
