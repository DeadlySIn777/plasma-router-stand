"""Check actual source housing/supports against all four ER11 capacity tools."""
import hashlib,json,os,sys
from pathlib import Path
import actual_atc as A
from build_atc import static

def run():
    files=[Path(__file__),Path(A.__file__),A.HERE/'build_atc.py',A.VENDOR_HOUSING_SOURCE]
    digest=lambda:{p.relative_to(A.ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
    before=digest();checks={}
    for label,t,hood in [('DEPLOYED',0,'stored'),('TRANSIT',100,'stored'),('PARKED',200,'fitted')]:
        tools=[q for q in A.acceptance_parts(t)if q[0].startswith('ATC_RETAINED_ER11_')]
        checks[label]=static(A.actual_atc_parts(t,hood=hood)+tools)
    gaps=[A.POCKET_X[0]-10.5-(A.MOUNT_X[0]+14),A.MOUNT_X[1]-14-(A.POCKET_X[-1]+10.5)]
    report=dict(source_sha256=before,checks=checks,
        capacity=dict(tool_nut_envelope_diameter_mm=21,manufacturer_ER11_nut_max_OD_mm=19.5,
            manufacturer_ER11_cutting_tool_max_diameter_mm=15,radial_allowance_mm=.75,
            below_body_base_projection_mm=26.35,left_right_arm_lateral_gaps_mm=gaps),
        source_consistent=before==digest(),actual_ER11_socket_or_loaded_tool_geometry_verified=False,
        scope='ExactBRepstaticcheckswithfourexplicitcapacitycylinders;whole-kitpurpleboxexcludedbecauseitduplicatesactualhousing. Physicalsocket/IR,nutengagementandreceivedrevisionremaincalibration/fitgates.',
        fabrication_release=False,operating_release=False)
    report['passed']=report['source_consistent']and min(gaps)>=2-1e-8 and all(q['passed']for q in checks.values())
    (A.HERE/'output/er11-retained-capacity-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],checks={k:v['passed']for k,v in checks.items()},arm_gaps_mm=gaps)),flush=True)
    return 0 if report['passed']else 2

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
