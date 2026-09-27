"""Exercise the GM1 panel model: Rev I behaviors, the stop, the mode race, welded contacts,
and (M12/M13) spindle reverse and the tool-changer drive.

Writes gm1-circuit-verification.json next to this file, plus the regenerated
netlist (gm1-terminal-netlist.json, GM1-TERMINALS.md). Every check is a
simulation of the connection graph in gm1_circuit.py with finite relay delays;
none is a measurement of a built panel.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import itertools
import json
import sys
import time

import gm1_circuit as gm1
from gm1_circuit import Simulator

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
REV_I_SOURCE = gm1.REV_I_DIR / 'circuit.py'
PICKUPS, DROPOUTS = (.005, .010, .020), (.005, .020, .050)
CONTACTOR_TIMING = ((.030, .010), (.060, .020), (.100, .040))
PLASMA = dict(plasma=True, bed_clear=True, bed_locked=False, minimum=True, empty=False)
ROUTER = dict(router=True, bed_locked=True, bed_clear=False, empty=True, minimum=False)
TOOL = {'router': 'router_run', 'plasma': 'torch_run'}
CHECKS = []


def check(name, passed, **evidence):
    CHECKS.append({'check': name, 'passed': bool(passed), **evidence})
    if not passed:
        raise AssertionError((name, evidence))


def started(pick=.010, drop=.020, **kw):
    """Powered panel after the operator's first reset, controller booted, SETUP."""
    s = Simulator(pick, drop, **kw)
    s.run(.2)
    s.reset()
    s.run(3.2)
    return s


def ready(mode, pick=.010, drop=.020, **kw):
    s = started(pick, drop, **kw)
    s.run(75.4 if mode == 'router' else 12.4, setup=False, **(ROUTER if mode == 'router' else PLASMA))
    return s


def running(mode, pick=.010, drop=.020, **kw):
    s = ready(mode, pick, drop, **kw)
    s.run(.3, run_request=True)
    return s


def filling(pick=.010, drop=.020, **kw):
    s = started(pick, drop, **kw)
    s.run(12.25, **PLASMA)
    return s


def structure():
    tags = [e.tag for e in gm1.CONTACTS + gm1.POWER]
    check('Every contact tag is unique', len(set(tags)) == len(tags))
    usage = gm1.pole_usage()
    over = {k: sorted(set(v) - set(gm1.DEVICES[k].get('no', [])) - set(gm1.DEVICES[k].get('nc', [])))
            for k, v in usage.items()}
    check('Every new device uses only its purchased poles', not any(over.values()), usage=usage)
    rev_i_relays = {k for k in gm1.LOADS if k.startswith('K') and k not in gm1.DEVICES}
    check('Rev I relays keep within their poles', all(
        len({e.tag.split(':')[1].split('-')[0] for e in gm1.CONTACTS if e.tag.startswith(k + ':')}) <= (4 if k.startswith('KM_') else 2)
        for k in rev_i_relays), relays=sorted(rev_i_relays))
    # Galvanic separation: with every contact forced closed, no dry pair or
    # safety-relay input loop joins the 24 V control network.
    s = Simulator()
    s.failed_closed = {e.tag for e in gm1.CONTACTS}
    live = s.live(s.graph(s.values()))
    dry = sorted(n for n in live if n.startswith(('XVFD:', 'XPLASMA:', 'XR:', 'XM:', 'SR:S', 'RST_')))
    check('Dry outputs and safety-relay input loops never join the 24 V network', not dry, joined=dry)
    removed = sorted({e.tag for e in gm1.DROPPED if e.control})
    check('Only the Rev I stop and start-chain contacts are removed', set(removed) == {
        'XW:21-22', 'XH:1-2', 'K_READY:11-14', 'K_READY:21-24', 'IF_RUN:13-14', 'K_REQUEST:11-12', 'K_REQUEST:21-24',
        'K_RUN_ARM:11-14', 'K_RUN_ARM:21-24', 'K_VFD_RUN:11-14', 'K_TORCH_RUN:11-14'}, removed=removed)
    rerouted = sorted(f'{e.tag} {e.a}-{e.b}' if e.directed else f'{e.a}-{e.b}' for e in gm1.DROPPED
                      if not e.control and (e.directed or {e.a, e.b} in ({'T_DRAIN:18', 'RR'}, {'K_FILL:14', 'FILL_COIL'})))
    check('Water logic changes reroute only the drain request, the drain-timer output and the fill self-hold',
          rerouted == ['D_R DR_REQ-DRAIN_COIL', 'K_FILL:14-FILL_COIL', 'T_DRAIN:18-RR'], rerouted=rerouted)


def rev_i_behaviors():
    """Rev I's own checks, repeated on the GM1 graph (stop_ok and hardware_stop_ok are now the E-stop)."""
    combos = 0
    for pick, drop in itertools.product(PICKUPS, DROPOUTS):
        s = filling(pick, drop)
        check('No fill without deliberate press', not s.outputs()['pump'], pickup=pick, dropout=drop)
        s.run(.15, fill_pressed=True)
        check('Deliberate fill starts', s.outputs()['pump'], pickup=pick, dropout=drop)
        s.run(.15, fill_pressed=False)
        check('Fill self-holds after release', s.outputs()['pump'])
        s.run(.15, fill_stop_healthy=False)
        check('Normal fill stop removes pump', not s.outputs()['pump'])
        s.run(.15, fill_pressed=True, fill_stop_healthy=True)
        check('Held fill does not restart after fill-stop', not s.outputs()['pump'])
        s.run(.15, fill_pressed=False)
        s.run(.15, fill_pressed=True)
        check('Release then press rearms after fill-stop', s.outputs()['pump'])
        for field in ('high_high_healthy', 'reservoir_healthy', 'bed_clear'):
            s = filling(pick, drop)
            s.run(.15, fill_pressed=True)
            s.run(.15, **{field: False})
            check('Fault stops pump: ' + field, not s.outputs()['pump'])
            s.run(.15, **{field: True})
            check('Held button does not recover: ' + field, not s.outputs()['pump'])
        s = filling(pick, drop)
        s.run(.15, fill_pressed=True)
        s.run(.15, estop_ch1=False, estop_ch2=False)
        check('E-stop stops pump', not s.outputs()['pump'])
        s.run(.15, estop_ch1=True, estop_ch2=True)
        s.reset()
        s.run(12.25)
        check('Held FILL does not recover after E-stop reset', not s.outputs()['pump'])
        for state in ({'drain_override': True}, {'setup': False}, {'plasma': False}):
            s = filling(pick, drop)
            s.run(.15, fill_pressed=True)
            s.run(.15, **state)
            check('Mode/setup/override stops pump', not s.outputs()['pump'], change=state)
        s = started(pick, drop)
        s.run(12.25, fill_pressed=True, **PLASMA)
        check('Held FILL on power-up never starts pump', not s.outputs()['pump'])
        combos += 1
    for short in ('P_CMD', 'P_LIMIT'):
        for field in ('high_high_healthy', 'reservoir_healthy'):
            s = filling()
            s.run(.15, fill_pressed=True)
            s.ssr_failed_short.add(short)
            s.run(.15, **{field: False})
            check('Single SSR short interrupted by healthy-chain loss', not s.outputs()['pump'], short=short, field=field)
    s = filling()
    s.run(.15, fill_pressed=True)
    s.run(.15, power=False)
    check('Power loss removes fill and arm', not any(s.outputs()[k] for k in ('pump', 'fill', 'fill_armed')))
    s.run(.2, power=True)
    s.reset()
    s.run(12.25)
    check('Held FILL after power restoration stays off', not s.outputs()['pump'])
    for mode, pick, drop in itertools.product(('router', 'plasma'), PICKUPS, DROPOUTS):
        other = 'plasma' if mode == 'router' else 'router'
        s = started(pick, drop, holds_request=True)
        s.run(75.4 if mode == 'router' else 12.4, setup=False, run_request=True, **(ROUTER if mode == 'router' else PLASMA))
        check('Held request cannot start tool after cold power-up', not s.outputs()['router_run'] and not s.outputs()['torch_run'],
              mode=mode, pickup=pick, dropout=drop)
        s.run(.3, run_request=False)
        s.run(.3, run_request=True)
        out = s.outputs()
        check('Only selected tool can run: ' + mode, out[TOOL[mode]] and not out[TOOL[other]])
        for field in ('door_closed', 'breakaway_seated'):
            s.run(.3, **{field: False})
            check('Hardware chain stops tools: ' + field, not s.outputs()['router_run'] and not s.outputs()['torch_run'])
            check('Permission loss while requested opens the Rodent door input: ' + field, not s.outputs()['door_ok'])
            s.run(.3, **{field: True})
            check('Held run cannot resume after permission recovery: ' + field,
                  not s.outputs()['router_run'] and not s.outputs()['torch_run'])
            s.run(.3, run_request=False)
            check('Door input closes again once the request drops: ' + field, s.outputs()['door_ok'])
            s.run(.3, run_request=True)
            check('Fresh run request after recovery starts selected tool', s.outputs()[TOOL[mode]])
        s.run(.3, power=False)
        s.run(.2, power=True)
        s.reset()
        s.run(75.4 if mode == 'router' else 12.4)
        check('Held run after power restoration stays off', not s.outputs()['router_run'] and not s.outputs()['torch_run'])
    s = started()
    s.run(74.9, setup=False, **ROUTER)
    check('Drain timer cannot ready early', not s.outputs()['ready'])
    s.run(.35)
    check('Drain dwell eventually permits ready', s.outputs()['ready'])
    s.run(.15, empty=False)
    check('Lost empty contact inhibits router ready', not s.outputs()['ready'])
    s = started()
    s.run(.25, drain_override=True)
    check('Drain override does not backfeed mode relays', not s.states['KM_R'] and not s.states['KM_P'] and s.outputs()['drain'])
    # Rev I's short-interruption counterexample, now split in two.
    s = filling(drop=.050)
    s.run(.15, fill_pressed=True)
    s.run(.005, estop_ch1=False, estop_ch2=False)
    s.run(.05, estop_ch1=True, estop_ch2=True)
    estop_5ms_filtered = s.outputs()['pump'] and s.outputs()['sr_out']
    s = filling(drop=.050)
    s.run(.15, fill_pressed=True)
    s.run(.030, estop_ch1=False, estop_ch2=False)
    s.run(.3, estop_ch1=True, estop_ch2=True)
    estop_glitch_restarts = s.outputs()['pump'] or s.outputs()['sr_out']
    check('An E-stop opening that trips the safety relay latches off until reset', not estop_glitch_restarts)
    s = filling(drop=.050)
    s.run(.15, fill_pressed=True)
    s.run(.005, reservoir_healthy=False)
    s.run(.05, reservoir_healthy=True)
    water_glitch_restarts = s.outputs()['pump']
    check('Model still exposes the short-interruption limit on water contacts', water_glitch_restarts)
    return {'fill_delay_combinations': combos, 'estop_30ms_opening_restarts_pump': estop_glitch_restarts,
            'estop_5ms_opening_filtered_by_safety_relay': estop_5ms_filtered,
            'water_contact_5ms_glitch_restarts_pump': water_glitch_restarts}


def stop_function():
    worst = {'power_removed_s': 0., 'tool_output_open_s': 0.}
    for (pick, drop), (kp, kd) in itertools.product(((.005, .005), (.010, .020), (.020, .050)), CONTACTOR_TIMING):
        for mode in ('router', 'plasma', 'setup', 'fill'):
            if mode in TOOL:
                s = running(mode, pick, drop, contactor_pickup=kp, contactor_dropout=kd)
                assert s.outputs()[TOOL[mode]]
            elif mode == 'fill':
                s = filling(pick, drop, contactor_pickup=kp, contactor_dropout=kd)
                s.run(.15, fill_pressed=True)
            else:
                s = started(pick, drop, contactor_pickup=kp, contactor_dropout=kd)
            s.inputs.update(estop_ch1=False, estop_ch2=False)
            t0, power_off, tool_off = s.time, None, None
            for _ in range(250):
                o = s.tick(.001)
                if power_off is None and not (o['motor_power'] or o['vfd_mains'] or o['plasma_mains']):
                    power_off = s.time - t0
                if tool_off is None and not (o['fwd_closed'] or o['start_closed']):
                    tool_off = s.time - t0
            o = s.outputs()
            check('E-stop removes 48 V, VFD mains and plasma mains', power_off is not None and not o['z_brake_released'] and not o['pump'],
                  mode=mode, pickup=pick, dropout=drop, contactor=(kp, kd), seconds=power_off)
            worst['power_removed_s'] = max(worst['power_removed_s'], power_off)
            if tool_off is not None:
                worst['tool_output_open_s'] = max(worst['tool_output_open_s'], tool_off)
            s.run(1., estop_ch1=True, estop_ch2=True)
            check('Released E-stop alone does not restore power', not s.outputs()['motor_power'] and not s.outputs()['sr_out'])
    s = started()
    s.run(.2, estop_ch1=False, estop_ch2=False)
    s.run(.2, reset_pressed=True)
    s.run(.3, estop_ch1=True, estop_ch2=True)
    check('Reset held through E-stop release does not restart (monitored reset)', not s.outputs()['sr_out'])
    s.run(.2, reset_pressed=False)
    check('Releasing that reset restarts, as a deliberate action', s.outputs()['sr_out'])
    for mode_name in ('monitored', 'level'):
        s = started(reset_mode=mode_name)
        s.run(.2, estop_ch1=False, estop_ch2=False)
        s.run(.2, reset_pressed=True)
        s.run(1., estop_ch1=True, estop_ch2=True)
        if mode_name == 'monitored':
            check('Stuck reset button never resets a monitored-reset unit', not s.outputs()['sr_out'])
        else:
            level_autorestart = s.outputs()['sr_out']
    s = started()
    s.run(.2, estop_ch1=False)
    check('One channel opening stops the machine', not s.outputs()['motor_power'])
    s.run(.2, estop_ch1=True)
    s.reset()
    check('Reset refused after a single-channel opening', not s.outputs()['sr_out'])
    s.run(.2, estop_ch1=False, estop_ch2=False)
    s.run(.2, estop_ch1=True, estop_ch2=True)
    s.reset()
    check('Opening both channels clears the lock', s.outputs()['sr_out'])
    welded_contactors = {}
    for k in ('K1', 'K2'):
        for stuck in (False, True):
            s = started()
            s.weld(f'{k}:1-2', stuck)
            s.run(.3, estop_ch1=False, estop_ch2=False)
            o = s.outputs()
            check('One welded contactor still leaves every power path open', not (o['motor_power'] or o['vfd_mains'] or o['plasma_mains']),
                  contactor=k, stuck=stuck)
            check('A welded contactor keeps the Z brake engaged', not o['z_brake_released'], contactor=k, stuck=stuck)
            s.run(.3, estop_ch1=True, estop_ch2=True)
            s.reset()
            welded_contactors[f'{k} stuck={stuck}'] = s.outputs()['sr_out']
            check('Reset refused while a contactor is welded (feedback loop open)', not s.outputs()['sr_out'], contactor=k, stuck=stuck)
    s = started()
    s.run(.2, estop_ch1=False, estop_ch2=False)
    s.run(.2, estop_ch1=True, estop_ch2=True)
    s.run(.1, reset_pressed=True)
    s.inputs['reset_pressed'] = False
    t_power = released_at = None
    for _ in range(900):
        o = s.tick(.005)
        if t_power is None and o['motor_power']:
            t_power = s.time
        if released_at is None and o['z_brake_released']:
            released_at = s.time - t_power
    check('Z brake releases only after the 3 s delay from power return', released_at is not None and released_at >= 2.995, seconds=released_at)
    s = running('plasma', holds_request=True)
    s.run(.3, estop_ch1=False, estop_ch2=False)
    s.run(.3, estop_ch1=True, estop_ch2=True)
    s.reset()
    s.run(12.4)
    check('Request held through a stop and reset cannot restart the torch', not s.outputs()['torch_run'])
    s = running('router')
    s.run(.3, estop_ch1=False, estop_ch2=False)
    s.run(.3, estop_ch1=True, estop_ch2=True)
    s.reset()
    s.run(75.4)
    o = s.outputs()
    check('After a stop the Rodent reboots with its request low', not o['router_run'] and not s.inputs['run_request'])
    return {'worst_modeled_power_removal_s': round(worst['power_removed_s'], 3),
            'worst_modeled_tool_output_open_s': round(worst['tool_output_open_s'], 3),
            'z_brake_release_after_power_s': round(released_at, 3),
            'level_reset_with_stuck_button_restarts': level_autorestart,
            'reset_with_welded_contactor': welded_contactors}


def race(sim_factory):
    """Change mode with the start signal held. Returns wrong-tool hits per direction/variant."""
    variants = ('bed key and water unchanged', 'bed key and water also switched')
    result = {}
    for src, dst in (('router', 'plasma'), ('plasma', 'router')):
        tally = {v: [0, 0, 0] for v in variants}
        for pick, drop in itertools.product(PICKUPS, DROPOUTS):
            base = sim_factory(src, pick, drop)
            for variant, off_ms in itertools.product(variants, (0, 10, 30, 60, 150, 300)):
                s = deepcopy(base)
                key = TOOL[dst]
                wrong = 0
                s.inputs[src] = False
                if variant.endswith('switched'):
                    s.inputs.update({k: v for k, v in (PLASMA if dst == 'plasma' else ROUTER).items() if k != dst})
                for _ in range(off_ms):
                    wrong += bool(s.tick(.001)[key])
                s.inputs[dst] = True
                for _ in range(600):
                    wrong += bool(s.tick(.001)[key])
                t = tally[variant]
                t[1] += 1
                if wrong:
                    t[0] += 1
                    t[2] = max(t[2], wrong)
        for variant, (hits, total, worst) in tally.items():
            result[f'{src} -> {dst}, {variant}'] = {'cases_with_wrong_tool': hits, 'cases': total, 'longest_ms': worst}
    return result


def gm1_running(mode, pick, drop):
    return running(mode, pick, drop)


def rev_i_running(mode, pick, drop):
    s = gm1.rev_i.Simulator(pick, drop)
    s.run(75.4 if mode == 'router' else 12.4, setup=False, run_request=False, **(ROUTER if mode == 'router' else PLASMA))
    s.run(.3, run_request=True)
    assert s.outputs()[TOOL[mode]]
    return s


def mode_race():
    gm1_result = race(gm1_running)
    rev_i_result = race(rev_i_running)
    for name, r in gm1_result.items():
        check('Changing mode with the start held never fires the other tool: ' + name, r['cases_with_wrong_tool'] == 0, **r)
    check('The same test finds the race in the Rev I circuit', any(r['cases_with_wrong_tool'] for r in rev_i_result.values()))
    s = running('router')
    s.run(.3, router=False)
    s.run(13., plasma=True, **{k: v for k, v in PLASMA.items() if k != 'plasma'})
    check('After a mode change the new tool still needs a fresh request', not s.outputs()['torch_run'])
    s.run(.3, run_request=False)
    s.run(.3, run_request=True)
    check('A fresh request then starts the new tool', s.outputs()['torch_run'])
    return {'gm1': gm1_result, 'rev_i_same_test': rev_i_result}


def weld_faults():
    """Weld each NO contact of each start-chain relay, one at a time, in both modes."""
    bases = {mode: running(mode) for mode in ('router', 'plasma')}
    rows = []
    for relay in gm1.TOOL_CHAIN:
        poles = sorted({e.tag for e in gm1.CONTACTS if e.tag.startswith(relay + ':') and not e.closed_when_control_false})
        for pole, stuck, mode in itertools.product(poles, (False, True), ('router', 'plasma')):
            key = TOOL[mode]
            row = {'relay': relay, 'pole': pole, 'stuck': stuck, 'mode': mode}
            s = deepcopy(bases[mode])
            s.weld(pole, stuck)
            s.run(.3, run_request=False)
            row['stops_on_controller_command'] = not s.outputs()[key]
            s = deepcopy(bases[mode])
            s.weld(pole, stuck)
            s.run(.3, breakaway_seated=False)
            row['stops_on_permission_loss'] = not s.outputs()[key]
            s.run(.6, breakaway_seated=True)
            row['no_restart_with_request_held'] = not s.outputs()['router_run'] and not s.outputs()['torch_run']
            s.run(.3, run_request=False)
            s.run(.6, setup=True)
            s.run(.6, run_request=True)
            row['no_start_in_setup'] = not s.outputs()['router_run'] and not s.outputs()['torch_run']
            s.run(.3, run_request=False)
            s.run(1., setup=False)
            row['arms_again'] = s.outputs()['armed']
            s.run(.3, run_request=True)
            row['tool_after_fresh_request'] = s.outputs()[key]
            rows.append(row)
            check('Single weld never starts a tool in SETUP', row['no_start_in_setup'], **row)
            check('Single weld never restarts a tool without a fresh request', row['no_restart_with_request_held'], **row)
            check('Single weld: the Rodent can still stop the tool', row['stops_on_controller_command'], **row)
    shorts = []
    for mode in ('router', 'plasma'):
        idle = deepcopy(bases[mode])
        idle.run(.3, run_request=False)
        assert idle.outputs()['armed']
        for e in gm1.CONTACTS:
            if e.tag.split(':')[0] not in gm1.TOOL_CHAIN and not e.tag.startswith('SETUP_RUN_B'):
                continue
            s = deepcopy(idle)
            s.failed_closed.add(e.tag)
            s.run(.6)
            ok = not s.outputs()['router_run'] and not s.outputs()['torch_run']
            shorts.append({'mode': mode, 'shorted': e.tag, 'no_start_without_request': ok})
            check('A single shorted start-chain contact never starts a tool without a request', ok, mode=mode, shorted=e.tag)
    setup_shorts = 0
    for mode in ('router', 'plasma'):
        s0 = deepcopy(bases[mode])
        s0.run(.3, run_request=False)
        s0.run(.6, setup=True)
        for e in gm1.CONTACTS:
            if e.tag.split(':')[0] not in gm1.TOOL_CHAIN and not e.tag.startswith(('SETUP_RUN', 'IF_RUN')):
                continue
            s = deepcopy(s0)
            s.failed_closed.add(e.tag)
            s.run(.6, run_request=True)
            setup_shorts += 1
            check('A single shorted start-chain contact never starts a tool in SETUP, even with a request',
                  not s.outputs()['router_run'] and not s.outputs()['torch_run'], mode=mode, shorted=e.tag)
    s = deepcopy(bases['plasma'])
    s.failed_closed.add('IF_RUN:13-14')
    s.run(.3, run_request=False)
    output_stage_short_keeps_torch = s.outputs()['torch_run']
    s.run(.6, setup=True)
    check('A shorted run-request output stage cannot run a tool in SETUP', not s.outputs()['torch_run'] and not s.outputs()['router_run'])
    s.run(.6, setup=False)
    s.run(.3, estop_ch1=False, estop_ch2=False)
    check('A shorted run-request output stage is still stopped by the E-stop', not s.outputs()['torch_run'])
    detected = sorted({(r['relay'], r['pole']) for r in rows if not r['arms_again']})
    masked = sorted({(r['relay'], r['pole']) for r in rows if r['arms_again']})
    return {'weld_cases': len(rows), 'short_cases': len(shorts), 'setup_short_cases': setup_shorts, 'rows': rows,
            'welds_that_block_the_next_arming': [f'{a} {b}' for a, b in detected],
            'welds_covered_by_another_channel_instead': [f'{a} {b}' for a, b in masked],
            'run_output_stage_short_keeps_torch_after_request_drops': output_stage_short_keeps_torch}


def rev_i_weld_cases():
    """The review's welded-contact cases, re-run on the Rev I simulator for comparison."""
    out = {}
    s = rev_i_running('plasma', .01, .02)
    s.failed_closed.add('K_REQUEST:21-24')
    s.run(.3, run_request=False)
    out['K_REQUEST:21-24 welded, request dropped: torch still on'] = s.outputs()['torch_run']
    s = rev_i_running('plasma', .01, .02)
    s.failed_closed.add('K_RUN_ARM:21-24')
    s.run(.3, door_closed=False)
    s.run(.3, door_closed=True)
    out['K_RUN_ARM:21-24 welded, door cycled with request held: torch restarts'] = s.outputs()['torch_run']
    s = rev_i_running('plasma', .01, .02)
    s.failed_closed.add('KM_R:31-34')
    s.run(.3, run_request=False)
    s.run(.3, run_request=True)
    out['KM_R:31-34 welded in plasma mode: spindle starts with the torch'] = s.outputs()['router_run']
    return out


def door_input():
    s = started()
    check('Door input closed in SETUP with no request', s.outputs()['door_ok'])
    s.run(5., setup=False, **ROUTER)
    s.run(.3, run_request=True)
    check('Request before the machine is ready opens the door input (grblHAL holds)', not s.outputs()['door_ok'])
    s.run(.3, run_request=False)
    s.run(75.)
    s.run(.3, run_request=True)
    check('Armed and requested: door input closed, spindle runs', s.outputs()['door_ok'] and s.outputs()['router_run'])


def router_drain():
    """M9: the drain closes after the router dwell and reopens only when needed."""
    rows = {}
    for pick, drop in itertools.product(PICKUPS, DROPOUTS):
        s = started(pick, drop)
        s.run(1., setup=False, **ROUTER)
        check('Router mode opens the pan drain', s.outputs()['drain'], pickup=pick, dropout=drop)
        s.run(73.9)
        o = s.outputs()
        check('The drain stays open through the 75 s dwell', o['drain'] and not o['ready'], pickup=pick, dropout=drop)
        s.run(.5)
        o = s.outputs()
        check('After the dwell the drain closes and the router is ready', not o['drain'] and o['ready'] and o['router_drained'],
              pickup=pick, dropout=drop)
        s.run(60.)
        o = s.outputs()
        check('The drain stays closed and ready holds while router mode stays selected', not o['drain'] and o['ready'])
        s.run(.3, run_request=True)
        check('The spindle runs with the drain closed', s.outputs()['router_run'] and not s.outputs()['drain'])
        s.run(.3, run_request=False)
        s.run(.3, empty=False)
        o = s.outputs()
        check('Liquid at the empty float drops router ready and reopens the drain', o['drain'] and not o['ready'] and not o['router_drained'],
              pickup=pick, dropout=drop)
        s.run(.3, empty=True)
        check('The reopened drain waits for a new dwell', s.outputs()['drain'] and not s.outputs()['ready'])
        s.run(75.2)
        o = s.outputs()
        check('After the new dwell the drain closes again with router ready', not o['drain'] and o['ready'], pickup=pick, dropout=drop)
        rows[f'{pick}/{drop}'] = True
    s = started()
    s.run(76., setup=False, **ROUTER)
    s.run(.3, estop_ch1=False, estop_ch2=False)
    o = s.outputs()
    check('An E-stop in router mode leaves the drain closed', not o['drain'] and not o['ready'] and o['router_drained'])
    s.run(.3, estop_ch1=True, estop_ch2=True)
    s.reset()
    s.run(.5)
    o = s.outputs()
    check('After the reset the router is ready again without a new dwell', o['ready'] and not o['drain'])
    s.run(.3, drain_override=True)
    o = s.outputs()
    check('DRAIN override opens the drain and holds ready off', o['drain'] and not o['ready'])
    s.run(.3, drain_override=False)
    o = s.outputs()
    check('Releasing the override closes the drain and restores ready', not o['drain'] and o['ready'])
    s.run(.3, bed_locked=False)
    check('Unlocking the bed drops ready and keeps the drain closed', not s.outputs()['ready'] and not s.outputs()['drain'])
    s.run(.3, bed_locked=True)
    check('Relocking restores ready', s.outputs()['ready'])
    s.run(.5, router=False, plasma=True, bed_locked=False, bed_clear=True)
    o = s.outputs()
    check('Leaving router mode drops the latch; plasma mode keeps the drain closed', not o['router_drained'] and not o['drain'])
    s.run(12.4, minimum=True, empty=False)
    check('Plasma mode then readies as before', s.outputs()['ready'])
    s.run(.5, plasma=False, router=True, bed_locked=True, bed_clear=False, minimum=False)
    check('Returning to router mode with water in the pan opens the drain again', s.outputs()['drain'] and not s.outputs()['ready'])
    s.run(20., empty=True)
    check('... and the dwell restarts once the pan is empty', s.outputs()['drain'] and not s.outputs()['ready'])
    s.run(55.5)
    check('... then the drain closes with router ready', not s.outputs()['drain'] and s.outputs()['ready'])
    # A welded latch contact: the other faults stay visible or harmless.
    s = ready('router')
    s.weld('K_DRAINED:21-24', False)
    s.run(.3, router=False)
    s.run(.3, plasma=True, run_request=True, **{k: v for k, v in PLASMA.items() if k != 'plasma'})
    o = s.outputs()
    check('Welded K_DRAINED 21-24: the spindle cannot run in plasma mode', not o['router_run'])
    held = False
    for _ in range(int(11.5 / .005)):
        held |= s.tick(.005)['torch_run']
    check('Welded K_DRAINED 21-24: the torch still waits for the plasma water sequence', not held)
    s = started()
    s.weld('K_DRAINED:11-14', True)
    s.run(80., setup=False, **dict(ROUTER, empty=False))
    o = s.outputs()
    check('Stuck K_DRAINED: the drain cannot open, and the router never becomes ready with water in the pan (fault shows)',
          not o['drain'] and not o['ready'])
    return {'delay_combinations': len(rows), 'drain_dwell_s': 75,
            'behaviour': 'Drain open on entering router mode until the pan has been empty for 75 s, then closed for as long as router '
                         'mode stays selected and the pan stays empty. An E-stop keeps it closed; DRAIN override opens it while held.'}


def fill_watchdog():
    """M10: an unattended fill stops at T_FILL. Simulated with T_FILL = 20 s; the panel setting is 1.5 x the timed fill."""
    t_fill = 20.
    for pick, drop in itertools.product(PICKUPS, DROPOUTS):
        s = filling(pick, drop, t_fill=t_fill)
        s.run(.15, fill_pressed=True)
        s.run(.15, fill_pressed=False)
        s.run(t_fill - .6)
        check('An unattended fill runs until the watchdog time', s.outputs()['pump'], pickup=pick, dropout=drop)
        s.run(.6)
        o = s.outputs()
        check('The fill watchdog stops a fill that never reaches the fill-stop float', not o['pump'] and not o['fill'],
              pickup=pick, dropout=drop)
        s.run(2.)
        check('... and the pump stays off', not s.outputs()['pump'])
        s.run(.15, fill_pressed=True)
        check('A new FILL press starts a new fill period', s.outputs()['pump'])
        s.run(.15, fill_pressed=False)
        s.run(5.)
        check('The new period runs self-held', s.outputs()['pump'])
        s.run(.15, fill_stop_healthy=False)
        check('The fill-stop float still ends a normal fill', not s.outputs()['pump'])
    s = filling(t_fill=t_fill)
    s.run(t_fill + 5., fill_pressed=True)
    check('Holding FILL keeps the pump running past the watchdog (attended)', s.outputs()['pump'])
    s.run(.3, fill_pressed=False)
    check('Releasing FILL after the watchdog time stops the pump', not s.outputs()['pump'])
    s = filling()
    s.run(.15, fill_pressed=True)
    s.run(.15, fill_pressed=False)
    s.run(600.)
    check('With the 25 min setting a normal fill is not cut short at 10 min', s.outputs()['pump'])
    return {'simulated_setting_s': t_fill, 'panel_setting': '25 min until the first fill is timed; then 1.5 x the measured fill time',
            'pump_open_flow_l_min': 7, 'expected_fill_80_l_min': [13, 18]}


def float_stop():
    """M11: the float switch in the head loop (modeled as the breakaway_seated input)."""
    for pick, drop in itertools.product(PICKUPS, DROPOUTS):
        s = running('plasma', pick, drop)
        s.run(.1, breakaway_seated=False)
        o = s.outputs()
        check('A float trip while cutting stops the torch', not o['torch_run'], pickup=pick, dropout=drop)
        check('A float trip while cutting opens the Rodent door input (feed hold)', not o['door_ok'], pickup=pick, dropout=drop)
        s = ready('plasma', pick, drop)
        s.run(.2, breakaway_seated=False)
        check('A float trip while probing (no request) keeps the door input closed', s.outputs()['door_ok'], pickup=pick, dropout=drop)
        s.run(.15, breakaway_seated=True)
        check('The chain re-arms within 150 ms of the float returning', s.outputs()['armed'], pickup=pick, dropout=drop)
        s.run(.3, run_request=True)
        check('The torch then starts on the next request', s.outputs()['torch_run'], pickup=pick, dropout=drop)


def spindle_reverse():
    """M12: the direction relay chooses FWD or REV; the run chain still starts and stops the spindle."""
    rows = []
    for pick, drop in itertools.product(PICKUPS, DROPOUTS):
        s = running('router', pick, drop)
        o = s.outputs()
        check('M3: the run command reaches FWD only', o['fwd_closed'] and not o['rev_closed'] and o['router_run'],
              pickup=pick, dropout=drop)
        s.run(.1, spindle_reverse=True)
        o = s.outputs()
        check('M4: the run command reaches REV only', o['rev_closed'] and not o['fwd_closed'] and o['router_run'],
              pickup=pick, dropout=drop)
        check('M4: the direction status input reports REV', o['direction_status_rev'], pickup=pick, dropout=drop)
        s.run(.3, run_request=False)
        check('M4: dropping the request stops the spindle', not s.outputs()['router_run'], pickup=pick, dropout=drop)
        s.run(.1, spindle_reverse=False)
        s.run(.3, run_request=True)
        o = s.outputs()
        check('Back to M3: FWD only again', o['fwd_closed'] and not o['rev_closed'], pickup=pick, dropout=drop)
    # FWD and REV never both closed: every direction, request and K_DIR weld, in both modes.
    for mode, reverse, request, weld in itertools.product(('router', 'plasma'), (False, True), (False, True),
                                                          (None, ('K_DIR:13-14', True), ('K_DIR:13-14', False))):
        s = running(mode)
        if weld:
            s.weld(*weld)
        s.run(.2, spindle_reverse=reverse, run_request=request)
        o = s.outputs()
        rows.append({'mode': mode, 'reverse': reverse, 'request': request, 'weld': weld and weld[0], 'stuck': weld and weld[1],
                     'fwd': o['fwd_closed'], 'rev': o['rev_closed']})
        check('FWD and REV are never both closed', not (o['fwd_closed'] and o['rev_closed']), **rows[-1])
        check('Plasma mode never runs the spindle in either direction', mode == 'router' or not o['router_run'], **rows[-1])
    s = started()
    s.run(5., **ROUTER)
    s.run(75.4)
    s.run(.3, spindle_reverse=True, run_request=True)
    check('SETUP: a reverse request cannot run the spindle', not s.outputs()['router_run'])
    s = running('router')
    s.weld('K_DIR:13-14', True)
    s.run(.2, spindle_reverse=False)
    welded_runs_reverse = s.outputs()['rev_closed']
    check('A welded K_DIR shows on the direction status input', s.outputs()['direction_status_rev'])
    return {'cases': len(rows), 'rows': rows, 'welded_k_dir_runs_reverse_on_m3': welded_runs_reverse,
            'note': 'A welded K_DIR runs the spindle in reverse on M3; the tool-change macro reads XM:8 before every start.'}


def tool_changer_drive():
    """M13: the dock motor runs only with the stop healthy, the spindle run relay released and a command."""
    DOCK_OUT = dict(dock_run_cmd=True, dock_in_dir=False, dock_at_parked=False)
    for pick, drop in itertools.product(PICKUPS, DROPOUTS):
        s = ready('router', pick, drop)
        s.run(.1, **DOCK_OUT)
        o = s.outputs()
        check('Command out: the dock moves out, not in', o['dock_out'] and not o['dock_in'], pickup=pick, dropout=drop)
        s.run(.02, dock_at_deployed=True)
        check('The deployed end switch stops it with the command held', not s.outputs()['dock_out'], pickup=pick, dropout=drop)
        s.run(.1, dock_in_dir=True)
        s.run(.02, dock_at_deployed=False)
        o = s.outputs()
        check('Command in: the dock moves in, not out', o['dock_in'] and not o['dock_out'], pickup=pick, dropout=drop)
        s.run(.02, dock_at_parked=True)
        check('The parked end switch stops it', not s.outputs()['dock_in'], pickup=pick, dropout=drop)
        s = ready('router', pick, drop)
        s.run(.1, **DOCK_OUT)
        s.run(.3, run_request=True)
        o = s.outputs()
        check('A spindle start stops a moving dock', o['router_run'] and not o['dock_out'] and not o['dock_in'],
              pickup=pick, dropout=drop)
        s = running('router', pick, drop)
        s.run(.1, **DOCK_OUT)
        check('The dock cannot move while the spindle runs', not s.outputs()['dock_out'], pickup=pick, dropout=drop)
        for reverse in (False, True):
            s = running('router', pick, drop)
            s.run(.1, spindle_reverse=reverse)
            s.run(.1, **DOCK_OUT)
            check('The dock cannot move while the spindle runs, either direction', not s.outputs()['dock_out'],
                  pickup=pick, dropout=drop, reverse=reverse)
    for stuck in (False, True):
        s = running('router')
        s.weld('K_VFD_RUN:13-14', stuck)
        s.run(.3, run_request=False)
        s.run(.1, **DOCK_OUT)
        check('A welded K_VFD_RUN keeps the dock from moving', not s.outputs()['dock_out'], stuck=stuck)
    s = ready('router')
    s.run(.1, **DOCK_OUT)
    s.run(.3, estop_ch1=False, estop_ch2=False)
    check('An E-stop stops a moving dock', not s.outputs()['dock_out'] and not s.outputs()['dock_in'])
    # M14: the Z top switch in the dock feed.
    for pick, drop in itertools.product(PICKUPS, DROPOUTS):
        s = ready('router', pick, drop)
        s.run(.1, z_at_top=False, **DOCK_OUT)
        o = s.outputs()
        check('With Z below its top the dock does not move, whatever is commanded', not o['dock_out'] and not o['dock_in'],
              pickup=pick, dropout=drop)
        s.run(.1, dock_in_dir=True)
        check('Nor in the other direction', not s.outputs()['dock_in'], pickup=pick, dropout=drop)
        s = ready('router', pick, drop)
        s.run(.1, **DOCK_OUT)
        check('At the top it moves', s.outputs()['dock_out'], pickup=pick, dropout=drop)
        s.run(.05, z_at_top=False)
        check('Z leaving the top stops a moving dock at once', not s.outputs()['dock_out'], pickup=pick, dropout=drop)
    for stuck in (False, True):
        s = ready('router')
        s.run(.1, z_at_top=False, **DOCK_OUT)
        s.weld('K_DOCK_RUN:11-14', stuck)
        s.run(.1)
        check('A welded K_DOCK_RUN still cannot move the dock with Z below its top', not s.outputs()['dock_out'], stuck=stuck)
    s = started()
    s.run(5., **ROUTER)
    s.run(.1, **DOCK_OUT)
    check('SETUP (bed change): the dock can move with the spindle off', s.outputs()['dock_out'])
    s = ready('router')
    s.weld('K_DOCK_RUN:11-14', True)
    s.run(.1, dock_run_cmd=False, dock_in_dir=False, dock_at_parked=False)
    runs_on = s.outputs()['dock_out']
    s.run(.02, dock_at_deployed=True)
    check('A welded K_DOCK_RUN still stops at the end switch', not s.outputs()['dock_out'], runs_until_end=runs_on)
    s = ready('router')
    s.run(.1, dock_run_cmd=True, dock_in_dir=True, dock_at_parked=False, dock_at_deployed=False)
    s.run(.1, dock_in_dir=False)
    s.run(.1, dock_in_dir=True)
    o = s.outputs()
    check('Direction changes never drive both directions', not (o['dock_out'] and o['dock_in']))
    return {'note': 'The motor is modeled as one load per direction. Pole 2 of each relay (the motor 0 V and the second '
                    'polarity pole) and the end-switch back-off diodes are wiring details in the README, not simulated.'}


def main():
    start = time.monotonic()
    gm1.write_netlist(OUT)
    report = {'scope': __doc__.strip(), 'changes': [dict(id=i, topic=t, change=c) for i, t, c in gm1.CHANGES]}
    structure()
    report['rev_i_behaviors'] = rev_i_behaviors()
    print('rev i behaviors', len(CHECKS), flush=True)
    report['stop_function'] = stop_function()
    print('stop', len(CHECKS), flush=True)
    report['mode_race'] = mode_race()
    print('race', json.dumps(report['mode_race']), flush=True)
    report['welded_contacts'] = weld_faults()
    report['rev_i_welded_contact_cases'] = rev_i_weld_cases()
    print('welds', report['welded_contacts']['weld_cases'], report['rev_i_welded_contact_cases'], flush=True)
    door_input()
    report['router_drain'] = router_drain()
    print('router drain', len(CHECKS), flush=True)
    report['fill_watchdog'] = fill_watchdog()
    float_stop()
    print('watchdog and float', len(CHECKS), flush=True)
    report['spindle_reverse'] = spindle_reverse()
    report['tool_changer_drive'] = tool_changer_drive()
    print('reverse and dock', len(CHECKS), flush=True)
    report['simulation_assumptions'] = {
        'relay_pickup_s': list(PICKUPS), 'relay_dropout_s': list(DROPOUTS), 'contactor_pickup_dropout_s': [list(c) for c in CONTACTOR_TIMING],
        'safety_relay_on_s': .050, 'safety_relay_off_s': .020, 'reset_min_press_s': .030, 'timer_recovery_s': .100,
        'controller_boot_s': 2.0, 'z_brake_delay_s': 3.0, 'photomos_on_off_s': [.005, .0005],
        'weld_semantics': 'A welded NO stays closed. Force-guided relays and contactor mirror contacts hold every NC of that relay open. '
                          'stuck=True also keeps the relay\'s other NO contacts closed; stuck=False lets them follow the coil. '
                          'Ordinary relays with stuck=False let their NC contacts reclose with the coil (worst case).'}
    report['limits'] = [
        'A model of the connection graph with assumed delays, not a measurement. Record real relay, contactor and safety-relay times at commissioning.',
        'The safety relay is modeled by its function (two channels, discrepancy lock, reset through the feedback loop). '
        'Its terminal numbers, cross-short detection, reset type and response times come from the purchased unit\'s manual.',
        'No performance level or category is claimed. The run request still has one output stage (the Rodent pin and its PhotoMOS); '
        'if that stage shorts, the tool keeps running after the Rodent drops the request, and only the E-stop stops it.',
        'Water-contact glitches shorter than a relay dropout can still resume a held fill, as in Rev I.',
        'The float stop (M11) is modeled as the existing head-loop input; the float switch itself, its cam and the probe optocoupler are not simulated.',
        'Mains wiring, contactor and brake sizing, VFD and cutter interfaces, and EMC are specified in the README, not simulated.',
        'M12/M13: the VFD\'s behavior with FWD and REV, its direction-change ramp, the dock motor current and the dock sensors are '
        'not simulated. The dock is modeled only through its relays and end switches.']
    report['passed_checks'] = len(CHECKS)
    report['checks'] = CHECKS
    report['result'] = 'PASS' if all(c['passed'] for c in CHECKS) else 'FAIL'
    sources = [Path(__file__), OUT / 'gm1_circuit.py', REV_I_SOURCE]
    report['source_sha256'] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    report['artifact_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (OUT / 'gm1-terminal-netlist.json', OUT / 'GM1-TERMINALS.md')}
    report['elapsed_s'] = round(time.monotonic() - start, 1)
    (OUT / 'gm1-circuit-verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(report['result'], report['passed_checks'], 'checks', report['elapsed_s'], 's', flush=True)


if __name__ == '__main__':
    sys.exit(main())
