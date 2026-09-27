"""GM1 Rev K working CAD: the one-piece hoisted bed (Rev J) completed for both tools.

Rev K is built on Rev J (`../RevE-ENGINEERING/build_revj.py`, used unchanged) and adds,
in this order:
  revk_water.py    refill spout air gap, pan drain screen, manual reservoir drain, NBR seals
  revk_service.py  the other session's Rev I drain, strainer and pressure hose (lowered to
                   the Rev J spout), and a suction line without a high point
  revk_cabinet.py  Rev I cabinet with the door, cable-entry, heat and VFD fixes
  plasma_drop.py   Rev I floating/breakaway head on a drop bracket, with the owner's torch

The sources live in this folder so the shared RevE-ENGINEERING inventory is unchanged.
Exports three states to ../RevK-CAD:
  RevK_ROUTER        bed module installed, router head, plasma head parked (cut list and DXF)
  RevK_PLASMA        module out, router tool stored, plasma head and torch on the Z adapter
  RevK_BED_MODULE    the lifted module alone (unchanged from Rev J)
Unknown purchased interfaces stay guarded; no manufacturing release is implied.
"""
from pathlib import Path
import hashlib
import importlib
import json
import os
import sys
import time

HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / 'RevE-ENGINEERING'
for path in (str(LEGACY), str(HERE)):
    if path not in sys.path:
        sys.path.insert(0, path)

from cad_helpers import export  # noqa: E402
import build_revj as rev_j  # noqa: E402

OUT = HERE.parent / 'RevK-CAD'
MACHINE = rev_j.MACHINE
EXTENSIONS = ('revk_water', 'revk_service', 'revk_cabinet', 'plasma_drop')
HOLD_TORCH = ('Torch: the owner\'s photo shows a PT31-style straight machine torch, 270 mm long with a 28 mm barrel (seller figures). '
              'Measure the barrel before boring the clamp insert. Release force, float trip, lead routing and the tether still need testing.')


def source_hashes():
    files = sorted(HERE.glob('*.py')) + sorted(LEGACY.glob('*.py'))
    return {f'{p.parent.name}/{p.name}': hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def purchased_material(model):
    """Earlier generators left purchased parts on the default 'A36 steel'; say what they are in the cut list."""
    for p in model.parts:
        if p.purchased and p.material == 'A36 steel':
            p.material = 'Purchased item: see the part number and notes'


def build_model(with_motion=True, gantry_y=1275.0, head_x=575.0, z_lift=100.0):
    model, details = rev_j.build_model(with_motion=False)
    for name in EXTENSIONS:
        details[name] = importlib.import_module(name).extend_router_model(model)
    details['revk_water']['nbr_seals'] = importlib.import_module('revk_water').nbr_seals(model)
    if with_motion:
        details['motion'], details['motion_completion'] = rev_j.add_motion(model, gantry_y, head_x, z_lift)
    purchased_material(model)
    model.holds[:] = [HOLD_TORCH if h.startswith(('The owned torch barrel/clamping zone', 'Actual torch barrel, straight grip')) else h
                      for h in model.holds]
    model.holds.append('Cabinet: the fan, glands and VFD are selected by function; confirm the received VFD size and heat, '
                       'and test the cabinet temperature rise at full load.')
    details['machine'] = MACHINE
    details['revision'] = 'K working design: Rev J one-piece bed with Rev I service and head, and the review fixes'
    details['status'] = 'WORKING CAD - NOT A FABRICATION RELEASE'
    return model, details


def plasma_model(router_model, **head):
    import plasma_drop
    stored = rev_j.plasma_layout(router_model)
    model, details = plasma_drop.plasma_head_model(stored, **head)
    purchased_material(model)
    return model, details


def main():
    start = time.monotonic()
    before = source_hashes()
    OUT.mkdir(parents=True, exist_ok=True)
    rev_j.OUT = OUT
    model, details = build_model()
    print('Rev K router:', len(model.parts), 'components', flush=True)
    router = export(model, OUT, 'RevK_ROUTER', individual=True)
    rev_j.write_mesh(model, 'RevK_ROUTER')
    plasma, details['plasma_head'] = plasma_model(model)
    print('Rev K plasma:', len(plasma.parts), 'components', flush=True)
    parked = export(plasma, OUT, 'RevK_PLASMA', individual=False)
    rev_j.write_mesh(plasma, 'RevK_PLASMA')
    module = rev_j.module_only(model)
    alone = export(module, OUT, 'RevK_BED_MODULE', individual=False)
    rev_j.write_mesh(module, 'RevK_BED_MODULE')
    details['state_checks'] = {
        key: {'part_count': r['part_count'], 'step_readback': r['step_readback'],
              'unresolved_intersections': r['unresolved_intersections']}
        for key, r in [('router', router), ('plasma', parked), ('bed_module_alone', alone)]}
    details['holds'] = sorted(set(model.holds) | set(plasma.holds))
    after = source_hashes()
    details['source_sha256'] = after
    details['sources_changed_during_build'] = {k: v for k, v in before.items() if after.get(k) != v}
    details['elapsed_seconds'] = round(time.monotonic() - start, 2)
    clashes = [len(r['unresolved_intersections']) for r in (router, parked, alone)]
    details['integrated_geometry_pass'] = not any(clashes) and not details['sources_changed_during_build']
    (OUT / 'engineering-manifest.json').write_text(json.dumps(details, indent=2, default=str) + '\n', encoding='utf-8')
    print('Exported three states; unresolved clashes (router, plasma, module):', clashes, flush=True)
    return 0 if details['integrated_geometry_pass'] else 2


if __name__ == '__main__':
    try:
        code = main()
    except Exception:
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
