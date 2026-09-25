"""Analytical inventory and specified relay-logic checks; not a hardware test."""
from itertools import product
from pathlib import Path
import json
import math

HERE = Path(__file__).parent
T = 3.048
pan_inner_area = (920 - 2*T) * (1200 - 2*T)
mean_floor_top = 741 + T / math.cos(math.atan(0.01))

def pan_litres(level):
    raw = pan_inner_area * max(0, level - mean_floor_top)
    slats = 19 * 880 * T * min(75, max(0, level - 775))
    # Two1120x6 combs. Bottom follows slope, comb top795, slots down to775.
    comb_mean_floor = 735 + 0.01*(1275-660) + T/math.cos(math.atan(0.01))
    combs = 2 * 6 * (1120*max(0, min(level,795)-comb_mean_floor)
                      - 19*3.6*min(20,max(0,level-775)))
    return (raw - slats - combs) / 1e6

normal_pan = pan_litres(820)
front_area = 900 * 460
rear_area = 900 * (140 - T)
reservoir_net_area = front_area + rear_area
inventory = 115
line_allowance = 1.0
remaining = inventory - normal_pan - line_allowance
normal_reservoir_depth = remaining * 1e6 / reservoir_net_area
low_level_volume = reservoir_net_area * 55 / 1e6
overflow_depth = 242
capacity_to_overflow = reservoir_net_area * overflow_depth / 1e6
internal_displacement_reserve = 1.0
conservative_return_capacity = capacity_to_overflow - internal_displacement_reserve
overflow_q_lpm = (2/3) * 0.6 * math.pi * 0.0409 * math.sqrt(2*9.81) * 0.010**1.5 * 60000

assert normal_reservoir_depth > 55, "Insufficient inventory to reach normal pan level"
assert normal_reservoir_depth > 50, "Communicating-bay calculation invalid"
assert conservative_return_capacity >= 125, "Insufficient all-return capacity including internal-volume reserve"
assert overflow_q_lpm > 7, "Screening overflow capacity is below pump open-flow rate"

# Truth table for the specified steady-state contacts, including arbitrary timer
# contact states. It cannot verify wiring, relay ratings, contact welding or races.
keys = ('setup','run','bedclear','bedlock','empty','minimum','belowstop',
        'belowhh','reservoir_ok','stop_ok','close_done','drain_done','drain_override','fill_press','was_filling','was_armed')
states_checked = 0
for mode in ('OFF','ROUTER','PLASMA'):
    for bits in product((False,True), repeat=len(keys)):
        s=dict(zip(keys,bits))
        # Physical keyed SETUP/RUN positions are mutually exclusive.
        if s['setup'] and s['run']:
            continue
        drain = mode=='ROUTER' or s['drain_override']
        allowed = (mode=='PLASMA' and s['setup'] and s['bedclear'] and s['close_done']
                   and not drain and s['stop_ok'] and s['reservoir_ok'] and s['belowhh'] and s['belowstop'])
        arm = allowed and (not s['fill_press'] or s['was_armed'])
        fill = allowed and arm and (s['fill_press'] or s['was_filling'])
        power_limit = (mode=='PLASMA' and s['setup'] and s['bedclear'] and s['stop_ok']
                       and s['reservoir_ok'] and s['belowhh'] and s['close_done'] and not drain)
        pump = fill and power_limit
        router_ready = mode=='ROUTER' and s['drain_done'] and s['empty'] and s['bedlock']
        plasma_ready = mode=='PLASMA' and s['close_done'] and s['minimum'] and s['belowhh'] and s['bedclear'] and not drain
        ready = s['stop_ok'] and s['belowhh'] and s['run'] and not fill and (router_ready or plasma_ready)
        # Manual drain override must defeat tool permission in ALL modes.
        ready = ready and not s['drain_override']
        assert not (pump and ready)
        assert not pump or (mode=='PLASMA' and not drain and s['bedclear'])
        assert not ready or s['run']
        if mode=='ROUTER':
            assert not pump
            assert not ready or (s['empty'] and s['bedlock'] and s['drain_done'])
        if mode=='OFF':
            assert not pump and not ready
        if not s['belowhh'] or not s['reservoir_ok'] or not s['stop_ok']:
            assert not power_limit and not pump
        if not s['belowhh'] or not s['stop_ok'] or s['drain_override']:
            assert not ready
        if not s['fill_press'] and not s['was_filling']:
            assert not fill
        if s['fill_press'] and not s['was_armed']:
            assert not fill
        states_checked += 1

# Logical transitions prove release-to-rearm at the specification level only.
# Real relay pickup/dropout and contact sequencing require a circuit-level check.
def fill_transition(allowed, pressed, armed, filling):
    next_armed = allowed and (not pressed or armed)
    next_filling = allowed and next_armed and (pressed or filling)
    return next_armed, next_filling

transition_checks = []
for label, sequence in [
    ('Held through power restoration', [(False,True),(True,True),(True,False),(True,True)]),
    ('Held through low-level recovery', [(True,False),(True,True),(False,True),(True,True),(True,False),(True,True)]),
    ('Released after normal fill stop', [(True,False),(True,True),(True,False),(False,False),(True,False)]),
]:
    armed = filling = False
    outputs = []
    for allowed, pressed in sequence:
        armed, filling = fill_transition(allowed,pressed,armed,filling)
        outputs.append({'allowed':allowed,'pressed':pressed,'armed':armed,'filling':filling})
    if label.startswith('Held through power'): assert [o['filling'] for o in outputs] == [False,False,False,True]
    elif label.startswith('Held through low'): assert [o['filling'] for o in outputs] == [False,True,False,False,False,True]
    else: assert outputs[-1]['filling'] is False
    transition_checks.append({'scenario':label,'states':outputs,'passed':True})

bom=json.loads((HERE/'water-bom.json').read_text())
observed=round(sum(i.get('extended_usd',0) for i in bom['items']),2)
allowance=round(sum(i.get('allowance_usd',0) for i in bom['items']),2)
total=round(observed+allowance+bom['summary']['unquoted_shipping_reserve_usd'],2)
assert observed==bom['summary']['observed_goods_usd']
assert allowance==bom['summary']['unquoted_goods_allowance_usd']
assert total==bom['summary']['planning_subtotal_before_tax_usd']
cad_water=json.loads((HERE/'state-summary.json').read_text())
assert cad_water['tank_displacement_at_overflow_litres'] < internal_displacement_reserve
assert cad_water['normal_pan_water_model_litres'] <= normal_pan

report={
    'status':'PASS analytical screen; physical acceptance unperformed',
    'logic_states_checked':states_checked,
    'release_to_rearm_transition_checks':transition_checks,
    'fluid_calculation':{
        'inventory_litres':inventory,'pan_at_Z820_litres':round(normal_pan,3),
        'assumed_lines_litres':line_allowance,'remaining_reservoir_litres':round(remaining,3),
        'reservoir_depth_above_floor_mm':round(normal_reservoir_depth,3),
        'reservoir_internal_mm':[900,600,250],
        'low_trip_depth_mm':55,'usable_margin_litres':round(remaining-low_level_volume,3),
        'tank_capacity_to_overflow_before_pipe_displacement_litres':round(capacity_to_overflow,3),
        'all_return_margin_before_pipe_displacement_litres':round(capacity_to_overflow-inventory,3),
        'internal_displacement_reserve_litres':internal_displacement_reserve,
        'conservative_return_capacity_litres':round(conservative_return_capacity,3),
        'conservative_all_return_margin_litres':round(conservative_return_capacity-inventory,3),
        'pan_overflow_circular_weir_at_10mm_head_lpm':round(overflow_q_lpm,3)
    },
    'final_cad_comparison':{
        'normal_pan_water_litres':cad_water['normal_pan_water_model_litres'],
        'tank_internal_solid_displacement_litres':cad_water['tank_displacement_at_overflow_litres'],
        'analytic_pan_inventory_is_conservative':True,
        'one_litre_internal_displacement_reserve_covers_modeled_solids':True,
        'source':'state-summary.json'
    },
    'cost':{'observed_goods_usd':observed,'unquoted_goods_allowance_usd':allowance,
            'shipping_reserve_usd':20,'planning_subtotal_before_tax_usd':total},
    'limitations':['Approximate analytic solid displacement; confirm against finalCAD and measuredfill.',
                   'Logic table is steady-state specification only, not relay wiring/dynamic proof.',
                   'No physical sensor, overflow, pump, current, timing or stop-chain test performed.']
}
(HERE/'water-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
