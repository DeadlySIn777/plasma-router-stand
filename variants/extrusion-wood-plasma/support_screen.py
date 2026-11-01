"""Engineering review loads, NOT seller profile properties or a machine rating."""
from pathlib import Path
import json,math
HERE=Path(__file__).resolve().parent
def screen():
    wet=json.loads((HERE/'bed-check.json').read_text())['all_bed_parts_plus_operating_water_weight_N']
    # A sheet allowance is an explicitly chosen example, not a released limit.
    stock_kg=.8*.96*.003*7850
    W=wet+stock_kg*9.80665
    span=1088.4  # plate-to-side-slot centers X30.8 / 1119.2, not just clear cut length
    E=69000
    K=lambda F,L:5*F*L**3/(384*E)
    cases=[]
    for frac in (1/3,.5):
        for span_case in ('full','center_support_engaged'):
            L=span if span_case=='full' else span/2
            # Uniform line load unchanged; halving the span also halves its total load.
            Fb=W*frac*(L/span)
            cases.append({'one_bearer_share':round(frac,4),'span_case':span_case,'ideal_span_mm':L,
                'same_distributed_load_N_per_mm':W*frac/span,'load_on_span_N':Fb,
                'I_required_cm4_for_0p5mm_static_sag':K(Fb,L)/0.5/1e4,
                'I_required_cm4_for_1mm_static_sag':K(Fb,L)/1e4})
    assert math.isclose(cases[2]['I_required_cm4_for_0p5mm_static_sag']/cases[3]['I_required_cm4_for_0p5mm_static_sag'],16)
    obj={'base_frame_usd':2*129.99+59.90,'additional_4x1000_pack_usd':59.90,
         'nine_foot_extrusion_usd':round(2*129.99+2*59.90,2),
         'wet_bed_weight_N':wet,'example_sheet_not_machine_rating':{'stock_mm':[800,960,3],'kg':stock_kg},
         'assumed_aluminium_E_MPa':E,'simple_uniform_bearer_sensitivities':cases,
         'scope':'Conditions only. Actual load distribution includes concentrated ledger and rear rack reactions. Selected series section I, joints, feet/floor, local tray sag, tool/drive loop and dynamic behavior unqualified. 0.5 and 1 mm are comparison sag values, not machining tolerances.',
         'reference':'https://ocw.mit.edu/courses/1-050-solid-mechanics-fall-2004/fd4eff39aec922b8c07660006f40686e_pset04_11.pdf'}
    (HERE/'review'/'support-screen.json').write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(cases,indent=2))
if __name__=='__main__':screen()
