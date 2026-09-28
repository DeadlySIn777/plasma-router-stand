"""Rev J water service: the Rev H hatches, washout and drain reserves, with the
refill spout moved clear of the one-piece bed module.

`water_completion.py` (Rev H) is used unchanged for the two service hatches,
the washout flange and cover and the drain space reserves. Its refill riser at
Y1255 stands under the module's rear crossmember (Z870), where the spout's
inverted U (top Z895.65) cannot fit, so Rev J builds the same NPS 1/2 miter
spout one slat bay forward:

- The riser rises in the bay between slats 18 (Y1170-1173) and 19
  (Y1230-1233), at Y1215.4. Below the pan it passes 3.95 mm behind pan bearer 3
  (Y1150-1200.8) and ends at Z665, below the bearer, so the hose adapter hangs
  clear of it.
- The head turns along -X, not toward the front, so the whole spout stays at
  Y1204.75-1226.05: behind the rear tool reach (tool centre Y1121.4) and
  20.95 mm in front of the module's rear crossmember (Y1247).
- A 6 mm floor gusset replaces the Rev H stay, which ran to the rear wall
  under slat 19 and cannot be reached from this bay.

Purchased plumbing reserves stay amber and guarded, as in Rev H.
"""
import math

import cadquery as cq

from cad_helpers import PURCHASED, WATER, box
import water_completion as rev_h

RISER_X, RISER_Y = 385.0, 1215.4
HEAD_X = 345.0                      # outlet centre, 40 mm along -X
RISER_BOTTOM_Z, BEND_Z, OUTLET_Z = 665.0, 885.0, 865.0
PIPE_OD, PIPE_ID = 21.3, 15.8
PAN_RIM_Z = 835.0
FLOOR_ORIGIN = (115.0, 105.0, 747.0)   # WP_FLOOR placement, as water_completion._refill
COS_SLOPE = 1 / math.sqrt(1.0001)


def floor_top_z(y, thickness):
    """Top of the pan floor (1 % fall toward the rear) at world Y."""
    return FLOOR_ORIGIN[2] + thickness / COS_SLOPE - .01 * (y - FLOOR_ORIGIN[1])


def _refill(m):
    pts = [(RISER_X, RISER_Y, RISER_BOTTOM_Z), (RISER_X, RISER_Y, BEND_Z),
           (HEAD_X, RISER_Y, BEND_Z), (HEAD_X, RISER_Y, OUTLET_Z)]
    path = cq.Wire.makePolygon([cq.Vector(*p) for p in pts])
    spout = (cq.Workplane(cq.Plane(origin=pts[0], xDir=(1, 0, 0), normal=(0, 0, 1)))
             .circle(PIPE_OD / 2).circle(PIPE_ID / 2).sweep(path, transition='right').val())
    riser, head, drop = BEND_Z - RISER_BOTTOM_Z, RISER_X - HEAD_X, BEND_Z - OUTLET_Z
    m.add_shape('J_REFILL_MITER_SPOUT', spout, group='water_refill',
                material='NPS0.5 schedule40 steel pipe, welded miter assembly', color=WATER,
                notes=[f'Fabricated pipe OD{PIPE_OD} ID{PIPE_ID} mm. Centerline: ' + ' -> '.join(f'({x:g},{y:g},{z:g})' for x, y, z in pts) + '.',
                       f'Two 90-degree turns use paired 45-degree miters. Centerline segment lengths {riser:g}/{head:g}/{drop:g} mm; '
                       f'long-point miter blank allowances {riser + PIPE_OD / 2:g}/{head + PIPE_OD:g}/{drop + PIPE_OD / 2:g} mm before dressing and thread allowance.',
                       'Rev J position: the Rev H riser at Y1255 stands under the bed module rear crossmember. This riser rises between slats 18 and 19, '
                       'passes 3.95 mm behind pan bearer 3 and 3.95 mm in front of slat 19, and its head turns along -X. Check both gaps at fit-up.',
                       'Bottom end is 1/2 NPT male at Z665, below pan bearer 3 (Z679), for a receipt-fit reinforced hose adapter. Top discharge remains open: no downstream valve or nozzle.',
                       f'Outlet low edge Z{OUTLET_Z:g} gives {OUTLET_Z - PAN_RIM_Z:g} mm nominal air gap above the Z{PAN_RIM_Z:g} pan rim; keep at least 25 mm as built.',
                       'Plasma sheets must stay in front of about Y1200 on the slats; the spout stands 45 mm above the slat tops, as in Rev H.'])
    floor = m.find('WP_FLOOR')
    floor.flat['holes'].append((RISER_X - FLOOR_ORIGIN[0], (RISER_Y - FLOOR_ORIGIN[1]) / COS_SLOPE, 21.6))
    rev_h._plate_again(floor, FLOOR_ORIGIN, v=(0, COS_SLOPE, -.01 * COS_SLOPE))
    floor.notes.append(f'Rev J: Ø21.6 normal hole at world XY({RISER_X:g},{RISER_Y:g}) receives the vertical refill riser; '
                       'seal weld annulus, leak-test and coat after welding.')
    # Right-triangle gusset, 45 along +X by 60 high, on the side away from the
    # outlet, 0.05 mm off the riser at its centre plane; the weld fills the gap.
    base_z = floor_top_z(RISER_Y - 3, floor.flat['thickness_mm']) + .005
    gusset = [(0, 0), (45, 0), (0, 60)]
    m.add_plate('J_REFILL_GUSSET', 45, 60, 6, outline=gusset, origin=(RISER_X + PIPE_OD / 2 + .05, RISER_Y + 3, base_z),
                u=(1, 0, 0), v=(0, 0, 1), group='water_refill', material='A36 steel6mm',
                notes=['Weld the 45 mm edge to the pan floor and the 60 mm edge to the riser, both sides, after the riser is seal-welded into the floor.',
                       'Replaces the Rev H stay: the riser now stands in the slat bay in front of slat 19, where a stay to the rear wall would pass under the slat.'])
    m.add('J_REFILL_CONNECTION_RESERVE', box(100, 100, 120), origin=(RISER_X - 50, RISER_Y - 50, RISER_BOTTOM_Z - 120),
          group='water_plumbing_reserve', material='Purchased hose/adapter space reservation', purchased=True, color=PURCHASED,
          release='HOSE CONNECTION SPACE - ACTUAL ADAPTER / BEND RADIUS UNVERIFIED',
          notes=[f'Reserve X{RISER_X - 50:g}..{RISER_X + 50:g}/Y{RISER_Y - 50:g}..{RISER_Y + 50:g}/Z{RISER_BOTTOM_Z - 120:g}..{RISER_BOTTOM_Z:g} '
                 'for the lower spout connection, below pan bearer 3. Keep conversion handling out of this volume.',
                 'This is a keep-out allocation, not a fitted hose or a manufacturer bend-radius claim. Select actual hose/fittings and revise the allocation if required.'])
    return {'outlet_xyz_mm': [HEAD_X, RISER_Y, OUTLET_Z], 'pan_rim_z_mm': PAN_RIM_Z, 'nominal_air_gap_mm': OUTLET_Z - PAN_RIM_Z,
            'minimum_as_built_air_gap_mm': 25, 'pump_hose_connection': f'1/2 NPT male at ({RISER_X:g},{RISER_Y:g},{RISER_BOTTOM_Z:g}), adapter engagement remains receipt-fit.',
            'connection_exclusion_bounds_mm': [RISER_X - 50, RISER_Y - 50, RISER_BOTTOM_Z - 120, RISER_X + 50, RISER_Y + 50, RISER_BOTTOM_Z],
            'change_from_rev_h': 'Riser moved from (385,1255) to (385,1215.4) and head turned along -X to clear the bed module rear crossmember; '
                                 'riser lengthened to end below pan bearer 3; floor gusset replaces the rear-wall stay.'}


def extend_router_model(m):
    rev_h._hatches(m)
    refill = _refill(m)
    drain = rev_h._drain_reserves(m)
    washout = rev_h._washout_cap(m)
    return {'revision': 'J water/service definition (Rev H hatches, washout and drain reserves; Rev J refill spout)',
            'routine_washout': 'Two independent lift-out hatches with captive upright parking; the full lid stays in place.',
            'service_hatches': list(rev_h.HATCHES), 'water_charge_limit_litres': 115, 'permanently_vented': True,
            'refill': refill, 'gravity_drain': drain, 'washout_cap': washout,
            'remaining_holds': ['Complete selected valve/union/strainer/pump port fit and supported hose route',
                                'Whole reservoir lid removal remains major disassembly, not routine service',
                                'Actual cabinet hinge/latch/door, gland entry and VFD heat rejection require selected enclosure drawings',
                                'Wet-test tank cleaning reach, float calibration, overflow flow and anti-siphon air gap']}
