"""Compare saved component screens and dated source prices, without FEA claims."""
from pathlib import Path
from decimal import Decimal
import hashlib,json,sys

HERE=Path(__file__).resolve().parent;MACHINE=HERE.parent;ROOT=MACHINE.parents[1]
sys.path.insert(0,str(MACHINE/'manufacturing'))
import budget_model

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def main():
 baseline=MACHINE/'bed/output/bed-local-check-before-retained-pivot-window.json'
 current=MACHINE/'bed/output/bed-local-check.json'
 gantry=MACHINE/'output/gantry-joint/gantry-joint-check.json'
 old=read(baseline);new=read(current);joint=read(gantry);budget=budget_model.current_budget()
 old_screen=old['analysis']['workbed_compliance_screen']
 new_screen=new['analysis']['workbed_compliance_screen']
 before=old_screen['sum_ideal_components_mm'];after=new_screen['sum_ideal_components_mm']
 assert old_screen['force_N']==new_screen['force_N']==100
 assert old_screen['profile_span_mm']==new_screen['profile_span_mm']
 assert old_screen['cross_span_mm']==new_screen['cross_span_mm']
 assert old_screen['profile_deflection_mm']==new_screen['profile_deflection_mm']
 assert old_screen['ledger_deflection_mm']==new_screen['ledger_deflection_mm']
 assert abs(new_screen['cross_deflection_mm']*4-old_screen['cross_deflection_mm'])<1e-10
 sources=[Path(__file__),Path(budget_model.__file__),baseline,current,gantry,
          MACHINE/'manufacturing/selected-cart-evidence.json']
 report=dict(observed_date='2026-11-05',revision_date='2026-11-06',
  scope='Saved nominal bed component screens and dated selected-source goods. Not full-machine FEA, a qualified supplier section, market minimum or delivered quotation.',
  source_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in sources},
  bed_component_comparison=dict(force_N=100,prior_assumed_weak_axis_I_mm4=134000,
   current_assumed_strong_axis_I_mm4=new_screen['assumed4080_I_strong_mm4'],
   prior_component_sum_mm=before,current_component_sum_mm=after,
   ideal_component_displacement_reduction_percent=100*(before-after)/before,
   current_drilled_section_sensitivity=new_screen['drill_section_sensitivity'],
   section_property_supplier_or_drilled_ligaments_qualified=False,
   HDPE_composite_action_credited=False,full_tool_work_loop_qualified=False,
   baseline_scope='Earlier saved two-layer/weak-crossbar case before retained-pivot-window changes; only the unchanged component formulas/spans are compared, not complete assembly mass or joint performance.'),
  current_nominal_moving_deck_mass_kg=[x['moving_mass_kg']for x in new['analysis']['mass_and_force_cases']],
  gantry_revision=dict(continuous_steel_rail_face_mm=[1200,112,6.35],upper_bridge_quantity=4,
   replaced_Al_guidebars=True,custom_parts_moving_mass_increase_kg=joint['mass']['custom_part_moving_mass_increase_kg'],
   added_hardware_mass_excluded=True,axis_acceleration_or_motor_capacity_verified=False,
   cap_component_screen=joint['conditional_cap_component_screen'],full_composite_torsion_qualified=False),
  selected_source_cost_comparison=dict(prior_three_core_goods_USD='1025.70',
   current_three_core_goods_USD=budget['three_core_goods_basis_USD'],
   core_goods_saving_USD=str(Decimal('1025.70')-Decimal(budget['three_core_goods_basis_USD'])),
   core_plus_staged_hardware_goods_USD=budget['known_core_plus_staged_hardware_goods_subset_USD'],
   core_plus_staged_hardware_plus_toolsetter_USD=budget['known_basic_goods_subset_USD'],
   tracks_in_core_and_cart_counted_once=True,complete_delivered_total_USD=None,budget_gate='FAIL'),
  passed=True,fabrication_release=False,operating_release=False)
 (HERE/'comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=True,ideal_bed_component_reduction_percent=report['bed_component_comparison']['ideal_component_displacement_reduction_percent'],core_goods_saving_USD=report['selected_source_cost_comparison']['core_goods_saving_USD'])))

if __name__=='__main__':main()
