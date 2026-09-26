"""Exercise the actual terminal graph, including relay delays and bounded faults."""
from pathlib import Path
import hashlib,itertools,json
from circuit import Simulator,WIRES,CONTACTS,DIODES,LOADS,write_netlist

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
checks=[]
def check(name,result,**evidence):
    checks.append({'check':name,'passed':bool(result),**evidence})
    assert result,(name,evidence)

def ready_fill(pickup=.01,dropout=.02):
    s=Simulator(pickup,dropout)
    s.run(12.25,plasma=True,bed_clear=True)
    return s

def main():
    write_netlist()
    check('Every contact tag is unique',len({e.tag for e in CONTACTS})==len(CONTACTS))
    check('Every physical relay uses at most its purchased poles',all(
        len({e.tag.split(':')[1].split('-')[0] for e in CONTACTS if e.tag.startswith(k+':')})<=
        (4 if k.startswith('KM_') else 2) for k in LOADS if k.startswith('K')))
    sequence_count=0
    for pick,drop in itertools.product((.005,.010,.020),(.005,.020,.050)):
        s=ready_fill(pick,drop)
        check('No fill without deliberate press',not s.outputs()['pump'],pickup=pick,dropout=drop)
        s.run(.15,fill_pressed=True);check('Deliberate fill starts',s.outputs()['pump'],pickup=pick,dropout=drop)
        s.run(.15,fill_pressed=False);check('Fill self-holds after release',s.outputs()['pump'])
        s.run(.15,fill_stop_healthy=False);check('Normal fill stop removes pump',not s.outputs()['pump'])
        s.run(.15,fill_pressed=True,fill_stop_healthy=True)
        check('Held fill does not restart after fill-stop',not s.outputs()['pump'])
        s.run(.15,fill_pressed=False);s.run(.15,fill_pressed=True)
        check('Release then press rearms after fill-stop',s.outputs()['pump'])
        # Each named healthy input is a physical open-contact fault.
        for field in ('stop_ok','high_high_healthy','reservoir_healthy','bed_clear'):
            s=ready_fill(pick,drop);s.run(.15,fill_pressed=True)
            s.run(.15,**{field:False});check('Fault stops pump: '+field,not s.outputs()['pump'])
            s.run(.15,**{field:True});check('Held button does not recover: '+field,not s.outputs()['pump'])
        for state in ({'drain_override':True},{'setup':False},{'plasma':False}):
            s=ready_fill(pick,drop);s.run(.15,fill_pressed=True);s.run(.15,**state)
            check('Mode/setup/override stops pump',not s.outputs()['pump'],change=state)
        s=Simulator(pick,drop);s.run(12.25,plasma=True,bed_clear=True,fill_pressed=True)
        check('Held FILL on power-up never starts pump',not s.outputs()['pump'])
        sequence_count+=1
    for short in ('P_CMD','P_LIMIT'):
        for field in ('high_high_healthy','reservoir_healthy'):
            s=ready_fill();s.run(.15,fill_pressed=True);s.ssr_failed_short.add(short)
            s.run(.15,**{field:False})
            check('Single SSR short interrupted by healthy-chain loss',not s.outputs()['pump'],short=short,field=field)
    # DC power loss directly removes pump and tool-coil energy, independent of
    # relay output-state delays. Actual mechanical contacts release afterward.
    s=ready_fill();s.run(.15,fill_pressed=True);s.run(.15,power=False)
    check('Power loss removes fill and arm',not any(s.outputs()[k] for k in ('pump','fill','armed')))
    s.run(12.25,power=True);check('Held FILL after power restoration stays off',not s.outputs()['pump'])
    for mode,pick,drop in itertools.product(('router','plasma'),(.005,.010,.020),(.005,.020,.050)):
        s=Simulator(pick,drop);s.run(75.4 if mode=='router' else 12.4,**{mode:True,'bed_locked':mode=='router','bed_clear':mode=='plasma','minimum':True,'setup':False,'run_request':True})
        check('Held request cannot start tool after cold power-up',not s.outputs()['router_run'] and not s.outputs()['torch_run'],mode=mode,pickup=pick,dropout=drop)
        s.run(.3,run_request=False);s.run(.3,run_request=True)
        out=s.outputs();check('Only selected tool can run: '+mode,out[mode+'_run' if mode=='router' else 'torch_run'] and not out['torch_run' if mode=='router' else 'router_run'])
        for field in ('hardware_stop_ok','door_closed','breakaway_seated'):
            s.run(.3,**{field:False});check('Hardware chain stops tools: '+field,not s.outputs()['router_run'] and not s.outputs()['torch_run'])
            check('Hardware permission loss also reaches controller PG6: '+field,not s.outputs()['machine_permission'])
            s.run(.3,**{field:True})
            check('Held run cannot resume after permission recovery: '+field,not s.outputs()['router_run'] and not s.outputs()['torch_run'])
            s.run(.3,run_request=False);s.run(.3,run_request=True)
            check('Fresh run request after recovery starts selected tool',s.outputs()['router_run' if mode=='router' else 'torch_run'])
        s.run(.3,power=False);s.run(75.4 if mode=='router' else 12.4,power=True)
        check('Held run after power restoration stays off',not s.outputs()['router_run'] and not s.outputs()['torch_run'])
    s=Simulator();s.run(74.9,router=True,bed_locked=True,setup=False)
    check('Drain timer cannot ready early',not s.outputs()['ready'])
    s.run(.35);check('Drain dwell eventually permits ready',s.outputs()['ready'])
    s.run(.15,empty=False);check('Lost empty contact inhibits router ready',not s.outputs()['ready'])
    # Backfeed test: DRAIN override must not energize router mode relay.
    s=Simulator();s.run(.25,drain_override=True)
    check('Drain override does not backfeed mode relays',not s.states['KM_R'] and not s.states['KM_P'] and s.outputs()['drain'])
    # This is a deliberate falsification probe, not a hidden blanket pass.
    s=ready_fill(dropout=.050);s.run(.15,fill_pressed=True)
    s.run(.005,stop_ok=False);s.run(.05,stop_ok=True)
    short_pulse_restarts=s.outputs()['pump']
    check('Model exposes short-interruption limitation',short_pulse_restarts)
    # Minimum wetting and maximum heating include supply/resistor tolerances.
    vmin,vmax=21.6,26.4;rtc=680.;rready=1000.
    timer_min_w=vmin*vmin/(rtc*1.05)
    timer_max_w=vmax*vmax/(rtc*.95)
    input_min_ma=(vmin-1.4)/(rready*1.05)*1000
    input_max_ma=(vmax-1.0)/(rready*.95)*1000
    input_resistor_max_w=(vmax-1.0)**2/(rready*.95)
    float_max_ma=112+vmax/(rtc*.95)*1000
    check('Timer output minimum resistive load exceeds 500mW',timer_min_w>=.5,minimum_W=timer_min_w)
    check('Timer load resistor remains below half 3W rating',timer_max_w<=1.5,maximum_W=timer_max_w)
    check('Ready input meets 300mW/5V/5mA minimum',vmin*input_min_ma>=300 and input_min_ma>=5,minimum_mA=input_min_ma)
    check('Input resistor below half 2W rating',input_resistor_max_w<=1,maximum_W=input_resistor_max_w)
    check('Conservative common float load stays below200mA',float_max_ma<=200,maximum_mA=float_max_ma)
    r={'status':'PASS_WITH_EXPLICIT_LIMITS','checks':checks,'passed_checks':len(checks),'dynamic_delay_combinations':sequence_count,
       'input_domain_v':[vmin,vmax], 'input_led_current_ma':[input_min_ma,input_max_ma],
       'simulation_assumptions':{'pickup_s':[.005,.010,.020],'dropout_s':[.005,.020,.050],'timer_recovery_s':.100,'tested_fill_fault_duration_s':.150,'tested_tool_fault_duration_s':.300,'photomos_catalogue_on_s':.005,'photomos_catalogue_off_s':.0005},
       'short_interrupt_counterexample':{'interruption_s':.005,'relay_dropout_s':.050,'held_button_restarts':bool(short_pulse_restarts)},
       'limits':['Relays with unspecified suppressed dropout do not guarantee release-to-rearm for arbitrary brief interruptions. Bench-record dropout and qualify a minimum interruption; use a separately latched monitored fault if shorter events must latch.',
                 'Mutually exclusive selector contacts are a normal-operation prerequisite. Welded mode/command contacts and multiple failures are not safety-qualified.',
                 'XH stop/door/breakaway contacts, output isolator hardware, dry tool interface, firmware pin polarity, wet levels and actual relay timing require commissioning.',
                 'No MCU firmware, mains switching, safety category, brake sequencing or raw arc-voltage isolation is modeled.'],
       'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'circuit.py',Path(__file__))},
       'artifact_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (OUT/'terminal-netlist.json',OUT/'TERMINALS.md',OUT/'RUN-INTERFACE.md',
                                    OUT/'SPEED-INTERFACE.md',OUT/'selected-components.json',OUT/'README.md',
                                    OUT/'head-interface.json',OUT/'HEAD-INTERFACE.md')}}
    (OUT/'verification.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(r['status'],r['passed_checks'],'checks',sequence_count,'delay combinations',flush=True)


if __name__=='__main__':main()
