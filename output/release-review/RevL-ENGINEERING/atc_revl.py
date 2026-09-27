"""GM1 Rev L: RapidChange-type magazine on a retracting carrier that rides on the bed module.

Every part is named MOD_ATC_*, so the dock is part of the one-piece module: it lifts out
with the bed (Rev J's hoist and sling) and is out of the machine for plasma. Nothing is
added to the frame.

  - Two 1 x 2 in tube beams stand on the 20100 strips behind the HDPE, on T-slot feet in
    the top slots at X275/315 and X835/875, and run back past the module's rear edge.
  - MGNR12 rails on machined seat bars; one MGN12H block each; rail plane Z1007 and carrier
    Z1020..1026.35, as the other session's small-machine carrier, so the magazine support
    plane stays at Z1050.35.
  - A U-shaped carrier: a tray under the magazine with a window for the stored tools, and two
    arms back to the blocks. Its middle is open behind the tray, so the Z body's lower end
    block passes over it.
  - 200 mm of travel. Deployed, the magazine sits over the rear 60 mm of the work area; parked,
    it is behind the Z body at the rear stop and under the gantry.
  - Drive on the right beam: a 24 V worm gearmotor and a GT2 belt, a tab on the right arm, a
    fitted front stop (the pocket datum), a rear stop, and two inductive sensors.
The magazine is an allocation (520 x 60 x 80 mm), not a supplier drawing; the saddles are blanks.
"""
from pathlib import Path
import sys

import cadquery as cq

from cad_helpers import ALU, HARDWARE, PURCHASED, box, cyl

HARDWARE_DIR = Path(__file__).resolve().parents[3] / 'variants' / 'retractable-atc' / 'hardware'
if str(HARDWARE_DIR) not in sys.path:
    sys.path.append(str(HARDWARE_DIR))
import hardware  # noqa: E402  (the other session's sourced MGN12H block)

PREFIX = 'MOD_ATC_'
BLUE = (.12, .48, .65)
GOLD = (.8, .6, .25)
MAGENTA = (.75, .25, .62)
RAIL_X = (295.0, 855.0)              # over strip 2 and strip 8 top slots; symmetric about X575
STRIP_TOP = 940.8
FOOT_T = 6.35
FEET_Y = ((1170.0, 1210.0), (1240.0, 1280.0))
TUBE_W, TUBE_H, TUBE_WALL = 25.4, 50.8, 2.108            # 1 x 2 x .083 in rectangular tube
TUBE_Z = STRIP_TOP + FOOT_T                             # 947.15
RB = 1007.0                                             # rail mounting plane (machined seat)
SEAT_Z = TUBE_Z + TUBE_H                                # 997.95
BEAM_Y = (1160.0, 1445.0)
RAIL_Y = (1162.0, 1443.0)
WT, T = 1020.0, 6.35                                    # carrier plate
TOP = WT + T
SADDLE_Z = 1044.0
MAG = 1050.35                                           # magazine support plane
TRAVEL = 200.0                                          # 0 = deployed, 200 = parked
BLOCK_Y = 1200.0                                        # block centre, deployed
CARRIER = (280.0, 870.0, 1065.0, 1232.0)                # x0, x1, y0, y1 deployed
TRAY_Y1 = 1140.0
WINDOW = (335.0, 815.0, 1080.0, 1120.0)
MAGAZINE = (315.0, 1070.0, 520.0, 60.0, 80.0)           # x0, y0, length, width, height (allocation)
POCKET_Y = 1100.0
TOOL_HANG = 36.55                                       # stored cutter below the magazine base
SADDLES = (295.0, 815.0)
RISER_X = (314.0, 328.0, 822.0, 836.0)                  # screw heads clear the rails and blocks
TAB = (870.0, 1185.0, 965.0)                            # x0, y0 deployed, z0
TAB_SIZE = (6.35, 36.0, TOP - 965.0)
PULLEY_Y = (1172.0, 1436.0)
PULLEY_Z = 995.0
BELT_X = (877.5, 883.5)
SENSOR_Y = (1203.0, 1403.0)                             # deployed, parked (tab centre)
TUBE_OUTER_X = RAIL_X[1] + TUBE_W / 2                   # 867.7, right beam outer face
DENSITY = {'steel': 7.85e-6, 'aluminum': 2.7e-6}        # kg/mm3
BOUGHT_KG = {'HIWIN_MGN12H': .10, 'HIWIN_MGNR12_281': .18, '24V_WORM_GEARMOTOR_30RPM': .35, 'GT2_20T_8MM_BORE': .02,
             'GT2_6MM_BELT': .01, 'M8_INDUCTIVE_PNP_NO_2MM': .05, 'M12_8PIN_PANEL_RECEPTACLE': .10,
             'RAPIDCHANGE_ER11_MAGAZINE_ALLOCATION': 3.0, 'STORED_CUTTER_ALLOCATION': .30}   # by part number
Y_TO_X = dict(u=(0, 1, 0), v=(-1, 0, 0))                # local X along world +Y, local Y along world -X


def rail(length):
    """MGNR12 as the other session's rail_350: 12 x 8, counterbored holes at 10 + 25 n."""
    body = box(length, 12, 8).translate((0, -6, 0))
    x = 10.0
    while x < length - 5:
        body = body.cut(cyl(3.5, 10).translate((x, 0, -1))).cut(cyl(6, 4.5).translate((x, 0, 3.5)))
        x += 25
    return body.clean()


def rect_tube(length, w=TUBE_W, h=TUBE_H, wall=TUBE_WALL):
    """Tube along local Y, width along X, height along Z."""
    return box(w, length, h).cut(box(w - 2 * wall, length + 2, h - 2 * wall).translate((wall, -1, wall))).clean()


def socket_screw(d, length, head_d, head_h, head_below=False):
    """Nominal shank plus head. Head on top by default; head_below puts the head under local Z0."""
    if head_below:
        return cyl(d, length).fuse(cyl(head_d, head_h).translate((0, 0, -head_h))).clean()
    return cyl(d, length).fuse(cyl(head_d, head_h).translate((0, 0, length))).clean()


def _add(m, name, shape, origin=(0, 0, 0), **kw):
    kw.setdefault('group', 'atc')
    return m.add(PREFIX + name, shape, origin, **kw)


def _fixed(m):
    ids = []
    for side, cx in zip('LR', RAIL_X):
        for i, (y0, y1) in enumerate(FEET_Y, 1):
            p = m.add_plate(f'{PREFIX}FOOT_{side}_{i}', 60, y1 - y0, FOOT_T, holes=[(10, 20, 5.5), (50, 20, 5.5)],
                            origin=(cx - 30, y0, STRIP_TOP), pn='MOD_ATC_FOOT_60x40', group='atc', color=BLUE,
                            notes=['1/4 in steel, welded under the beam tube. Two M5 x 12 button screws into M5 T-nuts in the strip top slots '
                                   f'at X{cx - 20:g} and X{cx + 20:g}. The T-nuts are not modeled.'])
            ids.append(p.id)
            for k, dx in enumerate((-20, 20), 1):
                s = _add(m, f'FOOT_SCREW_{side}_{i}_{k}', socket_screw(5, 12, 9.5, 2.75),
                         (cx + dx, (y0 + y1) / 2, STRIP_TOP + FOOT_T - 12), pn='STD_M5x12_ISO7380', group='atc_hardware',
                         material='M5 x 12 button head, A2 stainless', color=HARDWARE,
                         notes=['Shank ends inside the 20100 top slot; the T-nut is not modeled.'])
                ids.append(s.id)
        tube = _add(m, f'BEAM_{side}', rect_tube(BEAM_Y[1] - BEAM_Y[0]), (cx - TUBE_W / 2, BEAM_Y[0], TUBE_Z),
                    pn='MOD_ATC_BEAM_1x2_285', material='1 x 2 x .083 in steel rectangular tube', length=BEAM_Y[1] - BEAM_Y[0],
                    color=BLUE, notes=['Welded to its two feet and to the seat bar; stands 6.35 mm off the strip between the feet.',
                                       'Cantilevers 165 mm behind the rear foot, past the module rear edge (Y1347.8) to Y1445.'])
        seat_holes = []
        y = 10.0
        while y < RAIL_Y[1] - RAIL_Y[0] - 5:
            seat_holes.append((TUBE_W / 2, RAIL_Y[0] - BEAM_Y[0] + y, 2.5))
            y += 25
        seat = m.add_plate(f'{PREFIX}SEAT_{side}', TUBE_W, BEAM_Y[1] - BEAM_Y[0], RB - SEAT_Z, holes=seat_holes,
                           origin=(cx - TUBE_W / 2, BEAM_Y[0], SEAT_Z), pn='MOD_ATC_RAIL_SEAT_285', group='atc', color=BLUE,
                           notes=[f'Steel bar 25.4 x {RB - SEAT_Z:.2f} (from 3/8 in), welded on the tube, then machined flat at Z{RB:g} with the '
                                  'module level. M3 tapped at the rail pitch (tap drill 2.5 shown), 6 deep.'])
        r = _add(m, f'RAIL_{side}', rail(RAIL_Y[1] - RAIL_Y[0]), (cx, RAIL_Y[0], RB), **Y_TO_X, pn='HIWIN_MGNR12_281',
                 group='atc_guides', purchased=True, color=GOLD, material='HIWIN MGNR12 rail, cut to 281 mm',
                 notes=['Cut 281 mm with the first hole 10 mm from the front end (11 holes at 25 mm). M3 x 8 screws into the seat.'])
        ids += [tube.id, seat.id, r.id]
    x0 = TUBE_OUTER_X
    for name, y0 in (('FRONT_STOP', 1173.0), ('REAR_STOP', 1421.0)):
        p = _add(m, name, box(880 - x0, 12, 22), (x0, y0, 962), pn='MOD_ATC_' + name, color=BLUE,
                 notes=['Welded to the right beam outer face. ' + (
                     'Its rear face (Y1185) is the deployed datum: fit it after welding, then probe the pocket reference.'
                     if name == 'FRONT_STOP' else 'Soft end stop for the parked position; the drive tab stops 0-2 mm short.')])
        ids.append(p.id)
    for name, (y0, y1) in (('PULLEY_BRACKET_F', (1161.0, 1183.0)), ('PULLEY_BRACKET_R', (1425.0, 1445.0))):
        p = _add(m, name, box(6.3, y1 - y0, 20), (x0, y0, 985), pn='MOD_ATC_PULLEY_BRACKET', color=BLUE,
                 notes=['Carries the pulley shaft (8 mm, flanged bearing), welded to the right beam outer face. Shaft not modeled.'])
        ids.append(p.id)
    for name, py in zip('FR', PULLEY_Y):
        p = _add(m, 'PULLEY_' + name, cyl(16, 16), (875, py, PULLEY_Z), u=(0, 1, 0), v=(0, 0, 1), pn='GT2_20T_8MM_BORE',
                 group='atc_drive', purchased=True, color=HARDWARE, material='GT2 20-tooth pulley, 6 mm belt, 8 mm bore (flanged envelope)')
        ids.append(p.id)
    for name, z0 in (('UPPER', 1000.6), ('LOWER', 988.0)):
        p = _add(m, 'BELT_' + name, box(BELT_X[1] - BELT_X[0], PULLEY_Y[1] - PULLEY_Y[0], 1.4), (BELT_X[0], PULLEY_Y[0], z0),
                 pn='GT2_6MM_BELT', group='atc_drive', purchased=True, color=(.1, .1, .1),
                 material='GT2 6 mm belt, closed loop by the clamp', notes=['Straight runs between the pulley centres; the wraps are inside the pulley envelopes.'])
        ids.append(p.id)
        for pul in 'FR':
            m.permit(p.id, PREFIX + 'PULLEY_' + pul, 'Belt run ends at the pulley centre; the belt wraps the pulley.')
    motor = _add(m, 'GEARMOTOR', box(49, 30, 50), (891, 1415, 975), pn='24V_WORM_GEARMOTOR_30RPM', group='atc_drive',
                 purchased=True, color=PURCHASED, material='24 V DC worm gearmotor, about 30 rpm, 8 mm output shaft (envelope)',
                 notes=['Self-locking worm holds the carrier against the stops. 30 rpm on a 20T GT2 pulley is about 20 mm/s (200 mm in 10 s).',
                        'Envelope 49 x 30 x 50; select the actual unit and fit its face to the motor plate.'])
    plate_ = _add(m, 'MOTOR_PLATE', box(940 - (RAIL_X[1] - TUBE_W / 2), 4, 1025 - TUBE_Z), (RAIL_X[1] - TUBE_W / 2, BEAM_Y[1], TUBE_Z),
                  pn='MOD_ATC_MOTOR_PLATE', color=BLUE, notes=['3/16 in steel, welded to the right beam end; the gearmotor and connector bracket bolt to it.'])
    conn = _add(m, 'CONNECTOR', box(40, 20, 22), (895, 1420, 948), pn='M12_8PIN_PANEL_RECEPTACLE', group='atc_electrical',
                purchased=True, color=PURCHASED, material='M12 8-pin panel receptacle with its mating plug (envelope)',
                notes=['One plug for the gearmotor and both sensors; unplug it before the bed lift. The magazine cover/IR lead is a second plug, not yet defined.'])
    cbr = _add(m, 'CONNECTOR_BRACKET', box(40, 1445 - 1440, 22), (895, 1440, 948), pn='MOD_ATC_CONNECTOR_BRACKET', color=BLUE)
    ids += [motor.id, plate_.id, conn.id, cbr.id]
    for label, sy in zip(('DEPLOYED', 'PARKED'), SENSOR_Y):
        base = _add(m, f'SENSOR_BASE_{label}', box(900 - x0, 20, 6), (x0, sy - 10, 950), pn='MOD_ATC_SENSOR_BASE', color=BLUE)
        hole = cq.Solid.makeCylinder(4.1, 8, cq.Vector(-1, 10, 14), cq.Vector(1, 0, 0))
        upright = box(6, 20, 26).cut(hole).clean()
        up = _add(m, f'SENSOR_UPRIGHT_{label}', upright, (894, sy - 10, 956), pn='MOD_ATC_SENSOR_UPRIGHT', color=BLUE)
        sensor = _add(m, f'SENSOR_{label}', cyl(8, 45), (878, sy, 970), u=(0, 1, 0), v=(0, 0, 1), pn='M8_INDUCTIVE_PNP_NO_2MM',
                      group='atc_electrical', purchased=True, color=PURCHASED,
                      material='M8 inductive sensor, PNP NO, 2 mm range, 10-30 V (envelope)',
                      notes=[f'Face 1.65 mm from the drive tab when the carrier is {label.lower()}.'])
        ids += [base.id, up.id, sensor.id]
    return ids


def _carrier(m, travel):
    dy = travel
    ids = []
    x0, x1, y0, y1 = CARRIER
    w, d = x1 - x0, y1 - y0
    arm = 30.0
    outline = [(0, 0), (w, 0), (w, d), (w - arm, d), (w - arm, TRAY_Y1 - y0), (arm, TRAY_Y1 - y0), (arm, d), (0, d)]
    wx0, wx1, wy0, wy1 = WINDOW
    window = [(wx0 - x0, wy0 - y0), (wx1 - x0, wy0 - y0), (wx1 - x0, wy1 - y0), (wx0 - x0, wy1 - y0)]
    holes = []
    for cx in RAIL_X:
        holes += [(cx - x0 + dx, BLOCK_Y - y0 + dyy, 3.4) for dx in (-10, 10) for dyy in (-10, 10)]
    risers = [(rx, ry) for rx in RISER_X for ry in (1075.0, 1120.0)]
    holes += [(rx - x0, ry - y0, 5.5) for rx, ry in risers]
    p = m.add_plate(PREFIX + 'CARRIER', w, d, T, internal=[window], holes=holes, outline=outline, origin=(x0, y0 + dy, WT),
                    pn='MOD_ATC_CARRIER', group='atc_moving', color=BLUE,
                    notes=['1/4 in steel, one piece: tray under the magazine and two arms back to the guide blocks. The middle is open '
                           'behind the tray so the Z body lower end block (Z1040) passes over it.',
                           'Window X335-815 x Y1080-1120 (deployed) for cutters hanging below the pockets.'])
    ids.append(p.id)
    for name, (ux0, ux1), (uy0, uy1) in (('UPSTAND_FRONT', (336.0, 814.0), (1065.0, 1071.35)),
                                         ('UPSTAND_REAR', (310.0, 840.0), (1133.65, 1140.0))):
        u = _add(m, name, box(ux1 - ux0, uy1 - uy0, SADDLE_Z - TOP), (ux0, uy0 + dy, TOP), pn='MOD_ATC_' + name,
                 group='atc_moving', color=BLUE, notes=['1/4 in steel strip on edge, welded to the tray; stiffens it as a channel.'])
        ids.append(u.id)
    for side, sx in zip('LR', SADDLES):
        s = m.add_plate(f'{PREFIX}SADDLE_{side}', 40, 65, T,
                        holes=[(x - sx, y, 5.0) for x in RISER_X if sx <= x <= sx + 40 for y in (10, 55)],
                        origin=(sx, 1065 + dy, SADDLE_Z), pn='MOD_ATC_SADDLE_BLANK_40x65', group='atc_moving', color=ALU,
                        material='Aluminum plate 1/4 in; alloy to verify',
                        notes=['BLANK magazine interface: only the four riser holes (tap M5; drawn at 5.0). Drill the magazine holes '
                               'from the supplier drawing or the delivered part.'])
        ids.append(s.id)
    for k, (rx, ry) in enumerate(risers, 1):
        r = _add(m, f'RISER_{k}', cyl(12, SADDLE_Z - TOP).cut(cyl(5.5, SADDLE_Z - TOP)), (rx, ry + dy, TOP),
                 pn='MOD_ATC_RISER_12x17p65', group='atc_moving', color=GOLD, material='Steel spacer 12 OD x 5.5 ID x 17.65')
        s = _add(m, f'RISER_SCREW_{k}', socket_screw(5, 30, 8.5, 5, head_below=True), (rx, ry + dy, WT),
                 pn='STD_M5x30_ISO4762', group='atc_hardware', material='M5 x 30 socket head, class 8.8', color=HARDWARE,
                 notes=['From below: head under the tray (Z1015), threads into the saddle.'])
        m.permit(s.id, f'{PREFIX}SADDLE_{"L" if rx < 575 else "R"}', 'Nominal M5 screw in the tapped saddle hole (drawn at the major diameter).')
        ids += [r.id, s.id]
    for side, cx in zip('LR', RAIL_X):
        blk = _add(m, f'BLOCK_{side}', hardware.mgn12h_block(), (cx, BLOCK_Y + dy, RB), **Y_TO_X, pn='HIWIN_MGN12H',
                   group='atc_guides', purchased=True, color=GOLD, material='HIWIN MGN12H block')
        ids.append(blk.id)
        for j, (dx, dyy) in enumerate([(a, b) for a in (-10, 10) for b in (-10, 10)], 1):
            wsh = _add(m, f'BLOCK_WASHER_{side}_{j}', cyl(7, .5).cut(cyl(3.2, .5)), (cx + dx, BLOCK_Y + dyy + dy, TOP),
                       pn='WASHER_M3_7x0p5', group='atc_hardware', material='steel washer', color=HARDWARE)
            scr = _add(m, f'BLOCK_SCREW_{side}_{j}', socket_screw(3, 10, 5.5, 3), (cx + dx, BLOCK_Y + dyy + dy, TOP + .5 - 10),
                       pn='STD_M3x10_ISO4762', group='atc_hardware', material='M3 x 10 socket head, class 8.8', color=HARDWARE)
            m.permit(scr.id, blk.id, 'Nominal M3 screw in the tapped block hole.')
            ids += [wsh.id, scr.id]
    tx, ty, tz = TAB
    tab = _add(m, 'DRIVE_TAB', box(*TAB_SIZE), (tx, ty + dy, tz), pn='MOD_ATC_DRIVE_TAB', group='atc_moving', color=BLUE,
               notes=['1/4 in steel, welded to the right arm outer edge. Its front face stops on the front stop (deployed datum); '
                      'the sensors read its outer face.'])
    clamp = _add(m, 'BELT_CLAMP', box(886 - (tx + TAB_SIZE[0]), 16, 8), (tx + TAB_SIZE[0], 1195 + dy, 998), pn='MOD_ATC_BELT_CLAMP',
                 group='atc_moving', color=BLUE,
                 notes=['Clamps both belt ends. Bolt it to the tab through a slot with a stiff spring so the belt runs about 2 mm on '
                        'after the tab reaches the front stop: the self-locking worm then holds that preload.'])
    m.permit(clamp.id, PREFIX + 'BELT_UPPER', 'The belt ends are clamped in the carrier clamp (closed loop).')
    ids += [tab.id, clamp.id]
    mx0, my0, ml, mw, mh = MAGAZINE
    mag = _add(m, 'MAGAZINE_ALLOCATION', box(ml, mw, mh), (mx0, my0 + dy, MAG), pn='RAPIDCHANGE_ER11_MAGAZINE_ALLOCATION',
               group='atc_allocation', purchased=True, color=MAGENTA, release='SUPPLIER ALLOCATION - NOT A PURCHASED-PART DRAWING',
               material='RapidChange ER11 linear magazine: allocation only',
               notes=['520 x 60 x 80 mm allocation (the other session\'s), pocket line Y1100 deployed. Not a supplier drawing: '
                      'length, pocket pitch, mounting holes, nut datum and cover sweep come from the delivered kit.'])
    tools = _add(m, 'STORED_TOOLS_ALLOCATION', box(wx1 - wx0, 15, TOOL_HANG), (wx0, POCKET_Y - 7.5 + dy, MAG - TOOL_HANG),
                 pn='STORED_CUTTER_ALLOCATION', group='atc_allocation', purchased=True, color=MAGENTA,
                 release='SUPPLIER ALLOCATION - NOT A PURCHASED-PART DRAWING', material='Stored ER11 cutters: allocation only',
                 notes=['Cutters up to 15 mm OD hanging at most 36.55 mm below the magazine base (Z1013.8).'])
    ids += [mag.id, tools.id]
    return ids


def mass_properties(m):
    total, moment = 0.0, [0.0, 0.0, 0.0]
    for p in m.parts:
        if not p.id.startswith(PREFIX):
            continue
        kg = BOUGHT_KG.get(p.part_number)
        if kg is None:
            kg = p.shape.Volume() * (DENSITY['aluminum'] if 'luminum' in p.material else DENSITY['steel'])
        c = p.shape.Center().toTuple()
        total += kg
        moment = [moment[i] + kg * c[i] for i in range(3)]
    return round(total, 2), [round(v / total, 1) for v in moment]


def extend_router_model(m, travel=TRAVEL):
    assert 0 <= travel <= TRAVEL
    fixed = _fixed(m)
    moving = _carrier(m, travel)
    kg, cg = mass_properties(m)
    m.holds.append('ATC: the magazine is a 520 x 60 x 80 mm allocation, not a supplier drawing. Pocket pitch, mounting holes, nut datum, '
                   'cover sweep and cable come from the delivered RapidChange kit; the saddles stay blank until then.')
    m.holds.append('ATC: deployed-position repeatability (target 0.05 mm at the pocket reference, 20 cycles), gearmotor and spring '
                   'preload, and sensor settings are commissioning tests. Probe the pocket reference after every bed install.')
    return {'status': 'MODULE-MOUNTED RETRACTING DOCK: WORKING CAD, NOT A FABRICATION RELEASE',
            'travel_mm': travel, 'travel_state': 'deployed' if travel == 0 else 'parked' if travel == TRAVEL else 'between',
            'stroke_mm': TRAVEL, 'rail_x_mm': list(RAIL_X), 'rail_plane_z_mm': RB, 'carrier_z_mm': [WT, TOP],
            'magazine_support_plane_z_mm': MAG, 'magazine_allocation_mm': list(MAGAZINE[2:]),
            'magazine_y_deployed_mm': [MAGAZINE[1], MAGAZINE[1] + MAGAZINE[3]], 'pocket_line_y_deployed_mm': POCKET_Y,
            'stored_cutter_bottom_z_mm': MAG - TOOL_HANG, 'tool_window_mm': list(WINDOW),
            'deployed_datum': 'Drive tab front face on the front stop at Y1185',
            'fixed_part_count': len(fixed), 'moving_part_count': len(moving),
            'mass_kg': kg, 'cg_mm': cg,
            'mass_basis': 'Steel 7850 and aluminum 2700 kg/m3 on the modeled solids; bought parts by nominal mass; magazine 3.0 kg and '
                          'cutters 0.3 kg are placeholders. Weigh the module with the dock.'}
