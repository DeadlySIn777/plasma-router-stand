"""XR1 dry-cassette/slat analytical screen. No FEA, prices or load certification.

Reads selected dimensions from bed.py syntax without importing its CAD module.
Source consistency, ideal elastic targets and physical qualification are separate.
"""
from pathlib import Path
import ast,hashlib,json,math
import params as P
from structure_screen import angle_properties,ledger_case,cantilever_deflection

HERE=Path(__file__).resolve().parent
OUT=HERE/'review'
SPAN=1032.5-117.5
E_PLY_BASE=4000.
E_PLY_WEAK=2500.
STIFFNESS_FACTOR=.75
G_CORE=400.
SHEAR_FACTOR=5/6
WEB_COUNT_CREDITED=5
LOAD_PATCH=25.
SERVICE_TARGET=.30
SLAT_MIN_THICKNESS=1.8
G=9.80665

def source_values():
    tree=ast.parse((HERE/'bed.py').read_text(encoding='utf-8'))
    values={};pocket_ends=[];cabinet_notches=[]
    for node in tree.body:
        if not isinstance(node,ast.Assign):continue
        try:value=ast.literal_eval(node.value)
        except (ValueError,TypeError):continue
        for target in node.targets:
            if isinstance(target,ast.Name):values[target.id]=value
            elif isinstance(target,ast.Tuple) and isinstance(value,(tuple,list)):
                for name,v in zip(target.elts,value):
                    if isinstance(name,ast.Name):values[name.id]=v
    # Validate the shallow pull does not cut the second front web. Its load
    # path was a real design issue before the depth changed30.1 ->14.1.
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id!='box' or len(node.args)!=6:continue
        try:z,w,depth,h=[ast.literal_eval(a) for a in node.args[2:]]
        except (ValueError,TypeError):pass
        else:
            if abs(z-378.)<1e-8 and abs(w-22.02)<1e-8 and abs(depth-3.02)<1e-8:
                cabinet_notches.append([z,z+h])
        try:y,z,w,depth,h=[ast.literal_eval(a) for a in node.args[1:]]
        except (ValueError,TypeError):continue
        if abs(y+.1)<1e-8 and abs(z-22)<1e-8 and abs(w-80)<1e-8 and abs(h-20)<1e-8:
            pocket_ends.append(y+depth)
    return values,pocket_ends,cabinet_notches

def section(B,H,T,width,web_width,nwebs,track_width,groove_depth):
    # Geometric signed rectangles, no credit for Al track/tubes or MDF wear.
    rects=[{'name':'bottom_skin','w':width,'h':B,'z':B/2,'sign':1},
           {'name':'top_skin','w':width,'h':T,'z':B+H+T/2,'sign':1},
           {'name':'credited_webs','w':nwebs*web_width,'h':H,'z':B+H/2,'sign':1},
           {'name':'two_top_track_grooves','w':2*track_width,'h':groove_depth,
            'z':B+H+T-groove_depth/2,'sign':-1}]
    A=sum(r['sign']*r['w']*r['h'] for r in rects)
    zbar=sum(r['sign']*r['w']*r['h']*r['z'] for r in rects)/A
    I=sum(r['sign']*(r['w']*r['h']**3/12+r['w']*r['h']*(r['z']-zbar)**2) for r in rects)
    topQ=sum(r['sign']*r['w']*r['h']*(r['z']-zbar) for r in rects if r['name'] in ('top_skin','two_top_track_grooves'))
    return {'area_mm2':A,'neutral_axis_from_bottom_mm':zbar,'I_mm4':I,
            'top_skin_first_moment_mm3':topQ,'signed_rectangles':rects}

def local_skin(force,span,E,t,thin_end_length=0.,thin_t=None):
    I=LOAD_PATCH*t**3/12
    base=force*span**3/(48*E*I)
    # At the largest bay adjacent to a track, the groove extends5mm beyond
    # its supporting web. Account for this short thinner segment at one end.
    extra=0.
    if thin_end_length and thin_t:
        It=LOAD_PATCH*thin_t**3/12
        extra=force*thin_end_length**3/(12*E)*(1/It-1/I)
    return {'patch_width_mm':LOAD_PATCH,'clear_span_mm':span,'full_skin_thickness_mm':t,
            'thin_segment_at_one_support_mm':thin_end_length,'thin_segment_thickness_mm':thin_t,
            'regular_point_strip_mm':base,'short_groove_segment_extra_mm':extra,
            'deflection_mm':base+extra,
            'max_regular_strip_bending_stress_MPa':(force*span/4)*(t/2)/I,
            'patch_average_bearing_stress_MPa':force/(LOAD_PATCH**2),
            'scope':'Conservative25mm-wide strip with a midpoint point force. Actual plate distribution, grain and notch stresses are not qualified.'}

def cassette_case(force,Eraw,c,sec,skin_span,thin_length):
    E=Eraw*STIFFNESS_FACTOR
    EI=E*sec['I_mm4']
    bend=force*SPAN**3/(48*EI)
    As=WEB_COUNT_CREDITED*c['WEB']*c['CORE']
    shear=force*SPAN/(4*SHEAR_FACTOR*G_CORE*As)
    local=local_skin(force,skin_span,E,c['TOP'],thin_length,c['TOP']-6.35)
    M=force*SPAN/4
    neutral=sec['neutral_axis_from_bottom_mm'];height=c['BOTTOM']+c['CORE']+c['TOP']
    V=force/2
    q=V*sec['top_skin_first_moment_mm3']/sec['I_mm4']
    return {'force_N':force,'raw_plywood_E_MPa':Eraw,'effective_E_MPa':E,'core_G_MPa':G_CORE,
        'EI_Nmm2':EI,'global_bending_mm':bend,'web_shear_mm':shear,'local_top_skin':local,
        'cassette_component_sum_mm':bend+shear+local['deflection_mm'],
        'global_extreme_skin_stress_MPa':M*max(neutral,height-neutral)/sec['I_mm4'],
        'core_average_shear_stress_MPa':V/As,'core_peak_shear_factor1_5_MPa':1.5*V/As,
        'top_skin_to_web_shear_flow_N_per_mm':q,
        'nominal_required_glueline_shear_MPa':q/(WEB_COUNT_CREDITED*c['WEB']),
        'cassette_only_service_target_met':force<=P.WOOD_FORCE_N and bend+shear+local['deflection_mm']<=SERVICE_TARGET,
        'allowable_strength_comparison':'None: actual ply, adhesive, grain and moisture/temperature durability remain unqualified.'}

def slat_cases(nominal,overall_length):
    L=435.;h=40.;t=SLAT_MIN_THICKNESS;E=P.STEEL_E_MPA
    I=t*h**3/12;W=150*G/(8*2)
    uniform={'description':'150kg distributed among8slats and2equal spans each; no single-slat concentration',
             'load_per435mm_span_N':W,'deflection_mm':5*W*L**3/(384*E*I),
             'bending_stress_MPa':(W*L/8)*(h/2)/I,'support_reaction_per_span_end_N':W/2}
    F=200.
    point={'description':'200N at midpoint ofone435mm slat span',
           'deflection_mm':F*L**3/(48*E*I),'bending_stress_MPa':(F*L/4)*(h/2)/I,
           'support_reaction_per_span_end_N':F/2}
    return {'count':8,'overall_length_mm':overall_length,'supports_x_mm':[140.,575.,1010.],
            'span_mm':L,'height_mm':h,'nominal_thickness_mm':nominal,'screen_minimum_thickness_mm':t,
            'I_vertical_mm4':I,'distributed150kg_case':uniform,'single200N_case':point,
            'individual_elastic_target_mm':.30,
            'individual_cases_within_elastic_target':max(uniform['deflection_mm'],point['deflection_mm'])<=.30,
            'table_load_rating_qualified':False,
            'scope':'Slat members only. No credit here for comb/floor welds, pan plate, shims, bearer joints or the full table. Slats are plasma supports, not the routing/clamping bed.',
            'requirements':['Verify actual thickness>=1.8mm and material grade','Qualify actual comb contacts, slot clearance and weld/standoff load path',
                            'Check local edge bearing and concentrated workpiece placement','No generic mild-steel yield allowable or floor strength is asserted']}

def cabinet_strip_case(notches):
    t=3.;b=25.;A=b*t;I=b*t**3/12
    lengths=[hi-lo for lo,hi in notches]
    free=max(lengths) if lengths else None
    braces=[378.,410.,500.,600.,690.,704.]
    segment=max(b-a for a,b in zip(braces,braces[1:]))
    pinned=lambda L:math.pi**2*P.AL_E_MPA*I/L**2
    return {'load_path':'Cabinet stands on its own four floor columns. Rear links resist tipping only, not normal gravity. No cabinet ballast credit to main frame.',
        'section_width_mm':b,'section_thickness_mm':t,'area_mm2':A,'I_weak_mm4':I,
        'source_return_flange_notches_z_mm':notches,'unrestrained_length_mm':free,
        'ideal_unrestrained_pinned_Euler_N':pinned(free) if free else None,
        'ideal_unrestrained_K2_Euler_N':pinned(free)/4 if free else None,
        'assumed_side_skin_lateral_restraint_z_mm':braces[1:-1],
        'longest_assumed_braced_segment_mm':segment,
        'ideal_segment_pinned_Euler_N':pinned(segment),'ideal_segment_K2_Euler_N':pinned(segment)/4,
        'gravity_reaction_sensitivity':[{'cabinet_plus_contents_kg':m,'four_equal_column_reaction_N':m*G/4,
                                         'three_contact_average_N':m*G/3} for m in (25.,50.,75.)],
        'qualified':False,
        'requirements':['Do not treat thin skin or blind rivets as perfect buckling restraints without joint/lateral-restraint qualification',
            'Verify actual25x25x3 angle material, cut edge radius/quality and remaining weak strip',
            'Verify floor contact/levelling, shelf/skin rivet bearing, local wall buckling and actual loaded cabinet mass',
            'Proof rear anti-tip links and rivets independently; they must not suspend cabinet gravity loads'],
        'scope':'Ideal straight elastic strip sensitivities only. No allowable load rating, imperfection, local plate or complete cabinet stability calculation is asserted.'}

def run():
    c,pocket_ends,cabinet_notches=source_values()
    required=('BOTTOM','CORE','TOP','WEAR','WEB','WEB_CENTRES','TRACK_W','TRACK_CENTRES','SLAT_T','SLAT_LENGTH','SLAT_X0')
    assert all(k in c for k in required),'Missing explicit bed.py input'
    height=sum(c[k] for k in ('BOTTOM','CORE','TOP','WEAR'))
    spans=[b-a-c['WEB'] for a,b in zip(c['WEB_CENTRES'],c['WEB_CENTRES'][1:])]
    skin_span=max(spans)
    second_web_front=c['WEB_CENTRES'][1]-c['WEB']/2
    input_checks={'balanced_skins_12p7_mm':c['BOTTOM']==12.7 and c['TOP']==12.7,
        'selected_core_39p05_mm':abs(c['CORE']-39.05)<1e-8,
        'complete_height_matches_datums':abs(height-(P.DRY_TOP-P.DRY_BOTTOM))<1e-8,
        'seven_webs_modeled':len(c['WEB_CENTRES'])==7,
        'five_webs_conservatively_credited':WEB_COUNT_CREDITED==5,
        'skin_max_clear_span_45p75_mm':abs(skin_span-45.75)<1e-8,
        'front_pulls_preserve_Y19_web':bool(pocket_ends) and max(pocket_ends)<second_web_front,
        'groove_leaves6p35_skin_mm':abs(c['TOP']-6.35-6.35)<1e-8,
        'slat_nominal_not_below_screen_min':c['SLAT_T']>=SLAT_MIN_THICKNESS,
        'cabinet_notch_326mm_segment_detected':bool(cabinet_notches) and abs(max(b-a for a,b in cabinet_notches)-326)<1e-8}
    sec=section(c['BOTTOM'],c['CORE'],c['TOP'],P.PANEL_LENGTH,c['WEB'],WEB_COUNT_CREDITED,c['TRACK_W'],6.35)
    # Largest bay starts at theY19web's rearface23.5; groove ends28.5.
    thin_length=max(0.,c['TRACK_CENTRES'][0]+c['TRACK_W']/2-(c['WEB_CENTRES'][1]+c['WEB']/2))
    cases=[cassette_case(F,E,c,sec,skin_span,thin_length) for E in (E_PLY_BASE,E_PLY_WEAK) for F in (100.,300.)]
    a=angle_properties(50.8,6.35)
    ledger=ledger_case(100,max(b-a0 for a0,b in zip(P.POST_CENTRES_Y,P.POST_CENTRES_Y[1:])),a['I_vertical_mm4'],a['J_thin_wall_mm4'])
    header=cantilever_deflection(50,P.Y_LENGTH-P.POST_CENTRES_Y[-1],P.AL_E_MPA,P.PROFILE_I_STRONG_MIN_MM4)
    combined=[]
    for case in (r for r in cases if r['force_N']==100):
        sub=case['cassette_component_sum_mm']+ledger['sum_components_mm']+header
        combined.append({'raw_plywood_E_MPa':case['raw_plywood_E_MPa'],
            'cassette_mm':case['cassette_component_sum_mm'],'ledger_bending_and_torsion_mm':ledger['sum_components_mm'],
            'header_vertical_strong_axis_mm':header,'known_ideal_component_subtotal_mm':sub,
            'remaining_budget_to0p30_mm':SERVICE_TARGET-sub,'ideal_subtotal_target_met':sub<=SERVICE_TARGET,
            'assembled_target_qualified':False,
            'front_ledger_joint_detail':'Three stations per front arm aftertransfer relief, includingtwoX-separated back-row bolts; four perotherarm. Nominal twist restraint still requires test.',
            'excluded_compliance':'Post axial deformation, arm/angle joints, contact bedding, joint rotation/slip, actual diaphragm/adhesive behavior and owned motion/tooling.',
            'scope':'Aligned vertical100N component sensitivity only; no weak-axisX term, gravity sag, or unbalanced external-push displacement is added.'})
    hashes={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('params.py','frame.py','bed.py','structure_screen.py','bed_screen.py')}
    report={'revision':P.REVISION,'passed':all(input_checks.values()),
        'passed_scope':'Analytical-input/source consistency only. This flag does not certify part geometry, strength, service stiffness or the whole machine.',
        'release':False,'prices_included':False,'analysis_type':'Closed-form box-beam, shear, strip and slat sensitivities; not FEA.',
        'source_sha256':hashes,'input_checks':input_checks,
        'selected_source_inputs':{k:c[k] for k in required},
        'geometry':{'panel_width_X_mm':P.PANEL_WIDTH,'panel_length_Y_mm':P.PANEL_LENGTH,
            'hard_seat_centres_X_mm':[117.5,1032.5],'global_span_mm':SPAN,'structural_height_mm':height-c['WEAR'],
            'complete_height_mm':height,'front_pull_y_ends_mm':pocket_ends,
            'second_front_web_y_start_mm':second_web_front,'largest_local_clear_span_mm':skin_span},
        'section':sec,
        'material_assumptions':{'raw_required_E_along_span_MPa':E_PLY_BASE,'weaker_material_sensitivity_E_MPa':E_PLY_WEAK,
            'global_stiffness_factor':STIFFNESS_FACTOR,'core_G_MPa':G_CORE,'shear_factor':SHEAR_FACTOR,
            'interpretation':'EffectiveE is rawE×0.75. This is an assumed stiffness reduction, not a qualified glue efficiency or plywood grade.',
            'web_credit':'Seven modeled; five inner webs credited for global/shear, conservatively omitting outer edge rows. Shallow pulls preserveY19. End lifting-grip discontinuities, holes and adhesives still need physical verification.',
            'no_stiffness_credit':['Aluminum T-slot tracks','Al compression tubes/blocks','Removable MDF wear layer','Mechanical latches acting as a bonded laminate']},
        'cassette_cases':cases,'combined_vertical_service_sensitivities':combined,
        'slats':slat_cases(c['SLAT_T'],c['SLAT_LENGTH']),
        'cabinet_front_strip':cabinet_strip_case(cabinet_notches),
        'front_transfer_notches':{'frame_parts':4,'ledge_stations':22,'status':'Local notch/profile-lip/pan-seat/contact qualification remains required; analytical unrelieved arm reference is not a notch-strength proof.'},
        'skin_stock_orientation':{'count':8,'blank_mm':[932,257,12.7],
            'one_sheet_nominal_mm':[2440,1220],
            'nest':'2×932 along2440 and4×257 across1220;4mm gaps and2mm outer trim fit1872×1044.',
            'requirement':'Put the declared/measured stronger plywood bending direction along932. Generic plywood labeling or a rotated nest does not establishE4000.'},
        'qualification_required':['Supplier or coupon bending/shear data in the actual grain direction and moisture condition',
            'Continuous bonded web-to-skin interfaces, cure, sealing and repeated load/temperature durability',
            'Static100N relative work-surface deflection tests at midpoint, near pockets and panel seams',
            'Joint/ledger/contact compliance measured against the remaining ideal budget, not assumed zero',
            'Track lip, fastener, backing-block, compression-tube and skin-pull-through proof under actual clamp preload',
            'Local hand-grip and finger-pocket stress concentrations and repeated handling',
            'Front transfer-notch profile lip/contact behavior and three-station front-ledger anti-roll response',
            'Front cabinet stripped-angle segments, side-skin/rivet lateral restraint, floor contacts and rear anti-tip links',
            'Positive slat-to-comb-to-pan/frame load path and cold load test before assigning a table workpiece rating'],
        'proof_case_scope':'300N values are linear sensitivity results, not an approved machining load or an asserted nondestructive proof procedure.',
        'non_coverage':['Full assembled tool-to-work compliance','Owned gantry, rails, drive modules, screw lead, Z/spindle/tooling',
                        'Track/clamp hardware strength and exact supplier profiles','Pan floor/weld/comb system capacity and thermal distortion',
                        'Transfer sweep, water flow, electrical interface and protected-storage temperatures']}
    OUT.mkdir(exist_ok=True)
    (OUT/'bed-screen.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    nominal=combined[0];weak=combined[1];sl=report['slats']
    lines=['# XR1 bed structure — conditional analytical screen','',
        f'The selected cassette is932×257×{height:.1f}mm:12.7mm plywood skins around39.05mm core, plus6.35mm removable MDF wear. Seven9mm webs are modeled; five inner webs receive conservative global/shear credit. The front pulls end atY14, preserving theY19web. Aluminum tracks and MDF receive no stiffness credit.','',
        f'At100N and raw plywoodE4000MPa reduced by25%, the ideal cassette component sum is{nominal["cassette_mm"]:.3f}mm. Adding aligned vertical ledger and header components gives{nominal["known_ideal_component_subtotal_mm"]:.3f}mm against the0.30mm framework/bed target, leaving{nominal["remaining_budget_to0p30_mm"]:.3f}mm for omitted joints/contact/other components. This is an analytical budget, not a measured assembled pass.','',
        f'The weakerE2500MPa sensitivity gives{weak["known_ideal_component_subtotal_mm"]:.3f}mm before those omitted components and therefore misses the target. Actual plywood stiffness in the915mm span direction must be established. Orient the932mm dimension along the declared stronger bending direction: a2×4skin layout fits one2440×1220sheet without rotating the span across that direction.','',
        f'The top-skin calculation uses a25mm load strip over the45.75mm maximum clear web gap and includes the5mm short, thinner groove segment near one support. Core shear and global bending are separate terms. Glue stresses are demands only; no adhesive allowable or durability is established.','',
        f'For nominal1.9mm slats screened at1.8mm minimum, the member-only results are{sl["distributed150kg_case"]["deflection_mm"]:.3f}mm for150kg distributed among all8slats/two spans and{sl["single200N_case"]["deflection_mm"]:.3f}mm for200N at one435mm span midpoint. These do not establish a pan/table load rating: comb contacts, feet/welds, floor, shims and bearer joints require a positive load path and tests.','',
        'The four local front-frame notches clear the upright cassette channel. The front ledger joints retain three stations each, including twoX-separated back-row bolts; their local lip/contact and anti-roll behavior remains unqualified.','',
        'The cabinet stands on its own four columns and contributes no credited frame ballast. Its relieved front25×3mm strips have about360N pinned ideal buckling load over326mm (about90N forK2). Qualified side-skin restraints at410/500/600/690 shorten the largest segment to100mm, with about3831N ideal pinned buckling load. These ideal results do not qualify skin/rivet restraint, column feet, shelf connections or cabinet load capacity.','',
        'The machine remains a wood-carving/plasma development design. This report provides no steel-milling, ATC, clamp, thermal, water, electrical or complete tool-loop qualification. See bed-screen.json for assumptions, source hashes and acceptance requirements. No pricing is included.']
    (OUT/'BED.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'input_checks_passed':report['passed'],'balanced_height_mm':height,
        'nominal_combined_ideal_mm':nominal['known_ideal_component_subtotal_mm'],
        'weaker_combined_ideal_mm':weak['known_ideal_component_subtotal_mm'],
        'ideal_target_met_nominal':nominal['ideal_subtotal_target_met'],
        'ideal_target_met_weaker':weak['ideal_subtotal_target_met'],'release':False},indent=2))
    return report

if __name__=='__main__':
    r=run()
    raise SystemExit(0 if r['passed'] else 1)
