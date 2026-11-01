"""Reproducible XR1 analytical component/sensitivity screen, no prices.

This is NOT assembled-frame FEA or an actuator/tool-loop model. Closed-form
elastic idealizations expose governing assumptions and qualification tests.
All forces N, lengths mm, moduli N/mm2. No stiffness is inferred from CAD volume.
"""
from pathlib import Path
import csv,hashlib,json,math,sys
import params as P

G=9.80665
NU_AL=.33
BRACE_NOMINAL_THICKNESS=1.9
BRACE_MINIMUM_SCREEN_THICKNESS=1.8

def point_deflection(force,length,E,I):return force*length**3/(48*E*I)
def cantilever_deflection(force,length,E,I):return force*length**3/(3*E*I)
def uniform_deflection(total_force,length,E,I):return 5*total_force*length**3/(384*E*I)
def tube_I(b,t):return (b**4-(b-2*t)**4)/12
def tube_J_thin_wall(b,t):return t*(b-t)**3

def angle_properties(b=40.,t=5.):
    A=2*b*t-t*t
    z=(b*t*t/2+t*b*b/2-t*t*t/2)/A
    I=b*t**3/12+b*t*(t/2-z)**2+t*b**3/12+t*b*(b/2-z)**2-(t**4/12+t*t*(t/2-z)**2)
    return {'area_mm2':A,'centroid_z_mm':z,'I_vertical_mm4':I,
            'J_thin_wall_mm4':(2*b-t)*t**3/3}

def ledger_case(force_total,L,I,J,eccentricity=30.):
    # Two ledgers share a centred load. Supports restrain twist at each station.
    F=force_total/2
    bend=point_deflection(F,L,P.AL_E_MPA,I)
    Gal=P.AL_E_MPA/(2*(1+NU_AL))
    theta=F*eccentricity*L/(4*Gal*J)
    return {'total_force_N':force_total,'force_per_ledger_N':F,
            'bending_mm':bend,'torsion_load_point_motion_mm':theta*eccentricity,
            'sum_components_mm':bend+theta*eccentricity,
            'assumption':'Fixed twist at each support; actual unrestrained roll/joint slip can be larger.'}

def brace_case(dx,dz):
    L=math.hypot(dx,dz)
    # One of each X pair resists each direction; other strap is not credited.
    t=BRACE_MINIMUM_SCREEN_THICKNESS
    K=P.STEEL_E_MPA*30*t*dx*dx/L**3
    return {'hole_spacing_mm':L,'blank_length_mm':L+30,'active_horizontal_stiffness_N_per_mm':K,
            'force_in_strap_at_100N_horizontal_N':100*L/dx,
            'elastic_displacement_at_100N_mm':100/K,
            'horizontal_deadband_for_0_05mm_at_each_end_mm':.1*L/dx,
            'thickness_used_mm':t,
            'net_section_stress_at_300N_horizontal_MPa':300*L/dx/((30-6.6)*t)}

def tipping_required_mass(moving_mass,moving_y,force,stationary_cg_y=650.,ratio=1.5):
    edge=1410. # rear adjuster centres on the two added base members
    moving_tip=max(0,moving_mass*G*(moving_y-edge))
    force_tip=force*P.UPPER_TOP
    return ratio*(moving_tip+force_tip)/(G*(edge-stationary_cg_y))

def run():
    span=max(b-a for a,b in zip(P.POST_CENTRES_Y,P.POST_CENTRES_Y[1:]))
    overhang=P.Y_LENGTH-P.POST_CENTRES_Y[-1]
    cuts={'posts':[P.POST_LENGTH]*4+[P.POST_LENGTH-80]*2,'headers':[P.Y_LENGTH]*2,
          'pan_bearers':[P.CROSS_LENGTH]*3,'flat_ledger_arms':[75.2]*6,'rear_footbases':[300.]*2}
    total=sum(sum(v) for v in cuts.values())
    # Actual die can be lighter/different; this is the reference MINIMUM target.
    profile_mass=total*.001*P.PROFILE_AREA_MIN_MM2*.0027
    angle=angle_properties(50.8,6.35)
    upper=[]
    for Istrong,Iweak in ((400000.,100000.),(P.PROFILE_I_STRONG_MIN_MM4,P.PROFILE_I_WEAK_MIN_MM4),(976618.,252917.)):
        for moving_mass in (25.,50.,75.):
            F=moving_mass*G/2
            upper.append({'I_strong_mm4':Istrong,'I_weak_mm4':Iweak,'moving_mass_total_kg':moving_mass,
                          'gravity_midspan_mm':point_deflection(F,span,P.AL_E_MPA,Istrong),
                          'gravity_rear_tip_mm':cantilever_deflection(F,overhang,P.AL_E_MPA,Istrong),
                          '100N_vertical_rear_tip_mm':cantilever_deflection(50,overhang,P.AL_E_MPA,Istrong),
                          '100N_transverse_rear_tip_mm':cantilever_deflection(50,overhang,P.AL_E_MPA,Iweak)})
    pan=[]
    for mass in (60.,100.,150.):
        # Total wet table load distributed equally among three X bearers.
        W=mass*G/3
        R=W/2
        t=6.35;b=80.;a=40.;I=b*t**3/12
        pan.append({'wet_load_total_kg':mass,'load_per_bearer_N':W,'end_reaction_N':R,
                    'bearer_midspan_mm':uniform_deflection(W,P.CROSS_LENGTH,P.AL_E_MPA,P.PROFILE_I_STRONG_MIN_MM4),
                    'seat_deflection_at_40mm_projection_mm':cantilever_deflection(R,a,P.AL_E_MPA,I),
                    'seat_bending_stress_MPa':6*R*a/(b*t*t),
                    'per_post_bolt_shear_N':R/2,'per_post_bolt_tension_N':R/2})
    # Minimum bare frame material estimate uses the procurement requirement,
    # geometric plate/angle volumes and steel strap blank lengths; not CAD mass.
    brace_specs={'side_front':brace_case(530,740),'side_rear':brace_case(550,660),
                 'front_low':brace_case(1088.4,240),'rear_high':brace_case(1088.4,725)}
    brace_len=4*brace_specs['side_front']['blank_length_mm']+4*brace_specs['side_rear']['blank_length_mm']+2*brace_specs['front_low']['blank_length_mm']+2*brace_specs['rear_high']['blank_length_mm']
    mass_breakdown={'reference_profile_kg':profile_mass,
        'steel_straps_kg':brace_len*30*BRACE_NOMINAL_THICKNESS*7.85e-6,
        'fishplates_kg':10*80*80*6*2.7e-6,
        'foot_plates_kg':8*40*80*(P.FOOT_PLATE_TOP-P.FOOT_PLATE_BOTTOM)*2.7e-6,
        'pan_angles_kg':6*(80+80-6.35)*6.35*80*2.7e-6,
        'dry_arm_angles_kg':6*(40+32-6.35)*6.35*80*2.7e-6}
    framesum=sum(mass_breakdown.values())
    tipping=[]
    for stationary_cg in (650.,850.):
        for cg in (1355.,1450.):
            for moving in (25.,50.,75.):
                for force in (100.,300.):
                    tipping.append({'moving_mass_kg':moving,'moving_cg_y_mm':cg,'rearward_force_N':force,
                        'assumed_stationary_cg_y_mm':stationary_cg,
                        'required_stationary_mass_kg_for_1_5_moment_ratio':tipping_required_mass(moving,cg,force,stationary_cg)})
    buckling=math.pi**2*P.AL_E_MPA*P.PROFILE_I_WEAK_MIN_MM4/P.POST_LENGTH**2
    # Do not credit six equally loaded legs for minimum three-point support case.
    reaction=[]
    for totalmass in (125.,175.,225.):
        W=totalmass*G
        reaction.append({'total_mass_kg':totalmass,'eight_equal_foot_reaction_N':W/8,
                         'three_point_average_reaction_N':W/3,
                         'screened_one_foot_reaction_N':W/2,
                         'note':'W/2 is a screening load, not a reaction solution; uneven floor can unload feet.'})
    # Thread-root diameter is a sensitivity input, not a measured owned foot.
    root=6.5;exposed=max(0,P.FOOT_PLATE_BOTTOM-6.8-9)
    footI=math.pi*root**4/64
    foot={'assumed_M8_thread_root_diameter_mm':root,'exposed_stud_length_mm':exposed,
          '100N_total_lateral_eight_feet_elastic_mm':cantilever_deflection(100/8,exposed,P.STEEL_E_MPA,footI),
          '100N_total_lateral_three_feet_elastic_mm':cantilever_deflection(100/3,exposed,P.STEEL_E_MPA,footI),
          '200kg_total_three_point_average_axial_stress_MPa':200*G/3/(math.pi*root*root/4),
          'central_nominal_thread_engagement_mm':P.FOOT_PLATE_TOP-P.FOOT_PLATE_BOTTOM-1,
          'holds':['Actual rated foot/stud geometry and nut engagement','M8 central tapped-plate strip/pull-through proof','Two core taps and pad rating','No floor-sliding credit without measured friction/anchorage']}
    here=Path(__file__).resolve().parent
    hashes={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in ('params.py','frame.py','structure_screen.py')}
    out={'revision':P.REVISION,'release':False,'prices_included':False,'source_sha256':hashes,
      'scope':'Closed-form component and sensitivity calculations, NOT assembled-frame FEA or a certified strength result.',
      'load_path_separation':{'cutting':'Apply equal/opposite tool and work reactions for a true relative tool-to-bed stiffness model. Independent component deflections here are sensitivities, not an assembled compliance sum.',
        'external_push':'The100/300N overturning and floor-sliding cases are external pushes, not a net unbalanced cutting force.',
        'gravity':'Moving-assembly and wet-pan gravity cases evaluate sag and support loads separately from cutting compliance.'},
      'section_requirement':{'A_min_mm2':P.PROFILE_AREA_MIN_MM2,'I_strong_min_mm4':P.PROFILE_I_STRONG_MIN_MM4,'I_weak_min_mm4':P.PROFILE_I_WEAK_MIN_MM4,
        'source_name':'MISUMI HFSL8-4080 Light Type (reference requirement, not the selected Amazon die)',
        'source_url':'https://us.misumi-ec.com/pdf/fa/2019/2019_US_2768.pdf',
        'qualification':'Supplier die properties and straightness must meet these requirements. External4080 dimensions alone are insufficient.'},
      'cut_list_mm':cuts,'finished_profile_length_mm':total,
      'mass_screen':{'bare_frame_material_estimate_kg':framesum,'breakdown':mass_breakdown,
        'not_included':'Feet/fasteners, ledgers, pan, slats, storage, dry cassettes, wiring and all owned motion. Estimate is not a weighed machine mass.'},
      'geometry':{'side_post_centres_y_mm':list(P.POST_CENTRES_Y),'header_largest_support_span_mm':span,
                  'rear_cantilever_from_post_centre_mm':overhang,'front_brace_high_edge_nominal_z_mm':375.,
                  'rear_support_edge_foot_centre_y_mm':1410.,
                  'dry_arm_clearance_above_pan_bearer_mm':809.65-P.PAN_BEARER_TOP},
      'upper_header_sensitivity':upper,
      'six_vs_four_posts':{'four_post_largest_span_mm':1080.,'six_post_largest_span_mm':span,
                          'point_load_deflection_span_ratio':(1080./span)**3,
                          'four_post_with_middle_pan_hangers_profile_mm':4*P.POST_LENGTH+2*P.Y_LENGTH+3*P.CROSS_LENGTH+2*(P.UPPER_BOTTOM-P.PAN_BEARER_TOP),
                          'note':'Four posts require a separate middle-bearer load path; a floating middle bearer is invalid.'},
      'wet_pan_bearer_and_seat_cases':pan,
      'dry_ledger':{'span_mm':span,'angle_50_8x50_8x6_35_properties':angle,
                    'angle_cases':[ledger_case(f,span,angle['I_vertical_mm4'],angle['J_thin_wall_mm4']) for f in (100.,300.)],
                    'closed_tube_40x40x3_properties':{'I_mm4':tube_I(40,3),'J_thin_wall_mm4':tube_J_thin_wall(40,3)},
                    'closed_tube_cases':[ledger_case(f,span,tube_I(40,3),tube_J_thin_wall(40,3)) for f in (100.,300.)],
                    'required_support_detail':'Restrict support rotation with positive seats and at least two separated attachment stations across the bearing flange. A loose single attachment is not a fixed-twist support.',
                    'selection':'50.8x50.8x6.35 angle selected, positive seats and4 arm stations each. Closed tube retained only as a comparison.'},
      'dry_flat_arm':{'cantilever_load_arm_mm':66.7,'at_250N_reaction_deflection_mm':cantilever_deflection(250,66.7,P.AL_E_MPA,P.PROFILE_I_WEAK_MIN_MM4),
                       'scope':'Unrelieved reference short4080arm only. The two front tip notches require local section/lip/contact proof; no notch section stiffness is inferred from CAD envelope. Add angle/joint/ledger/cassette compliance separately.'},
      'brace_cases':brace_specs,
      'brace_limits':{'nominal_thickness_mm':BRACE_NOMINAL_THICKNESS,'minimum_screen_thickness_mm':BRACE_MINIMUM_SCREEN_THICKNESS,
                      'width_mm':30,'tension_only':True,'clearance_sensitivity':'0.05mm slip at each end adds roughly0.10–0.17mm of bay racking before elastic action.',
                      'requirements':['Bare steel, not galvanized, in hot exposure','Do not credit compression diagonal','Drill fixed end holes after frame is squared; lock and proof joints','Verify T-slot lip pullout, bolt bearing, net-section and sheet edge quality','No credit for friction before measured joint-slip proof']},
      'column_buckling':{'pinned_pinned_ideal_N':buckling,'cantilever_K2_ideal_N':buckling/4,
                         'note':'Ideal straight elastic column only; joints/feet and lateral sway govern long before this ideal capacity.'},
      'feet':foot,'support_reaction_sensitivity':reaction,
      'rear_tipping_required_stationary_mass_cases':tipping,
      'rear_base_moment_joint':{'external_push_N':100.,'assumed_push_height_mm':P.UPPER_TOP,
           'moment_per_base_Nmm':100*P.UPPER_TOP/2,
           'bolt_row_vertical_separation_mm':50.,
           'horizontal_couple_per_base_N':100*P.UPPER_TOP/2/50,
           'ideal_shared_shear_per_bolt_in_each_row_N':100*P.UPPER_TOP/2/50/4,
           'requirement':'TheY1410 support polygon requires positive post/base moment transfer through both fishplates. Qualify clamp slip, slot lips and plate contact; do not assume a pin joint can engage the rear foot as a stabilizer.'},
      'floor_sliding_sensitivity':[{'total_machine_mass_kg':m,'required_static_friction_mu_at_100N':100/(m*G),
                                    'required_static_friction_mu_at_300N':300/(m*G)} for m in (75.,125.,175.)],
      'side_tipping_stationary_mass_only':{'stationary_cg_x_mm':575.,'foot_centre_support_edges_x_mm':[P.LEFT_X+20,P.RIGHT_X+20],
          'minimum_stationary_mass_at_100N_and_1_5_ratio_kg':1.5*100*P.UPPER_TOP/(G*min(575.-P.LEFT_X-20,P.RIGHT_X+20-575.)),
          'note':'Moving mass inside the support polygon is omitted conservatively. Verify actual X CG and extreme head position.'},
      'stability_limits':['No water ballast may be credited in dry mode.','Stationary CGY650/850 and movingCGY1355/1450 are explicit sensitivities, not measured values.',
                          'Weigh completed stationary and moving assemblies and solve actual reactions.',
                          'Two300mm rear base members add support centresY1410, fixing the previousY1180 support-polygon weakness within the existing plan footprint.',
                          'If actual measurements still fail moment margin, add positive rated floor anchorage before use.',
                          'External300N force is a proof sensitivity, not an allowed unattended service load.','Assembled eight-foot support must be levelled; all feet sharing gravity equally is not guaranteed.'],
      'qualification_tests':[{'test':'Frame and bed static compliance','acceptance':'Apply100N in±X,±Y,±Z at tool location; framework/ledger/dry-bed displacement relative to work datum≤0.30mm. Measure tool-loop separately.'},
         {'test':'Joint slip','acceptance':'After squaring and controlled tightening, reversible±100N loads must not leave permanent datum motion; target≤0.05mm slip per structural joint.'},
         {'test':'Service/proof separation','acceptance':'Test100N service stiffness;300N sensitivity exposes looseness/instability. Select proof procedure and load limits for actual fasteners/profile.'},
         {'test':'Foot loads and tipping','acceptance':'Dry rear/head worst pose: all intended feet remain seated with required overturning margin. Measure mass/CG and floor friction; qualify anchorage if needed.'},
         {'test':'Dynamics','acceptance':'Tap-test completed dry and wet assemblies, measure resonance/damping; avoid cutting settings that excite modes. Natural frequency cannot be inferred from memberI alone.'},
         {'test':'Heat/water','acceptance':'Cold-water leak/drain/overflow test; then thermal test protected storage and aluminum clearances before wood is stored during plasma.'}],
      'front_transfer_notch_hold':{'parts':4,'upright_channel_width_Y_mm':72.8,'upright_cassette_depth_mm':70.8,
          'ledger_station_count':22,'support_detail':'Two front arms retain three ledger stations each, including two X-separated back-row bolts; other arms retain four stations each.',
          'qualification':'Verify local profile wall/slot-lip integrity, pan-seat bearing, notch edge radii, clamp slip andanti-roll response before release. Reference unnotchedI does not qualify the machined tips.'},
      'non_coverage':['Owned gantry, rail blocks, motion modules, screw lead, Z/tooling and spindle bearings','Local T-slot lip bending/pullout and supplier fastener allowables','Actual joint contact/friction, damping, thermal distortion, welded-pan residual stress','Physical transfer human clearance and hose/torch-lead routes; see separate bed/motion audit']}
    folder=Path(__file__).resolve().parent/'review';folder.mkdir(exist_ok=True)
    (folder/'structure-screen.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    sample=next(v for v in upper if v['I_strong_mm4']==P.PROFILE_I_STRONG_MIN_MM4 and v['moving_mass_total_kg']==75)
    lines=[f'# {P.REVISION} structure screen — development, not fabrication release','',
      f'Finished profile: **{total/1000:.4f}m**. Six continuous posts reduce the largest supported header span to{span:.0f}mm; a four-post1080mm span bends{(1080/span)**3:.2f}times as much under an equal midpoint point load.','',
      f'At the conditional minimum section properties,75kg moving mass split across the headers produces an ideal rear-overhang gravity deflection of{sample["gravity_rear_tip_mm"]:.3f}mm per header. A100N transverse service force split between them adds{sample["100N_transverse_rear_tip_mm"]:.3f}mm at the270mm overhang. These are member calculations; they do not include joint or owned motion compliance.','',
      'The selected50.8×50.8×6.35 dry ledgers require torsion restraint. Under100N split across both ledgers, the ideal550mm-span bending plus eccentric-torsion component is'+f'{out["dry_ledger"]["angle_cases"][0]["sum_components_mm"]:.3f}mm, versus{out["dry_ledger"]["closed_tube_cases"][0]["sum_components_mm"]:.3f}mm for40×40×3 closed tube. Four attachment stations per arm restrain support roll; actual joint compliance still needs a test.','',
      f'The bare frame material estimate is{framesum:.1f}kg before feet, hardware, bed, pan, storage and owned motion. Do not use decorative CAD volume as a real weight. The two300mm rear base members move the rear foot centres fromY1180 toY1410. At75kg moving mass/CGY1355, stationaryCGY650 and100N rearward atZ1053, at least{tipping_required_mass(75,1355,100):.1f}kg stationary mass is required for the chosen1.5moment ratio; water ballast is unavailable in dry mode. Actual mass, CG and foot contact must be measured.','',
      'Strap pairs are nominal1.9mm uncoated steel, matching the pan-sheet stock plan. Capacity and elastic compliance use a conservative1.8mm minimum thickness; measure the real sheet. Straps are tension-only. Two0.05mm end slips add approximately0.10–0.17mm of racking before elastic strap action, which can consume much of the0.30mm framework/bed target. Slot lip, joint-slip, foot and assembled tool-loop tests are therefore required.','',
      'Conditional profile properties are taken from the[manufacturer reference table](https://us.misumi-ec.com/pdf/fa/2019/2019_US_2768.pdf). They are procurement requirements, not properties attributed to an unverified Amazon die.','',
      'See structure-screen.json for all loads, formulas, sensitivities, limitations and acceptance tests. No pricing is included.']
    (folder/'STRUCTURE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'finished_profile_m':total/1000,'reference_bare_frame_material_kg':framesum,'rear_tip75kg_mm':sample['gravity_rear_tip_mm'],
                      'angle100N_total_mm':out['dry_ledger']['angle_cases'][0]['sum_components_mm'],
                      'tube100N_total_mm':out['dry_ledger']['closed_tube_cases'][0]['sum_components_mm'],
                      'required_stationary_mass_75kg_CGY1355_100N_kg':tipping_required_mass(75,1355,100),'release':False},indent=2))
    return out

def write_fabrication():
    """Part-level review takeoff; requires the same CadQuery environment as build.

    These rows are NOT released machining drawings. Named locations describe
    nominal CAD; all profile slot/core and rated hardware interfaces are held.
    """
    from frame import frame_parts,design_metadata,ARM_BOTTOM
    folder=Path(__file__).resolve().parent/'review';folder.mkdir(exist_ok=True)
    rows=[];parts=frame_parts()
    for name,s,_ in parts:
        b=s.BoundingBox();dims=[b.xlen,b.ylen,b.zlen]
        origin=[b.xmin,b.ymin,b.zmin]
        category='';material='';blank='';holes='';note='Nominal development geometry; no fabrication/CAM release.'
        if '_EX_' in name:
            category='4080 extrusion';material='Al profile, qualified section/slot/core'
            if '_POST_' in name:L=b.zlen;orientation='40X x80Y, continuous vertical'
            elif '_DRY_ARM_' in name:L=b.xlen;orientation='80Y x40Z, short flat arm'
            elif '_PAN_X_' in name:L=b.xlen;orientation='40Y x80Z, strong axis vertical'
            else:L=b.ylen;orientation='40X x80Z, strong axis vertical'
            blank=f'4080 x{L:.3f}; {orientation}'
            holes='T-slot attachment stations only; four front/middle post bottoms need2x M8 end-core taps each.' if '_POST_' in name else 'No invented supplier mounting holes.'
        elif 'FOOT_PLATE' in name:
            category='Flat plate';material='Al, verified alloy/temper';blank='80Y x40X x9.525'
            cy=(b.ymin+b.ymax)/2
            rowsY=[1390,1427] if cy==1410 else [cy-20,cy+20]
            base=name.endswith(('3A','3B'))
            holes=f'CentreM8 tap atX{b.xmin+20:.3f}/Y{cy:.3f}; '+('2x dia6.6 to bottom T-slot' if base else '2x dia8.5 to M8 post end cores')+f' atY{rowsY}'
            note='Centre nominal CAD dia8 is thread envelope: drill6.8/tapM8. Nominal engagement8.525. Proof thread strip, foot rating and locknut bearing.'
        elif 'FISHPLATE' in name:
            category='Flat plate';material='Al, verified alloy/temper';blank='80Y x80Z x6'
            holes='4x dia6.6; localY20/60 x localZ10/60 (same pattern for top and rear-base plates).'
        elif 'PAN_BEARING_ANGLE' in name:
            category='One-piece bearing angle';material='Al angle, minimum6.35 thickness';blank='80 wide x80 horizontal leg x80 vertical leg x6.35'
            holes='2x dia6.6 post face:worldYcentre±20, Z686.5;2x dia6.6 seat:35/65 from post inner face, Ycentre.'
            note='Require real one-piece formed/purchased angle. Qualify bend radius, seats and bolt capacities; two unwelded touching plates are not equivalent.'
        elif 'DRY_ARM_ANGLE' in name:
            category='One-piece bearing angle';material='Al angle, minimum6.35 thickness';blank='80 wide x40 horizontal leg x32 vertical leg x6.35'
            holes=f'2x dia6.6 post face:worldYcentre±20,Z{ARM_BOTTOM-20:.3f};2x dia6.6 arm-bottom at25 from post/Ycentre±20.'
            note='One-piece angle required; cropped vertical leg keeps3.15mm nominal clearance above pan bearer.'
        elif '_SIDE_X_' in name or '_END_X_' in name:
            category='Tension strap';material='Uncoated steel sheet1.9mm nominal;1.8mm minimum structural screen'
            # The rounded strap length is the in-plane bbox diagonal of its
            # hole span plus30mm; recover hole span from known endpoint rules.
            if '_SIDE_X_' in name:
                bay=int(name.split('_')[-2]);dx,dz=((530,740) if bay==1 else (550,660))
            else:dx,dz=(1088.4,240 if '_FRONT_' in name else 725)
            span=math.hypot(dx,dz)
            blank=f'{span+30:.3f} x30 x1.9, rounded15radius ends'
            holes=f'2x dia6.6:centre spacing{span:.3f},15mm end distance.'
            note='Paired tension-only X braces. Drill after squaring; qualify preload/slip and sheet edge quality. Front nominal top edge375.'
        elif 'SPACER' in name:
            category='Brace spacer';material='Steel/Al metal bearing spacer';blank='OD18 x3'
            holes='Dia6.6 through; one3mm spacer at each end of every offset diagonal.'
        elif 'LOCKNUT' in name:
            category='Rated hardware allowance';material='Steel';blank='M8 nut nominal6.8 high'
            holes='M8 thread nominal CAD envelope.'
            note='Verify actual foot locknut dimensions and bearing; not a custom fabrication instruction.'
        elif 'RATED_FOOT' in name:
            category='Rated hardware allowance';material='Rated M8 adjuster/steel pad';blank='PadOD50.8 x9; studtipZ68.5'
            holes='Rated M8 adjuster; central tapped plate retains stud; underside nut bears plate.'
            note='Actual rated part, exposed stud, pad friction and adjustment travel require verification.'
        else:raise ValueError(name)
        if name in ('XR_EX_DRY_ARM_L_1','XR_EX_DRY_ARM_R_1','XR_PAN_BEARING_ANGLE_L_1','XR_PAN_BEARING_ANGLE_R_1'):
            notch='X108..132' if '_L_' in name else 'X1018..1042'
            note+=f' FRONT CHANNEL NOTCH:world{notch},Y59..72.8,throughpartZ; qualify local section/slot lip, seats andedge radii.'
        rows.append([name,category,1,material,blank,json.dumps([round(v,4) for v in origin]),holes,note])
    stations=[('TOP_FISHPLATE_M6',24,'M6 +washer +matching slot nut','4 per plate; length/grip after actual slot-nut stack verification.'),
       ('REAR_BASE_FISHPLATE_M6',16,'M6 +washer +matching slot nut','4 per plate; continuous post stands directly on base.'),
       ('PAN_BEARING_ANGLE_M6',24,'M6 +washer +matching slot nut','2 post+2 bearer per angle.'),
       ('DRY_ARM_BEARING_ANGLE_M6',24,'M6 +washer +matching slot nut','2 post+2 arm per angle.'),
       ('BRACE_DIRECT_M6',12,'M6 +washer +matching slot nut','1.9mm nominal strap stack; do not reuse long screw without checking bottoming.'),
       ('BRACE_STANDOFF_M6',12,'M6 +washer +matching slot nut','1.9mm nominal strap+3mm spacer; check nut engagement and bottoming.'),
       ('FRONT_MID_FOOT_CORE_M8',8,'M8 capscrew+washer','4 plates;2 tapped post cores per foot. Exact length/tap depth HOLD.'),
       ('REAR_FOOT_BASE_M6',8,'M6 +washer +matching slot nut','4 plates;2 lower-rail-slot attachments each;9.525mm plate grip.'),
       ('RATED_M8_ADJUSTER',8,'Rated M8 adjuster+locknut','Quantity includes two new rear support stationsY1410.'),
       ('LEDGER_TO_ARM_M6_BED_SCOPE',22,'M6 +washer +matching slot nut','Bed-agent scope:3 per front arm (omitXY116/80 and1034/80),4 per other arm. Front backrow retains2X-separated bolts foranti-roll; avoid double count.')]
    for name,qty,material,note in stations:
        rows.append([name,'Hardware station allowance',qty,material,'Length not released','',note,'Supplier slot/thread/stack measurements required.'])
    with (folder/'frame-fabrication.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['id','category','quantity','material','finished_blank_or_allowance_mm','world_bbox_min_mm','holes_or_stations','qualification']);w.writerows(rows)
    report=design_metadata();report['part_rows']=len(parts);report['hardware_station_rows']=len(stations)
    here=Path(__file__).resolve().parent
    hashes={n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in ('params.py','frame.py','structure_screen.py')}
    report['source_sha256']=hashes
    report['station_rows_are_not_additional_physical_parts']='Do not double-count named rated-hardware allowances with the corresponding station group.'
    (folder/'frame-fabrication-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    bad=[n for n,s,_ in parts if not s.isValid() or s.Volume()<=0]
    bounds=[]
    for _,s,_ in parts:
        b=s.BoundingBox();bounds.append([b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax])
    checked=0;hits=[]
    for i,(na,sa,_) in enumerate(parts):
        for j in range(i+1,len(parts)):
            if not all(min(bounds[i][k+3],bounds[j][k+3])-max(bounds[i][k],bounds[j][k])>1e-5 for k in range(3)):continue
            checked+=1;v=sa.intersect(parts[j][1]).Volume()
            if v>.05:hits.append({'a':na,'b':parts[j][0],'volume_mm3':v})
    check={'revision':P.REVISION,'parts':len(parts),'invalid_parts':bad,'exact_pairs':checked,
           'positive_intersections':hits,'source_sha256':hashes,'release':False,
           'scope':'Exact frame-self intersections only; thread envelopes and external assembly interactions need separate evidence.'}
    (folder/'frame-self-check.json').write_text(json.dumps(check,indent=2)+'\n',encoding='utf-8')
    assert not bad and not hits,check
    print('Wrote frame-fabrication.csv:',len(parts),'physical part rows plus',len(stations),'hardware station groups.')
    print('Frame self-check:',len(parts),'valid parts,',checked,'exact pairs,',len(hits),'positive intersections.')

if __name__=='__main__':
    run()
    if '--fabrication' in sys.argv:
        write_fabrication()
        # Local OCP runtime has an unrelated interpreter-teardown fault.
        import os
        sys.stdout.flush();sys.stderr.flush();os._exit(0)
