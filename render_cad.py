"""Small orthographic CAD renderer with a real, per-pixel depth buffer.

Only NumPy and Pillow are required. Coordinates are in any consistent units;
X and Y are horizontal and Z is up. ``view`` is the vector from the model
toward the camera. Boxes are (x, y, z, dx, dy, dz, '#rrggbb'). Rods are
((ax, ay, az), (bx, by, bz), width, '#rrggbb'); width is the actual side of
a square-section prism, not a screen-space line width.

Example::

    from render_cad import render_scene
    result = render_scene(boxes=[(0,0,0,100,200,20,'#376070')],
                          rods=[], output_path='part.png')
    screen_xy = result.project((50,100,20))

No painter sorting is used: intersecting and overlapping faces are correctly
resolved at each pixel. Edges are also tested against the completed depth
buffer, so hidden edges do not bleed through foreground members. Coplanar
overlapping faces are inherently ambiguous and should be avoided in a model.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


@dataclass
class RenderResult:
    """Projection metadata, useful for accurately anchored external labels."""

    output_path: str
    width: int
    height: int
    basis: np.ndarray
    scale: float
    offset: np.ndarray
    bounds: np.ndarray

    def project(self, points):
        """World XYZ point(s) to final image XY pixel coordinates."""
        p = np.asarray(points, dtype=float)
        return (p @ self.basis[:2].T) * self.scale + self.offset


def _rgb(value):
    if isinstance(value, str):
        value = value.lstrip('#')
        if len(value) == 3:
            value = ''.join(c * 2 for c in value)
        return np.array([int(value[i:i+2], 16) for i in (0, 2, 4)], float)
    result = np.asarray(value, dtype=float)
    if result.shape != (3,):
        raise ValueError('Color must be a hex string or RGB triple.')
    return result


def _unit(v):
    v = np.asarray(v, float)
    length = np.linalg.norm(v)
    if length < 1e-12:
        raise ValueError('A direction vector must have nonzero length.')
    return v / length


_FACES = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
          (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
_EDGES = ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6),
          (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7))


def _box_mesh(box):
    if len(box) != 7:
        raise ValueError('Each box must contain x,y,z,dx,dy,dz,color.')
    x, y, z, dx, dy, dz, color = box
    if min(dx, dy, dz) <= 0:
        raise ValueError('Box dimensions must be positive.')
    vertices = np.array([(x, y, z), (x+dx, y, z),
                         (x+dx, y+dy, z), (x, y+dy, z),
                         (x, y, z+dz), (x+dx, y, z+dz),
                         (x+dx, y+dy, z+dz), (x, y+dy, z+dz)], float)
    return vertices, _rgb(color)


def _rod_mesh(rod):
    a, b, width, color = rod
    a, b = np.asarray(a, float), np.asarray(b, float)
    if width <= 0:
        raise ValueError('Rod width must be positive.')
    axis = _unit(b-a)
    # For ordinary diagonal braces this makes one section direction horizontal.
    helper = np.array((0, 0, 1.)) if abs(axis[2]) < .95 else np.array((0, 1., 0))
    u = _unit(np.cross(helper, axis)) * width / 2
    v = np.cross(axis, u)
    # Same local winding as the axis-aligned box mesh.
    vertices = np.array((a-u-v, a+u-v, a+u+v, a-u+v,
                         b-u-v, b+u-v, b+u+v, b-u+v))
    return vertices, _rgb(color)


def _triangle(screen, rgb, pixels, depths):
    """Rasterize an orthographic triangle with barycentric depth interpolation."""
    h, w = depths.shape
    x0 = max(0, int(np.floor(screen[:, 0].min())))
    x1 = min(w-1, int(np.ceil(screen[:, 0].max())))
    y0 = max(0, int(np.floor(screen[:, 1].min())))
    y1 = min(h-1, int(np.ceil(screen[:, 1].max())))
    if x0 > x1 or y0 > y1:
        return
    a, b, c = screen
    denominator = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
    if abs(denominator) < 1e-9:
        return
    # Evaluate at pixel centers. Broadcasting avoids full meshgrid allocation.
    xs = np.arange(x0, x1+1, dtype=np.float32)[None, :] + .5
    ys = np.arange(y0, y1+1, dtype=np.float32)[:, None] + .5
    w0 = ((b[1]-c[1])*(xs-c[0]) + (c[0]-b[0])*(ys-c[1])) / denominator
    w1 = ((c[1]-a[1])*(xs-c[0]) + (a[0]-c[0])*(ys-c[1])) / denominator
    w2 = 1-w0-w1
    z = w0*a[2] + w1*b[2] + w2*c[2]
    region = depths[y0:y1+1, x0:x1+1]
    take = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6) & (z > region)
    region[take] = z[take]
    pixels[y0:y1+1, x0:x1+1][take] = rgb


def _edge(a, b, rgb, pixels, depths, edge_depths, thickness, depth_tolerance):
    """Round-capped line with interpolated depth and proper surface occlusion."""
    h, w = depths.shape
    radius = max(.5, thickness / 2)
    x0 = max(0, int(np.floor(min(a[0], b[0])-radius)))
    x1 = min(w-1, int(np.ceil(max(a[0], b[0])+radius)))
    y0 = max(0, int(np.floor(min(a[1], b[1])-radius)))
    y1 = min(h-1, int(np.ceil(max(a[1], b[1])+radius)))
    if x0 > x1 or y0 > y1:
        return
    d = b[:2]-a[:2]
    d2 = np.dot(d, d)
    if d2 < 1e-8:
        return
    xs = np.arange(x0, x1+1, dtype=np.float32)[None, :] + .5
    ys = np.arange(y0, y1+1, dtype=np.float32)[:, None] + .5
    t = np.clip(((xs-a[0])*d[0] + (ys-a[1])*d[1]) / d2, 0, 1)
    distance2 = (xs-a[0]-t*d[0])**2 + (ys-a[1]-t*d[1])**2
    z = a[2] + t*(b[2]-a[2])
    region = depths[y0:y1+1, x0:x1+1]
    prior_edges = edge_depths[y0:y1+1, x0:x1+1]
    visible = ((distance2 <= radius**2) & (z >= region-depth_tolerance)
               & (z > prior_edges))
    pixels[y0:y1+1, x0:x1+1][visible] = rgb
    prior_edges[visible] = z[visible]


def render_scene(boxes=(), rods=(), output_path='render.png', width=1800,
                 height=1400, background='#F7F9FA', view=(1.5, -2, 1.4),
                 supersample=2, margin=.065, edges=True, edge_width=.7,
                 shadow=False, light=(-1.1, -1.7, 3.4)):
    """Render axis-aligned boxes and arbitrary square rods to a PNG.

    ``view`` is a three-vector pointing *towards the camera*. Useful views:
    front-right (1.5,-2,1.4), front-left (-1.5,-2,1.4), top (0,0,1),
    front (0,-1,0). ``margin`` is a fraction of the image's shorter side.
    The scene is automatically fitted without perspective distortion.

    Return a RenderResult whose ``project(world_xyz)`` gives image coordinates.
    Inputs are not changed. Output directories are created automatically.
    """
    width, height = int(width), int(height)
    ss = max(1, int(supersample))
    if min(width, height) <= 0 or not 0 <= margin < .45:
        raise ValueError('Invalid image dimensions or margin.')
    meshes = [_box_mesh(b) for b in boxes] + [_rod_mesh(r) for r in rods]
    if not meshes:
        raise ValueError('At least one box or rod is required.')
    camera = _unit(view)
    up = np.array((0., 0., 1.))
    if abs(np.dot(up, camera)) > .999:
        up = np.array((0., 1., 0.))
    right = _unit(np.cross(up, camera))
    image_up = np.cross(camera, right)
    basis = np.array((right, -image_up, camera))
    vertices = np.concatenate([m[0] for m in meshes])
    projected = vertices @ basis.T
    lo, hi = projected[:, :2].min(0), projected[:, :2].max(0)
    padding = margin * min(width, height)
    scale = min((width-2*padding)/max(hi[0]-lo[0], 1e-6),
                (height-2*padding)/max(hi[1]-lo[1], 1e-6))
    offset = np.array((width, height)) / 2 - (lo+hi)/2 * scale
    target = Path(output_path).resolve()
    result = RenderResult(str(target), width, height, basis, scale,
                          offset, np.array((vertices.min(0), vertices.max(0))))
    pixels = np.empty((height*ss, width*ss, 3), dtype=np.uint8)
    pixels[:] = np.clip(_rgb(background), 0, 255).astype(np.uint8)

    if shadow:
        # Soft contact shadow of the genuine model's vertical ground projection.
        mask = Image.new('L', (width*ss, height*ss), 0)
        draw = ImageDraw.Draw(mask)
        z_floor = vertices[:, 2].min()
        for points, _ in meshes:
            ground = points.copy()
            ground[:, 2] = z_floor
            xy = result.project(ground) * ss
            # Ground XY shadows of all convex prism faces; union, not overprint.
            for face in _FACES:
                draw.polygon([tuple(p) for p in xy[list(face)]], fill=22)
        alpha = np.asarray(mask.filter(ImageFilter.GaussianBlur(8*ss)), float)/255
        pixels[:] = np.clip(pixels.astype(float)*(1-alpha[:, :, None]), 0, 255)

    depths = np.full((height*ss, width*ss), -np.inf, dtype=np.float32)
    light = _unit(light)
    projected_meshes = []
    for points, base_color in meshes:
        screen = points @ basis.T
        screen[:, :2] = (screen[:, :2]*scale+offset)*ss
        visible_faces = []
        for face in _FACES:
            p = points[list(face)]
            normal = _unit(np.cross(p[1]-p[0], p[2]-p[0]))
            if np.dot(normal, camera) <= 1e-9:
                continue
            visible_faces.append(face)
            shade = .75 + .25*max(0, np.dot(normal, light))
            rgb = np.clip(base_color*shade, 0, 255).astype(np.uint8)
            f = screen[list(face)]
            _triangle(f[[0, 1, 2]], rgb, pixels, depths)
            _triangle(f[[0, 2, 3]], rgb, pixels, depths)
        projected_meshes.append((screen, base_color, visible_faces))

    if edges:
        # A fractional pixel's world depth tolerance prevents tiny edge cracks.
        tolerance = 1.3 / (scale*ss)
        edge_depths = np.full_like(depths, -np.inf)
        for screen, base_color, faces in projected_meshes:
            edge_set = set()
            for face in faces:
                for i in range(4):
                    edge_set.add(tuple(sorted((face[i], face[(i+1) % 4]))))
            color = np.clip(base_color*.46 + np.array((20, 28, 32))*.20,
                            0, 255).astype(np.uint8)
            for a, b in sorted(edge_set):
                _edge(screen[a], screen[b], color, pixels, depths, edge_depths,
                      edge_width*ss, tolerance)

    image = Image.fromarray(pixels)
    if ss != 1:
        image = image.resize((width, height), Image.Resampling.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    return result


def _self_test():
    """Check depth visibility, draw-order independence, and arbitrary braces."""
    root = Path(__file__).resolve().parent / 'output' / 'renderer-test'
    # Two crossing prisms: the left member is nearest at their intersection.
    boxes = [(0, 0, 0, 25, 180, 25, '#338894'),
             (-60, 70, 0, 150, 25, 22, '#DA983E'),
             (70, 125, 0, 40, 40, 100, '#526C7B'),
             (-65, -5, -8, 180, 180, 6, '#D8DFE3')]
    rods = [((-45, 5, 5), (75, 145, 85), 10, '#B05C40')]
    a = render_scene(boxes, rods, root / 'overlap.png', width=1000, height=800,
                     shadow=True)
    b = render_scene(list(reversed(boxes)), rods, root / 'overlap-reversed.png',
                     width=1000, height=800, shadow=True)
    first = np.array(Image.open(a.output_path))
    second = np.array(Image.open(b.output_path))
    assert np.array_equal(first, second), 'Depth result depends on input order.'
    # Straight-on verification: a foreground small orange box must occlude the
    # large blue rear face, independent of their order in the input list.
    front = render_scene([(0, 20, 0, 100, 10, 100, '#2244DD'),
                          (30, 0, 30, 40, 10, 40, '#DD6622')], [],
                         root / 'occlusion.png', 400, 400, view=(0, -1, 0),
                         edges=False, supersample=1)
    im = np.array(Image.open(front.output_path))
    center = front.project((50, 0, 50)).astype(int)
    sample = im[center[1], center[0]]
    assert sample[0] > sample[2]*3, 'Foreground failed depth test.'
    print('PASS: draw order invariant; foreground visibility; arbitrary rods.')
    print(a.output_path)


if __name__ == '__main__':
    _self_test()
