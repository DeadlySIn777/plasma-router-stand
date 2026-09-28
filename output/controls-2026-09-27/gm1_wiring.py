"""GM1 wiring by terminal: every screw terminal, its wire number, and where the other end of each wire lands.

Built from gm1-terminal-netlist.json (the circuit that verify_gm1_circuit.py simulates) plus the physical
decisions written in this file: which nets get a bridged distribution rail, what field device sits behind each
XW/XH pair, how the dock motor reverses, the Rodent's connectors, the interface board's terminals, the VFD and
cutter side, the power paths, and the BT30 variant's add-on. It writes:

  GM1-WIRING-BY-TERMINAL.md   the builder's list, device by device
  gm1-wire-list.csv           one row per wire: number, both ends, net, colour, size
  gm1-wiring.json             the same, with the netlist's hash and the consistency checks

The simulated circuit is not changed here. Anything this file adds beyond the netlist (rails, the reversing
contacts, connector pins, the BT30 add-on) is a wiring decision, marked as such in the output, not a simulated
behaviour. Terminal marks come from the makers' datasheets named in the controls README: check them on the parts.
"""
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
NETLIST = HERE / 'gm1-terminal-netlist.json'

# --------------------------------------------------------------------------------------------------------------
# Terminal marks: where the netlist's node names differ from the physical terminal, rename them.
RENAME = {
    'XR:E1_SIG': 'RODENT:E1-MAX.1', 'XR:E1_GND': 'RODENT:E1-MAX.2',
    'IF_RUN:13': 'IFB:RUN.13', 'IF_RUN:14': 'IFB:RUN.14',
    'IF_DOCK_RUN:1': 'IFB:DOCK_RUN.1', 'IF_DOCK_RUN:2': 'IFB:DOCK_RUN.2',
    'IF_DOCK_DIR:1': 'IFB:DOCK_DIR.1', 'IF_DOCK_DIR:2': 'IFB:DOCK_DIR.2',
    'PSU48:+': 'PSU48:V+', 'VFD:L': 'VFD:L1', 'PLASMA:L': 'PLASMA:L1',
    'MAINS:L_VFD': 'CB_VFD:2', 'MAINS:L_PLASMA': 'CB_PLASMA:2',
}
for i in (1, 2, 3, 4, 8):
    RENAME[f'XM:{i}'] = f'IFB:XM.{i}'
RENAME['XM:COM'] = 'IFB:XM.COM'
# Netlist nodes that are junctions inside a contact chain, not screw terminals; and Rev I strip positions that the
# GM1 rails replace (XW:1-4 were the supply and rail feeds, XW:21-22 and XH:1-2 the old stop loops, now plain links).
INTERNAL = {'XVFD:DIR', 'XVFD:F1', 'XVFD:F2', 'XPLASMA:S1', 'XPLASMA:S2', 'RODENT:VCC_K1', 'VFD:L_K1', 'PLASMA:L_K1',
            'XW:1', 'XW:2', 'XW:3', 'XW:4', 'XW:21', 'XW:22', 'XH:1', 'XH:2'}
# Netlist parts that this file wires by hand instead (the modeled two-load dock motor, the V-MOS coil supply).
EXCLUDE_NODES = {'LS_ZTOP:13', 'LS_ZTOP:14', 'IFB:DOCK_RUN.1', 'IFB:DOCK_RUN.2', 'IFB:DOCK_DIR.1', 'IFB:DOCK_DIR.2', 'DOCK_RUN_COIL', 'DOCK_DIR_COIL',
                 'Z_BRAKE:A1', 'Z_BRAKE:A2', 'M_DOCK_OUT:A1', 'M_DOCK_OUT:A2', 'M_DOCK_IN:A1', 'M_DOCK_IN:A2', 'M_DOCK_OUT_IN', 'M_DOCK_IN_IN',
                 'K_DOCK_DIR:11', 'K_DOCK_DIR:12', 'K_DOCK_DIR:14', 'LS_OUT:11', 'LS_OUT:12', 'LS_IN:11', 'LS_IN:12',
                 'VMOS_HE1:D', 'VMOS_HE1:S', 'DIR_COIL'}
EXCLUDE_TAGS = {'LS_ZTOP:13-14', 'K_DOCK_DIR:11-12', 'K_DOCK_DIR:11-14', 'LS_OUT:11-12', 'LS_IN:11-12', 'VMOS_HE1:D-S'}
EXCLUDE_WIRES = {frozenset(('K_DIR:A2', 'XW:2')), frozenset(('K_DOCK_RUN:A2', 'XW:2')), frozenset(('K_DOCK_DIR:A2', 'XW:2'))}

# --------------------------------------------------------------------------------------------------------------
# Net names: the netlist's junction labels, and what they carry.
NET_INFO = {
    '0V': ('0 V', 'control 0 V (PSU24 V-)', '0v'),
    '24V': ('+24 V', '+24 V from PSU24, unfused', 'dc24'),
    'C': ('C', '+24 V control, after F_CONTROL', 'dc24'),
    'V': ('V', '+24 V valve supply, after F_VALVE', 'dc24'),
    'S': ('S', '+24 V safety-circuit supply, after F_SAFETY', 'dc24'),
    'BRK_PWR': ('BRK', '+24 V after K1 and K2 (Z brake, dock feed)', 'dc24'),
    'STOP_OK': ('STOP_OK', 'C through the safety relay output SR 33-34', 'dc24'),
    'STOP_HEALTHY': ('STOP_HEALTHY', 'STOP_OK after the XW:21-22 link', 'dc24'),
    'H': ('H', 'STOP_HEALTHY through the high-high float (XW:17-18)', 'dc24'),
    'HARD_SAFE': ('HARD_SAFE', 'STOP_OK after the XH:1-2 link', 'dc24'),
    'DOOR_SAFE': ('DOOR_SAFE', 'HARD_SAFE through the door switch (XH:3-4)', 'dc24'),
    'HEAD_SAFE': ('HEAD_SAFE', 'DOOR_SAFE through the head loop (XH:5-6)', 'dc24'),
    'RDY_SRC': ('RDY_SRC', 'ready source, after AUTO_DRAIN 21-22', 'dc24'),
    'READY_COIL': ('READY_COIL', 'K_READY coil +', 'dc24'),
    'PERMIT_SRC': ('PERMIT_SRC', 'HEAD_SAFE through K_READY 23-24', 'dc24'),
    'PERMIT_COIL': ('PERMIT_COIL', 'K_PERMIT coil +', 'dc24'),
    'PERMIT': ('PERMIT', 'PERMIT_SRC through K_PERMIT 23-24', 'dc24'),
    'ARM_SRC': ('ARM_SRC', 'PERMIT through the RUN block SETUP_RUN_B 13-14', 'dc24'),
    'ARM_1': ('ARM_1', 'arm chain after K_REQ_A 31-32', 'dc24'),
    'ARM_2': ('ARM_2', 'arm chain after K_REQ_B 31-32', 'dc24'),
    'ARM_3': ('ARM_3', 'arm chain after K_VFD_RUN 31-32', 'dc24'),
    'RUN_ARM_COIL': ('RUN_ARM_COIL', 'K_RUN_ARM coil +', 'dc24'),
    'ARMED': ('ARMED', 'ARM_SRC through K_RUN_ARM 23-24', 'dc24'),
    'REQUEST_COIL': ('REQUEST_COIL', 'K_REQ_A and K_REQ_B coils +, from the run interface', 'dc24'),
    'REQUEST': ('REQUEST', 'ARMED through K_REQ_A 13-14 (tool request)', 'dc24'),
    'RR': ('RR', 'router ready', 'dc24'), 'PR': ('PR', 'plasma ready', 'dc24'),
    'J': ('J', 'ready OR: RR or PR through the diodes', 'dc24'),
    'RE': ('RE', 'router mode with pan empty', 'dc24'), 'RD': ('RD', 'router drain path', 'dc24'),
    'VFD_RUN_COIL': ('VFD_RUN_COIL', 'K_VFD_RUN coil +', 'dc24'), 'TORCH_RUN_COIL': ('TORCH_RUN_COIL', 'K_TORCH_RUN coil +', 'dc24'),
    'K1_COIL': ('K1_COIL', 'K1 coil +, from SR 13-14', 'dc24'), 'K2_COIL': ('K2_COIL', 'K2 coil +, from SR 23-24', 'dc24'),
    'BRK_1': ('BRK_1', 'S through K1 13-14', 'dc24'), 'Z_BRAKE_COIL': ('Z_BRAKE_COIL', 'brake coil +, after T_BRAKE', 'dc24'),
    'RST_1': ('RST_1', 'reset loop after the RESET button', 'dc24'), 'RST_2': ('RST_2', 'reset loop after K1 21-22', 'dc24'),
    'MR': ('MR', 'router selected', 'dc24'), 'MP': ('MP', 'plasma selected', 'dc24'),
    'KMR_COIL': ('KMR_COIL', 'KM_R coil +', 'dc24'), 'KMP_COIL': ('KMP_COIL', 'KM_P coil +', 'dc24'),
    'EMPTY_COIL': ('EMPTY_COIL', 'K_EMPTY and K_EMPTY_B coils +', 'dc24'), 'MIN_COIL': ('MIN_COIL', 'K_MIN coil +', 'dc24'),
    'DR_REQ': ('DR_REQ', 'drain request from router mode', 'dc24'), 'DO_REQ': ('DO_REQ', 'drain request from AUTO_DRAIN', 'dc24'),
    'DRAIN_COIL': ('DRAIN_COIL', 'K_DRAIN coil +', 'dc24'), 'DRN_COIL': ('DRN_COIL', 'K_DRAINED coil +', 'dc24'),
    'DV': ('DV', 'V through K_DRAIN 11-14 (drain valve +)', 'dc24'),
    'PCLOSE': ('PCLOSE', 'plasma close path', 'dc24'), 'TC_POWER': ('TC_POWER', 'T_CLOSE supply', 'dc24'),
    'P_HEALTHY': ('P_HEALTHY', 'H through KM_P 21-24', 'dc24'), 'P_CLEAR': ('P_CLEAR', 'plasma bed confirmed', 'dc24'),
    'PC': ('PC', 'plasma close done (T_CLOSE 15-18)', 'dc24'), 'SETUP_PC': ('SETUP_PC', 'PC in SETUP', 'dc24'),
    'L': ('L', 'reservoir healthy (pump limit)', 'dc24'), 'A': ('A', 'fill-stop healthy (fill arm source)', 'dc24'),
    'ARM_COIL': ('ARM_COIL', 'K_ARM coil +', 'dc24'), 'AF': ('AF', 'A through K_ARM 21-24', 'dc24'),
    'FILL_COIL': ('FILL_COIL', 'K_FILL, T_FILL and pump command +', 'dc24'), 'NOT_FILL': ('NOT_FILL', 'fill self-hold path', 'dc24'),
    'R_LOCKED': ('R_LOCKED', 'router bed confirmed', 'dc24'), 'TD_POWER': ('TD_POWER', 'T_DRAIN supply', 'dc24'),
    'RUN_READY': ('RUN_READY', 'ready in RUN', 'dc24'),
    'DOCK_1': ('DOCK_1', 'dock feed after F_DOCK', 'dc24'), 'DOCK_ZTOP': ('DOCK_ZTOP', 'dock feed after K_VFD_RUN 41-42', 'dc24'),
    'DOCK_24V': ('DOCK_24V', 'dock motor +24 V, after LS_ZTOP 13-14', 'dc24'),
    'DOCK_RUN_COIL': ('DOCK_RUN_COIL', 'K_DOCK_RUN coil +', 'dc24'), 'DOCK_DIR_COIL': ('DOCK_DIR_COIL', 'K_DOCK_DIR coil +', 'dc24'),
    'XVFD:DIR': ('VFD_DIR', 'run chain: K_VFD_RUN 14 to the K_DIR commons (dry)', 'dry'),
    'XVFD:F1': ('VFD_F1', 'run chain: K_RUN_ARM 34 to K_VFD_RUN 13 (dry)', 'dry'),
    'XVFD:F2': ('VFD_F2', 'run chain: K_REQ_B 14 to K_RUN_ARM 33 (dry)', 'dry'),
    'XPLASMA:S1': ('PLASMA_S1', 'start chain: K_TORCH_RUN 14 to K_RUN_ARM 43 (dry)', 'dry'),
    'XPLASMA:S2': ('PLASMA_S2', 'start chain: K_RUN_ARM 44 to K_REQ_B 23 (dry)', 'dry'),
    'RODENT:VCC_K1': ('48V_LINK', '48 V between K1 pole 1 and K2 pole 1', '48v'),
    'VFD:L_K1': ('VFD_L_LINK', 'VFD mains between K1 pole 2 and K2 pole 2', 'mains'),
    'PLASMA:L_K1': ('PLASMA_L_LINK', 'plasma mains between K1 pole 3 and K2 pole 3', 'mains'),
}
HINT_CLASSES = {'dc24', '0V', '24V'}
NET_INFO.update({
    'RODENT:E1-MAX.1': ('DOOR_SIG', 'Rodent door input signal: K_REQ_A 41-42 and K_RUN_ARM 53-54 in parallel (dry)', 'dry'),
    'RODENT:E1-MAX.2': ('DOOR_GND', 'Rodent door input return (dry)', 'dry'),
    'IFB:XM.1': ('STATUS_READY', 'K_READY status to the expander GPA0 (dry)', 'dry'), 'IFB:XM.2': ('STATUS_PERMIT', 'K_PERMIT status, GPA1 (dry)', 'dry'),
    'IFB:XM.3': ('STATUS_RR', 'router-ready status, GPA2 (dry)', 'dry'), 'IFB:XM.4': ('STATUS_PR', 'plasma-ready status, GPA3 (dry)', 'dry'),
    'IFB:XM.8': ('STATUS_DIR', 'K_DIR status, GPA7 (dry)', 'dry'), 'IFB:XM.COM': ('STATUS_COM', 'status contacts common (board 0 V)', 'dry'),
    'XD:1': ('M1', 'dock motor lead 1: +24 V when deploying (K_DOCK_DIR 12 and 24)', 'dc24'), 'XD:2': ('M2', 'dock motor lead 2: +24 V when parking (K_DOCK_DIR 22 and 14)', 'dc24'),
    'XD:3': ('SEN_24', '+24 V to the dock sensors', 'dc24'), 'XD:4': ('SEN_0V', '0 V to the dock sensors', '0v'),
    'K_DOCK_DIR:11': ('DOCK_PLUS', 'dock motor +24 V, K_DOCK_RUN pole 1 to K_DOCK_DIR pole 1', 'dc24'),
    'K_DOCK_DIR:21': ('DOCK_MINUS', 'dock motor 0 V, K_DOCK_RUN pole 2 to K_DOCK_DIR pole 2', '0v'),
    'K_DOCK_RUN:A2': ('DOCK_RUN_SINK', 'K_DOCK_RUN coil - to the ULN output', 'dc24'), 'K_DOCK_DIR:A2': ('DOCK_DIR_SINK', 'K_DOCK_DIR coil - to the ULN output', 'dc24'),
    'SR:S11': ('ESTOP_CH1', 'E-stop channel 1 loop', 'dc24'), 'SR:S12': ('ESTOP_CH1', 'E-stop channel 1 loop', 'dc24'),
    'SR:S21': ('ESTOP_CH2', 'E-stop channel 2 loop', 'dc24'), 'SR:S22': ('ESTOP_CH2', 'E-stop channel 2 loop', 'dc24'),
    'SR:S33': ('RESET_LOOP', 'reset loop: RESET, K1 and K2 mirror contacts', 'dc24'), 'SR:S34': ('RESET_LOOP', 'reset loop end', 'dc24'),
    'K1:2': ('48V_LINK', '48 V between K1 pole 1 and K2 pole 1', '48v'), 'K1:4': ('VFD_L_LINK', 'VFD mains between K1 pole 2 and K2 pole 2', 'mains'),
    'K1:6': ('PLASMA_L_LINK', 'plasma mains between K1 pole 3 and K2 pole 3', 'mains'),
    'K_READY:41': ('FILL_NC', 'FILL 21-22 to K_READY 41-42 (fill arm pickup, M8)', 'dc24'),
})       # EXTRA wires of these classes only say which net a terminal joins
# Nets that get a bridged distribution rail whatever their size, and the strip name.
RAIL_NAMES = {'0V': 'X0V', 'C': 'XC', 'S': 'XS24', 'BRK_PWR': 'XBRK', 'V': 'XV', '24V': 'X24'}
RAIL_MIN_MEMBERS = 5          # other nets this big get a rail named after their label

# --------------------------------------------------------------------------------------------------------------
# The devices: heading order, where they are, what each terminal is. Terminal functions are shown in the tables;
# terminals listed here but not wired are shown as "not used".
G7SA = {'A1': 'coil +', 'A2': 'coil 0 V'}
def g7sa(no, nc):
    t = dict(G7SA)
    for i, p in enumerate(no, 1):
        a, b = p.split('-'); t[a] = f'NO {i}'; t[b] = f'NO {i}'
    for i, p in enumerate(nc, 1):
        a, b = p.split('-'); t[a] = f'NC {i}'; t[b] = f'NC {i}'
    return t
F4052 = {'11': 'pole 1 common', '12': 'pole 1 NC', '14': 'pole 1 NO', '21': 'pole 2 common', '22': 'pole 2 NC', '24': 'pole 2 NO',
         'A1': 'coil +', 'A2': 'coil 0 V'}
F5534 = {**{f'{p}1': f'pole {p} common' for p in '1234'}, **{f'{p}2': f'pole {p} NC' for p in '1234'},
         **{f'{p}4': f'pole {p} NO' for p in '1234'}, 'A1': 'coil +', 'A2': 'coil 0 V'}
F8001 = {'A1': 'supply +', 'A2': 'supply 0 V', 'B1': 'start input (not used, function AI)', '15': 'timed contact common',
         '16': 'timed NC (opens after the delay)', '18': 'timed NO (closes after the delay)'}
LC1D = {'1': 'main pole 1 in (L1)', '2': 'main pole 1 out (T1)', '3': 'main pole 2 in (L2)', '4': 'main pole 2 out (T2)',
        '5': 'main pole 3 in (L3)', '6': 'main pole 3 out (T3)', '13': 'aux NO', '14': 'aux NO', '21': 'aux NC (mirror)', '22': 'aux NC (mirror)',
        'A1': 'coil +', 'A2': 'coil 0 V'}
PNOZ = {'A1': 'supply +24 V', 'A2': 'supply 0 V', 'S11': 'channel 1 out', 'S12': 'channel 1 in', 'S21': 'channel 2 out', 'S22': 'channel 2 in',
        'S33': 'reset loop out', 'S34': 'reset loop in', '13': 'safety NO 1', '14': 'safety NO 1', '23': 'safety NO 2', '24': 'safety NO 2',
        '33': 'safety NO 3', '34': 'safety NO 3', '41': 'aux NC', '42': 'aux NC'}
DEV = {}
ORDER = []
def dev(key, name, part, where, terms, note=''):
    DEV[key] = dict(name=name, part=part, where=where, terms=dict(terms), note=note)
    ORDER.append(key)

# power and supplies
dev('MAINS', 'Mains distribution', 'Disconnect load side and N / PE distribution blocks (multi-terminal), 240 V split-phase (not modeled)', 'power',
    {'L': 'line distribution (to the breakers)', 'N': 'neutral distribution block', 'PE': 'earth bar'}, 'Distribution blocks take as many wires as they have positions.')
DEV['MAINS']['multi'] = True
dev('CB_CTRL', 'Breaker, control supplies', '2-pole breaker, 10 A (PSU24, PSU48)', 'power', {'1': 'in from mains L', '2': 'out to the PSUs'})
dev('CB_VFD', 'Breaker, VFD', '2-pole breaker sized to the VFD (1.5 kW ER11: 20 A; 4 kW BT30: 30 A)', 'power', {'1': 'in from mains L', '2': 'out to K1:3'})
dev('CB_PLASMA', 'Breaker, plasma cutter', '2-pole breaker for the CUT-50 (30 A)', 'power', {'1': 'in from mains L', '2': 'out to K1:5'})
dev('CB_PUMP', 'Breaker, pump', '1-pole breaker, 5 A (pump SSRs)', 'power', {'1': 'in from mains L', '2': 'out to P_LIMIT:L1'})
dev('PSU24', '24 V control supply', 'MeanWell LRS-350-24 (Rev I)', 'panel',
    {'L': 'mains L', 'N': 'mains N', 'PE': 'earth', 'V+': '+24 V out', 'V-': '0 V out'})
dev('PSU48', '48 V motor supply', '48 V DC supply for the Rodent, 10 A class (Rev K cabinet)', 'panel',
    {'L': 'mains L', 'N': 'mains N', 'PE': 'earth', 'V+': '+48 V out (to K1:1)', 'V-': '48 V return'})
dev('DCDC', '48-to-24 V converter for the Rodent V-MOS outputs', 'Isolated 48 V to 24 V DC-DC, 2 A (mist valve, K_DIR coil)', 'panel',
    {'IN+': '48 V in, after K1 and K2', 'IN-': '48 V return', 'OUT+': '+24 V to the Rodent V-MOS input', 'OUT-': '0 V to the Rodent V-MOS input'},
    'Fed after the contactors, so the mist and the direction relay drop at every E-stop.')
dev('F_CONTROL', 'Fuse, control 24 V', 'DIN fuse terminal, 4 A time-delay (Rev I)', 'panel', {'1': 'in', '2': 'out (C)'})
dev('F_VALVE', 'Fuse, valve 24 V', 'DIN fuse terminal, 2 A (Rev I)', 'panel', {'1': 'in', '2': 'out (V)'})
dev('F_SAFETY', 'Fuse, safety circuit', 'DIN fuse terminal, 2 A time-delay', 'panel', {'1': 'in', '2': 'out (S)'})
dev('F_DOCK', 'Fuse, dock motor', 'DIN fuse terminal, 2 A time-delay', 'panel', {'1': 'in (BRK)', '2': 'out (DOCK_1)'})
# terminal strips
dev('XW', 'XW field terminal strip', 'DIN feed-through terminals, Rev I numbering (2.5 mm2)', 'panel',
    {'7': 'drain valve +', '8': 'drain valve 0 V', '11': 'pan-empty float', '12': 'pan-empty float', '13': 'minimum float', '14': 'minimum float',
     '15': 'fill-stop float', '16': 'fill-stop float', '17': 'high-high float', '18': 'high-high float', '19': 'reservoir level switch',
     '20': 'reservoir level switch', '23': 'BED CONFIRM plasma block', '24': 'BED CONFIRM plasma block', '25': 'BED CONFIRM router block',
     '26': 'BED CONFIRM router block'},
    'Rev I positions 1-4 and 21-22 are not fitted: the rails X24, XC, XV and X0V take their job, and the old stop loop is a link inside SR 33-34.')
dev('XH', 'XH head-loop terminal strip', 'DIN feed-through terminals (Rev I)', 'panel',
    {'3': 'guard door switch', '4': 'guard door switch', '5': 'head loop: U_HEAD output', '6': 'head loop: U_HEAD output'},
    'Positions 1-2 (the old hardware-stop loop) are not fitted.')
dev('XS', 'XS safety-fuse terminal', 'DIN feed-through terminal', 'panel', {'1': 'S rail feed'})
dev('XG', 'XG gantry terminal strip', 'DIN feed-through terminals for the gantry cables that stay in the panel circuit', 'panel',
    {'1': 'LS_ZTOP 13 (dock feed)', '2': 'LS_ZTOP 14 (dock feed)', '3': 'Z brake +', '4': 'Z brake 0 V'})
dev('XD', 'XD dock connector', 'M12 8-pin panel receptacle at the back of the bed module (Rev L) and its plug', 'module',
    {'1': 'motor M1 (through LS_OUT)', '2': 'motor M2 (through LS_IN)', '3': '+24 V sensors', '4': '0 V sensors', '5': 'deployed sensor signal',
     '6': 'parked sensor signal', '7': 'spare (reserved: cover / IR)', '8': 'spare'})
dev('XVFD', 'XVFD terminal strip to the VFD', 'DIN terminals; the VFD sits outside the cabinet on its own plate', 'panel',
    {'FWD': 'forward run (to VFD FOR)', 'REV': 'reverse run (to VFD REV)', 'COM': 'run common (to VFD DCM)', 'VI': '0-10 V speed (to VFD VI)',
     'ACM': '0-10 V common (to VFD ACM)', 'FA': 'VFD "running" relay (BT30)', 'FB': 'VFD "running" relay (BT30)'})
dev('XPLASMA', 'XPLASMA terminal strip to the cutter box', 'DIN terminals; shielded cable to the K_TS box at the cutter', 'panel',
    {'START1': 'torch start pair', 'START2': 'torch start pair'})
# safety and contactors
dev('SR', 'SR safety relay', 'Pilz PNOZ X2.8P 24 V (candidate)', 'panel', PNOZ)
dev('K1', 'K1 contactor', 'Schneider LC1D18BD, 24 V DC coil', 'panel', LC1D)
dev('K2', 'K2 contactor', 'Schneider LC1D18BD, 24 V DC coil', 'panel', LC1D)
dev('ESTOP', 'E-STOP button', 'Latching E-stop, two NC blocks (channels 1 and 2)', 'door', {'11': 'channel 1', '12': 'channel 1', '21': 'channel 2', '22': 'channel 2'},
    'More stations go in series in each channel.')
dev('RESET', 'RESET button', 'Blue momentary, 1 NO', 'door', {'13': 'NO', '14': 'NO'})
dev('T_BRAKE', 'T_BRAKE timer', 'Finder 80.01, function AI, 3 s', 'panel', F8001)
dev('Z_BRAKE', 'Z brake', 'Z motor power-off brake, 24 V coil (energized = released)', 'gantry', {'A1': 'coil +', 'A2': 'coil 0 V'})
# operator switches
dev('MODE_R', 'MODE selector, ROUTER block', 'Schneider XB5AD33 (ROUTER / OFF / PLASMA), NO block 1', 'door', {'13': 'NO', '14': 'NO'})
dev('MODE_P', 'MODE selector, PLASMA block', 'the same selector, NO block 2', 'door', {'13': 'NO', '14': 'NO'})
dev('SETUP_RUN', 'SETUP/RUN selector', 'Schneider XB5AD25, NO + NC blocks', 'door', {'13': 'NO (closes in SETUP)', '14': 'NO', '21': 'NC (opens in SETUP)', '22': 'NC'})
dev('SETUP_RUN_B', 'SETUP/RUN selector, added block', 'Schneider ZBE101 NO block (closes in RUN)', 'door', {'13': 'NO', '14': 'NO'})
dev('AUTO_DRAIN', 'AUTO/DRAIN selector', 'Schneider XB5AD25, NO + NC blocks', 'door', {'13': 'NO (closes in DRAIN)', '14': 'NO', '21': 'NC', '22': 'NC'})
dev('FILL', 'FILL button', 'Schneider XB5AA35, 1 NO + 1 NC', 'door', {'13': 'NO', '14': 'NO', '21': 'NC', '22': 'NC'})
dev('BED_P', 'BED CONFIRM selector, PLASMA CHECKED block', 'Schneider XB5AG03 key selector, NO block 1', 'door', {'13': 'NO', '14': 'NO'})
dev('BED_R', 'BED CONFIRM selector, ROUTER CHECKED block', 'the same key selector, NO block 2', 'door', {'13': 'NO', '14': 'NO'})
# mode and water relays (Rev I)
dev('KM_R', 'KM_R router mode relay', 'Finder 55.34, 94.04 socket', 'panel', F5534)
dev('KM_P', 'KM_P plasma mode relay', 'Finder 55.34, 94.04 socket', 'panel', F5534)
for k, n in (('K_EMPTY', 'pan empty'), ('K_EMPTY_B', 'pan empty, second relay (M9)'), ('K_MIN', 'minimum level'), ('K_DRAIN', 'drain'),
             ('K_DRAINED', 'router drained latch (M9)'), ('K_ARM', 'fill armed'), ('K_FILL', 'fill'), ('K_RDY_R', 'router ready (M2)'),
             ('K_RDY_P', 'plasma ready (M2)'), ('K_DOCK_RUN', 'dock motor run (M13)'), ('K_DOCK_DIR', 'dock motor direction (M13)')):
    dev(k, f'{k} relay: {n}', 'Finder 40.52, 95.05 socket', 'panel', F4052)
dev('T_CLOSE', 'T_CLOSE timer', 'Finder 80.01, function AI, 12 s', 'panel', F8001)
dev('T_DRAIN', 'T_DRAIN timer', 'Finder 80.01, function AI, 75 s', 'panel', F8001)
dev('T_FILL', 'T_FILL timer (M10)', 'Finder 80.01, function AI, 25 min until timed', 'panel', F8001)
dev('R_TC', 'R_TC minimum-load resistor', '680 ohm 3 W (Rev I)', 'panel', {'1': 'end', '2': 'end'})
dev('R_TD', 'R_TD minimum-load resistor', '680 ohm 3 W (Rev I)', 'panel', {'1': 'end', '2': 'end'})
dev('P_LIMIT', 'P_LIMIT pump SSR', 'Carlo Gavazzi RM1D060D20 (Rev I)', 'panel', {'A1': 'control +', 'A2': 'control -', 'L1': 'load in', 'T1': 'load out'})
dev('P_CMD', 'P_CMD pump SSR', 'Carlo Gavazzi RM1D060D20 (Rev I)', 'panel', {'A1': 'control +', 'A2': 'control -', 'L1': 'load in', 'T1': 'load out'})
# start chain (GM1)
for k, no, nc, n in (('K_READY', ['13-14', '23-24', '33-34'], ['41-42'], 'ready'), ('K_PERMIT', ['13-14', '23-24', '33-34'], ['41-42'], 'permit'),
                     ('K_RUN_ARM', ['13-14', '23-24', '33-34', '43-44', '53-54'], ['61-62'], 'run armed'),
                     ('K_REQ_A', ['13-14', '23-24'], ['31-32', '41-42'], 'request A'), ('K_REQ_B', ['13-14', '23-24'], ['31-32', '41-42'], 'request B'),
                     ('K_VFD_RUN', ['13-14', '23-24'], ['31-32', '41-42'], 'spindle run'), ('K_TORCH_RUN', ['13-14', '23-24'], ['31-32', '41-42'], 'torch run'),
                     ('K_DIR', ['13-14', '23-24'], ['31-32', '41-42'], 'spindle direction (M12)')):
    dev(k, f'{k} relay: {n}', 'Omron G7SA force-guided, P7SA socket', 'panel', g7sa(no, nc))
# diodes (added after the netlist is read)
# field devices
dev('DRAIN_VALVE', 'Drain valve', '24 V solenoid valve (Rev I)', 'field', {'1': 'coil +', '2': 'coil 0 V'})
dev('FLOAT_EMPTY', 'Pan empty float', 'Float switch, closes when the pan is empty (Rev I XW:11-12)', 'field', {'1': '', '2': ''})
dev('FLOAT_MIN', 'Minimum level float', 'Float switch (Rev I XW:13-14)', 'field', {'1': '', '2': ''})
dev('FLOAT_FILLSTOP', 'Fill-stop float', 'Float switch, healthy = closed (Rev I XW:15-16)', 'field', {'1': '', '2': ''})
dev('FLOAT_HH', 'High-high float', 'Float switch, healthy = closed (Rev I XW:17-18)', 'field', {'1': '', '2': ''})
dev('RES_LEVEL', 'Reservoir level switch', 'Level switch, healthy = closed (Rev I XW:19-20)', 'field', {'1': '', '2': ''})
dev('DOOR_SW', 'Guard door switch', 'Door closed = closed (Rev I XH:3-4)', 'field', {'1': '', '2': ''})
dev('HEADIF', 'Head interface board (Rev I)', 'U_HEAD and U_PROBE AQY212GS, XHEAD 1-8; see HEAD-INTERFACE.md', 'panel',
    {'U_HEAD.3': 'U_HEAD output', 'U_HEAD.4': 'U_HEAD output', 'U_HEAD.1': 'U_HEAD LED +', 'U_HEAD.2': 'U_HEAD LED -',
     'U_PROBE.3': 'U_PROBE output', 'U_PROBE.4': 'U_PROBE output', 'U_PROBE.1': 'U_PROBE LED +', 'U_PROBE.2': 'U_PROBE LED -',
     'XHEAD.1': 'float loop (R_PROBE)', 'XHEAD.2': 'float loop', 'XHEAD.3': 'presence loop (R_HEAD)', 'XHEAD.4': 'presence loop',
     'XHEAD.5': 'presence loop', 'XHEAD.6': 'presence loop', 'XHEAD.7': 'presence loop', 'XHEAD.8': 'presence loop'},
    'The head switches wire to XHEAD 1-8 as HEAD-INTERFACE.md draws them (four Omron D2HW on the floating head).')
dev('PUMP', 'Water pump', 'Seaflo 31 series 12/24 V or the Rev I AC pump: check the register', 'field', {'L': 'supply', 'N': 'return'})
dev('MIST', 'Router mist valve', '24 V solenoid on the Rodent V-MOS HE0', 'field', {'1': 'coil +', '2': 'coil -'})
dev('LS_ZTOP', 'Z top switch', 'Two-circuit limit switch at the top of Z: NC to the Rodent Z-MAX, NO into the dock feed (M14)', 'gantry',
    {'11': 'NC (Z limit) ', '12': 'NC (Z limit)', '13': 'NO, closed at top', '14': 'NO, closed at top'})
dev('LS_X', 'X limit switch', 'NC switch to the Rodent X-MAX', 'gantry', {'11': 'NC', '12': 'NC'})
dev('LS_Y1', 'Y1 limit switch', 'NC switch to the Rodent Y-MAX', 'gantry', {'11': 'NC', '12': 'NC'})
dev('LS_Y2', 'Y2 limit switch', 'NC switch to the Rodent E0-MAX', 'gantry', {'11': 'NC', '12': 'NC'})
dev('LS_OUT', 'Dock end switch, deployed', 'Microswitch NC, opens at the deployed stop; diode D_OUT across it', 'module', {'11': 'NC', '12': 'NC'})
dev('LS_IN', 'Dock end switch, parked', 'Microswitch NC, opens at the parked stop; diode D_IN across it', 'module', {'11': 'NC', '12': 'NC'})
dev('M_DOCK', 'Dock gearmotor', '24 V worm gearmotor (Rev L)', 'module', {'M1': 'motor lead 1', 'M2': 'motor lead 2'})
dev('SEN_OUT', 'Dock sensor, deployed', 'M8 inductive PNP NO (Rev L)', 'module', {'BN': 'brown: +24 V', 'BU': 'blue: 0 V', 'BK': 'black: signal'})
dev('SEN_IN', 'Dock sensor, parked', 'M8 inductive PNP NO (Rev L)', 'module', {'BN': 'brown: +24 V', 'BU': 'blue: 0 V', 'BK': 'black: signal'})
dev('D_OUT', 'D_OUT diode', '1N4007 across LS_OUT, on the module', 'module', {'A': 'anode (motor side)', 'K': 'cathode (connector side)'})
dev('D_IN', 'D_IN diode', '1N4007 across LS_IN, on the module', 'module', {'A': 'anode (motor side)', 'K': 'cathode (connector side)'})
# controller side
dev('RODENT', 'BTT Rodent V1.1', 'Controller; connector pins per BTT manual and schematic (rodent-io.json)', 'panel',
    {'VCC': 'power in +, 24-56 V (48 V here)', 'GND': 'power in -', 'X-MAX.1': 'X limit signal', 'X-MAX.2': 'X limit GND', 'Y-MAX.1': 'Y1 limit signal',
     'Y-MAX.2': 'Y1 limit GND', 'E0-MAX.1': 'Y2 limit signal', 'E0-MAX.2': 'Y2 limit GND', 'Z-MAX.1': 'Z limit signal', 'Z-MAX.2': 'Z limit GND',
     'E1-MAX.1': 'door input signal', 'E1-MAX.2': 'door input GND', 'PROBE.1': 'probe signal', 'PROBE.2': 'probe GND', 'PROBE.3': 'VProbe (12 V jumper)',
     'CN51.2': 'Sp-Enable GND', 'CN51.3': 'Sp-Enable GPIO25 (run request out)', 'CN52.2': 'Sp-Direction GND', 'CN52.3': 'Sp-Direction GPIO15 (arc OK in)',
     'CN53.2': 'Sp-Feedback GND', 'CN53.3': 'Sp-Feedback GPIO14 (THCAD in)', 'J47.OUT': 'SP-PWM 0-10 V out', 'J47.GND': 'SP-PWM GND',
     'VMOS.+': 'V-MOS supply in +', 'VMOS.-': 'V-MOS supply in -', 'HE0.+': 'HE0 load +', 'HE0.-': 'HE0 load - (switched)',
     'HE1.+': 'HE1 load +', 'HE1.-': 'HE1 load - (switched)', 'OLED.5V': 'OLED +5 V', 'OLED.GND': 'OLED GND', 'OLED.SDA': 'GPIO27 SDA', 'OLED.SCL': 'GPIO26 SCL'},
    'SW_VCC and VProbe jumpers on 12 V (48 V board). The stepper outputs go to the HMS40 and ZBX80 motors as their receiving notes say.')
dev('IFB', 'GM1 interface board', 'One board: run interface (Rev I), MCP23017 expander, ULN2803A, optocouplers, arc-OK pull-up, THCAD buffer', 'panel',
    {'RUN.13': 'U_RUN PhotoMOS output', 'RUN.14': 'U_RUN PhotoMOS output', 'RUN.IN': 'run request in (from CN51.3)', 'RUN.GND': 'controller 0 V (from CN51.2)',
     'XM.1': 'status in: K_READY', 'XM.2': 'status in: K_PERMIT', 'XM.3': 'status in: router ready', 'XM.4': 'status in: plasma ready',
     'XM.8': 'status in: K_DIR', 'XM.COM': 'status common (board 0 V)', 'DOCK_RUN.OUT': 'ULN2803A output, GPB0: sinks the K_DOCK_RUN coil',
     'DOCK_DIR.OUT': 'ULN2803A output, GPB1: sinks the K_DOCK_DIR coil', 'SEN.24': '+24 V to the dock sensors', 'SEN.0V': '0 V to the dock sensors',
     'SEN.OUT': 'deployed sensor in (GPA4)', 'SEN.IN': 'parked sensor in (GPA5)', 'ARC.IN': 'arc OK contact in', 'ARC.COM': 'arc OK common',
     'ARC.OUT': 'to CN52.3', 'THC.IN': 'THCAD frequency in', 'THC.GND': 'THCAD 0 V', 'THC.OUT': 'to CN53.3', 'I2C.5V': 'from OLED 5 V',
     'I2C.GND': 'from OLED GND', 'I2C.SDA': 'from OLED SDA', 'I2C.SCL': 'from OLED SCL', 'FLD.24': 'field +24 V (C) in', 'FLD.0V': 'field 0 V in'},
    'Two ground domains: FLD.* and the DOCK/SEN/XM terminals are field side; RUN.GND, I2C.*, ARC.*, THC.* are controller side. Never join them. '
    'The ULN2803A COM pin (its flyback diodes) goes to FLD.24 on the board; its GND to FLD.0V.')
dev('SPEED', 'Isolated 0-10 V speed converter', 'Isolated signal conditioner between the Rodent J47 and the VFD analog input', 'panel',
    {'IN+': '0-10 V in', 'IN-': 'in common', 'OUT+': '0-10 V out', 'OUT-': 'out common'})
dev('ARC_SW', 'Arc OK current switch', 'Isolated DC current switch on the work lead, dry contact', 'field', {'1': 'contact', '2': 'contact'})
dev('THCAD', 'Mesa THCAD-300', 'Arc voltage to frequency, divider /64 or /128', 'panel', {'FOUT': 'frequency out', 'GND': '0 V', 'IN+': 'arc +', 'IN-': 'arc -'})
dev('VFD', 'VFD', 'Spindle drive on its own plate outside the cabinet (1.5 kW ER11; 4 kW / 800 Hz for BT30)', 'field',
    {'L1': 'mains L (from K2:4)', 'L2/N': 'mains N', 'PE': 'earth', 'U': 'spindle U', 'V': 'spindle V', 'W': 'spindle W', 'FOR': 'forward run',
     'REV': 'reverse run', 'DCM': 'run common', 'VI': '0-10 V speed', 'ACM': 'analog common', 'RA': 'relay out', 'RB': 'relay out (NC)'},
    'Terminal names as the common HY-type drives; map them to the delivered VFD\'s manual.')
dev('PLASMA', 'Plasma cutter and K_TS box', 'CUT-50 with the interposing relay K_TS in a shielded box at the cutter (Rev K)', 'field',
    {'L1': 'mains L (from K2:6)', 'N': 'mains N', 'PE': 'earth', 'KTS.A1': 'K_TS coil + (from XPLASMA)', 'KTS.A2': 'K_TS coil - (from XPLASMA)',
     'KTS.11': 'K_TS contact to the torch trigger', 'KTS.14': 'K_TS contact to the torch trigger'},
    'The K_TS box has its own 24 V supply from the cutter mains after K1/K2; its coil is switched by the XPLASMA pair.')
dev('X24', '+24 V rail', 'Bridged DIN terminals: PSU24 V+ to the three fuses', 'panel', {})
dev('X0V', '0 V distribution rail', 'Bridged DIN terminals (jumper bar): control 0 V', 'panel', {})
dev('XC', 'C distribution rail', 'Bridged DIN terminals: +24 V control after F_CONTROL', 'panel', {})
dev('XS24', 'S distribution rail', 'Bridged DIN terminals: safety-circuit +24 V after F_SAFETY', 'panel', {})
dev('XBRK', 'BRK distribution rail', 'Bridged DIN terminals: +24 V after K1 and K2', 'panel', {})
dev('XV', 'V distribution rail', 'Bridged DIN terminals: +24 V valve supply', 'panel', {})

WHERE_ORDER = ['power', 'panel', 'door', 'gantry', 'module', 'field']
DEVICE_RANK = {k: i for i, k in enumerate(ORDER)}

# --------------------------------------------------------------------------------------------------------------
# Wires added to the netlist's circuit: supplies, the reversing dock motor, the Rodent, the interface board, the
# VFD and cutter side, and the field devices behind each terminal pair. (a, b, net label, note)
EXTRA = [
    # 24 V supply and 0 V
    ('PSU24:V+', '24V', '24V', ''), ('PSU24:V-', 'XW:2', '0V', ''),
    ('CB_CTRL:2', 'PSU24:L', 'mains', ''), ('MAINS:N', 'PSU24:N', 'mains', ''), ('MAINS:PE', 'PSU24:PE', 'pe', ''),
    ('CB_CTRL:2', 'PSU48:L', 'mains', ''), ('MAINS:N', 'PSU48:N', 'mains', ''), ('MAINS:PE', 'PSU48:PE', 'pe', ''),
    ('MAINS:L', 'CB_CTRL:1', 'mains', ''), ('MAINS:L', 'CB_VFD:1', 'mains', ''), ('MAINS:L', 'CB_PLASMA:1', 'mains', ''), ('MAINS:L', 'CB_PUMP:1', 'mains', ''),
    # 48 V: PSU48 -> K1 1-2 -> K2 1-2 -> Rodent VCC (in the netlist); the return and the DC-DC
    ('PSU48:V-', 'RODENT:GND', '48v', ''), ('RODENT:VCC', 'DCDC:IN+', '48v', 'second wire on the Rodent VCC terminal'),
    ('PSU48:V-', 'DCDC:IN-', '48v', ''), ('DCDC:OUT+', 'RODENT:VMOS.+', 'vmos', ''), ('DCDC:OUT-', 'RODENT:VMOS.-', 'vmos', ''),
    # V-MOS loads: K_DIR coil (M12) and the mist valve
    ('RODENT:HE1.+', 'K_DIR:A1', 'vmos', 'K_DIR coil on the HE1 output; 1N4007 across A1-A2, cathode to A1'),
    ('RODENT:HE1.-', 'K_DIR:A2', 'vmos', ''),
    ('RODENT:HE0.+', 'MIST:1', 'vmos', '1N4007 across the valve, cathode to +'), ('RODENT:HE0.-', 'MIST:2', 'vmos', ''),
    # VFD and plasma mains after the contactors (K2:4 and K2:6 are in the netlist), neutrals and earths
    ('MAINS:N', 'VFD:L2/N', 'mains', ''), ('MAINS:PE', 'VFD:PE', 'pe', ''), ('MAINS:N', 'PLASMA:N', 'mains', ''), ('MAINS:PE', 'PLASMA:PE', 'pe', ''),
    # pump: two SSRs in series on the mains
    ('CB_PUMP:2', 'P_LIMIT:L1', 'mains', ''), ('P_LIMIT:T1', 'P_CMD:L1', 'mains', ''), ('P_CMD:T1', 'PUMP:L', 'mains', ''), ('MAINS:N', 'PUMP:N', 'mains', ''),
    # field devices behind the XW / XH pairs
    ('XW:7', 'DRAIN_VALVE:1', 'field', ''), ('XW:8', 'DRAIN_VALVE:2', 'field', ''),
    ('XW:11', 'FLOAT_EMPTY:1', 'field', ''), ('XW:12', 'FLOAT_EMPTY:2', 'field', ''),
    ('XW:13', 'FLOAT_MIN:1', 'field', ''), ('XW:14', 'FLOAT_MIN:2', 'field', ''),
    ('XW:15', 'FLOAT_FILLSTOP:1', 'field', ''), ('XW:16', 'FLOAT_FILLSTOP:2', 'field', ''),
    ('XW:17', 'FLOAT_HH:1', 'field', ''), ('XW:18', 'FLOAT_HH:2', 'field', ''),
    ('XW:19', 'RES_LEVEL:1', 'field', ''), ('XW:20', 'RES_LEVEL:2', 'field', ''),
    ('XH:3', 'DOOR_SW:1', 'field', ''), ('XH:4', 'DOOR_SW:2', 'field', ''),
    ('XH:5', 'HEADIF:U_HEAD.4', 'signal', ''), ('XH:6', 'HEADIF:U_HEAD.3', 'signal', ''),
    ('C', 'HEADIF:XHEAD.3', 'dc24', 'C feed to the head loops through R_HEAD and R_PROBE on the board (HEAD-INTERFACE.md)'),
    ('HEADIF:U_HEAD.2', 'XW:2', '0V', ''), ('HEADIF:U_PROBE.2', 'XW:2', '0V', ''),
    ('HEADIF:U_PROBE.4', 'RODENT:PROBE.3', 'probe', 'controller side'), ('HEADIF:U_PROBE.3', 'RODENT:PROBE.1', 'probe', 'controller side'),
    # Z top switch second contact through the XG strip (M14); the limit switches to the Rodent
    ('XG:1', 'DOCK_ZTOP', 'dc24', ''), ('XG:2', 'DOCK_24V', 'dc24', ''), ('XG:1', 'LS_ZTOP:13', 'field', ''), ('XG:2', 'LS_ZTOP:14', 'field', ''),
    ('LS_ZTOP:11', 'RODENT:Z-MAX.1', 'limit', ''), ('LS_ZTOP:12', 'RODENT:Z-MAX.2', 'limit', ''),
    ('LS_X:11', 'RODENT:X-MAX.1', 'limit', ''), ('LS_X:12', 'RODENT:X-MAX.2', 'limit', ''),
    ('LS_Y1:11', 'RODENT:Y-MAX.1', 'limit', ''), ('LS_Y1:12', 'RODENT:Y-MAX.2', 'limit', ''),
    ('LS_Y2:11', 'RODENT:E0-MAX.1', 'limit', ''), ('LS_Y2:12', 'RODENT:E0-MAX.2', 'limit', ''),
    # dock motor: K_DOCK_RUN pole 1 switches +24 V, pole 2 the 0 V; K_DOCK_DIR's two poles reverse the motor (M13)
    ('K_DOCK_RUN:14', 'K_DOCK_DIR:11', 'dc24', ''), ('XW:2', 'K_DOCK_RUN:21', '0V', ''), ('K_DOCK_RUN:24', 'K_DOCK_DIR:21', '0V', 'switched 0 V'),
    ('K_DOCK_DIR:12', 'XD:1', 'dc24', 'M1: +24 V when deploying'), ('K_DOCK_DIR:24', 'K_DOCK_DIR:12', 'dc24', 'jumper on the socket'),
    ('K_DOCK_DIR:22', 'XD:2', 'dc24', 'M2: +24 V when parking'), ('K_DOCK_DIR:14', 'K_DOCK_DIR:22', 'dc24', 'jumper on the socket'),
    ('XD:1', 'LS_OUT:11', 'field', 'on the module'), ('LS_OUT:12', 'M_DOCK:M1', 'field', ''), ('D_OUT:K', 'LS_OUT:11', 'field', ''), ('D_OUT:A', 'LS_OUT:12', 'field', ''),
    ('XD:2', 'LS_IN:11', 'field', 'on the module'), ('LS_IN:12', 'M_DOCK:M2', 'field', ''), ('D_IN:K', 'LS_IN:11', 'field', ''), ('D_IN:A', 'LS_IN:12', 'field', ''),
    # dock relay coils: + from C, - sunk by the ULN2803A outputs (the netlist draws the channel as a contact on the + side)
    ('C', 'K_DOCK_RUN:A1', 'dc24', ''), ('K_DOCK_RUN:A2', 'IFB:DOCK_RUN.OUT', 'dc24', ''),
    ('C', 'K_DOCK_DIR:A1', 'dc24', ''), ('K_DOCK_DIR:A2', 'IFB:DOCK_DIR.OUT', 'dc24', ''),
    # dock sensors through the connector to the interface board optocouplers
    ('IFB:SEN.24', 'XD:3', 'dc24', ''), ('IFB:SEN.0V', 'XD:4', '0V', ''), ('XD:5', 'IFB:SEN.OUT', 'signal', ''), ('XD:6', 'IFB:SEN.IN', 'signal', ''),
    ('XD:3', 'SEN_OUT:BN', 'field', 'on the module'), ('XD:4', 'SEN_OUT:BU', 'field', ''), ('XD:5', 'SEN_OUT:BK', 'field', ''),
    ('SEN_OUT:BN', 'SEN_IN:BN', 'field', ''), ('SEN_OUT:BU', 'SEN_IN:BU', 'field', ''), ('XD:6', 'SEN_IN:BK', 'field', ''),
    ('C', 'IFB:FLD.24', 'dc24', ''), ('XW:2', 'IFB:FLD.0V', '0V', ''),
    # Rodent <-> interface board (controller side)
    ('RODENT:CN51.3', 'IFB:RUN.IN', 'ctl', ''), ('RODENT:CN51.2', 'IFB:RUN.GND', 'ctl', ''),
    ('RODENT:CN52.3', 'IFB:ARC.OUT', 'ctl', ''), ('ARC_SW:1', 'IFB:ARC.IN', 'signal', ''), ('ARC_SW:2', 'IFB:ARC.COM', 'signal', ''),
    ('RODENT:CN53.3', 'IFB:THC.OUT', 'ctl', ''), ('THCAD:FOUT', 'IFB:THC.IN', 'signal', ''), ('THCAD:GND', 'IFB:THC.GND', 'signal', ''),
    ('RODENT:OLED.5V', 'IFB:I2C.5V', 'ctl', ''), ('RODENT:OLED.GND', 'IFB:I2C.GND', 'ctl', ''), ('RODENT:OLED.SDA', 'IFB:I2C.SDA', 'ctl', ''),
    ('RODENT:OLED.SCL', 'IFB:I2C.SCL', 'ctl', ''),
    # speed
    ('RODENT:J47.OUT', 'SPEED:IN+', 'ctl', ''), ('RODENT:J47.GND', 'SPEED:IN-', 'ctl', ''), ('SPEED:OUT+', 'XVFD:VI', 'signal', ''), ('SPEED:OUT-', 'XVFD:ACM', 'signal', ''),
    # cabinet strips to the VFD and the cutter box
    ('XVFD:FWD', 'VFD:FOR', 'signal', ''), ('XVFD:REV', 'VFD:REV', 'signal', ''), ('XVFD:COM', 'VFD:DCM', 'signal', ''),
    ('XVFD:VI', 'VFD:VI', 'signal', ''), ('XVFD:ACM', 'VFD:ACM', 'signal', ''),
    ('XPLASMA:START1', 'PLASMA:KTS.A1', 'signal', 'shielded pair'), ('XPLASMA:START2', 'PLASMA:KTS.A2', 'signal', ''),
    # Z brake: its leads run up the gantry to XG (the netlist wires Z_BRAKE:A1/A2 directly)
    ('XG:3', 'Z_BRAKE_COIL', 'dc24', ''), ('XG:4', 'XW:2', '0V', ''), ('XG:3', 'Z_BRAKE:A1', 'field', ''), ('XG:4', 'Z_BRAKE:A2', 'field', ''),
]
JUMPER_NOTE = 'jumper on the socket'

COLOUR = {'0v': ('blue/white', '18 AWG'), 'dc24': ('blue', '18 AWG'), '24V': ('blue', '16 AWG'), 'mains': ('black (L) / white (N)', '12 AWG; 10 AWG plasma'),
          'pe': ('green/yellow', '12 AWG'), '48v': ('black', '14 AWG'), 'vmos': ('blue', '18 AWG'), 'field': ('blue', '18 AWG, or the device cable'),
          'signal': ('blue, shielded pair where noted', '20 AWG'), 'ctl': ('grey (controller 3.3/5 V side)', '22 AWG'), 'limit': ('blue', '20 AWG, shielded'),
          'probe': ('grey', '22 AWG'), 'dry': ('blue', '18 AWG')}


def is_terminal(node):
    return ':' in node and node not in INTERNAL


def device_of(term):
    return term.split(':', 1)[0]


class UF:
    def __init__(self):
        self.p = {}
    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


EXTERNAL_WHERE = {'door', 'gantry', 'module', 'field'}
STRIPS = ('XW', 'XH', 'XS', 'XG', 'XD', 'XVFD', 'XPLASMA')


def main():
    raw = NETLIST.read_bytes()
    net = json.loads(raw)
    rows = net['connections']
    rn = lambda n: RENAME.get(n, n)
    node_terms = defaultdict(set)      # node -> physical terminals on it
    uf = UF()
    graph_wires = []                   # (a, b) wires that define the nets
    fixed = []                         # (a, b, cls, note) physical wires emitted verbatim
    hint_notes = {}
    excluded = 0
    for r in rows:
        a, b = rn(r['a']), rn(r['b'])
        if a in EXCLUDE_NODES or b in EXCLUDE_NODES or r['tag'] in EXCLUDE_TAGS or frozenset((r['a'], r['b'])) in EXCLUDE_WIRES:
            excluded += 1
            continue
        kind = r['kind']
        if kind == 'wire':
            graph_wires.append((a, b))
        elif kind == 'diode':
            d = r['tag']
            DEV[d] = dict(name=f'{d} diode', part='1N4007 in a diode terminal or on the socket (Rev I / M9)', where='panel',
                          terms={'A': 'anode', 'K': 'cathode'}, note='')
            ORDER.insert(ORDER.index('DRAIN_VALVE'), d)
            graph_wires.append((a, f'{d}:A')); graph_wires.append((f'{d}:K', b))
        else:   # contact or power contact: the device's two terminals sit on the two nodes
            tag = r['tag']
            if ':' in tag:
                dv, poles = tag.split(':')
                pq = poles.split('-')
            else:
                dv, pq = tag, ('1', '2')
            ta, tb = rn(f'{dv}:{pq[0]}'), rn(f'{dv}:{pq[1]}')
            node_terms[a].add(ta); node_terms[b].add(tb)
            uf.find(a); uf.find(b)
    for a, b, cls, note in EXTRA:
        if cls in HINT_CLASSES:
            graph_wires.append((a, b))
            if note:
                hint_notes[frozenset((a, b))] = note
        else:
            fixed.append((a, b, cls, note))
    for a, b in graph_wires:
        for n in (a, b):
            if is_terminal(n):
                node_terms[n].add(n)
        uf.union(a, b)
    for n in list(node_terms):
        uf.find(n)
    DEVICE_RANK.update({k: i for i, k in enumerate(ORDER)})
    nets = defaultdict(set)
    for n in list(uf.p):
        nets[uf.find(n)].add(n)
    # direct partners: terminals sharing a node, or joined by one graph wire
    partners = defaultdict(set)
    for n, ts in node_terms.items():
        for t in ts:
            partners[t] |= ts - {t}
    for a, b in graph_wires:
        for ta in node_terms.get(a, ()):
            for tb in node_terms.get(b, ()):
                if ta != tb:
                    partners[ta].add(tb); partners[tb].add(ta)

    def where(t):
        d = device_of(t)
        return DEV[d]['where'] if d in DEV else 'field'
    def rank(t):
        d = device_of(t)
        strip = 0 if d in STRIPS else 1
        return (strip, WHERE_ORDER.index(where(t)) if where(t) in WHERE_ORDER else 9, DEVICE_RANK.get(d, 999), term_sort_key(t.split(':', 1)[1]))
    def label_of(nodes):
        if 'XW:2' in nodes:
            return '0V'
        labels = [n for n in nodes if n in NET_INFO]
        if labels:
            return sorted(labels, key=lambda l: list(NET_INFO).index(l))[0]
        ts = sorted((t for t in nodes if is_terminal(t)), key=rank)
        return ts[0] if ts else sorted(nodes)[0]

    realized, rails = [], {}
    used = defaultdict(list)           # terminal -> [(wire no, other end, net label, note)]
    counter = [0]
    def emit(entry, a, b, note=''):
        counter[0] += 1
        n = counter[0]
        if device_of(a) == device_of(b) and not note:
            note = JUMPER_NOTE
        entry['wires'].append(dict(no=n, a=a, b=b, note=note))
        used[a].append((n, b, entry['label'], note)); used[b].append((n, a, entry['label'], note))
    def cap(t):
        return 2 - len(used[t])

    # the fixed wires first: cables to devices and connectors outside the relay logic
    groups = defaultdict(list)
    for a, b, cls, note in fixed:
        groups[cls].append((a, b, note))
    CLASS_LABEL = {'field': ('FIELD', 'cables to field devices'), 'mains': ('MAINS', 'mains wiring'), 'pe': ('PE', 'protective earth'),
                   '48v': ('48V', '48 V motor supply'), 'vmos': ('VMOS', 'Rodent V-MOS loads'), 'signal': ('SIGNAL', 'signal cables'),
                   'ctl': ('CTL', 'controller-side signals'), 'limit': ('LIMIT', 'limit switches to the Rodent'), 'probe': ('PROBE', 'probe to the Rodent')}
    cable_entries = []
    for cls in CLASS_LABEL:
        if cls not in groups:
            continue
        lab, desc = CLASS_LABEL[cls]
        entry = dict(label=lab, description=desc, cls=cls, members=sorted({x for a, b, _ in groups[cls] for x in (a, b)}), wires=[], rail=None)
        for a, b, note in groups[cls]:
            emit(entry, a, b, note)
        cable_entries.append(entry)

    ordered = sorted(nets.values(), key=lambda ns: (0 if 'XW:2' in ns else 1,
                                                    min((rank(t) for t in ns if is_terminal(t)), default=(9, 9, 999, ''))))
    problems = []
    for nodes in ordered:
        members = sorted({t for n in nodes for t in node_terms.get(n, set())} | {n for n in nodes if is_terminal(n)}, key=rank)
        if not members:
            continue
        lab = label_of(nodes)
        info = NET_INFO.get(lab, ('link', f'{members[0]} to {members[-1]}', 'dc24'))
        entry = dict(label=info[0], description=info[1], cls=info[2], members=members, wires=[], rail=None)
        # external devices (door, gantry, module, field) wire only to their own strip position or panel terminal
        for t in list(members):
            if where(t) in EXTERNAL_WHERE:
                ps = [u for u in partners[t] if u in members and where(u) not in EXTERNAL_WHERE]
                if len(ps) == 1:
                    emit(entry, ps[0], t, hint_notes.get(frozenset((ps[0], t)), ''))
                    members.remove(t)
        ends = [m for m in members if cap(m) == 1]
        full = [m for m in members if cap(m) <= 0]
        if full:
            problems.append({'net': info[0], 'no free side': full})
        rail_name = RAIL_NAMES.get(lab)
        board = any(device_of(m) in ('IFB', 'RODENT', 'HEADIF') for m in members)   # a board terminal is one screw: chain the relay contacts to it
        if rail_name is None and not board and (len(members) >= RAIL_MIN_MEMBERS or (len(ends) > 2 and len(members) >= 3)):
            rail_name = 'X_' + re.sub(r'[^A-Z0-9]', '', info[0].upper())[:10]
        if rail_name and len(members) >= 3:
            k = math.ceil(len(members) / 2)
            rails[rail_name] = dict(label=info[0], description=info[1], positions=k)
            DEV.setdefault(rail_name, dict(name=f'{rail_name} distribution rail', part='Bridged DIN terminals (jumper bar)', where='panel', terms={}, note=''))
            if rail_name not in ORDER:
                ORDER.insert(ORDER.index('X0V'), rail_name)
                DEVICE_RANK.update({k_: i for i, k_ in enumerate(ORDER)})
            for i, m in enumerate(members):
                emit(entry, m, f'{rail_name}:{i // 2 + 1}')
            entry['rail'] = rail_name
        else:
            middle = [m for m in members if cap(m) >= 2]
            chain = ends[:1] + middle + ends[1:2]
            for i in range(len(chain) - 1):
                emit(entry, chain[i], chain[i + 1], hint_notes.get(frozenset((chain[i], chain[i + 1])), ''))
        realized.append(entry)
    realized += cable_entries
    # renumber in document order and rebuild the terminal index
    used.clear()
    n = 100
    for e in realized:
        for w in e['wires']:
            n += 1
            w['no'] = n
            used[w['a']].append((n, w['b'], e['label'], w['note'])); used[w['b']].append((n, w['a'], e['label'], w['note']))
    for rail_name, r in rails.items():
        DEV[rail_name]['terms'] = {str(i + 1): 'bridged' for i in range(r['positions'])}
        DEV[rail_name]['note'] = f'{r["positions"]} positions bridged together: {r["description"]}. One wire per side of each position.'
    overloaded = {t: len(w) for t, w in used.items() if len(w) > 2 and not DEV.get(device_of(t), {}).get('multi')}
    all_wires = [w for e in realized for w in e['wires']]
    checks = {'nets': len(realized), 'wires': len(all_wires), 'terminals_wired': len(used),
              'terminals_with_more_than_two_wires': overloaded, 'terminals_with_no_free_side': problems,
              'netlist_connections': len(rows), 'netlist_excluded_by_hand': excluded,
              'devices_without_catalogue_entry': sorted({device_of(t) for t in used} - set(DEV)),
              'field_terminals_left_in_chains': sorted(t for e in realized if e['cls'] not in CLASS_LABEL for t in e['members']
                                                       if where(t) in ('gantry', 'module', 'field') and any(t in (w['a'], w['b']) for w in e['wires']) and not e['rail'] and len(e['members']) > 2)}
    checks['pass'] = not overloaded and not problems and not checks['devices_without_catalogue_entry'] and not checks['field_terminals_left_in_chains']
    write(realized, used, rails, checks, raw)
    print(json.dumps(checks, indent=1))
    return 0 if checks['pass'] else 2


def term_sort_key(t):
    m = re.match(r'(\D*)(\d+)(.*)', t)
    return (0, m.group(1), int(m.group(2)), m.group(3)) if m else (1, t, 0, '')


def write(realized, used, rails, checks, raw):
    lines = ['# GM1 wiring by terminal', '',
             'Every screw terminal in the GM1 controls, the wire number on it and where that wire\'s other end lands. Generated by '
             '`gm1_wiring.py` from [the simulated circuit](gm1-terminal-netlist.json) (M1-M14) and the wiring decisions listed in that '
             'file. The [wire list](gm1-wire-list.csv) has the same wires one per row.', '',
             '**How to use it.** Cut each wire, put its number on both ends, and on each end also write the terminal at the *other* end '
             '(the ferrule label reads, for example, `104 > K_ARM:A1`). Then go device by device: the table for each device lists every '
             'terminal that gets a wire, what lands on it and where it goes. A terminal that is not in the table gets nothing. '
             '"Jumper on the socket" is a short link between two terminals of the same device.', '',
             '**Rails.** Nets with many members (0 V, C, S, BRK, V and a few more) are not daisy-chained: each member gets its own wire to '
             'a position on a bridged terminal group (a DIN terminal strip with a jumper bar across all its positions). One wire per side '
             'of each position, so no screw ever carries more than two wires.', '',
             '**Colours and sizes** (NFPA 79 style, all copper, ferruled): blue = 24 V DC control; blue/white = 0 V; black = 48 V and mains '
             'line; white = mains neutral; green/yellow = earth; grey = controller-side (3.3 / 5 V) signals; shielded pairs where the row '
             'says so. Control 18 AWG, controller signals 22 AWG, 48 V 14 AWG, VFD mains 12 AWG (10 AWG for the 4 kW BT30 drive), plasma '
             'mains 10 AWG. The exact breaker and wire sizes follow the delivered VFD, cutter and PSUs.', '',
             '**Two 0 V domains.** Field 0 V (X0V, XW:2, everything blue/white) and the controller\'s ground (Rodent GND, the OLED, CN51-53, '
             'the interface board\'s RUN, I2C, ARC and THC terminals) are never joined. The optocouplers and PhotoMOS parts on the interface '
             'board are the only things that cross between them.', '',
             'This is a wiring list for a working design, not a certified panel. Terminal marks come from the makers\' datasheets named in the '
             '[controls README](README.md): check them on the actual parts, and read that page for what each circuit does before energizing anything.', '',
             f'{checks["nets"]} nets, {checks["wires"]} wires, {checks["terminals_wired"]} terminals; '
             f'{"no terminal carries more than two wires" if not checks["terminals_with_more_than_two_wires"] else "OVERLOADED: " + str(checks["terminals_with_more_than_two_wires"])}.', '',
             '## Contents', '']
    sections = [('power', 'Power and supplies'), ('panel', 'Inside the cabinet'), ('door', 'Cabinet door'), ('gantry', 'Gantry'),
                ('module', 'Bed module (tool changer)'), ('field', 'Field devices, VFD and cutter')]
    by_where = defaultdict(list)
    for key in ORDER:
        if key in DEV and (any(t.startswith(key + ':') for t in used) or key in rails):
            by_where[DEV[key]['where']].append(key)
    for w, title in sections:
        lines.append(f'- **{title}**: ' + ', '.join(f'[{k}](#{k.lower().replace("_", "")})' for k in by_where[w]))
    lines += ['', '## Rails', '', '| Rail | Carries | Positions |', '|---|---|---|']
    for rail_name, r in rails.items():
        lines.append(f'| {rail_name} | {r["label"]}: {r["description"]} | {r["positions"]}, all bridged |')
    lines += ['']
    for w, title in sections:
        lines += [f'## {title}', '']
        for key in by_where[w]:
            d = DEV[key]
            lines += [f'### {key}', '', f'**{d["name"]}** — {d["part"]}. ' + (d['note'] or ''), '',
                      '| Terminal | Function | Wire | Goes to | Net |', '|---|---|---|---|---|']
            terms = list(d['terms'])
            wired = {t.split(':', 1)[1] for t in used if device_of(t) == key}
            for t in sorted(set(terms) | wired, key=term_sort_key):
                full = f'{key}:{t}'
                func = d['terms'].get(t, '')
                if full in used:
                    for n, other, lab, note in sorted(used[full]):
                        lines.append(f'| **{t}** | {func} | {n} | {other}{(" — " + note) if note else ""} | {lab} |')
                else:
                    lines.append(f'| {t} | {func} | — | not used | |')
            lines.append('')
    lines += ['## The BT30 variant: what changes on these terminals (M15, M16; not simulated)', '',
              'For the [BT30 package](../release-review/RevL-BT30-CAD/README.md). Everything above stays; add:', '',
              '| Add | Terminals |', '|---|---|',
              '| **F_AIR** fuse, 2 A, and **K_DRAWBAR** (Finder 40.52) | XBRK rail → F_AIR:1; F_AIR:2 → K_REQ_B:41; K_REQ_B:42 → XVFD:FA; XVFD:FB → K_DRAWBAR:11; K_DRAWBAR:14 → drawbar valve +; valve − → X0V. VFD relay RA/RB programmed "running", wired to XVFD:FA/FB (the NC side, so it is closed only with the spindle stopped). K_DRAWBAR:A1 ← XC rail, A2 → IFB:DRAWBAR.OUT (ULN2803A, GPB2), like the dock relays |',
              '| **Blow-off valve** (if the spindle has the port) | Same pattern on GPB3: K_BLOW:A1 ← XC, A2 → IFB:BLOW.OUT; K_BLOW:11 from F_AIR:2, 14 → valve +; valve − → X0V |',
              '| **Clamp sensors** (spindle\'s PNP sensors) | Brown → XC rail, blue → X0V, black "clamped" → IFB:SEN.CLAMPED (GPA6), black "released" → IFB:SEN.RELEASED (GPB4 as input); each through the optocoupler pattern of the dock sensors |',
              '| **K_RELEASED** (Finder 40.52) | Coil A1 ← the "released" sensor black wire (second core), A2 → X0V. Move the wire that runs K_RDY_R:14 → K_VFD_RUN:A1 (VFD_RUN_COIL): K_RDY_R:14 → K_RELEASED:11; K_RELEASED:12 → K_VFD_RUN:A1. The spindle cannot start with the drawbar released |',
              '| **Air pressure switch** | Contact between XC rail and IFB:SEN.AIR (GPB5 as input) |',
              '| **VFD** | 4 kW, 800 Hz output; the same XVFD:FWD/REV/COM/VI/ACM terminals plus FA/FB |', '',
              'Add these to `gm1_circuit.py` and its tests when the spindle\'s sensor arrangement is known; until then they are wiring instructions only.', '']
    (HERE / 'GM1-WIRING-BY-TERMINAL.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    with open(HERE / 'gm1-wire-list.csv', 'w', newline='', encoding='utf-8') as f:
        wr = csv.writer(f)
        wr.writerow(['wire', 'from', 'to', 'net', 'colour', 'size', 'note'])
        for e in realized:
            col, size = COLOUR.get(e['cls'], ('blue', '18 AWG'))
            for w in e['wires']:
                wr.writerow([w['no'], w['a'], w['b'], e['label'], col, size, w['note']])
    doc = {'scope': __doc__.strip(), 'netlist_sha256': hashlib.sha256(raw).hexdigest(), 'checks': checks, 'rails': rails,
           'nets': [{k: v for k, v in e.items()} for e in realized]}
    (HERE / 'gm1-wiring.json').write_text(json.dumps(doc, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    raise SystemExit(main())
