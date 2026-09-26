"""Rev I low-voltage terminal netlist and finite-delay relay simulation.

This is a wiring-graph model, not firmware and not a certified safety function.
Loads terminate at 0 V; they do not connect their input nets together. Diodes
are directed, wire/contact connections bidirectional. Relay contacts use the
previous mechanical state and pickup/dropout takes finite, configurable time.
"""
from dataclasses import dataclass
from collections import defaultdict, deque
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent


@dataclass(frozen=True)
class Edge:
    a:str
    b:str
    tag:str
    control:str=''
    # Logic inversion is independent of a purchased contact's factory NO/NC.
    closed_when_control_false:bool=False
    directed:bool=False
    physical_form:str=''
    device:str=''


def definition():
    wires=[];contacts=[];diodes=[];loads={}
    def wire(a,b):wires.append(Edge(a,b,f'W{len(wires)+1:03}'))
    def contact(tag,a,b,control,inverted=False,physical_form='',device=''):
        if not physical_form:
            physical_form=('NC' if inverted else 'NO') if tag.startswith(('K_', 'KM_', 'T_')) else 'External closure; device form unspecified'
        contacts.append(Edge(a,b,tag,control,inverted,physical_form=physical_form,device=device))
    def diode(tag,a,b):diodes.append(Edge(a,b,tag,directed=True))
    def branch(source,tag,control,dest,inverted=False,physical_form='',device=''):
        a,b=tag.split(':')[0]+':'+tag.split(':')[1].split('-')[0],tag.split(':')[0]+':'+tag.split('-')[1]
        wire(source,a);contact(tag,a,b,control,inverted,physical_form,device);wire(b,dest)
    def field_branch(source,terminals,tag,control,dest,physical_form,device):
        first,last=terminals
        wire(source,first);branch(first,tag,control,last,physical_form=physical_form,device=device);wire(last,dest)
    def coil(tag,source):wire(source,tag+':A1');wire(tag+':A2','XW:2');loads[tag]=tag+':A1'
    # Branch fuses and field terminals. C/V are separately fused 24 V nodes.
    wire('24V','XW:1');wire('XW:1','F_CONTROL:1');wire('F_CONTROL:2','XW:3');wire('XW:3','C')
    contact('F_CONTROL','F_CONTROL:1','F_CONTROL:2','f_control',physical_form='Fuse continuity')
    wire('XW:1','F_VALVE:1');wire('F_VALVE:2','XW:4');wire('XW:4','V')
    contact('F_VALVE','F_VALVE:1','F_VALVE:2','f_valve',physical_form='Fuse continuity')
    # A two-contact selector drives two 4-pole relays; no invented extra blocks.
    branch('C','MODE_R:13-14','router','MR',physical_form='NO',device='MODE / Schneider XB5AD33, router block')
    branch('C','MODE_P:13-14','plasma','MP',physical_form='NO',device='MODE / Schneider XB5AD33, plasma block')
    branch('MR','KM_P:41-42','KM_P','KMR_COIL',True);coil('KM_R','KMR_COIL')
    branch('MP','KM_R:41-42','KM_R','KMP_COIL',True);coil('KM_P','KMP_COIL')
    branch('C','XW:11-12','empty','EMPTY_COIL');coil('K_EMPTY','EMPTY_COIL')
    branch('C','XW:13-14','minimum','MIN_COIL');coil('K_MIN','MIN_COIL')
    branch('C','XW:21-22','stop_ok','STOP_HEALTHY')
    branch('STOP_HEALTHY','XW:17-18','high_high_healthy','H')
    branch('C','KM_R:11-14','KM_R','DR_REQ')
    branch('C','AUTO_DRAIN:13-14','drain_override','DO_REQ',physical_form='NO',device='Schneider XB5AD25')
    diode('D_R','DR_REQ','DRAIN_COIL');diode('D_O','DO_REQ','DRAIN_COIL');coil('K_DRAIN','DRAIN_COIL')
    branch('V','K_DRAIN:11-14','K_DRAIN','DV');wire('DV','XW:7');wire('XW:8','XW:2')
    branch('C','KM_P:11-14','KM_P','PCLOSE')
    branch('PCLOSE','K_DRAIN:21-22','K_DRAIN','TC_POWER',True);coil('T_CLOSE','TC_POWER')
    branch('H','KM_P:21-24','KM_P','P_HEALTHY')
    field_branch('P_HEALTHY',('XW:23','XW:24'),'BED_P:13-14','bed_clear','P_CLEAR','NO','BED_CONFIRM / Schneider XB5AG03, plasma block')
    branch('P_CLEAR','T_CLOSE:15-18','T_CLOSE','PC')
    # Permanent timer minimum-load resistor, independent of downstream contacts.
    wire('PC','R_TC:1');wire('R_TC:2','XW:2')
    branch('PC','SETUP_RUN:21-22','setup','SETUP_PC',physical_form='NC',device='Schneider XB5AD25')
    branch('SETUP_PC','XW:19-20','reservoir_healthy','L')
    wire('L','P_LIMIT:A1');wire('P_LIMIT:A2','XW:2')
    branch('L','XW:15-16','fill_stop_healthy','A')
    branch('A','FILL:21-22','fill_pressed','ARM_COIL',True,physical_form='NC',device='Schneider XB5AA35')
    branch('A','K_ARM:11-14','K_ARM','ARM_COIL');coil('K_ARM','ARM_COIL')
    branch('A','K_ARM:21-24','K_ARM','AF')
    branch('AF','FILL:13-14','fill_pressed','FILL_COIL',physical_form='NO',device='Schneider XB5AA35')
    branch('AF','K_FILL:11-14','K_FILL','FILL_COIL');coil('K_FILL','FILL_COIL')
    wire('FILL_COIL','P_CMD:A1');wire('P_CMD:A2','XW:2')
    branch('DV','KM_R:21-24','KM_R','RD')
    branch('RD','K_EMPTY:21-24','K_EMPTY','TD_POWER');coil('T_DRAIN','TD_POWER')
    field_branch('H',('XW:25','XW:26'),'BED_R:13-14','bed_locked','R_LOCKED','NO','BED_CONFIRM / Schneider XB5AG03, router block')
    branch('R_LOCKED','K_EMPTY:11-14','K_EMPTY','RE')
    branch('RE','T_DRAIN:15-18','T_DRAIN','RR')
    wire('RR','R_TD:1');wire('R_TD:2','XW:2');diode('D_R_READY','RR','J')
    branch('PC','K_MIN:11-14','K_MIN','PR');diode('D_P_READY','PR','J')
    branch('J','K_FILL:21-22','K_FILL','NOT_FILL',True)
    branch('NOT_FILL','SETUP_RUN:13-14','setup','RUN_READY',True,physical_form='NO',device='Schneider XB5AD25')
    branch('RUN_READY','AUTO_DRAIN:21-22','drain_override','READY_COIL',True,physical_form='NC',device='Schneider XB5AD25');coil('K_READY','READY_COIL')
    # Controller status loop carries a defined 24 V optocoupler load.
    wire('HEAD_SAFE','XW:31');branch('XW:31','K_READY:11-14','K_READY','XW:32')
    wire('XW:32','IF_READY:IN+');wire('IF_READY:IN-','XW:2')
    # Hardware tool request gating; safety-relay/door/breakaway feeds are field
    # inputs, never inferred from a GPIO or from K_READY alone.
    branch('C','XH:1-2','hardware_stop_ok','HARD_SAFE')
    branch('HARD_SAFE','XH:3-4','door_closed','DOOR_SAFE')
    branch('DOOR_SAFE','XH:5-6','breakaway_seated','HEAD_SAFE',physical_form='Normally-off PhotoMOS',
           device='U_HEAD / Panasonic AQY212GS output; head-interface.json')
    wire('HEAD_SAFE','XW:33');branch('XW:33','K_READY:21-24','K_READY','XW:34');wire('XW:34','PERMIT')
    # Request sensing remains powered while permission is absent. A held CNC
    # request therefore cannot rearm after a stop or a cold start. Ready has
    # a 12/75 second power-up delay; request relay settles before arming.
    branch('C','IF_RUN:13-14','run_request','REQUEST_COIL',physical_form='Normally-off PhotoMOS',device='Panasonic AQY212GS output; interface terminal numbers');coil('K_REQUEST','REQUEST_COIL')
    branch('PERMIT','K_REQUEST:11-12','K_REQUEST','RUN_ARM_COIL',True)
    branch('PERMIT','K_RUN_ARM:11-14','K_RUN_ARM','RUN_ARM_COIL');coil('K_RUN_ARM','RUN_ARM_COIL')
    branch('PERMIT','K_RUN_ARM:21-24','K_RUN_ARM','ARMED_PERMIT')
    branch('ARMED_PERMIT','K_REQUEST:21-24','K_REQUEST','REQUEST')
    branch('REQUEST','KM_R:31-34','KM_R','VFD_RUN_COIL');coil('K_VFD_RUN','VFD_RUN_COIL')
    branch('REQUEST','KM_P:31-34','KM_P','TORCH_RUN_COIL');coil('K_TORCH_RUN','TORCH_RUN_COIL')
    # These are dry output boundaries. No voltage source exists on tool side.
    contact('K_VFD_RUN:11-14','XVFD:RUN','XVFD:COM','K_VFD_RUN')
    contact('K_TORCH_RUN:11-14','XPLASMA:START1','XPLASMA:START2','K_TORCH_RUN')
    return wires,contacts,diodes,loads


WIRES,CONTACTS,DIODES,LOADS=definition()
RELAY_TAGS=[k for k in LOADS if not k.startswith('T_')]
DEFAULT={'power':True,'f_control':True,'f_valve':True,'pump_fuse':True,
         'router':False,'plasma':False,'setup':True,'fill_pressed':False,
         'drain_override':False,'empty':True,'minimum':False,'fill_stop_healthy':True,
         'high_high_healthy':True,'reservoir_healthy':True,'stop_ok':True,
         'bed_clear':False,'bed_locked':False,'hardware_stop_ok':True,
         'door_closed':True,'breakaway_seated':True,'run_request':False}


def energized(inputs,states,failed_open=(),failed_closed=()):
    values={**inputs,**states};graph=defaultdict(list)
    for edge in WIRES+DIODES+CONTACTS:
        if edge.tag in failed_open:continue
        enabled=not edge.control or bool(values.get(edge.control,False))!=edge.closed_when_control_false
        if enabled or edge.tag in failed_closed:
            graph[edge.a].append(edge.b)
            if not edge.directed:graph[edge.b].append(edge.a)
    reached={'24V'} if inputs.get('power') else set();queue=deque(reached)
    while queue:
        node=queue.popleft()
        for nxt in graph[node]:
            if nxt not in reached:reached.add(nxt);queue.append(nxt)
    return reached


class Simulator:
    def __init__(self,pickup=.010,dropout=.020,t_close=12.,t_drain=75.,timer_recovery=.100):
        self.inputs=DEFAULT.copy();self.states={k:False for k in LOADS};self.elapsed={k:0. for k in LOADS}
        self.pickup=pickup;self.dropout=dropout;self.timers={'T_CLOSE':t_close,'T_DRAIN':t_drain}
        self.timer_recovery=timer_recovery;self.timer_off={k:0. for k in self.timers};self.time=0.
        self.isolated_request=False;self.request_elapsed=0.
        self.failed_open=set();self.failed_closed=set();self.ssr_failed_short=set()
    def graph_inputs(self):
        return {**self.inputs,'run_request':self.isolated_request}
    def tick(self,dt=.001):
        if self.inputs['run_request']==self.isolated_request:self.request_elapsed=0.
        else:
            self.request_elapsed+=dt
            if self.request_elapsed+1e-9 >= (.005 if self.inputs['run_request'] else .0005):
                self.isolated_request=self.inputs['run_request'];self.request_elapsed=0.
        reached=energized(self.graph_inputs(),self.states,self.failed_open,self.failed_closed)
        for tag,node in LOADS.items():
            command=node in reached
            if tag in self.timers:
                if command:
                    self.timer_off[tag]=0.;self.elapsed[tag]+=dt
                    if self.elapsed[tag]+1e-9>=self.timers[tag]:self.states[tag]=True
                else:
                    self.timer_off[tag]+=dt
                    # Worst-case recovery hold is explicit; a shorter interruption
                    # is NOT falsely treated as a guaranteed timer reset.
                    if self.timer_off[tag]+1e-9>=self.timer_recovery:
                        self.elapsed[tag]=0.;self.states[tag]=False
            elif command==self.states[tag]:self.elapsed[tag]=0.
            else:
                self.elapsed[tag]+=dt
                if self.elapsed[tag]+1e-9>=(self.pickup if command else self.dropout):
                    self.states[tag]=command;self.elapsed[tag]=0.
        self.time+=dt
        return self.outputs()
    def outputs(self):
        reached=energized(self.graph_inputs(),self.states,self.failed_open,self.failed_closed)
        limit='P_LIMIT:A1' in reached or 'P_LIMIT' in self.ssr_failed_short
        cmd='P_CMD:A1' in reached or 'P_CMD' in self.ssr_failed_short
        return {'pump':self.inputs['power'] and self.inputs['pump_fuse'] and limit and cmd,
                'drain':'XW:7' in reached,'ready':self.states['K_READY'],
                'router_run':self.states['K_VFD_RUN'],'torch_run':self.states['K_TORCH_RUN'],
                'armed':self.states['K_ARM'],'fill':self.states['K_FILL'],
                'machine_permission':'IF_READY:IN+' in reached}
    def run(self,seconds,**changes):
        self.inputs.update(changes)
        for _ in range(round(seconds/.005)):self.tick(.005)
        return self.outputs()


def write_netlist():
    rows=[]
    for kind,edges in [('wire',WIRES),('contact',CONTACTS),('diode',DIODES)]:
        for edge in edges:
            row={'kind':kind,**edge.__dict__}
            row['closed_condition']=(edge.control+' = '+str(not edge.closed_when_control_false).lower()) if kind=='contact' else ''
            rows.append(row)
    d={'scope':__doc__,'connections':rows,'loads':LOADS,
       'contact_semantics':'closed_when_control_false is Boolean model inversion only. physical_form is the purchased/de-energized contact form. A selector NC can close when setup=true; do not infer NO/NC from a variable name.',
       'operator_devices':{'MODE':'Schneider XB5AD33; two separate NO blocks, each identified as 13-14 by the primary datasheet; MODE_R/MODE_P distinguish blocks',
                           'SETUP_RUN':'Schneider XB5AD25; 21-22 NC closes at SETUP, 13-14 NO closes at RUN',
                           'AUTO_DRAIN':'Schneider XB5AD25; 21-22 NC closes at AUTO, 13-14 NO closes at DRAIN',
                           'FILL':'Schneider XB5AA35; 13-14 NO closes pressed, 21-22 NC closes released',
                           'BED_CONFIRM':'Schneider XB5AG03; 3 maintained positions, two separate NO 13-14 blocks, key removable in any position; center unconfirmed opens both'},
       'timers':{'T_CLOSE':{'mpn':'80.01.0.240.0000','function':'AI','nominal_s':12,'required_minimum_s':10},
                 'T_DRAIN':{'mpn':'80.01.0.240.0000','function':'AI','nominal_s':75,'required_minimum_s':60}},
       'minimum_load_resistors':{'R_TC':{'ohms':680,'watts':3,'tolerance_percent':5},
                                 'R_TD':{'ohms':680,'watts':3,'tolerance_percent':5}},
       'boundary':'XH stop/door health contacts, the U_HEAD presence output and isolated IF_RUN are specified interfaces, not a modeled safety relay or installed interface PCB. U_HEAD is defined in head-interface.json. Tool-side connector compatibility is not assumed.'}
    (OUT/'terminal-netlist.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    lines=['# Rev I low-voltage terminal connections','',
           'Generated from circuit.py. Wires are point-to-point; contact rows specify the device terminals between them. These circuits use only isolated 24 V control power. Tool-output pairs remain floating. Read the controls README before fabrication.','',
           'Factory contact form and logical closed condition are separate columns. For SETUP_RUN, the physical NC contact closes when setup=true, while the physical NO contact closes when setup=false. XW/XH rows with unspecified device form describe field-loop continuity only. MODE_R/MODE_P and BED_R/BED_P identify separate blocks on one head; each block uses the manufacturer-listed 13/14 terminals, not an invented 23/24 stamping. Verify positions by continuity before fitting labels.','',
           '| Tag | Type | From | To | Physical contact form | Closed condition | Device |','|---|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['tag']} | {r['kind']} | {r['a']} | {r['b']} | {r['physical_form'] or '-'} | {r['closed_condition'] or '-'} | {r['device'] or '-'} |")
    (OUT/'TERMINALS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':write_netlist()
