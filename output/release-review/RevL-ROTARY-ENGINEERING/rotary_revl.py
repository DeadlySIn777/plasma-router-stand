"""GM1 Rev L rotary axis for plasma tube notching (owner, 28 September: "can we add a 4th axis for the
plasma/cnc?" - "plasma for tube knotching").

The Rodent has four stepper drivers and GM1 uses all four (X, Y1, Y2, Z), so there is no fifth axis to
give a rotary. The rotary takes the X driver through a plug swap at the cabinet: in rotary mode the torch
runs along Y on the two squared Y motors, the tube turns on what the controller thinks is X, and the X
carriage stays where it was put. The tube lies along Y on the tool axis centre line (X575), held in a
four-jaw chuck at the front of the machine, over the water pan; long tubes go out the back over the rear
cross tube.

Parts (ROT_*), all on the frame, nothing on the bed module:
  - A 2 x 2 x .083 in steel cross tube across the front at ledger height, bolted to the two front legs with
    four M10 through-bolts (3.5 mm spacers keep it clear of the ledgers' sand end caps; bolts and spacers
    are not drawn). A U of the same tube welded to its front face and a 1/4 in plate on top make the shelf.
  - The rotary unit as an allocation: a 210 x 200 x 175 body (spindle housing, belt reduction, NEMA 23 on
    the X driver) and a Ø125 x 65 four-jaw chuck (K72-125 class, hollow) facing the machine. Axis Z962.7,
    chuck face at Y-10, so the bed module (front edge Y5) stays in for router work with the rotary fitted.
  - The workpiece as an allocation: a round tube along Y from 20 mm inside the jaws.
The unit's real footprint, holes, through-bore and height come from the delivered rotary.
"""
from cad_helpers import PURCHASED, box, cyl, place

PREFIX = 'ROT_'
BLUE = (.12, .48, .65)
MAGENTA = (.75, .25, .62)
T_W, T_WALL = 50.8, 2.108                 # 2 x 2 x .083 in tube
FRAME_X = (0.0, 1150.0)                   # the front legs' outer faces
CAP_GAP = 3.5                             # the ledger end caps stand 3.05 mm proud of the legs' front faces (Y0)
CROSS_Y1 = -CAP_GAP                       # cross tube rear face
CROSS_Y0 = CROSS_Y1 - T_W                 # -54.3
SHELF_X = (465.0, 685.0)                  # plate width across the tool axis
SHELF_Y0 = -288.0                         # plate front edge
PLATE_T = 6.35
AXIS_X = 575.0
AXIS_ABOVE_PLATE = 116.35                 # allocation: base plate to spindle axis
BODY = (470.0, 680.0, -275.0, -75.0, 175.0)   # x0, x1, y0, y1, height on the plate
CHUCK_D, CHUCK_L = 125.0, 65.0
CHUCK_Y = (-75.0, -10.0)                  # chuck face at Y-10: 15 mm in front of the bed module's front edge (Y5)
TUBE_IN_JAWS = 20.0
TUBE_D, TUBE_WALL = 60.0, 3.0             # the checked workpiece
TUBE_L = 1200.0
MIN_TORCH_Y = 275.0 - 201.4               # torch axis at the gantry's front stop (Rev K offset)
BOUGHT_KG = {'ROTARY_AXIS_ALLOCATION': 9.0, 'ROTARY_CHUCK_K72_125_ALLOCATION': 4.5}
HOLDS = ['ROTARY: the unit, its chuck and its through-bore are allocations (Ø125 four-jaw, hollow, belt reduction, NEMA 23). '
         'Drill the shelf plate from the delivered base; the axis height sets the touch-off heights below.',
         'ROTARY: the X motor plug swap must be made with the 48 V off (E-stop pressed). Hot-plugging a stepper driver damages it.',
         'ROTARY: the X carriage is not held while its motor is unplugged; a ball screw back-drives. Do not push on the gantry '
         'during a tube job, and re-home X after swapping back.']


def _add(m, name, shape, origin=(0, 0, 0), **kw):
    kw.setdefault('group', 'rotary')
    return m.add(PREFIX + name, shape, origin, **kw)


def rect_tube(length, w=T_W, wall=T_WALL):
    """Tube along local X."""
    return box(length, w, w).cut(box(length + 2, w - 2 * wall, w - 2 * wall).translate((-1, wall, wall))).clean()


def ledger_top(m):
    from cad_helpers import bbox
    return bbox(m.find('MF_RECEIVER_LEDGER_1').shape)[5]


def add_bracket(m):
    """Cross tube, U stubs and the shelf plate at the front of the frame."""
    z1 = ledger_top(m)
    z0 = z1 - T_W
    ids = []
    cross = _add(m, 'CROSS_TUBE', rect_tube(FRAME_X[1] - FRAME_X[0]), (FRAME_X[0], CROSS_Y0, z0), pn='ROT_CROSS_TUBE_2x2_1150',
                 material='2 x 2 x .083 in steel square tube', length=FRAME_X[1] - FRAME_X[0], color=BLUE,
                 notes=[f'Across the front of the frame at ledger height (Z{z0:g}-{z1:g}), {CAP_GAP:g} mm in front of the legs\' faces so it '
                        'clears the ledgers\' sand end caps. Four M10 x 120 through-bolts, two per leg at Z' + f'{z0 + 12.7:g} and Z{z1 - 12.7:g}, with '
                        f'{CAP_GAP:g} mm spacer washers between the tube and the leg (bolts and spacers not drawn).',
                        'Remove it with the four bolts if the front of the machine must be clear.'])
    ids.append(cross.id)
    sx0, sx1 = SHELF_X
    stub_l = CROSS_Y0 - SHELF_Y0            # 233.7
    for side, x in (('L', sx0), ('R', sx1 - T_W)):
        s = _add(m, f'STUB_{side}', place(rect_tube(stub_l), (x, SHELF_Y0, z0), u=(0, 1, 0), v=(-1, 0, 0)).translate((T_W, 0, 0)),
                 pn='ROT_STUB_2x2_234', material='2 x 2 x .083 in steel square tube', length=stub_l, color=BLUE,
                 notes=['Welded to the cross tube\'s front face; carries the shelf plate.'])
        ids.append(s.id)
    front = _add(m, 'STUB_FRONT', rect_tube(sx1 - sx0 - 2 * T_W), (sx0 + T_W, SHELF_Y0, z0), pn='ROT_STUB_2x2_118',
                 material='2 x 2 x .083 in steel square tube', length=sx1 - sx0 - 2 * T_W, color=BLUE,
                 notes=['Closes the U between the two stubs at the front.'])
    ids.append(front.id)
    plate = m.add_plate(PREFIX + 'PLATE', sx1 - sx0, CROSS_Y1 - SHELF_Y0, PLATE_T, origin=(sx0, SHELF_Y0, z1), pn='ROT_SHELF_PLATE_220x285',
                        group='rotary', color=BLUE, material='A36 steel plate 1/4 in',
                        notes=[f'{sx1 - sx0:g} x {CROSS_Y1 - SHELF_Y0:g} x {PLATE_T:g} on the cross tube and the U stubs, welded. The rotary\'s base '
                               'bolts through it: drill from the delivered unit (no holes drawn).'])
    ids.append(plate.id)
    return ids, z1 + PLATE_T


def add_rotary(m, plate_top):
    """The rotary unit and its chuck (allocations)."""
    x0, x1, y0, y1, h = BODY
    axis_z = plate_top + AXIS_ABOVE_PLATE
    body = _add(m, 'UNIT_ALLOCATION', box(x1 - x0, y1 - y0, h), (x0, y0, plate_top), pn='ROTARY_AXIS_ALLOCATION', group='rotary_allocation',
                purchased=True, color=MAGENTA, release='SUPPLIER ALLOCATION - NOT A PURCHASED-PART DRAWING',
                material='Hollow rotary axis, belt reduction, NEMA 23: allocation only',
                notes=[f'{x1 - x0:g} x {y1 - y0:g} x {h:g} envelope on the shelf: spindle housing, belt reduction (about 6:1) and the NEMA 23 '
                       f'stepper on the X driver. Spindle axis at Z{axis_z:g}, X{AXIS_X:g}. Real size, holes and bore from the delivered unit.'])
    chuck = _add(m, 'CHUCK_ALLOCATION', place(cyl(CHUCK_D, CHUCK_L), (AXIS_X, CHUCK_Y[1], axis_z), u=(1, 0, 0), v=(0, 0, 1)),
                 pn='ROTARY_CHUCK_K72_125_ALLOCATION', group='rotary_allocation', purchased=True, color=MAGENTA,
                 release='SUPPLIER ALLOCATION - NOT A PURCHASED-PART DRAWING', material='K72-125 class four-jaw independent chuck: allocation only',
                 notes=[f'Ø{CHUCK_D:g} x {CHUCK_L:g}, face at Y{CHUCK_Y[1]:g} toward the machine. Independent jaws centre round and square tube. '
                        'The torch axis can come to Y' + f'{MIN_TORCH_Y:.1f}, so a tube end can be notched {MIN_TORCH_Y - CHUCK_Y[1]:.0f} mm from the jaws.'])
    return [body.id, chuck.id], axis_z


def add_tube(m, axis_z, length=TUBE_L, d=TUBE_D, wall=TUBE_WALL):
    """A round tube along Y from 20 mm inside the jaws (allocation)."""
    y0 = CHUCK_Y[1] - TUBE_IN_JAWS
    solid = cyl(d, length).cut(cyl(d - 2 * wall, length + 2).translate((0, 0, -1))).clean()
    tube = _add(m, 'TUBE_ALLOCATION', place(solid, (AXIS_X, y0, axis_z), u=(1, 0, 0), v=(0, 0, -1)), pn=f'ROT_TUBE_D{d:g}x{length:g}_ALLOCATION',
                group='rotary_workpiece', purchased=True, color=(.55, .55, .58), release='WORKPIECE ALLOCATION',
                material=f'Round steel tube Ø{d:g} x {wall:g} wall, {length:g} long: workpiece allocation',
                notes=[f'Along Y from Y{y0:g} ({TUBE_IN_JAWS:g} mm inside the jaws) to Y{y0 + length:g}, on the spindle axis Z{axis_z:g}. Top at '
                       f'Z{axis_z + d / 2:g}, bottom at Z{axis_z - d / 2:g}.'])
    m.permit(tube.id, PREFIX + 'CHUCK_ALLOCATION', 'The jaws grip the tube end (allocation).')
    return tube.id, {'d_mm': d, 'length_mm': length, 'y_mm': [y0, y0 + length], 'top_z_mm': axis_z + d / 2, 'bottom_z_mm': axis_z - d / 2}


def extend_model(m, tube_length=None, tube_d=TUBE_D):
    """Bracket and rotary on the frame; optionally a tube in the chuck."""
    bracket, plate_top = add_bracket(m)
    unit, axis_z = add_rotary(m, plate_top)
    info = {'status': 'ROTARY AXIS FOR TUBE NOTCHING: WORKING CAD, ALLOCATIONS FOR THE UNIT AND THE WORKPIECE',
            'axis_xz_mm': [AXIS_X, round(axis_z, 3)], 'chuck_face_y_mm': CHUCK_Y[1], 'plate_top_z_mm': round(plate_top, 3),
            'cross_tube_y_mm': [CROSS_Y0, CROSS_Y1], 'shelf_x_mm': list(SHELF_X), 'shelf_y_mm': [SHELF_Y0, CROSS_Y1],
            'torch_min_y_mm': round(MIN_TORCH_Y, 1), 'shortest_reach_from_jaws_mm': round(MIN_TORCH_Y - CHUCK_Y[1], 1),
            'drive': 'X driver through a plug swap; the tube turns on X commands, the torch runs along Y',
            'bracket_part_count': len(bracket), 'unit_part_count': len(unit)}
    if tube_length:
        tube_id, tube = add_tube(m, axis_z, tube_length, tube_d)
        info['tube'] = tube
    m.holds.extend(h for h in HOLDS if h not in m.holds)
    return info


def mass_kg(m):
    total = 0.0
    for p in m.parts:
        if not p.id.startswith(PREFIX) or p.id.startswith(PREFIX + 'TUBE'):
            continue
        kg = BOUGHT_KG.get(p.part_number)
        total += kg if kg is not None else p.shape.Volume() * 7.85e-6
    return round(total, 2)
