"""Regenerate motion-validation.json: five sampled motion-subsystem configurations.

Recreates the original motion-only screen (the one-off generator script was not
retained): for each configuration, a fresh model containing only the rail-cap
blanks at the assembled frame datum and the make_motion output is validated for solid validity and
positive-volume intersections, and every part's local blank is volume-checked
against its placed world solid (a rigid transform preserves volume).
"""
from pathlib import Path
import argparse,hashlib,json,sys,os
import cadquery as cq
from cad_helpers import *
import geometry_base as base

ROOT=Path(__file__).resolve().parent

STATES=[(1275,575,100,'router'),(275,175,0,'router'),(275,975,100,'router'),(1275,175,100,'router'),(1275,975,0,'router')]

def normalized_add(m,p):
    bb=bbox(p.shape);local=p.shape.translate(tuple(-x for x in bb[:3]))
    return m.add(p.id,local,origin=bb[:3],group=p.group,material=p.material,pn=p.id,color=p.color,
                 notes=list(getattr(p,'notes',[])))

def assembled_rail_caps():
    """Take cap blanks from the real frame builder, before motion drills holes.

    Keep only the original two cap blanks: this remains a motion-and-caps
    subsystem screen, not a second full-frame test. In particular, never move
    a cap after make_motion has drilled its stop-fastener holes.
    """
    from frame_details import make_frame
    frame=Model();cap_ids={p.id for p in base.fixed if p.group=='rail_cap'}
    for p in base.fixed:
        if p.group in ('main_frame','rail_cap'):normalized_add(frame,p)
    make_frame(frame)
    return [p for p in frame.parts if p.id in cap_ids]

def main(output_dir=ROOT):
    from motion_details import make_motion
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    states=[];mismatches=[];caps=assembled_rail_caps()
    cap_datums=[{'id':p.id,'bounds_mm':bbox(p.shape)} for p in caps]
    for gy,hx,zl,tool in STATES:
        m=Model()
        for p in caps:normalized_add(m,p)
        make_motion(m,gantry_y=float(gy),head_x=float(hx),z_lift=float(zl),tool=tool)
        r=validate(m)
        states.append({'configuration':{'gantry_y':gy,'beam_center_y':gy+80,'head_x':hx,'z_lift':zl,'tool':tool},
                       'parts':r['part_count'],'clashes':r['unresolved_intersections'],
                       'documented_intersection_count':len(r['documented_intersections'])})
        for p in m.parts:
            dv=abs(p.shape.Volume()-p.local.Volume())
            if dv>max(.05,p.shape.Volume()*1e-7):
                mismatches.append({'state':[gy,hx,zl],'id':p.id,'volume_delta_mm3':round(dv,5)})
        print('state',gy,hx,zl,'parts',r['part_count'],'clashes',len(r['unresolved_intersections']),flush=True)
    report={'source_file':'motion_details.py',
            'source_sha256':hashlib.sha256((ROOT/'motion_details.py').read_bytes()).hexdigest(),
            'fixture_source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                                     for name in ('frame_details.py','geometry_base.py','cad_helpers.py','check_motion_states.py')},
            'rail_caps_before_motion_drilling':cap_datums,
            'fixture':'Original two rail-cap blanks after frame_details.make_frame sets their assembled datum, before make_motion drills holes. Other frame parts and spacers are excluded from this subsystem screen.',
            'states':states,'local_world_geometry_mismatches':mismatches,
            'switch_actuation_handling':'For a roller on the 0.63-slope cam ramp, roller top is lowered by R*(sqrt(1+slope^2)-1), in addition to the cam underside at its center. Flat-land position follows the underside without intersection. The small lever and internal switch mechanism are not modeled. No positive overlap is permitted merely because a part is a switch.',
            'scope':'Five configurations of the motion subsystem only. No claim of continuous swept-volume clearance or complete machine strength/commissioning.'}
    (output_dir/'motion-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    ok=not mismatches and not any(s['clashes'] for s in states)
    lines=['# Motion subsystem verification','',
           '**Result: '+('PASS' if ok else 'FAIL')+'** for the sampled nominal configurations below.','',
           report['fixture'],'',
           '| Gantry Y | Head X | Z lift | Valid solids | Unresolved intersections | Documented overlaps |',
           '| ---: | ---: | ---: | ---: | ---: | ---: |']
    for state in states:
        c=state['configuration']
        lines.append(f"| {c['gantry_y']} | {c['head_x']} | {c['z_lift']} | {state['parts']} | {len(state['clashes'])} | {state['documented_intersection_count']} |")
    lines.extend(['',f'Local/world volume mismatches: {len(mismatches)}.','',report['scope'],'',
                  'The original unraised fixture was 6 mm too low and produced 22 spurious clashes per state. The test now obtains the cap datum from the assembly frame builder. Supplier interfaces, operational tool/cable geometry and Z retention remain unresolved; a passing screen does not release those items.','',
                  'Exact source hashes, cap bounds and configurations are recorded in `motion-validation.json`.',''])
    (output_dir/'motion-validation.md').write_text('\n'.join(lines),encoding='utf-8')
    print('MOTION-STATES',('PASS' if ok else 'FAIL'),flush=True)
    return 0 if ok else 2

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT,help='Directory for the generated JSON and Markdown report.')
    args=parser.parse_args()
    try:code=main(args.output_dir)
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
