"""Check nominal top-slot nut evacuation, not hand/pickup access or tray transfer."""
from pathlib import Path
import hashlib,json,sys,os
SOURCE=Path(__file__).resolve().parents[1]/'release-review'/'RevE-ENGINEERING'
sys.path.insert(0,str(SOURCE))
from build_revg import build_model,store_router_tool
from cad_helpers import bbox
from sweep_checks import translation_segment
import bed_cassettes as bed

def main():
    before={n:hashlib.sha256((SOURCE/n).read_bytes()).hexdigest() for n in ('bed_cassettes.py','build_revg.py','sweep_checks.py')}
    m,_=build_model();m=store_router_tool(m)
    for p in m.parts:
        if bed._PLACEMENTS.get(p.id,('',))[0] in ('spoil','spoil_bolt'):
            p.shape=bed.transformed_to_storage(p)
    results=[]
    for p in m.parts:
        rec=bed._PLACEMENTS.get(p.id)
        if not rec or rec[0]!='spoil_nut':continue
        index=rec[1];panel=index//4;row=panel//2
        fixed={q.id:q.shape for q in m.parts if q.id!=p.id}
        delta=(0,bed.PANEL_Y[row]-5-rec[2][1],0)
        a=translation_segment({p.id:p.shape},fixed,delta)
        gap=p.shape.translate(delta)
        b=translation_segment({p.id:gap},fixed,(0,0,20))
        results.append({'id':p.id,'slide_to_open_end':a,'lift20_through_gap':b})
        p.shape=bed.transformed_to_storage(p)
        print(p.id,a['status'],b['status'],flush=True)
    after={n:hashlib.sha256((SOURCE/n).read_bytes()).hexdigest() for n in before}
    report={'scope':__doc__,'sources_sha256':before,'sources_unchanged':before==after,'nut_count':len(results),
        'assumptions':['All spoilboards and their screws have already been removed and stored.','Each8mm square nut slides forward along its actual nominal open slot and lifts through a10mm panel joint.','Magnetic pickup, fingers, tool access, real profile tolerance, and travel from the gap to its paired screw in the tray remain unverified.','The final model stores nuts threaded onto removed screws; none is assumed captive in a vertical panel.'],
        'results':results,'pass':before==after and all(r[k]['status']=='CLEAR' for r in results for k in ('slide_to_open_end','lift20_through_gap'))}
    Path(__file__).with_name('nut-evacuation-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',report['pass'],flush=True)
    return 0 if report['pass'] else 2
if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
