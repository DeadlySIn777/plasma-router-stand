"""Presentation renders of every GM1 version in the owner's paint scheme (28 September): steel painted red and
black, aluminium in its natural finish, the plasma slats bare, bought parts graphite. Actual CAD geometry
from the same builds as the packages; no illustration parts. Writes the PNGs next to this script.

  red    the welded stand: frame, legs, bracing, feet, pan bearers, the steel water pan and reservoir, cabinet frame and drip cap, cradles
  black  what lifts out or bolts on: the bed module weldment, the tool changer's steel, the rotary shelf
  natural  aluminium (gantry plates, Z carrier, adapters, bed strips, rack bar), stainless (pan, drain), HDPE, MDF
  bare   the plasma slats and their combs, consumable steel in the water
  graphite  bought parts that are not aluminium (rails, blocks, motors, torch, switches); allocations a lighter grey
"""
from pathlib import Path
import json
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
RR = HERE.parent
for p in ('RevE-ENGINEERING', 'RevK-ENGINEERING', 'RevL-ENGINEERING', 'RevL-BT30-ENGINEERING', 'RevL-ROTARY-ENGINEERING'):
    sys.path.insert(0, str(RR / p))
sys.path.insert(0, str(RR.parents[1]))
from render_cad import _triangle, _unit  # noqa: E402
import build_revl  # noqa: E402
import build_revl_bt30 as bb  # noqa: E402
import bt30_revl as bt30  # noqa: E402
import build_revl_rotary as br  # noqa: E402
import rotary_revl as rotary  # noqa: E402

MESH = HERE / '_mesh'
RED, BLACK = (168, 30, 34), (36, 38, 42)
ALU, STAINLESS, HDPE = (200, 204, 208), (172, 178, 184), (234, 233, 226)
MDF, POLYMER = (214, 190, 150), (236, 236, 230)
GRAPHITE, ALLOC, RUBBER, BARE = (66, 70, 76), (150, 152, 158), (30, 30, 30), (110, 114, 118)
BLACK_PREFIXES = ('MOD_', 'ROT_')
BLACK_GROUPS = {'atc', 'atc_moving', 'rotary', 'plasma_head_hardware'}
BARE_GROUPS = {'slats', 'slat_support'}      # consumable bare steel in the water
RED_GROUPS = {'main_frame', 'bracing', 'feet', 'pan_support', 'tank_support', 'controls_support', 'controls_shield', 'rail_cap',
              'bed_fixed', 'tool_parking', 'bed_storage', 'hardware_storage', 'tool_storage', 'ballast', 'water_hose_support',
              'float_mount', 'float_guard', 'overflow_catch', 'motion_stops', 'limit_switches'}
ALU_KEYS = ('luminum', 'aluminium', '6061', '6063', '80/20', 'extrusion')
RUBBER_KEYS = ('epdm', 'nbr', 'rubber', 'belt', 'gasket', 'hose')
POLYMER_KEYS = ('acetal', 'polymer', 'plastic', 'ptfe', 'insulating', 'nylon', 'delrin')
HARDWARE_KEYS = ('screw', 'bolt', 'nut', 'washer', 'dowel', 'pin', 'spacer', 'contact', 'shoulder', 'grub', 'class 8.8', 'class8.8',
                 'rod end', 'shaft', 'plug', 'coupling', 'sleeve', 'hardened')
STEEL_KEYS = ('steel', 'a36', 'a500', 'tube', 'pipe', 'hss', 'weld', 'carbon', 'q235', 'iron', 'offcut')
FALLTHROUGH = []


def painted(part):
    """Red for the stand, black for what lifts out or bolts on (module, changer steel, rotary shelf)."""
    if part.id.startswith(BLACK_PREFIXES) or part.group in BLACK_GROUPS:
        return BLACK
    return RED


def paint(part):
    mat = (part.material or '').lower()
    if 'ALLOCATION' in part.id or (getattr(part, 'release', None) and 'ALLOCATION' in str(part.release)) or 'allocation' in mat:
        return ALLOC
    if part.group in BARE_GROUPS:
        return BARE
    if 'hdpe' in mat:
        return HDPE
    if 'mdf' in mat:
        return MDF
    if any(k in mat for k in RUBBER_KEYS):
        return RUBBER
    if 'stainless' in mat or 'galvan' in mat:
        return STAINLESS                # bare: the pan, drain, float, zinc-coated sheet
    if any(k in mat for k in ALU_KEYS):
        return ALU                      # natural finish, bought or made
    if getattr(part, 'purchased', False):
        return GRAPHITE
    if any(k in mat for k in POLYMER_KEYS):
        return POLYMER
    if 'weld' in mat:
        return painted(part)            # weld deposits and weld nuts are on the part before it is coated
    if any(k in mat for k in HARDWARE_KEYS):
        return GRAPHITE                 # bare fasteners, pins, spacers and contacts
    if any(k in mat for k in STEEL_KEYS):
        return painted(part)
    if part.group in RED_GROUPS or part.group in BLACK_GROUPS or part.id.startswith(BLACK_PREFIXES):
        return painted(part)
    FALLTHROUGH.append((part.id, part.group, part.material))
    return tuple(int(round(c * 255)) for c in part.color)


def repaint(model):
    for part in model.parts:
        part.color = tuple(c / 255 for c in paint(part))
    return model


def write_mesh(model, name):
    """Tessellate the painted model. The package builds' own writer forces a fixed grey on the frame groups, so the
    painted renders use this one, which keeps every part's colour."""
    dest = MESH / 'previews'
    dest.mkdir(parents=True, exist_ok=True)
    vertices, triangles, colors = [], [], []
    offset = 0
    for part in model.parts:
        points, faces = part.shape.tessellate(.7, .25)
        v = np.array([q.toTuple() for q in points], dtype=np.float32)
        f = np.asarray(faces, dtype=np.int32)
        if not len(f):
            continue
        vertices.append(v)
        triangles.append(f + offset)
        offset += len(v)
        rgb = np.asarray(part.color) * 255
        colors.append(np.tile(rgb.astype(np.uint8), (len(f), 1)))
    np.savez_compressed(dest / (name + '.npz'), vertices=np.concatenate(vertices),
                        triangles=np.concatenate(triangles), colors=np.concatenate(colors))


def font(bold, size):
    for path in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render(name, title, note, view=(-1.25, -1.8, 1.25), size=(1600, 1400), out=None):
    data = np.load(MESH / 'previews' / (name + '.npz'))
    vertices = data['vertices']; faces = data['triangles']; colors = data['colors']
    camera = _unit(view); right = _unit(np.cross(np.array([0., 0., 1.]), camera))
    basis = np.array((right, -np.cross(camera, right), camera))
    projected = vertices @ basis.T
    w, h = size; lo = projected[:, :2].min(0); hi = projected[:, :2].max(0)
    scale = min((w - 110) / (hi[0] - lo[0]), (h - 220) / (hi[1] - lo[1]))
    projected[:, :2] = projected[:, :2] * scale + np.array([w / 2, (h + 10) / 2]) - (lo + hi) / 2 * scale
    pixels = np.empty((h, w, 3), np.uint8); pixels[:] = (240, 241, 238)
    depth = np.full((h, w), -np.inf, np.float32)
    pts = vertices[faces]; normal = np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
    lengths = np.linalg.norm(normal, axis=1); valid = lengths > 1e-8
    normal[valid] /= lengths[valid, None]
    visible = valid & (normal @ camera > 1e-8)
    shade = .55 + .45 * np.maximum(0, normal @ _unit((-1.5, -2, 3)))
    rgb = np.clip(colors * shade[:, None], 0, 255).astype(np.uint8)
    for i in np.flatnonzero(visible):
        _triangle(projected[faces[i]], rgb[i], pixels, depth)
    finite = np.isfinite(depth); edge = np.zeros((h, w), bool)
    for axis in (0, 1):
        delta = np.diff(np.where(finite, depth, -1e9), axis=axis)
        selected = (np.abs(delta) > 10) & (np.abs(delta) < 1e8)
        if axis == 0: edge[:-1] |= selected
        else: edge[:, :-1] |= selected
    pixels[edge] = (pixels[edge].astype(float) * .7).astype(np.uint8)
    picture = Image.fromarray(pixels); draw = ImageDraw.Draw(picture)

    def fitted(text, bold, size, floor):
        f = font(bold, size)
        while draw.textlength(text, font=f) > w - 84 and size > floor:
            size -= 1; f = font(bold, size)
        return f

    draw.text((42, 25), title, font=fitted(title, True, 30, 20), fill=(28, 30, 34))
    draw.text((42, 69), 'Actual CAD geometry in the paint scheme: stand red, module and changer black, aluminium natural, slats and stainless bare, bought parts graphite.',
              font=font(False, 19), fill=(85, 90, 96))
    draw.text((42, h - 77), 'WORKING DESIGN: not a fabrication release. Bought parts are drawn as their envelopes.', font=font(False, 19), fill=(112, 66, 18))
    draw.text((42, h - 46), note, font=fitted(note, False, 19, 14), fill=(85, 90, 96))
    dest = HERE / ((out or name) + '.png'); picture.save(dest)
    return {'file': dest.name, 'title': title, 'triangles': int(len(faces))}


def main():
    start = time.monotonic()
    MESH.mkdir(exist_ok=True)
    results = []

    def state(model, name, title, note, views):
        repaint(model)
        write_mesh(model, name)
        for suffix, view, size in views:
            results.append(render(name, title, note, view, size, out=name + suffix) | {'view': suffix})
        for item in FALLTHROUGH:
            print('  engineering colour kept:', *item, flush=True)
        FALLTHROUGH.clear()
        print('rendered', name, round(time.monotonic() - start), 's', flush=True)

    ISO = [('', (-1.25, -1.8, 1.25), (1600, 1400))]
    ISO_REAR = ISO + [('_rear', (1.0, 1.6, 0.95), (1600, 1300))]
    # Rev L (the ER11 machine)
    router, _ = build_revl.build_model()
    state(router, 'GM1_RevL_router', 'GM1 Rev L | Router: tool changer parked behind the Z, gantry at the rear stop, Z up',
          'Red stand, black bed module and tool changer, natural aluminium gantry and bed strips. Tool setter on the changer\'s wing; work light under the beam.', ISO)
    plasma, _ = build_revl.plasma_model(router)
    state(plasma, 'GM1_RevL_plasma', 'GM1 Rev L | Plasma: bed module lifted out, torch on the Z over the water pan',
          'The welded steel pan is painted with the stand; its slats are bare, consumable steel. The spindle and the module are out of the machine.', ISO)
    change, _ = build_revl.build_model(gantry_y=build_revl.POCKET_GANTRY_Y, head_x=575.0, atc_travel=0.0)
    state(change, 'GM1_RevL_toolchange', 'GM1 Rev L | Tool change: magazine deployed over the back of the bed, spindle on the pocket line',
          'The RapidChange magazine and its lid are allocations (light grey).', ISO)
    # BT30 variant
    b_router, _ = bb.build_model()
    state(b_router, 'GM1_RevL_BT30_router', 'GM1 Rev L BT30 | Router: BT30 spindle in its one-piece clamp, fork rack parked behind the Z',
          'The 3.2 kW BT30 spindle is a bought envelope (graphite); holders and forks are allocations.', ISO)
    b_plasma, _ = bb.plasma_model(b_router)
    state(b_plasma, 'GM1_RevL_BT30_plasma', 'GM1 Rev L BT30 | Plasma: module and rack out, spindle parked on the reservoir lid',
          'Same stand, pan and gantry as Rev L.', ISO)
    b_change, _ = bb.build_model(gantry_y=bb.POCKET_GANTRY_Y, head_x=bt30.POCKET_X[2], z_lift=bt30.Z_ENGAGE, atc_travel=0.0, held_tool=False)
    state(b_change, 'GM1_RevL_BT30_toolchange', 'GM1 Rev L BT30 | Tool change: rack deployed, spindle nose down on the holder in pocket 3',
          'Six BT30 holders at 90 mm on the black carrier tray; the aluminium rack bar stays natural.', ISO)
    # Rotary variant
    r_router, _ = br.build_model()
    state(r_router, 'GM1_RevL_rotary_router', 'GM1 Rev L rotary | Router mode with the rotary fitted at the back of the frame',
          'The black shelf on the red rear cross tube carries the rotary (allocation); the bed module and its exit path are untouched.', ISO_REAR)
    probe, pd = br.build_model(gantry_y=br.TUBE_GANTRY_Y, head_x=rotary.AXIS_X, z_lift=0.0, tube_length=rotary.TUBE_L)
    _, head0 = br.plasma_model(probe)
    z_cut = round(pd['rotary']['tube']['top_z_mm'] + br.CUT_STANDOFF - head0['tip_z_mm'], 3)
    with_tube, _ = br.build_model(gantry_y=br.TUBE_GANTRY_Y, head_x=rotary.AXIS_X, z_lift=z_cut, tube_length=rotary.TUBE_L)
    r_plasma, _ = br.plasma_model(with_tube)
    state(r_plasma, 'GM1_RevL_rotary_tube', 'GM1 Rev L rotary | Tube notching: a 60 mm tube in the chuck along the table, torch over it',
          'The tube turns on the X driver (plug swap) while the torch runs along it on the Y motors. Long tubes go out of the front.', ISO_REAR)
    (HERE / 'renders.json').write_text(json.dumps({'scheme': __doc__.strip(), 'renders': results, 'elapsed_seconds': round(time.monotonic() - start, 1)}, indent=2) + '\n')
    print('done', len(results), 'renders', round(time.monotonic() - start), 's', flush=True)


if __name__ == '__main__':
    main()
