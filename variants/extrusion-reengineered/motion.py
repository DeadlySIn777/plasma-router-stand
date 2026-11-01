"""XR1 nominal motion integration; no supplier interfaces or CAM are released.

HGR20 seats directly on the inner 4080 faces. No long steel caps/datums.
This module builds review solids only and never exports or changes source files.
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import math
import sys

import cadquery as cq
import params as P

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'variants' / 'extrusion-wood-plasma'
SOURCE = ROOT / 'output' / 'release-review' / 'RevE-ENGINEERING'
for directory in (SOURCE, OLD):
    if str(directory) not in sys.path:
        sys.path.append(str(directory))
from motion_context import _bare_motion, _local_head, MOUNT_PATTERN
from cad_helpers import bbox, place, cyl, plate, rect

ALU = (.64, .71, .74)
STEEL = (.36, .40, .43)
HARDWARE = (.45, .47, .49)
OLD_BASE = 1063.9375
SADDLE_THICKNESS = 12.7
MODULE_BASE = P.UPPER_TOP + SADDLE_THICKNESS
MODULE_RISE = MODULE_BASE - OLD_BASE
GUIDE_Z = 1033.
SADDLE_STATIONS = (190., 700., 1100.)
PLASMA_DROP = 115. + 911. - P.SLAT_TOP
LINK_Z = 1154.7875
LINK_ANGLE_DEG = -math.degrees(math.atan2(MODULE_RISE, 80.))


def box(x, y, z, dx, dy, dz):
    return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x, y, z))


def cylinder(d, length, origin, direction=(0, 0, 1)):
    return cq.Solid.makeCylinder(d/2, length, cq.Vector(*origin), cq.Vector(*direction))


def mirrored(shape, left):
    return shape if left else shape.mirror('YZ', (575, 0, 0))


def _shift_side(name):
    """Outward X shift for guide/load-bearing parts, never the screw module."""
    for side, dx in (('L', -8.), ('R', 8.)):
        if name in ('Y_RAIL_'+side, 'Y_SHOE_'+side):
            return dx
        if name.startswith(tuple(prefix+side+'_' for prefix in
                ('Y_BLOCK_', 'Y_BLOCK_BOLT_', 'GANTRY_WEB_BOLT_',
                 'Y_LINK_BRACKET_', 'Y_LIMIT_', 'Y_BUFFER_', 'Y_STOP_', 'Y_CAM_'))):
            return dx
    return 0.


def _gantry_bracket(left, gantry_y):
    """Selected integral150x80x82.7 billet; web shifted8mmoutward.

    The user's selective-billet preference applies to the main gantry corner
    and clevises. No gussets, flange edge joints or long guide-face changes.
    """
    beam_y=gantry_y+80
    x0=-25 if left else 1025
    flange_x=(25,100) if left else(50,125)
    flange=plate(rect(150,80),12.7,[(x,y,8.5) for x in flange_x for y in(20,60)])
    for x in flange_x:
        for y in(20,60):flange=flange.cut(cyl(13.5,8).translate((x,y,0)))
    web_x=118.5 if left else 18.8
    s=flange.fuse(box(web_x,0,-70,12.7,80,70))
    for y in(15,65):
        for z in(-24,-54):s=s.cut(cylinder(6,15,(web_x-1,y,z),(1,0,0)))
    return s.clean().translate((x0,beam_y-40,1142.3))


def _link_support(left, gantry_y):
    """Two bolted flat parts; original fixed link/output height is preserved."""
    wx, webx, cx = 6.4, 93.5, 25.4
    wz = OLD_BASE+65.5
    flange = box(wx, gantry_y-61, wz, 99.8, 48, 6.35)
    web = box(webx, gantry_y-61, wz-40, 12.7, 48, 40)
    for x in (cx-19, cx+19):
        flange = flange.cut(cylinder(4, 8, (x, gantry_y-37, wz-1)))
    for y in (gantry_y-45, gantry_y-29):
        for dz in (10, 28):
            web = web.cut(cylinder(6, 10, (webx-1, y, wz-dz), (1, 0, 0)))
    result=[]; side='L' if left else 'R'
    for i,y in enumerate((gantry_y-55,gantry_y-19),1):
        flange=flange.cut(cylinder(5.5,8.35,(99.85,y,wz-1)))
        flange=flange.cut(cq.Solid.makeCone(5,2.75,2.8,cq.Vector(99.85,y,wz+6.35),cq.Vector(0,0,-1)))
        web=web.cut(cylinder(5,15,(99.85,y,wz-15)))
        screw=cylinder(5,17.2,(99.85,y,wz-13.65)).fuse(
            cq.Solid.makeCone(2.75,5,2.8,cq.Vector(99.85,y,wz+3.55),cq.Vector(0,0,1)))
        result.append((f'Y_LINK_SUPPORT_TOP_M5x20_{side}_{i}',mirrored(screw.clean(),left),HARDWARE))
    result.append((f'Y_LINK_SUPPORT_FLANGE_{side}',mirrored(flange.clean(),left),ALU))
    result.append((f'Y_LINK_SUPPORT_WEB_{side}',mirrored(web.clean(),left),ALU))
    return result


def _tilt_link(name, shape, gantry_y):
    """Tilt only rod/shank/coupler bodies; keep the two clevis soles horizontal."""
    side = 'L' if name.startswith('Y_LINK_L_') else 'R'
    cx = 25.4 if side == 'L' else 1124.6
    a = (cx, gantry_y-117, LINK_Z)
    b = (cx, gantry_y-37, LINK_Z)
    if '_A_' in name:
        if name.endswith(('_ROD_END', '_ROD_SHANK')):
            shape = shape.rotate(a, (cx+1, a[1], a[2]), LINK_ANGLE_DEG)
        return shape.translate((0, 0, MODULE_RISE))
    if '_B_' in name:
        if name.endswith(('_ROD_END', '_ROD_SHANK')):
            return shape.rotate(b, (cx+1, b[1], b[2]), LINK_ANGLE_DEG)
        return shape
    middle = (cx, gantry_y-77, LINK_Z)
    return shape.rotate(middle, (cx+1, middle[1], middle[2]), LINK_ANGLE_DEG).translate((0, 0, MODULE_RISE/2))



def _saddles():
    """Six side-access, two-piece saddles; all dimensions are candidate design.

    Bottom M4 attachment uses the published continuous slots, not invented
    factory hole pitches. Frame screws show external grip/head only: the real
    nut profile and screw-tip clearance remain measured interface holds.
    """
    out = []
    def add(n, s, c=ALU):
        out.append((n, s.clean(), c))
    for side, left in (('L', True), ('R', False)):
        for i, y in enumerate(SADDLE_STATIONS, 1):
            key = f'XR_SADDLE_{side}_{i}'
            # Inboard edge stops0.5mm before guide-seat face, avoiding the
            # upper2mm of the moving HGH block. Blank size remains70x60.
            pad = box(-19.7, y-30, P.UPPER_TOP, 70, 60, SADDLE_THICKNESS)
            # Centred bottom-slot separation28, from recovered HMS40 drawing.
            # These are selected sliding-nut stations, not supplier fixed holes.
            for x in (11.4, 39.4):
                pad = pad.cut(cylinder(4.5, 14.7, (x, y, P.UPPER_TOP-1)))
                pad = pad.cut(cylinder(7.5, 4, (x, y, P.UPPER_TOP)))
            for yy in (y-18, y+18):
                pad = pad.cut(cylinder(5.5, 14.7, (-.3625, yy, P.UPPER_TOP-1)))
            add(key+'_PAD_70x60x12p7', mirrored(pad, left))
            sideplate = box(-5.125, y-30, 973, 9.525, 60, 80)
            for yy in (y-18, y+18):
                for z in (993, 1033):
                    sideplate = sideplate.cut(cylinder(6.6, 12, (-6.125, yy, z), (1, 0, 0)))
                # Nominal tapped thread cylinder, not a drill-size instruction.
                sideplate = sideplate.cut(cylinder(5, 15, (-.3625, yy, 1038)))
            add(key+'_SIDE_60x80x9p525', mirrored(sideplate, left))
            for j, x in enumerate((11.4, 39.4), 1):
                screw = cylinder(4, 16, (x, y, 1057))
                screw = screw.fuse(cylinder(7, 4, (x, y, 1053)))
                add(key+f'_MODULE_M4x16_{j}', mirrored(screw, left), HARDWARE)
            for j, yy in enumerate((y-18, y+18), 1):
                screw = cylinder(5, 25, (-.3625, yy, 1040.7))
                screw = screw.fuse(cylinder(8.5, 5, (-.3625, yy, MODULE_BASE)))
                add(key+f'_EDGE_M5x25_{j}', mirrored(screw, left), HARDWARE)
                for k, z in enumerate((993, 1033), 1):
                    spacer = cylinder(12, 6.4, (4.4, yy, z), (1, 0, 0))
                    spacer = spacer.cut(cylinder(6.6, 8, (3.4, yy, z), (1, 0, 0)))
                    add(key+f'_SPACER_6p4_{j}_{k}', mirrored(spacer, left))
                    washer = cylinder(12, 1.6, (-6.725, yy, z), (1, 0, 0))
                    washer = washer.cut(cylinder(6.6, 3, (-7.425, yy, z), (1, 0, 0)))
                    add(key+f'_M6_WASHER_{j}_{k}', mirrored(washer, left), HARDWARE)
                    # External grip ends at beam faceX10.8. Omitted in-slot
                    # thread is explicitly recorded; never drill into a rail.
                    grip = cylinder(6, 17.525, (-6.725, yy, z), (1, 0, 0))
                    grip = grip.fuse(cylinder(10, 6, (-12.725, yy, z), (1, 0, 0)))
                    add(key+f'_M6x25_EXTERNAL_GRIP_{j}_{k}', mirrored(grip, left), HARDWARE)
    return out


def _stop_carrier(side, end, old_bracket):
    """Short welded lower cradle, around/under the guide; no long rail cap.

    Preserve the actual existing stop base footprint so its inboard tongue
    does not grow into the moving shoe. Joint sizing is not certified.
    """
    left, front = side == 'L', end == 'FRONT'
    canonical = old_bracket if left else old_bracket.mirror('YZ', (575, 0, 0))
    base = canonical.intersect(box(-100, 0, OLD_BASE, 300, 1450, 6.35))
    base = base.translate((0, 0, -6.35))
    for y in ((90, 140) if front else (1410, 1442)):
        base = base.fuse(cylinder(6.6, 6.35, (58.5, y, OLD_BASE-6.35)))
        base = base.cut(cylinder(6, 8.35, (58.5, y, OLD_BASE-7.35)))
    y0, y1 = (80, 135) if front else (1408, 1450)
    ty0, ty1 = (80, 105) if front else (1425, 1450)
    leg = box(50.8, y0, 973, 6, y1-y0, 36)
    floor = box(50.8, y0, 1003, 30.2, y1-y0, 6)
    tower = box(75, ty0, 1009, 6, ty1-ty0, OLD_BASE-6.35-1009)
    s = base.fuse(leg, floor, tower)
    for y in ((90, 120) if front else (1416, 1442)):
        s = s.cut(cylinder(6.6, 9, (49.8, y, 993), (1, 0, 0)))
    return mirrored(s.clean(), left)


def _add_plasma(router):
    common = [p for p in router if not p[0].startswith(('TOOL_SPINDLE_', 'TOOL_SPLIT_CLAMP_', 'TOOL_CLAMP_'))]
    adapter = next(s for n, s, c in common if n == 'TOOL_ADAPTER_110')
    ox, oy, oz, *_ = bbox(adapter)
    upper = (ox, oy, oz)
    bracket = (ox, oy, oz-PLASMA_DROP)
    lower = (ox, oy-12.7, oz-PLASMA_DROP)
    blank = plate(rect(110, PLASMA_DROP+70), 12.7,
                  [(x, y+PLASMA_DROP, 6) for x, y in MOUNT_PATTERN]+
                  [(x, y, 6.6) for x, y in MOUNT_PATTERN])
    for x, y in MOUNT_PATTERN:
        blank = blank.cut(cyl(10.5, 6.1).translate((x, y, -.1)))
    def install(s, origin):
        return place(s, origin, u=(1, 0, 0), v=(0, 0, 1))
    common.append(('XR_PLASMA_DROP_'+str(int(PLASMA_DROP)), install(blank.clean(), bracket), (.30, .50, .52)))
    for n, s, c in _local_head():
        common.append((n, install(s, lower), c))
    screw = cyl(6, 16).fuse(cyl(10.2, 6).translate((0, 0, 16))).clean()
    for i, (x, y) in enumerate(MOUNT_PATTERN, 1):
        local = place(screw, (x, y, 9.3), u=(1, 0, 0), v=(0, -1, 0))
        for label, origin in (('UPPER', upper), ('LOWER', lower)):
            common.append((f'XR_DROP_M6x16_{label}_{i}', install(local, origin), HARDWARE))
    return common


@lru_cache(maxsize=8)
def _wood(gantry_y, head_x, z_lift):
    out = []
    old = _bare_motion(gantry_y, head_x, z_lift)
    for name, shape, color in old:
        if name in ('Y_DATUM_L', 'Y_DATUM_R'):
            continue
        if name.startswith('Y_STOP_') and ('_CAP_' in name or '_NUT_' in name):
            continue
        if name.startswith('GANTRY_END_BRACKET_'):
            shape = _gantry_bracket(name.endswith('_L'), gantry_y)
        elif name.startswith('Y_LINK_SUPPORT_'):
            out += _link_support(name.endswith('_L'), gantry_y)
            continue
        elif name.startswith(('HMS_Y_L_', 'HMS_Y_R_')):
            shape = shape.translate((0, 0, MODULE_RISE))
        elif name.startswith(('Y_LINK_L_', 'Y_LINK_R_')):
            shape = _tilt_link(name, shape, gantry_y)
        else:
            dx = _shift_side(name)
            if dx:
                shape = shape.translate((dx, 0, 0))
            if name in ('Y_SHOE_L','Y_SHOE_R'):
                x=80.8 if name.endswith('_L') else 1056.5
                shape=shape.cut(box(x-1,gantry_y-61.5,OLD_BASE+65.5-.5,15,49,7.35)).clean()
        out.append((name, shape, color))
    out += _saddles()
    lookup = {n:s for n, s, c in out}
    for side, left in (('L', True), ('R', False)):
        for end, front in (('FRONT', True), ('REAR', False)):
            carrier = _stop_carrier(side, end, lookup[f'Y_STOP_{side}_{end}_BRACKET'])
            out.append((f'XR_STOP_CARRIER_{side}_{end}', carrier, STEEL))
            for i, y in enumerate((90, 140) if front else (1410, 1442), 1):
                # Short replacement screw into carrier's6.35mm nominal tapped
                # landing. Engagement5.65mm; actual thread/joint check held.
                screw = cylinder(6, 12, (58.5, y, OLD_BASE-5.65))
                screw = screw.fuse(cylinder(10, 6, (58.5, y, OLD_BASE+6.35)))
                out.append((f'XR_STOP_BASE_M6x12_{side}_{end}_{i}', mirrored(screw.clean(), left), HARDWARE))
            for i, y in enumerate((90, 120) if front else (1416, 1442), 1):
                grip = cylinder(6, 7.6, (50.8, y, 993), (1, 0, 0))
                grip = grip.fuse(cylinder(10, 6, (58.4, y, 993), (1, 0, 0)))
                washer = cylinder(12, 1.6, (56.8, y, 993), (1, 0, 0)).cut(cylinder(6.6, 3.6, (55.8, y, 993), (1, 0, 0)))
                out.append((f'XR_STOP_FRAME_M6x16_EXTERNAL_GRIP_{side}_{end}_{i}', mirrored(grip.clean(), left), HARDWARE))
                out.append((f'XR_STOP_FRAME_WASHER_{side}_{end}_{i}', mirrored(washer.clean(), left), HARDWARE))
    return tuple(out)


def motion_parts(plasma, gantry_y=775., head_x=575., z_lift=50.):
    """Return world-space named review solids; poses remain nominal travel."""
    router = list(_wood(float(gantry_y), float(head_x), float(z_lift)))
    return _add_plasma(router) if plasma else router


def is_stationary(name):
    if name.startswith(('XR_SADDLE_', 'XR_STOP_', 'Y_RAIL_', 'Y_LIMIT_', 'Y_BUFFER_', 'Y_STOP_')):
        return True
    return name in ('HMS_Y_L_BODY', 'HMS_Y_L_MOTOR', 'HMS_Y_L_MOTOR_BRACKET',
                    'HMS_Y_R_BODY', 'HMS_Y_R_MOTOR', 'HMS_Y_R_MOTOR_BRACKET')


def part_motion_class(name):
    """Classification for external sweep evidence; all nonstationary parts moveY."""
    if is_stationary(name):
        return 'stationary'
    if name=='ZBX80_OUTPUT_HOLD' or name.startswith(('TOOL_', 'I_HEAD_', 'XR_PLASMA_DROP_', 'XR_DROP_')):
        return 'Y_X_Z_tool'
    if name.startswith(('ZBX80_', 'Z_CARRIER', 'X_BLOCK_', 'X_BLOCK_BOLT_', 'X_HOME_CAM', 'X_LINK_', 'HMS_X_CARRIAGE', 'HMS_X_SHOE')):
        return 'Y_X_head'
    return 'Y_gantry_or_drive'


def interface_metadata():
    sources = [Path(__file__), HERE/'params.py', OLD/'motion_context.py']
    sources += [SOURCE/(n+'.py') for n in ('motion_details', 'motion_completion', 'motion_finish', 'cad_helpers')]
    return {
        'status':'XR1 integration candidate, not fabrication/CAM release',
        'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'guide_seat_planes_X_mm':[50.8,1099.2], 'guide_center_Z_mm':GUIDE_Z,
        'upper_beam_Z_mm':[P.UPPER_BOTTOM,P.UPPER_TOP],
        'module_base_Z_mm':MODULE_BASE, 'module_rise_mm':MODULE_RISE,
        'saddle_station_Y_mm':list(SADDLE_STATIONS),
        'link_endpoint_delta_Z_mm':MODULE_RISE,
        'link_angle_deg':abs(LINK_ANGLE_DEG),
        'link_eye_distance_mm':math.hypot(80,MODULE_RISE),
        'nominal_link_thread_engagement_each_mm':10-(math.hypot(80,MODULE_RISE)-80)/2,
        'plasma_drop_mm':PLASMA_DROP,
        'no_long_caps_or_datums':True,
        'moving_parts':'part_motion_class() is authoritative broad classification; ZBX80 body and motor moveX/Y but output/head also movesZ through inherited geometry.',
        'unmodeled_slot_threads':'Saddle and stop frame screws show external grip/head only. In-slot threads/Tnut bodies are not fabricated solid geometry. Rail factory screw holes and fasteners are absent pending actual pattern.',
    }
