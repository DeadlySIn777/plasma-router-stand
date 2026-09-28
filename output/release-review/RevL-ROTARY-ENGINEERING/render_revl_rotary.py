"""Render the GM1 Rev L rotary variant CAD tessellations (actual model geometry, no illustration parts)."""
from pathlib import Path
import sys
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE.parents[2]))
from render_cad import _triangle, _unit
ROOT = SOURCE.parent / 'RevL-ROTARY-CAD'


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
    titles = {'RevLROT_ROUTER': 'GM1 Rev L rotary | Router mode, rotary fitted at the back, dock parked, Z up',
              'RevLROT_PLASMA': 'GM1 Rev L rotary | Tube notching: a 60 mm tube in the chuck, torch over it at Y575',
              'RevLROT_SHELF_DETAIL': 'GM1 Rev L rotary | The shelf on the rear cross tube: rails, tie, plate, rotary, chuck'}
    draw.text((42, 25), titles.get(name, name), font=font(True, 30), fill=(28, 43, 50))
    draw.text((42, 69), 'Actual CAD geometry. Amber parts are purchased envelopes; magenta parts are allocations.', font=font(False, 19), fill=(85, 101, 112))
    draw.text((42, h - 77), 'WORKING DESIGN: owner hoist, torch measurement and supplier interfaces still open. Not a fabrication release.',
              font=font(False, 19), fill=(112, 66, 18))
    notes = {'RevLROT_ROUTER': 'The chuck face stops 15 mm behind the bed module, so the rotary stays on for router work and the module still slides out of the front.',
             'RevLROT_PLASMA': 'The tube turns on the X driver (plug swap); the torch runs along Y. Long tubes go out of the front over the low cross tubes.',
             'RevLROT_SHELF_DETAIL': 'A U of 2 x 4 in tube on the rear cross tube, two M10 bolts in welded sleeves; the rotary and its K72-125 chuck are allocations.'}
    draw.text((42, h - 46), notes.get(name, ''), font=font(False, 19), fill=(85, 101, 112))
    dest = ROOT / 'previews' / (name + suffix + '.png'); picture.save(dest)
    return {'file': dest.name, 'bounds_min': vertices.min(0).tolist(), 'bounds_max': vertices.max(0).tolist()}


def main():
    results = []
    for name in ('RevLROT_ROUTER', 'RevLROT_PLASMA'):
        print('Render', name, flush=True); results.append(render(name))
    results.append(render('RevLROT_PLASMA', view=(.9, 1.6, .9), size=(1600, 1200), suffix='_rear'))
    results.append(render('RevLROT_SHELF_DETAIL', view=(1.1, 1.5, 1.0), size=(1600, 1200)))
    (ROOT / 'previews' / 'preview-metadata.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Rendered', len(results), 'CAD views', flush=True)


if __name__ == '__main__':
    main()
