"""Analytic XR2 ATC crossbeam point-couple screen, standard-library only.

Run after check_atc.py and atc_fabrication.py:
    python variants/extrusion-reengineered/atc_stiffness.py

'passed' means calculation and input/source consistency. It never means
physical rigidity, joint capacity, real magazine alignment or fabrication release.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import sys
import params as P

HERE=Path(__file__).resolve().parent
REPORT=HERE/'review'/'atc-stiffness.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def candidate_extrema(a,L):
    """All x extrema for a couple at a on a simply-supported span L."""
    C=(L-a)**2/(2*L)-L/6
    xs=[0.,a,L]
    if C<=0:
        x=math.sqrt(max(0.,-2*L*C))
        if 0<=x<=a:xs.append(x)
    discriminant=L*L-2*L*(a+C)
    if discriminant>=0:
        for x in(L-math.sqrt(discriminant),L+math.sqrt(discriminant)):
            if a<=x<=L:xs.append(x)
    return sorted(set(xs))

def f(x,a,L):
    return x**3/(6*L)-max(0.,x-a)**2/2+x*((L-a)**2/(2*L)-L/6)

def extremes_at(a,L,M,EI,left):
    rows=[dict(x_from_left_pin_mm=x,world_X_mm=left+x,
               deflection_mm=M/EI*f(x,a,L))for x in candidate_extrema(a,L)]
    return dict(couple_at_world_X_mm=left+a,couple_a_mm=a,
                candidates=rows,worst=max(rows,key=lambda r:abs(r['deflection_mm'])))

def source_value(source_map,name):
    candidates=[v for k,v in source_map.items()if k.replace('\\','/').split('/')[-1]==name]
    return candidates[0]if len(candidates)==1 else None

def run(torque_Nm):
    files=[Path(__file__),HERE/'params.py',HERE/'atc.py',HERE/'motion.py',
           HERE/'check_atc.py',HERE/'review'/'atc-check.json',
           HERE/'review'/'atc-manufacturing.json']
    if any(not p.exists()for p in files):
        raise FileNotFoundError('Run the geometry and manufacturing generators before this screen.')
    sources=lambda:{p.relative_to(HERE).as_posix():sha(p)for p in files}
    start=sources()
    mfg=json.loads((HERE/'review'/'atc-manufacturing.json').read_text())
    geo=json.loads((HERE/'review'/'atc-check.json').read_text())
    byid={r['id']:r for r in mfg['custom_exports']}
    leftrow=byid['ATC_LOCK_DEPLOY_PIN'];rightrow=byid['ATC_R_LOCK_DEPLOY_PIN']
    centre=lambda r:r['world_origin_mm'][0]+r['finished_world_aligned_size_mm'][0]/2
    left,right=centre(leftrow),centre(rightrow);L=right-left
    beam=next(r for n,r in byid.items()if n.startswith('ATC_MOVING_RHS_'))
    beam_length,B,H=beam['finished_world_aligned_size_mm']
    area=beam['finished_volume_mm3']/beam_length
    #Uniform square-corner RHS: A=BH-(B-2t)(H-2t).
    t=((B+H)-math.sqrt((B+H)**2-4*area))/4
    inner_B,inner_H=B-2*t,H-2*t
    I=(H*B**3-inner_H*inner_B**3)/12
    E=P.STEEL_E_MPA;EI=E*I;M=torque_Nm*1000
    pocket=mfg['runtime_interface_metadata']['pocket_centre_acceptance_XY_mm']
    amin,amax=pocket[0]-left,pocket[2]-left
    if not(0<amin<=amax<L and min(E,I,t,B,H)>0 and 2*t<min(B,H)):
        raise ValueError('The pocket field, supports or RHS section is inconsistent.')
    endpoints=[extremes_at(a,L,M,EI,left)for a in(amin,amax)]
    worst=max((dict(load_world_X_mm=r['couple_at_world_X_mm'],**r['worst'])for r in endpoints),key=lambda r:abs(r['deflection_mm']))
    center=extremes_at(L/2,L,M,EI,left)
    center_expected=abs(M)*L*L/(72*math.sqrt(3)*EI)
    boundary_error=max(abs(M/EI*f(x,a,L))for a in(amin,L/2,amax)for x in(0,L))
    #Verify the independent closed-form centre result and exact end conditions.
    math_pass=(abs(abs(center['worst']['deflection_mm'])-center_expected)<1e-10 and boundary_error<1e-10)
    mfg_bound=all(source_value(mfg.get('source_sha256',{}),n)==sha(HERE/n)for n in('atc.py','motion.py','params.py'))
    geo_bound=all(source_value(geo.get('source_sha256',{}),n)==sha(HERE/n)for n in('atc.py','motion.py','params.py','check_atc.py'))
    geometry_current=bool(geo.get('source_consistent_during_check')and geo.get('mechanism_geometry_pass')and geo.get('selectedZ_clearance_case_pass')and geo_bound)
    end=sources();consistent=start==end
    r=dict(revision=P.REVISION,generated_UTC=datetime.now(timezone.utc).isoformat(),
        passed=bool(math_pass and mfg_bound and mfg.get('passed')and mfg.get('source_unchanged')and geometry_current and consistent),
        pass_scope='Calculation checks, current geometry/manufacturing input binding and unchanged input files only.',
        screen_only=True,physical_target_pass=None,physical_rigidity_qualified=False,release=False,
        source_sha256=end,source_consistent_during_check=consistent,
        geometry_check_current=geometry_current,geometry_check_source_binding=geo_bound,
        manufacturing_source_binding=mfg_bound,calculation_checks_pass=math_pass,
        input_geometry=dict(left_pin_world_X_mm=left,right_pin_world_X_mm=right,support_span_mm=L,
            accepted_pocket_X_mm=[pocket[0],pocket[2]],load_position_a_mm=[amin,amax],
            actual_RHS_length_mm=beam_length,outer_depth_Y_mm=B,outer_height_Z_mm=H,
            inferred_uniform_wall_mm=t,section_area_mm2=area,I_vertical_axis_mm4=I,E_assumed_MPa=E),
        load_model=dict(reversible_Z_couple_Nm=[-torque_Nm,torque_Nm],positive_case_Nmm=M,
            support_model='Two ideal translational supports at the deployed pin centres; unrestricted beam rotation, no support settlement.',
            member_model='One uniform prismatic RHS section over the full pin span. The actual shorter tube and its end adapters/joints are not a qualified equivalent assembly.',
            application='One concentrated in-plane couple at an accepted pocket X; not an envelope for every possible distributed magazine/contact load.'),
        analytic_derivation=dict(
            displacement='v=(M/EI)*(x^3/(6L)-max(0,x-a)^2/2+x*((L-a)^2/(2L)-L/6))',
            x_stationary_left='x=sqrt(-2LC), C=(L-a)^2/(2L)-L/6, include only 0<=x<=a.',
            x_stationary_right='x=L +/- sqrt(L^2-2L(a+C)), include only a<=x<=L.',
            load_position_extrema='For positive M, df/da=-x*(L-a)/L for x<a, and -a*(1-x/L) for x>a. Both are nonpositive throughout 0<=x,a<=L. Thus every x displacement is monotone in a; global positive/negative extrema over the pocket field occur at its endpoint load positions. Reversing M reverses signs only.',
            boundary_deflection_error_mm=boundary_error),
        endpoint_load_cases=endpoints,center_only_case=center,
        center_only_beam_deflection_mm=center_expected,
        worst_case=worst,worst_pocket_beam_deflection_mm=abs(worst['deflection_mm']),
        old_check_atc_value_disposition='The approximately0.01486mm value in the geometry check is a centre-couple component case only. This source-bound report supersedes any interpretation of it as the worst over the accepted pocket field.',
        nominal_alignment_reference_mm=.2,
        alignment_disposition='No whole-assembly or physical0.2mm target pass is inferred from this component calculation.',
        excluded_compliance=['magazine housing/endcaps and nut pocket','aluminum U bridge and risers','frame/backbar/cradle flexibility','end adapters, welds and bolted joints','guide/contact play','pin/lug fits and seating','thermal drift','actual measured material/section properties','dynamic spindle and tool-change forces'],
        acceptance='Measure reversible loaded alignment and repeatability at every actual pocket, under actual change torque, before releasing automatic operation.')
    REPORT.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:r[k]for k in('passed','calculation_checks_pass','geometry_check_current','worst_pocket_beam_deflection_mm','center_only_beam_deflection_mm','physical_rigidity_qualified')}))
    return 0 if r['passed']else 1

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--torque-nm',type=float,default=19.)
    a=ap.parse_args()
    if a.torque_nm<=0:ap.error('torque must be positive')
    try:code=run(a.torque_nm)
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.exit(code)

