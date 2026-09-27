"""GM1 controls: the Rev I relay circuit with the review's safety fixes, for the BTT Rodent.

The other session's Rev I terminal graph
(output/design-finish-2026-09-26/controls/circuit.py) is imported read-only;
verify_gm1_circuit.py records its hash. The water logic (fill, drain, timers,
bed confirmation, mode relays) stays Rev I's, with one added check contact in
the fill arm. The stop, the tool-permission chain, the tool outputs and the
controller interface are replaced. Each change is listed in CHANGES.

M12 and M13 (later on 27 September, for the Rev L tool changer) add spindle
reverse and the tool-changer drive.

This is a wiring-graph and relay-timing model, like Rev I's. It is not a
certified safety function, a PL/category claim or a tested panel.
"""
from collections import defaultdict, deque
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REV_I_DIR = HERE.parent / 'design-finish-2026-09-26' / 'controls'
sys.path.insert(0, str(REV_I_DIR))
try:
    import circuit as rev_i
finally:
    sys.path.remove(str(REV_I_DIR))

Edge = rev_i.Edge

CHANGES = [
    ('M1', 'Stop', 'A dual-channel safety relay (SR) with manual reset replaces the two field stop contacts (XW:21-22 and XH:1-2). '
     'SR:13-14 and SR:23-24 drive contactors K1 and K2. One main pole of each, in series, switches each of: the 48 V '
     'supply to the Rodent, VFD mains and plasma-cutter mains. Their NC mirror auxiliaries form the feedback loop in the '
     'reset circuit. SR:33-34 feeds the water and tool permission chains. The Z brake is powered through the K1 and K2 NO '
     'auxiliaries and a 3 s on-delay, so it engages whenever either contactor opens.'),
    ('M2', 'Mode race', 'Per-mode ready relays K_RDY_R (coil on RR) and K_RDY_P (coil on PR) sit in series in the spindle '
     'and torch coil paths. A tool coil can only energize after its own mode has finished its water sequence (12 s '
     'plasma, 75 s router), so changing mode with the start signal held cannot fire the other tool.'),
    ('M3', 'Welded relays', 'Every relay in the start chain is force-guided (Omron G7SA). Each relay can only pick up while '
     'the next relay down the chain is released: K_READY checks K_PERMIT, K_PERMIT checks K_RUN_ARM, and K_RUN_ARM checks '
     'both request relays and both tool relays. A welded contact therefore blocks the next start instead of starting a tool.'),
    ('M4', 'Controller stop', 'Two request relays, K_REQ_A and K_REQ_B, both follow the Rodent run request. K_REQ_A feeds '
     'the tool coils. K_REQ_B is in series in both tool outputs, so a single welded request or tool relay cannot keep a '
     'tool running after the Rodent drops its request.'),
    ('M5', 'Setup', 'A second SETUP channel: an added Schneider ZBE101 NO block on the SETUP/RUN selector sits in series '
     'ahead of K_RUN_ARM. Both the arming and every tool output need RUN, through two independent contacts.'),
    ('M6', 'Tool outputs', 'Each tool output is three contacts in series from three relays: the VFD FWD terminal uses '
     'K_VFD_RUN, K_RUN_ARM and K_REQ_B, and the cutter start uses K_TORCH_RUN, K_RUN_ARM and K_REQ_B. There is no RS485. '
     'The VFD takes run only through FWD and speed only through an isolated 0-10 V signal, so no serial command can start '
     'the spindle.'),
    ('M7', 'Rodent door input', 'A dry contact pair to the Rodent E1-MAX input: K_REQ_A NC (no request) in parallel with '
     'K_RUN_ARM NO (armed). It opens only when the Rodent is requesting a tool that is not armed. grblHAL treats that as '
     'a safety door: feed hold and spindle off.'),
    ('M8', 'Fill check', 'K_READY NC in the fill-arm pickup. FILL cannot arm in SETUP if K_READY is welded, so that '
     'fault shows up as "fill will not start".'),
    ('M9', 'Router drain', 'Rev I left the pan drain open for as long as router mode was selected, so chips, aluminium fines '
     'and mist coolant ran to the plasma reservoir. A latch relay K_DRAINED now picks up when the 75 s drain dwell ends '
     '(T_DRAIN output through diode D_SET). Its NC contact opens the drain request (the valve closes) and its NO contacts '
     'hold router ready in place of the timer. The latch holds only while router mode is selected (fed from KM_R) and the pan '
     'stays empty (K_EMPTY_B, a second relay on the empty-float coil line). Liquid reaching the empty float, or leaving router '
     'mode, drops the latch; the drain then reopens and a new dwell starts. An E-stop does not drop it.'),
    ('M10', 'Fill watchdog', 'On-delay timer T_FILL runs whenever the fill is commanded; its NC contact is in the K_FILL '
     'self-hold. A fill that has not reached the fill-stop float within the set time (commission it to 1.5 x the measured '
     'fill, 25 min until then) stops and needs a new FILL press. Holding FILL keeps the pump running only while it is held.'),
    ('M11', 'Float stop', 'The torch-head float switch is added in series with the three head-presence switches in the U_HEAD '
     'loop (XH:5-6). A float trip while the torch is requested therefore drops the permission (torch off) and opens the '
     'Rodent door input (feed hold). During probing the request is low, so the door input stays closed and the chain re-arms '
     'when the float returns. The same loop drives the Rodent probe input through a second optocoupler.'),
    ('M12', 'Spindle reverse', 'The RapidChange tool changer unloads a tool with the spindle in reverse (M4), so the VFD also '
     'needs its REV terminal. A force-guided direction relay K_DIR (G7SA-2A2B) sits at the end of the three-contact run chain: '
     'its NC 31-32 passes the run command to FWD and its NO 13-14 to REV, so the VFD never sees both, even with a welded '
     'contact. Its coil is on the Rodent V-MOS HE1 output (GPIO2, the grblHAL spindle direction), fed like the mist from the '
     '48-to-24 V DC-DC after K1 and K2. K_DIR only chooses the direction: K_VFD_RUN, K_RUN_ARM and K_REQ_B still start and '
     'stop the spindle. Its spare NO 23-24 reports the direction to the MCP23017 (XM:8).'),
    ('M13', 'Tool changer drive', 'The Rev L dock\'s 24 V gearmotor is fed from the Z-brake supply, which is live only while K1 '
     'and K2 are closed, so every E-stop stops it. The feed then passes fuse F_DOCK and K_VFD_RUN NC 41-42: the dock cannot '
     'move while the spindle run relay is picked up, or if that relay is welded, and a spindle start stops a moving dock. '
     'K_DOCK_RUN switches the motor on and K_DOCK_DIR chooses the direction, so the two directions can never be driven at '
     'once. Each direction runs through its own end microswitch (LS_OUT at the deployed stop, LS_IN at the parked stop), '
     'which opens at the end of travel even if a relay welds. The Rodent drives both coils from MCP23017 outputs through a '
     'ULN2803A and reads the two dock sensors on MCP23017 inputs.'),
]

# Relay families and poles. G7SA terminal marks follow EN 50005 (13-14 NO,
# 31-32 NC and so on); confirm them on the P7SA socket label.
G7SA_2A2B = dict(no=['13-14', '23-24'], nc=['31-32', '41-42'])
G7SA_3A1B = dict(no=['13-14', '23-24', '33-34'], nc=['41-42'])
G7SA_5A1B = dict(no=['13-14', '23-24', '33-34', '43-44', '53-54'], nc=['61-62'])
DEVICES = {
    'SR': dict(part='Dual-channel E-stop safety relay, 24 V, 3 NO safety + 1 NC auxiliary, manual reset, external '
               'contactor feedback loop. Candidate: Pilz PNOZ X2.8P 24VACDC 3n/o 1n/c (777301)', kind='safety relay',
               no=['13-14', '23-24', '33-34'], nc=['41-42']),
    'K1': dict(part='Schneider TeSys LC1D18BD (24 V DC coil), 3 NO main poles + 1 NO/1 NC auxiliary; NC is a mirror contact',
               kind='contactor', no=['1-2', '3-4', '5-6', '13-14'], nc=['21-22']),
    'K2': dict(part='Schneider TeSys LC1D18BD (24 V DC coil), 3 NO main poles + 1 NO/1 NC auxiliary; NC is a mirror contact',
               kind='contactor', no=['1-2', '3-4', '5-6', '13-14'], nc=['21-22']),
    'K_READY': dict(part='Omron G7SA-3A1B 24 VDC + P7SA-10F socket', kind='force-guided', **G7SA_3A1B),
    'K_PERMIT': dict(part='Omron G7SA-3A1B 24 VDC + P7SA-10F socket', kind='force-guided', **G7SA_3A1B),
    'K_RUN_ARM': dict(part='Omron G7SA-5A1B 24 VDC + P7SA-14F socket', kind='force-guided', **G7SA_5A1B),
    'K_REQ_A': dict(part='Omron G7SA-2A2B 24 VDC + P7SA-10F socket', kind='force-guided', **G7SA_2A2B),
    'K_REQ_B': dict(part='Omron G7SA-2A2B 24 VDC + P7SA-10F socket', kind='force-guided', **G7SA_2A2B),
    'K_VFD_RUN': dict(part='Omron G7SA-2A2B 24 VDC + P7SA-10F socket', kind='force-guided', **G7SA_2A2B),
    'K_TORCH_RUN': dict(part='Omron G7SA-2A2B 24 VDC + P7SA-10F socket', kind='force-guided', **G7SA_2A2B),
    'K_RDY_R': dict(part='Finder 40.52.9.024.0000 + 95.05 socket (as Rev I)', kind='relay', no=['11-14', '21-24'], nc=['11-12', '21-22']),
    'K_RDY_P': dict(part='Finder 40.52.9.024.0000 + 95.05 socket (as Rev I)', kind='relay', no=['11-14', '21-24'], nc=['11-12', '21-22']),
    'T_BRAKE': dict(part='Finder 80.01.0.240.0000, function AI (on-delay), set 3 s (as Rev I timers)', kind='timer',
                    no=['15-18'], nc=['15-16']),
    'K_DRAINED': dict(part='Finder 40.52.9.024.0000 + 95.05 socket (as Rev I water relays)', kind='relay',
                      no=['11-14', '21-24'], nc=['11-12', '21-22']),
    'K_EMPTY_B': dict(part='Finder 40.52.9.024.0000 + 95.05 socket, coil in parallel with K_EMPTY', kind='relay',
                      no=['11-14', '21-24'], nc=['11-12', '21-22']),
    'T_FILL': dict(part='Finder 80.01.0.240.0000, function AI (on-delay), 25 min until the fill is timed', kind='timer',
                   no=['15-18'], nc=['15-16']),
    'Z_BRAKE': dict(part='Z motor power-off holding brake, 24 V coil (energized = released)', kind='brake', no=[], nc=[]),
    'K_DIR': dict(part='Omron G7SA-2A2B 24 VDC + P7SA-10F socket', kind='force-guided', **G7SA_2A2B),
    'K_DOCK_RUN': dict(part='Finder 40.52.9.024.0000 + 95.05 socket: pole 1 switches the dock motor +24 V, pole 2 its 0 V',
                       kind='relay', no=['11-14', '21-24'], nc=['11-12', '21-22']),
    'K_DOCK_DIR': dict(part='Finder 40.52.9.024.0000 + 95.05 socket: both poles reverse the dock motor polarity',
                       kind='relay', no=['11-14', '21-24'], nc=['11-12', '21-22']),
}
GUIDED = {k for k, d in DEVICES.items() if d['kind'] in ('force-guided', 'contactor')}
TOOL_CHAIN = ['K_READY', 'K_PERMIT', 'K_RUN_ARM', 'K_REQ_A', 'K_REQ_B', 'K_VFD_RUN', 'K_TORCH_RUN',
              'K_RDY_R', 'K_RDY_P', 'KM_R', 'KM_P', 'K_DIR']

# Rev I edges that the new start chain replaces.
DROP_PREFIXES = ('K_READY:', 'K_REQUEST:', 'K_RUN_ARM:', 'K_VFD_RUN:', 'K_TORCH_RUN:', 'IF_RUN:', 'IF_READY:')
DROP_NODES = {'XW:21', 'XW:22', 'XH:1', 'XH:2', 'XW:31', 'XW:32', 'XW:33', 'XW:34', 'PERMIT', 'REQUEST_COIL',
              'RUN_ARM_COIL', 'ARMED_PERMIT', 'REQUEST', 'VFD_RUN_COIL', 'TORCH_RUN_COIL', 'READY_COIL',
              'XVFD:RUN', 'XVFD:COM', 'XPLASMA:START1', 'XPLASMA:START2'}
DROP_CONTACTS = {'XW:21-22', 'XH:1-2'}
DROP_WIRES = {frozenset(('FILL:22', 'ARM_COIL')),
              frozenset(('T_DRAIN:18', 'RR')),        # M9: timer output now through diodes D_TD and D_SET
              frozenset(('K_FILL:14', 'FILL_COIL'))}  # M10: fill self-hold now through T_FILL NC
DROP_DIODES = {'D_R'}                                 # M9: drain request now through K_DRAINED NC and D_R2


def _dropped(edge):
    if edge.tag in DROP_CONTACTS or edge.tag.startswith(DROP_PREFIXES):
        return True
    ends = {edge.a, edge.b}
    return bool(ends & DROP_NODES) or any(n.startswith(DROP_PREFIXES) for n in ends) or frozenset(ends) in DROP_WIRES


def definition():
    wires = [e for e in rev_i.WIRES if not _dropped(e)]
    contacts = [e for e in rev_i.CONTACTS if not _dropped(e)]
    diodes = [d for d in rev_i.DIODES if d.tag not in DROP_DIODES]
    loads = {k: v for k, v in rev_i.LOADS.items() if k not in ('K_READY', 'K_REQUEST', 'K_RUN_ARM', 'K_VFD_RUN', 'K_TORCH_RUN')}
    dropped = [e for e in rev_i.WIRES + rev_i.CONTACTS if _dropped(e)] + [d for d in rev_i.DIODES if d.tag in DROP_DIODES]
    power = []
    n = [0]

    def wire(a, b, into=None):
        n[0] += 1
        (wires if into is None else into).append(Edge(a, b, f'G{n[0]:03}'))

    def contact(tag, a, b, control, inverted=False, form='', device='', into=None):
        if not form:
            form = 'NC' if inverted else 'NO'
        dev = tag.split(':')[0]
        if not device and dev in DEVICES:
            device = DEVICES[dev]['part']
        (contacts if into is None else into).append(Edge(a, b, tag, control, inverted, physical_form=form, device=device))

    def branch(source, tag, control, dest, inverted=False, form='', device=''):
        dev, poles = tag.split(':')
        a, b = f'{dev}:{poles.split("-")[0]}', f'{dev}:{poles.split("-")[1]}'
        wire(source, a)
        contact(tag, a, b, control, inverted, form, device)
        wire(b, dest)

    def coil(tag, source):
        wire(source, tag + ':A1')
        wire(tag + ':A2', 'XW:2')
        loads[tag] = tag + ':A1'

    # M1: safety relay, contactors, stop output and Z brake.
    wire('XW:1', 'F_SAFETY:1')
    contact('F_SAFETY', 'F_SAFETY:1', 'F_SAFETY:2', 'f_safety', form='Fuse continuity', device='Safety-circuit fuse')
    wire('F_SAFETY:2', 'XS:1')
    wire('XS:1', 'S')
    wire('S', 'SR:A1')
    wire('SR:A2', 'XW:2')
    # Input and reset circuits are the relay's own low-voltage loops; they are
    # evaluated as dry paths by the simulator, not powered from S.
    contact('ESTOP:11-12', 'SR:S11', 'SR:S12', 'estop_ch1', form='NC',
            device='E-STOP pushbutton, latching, turn to release; channel 1 contact block')
    contact('ESTOP:21-22', 'SR:S21', 'SR:S22', 'estop_ch2', form='NC',
            device='E-STOP pushbutton, same actuator; channel 2 contact block')
    contact('RESET:13-14', 'SR:S33', 'RST_1', 'reset_pressed', form='NO', device='RESET pushbutton, blue, momentary')
    contact('K1:21-22', 'RST_1', 'RST_2', 'K1', True, form='NC mirror contact (IEC 60947-4-1 Annex F)')
    contact('K2:21-22', 'RST_2', 'SR:S34', 'K2', True, form='NC mirror contact (IEC 60947-4-1 Annex F)')
    branch('S', 'SR:13-14', 'SR_OUT', 'K1_COIL', form='Safety NO')
    coil('K1', 'K1_COIL')
    branch('S', 'SR:23-24', 'SR_OUT', 'K2_COIL', form='Safety NO')
    coil('K2', 'K2_COIL')
    branch('C', 'SR:33-34', 'SR_OUT', 'STOP_OK', form='Safety NO')
    # Former field stop contacts become panel links fed from the safety output.
    for first, last, dest in (('XW:21', 'XW:22', 'STOP_HEALTHY'), ('XH:1', 'XH:2', 'HARD_SAFE')):
        wire('STOP_OK', first)
        wire(first, last)
        wire(last, dest)
    branch('S', 'K1:13-14', 'K1', 'BRK_1')
    branch('BRK_1', 'K2:13-14', 'K2', 'BRK_PWR')
    coil('T_BRAKE', 'BRK_PWR')
    branch('BRK_PWR', 'T_BRAKE:15-18', 'T_BRAKE', 'Z_BRAKE_COIL')
    coil('Z_BRAKE', 'Z_BRAKE_COIL')
    # Hazardous-energy paths: one main pole of each contactor in series.
    for label, src, dst, pole in (('48 V to Rodent VCC', 'PSU48:+', 'RODENT:VCC', '1-2'),
                                  ('VFD mains L', 'MAINS:L_VFD', 'VFD:L', '3-4'),
                                  ('Plasma mains L', 'MAINS:L_PLASMA', 'PLASMA:L', '5-6')):
        mid = f'{dst}_K1'
        contact(f'K1:{pole}', src, mid, 'K1', form='NO main pole', device=f'{DEVICES["K1"]["part"]}; {label}', into=power)
        contact(f'K2:{pole}', mid, dst, 'K2', form='NO main pole', device=f'{DEVICES["K2"]["part"]}; {label}', into=power)

    # M2/M3/M5: permission chain with monitored pickups.
    wire('AUTO_DRAIN:22', 'RDY_SRC')
    branch('RDY_SRC', 'K_PERMIT:41-42', 'K_PERMIT', 'READY_COIL', True)
    branch('RDY_SRC', 'K_READY:33-34', 'K_READY', 'READY_COIL')
    coil('K_READY', 'READY_COIL')
    branch('HEAD_SAFE', 'K_READY:23-24', 'K_READY', 'PERMIT_SRC')
    branch('PERMIT_SRC', 'K_RUN_ARM:61-62', 'K_RUN_ARM', 'PERMIT_COIL', True)
    branch('PERMIT_SRC', 'K_PERMIT:13-14', 'K_PERMIT', 'PERMIT_COIL')
    coil('K_PERMIT', 'PERMIT_COIL')
    branch('PERMIT_SRC', 'K_PERMIT:23-24', 'K_PERMIT', 'PERMIT')
    branch('PERMIT', 'SETUP_RUN_B:13-14', 'setup', 'ARM_SRC', True, form='NO',
           device='Schneider ZBE101 NO block added to the SETUP/RUN selector (closes in RUN)')
    branch('ARM_SRC', 'K_REQ_A:31-32', 'K_REQ_A', 'ARM_1', True)
    branch('ARM_1', 'K_REQ_B:31-32', 'K_REQ_B', 'ARM_2', True)
    branch('ARM_2', 'K_VFD_RUN:31-32', 'K_VFD_RUN', 'ARM_3', True)
    branch('ARM_3', 'K_TORCH_RUN:31-32', 'K_TORCH_RUN', 'RUN_ARM_COIL', True)
    branch('ARM_SRC', 'K_RUN_ARM:13-14', 'K_RUN_ARM', 'RUN_ARM_COIL')
    coil('K_RUN_ARM', 'RUN_ARM_COIL')
    branch('ARM_SRC', 'K_RUN_ARM:23-24', 'K_RUN_ARM', 'ARMED')
    # M4: two request relays on the one isolated run request.
    branch('C', 'IF_RUN:13-14', 'run_request', 'REQUEST_COIL', form='Normally-off PhotoMOS',
           device='U_RUN Panasonic AQY212GS output (Rev I run interface), driven from Rodent GPIO25 / Sp-Enable')
    coil('K_REQ_A', 'REQUEST_COIL')
    coil('K_REQ_B', 'REQUEST_COIL')
    branch('ARMED', 'K_REQ_A:13-14', 'K_REQ_A', 'REQUEST')
    # M2: per-mode ready in each tool coil path.
    coil('K_RDY_R', 'RR')
    coil('K_RDY_P', 'PR')
    wire('REQUEST', 'KM_R:31')
    wire('KM_R:34', 'K_RDY_R:11')
    contact('K_RDY_R:11-14', 'K_RDY_R:11', 'K_RDY_R:14', 'K_RDY_R')
    wire('K_RDY_R:14', 'VFD_RUN_COIL')
    coil('K_VFD_RUN', 'VFD_RUN_COIL')
    wire('REQUEST', 'KM_P:31')
    wire('KM_P:34', 'K_RDY_P:11')
    contact('K_RDY_P:11-14', 'K_RDY_P:11', 'K_RDY_P:14', 'K_RDY_P')
    wire('K_RDY_P:14', 'TORCH_RUN_COIL')
    coil('K_TORCH_RUN', 'TORCH_RUN_COIL')
    # M6: dry tool outputs, three relays in series each.
    contact('K_VFD_RUN:13-14', 'XVFD:DIR', 'XVFD:F1', 'K_VFD_RUN')
    # M12: direction changeover at the end of the run chain; one relay, so FWD and REV never both close.
    contact('K_DIR:31-32', 'XVFD:DIR', 'XVFD:FWD', 'K_DIR', True)
    contact('K_DIR:13-14', 'XVFD:DIR', 'XVFD:REV', 'K_DIR')
    branch('BRK_PWR', 'VMOS_HE1:D-S', 'spindle_reverse', 'DIR_COIL', form='MOSFET output (low side in the real wiring)',
           device='BTT Rodent V-MOS HE1, GPIO2 = grblHAL spindle direction, fed from the 48-to-24 V DC-DC after K1/K2')
    coil('K_DIR', 'DIR_COIL')
    contact('K_RUN_ARM:33-34', 'XVFD:F1', 'XVFD:F2', 'K_RUN_ARM')
    contact('K_REQ_B:13-14', 'XVFD:F2', 'XVFD:COM', 'K_REQ_B')
    contact('K_TORCH_RUN:13-14', 'XPLASMA:START1', 'XPLASMA:S1', 'K_TORCH_RUN')
    contact('K_RUN_ARM:43-44', 'XPLASMA:S1', 'XPLASMA:S2', 'K_RUN_ARM')
    contact('K_REQ_B:23-24', 'XPLASMA:S2', 'XPLASMA:START2', 'K_REQ_B')
    # M7: dry door input to the Rodent; M3 status outputs to the MCP23017.
    contact('K_REQ_A:41-42', 'XR:E1_SIG', 'XR:E1_GND', 'K_REQ_A', True)
    contact('K_RUN_ARM:53-54', 'XR:E1_SIG', 'XR:E1_GND', 'K_RUN_ARM')
    contact('K_READY:13-14', 'XM:1', 'XM:COM', 'K_READY')
    contact('K_PERMIT:33-34', 'XM:2', 'XM:COM', 'K_PERMIT')
    contact('K_RDY_R:21-24', 'XM:3', 'XM:COM', 'K_RDY_R')
    contact('K_RDY_P:21-24', 'XM:4', 'XM:COM', 'K_RDY_P')
    contact('K_DIR:23-24', 'XM:8', 'XM:COM', 'K_DIR')
    # M8: K_READY NC in the fill-arm pickup.
    branch('FILL:22', 'K_READY:41-42', 'K_READY', 'ARM_COIL', True)

    def diode(tag, a, b):
        diodes.append(Edge(a, b, tag, directed=True, physical_form='1N4007 in the terminal row'))

    # M9: router drain latch. K_DRAINED's first changeover shares common 11:
    # NC 11-12 passes the drain request, NO 11-14 is the self-hold.
    wire('DR_REQ', 'K_DRAINED:11')
    contact('K_DRAINED:11-12', 'K_DRAINED:11', 'K_DRAINED:12', 'K_DRAINED', True)
    diode('D_R2', 'K_DRAINED:12', 'DRAIN_COIL')
    contact('K_DRAINED:11-14', 'K_DRAINED:11', 'K_DRAINED:14', 'K_DRAINED')
    branch('K_DRAINED:14', 'K_EMPTY_B:11-14', 'K_EMPTY_B', 'DRN_COIL')
    coil('K_EMPTY_B', 'EMPTY_COIL')
    coil('K_DRAINED', 'DRN_COIL')
    diode('D_TD', 'T_DRAIN:18', 'RR')
    diode('D_SET', 'T_DRAIN:18', 'DRN_COIL')
    branch('RE', 'K_DRAINED:21-24', 'K_DRAINED', 'RR')
    # M10: fill watchdog in the K_FILL self-hold.
    coil('T_FILL', 'FILL_COIL')
    branch('K_FILL:14', 'T_FILL:15-16', 'T_FILL', 'FILL_COIL', True)
    # M13: tool-changer drive. Motor feed after K1/K2 and the spindle-run interlock; run and
    # direction relays; one end switch per direction. The motor is modeled as one load per direction.
    contact('F_DOCK', 'BRK_PWR', 'DOCK_1', 'f_dock', form='Fuse continuity', device='Dock motor fuse, 2 A time-delay')
    branch('DOCK_1', 'K_VFD_RUN:41-42', 'K_VFD_RUN', 'DOCK_24V', True)
    branch('C', 'IF_DOCK_RUN:1-2', 'dock_run_cmd', 'DOCK_RUN_COIL', form='Open-collector sink',
           device='Interface board ULN2803A channel, driven by MCP23017 GPB0')
    coil('K_DOCK_RUN', 'DOCK_RUN_COIL')
    branch('C', 'IF_DOCK_DIR:1-2', 'dock_in_dir', 'DOCK_DIR_COIL', form='Open-collector sink',
           device='Interface board ULN2803A channel, driven by MCP23017 GPB1 (on = toward parked)')
    coil('K_DOCK_DIR', 'DOCK_DIR_COIL')
    branch('DOCK_24V', 'K_DOCK_RUN:11-14', 'K_DOCK_RUN', 'K_DOCK_DIR:11')
    contact('K_DOCK_DIR:11-12', 'K_DOCK_DIR:11', 'K_DOCK_DIR:12', 'K_DOCK_DIR', True)
    contact('K_DOCK_DIR:11-14', 'K_DOCK_DIR:11', 'K_DOCK_DIR:14', 'K_DOCK_DIR')
    branch('K_DOCK_DIR:12', 'LS_OUT:11-12', 'dock_at_deployed', 'M_DOCK_OUT_IN', True, form='NC',
           device='End microswitch at the deployed stop; opens when the drive tab reaches it (with a diode for backing off)')
    coil('M_DOCK_OUT', 'M_DOCK_OUT_IN')
    branch('K_DOCK_DIR:14', 'LS_IN:11-12', 'dock_at_parked', 'M_DOCK_IN_IN', True, form='NC',
           device='End microswitch at the parked stop; opens when the drive tab reaches it (with a diode for backing off)')
    coil('M_DOCK_IN', 'M_DOCK_IN_IN')
    return wires, contacts, diodes, loads, power, dropped


WIRES, CONTACTS, DIODES, LOADS, POWER, DROPPED = definition()
CONTACT_IDS = {id(e) for e in CONTACTS + POWER}
ALL_EDGES = WIRES + DIODES + CONTACTS
TIMERS = ('T_CLOSE', 'T_DRAIN', 'T_BRAKE', 'T_FILL')
DEFAULT = {k: v for k, v in rev_i.DEFAULT.items() if k not in ('stop_ok', 'hardware_stop_ok')}
DEFAULT.update(f_safety=True, estop_ch1=True, estop_ch2=True, reset_pressed=False, supply_48v=True, mains=True)
DEFAULT.update(spindle_reverse=False, f_dock=True, dock_run_cmd=False, dock_in_dir=False,
               dock_at_deployed=False, dock_at_parked=True)


class Simulator:
    """Finite-delay model of the GM1 panel, extending Rev I's approach.

    Relays switch after a pickup or dropout delay. Contactors K1/K2 have their
    own delays. Timers follow Rev I (a timer restarts only after power has been
    off for timer_recovery). The safety relay is a state machine: both input
    channels closed, no single-channel discrepancy, and a reset whose circuit
    includes the K1/K2 feedback loop. The Rodent is powered through K1/K2, so it
    reboots after every stop, and its run request is low until reissued unless
    holds_request forces the request line high throughout (worst case).
    """

    def __init__(self, pickup=.010, dropout=.020, contactor_pickup=.060, contactor_dropout=.020,
                 sr_on=.050, sr_off=.020, t_close=12., t_drain=75., t_brake=3., t_fill=1500., timer_recovery=.100,
                 controller_boot=2., reset_mode='monitored', holds_request=False):
        self.inputs = DEFAULT.copy()
        self.states = {k: False for k in LOADS}
        self.elapsed = {k: 0. for k in LOADS}
        self.pickup, self.dropout = pickup, dropout
        self.contactor = (contactor_pickup, contactor_dropout)
        self.timers = {'T_CLOSE': t_close, 'T_DRAIN': t_drain, 'T_BRAKE': t_brake, 'T_FILL': t_fill}
        self.timer_recovery = timer_recovery
        self.timer_off = {k: 0. for k in self.timers}
        self.sr_on, self.sr_off = sr_on, sr_off
        self.sr_out = False
        self.sr_pending_on = None
        self.sr_off_elapsed = 0.
        self.sr_lock = False
        self.prev_channels = (True, True)
        self.reset_prev = False
        self.reset_held = 0.
        self.reset_mode = reset_mode
        self.controller_boot = controller_boot
        self.controller_up = 0.
        self.holds_request = holds_request
        self.isolated_request = False
        self.request_elapsed = 0.
        self.time = 0.
        self.failed_open = set()
        self.failed_closed = set()
        self.welds = {}
        self.ssr_failed_short = set()

    # -- contact state ----------------------------------------------------
    def weld(self, tag, stuck):
        """Weld one NO contact closed. stuck=True: that relay's armature stays
        in the energized position, so its other NO contacts stay closed too."""
        relay = tag.split(':')[0]
        self.welds[relay] = (tag, stuck)

    def values(self):
        return {**self.inputs, 'run_request': self.isolated_request, **self.states, 'SR_OUT': self.sr_out}

    def closed(self, edge, values):
        if id(edge) not in CONTACT_IDS:
            return True
        if edge.tag in self.failed_open:
            return False
        if edge.tag in self.failed_closed:
            return True
        relay = edge.control
        if relay in self.welds:
            pole, stuck = self.welds[relay]
            if edge.tag == pole:
                return True
            if edge.closed_when_control_false:
                # Force-guided and mirror contacts: a welded NO holds every NC open.
                # Ordinary relays: worst case, the NC may reclose with the coil.
                return False if (relay in GUIDED or stuck) else not values.get(relay, False)
            return True if stuck else bool(values.get(relay, False))
        return bool(values.get(relay, False)) != edge.closed_when_control_false

    def graph(self, values, edges=None):
        g = defaultdict(list)
        plain = not (self.failed_open or self.failed_closed or self.welds)
        for e in ALL_EDGES if edges is None else edges:
            if e.control and id(e) in CONTACT_IDS:
                if plain:
                    if bool(values.get(e.control, False)) == e.closed_when_control_false:
                        continue
                elif not self.closed(e, values):
                    continue
            g[e.a].append(e.b)
            if not e.directed:
                g[e.b].append(e.a)
        return g

    @staticmethod
    def reach(g, start):
        seen = {start}
        todo = deque([start])
        while todo:
            for nxt in g[todo.popleft()]:
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append(nxt)
        return seen

    def live(self, g):
        """Nodes energized from the 24 V supply (diodes directed)."""
        return self.reach(g, '24V') if self.inputs['power'] else set()

    # -- devices ----------------------------------------------------------
    def power_paths(self, values):
        g = self.graph(values, POWER)
        return {'motor_power': self.inputs['supply_48v'] and 'RODENT:VCC' in self.reach(g, 'PSU48:+'),
                'vfd_mains': self.inputs['mains'] and 'VFD:L' in self.reach(g, 'MAINS:L_VFD'),
                'plasma_mains': self.inputs['mains'] and 'PLASMA:L' in self.reach(g, 'MAINS:L_PLASMA')}

    def _safety_relay(self, dt, g, reached):
        powered = 'SR:A1' in reached
        ch = ('SR:S12' in self.reach(g, 'SR:S11'), 'SR:S22' in self.reach(g, 'SR:S21'))
        if not any(ch):
            self.sr_lock = False
        elif ch[0] != ch[1] and all(self.prev_channels):
            self.sr_lock = True
        self.prev_channels = ch
        healthy = powered and all(ch)
        if not healthy:
            self.sr_pending_on = None
            if self.sr_out:
                self.sr_off_elapsed += dt
                if not powered or self.sr_off_elapsed + 1e-9 >= self.sr_off:
                    self.sr_out = False
                    self.sr_off_elapsed = 0.
        else:
            self.sr_off_elapsed = 0.
        reset = 'SR:S34' in self.reach(g, 'SR:S33')
        if reset:
            self.reset_held += dt
            trigger = self.reset_mode == 'level' and self.reset_held + 1e-9 >= .03
        else:
            trigger = self.reset_mode == 'monitored' and self.reset_prev and self.reset_held + 1e-9 >= .03
            self.reset_held = 0.
        self.reset_prev = reset
        if trigger and healthy and not self.sr_lock and not self.sr_out and self.sr_pending_on is None:
            self.sr_pending_on = 0.
        if self.sr_pending_on is not None:
            self.sr_pending_on += dt
            if self.sr_pending_on + 1e-9 >= self.sr_on:
                self.sr_out = True
                self.sr_pending_on = None

    def tick(self, dt=.005):
        paths = self.power_paths(self.values())
        if paths['motor_power']:
            self.controller_up += dt
        else:
            self.controller_up = 0.
            if not self.holds_request:
                self.inputs['run_request'] = False
        controller_ready = self.controller_up >= self.controller_boot
        wanted = self.inputs['run_request'] and (controller_ready or self.holds_request)
        if wanted == self.isolated_request:
            self.request_elapsed = 0.
        else:
            self.request_elapsed += dt
            if self.request_elapsed + 1e-9 >= (.005 if wanted else .0005):
                self.isolated_request = wanted
                self.request_elapsed = 0.
        g = self.graph(self.values())
        reached = self.live(g)
        self._safety_relay(dt, g, reached)
        for tag, node in LOADS.items():
            command = node in reached
            if tag in self.timers:
                if command:
                    self.timer_off[tag] = 0.
                    self.elapsed[tag] += dt
                    if self.elapsed[tag] + 1e-9 >= self.timers[tag]:
                        self.states[tag] = True
                else:
                    self.timer_off[tag] += dt
                    if self.timer_off[tag] + 1e-9 >= self.timer_recovery:
                        self.elapsed[tag] = 0.
                        self.states[tag] = False
                continue
            if command == self.states[tag]:
                self.elapsed[tag] = 0.
                continue
            self.elapsed[tag] += dt
            on, off = self.contactor if tag in ('K1', 'K2') else (self.pickup, self.dropout)
            if self.elapsed[tag] + 1e-9 >= (on if command else off):
                self.states[tag] = command
                self.elapsed[tag] = 0.
        self.time += dt
        return self.outputs()

    def outputs(self):
        values = self.values()
        g = self.graph(values)
        reached = self.live(g)
        paths = self.power_paths(values)
        fwd = 'XVFD:COM' in self.reach(g, 'XVFD:FWD')
        rev = 'XVFD:COM' in self.reach(g, 'XVFD:REV')
        start = 'XPLASMA:START2' in self.reach(g, 'XPLASMA:START1')
        limit = 'P_LIMIT:A1' in reached or 'P_LIMIT' in self.ssr_failed_short
        cmd = 'P_CMD:A1' in reached or 'P_CMD' in self.ssr_failed_short
        return {'pump': self.inputs['power'] and self.inputs['pump_fuse'] and limit and cmd,
                'drain': 'XW:7' in reached, 'fill': self.states['K_FILL'], 'fill_armed': self.states['K_ARM'],
                'ready': self.states['K_READY'], 'permit': self.states['K_PERMIT'], 'armed': self.states['K_RUN_ARM'],
                'fwd_closed': fwd, 'rev_closed': rev, 'start_closed': start, **paths,
                'router_run': (fwd or rev) and paths['vfd_mains'], 'torch_run': start and paths['plasma_mains'],
                'dock_out': 'M_DOCK_OUT:A1' in reached, 'dock_in': 'M_DOCK_IN:A1' in reached,
                'direction_status_rev': 'XM:COM' in self.reach(g, 'XM:8'),
                'z_brake_released': self.states['Z_BRAKE'], 'sr_out': self.sr_out,
                'router_drained': self.states['K_DRAINED'], 'fill_timed_out': self.states['T_FILL'],
                'door_ok': 'XR:E1_GND' in self.reach(g, 'XR:E1_SIG'),
                'controller_ready': paths['motor_power'] and self.controller_up >= self.controller_boot,
                'status': {name: 'XM:COM' in self.reach(g, f'XM:{i}')
                           for i, name in enumerate(('ready', 'permit', 'router_water_ready', 'plasma_water_ready'), 1)}}

    def run(self, seconds, dt=.005, **changes):
        self.inputs.update(changes)
        for _ in range(round(seconds / dt)):
            self.tick(dt)
        return self.outputs()

    def reset(self):
        """Operator presses and releases RESET."""
        self.run(.1, reset_pressed=True)
        return self.run(.2, reset_pressed=False)


def pole_usage():
    used = defaultdict(set)
    for e in CONTACTS + POWER:
        dev = e.tag.split(':')[0]
        if dev in DEVICES and ':' in e.tag:
            used[dev].add(e.tag.split(':')[1])
    return {k: sorted(v) for k, v in used.items()}


def write_netlist(out_dir=HERE):
    rows = []
    for kind, edges in (('wire', WIRES), ('contact', CONTACTS), ('diode', DIODES), ('power contact', POWER)):
        for e in edges:
            row = {'kind': kind, **e.__dict__}
            row['closed_condition'] = (e.control + ' = ' + str(not e.closed_when_control_false).lower()) if kind.endswith('contact') else ''
            rows.append(row)
    doc = {'scope': __doc__, 'changes': [dict(id=i, topic=t, change=c) for i, t, c in CHANGES],
           'base': 'output/design-finish-2026-09-26/controls/circuit.py (Rev I), imported read-only',
           'removed_rev_i_edges': [{'kind': 'contact' if e.control else ('diode' if e.directed else 'wire'), 'tag': e.tag, 'a': e.a, 'b': e.b}
                                   for e in DROPPED],
           'devices': DEVICES, 'pole_usage': pole_usage(), 'connections': rows, 'loads': LOADS,
           'contact_semantics': 'closed_when_control_false is the model inversion only; physical_form is the purchased contact form. '
                                'A contact whose control is an operator input (setup, router, estop_ch1 ...) is a switch block, not a relay.'}
    (out_dir / 'gm1-terminal-netlist.json').write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8')
    lines = ['# GM1 low-voltage terminal connections', '',
             'Generated by `gm1_circuit.py` from the Rev I netlist plus the changes listed in the controls README. '
             'Wires are point-to-point. Contact rows name the device terminals between two nodes. "Power contact" rows are '
             'the contactor main poles in the 48 V, VFD-mains and plasma-mains paths. Dry pairs (XVFD, XPLASMA, XR, XM) carry '
             'no panel voltage.', '',
             '| Tag | Type | From | To | Contact form | Closed when | Device |', '|---|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['tag']} | {r['kind']} | {r['a']} | {r['b']} | {r['physical_form'] or '-'} | "
                     f"{r['closed_condition'] or '-'} | {r['device'] or '-'} |")
    (out_dir / 'GM1-TERMINALS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    write_netlist()
