"""Rev H one-piece router bed module for GM1: welded steel, aluminum T-slot, HDPE top.

Owner requirements of 26 September 2026: one piece, lifted out with an
overhead beam and trolley hoist, released by no more than about twelve M8-M12
screws, and waterproof for mist coolant when cutting aluminum (no MDF).

The module (MOD_* ids) lifts 70 mm in place, travels forward out of the open
front window on the hoist, and is set down outside the machine. Six M10
drawdowns (BED_M10_*) are removed first; two pins locate it on return. Four
lift lugs sit beyond the ends of the T-slot deck at X150/X1000, so the sling
legs stay clear of the rear-parked gantry, the Y rails and the front stops.
Nominal engineering definition, not a released load rating.
"""
import math
import cadquery as cq
from cad_helpers import *
from bed_details import profile_20100

TOP = 920.8                     # T-slot strip underside = crossmember tops
PAD_T = 6.0
PAD_Z = 840.0                   # ledger top
RAIL_Z = PAD_Z + PAD_T          # 846, module rail underside
SIDE = 50.8; WALL = 3.048
RAIL_X = (62.0, 1037.2)         # rail x0, left/right; 11.2 mm to the frame legs
BOLT_X = (87.4, 1062.6)         # drawdown and pin axis, 2.15 mm inside ledger walls
RAIL_Y = (8.0, 1345.0)          # caps included; sand ports on the ledgers start Y1355
STATIONS = (25.0, 670.0, 1310.0)        # drawdown Y, front/middle/rear
PAD_Y = ((5.0, 65.0), (640.0, 700.0), (1280.0, 1340.0))
PAD_X = ((55.0, 100.0), (1050.0, 1095.0))
PIN_Y = 52.0                    # both pins at the front station; right pad slotted in X
XM_X = (118.8, 1031.2)          # crossmember between 6 mm end plates
XM_Y = (85.4, 476.0, 867.0, 1257.4)     # centres; float bands Y575..745 and 1172..1222 avoided
XM_Z = TOP - SIDE               # 870
STRIP_X0 = 125.0; STRIPS = 9; STRIP_Y = (73.0, 1270.0)
STRIP_SLOT = {0: 30, 1: 70, 2: 30, 3: 70}   # bottom slot used at each crossmember
PLATE_T = 18.0                  # finished HDPE thickness (19.05 rough, one skim)
PLATES = ((176.0, 574.0), (576.0, 974.0))
PLATE_Y = (130.0, 1130.0)
PLATE_FIX_X = ((215.0, 535.0), (615.0, 935.0))  # top-slot centres under each plate
PLATE_FIX_Y = (170.0, 630.0, 1090.0)
CB_D = 20.0; CB_FLOOR = TOP + 20 + 6.0         # counterbore floor Z946.8: 6 mm HDPE under washer
LUG_X = (150.0, 1000.0)
LUG_T = 9.525                  # 3/8 in plate
LUG_FRONT_Y = XM_Y[0] - SIDE / 2              # 60, lug rear face on crossmember 1
LUG_REAR_Y = XM_Y[3] + SIDE / 2               # 1282.8
LUG_HOLE_Z = 920.0; LUG_HOLE_D = 14.0
LIFT_MM = 70.0                 # every part near the float backrails passes 6 mm above them
DENSITY = {'steel': 7.85e-6, 'aluminum': 2.7e-6, 'hdpe': 9.5e-7}


def hollow_y(length):
    """2 x 2 x .120 tube along +Y from the local origin."""
    return box(SIDE, length, SIDE).cut(box(SIDE - 2 * WALL, length + 2, SIDE - 2 * WALL).translate((WALL, -1, WALL))).clean()


def hollow_x(length):
    return box(length, SIDE, SIDE).cut(box(length + 2, SIDE - 2 * WALL, SIDE - 2 * WALL).translate((-1, WALL, WALL))).clean()


def density(p):
    text = p.material.lower()
    if 'hdpe' in text:
        return DENSITY['hdpe']
    if '6063' in text or 'alumin' in text:
        return DENSITY['aluminum']
    return DENSITY['steel']


def make_bed(m):
    ledger_cuts = {0: [], 1: []}
    # --- Fixed receiver: six welded pads, six sealed M10 sleeves in the sand-filled ledgers.
    for side in (0, 1):
        bx = BOLT_X[side]; px0, px1 = PAD_X[side]
        for si, (sy, (py0, py1)) in enumerate(zip(STATIONS, PAD_Y)):
            holes = [(bx - px0, sy - py0, 11.0)]
            slots = []
            label = f'{"LR"[side]}_{si + 1}'
            if si == 0:
                if side == 0:
                    holes.append((bx - px0, PIN_Y - py0, 10.05))
                else:
                    slots.append((bx - px0, PIN_Y - py0, 16.0, 10.05, 0))
            pn = 'H_PAD_' + ('FRONT_ROUND' if si == 0 and side == 0 else 'FRONT_SLOT' if si == 0 else 'PLAIN')
            p = m.add_plate('H_PAD_' + label, px1 - px0, py1 - py0, PAD_T, holes=holes, slots=slots,
                            origin=(px0, py0, PAD_Z), pn=pn, group='bed_fixed',
                            notes=['6 mm steel seat pad, fully on the ledger top. Weld all round with 3 mm fillets BEFORE the ledger is sand-filled.',
                                   'After welding, face all six pad tops coplanar within 0.1 mm (fly-cut or shim-map), then drill the Ø11 bolt hole through into the ledger sleeve.',
                                   'Front pads only: left Ø10.05 locating hole (reamed to the measured pin), right 10.05 x 16 slot along X. The slot axis passes through the left pin.'])
            p.flat['machining_notes'] = ['Face top after welding; the six pad tops define the bed seating plane.',
                                         'Ø11 clearance hole concentric with the ledger sleeve below.',
                                         'Front pads: ream the pin hole/slot to the measured Ø10 pin plus 0.05 mm.']
            m.add(f'H_LEDGER_SLEEVE_{label}', pipe(SIDE, 18, 10), origin=(bx, sy, 789.2), pn='H_LEDGER_M10_SLEEVE',
                  group='bed_fixed', material='Machined steel',
                  notes=['OD18 x 50.8 sleeve through BOTH ledger walls; continuous seal welds top and bottom, finished flush, BEFORE sand fill. The ledger is a ballast compartment: never drill it after filling.',
                         'Drill 8.5 and tap M10x1.5 at least 25 deep from the top after welding. STEP bore is the nominal M10 thread envelope.'])
            ledger_cuts[side].append(cyl(18, SIDE + 2).translate((bx, sy, 788.2)))
    for side in (0, 1):
        ledger = m.find('MF_RECEIVER_LEDGER_' + str(side + 1))
        ledger.shape = ledger.shape.cut(cq.Compound.makeCompound(ledger_cuts[side])).clean()
        bb = bbox(ledger.shape); ledger.local = ledger.shape.translate(tuple(-v for v in bb[:3]))
        ledger.notes.append(f'Rev H receiver: three Ø18 sleeve bores through both walls at X{BOLT_X[side]}, Y{"/".join(str(int(y)) for y in STATIONS)}. '
                            'Weld the sleeves and the three seat pads before ballast filling.')

    # --- Module weldment: two capped side rails, four crossmembers with end plates, four lugs.
    rail_len = RAIL_Y[1] - RAIL_Y[0] - 2 * WALL
    for side in (0, 1):
        x0 = RAIL_X[side]; bx = BOLT_X[side]
        tools = [cyl(18, SIDE + 2).translate((bx - x0, sy - RAIL_Y[0] - WALL, -1)) for sy in STATIONS]
        tools.append(cyl(10, SIDE + 2).translate((bx - x0, PIN_Y - RAIL_Y[0] - WALL, -1)))
        rail = hollow_y(rail_len).cut(cq.Compound.makeCompound(tools)).clean()
        m.add(f'MOD_RAIL_{"LR"[side]}', rail, origin=(x0, RAIL_Y[0] + WALL, RAIL_Z), pn='MOD_RAIL', group='bed_module',
              material='A500 2x2x.120 tube', length=rail_len,
              notes=['Module side rail. Bears only on the three seat pads; no other contact with the ledger.',
                     'Ø18 bores through both walls at the three drawdown stations; Ø10 bores through both walls for the front locating pin.',
                     'Weld sleeves, pins, crossmember end plates and end caps, then hot-dip galvanize the complete module weldment (vent holes per galvanizer).'])
        for end, y in (('F', RAIL_Y[0]), ('R', RAIL_Y[1] - WALL)):
            m.add_plate(f'MOD_RAIL_CAP_{"LR"[side]}_{end}', SIDE, SIDE, WALL, origin=(x0, y + WALL, RAIL_Z), u=(1, 0, 0), v=(0, 0, 1),
                        pn='MOD_RAIL_CAP', group='bed_module', material='A36 steel 0.120 in sheet',
                        notes=['Seal-weld end cap. Galvanizing vent holes as the galvanizer specifies; seal or leave open to drain as agreed.'])
        for si, sy in enumerate(STATIONS):
            m.add(f'MOD_SLEEVE_{"LR"[side]}_{si + 1}', pipe(SIDE, 18, 11), origin=(bx, sy, RAIL_Z), pn='MOD_COMPRESSION_SLEEVE',
                  group='bed_module', material='Machined steel', length=SIDE,
                  notes=['OD18 ID11 x 50.8 through both rail walls; weld and finish flush both faces. Carries the M10 drawdown preload without crushing the tube.'])
        m.add(f'MOD_PIN_{"LR"[side]}', cyl(10, 56), origin=(bx, PIN_Y, RAIL_Z - 5.2), pn='STD_DOWEL_10x56', group='bed_module',
              material='Hardened stainless dowel pin, Ø10 m6 x 56', purchased=True, color=HARDWARE,
              notes=['Press through both rail walls; top flush with the rail top, 5.2 mm projects below the rail into the front pad hole (left) or slot (right).',
                     'Pins sit in the moving module, so nothing projects above the pads in plasma mode (pad tops Z846, slat tops Z850).'])
    for ci, cy in enumerate(XM_Y, 1):
        y0 = cy - SIDE / 2
        top = []; bottom = []
        for k in range(STRIPS):
            sx = STRIP_X0 + 100 * k + STRIP_SLOT[ci - 1]
            sy = strip_screw_y(ci - 1)
            top.append(cyl(5.5, WALL + 2).translate((sx - XM_X[0], sy - y0, SIDE - WALL - 1)))
            bottom.append(cyl(14, WALL + 2).translate((sx - XM_X[0], sy - y0, -1)))
        xm = hollow_x(XM_X[1] - XM_X[0]).cut(cq.Compound.makeCompound(top + bottom)).clean()
        m.add(f'MOD_XM_{ci}', xm, origin=(XM_X[0], y0, XM_Z), pn=f'MOD_CROSSMEMBER_{ci}', group='bed_module',
              material='A500 2x2x.120 tube', length=XM_X[1] - XM_X[0],
              notes=['2 x 2 x .120 crossmember; top is the T-slot seating plane at Z920.8. Not a precision surface: the HDPE top is surfaced in the machine.',
                     'Top wall: nine Ø5.5 holes for the M5 strip screws. Bottom wall: nine Ø14 access holes on the same axes, which also drain coolant after galvanizing.',
                     'Y position keeps the crossmember out of the pan-float bands at Y575..745 and Y1172..1222 in the installed position.'])
        for side, ex in enumerate((XM_X[0] - 6, XM_X[1])):
            m.add_plate(f'MOD_XM_END_{ci}_{"LR"[side]}', SIDE, TOP - RAIL_Z, 6, origin=(ex, y0, RAIL_Z), u=(0, 1, 0), v=(0, 0, 1),
                        pn='MOD_XM_END_PLATE', group='bed_module', material='A36 steel',
                        notes=['6 mm end plate 50.8 x 74.8: closes the crossmember and joins it over the full rail height. Continuous 4 mm fillets to crossmember and rail.'])
    lug = [(0, 0), (50, 0), (50, 60), (40, 75), (10, 75), (0, 60)]
    for end, y0 in (('F', LUG_FRONT_Y - 50), ('R', LUG_REAR_Y)):
        for li, lx in enumerate(LUG_X, 1):
            m.add_plate(f'MOD_LUG_{end}_{li}', 50, 75, LUG_T, outline=lug, holes=[(25, LUG_HOLE_Z - XM_Z, LUG_HOLE_D)],
                        origin=(lx - LUG_T / 2, y0, XM_Z), u=(0, 1, 0), v=(0, 0, 1), pn='MOD_LIFT_LUG', group='bed_module', material='A36 steel',
                        notes=['3/8 in (9.525) lift lug welded to the crossmember end face, full height, 6 mm fillets both sides. Ø14 hole takes a 3/8 in screw-pin shackle (7/16 in pin).',
                               'Four lugs at X150/X1000 beyond both deck ends. The 4-leg sling runs inboard of the Y rails and forward of the rear-parked gantry; see the handling check.',
                               'Proof-load the finished module lift once at 2 x module mass before first use; lifting-equipment rules for the jurisdiction apply.'])

    # --- Nine cut-only T-slot strips seated directly on the crossmembers, fastened from inside.
    nominal = profile_20100(STRIP_Y[1] - STRIP_Y[0])
    tnut = box(8, 8, 2.7).translate((-4, -4, 0)).cut(cyl(5, 2.7)).clean()
    for k in range(STRIPS):
        sx = STRIP_X0 + 100 * k
        m.add(f'MOD_STRIP_{k + 1}', nominal, origin=(sx, STRIP_Y[0], TOP), pn='BUY_20100_1197', group='bed_module', material='Purchased 6063-T5 profile',
              color=ALU, purchased=True,
              notes=['Purchased 20100 profile, one saw cut per 1220 mm bar to 1197. No drilling. Slots run front-to-back.',
                     'Seated directly on the four crossmembers; one M5 screw per crossmember from inside the tube into a square nut in the bottom slot.'])
        for ci in range(4):
            x = sx + STRIP_SLOT[ci]; y = strip_screw_y(ci)
            screw = cyl(5, 8).fuse(cyl(9.5, 2.75).translate((0, 0, -2.75))).clean()
            sc = m.add(f'MOD_STRIP_{k + 1}_XM{ci + 1}_SCREW', screw, origin=(x, y, TOP - WALL), pn='STD_M5x8_ISO7380_A4', group='bed_module_hardware',
                       material='M5x8 stainless button head', purchased=True, color=HARDWARE,
                       notes=['Inserted upward through the Ø14 bottom access hole. Stainless A4; anti-seize on aluminum.'])
            nut = m.add(f'MOD_STRIP_{k + 1}_XM{ci + 1}_NUT', tnut, origin=(x, y, TOP + 1.3), pn='STD_DIN562_M5_A4', group='bed_module_hardware',
                        material='M5 stainless square nut DIN562', purchased=True, color=HARDWARE,
                        notes=['Slide into the bottom slot from the strip end before the strip is placed; seats on the 1.3 mm lips.'])
            m.permit(sc.id, nut.id, 'M5 thread engages the square nut inside the bottom slot.')

    # --- Two HDPE plates within tool reach, counterbored M5 into top-slot nuts.
    for pi, ((x0, x1), fix_x) in enumerate(zip(PLATES, PLATE_FIX_X), 1):
        w = x1 - x0; length = PLATE_Y[1] - PLATE_Y[0]
        holes = []; slots = []; ops = []
        for ri, fy in enumerate(PLATE_FIX_Y):
            for ci, fx in enumerate(fix_x):
                lx, ly = fx - x0, fy - PLATE_Y[0]
                if ri == 1 and ci == 0:
                    holes.append((lx, ly, 5.5))                  # fixed point
                elif ri == 1:
                    slots.append((lx, ly, 9.0, 5.5, 0))          # grows along X only
                elif ci == 0:
                    slots.append((lx, ly, 9.0, 5.5, 90))         # grows along Y only
                else:
                    holes.append((lx, ly, 9.0))                  # grows both ways
                ops.append({'type': 'circle', 'x': lx, 'y': ly, 'diameter': CB_D, 'layer': 'MILL_TOP_COUNTERBORE_FLOOR_6_ABOVE_UNDERSIDE'})
        plate_shape = plate(rect(w, length), PLATE_T, holes=holes, slots=slots)
        pockets = [cyl(CB_D, PLATE_T).translate((op['x'], op['y'], CB_FLOOR - (TOP + 20))) for op in ops]
        plate_shape = plate_shape.cut(cq.Compound.makeCompound(pockets)).clean()
        flat = {'outline': rect(w, length), 'thickness_mm': PLATE_T, 'holes': holes, 'slots': slots, 'internal': [], 'operations': ops,
                'machining_notes': ['Cut from 3/4 in (19.05 nominal) HDPE sheet; skim to 18.0 in the machine after installation. STEP is the finished state.',
                                    'Counterbore Ø20 so its floor is 6.0 mm above the underside (room for the 15 mm washer to move with the slots). M5 heads then sit 5.5 mm below the finished top.',
                                    'Thermal growth: one fixed Ø5.5 hole, 9 x 5.5 slots radiate from it, far corner holes Ø9 under 15 mm washers. Do not over-tighten; snug only.']}
        m.add(f'MOD_HDPE_{pi}', plate_shape, origin=(x0, PLATE_Y[0], TOP + 20), pn=f'MOD_HDPE_PLATE_{pi}', group='bed_module',
              material='HDPE sheet 3/4 in, finish 18.0', color=(.86, .87, .84), flat=flat,
              notes=['398 x 1000 sacrificial top within tool reach (X175..975, Y130..1130 covers the nominal and the possible 20 mm rearward ZBX80 shift).',
                     'Waterproof, does not swell with coolant. Surface in place after the module is seated; re-skim if the module is reinstalled and the probe map moves.',
                     'HDPE expands about 0.15 mm per metre per degC: the fastener pattern lets it grow from one fixed point.'])
        for ri, fy in enumerate(PLATE_FIX_Y):
            for ci, fx in enumerate(fix_x):
                pre = f'MOD_HDPE_{pi}_F{ri + 1}{ci + 1}'
                screw = cyl(5, 12).fuse(cyl(8.5, 5).translate((0, 0, 12))).clean()
                washer_z = CB_FLOOR
                sc = m.add(pre + '_SCREW', screw, origin=(fx, fy, washer_z + 1.5 - 12), pn='STD_M5x12_ISO4762_A4', group='bed_module_hardware',
                           material='M5x12 stainless socket head', purchased=True, color=HARDWARE)
                m.add(pre + '_WASHER', pipe(1.5, 15, 5.3), origin=(fx, fy, washer_z), pn='STD_M5_WASHER_15_A4', group='bed_module_hardware',
                      material='M5 stainless washer 15x5.3x1.5', purchased=True, color=HARDWARE)
                nut = m.add(pre + '_NUT', tnut, origin=(fx, fy, TOP + 20 - 1.3 - 2.7), pn='STD_DIN562_M5_A4', group='bed_module_hardware',
                            material='M5 stainless square nut DIN562', purchased=True, color=HARDWARE,
                            notes=['Top-slot nut; slide in from the strip end before the plate is placed.'])
                m.permit(sc.id, nut.id, 'M5 thread engages the square nut inside the top slot.')

    # --- Six removable drawdowns: the only release fasteners.
    for side in (0, 1):
        bx = BOLT_X[side]
        for si, sy in enumerate(STATIONS):
            label = f'{"LR"[side]}_{si + 1}'
            washer_z = RAIL_Z + SIDE
            bolt = cyl(10, 80).fuse(cyl(16, 10).translate((0, 0, 80))).clean()
            m.add(f'BED_M10_{label}', bolt, origin=(bx, sy, washer_z + 2 - 80), pn='STD_M10x80_ISO4762_A4', group='removable_hardware',
                  material='M10x80 stainless A4-70 socket head', purchased=True, color=HARDWARE,
                  notes=['One of six module drawdowns, the only screws released for a bed change. 23 mm thread engagement in the ledger sleeve.',
                         'Anti-seize on the thread; 30 N m. Remove all six to the bolt tray before lifting.'])
            m.add(f'BED_M10_WASHER_{label}', pipe(2, 20, 10.5), origin=(bx, sy, washer_z), pn='STD_M10_WASHER_A4', group='removable_hardware',
                  material='M10 stainless washer 20x10.5x2', purchased=True, color=HARDWARE)

    make_bolt_tray(m)
    module = [p for p in m.parts if p.id.startswith('MOD_')]
    mass = sum(p.shape.Volume() * density(p) for p in module)
    cg = [sum(p.shape.Center().toTuple()[k] * p.shape.Volume() * density(p) for p in module) / mass for k in range(3)]
    return {'revision': 'H one-piece hoisted module',
            'architecture_assumption': 'One-piece welded module lifted in place and carried out of the front window on the owner overhead beam and trolley hoist; set down outside the machine for plasma work.',
            'owner_requirements_2026_09_26': ['one piece, lifted out with a winch/hoist', 'at most about 12 release screws, M8 to M12',
                                              'waterproof for mist coolant on aluminum: no MDF'],
            'bare_deck_mm': [STRIPS * 100, STRIP_Y[1] - STRIP_Y[0], 20], 'workplane_z_mm': TOP + 20,
            'finished_top_z_mm': TOP + 20 + PLATE_T, 'hdpe_plates_mm': [[x0, PLATE_Y[0], x1, PLATE_Y[1]] for x0, x1 in PLATES],
            'module_stack': 'Ledger Z840 > 6 mm seat pads 846 > rails 2x2 846..896.8 > crossmembers 2x2 870..920.8 > 20100 strips 920.8..940.8 > HDPE 940.8..958.8 finished',
            'release_fasteners': {'count': 6, 'size': 'M10x80 ISO 4762 A4-70', 'locating_pins': 2},
            'module_internal_fasteners': {'strip_M5': STRIPS * 4, 'hdpe_M5': 12},
            'lift_lugs': {'count': 4, 'holes_xyz_mm': [[x, y, LUG_HOLE_Z] for y in (LUG_FRONT_Y - 25, LUG_REAR_Y + 25) for x in LUG_X],
                          'shackle': '3/8 in screw-pin anchor shackle, WLL at least 0.5 t each'},
            'module_mass_estimate_kg': round(mass, 1), 'module_cg_mm': [round(v, 1) for v in cg],
            'module_mass_basis': 'Nominal solids: steel 7850, aluminum 2700 (reconstructed 20100 section), HDPE 950 kg/m3, stainless hardware as steel. Weigh the module before the first lift.',
            'handling_lift_mm': LIFT_MM,
            'handling': 'Owner overhead beam with trolley hoist over the machine centreline, running at least 1.6 m in front of the machine. 4-leg sling to the four lugs, hook above the module centre of mass.',
            'sequence': ['Router off and isolated; spindle removed or Z fully raised. Gantry at the front: remove the two rear M10 drawdowns.',
                         'Gantry to the rear stop, head at X575 (centre). Remove the four remaining drawdowns; all six go to the bolt tray.',
                         'Rig the 4-leg sling to the lugs, take the slack, lift 70 mm: pins clear the pads and every module part passes above the pan-float backrails (top Z910).',
                         'Trolley forward about 1.45 m, guiding the module by hand through the front window; two people.',
                         'Set the module down on its stand outside the machine. Clear chips, then continue with the plasma water sequence.',
                         'Reverse to install: lower the last 70 mm onto the pins, fit and torque the six drawdowns, re-probe the HDPE surface.'],
            'storage': {'module': 'Outside the machine footprint on an owner-provided stand or cart; not left suspended over a walkway.',
                        'bolts': 'Six M10 drawdowns and washers in the bolt tray on the reservoir lid.',
                        'stored_inside': 'Spindle in the existing cradle; tool-clamp hardware in the existing tray.'},
            'plasma_support_clearance': 'With the module out, the seat pads (top Z846) stay 4 mm below the slat tops (Z850); nothing projects above them.',
            'release_holds': ['Owner hoist, beam, trolley and sling ratings; beam height gives the hook at least 1.0 m above the lugs.',
                              'Module weighed; lift proof test; galvanized weldment inspected.',
                              'Seat-pad coplanarity and repeat-seating map; surfacing of the HDPE in place.',
                              'Actual 20100 section, square-nut fit and M5 preload in the strips.',
                              'Owner-provided module stand or cart and the floor space in front of the machine.']}


def strip_screw_y(ci):
    """Y of the strip screws at crossmember ci, inside the strip bearing length."""
    y = XM_Y[ci]
    if ci == 0:
        return (STRIP_Y[0] + XM_Y[0] + SIDE / 2) / 2      # between strip front end and crossmember rear face
    if ci == 3:
        return (XM_Y[3] - SIDE / 2 + STRIP_Y[1]) / 2      # between crossmember front face and strip rear end
    return y


def make_bolt_tray(m):
    """Small tray on the reservoir lid for the six drawdowns (Rev G front-seat tray location)."""
    lid_top = 433.096
    m.add_plate('H_BOLT_TRAY_FLOOR', 210, 120, 3, origin=(300, 800, lid_top), group='bed_storage', pn='H_BOLT_TRAY_FLOOR',
                material='304 stainless 3 mm sheet',
                notes=['Seal-weld to the removable reservoir lid. Holds the six M10 drawdowns and washers while the module is out.'])
    for side, x in enumerate((300, 507)):
        m.add_plate(f'H_BOLT_TRAY_SIDE_{side + 1}', 120, 20, 3, origin=(x, 800, lid_top + 3), u=(0, 1, 0), v=(0, 0, 1),
                    pn='H_BOLT_TRAY_SIDE', group='bed_storage', material='304 stainless 3 mm sheet')
    for side, y in enumerate((803, 920)):
        m.add_plate(f'H_BOLT_TRAY_END_{side + 1}', 204, 20, 3, origin=(303, y, lid_top + 3), u=(1, 0, 0), v=(0, 0, 1),
                    pn='H_BOLT_TRAY_END', group='bed_storage', material='304 stainless 3 mm sheet')


def bolt_tray_positions():
    """Stored bolt axis origins: shank tip at x0, lying along +X on their washers."""
    return [(x0, y, 433.096 + 3 + 10) for x0 in (312.0, 410.0) for y in (825.0, 857.0, 889.0)]
