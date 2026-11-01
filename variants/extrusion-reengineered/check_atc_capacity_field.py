"""Exact box-expansion proof of parked ATC capacity versus the cutting field.

These are declared supplier/tool design volumes, not an installed magazine.
For a fixed box B and independent translation box T, B-T is exactly a box.
Checking the actual reference moving solid against B-T covers every translation.
"""
from pathlib import Path
import hashlib,json,os,sys,math
import cadquery as cq
import atc,motion,params as P
from cad_helpers import bbox

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def box(b):return cq.Solid.makeBox(*(b[k+3]-b[k]for k in range(3)),cq.Vector(*b[:3]))
def run():
    upstream_path=HERE/'review'/'atc-check.json'
    upstream=json.loads(upstream_path.read_text(encoding='utf-8'))
    upstream_current=True
    for n,digest in upstream['source_sha256'].items():
        p=ROOT/n
        if not p.exists():p=HERE/n
        if not p.exists()or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:upstream_current=False
    upstream_pass=bool(upstream_current and upstream.get('source_consistent_during_check')
        and upstream.get('mechanism_geometry_pass')and upstream.get('selectedZ_clearance_case_pass'))
    paths=[Path(__file__),HERE/'atc.py',HERE/'motion.py',HERE/'params.py',Path(atc.guide_source.__file__),upstream_path]
    paths.extend(ROOT/n for n in motion.interface_metadata()['source_sha256'])
    paths=list(dict.fromkeys(paths))
    hashes=lambda:{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
    start=hashes()
    x,y,z=575.,775.,P.Z_TRAVEL/2
    parts=motion.motion_parts(False,y,x,z)
    meta=atc.interface_metadata();pmax=meta['loaded_tool_projection_P_mm'][1]
    spindle=next(s for n,s,c in parts if n=='TOOL_SPINDLE_65x259')
    parts.append(('DECLARED_LOADED_TOOL_CAPACITY_P50_D15',atc.cyl(meta['loaded_tool_radius_mm']*2,pmax,
        (x,y-153.6,bbox(spindle)[2]-pmax)),(1,0,0)))
    capacity=atc.acceptance_parts(False)
    records=[];box_clear=0;minimum=None;invalid=[]
    for n,s,c in parts:
        if not s.isValid():invalid.append(n)
        cls='Y_X_Z_tool'if n.startswith('DECLARED_')else motion.part_motion_class(n)
        span={'stationary':(0.,0.,0.),'Y_gantry_or_drive':(0.,P.Y_TRAVEL/2,0.),
              'Y_X_head':(P.X_TRAVEL/2,P.Y_TRAVEL/2,0.),
              'Y_X_Z_tool':(P.X_TRAVEL/2,P.Y_TRAVEL/2,P.Z_TRAVEL/2)}[cls]
        a=bbox(s)
        for nf,sf,cf in capacity:
            b=bbox(sf);expanded=[b[k]-span[k]for k in range(3)]+[b[k+3]+span[k]for k in range(3)]
            gaps=[max(0.,a[k]-expanded[k+3],expanded[k]-a[k+3])for k in range(3)]
            bound_gap=math.sqrt(sum(q*q for q in gaps))
            if minimum is None or bound_gap<minimum['gap_mm']:
                minimum=dict(moving=n,capacity=nf,gap_mm=bound_gap)
            if bound_gap>.01:box_clear+=1;continue
            obstacle=box(expanded)
            vol=s.intersect(obstacle).Volume();distance=s.distance(obstacle)
            records.append(dict(moving=n,capacity=nf,motion_class=cls,
                half_translation_mm=span,expanded_capacity_bounds_mm=expanded,
                intersection_mm3=vol,distance_mm=distance,passed=vol<1e-7 and distance>.01))
    end=hashes()
    report=dict(revision=P.REVISION,passed=start==end and upstream_pass and not invalid and all(r['passed']for r in records),
        source_consistent_during_check=start==end,source_sha256=end,invalid_parts=invalid,
        upstream_ATC_mechanism_check_pass=upstream_pass,upstream_ATC_sources_current=upstream_current,
        upstream_ATC_check_sha256=hashlib.sha256(upstream_path.read_bytes()).hexdigest(),
        reference_X_Yguide_Zlift_mm=[x,y,z],reference_tool_Y_mm=y-153.6,
        loaded_tool_capacity_projection_mm=pmax,loaded_tool_capacity_radius_mm=meta['loaded_tool_radius_mm'],
        parked_capacity=[dict(id=n,bounds_mm=bbox(s))for n,s,c in capacity],
        broad_phase_clear_pairs=box_clear,exact_candidate_pairs=len(records),exact_records=records,
        minimum_broad_bound_gap=minimum,release=False,
        scope='Continuous independent nominal XYZ translation of every physical wood motion part and declared P50/radius7.5 cutter capacity against both parked supplier-kit and retained-tool capacity boxes. Gate pose does not change these capacity boxes. Exact B-T box expansion; this does not establish actual vendor pocket fit, nut datum, tool release or an executable M6 cycle.')
    (HERE/'review'/'atc-capacity-field-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],broad_pairs=box_clear,exact_pairs=len(records),failed=[r for r in records if not r['passed']])),flush=True)
    return 0 if report['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
