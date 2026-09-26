"""Run unchanged Rev G continuous large-part solvers against full Rev H.

Builder injection changes the actual obstacles and moved components. Each phase
uses the defined Rev H restraint state. This is not a proof of small-part moves,
human reach, tolerance allowance, mechanical strength or complete conversion.
The added restraint movements are verified separately by the bed checker.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
import traceback
import types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'output/release-review/RevE-ENGINEERING'
OLD = ROOT / 'output/cad-repair-2026-09-25'
OUT = Path(__file__).resolve().parent / 'routes'
sys.path.insert(0, str(OLD))
sys.path.insert(0, str(SOURCE))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hashes():
    paths = set(SOURCE.glob('*.py')) | {
        Path(__file__).resolve(), OLD / 'check_spoil_transfer.py',
        OLD / 'verify_revg_beam_path.py',
    }
    return {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
            for p in sorted(paths)}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(kind):
    import build_revg
    import build_revh
    import bed_completion

    initial = hashes()
    begin = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=True)
    definitions = {
        'spoil': (OLD / 'check_spoil_transfer.py', 'spoil-transfer-check.json',
                  bed_completion.prepare_handling_model),
        'panel': (SOURCE / 'verify_revg_panel_path.py', 'panel-path-check.json',
                  bed_completion.prepare_panel_handling_model),
        'beam': (OLD / 'verify_revg_beam_path.py', 'beam-path-check.json',
                 bed_completion.prepare_beam_handling_model),
    }
    script, result_name, prepare = definitions[kind]
    old_module = load('revh_reused_' + kind, script)
    record = {}

    def completed_builder(*args, **kwargs):
        model, details = build_revh.build_model(*args, **kwargs)
        prepare(model)
        record['part_count'] = len(model.parts)
        record['restraint_preparation'] = prepare.__name__
        record['holds'] = sorted(set(model.holds))
        return model, details

    # Spoil/beam solvers hold an imported builder; panel imports it in main.
    # A module proxy supplies only the panel import. build_revh.previous still
    # points to the actual baseline module, so its builder cannot recurse.
    proxy = types.ModuleType('build_revg')
    proxy.__dict__.update(build_revg.__dict__)
    proxy.build_model = completed_builder
    old_module.build_model = completed_builder
    old_module.hashes = hashes
    old_module.__file__ = str(OUT / script.name)
    old_module.OUT = OUT / result_name
    sys.modules['build_revg'] = proxy
    try:
        code = old_module.main()
    finally:
        sys.modules['build_revg'] = build_revg
    output = OUT / result_name
    result = json.loads(output.read_text(encoding='utf-8'))
    after = hashes()
    changed = {p: {'before': value, 'after': after.get(p)}
               for p, value in initial.items() if after.get(p) != value}
    result['revision'] = 'Rev H full integrated machine, original prescribed large-part route'
    result['builder'] = 'build_revh.build_model'
    result['revh_obstacle_state'] = record
    result['original_solver_source'] = str(script.relative_to(ROOT)).replace('\\', '/')
    result['complete_source_sha256'] = initial
    result['complete_sources_changed_during_run'] = changed
    result['runner_sha256'] = sha(__file__)
    result['integrated_elapsed_seconds'] = round(time.monotonic() - begin, 2)
    if kind == 'spoil':
        result['scope'] = ('All prescribed bare-board motions from installed state to internal storage on the complete Rev H model. All 24 spoilboard screws are already removed. Retained nut strips and M3 set screws remain with panels. Human handling, finger clearance, hardware-transfer paths and new restraint movements are excluded.')
        result['hardware_sequence'] = ('All 24 spoilboard screws pre-stored. The 12 Rev H nut strips and 24 M3 retainers remain installed through both board and panel moves. Panel restraint pieces are in prepare_handling_model staging poses, spoil guard OPEN and stack bolts parked; the separate restraint checker must prove the transitions into and out of those poses.')
    result['integrated_passed'] = code == 0 and not changed
    if changed:
        result['status'] = 'STALE'
        if 'pass' in result:
            result['pass'] = False
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('REVH_ROUTE', kind, 'PASS' if result['integrated_passed'] else 'FAIL',
          result['integrated_elapsed_seconds'], 'seconds', flush=True)
    return result['integrated_passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=('spoil', 'panel', 'beam', 'all'), default='all', nargs='?')
    args = parser.parse_args()
    try:
        kinds = ('spoil', 'panel', 'beam') if args.kind == 'all' else (args.kind,)
        results = [run(kind) for kind in kinds]
        code = 0 if all(results) else 2
    except Exception:
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
