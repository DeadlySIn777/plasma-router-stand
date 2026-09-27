"""Bounded hand-calculation screens; not a substitute for measured load ratings."""
from pathlib import Path
import json,hashlib,sys,os,math
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE))
import build
m,meta=build.build();moving=set(meta['moving_ids']);mass=0;fabricated=0
for p in m.parts:
 if p.purchased:continue
 rho=2700 if p.material.startswith('Aluminum') else 7850
 weight=p.shape.Volume()*1e-9*rho;fabricated+=weight
 if p.id in moving:mass+=weight
E=200000;P=150;L=863;b=25.4;h=50.8;t=3.175
I=(b*h**3-(b-2*t)*(h-2*t)**3)/12
stress=P*L*h/(8*I);deflection=P*L**3/(48*E*I)
Am=(b-t)*(h-t);J=4*Am**2/(2*((b-t)+(h-t))/t)
nut_torque=19000;Iw=(h*b**3-(h-2*t)*(b-2*t)**3)/12
nut_stress=(nut_torque/2)*(b/2)/Iw
nut_slope=nut_torque*L/(12*E*Iw)
nut_deflection=nut_torque*L**2/(72*math.sqrt(3)*E*Iw)
eccentricity=50;eccentric_torque=P*eccentricity
torsion_tau=eccentric_torque/(2*Am*t);torsion_angle=eccentric_torque*L/(77000*J)
Irail=33*12.7**3/12
# Tip force at120mm; reduced5mm station begins65.2mm after the support.
def integral(a,b):return ((120-a)**3-(120-b)**3)/3
piecewise_rail=75/E*(integral(0,120)/Irail+integral(65.2,70.2)*(1/(33*6.8**3/12)-1/Irail))
# Deliberately pessimistic entire120mm cantilever at the notched6.8mm thickness.
Ir=33*6.8**3/12;rail_stress=75*120*3.4/Ir;rail_deflection=75*120**3/(3*E*Ir)
r={'scope':'Elastic screening of nominal sound A36 welded carrier under stated assumed loads; weld fatigue, scrap defects, guide ratings, actuator speed force and actual magazine loads are not qualified.', 'assumptions':{'carrier_vertical_load_N':150,'collet_reaction_torque_Nm':19,'torque_source':'RapidChange manufacturer FAQ advertises approximately14ftlb; selected kit and actual reaction still require confirmation','steel_E_MPa':E,'steel_G_MPa':77000,'assumed_minimum_yield_MPa':250,'allowable_stress_screen_MPa':250/3,'lock_shear_design_load_N':300,'aluminum_density_kg_m3':2700,'steel_density_kg_m3':7850},'fabricated_mass_kg':fabricated,'moving_fabricated_mass_kg':mass,'excluded_mass':'Purchased rails, blocks, motor, springs, fasteners and actual magazine/tools; not total machine or complete carriage mass.', 'crossbeam':{'I_mm4':I,'bending_stress_MPa':stress,'midspan_deflection_mm':deflection,'torsion_shear_MPa':torsion_tau,'vertical_load_eccentricity_mm':50,'eccentric_vertical_load_torque_Nm':7.5,'conservative_twist_degrees_over_863mm':math.degrees(torsion_angle),'at_50mm_offset_displacement_mm':50*torsion_angle},'vertical_spindle_nut_torque_about_Z':{'torque_Nm':19,'weak_axis_I_mm4':Iw,'max_bending_stress_MPa':nut_stress,'max_transverse_deflection_mm':nut_deflection,'center_rotation_degrees':math.degrees(nut_slope),'at50mm_offset_mm':50*nut_slope},'railbar_notch_pessimistic_screen':{'section_mm':[33,6.8],'cantilever_mm':120,'load_N':75,'stress_MPa':rail_stress,'deflection_mm':rail_deflection,'actual_reduction_length_mm':5,'piecewise_I_deflection_mm':piecewise_rail},'pin':{'diameter_mm':6,'engagement_mm':4,'single_shear_stress_MPa':300/(math.pi*6**2/4),'receiver_bearing_MPa':300/(6*4)},'M6_bracket_fasteners':{'one_pair_per_support':True,'assumed_load_per_support_N':25,'eccentricity_mm':95.6,'couple_distance_mm':16.5,'separate_local_moment_assumption_Nmm':5000,'tension_per_bolt_N':25/2+5000/16.5,'M6_tensile_area_mm2':20.1,'nominal_tension_stress_MPa':(25/2+5000/16.5)/20.1},'actuator':{'holding_torque_Nm':.44,'assumed_screw_efficiency':.3,'ideal_static_thrust_from_holding_N':2*math.pi*.44*.3/.008,'running_thrust_qualified':False},'repeatability':{'nominal_pin_diametral_clearance_mm':[.05,.078],'qualification_target_mm':.05,'rule':'Approach the same positive stop flank under limited motor preload, engage pin only when aligned; verify every pocket after installation. Pin clearance alone is not pocket calibration.'}}
r['deformation_budget']={'scalar_sum_named_effects_mm':deflection+50*torsion_angle+nut_deflection+50*nut_slope+piecewise_rail,'target_for_review_mm':.2,'not_machine_acceptance':'Conservative component screens; does not include rail preload, weld/joint compliance, actual magazine mount, Z module, spindle tram or repeatability. Bench-calibrate pockets and actual load loop.'}
r['passed']=max(stress,rail_stress,nut_stress)<250/3
r['stiffness_qualified']=False
r['source_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'build.py',HERE/'lock.py',HERE/'sensors.py']}
(HERE/'structure-check.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2),flush=True);os._exit(0 if r['passed'] else 2)

