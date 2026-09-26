"""Render the actual unbored head geometry for the Rev I review document."""
from pathlib import Path
import hashlib,json,os,sys

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
CAD=ROOT/'output/release-review/RevI-CAD'
sys.path.insert(0,str(SOURCE))


def main():
    from motion_finish import make_head
    from build_revi import write_mesh
    from render_revi import render
    paths=[SOURCE/n for n in ('motion_finish.py','cad_helpers.py','build_revi.py','build_revh.py','render_revi.py')]+[Path(__file__).resolve(),ROOT/'render_cad.py']
    before={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    head,details=make_head()
    # Head's local Y is up; rotate the complete geometry into the assembly's
    # vertical Z convention. No component positions or fabrication features change.
    for part in head.parts:part.shape=part.shape.rotate((0,0,0),(1,0,0),90)
    write_mesh(head,'RevI_HEAD_DETAIL')
    preview=render('RevI_HEAD_DETAIL',view=(-1.05,-1.8,1.1),size=(1400,1400))
    after={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    image=CAD/'previews'/preview['file']
    result={'source_sha256':after,'sources_unchanged':before==after,'head_component_count':len(head.parts),
            'actual_torch_present':False,'preview':preview,'image_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
            'scope':'Actual CAD render only, not a force, thermal, supplier-fit or operating-machine qualification.'}
    (Path(__file__).resolve().parent/'head-preview-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('HEAD_PREVIEW',len(head.parts),'parts',before==after,flush=True)
    return 0 if before==after else 2


if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
