"""Reproduce MT01 closure evidence without overwriting release or audit files.

The adapter is still a provisional mating interface. These exports are geometry
verification artifacts, not released fabrication instructions.
"""
from pathlib import Path
import hashlib,json,os,sys

ROOT=Path(__file__).resolve().parent
# ROOT is <repo>/output/cad-repair-2026-09-25/motion.
ENGINEERING=ROOT.parents[1]/'release-review'/'RevE-ENGINEERING'
sys.path.insert(0,str(ENGINEERING))
import cadquery as cq
import ezdxf
from ezdxf import bbox as dxf_bbox
from cad_helpers import Model,bbox,box,write_dxf,intersection_volume
from check_motion_states import assembled_rail_caps,normalized_add
from motion_details import make_motion

def dxf_wire(polyline):
    """Recover machining geometry from DXF line/arc entities, not CAD metadata."""
    edges=[]
    for ent in polyline.virtual_entities():
        if ent.dxftype()=='LINE':
            edges.append(cq.Edge.makeLine(cq.Vector(*ent.dxf.start),cq.Vector(*ent.dxf.end)))
        elif ent.dxftype()=='ARC':
            start,end=ent.dxf.start_angle,ent.dxf.end_angle
            if end<=start:end+=360
            edges.append(cq.Edge.makeCircle(ent.dxf.radius,cq.Vector(*ent.dxf.center),cq.Vector(0,0,1),start,end))
        else:raise AssertionError(ent.dxftype())
    wire=cq.Wire.assembleEdges(edges)
    assert wire.isValid() and wire.IsClosed()
    return wire

def main():
    model=Model()
    for p in assembled_rail_caps():normalized_add(model,p)
    make_motion(model)
    part=model.find('TOOL_ADAPTER_110')
    step_path=ROOT/'TOOL_ADAPTER_110.PROVISIONAL.step'
    dxf_path=ROOT/'TOOL_ADAPTER_110.PROVISIONAL.dxf'
    cq.exporters.export(part.local,str(step_path))
    write_dxf(dxf_path,part.flat)
    reread=cq.importers.importStep(str(step_path)).val()
    assert reread.isValid() and len(reread.Solids())==1
    step_volume_delta=abs(reread.Volume()-part.local.Volume())
    assert step_volume_delta<1e-5
    doc=ezdxf.readfile(dxf_path)
    assert doc.units==4 and not doc.audit().has_errors
    recesses=list(doc.modelspace().query('LWPOLYLINE[layer=="MILL_FRONT_COUNTERSLOT_DEPTH_6_6"]'))
    assert len(recesses)==2
    checks=[];eps=1e-4
    for polyline,cx in zip(recesses,(20,90)):
        bb=dxf_bbox.extents([polyline]);actual_bounds=[bb.extmin.x,bb.extmin.y,bb.extmax.x,bb.extmax.y]
        expected_bounds=[cx-5.5,30,cx+5.5,60]
        assert max(abs(a-b) for a,b in zip(actual_bounds,expected_bounds))<1e-6
        # At a front-face interior slab, recover the actual STEP void. It must
        # equal the exported DXF pocket exactly, not just share its AABB.
        z0,z1=6.1+eps,12.7-eps
        region=box(12,32,z1-z0).translate((cx-6,29,z0))
        actual_void=region.cut(reread).clean()
        exported_void=cq.Workplane('XY').add(dxf_wire(polyline)).toPending().extrude(z1-z0).val().translate((0,0,z0))
        common=intersection_volume(actual_void,exported_void)
        symmetric_difference=actual_void.Volume()+exported_void.Volume()-2*common
        assert abs(symmetric_difference)<1e-5
        # The radius-5.5 half-cylinder faces establish the actual pocket's
        # local-Z depth independently of the operation label/metadata.
        ends=[]
        for face in reread.Faces():
            if face.geomType()!='CYLINDER':continue
            cylinder=face._geomAdaptor().Cylinder()
            loc=cylinder.Location()
            if abs(cylinder.Radius()-5.5)<1e-6 and abs(loc.X()-cx)<1e-6:
                fb=bbox(face)
                assert abs(fb[2]-6.1)<1e-6 and abs(fb[5]-12.7)<1e-6
                ends.append({'bounds_mm':fb,'depth_mm':fb[5]-fb[2]})
        assert len(ends)==2
        checks.append({'center_x_mm':cx,'dxf_bounds_xy_mm':actual_bounds,
                       'expected_bounds_xy_mm':expected_bounds,'step_recess_end_faces':ends,
                       'front_slice_dxf_step_symmetric_difference_mm3':symmetric_difference})
    operations={'part_number':part.part_number,'release':part.release,
                'scope':'Provisional adapter. Rotation/depth alignment verified; supplier interface remains open.',
                'manufacturing_flat':part.flat,'notes':part.notes}
    (ROOT/'TOOL_ADAPTER_110.operations.json').write_text(json.dumps(operations,indent=2)+'\n',encoding='utf-8')
    report={'finding':'MT01','result':'PASS','scope':operations['scope'],
            'step_valid':True,'step_solids':len(reread.Solids()),'step_volume_delta_mm3':step_volume_delta,
            'dxf_units':'mm','dxf_audit_errors':False,'recess_checks':checks,
            'sources_sha256':{name:hashlib.sha256((ENGINEERING/name).read_bytes()).hexdigest()
                              for name in ('cad_helpers.py','motion_details.py','check_motion_states.py')},
            'artifacts_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (step_path,dxf_path)}}
    (ROOT/'adapter-export-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)
    return 0

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
