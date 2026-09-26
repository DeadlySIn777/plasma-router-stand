"""Nine-pose baseline checks for Rev H motion additions; no fabrication release."""
from pathlib import Path
import sys,json,itertools,hashlib,os,traceback,time
REPO=Path(__file__).resolve().parents[3]
SOURCE=REPO/'output/release-review/RevE-ENGINEERING'
sys.path.insert(0,str(SOURCE))
from cad_helpers import Model,validate,bbox,write_dxf
from build_revg import build_model,stored_model
from motion_details import make_motion
from motion_completion import extend_router_model,adapter_local,OutputHole,TorchMeasurement,torch_clamp,static_brake_screen
from verify_revg_motion import clone_fixed
import cadquery as cq

def main():
    out=Path(__file__).resolve().parent
    begin=time.monotonic()
    initial=hashlib.sha256((SOURCE/'motion_completion.py').read_bytes()).hexdigest()
    report={'scope':'Nine full Rev G base poses plus proposed Rev H adapter blank and brake-motor body. Excludes parallel bed/water changes; root integration requires its own check.',
            'source_sha256':initial,'states':[],'checks':{}}
    # The blank contains the four known clamp holes and no unknown carriage holes.
    blank,flat=adapter_local()
    assert len(flat['holes'])==4 and not flat['slots']
    assert blank.isValid() and len(blank.Solids())==1
    tmp=out/'adapter-transfer-blank.dxf';write_dxf(tmp,flat)
    # Explicit synthetic data only checks the API, never represents the user's torch.
    candidate=torch_clamp(TorchMeasurement(30,45,80,.02,'SYNTHETIC_GEOMETRY_CHECK_ONLY',True))
    assert validate(candidate)['unresolved_intersections']==[]
    try:torch_clamp(TorchMeasurement(28,40,60,.02,'',True))
    except ValueError:report['checks']['unmeasured_torch_rejected']=True
    else:raise AssertionError('Missing torch evidence accepted')
    try:adapter_local([OutputHole(10,22,5.5,9,5,'M5',8,'SYNTHETIC')]*4)
    except ValueError:report['checks']['overlapping_output_pockets_rejected']=True
    else:raise AssertionError('Intersecting head pockets accepted')
    report['checks']['adapter_blank_valid']=True
    report['checks']['parametric_clamp_synthetic_geometry_valid']=True
    report['checks']['brake_static_screen']=static_brake_screen(20,downward_external_force_n=200)
    fixed,_=build_model(with_motion=False)
    for gy,hx,z in list(itertools.product((275,1275),(175,975),(0,100)))+[(775,575,50)]:
        m=clone_fixed(fixed);make_motion(m,gantry_y=gy,head_x=hx,z_lift=z)
        meta=extend_router_model(m);r=validate(m)
        rec={'gantry_y':gy,'head_x':hx,'z_lift':z,'parts':len(m.parts),
             'unresolved_intersections':r['unresolved_intersections'],
             'brake_motor_bounds_mm':bbox(m.find('ZBX80_MOTOR').shape),
             'adapter_blank_bounds_mm':bbox(m.find('TOOL_ADAPTER_110').shape)}
        assert all(p.local.isValid() and len(p.local.Solids())==1 for p in m.parts)
        rec['local_world_volume_match']=all(abs(p.local.Volume()-p.shape.Volume())<max(.05,p.shape.Volume()*1e-7) for p in m.parts)
        rec['passed']=not rec['unresolved_intersections'] and rec['local_world_volume_match']
        report['states'].append(rec)
        (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
        print('pose',gy,hx,z,'clear',rec['passed'],flush=True)
    report['source_unchanged']=initial==hashlib.sha256((SOURCE/'motion_completion.py').read_bytes()).hexdigest()
    report['elapsed_seconds']=time.monotonic()-begin
    report['status']='PASS' if all(x['passed'] for x in report['states']) and report['source_unchanged'] else 'FAIL'
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],report['elapsed_seconds'],flush=True)
    return 0 if report['status']=='PASS' else 2

if __name__=='__main__':
    try:result=main()
    except Exception:traceback.print_exc();result=1
    sys.stdout.flush();sys.stderr.flush();os._exit(result)
