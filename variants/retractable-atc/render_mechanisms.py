"""Render exported STEP bodies, never substitute illustrative mechanism geometry.

Run with CAD Python and a JSON manifest at previews/render-inputs.json. Each
machine supplies deployed_step and parked_step (repo-relative). Context is
either one separate context_step, or deployed_context_step/parked_context_step
with context_contains_mechanism=true for complete named machine assemblies.
Optional camera vectors point from the model toward the viewer. STEP assembly
names are retained so explicit UNVERIFIED/ALLOCATION bodies remain distinguishable.
The shared root renderer provides the per-pixel triangle depth test.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time

import cadquery as cq
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.TopLoc import TopLoc_Location
from OCP.Quantity import Quantity_Color
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from render_cad import _triangle, _unit

OUT = HERE / 'previews'
COLORS = {'context': (164, 173, 178), 'mechanism': (35, 139, 181),
          'allocation': (171, 95, 158)}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


@dataclass
class Body:
    name: str
    shape: cq.Shape
    role: str
    vertices: np.ndarray | None = None
    triangles: np.ndarray | None = None

    def mesh(self):
        if self.vertices is None:
            vertices, triangles = self.shape.tessellate(.35, .14)
            self.vertices = np.array([v.toTuple() for v in vertices], dtype=float)
            self.triangles = np.array(triangles, dtype=np.int32)
            if not len(self.vertices) or not len(self.triangles):
                raise ValueError('Empty tessellation: ' + self.name)
        return self.vertices, self.triangles


def step_bodies(path, role):
    """Read XCAF occurrence transforms and names from the actual exported STEP."""
    doc = TDocStd_Document(TCollection_ExtendedString('CAD preview'))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    reader.SetColorMode(True)
    if reader.ReadFile(str(path)) != IFSelect_RetDone or not reader.Transfer(doc):
        raise ValueError('STEP import failed: ' + str(path))
    tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    free = TDF_LabelSequence()
    tool.GetFreeShapes(free)
    result = []

    def name(label):
        attribute = TDataStd_Name()
        return attribute.Get().ToExtString() if label.FindAttribute(TDataStd_Name.GetID_s(), attribute) else ''

    def source_is_magenta(label):
        color = Quantity_Color()
        for kind in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen):
            if XCAFDoc_ColorTool.GetColor_s(label, kind, color):
                # XCAF returns linear RGB here. The source builders explicitly
                # use magenta for unverified replacement/acceptance allocations.
                return color.Red() > .35 and color.Blue() > .25 and color.Green() < .15
        return False

    def walk(label, parent_location, occurrence_name='', occurrence_magenta=False):
        actual = TDF_Label()
        if tool.IsReference_s(label):
            assert tool.GetReferredShape_s(label, actual)
            location = parent_location.Multiplied(tool.GetLocation_s(label))
            walk(actual, location, occurrence_name or name(label),
                 occurrence_magenta or source_is_magenta(label))
        elif tool.IsAssembly_s(label):
            children = TDF_LabelSequence()
            tool.GetComponents_s(label, children)
            for i in range(1, children.Length() + 1):
                walk(children.Value(i), parent_location)
        else:
            title = occurrence_name or name(label) or 'unnamed_body'
            shape = cq.Shape.cast(tool.GetShape_s(label)).moved(cq.Location(parent_location))
            selected_role = 'allocation' if occurrence_magenta or source_is_magenta(label) or any(s in title.upper() for s in
                ('UNVERIFIED', 'ALLOCATION', 'ACCEPTANCE', 'ATC_MAGAZINE')) else role
            for n, solid in enumerate(shape.Solids()):
                assert solid.isValid() and solid.Volume() > 0, title
                result.append(Body(title if len(shape.Solids()) == 1 else f'{title}/{n}', solid, selected_role))

    for i in range(1, free.Length() + 1):
        walk(free.Value(i), TopLoc_Location())
    # Independent flat importer cross-checks occurrence transforms and inventory.
    flat = cq.importers.importStep(str(path)).val()
    total = sum(b.shape.Volume() for b in result)
    assert len(result) == len(flat.Solids()), (path, len(result), len(flat.Solids()))
    assert abs(total - flat.Volume()) < max(.2, total * 1e-7)
    union_bounds = np.array([bounds(b.shape) for b in result])
    actual_bounds = np.r_[union_bounds[:, :3].min(axis=0), union_bounds[:, 3:].max(axis=0)]
    assert np.max(np.abs(actual_bounds - np.array(bounds(flat)))) < .01
    return result, {'solid_count': len(result), 'all_solids_valid': True,
                    'volume_mm3': total, 'bounds_mm': actual_bounds.tolist(),
                    'flat_import_crosscheck': True,
                    'allocation_names': [b.name for b in result if b.role == 'allocation']}


def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf', size)


def render(bodies, output, title, subtitle, view, full_context, width=1800, height=1320):
    camera = _unit(view)
    up = np.array([0., 0., 1.]) if abs(camera[2]) < .98 else np.array([0., 1., 0.])
    right = _unit(np.cross(up, camera))
    image_up = np.cross(camera, right)
    basis = np.array((right, -image_up, camera))
    projected = [b.mesh()[0] @ basis.T for b in bodies]
    lo = np.vstack([p.min(axis=0) for p in projected]).min(axis=0)
    hi = np.vstack([p.max(axis=0) for p in projected]).max(axis=0)
    canvas_height = height - 230
    scale = min((width - 160) / (hi[0] - lo[0]), (canvas_height - 60) / (hi[1] - lo[1]))
    center = (lo[:2] + hi[:2]) / 2
    offset = np.array((width / 2, canvas_height / 2)) - center * scale
    pixels = np.full((canvas_height, width, 3), [242, 246, 248], np.uint8)
    depths = np.full((canvas_height, width), -np.inf, np.float32)
    light = _unit((-1.1, -1.8, 3.2))
    triangle_count = 0
    for body, p in zip(bodies, projected):
        v, indices = body.mesh()
        screen = p.copy()
        screen[:, :2] = screen[:, :2] * scale + offset
        for index in indices:
            actual = v[index]
            normal = np.cross(actual[1] - actual[0], actual[2] - actual[0])
            length = np.linalg.norm(normal)
            if length < 1e-12:
                continue
            normal /= length
            if normal @ camera < 0:
                normal = -normal
            shade = .64 + .36 * max(0., normal @ light)
            color = np.clip(np.array(COLORS[body.role]) * shade, 0, 255).astype(np.uint8)
            _triangle(screen[index], color, pixels, depths)
            triangle_count += 1
    occupied = np.isfinite(depths)
    edges = np.zeros_like(occupied)
    for axis in (0, 1):
        previous = np.roll(depths, 1, axis=axis)
        valid = occupied & np.isfinite(previous)
        difference = np.zeros_like(depths)
        np.subtract(depths, previous, out=difference, where=valid)
        edges |= occupied & ((~np.isfinite(previous)) | (np.abs(difference) > (12 if full_context else 4)))
    pixels[edges] = (pixels[edges].astype(float) * .68).astype(np.uint8)
    occupied_count = int(occupied.sum())
    mechanism_pixels = int((occupied & (pixels[:, :, 2].astype(int) > pixels[:, :, 0].astype(int) + 35)
                            & (pixels[:, :, 1].astype(int) > pixels[:, :, 0].astype(int) + 25)).sum())
    assert occupied_count > 10000 and mechanism_pixels > 100, 'Blank or fully hidden mechanism view'
    image = Image.new('RGB', (width, height), '#f2f6f8')
    image.paste(Image.fromarray(pixels), (0, 128))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 10), fill='#268bb5')
    draw.text((48, 30), title, fill='#173e50', font=font(36, True))
    draw.text((48, 83), subtitle, fill='#3f5662', font=font(22))
    draw.line((48, height - 96, width - 48, height - 96), fill='#bdcbd2', width=2)
    draw.text((48, height - 82), 'DEVELOPMENT — NOT FABRICATION RELEASE', fill='#a5422c', font=font(25, True))
    legend = 'Gray: machine context   •   Blue: mechanism   •   Purple: unverified allocation'
    if not full_context:
        legend = 'Mechanism isolated for inspection; machine context hidden. Purple bodies, if present, are unverified allocations.'
    draw.text((48, height - 43), legend, fill='#3f5662', font=font(19))
    # Axis key follows the same projection as the actual geometry.
    origin = np.array([90., height - 165.])
    for axis, color, label in [(np.array([1., 0, 0]), '#b24739', 'X'),
                               (np.array([0, 1., 0]), '#42845c', 'Y'),
                               (np.array([0, 0, 1.]), '#3979b0', 'Z')]:
        end = origin + (basis @ axis)[:2] * 43
        draw.line((tuple(origin), tuple(end)), fill=color, width=3)
        draw.text(tuple(end + 2), label, fill=color, font=font(17, True))
    image.save(output)
    return {'image': rel(output), 'width': width, 'height': height, 'body_count': len(bodies),
            'triangles': triangle_count, 'occupied_pixels': occupied_count,
            'visible_mechanism_pixels': mechanism_pixels, 'camera_toward_viewer': list(view),
            'full_machine_context': full_context, 'orthographic_scale_pixels_per_mm': scale,
            'allocation_names': [b.name for b in bodies if b.role == 'allocation'],
            'sha256': sha(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=OUT / 'render-inputs.json')
    parser.add_argument('--allow-partial', action='store_true', help='Render one frozen machine while the other is still being checked')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    if manifest.get('geometry_frozen') is not True:
        raise ValueError('Final rendering requires an explicit frozen input manifest')
    OUT.mkdir(exist_ok=True, parents=True)
    files = [Path(__file__), ROOT / 'render_cad.py', args.manifest.resolve()]
    for machine in manifest['machines']:
        keys = ('deployed_step', 'parked_step') + (('deployed_context_step', 'parked_context_step')
            if machine.get('context_contains_mechanism') else ('context_step',))
        files += [ROOT / machine[k] for k in keys]
    before = {rel(p): sha(p) for p in sorted(set(files))}
    report_path = HERE / 'preview-verification.json'
    previous = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
    cached = {x['image']: x for x in previous.get('images', [])}
    imported = {}; images = []; start = time.monotonic()
    for machine in manifest['machines']:
        ident = machine['id']
        print('Importing', ident, flush=True)
        context = None
        if not machine.get('context_contains_mechanism'):
            context_path = ROOT / machine['context_step']
            context, imported[rel(context_path)] = step_bodies(context_path, 'context')
        for state in ('deployed', 'parked'):
            path = ROOT / machine[state + '_step']
            mechanism, imported[rel(path)] = step_bodies(path, 'mechanism')
            if machine.get('context_contains_mechanism'):
                context_path = ROOT / machine[state + '_context_step']
                complete, imported[rel(context_path)] = step_bodies(context_path, 'context')
                source_by_name = {b.name: b for b in mechanism}
                complete_by_name = {b.name: b for b in complete}
                assert len(source_by_name) == len(mechanism) and len(complete_by_name) == len(complete)
                # Color the exact combined STEP occurrences; do not overlay
                # a second copy of mechanism solids onto the machine assembly.
                for name, body in source_by_name.items():
                    actual = complete_by_name[name]
                    assert np.max(np.abs(np.array(bounds(body.shape)) - np.array(bounds(actual.shape)))) < .01, name
                    assert abs(body.shape.Volume() - actual.shape.Volume()) < max(.2, body.shape.Volume()*1e-7), name
                    if actual.role != 'allocation':
                        actual.role = body.role
                imported[rel(context_path)]['mechanism_name_bounds_volume_matches'] = len(mechanism)
            else:
                complete = context + mechanism
            note = machine.get('subtitle', 'Actual exported STEP solids; supplier magazine interface remains unverified')
            for full in (True, False):
                key = 'full' if full else 'mechanism'
                name = f'{ident}-{state}-{key}.png'
                title = f'{machine["title"]}  |  {state.upper()}  |  {"MACHINE" if full else "MECHANISM"}'
                default = (1.4, 1.7, 1.25) if ident == 'small' else (1.4, -1.5, 1.2)
                camera = machine.get('full_camera' if full else 'mechanism_camera', default)
                image_path = OUT / name
                signature = {'renderer': before[rel(__file__)], 'depth_rasterizer': before[rel(ROOT / 'render_cad.py')],
                             'mechanism_step': before[rel(path)], 'context_step': before[rel(context_path)] if full else None,
                             'title': title, 'subtitle': note, 'camera': camera, 'full_context': full}
                prior = cached.get(rel(image_path))
                if prior and prior.get('input_signature') == signature and image_path.exists() and sha(image_path) == prior['sha256']:
                    record = prior
                else:
                    record = render(complete if full else mechanism, image_path, title, note, camera, full)
                    record['input_signature'] = signature
                images.append(record)
                print('Rendered', name, flush=True)
    after = {rel(p): sha(p) for p in sorted(set(files))}
    unchanged = before == after
    complete_set = {m['id'] for m in manifest['machines']} == {'small', 'large'}
    report = {'schema': 1, 'passed': unchanged and len(images) == 4*len(manifest['machines']) and (complete_set or args.allow_partial),
              'complete_machine_set': complete_set,
              'scope': 'Actual STEP tessellation and preview provenance; not interference, strength, handling, control or fabrication qualification.',
              'machine_release': False, 'geometry_frozen_manifest': True,
              'source_sha256_before': before, 'source_sha256': after, 'sources_unchanged': unchanged,
              'step_readback': imported, 'images': images,
              'image_sha256': {x['image']: x['sha256'] for x in images},
              'render_seconds': round(time.monotonic() - start, 2),
              'limitations': ['Tessellation is a display approximation of exported BREP.',
                              'Opaque hidden bodies are not visible from every camera.',
                              'Mechanism-only images deliberately hide all machine context.',
                              'Purchased envelopes and allocations do not establish delivered supplier fit.']}
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    assert report['passed'], 'Input changed during rendering or missing required views'
    print('Preview verification PASS', len(images), 'images', flush=True)


if __name__ == '__main__':
    try:
        main(); code = 0
    except Exception:
        import traceback
        traceback.print_exc(); code = 1
    sys.stdout.flush(); sys.stderr.flush(); os._exit(code)
