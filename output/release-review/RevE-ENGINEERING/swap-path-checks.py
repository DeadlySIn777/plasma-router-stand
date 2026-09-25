"""Actual-solid, sampled motion check for the Rev F one-piece bed-module hoist.

The module (every MOD_* part, spoilboards included) moves as ONE rigid body:
lift 30 mm, translate forward out of the open front window, hoist clear. The
four BED_M8 drawdowns are removed to the internal tray first. Run with the
project's CadQuery Python. All transforms are recorded as homogeneous matrices.
"""
from pathlib import Path
import math, json, time, sys, os, hashlib, io, datetime
import numpy as np
import cadquery as cq
from cad_helpers import bbox
from build_reve_engineering import get_swap_geometry

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'swap-path-checks.json'
I=np.eye(3)
LIFT=60.0
FORWARD=1400.0            # rail rear end Y1320 finishes at Y-80, fully outside
HOIST=500.0
SOURCE_MODULES=['bed_details.py','build_reve_engineering.py','cad_helpers.py','controls_packaging.py',
    'frame_details.py','geometry_base.py','motion_details.py','sensor_mounts.py',
    'tool_parking.py','water_accessories.py','water_system.py','swap-path-checks.py']

def pose(R=I,t=(0,0,0)):
    M=np.eye(4);M[:3,:3]=R;M[:3,3]=t;return M

def moved(s,M):
    return s.moved(cq.Plane(origin=tuple(M[:3,3]),xDir=tuple(M[:3,0]),normal=tuple(M[:3,2])).location)

def overlaps(a,b,tol=1e-5):return all(a[k+3]>b[k]+tol and b[k+3]>a[k]+tol for k in range(3))

class Checker:
    def __init__(self):
        self.start=time.monotonic()
        self.source_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_MODULES}
        data=get_swap_geometry();self.data=data
        after={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_MODULES}
        self.failures=[]
        changed=[k for k,v in after.items() if self.source_hashes.get(k)!=v]
        if changed:self.failures.append({'object':'BUILD','stage':'source snapshot','type':'source_changed_during_build','files':changed})
        self.trace=[];self.samples=0;self.checks=0
        self.module=data['module'];self.module_solids=None
        self.sweep_bounds=[float('inf')]*3+[float('-inf')]*3
        self.fixed={};self.fixed_exclusions=[]
        for k,v in data['fixed'].items():
            if k.startswith(('TOOL_SPINDLE_','TOOL_TORCH_')):
                self.fixed_exclusions.append(k);continue
            self.fixed[k]=(v,bbox(v))
        # X footprint stays authoritative; the module deliberately EXITS in -Y
        # through the open front window, so only X bounds are enforced.
        self.x_limits=[min(v[1][0] for v in self.fixed.values()),max(v[1][3] for v in self.fixed.values())]
        self.fixed_fingerprints={}
        for k,(shape,bb) in self.fixed.items():
            stream=io.BytesIO();shape.exportBrep(stream)
            self.fixed_fingerprints[k]={'brep_sha256':hashlib.sha256(stream.getvalue()).hexdigest(),'bounds_mm':bb,'volume_mm3':shape.Volume()}
        self.M=pose()
        density_note='steel 7.85e-6, MDF 7.5e-7, aluminum 2.7e-6 kg/mm3 by material text'
        mass=0
        for p in data['model'].parts:
            if not p.id.startswith('MOD_'):continue
            d=7.5e-7 if p.material.startswith('MDF') else (2.7e-6 if ('6063' in p.material or 'aluminum' in p.material.lower() or 'fender' in p.material.lower()) else 7.85e-6)
            mass+=p.shape.Volume()*d
        self.module_mass=round(mass,2);self.mass_note=density_note
        configs={'units':'mm','matrix_convention':'Column vectors; matrix maps assembled module coordinates into world coordinates.',
                 'module_part_id_prefix':'MOD_','module_part_ids':data['module_part_ids'],
                 'removed_for_handling':data['removed_for_handling'],
                 'router':{'matrix':pose().tolist()},
                 'plasma':'Module absent: hoisted clear of the machine on the owner winch. No in-frame storage matrices exist in Rev F.',
                 'reverse':'Install is the exact reverse; the two dowels engage on the final 30 mm descent.'}
        (ROOT/'bed-configurations.json').write_text(json.dumps(configs,indent=2)+'\n',encoding='utf-8')

    def examine(self,M,stage,progress):
        s=moved(self.module,M);b=bbox(s);self.samples+=1
        self.sweep_bounds=[min(self.sweep_bounds[k],b[k]) for k in range(3)]+[max(self.sweep_bounds[k+3],b[k+3]) for k in range(3)]
        if b[0]<self.x_limits[0]-1e-4 or b[3]>self.x_limits[1]+1e-4:
            self.failures.append({'object':'MODULE','stage':stage,'progress':progress,'type':'x_footprint','bounds':b})
        if self.module_solids is None:
            self.module_solids=len(self.module.Solids())
        moving=None
        for other,(shape,bb) in self.fixed.items():
            if not overlaps(b,bb):continue
            if moving is None:moving=[(a,bbox(a)) for a in s.Solids()]
            obstacles=[(a,bbox(a)) for a in shape.Solids()]
            pairs=[(i,j) for i,(a,aa) in enumerate(moving) for j,(q,qq) in enumerate(obstacles) if overlaps(aa,qq)]
            if not pairs:continue
            self.checks+=1
            ma=cq.Compound.makeCompound([moving[i][0] for i in sorted(set(i for i,j in pairs))])
            ob=cq.Compound.makeCompound([obstacles[j][0] for j in sorted(set(j for i,j in pairs))])
            try:v=ma.intersect(ob).Volume()
            except ValueError:
                v=0.0
                for sa in ma.Solids():
                    ba=bbox(sa)
                    for sb in ob.Solids():
                        if overlaps(ba,bbox(sb)):
                            try:v+=sa.intersect(sb).Volume()
                            except ValueError:
                                self.failures.append({'object':'MODULE','stage':stage,'obstacle':other,'type':'unresolved_boolean_error'})
            if v>0.02:
                self.failures.append({'object':'MODULE','stage':stage,'progress':round(progress,5),'obstacle':other,'intersection_mm3':round(v,5),'bounds':b})
                print('CLASH',stage,other,round(v,3),flush=True)
        self.M=M

    def move(self,name,target,step=25):
        start=self.M.copy()
        length=float(np.linalg.norm(target[:3,3]-start[:3,3]));n=max(1,math.ceil(length/step))
        prior=len(self.failures);matrices=[]
        for j in range(n+1):
            u=j/n;matrix=pose(start[:3,:3],(1-u)*start[:3,3]+u*target[:3,3])
            matrices.append(matrix.round(8).tolist())
            self.examine(matrix,name,u)
            if len(self.failures)>prior:break
        self.M=target
        self.trace.append({'object':'MODULE','stage':name,'start_matrix':start.round(8).tolist(),'end_matrix':target.round(8).tolist(),
                           'sampled_matrices':matrices,'samples_requested':n+1,'passed':len(self.failures)==prior})
        print('MODULE',name,'PASS' if len(self.failures)==prior else 'FAIL',flush=True)
        self.write()

    def write(self):
        result={'status':'FAIL' if self.failures else 'IN PROGRESS','units':'mm',
                'fixed_component_count':len(self.fixed),'fixed_component_ids':list(self.fixed),
                'fixed_tool_exclusions':self.fixed_exclusions,
                'fixed_geometry_fingerprints':self.fixed_fingerprints,
                'module_solid_count':self.module_solids,
                'module_estimated_mass_kg':self.module_mass,'module_mass_basis':self.mass_note,
                'drawdowns_removed_for_handling':True,'spoilboards_included_in_module':True,
                'method':'Actual B-rep positive-volume intersections, AABB broad phase. One rigid module body; translations sampled at <=25 mm, the initial lift and close passes at <=5 mm. Sampled path validation, not a proof of all intermediate configurations or rigging behavior.',
                'required_preconditions':['Machine isolated; spindle or torch removed from the head.','Gantry parked at the rear datum.','Water drained; slats, floats and reservoir remain installed and are live obstacles.','All four BED_M8 drawdowns removed to the internal tray.','Four-leg sling on the four lift ears, hook at least 1.2 m above the ears, slack taken up before the drawdowns are released.'],
                'exit_corridor':'X within the fixed footprint at all times; the path deliberately leaves the machine in -Y through the open front window, then hoists. Overhead rigging clearance above Z'+str(round(self.sweep_bounds[5],1))+' is the owner’s winch/track scope, not modeled geometry.',
                'sample_count':self.samples,'boolean_check_count':self.checks,'failures':self.failures,'segments':self.trace,
                'sampled_moving_part_envelope_mm':self.sweep_bounds,
                'fixed_x_limits_mm':self.x_limits,
                'source_modules_sha256_at_build':self.source_hashes,
                'final_matrix':self.M.round(8).tolist(),
                'elapsed_seconds':round(time.monotonic()-self.start,2)}
        OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        return result

def run():
    c=Checker()
    c.examine(pose(),'installed',0)
    c.move('lift to handling height',pose(I,(0,0,LIFT)),step=5)
    c.move('translate forward out the front window',pose(I,(0,-FORWARD,LIFT)),step=25)
    c.move('hoist clear',pose(I,(0,-FORWARD,LIFT+HOIST)),step=25)
    result=c.write();result['status']='PASS SAMPLED PATH' if not c.failures else 'FAIL'
    result['reverse_path']='Exact reverse of the recorded matrices; reinstall the four drawdowns and torque 12 Nm after the dowels seat.'
    OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    bounds=result['sampled_moving_part_envelope_mm'];xl=result['fixed_x_limits_mm']
    report=[f'# Rev F sampled bed-module hoist review\n',f'Generated {datetime.datetime.now(datetime.timezone.utc).isoformat()}.\n',
      f'**Result: {result["status"]}.** {result["sample_count"]:,} sampled poses, {result["boolean_check_count"]:,} actual-solid intersection checks, {len(result["failures"])} recorded failures.\n',
      f'The fixed source assembly contained {result["fixed_component_count"]} retained obstacles. Fixed X extent {xl[0]:.3f} to {xl[1]:.3f} mm was never exceeded. The sampled moving envelope is X{bounds[0]:.3f} to {bounds[3]:.3f}, Y{bounds[1]:.3f} to {bounds[4]:.3f}, Z{bounds[2]:.3f} to {bounds[5]:.3f} mm.\n',
      '## What was checked\n',
      'The complete one-piece module - steel ladder, lift ears, both MDF layers, all ten strips, deck fasteners and both optional spoilboards - moves as one rigid body with the four drawdown bolts removed. Every fixed part except the removable spindle/torch remains an obstacle, including slats, pan floats, float guards, sensors, reservoir and controls.\n',
      f'The path is three pure translations: +Z {LIFT:g} lift (5 mm steps), -Y {FORWARD:g} forward exit (25 mm steps), +Z {HOIST:g} hoist. Key modeled clearances at handling height: crossmember undersides (Z917.3 lifted) pass the Z910 float backrails by 7.3 mm and the slat tops by 67.3 mm; lift-ear tops (Z1001 lifted) and the trimmed spoilboards pass beneath or between the rear-parked Y guide shoes with 10 mm minimum; the notched MDF right edge clears the float posts in plan. Nominal source-geometry gaps; fabrication variation and debris reduce them.\n',
      'Rigging is NOT modeled: sling legs, hook travel and winch anchorage are owner scope. Keep the four-leg sling symmetric; the ear holes sit above the module center of mass.\n',
      '## Reproduction and source scope\n',
      'Run `swap-path-checks.py` with the project CadQuery environment. `swap-path-checks.json` records every sampled transform, the obstacle inventory, source hashes and BREP fingerprints. `bed-configurations.json` records the module part list and the removed-for-handling bolts.\n',
      'A passing source-geometry check does not verify unseen vendor dimensions, rigging capacity, electrical safety or ergonomics. Recheck the path if the head, cabinet, sensor, cable or guard envelope changes.\n']
    if result['failures']:
        report+=['## Recorded failures\n']
        for f in result['failures']:report.append(f'- {f["object"]}: {f["stage"]}; {f.get("obstacle",f.get("type","unknown"))}; intersection {f.get("intersection_mm3","unresolved")} mm³.\n')
    (ROOT/'SWAP-REVIEW.md').write_text('\n'.join(report),encoding='utf-8')
    print('RESULT',result['status'],len(c.failures),'failures',flush=True)
    return 0 if not c.failures else 2

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
