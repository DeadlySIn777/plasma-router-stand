"""Fresh check of the supplied plasma bed/setup view, not an operational torch model."""
from pathlib import Path
import json
import os
import sys

OUT=Path(__file__).resolve().parent
CAD=OUT.parents[1]/'output/release-review/RevE-ENGINEERING'
sys.path.insert(0,str(CAD))

def main():
    from build_reve_engineering import build_model
    from export_states import plasma_model
    from cad_helpers import validate,bbox
    m,_=build_model()
    plasma=plasma_model(m)
    bare_report=validate(plasma)
    saved=json.loads((CAD/'RevE_PLASMA_SETUP-validation.json').read_text())
    prior={p['id']:p for p in saved['parts']}
    bare_bounds_mismatches=[p['id'] for p in bare_report['parts']
        if p['id'] in prior and max(abs(a-b) for a,b in zip(p['bounds_mm'],prior[p['id']]['bounds_mm']))>1e-4]
    # export_states.py tessellates the router preview BEFORE constructing its
    # plasma copy. OCC's default bounding box may then use cached triangulation.
    # Reproduce that sequence instead of misclassifying loose cached bounds as
    # an actual shape change. Mesh data is in memory only.
    for p in m.parts:p.shape.tessellate(.7,.25)
    plasma=plasma_model(m)
    report=validate(plasma)
    diffs=[]
    for p in plasma.parts:
        old=prior.get(p.id)
        if old is None or abs(p.shape.Volume()-old['volume_mm3'])>max(.05,p.shape.Volume()*1e-7) or max(abs(a-b) for a,b in zip(bbox(p.shape),old['bounds_mm']))>1e-4:
            diffs.append(p.id)
    report['saved_geometry_mismatches']=diffs
    report['pre_preview_bounds_mismatch_count']=len(bare_bounds_mismatches)
    report['bounds_comparison_note']='Production export tessellates the router before making the plasma state. Fresh untessellated shapes may report tighter bounding boxes even at identical volumes. This comparison reproduces the production mesh-cache sequence; no source solid is edited.'
    report['missing_saved_ids']=sorted(set(prior)-{p.id for p in plasma.parts})
    report['scope']='Supplied bed-conversion/setup state only. It contains no installed plasma torch, floating touch-off or breakaway; no operational plasma sweep is verified.'
    (OUT/'fresh-plasma-display-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Plasma display:',report['part_count'],'solids;',len(report['unresolved_intersections']),'unresolved;',len(diffs),'source/export mismatches',flush=True)

if __name__=='__main__':
    code=0
    try:main()
    except Exception:
        import traceback
        traceback.print_exc()
        code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
