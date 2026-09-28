"""GM1 Rev L rotary axis for plasma tube notching (owner, 28 September: "can we add a 4th axis for the
plasma/cnc?" - "plasma for tube knotching").

The Rodent has four stepper drivers and GM1 uses all four (X, Y1, Y2, Z), so there is no fifth axis to
give a rotary. The rotary takes the X driver through a plug swap at the cabinet: in rotary mode the torch
runs along Y on the two squared Y motors, the tube turns on what the controller thinks is X, and the X
carriage stays where it was put. The tube lies along Y on the tool-axis centre line (X575), held in a
four-jaw chuck at the BACK of the machine, over the water pan; long tubes go out the front over the low
front cross tubes, and the bed module's exit path (it slides out of the front window 70 mm up) stays
clear. A first draft put the chuck at the front and the hoist check caught it.

Parts (ROT_*), all on the frame, nothing on the bed module:
  - A U of 2 x 4 x .083 in steel tube on edge (two rails and a tie) sitting on the rear upper cross tube
    (MF_END_REAR_UPPER) and cantilevered 190 mm behind it, held by two M10 through-bolts in sleeves welded
    through the cross tube before the frame is filled (bolts and sleeves are not drawn), with a 1/4 in
    plate on top: the rotary's shelf. The rails start at the cross tube's front face, behind the bed
    module's rear edge.
  - The rotary unit as an allocation: a 210 x 200 x 175 body (spindle housing, belt reduction, NEMA 23 on
    the X driver) and a Ø125 x 65 four-jaw chuck (K72-125 class, hollow) facing the machine. Axis
    Z954.35, chuck face at Y1363, 15 mm behind the bed module's rear edge (Y1347.8), so the rotary stays
    fitted for router work.
  - The workpiece as an allocation: a round tube along Y from 20 mm inside the jaws, forward over the pan.
The unit's real footprint, holes, through-bore and height come from the delivered rotary.
"""
from cad_helpers import PURCHASED, bbox, box, cyl, place

PREFIX = 'ROT_'
BLUE = (.12, .48, .65)
MAGENTA = (.75, .25, .62)
T_W, T_H, T_WALL = 50.8, 101.6, 2.108     # 2 x 4 x .083 in tube, on edge
REAR_TUBE = 'MF_END_REAR_UPPER'           # the frame's rear upper cross tube: the shelf sits on it
RAIL_L = 240.0                            # rails from the cross tube's front face, back past its rear face
SHELF_X = (465.0, 685.0)                  # rails' outer faces, across the tool axis
PLATE_T = 6.35
AXIS_X = 575.0
AXIS_ABOVE_PLATE = 116.35                 # allocation: base plate to spindle axis
BODY = (470.0, 680.0, 200.0, 175.0)       # x0, x1, length along Y, height on the plate
CHUCK_D, CHUCK_L = 125.0, 65.0
MODULE_REAR_Y = 1347.8                    # the bed module's rear edge (Rev J)
CHUCK_FACE_Y = 1363.0                     # 15.2 mm behind the module, facing forward
TUBE_IN_JAWS = 20.0
TUBE_D, TUBE_WALL = 60.0, 3.0             # the checked workpiece
TUBE_L = 1200.0
MAX_TORCH_Y = 1275.0 - 201.4              # torch axis at the gantry's rear stop (Rev K offset): 1073.6
BOUGHT_KG = {'ROTARY_AXIS_ALLOCATION': 9.0, 'ROTARY_CHUCK_K72_125_ALLOCATION': 4.5}
HOLDS = ['ROTARY: the unit, its chuck and its through-bore are allocations (Ø125 four-jaw, hollow, belt reduction, NEMA 23). '
         'Drill the shelf plate from the delivered base; the axis height sets the touch-off heights below.',
         'ROTARY: the X motor plug swap must be made with the 48 V off (E-stop pressed). Hot-plugging a stepper driver damages it.',
         'ROTARY: the X carriage is not held while its motor is unplugged; a ball screw back-drives. Do not push on the gantry '
         'during a tube job, and re-home X after swapping back.',
         'ROTARY: two M10 sleeves through the rear upper cross tube, welded before the frame is filled, take the shelf bolts.']


def _add(m, name, shape, origin=(0, 0, 0), **kw):
    kw.setdefault('group', 'rotary')
    return m.add(PREFIX + name, shape, origin, **kw)


def rect_tube(length, w=T_W, h=T_H, wall=T_WALL):
    """Tube along local X, width w across local Y, height h along local Z."""
    return box(length, w, h).cut(box(length + 2, w - 2 * wall, h - 2 * wall).translate((-1, wall, wall))).clean()


def add_bracket(m):
    """The U on the rear cross tube and the shelf plate."""
    tb = bbox(m.find(REAR_TUBE).shape)
    y0, z0 = tb[1], tb[5]                  # cross tube front face and top
    y1 = y0 + RAIL_L
    ids = []
    sx0, sx1 = SHELF_X
    for side, x in (('L', sx0), ('R', sx1 - T_W)):
        r = _add(m, f'RAIL_{side}', place(rect_tube(RAIL_L), (x + T_W, y0, z0), u=(0, 1, 0), v=(-1, 0, 0)), pn='ROT_RAIL_2x4_240',
                 material='2 x 4 x .083 in steel rectangular tube, on edge', length=RAIL_L, color=BLUE,
                 notes=[f'On the rear upper cross tube from its front face (Y{y0:g}) to Y{y1:g}, {RAIL_L - (tb[4] - y0):g} mm behind it. One M10 x 130 '
                        f'through-bolt at Y{(y0 + tb[4]) / 2:g} in a sleeve welded through the cross tube (not drawn).'])
        ids.append(r.id)
    tie = _add(m, 'TIE', rect_tube(sx1 - sx0 - 2 * T_W), (sx0 + T_W, y1 - T_W, z0), pn='ROT_TIE_2x4_118',
               material='2 x 4 x .083 in steel rectangular tube, on edge', length=sx1 - sx0 - 2 * T_W, color=BLUE,
               notes=['Closes the U between the two rails at the back; welded.'])
    ids.append(tie.id)
    plate = m.add_plate(PREFIX + 'PLATE', sx1 - sx0, RAIL_L, PLATE_T, origin=(sx0, y0, z0 + T_H), pn='ROT_SHELF_PLATE_220x240',
                        group='rotary', color=BLUE, material='A36 steel plate 1/4 in',
                        notes=[f'{sx1 - sx0:g} x {RAIL_L:g} x {PLATE_T:g} on the U, welded. The rotary\'s base bolts through it: drill from the '
                               'delivered unit (no holes drawn).'])
    ids.append(plate.id)
    return ids, z0 + T_H + PLATE_T, (y0, y1)


def add_rotary(m, plate_top):
    """The rotary unit and its chuck (allocations), chuck toward the machine."""
    x0, x1, length, h = BODY
    axis_z = plate_top + AXIS_ABOVE_PLATE
    body_y0 = CHUCK_FACE_Y + CHUCK_L
    body = _add(m, 'UNIT_ALLOCATION', box(x1 - x0, length, h), (x0, body_y0, plate_top), pn='ROTARY_AXIS_ALLOCATION', group='rotary_allocation',
                purchased=True, color=MAGENTA, release='SUPPLIER ALLOCATION - NOT A PURCHASED-PART DRAWING',
                material='Hollow rotary axis, belt reduction, NEMA 23: allocation only',
                notes=[f'{x1 - x0:g} x {length:g} x {h:g} envelope on the shelf: spindle housing, belt reduction (about 6:1) and the NEMA 23 '
                       f'stepper on the X driver. Spindle axis at Z{axis_z:g}, X{AXIS_X:g}. Real size, holes and bore from the delivered unit.'])
    chuck = _add(m, 'CHUCK_ALLOCATION', place(cyl(CHUCK_D, CHUCK_L), (AXIS_X, body_y0, axis_z), u=(1, 0, 0), v=(0, 0, 1)),
                 pn='ROTARY_CHUCK_K72_125_ALLOCATION', group='rotary_allocation', purchased=True, color=MAGENTA,
                 release='SUPPLIER ALLOCATION - NOT A PURCHASED-PART DRAWING', material='K72-125 class four-jaw independent chuck: allocation only',
                 notes=[f'Ø{CHUCK_D:g} x {CHUCK_L:g}, face at Y{CHUCK_FACE_Y:g} toward the machine, {CHUCK_FACE_Y - MODULE_REAR_Y:.1f} mm behind the bed '
                        f'module\'s rear edge. Independent jaws centre round and square tube. The torch axis comes back to Y{MAX_TORCH_Y:.1f}, so a '
                        f'tube end can be notched {CHUCK_FACE_Y - MAX_TORCH_Y:.0f} mm from the jaws.'])
    return [body.id, chuck.id], axis_z


def add_tube(m, axis_z, length=TUBE_L, d=TUBE_D, wall=TUBE_WALL):
    """A round tube along Y, forward from 20 mm inside the jaws (allocation)."""
    y_start = CHUCK_FACE_Y + TUBE_IN_JAWS
    solid = cyl(d, length).cut(cyl(d - 2 * wall, length + 2).translate((0, 0, -1))).clean()
    tube = _add(m, 'TUBE_ALLOCATION', place(solid, (AXIS_X, y_start, axis_z), u=(1, 0, 0), v=(0, 0, 1)), pn=f'ROT_TUBE_D{d:g}x{length:g}_ALLOCATION',
                group='rotary_workpiece', purchased=True, color=(.55, .55, .58), release='WORKPIECE ALLOCATION',
                material=f'Round steel tube Ø{d:g} x {wall:g} wall, {length:g} long: workpiece allocation',
                notes=[f'Along Y from Y{y_start:g} ({TUBE_IN_JAWS:g} mm inside the jaws) forward to Y{y_start - length:g}, on the spindle axis '
                       f'Z{axis_z:g}. Top at Z{axis_z + d / 2:g}, bottom at Z{axis_z - d / 2:g}.'])
    m.permit(tube.id, PREFIX + 'CHUCK_ALLOCATION', 'The jaws grip the tube end (allocation).')
    return tube.id, {'d_mm': d, 'length_mm': length, 'y_mm': [y_start - length, y_start], 'top_z_mm': axis_z + d / 2, 'bottom_z_mm': axis_z - d / 2}


def extend_model(m, tube_length=None, tube_d=TUBE_D):
    """Bracket and rotary on the frame; optionally a tube in the chuck."""
    bracket, plate_top, rail_y = add_bracket(m)
    unit, axis_z = add_rotary(m, plate_top)
    info = {'status': 'ROTARY AXIS FOR TUBE NOTCHING: WORKING CAD, ALLOCATIONS FOR THE UNIT AND THE WORKPIECE',
            'mount': 'on the rear upper cross tube; the bed module slides out of the front window, which stays clear',
            'axis_xz_mm': [AXIS_X, round(axis_z, 3)], 'chuck_face_y_mm': CHUCK_FACE_Y, 'plate_top_z_mm': round(plate_top, 3),
            'rail_y_mm': [round(v, 3) for v in rail_y], 'shelf_x_mm': list(SHELF_X),
            'torch_max_y_mm': round(MAX_TORCH_Y, 1), 'shortest_reach_from_jaws_mm': round(CHUCK_FACE_Y - MAX_TORCH_Y, 1),
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
