"""Verified base-plate operation references for the revised welded stops."""
from pathlib import Path
import json,os,sys
import ezdxf
import z300_fit_study as S
import custom_joint_repair as R
import front_stop_repair as F

HERE=Path(__file__).resolve().parent;OUT=HERE/'output'/'front-stop-repair'

def run():
    paths=[Path(__file__),Path(F.__file__),OUT/'front-stop-repair-check.json',*R.sources()]
    hashes=lambda:{p.relative_to(S.ROOT).as_posix():S.sha(p)for p in dict.fromkeys(paths)}
    start=hashes();parts={n:s for n,s,_ in F.apply_repairs(R.apply_repairs(S.overlay(S.M.motion_parts(False,775,575,100))))}
    records={};z=S.M.OLD_BASE
    for side in('L','R'):
        for carrier in(False,True):
            ident=(f'XR_STOP_CARRIER_{side}_FRONT'if carrier else f'Y_STOP_{side}_FRONT_BRACKET')
            outline=[(49.5,80),(92.8,80),(92.8,120),(69.8,120),(69.8,151),(49.5,151)]if carrier else[(55.9,80),(92.8,80),(92.8,120),(69.8,120),(69.8,151),(49.5,151),(49.5,95.5),(55.9,95.5)]
            points=[(1150-x,y)if side=='R'else(x,y)for x,y in outline]
            x=1091.5 if side=='R'else 58.5
            origin=[min(p[0]for p in points),80.]
            local=[(a-origin[0],b-origin[1])for a,b in points]
            d=6. if carrier else 6.6
            layer='NOMINAL_M6_MAJOR_REFERENCE_NOT_TAP_DRILL'if carrier else'CLEARANCE_D6p6_THROUGH'
            doc=ezdxf.new('R2010');doc.units=4;m=doc.modelspace()
            doc.layers.new('FINISHED_BASE_OUTLINE',dxfattribs={'color':7});doc.layers.new(layer,dxfattribs={'color':1})
            m.add_lwpolyline(local,close=True,dxfattribs={'layer':'FINISHED_BASE_OUTLINE'})
            for y in(105,140):m.add_circle((x-origin[0],y-origin[1]),d/2,dxfattribs={'layer':layer})
            path=OUT/(ident+'_BASE_OPERATION_REFERENCE.dxf');doc.saveas(path)
            # Prove the reference profile against the actual finished base
            # material at its full6.35mm thickness, excluding welded uprights.
            reference=S.cq.Workplane('XY').polyline(points).close().extrude(6.35).val().translate((0,0,z-(6.35 if carrier else 0)))
            base_z=z-(6.35 if carrier else 0)
            for y in(105,140):reference=reference.cut(F.cyl(d,8.35,(x,y,base_z-1)))
            slab=S.box([0,0,base_z,1200,1450,base_z+6.35])
            actual=parts[ident].intersect(slab)
            difference=actual.cut(reference).Volume()+reference.cut(actual).Volume()
            read=ezdxf.readfile(path)
            records[ident]=dict(file=path.relative_to(HERE).as_posix(),sha256=S.sha(path),
                local_origin_world_X_Y_mm=origin,base_lower_world_Z_mm=base_z,
                thickness_mm=6.35,nominal_hole_axes_world_X_Y_mm=[[x,105],[x,140]],
                DXF_units='millimetres',dxf_circles=len(read.modelspace().query('CIRCLE')),
                exact_profile_symmetric_difference_mm3=difference,passed=difference<.05,
                instruction='Base constituent only; welded post/switch upright/tower and other bores follow the revised finished3D model. Carrier circle is nominal thread-major geometry; specify M6x1 thread with suitable pilot (nominal5mm), not a6mm drilled clearance hole.'if carrier else'Base constituent only;6.6mm clearance holes. Keep the original welded uprights and buffer/switch axes from revised finished3D. Superseded Y90hole is absent.')
    report=dict(study='REVISED_FRONT_STOP_BASE_OPERATION_REFERENCES',source_sha256=start,outputs=records,
        scope='Four exact base outlines/hole references tied to revised finished3D. These do not flatten the complete welded assemblies or qualify welds, tapping or joint capacity.',fabrication_release=False,
        source_consistent_during_check=start==hashes())
    report['passed']=report['source_consistent_during_check']and all(q['passed']for q in records.values())
    (OUT/'front-stop-base-reference-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],profiles={n:r['exact_profile_symmetric_difference_mm3']for n,r in records.items()})),flush=True)
    return 0 if report['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
