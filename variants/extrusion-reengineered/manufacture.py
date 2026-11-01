"""Export actual custom solids, with explicit nominal-thread/interface limits.

These files preserve the designed geometry for CAM preparation. They are not
an instruction to machine unknown vendor interfaces without measuring them.
"""
from pathlib import Path
import csv, hashlib, json, os, sys
import cadquery as cq
import ezdxf
import params as P
from frame import frame_parts
from motion import motion_parts

HERE=Path(__file__).resolve().parent
OUT=HERE/'fabrication'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dims(s):
    b=s.BoundingBox()
    return [b.xlen,b.ylen,b.zlen],[b.xmin,b.ymin,b.zmin]

def run():
    files=['params.py','frame.py','motion.py','manufacture.py','motion-fabrication.csv',
           'review/frame-fabrication.csv']
    source={n:sha(HERE/n) for n in files}
    frame={n:s for n,s,_ in frame_parts()}
    moving={}
    for hot in (False,True):
        for n,s,_ in motion_parts(hot):moving.setdefault(n,s)
    selected=[]
    with (HERE/'review/frame-fabrication.csv').open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            if row['category'] in ('Flat plate','One-piece bearing angle','Tension strap','Brace spacer'):
                selected.append((row['id'],frame[row['id']],row['material'],row['category'],row['qualification']))
    with (HERE/'motion-fabrication.csv').open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            if row['category'].startswith('CUSTOM_'):
                if row['id'] not in moving:raise ValueError('Manifest lacks actual solid: '+row['id'])
                selected.append((row['id'],moving[row['id']],row['material'],'Motion custom',row['notes']))
    assert len({n for n,*_ in selected})==len(selected),'Duplicate custom part IDs'
    for directory in ('custom-step','plate-section-reference'): (OUT/directory).mkdir(parents=True,exist_ok=True)
    rows=[];fail=[]
    for n,s,material,category,note in selected:
        size,origin=dims(s)
        local=s.translate(tuple(-v for v in origin))
        path=OUT/'custom-step'/f'{n}.step'
        cq.exporters.export(local,str(path))
        back=cq.importers.importStep(str(path)).val()
        volume_error=abs(back.Volume()-local.Volume())
        back_size,back_origin=dims(back)
        bbox_error=max(abs(a-b) for a,b in zip(back_size+back_origin,size+[0.,0.,0.]))
        valid=back.isValid() and len(back.Solids())==len(local.Solids()) and volume_error<max(.01,local.Volume()*1e-7) and bbox_error<1e-5
        if not valid:fail.append(n)
        section='';section_sha='';section_transform=None
        if category in ('Flat plate','Tension strap','Brace spacer'):
            axis=min(range(3),key=lambda i:size[i]);sheet=local
            if axis==0:sheet=sheet.rotate((0,0,0),(0,1,0),90)
            elif axis==1:sheet=sheet.rotate((0,0,0),(1,0,0),90)
            bs=sheet.BoundingBox();sheet=sheet.translate((-bs.xmin,-bs.ymin,-bs.zmin))
            profile=cq.Workplane('XY').newObject([sheet]).section(size[axis]/2)
            dxf=OUT/'plate-section-reference'/f'{n}_MIDSECTION_REFERENCE.dxf'
            cq.exporters.export(profile,str(dxf))
            drawing=ezdxf.readfile(dxf);drawing.header['$INSUNITS']=4;drawing.saveas(dxf)
            assert len(drawing.modelspace())>0,n
            section=dxf.relative_to(HERE).as_posix()
            section_sha=sha(dxf)
            transforms={
                0:[[0,0,1,0],[0,1,0,0],[-1,0,0,size[0]],[0,0,0,1]],
                1:[[1,0,0,0],[0,0,-1,size[2]],[0,1,0,0],[0,0,0,1]],
                2:[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]}
            # Preserve the actual CAD bounding-box normalization, including
            # numerical edge tolerances, rather than an assumed ideal shift.
            for i,value in enumerate((-bs.xmin,-bs.ymin,-bs.zmin)):transforms[axis][i][3]=value
            section_transform={'STEP_local_to_section_frame_4x4':transforms[axis],
                'section_frame_Z_mm':size[axis]/2,'thickness_axis_in_STEP':'XYZ'[axis],
                'DXF_axes':'DXF X/Y are the first two coordinates after this transform; section Z is discarded. Millimetres.'}
        rows.append({'id':n,'category':category,'material':material,
            'step':path.relative_to(HERE).as_posix(),'step_sha256':sha(path),
            'world_origin_mm':origin,'world_aligned_size_mm':size,'volume_mm3':local.Volume(),
            'step_roundtrip_valid':valid,'step_roundtrip_volume_error_mm3':volume_error,
            'step_roundtrip_bbox_error_mm':bbox_error,
            'midsection_reference_dxf':section,
            'midsection_reference_sha256':section_sha,'midsection_reference_transform':section_transform,
            'qualification':note})
        print('CUSTOM',n,flush=True)
    with (OUT/'custom-part-index.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    current=source=={n:sha(HERE/n) for n in files}
    report={'revision':P.REVISION,'source_sha256':source,'source_unchanged':current,
        'passed':current and not fail,'failed_parts':fail,'custom_step_count':len(rows),
        'plate_section_reference_count':sum(bool(r['midsection_reference_dxf']) for r in rows),
        'parts':rows,'fabrication_release':False,
        'scope':'Actual custom frame and motion solids exported individually, translated from their recorded world origins; every STEP is reimported and checked for validity, solid count and volume. Plate DXFs are labeled middle-thickness sections only. They do not describe counterbores, countersinks, edge holes, taps or bends; use the STEP and manufacturing notes. Owned inventory credit and vendor-interface release remain separate.'}
    (HERE/'review/custom-parts-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (OUT/'README.md').write_text('''# XR2 nominal custom machining pack

The custom STEP files contain the actual designed frame and motion solids.
Each part is translated so its world-aligned minimum corner is at 0,0,0;
the index records the original assembly origin. Right and left parts remain
separate. Units are millimetres. Reimport checks are in the review report.

Use the matching frame/motion manifests for material, thread and interface
notes. Nominal thread cylinders are not tap-drill diameters. Preserve the
billet gantry corners and six clevises as integral parts. Do not substitute
touching plates for one-piece bearing angles. Allow facing and saw cleanup
outside the listed finished blank dimensions.

The explicitly labeled MIDSECTION_REFERENCE DXFs are cross-sections for
checking planar plate profiles. They are not complete machining drawings:
counterbores, countersinks, edge holes, taps and bend information live in
the STEP/manifests. Bed, pan, shields and ATC have their own fabrication
files; the custom-part index does not replace those schedules.

This is a nominal engineering pack for CAM preparation. Do not post or
run a toolpath until the delivered hardware interfaces, stock/alloy,
thread depths and physical acceptance items in the release register close.
''',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'custom_step_count':len(rows),'reference_dxf_count':report['plate_section_reference_count']},indent=2),flush=True)
    return 0 if report['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
