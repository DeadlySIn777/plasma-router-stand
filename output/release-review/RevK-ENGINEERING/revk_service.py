"""GM1 Rev K service: the other session's Rev I plumbing on the one-piece-bed line.

`service_finish.py` (Rev I) is used unchanged for the drain and the strainer
carrier. Its pressure hose was routed from the Rev H refill spout. Rev J moved that spout's riser to Y1215.4 with its 1/2 NPT end at Z665,
exactly where the Rev I hose centreline (Z665) starts, so Rev K lowers the whole
pressure route, its three split clamps and their bolts by 20 mm:

- A street elbow on the riser end turns the flow forward (-Y) and meets the
  hose at Z645. Its fitting zone sits below the riser end and behind the hose
  start, clear of pan bearer 3 (bottom Z679).
- The clamp straps grow from 45 to 65 mm so they still weld to bearer 3's
  front face above Z679.2.

The suction hose is rerouted without a high point. Rev I ran it up to Z710, over
the six-panel bed's staged hoops, and back down to the strainer inlet at Z620, so
air collected at the top. The one-piece bed has no hoops there, so Rev K runs the
rear leg at Z540 and enters the strainer end zone from below: the line only rises
from the pickup to the strainer. Two posts on standoffs from the tank's rear wall
replace the Rev I eyes that hung from the pan wall.

The cabinet is Rev K's own (`revk_cabinet.py`).
"""
import math
from cad_helpers import box, cyl, place, plate
from frame_details import hexpart
import service_finish as rev_i

DZ = -20.0
PRESSURE_POINTS = [(x, y, z + DZ) for x, y, z in rev_i.PRESSURE_POINTS]
PRESSURE_ARCS = [(i, (x, y, z + DZ)) for i, (x, y, z) in rev_i.PRESSURE_ARCS]
HOSE_Z = 665.0 + DZ
CLAMP_X = (500, 700, 850)


def _pressure_route(m):
    rev_i._remove(m, ['J_REFILL_CONNECTION_RESERVE', 'H_REFILL_CONNECTION_RESERVE'])
    s, length = rev_i._route(PRESSURE_POINTS, PRESSURE_ARCS)
    m.add_shape('I_REFILL_PRESSURE_HOSE', s, pn='PARKER_801_6_PRESSURE_ROUTE', group='water_hose', purchased=True,
                material='Parker 801-6 hose, 3/8 in ID', color=(.13, .15, .16), length=length,
                release='DEFINED ROUTE - FIELD-TRIM ENDS / APPROVED 82 SERIES CONNECTIONS STILL REQUIRED',
                notes=[rev_i.HOSE_SOURCE,
                       'Parker 801-6: 3/8 in nominal ID, 15.9 mm OD, 350 psi, 75 mm minimum bend radius. All three designed bends R80.',
                       f'Rev K route: the Rev I route lowered 20 mm (centreline Z{HOSE_Z:g}) to meet the Rev J spout riser end at Z665. '
                       'Use matching Parker 82 series fittings; the hose pressure rating exceeds the 120 psi pump shutoff.',
                       'Centreline length is routing length only; cut to the measured pump and spout fittings.'])
    m.add('K_REFILL_SPOUT_CONNECTION_ZONE', box(40, 26, 45), origin=(365, 1210, 620), group='water_hose_interface', purchased=True,
          material='Purchased fittings: space reservation',
          release='ADJUSTABLE END CONNECTION ZONE - RECEIPT SELECT 1/2 NPT STREET ELBOW AND 82 SERIES ADAPTER',
          notes=['Fitting volume X365..405 / Y1210..1236 / Z620..665, directly below the Rev J riser end (1/2 NPT male, Z665) and behind '
                 f'the hose start (385, 1210, {HOSE_Z:g}), which heads forward under pan bearer 3.',
                 'The selected street elbow and adapter must fit this zone and let the hose leave without forcing the spout. '
                 'Pan bearer 3 (Y1150..1200.8, bottom Z679) is above and in front of the zone.'])
    for i, x in enumerate(CLAMP_X, 1):
        for half, z in (('UPPER', HOSE_Z), ('LOWER', HOSE_Z - 14)):
            local = box(20, 37, 14)
            bore = place(cyl(20, 22), (-1, 20, 0 if half == 'UPPER' else 14), u=(0, 1, 0), v=(0, 0, 1))
            local = local.cut(bore)
            for yy in (5, 33):
                local = local.cut(cyl(4.5, 16).translate((10, yy, -1)))
            m.add(f'I_HOSE_CLAMP_{i}_{half}', local.clean(), origin=(x - 10, 1110, z), pn='I_HOSE_CLAMP_' + half,
                  group='water_hose_support', material='Mild steel 20x37x14 offcut',
                  notes=['Rev I split block, half Ø20 bore; split plane at the hose centre. Fit a 2 mm liner around the 15.9 mm hose; '
                         'never clamp directly on the rubber.'])
        m.add_plate(f'K_HOSE_CLAMP_STRAP_{i}', 20, 65, 3, origin=(x - 10, 1150, HOSE_Z), u=(1, 0, 0), v=(0, 0, 1),
                    pn='K_HOSE_CLAMP_STRAP', group='water_hose_support',
                    notes=[f'Steel 20x65x3 strap on bearer 3 front face Y1150, Z{HOSE_Z:g}..710; weld to the bearer over Z679.2..710. '
                           'The upper clamp block welds or bolts to it (steel block).'])
        for j, yy in enumerate((1115, 1143), 1):
            b = cyl(7, 4).fuse(cyl(4, 35).translate((0, 0, 4))).clean()
            m.add(f'I_HOSE_CLAMP_{i}_BOLT_{j}', b, origin=(x, yy, HOSE_Z - 18), pn='STD_M4x35_HEAD_DOWN', purchased=True,
                  group='water_hose_support')
            m.add(f'I_HOSE_CLAMP_{i}_NUT_{j}', hexpart(7, 4, 4), origin=(x, yy, HOSE_Z + 14), pn='STD_M4_NYLOC', purchased=True,
                  group='water_hose_support')
    return {'hose': 'Parker 801-6, 3/8 ID, 15.9 OD, 350 psi, min R75', 'designed_bend_radius_mm': 80,
            'routed_centerline_length_mm': length, 'points_mm': PRESSURE_POINTS, 'arcs_midpoints_mm': PRESSURE_ARCS,
            'change_from_rev_i': 'Whole route, clamps and bolts 20 mm lower; straps 65 mm instead of 45 mm; spout fitting zone below the Rev J riser end.',
            'end_zones': {'spout': [365, 1210, 620, 405, 1236, 665], 'pump_connection': [895, 810, 450, 1030, 1010, 620]}}


SUCTION_Z = 540.0
R = 80.0
C45 = R * (1 - math.cos(math.pi / 4))
S45 = R * math.sin(math.pi / 4)
SUCTION_POINTS = [(180, 1358, 280), (180, 1358, SUCTION_Z - R), (180 + R, 1358, SUCTION_Z), (1040, 1358, SUCTION_Z),
                  (1120, 1278, SUCTION_Z), (1120, 1130, SUCTION_Z), (1120, 1050, 620), (1120, 1050, 628)]
SUCTION_ARCS = [(1, (180 + C45, 1358, SUCTION_Z - R + S45)), (3, (1040 + S45, 1358 - C45, SUCTION_Z)),
                (5, (1120, 1130 - S45, 620 - S45))]
POST_X = (500.0, 800.0)


def _suction(m):
    rev_i._remove(m, ['I_SUCTION_HOSE', 'I_SUCTION_STANCHION', 'I_SUCTION_GUIDE_2']
                  + [f'I_SUCTION_REAR_{k}_{i}' for k in ('EYE', 'STRAP') for i in (1, 2)])
    s, length = rev_i._route(SUCTION_POINTS, SUCTION_ARCS)
    heights = [z for _, _, z in SUCTION_POINTS]
    assert all(b >= a for a, b in zip(heights, heights[1:])), 'suction line must only rise'
    m.add_shape('K_SUCTION_HOSE', s, pn='PARKER_801_6_SUCTION_ROUTE', group='water_hose', purchased=True, color=(.12, .14, .16),
                material='Parker 801-6 hose, 3/8 in ID',
                length=length, release='DEFINED SUCTION ROUTE - FIELD-FIT END 82 SERIES CONNECTIONS REQUIRED',
                notes=[rev_i.HOSE_SOURCE,
                       'Parker 801-6, 3/8 ID, 15.9 OD, 28 inHg vacuum rating, min R75; designed R80.',
                       f'Rev K route rises the whole way: pickup Z280, rear leg Y1358/Z{SUCTION_Z:g}, then up into the strainer end zone '
                       'from below. No high point for air to collect in (Rev I peaked at Z710).',
                       'At 7 L/min the 9.5 mm bore runs at about 1.6 m/s, enough to carry air bubbles along. Commissioning test: '
                       'the pump primes from dry within 30 s and fills at 5 L/min or more; otherwise go to 1/2 in hose.'])
    m.add_plate('K_SUCTION_STANCHION', 20, 230, 6, origin=(145, 1355, 220), u=(1, 0, 0), v=(0, 0, 1), group='water_hose_support',
                notes=['20x230x6 strip on the two Rev I standoffs; the Rev I 490 mm strip is cut down because the line turns at Z460.'])
    m.add_plate('K_SUCTION_GUIDE_2', 35, 32, 3, holes=[(15, 20, 20)], origin=(165, 1338, 405), pn='I_SUCTION_GUIDE',
                group='water_hose_support', notes=['Rev I guide, moved from Z600 to Z405: below the tank rim (Z422) and the bend. '
                                                   'Fit a split soft liner.'])
    # Rear posts: an L-shaped plate in the YZ plane, clear of the tank rim below Z480,
    # widened above the lid to carry the Ø20 hose eye at Y1358 / Z540.
    outline = [(13, 0), (34, 0), (34, 270), (0, 270), (0, 190), (13, 190)]
    hole = (22, 250, 20)
    for i, x in enumerate(POST_X, 1):
        m.add('K_SUCTION_REAR_POST_' + str(i), plate(outline, 6, [hole]), origin=(x, 1336, 290), u=(0, 1, 0), v=(0, 0, 1),
              pn='K_SUCTION_REAR_POST', group='water_hose_support', material='A36 steel 6 mm',
              flat=dict(outline=outline, thickness_mm=6, holes=[hole], slots=[], internal=[]),
              notes=['Post Y1349..1370 below Z480, Y1336..1370 above it; Ø20 eye for the hose at Y1358 / Z540 with a split soft liner.',
                     'Welded to two standoffs from the tank rear wall. Carries the hose only.'])
        for j, z in enumerate((300.0, 390.0), 1):
            m.add_plate(f'K_SUCTION_REAR_STANDOFF_{i}_{j}', 20, 30.952, 6, origin=(x - 7, 1318.048, z), pn='I_SUCTION_STANDOFF',
                        group='water_hose_support',
                        notes=['As the Rev I standoff: weld the front edge to the tank rear wall (Y1318.048), the rear edge to the post. '
                               'No tank penetration.'])
    return {'route_points_mm': SUCTION_POINTS, 'arc_midpoints_mm': SUCTION_ARCS, 'centerline_length_mm': length,
            'highest_point_z_mm': max(heights), 'rises_monotonically': True,
            'hose': 'Parker 801-6, 3/8 ID', 'velocity_at_7_l_min_m_s': round(7e-3 / 60 / (math.pi / 4 * .0095 ** 2), 2),
            'change_from_rev_i': 'Rear leg Z540 instead of Z710; enters the strainer end zone from below; new rear posts replace the pan-wall eyes.'}


def extend_router_model(m):
    drain = rev_i._drain(m)
    pressure = _pressure_route(m)
    suction = rev_i._suction_and_strainer(m)
    suction['rev_k_route'] = _suction(m)
    return {'revision': 'K service: Rev I drain and strainer; pressure hose lowered 20 mm to the Rev J spout; suction without a high point',
            'drain': drain, 'pressure_hose': pressure, 'suction_strainer': suction,
            'preserved': 'Tank permanently vented; 115 L circuit charge maximum; existing hatches and washout.',
            'open_interfaces': ['Valve face length, stem offset and nipple fit', 'Pressure and suction hose end fittings',
                                'Pump port positions and mounting feet']}
