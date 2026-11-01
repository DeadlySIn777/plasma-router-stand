"""Independent wet volume and manual pad path checks. No geometry edits."""
from pathlib import Path
import importlib.util, json, hashlib, math, os, sys
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('whole_budget',HERE/'build.py')
SOURCE_BYTES=(HERE/'build.py').read_bytes()
b=importlib.util.module_from_spec(spec)
exec(compile(SOURCE_BYTES,str(HERE/'build.py'),'exec'),b.__dict__)
def bb(s):
 a=s.BoundingBox();return [a.xmin,a.ymin,a.zmin,a.xmax,a.ymax,a.zmax]
def overlap(a,c):
 return min(min(a[i+3],c[i+3])-max(a[i],c[i]) for i in range(3))
def check(s, obstacles):
 a=bb(s);out=[]
 for n,o in obstacles:
  if overlap(a,bb(o)) > .015:
   v=s.intersect(o).Volume()
   if v>.05:out.append({'part':n,'volume_mm3':v})
 return out
def steps():return [i/12 for i in range(13)]
def main():
 fixed,wood,plasma=b.components()
 pads={i:next(s for n,s,c in wood if n==f'removable_wood_pad_{i}') for i in range(4)}
 stored={i:next(s for n,s,c in plasma if n==f'parked_wood_pad_{i}') for i in range(4)}
 park=[(n,s.translate((0,0,-b.LOWER))) for n,s,c in b._bare_motion(275.,575.,100.) if n not in ('Y_DATUM_L','Y_DATUM_R')]
 static=[(n,s) for n,s,c in fixed]+park
 source=SOURCE_BYTES
 result={'source_sha256':hashlib.sha256(source).hexdigest(),'pose':{'gantry_y':275,'head_x':575,'z_lift':100,'cutter':'No cutter modeled; cutter must be removed. Spindle envelope retained in this check.'},
 'limits':'Discrete 12 subdivisions per segment, actual CAD common volumes after AABB culling, plus conservative bounding solids enclosing each complete translation/rotation phase. No cable, hand-access, structural or thermal qualification.',
 'water':{'inside_floor_z_mm':b.INSIDE,'wall_rim_z_mm':b.FLOOR+35,
 'gross_floor_area_mm2':830*1030,'normal_fill_20mm_upper_L':830*1030*20/1e6,'overflow_26mm_upper_L':830*1030*26/1e6,
 'absolute_rim_upper_L':830*1030*(35-b.SHEET)/1e6,'hose_allowance_L':1,
 'absolute_rim_plus_hose_upper_L':830*1030*(35-b.SHEET)/1e6+1,
 'receiver_required_measured_usable_L':30,'capacity_bound_pass':830*1030*(35-b.SHEET)/1e6+1<30,
 'note':'Gross bound ignores all wall, comb, slat and fixture displacement, hence conservatively exceeds actual water volume. Nominal34L receiver is not a measured usable volume.'},
 'cabinet':{'closed_guard_parts_present_in_plasma':[n for n,s,c in plasma if n.startswith('cold_case_lid_')],
 'lid_parts_in_carving':[n for n,s,c in wood if n.startswith('cold_case_lid_')],
 'use':'All four pads enclosed and lid mechanically secured before plasma mode. Open case only with tools isolated, water and steel cooled, cutter removed, and no work/fixtures on pads.',
 'qualification':'Thin galvanized secondary spark/dust guard beyond nominal tool travel. Neither hermetic sealing nor thermal/fire protection is established by this geometry.',
 'receiver':'Cold stationary open service receiver only, full bottom supported, no lifting filled, no pressure; usable volume must be measured at >=30L before draining.'},
 'path':[]}
 overflow=next((s for n,s,c in fixed if n=='independent_overflow_return'),None)
 if overflow is not None:
  solids=list(overflow.Solids())
  down=next(s for s in solids if bb(s)[4]-bb(s)[1]<b.SHEET+.01 and bb(s)[5]-bb(s)[2]>100)
  d=bb(down)
  obstacles=[(n,s) for n,s,c in fixed if s is not overflow and not n.startswith(('pan_','comb_','slat_','pad_'))]
  result['water']['overflow_geometry']={
   'component_solids':[{'valid':s.isValid(),'bounds_mm':bb(s)} for s in solids],
   'deflector_bounds_mm':d,'receiver_nominal_envelope_mm':[320,140,0,720,790,300],
   'receiver_open_fit_envelope_mm':[324,144,300,716,786,300],
   'downward_outlet_projection_inside_receiver':d[0]>=324 and d[3]<=716 and d[1]>=144 and d[4]<=786,
   'front_projection_margin_mm':d[1]-144,'side_projection_margin_mm':min(d[0]-324,716-d[3]),
   'vs_frame_interferences':check(overflow,obstacles),
   'flow_qualification':'Drop box intercepts front notch; back low opening feeds under-beam return; end deflector blocks forward jet and gives downward outlet. Gravity projection only: overflow throughput, wetting, splash, blockage and heating need cold-water/operating validation. No CFD claim.',
   'receiver_temperature':'Deploy as cold-service receiver only with tools isolated and pan cooled unless its shielding and liquid temperature are separately qualified. Primary pan coverage alone does not prove thermal safety.'}
 parked={}
 installed=dict(pads)
 for i in (3,2,1,0):
  base=pads[i];a=bb(base);cy=(a[1]+a[4])/2;cz=(a[2]+a[5])/2
  target=bb(stored[i]);targetcy=(target[1]+target[4])/2
  lift=base.translate((0,0,850-a[2]))
  rear=lift.translate((0,1282-cy,0))
  high=rear.translate((0,0,100))
  pivot=(575,1282,950+b.WOOD_T/2)
  turned=high.rotate(pivot,(576,1282,pivot[2]),90)
  shifted=turned.translate((0,targetcy-1282,0))
  down=shifted.translate((0,0,target[2]-bb(shifted)[2]))
  stages=[
   ('lift_to_bottom850',lambda t:base.translate((0,0,(850-a[2])*t))),
   ('translate_centerY1282',lambda t:lift.translate((0,(1282-cy)*t,0))),
   ('raise_to_bottom950',lambda t:rear.translate((0,0,100*t))),
   ('rotate90_about_center',lambda t:high.rotate(pivot,(576,1282,pivot[2]),90*t)),
   ('align_vertical_slot',lambda t:turned.translate((0,(targetcy-1282)*t,0))),
   ('lower_into_slot',lambda t:shifted.translate((0,0,(target[2]-bb(shifted)[2])*t)))]
  obstacles=static+[(f'installed_pad_{j}',s) for j,s in installed.items() if j!=i]+[(f'stored_pad_{j}',s) for j,s in parked.items()]
  item={'pad':i,'installed_bounds_mm':a,'stored_bounds_mm':target,
        'final_pose_symmetric_difference_mm3':down.cut(stored[i]).Volume()+stored[i].cut(down).Volume(),'steps':[]}
  for name,fn in stages:
   hit=[];bounds=[math.inf]*3+[-math.inf]*3
   for t in steps():
    s=fn(t);sbb=bb(s)
    for k in range(3):bounds[k]=min(bounds[k],sbb[k]);bounds[k+3]=max(bounds[k+3],sbb[k+3])
    bad=check(s,obstacles)
    if bad:hit.append({'t':t,'clashes':bad})
   if name=='rotate90_about_center':
    rad=math.sqrt(125**2+(b.WOOD_T/2)**2)
    bounds=[a[0],1282-rad,pivot[2]-rad,a[3],1282+rad,pivot[2]+rad]
   sweep=b.box(bounds[0],bounds[1],bounds[2],bounds[3]-bounds[0],bounds[4]-bounds[1],bounds[5]-bounds[2])
   envelope_hit=check(sweep,obstacles)
   item['steps'].append({'stage':name,'bounds_mm':bounds,'outside_table_XY':bounds[0]<0 or bounds[3]>1150 or bounds[1]<0 or bounds[4]>1450,'interferences':hit,
       'conservative_sweep_envelope_interferences':envelope_hit,
       'sweep_note':'Linear phase: union endpoint AABB encloses entire translation. Rotation: full YZ radius encloses every angle. An empty envelope intersection is a sufficient modeled-geometry clearance condition.'})
   print('checked',i,name,'clash_samples',len(hit),'sweep_envelope_hits',len(envelope_hit),flush=True)
  result['path'].append(item)
  installed.pop(i);parked[i]=down
 result['stored_pad_pair_min_gaps_Y_mm']=[bb(stored[i+1])[1]-bb(stored[i])[4] for i in range(3)]
 router=bb(next(s for n,s in park if n=='TOOL_SPINDLE_65x259'))
 axis_x=(router[0]+router[3])/2;axis_y=(router[1]+router[4])/2
 installed_bounds=sorted([bb(s) for s in pads.values()],key=lambda q:q[1])
 physical=[min(q[0] for q in installed_bounds),min(q[1] for q in installed_bounds),max(q[3] for q in installed_bounds),max(q[4] for q in installed_bounds)]
 result['process_extent']={'wood_board_extents_XY_mm':physical,
  'router_nominal_axis_X_mm':[axis_x-400,axis_x+400],'router_nominal_axis_Y_mm':[axis_y,axis_y+1000],
  'nominal_router_rectangle_within_board_outer_extents':physical[0]<=axis_x-400 and physical[2]>=axis_x+400 and physical[1]<=axis_y+1e-7 and physical[3]>=axis_y+1000-1e-7,
  'wood_panel_seams_mm':[[installed_bounds[i][4],installed_bounds[i+1][1]] for i in range(3)],
  'wood_note':'Nominal1000mm axis extent is supported by the board arrangement, with three1mm panel seams. This does not establish facing every outer edge or actual cutter/work/clamp clearance.',
  'plasma_nominal_axis_Y_mm':[73.6,1073.6],'pan_outer_Y_mm':[85,1115],
  'plasma_note':'Inherited plasma axis begins11.4mm ahead of pan. Select actual cuts within supported pan/slat area with measured torch margins; this model does not set safe operating limits.'}
 result['path_pass']=all(pad['final_pose_symmetric_difference_mm3']<.05 for pad in result['path']) and all(not stage['outside_table_XY'] and not stage['interferences'] and not stage['conservative_sweep_envelope_interferences'] for pad in result['path'] for stage in pad['steps'])
 result['recorded_pair_gaps_pass']=min(result['stored_pad_pair_min_gaps_Y_mm'])>=.99
 result['source_hash_at_completion']=hashlib.sha256((HERE/'build.py').read_bytes()).hexdigest()
 result['source_unchanged_during_check']=result['source_hash_at_completion']==result['source_sha256']
 (HERE/'wetdry-validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'source_sha':result['source_sha256'],'path_pass':result['path_pass'],'water_pass':result['water']['capacity_bound_pass'],'stored_gaps':result['stored_pad_pair_min_gaps_Y_mm']}),flush=True)
if __name__=='__main__':
 try:main();exitcode=0
 except Exception:
  import traceback;traceback.print_exc();exitcode=1
 sys.stdout.flush();sys.stderr.flush();os._exit(exitcode)

