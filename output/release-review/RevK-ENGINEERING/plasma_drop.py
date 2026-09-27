"""GM1 Rev K plasma drop bracket: lowers the Rev I floating head so the torch reaches the work.

At the bottom of the 100 mm Z stroke the Rev I head's torch clamp ends at Z1095,
while the slats that carry plasma sheets are at Z850 (review blocker 4). Rev K fits a
1/2 in 6061 plate between the Z tool adapter and the head's backplate:

- The head sits DROP (135) mm lower and T (12.7) mm further forward, on the adapter's
  centreline: the torch axis is at machine X, Y = gantry Y - 201.4. A sideways offset
  was tried and dropped: at X175 the head is only 13.5 mm from the gantry's left Y shoe
  and its bolts.
- The three pan level sensors (X978..1015, Y578..745) stand up to 38 mm above the slats,
  so no sheet can lie over them. With the torch below Z900, plasma paths stay at X955
  or less in the band Y558..765; at the top of Z the torch clears them at full X.
- The owner's torch (photo, 27 Sep 2026) is a straight PT31-style machine torch, 270 mm
  long with a 28 mm barrel (seller's dimensions). The clamp holds the straight rear
  barrel with its lower face TORCH_PROJECTION (115) mm above the tip; a 28 mm shaft
  collar on the barrel sets that on every refit.
- At the bottom of Z the tip is at Z845, 5 mm below the slat tops: with no sheet the
  6 mm float is 5 mm compressed, so Z can bottom out without reaching the float's hard
  stop. At the top of Z the tip is at Z945.
- Two vertical slots give +/-25 mm, covering projections of 90..140 mm.

The bracket stays bolted to the head by four countersunk screws. The pair leaves the
adapter by four M6x30 screws through the slots (nuts on the bracket front, where the
Rev I head used four M6x16) and parks on its back on the reservoir lid: three new
pads, two M5 screws in the bracket's top section. The torch comes out of the clamp
(two M4 pinch screws) and hangs from its lead while the router is fitted.
"""
import cadquery as cq

from cad_helpers import cyl, plate, place, bbox, ALU, HARDWARE, PURCHASED
from frame_details import hexpart
import motion_finish as rev_i

DROP = 135.0
SLOT = 25.0
T = 12.7
X_OFFSET = 0.0                      # head on the adapter centreline (see the docstring)
TORCH_PROJECTION = 115.0            # clamp lower face to nozzle tip
TORCH_LENGTH = 270.0                # PT31-style straight machine torch, seller's figure
TORCH_BARREL_D = 28.0               # seller's figure; confirm with calipers before boring the insert
TORCH_NOSE_D = 30.0                 # conservative envelope for the cup, standoff guide and ring collar
TORCH_NOSE_LENGTH = 105.0           # tip to the start of the straight rear barrel, scaled from the photo
INSERT_BORE = TORCH_BARREL_D + .10  # Rev I rule: measured barrel + 0.10
COLLAR_D, COLLAR_W = 50.0, 16.0     # one-piece 28 mm bore clamp collar, outer envelope
LEAD_ZONE = 80.0                    # lead bend zone above the torch's rear end (check envelope)
TIP_TARGET_Z = 845.0
CLAMP_BOTTOM_HEAD_Y = 25.0          # Rev I clamp and insert start at head-local Y25
TORCH_AXIS_HEAD = (55.0, 80.6)      # head-local X, Z of the clamp bore
TOP_Y = 90.0                        # bracket top, head-local Y (the adapter face is Y0..110)
ADAPTER_HOLES = [(x, y) for x in (10.0, 100.0) for y in (22.0, 48.0)]
PARK_SCREWS = [(30.0, 40.0), (80.0, 40.0)]            # bracket top section, clear of the head and the slots
PARK_PADS = PARK_SCREWS + [(25.0, -100.0)]            # third pad between the head screw columns
PARK = (550.0, 830.0, 442.096)      # bracket origin when parked; Rev I parked at Y745, which left this longer bracket off the lid
ADAPTER_WEB = 6.7                   # Rev I: adapter web the mount screws pass


def outline(drop=DROP):
    return [(X_OFFSET, -drop), (110.0, -drop), (110.0, TOP_Y), (X_OFFSET, TOP_Y)]


def bracket_flat(drop=DROP):
    """Flat definition in bracket-local X/Y (= head-local X/Y); thickness along head-local Z, Z0 = rear face."""
    lo, hi = 22.0 - SLOT, 48.0 + SLOT
    slots = [(x, (lo + hi) / 2, hi - lo + 6.6, 6.6, 90) for x in (10.0, 100.0)]
    holes = [(x + X_OFFSET, y - drop, 6.6) for x, y in ADAPTER_HOLES] + [(x, y, 5.5) for x, y in PARK_SCREWS]
    return dict(outline=outline(drop), thickness_mm=T, holes=holes, slots=slots, internal=[],
                operations=[dict(type='circle', x=x + X_OFFSET, y=y - drop, diameter=13.0, layer='CSK90_REAR_FACE') for x, y in ADAPTER_HOLES],
                machining_notes=[f'Two 6.6 wide vertical slots at X10/X100, centres Y{lo:g}..{hi:g}, take the four adapter screws. '
                                 'Set the height from the measured torch, tighten the nyloc nuts and scribe a witness line.',
                                 f'Four Ø6.6 holes at X{10 + X_OFFSET:g}/{100 + X_OFFSET:g}, Y{22 - drop:g}/{48 - drop:g}, 90° countersink to Ø13 on the REAR face, '
                                 'for M6x20 countersunk screws into the Rev I head backplate taps. Heads finish flush or below the rear face.',
                                 'Two Ø5.5 park-screw holes at X30/80, Y40.'])


def bracket_solid(drop=DROP):
    f = bracket_flat(drop)
    s = plate(f['outline'], T, f['holes'], f['slots'], [])
    for x, y in ADAPTER_HOLES:
        s = s.cut(cq.Solid.makeCone(6.5, 3.3, 3.2).translate((x + X_OFFSET, y - drop, 0)))
    return s.clean()


def csk_screw():
    """M6x20 countersunk envelope along +Z: head in the countersink, shank beyond."""
    return cq.Solid.makeCone(6.0, 3.0, 3.0).translate((0, 0, .15)).fuse(cyl(6, 16.85).translate((0, 0, 3.15))).clean()


def add_bracket(m, origin, working, drop=DROP):
    """origin: bracket-frame origin (adapter min corner in work, park corner when stored)."""
    uv = dict(u=(1, 0, 0), v=(0, 0, 1)) if working else {}
    p = m.add('K_HEAD_DROP_BRACKET', bracket_solid(drop), origin, pn=f'K_HEAD_DROP_BRACKET_{int(drop)}',
              group='plasma_head_hardware', material='6061-T6 aluminium plate 1/2 in (12.7)', color=ALU, flat=bracket_flat(drop),
              notes=[f'{110 - X_OFFSET:g} x {TOP_Y + drop:g} x 12.7 plate between the Z tool adapter and the Rev I head backplate. '
                     f'Lowers the head {drop:g} mm and moves it 12.7 mm forward; slots give +/-{SLOT:g} mm.',
                     f'Set the height from the measured torch so the tip is at Z{TIP_TARGET_Z:g} at the bottom of Z '
                     f'(clamp-to-tip projection {TORCH_PROJECTION:g} mm nominal, {TORCH_PROJECTION - SLOT:g}..{TORCH_PROJECTION + SLOT:g} in range).',
                     'Stays bolted to the head. The pair parks on its back on the reservoir lid.'], **uv)
    for i, (x, y) in enumerate(ADAPTER_HOLES, 1):
        s = m.add(f'K_HEAD_DROP_SCREW_{i}', csk_screw(), origin, pn='K_STD_M6x20_CSK', group='plasma_head_hardware',
                  material='M6x20 ISO 10642 countersunk steel screw', purchased=True, color=HARDWARE, **uv)
        s.local = csk_screw().translate((x + X_OFFSET, y - drop, 0))
        s.shape = place(s.local, origin, **uv) if working else s.local.translate(origin)
        m.permit(s.id, rev_i.PREFIX + 'BACKPLATE', 'M6 thread engagement in the tapped Rev I backplate.')
    return p


def _bore_inserts(head):
    """Bore the Rev I split insert blank for the 28 mm barrel (head coordinates, before placing)."""
    tool = rev_i.axis_y(cyl(INSERT_BORE, 42)).translate((TORCH_AXIS_HEAD[0], 24, TORCH_AXIS_HEAD[1]))
    for side, z in (('REAR', 50.6), ('FRONT', 80.85)):
        p = head.find(rev_i.PREFIX + 'INSERT_' + side)
        p.shape = p.shape.cut(tool).clean()
        p.local = p.shape.translate((-25, -25, -z))
        p.release = 'BORE TO THE MEASURED BARREL + 0.10 - SELLER NOMINAL 28.0 SHOWN'
        p.notes = [f'Bored Ø{INSERT_BORE:.2f} across the assembled halves for the owner\'s PT31-style torch (seller: 28 mm barrel). '
                   'Measure the barrel with calipers (diameter and roundness, 40 mm straight zone) before boring; bore = measured + 0.10.',
                   'Insulating insert: confirm grade and temperature rating; set the pinch torque from the torch maker\'s allowable clamp load.']


def torch_model(axis_xy, clamp_bottom_z):
    """Owner's torch: nose envelope, straight barrel, depth collar and lead zone (world, vertical)."""
    x, y = axis_xy
    tip = clamp_bottom_z - TORCH_PROJECTION
    body = cyl(TORCH_NOSE_D, TORCH_NOSE_LENGTH).fuse(
        cyl(TORCH_BARREL_D, TORCH_LENGTH - TORCH_NOSE_LENGTH).translate((0, 0, TORCH_NOSE_LENGTH))).clean()
    collar = cyl(COLLAR_D, COLLAR_W).cut(cyl(TORCH_BARREL_D, COLLAR_W)).clean()
    lead = cyl(TORCH_NOSE_D, LEAD_ZONE)
    return {'body': body.translate((x, y, tip)), 'collar': collar.translate((x, y, clamp_bottom_z + 40)),
            'lead': lead.translate((x, y, tip + TORCH_LENGTH)), 'tip_z': tip}


def add_torch(m, axis_xy, clamp_bottom_z):
    t = torch_model(axis_xy, clamp_bottom_z)
    m.add('K_TORCH_PT31', t['body'], pn='OWNER_TORCH_PT31_STRAIGHT_270', group='plasma_torch', purchased=True, color=PURCHASED,
          material='Owner plasma torch, PT31-style straight machine torch',
          release='OWNER PART - SELLER DIMENSIONS; MEASURE BEFORE BORING THE CLAMP INSERT',
          notes=[f'Straight PT31-style machine torch: {TORCH_LENGTH:g} mm overall, Ø{TORCH_BARREL_D:g} barrel (seller listing, owner photo 27 Sep 2026).',
                 f'Lower {TORCH_NOSE_LENGTH:g} mm (cup, standoff guide, front sleeve and ring collar) modeled as a Ø{TORCH_NOSE_D:g} envelope; '
                 'their true diameters are not published.',
                 f'Clamped on the straight rear barrel with the clamp lower face {TORCH_PROJECTION:g} mm above the tip.'])
    m.add('K_TORCH_DEPTH_COLLAR', t['collar'], pn='K_COLLAR_28_ONE_PIECE', group='plasma_torch', purchased=True, color=HARDWARE,
          material='Purchased one-piece clamp collar, 28 mm bore',
          release='SELECT A ONE-PIECE CLAMP COLLAR, 28 MM BORE, OD <= 50, WIDTH <= 16',
          notes=['Clamped on the barrel so it seats on the clamp top: the torch goes back to the same height after every router session.'])
    m.add('K_TORCH_LEAD_ZONE', t['lead'], pn='K_TORCH_LEAD_ZONE', group='plasma_torch_envelope', purchased=True, color=PURCHASED,
          material='Check envelope, not a part',
          release='CHECK ENVELOPE ONLY - LEAD BEND ZONE ABOVE THE TORCH',
          notes=[f'Ø{TORCH_NOSE_D:g} x {LEAD_ZONE:g} mm above the rear end, where the lead leaves the torch. Strap the lead to the head\'s lead saddle '
                 'and give it a service loop for the full Z stroke and the 6 mm float.'])
    m.permit('K_TORCH_DEPTH_COLLAR', 'K_TORCH_PT31', 'Collar clamped on the torch barrel.')
    return t['tip_z']


def _mount_hardware(m, stored):
    """Four adapter screws with washers and nyloc nuts, loose in the tray when stored."""
    for i in range(1, 5):
        bolt = cyl(6, 30).fuse(cyl(10.2, 6).translate((0, 0, 30))).clean()
        m.add(f'K_TOOL_MOUNT_{i}', bolt, (920 + 18 * (i - 1), 770, 436.144), pn='K_STD_M6x30_SOCKET', group='stored_hardware',
              material='M6x30 steel socket screw', purchased=True, color=HARDWARE,
              notes=['Adapter to bracket: from the adapter rear, through the bracket slot, then washer and M6 nyloc on the bracket front face.'])
        m.add(f'K_TOOL_MOUNT_WASHER_{i}', cyl(12, 1.6).cut(cyl(6.4, 1.6)).clean(), (920 + 18 * (i - 1), 790, 436.144),
              pn='STD_M6_WASHER', group='stored_hardware', purchased=True, color=HARDWARE)
        m.add(f'K_TOOL_MOUNT_NUT_{i}', hexpart(10, 6, 6), (920 + 18 * (i - 1), 805, 436.144), pn='STD_M6_NYLOC',
              group='stored_hardware', purchased=True, color=HARDWARE)


def extend_router_model(m):
    """Router state: head and bracket parked together on the reservoir lid."""
    head, meta = rev_i.make_head()
    _bore_inserts(head)
    px, py, pz = PARK
    add_bracket(m, (px, py, pz), working=False)
    rev_i._copy_into(m, head, (px + X_OFFSET, py - DROP, pz + T))
    lid = pz - 9.0
    for i, (x, y) in enumerate(PARK_PADS, 1):
        screwed = i <= len(PARK_SCREWS)
        holes = [(20, 15, 4.2)] if screwed else []
        m.add_plate(f'K_HEAD_PARK_FOOT_{i}', 40, 30, 6.35, holes=holes, origin=(px + x - 20, py + y - 15, lid), group='tool_storage',
                    pn='K_HEAD_PARK_FOOT' + ('_M5' if screwed else ''), material='Low carbon steel 1/4 in',
                    notes=['Weld to the reservoir lid with four 10 mm, 3 mm fillets; coat and leak-test.',
                           'M5x0.8 through tap.' if screwed else 'Support only.'])
        pad = rev_i.annulus(12, 5.5, 2.65) if screwed else cyl(12, 2.65)
        m.add(f'K_HEAD_PARK_PAD_{i}', pad, (px + x, py + y, pz - 2.65), pn='K_HEAD_PARK_PAD', group='tool_storage',
              material='Machined steel support pad', notes=['Machine 3 mm stock to 2.65; tack below the top datum. Check the three pads are coplanar.'])
        if screwed:
            bolt = cyl(5, 20).fuse(cyl(8.5, 5).translate((0, 0, 20))).clean()
            m.add(f'K_PARK_BOLT_{i}', bolt, (px + x, py + y, pz + T - 20), pn='K_STD_M5x20_SOCKET', group='tool_storage',
                  material='M5x20 steel socket screw', purchased=True, color=HARDWARE,
                  notes=['Head bears on the bracket top section; engages the tapped foot below the pad.'])
            m.permit(f'K_PARK_BOLT_{i}', f'K_HEAD_PARK_FOOT_{i}', 'M5 park screw thread engagement in the tapped foot.')
    _mount_hardware(m, stored=True)
    meta['parking_origin_mm'] = PARK
    meta['drop_bracket'] = {'drop_mm': DROP, 'x_offset_mm': X_OFFSET, 'adjust_mm': SLOT, 'thickness_mm': T,
                            'torch_projection_nominal_mm': TORCH_PROJECTION,
                            'torch_projection_range_mm': [TORCH_PROJECTION - SLOT, TORCH_PROJECTION + SLOT], 'tip_target_z_mm': TIP_TARGET_Z}
    meta['torch'] = {'type': 'PT31-style straight machine torch (owner photo, 27 Sep 2026)', 'length_mm': TORCH_LENGTH,
                     'barrel_d_mm': TORCH_BARREL_D, 'insert_bore_mm': INSERT_BORE, 'source': 'seller listing dimensions; not measured',
                     'parked': 'Torch out of the clamp while the router is fitted; the head and bracket park without it.'}
    return meta


def plasma_head_model(stored, drop=DROP, float_lift=0., breakaway_offset=0.):
    """Head, bracket and the owner's torch in the work position on the Z adapter."""
    import build_revg
    result = build_revg.clone_model(stored)
    moving = ('K_HEAD_DROP_BRACKET', 'K_HEAD_DROP_SCREW_')
    result.parts = [p for p in result.parts
                    if not (p.id.startswith(rev_i.PREFIX) or p.id.startswith(moving))]
    adapter = result.find('TOOL_ADAPTER_110')
    bb = bbox(adapter.shape)
    head, details = rev_i.make_head(float_lift, breakaway_offset, None)
    _bore_inserts(head)
    add_bracket(result, (bb[0], bb[1], bb[2]), working=True, drop=drop)
    rev_i._copy_into(result, head, (bb[0] + X_OFFSET, bb[1] - T, bb[2] - drop), working=True)
    uv = dict(u=(1, 0, 0), v=(0, 0, 1))
    for i, (x, y) in enumerate(ADAPTER_HOLES, 1):
        bolt = result.find(f'K_TOOL_MOUNT_{i}')
        # Head behind the adapter web; shank forward through the web and the slot.
        bolt.shape = place(place(bolt.local, (x, y, 30 - ADAPTER_WEB), u=(1, 0, 0), v=(0, -1, 0)), (bb[0], bb[1], bb[2]), **uv)
        washer = result.find(f'K_TOOL_MOUNT_WASHER_{i}')
        washer.shape = place(washer.local.translate((x, y, T)), (bb[0], bb[1], bb[2]), **uv)
        nut = result.find(f'K_TOOL_MOUNT_NUT_{i}')
        nut.shape = place(nut.local.translate((x, y, T + 1.6)), (bb[0], bb[1], bb[2]), **uv)
        for part in (bolt, washer, nut):
            part.group = 'plasma_head_hardware'
        result.permit(bolt.id, 'TOOL_ADAPTER_110', 'M6 screw in the adapter clearance hole (nominal envelope).')
    clamp_bottom = bb[2] - drop + CLAMP_BOTTOM_HEAD_Y + float_lift
    axis = (bb[0] + X_OFFSET + TORCH_AXIS_HEAD[0], bb[1] - T - TORCH_AXIS_HEAD[1])
    tip = add_torch(result, axis, clamp_bottom)
    details['status'] = 'PLASMA HEAD ON A DROP BRACKET WITH THE OWNER TORCH (SELLER DIMENSIONS); NO ENERGIZED OPERATION'
    details['drop_mm'] = drop
    details['clamp_bottom_z_mm'] = round(clamp_bottom, 3)
    details['torch_axis_xy_mm'] = [round(v, 3) for v in axis]
    details['tip_z_mm'] = round(tip, 3)
    return result, details
