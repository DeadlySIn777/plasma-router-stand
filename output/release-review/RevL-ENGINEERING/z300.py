"""The 300 mm Z slide on the Rev K motion model (GM1 Rev L).

Rev J's motion model (motion_details.make_motion, used unchanged) draws the
ZBX80 with a 100 mm stroke: body Z1040..1259 and spindle nut Z960..1060. The
300 mm slide keeps the lower datum. The body grows 200 mm upward (Z1040..1459),
the top end block, coupler guard and braked motor move up 200 mm, and the
carriage travels 300 mm (nut Z960..1260). Positions above the 100 mm model's
range are reached by building at z_lift 100 and raising the carriage parts.
"""
from cad_helpers import bbox, box

STROKE = 300.0
MODEL_STROKE = 100.0
EXTRA = STROKE - MODEL_STROKE
BODY_LENGTH = 219.0 + EXTRA          # stroke + 119, scaled from the 100 mm listing drawing
# Parts that ride on the Z carriage (found by comparing the Rev K model at z_lift 0 and 100).
CARRIAGE = ('ZBX80_OUTPUT_HOLD', 'TOOL_ADAPTER_110', 'TOOL_CLAMP_MOUNT_', 'TOOL_CLAMP_PINCH_',
            'TOOL_SPLIT_CLAMP_', 'TOOL_SPINDLE_65x259')
RAISED = ('ZBX80_END_TOP', 'ZBX80_COUPLER_GUARD', 'ZBX80_MOTOR')


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
    body.notes = [f'ZBX80 with a 300 mm stroke (Rev L). Body {BODY_LENGTH:g} x 80 assumed from the 100 mm drawing '
                  '(stroke + 119); measure on receipt. The lower end and the carriage\'s lowest position are unchanged.',
                  'Exact base-slot fastening interface remains HOLD; base fastening is measure-on-receipt.']
    for part in model.parts:
        if part.id in RAISED:
            part.shape = part.shape.translate((0, 0, EXTRA))
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
    motion['z_slide'] = {'stroke_mm': STROKE, 'body_z_mm': [origin[2], origin[2] + BODY_LENGTH],
                         'spindle_nut_z_range_mm': [960.0, 960.0 + STROKE],
                         'motor_top_z_mm': round(bbox(model.find('ZBX80_MOTOR').shape)[5], 3)}
    return motion, completion
