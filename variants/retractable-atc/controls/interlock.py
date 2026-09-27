"""Offline executable retractable-dock contract; NEVER communicates with a machine.

Inputs are conditioned snapshots, not trusted Boolean settings. A future firmware
adapter must provide the timestamps, leases, completed pulse counts and feedback.
No M6, GPIO driver, motor scheduler or certified safety logic is implemented here.
"""
from dataclasses import dataclass
from enum import Enum
import math


class State(str, Enum):
    BOOT = 'BOOT_UNKNOWN'
    PARKED = 'PARKED_LOCKED'
    STOP = 'WAIT_STOP'
    RELEASE_OPEN = 'RELEASE_SHUTTER_CATCH_TO_OPEN'
    OPEN = 'OPEN_SHUTTER'
    CAPTURE_OPEN = 'CAPTURE_SHUTTER_OPEN'
    UNLOCK_OUT = 'UNLOCK_PARK'
    OUT = 'DEPLOY'
    LOCK_OUT = 'LOCK_DEPLOYED'
    READY = 'ATC_READY'
    TOOL = 'TOOL_CYCLE'
    STOP_AFTER = 'WAIT_STOP_AFTER_TOOL'
    CLEAR = 'WAIT_AXIS_CLEAR'
    UNLOCK_IN = 'UNLOCK_DEPLOYED'
    IN = 'RETRACT'
    LOCK_IN = 'LOCK_PARKED'
    RELEASE_CLOSE = 'RELEASE_SHUTTER_CATCH_TO_CLOSE'
    CLOSE = 'CLOSE_SHUTTER'
    CAPTURE_CLOSED = 'CAPTURE_SHUTTER_CLOSED'
    FAULT = 'FAULT_LATCHED'


@dataclass(frozen=True)
class Config:
    # Deliberately false in the delivered candidate. Tests opt into a simulated
    # qualified fixture; changing a Boolean is NOT hardware qualification.
    qualified_fixture: bool = False
    stroke_mm: float = 200.0
    shutter_mm: float = 164.0
    machine_variant: str = 'large'
    slide_speed_mm_s: float = 10.0
    shutter_speed_mm_s: float = 10.0
    input_max_age_ms: int = 50
    stop_dwell_ms: int = 300
    feedback_dwell_ms: int = 30
    motion_timeout_ms: int = 30000
    shutter_timeout_ms: int = 25000
    lock_timeout_ms: int = 3000
    stop_timeout_ms: int = 15000
    spinup_feedback_timeout_ms: int = 1500
    tool_timeout_ms: int = 120000

    def __post_init__(self):
        # No smaller-machine fallback: it has no selected independent shutter.
        if self.machine_variant != 'large':
            raise ValueError('UNAVAILABLE_MACHINE_PROFILE: small cover mechanism is unselected')
        if self.stroke_mm != 200.0 or self.shutter_mm != 164.0:
            raise ValueError('GEOMETRY_PROFILE_MISMATCH: large slide 200 mm, shutter 164 mm')


@dataclass(frozen=True)
class Inputs:
    sequence: int
    sampled_ms: int
    bus_ok: bool = True
    config_readback_ok: bool = True
    control_power: bool = True
    hardware_permission: bool = True
    router_mode: bool = True
    dock_present: bool = True
    driver_ok: bool = True
    parked: bool = True
    deployed: bool = False
    park_pin_extended: bool = True
    park_pin_retracted: bool = False
    deploy_pin_extended: bool = True
    deploy_pin_retracted: bool = False
    shutter_open: bool = False
    shutter_closed: bool = True
    shutter_catch_extended: bool = True
    shutter_catch_retracted: bool = False
    # Separate kit lid remains unverified; tests supply explicit confirmations.
    kit_cover_open: bool = False
    kit_cover_closed: bool = True
    spindle_stopped: bool = True
    spindle_running: bool = False
    spindle_feedback_ms: int = 0
    axis_homed: bool = True
    axis_idle: bool = True
    pose_epoch: int = 1
    axis_clear: bool = True
    axis_clear_epoch: int = 1
    axis_clear_ms: int = 0
    toolpath_lease: bool = False
    toolpath_session: int = 0
    ir_ok: bool = True
    # Completed pulse counter, NOT encoder/physical travel. Starts at known park
    # only after inspected reset; adapter must not equate steps with clearance.
    slide_mm: float = 0.0
    shutter_position_mm: float = 0.0

    @property
    def lock_engaged(self):
        # Extension of a pin away from its receiver is NOT engagement evidence.
        return ((self.parked and not self.deployed and self.park_pin_extended and not self.park_pin_retracted)
                or (self.deployed and not self.parked and self.deploy_pin_extended and not self.deploy_pin_retracted))

    @property
    def lock_retracted(self):
        return (self.park_pin_retracted and self.deploy_pin_retracted
                and not self.park_pin_extended and not self.deploy_pin_extended)


@dataclass(frozen=True)
class Command:
    acknowledge: bool = False
    recover_inspected: bool = False
    start_change: bool = False
    begin_tool: bool = False
    tool_done: bool = False
    spindle_request: bool = False
    abort: bool = False


@dataclass(frozen=True)
class Outputs:
    state: State
    slide_velocity: float = 0.0
    shutter_velocity: float = 0.0
    unlock: bool = False
    shutter_catch_release: bool = False
    kit_cover_action: str = 'HOLD'
    spindle_gate: bool = False
    allow_toolpath: bool = False
    session: int = 0
    fault: str = ''
    slide_target_mm: float | None = None
    shutter_target_mm: float | None = None


class Dock:
    def __init__(self, config=Config()):
        self.c = config
        self.state = State.BOOT
        self.enter_ms = 0
        self.last_ms = -1
        self.last_sequence = -1
        self.stop_since = None
        self.condition_since = None
        self.pose_lease = None
        self.session = 0
        self.fault = ''
        self.prev = Command()
        self.seen_running = False
        self.request_since = None
        self.tool_was_requested = False
        self.pending_done = False

    def _to(self, state, now):
        self.state, self.enter_ms = state, now
        self.condition_since = None

    def _fault(self, reason, now):
        self.fault = reason
        self.pose_lease = None
        self.stop_since = None
        self._to(State.FAULT, now)

    def _stable(self, condition, now, ms):
        if not condition:
            self.condition_since = None
            return False
        if self.condition_since is None:
            self.condition_since = now
        return now - self.condition_since >= ms

    def _clear(self, x, now):
        return (x.axis_homed and x.axis_idle and x.axis_clear and
                x.axis_clear_epoch == x.pose_epoch and
                0 <= now - x.axis_clear_ms <= self.c.input_max_age_ms)

    def step(self, now, x, cmd=Command()):
        c = self.c
        numbers=(now,x.sampled_ms,x.spindle_feedback_ms,x.axis_clear_ms,
                 x.slide_mm,x.shutter_position_mm)
        if (not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in numbers)
                or not isinstance(x.sequence,int) or isinstance(x.sequence,bool) or x.sequence<0):
            self._fault('NONFINITE_OR_INVALID_NUMERIC_INPUT',max(self.last_ms,0))
            self.prev=cmd
            return Outputs(state=self.state,session=self.session,fault=self.fault)
        rising_ack = cmd.acknowledge and not self.prev.acknowledge
        rising_start = cmd.start_change and not self.prev.start_change
        rising_begin = cmd.begin_tool and not self.prev.begin_tool
        rising_done = cmd.tool_done and not self.prev.tool_done
        fresh = (x.bus_ok and x.config_readback_ok and x.sequence > self.last_sequence
                 and 0 <= now-x.sampled_ms <= c.input_max_age_ms and now > self.last_ms)
        self.last_sequence, self.last_ms, self.prev = x.sequence, now, cmd
        bad = None
        if not fresh: bad = 'STALE_OR_INVALID_IO'
        elif not x.control_power: bad = 'CONTROL_POWER_LOST'
        elif not x.hardware_permission: bad = 'HARDWARE_PERMISSION_LOST'
        elif not x.driver_ok: bad = 'DRIVER_FAULT'
        elif cmd.abort: bad = 'OPERATOR_ABORT'
        elif x.parked and x.deployed: bad = 'CONTRADICTORY_SLIDE_SWITCHES'
        elif x.park_pin_extended and x.park_pin_retracted: bad = 'CONTRADICTORY_PARK_PIN'
        elif x.deploy_pin_extended and x.deploy_pin_retracted: bad = 'CONTRADICTORY_DEPLOY_PIN'
        elif x.shutter_open and x.shutter_closed: bad = 'CONTRADICTORY_SHUTTER_SWITCHES'
        elif x.shutter_catch_extended and x.shutter_catch_retracted: bad = 'CONTRADICTORY_SHUTTER_CATCH'
        elif x.kit_cover_open and x.kit_cover_closed: bad = 'CONTRADICTORY_KIT_COVER'
        elif x.spindle_stopped and x.spindle_running: bad = 'CONTRADICTORY_SPINDLE_FEEDBACK'
        elif not x.dock_present: bad = 'DOCK_REMOVED'
        elif not 0<=x.slide_mm<=c.stroke_mm: bad = 'SLIDE_COUNTER_OUT_OF_RANGE'
        elif not 0<=x.shutter_position_mm<=c.shutter_mm: bad = 'SHUTTER_COUNTER_OUT_OF_RANGE'
        elif self.state not in (State.BOOT,State.PARKED,State.FAULT) and not x.router_mode:
            bad = 'MODE_CHANGED_DURING_CONVERSION'
        if bad: self._fault(bad, now)
        if self.state==State.OUT and x.slide_mm>=c.stroke_mm and not x.deployed:
            self._fault('SLIDE_DEPLOY_PULSE_BUDGET_EXHAUSTED',now)
        elif self.state==State.IN and x.slide_mm<=0 and not x.parked:
            self._fault('SLIDE_RETRACT_PULSE_BUDGET_EXHAUSTED',now)
        elif self.state==State.OPEN and x.shutter_position_mm>=c.shutter_mm and not x.shutter_open:
            self._fault('SHUTTER_OPEN_PULSE_BUDGET_EXHAUSTED',now)
        elif self.state==State.CLOSE and x.shutter_position_mm<=0 and not x.shutter_closed:
            self._fault('SHUTTER_CLOSE_PULSE_BUDGET_EXHAUSTED',now)

        # Check position/cover prerequisites BEFORE state transitions generate a
        # new command. Otherwise a lost park switch during WAIT_STOP could issue
        # one cycle of catch release before the next state's guard ran.
        must_park=(State.STOP,State.RELEASE_OPEN,State.OPEN,State.CAPTURE_OPEN,
                   State.UNLOCK_OUT,State.LOCK_IN,State.RELEASE_CLOSE,State.CLOSE,State.CAPTURE_CLOSED)
        must_deploy=(State.LOCK_OUT,State.READY,State.TOOL,State.STOP_AFTER,
                     State.CLEAR,State.UNLOCK_IN)
        must_park_lock=(State.STOP,State.RELEASE_OPEN,State.OPEN,State.CAPTURE_OPEN,
                        State.RELEASE_CLOSE,State.CLOSE,State.CAPTURE_CLOSED)
        must_capture=(State.UNLOCK_OUT,State.OUT,State.LOCK_OUT,State.READY,
                      State.TOOL,State.STOP_AFTER,State.CLEAR,State.UNLOCK_IN,
                      State.IN,State.LOCK_IN)
        if self.state in must_park and not (x.parked and not x.deployed):
            self._fault('REQUIRED_PARK_POSITION_LOST',now)
        elif self.state in must_deploy and not (x.deployed and not x.parked):
            self._fault('REQUIRED_DEPLOYED_POSITION_LOST',now)
        elif self.state in must_park_lock and not (x.park_pin_extended and not x.park_pin_retracted):
            self._fault('REQUIRED_PARK_LOCK_LOST',now)
        elif self.state in must_capture and not (x.shutter_open and not x.shutter_closed
                and x.shutter_catch_extended and not x.shutter_catch_retracted
                and x.kit_cover_open and not x.kit_cover_closed):
            self._fault('OPEN_CAPTURE_CONFIRMATION_LOST',now)

        fresh_stop = (fresh and 0 <= now-x.spindle_feedback_ms <= c.input_max_age_ms
                      and x.spindle_stopped and not x.spindle_running
                      and not cmd.spindle_request)
        if fresh_stop:
            if self.stop_since is None: self.stop_since = now
        else:
            self.stop_since = None
        stopped = self.stop_since is not None and now-self.stop_since >= c.stop_dwell_ms
        # A lease is invalidated by any axis motion/re-home/coordinate epoch change.
        moving_states = (State.RELEASE_OPEN,State.OPEN,State.CAPTURE_OPEN,
                         State.UNLOCK_OUT,State.OUT,State.LOCK_OUT,
                         State.UNLOCK_IN,State.IN,State.LOCK_IN,State.RELEASE_CLOSE,State.CLOSE,State.CAPTURE_CLOSED)
        if self.state in moving_states:
            if not self._clear(x,now) or self.pose_lease != x.pose_epoch:
                self._fault('AXIS_CLEAR_LEASE_INVALIDATED',now)
            elif not fresh_stop:
                self._fault('SPINDLE_NOT_STOPPED_FOR_MECHANISM',now)
        park_ok = (x.parked and not x.deployed and x.lock_engaged and
                   not x.lock_retracted and x.shutter_closed and not x.shutter_open
                   and x.kit_cover_closed and not x.kit_cover_open)
        closed_captured = x.shutter_catch_extended and not x.shutter_catch_retracted
        deployed_ok = (x.deployed and not x.parked and x.lock_engaged and
                       not x.lock_retracted and x.shutter_open and not x.shutter_closed
                       and x.shutter_catch_extended and not x.shutter_catch_retracted
                       and x.kit_cover_open and not x.kit_cover_closed)
        if self.state in (State.BOOT,State.FAULT):
            if (not bad and rising_ack and not cmd.start_change and not cmd.spindle_request
                    and c.qualified_fixture and park_ok and closed_captured and stopped and self._clear(x,now)
                    and (self.state == State.BOOT or cmd.recover_inspected)):
                self.fault=''
                self._to(State.PARKED,now)
        elif self.state == State.PARKED:
            if not (park_ok and closed_captured): self._fault('PARK_CONFIRMATION_LOST',now)
            elif rising_start:
                if not c.qualified_fixture or not x.router_mode or not self._clear(x,now):
                    self._fault('CHANGE_PREREQUISITE_MISSING',now)
                else:
                    self.session += 1
                    self.pose_lease = x.pose_epoch
                    self.stop_since = None  # fresh stop after spindle gate removal
                    self._to(State.STOP,now)
        elif self.state == State.STOP:
            if stopped and self._clear(x,now):
                self.pose_lease=x.pose_epoch
                self._to(State.RELEASE_OPEN,now)
        elif self.state in (State.RELEASE_OPEN,State.RELEASE_CLOSE):
            if not(x.parked and x.lock_engaged and not x.lock_retracted):
                self._fault('PARK_LOCK_LOST_AT_SHUTTER_RELEASE',now)
            elif self._stable(x.shutter_catch_retracted and not x.shutter_catch_extended,now,c.feedback_dwell_ms):
                self._to(State.OPEN if self.state==State.RELEASE_OPEN else State.CLOSE,now)
        elif self.state == State.OPEN:
            if not (x.parked and x.lock_engaged and not x.lock_retracted):
                self._fault('PARK_LOCK_LOST_WHILE_OPENING',now)
            elif not(x.shutter_catch_retracted and not x.shutter_catch_extended):
                self._fault('SHUTTER_CATCH_NOT_RELEASED',now)
            elif self._stable(x.shutter_open and not x.shutter_closed and
                              x.kit_cover_open and not x.kit_cover_closed and
                              x.shutter_position_mm >= c.shutter_mm-1, now,c.feedback_dwell_ms):
                self._to(State.CAPTURE_OPEN,now)
        elif self.state==State.CAPTURE_OPEN:
            if not(x.shutter_open and not x.shutter_closed):
                self._fault('SHUTTER_UPPER_POSITION_LOST',now)
            elif self._stable(x.shutter_catch_extended and not x.shutter_catch_retracted,now,c.feedback_dwell_ms):
                self._to(State.UNLOCK_OUT,now)
        elif self.state in (State.UNLOCK_OUT,State.UNLOCK_IN):
            if self._stable(x.lock_retracted and not x.lock_engaged,now,c.feedback_dwell_ms):
                self._to(State.OUT if self.state==State.UNLOCK_OUT else State.IN,now)
        elif self.state in (State.OUT,State.IN):
            if not (x.lock_retracted and not x.lock_engaged and x.shutter_open
                    and not x.shutter_closed and x.kit_cover_open and not x.kit_cover_closed):
                self._fault('MOTION_CLEARANCE_OR_UNLOCK_LOST',now)
            elif not(x.shutter_catch_extended and not x.shutter_catch_retracted):
                self._fault('SHUTTER_CAPTURE_LOST',now)
            elif self.state == State.OUT and x.deployed:
                if x.slide_mm < c.stroke_mm-1: self._fault('DEPLOYED_FEEDBACK_EARLY',now)
                elif self._stable(True,now,c.feedback_dwell_ms): self._to(State.LOCK_OUT,now)
            elif self.state == State.IN and x.parked:
                if x.slide_mm > 1: self._fault('PARKED_FEEDBACK_EARLY',now)
                elif self._stable(True,now,c.feedback_dwell_ms): self._to(State.LOCK_IN,now)
            else: self.condition_since=None
        elif self.state in (State.LOCK_OUT,State.LOCK_IN):
            pos_ok=x.deployed if self.state==State.LOCK_OUT else x.parked
            if not pos_ok: self._fault('END_POSITION_LOST_WHILE_LOCKING',now)
            elif self._stable(x.lock_engaged and not x.lock_retracted,now,c.feedback_dwell_ms):
                if self.state==State.LOCK_OUT: self._to(State.READY,now)
                else: self._to(State.RELEASE_CLOSE,now)
        elif self.state==State.READY:
            if not deployed_ok: self._fault('DEPLOYED_LOCK_OR_COVER_LOST',now)
            elif rising_begin:
                if not (x.toolpath_lease and x.toolpath_session==self.session and x.ir_ok and stopped):
                    self._fault('TOOLPATH_CONTRACT_MISSING',now)
                else:
                    self.seen_running=False
                    self.tool_was_requested=False
                    self.request_since=None
                    self.pending_done=False
                    self.pose_lease=None
                    self._to(State.TOOL,now)
        elif self.state==State.TOOL:
            if not deployed_ok or not x.ir_ok:
                self._fault('TOOL_CYCLE_FEEDBACK_LOST',now)
            elif not x.toolpath_lease or x.toolpath_session!=self.session:
                self._fault('TOOLPATH_LEASE_LOST',now)
            elif not 0<=now-x.spindle_feedback_ms<=c.input_max_age_ms:
                self._fault('SPINDLE_FEEDBACK_STALE',now)
            else:
                if cmd.spindle_request:
                    self.tool_was_requested=True
                    if self.request_since is None:self.request_since=now
                    if x.spindle_running and not x.spindle_stopped:self.seen_running=True
                    if not self.seen_running and now-self.request_since>c.spinup_feedback_timeout_ms:
                        self._fault('RUN_FEEDBACK_NEVER_CHANGED',now)
                if rising_done:
                    if cmd.spindle_request or not self.tool_was_requested or not self.seen_running:
                        self._fault('TOOL_COMPLETION_UNPROVEN',now)
                    else:
                        self.stop_since=None
                        self._to(State.STOP_AFTER,now)
        elif self.state==State.STOP_AFTER:
            if not deployed_ok: self._fault('DEPLOYED_LOCK_OR_COVER_LOST',now)
            elif stopped: self._to(State.CLEAR,now)
        elif self.state==State.CLEAR:
            if not deployed_ok: self._fault('DEPLOYED_LOCK_OR_COVER_LOST',now)
            elif stopped and self._clear(x,now):
                self.pose_lease=x.pose_epoch
                self._to(State.UNLOCK_IN,now)
        elif self.state==State.CLOSE:
            if not(x.parked and x.lock_engaged and not x.lock_retracted):
                self._fault('PARK_LOCK_LOST_WHILE_CLOSING',now)
            elif not(x.shutter_catch_retracted and not x.shutter_catch_extended):
                self._fault('SHUTTER_CATCH_NOT_RELEASED',now)
            elif self._stable(park_ok and x.shutter_position_mm<=1,now,c.feedback_dwell_ms):
                self._to(State.CAPTURE_CLOSED,now)
        elif self.state==State.CAPTURE_CLOSED:
            if not park_ok or x.shutter_position_mm>1:
                self._fault('CLOSED_POSITION_LOST_WHILE_CAPTURING',now)
            elif self._stable(closed_captured,now,c.feedback_dwell_ms):
                self._to(State.PARKED,now)

        limit = {State.STOP:c.stop_timeout_ms,State.STOP_AFTER:c.stop_timeout_ms,
                 State.OPEN:c.shutter_timeout_ms,State.CLOSE:c.shutter_timeout_ms,
                 State.UNLOCK_OUT:c.lock_timeout_ms,State.UNLOCK_IN:c.lock_timeout_ms,
                 State.RELEASE_OPEN:c.lock_timeout_ms,State.RELEASE_CLOSE:c.lock_timeout_ms,
                 State.CAPTURE_OPEN:c.lock_timeout_ms,State.CAPTURE_CLOSED:c.lock_timeout_ms,
                 State.LOCK_OUT:c.lock_timeout_ms,State.LOCK_IN:c.lock_timeout_ms,
                 State.OUT:c.motion_timeout_ms,State.IN:c.motion_timeout_ms,
                 State.TOOL:c.tool_timeout_ms}.get(self.state)
        if limit is not None and now-self.enter_ms>limit:
            self._fault('STATE_TIMEOUT_'+self.state.value,now)
        s=self.state
        # All outputs are recomputed after faults; no retained run/unlock command.
        off=s in (State.BOOT,State.FAULT)
        return Outputs(s,
            0 if off else (c.slide_speed_mm_s if s==State.OUT and not x.deployed else
                           -c.slide_speed_mm_s if s==State.IN and not x.parked else 0),
            0 if off else (c.shutter_speed_mm_s if s==State.OPEN and not x.shutter_open else
                           -c.shutter_speed_mm_s if s==State.CLOSE and not x.shutter_closed else 0),
            s in (State.UNLOCK_OUT,State.OUT,State.UNLOCK_IN,State.IN),
            s in (State.RELEASE_OPEN,State.OPEN,State.RELEASE_CLOSE,State.CLOSE),
            ('HOLD' if off or s in (State.PARKED,State.STOP) else
             'CLOSE' if s in (State.RELEASE_CLOSE,State.CLOSE,State.CAPTURE_CLOSED) else 'OPEN'),
            not off and x.router_mode and ((s==State.PARKED and park_ok and closed_captured) or
                         (s==State.TOOL and deployed_ok and x.ir_ok and x.toolpath_lease
                          and x.toolpath_session==self.session)),
            s==State.TOOL and deployed_ok and x.toolpath_lease and x.toolpath_session==self.session,
            self.session,self.fault,
            c.stroke_mm if s==State.OUT else 0.0 if s==State.IN else None,
            c.shutter_mm if s==State.OPEN else 0.0 if s==State.CLOSE else None)
