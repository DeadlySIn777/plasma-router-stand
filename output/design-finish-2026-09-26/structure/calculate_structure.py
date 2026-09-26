"""Executable nominal-member and connection calculations for the current stand.
Units: N, mm, MPa. This is an explicit engineering model, not a whole-machine rating.
"""
from pathlib import Path
import sys,os,json,math,hashlib
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
sys.path.insert(0,str(SOURCE))
import cadquery as cq
from build_revh import build_model,stored_model
from cad_helpers import bbox,validate
from bed_details import profile_20100
import structure_finish
OUT=Path(__file__).resolve().parent
E=200000.;EA=69000.;G=E/2.6

def square(b,t,rounded=True):
    s=cq.Workplane('XY').box(b,b,1,centered=False)
    if rounded:s=s.edges('|Z').fillet(2*t)
    v=cq.Workplane('XY').box(b-2*t,b-2*t,3,centered=False)
    if rounded:v=v.edges('|Z').fillet(t)
    sh=s.val().cut(v.val().translate((t,t,-1))).clean()
    area=sh.Volume();i=cq.Shape.matrixOfInertia(sh)[0][0]-area/12
    return {'b':b,'t':t,'A':area,'I':i,'J_thinwall':(b-t)**3*t,'corner_model':'outer2t/inner1t; no credit for sand'}

def point(f,l,e,i,c):
    return {'F_N':f,'L_mm':l,'delta_mm':f*l**3/(48*e*i),'stress_MPa':f*l*c/(4*i)}

def cantilever(f,l,e,i,c):
    return {'F_N':f,'L_mm':l,'delta_mm':f*l**3/(3*e*i),'stress_MPa':f*l*c/i}

def weld_group(force,moment,radius,leg=3):
    throat=leg/math.sqrt(2);area=2*math.pi*radius*throat;section=math.pi*radius**2*throat
    # Conservative addition of direct shear and bending traction magnitudes.
    stress=force/area+moment/section;allowable=.6*(70*6.894757293)/2
    return {'force_N':force,'moment_Nmm':moment,'radius_mm':radius,'leg_mm':leg,'effective_area_mm2':area,'stress_sum_MPa':stress,'E70_ASD_screen_MPa':allowable,'allowable_over_demand':allowable/stress}

def weld_rectangle(force,moment,b,h,leg=3):
    throat=leg/math.sqrt(2);area=2*(b+h)*throat;section=throat*(b*h*h/2+h**3/6)/(h/2)
    stress=force/area+moment/section;allowable=.6*(70*6.894757293)/2
    return {'force_N':force,'moment_Nmm':moment,'perimeter_mm':[b,h],'leg_mm':leg,'stress_sum_MPa':stress,'E70_ASD_screen_MPa':allowable,'allowable_over_demand':allowable/stress}

def sources():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in list(SOURCE.glob('*.py'))+[Path(__file__)]}

# Explicit nominal densities for current registered handling assemblies.
# Unknown materials fail instead of receiving a density from a part-name prefix.
NOMINAL_DENSITY_KG_MM3={
    'Purchased6063T5profile':2.7e-6, 'Aluminum alloy unverified':2.7e-6,
    'Steel M5x16':7.85e-6, 'Steel washer':7.85e-6, 'Steel square nut':7.85e-6,
    'Low carbon steel':7.85e-6, 'Steel M3 flat point set screw':7.85e-6,
    'A5002x2x.120tube':7.85e-6, 'A36 steel':7.85e-6,
    'Machined steel':7.85e-6, 'Hardened steel pin':7.85e-6,
    'Steel tube OD10 ID6.6':7.85e-6,
}


def handling_mass_inventory(model,kind,count):
    import bed_cassettes as bc
    assemblies=[]
    for index in range(count):
        members=[p for p in model.parts if bc._PLACEMENTS.get(p.id,('',-1))[:2]==(kind,index)]
        assert members,(kind,index)
        rows=[]
        for p in members:
            if p.material not in NOMINAL_DENSITY_KG_MM3:raise ValueError(('Unassigned nominal material density',p.id,p.material))
            rho=NOMINAL_DENSITY_KG_MM3[p.material];volume=p.shape.Volume()
            rows.append({'id':p.id,'part_number':p.part_number,'material':p.material,
                         'volume_mm3':volume,'density_kg_per_mm3':rho,'mass_kg':volume*rho})
        assemblies.append({'kind':kind,'index':index,'part_count':len(rows),'parts':rows,'nominal_mass_kg':sum(p['mass_kg'] for p in rows)})
    assigned=[p['id'] for a in assemblies for p in a['parts']]
    group='bed_panel' if kind=='panel' else 'bed_beam'
    assert len(assigned)==len(set(assigned))
    assert set(assigned)=={p.id for p in model.parts if p.group==group},('Handling/group membership mismatch',kind)
    return assemblies


def main():
    before=sources()
    if "--integrated" in sys.argv:
        from build_revi import build_model as builder,stored_model as storer
        m,meta=builder()
    else:
        storer=stored_model;m,meta=build_model();structure_finish.extend_router_model(m)
    profile=profile_20100(397);pa=profile.Volume()/397
    ip=cq.Shape.matrixOfInertia(profile)[0][0]/397-pa*397**2/12
    assert abs(ip-27207.732888568193)<.01
    assert len([p for p in m.parts if p.id.startswith('G_BEAM_') and p.id[7:].isdigit()])==4
    assert abs(bbox(m.find('G_BEAM_1').shape)[3]-bbox(m.find('G_BEAM_1').shape)[0]-924)<1e-6
    assert abs(bbox(m.find('G_RACK_PANEL_SEAT_1').shape)[2]-167)<1e-6
    assert abs(bbox(m.find('H_PANEL_HOOP_ROD_1').shape)[3]-bbox(m.find('H_PANEL_HOOP_ROD_1').shape)[0]-14)<1e-6
    panel_inventory=handling_mass_inventory(m,'panel',6)
    beam_inventory=handling_mass_inventory(m,'beam',4)
    panel_mass=[a['nominal_mass_kg'] for a in panel_inventory]
    beam_mass=[a['nominal_mass_kg'] for a in beam_inventory]
    steel_parts=[p for p in m.parts if p.group=='main_frame']
    min_mass=sum(p.shape.Volume()*7.85e-6 for p in steel_parts)
    min_cg=[sum(p.shape.Volume()*p.shape.Center().toTuple()[i] for p in steel_parts)/sum(p.shape.Volume() for p in steel_parts) for i in range(3)]
    report={'status':'CONDITIONAL NOMINAL MEMBER AND JOINT DESIGN; NOT FULL TOOL-TO-WORK RIGIDITY QUALIFICATION',
      'source_sha256':before,'builder':'build_revi.build_model' if '--integrated' in sys.argv else 'build_revh plus structure_finish','geometry':{'parts':len(m.parts),'20100_area_mm2':pa,'20100_Ivertical_mm4':ip,'panel_mass_estimates_kg':panel_mass,'beam_mass_estimates_kg':beam_mass,'panel_mass_inventory':panel_inventory,'beam_mass_inventory':beam_inventory,'handling_mass_basis':'Exact current bed_cassettes placement membership; explicit material density per component, no ID-prefix density. Nominal solids omit unmodeled weld beads and actual stock variation.','main_frame_only_mass_kg':min_mass,'main_frame_only_CG_mm':min_cg},
      'design_basis':{'routing':'Light wood/plastics routing; not metal milling or crash loads','tool_force_N':100,'proposed_static_tool_work_target_mm':.20,'service_stock_kg':25,'local_downward_accidental_load_N':500,'gross_mass_upper_kg':650,'storage_single_rod_horizontal_N':100,'retention_acceleration_g':.5,'E_steel_MPa':E,'E_aluminum_MPa':EA,'steel_yield_screen_MPa':245,'rod_required_yield_MPa':300,'6063T5_lip_yield_screen_MPa':110,
      'conditions':['All six feet adjusted in contact and jammed. Sound welds; square frame and matched seat shims.','The0.20 mm target is a proposed acceptance criterion, not demonstrated cutting accuracy.','Unknown scrap has no assigned certified yield or wall. Sensitivities below are conditional; measure clean remaining wall.','Static member calculations exclude dynamics, joint microslip, bearing preload, local tube-wall distortion and actual purchased head/module compliance.']},
      'vertical_member_chain':[]}
    for nominal,t,desc in [(3.048,3.048,'nominal CAD wall'),(3.048,.93*3.048,'A500 design wall'),(2,2,'measured2.0 remaining wall sensitivity'),(1.5,1.5,'measured1.5 remaining wall sensitivity')]:
        sec=square(50.8,t);beam=point(100,874,E,sec['I'],25.4);ledger=point(100,699.6,E,sec['I'],25.4)
        strip=point(100,397,EA,ip,10);seat=cantilever(100,36.4,E,50.8*6**3/12,3)
        torsion=100*61.8**2*699.6/(4*G*sec['J_thinwall'])
        total=sum(x['delta_mm'] for x in (beam,ledger,strip,seat))+torsion
        report['vertical_member_chain'].append({'wall_basis':desc,'nominal_wall_mm':nominal,'section':sec,'one_strip':strip,'one_bed_beam':beam,'one_ledger':ledger,'one_overhanging_seat':seat,'ledger_eccentric_torsion_mm':torsion,'identified_member_sum_mm':total,'remaining_budget_mm':.20-total,
            'interpretation':'Deliberately assigns the entire100 N to each member, full397 mm strip span,874 mm beam support-center span and699.6 mm leg-center span. No MDF composite/load-sharing credit. This is a component sum, not a global finite-element solution or a bound on omitted interfaces.'})
    sec=square(50.8,.93*3.048);br=square(25.4,.93*2.1082)
    braces=[]
    for name,a,b in [('side',598.8,689.2),('rear',998.4,689.2)]:
        l=math.hypot(a,b);n=100*l/a;k=E*br['A']/l*(a/l)**2;pcr=math.pi**2*E*br['I']/l**2
        braces.append({'name':name,'horizontal_mm':a,'vertical_mm':b,'length_mm':l,'axial_demand_N':n,'ideal_k_N_per_mm':k,'Euler_pinned_N':pcr,'Euler_over_demand':pcr/n,'yield_stress_MPa':n/br['A'],'ideal100N_sway_mm':100/k,'ten_percent_joint_efficiency_sensitivity_mm':100/(.1*k),'weld_two50mm_edges_shear_MPa':n/(2*50*3/math.sqrt(2))})
    report['chassis']={'braces':braces,'brace_network':'Side pair in series on each side, two sides in parallel gives one-member k for equal bays; rear brace alone gives X shear stiffness. Welded frame, gusset/leg bending, brace end eccentricity and floor-slip are not replaced by this ideal axial calculation.','vertical_member_500N':point(500,874,E,sec['I'],25.4),'leg_max_gravity_stress_MPa':(650*9.80665/3)/sec['A'],'leg_Euler_pinned_949_2_N':math.pi**2*E*sec['I']/949.2**2}
    # Member checks for the real workholding/load-bearing joints.
    dowel=6;pin_force=500;pin_bend=pin_force*4/(math.pi*dowel**3/32)
    report['locators']={'single_pin_proof_force_N':pin_force,'pin_shear_MPa':pin_force/(math.pi*dowel**2/4),'pin_bending_MPa':pin_bend,'seat_bearing_MPa':pin_force/(6*4),'conditional_yield_reserve':245/pin_bend,'nominal_full_diametral_clearance_mm':.03,'scope':'One round left locator carries X/Y; relieved right locator carries Y. Capacity is checked without friction. Actual hardened pin retention,6.03 bore fit and full4 mm engagement must match.'}
    report['preloads']={'beam_M8_N':[2000,4000],'front_seat_M8_N':[2000,4000],'panel_clamp_M6_N':[800,1000],
      'spoil_M5':'UNRELEASED pending actual extrusion coupon. Qualification starting range50..75 N; combined preload plus local uplift must remain<=175 N under this lip screen.',
      'M8_at4000_tensile_MPa':4000/36.6,'M8_class88_proof_load_N':580*36.6,'M8_sleeve_compression_MPa':4000/(math.pi/4*(18**2-9**2)),
      'M6_panel_at1000_tensile_MPa':1000/20.1,'panel_end_bridge_stress_at1000_MPa':6*1000*11.5/(20*6**2),'panel_end_contact_pressure_at1000_MPa':1000/(20*3.5),
      'panel_friction_min_N':2*800*.15,'front_seat_friction_min_N':2*2000*.15,'minimum_assumed_mu':.15,
      'front_seat_bolt_prying_at500N_reaction_N_each':500*36.4/13.6/2,'torque_rule':'No universal torque substituted. Calibrate actual finish/lubrication/joint using force measurement or tension verification; T=KFd is sensitivity only.'}
    # Strip as infinite beam on two slot-lip elastic foundations; conservative local screen.
    lip_t=1.3;arm=1.95;strip_EI=E*8*2.7**3/12;kfoundation=2*EA*lip_t**3/(4*arm**3);beta=(kfoundation/(4*strip_EI))**.25
    report['slot_lip_screen']={'lip_t_mm':lip_t,'lip_load_centroid_arm_mm':arm,'steel_strip_EI_Nmm2':strip_EI,'foundation_k_N_per_mm2':kfoundation,'beta_per_mm':beta,'effective_peak_load_length_mm':2/beta,
      'stress_per_bolt_N_MPa':1.5*beta*arm/lip_t**2,'75N_preload_lip_stress_MPa':75*1.5*beta*arm/lip_t**2,'175N_combined_lip_stress_MPa':175*1.5*beta*arm/lip_t**2,'yield110_twofold_reserve_force_N':55/(1.5*beta*arm/lip_t**2),
      'result':'UNQUALIFIED: a normal torque-table preload is not justified. Lip/root section and contact foundation are approximated; the reconstructed slot is not supplier-certified. Test the actual extrusion and nut strip before releasing a preload.',
      'coupon_requirement':'Apply350 N upward at each actual M5 station with the same strip/retainers/profile, hold60 seconds, repeat10 times. Require no lip cracking, thread damage or slip, and residual movement<=0.02 mm. This is a proposed acceptance test, not a predicted pass or completed test.'}
    # Storage receiver correction: use a point load on either single rod, without load-sharing credit.
    f=100;free=573.5-215;rod=cantilever(f,free,E,math.pi*14**4/64,7);old=cantilever(f,398.5,E,math.pi*10**4/64,5)
    base_m=f*398.5;seat_stress=(base_m/2)*4/((45-18.2)*8**3/12)
    report['panel_retainer']={'old10mm':old,'new14mm':rod,'new_yield_reserve':300/rod['stress_MPa'],'socket_bearing_force_couple_N':f*free/40,'socket_conservative10mm_end_bearing_MPa':(f*free/40)/(14*10),'socket_weld':weld_group(f,base_m,9.1),
      'seat8mm_net_section_bending_MPa':seat_stress,'seat_assumed_two_sided_restraint':'Moment splits between fore/aft seat strips around the socket; clear28 mm web relief and net width26.8 mm. Verify welded continuity.','seat_yield_reserve':245/seat_stress,
      'web_relief_remaining_height_mm':10.4,'web_shear_from_moment_MPa':(base_m/28)/(6*10.4),'socket_design_fit_mm':[.15,.30],'max_fit_rotation_displacement_mm':.30/40*free,
      'saddle_rod_departure_lift_mm':8.5,'lower_screw_thread_engagement_mm':9,'load_scope':'100 N at a single rod top. No lifting/standing, no collision-energy rating. Elastic rod travel and sliding-fit play are storage containment, not a precision datum.'}
    report['panel_retainer']['socket_bending_MPa']=base_m*(18.2/2)/(math.pi*(18.2**4-14.2**4)/64)
    report['panel_retainer']['socket_yield_reserve']=250/report['panel_retainer']['socket_bending_MPa']
    g=9.80665;foot=650*g/3;root_d=13.546;free_stem=31.3
    tip=100*free_stem/(math.pi*root_d**3/32);stem=cantilever(100,free_stem,E,math.pi*root_d**4/64,root_d/2)
    edge_margin=min(min_cg[0]-25.4,1124.6-min_cg[0]);tipforce=min_mass*g*edge_margin/1255
    report['feet_and_stability']={'one_third_650kg_N':foot,'M16_stress_on157mm2_MPa':foot/157,'M16_31_3mm_stem_100N_lateral':stem,'foot_pad_gross_pressure_MPa':foot/6400,
      'pad_strip_model':'Two opposite halves each take half of foot load over26 mm beyond a28 mm head bearing footprint,80 mm effective width. Assumes full-area support; hard-point floors invalidate this screen.',
      'pad_bending_MPa':6*(foot/2)*26/(80*12.7**2),'closure_weld_direct_shear_MPa':foot/(4*50.8*3/math.sqrt(2)),
      'stationary_main_frame_only_mass_kg':min_mass,'frame_only_X_tipping_force_at1255_N':tipforce,'500N_external_pull_tip_margin':tipforce/500,'sliding_coefficient_required_for500N_on_frame_only':500/(min_mass*g),
      'scope':'Global stability under a500 N external pull is separate from internally balanced cutting force. Full machine mass/CG and floor friction must be measured. Existing optional anchors require site-specific selection; no anchor capacity assumed.'}
    known_groups={'main_frame','feet','bracing','bed_beam','bed_fixed','bed_storage','bed_rack_restraint','bed_temporary_restraint','pan_support','tank_support','water_pan','reservoir','slat_support','slats'}
    known=[p for p in m.parts if p.group in known_groups and not p.purchased and any(x in p.material.lower() for x in ('steel','a500','a36'))]
    known_mass=sum(p.shape.Volume()*7.85e-6 for p in known)
    known_cg=[sum(p.shape.Volume()*p.shape.Center().toTuple()[i] for p in known)/sum(p.shape.Volume() for p in known) for i in range(3)]
    conservative_mass=.85*known_mass
    margin_x=min(known_cg[0]-25.4,1124.6-known_cg[0]);margin_y=min(known_cg[1]-25.4,1424.6-known_cg[1])
    report['feet_and_stability']['known_fabricated_steel']={'part_ids':[p.id for p in known],'CAD_mass_kg':known_mass,'CG_mm':known_cg,'mass_after15percent_deduction_kg':conservative_mass,'tipping_force_X_N':conservative_mass*g*margin_x/1255,'tipping_force_Y_N':conservative_mass*g*margin_y/1255,'minimum_Coulomb_mu_for500N':500/(conservative_mass*g),'scope':'Conditional on nominal specified plate/tube.15 percent mass deduction screens square corners and stock tolerance; this is not valid for arbitrary thin scrap. All purchased parts, water and sand excluded. CG of omitted parts must remain within supports for their omission to be conservative.'}
    report['retaining_hardware']={'stored_beam_total_kg':sum(beam_mass),'beam_stack_point5g_force_N':.5*g*sum(beam_mass),'fourM6_single_shear_MPa':(.5*g*sum(beam_mass)/4)/20.1,'fourM6_twofold_yield_capacity_N':4*20.1*640/(2*math.sqrt(3)),
      'shelf8M6_sleeves':'Sleeves transfer clamp preload through tube walls; thread/nut engagement and welds remain actual-build checks.',
      'temporary_box_gate100N_each_M5_shear_MPa':(100/2)/14.2,'temporary_box_scope':'Geometric containment; beam1 already rests on beam2. No lifting rating; only remove seats after both gates and locators are fitted.'}
    report['weld_demands']={'front_seat_boss500N':weld_group(500,500*36.4,10),
      'panel_fork_root':weld_rectangle(100+.5*g*sum(panel_mass),base_m+.5*g*sum(panel_mass)*75,30,30),
      'beam_stack_shelf':weld_group(.5*g*sum(beam_mass),.5*g*sum(beam_mass)*75,25.4),
      'scope':'Actual circular socket/boss and square30 mm fork groups. The shelf circular-equivalent value is demand scale only, not weld-group certification; use actual accessible weld lengths and local base-metal checks.'}
    scans={}
    for ident,axis,stations in [('G_BEAM_1',0,[123.5,138,400,523.5,575,626.5,950,1012,1026.5]),('MF_RECEIVER_LEDGER_1',1,[25.4,45,65,85,350,478.5,699.6,885.5,1100,1299,1370])]:
        body=m.find(ident).shape;bounds=bbox(body);rows=[]
        for station in stations:
            xyz=[bounds[k]-1 for k in range(3)];dims=[bounds[k+3]-bounds[k]+2 for k in range(3)];xyz[axis]=station-.25;dims[axis]=.5
            knife=cq.Workplane('XY').box(*dims,centered=False).val().translate(tuple(xyz));slice_shape=body.intersect(knife)
            area=slice_shape.Volume()/.5;inertia_axis=1 if axis==0 else 0
            inertia=cq.Shape.matrixOfInertia(slice_shape)[inertia_axis][inertia_axis]/.5-area*.5**2/12
            rows.append({'station_mm':station,'area_mm2':area,'I_vertical_mm4':inertia})
        scans[ident]={'samples':rows,'minimum_sampled_I_mm4':min(r['I_vertical_mm4'] for r in rows)}
    net_beam=point(100,874,E,scans['G_BEAM_1']['minimum_sampled_I_mm4'],25.4)
    net_ledger=point(100,699.6,E,scans['MF_RECEIVER_LEDGER_1']['minimum_sampled_I_mm4'],25.4)
    scans['scope']='0.5 mm slices through actual cut parent tube solids at enumerated critical drill/service-port stations. Minimum sampled section is not a continuous-section optimization. Welded sleeve/boss reinforcement is deliberately excluded.'
    scans['minimum_sampled_I_assigned_over_entire_span_member_sum_mm']=report['vertical_member_chain'][0]['identified_member_sum_mm']-report['vertical_member_chain'][0]['one_bed_beam']['delta_mm']-report['vertical_member_chain'][0]['one_ledger']['delta_mm']+net_beam['delta_mm']+net_ledger['delta_mm']
    report['actual_cut_section_sensitivity']=scans
    report['whole_chain_budget']={'target_mm':.20,'identified_bed_member_mm':report['vertical_member_chain'][1]['identified_member_sum_mm'],'unallocated_mm':.20-report['vertical_member_chain'][1]['identified_member_sum_mm'],
      'unknown_series_compliances':['Actual HGR20 guide/block preload and bolted rail seats','Actual8080 gantry bending/torsion and end brackets','ZBX80 screw/bearings/carriage, measured mounting and adapter','Spindle clamp, spindle bearings, collet/tool and projection','MDF contact, actual20100 profile tolerances and clamp microslip','Welded frame joints, alignment and feet/floor contact'],
      'conclusion':'The known-member screen alone does not establish whole-tool stiffness. A measured series-compliance sum must fit the remaining budget; missing stiffness terms have no invented zero or finite bound.'}
    # Numerical checks independent of the release conclusions.
    b=point(100,397,EA,ip,10)
    assert abs(point(200,397,EA,ip,10)['delta_mm']/b['delta_mm']-2)<1e-10
    assert abs(point(100,794,EA,ip,10)['delta_mm']/b['delta_mm']-8)<1e-10
    assert all(a['identified_member_sum_mm']<b['identified_member_sum_mm'] for a,b in zip(report['vertical_member_chain'],report['vertical_member_chain'][1:]))
    assert report['panel_retainer']['new_yield_reserve']>2
    assert report['panel_retainer']['seat_yield_reserve']>2
    report['arithmetic_checks_pass']=True
    report['static_states']={}
    for name,model in [('router',m),('stored',storer(m))]:
        v=validate(model);report['static_states'][name]={'parts':len(model.parts),'unresolved_intersections':v['unresolved_intersections']};print(name,report['static_states'][name],flush=True)
    report['sources_unchanged']=before==sources();report['nominal_geometry_pass']=all(not v['unresolved_intersections'] for v in report['static_states'].values())
    report['full_machine_rigidity_qualified']=False
    (OUT/'calculations.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'bed_member_mm':report['whole_chain_budget'],'retainer':report['panel_retainer'],'geometry_pass':report['nominal_geometry_pass']},indent=2),flush=True)
    return 0 if report['arithmetic_checks_pass'] and report['nominal_geometry_pass'] else 2
if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
