"""Render the GM1 Rev L BT30 variant CAD tessellations (actual model geometry, no illustration parts)."""
from pathlib import Path
import sys
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE.parents[2]))
from render_cad import _triangle, _unit
ROOT = SOURCE.parent / 'RevL-BT30-CAD'


def font(bold, size):
    for path in (('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf'),
                 ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render(name, view=(-1.25, -1.8, 1.25), size=(1600, 1400), suffix=''):
    data = np.load(ROOT / 'previews' / (name + '.npz'))
    vertices = data['vertices']; faces = data['triangles']; colors = data['colors']
    camera = _unit(view); right = _unit(np.cross(np.array([0., 0., 1.]), camera))
    basis = np.array((right, -np.cross(camera, right), camera))
    projected = vertices @ basis.T
    w, h = size; lo = projected[:, :2].min(0); hi = projected[:, :2].max(0)
    scale = min((w - 110) / (hi[0] - lo[0]), (h - 220) / (hi[1] - lo[1]))
    projected[:, :2] = projected[:, :2] * scale + np.array([w / 2, (h + 10) / 2]) - (lo + hi) / 2 * scale
    pixels = np.empty((h, w, 3), np.uint8); pixels[:] = (246, 249, 251)
    depth = np.full((h, w), -np.inf, np.float32)
    pts = vertices[faces]; normal = np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
    lengths = np.linalg.norm(normal, axis=1); valid = lengths > 1e-8
    normal[valid] /= lengths[valid, None]
    visible = valid & (normal @ camera > 1e-8)
    shade = .60 + .40 * np.maximum(0, normal @ _unit((-1.5, -2, 3)))
    rgb = np.clip(colors * shade[:, None], 0, 255).astype(np.uint8)
    for i in np.flatnonzero(visible):
        _triangle(projected[faces[i]], rgb[i], pixels, depth)
    finite = np.isfinite(depth); edge = np.zeros((h, w), bool)
    for axis in (0, 1):
        delta = np.diff(np.where(finite, depth, -1e9), axis=axis)
        selected = (np.abs(delta) > 10) & (np.abs(delta) < 1e8)
        if axis == 0: edge[:-1] |= selected
        else: edge[:, :-1] |= selected
    pixels[edge] = (pixels[edge].astype(float) * .72).astype(np.uint8)
    picture = Image.fromarray(pixels); draw = ImageDraw.Draw(picture)
    titles = {'RevLBT30_ROUTER': 'GM1 Rev L BT30 | Router: BT30 spindle, fork rack parked behind the Z body, Z fully up',
              'RevLBT30_TOOL_CHANGE': 'GM1 Rev L BT30 | Tool change: rack deployed, spindle nose down on pocket 3',
              'RevLBT30_PLASMA': 'GM1 Rev L BT30 | Plasma: module and rack out, spindle parked on the reservoir lid',
              'RevLBT30_BED_MODULE': 'GM1 Rev L BT30 | Bed module with the fork rack, as lifted for a bed change',
              'RevLBT30_DOCK_DETAIL': 'GM1 Rev L BT30 | Fork rack on the bed module, deployed'}
    draw.text((42, 25), titles.get(name, name), font=font(True, 30), fill=(28, 43, 50))
    draw.text((42, 69), 'Actual CAD geometry. Amber parts are purchased envelopes.', font=font(False, 19), fill=(85, 101, 112))
    draw.text((42, h - 77), 'WORKING DESIGN: owner hoist, torch measurement and supplier interfaces still open. Not a fabrication release.',
              font=font(False, 19), fill=(112, 66, 18))
    notes = {'RevLBT30_ROUTER': 'BT30 spindle envelope 105 x 450 on a 3/4 in adapter; tool axis 26 mm forward of Rev L. Magenta: holder, fork and stored-tool allocations.',
             'RevLBT30_TOOL_CHANGE': 'Spindle nose at the gauge line (Z 37.7); the neighbours\' pull studs clear the clamp by 6 mm.',
             'RevLBT30_PLASMA': 'Spindle with its clamp on it, on two cradles over the clarified-tank cover, nose to the right; its screws in the hardware bin.',
             'RevLBT30_BED_MODULE': 'About 78 kg with the rack and six holders (allocations). Hook over the new centre of mass.',
             'RevLBT30_DOCK_DETAIL': 'Six pockets at 90 mm on a 5/8 in bar; stored holders hang through the tray. Rev L beams, rails and drive.'}
    draw.text((42, h - 46), notes.get(name, ''), font=font(False, 19), fill=(85, 101, 112))
    dest = ROOT / 'previews' / (name + suffix + '.png'); picture.save(dest)
    return {'file': dest.name, 'bounds_min': vertices.min(0).tolist(), 'bounds_max': vertices.max(0).tolist()}


def main():
    results = []
    for name in ('RevLBT30_ROUTER', 'RevLBT30_TOOL_CHANGE', 'RevLBT30_PLASMA', 'RevLBT30_BED_MODULE'):
        print('Render', name, flush=True); results.append(render(name))
    results.append(render('RevLBT30_DOCK_DETAIL', view=(-1.1, -1.5, 1.35), size=(1600, 1200)))
    results.append(render('RevLBT30_ROUTER', view=(1, 0, .12), size=(1400, 1400), suffix='_side'))
    results.append(render('RevLBT30_TOOL_CHANGE', view=(-.4, -1.0, .35), size=(1600, 1200), suffix='_front'))
    (ROOT / 'previews' / 'preview-metadata.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Rendered', len(results), 'CAD views', flush=True)


if __name__ == '__main__':
    main()
