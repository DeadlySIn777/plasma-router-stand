"""Verify the defined head schematic against the existing Rev I relay graph.

This is a bounded schematic/delay model, not an assembled-board or EMC test.
"""
from pathlib import Path
from collections import defaultdict, deque
import hashlib, itertools, json, math
from circuit import Simulator, WIRES, CONTACTS, DIODES, LOADS

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SPEC = OUT / 'head-interface.json'
SELF = Path(__file__).resolve()
CHECKS = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name, passed, **evidence):
    CHECKS.append(dict(check=name, passed=bool(passed), **evidence))
    if not passed:
        raise AssertionError((name, evidence))


def reachable(edges, start):
    graph = defaultdict(set)
    for a, b in edges:
        graph[a].add(b)
        graph[b].add(a)
    seen = {start}
    todo = deque([start])
    while todo:
        for node in graph[todo.popleft()] - seen:
            seen.add(node)
            todo.append(node)
    return seen


class Head:
    def __init__(self, spec):
        self.spec = spec
        self.state = dict(left=True, right=True, top=True, float_healthy=True)
        self.power = True
        self.open_wires = set()
        self.output = False
        self.elapsed = 0.0

    def led(self, channel):
        # Test the series path BEFORE the LED. Do not mistake a route backwards
        # through another channel's return/shunt for forward LED current.
        edges = []
        for e in self.spec['connections']:
            if e['id'] in self.open_wires:
                continue
            active = e['kind'] == 'wire' or (e['kind'] == 'resistor' and e['id'] in ('R_HEAD', 'R_PROBE'))
            if e['kind'] == 'contact':
                active = self.state[e['closed_key']]
            if active:
                edges.append((e['a'], e['b']))
        return self.power and f'U_{channel}:1' in reachable(edges, 'C') and 'XW:2' in reachable(edges, f'U_{channel}:2')

    def tick(self, dt):
        command = self.led('HEAD')
        if command == self.output:
            self.elapsed = 0.0
        else:
            self.elapsed += dt
            key = 'on_s' if command else 'off_s'
            if self.elapsed + 1e-12 >= self.spec['model']['photomos'][key]:
                self.output = command
                self.elapsed = 0.0
        return self.output


def advance(sim, head, seconds):
    dt = head.spec['model']['delay_test']['integration_step_s']
    for _ in range(round(seconds / dt)):
        sim.inputs['breakaway_seated'] = head.tick(dt)
        sim.tick(dt)
    return sim.outputs()


def main():
    binding = [SPEC, SELF, OUT/'circuit.py', OUT/'terminal-netlist.json',
               OUT/'selected-components.json', OUT/'HEAD-INTERFACE.md',
               OUT/'RUN-INTERFACE.md', OUT/'README.md',
               ROOT/'RevE-ENGINEERING/controls/source-overlay/boards/my_machine_map.h',
               ROOT/'RevE-ENGINEERING/controls/grblhal-h7/Src/driver.c',
               ROOT/'RevE-ENGINEERING/controls/grblhal-h7/grbl/probe.c',
               ROOT/'RevE-ENGINEERING/controls/Kraken-V1.0-SCH.pdf',
               OUT/'sources/Panasonic-AQY212GS.pdf',
               OUT.parent/'motion/sources/omron-d2hw.pdf']
    before = {str(p.relative_to(ROOT)).replace('\\','/'): digest(p) for p in binding}
    spec = json.loads(SPEC.read_text(encoding='utf-8'))
    c, model = spec['components'], spec['model']
    check('Unique head connection identities', len({e['id'] for e in spec['connections']}) == len(spec['connections']))
    # Every logical series state, independent probe state, and supply state.
    head = Head(spec)
    for left, right, top, probe, power in itertools.product((False, True), repeat=5):
        head.state.update(left=left, right=right, top=top, float_healthy=probe)
        head.power = power
        check('Three contacts are series, separate from float', head.led('HEAD') == (power and left and right and top), left=left, right=right, top=top, float_healthy=probe, field_power=power)
        check('NC float responds independently', head.led('PROBE') == (power and probe), float_healthy=probe, field_power=power)
    head.state = dict(left=True, right=True, top=True, float_healthy=True)
    head.power = True
    for channel, prefix in [('HEAD','W_H'), ('PROBE','W_P')]:
        for e in spec['connections']:
            if e['id'].startswith(prefix):
                head.open_wires = {e['id']}
                check('Each open field conductor de-energizes its receiver', not head.led(channel), channel=channel, opened=e['id'])
    head.open_wires.clear()
    # Check galvanic separation with both outputs conducting. Semiconductor
    # optical control is never represented as a conductive LED-output edge.
    galvanic = [(e['a'],e['b']) for e in spec['connections']]
    field = reachable(galvanic, 'C')
    check('Field has no conductive path into controller domain', not {'PE11','3V3','LOGIC_0'} & field)
    check('Receiver output spans actual XH5/6 boundary', spec['model']['presence_boundary'] == ['XH:5','XH:6'])
    actual = next(e for e in CONTACTS if e.tag == 'XH:5-6')
    check('Existing graph boundary has correct control and polarity', actual.a == 'XH:5' and actual.b == 'XH:6' and actual.control == 'breakaway_seated' and not actual.closed_when_control_false)
    netlist = json.loads((OUT/'terminal-netlist.json').read_text(encoding='utf-8'))
    actual_rows = [{ 'kind':kind, **e.__dict__ } for kind, seq in [('wire',WIRES),('contact',CONTACTS),('diode',DIODES)] for e in seq]
    exported_rows = [{k:v for k,v in e.items() if k != 'closed_condition'} for e in netlist['connections']]
    check('Bound terminal netlist exactly matches the actual circuit definition', actual_rows == exported_rows and netlist['loads'] == LOADS)
    # Remove only upstream XH5/6, then close all downstream contacts. This
    # identifies every possible supplied coil without backfeeding the C rail.
    downstream = [(e.a,e.b) for e in WIRES] + [(e.a,e.b) for e in CONTACTS if e.tag != 'XH:5-6']
    reached = reachable(downstream, 'HEAD_SAFE')
    supplied = sorted(k for k,v in LOADS.items() if v in reached)
    check('HEAD_SAFE coil inventory covers both tool outputs and run arm only', supplied == ['K_RUN_ARM','K_TORCH_RUN','K_VFD_RUN'], loads=supplied)
    check('HEAD_SAFE also supplies IF_READY', 'IF_READY:IN+' in reached)
    vmin,vmax=spec['supply']['field_v']; lvmin,lvmax=spec['supply']['logic_v']
    tol=spec['supply']['resistor_effective_tolerance']; pm=model['photomos']; drop=spec['supply']['field_loop_drop_allowance_v']
    r=c['R_HEAD']['ohms']; shunt=c['R_HEAD_SHUNT']['ohms']
    minimum=(vmin-drop-pm['vf_max_v'])/(r*(1+tol))-pm['vf_max_v']/(shunt*(1-tol))
    maximum=vmax/(r*(1-tol))
    resistor_w=vmax*vmax/(r*(1-tol))
    check('Both channels use the same defined current-limit and shunt values', c['R_PROBE']['ohms']==r and c['R_PROBE_SHUNT']['ohms']==shunt)
    check('Minimum LED current exceeds recommended5mA', minimum >= pm['recommended_if_a'][0], minimum_A=minimum)
    check('Maximum LED current below recommended30mA', maximum <= pm['recommended_if_a'][1], maximum_A=maximum)
    check('Field resistor below half selected0.6W rating including output short', resistor_w < c['R_HEAD']['watts']/2, maximum_W=resistor_w)
    check('LED dissipation stays below75mW', maximum*pm['vf_max_v'] < pm['input_power_max_w'])
    check('Switch wetting minimum circuit voltage/current satisfied', vmin-drop > model['switch']['minimum_circuit_v'] and minimum > model['switch']['minimum_a'])
    check('Switch resistive current below24V1A reference rating', maximum < model['switch']['resistive_24v_a'])
    check('Field normal voltage below48V recommended PhotoMOS maximum', vmax < pm['load_recommended_max_v'])
    load=model['head_load']
    ready=(vmax-load['if_ready_vf_min_v'])/(load['if_ready_r_ohm']*(1-load['if_ready_r_tolerance']))
    bleed=vmax/(c['R_BLEED']['ohms']*(1-tol))
    normal=ready+load['run_arm_coil_cap_a']+load['normal_tool_coils']*load['each_tool_coil_cap_a']+bleed
    both=ready+load['run_arm_coil_cap_a']+load['abnormal_both_tool_coils']*load['each_tool_coil_cap_a']+bleed
    check('Normal complete HEAD_SAFE current below150mA', normal < load['output_design_cap_a'], maximum_A=normal)
    check('Both tool coils still below output allocation, without qualifying that fault', both < load['output_design_cap_a'], maximum_A=both)
    cap=load['output_design_cap_a']; voltage_drop=cap*pm['ron_max_ohm']; output_w=cap*cap*pm['ron_max_ohm']
    check('PhotoMOS output dissipation below400mW catalogue limit', output_w < pm['output_power_max_w'], maximum_W=output_w)
    off_v=pm['off_leak_max_a']*c['R_BLEED']['ohms']*(1+tol)
    check('Bleeder defines off output below0.2V with all loads disconnected', off_v < .2, maximum_V=off_v)
    check('Bleeder power below half selected rating', vmax*vmax/(c['R_BLEED']['ohms']*(1-tol)) < c['R_BLEED']['watts']/2)
    logic=model['logic']; pull=c['R_PULLUP']['ohms']; series=c['R_SERIES']['ohms']
    # An enabled internal pull-up strengthens high but increases closed-output
    # current. Include its smallest catalogue value in the low bound.
    pull_min=1/(1/(pull*(1-tol))+1/logic['internal_pullup_min_ohm'])
    low_r=series*(1+tol)+pm['ron_max_ohm']
    low_v=lvmax*low_r/(pull_min+low_r)+logic['pad_leak_allowance_a']*low_r
    high_v=lvmin-(pm['off_leak_max_a']+logic['pad_leak_allowance_a'])*pull*(1+tol)
    check('Healthy PE11 below conservative CMOS low threshold', low_v < lvmin*logic['vil_vdd_fraction'], maximum_V=low_v)
    check('Open PE11 above conservative CMOS high threshold', high_v > lvmax*logic['vih_vdd_fraction'], minimum_V=high_v)
    # Extra 1nF is an explicit layout/cable capacitance allowance, not a measured
    # cable property. Header placement keeps the capacitance measurable.
    capacitance=c['C_PROBE']['farads']*(1+c['C_PROBE']['tolerance'])+1e-9
    tau=pull*(1+tol)*capacitance
    # Worst low-to-high threshold using cross-corner supply/leakage bounds.
    rc_delay=-tau*math.log(1-lvmax*logic['vih_vdd_fraction']/high_v)
    response=pm['off_s']+rc_delay
    check('Probe catalogue-delay plus specified RC screen below1ms', response < .001, reference_response_s=response)
    check('NC probe polarity is healthyLOW/openHIGH', model['probe_healthy_logic']==0 and model['probe_open_logic']==1 and logic['probe_invert_setting']==0)
    # The mechanical head can remain assembled in its park during router use.
    # This input is deliberately not represented as a spindle touchplate.
    maptext=binding[8].read_text(encoding='utf-8')
    check('Current board map still assigns PE11 to probe', '#define AUXINPUT6_PORT GPIOE' in maptext and '#define AUXINPUT6_PIN 11' in maptext and '#define PROBE_PIN AUXINPUT6_PIN' in maptext)
    delay=model['delay_test']; cases=0
    for mode,pick,release in itertools.product(('router','plasma'),delay['relay_pickup_s'],delay['relay_dropout_s']):
        sim=Simulator(pick,release); head=Head(spec)
        sim.inputs['breakaway_seated']=False
        advance(sim,head,.010)
        sim.run(75.4 if mode=='router' else 12.4,**{mode:True,'bed_locked':mode=='router','bed_clear':mode=='plasma','minimum':True,'setup':False,'run_request':True})
        check('Held request on power-up remains inhibited with real head receiver', not sim.outputs()['router_run'] and not sim.outputs()['torch_run'], mode=mode,pickup=pick,dropout=release)
        sim.run(.3,run_request=False);sim.run(.3,run_request=True)
        run='router_run' if mode=='router' else 'torch_run'
        check('Deliberate selected request starts after receiver settles',sim.outputs()[run])
        for fault in ('left','right','top','field_supply','field_cable'):
            if fault in head.state: head.state[fault]=False
            elif fault=='field_supply': head.power=False
            else: head.open_wires={'W_H8U'}
            advance(sim,head,delay['fault_hold_s'])
            check('300ms physical head fault drops both tools and PG6 permission',not any(sim.outputs()[k] for k in ('router_run','torch_run','machine_permission')),mode=mode,fault=fault,pickup=pick,dropout=release)
            head.state.update(left=True,right=True,top=True);head.power=True;head.open_wires.clear()
            advance(sim,head,.3)
            check('Recovered head cannot restart a held tool request',not sim.outputs()['router_run'] and not sim.outputs()['torch_run'],mode=mode,fault=fault)
            sim.run(.3,run_request=False);sim.run(.3,run_request=True)
            check('Release and fresh request restores only selected tool',sim.outputs()[run] and not sim.outputs()['torch_run' if mode=='router' else 'router_run'])
        cases+=1
    # Expected uncovered faults are explicit counterexamples, not hidden safe
    # outcomes. A shorted output bypasses all three presence contacts.
    sim=Simulator();sim.run(12.4,plasma=True,bed_clear=True,minimum=True,setup=False)
    sim.run(.3,run_request=True);sim.failed_closed.add('XH:5-6');sim.run(.3,breakaway_seated=False)
    check('Counterexample: shorted presence output masks release',sim.outputs()['torch_run'])
    check('Counterexample: shorted probe output masks NC cable open',low_v < lvmin*logic['vil_vdd_fraction'])
    schedule=json.loads((OUT/'selected-components.json').read_text(encoding='utf-8'))
    q={p['part']:p['quantity'] for p in schedule['parts']}
    check('Whole controls schedule counts run plus two head isolators once',q.get('Panasonic AQY212GS')==3)
    check('Whole controls schedule counts existing mechanical switches once',q.get('Omron D2HW-C202MR')==1 and q.get('Omron D2HW-C203MR')==3)
    after={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in binding}
    check('All bound sources and artifacts remained unchanged during verification',before==after)
    result={'status':'PASS_WITH_EXPLICIT_LIMITS','scope':__doc__,'passed_checks':len(CHECKS),'checks':CHECKS,
            'verifier_file':str(SELF.relative_to(ROOT)).replace('\\','/'),'verifier_sha256_before':before[str(SELF.relative_to(ROOT)).replace('\\','/')],
            'verifier_sha256_after':digest(SELF),'verifier_changed':False,'source_sha256':after,
            'calculations':{'led_current_a':[minimum,maximum],'field_resistor_max_w':resistor_w,'head_normal_max_a':normal,'head_both_tool_max_a':both,
            'head_output_max_drop_v':voltage_drop,'head_output_max_w':output_w,'head_off_max_v':off_v,'probe_healthy_max_v':low_v,'probe_open_min_v':high_v,
            'probe_rc_threshold_s':rc_delay,'probe_reference_response_s':response,'probe_reference_travel_mm':response*logic['probe_speed_mm_s']},
            'dynamic_cases':cases,'delay_test':delay,'timing_reference_conditions':pm['test_condition'],'limits':spec['limits']}
    (OUT/'head-interface-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(result['status'],len(CHECKS),'checks',cases,'dynamic cases',flush=True)


if __name__=='__main__':
    main()
