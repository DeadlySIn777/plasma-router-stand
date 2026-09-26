"""Local CAD and arithmetic checks; deliberately does not release a machine."""
from pathlib import Path
import hashlib,json,math,sys,os
import numpy as np
import cadquery as cq
import locator_dock as d
from cad_helpers import validate,intersection_volume,bbox,export,plate,rect,cyl

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sources():
    paths=[HERE/'locator_dock.py',HERE/'verify_location.py',d.LEGACY/'cad_helpers.py']
    paths += [HERE/'source-data.json']
    return {str(p.relative_to(d.ROOT)):sha(p) for p in paths}

def constraints(meta):
    rows=[]; scale=max(meta['panel_size_mm'])
    def row(n,p):return list(n)+list(np.cross(np.array(p)/scale,n))
    for q in meta['supports'][:3]:rows.append(row((0,0,1),(*q['center_mm'],14)))
    a,b=meta['centers_mm'];rows += [row((1,0,0),(*a,14)),row((0,1,0),(*a,14))]
    dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy)
    rows.append(row((-dy/L,dx/L,0),(*b,14)))
    rank=int(np.linalg.matrix_rank(np.array(rows)))
    return {'rows_6dof':rows,'rank':rank,'passed':rank==6,
            'note':'Only three primary seats included; fourth support fitted after datum setting, not a seventh independent constraint.'}

def checks(meta):
    W,L=meta['panel_size_mm'];pitch=meta['pitch_mm']
    # Primary supplier limits, mm. Pressing may change bore; installed inspection mandatory.
    pin=(9.986,9.995);bush=(10.013,10.028)
    cd_min=bush[0]-pin[1];cd_max=bush[1]-pin[0]
    a=meta['centers_mm'][0]
    rmax=max(math.hypot(x-a[0],y-a[1]) for x,y in [(0,0),(W,0),(0,L),(W,L)])
    # Conservative extreme-to-extreme free-play bound, not statistical repeatability.
    return_bound=cd_max+2*cd_max*rmax/pitch
    selected_clearance=.025
    selected_bound=selected_clearance+2*selected_clearance*rmax/pitch
    alpha_al=13.1e-6*1.8  # Hydro6061 /degF -> /K
    alpha_hdpe=6.5e-5*1.8  # Ensinger US /degF -> /K
    alpha_steel=12e-6  # engineering sensitivity assumption, not a specific scrap certificate
    temp=20
    metal_differential=pitch*(alpha_al-alpha_steel)*temp
    # HDPE uses central low-force restraint and radial slots at every perimeter screw.
    hdpe_radius=math.hypot(W,L)/2
    hdpe_differential=hdpe_radius*(alpha_hdpe-alpha_al)*temp
    # 1.5x1in rectangular tube, 1/8in wall, vertical height1.5in.
    b=25.4;h=38.1;t=3.175;E=69000
    I=(b*h**3-(b-2*t)*(h-2*t)**3)/12
    span=L-50;F=100
    tube_deflection=F*span**3/(48*E*I)
    # 6.35 backing sheet, conservative50mm effective strip, 150mm maximum clear span.
    bp_t=6.35;bp_b=50;bp_span=150
    bp_I=bp_b*bp_t**3/12
    plate_deflection=F*bp_span**3/(48*E*bp_I)
    plate_stress=1.5*F*bp_span/(bp_b*bp_t**2)
    # Pins transfer lateral load independent of friction. 300N/pin is a local screen
    # enclosing the100N serviceforce plus simple planar moment allocation.
    pin_load=300;shank=6;lever=9
    bend=32*pin_load*lever/(math.pi*shank**3)
    shear=4*pin_load/(math.pi*shank**2)
    # Upper contact begins2mm above pedestal, straight head contact remaining10mm.
    pressure=pin_load/(10*10)
    return {'supplier_fit':{'pin_10g6_mm':pin,'installed_bush_10F7_mm':bush,
                            'diametral_clearance_mm':[cd_min,cd_max],
                            'clearance_only_extreme_to_extreme_corner_return_bound_mm':return_bound,
                            'target_mm':.15,'target_demonstrated':False,
                            'catalog_worst_fit_establishes_combined_target':False,
                            'candidate_measured_maximum_paired_clearance_mm':selected_clearance,
                            'selected_fit_clearance_only_bound_mm':selected_bound,
                            'selected_fit_remaining_combined_error_allowance_mm':.15-selected_bound,
                            'selected_fit_accepted':False,
                            'note':'Bound excludes swarf, wear, face error, joint slip, manufacturing error and temperature; target requires20 actual clean re-seats.'},
      'thermal':{'temperature_change_K':temp,'alpha_al_perK':alpha_al,'alpha_hdpe_perK':alpha_hdpe,'alpha_steel_assumption_perK':alpha_steel,
                 'panel_pin_pitch_mm':pitch,'metal_pin_pitch_differential_mm':metal_differential,
                 'required_measured_diamond_relief_each_direction_mm':.20,
                 'diamond_relief_supplier_certified':False,
                 'hdpe_vs_carrier_max_radial_shift_mm':hdpe_differential,
                 'hdpe_slot_spec':'M5 screws with OD8 metal compression limiters in12x9 radial slots; OD18 counterbore also radially elongated. Limiters stop .10mm above measured local plastic thickness; steel cap washer bears on limiter, not a crushing clamp on HDPE.',
                 'slot_available_radial_travel_mm':2,
                 'slot_margin_mm':2-hdpe_differential,
                 'four_by_eight_HDPE_steel_differential_over2438p4_mm':2438.4*(alpha_hdpe-alpha_steel)*temp},
      'local_load_screen':{'service_horizontal_N':100,'service_downward_point_N':100,'service_uplift_N':100,'load_height_above_metal_land_mm':100,
                  'tube_section_mm':[b,h,t],'tube_second_moment_mm4':I,'tube_simple_support_span_mm':span,'tube_deflection_mm':tube_deflection,
                  'backing_plate_mm':bp_t,'maximum_backing_clear_span_mm':bp_span,'backing_effective_strip_mm':bp_b,
                  'backing_deflection_mm':plate_deflection,'backing_bending_stress_MPa':plate_stress,
                  'local_member_deflection_sum_mm':tube_deflection+plate_deflection,
                  'actual_carrier_joints_and_grid_included':False,'full_machine_stiffness_qualified':False,
                  'pin_design_screen_load_N':pin_load,'pin_shank_bending_stress_MPa':bend,'pin_shank_mean_shear_MPa':shear,
                  'nominal_head_bearing_MPa':pressure,'pin_strength_rating_verified':False,
                  'clamp_preload_per_station_N':[600,900],'clamp_reaction_path':'M6 screw -> steel washer -> steel carrier landing -> hard seat -> rigid grid; HDPE absent from preload loop.',
                  'minimum_four_clamp_preload_N':2400,'first_order_max_uplift_at_one_support_N':100+100*100/(min(W,L)-50),
                  'lateral_transfer':'Pins -> steelcartridge -> twoØ4matchdowels -> metalcarrier/grid; do not credit friction. Full chassis/support joints still require design.'},
      'small_existing_machine':{'front_removable_seat_precision_return':False,'six_20100_panel_precision_return':False,
                  'evidence':'bed_cassettes.py front seat twoØ8.5M8clearanceholes; perbeamØ6round/relievedlocators return only to seats; panels have frictionclamps and noXYlocators.',
                  'required_interfaces':['positively locate each removable front seat to frame','locate each individual metalpanel/cassette to supported beams','preserve existingbeamremoval, storage, torchtravel and spoilboardreach'],
                  'candidate_integrated':False},
      'sensors':{'dock_present_sensor_proves_pin_seating':False,'dock_present_sensor_proves_clamp_preload':False}}

def extraction(m):
    """Exact continuous vertical extrusion of the three constant-section moving
    part types after all four drawbolts/washers have been removed. This proves
    the local interface only; no missing carrier is silently inferred.
    """
    fixed=[p for p in m.parts if p.group=='locator_fixed']
    motions=[]
    for p in m.parts:
        if p.group!='locator_carrier':continue
        bb=bbox(p.shape); dz=35
        if p.id.endswith('_RECEIVER'):
            f=p.flat;s=plate(f['outline'],12+dz,f['holes']).translate((bb[0],bb[1],bb[2]))
        elif p.id.endswith('_BUSH'):
            center=p.shape.Center();s=cyl(15,12+dz).cut(cyl(d.BUSH_ID,12+dz)).translate((center.x,center.y,bb[2]))
        elif p.id.endswith('_LAND'):
            s=plate(rect(40,40),12+dz,slots=[(20,20,12,9,0)]).translate((bb[0],bb[1],bb[2]))
        else:raise ValueError(p.id)
        clashes=[]
        for q in fixed:
            v=intersection_volume(s,q.shape)
            if v>.02:clashes.append({'fixed':q.id,'swept_intersection_mm3':v})
        motions.append({'part':p.id,'translation_mm':[0,0,dz],
                        'sweep_method':'Exact constant-section prismatic sweep',
                        'clashes':clashes,'passed':not clashes})
    return {'passed':all(x['passed'] for x in motions),'motions':motions,
            'scope':'Only receiver/land/bush removal from fixed localdock after bolts+washers removed; integration mustproveactualcarrier/grid/machine/handmotion.',
            'screw_removal_paths_included':False}

def main():
    before=sources();m,meta=d.build_dock();protected,_=d.build_protected_dock()
    normal=validate(m);park=validate(protected);arithmetic=checks(meta);constraint=constraints(meta);path=extraction(m)
    out=HERE/'output';out.mkdir(exist_ok=True)
    export(m,out,'common-locator-dock',individual=True)
    export(protected,out/'protected','common-locator-protected',individual=True)
    report={'source_sha256_before':before,'source_sha256_after':sources(),
      'installed_static':normal,'protected_static':park,'kinematic_constraints':constraint,
      'local_extraction':path,'calculations':arithmetic,
      'component_geometry_checks_passed':not normal['unresolved_intersections'] and not park['unresolved_intersections'],
      'machine_integrated':False,'full_machine_release':False,'repeatability_qualified':False}
    report['source_current']=report['source_sha256_before']==report['source_sha256_after']
    report['local_verification_passed']=report['component_geometry_checks_passed'] and constraint['passed'] and path['passed'] and report['source_current']
    (out/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    (out/'interface.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    print(json.dumps({k:report[k] for k in ('local_verification_passed','source_current','machine_integrated','full_machine_release','repeatability_qualified')}),flush=True)
    return 0 if report['local_verification_passed'] else 1

if __name__=='__main__':
    code=main();sys.stdout.flush();sys.stderr.flush();os._exit(code)
