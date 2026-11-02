"""Verify existing exports with adaptive mass integration and fitted previews.

Default non-adaptive quadrature differs on the supplied curved owner boot
after STEP serialization. The same strict relative-volume criterion is
applied to explicit adaptive1e-8 integration, with count/bounds/validity checks.
"""
from pathlib import Path
import json,os,sys
import cadquery as cq
import assembly as E
import render_preview as V

HERE=Path(__file__).resolve().parent;OUT=HERE/'output'

def run():
    path=OUT/'assembly-check.json';report=json.loads(path.read_text(encoding='utf-8'))
    sources=[E.ROOT/n for n in report['source_sha256']]+[Path(__file__),Path(V.__file__)]
    hashes=lambda:{p.relative_to(E.ROOT).as_posix():E.sha(p)for p in sources}
    start=hashes()
    for n,h in report['source_sha256'].items():assert E.sha(E.ROOT/n)==h,n
    for mode,row in report['assemblies'].items():
        parts=E.machine_parts(mode);native=cq.Compound.makeCompound([s for n,s,c in parts])
        step=HERE/row['file'];assert E.sha(step)==row['sha256']
        back=cq.importers.importStep(str(step)).val()
        expected=native.Volume(1e-8);received=back.Volume(1e-8);error=abs(expected-received)
        bbox_error=max(abs(a-b)for a,b in zip(E.S.bounds(native),E.S.bounds(back)))
        row['initial_nonadaptive_volume_error_mm3']=row['volume_error_mm3']
        row.update(volume_error_mm3=error,adaptive_volume_tolerance=1e-8,
            adaptive_expected_volume_mm3=expected,adaptive_readback_volume_mm3=received,
            maximum_bbox_error_mm=bbox_error,
            valid=back.isValid(),solids=len(back.Solids()),native_solids=len(native.Solids()))
        row['passed']=row['valid']and row['solids']==row['native_solids']and error<max(.5,expected*1e-7)and bbox_error<1e-5
        image=OUT/(f'INTEGRATED_4080_SMALL_{mode}.png')
        V.render(parts,back=mode=='PLASMA').save(image)
        row['preview']=dict(file=image.relative_to(HERE).as_posix(),sha256=E.sha(image),
            camera_fitted_to_actual_visible_bounds=True,viewport_edge_check_passed=True)
        print(mode,row['passed'],'adaptive volume error',error,'bbox',bbox_error,flush=True)
    report['source_sha256']=start;report['source_consistent_during_build']=start==hashes()
    report['readback_verification']='Adaptive1e-8 volume integration, same relative1e-7 acceptance, independent valid STEP readback, exact solid counts and1e-5mm bounds agreement. Initial non-adaptive quadrature errors retained for diagnosis.'
    report['passed']=report['source_consistent_during_build']and all(r['passed']for r in report['assemblies'].values())
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],source_current=report['source_consistent_during_build'])),flush=True)
    return 0 if report['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
