"""The 300 mm Z slide on the Rev K motion model (GM1 Rev L), raised 125 mm over the tool changer.

Rev J's motion model (motion_details.make_motion, used unchanged) draws the
ZBX80 with a 100 mm stroke: body Z1040..1259 and spindle nut Z960..1060. The
300 mm slide keeps the spindle's lower datum. The body grows 200 mm upward and
the carriage travels 300 mm (nut Z960..1260). Positions above the 100 mm
model's range are reached by building at z_lift 100 and raising the carriage
parts.

Raise (27 Sep, after the owner's "when it retracts, or it moves forward it
will hit the autochanger"): the Z body's lower end block sat at Z1040, below
the magazine top (Z1130) and its lid, so the changer could only move with the
head parked out of its way. The body now sits RAISE (110) mm higher on the Z
carrier (Z1150..1569), and the tool adapter is 110 mm taller so the spindle
hangs where it did: the nut still runs Z960..1260 and the tool axis is
unchanged. The body's lower end is then level with the gantry's X blocks and
Z carrier (Z1143), which set the height under the gantry, and clears the
magazine's lid allocation (Z1132.35) by 17.65 mm. The changer can slide with
the head anywhere and the gantry can drive over the deployed magazine, with
Z up.
"""
from cad_helpers import bbox, box

import cadquery as cq

STROKE = 300.0
MODEL_STROKE = 100.0
EXTRA = STROKE - MODEL_STROKE
BODY_LENGTH = 219.0 + EXTRA          # stroke + 119; the 300 mm listing drawing gives 419
RAISE = 110.0                        # the Z body sits this much higher on the carrier than in Rev K
BODY_BOTTOM = 1040.0 + RAISE         # lower end block, Z1150, level with the gantry's X blocks and carrier (Z1143)
ADAPTER_H = 110.0 + RAISE            # the tool adapter grows upward by the raise
ADAPTER_PN = f'TOOL_ADAPTER_110x{int(ADAPTER_H)}_DROP'
# Parts that ride on the Z carriage (found by comparing the Rev K model at z_lift 0 and 100).
CARRIAGE = ('ZBX80_OUTPUT_HOLD', 'TOOL_ADAPTER_110', 'TOOL_CLAMP_MOUNT_', 'TOOL_CLAMP_PINCH_',
            'TOOL_SPLIT_CLAMP_', 'TOOL_SPINDLE_65x259')
RAISED = ('ZBX80_END_TOP', 'ZBX80_COUPLER_GUARD', 'ZBX80_MOTOR')
BODY = ('ZBX80_BASE', 'ZBX80_END_BOTTOM', 'ZBX80_END_TOP', 'ZBX80_COUPLER_GUARD', 'ZBX80_MOTOR', 'ZBX80_OUTPUT_HOLD')


def drop_adapter(model):
    """Replace TOOL_ADAPTER_110 with the taller plate: the same lower 110 mm (clamp pattern, plasma bracket
    mount), and the two carriage slots RAISE mm higher. Same id, so the existing permits and mounts still apply."""
    from cad_helpers import place, plate, rect
    a = model.find('TOOL_ADAPTER_110')
    bb = bbox(a.shape)
    origin = (bb[0], bb[4], bb[2])        # place(): local X -> +X, local Y -> +Z, thickness toward -Y
    holes = [h for h in a.flat['holes']]                               # the four 6.6 clamp holes (lower 110 mm)
    slots = [(x, y + RAISE, L, w, ang) for x, y, L, w, ang in a.flat['slots']]
    local = plate(rect(110.0, ADAPTER_H), 12.7, holes, slots)
    for x, y, d in holes:                                              # rear-face counterbores, as before
        local = local.cut(cq.Workplane('XY').circle(10.5 / 2).extrude(6).translate((x, y, 0)).val())
    cslot = cq.Compound.makeCompound([cq.Workplane('XY').center(sx, 45 + RAISE).slot2D(30, 11, 90).extrude(7.6).translate((0, 0, 6.1)).val()
                                      for sx in (20, 90)])
    local = local.cut(cslot).clean()
    a.local = local
    a.shape = place(local, origin, (1, 0, 0), (0, 0, 1))
    a.part_number = ADAPTER_PN
    a.flat = dict(a.flat, outline=rect(110.0, ADAPTER_H), slots=slots,
                  operations=[op for op in a.flat.get('operations', []) if op.get('type') == 'circle'] +
                             [{'type': 'slot', 'x': sx, 'y': 45 + RAISE, 'length': 30, 'width': 11, 'angle': 90, 'depth_mm': 6.6,
                               'face': 'front', 'layer': 'MILL_FRONT_COUNTERSLOT_DEPTH_6_6'} for sx in (20, 90)])
    a.material = '6061-T6 aluminum 12.7'
    a.notes = [f'Rev L drop adapter: 110 x {ADAPTER_H:g} x 12.7 plate. Its lower 110 mm is the Rev K adapter (four 6.6 clamp holes '
               'at X10/100, Y22/48 with 10.5 counterbores on the rear face: the shared spindle/torch clamp pattern), so the '
               'spindle clamp and the plasma drop bracket mount unchanged.',
               f'The two carriage slots (7 x 30 vertical, 70 mm centres, 11 x 6.6 front counter-slots) sit {RAISE:g} mm higher, '
               f'at the top, so the spindle hangs {RAISE:g} mm lower from the Z carriage than in Rev K and the Z body clears the tool changer.',
               'Provisional, as before: the carriage hole pitch, thread and the 80 mm output stack come from the delivered slide. '
               'Do not manufacture until the carriage is measured.',
               'Stiffness screen: a 12.7 plate, 110 wide, cantilevered 110 mm deflects about 0.04 mm per 100 N at the clamp '
               '(I = 18,800 mm^4). Light-duty cuts (10-20 N) give under 0.01 mm. Two side ribs would stiffen it if needed.']
    return a


def add_motion(model, gantry_y=1275.0, head_x=575.0, z_lift=STROKE):
    """Router motion at one pose with the 300 mm Z. z_lift is the carriage height above the lowest position."""
    import build_revj as rev_j
    assert 0 <= z_lift <= STROKE, z_lift
    base = min(z_lift, MODEL_STROKE)
    motion, completion = rev_j.add_motion(model, gantry_y=gantry_y, head_x=head_x, z_lift=base)
    body = model.find('ZBX80_BASE')
    origin = bbox(body.shape)[:3]
    body.local = box(80, 20, BODY_LENGTH)
    body.shape = body.local.translate(tuple(origin))
    body.part_number = 'RATTMOTOR_ZBX80_300'
    body.notes = [f'ZBX80 with a 300 mm stroke (Rev L). Body {BODY_LENGTH:g} x 80: the 300 mm listing drawing gives 419 x 80, '
                  '395 between the 12 mm end blocks and 530 with the motor; measure on receipt.',
                  f'Mounted {RAISE:g} mm higher on the Z carrier than Rev K (lower end block Z{BODY_BOTTOM:g}) so it clears the tool '
                  'changer. The carrier plate (Z1143-1313) overlaps the base over its lowest 163 mm: at least three M5 slide nuts '
                  'per base slot there.',
                  'Exact base-slot fastening interface remains HOLD; base fastening is measure-on-receipt.']
    for part in model.parts:
        if part.id in RAISED:
            part.shape = part.shape.translate((0, 0, EXTRA))
        if part.id in BODY:
            part.shape = part.shape.translate((0, 0, RAISE))
    drop_adapter(model)
    lift = z_lift - base
    moved = []
    if lift:
        for part in model.parts:
            if part.id.startswith(CARRIAGE):
                part.shape = part.shape.translate((0, 0, lift))
                moved.append(part.id)
        assert 'TOOL_ADAPTER_110' in moved and 'TOOL_SPINDLE_65x259' in moved, moved
    motion['configuration']['z_lift'] = z_lift
    motion['travel_mm']['Z'] = STROKE
    motion['z_slide'] = {'stroke_mm': STROKE, 'raise_mm': RAISE, 'body_z_mm': [origin[2] + RAISE, origin[2] + RAISE + BODY_LENGTH],
                         'spindle_nut_z_range_mm': [960.0, 960.0 + STROKE], 'adapter_height_mm': ADAPTER_H,
                         'motor_top_z_mm': round(bbox(model.find('ZBX80_MOTOR').shape)[5], 3)}
    return motion, completion
