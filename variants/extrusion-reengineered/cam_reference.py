"""Export the modeled replaceable wear surfaces and explicit setup datums.

No stock, clamps, cutter or machine postprocessor is inferred. No G-code.
"""
from pathlib import Path
import hashlib, json, os, sys
import cadquery as cq
import ezdxf
import params as P
from bed import cassette_parts,SKIM

HERE=Path(__file__).resolve().parent

def run():
    source={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('cam_reference.py','params.py','bed.py')}
    out=HERE/'fabrication'/'cam-reference';out.mkdir(parents=True,exist_ok=True)
    origin=(SKIM[0],SKIM[2],P.DRY_TOP)
    parts=[];wires=[];rows=[]
    for i in range(4):
        for n,s,c in cassette_parts(i):
            if 'REPLACEABLE_' not in n or '_MDF_WEAR_' not in n:continue
            local=s.translate(tuple(-v for v in origin));b=local.BoundingBox()
            faces=[f for f in local.Faces() if f.geomType()=='PLANE' and abs(f.BoundingBox().zmin)<1e-6 and abs(f.BoundingBox().zmax)<1e-6]
            assert faces,n
            for face in faces:wires.extend([face.outerWire(),*face.innerWires()])
            parts.append(local)
            rows.append({'id':n,'setup_local_bounds_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],
                         'top_face_area_mm2':sum(f.Area() for f in faces)})
    assert len(parts)==4,rows
    mask=cq.Compound.makeCompound(wires)
    dxf=out/'WOOD_WEAR_TOP_BOUNDARIES_AND_SCREW_RECESSES.dxf'
    cq.exporters.export(cq.Workplane('XY').newObject([mask]),str(dxf))
    drawing=ezdxf.readfile(dxf);drawing.header['$INSUNITS']=4;drawing.saveas(dxf)
    assert len(drawing.modelspace())>0
    step=out/'WOOD_REPLACEABLE_WEAR_PADS.step'
    combined=cq.Compound.makeCompound(parts);cq.exporters.export(combined,str(step))
    reimport=cq.importers.importStep(str(step)).val()
    assert reimport.isValid() and len(reimport.Solids())==4
    current=source=={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in source}
    report={'revision':P.REVISION,'passed':current,'source_unchanged':current,'source_sha256':source,
        'output_sha256':{p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (dxf,step)},
        'nominal_wood_setup_origin_world_mm':list(origin),
        'setup_axes':'X right, Y rear, Z up. Setup Z0 is the modeled final wear-pad top; establish it by measurement after installation.',
        'enclosing_wear_field_mm':[SKIM[1]-SKIM[0],SKIM[3]-SKIM[2]],
        'actual_surface_pads':rows,'boundary_dxf':dxf.relative_to(HERE).as_posix(),
        'surface_step':step.relative_to(HERE).as_posix(),
        'manufacturing_release':False,
        'required_CAM_inputs':['Actual cutter envelope and projection','Workpiece and hold-down/clamp solids',
            'Purchased track die and any inserted track bolts','Measured machine WCS and tool-length offset',
            'Actual cutting tool reach over the whole stock','Machine controller and correct verified postprocessor'],
        'keepout_rule':'The enclosing770x960 field is not one uninterrupted spoilboard. Only the exported pad faces are wear surface. Tracks, seams, recessed edge structure, locating/clamping hardware and screw recesses are separate keep-outs. Offset every obstacle by the actual cutter and holder envelope before creating a path.',
        'surface_maintenance':'Prepare replaceable wear pads to final6.35mm before installing flush with tracks. Repeatedly skimming below the track tops does not preserve a continuous flat support plane. Replace pads or deliberately re-establish the complete finished datum.',
        'plasma_setup':'No operational plasma nozzle WCS or THC values are invented. Use actual torch projection, touch-off and verified postprocessor after cutter integration.',
        'scope':'Geometric wear-surface setup reference only. No stock layout, feeds/speeds, toolpath, simulation of cutting or machine program has been generated.'}
    (HERE/'review'/'cam-reference-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Exported four wear pads, top boundary DXF and explicit measured-WCS requirements.',flush=True)
    return 0 if current else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
