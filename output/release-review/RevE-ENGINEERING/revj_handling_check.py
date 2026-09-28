"""Actual-solid sampled check of the Rev J bed-module hoist path, rigging included.

The one-piece module (every MOD_* part) and a modeled 4-leg sling move as ONE
rigid body: lift 70 mm in place, then travel forward out of the open front
window. The six BED_M10 drawdowns are removed first. The gantry is at the rear
stop with the head centred (X575) and Z fully raised; the spindle stays in place
as a conservative obstacle. Sling legs run from each lug-hole centre to a hook
point above the module centre of mass; three hook heights are checked. Fixed
obstacles include the Rev H service hatches, the relocated Rev J refill spout
and the Rev H braked Z-motor candidate envelope (top Z1430.5).
Run with the project CadQuery environment.
"""
from pathlib import Path
import datetime
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
import cadquery as cq

from cad_helpers import bbox, cyl, intersection_volume

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT.parent / 'RevJ-CAD'
OUT = OUT_DIR / 'handling-check.json'
LIFT = 70.0
FORWARD = 1420.0              # module rear end (lugs, Y1347.8) finishes at Y-72.2, ahead of the feet at Y-14.6
HOOK_RISES = (700.0, 1000.0, 2000.0)   # hook point above the lug-hole plane
LEG_D = 13.0                  # chain leg plus shackle envelope
HOOK_BLOCK = (90.0, 180.0)    # hook and bottom block envelope, diameter x height
CLEARANCE_MARGIN = 40.0
I = np.eye(3)


def pose(t=(0, 0, 0)):
    M = np.eye(4); M[:3, 3] = t; return M


def moved(shape, M):
    return shape.moved(cq.Plane(origin=tuple(M[:3, 3]), xDir=(1, 0, 0), normal=(0, 0, 1)).location)


def overlaps(a, b, tol=1e-5):
    return all(a[k + 3] > b[k] + tol and b[k + 3] > a[k] + tol for k in range(3))


def near(a, b, margin):
    return all(a[k + 3] + margin > b[k] and b[k + 3] + margin > a[k] for k in range(3))


def segment(p0, p1, d):
    p0 = cq.Vector(*p0); p1 = cq.Vector(*p1); axis = p1 - p0
    return cq.Solid.makeCylinder(d / 2, axis.Length, p0, axis.normalized())


def rigging(lugs, hook):
    legs = [(f'SLING_LEG_{i}', segment(h, hook, LEG_D)) for i, h in enumerate(lugs, 1)]
    block = cyl(HOOK_BLOCK[0], HOOK_BLOCK[1]).translate(hook)
    return legs + [('HOOK_BLOCK', block)]


class Checker:
    def __init__(self, model, details, hook_rise):
        self.hook_rise = hook_rise
        bed = details['bed']
        self.module = [(p.id, p.shape) for p in model.parts if p.id.startswith('MOD_')]
        self.removed = [p.id for p in model.parts if p.id.startswith('BED_M10_')]
        self.fixed = [(p.id, p.shape, bbox(p.shape)) for p in model.parts
                      if not p.id.startswith(('MOD_', 'BED_M10_'))]
        cg = bed['module_cg_mm']
        lugs = bed['lift_lugs']['holes_xyz_mm']
        self.hook = (cg[0], cg[1], lugs[0][2] + hook_rise)
        self.rig = rigging(lugs, self.hook)
        self.lugs = lugs
        self.failures = []; self.samples = 0; self.checks = 0; self.trace = []
        self.sweep = [math.inf] * 3 + [-math.inf] * 3
        self.M = pose()

    def bodies(self, M):
        return [('module', i, moved(s, M)) for i, s in self.module] + [('rigging', i, moved(s, M)) for i, s in self.rig]

    def examine(self, M, stage, progress):
        self.samples += 1
        prior = len(self.failures)
        for kind, name, shape in self.bodies(M):
            b = bbox(shape)
            if kind == 'module':
                self.sweep = [min(self.sweep[k], b[k]) for k in range(3)] + [max(self.sweep[k + 3], b[k + 3]) for k in range(3)]
            for other, obstacle, ob in self.fixed:
                if not overlaps(b, ob):
                    continue
                self.checks += 1
                v = intersection_volume(shape, obstacle)
                if v > 0.02:
                    self.failures.append({'moving': name, 'kind': kind, 'stage': stage, 'progress': round(progress, 5),
                                          'obstacle': other, 'intersection_mm3': round(v, 4)})
        return len(self.failures) == prior

    def move(self, name, target, step):
        start = self.M.copy()
        length = float(np.linalg.norm(target[:3, 3] - start[:3, 3])); n = max(1, math.ceil(length / step))
        prior = len(self.failures)
        for j in range(n + 1):
            u = j / n
            self.examine(pose((1 - u) * start[:3, 3] + u * target[:3, 3]), name, u)
        self.M = target
        self.trace.append({'stage': name, 'start_translation_mm': start[:3, 3].round(4).tolist(),
                           'end_translation_mm': target[:3, 3].round(4).tolist(), 'samples': n + 1,
                           'step_mm': step, 'passed': len(self.failures) == prior})
        print(f'  hook +{self.hook_rise:g}: {name}', 'PASS' if len(self.failures) == prior else 'FAIL', flush=True)

    def clearances(self, M, label, kinds=('module', 'rigging'), limit=12):
        """Smallest nominal gaps from moving solids to fixed parts within the margin."""
        found = []
        for kind, name, shape in self.bodies(M):
            if kind not in kinds:
                continue
            b = bbox(shape)
            for other, obstacle, ob in self.fixed:
                if not near(b, ob, CLEARANCE_MARGIN):
                    continue
                d = shape.distance(obstacle)
                if d < CLEARANCE_MARGIN:
                    found.append({'moving': name, 'kind': kind, 'obstacle': other, 'gap_mm': round(d, 2)})
        best = {}
        for f in sorted(found, key=lambda f: f['gap_mm']):
            key = (f['kind'], f['obstacle'].rstrip('0123456789_'))
            best.setdefault(key, f)
        return {'pose': label, 'nearest': sorted(best.values(), key=lambda f: f['gap_mm'])[:limit]}

    def rigging_vs_module(self):
        """Sling legs must not bear on the deck, strips or HDPE (lugs themselves excluded)."""
        hits = []
        for name, leg in self.rig:
            lb = bbox(leg)
            for mid, shape in self.module:
                if mid.startswith('MOD_LUG_'):
                    continue
                if overlaps(lb, bbox(shape)) and intersection_volume(leg, shape) > 0.02:
                    hits.append({'leg': name, 'module_part': mid})
        return hits

    def run(self):
        self.examine(pose(), 'installed, sling taut', 0)
        self_contact = self.rigging_vs_module()
        near_installed = self.clearances(pose(), 'installed, sling only (module seating contacts are intended)', kinds=('rigging',))
        self.move(f'lift {LIFT:g} mm in place', pose((0, 0, LIFT)), 5)
        near_lifted = self.clearances(pose((0, 0, LIFT)), f'lifted {LIFT:g} mm')
        self.move('forward out of the front window', pose((0, -FORWARD, LIFT)), 25)
        leg_angles = []
        for (x, y, z) in self.lugs:
            dx, dy, dz = self.hook[0] - x, self.hook[1] - y, self.hook[2] - z
            leg_angles.append(round(math.degrees(math.atan2(dz, math.hypot(dx, dy))), 1))
        return {'hook_rise_above_lug_holes_mm': self.hook_rise, 'hook_point_installed_mm': [round(v, 1) for v in self.hook],
                'sling_leg_angle_from_horizontal_deg': leg_angles,
                'sling_leg_lengths_mm': [round(math.dist(l, self.hook), 1) for l in self.lugs],
                'samples': self.samples, 'boolean_checks': self.checks, 'failures': self.failures,
                'rigging_contacts_with_module': self_contact, 'segments': self.trace,
                'nearest_fixed_parts': [near_installed, near_lifted],
                'module_sweep_envelope_mm': [round(v, 2) for v in self.sweep],
                'result': 'PASS SAMPLED PATH' if not self.failures and not self_contact else 'FAIL'}


def main():
    start = time.monotonic()
    from build_revj import build_model
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')}
    model, details = build_model(with_motion=True)
    motion = details['motion']['configuration']
    cases = []
    for rise in HOOK_RISES:
        cases.append(Checker(model, details, rise).run())
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')}
    bed = details['bed']
    passed = all(c['result'].startswith('PASS') for c in cases) and before == after
    report = {'machine': details.get('machine'), 'revision': details.get('revision'),
              'result': 'PASS SAMPLED PATH' if passed else 'FAIL',
              'scope': __doc__.strip(),
              'motion_state': motion,
              'module_part_count': sum(1 for p in model.parts if p.id.startswith('MOD_')),
              'removed_for_handling': [p.id for p in model.parts if p.id.startswith('BED_M10_')],
              'module_mass_estimate_kg': bed['module_mass_estimate_kg'], 'module_cg_mm': bed['module_cg_mm'],
              'lift_mm': LIFT, 'forward_mm': FORWARD,
              'rigging_model': f'Four Ø{LEG_D:g} mm legs from lug-hole centres to one hook point above the centre of mass; hook and block Ø{HOOK_BLOCK[0]:g} x {HOOK_BLOCK[1]:g} mm. Shackle bodies and chain sag are not modeled.',
              'method': 'Actual B-rep positive-volume intersections (threshold 0.02 mm3), AABB broad phase, lift sampled every 5 mm and travel every 25 mm. Nearest gaps by BRep distance within 40 mm. Sampled path, not a proof of all intermediate poses or of rigging behavior.',
              'required_preconditions': bed['sequence'][:3],
              'fixed_obstacle_count': len(model.parts) - sum(1 for p in model.parts if p.id.startswith(('MOD_', 'BED_M10_'))),
              'sources_unchanged_during_run': before == after,
              'source_sha256': before, 'cases': cases,
              'elapsed_seconds': round(time.monotonic() - start, 1),
              'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('RESULT', report['result'], [(c['hook_rise_above_lug_holes_mm'], c['result'], len(c['failures'])) for c in cases], flush=True)
    return 0 if passed else 2


if __name__ == '__main__':
    try:
        code = main()
    except Exception:
        import traceback
        traceback.print_exc(); code = 1
    sys.stdout.flush(); sys.stderr.flush(); os._exit(code)
