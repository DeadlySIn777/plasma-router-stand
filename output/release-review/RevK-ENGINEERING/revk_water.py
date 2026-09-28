"""GM1 Rev K water fixes on the Rev J water service (review 26 Sep 2026, water and coolant).

- Refill spout 2 mm higher (bend Z887, outlet Z867): 32 mm air gap over the Z835 pan
  rim, above the two-bore rule for its 15.8 mm bore (31.6 mm). Rev J had 30 mm.
- Drain screen basket in the pan drain neck: chips, dross and aluminium fines stay
  in the pan instead of reaching the reservoir. Lift it out by its tab to empty it.
- Manual reservoir drain: a 1/2 in NPT half coupling on the tank's right wall at the
  clarified bay's floor, a full-port ball valve and a garden-hose outlet with cap, for
  freezing weather and water changes. The settling bay (about 6 L below its weir)
  empties through the existing washout cover.
- Seals that water or coolant reaches are nitrile (NBR) instead of EPDM, so an
  oil-bearing coolant does not swell them.

The GM1 controls close the pan drain after the router-mode dwell (M9) and add a fill
watchdog (M10); see output/controls-2026-09-27.
"""
import math

import cadquery as cq

from cad_helpers import PURCHASED, WATER, HARDWARE, box, cyl
import water_completion as rev_h
import water_revj as rev_j

BEND_Z, OUTLET_Z = 887.0, 867.0
SCREEN_OD, SCREEN_DEPTH, SCREEN_WALL, FLANGE_OD, FLANGE_T = 40.0, 40.0, .8, 60.0, 1.5   # flange clears the pan rear wall (Y1301.95) by 1.95
DRAIN_XY = (900.0, 1270.0)
NECK_TOP_Z = rev_j.floor_top_z(DRAIN_XY[1], 3.048)
TANK_DRAIN = dict(y=1150.0, z=193.0, hole=22.0)
WALL = dict(origin=(1025.0, 711.952, 178.048))           # WT_SIDE_RIGHT placement (water_system.py)
NBR = '2 mm nitrile (NBR) sheet, oil- and coolant-resistant'


def _spout(m):
    old = m.find('J_REFILL_MITER_SPOUT')
    m.parts.remove(old)
    x, y, head_x = rev_j.RISER_X, rev_j.RISER_Y, rev_j.HEAD_X
    pts = [(x, y, rev_j.RISER_BOTTOM_Z), (x, y, BEND_Z), (head_x, y, BEND_Z), (head_x, y, OUTLET_Z)]
    path = cq.Wire.makePolygon([cq.Vector(*p) for p in pts])
    spout = (cq.Workplane(cq.Plane(origin=pts[0], xDir=(1, 0, 0), normal=(0, 0, 1)))
             .circle(rev_j.PIPE_OD / 2).circle(rev_j.PIPE_ID / 2).sweep(path, transition='right').val())
    riser, head, drop = BEND_Z - rev_j.RISER_BOTTOM_Z, x - head_x, BEND_Z - OUTLET_Z
    gap = OUTLET_Z - rev_j.PAN_RIM_Z
    m.add_shape('K_REFILL_MITER_SPOUT', spout, group='water_refill',
                material='NPS0.5 schedule40 steel pipe, welded miter assembly', color=WATER,
                notes=['Rev J spout with the riser 2 mm longer. Centerline: ' + ' -> '.join(f'({a:g},{b:g},{c:g})' for a, b, c in pts) + '.',
                       f'Segment lengths {riser:g}/{head:g}/{drop:g} mm; long-point miter blanks {riser + rev_j.PIPE_OD / 2:g}/'
                       f'{head + rev_j.PIPE_OD:g}/{drop + rev_j.PIPE_OD / 2:g} mm before dressing and thread allowance.',
                       f'Outlet low edge Z{OUTLET_Z:g}: {gap:g} mm air gap over the Z{rev_j.PAN_RIM_Z:g} pan rim, at least twice the '
                       f'{rev_j.PIPE_ID:g} mm bore. Keep at least 31.6 mm as built.',
                       'Bottom end 1/2 NPT male at Z665 (as Rev J). Top discharge stays open: no valve or nozzle downstream.'])
    return {'outlet_z_mm': OUTLET_Z, 'bend_z_mm': BEND_Z, 'air_gap_mm': gap, 'two_bore_rule_mm': 2 * rev_j.PIPE_ID,
            'top_z_mm': BEND_Z + rev_j.PIPE_OD / 2}


def _screen(m):
    x, y = DRAIN_XY
    # The flange rests on the high (front) side of the 1 % floor fall.
    base = rev_j.floor_top_z(y - FLANGE_OD / 2, 3.048) + .01
    wall = cyl(SCREEN_OD, SCREEN_DEPTH).cut(cyl(SCREEN_OD - 2 * SCREEN_WALL, SCREEN_DEPTH)).translate((0, 0, -SCREEN_DEPTH))
    bottom = cyl(SCREEN_OD, SCREEN_WALL).translate((0, 0, -SCREEN_DEPTH))
    flange = cyl(FLANGE_OD, FLANGE_T).cut(cyl(SCREEN_OD - 2 * SCREEN_WALL, FLANGE_T))
    tab = box(8, 1.5, 25).translate((21, -.75, FLANGE_T)).cut(
        cyl(5, 3).rotate((0, 0, 0), (1, 0, 0), 90).translate((25, 1.5, FLANGE_T + 17)))
    s = wall.fuse(bottom).fuse(flange).fuse(tab).clean()
    m.add('K_DRAIN_SCREEN', s, origin=(x, y, base), pn='K_DRAIN_SCREEN_BASKET', group='water_drain',
          material='304 stainless perforated sheet 0.8 mm, 3 mm holes, about 40 % open', color=(.7, .72, .74),
          notes=[f'Basket Ø{SCREEN_OD:g} x {SCREEN_DEPTH:g} deep in the Ø40.9 pan drain neck, flange Ø{FLANGE_OD:g} x {FLANGE_T:g} on the pan floor, '
                 '8 x 25 lift tab with a Ø5 hole on the flange ring. Roll and seam the side, weld on the bottom disc and flange, then the tab.',
                 f'Open area about {math.pi * SCREEN_OD * SCREEN_DEPTH * .4 + math.pi * SCREEN_OD ** 2 / 4 * .4:.0f} mm², about 4x the NPS1 drain bore: '
                 'the drain still passes the pan with the screen half blocked. Empty it before every mode change and after long cuts.',
                 'The flange rests on its front edge; the 1 % floor fall leaves up to 0.7 mm under its rear edge.'])
    return {'basket_od_mm': SCREEN_OD, 'depth_mm': SCREEN_DEPTH, 'flange_od_mm': FLANGE_OD, 'hole_mm': 3,
            'flange_underside_z_mm': round(base, 3), 'neck_top_z_mm': round(NECK_TOP_Z, 3)}


def _tank_drain(m):
    wall = m.find('WT_SIDE_RIGHT')
    ox, oy, oz = WALL['origin']
    local = (TANK_DRAIN['y'] - oy, TANK_DRAIN['z'] - oz, TANK_DRAIN['hole'])
    wall.flat['holes'].append(local)
    rev_h._plate_again(wall, WALL['origin'], u=(0, 1, 0), v=(0, 0, 1))
    wall.notes = list(wall.notes) + [
        f'Rev K: Ø{TANK_DRAIN["hole"]:g} hole at world Y{TANK_DRAIN["y"]:g} Z{TANK_DRAIN["z"]:g} (local {local[0]:.3f}, {local[1]:.3f}) '
        'for the manual drain coupling; its bottom edge is 4 mm above the tank floor.']
    y, z = TANK_DRAIN['y'], TANK_DRAIN['z']
    coupling = cyl(32, 25).cut(cyl(21.3, 25)).rotate((0, 0, 0), (0, 1, 0), 90)
    m.add('K_TANK_DRAIN_COUPLING', coupling, origin=(1028.048, y, z), pn='STD_HALF_COUPLING_1_2_NPT_3000', group='water_drain',
          purchased=True, color=HARDWARE, material='1/2 NPT 3000# forged steel half coupling',
          notes=['Seal weld to the outside of the tank right wall over the Ø22 hole, then leak-test and coat. Envelope Ø32 x 25.'])
    m.add('K_TANK_DRAIN_VALVE_ZONE', box(45, 130, 50), origin=(1053.048, y - 15, 176.0), pn='K_TANK_DRAIN_VALVE_SET',
          group='water_plumbing_reserve', purchased=True, color=PURCHASED, material='Purchased fittings: space reservation',
          release='PURCHASED FITTING ZONE - SELECT VALVE, CLOSE NIPPLE AND HOSE ADAPTER TO FIT',
          notes=['1/2 in street elbow turned rearward, full-port ball valve with lever, 1/2 NPT close nipple, 1/2 MNPT x 3/4 '
                 'garden-hose adapter and cap. Zone X1053..1098 / Y1135..1265 / Z176..226: inside the frame side (X1099), above the '
                 'tank-support tubes (Z175) and below the frame side rail (Z230). Reach it from the right side between the legs.',
                 'To drain: screw on a garden hose to a floor drain, uncap, open the valve. It empties the clarified bay to 4 mm; '
                 'the settling bay (about 6 L below its weir) empties through the washout cover.'])
    return {'coupling_world_xyz_mm': [1028.048, y, z], 'wall_hole_local_mm': [round(local[0], 3), round(local[1], 3)],
            'drains': 'clarified bay to 4 mm above the floor; settling bay through the washout cover',
            'fittings_zone_mm': [1053.048, y - 15, 176.0, 1098.048, y + 115, 226.0]}


def nbr_seals(m):
    """Run after every extension, so the Rev I drain gasket is included."""
    changed = []
    for p in m.parts:
        if 'EPDM' in (p.material or '') and not p.group.startswith('controls'):
            p.material = NBR
            p.notes = list(p.notes) + ['Rev K: nitrile (NBR) instead of EPDM, because router coolant reaches the water.']
            changed.append(p.id)
    return changed


def extend_router_model(m):
    return {'revision': 'K water fixes', 'refill_spout': _spout(m), 'drain_screen': _screen(m),
            'manual_tank_drain': _tank_drain(m), 'nbr_seals': 'applied by build_revk after every extension (nbr_seals)',
            'controls': 'Pan drain closes after the router-mode dwell (GM1 M9); fill watchdog T_FILL (GM1 M10).'}
