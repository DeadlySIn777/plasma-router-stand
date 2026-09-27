"""GM1 Rev L: move the frame's fill ports to the high end of each tube, so every tube can be filled full.

Rev K, and the shared RevE frame (`frame_details.py`), give each of the 18 frame tubes one sealed compartment
and one fill port: a Ø30 weld bung with an M20 x 1.5 plug. Those ports were placed for access, not for
filling. The top rails' ports are on the outer face at mid-height, the front cross tubes' on the front face,
the legs' 200 mm below the top, and the others at mid-length on top. Poured with the frame standing, the fill
reaches only part of several tubes. The design counted the sand as mass and damping only ("weigh the fill").

Rev L keeps one port per tube, with the same bung and plug, and moves it to the tube's high end for a defined
fill attitude. That suits epoxy sand, which the owner is considering, and dry sand:
  legs                     35 mm below the top (Z965). Outer face on the front legs. Rear face on the
                           others, whose outer faces carry the side-brace gussets there.
  front-to-back tubes (Y)  the rear end. The top rails' ports are in their rear end caps. The lower side
                           tubes' ports are on top, 40 mm from the rear end. The bed ledgers keep theirs
                           (top face, Y1370).
  cross tubes (X)          the right-hand end, on top where the face is free. The front lower tube's port
                           is on its front face; the rear upper tube's sits just inboard of the right ledger.
Fill attitudes:
  epoxy sand  self-levels. Stage 1: the frame's rear end raised about 15 degrees; pour the legs and the
              front-to-back tubes. Stage 2, after it cures: the right side raised about 15 degrees; pour
              the cross tubes.
  dry sand    does not run along a tube at those angles. Fill each tube near vertical: the legs with the
              frame upright, the front-to-back tubes with it on its front end, the cross tubes with it on
              its left side.
The old holes are closed in the model by restoring the tube wall; nothing else in the frame changes.
`fill_estimates` samples each tube's cavity against the level through its port's lowest opening point.
"""
import math

import cadquery as cq
from cad_helpers import bbox, cyl, pipe, place
from frame_details import edit_global, hexpart

WALL = 3.048
BORE_R = 9.25                  # M20 x 1.5 tap drill 18.5: the opening left when the plug is out
TILT_DEG = 15.0
OLD_NOTE = 'Sandserviceport:Ø30weldbung,M20×1.5removableplug. Fillonlyafterallwelding/coating;weightactualdryballast.'
NOTE = ('Fill port (Rev L): Ø30 weld bung and M20×1.5 plug at this tube\'s high end, for the fill attitude in '
        'RevL-CAD/BUILD-ORDER.md. Fill only after all welding, drilling and coating, with epoxy sand or dry sand; '
        'weigh the fill.')
CAP_PN = 'SAND_ENDCAP_2IN_PORTED'
CAP_NOTE = 'Rev L: carries the top rail\'s fill port (Ø30 hole, weld bung and M20×1.5 plug).'
BUNG_NOTE = 'OD30×10;M20×1.5female,predrill18.5beforetap;nominalthreadenvelopeinSTEP. Continuouswatertightweldtotube.'
PLUG_NOTE = 'Turn20mmthread×10long,28mmhead×6,6mmhexsocket4deep;sealwasherorremovabledustsealant.'

# Stages: the "up" direction in machine coordinates while each group is poured.
UP = {
    'upright': (0.0, 0.0, 1.0),
    'rear_up': (0.0, math.sin(math.radians(TILT_DEG)), math.cos(math.radians(TILT_DEG))),
    'right_up': (math.sin(math.radians(TILT_DEG)), 0.0, math.cos(math.radians(TILT_DEG))),
    'on_front_end': (0.0, 1.0, 0.0),
    'on_left_side': (1.0, 0.0, 0.0),
}

# (tube, part carrying the port, where, point on the outer face, u, v); outward normal = u x v.
# Epoxy stage and dry-sand attitude for each group follow the module docstring.
PORTS = [
    ('MF_LEG_1_1', 'MF_LEG_1_1', 'outer face, 35 mm below the top', (0.0, 25.4, 965.0), (0, 1, 0), (0, 0, -1)),
    ('MF_LEG_1_2', 'MF_LEG_1_2', 'rear face, 35 mm below the top', (25.4, 750.4, 965.0), (-1, 0, 0), (0, 0, 1)),
    ('MF_LEG_1_3', 'MF_LEG_1_3', 'rear face, 35 mm below the top', (25.4, 1450.0, 965.0), (-1, 0, 0), (0, 0, 1)),
    ('MF_LEG_2_1', 'MF_LEG_2_1', 'outer face, 35 mm below the top', (1150.0, 25.4, 965.0), (0, 1, 0), (0, 0, 1)),
    ('MF_LEG_2_2', 'MF_LEG_2_2', 'rear face, 35 mm below the top', (1124.6, 750.4, 965.0), (-1, 0, 0), (0, 0, 1)),
    ('MF_LEG_2_3', 'MF_LEG_2_3', 'rear face, 35 mm below the top', (1124.6, 1450.0, 965.0), (-1, 0, 0), (0, 0, 1)),
    ('MF_TOP_Y_1', 'SAND_ENDCAP_TOP_L_REAR', 'rear end cap', (25.4, 1453.048, 1024.6), (-1, 0, 0), (0, 0, 1)),
    ('MF_TOP_Y_2', 'SAND_ENDCAP_TOP_R_REAR', 'rear end cap', (1124.6, 1453.048, 1024.6), (-1, 0, 0), (0, 0, 1)),
    ('MF_LOWER_SIDE_1_1', 'MF_LOWER_SIDE_1_1', 'top face, 40 mm from the rear end', (25.4, 659.6, 280.8), (1, 0, 0), (0, 1, 0)),
    ('MF_LOWER_SIDE_1_2', 'MF_LOWER_SIDE_1_2', 'top face, 40 mm from the rear end', (25.4, 1359.2, 280.8), (1, 0, 0), (0, 1, 0)),
    ('MF_LOWER_SIDE_2_1', 'MF_LOWER_SIDE_2_1', 'top face, 40 mm from the rear end', (1124.6, 659.6, 280.8), (1, 0, 0), (0, 1, 0)),
    ('MF_LOWER_SIDE_2_2', 'MF_LOWER_SIDE_2_2', 'top face, 40 mm from the rear end', (1124.6, 1359.2, 280.8), (1, 0, 0), (0, 1, 0)),
    ('MF_RECEIVER_LEDGER_1', 'MF_RECEIVER_LEDGER_1', 'top face at Y1370, unchanged', (76.2, 1370.0, 840.0), (1, 0, 0), (0, 1, 0)),
    ('MF_RECEIVER_LEDGER_2', 'MF_RECEIVER_LEDGER_2', 'top face at Y1370, unchanged', (1073.8, 1370.0, 840.0), (1, 0, 0), (0, 1, 0)),
    ('MF_END_FRONT_LOW', 'MF_END_FRONT_LOW', 'front face, right end', (1069.2, 0.0, 75.4), (1, 0, 0), (0, 0, 1)),
    ('MF_END_FRONT_UPPER', 'MF_END_FRONT_UPPER', 'top face, right end', (1069.2, 25.4, 151.6), (1, 0, 0), (0, 1, 0)),
    ('MF_END_REAR_LOW', 'MF_END_REAR_LOW', 'top face, right end', (1069.2, 1424.6, 280.8), (1, 0, 0), (0, 1, 0)),
    ('MF_END_REAR_UPPER', 'MF_END_REAR_UPPER', 'top face, inboard of the right ledger', (1020.0, 1424.6, 730.0), (1, 0, 0), (0, 1, 0)),
]


def _group(tube):
    if 'LEG_' in tube:
        return 'leg'
    return 'x_tube' if tube.startswith('MF_END_') else 'y_tube'


EPOXY_STAGE = {'leg': 'rear_up', 'y_tube': 'rear_up', 'x_tube': 'right_up'}
DRY_ATTITUDE = {'leg': 'upright', 'y_tube': 'on_front_end', 'x_tube': 'on_left_side'}


def _vec(t):
    return cq.Vector(*t)


def _frame_for(n):
    """Unit u, v with u x v = n."""
    n = n.normalized()
    a = cq.Vector(1, 0, 0) if abs(n.x) < 0.9 else cq.Vector(0, 1, 0)
    u = a.cross(n).normalized()
    v = n.cross(u).normalized()
    return u, v


def _old_ports(m):
    """The inherited ports, from the SAND_BUNG parts: (tube id, outer-face point, outward normal)."""
    tubes = [p for p in m.parts if p.group == 'main_frame']
    out = []
    for b in [p for p in m.parts if p.id.startswith('SAND_BUNG_')]:
        bb = bbox(b.shape)
        ext = [bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]]
        k = min(range(3), key=lambda i: abs(ext[i] - 10.0))
        c = [(bb[i] + bb[i + 3]) / 2 for i in range(3)]
        owner = None
        for t in tubes:
            tb = bbox(t.shape)
            if all(tb[i] - 0.1 <= c[i] <= tb[i + 3] + 0.1 for i in range(3) if i != k):
                if tb[k] - 12 <= c[k] <= tb[k + 3] + 12:
                    owner = t
                    break
        assert owner is not None, b.id
        tb = bbox(owner.shape)
        sign = 1.0 if c[k] > (tb[k] + tb[k + 3]) / 2 else -1.0
        n = [0.0, 0.0, 0.0]
        n[k] = sign
        origin = tuple(c[i] + n[i] * (WALL - 5.0) for i in range(3))
        out.append((owner.id, origin, tuple(n)))
    return out


def _add_port(m, index, tube, carrier, origin, u, v):
    n = _vec(u).cross(_vec(v))
    p0 = tuple(origin[k] - n.toTuple()[k] * WALL for k in range(3))
    m.add(f'SAND_BUNG_{index}', pipe(10, 30, 20), origin=p0, u=u, v=v, pn='SAND_M20_BUNG', group='ballast',
          material='Machinedmildsteel', notes=[BUNG_NOTE, f'Rev L: fill port for {tube}.'])
    plug = cyl(20, 10).fuse(cyl(28, 6).translate((0, 0, 10))).cut(hexpart(6, 4).translate((0, 0, 12))).clean()
    m.add(f'SAND_PLUG_{index}', plug, origin=p0, u=u, v=v, pn='SAND_M20_PLUG', group='ballast',
          material='CustomM20×1.5steelplug', notes=[PLUG_NOTE])


def apply(m):
    """Move the fill ports in model m (a Rev K router model before motion is added). Returns a record."""
    old = _old_ports(m)
    assert len(old) == 18, len(old)
    restored, kept = [], []
    for tube, origin, n in old:
        if any(t == tube and max(abs(origin[k] - o[k]) for k in range(3)) < 0.05 for t, _, _, o, _, _ in PORTS):
            kept.append(tube)
            continue
        nv = _vec(n)
        u, v = _frame_for(nv)
        p0 = tuple(origin[k] - n[k] * WALL for k in range(3))
        part = m.find(tube)
        before = part.shape.Volume()
        part.shape = part.shape.fuse(place(cyl(30, WALL), p0, u.toTuple(), v.toTuple())).clean()
        added = part.shape.Volume() - before
        assert abs(added - math.pi * 15 ** 2 * WALL) < 5.0, (tube, added)
        pb = bbox(part.shape)
        part.local = part.shape.translate(tuple(-x for x in pb[:3]))
        restored.append({'tube': tube, 'old_port_mm': [round(x, 2) for x in origin], 'wall_restored_mm3': round(added, 1)})
    for p in m.parts:
        if p.group == 'main_frame':
            p.notes = [x for x in p.notes if x != OLD_NOTE]
    for pid in [p.id for p in m.parts if p.id.startswith(('SAND_BUNG_', 'SAND_PLUG_'))]:
        m.remove(pid)
    ports = []
    for i, (tube, carrier, where, origin, u, v) in enumerate(PORTS, 1):
        n = _vec(u).cross(_vec(v))
        if tube not in kept:
            tool = place(cyl(30, 12).translate((0, 0, -6)), origin, u, v)
            edit_global(m, carrier, tool, NOTE if carrier == tube else CAP_NOTE)
            if carrier != tube:
                # A ported end cap is its own part: 50.8 square plate with the Ø30 hole at its centre.
                cap = m.find(carrier)
                cap.part_number = CAP_PN
                cap.flat = dict(cap.flat, holes=list(cap.flat['holes']) + [(25.4, 25.4, 30.0)])
        if carrier != tube or tube in kept:
            m.find(tube).notes.append(NOTE if carrier == tube else
                                      NOTE.replace('at this tube\'s high end', 'in this tube\'s rear end cap'))
        _add_port(m, i, tube, carrier, origin, u, v)
        ports.append({'tube': tube, 'carrier': carrier, 'where': where, 'outer_face_point_mm': list(origin),
                      'outward_normal': [round(x, 3) for x in n.toTuple()], 'group': _group(tube),
                      'epoxy_stage': EPOXY_STAGE[_group(tube)], 'dry_attitude': DRY_ATTITUDE[_group(tube)]})
    return {'ports': ports, 'restored_old_holes': restored, 'unchanged_ports': kept,
            'tilt_deg': TILT_DEG, 'bore_radius_mm': BORE_R, 'estimates': fill_estimates(m, ports, old)}


def _cavity(tube_bb):
    """Inner cavity box of a 2 x 2 x .120 tube: its bounding box less the wall on the two cross axes."""
    ext = [tube_bb[3] - tube_bb[0], tube_bb[4] - tube_bb[1], tube_bb[5] - tube_bb[2]]
    axis = max(range(3), key=lambda i: ext[i])
    lo = [tube_bb[i] + (0 if i == axis else WALL) for i in range(3)]
    hi = [tube_bb[i + 3] - (0 if i == axis else WALL) for i in range(3)]
    return lo, hi, axis


def _fraction(cavity, opening_low_height, up, samples=(8, 8, 160)):
    lo, hi, axis = cavity
    counts = [samples[2] if i == axis else samples[0] for i in range(3)]
    below = total = 0
    for a in range(counts[0]):
        x = lo[0] + (a + 0.5) * (hi[0] - lo[0]) / counts[0]
        for b in range(counts[1]):
            y = lo[1] + (b + 0.5) * (hi[1] - lo[1]) / counts[1]
            for c in range(counts[2]):
                z = lo[2] + (c + 0.5) * (hi[2] - lo[2]) / counts[2]
                total += 1
                if x * up[0] + y * up[1] + z * up[2] <= opening_low_height:
                    below += 1
    return below / total


def _opening_low(origin, n, up):
    """Height of the lowest point of the port's opening at the inner wall face, and whether the port faces down."""
    n = _vec(n).normalized()
    upv = _vec(up)
    inner = _vec(origin) - n * WALL
    d = upv - n * upv.dot(n)
    low = inner - (d.normalized() * BORE_R if d.Length > 1e-9 else cq.Vector(0, 0, 0))
    return low.dot(upv), n.dot(upv) < -0.02


def fill_estimates(m, ports, old):
    """Filled fraction of each tube's cavity: new ports in their stated attitudes, old ports with the frame level."""
    rows = []
    old_by_tube = {t: (o, n) for t, o, n in old}
    for p in ports:
        cav = _cavity(bbox(m.find(p['tube']).shape))
        rec = {'tube': p['tube']}
        for label, att in (('epoxy', p['epoxy_stage']), ('dry_sand', p['dry_attitude'])):
            h, down = _opening_low(p['outer_face_point_mm'], p['outward_normal'], UP[att])
            rec[label] = {'attitude': att, 'port_faces_down': down,
                          'filled_fraction': 0.0 if down else round(_fraction(cav, h, UP[att]), 3)}
        o, n = old_by_tube[p['tube']]
        h, down = _opening_low(o, n, UP['upright'])
        rec['old_port_frame_level_liquid'] = 0.0 if down else round(_fraction(cav, h, UP['upright']), 3)
        rows.append(rec)
    return rows
