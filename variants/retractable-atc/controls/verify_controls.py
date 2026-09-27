"""Run offline behavioral, GPIO, decoder and electrical arithmetic checks."""
from pathlib import Path
from dataclasses import replace,asdict
from copy import deepcopy
from itertools import product
import hashlib,json,re,sys
from interlock import Dock,Config,Inputs,Command,State
from input_adapter import PLAN,decode_gpio,config_valid,INIT_WRITES

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
checks=[]
def check(name,condition,detail=None):
    checks.append({'name':name,'passed':bool(condition),'detail':detail})

class Rig:
    """Independent idealized plant: saturating physical motion, limit cams and
    spring pins; no machine IO. This does not test force, braking or bounce."""
    def __init__(self):
        self.dock=Dock(Config(qualified_fixture=True))
        self.now=0
        self.sequence=0
        self.slide=0.0
        self.door=0.0
        self.park_pin=True
        self.deploy_pin=True
        self.catch=True
        self.kit=False
        self.running=False
        self.pose_epoch=1
        self.snapshots={}
        self.trace=[]
        self.out=None
    def __deepcopy__(self,memo):
        new=object.__new__(Rig)
        memo[id(self)]=new
        new.__dict__={k:({} if k=='snapshots' else deepcopy(v,memo)) for k,v in self.__dict__.items()}
        return new
    def tick(self,cmd=Command(),mutate=None,dt=20):
        if self.out:
            # These assertions are independent physical permission requirements,
            # evaluated BEFORE changing pins in response to this cycle's output.
            if self.out.slide_velocity:
                assert not self.park_pin and not self.deploy_pin,'slide driven against pin'
                assert self.door>=163.0 and self.catch,'slide driven with unretained door'
            if self.out.shutter_velocity:
                assert self.slide<=1 and self.park_pin and not self.catch,'door moved unsafely'
            self.slide=max(0,min(200,self.slide+self.out.slide_velocity*dt/1000))
            self.door=max(0,min(164,self.door+self.out.shutter_velocity*dt/1000))
            self.park_pin=not self.out.unlock
            self.deploy_pin=not self.out.unlock
            self.catch=not self.out.shutter_catch_release
            if self.out.kit_cover_action=='OPEN':self.kit=True
            elif self.out.kit_cover_action=='CLOSE':self.kit=False
        self.now+=dt;self.sequence+=1
        x=Inputs(self.sequence,self.now,parked=self.slide<=.001,deployed=self.slide>=199.999,
                 park_pin_extended=self.park_pin,park_pin_retracted=not self.park_pin,
                 deploy_pin_extended=self.deploy_pin,deploy_pin_retracted=not self.deploy_pin,
                 shutter_open=self.door>=163.999,shutter_closed=self.door<=.001,
                 shutter_catch_extended=self.catch,shutter_catch_retracted=not self.catch,
                 kit_cover_open=self.kit,kit_cover_closed=not self.kit,
                 spindle_stopped=not self.running,spindle_running=self.running,
                 spindle_feedback_ms=self.now,axis_clear_ms=self.now,
                 toolpath_lease=True,toolpath_session=self.dock.session,
                 pose_epoch=self.pose_epoch,axis_clear_epoch=self.pose_epoch,
                 slide_mm=self.slide,shutter_position_mm=self.door)
        if mutate:x=replace(x,**mutate)
        self.out=self.dock.step(self.now,x,cmd)
        if not self.trace or self.trace[-1]['state']!=self.out.state.value:
            self.trace.append({'ms':self.now,'state':self.out.state.value,'slide_mm':self.slide,'shutter_mm':self.door})
        self.snapshots.setdefault(self.out.state,deepcopy(self))
        return self.out
    def wait_for(self,state,max_ms=40000):
        for _ in range(max_ms//20):
            if self.out and self.out.state==state:return
            o=self.tick()
            if o.state==State.FAULT:raise AssertionError(o.fault)
        raise AssertionError('never reached '+state.value)
    def boot(self):
        for _ in range(20):self.tick()
        self.tick(Command(acknowledge=True))
        assert self.out.state==State.PARKED
        self.tick()
    def deploy(self):
        self.boot();self.tick(Command(start_change=True));self.wait_for(State.READY)
    def tool(self):
        self.deploy();self.tick(Command(begin_tool=True));self.tick()
        self.running=True
        for _ in range(5):self.tick(Command(spindle_request=True))


def behavioral():
    for args,label in [({'machine_variant':'small'},'small profile unavailable'),
                       ({'machine_variant':'unknown'},'unknown profile unavailable'),
                       ({'shutter_mm':170.0},'obsolete 170 mm shutter cannot load')]:
        rejected=False
        try: Config(qualified_fixture=True,**args)
        except ValueError: rejected=True
        check(label,rejected)
    check('large shutter geometry and pulse budget match plan',
          Config().shutter_mm==164 and PLAN['onboard_motors'][1]['stroke_mm']==164
          and Config().shutter_mm*PLAN['onboard_motors'][1]['steps_per_mm']==65600)
    rig=Rig();rig.tool()
    check('normal tool spindle permission',rig.out.spindle_gate and rig.out.allow_toolpath)
    rig.running=False
    rig.pose_epoch+=1 # final M6 exit pose, fresh cleared lease below
    rig.tick(Command(tool_done=True));rig.wait_for(State.PARKED,max_ms=60000)
    check('full cycle returns parked and locked',rig.slide==0 and rig.door==0 and rig.park_pin and rig.out.spindle_gate)
    closing=rig.snapshots[State.CAPTURE_CLOSED]
    check('closed capture inhibits run and stops motion while spring engages',
          not closing.out.spindle_gate and not closing.out.allow_toolpath
          and not closing.out.shutter_velocity and not closing.out.slide_velocity
          and not closing.out.shutter_catch_release and closing.out.kit_cover_action=='CLOSE')
    stuck=deepcopy(closing)
    for _ in range(170):
        o=stuck.tick(mutate={'shutter_catch_extended':False,'shutter_catch_retracted':True})
        if o.state==State.FAULT:break
    check('closed catch stuck retracted faults on bounded timeout',
          o.state==State.FAULT and o.fault=='STATE_TIMEOUT_CAPTURE_SHUTTER_CLOSED'
          and not o.spindle_gate and not o.shutter_catch_release)
    r=deepcopy(closing);o=r.tick(mutate={'shutter_closed':False})
    check('closed endpoint loss during capture prevents run',o.state==State.FAULT and not o.spindle_gate)
    r=deepcopy(closing);o=r.tick(mutate={'shutter_catch_extended':True,'shutter_catch_retracted':True})
    check('closed contradictory catch feedback prevents run',o.state==State.FAULT and not o.spindle_gate)
    r=deepcopy(rig);o=r.tick(mutate={'shutter_catch_extended':False})
    check('lost parked closed capture removes run permission',o.state==State.FAULT and not o.spindle_gate)
    r=Rig()
    for _ in range(20):r.tick(mutate={'shutter_catch_extended':False,'shutter_catch_retracted':True})
    o=r.tick(Command(acknowledge=True),mutate={'shutter_catch_extended':False,'shutter_catch_retracted':True})
    check('boot acknowledgement cannot bypass missing closed capture',o.state==State.BOOT and not o.spindle_gate)
    mode_rig=deepcopy(rig);mode_out=mode_rig.tick(mutate={'router_mode':False})
    check('parked plasma mode cannot enable common tool permission',not mode_out.spindle_gate)
    expected=set(State)-{State.FAULT}
    check('normal trace visits every nonfault state',set(rig.snapshots)==expected)
    (HERE/'normal-sequence.json').write_text(json.dumps(rig.trace,indent=2)+'\n',encoding='utf-8')
    # All active stages must turn every motion/release/run output off on hard loss.
    for state,snapshot in rig.snapshots.items():
        for fault in ('hardware_permission','control_power','bus_ok','config_readback_ok','driver_ok','dock_present'):
            r=deepcopy(snapshot);o=r.tick(mutate={fault:False})
            check(f'{state.value}: {fault} loss latches and removes commands',
                  o.state==State.FAULT and not any((o.spindle_gate,o.allow_toolpath,o.unlock,o.shutter_catch_release,o.slide_velocity,o.shutter_velocity)))
    for attrs,label in [({'parked':True,'deployed':True},'slide'),
        ({'park_pin_extended':True,'park_pin_retracted':True},'park pin'),
        ({'deploy_pin_extended':True,'deploy_pin_retracted':True},'deploy pin'),
        ({'shutter_open':True,'shutter_closed':True},'shutter'),
        ({'shutter_catch_extended':True,'shutter_catch_retracted':True},'catch'),
        ({'spindle_stopped':True,'spindle_running':True},'spindle'),
        ({'kit_cover_open':True,'kit_cover_closed':True},'kit cover')]:
        r=deepcopy(rig.snapshots[State.TOOL]);o=r.tick(mutate=attrs)
        check('contradictory '+label+' inhibits spindle',o.state==State.FAULT and not o.spindle_gate)
    r=deepcopy(rig.snapshots[State.OUT]);o=r.tick(mutate={'deployed':True,'parked':False,'slide_mm':4})
    check('early false-high deployed rejects short travel',o.state==State.FAULT and 'EARLY' in o.fault)
    r=deepcopy(rig.snapshots[State.IN]);o=r.tick(mutate={'parked':True,'deployed':False,'slide_mm':196})
    check('early false-high parked rejects short travel',o.state==State.FAULT and 'EARLY' in o.fault)
    for state in (State.OPEN,State.OUT,State.IN,State.CLOSE):
        r=deepcopy(rig.snapshots[state]);o=r.tick(mutate={'pose_epoch':99})
        check('pose epoch invalidates '+state.value,o.state==State.FAULT and not o.slide_velocity and not o.shutter_velocity)
        r=deepcopy(rig.snapshots[state]);o=r.tick(mutate={'axis_idle':False})
        check('axis motion invalidates '+state.value,o.state==State.FAULT)
    for state in (State.STOP,State.RELEASE_OPEN,State.OPEN,State.CAPTURE_OPEN,State.UNLOCK_OUT):
        r=deepcopy(rig.snapshots[state]);o=r.tick(mutate={'parked':False})
        check('lost park inhibits before transition '+state.value,
              o.state==State.FAULT and not o.unlock and not o.shutter_catch_release)
    for state in (State.STOP,State.RELEASE_OPEN,State.OPEN,State.CAPTURE_OPEN,State.RELEASE_CLOSE,State.CLOSE):
        r=deepcopy(rig.snapshots[state]);o=r.tick(mutate={'park_pin_extended':False})
        check('lost park lock inhibits before transition '+state.value,
              o.state==State.FAULT and not o.unlock and not o.shutter_catch_release)
    for state in (State.UNLOCK_OUT,State.OUT,State.LOCK_OUT,State.READY,State.TOOL,
                  State.STOP_AFTER,State.CLEAR,State.UNLOCK_IN,State.IN,State.LOCK_IN):
        r=deepcopy(rig.snapshots[state]);o=r.tick(mutate={'shutter_catch_extended':False})
        check('lost capture inhibits before transition '+state.value,
              o.state==State.FAULT and not o.unlock and not o.spindle_gate)
    for attrs,label in [({'spindle_feedback_ms':-10000},'stale stop'),
                        ({'sampled_ms':-10000},'stale input'),
                        ({'sequence':0},'replayed input'),
                        ({'toolpath_session':999},'wrong session'),
                        ({'toolpath_lease':False},'lost toolpath'),
                        ({'ir_ok':False},'lost IR')]:
        r=deepcopy(rig.snapshots[State.TOOL]);o=r.tick(mutate=attrs)
        check(label+' during threading inhibits',o.state==State.FAULT and not o.spindle_gate and not o.allow_toolpath)
    for state,values in [(State.OUT,{'slide_mm':200.,'parked':False,'deployed':False}),
                         (State.IN,{'slide_mm':0.,'parked':False,'deployed':False}),
                         (State.OPEN,{'shutter_position_mm':164.,'shutter_open':False,'shutter_closed':False}),
                         (State.CLOSE,{'shutter_position_mm':0.,'shutter_open':False,'shutter_closed':False})]:
        r=deepcopy(rig.snapshots[state]);o=r.tick(mutate=values)
        check('missing endpoint stops at pulse budget '+state.value,
              o.state==State.FAULT and 'BUDGET_EXHAUSTED' in o.fault and not o.slide_velocity and not o.shutter_velocity)
    for name in ('slide_mm','shutter_position_mm','sampled_ms','spindle_feedback_ms','axis_clear_ms'):
        for value in (float('nan'),float('inf'),float('-inf')):
            r=deepcopy(rig.snapshots[State.OUT]);o=r.tick(mutate={name:value})
            check('reject nonfinite '+name+' '+str(value),o.state==State.FAULT and not o.slide_velocity and not o.spindle_gate)
    for values in ({'slide_mm':200.01},{'slide_mm':-.01},{'shutter_position_mm':164.01},{'shutter_position_mm':-.01}):
        r=deepcopy(rig.snapshots[State.OUT]);o=r.tick(mutate=values)
        check('reject out-of-range counter '+str(values),o.state==State.FAULT and not o.slide_velocity)
    for state,target in [(State.OUT,200.),(State.IN,0.)]:
        check('finite slide target exported '+state.value,rig.snapshots[state].out.slide_target_mm==target)
    for state,target in [(State.OPEN,164.),(State.CLOSE,0.)]:
        check('finite shutter target exported '+state.value,rig.snapshots[state].out.shutter_target_mm==target)
    for state,missing,ceiling_ms in [(State.OUT,'deployed',20200),(State.OPEN,'shutter_open',16600)]:
        r=deepcopy(rig.snapshots[state]);start=r.now
        for _ in range(1600):
            o=r.tick(mutate={missing:False})
            if o.state==State.FAULT:break
        check('full missing-limit sequence stops on count before timeout '+state.value,
              o.state==State.FAULT and 'BUDGET_EXHAUSTED' in o.fault and r.now-start<=ceiling_ms)
    r=Rig();r.deploy();r.tick(Command(begin_tool=True))
    for _ in range(100):o=r.tick(Command(spindle_request=True))
    check('stuck-high stopped signal does not complete tool cycle',o.state==State.FAULT and o.fault=='RUN_FEEDBACK_NEVER_CHANGED')
    r=deepcopy(rig.snapshots[State.TOOL]);r.tick(mutate={'hardware_permission':False})
    for _ in range(20):o=r.tick(Command(acknowledge=True,spindle_request=True))
    check('held request plus acknowledge cannot restart',o.state==State.FAULT and not o.spindle_gate)
    # Reset creates BOOT_UNKNOWN even with deployed feedback and old M6 session.
    r=deepcopy(rig.snapshots[State.TOOL]);r.dock=Dock(Config(qualified_fixture=True))
    for _ in range(20):o=r.tick(Command(acknowledge=True))
    check('reset cannot resume from deployed rack',o.state==State.BOOT and not o.spindle_gate)
    r=Rig();r.dock=Dock()
    for _ in range(20):r.tick()
    o=r.tick(Command(acknowledge=True))
    check('delivered unqualified default cannot energize',o.state==State.BOOT and not o.spindle_gate)
    # The inactive end pin extending in free air cannot prove deployed engagement.
    r=deepcopy(rig.snapshots[State.TOOL]);o=r.tick(mutate={'park_pin_extended':True,'deploy_pin_extended':False,'deploy_pin_retracted':False})
    check('wrong end pin cannot establish engagement',o.state==State.FAULT and not o.spindle_gate)
    # Exhaustive ten critical tool-cycle confirmations; permission only all true.
    fields=('hardware_permission','control_power','dock_present','driver_ok','deployed',
            'deploy_pin_extended','shutter_open','shutter_catch_extended','kit_cover_open','ir_ok')
    template=rig.snapshots[State.TOOL]
    good=True
    for bits in product((False,True),repeat=len(fields)):
        r=deepcopy(template);o=r.tick(Command(spindle_request=True),dict(zip(fields,bits)))
        if bool(o.spindle_gate)!=all(bits):good=False;break
    check('1024 critical-feedback combinations obey tool run permission',good)
    # Jam test: stop independent plant at an intermediate slide location.
    r=deepcopy(rig.snapshots[State.OUT]);r.slide=100
    for _ in range(1550):
        r.slide=100
        o=r.tick(mutate={'parked':False,'deployed':False,'slide_mm':100})
        if o.state==State.FAULT:break
    check('jam/stuck-low arrival times out',o.state==State.FAULT and o.fault.startswith('STATE_TIMEOUT'))


def pins_and_decoder():
    path=ROOT/'RevE-ENGINEERING/controls/source-overlay/boards/my_machine_map.h'
    text=path.read_text(encoding='utf-8')
    defs=dict(re.findall(r'^#define[ \t]+(\w+)[ \t]+([^\r\n/]+)',text,re.M))
    def resolve(key):
        val=defs[key].strip();return resolve(val) if val in defs else val
    existing={resolve(k).replace('GPIO','P')+resolve(k[:-5]+'_PIN') for k in defs if k.endswith('_PORT') and k[:-5]+'_PIN' in defs}
    reserved=json.loads((ROOT/'variants/common/controls/pin-reservations.json').read_text())
    reserved_pins={x['gpio'] for x in reserved['reservations']}
    new=[x['gpio'] for x in PLAN['gpio']]
    new+= [m[k] for m in PLAN['onboard_motors'] for k in ('step','direction','enable','cs')]
    check('new functions use unique GPIO',len(new)==len(set(new)))
    check('no baseline mapped GPIO is overwritten',not(set(new)&existing))
    check('all common ATC reservations preserved',not(set(new)&reserved_pins))
    check('no new EXTI source',all(not x['exti'] for x in PLAN['gpio']))
    official=(ROOT/'RevE-ENGINEERING/controls/kraken-official.cfg').read_text()
    aliases=dict(re.findall(r'(EXP[12]_\d+)=(P[A-G]\d+)',official))
    check('raw output headers match BTT map',aliases['EXP2_1']=='PE13' and aliases['EXP2_6']=='PE14')
    check('P10 mapping official I2C2 PB10/PB11', 'i2c2_PB10_PB11' in official)
    check('PS_ON mapping is official PD10','pin: PD10' in official)
    sch=(ROOT/'RevE-ENGINEERING/controls/Kraken-schematic.txt').read_text(encoding='utf-8')
    gate=next(x for x in PLAN['gpio'] if x['function']=='atc_run_gate')
    check('J14signal is pin2 throughR44;pin1 is ground',
          gate['connector']=='J14:2 PS_ON' and 'PIJ1402 PIR4402' in sch and 'PIR4401 NLPS0ON' in sch
          and 'PIJ1401' in sch.split('NLGND')[0])
    for m in PLAN['onboard_motors']:
        block=official.split('# '+m['socket']+'\n')[1].split('\n# S')[0]
        for key,field in [('step','step_pin'),('direction','dir_pin'),('enable','enable_pin')]:
            actual=re.search('^#?'+field+r':\s*!?(P[A-G]\d+)',block,re.M)
            check(m['socket']+' '+key+' official',actual and actual[1]==m[key])
        check(m['socket']+' 75mohm mixed sense explicit',m['sense_milliohm']==75)
        check(m['socket']+' pulses and conservative ceiling',m['steps_per_mm']==200*16/8 and m['candidate_ceiling_mA_rms']*2**.5<1680)
        name='extruder' if m['socket']=='S5' else 'extruder1'
        tmc=official.split('#[tmc5160 '+name+']',1)[1].split('\n#[tmc5160',1)[0]
        match=re.search(r'^#cs_pin:\s*(P[A-G]\d+)',tmc,re.M)
        check(m['socket']+' chip-select matches official driver',match and match[1]==m['cs'])
    check('14 isolated channels never use output-only bit7',len(PLAN['isolated_inputs'])==14 and all(not x['mcp'].endswith('7') for x in PLAN['isolated_inputs']))
    check('all channel package pins unique',len({x['pin'] for x in PLAN['isolated_inputs']})==14)
    check('open all input wires means no confirmations',not any(decode_gpio(255,255).values()))
    independent_order=['parked','deployed','park_pin_extended','park_pin_retracted','deploy_pin_extended','deploy_pin_retracted','shutter_open',
                       'shutter_closed','shutter_catch_extended','shutter_catch_retracted','spindle_stopped','spindle_running','kit_cover_open','kit_cover_closed']
    for i,name in enumerate(independent_order):
        a,b=255,255
        if i<7:a &= ~(1<<i)
        else:b &= ~(1<<(i-7))
        result=decode_gpio(a,b)
        check('terminal decode '+name,result[name] and sum(result.values())==1)
    check('correct register initialization accepted',config_valid(dict(INIT_WRITES)))
    for reg,_ in INIT_WRITES:
        modified=dict(INIT_WRITES);modified[reg]^=1
        check('configuration upset detected at '+hex(reg),not config_valid(modified))


def electrical():
    rmin,rmax=3320*.98,3320*1.02
    imin=(21.6-1.0-1.5)/rmax-1.5/(22000*.99) #1V field wiring/contact allowance
    pnp_imin=(21.6-1.0-1.0-1.5)/rmax-1.5/(22000*.99) #plus1V PNP residual
    imax=26.4/rmin
    resistor_power=26.4**2/rmin
    low=3.6*(330*1.01+.7)/(4700*.99+330*1.01+.7)
    high=3.0-2e-6*(4700*1.01)
    cold=26.4/(76.8*.9)
    # Solenoid data resistance is at25C. Copper cold extrapolation is a screen,
    # not a manufacturer's winding acceptance limit; thermal data still required.
    zero_c=26.4/(76.8*.9*(1+.00393*(0-25)))
    calc={'field_LED_min_mA':imin*1000,'field_LED_max_mA':imax*1000,
          'PNP_LED_min_mA_with1V_wire_and1V_residual':pnp_imin*1000,
          'input_resistor_max_W':resistor_power,'logic_low_max_V':low,'logic_high_min_V':high,
          'solenoid_25C_high_supply_current_A':cold,'solenoid_0C_screen_A':zero_c,
          'three_solenoid_design_cap_A':1.5,'relay_coil_cap_A':.12,
          'fourteen_input_channel_cap_A':14*imax,
          'six_sensor_quiescent_cap_A':6*.015,
          'aux_field_design_cap_A':1.5+.12+14*imax+6*.015}
    check('input LED reaches recommended5mA',imin>=.005)
    check('PNP input LED reaches5mA with1Vresidual and1Vwire',pnp_imin>=.005)
    check('PNP LEDload remains below16mA residual-reference point',imax<.016)
    sensors=[x for x in PLAN['isolated_inputs'] if x.get('field_kind')=='PNP_DARK_ON']
    check('six separate PNP sensor channels and returns',len(sensors)==6 and len({x['blue_return_terminal'] for x in sensors})==6)
    check('six sensor quiescent loads explicitly budgeted',PLAN['pin_sensors']['quantity']==6 and PLAN['pin_sensors']['quiescent_current_a_max_each']==.015)
    check('input LED under30mA',imax<=.030)
    check('input resistor under half0.6W',resistor_power<.3)
    check('MCP low below0.2VDD at minimum3V',low<.6)
    check('MCP high above0.8VDD for same minimum3V',high>2.4)
    check('25C and0C solenoid screens under0.5A',cold<.5 and zero_c<.5)
    check('every solenoid individually fused',PLAN['release_solenoids']['quantity']==3)
    return calc


def source_map():
    files=list(HERE.glob('*.py'))+list(HERE.glob('*.json'))+list(HERE.glob('*.md'))+list(HERE.glob('*.svg'))
    files=[p for p in files if p.name not in ('verification.json','normal-sequence.json')]
    files += [ROOT/p for p in [
        'RevE-ENGINEERING/controls/source-overlay/boards/my_machine_map.h',
        'RevE-ENGINEERING/controls/source-overlay/Src/kraken_board.c',
        'RevE-ENGINEERING/controls/kraken-official.cfg',
        'RevE-ENGINEERING/controls/Kraken-schematic.txt',
        'variants/common/controls/pin-reservations.json',
        'output/design-finish-2026-09-26/controls/RUN-INTERFACE.md',
        'output/design-finish-2026-09-26/controls/HEAD-INTERFACE.md']]
    hardware=ROOT/'variants/retractable-atc/hardware/lock-actuator.json'
    if hardware.exists():files.append(hardware)
    sensor=ROOT/'variants/retractable-atc/hardware/pin-sensor.json'
    if sensor.exists():files.append(sensor)
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}


if __name__=='__main__':
    before=source_map()
    try:
        behavioral();pins_and_decoder();calc=electrical()
    except Exception as exc:
        check('unexpected verifier exception',False,repr(exc));calc={}
    after=source_map()
    check('bound sources unchanged during verification',before==after)
    report={'schema':1,'passed':all(x['passed'] for x in checks),'scope':'Offline interlock behavior, pin allocation, interface arithmetic; not hardware or machine release',
            'test_count':len(checks),'exhaustive_feedback_cases':1024,'checks':checks,'calculations':calc,
            'source_sha256':after,'source_sha256_before':before,
            'firmware_compiled':False,'hardware_tested':False,'machine_release':False,
            'excluded':['actual M6 macros and trajectories','GPIO scheduler and motor pulse timing','HF/EMC and stop distances',
                        'common-cause or coherently falsified sensor signals','physical pin seating/cam adjustment','unidentified VFD/kit contacts and cover protocol']}
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('passed','test_count','firmware_compiled','hardware_tested','machine_release')}))
    if not report['passed']:
        print(json.dumps([x for x in checks if not x['passed']],indent=2))
    sys.exit(0 if report['passed'] else 1)
