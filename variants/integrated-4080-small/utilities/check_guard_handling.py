"""Continuous box-enclosure proof for each sectional screen's manual route."""
from pathlib import Path
import hashlib,json,math,os,sys
import cadquery as cq
import integrated_utilities as U
HERE=Path(__file__).resolve().parent;OUT=HERE/'output';ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent));sys.path.insert(0,str(HERE.parent/'atc'))
import assembly as I
import actual_atc as A
import front_stop_bed_clearance as T
from build_utilities import overlap,clashes
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arc_bounds(s,cx,cy,a,b):
 lo,hi=sorted((math.radians(a),math.radians(b)));xx=[];yy=[]
 for v in s.Vertices():
  dx,dy=v.X-cx,v.Y-cy
  ts=[lo,hi]
  for q in(math.atan2(-dy,dx),math.atan2(dx,dy)):
   for k in range(-3,4):
    t=q+k*math.pi
    if lo<t<hi:ts.append(t)
  for t in ts:
   xx.append(cx+dx*math.cos(t)-dy*math.sin(t));yy.append(cy+dx*math.sin(t)+dy*math.cos(t))
 z=U.bb(s);return[min(xx),min(yy),z[2],max(xx),max(yy),z[5]]
def run():
 sources=list(dict.fromkeys([Path(p)for p in(__file__,HERE/'build_utilities.py',U.__file__,U.B.__file__,I.M.__file__,I.GJ.__file__,HERE.parent/'check_gantry_joint.py',HERE.parent/'output/gantry-joint/gantry-joint-check.json',A.__file__,I.__file__,T.__file__,
  I.Q.__file__,I.P.__file__,I.Q.D.__file__,U.O.__file__,U.SH.__file__,I.M.X.__file__,I.M.X.P.__file__,U.O.P.__file__,
  A.VENDOR_HOUSING_SOURCE,*I.H.sources())]))
 hashes=lambda:{p.relative_to(ROOT).as_posix():sha(p)for p in sources}
 source_start=hashes()
 fixed=I.M.frame_parts()+U.retained_wet_parts()+list(U.drain_parts())+list(U.guide_rack_parts())
 common=I.integrated_motion(False,1275,975,250,module_removed=True,spindle_context=False)
 fixed +=[p for p in common if not T.is_front_module(p[0])]
 fixed +=[p for p in I.M.motion_parts(False,1275,975,250)if T.is_front_module(p[0])]
 fixed+=A.actual_atc_parts(200,hood='stored',include_allocations=True)
 fixed +=[('ALTERNATE_FITTED_'+n,s,c)for n,s,c in A.hood_parts('fitted')]
 guides={(side,i):U.guide_screen(side,i)for side in('L','R')for i in range(3)}
 report=dict(source_sha256=source_start,
  checked_bed_angles_deg=[0.,90.],checked_hood_states=['stored','fitted'],prerequisites=['Bedat0orpositivelypinned90; usematchingcorridor','Removecompletehead/toolmodule','CommonheadX975/Y1275/Z250','ATCparked200;hoodstoredorfitted;frontstopsoperating',
   'TransferL1,L2,L3,R1,R2,R3inorder','All12M6guidefastenerstransfertostoragerackaftereachpanelisplaced'],
  method='Four conservative exterior boxes per section; translation AABBs are exact axis-aligned sweeps. Rotation XYbounds include analytic vertex arc extrema in1degreeintervals. Borevoids ignored conservatively.',
  paths=[],hits=[],total_enclosures=0,manual_hand_forces_or_person_clearances_verified=False)
 bounds=[]
 for upright in(False,True):
  guides={(side,i):U.guide_screen(side,i)for side in('L','R')for i in range(3)}
  for side in('L','R'):
   for i in range(3):
    obstacles=fixed+[(p['id'],p['shape'],p['color'])for p in U.B.bed_parts(90. if upright else 0.)]+[(f'OTHER_GUIDE_{q}_{j+1}',s,U.STEEL)for(q,j),s in guides.items()if(q,j)!=(side,i)]
    obs=[(n,s,U.bb(s))for n,s,c in obstacles]
    path=[];lo,hi,cy=U.GUIDE_SECTIONS[i];center=(lo+hi)/2;dy0=-250. if i==2 else 0.
    for stage in range(9):
     steps=90 if stage in(2,7)else 1
     for prim in U.guide_primitives(side,i):
      start=U.guide_handling_pose(side,i,stage,0,shape=prim,upright=upright)
      for k in range(steps):
       t0,t1=k/steps,(k+1)/steps
       if stage in(2,7):
        angle=(90 if side=='L'else -90)*(1 if stage==2 else -1)
        cx,cyc=(575,center+dy0)if stage==2 else(575,336)
        b=arc_bounds(start,cx,cyc,angle*t0,angle*t1)
       else:
        b0=U.bb(U.guide_handling_pose(side,i,stage,t0,shape=prim,upright=upright));b1=U.bb(U.guide_handling_pose(side,i,stage,t1,shape=prim,upright=upright))
        b=[min(b0[j],b1[j])for j in range(3)]+[max(b0[j],b1[j])for j in range(3,6)]
       bounds.append(b);report['total_enclosures']+=1;env=None
       for n,s,ob in obs:
        if not overlap(b,ob):continue
        if env is None:env=U.box(*b[:3],*(b[j+3]-b[j]for j in range(3)))
        v=env.intersect(s).Volume()
        if v>.01:report['hits'].append(dict(bed_angle_deg=90 if upright else 0,side=side,section=i+1,stage=stage,interval=[t0,t1],obstacle=n,volume_mm3=v))
     path.append(dict(stage=stage,end_bounds_mm=U.bb(U.guide_handling_pose(side,i,stage,1,upright=upright))))
    guides[(side,i)]=U.guide_handling_pose(side,i,8,1,upright=upright)
    report['paths'].append(dict(bed_angle_deg=90 if upright else 0,side=side,section=i+1,stages=path))
    print('bed',90 if upright else 0,side,i+1,'pathdone hits',len(report['hits']),flush=True)
 report['whole_route_bounds_mm']=[min(b[j]for b in bounds)for j in range(3)]+[max(b[j]for b in bounds)for j in range(3,6)]
 report['within_fixed_machine_plan']=report['whole_route_bounds_mm'][0]>=-50 and report['whole_route_bounds_mm'][1]>=-160 and report['whole_route_bounds_mm'][3]<=1200 and report['whole_route_bounds_mm'][4]<=1600
 report['source_consistent_during_check']=source_start==hashes()
 report['passed']=not report['hits']and report['within_fixed_machine_plan']and report['source_consistent_during_check']
 report['fabrication_release']=False
 (OUT/'guide-handling-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print('guardhandling',report['passed'],report['whole_route_bounds_mm'],report['hits'][:5],flush=True)
 sys.stdout.flush();os._exit(0 if report['passed']else 2)
if __name__=='__main__':run()
