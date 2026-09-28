"""GM1 Rev L, BT30 variant: a 3.2 kW BT30 ATC spindle instead of the ER11, a fork rack instead of the
RapidChange magazine, a thicker tool adapter and a bigger parking cradle. Everything else is Rev L
(frame, one-piece bed module, water, plasma head, the raised 300 mm Z, the dock's beams, rails and drive).

Spindle (owner's Amazon listing B0HJ89DJL6, "3.2KW 24000RPM 4-pole BT30"; the listing itself could not be
read from here): drawn as a 105 x 450 mm cylinder of 15 kg. A JGL-100-class body is 100 mm across and
shorter and lighter; the envelope is deliberately larger. Check the listing's diameter, length, mass, air
pressure and the 800 Hz rating against these numbers before ordering the clamp material.

Tool holders: BT30 with a 60 mm projection (BT30-ER32-60 class): flange 46 x 16 under the gauge line, nut
50 across, taper and pull stud 74.4 above the gauge line. The spindle nose sits 60 mm higher than Rev L's
ER11 nut so the held holder's nose is at Rev L's tool datum (Z960 + z) and the cutting envelope is the same.

Geometry that follows from the spindle:
  - the clamp is bored 105 with 13 / 12.5 mm walls, so the tool axis is 26.35 mm further forward than
    Rev L's: Y = gantry Y - 179.95, work area Y95.05..1095.05 (the front 13 mm is over the pan's front
    wall; set the front soft limit there or keep the 26 mm loss);
  - the adapter is 19.05 thick (3/4 in) with the Rev L web of 6.7 mm behind the clamp screws and 6.1 mm
    behind the carriage screws, so the same screws and the same plasma drop bracket fit; the torch axis
    moves 6.35 mm forward with it;
  - the rack's pocket line is 26.35 mm further forward on a longer carrier tray; the dock's fixed parts
    (beams, rails, stops, drive, sensors) are Rev L's, unchanged, and so is its 200 mm travel;
  - the holders in the rack fit between the HDPE (Z958.8) and the gantry's lowest members (Z1143):
    cutters stored with at most 30 mm below the nut, an 8.9 mm stock allowance under the deployed rack,
    pull-stud tops 10.9 mm under the gantry.
Every dock part is still MOD_ATC_*: it lifts out with the bed for plasma.
"""
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
REVL = HERE.parent / 'RevL-ENGINEERING'
REVK = HERE.parent / 'RevK-ENGINEERING'
LEGACY = HERE.parent / 'RevE-ENGINEERING'
for path in (str(LEGACY), str(REVK), str(REVL)):
    if path not in sys.path:
        sys.path.insert(0, path)

from cad_helpers import ALU, HARDWARE, PURCHASED, bbox, box, cyl, place, plate, rect  # noqa: E402
from motion_details import bolt, envelope  # noqa: E402
from frame_details import hexpart  # noqa: E402
import atc_revl  # noqa: E402
import z300  # noqa: E402
from atc_revl import BLUE, GOLD, MAGENTA, PREFIX, T, TOP, WT, socket_screw, _add  # noqa: E402

# --- the spindle and its holders (assumptions to check against the listing) ---
SPINDLE_D = 105.0
SPINDLE_L = 450.0
SPINDLE_KG = 15.0
SPINDLE_PN = 'SPINDLE_BT30_3p2KW_B0HJ89DJL6'
SPINDLE_ID = 'TOOL_SPINDLE_105x450'
HOLDER_PROJ = 60.0            # gauge line to nose
FLANGE_D, FLANGE_H = 46.0, 16.0
NUT_D = 50.0
TAPER_D, TAPER_H = 32.0, 48.4  # taper large end and length above the gauge line
STUD_D, STUD_L = 14.0, 26.0    # pull stud head and its projection above the taper
STUD_H = TAPER_H + STUD_L     # 74.4: stud top above the gauge line
GROOVE = 8.0                  # fork plane below the gauge line (flange V-groove)
STORED_CUTTER = 30.0          # stick-out below the nut, tools stored in the rack
HELD_CUTTER = 40.0            # the Z rule for the tool in the spindle (as Rev L)
NOSE_RAISE = HOLDER_PROJ      # spindle nose above Rev L's nut datum

# --- adapter and clamp ---
ADAPTER_T = 19.05
WEB = 6.7                     # Rev L: the M6 x 20 clamp screws and the plasma bracket's M6 x 30 pass this web
CBORE_D, CBORE_DEPTH = 10.5, ADAPTER_T - WEB          # 12.35
CSLOT_DEPTH = ADAPTER_T - 6.1                        # 12.95: the same carriage screws as Rev L
CLAMP_ROWS = (12.0, 38.0, 64.0, 90.0)                # above the output datum; the lower two are Rev L's pattern
CLAMP_X = 45.0
CLAMP_H = 100.0
WALL_REAR, WALL_FRONT = 13.0, 12.5
CLAMP_W = SPINDLE_D + 2 * WALL_FRONT                 # 130: at X175 its edge clears the left Y shoe (X101.5) by 8.5 mm
CLAMP_DEPTH = WALL_REAR + SPINDLE_D + WALL_FRONT     # 130.5
AXIS_BACK = WALL_REAR + SPINDLE_D / 2                # 65.5 from the adapter's front face
LUG_W, LUG_L, SLIT = 20.0, 25.0, 3.0                 # two lugs ahead of the bore, either side of the slit
PINCH_Z, PINCH_L = (25.0, 85.0), 60.0                # M8 x 60 through the lugs, along X, nut on the left
TOOL_Y_SHIFT = (ADAPTER_T + AXIS_BACK) - (12.7 + 45.5)   # 26.35 forward of Rev L
TOOL_AXIS_OFFSET = 153.6 + TOOL_Y_SHIFT                  # spindle axis Y = gantry Y - 179.95
TOOL_AXIS_Y_LIMITS = [121.4 - TOOL_Y_SHIFT, 1121.4 - TOOL_Y_SHIFT]

# --- rack on the dock ---
POCKET_Y = atc_revl.POCKET_Y - TOOL_Y_SHIFT          # 1073.65 deployed
POCKET_PITCH = 90.0
POCKET_X = tuple(575.0 + POCKET_PITCH * (i - 2.5) for i in range(6))   # 350 .. 800
TRAY_Y0 = atc_revl.CARRIER[2] - TOOL_Y_SHIFT         # 1038.65: the tray starts 26.35 further forward
TRAY_Y1 = 1165.0                                     # tray to here, then the arms (Rev L: 1140)
TRAY_SLOT_W, TRAY_SLOT_BACK = 56.0, 30.0             # open-front slots for the hanging nuts, to pocket + 30
BAR_X0, BAR_L, BAR_D, BAR_T = 315.0, 520.0, 80.0, 15.875   # 5/8 in 6061 bar: pocket - 26 .. pocket + 54
BAR_Y0 = POCKET_Y - 26.0
BAR_SLOT_W = 52.0
BAR_SCREWS = tuple((x, POCKET_Y + y) for x in (330.0, 575.0, 820.0) for y in (40.0, 50.0))
FORK_W, FORK_D, FORK_T, FORK_U = 60.0, 60.0, 11.5, 39.0
BAR_TOP = TOP + BAR_T                                # 1042.225
FORK_TOP = BAR_TOP + FORK_T                          # 1053.725
GAUGE_Z = FORK_TOP + 4.0                             # 1057.725: holder gauge line in the rack
FORK_PLANE = GAUGE_Z - GROOVE                        # 1049.725
NOSE_Z = GAUGE_Z - HOLDER_PROJ                       # 997.725: stored holder nose
RACK_TOP = GAUGE_Z + STUD_H                          # 1132.125: pull-stud tops
STORED_BOTTOM = NOSE_Z - STORED_CUTTER               # 967.725
HDPE_TOP = 958.8
GANTRY_UNDERSIDE = 1143.0                            # Z carrier, X blocks and guide face (Rev L, gantry at any Y)
STOCK_ALLOWANCE = STORED_BOTTOM - HDPE_TOP           # 8.925
Z_ENGAGE = GAUGE_Z - NOSE_RAISE - 960.0              # 37.725: spindle nose at the gauge line
Z_DOCK_MIN = RACK_TOP + HELD_CUTTER + 15.0 - 920.0   # 267.125: held tool clears the studs by 15
APPROACH_Y = 70.0                                    # held holder this far in front of the pocket before sliding in

# --- parking (plasma) ---
PARK_X = (720.0, 985.0)                              # cradle plates: right of the clarified-tank cover, clear of the clamp (X865-965) and the strainer post
PARK_Y, PARK_AXIS_Z = 1080.0, 500.0                  # spindle axis on the lid; the clamp's lower edge is then 1.9 mm over the lid
PARK_NOSE_X = 1030.0                                 # nose to the right; body to X580, the clamp (still on the spindle) at X865..965
LID_TOP, LID_T = 433.096, 3.048
BOUGHT_KG = dict(atc_revl.BOUGHT_KG, BT30_TOOL_FORK_ALLOCATION=.06, BT30_ER32_HOLDER_ALLOCATION=.95)
HOLDS = [
    f'BT30 spindle: drawn as a {SPINDLE_D:g} x {SPINDLE_L:g} envelope of {SPINDLE_KG:g} kg from the listing title alone. '
    'Confirm diameter, length, mass, drawbar air pressure, clamp sensors and the 800 Hz rating from the delivered unit; '
    'bore the clamp to the measured body.',
    'BT30 on the ZBX80: the slide carries about 20 kg (spindle, clamp, adapter) 130 mm ahead of its carriage; the ZBX80 '
    'moment rating is not published. A brake or counterbalance for the Z is still open (Rev K hold), and matters more here.',
    'Rack: the fork inserts and holders are allocations (BT30-ER32-60 class, plastic forks). Stored cutters may not '
    f'project more than {STORED_CUTTER:g} mm below the nut, and the rear 60 mm of the work area carries nothing over '
    f'{STOCK_ALLOWANCE:.1f} mm thick while the dock is deployed.',
    'Controls: the drawbar valve, clamp sensors, the 4 kW / 800 Hz VFD and the air supply are documented in the BT30 README, '
    'not built into gm1_circuit.py (the ER11 circuit record is unchanged).']


def holder_solid(taper=True, cutter=0.0):
    """A BT30 holder about its nose: nut, flange, then the taper and stud above the gauge line, cutter below."""
    s = cyl(NUT_D, HOLDER_PROJ - FLANGE_H).fuse(cyl(FLANGE_D, FLANGE_H).translate((0, 0, HOLDER_PROJ - FLANGE_H)))
    if taper:
        s = s.fuse(cyl(TAPER_D, TAPER_H).translate((0, 0, HOLDER_PROJ))).fuse(cyl(STUD_D, STUD_L).translate((0, 0, HOLDER_PROJ + TAPER_H)))
    if cutter:
        s = s.fuse(cyl(12, cutter).translate((0, 0, -cutter)))
    return s.clean()


def _adapter(model):
    """Rev L's 110 x 220 drop adapter, 19.05 thick, with eight clamp holes. Same id, so the plasma bracket and
    the existing permits still apply. Returns (head_x, output_y, out_z)."""
    a = model.find('TOOL_ADAPTER_110')
    bb = bbox(a.shape)
    origin = (bb[0], bb[4], bb[2])
    holes = [h for h in a.flat['holes'] if h[2] == 6.6]
    assert len(holes) == 4, holes
    holes += [(10.0 + 90.0 * (i % 2), z, 6.6) for z in (22.0 + (r - 12.0) for r in CLAMP_ROWS[2:]) for i in range(2)]
    slots = list(a.flat['slots'])
    local = plate(rect(110.0, z300.ADAPTER_H), ADAPTER_T, holes, slots)
    for x, y, d in holes:
        local = local.cut(cq.Workplane('XY').circle(CBORE_D / 2).extrude(CBORE_DEPTH).translate((x, y, 0)).val())
    cslot = cq.Compound.makeCompound([cq.Workplane('XY').center(sx, 45 + z300.RAISE).slot2D(30, 11, 90).extrude(CSLOT_DEPTH + 1)
                                      .translate((0, 0, ADAPTER_T - CSLOT_DEPTH)).val() for sx in (20, 90)])
    local = local.cut(cslot).clean()
    a.local = local
    a.shape = place(local, origin, (1, 0, 0), (0, 0, 1))
    a.part_number = f'TOOL_ADAPTER_110x{int(z300.ADAPTER_H)}_BT30'
    a.material = '6061-T6 aluminum 19.05 (3/4 in)'
    a.flat = dict(a.flat, holes=holes, slots=slots,
                  operations=[{'type': 'circle', 'x': x, 'y': y, 'diameter': CBORE_D, 'layer': f'MILL_REAR_COUNTERBORE_DEPTH_{CBORE_DEPTH:g}'.replace('.', '_')}
                              for x, y, d in holes] +
                             [{'type': 'slot', 'x': sx, 'y': 45 + z300.RAISE, 'length': 30, 'width': 11, 'angle': 90, 'depth_mm': CSLOT_DEPTH,
                               'face': 'front', 'layer': f'MILL_FRONT_COUNTERSLOT_DEPTH_{CSLOT_DEPTH:g}'.replace('.', '_')} for sx in (20, 90)])
    a.notes = [f'BT30 adapter: Rev L\'s 110 x {z300.ADAPTER_H:g} drop adapter in {ADAPTER_T:g} mm plate (3/4 in). Eight 6.6 clamp holes at '
               f'X10/100, Y22/48/74/100 with {CBORE_D:g} counterbores {CBORE_DEPTH:g} deep on the rear face, leaving Rev L\'s {WEB:g} mm web: '
               'the same M6 x 20 clamp screws, and the plasma drop bracket with its M6 x 30 screws on the lower four holes, fit unchanged.',
               f'Carriage slots as Rev L (7 x 30 vertical, 70 mm centres, {z300.RAISE:g} mm up); the front counter-slots are {CSLOT_DEPTH:g} deep '
               'so the carriage screws keep their 6.1 mm web.',
               'Stiffness: 3.4 times Rev L\'s 12.7 plate (about 0.012 mm per 100 N at the clamp). The 20 kg head and its cutting loads '
               'are why.',
               'Provisional, as Rev L: the carriage hole pitch, thread and the 80 mm output stack come from the delivered slide.']
    return (bb[0] + bb[3]) / 2, bb[4], bb[2] + 10.0


def _head(m, head_x, output_y, out_z, z_lift, held_tool):
    """One-piece clamp bored for the spindle, slit at the front with two lugs and two M8 pinch bolts along X, eight mount
    screws into its back, the spindle envelope and the held holder."""
    clamp_back = output_y - ADAPTER_T
    axis_y = clamp_back - AXIS_BACK
    z0 = out_z + 5.0
    front = clamp_back - CLAMP_DEPTH
    clamp = box(CLAMP_W, CLAMP_DEPTH, CLAMP_H).translate((head_x - CLAMP_W / 2, front, z0)) \
        .fuse(box(2 * LUG_W + SLIT, LUG_L, CLAMP_H).translate((head_x - LUG_W - SLIT / 2, front - LUG_L, z0)))
    clamp = clamp.cut(cyl(SPINDLE_D, CLAMP_H + 2).translate((head_x, axis_y, z0 - 1)))
    clamp = clamp.cut(box(SLIT, LUG_L + WALL_FRONT + 2, CLAMP_H + 2).translate((head_x - SLIT / 2, front - LUG_L - 1, z0 - 1)))
    for x in (head_x - CLAMP_X, head_x + CLAMP_X):
        for dz in CLAMP_ROWS:
            z = out_z + dz
            clamp = clamp.cut(place(cyl(6, 17), (x, clamp_back, z), u=(1, 0, 0), v=(0, 0, 1)))
            bo = bolt(m, f'TOOL_CLAMP_MOUNT_{int(x - head_x)}_{int(dz)}', 6, 20, (x, output_y - CBORE_DEPTH - 20, z), u=(1, 0, 0), v=(0, 0, -1))
            bo.group = 'removable_tool'
            bo.notes = [f'M6 x 20 in the adapter\'s {CBORE_DEPTH:g} mm counterbore; 13.3 mm into the clamp.']
    lug_y = front - LUG_L / 2
    for j, dz in enumerate(PINCH_Z, 1):
        z = z0 + dz
        clamp = clamp.cut(place(cyl(8.5, 2 * LUG_W + SLIT + 2), (head_x - LUG_W - SLIT / 2 - 1, lug_y, z), u=(0, 1, 0), v=(0, 0, 1)))
        bo = bolt(m, f'TOOL_CLAMP_PINCH_{j}', 8, PINCH_L, (head_x + LUG_W + SLIT / 2 - PINCH_L, lug_y, z), u=(0, 1, 0), v=(0, 0, 1))
        bo.group = 'removable_tool'
        bo.notes = ['M8 x 60 through both lugs, head on the right lug, nut on the left.']
        nut = m.add(f'TOOL_CLAMP_PINCH_NUT_{j}', hexpart(13, 6.5, 8), origin=(head_x - LUG_W - SLIT / 2, lug_y, z), u=(0, 0, 1), v=(0, 1, 0),
                    pn='STD_M8_NYLOC', group='removable_tool', material='M8 nyloc nut', purchased=True, color=HARDWARE)
        m.permit(nut.id, bo.id, 'Nut on the pinch bolt (drawn at the major diameter).')
    clamp = clamp.clean()
    bb = bbox(clamp)
    m.add('TOOL_SPINDLE_CLAMP', clamp.translate(tuple(-v for v in bb[:3])), origin=bb[:3], pn='SPINDLE_CLAMP_BT30', group='removable_tool',
          material='6061-T6 aluminum billet',
          notes=[f'One piece: {CLAMP_W:g} wide, {CLAMP_DEPTH:g} deep, {CLAMP_H:g} tall, plus two {LUG_W:g} x {LUG_L:g} lugs at the front either '
                 f'side of a {SLIT:g} mm slit. Bore {SPINDLE_D:g} drawn; bore to the measured spindle body +0.03 with the slit shimmed closed.',
                 f'Walls {WALL_REAR:g} behind the bore and {WALL_FRONT:g} beside and ahead of it: at X175 the clamp\'s edge is 8.5 mm from the '
                 'gantry\'s left Y shoe (X101.5), so the full 800 mm X travel is kept. A wider two-piece clamp lost 24 mm.',
                 f'Eight blind M6 x 1 in the back at X+/-{CLAMP_X:g}, Z+12/38/64/90 from the output datum (pilot 17, tap 15; 38 mm of material '
                 f'at those holes). Two M8 x {PINCH_L:g} pinch bolts through the lugs at Z+{PINCH_Z[0]:g}/+{PINCH_Z[1]:g} of the clamp, nyloc nuts on the left.',
                 'Clamps the lower 100 mm of the spindle, 65 mm above its nose. Fit the spindle from below with the clamp on the bench; for a '
                 'bed swap take the adapter off the carriage (two screws), then the clamp with the spindle in it (eight screws), and park the pair.'])
    envelope(m, SPINDLE_ID, cyl(SPINDLE_D, SPINDLE_L), (head_x, axis_y, 960.0 + NOSE_RAISE + z_lift), pn=SPINDLE_PN, group='removable_tool',
             material='3.2 kW 220 V BT30 ATC spindle, 4-pole (24,000 rpm at 800 Hz), air-cooled, pneumatic drawbar (envelope)',
             notes=[f'Envelope {SPINDLE_D:g} x {SPINDLE_L:g}, {SPINDLE_KG:g} kg, from the listing title; a JGL-100-class body is 100 across. '
                    'The nose is at Z1020 + z: 60 mm above Rev L\'s ER11 nut, so a 60 mm holder\'s nose is at Rev L\'s datum (Z960 + z).',
                    'Air: drawbar release at 6-8 bar and taper blow-off; power: 4 kW VFD with an 800 Hz output. Leads and air lines are '
                    'not drawn (Rev L does not draw the spindle cable either).'])
    if held_tool:
        m.add('TOOL_HOLDER_HELD_ALLOCATION', holder_solid(taper=False), origin=(head_x, axis_y, 960.0 + z_lift), pn='BT30_ER32_HOLDER_ALLOCATION',
              group='removable_tool', purchased=True, color=MAGENTA, release='SUPPLIER ALLOCATION - NOT A PURCHASED-PART DRAWING',
              material='BT30 holder in the spindle: nut and flange below the gauge line (allocation)',
              notes=[f'BT30-ER32-60 class: nose at Z960 + z, flange {FLANGE_D:g} x {FLANGE_H:g} under the gauge line. The taper and stud are '
                     f'inside the spindle and not drawn. A cutter up to {HELD_CUTTER:g} mm below the nut is the Z rule, not a part.'])
    return axis_y


def add_motion(model, gantry_y=1275.0, head_x=575.0, z_lift=z300.STROKE, held_tool=True):
    """Rev L's motion at one pose, then the ER11 head swapped for the BT30 head."""
    motion, completion = z300.add_motion(model, gantry_y, head_x, z_lift)
    for p in list(model.parts):
        if p.id == 'TOOL_SPINDLE_65x259' or p.id.startswith(('TOOL_SPLIT_CLAMP_', 'TOOL_CLAMP_MOUNT_', 'TOOL_CLAMP_PINCH_')):  # Rev L's ER11 head
            model.remove(p.id)
    hx, output_y, out_z = _adapter(model)
    axis_y = _head(model, hx, output_y, out_z, z_lift, held_tool)
    motion['configuration']['tool'] = 'router_bt30'
    motion['configuration']['held_tool'] = held_tool
    motion['tool_axis_y_nominal_limits'] = TOOL_AXIS_Y_LIMITS
    motion['bt30'] = {'spindle_envelope_mm': [SPINDLE_D, SPINDLE_L], 'spindle_mass_kg_assumed': SPINDLE_KG,
                      'spindle_axis_y_mm': round(axis_y, 3), 'spindle_nose_z_mm': 960.0 + NOSE_RAISE + z_lift,
                      'held_holder_nose_z_mm': 960.0 + z_lift, 'tool_axis_forward_of_rev_l_mm': round(TOOL_Y_SHIFT, 3),
                      'tool_axis_y_offset_from_gantry_mm': round(TOOL_AXIS_OFFSET, 3),
                      'adapter_thickness_mm': ADAPTER_T, 'clamp_mm': [CLAMP_W, CLAMP_DEPTH + LUG_L, CLAMP_H],
                      'head_mass_estimate_kg': round(SPINDLE_KG + 2.7 + 1.9 + .5, 1)}
    return motion, completion


def _carrier(m, travel, empty_pockets=()):
    """Rev L's carrier with a longer tray, open-front slots for the hanging nuts, and the rack instead of the magazine."""
    dy = travel
    ids = []
    x0, x1 = atc_revl.CARRIER[0], atc_revl.CARRIER[1]
    y0, y1 = TRAY_Y0, atc_revl.CARRIER[3]
    w, d = x1 - x0, y1 - y0
    arm = 30.0
    outline = [(0.0, 0.0)]
    for px in POCKET_X:
        sx0, sx1 = px - TRAY_SLOT_W / 2 - x0, px + TRAY_SLOT_W / 2 - x0
        back = POCKET_Y + TRAY_SLOT_BACK - y0
        outline += [(sx0, 0.0), (sx0, back), (sx1, back), (sx1, 0.0)]
    outline += [(w, 0.0), (w, d), (w - arm, d), (w - arm, TRAY_Y1 - y0), (arm, TRAY_Y1 - y0), (arm, d), (0.0, d)]
    holes = []
    for cx in atc_revl.RAIL_X:
        holes += [(cx - x0 + dx, atc_revl.BLOCK_Y - y0 + dyy, 3.4) for dx in (-10, 10) for dyy in (-10, 10)]
    holes += [(bx - x0, by - y0, 5.5) for bx, by in BAR_SCREWS]
    p = m.add_plate(PREFIX + 'CARRIER', w, d, T, holes=holes, outline=outline, origin=(x0, y0 + dy, WT), pn='MOD_ATC_CARRIER_BT30',
                    group='atc_moving', color=BLUE,
                    notes=['1/4 in steel, one piece: tray under the rack and two arms back to the guide blocks. The tray starts '
                           f'{TOOL_Y_SHIFT:g} mm further forward than Rev L\'s (Y{TRAY_Y0:g} deployed) and runs to Y{TRAY_Y1:g}.',
                           f'Six open-front slots {TRAY_SLOT_W:g} wide, from the front edge to {TRAY_SLOT_BACK:g} mm behind the pocket line, '
                           'for the holders\' nuts: they hang below the tray, and slide in from the front at the fork height.',
                           'Six 5.5 holes for the rack bar screws (from below). Block holes as Rev L.'])
    ids.append(p.id)
    u = _add(m, 'UPSTAND_REAR', box(530.0, 6.35, atc_revl.SADDLE_Z - TOP), (310.0, TRAY_Y1 - 6.35 + dy, TOP), pn='MOD_ATC_UPSTAND_REAR',
             group='atc_moving', color=BLUE, notes=['1/4 in steel strip on edge, welded along the tray\'s rear edge. The rack bar '
                                                     'stiffens the front, so there is no front upstand.'])
    ids.append(u.id)
    for side, cx in zip('LR', atc_revl.RAIL_X):
        blk = _add(m, f'BLOCK_{side}', atc_revl.hardware.mgn12h_block(), (cx, atc_revl.BLOCK_Y + dy, atc_revl.RB), **atc_revl.Y_TO_X,
                   pn='HIWIN_MGN12H', group='atc_guides', purchased=True, color=GOLD, material='HIWIN MGN12H block')
        ids.append(blk.id)
        for j, (dx, dyy) in enumerate([(a, b) for a in (-10, 10) for b in (-10, 10)], 1):
            wsh = _add(m, f'BLOCK_WASHER_{side}_{j}', cyl(7, .5).cut(cyl(3.2, .5)), (cx + dx, atc_revl.BLOCK_Y + dyy + dy, TOP),
                       pn='WASHER_M3_7x0p5', group='atc_hardware', material='steel washer', color=HARDWARE)
            scr = _add(m, f'BLOCK_SCREW_{side}_{j}', socket_screw(3, 10, 5.5, 3), (cx + dx, atc_revl.BLOCK_Y + dyy + dy, TOP + .5 - 10),
                       pn='STD_M3x10_ISO4762', group='atc_hardware', material='M3 x 10 socket head, class 8.8', color=HARDWARE)
            m.permit(scr.id, blk.id, 'Nominal M3 screw in the tapped block hole.')
            ids += [wsh.id, scr.id]
    tx, ty, tz = atc_revl.TAB
    tab = _add(m, 'DRIVE_TAB', box(*atc_revl.TAB_SIZE), (tx, ty + dy, tz), pn='MOD_ATC_DRIVE_TAB', group='atc_moving', color=BLUE,
               notes=['1/4 in steel, welded to the right arm outer edge. Its front face stops on the front stop (deployed datum); '
                      'the sensors read its outer face.'])
    clamp = _add(m, 'BELT_CLAMP', box(886 - (tx + atc_revl.TAB_SIZE[0]), 16, 8), (tx + atc_revl.TAB_SIZE[0], 1195 + dy, 998),
                 pn='MOD_ATC_BELT_CLAMP', group='atc_moving', color=BLUE,
                 notes=['Clamps both belt ends. Bolt it to the tab through a slot with a stiff spring so the belt runs about 2 mm on '
                        'after the tab reaches the front stop: the self-locking worm then holds that preload.'])
    m.permit(clamp.id, PREFIX + 'BELT_UPPER', 'The belt ends are clamped in the carrier clamp (closed loop).')
    ids += [tab.id, clamp.id]
    # The rack: a 5/8 in aluminium bar on the tray with six open-front slots, a plastic fork on each, and six holders.
    bar = m.add_plate(PREFIX + 'RACK_BAR', BAR_L, BAR_D, BAR_T, holes=[(bx - BAR_X0, by - BAR_Y0, 5.0) for bx, by in BAR_SCREWS],
                      slots=[(px - BAR_X0, 0.0, 2 * BAR_SLOT_W, BAR_SLOT_W, 90) for px in POCKET_X],
                      origin=(BAR_X0, BAR_Y0 + dy, TOP), pn='MOD_ATC_RACK_BAR_BT30', group='atc_moving', color=ALU,
                      material='6061-T6 aluminum 5/8 in (15.875)',
                      notes=[f'{BAR_L:g} x {BAR_D:g} x {BAR_T:g} on the tray, pocket line {26:g} mm behind its front edge. Six slots '
                             f'{BAR_SLOT_W:g} wide, open to the front, round ends on the pocket line (the holders\' flanges and nuts pass '
                             f'{(BAR_SLOT_W - NUT_D) / 2:g} mm clear). Six M5 tapped holes (drawn 5.0) for the screws from below.',
                             f'Pockets at {POCKET_PITCH:g} mm pitch, X{POCKET_X[0]:g}..{POCKET_X[-1]:g}: the clamp (154 wide) at the engage height '
                             'clears the neighbours\' pull studs by 7 mm.'])
    ids.append(bar.id)
    for k, (bx, by) in enumerate(BAR_SCREWS, 1):
        s = _add(m, f'BAR_SCREW_{k}', socket_screw(5, 16, 8.5, 5, head_below=True), (bx, by + dy, WT), pn='STD_M5x16_ISO4762',
                 group='atc_hardware', material='M5 x 16 socket head, class 8.8', color=HARDWARE,
                 notes=['From below: head under the tray (Z1015), 9.6 mm into the tapped bar.'])
        m.permit(s.id, bar.id, 'Nominal M5 screw in the tapped bar hole (drawn at the major diameter).')
        ids.append(s.id)
    for k, px in enumerate(POCKET_X, 1):
        fork = box(FORK_W, FORK_D, FORK_T).cut(cyl(FORK_U, FORK_T + 2).translate((FORK_W / 2, 26.0, -1))) \
            .cut(box(FORK_U, 27.0, FORK_T + 2).translate((FORK_W / 2 - FORK_U / 2, -1, -1))).clean()
        f = _add(m, f'FORK_{k}', fork, (px - FORK_W / 2, BAR_Y0 + dy, BAR_TOP), pn='BT30_TOOL_FORK_ALLOCATION', group='atc_allocation',
                 purchased=True, color=MAGENTA, release='SUPPLIER ALLOCATION - NOT A PURCHASED-PART DRAWING',
                 material='BT30 tool fork (plastic, spring lips): allocation only',
                 notes=[f'{FORK_W:g} x {FORK_D:g} x {FORK_T:g} allocation on the bar, U opening {FORK_U:g} to the front; its lips sit in the '
                        f'flange V-groove at Z{FORK_PLANE:g}. Two M5 screws into the bar are not drawn. Buy forks for BT30 (46 mm flange).'])
        ids.append(f.id)
        if k in empty_pockets:
            continue
        h = _add(m, f'STORED_HOLDER_{k}', holder_solid(taper=True, cutter=STORED_CUTTER), (px, POCKET_Y + dy, NOSE_Z),
                 pn='BT30_ER32_HOLDER_ALLOCATION', group='atc_allocation', purchased=True, color=MAGENTA,
                 release='SUPPLIER ALLOCATION - NOT A PURCHASED-PART DRAWING', material='BT30-ER32-60 holder with a cutter: allocation only',
                 notes=[f'Gauge line Z{GAUGE_Z:g}, nose Z{NOSE_Z:g}, taper {TAPER_D:g} x {TAPER_H:g} and stud {STUD_D:g} x {STUD_L:g} above it (top Z{RACK_TOP:g}), cutter to Z{STORED_BOTTOM:g} '
                        f'({STORED_CUTTER:g} mm below the nut, the most a stored tool may project).'])
        m.permit(h.id, f.id, 'Fork lips in the holder\'s flange V-groove (allocation).')
        ids.append(h.id)
    return ids


def mass_properties(m):
    total, moment = 0.0, [0.0, 0.0, 0.0]
    for p in m.parts:
        if not p.id.startswith(PREFIX):
            continue
        kg = BOUGHT_KG.get(p.part_number)
        if kg is None:
            kg = p.shape.Volume() * (atc_revl.DENSITY['aluminum'] if 'luminum' in p.material else atc_revl.DENSITY['steel'])
        c = p.shape.Center().toTuple()
        total += kg
        moment = [moment[i] + kg * c[i] for i in range(3)]
    return round(total, 2), [round(v / total, 1) for v in moment]


def extend_router_model(m, travel=atc_revl.TRAVEL, empty_pockets=()):
    """empty_pockets: 1-based pockets drawn without a holder (a drop-off target); the fork stays."""
    assert 0 <= travel <= atc_revl.TRAVEL
    fixed = atc_revl._fixed(m)
    moving = _carrier(m, travel, empty_pockets)
    kg, cg = mass_properties(m)
    m.holds.append('ATC (BT30): the fork inserts and holders are allocations; the pocket X positions are the fork centres and must be '
                   'probed after every bed install, as Rev L\'s pocket reference. Repeatability, preload and sensors are commissioning tests.')
    return {'status': 'MODULE-MOUNTED RETRACTING DOCK WITH A BT30 FORK RACK: WORKING CAD, NOT A FABRICATION RELEASE',
            'travel_mm': travel, 'travel_state': 'deployed' if travel == 0 else 'parked' if travel == atc_revl.TRAVEL else 'between',
            'stroke_mm': atc_revl.TRAVEL, 'rail_x_mm': list(atc_revl.RAIL_X), 'rail_plane_z_mm': atc_revl.RB, 'carrier_z_mm': [WT, TOP],
            'pocket_line_y_deployed_mm': POCKET_Y, 'pocket_x_mm': list(POCKET_X), 'pocket_pitch_mm': POCKET_PITCH,
            'bar_z_mm': [TOP, BAR_TOP], 'fork_plane_z_mm': FORK_PLANE, 'gauge_line_z_mm': GAUGE_Z, 'rack_top_z_mm': RACK_TOP,
            'stored_tool_bottom_z_mm': STORED_BOTTOM, 'stock_allowance_under_deployed_rack_mm': round(STOCK_ALLOWANCE, 3),
            'rack_top_under_gantry_mm': round(GANTRY_UNDERSIDE - RACK_TOP, 3), 'tray_y_deployed_mm': [TRAY_Y0, TRAY_Y1],
            'deployed_datum': 'Drive tab front face on the front stop at Y1185 (Rev L, unchanged)',
            'fixed_part_count': len(fixed), 'moving_part_count': len(moving), 'mass_kg': kg, 'cg_mm': cg,
            'mass_basis': 'Steel 7850 and aluminum 2700 kg/m3 on the modeled solids; bought parts by nominal mass; six holders at 0.95 kg '
                          'and forks at 0.06 kg are placeholders. Weigh the module with the dock.'}


def replace_cradle(m):
    """Rev K's ER11 cradle on the reservoir lid becomes a pair of 140 mm cradles for the BT30 spindle (X580..1030, axis Y1080)."""
    for p in list(m.parts):
        if p.id.startswith('TOOL_PARK_'):
            m.remove(p.id)
    lid = m.find('WT_LID')
    bb = bbox(lid.shape)
    holes = []
    for i, x in enumerate(PARK_X, 1):
        m.add_plate(f'BT30_PARK_BASE_{i}', 30, 150, LID_T, holes=[(5, 10, 6.6), (5, 140, 6.6)], origin=(x - 15, PARK_Y - 75, LID_TOP),
                    pn='BT30_PARK_BASE', group='tool_parking',
                    notes=['Spindle parked horizontally along X inside the rear bay, on two cradles. Disconnect power and air before '
                           'lifting it off the head: about 15 kg, two hands.'])
        h, cz = 80.0, PARK_AXIS_Z - (LID_TOP + LID_T)
        s = plate(rect(140, h), 6, slots=[(10, 60, 16, 6, 90), (130, 60, 16, 6, 90)])
        s = s.cut(cyl(SPINDLE_D + 1, 8).translate((70, cz, -1)).fuse(box(SPINDLE_D + 1, h - cz + 1, 8).translate((70 - (SPINDLE_D + 1) / 2, cz, -1)))).clean()
        m.add(f'BT30_PARK_CRADLE_{i}', s, origin=(x - 3, PARK_Y - 70, LID_TOP + LID_T), u=(0, 1, 0), v=(0, 0, 1), pn='BT30_PARK_CRADLE',
              group='tool_parking',
              notes=[f'140 wide, 6 thick, {h:g} tall; {SPINDLE_D + 1:g} open-top cradle centred at Y{PARK_Y:g}/Z{PARK_AXIS_Z:g}, {cz - (SPINDLE_D + 1) / 2:.1f} mm of '
                     'plate under it. Weld the bottom to the base with 3 mm fillets. Line the cradle with 3 mm rubber.',
                     'Two 6 x 16 strap slots at local X10/130, Z60. Two 25 mm cam straps retain the spindle.',
                     'The spindle body passes 9.4 mm over the clarified-tank cover (X330-690); the clamp stays on the spindle, lugs forward.'])
        for j, y in enumerate((PARK_Y - 65, PARK_Y + 65), 1):
            holes.append((x - 10, y))
            m.add(f'BT30_PARK_NUT_{i}_{j}', hexpart(10, 5, 6), origin=(x - 10, y, LID_TOP - LID_T - 5), pn='STD_M6_WELDNUT', group='tool_parking',
                  material='M6 weld nut', purchased=True, color=HARDWARE)
            b = cyl(6, 20).fuse(cyl(10, 6).translate((0, 0, 20))).clean()
            m.add(f'BT30_PARK_BOLT_{i}_{j}', b, origin=(x - 10, y, LID_TOP + LID_T - 20), pn='STD_M6x20_SOCKET', group='tool_parking',
                  material='M6x20 socket screw', purchased=True, color=HARDWARE)
    lid.shape = lid.shape.cut(cq.Compound.makeCompound([cyl(6.6, 5).translate((x, y, LID_TOP - 4)) for x, y in holes])).clean()
    lid.local = lid.shape.translate(tuple(-v for v in bb[:3]))
    lid.flat['holes'].extend((x - bb[0], y - bb[1], 6.6) for x, y in holes)
    lid.notes = list(lid.notes) + ['BT30 variant: four 6.6 holes for the BT30 cradle bases replace the ER11 cradle\'s; the ER11 holes are not drilled.']
    return {'spindle_nose_xyz_mm': [PARK_NOSE_X, PARK_Y, PARK_AXIS_Z], 'spindle_along': '-X from the nose', 'spindle_envelope_mm': [SPINDLE_D, SPINDLE_L],
            'cradle_x_mm': list(PARK_X), 'strap_count': 2}


def plasma_layout(model):
    """Module and dock out, drawdowns in their tray, the BT30 spindle in its cradles with the clamp on it (lugs forward), its
    mount and pinch screws in the hardware bin."""
    import build_revj as rev_j
    m = rev_j.plasma_layout(model)
    for p in list(m.parts):
        if p.id == 'TOOL_HOLDER_HELD_ALLOCATION':
            m.remove(p.id)
    along_x = dict(u=(0, 0, 1), v=(0, 1, 0))          # local Z (the spindle axis) along world -X
    pinch = mount = nuts = 0
    for p in m.parts:
        if p.id == SPINDLE_ID:
            p.shape = place(p.local, (PARK_NOSE_X, PARK_Y, PARK_AXIS_Z), **along_x)
            p.group = 'stored_tool'
        elif p.id == 'TOOL_SPINDLE_CLAMP':
            p.shape = place(p.local, (PARK_NOSE_X - 65.0, PARK_Y - (LUG_L + WALL_FRONT + SPINDLE_D / 2), PARK_AXIS_Z - CLAMP_W / 2), **along_x)
            p.group = 'stored_tool'
        elif p.id.startswith('TOOL_CLAMP_PINCH_NUT_'):
            nuts += 1
            p.shape = place(p.local, (815 + 15 * nuts, 810, 436.144))
            p.group = 'stored_hardware'
        elif p.id.startswith('TOOL_CLAMP_PINCH_'):
            pinch += 1
            p.shape = place(p.local, (815, 740 + 18 * pinch, 442.7), u=(0, 1, 0), v=(0, 0, 1))
            p.group = 'stored_hardware'
        elif p.id.startswith('TOOL_CLAMP_MOUNT_'):
            p.shape = place(p.local, (910 + 11 * mount, 745, 436.144), u=(1, 0, 0), v=(0, 1, 0))
            mount += 1
            p.group = 'stored_hardware'
    return m
