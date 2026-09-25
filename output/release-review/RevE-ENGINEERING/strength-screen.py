"""Transparent first-order checks; no implied whole-machine stiffness rating."""
from pathlib import Path
import json, math
ROOT=Path(__file__).resolve().parent

def tube(a,t):return {'area_mm2':a*a-(a-2*t)**2,'I_mm4':(a**4-(a-2*t)**4)/12,'c_mm':a/2}
def point_beam(F,L,E,I,c):
    return {'force_N':F,'span_mm':L,'deflection_mm':F*L**3/(48*E*I),'stress_MPa':F*L*c/(4*I)}
def brace(horizontal,vertical,section):
    L=math.hypot(horizontal,vertical);A=section['area_mm2'];I=section['I_mm4'];E=200000
    return {'length_mm':L,'ideal_horizontal_stiffness_N_per_mm':E*A/L*(horizontal/L)**2,
            'Euler_pinned_buckling_N':math.pi**2*E*I/L**2,
            'axial_force_for_100_N_horizontal_N':100*L/horizontal,
            'qualification':'Ideal axial member only. Joint rotation, tube corner radii, weld distortion, gusset bending and complete frame flexibility are excluded.'}

def rect_tube(b,h,t):
    return {'area_mm2':b*h-(b-2*t)*(h-2*t),'I_mm4':(b*h**3-(b-2*t)*(h-2*t)**3)/12,'c_mm':h/2}

def main():
    sq=tube(50.8,3.048);br=tube(25.4,2.1082);xm=rect_tube(50.8,38.1,3.048)
    manifest=json.loads((ROOT/'engineering-manifest.json').read_text(encoding='utf-8'))
    ip=manifest['bed']['profile_nominal_Ixx_mm4']
    ap=manifest['bed']['profile_nominal_section_area_mm2']
    Ffoot=650*9.80665/3
    data={'status':'PRELIMINARY ELASTIC STRENGTH SCREEN; NOT A CERTIFIED MACHINE LOAD RATING',
          'assumptions':{'steel_E_MPa':200000,'aluminum_E_MPa':69000,'steel_yield_screen_MPa':250,
             'router_transverse_tool_force_N':100,'illustrative_tool_lever_mm':250,'local_downward_bed_force_N':500,
             'distributed_workstock_mass_kg':25,'gross_machine_design_mass_kg':650,
             'foot_support_case':'One third of gross weight on one foot; all six feet adjusted into contact.',
             'dimensions':'Nominal geometry; real stock wall thickness, rail preload, welds and material certification must be checked against procurement.'},
          'square_2in_0120in_tube':sq,'crossmember_2x1p5in_0120in_flat':xm,
          'one_module_crossmember':[point_beam(f,938.4,200000,xm['I_mm4'],19.05) for f in (100,500)],
          'beam_method':'Simply supported at the rail inner faces X105.8/1044.2. Each check assigns the entire load to ONE crossmember; sharing through the continuous MDF/strip plate is excluded. Module side rails bear continuously on the fixed ledgers and are not a spanning member.',
          'profile_section':{'reconstructed_area_mm2':ap,'reconstructed_I_mm4':ip,'source':'https://m.media-amazon.com/images/I/71myeCep6iL._SL1500_.jpg',
             'qualification':'Section properties from reconstructed nominal CAD; unnamed transitions are approximated and properties are not supplier certified.'},
          'one_20100_strip':[point_beam(f,400,69000,ip,10) for f in (100,500)],
          'strip_method':'Conservative simply-supported single 400 mm crossmember bay for ONE strip carrying the whole load; the strip is actually continuous over four supports and bonded to the 25.4 mm MDF sub-bed, both of which reduce deflection.',
          'bed_combined_vertical_screen':{'100_N_sum_mm':point_beam(100,938.4,200000,xm['I_mm4'],19.05)['deflection_mm']+point_beam(100,400,69000,ip,10)['deflection_mm'],
             '500_N_sum_mm':point_beam(500,938.4,200000,xm['I_mm4'],19.05)['deflection_mm']+point_beam(500,400,69000,ip,10)['deflection_mm'],
             'qualification':'Conservative sum of one strip bay and one bare crossmember only; excludes MDF composite action, load sharing between strips and members, continuous rail bearing, and gantry/guide/tool compliance.'},
          'side_brace':brace(598.8,689.2,br),'rear_brace':brace(998.4,689.2,br),
          'gantry_bending':point_beam(100,1000,69000,171.6341*10000,40),
          'gantry_qualification':'Sensitivity estimate using assumed 8080 extrusion I=171.6341 cm4. This value has not been verified against a selected purchased cross-section and does not establish torsional rigidity or complete head stiffness.',
          'beam_M8_joint':{'nominal_torque_Nm':12,'nut_factor_assumed':.2,'estimated_preload_N':7500,'tensile_stress_MPa':7500/36.6,
             'compression_sleeve_OD_ID_mm':[18,9],'sleeve_compression_MPa':7500/(math.pi/4*(18**2-9**2)),
             'warning':'Torque/preload is approximate; use lubricity-controlled hardware and verify seats are flat. This is deliberately below typical class8.8 maximum torque.'},
          'M6_guide_datum_clamps':{'torque_Nm':6,'estimated_preload_N':5000,'sleeve_OD_ID_mm':[12,6.6],'sleeve_compression_MPa':5000/(math.pi/4*(12**2-6.6**2))},
          'module_deck_fastening':{'deck_M5_count':50,'screw':'M5x25 ISO7380 button + DIN562 square nut in the strip bottom slot, entered from below through the MDF',
             'clamp_member':'25.4 mm MDF sandwich, not the 1.3 mm aluminum lips: the nut bears UP on the lips only under uplift, and the fastener torque is reacted by the MDF, so the Rev E 0.35 Nm lip-torque limit no longer applies. Snug plus a quarter turn; do not crush MDF.',
             'uplift_demand_screen_N':'Deck weight is downward; uplift comes from clamping reactions and lift handling. At 20 kg workpiece-clamp uplift concentrated on one strip station, one screw sees under 200 N.',
             'lip_bearing_at_600N_MPa':6*(600/2)*.45/(8*1.3**2),
             'mdf_pullout_note':'Machine-screw-into-MDF is NOT the retention path; the screw passes through the MDF into a steel-backed square nut. The MDF sees only compression under the fender washer (Ø15, bearing area about 154 mm2; 600 N gives about 3.9 MPa, inside typical MDF face compressive strength).',
             'frame_TEK_fasteners':{'count':16,'screw':'#12-14x32 self-drilling into the 3.048 crossmember top wall','engagement':'about 1.1 thread pitches in the wall; the module weight passes in compression, TEKs only register the MDF','verification':'Prototype drive-and-strip check in the actual 2 x 1.5 tube wall before committing the pattern.'},
             'verification':'Prototype: one strip screwed to a surfaced MDF offcut, 600 N pull on the strip with no lip deformation and no visible MDF crush; weigh the finished module before the first hoist.'},
          'module_hoist':{'winch_rating_kg':567,'module_estimate_kg':None,
             'note':'Module mass estimate is recorded in engineering-manifest.json bed.module_mass_estimate_kg and swap-path-checks.json; margin against the 1250 lb winch exceeds 6x. Four M12-class ear holes (Ø16) each see under 300 N static; the ears are not the weak link, the owner rigging and anchorage are, and those are not modeled.'},
          'pan_hanger_joint':{'pan_water_slats_stock_design_mass_kg':200,'six_end_reactions_N':200*9.80665/6,
             'M8_per_hanger':4,'nominal_thread_engagement_mm':6.4,'bolt_shear_per_fastener_N':200*9.80665/24,
             'weld':'3 mm fillets along both80 mm accessible sides of hanger top. Weld quality and parent wall thickness govern final joint acceptance.'},
          'tank_shelf':{'three_crossmembers':'50.8×50.8×3.048','span_mm':1048.4,
             'tank_water_and_equipment_design_mass_kg':200,
             '200_kg_load_shared_three_members_conservative_point_load':point_beam(200*9.80665/3,1048.4,200000,sq['I_mm4'],25.4),
             'uniformly_distributed_case_deflection_mm':point_beam(200*9.80665/3,1048.4,200000,sq['I_mm4'],25.4)['deflection_mm']*5/8},
          'custom_M16_feet':{'worst_foot_N':Ffoot,'M16_tensile_area_mm2':157,'nominal_compressive_stress_MPa':Ffoot/157,
             'exposed_stem_nominal_mm':23.3,'adjustment_mm':8,'pad_mm':[80,80,12.7],
             'gross_pad_pressure_MPa':Ffoot/(80*80),
             'qualification':'Pad bending, floor bearing and anchors require the actual support surface; do not apply a purchased foot rating to the custom jack.'},
          'independent_guides':{'tool_moment_Nm':25,'X_rail_vertical_separation_mm':60,'X_blocks_per_row':2,
             'incremental_couple_load_per_X_block_N':25*1000/60/2,'direct_tool_load_per_X_block_N':25,
             'Y_block_separation_mm':180,'incremental_pitch_load_per_Y_block_N':25*1000/2/180,
             'assumed_complete_Y_moving_mass_kg':50,'physical_gantry_rearward_offset_mm':80,
             'additional_Y_gravity_couple_per_block_N':50*9.80665*80/2/180,
             'direct_Y_gravity_per_block_N':50*9.80665/4,
             'conservative_sum_Y_gravity_and_tool_per_block_N':50*9.80665*80/2/180+50*9.80665/4+25*1000/2/180,
             'assumed_complete_X_head_mass_kg':12,'assumed_head_gravity_lever_mm':120,
             'additional_X_gravity_couple_per_block_N':12*9.80665*120/60/2,
             'conservative_sum_X_gravity_and_tool_per_block_N':12*9.80665*120/60/2+12*9.80665/4+25*1000/60/2+25,
             'supplier_claimed_static_rating_per_block_N':27760,
             'qualification':'Supplier iMetrx rating is a capacity claim, not a stiffness/preload certificate. Gantry and head gravity loads must be added. No HIWIN certification is implied.'},
          'HMS40_drive_only_requirement':{'supplier_moments_Nm':{'MY':13,'MP':12,'MR':15},'source':'https://www.khmos.com/high-performance-easy-access/hms40',
             'reason':'100 N at250 mm produces25 Nm before head weight. The small actuator carriage cannot be treated as the sole router support. Independent X/Y guides carry the head; axial floating links drive it.'},
          'HMS40_floating_link_eccentricity':{'screen_axial_drive_force_N':250,
             'X_pin_above_carriage_output_mm':38.05,'Y_pin_above_carriage_output_mm':25.35,
             'X_drive_only_moment_Nm':250*38.05/1000,'Y_drive_only_moment_Nm':250*25.35/1000,
             'least_published_axis_moment_Nm':12,
             'X_fraction_of_least_published_moment':250*38.05/1000/12,
             'Y_fraction_of_least_published_moment':250*25.35/1000/12,
             'qualification':'Axial drive force at the actual link-pin height produces a residual actuator moment even with independent guides. These isolated static components are below the least listed 12 N m moment, but do not establish a combined-load, fatigue or impact rating. Set acceleration and link alignment from measured moving masses and the supplier load conditions; do not transmit router support loads through the drive shoe.'},
          'unresolved_complete_machine_compliance':['Actual independent rail preload/straightness and mounting accuracy','Gantry torsion and head adapter bending','Actual ZBX80 mounting plane height and mounting-hole thread geometry','Spindle clamp/tool projection and cutting dynamics'],
          'sources':['https://www.bossard.com/ie-en/-/media/bossard-group/website/documents/technical-resources/en/f-047-en.pdf']}
    (ROOT/'strength-screen.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'crossmember_100N_mm':data['one_module_crossmember'][0]['deflection_mm'],'strip_100N_mm':data['one_20100_strip'][0]['deflection_mm'],'bed_combined_100N_mm':data['bed_combined_vertical_screen']['100_N_sum_mm'],'side_brace_kN':data['side_brace']['Euler_pinned_buckling_N']/1000},indent=2))

if __name__=='__main__':main()
