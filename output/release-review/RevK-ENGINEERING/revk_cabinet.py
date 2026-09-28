"""GM1 Rev K control cabinet: the Rev I VEVOR box with the review's cabinet findings fixed.

Rev I's cabinet (`service_finish._cabinet`) is built first, then changed:

- Door: the Rev F drip cap's 20 mm front lip hung 9.5 mm below the new box top and
  stopped a side-hinged door at about 2.4 degrees. Its lip is now 8 mm, so its lower
  edge is 2.5 mm above the box top and the door swings under it.
- Cable entries: two 175 x 150 bottom gland plates with 145 x 120 windows replace the
  Rev I 175 x 110 plates. Power plate: 4 x M25 (mains in, VFD supply, cutter supply,
  spare) and 6 x M20 (four motors, Z brake, spare). Signal plate: 20 x M16. 30 entries
  for about 28 field cables. Plates are bare stainless, bonded to the PE stud.
- Heat: the sealed box sheds about 33 W at 10 K rise; the Rodent, supplies, relays and
  contactors inside make about 60 W. An IP54 filter fan low on the left wall and an
  exhaust filter high on the right wall carry it out (about 20 m3/h needed for 10 K).
  The VFD (45-110 W of loss) is outside the box, on a plate welded to the cage's right
  upright and stringer, under its own drip roof, with 100 mm of air above and below.
- The torch-start relay moves to a shielded box at the cutter (controls README), so no
  HF-exposed lead enters this cabinet.
"""
import math

from cad_helpers import PURCHASED, HARDWARE, box, cyl, place
from frame_details import hexpart
import controls_packaging as cp
import service_finish as rev_i

BODY_ORIGIN = (375.0, 255.0, 165.0)
PLATE = dict(w=175.0, h=150.0, t=2.0, y=300.0, window=(15.0, 15.0, 160.0, 135.0))
CORNERS = [(10.0, 10.0), (165.0, 10.0), (10.0, 140.0), (165.0, 140.0)]
M25, M20, M16 = 25.5, 20.5, 16.5
POWER_HOLES = ([(x, 38.0, M25) for x in (38.0, 76.0, 114.0)] + [(x, 76.0, M20) for x in (32.0, 64.0, 96.0, 128.0)]
               + [(32.0, 113.0, M20), (64.0, 113.0, M20), (110.0, 113.0, M25)])
SIGNAL_HOLES = [(x, y, M16) for y in (30.0, 56.0, 82.0, 108.0) for x in (30.0, 56.0, 82.0, 108.0, 134.0)]
FAN = dict(y=355.0, z_in=275.0, z_out=545.0, frame=150.0, cut=125.0)
LIP = 8.0
HEAT_W = {'48 V supply (about 150 W out at 89 %)': 19, '24 V supply': 5, 'Rodent drivers and ESP32': 12,
          'K1/K2 contactor coils (LC1D18BD, 5.4 W each)': 10.8, 'G7SA relays (8)': 3.5, 'Finder relays and timers': 8,
          'Safety relay': 2.5, 'SSRs, THCAD, interface board': 2}


def _body(m):
    body = m.find('I_CABINET_BODY')
    shell = box(400, 200, 500).cut(box(397, 198.5, 497).translate((1.5, 0, 1.5)))
    for x in (85, 315):
        for z in (25, 455):
            shell = shell.cut(place(cyl(6.6, 5), (x, 197, z), u=(1, 0, 0), v=(0, 0, -1)))
    wx0, wy0, wx1, wy1 = PLATE['window']
    for px in (385.0, 590.0):
        lx, ly = px - BODY_ORIGIN[0], PLATE['y'] - BODY_ORIGIN[1]
        shell = shell.cut(box(wx1 - wx0, wy1 - wy0, 5).translate((lx + wx0, ly + wy0, -1)))
        for cx, cy in CORNERS:
            shell = shell.cut(cyl(5.5, 5).translate((lx + cx, ly + cy, -1)))
    c = FAN['cut']
    ly = FAN['y'] - BODY_ORIGIN[1] - c / 2
    shell = shell.cut(box(5, c, c).translate((-1, ly, FAN['z_in'] - BODY_ORIGIN[2] - c / 2)))
    shell = shell.cut(box(5, c, c).translate((397, ly, FAN['z_out'] - BODY_ORIGIN[2] - c / 2)))
    body.local = shell.clean()
    body.shape = place(body.local, BODY_ORIGIN)
    body.notes = list(body.notes) + [
        'Rev K: two 145 x 120 floor windows (world X400..545 and X605..750, Y315..435) under the gland plates, eight Ø5.5 plate holes, '
        f'and two {c:g} x {c:g} side cutouts: fan inlet on the left wall centred Y{FAN["y"]:g} Z{FAN["z_in"]:g}, exhaust filter on the right '
        f'wall centred Y{FAN["y"]:g} Z{FAN["z_out"]:g}. With the fan the box is IP54, not IP65.']


def _glands(m):
    rev_i._remove(m, [p.id for p in m.parts if p.id.startswith('I_CAB_GLAND_')])
    entries = []
    for tag, px, holes in (('POWER', 385.0, POWER_HOLES), ('SIGNAL', 590.0, SIGNAL_HOLES)):
        w, h, t = PLATE['w'], PLATE['h'], PLATE['t']
        wx0, wy0, wx1, wy1 = PLATE['window']
        m.add_plate('K_CAB_GLAND_' + tag, w, h, t, holes=holes + [(x, y, 5.5) for x, y in CORNERS], origin=(px, PLATE['y'], 161),
                    group='controls_glands', material='304 stainless 2 mm, bare (EMC bonding face)',
                    notes=[f'{len(holes)} entries: ' + ', '.join(f'{sum(1 for hh in holes if hh[2] == d)} x M{int(d - .5)}' for d in sorted({hh[2] for hh in holes})) + '.',
                           'EMC glands (nickel-plated brass, 360-degree shield contact) on the motor, VFD-control, THCAD, head and '
                           'torch-start cables; plain nylon glands elsewhere; rated blanking plugs in spare entries.',
                           'Bond the plate to the cabinet PE stud with a 16 mm² braid; use serrated washers under the four M5 nuts. '
                           'Keep 230 V (power plate, row 1) and motor cables apart from the signal plate inside the box.'])
        opening = [(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)]
        m.add_plate('K_CAB_GLAND_GASKET_' + tag, w, h, 2, holes=[(x, y, 5.5) for x, y in CORNERS], internal=[opening],
                    origin=(px, PLATE['y'], 163), group='controls_glands', material='2 mm closed-cell EPDM',
                    notes=['Knife-cut around the 145 x 120 window. Ingress test after assembly.'])
        for i, (cx, cy) in enumerate(CORNERS, 1):
            bolt = cyl(8.5, 5).fuse(cyl(5, 16).translate((0, 0, 5))).clean()
            m.add(f'K_CAB_GLAND_{tag}_BOLT_{i}', bolt, origin=(px + cx, PLATE['y'] + cy, 156), pn='STD_M5x16_HEAD_DOWN',
                  purchased=True, group='controls_glands', color=HARDWARE)
            m.add(f'K_CAB_GLAND_{tag}_NUT_{i}', hexpart(8, 4, 5), origin=(px + cx, PLATE['y'] + cy, 166.5), pn='STD_M5_NYLOC',
                  purchased=True, group='controls_glands', color=HARDWARE)
        entries.append({'plate': tag, 'bounds_mm': [px, PLATE['y'], 161, px + w, PLATE['y'] + h, 163],
                        'entries': [[round(px + x, 1), round(PLATE['y'] + y, 1), f'M{int(d - .5)}'] for x, y, d in holes]})
    return entries


def _fans(m):
    f, c = FAN['frame'], FAN['cut'] - 1
    y0 = FAN['y'] - f / 2
    inlet = box(20, f, f).translate((-20, 0, 0)).fuse(box(40, c, c).translate((0, (f - c) / 2, (f - c) / 2))).clean()
    m.add('K_CAB_FILTER_FAN', inlet, origin=(375.0, y0, FAN['z_in'] - f / 2), pn='K_FILTER_FAN_IP54_120', group='controls_envelope',
          purchased=True, color=PURCHASED, material='Purchased IP54 filter fan (envelope)', release='PURCHASED ENVELOPE - SELECT IP54 FILTER FAN, 24 V DC, 40 M3/H OR MORE FREE-BLOWING',
          notes=['150 x 150 frame outside the left wall, 124 x 124 x 40 fan body inside through a 125 x 125 cutout. Blows in, low.',
                 'Keep components on the backplate at least 45 mm clear of the left wall in front of the fan.'])
    outlet = box(20, f, f).fuse(box(15, c, c).translate((-15, (f - c) / 2, (f - c) / 2))).clean()
    m.add('K_CAB_EXHAUST_FILTER', outlet, origin=(775.0, y0, FAN['z_out'] - f / 2), pn='K_EXHAUST_FILTER_IP54_120',
          group='controls_envelope', purchased=True, color=PURCHASED, material='Purchased IP54 outlet filter (envelope)',
          release='PURCHASED ENVELOPE - MATCHING IP54 OUTLET FILTER (SAME MAKER AND SIZE AS THE FAN)',
          notes=['150 x 150 frame outside the right wall, high; 15 mm inside through the 125 x 125 cutout.'])
    losses = sum(HEAT_W.values())
    passive = 5.5 * .6 * 10
    return {'inside_losses_w': HEAT_W, 'inside_total_w': round(losses, 1), 'sealed_box_capacity_at_10k_w': round(passive, 1),
            'airflow_for_10k_m3_h': round(3.1 * losses / 10, 1), 'fan': 'IP54 filter fan, 24 V DC, 40 m3/h or more free-blowing',
            'vfd': 'outside the box (45-110 W loss for a 1.5-2.2 kW unit)'}


def _drip_lip(m):
    old = m.find('CAB_DRIP_FRONT_LIP')
    m.parts.remove(old)
    m.add_plate('K_CAB_DRIP_FRONT_LIP', cp.CAP_W, LIP, cp.CAP_T, origin=cp.cap_point(0, cp.CAP_T, -LIP), u=(1, 0, 0), v=cp.CAP_N,
                group='controls_shield', material='Mild steel 1.5 mm',
                notes=[f'Flat {cp.CAP_W:g} x {LIP:g} x 1.5 front drip lip (was 20 mm). Lower edge Z{cp.CAP_ORIGIN[2] - LIP:g}, 2.5 mm above the box top '
                       '(Z665), so a side-hinged door swings under it. Continuous sealed weld to the roof underside.'])
    return {'lip_height_mm': LIP, 'lip_bottom_z_mm': cp.CAP_ORIGIN[2] - LIP, 'box_top_z_mm': BODY_ORIGIN[2] + 500,
            'clearance_mm': cp.CAP_ORIGIN[2] - LIP - (BODY_ORIGIN[2] + 500)}


def _vfd(m):
    m.add_plate('K_VFD_PLATE', 210.4, 389.2, 3, origin=(822.7, 270.0, 290.0), u=(0, 1, 0), v=(0, 0, 1), group='controls_support',
                material='A36 steel 3 mm',
                notes=['Welded along the right faces of cage upright 2 (Y455..480.4) and stringer 2 (Z653.8..679.2). '
                       'Drill the VFD fixing holes to the received unit; mount it with its air inlet down.'])
    m.add('K_VFD_ENVELOPE', box(180, 160, 250), origin=(825.7, 290.0, 320.0), pn='OWNER_SPINDLE_VFD', group='controls_envelope',
          purchased=True, color=PURCHASED, material='Owner spindle VFD (envelope)', release='OWNER VFD NOT IDENTIFIED - ENVELOPE FOR A 1.5-2.2 KW UNIT',
          notes=['180 deep x 160 wide x 250 tall, keypad facing +X (read from the right side of the machine).',
                 'Keep 100 mm clear above (to the drip roof) and below for its fan. Supply from the cabinet power plate through K1/K2; '
                 'FWD/COM and the isolated 0-10 V from the signal plate; shielded spindle cable, shield bonded at both ends.'])
    m.add_plate('K_VFD_DRIP_ROOF', 200, 240, 1.5, origin=(825.7, 255.0, 672.0), group='controls_shield', material='Mild steel 1.5 mm',
                notes=['Flat roof over the VFD, welded to the plate edge and two gussets; turn down a 10 mm lip on the three free edges.'])
    for i, y in enumerate((288.0, 468.0), 1):
        m.add_plate(f'K_VFD_ROOF_GUSSET_{i}', 60, 60, 3, outline=[(0, 0), (0, 60), (60, 60)], origin=(825.7, y, 612.0),
                    u=(1, 0, 0), v=(0, 0, 1), pn='K_VFD_ROOF_GUSSET', group='controls_support', material='A36 steel 3 mm',
                    notes=['Triangle 60 x 60: vertical edge welded to the VFD plate, top edge to the roof underside.'])
    return {'plate_bounds_mm': [822.7, 270, 290, 825.7, 480.4, 679.2], 'vfd_envelope_mm': [825.7, 290, 320, 1005.7, 450, 570],
            'roof_z_mm': 672, 'air_gap_above_mm': 102}


def extend_router_model(m):
    base = rev_i._cabinet(m)
    _body(m)
    glands = _glands(m)
    return {'revision': 'K cabinet', 'rev_i_cabinet': base, 'gland_plates': glands,
            'entry_count': len(POWER_HOLES) + len(SIGNAL_HOLES), 'heat': _fans(m), 'door_drip_lip': _drip_lip(m), 'vfd': _vfd(m),
            'torch_start_relay': 'In a shielded box at the cutter (controls README); not in this cabinet.'}
