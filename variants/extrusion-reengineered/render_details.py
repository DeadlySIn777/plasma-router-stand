"""Render current CAD service/ATC details, never illustrative substitutes."""
from pathlib import Path
import hashlib,json,os,sys
import params as P
from preview import legacy

HERE=Path(__file__).resolve().parent

def run():
    from bed_service import service_scene
    from atc import atc_parts,interface_metadata
    out=HERE/'review'
    names=('params.py','frame.py','bed.py','motion.py','shields.py','atc.py',
           'bed_service.py','render_details.py','preview.py')
    source={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in names}
    reservoir=[p for p in service_scene('hatch_open') if p[0].startswith(
        ('WATER_RED20GAL','WATER_REMOVABLE_LID','RECEIVER_HATCH','SH_RECEIVER'))]
    scenes={'receiver-service':reservoir,
            'atc-deployed':atc_parts(False,deployed=True)}
    for n,parts in scenes.items():
        assert parts,n
        im=legacy.render(parts,back=False,w=1450,h=1050)
        im.save(out/f'{n}.png')
        print('Rendered',n,len(parts),'CAD components',flush=True)
    from bed import water_hatch_parts
    hatch_top=max(s.BoundingBox().zmax for _,s,_ in water_hatch_parts(opened=True))
    current=source=={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in names}
    r={'revision':P.REVISION,'rendered':current,'source_sha256':source,
       'receiver_hatch_open_max_z_mm':hatch_top,'ATC_metadata':interface_metadata(),
       'views':{n:{'parts':len(parts),'file':f'review/{n}.png',
             'sha256':hashlib.sha256((out/f'{n}.png').read_bytes()).hexdigest()} for n,parts in scenes.items()},
       'scope':'Actual generated service and ATC mechanism solids. Service detail deliberately omits surrounding machine parts, which remain in the service collision check. Manufacturer magazine internals, tool setup and operational qualification remain governed by the ATC report.'}
    (out/'detail-views.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    return 0 if current else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
