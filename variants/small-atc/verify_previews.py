"""Bind already-rendered, visually reviewed CAD previews to their inputs."""
from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/'output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[Path(__file__),Path(__file__).with_name('build_small_atc.py'),Path(__file__).with_name('render_small_atc.py'),ROOT/'render_cad.py',
       ROOT/'variants/common/location/locator_dock.py']
fit=json.loads((OUT/'fit-report.json').read_text())
images=[]
for name,size in [('SMALL_ATC_CONTEXT',(1600,1400)),('SMALL_ATC_DOCK',(1600,950))]:
    p=OUT/(name+'.png');im=Image.open(p);im.verify();actual=Image.open(p).size
    images.append({'file':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'size_px':list(actual),'expected_size_matches':actual==size,
                   'mesh_file':str((OUT/(name+'.npz')).relative_to(ROOT)).replace('\\','/'),'mesh_sha256':sha(OUT/(name+'.npz'))})
sources={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in files}
report={'scope':'Readable rendered CAD previews and exact input/output association only; not machine fit, load or motion approval.',
        'visual_review':'Both current PNGs reviewed by root: readable, clean, no clipping; magenta cage explicitly labeled unverified allocation.',
        'source_sha256':sources,'fit_report_sha256':sha(OUT/'fit-report.json'),'images':images,
        'build_source_matches_fit':fit['source_sha256']['variants/small-atc/build_small_atc.py']==sources['variants/small-atc/build_small_atc.py']}
report['passed']=report['build_source_matches_fit'] and all(i['expected_size_matches'] for i in images)
(OUT/'preview-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'file':str(OUT/'preview-verification.json')}))
