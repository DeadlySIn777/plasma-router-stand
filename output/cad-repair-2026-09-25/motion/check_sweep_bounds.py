"""Small geometry checks for the conservative translation/rotation helper."""
from pathlib import Path
import json,math,os,sys,traceback
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'release-review'/'RevE-ENGINEERING'))
from cad_helpers import box,pipe,cyl,intersection_volume
from sweep_checks import translation_segment,rotation_segment

def main():
    out={}
    moving={'block':box(1,1,1)}
    out['clear_translation']=translation_segment(moving,{'wall':box(1,1,1).translate((5,3,0))},(10,0,0))
    assert out['clear_translation']['status']=='CLEAR'
    out['intermediate_translation_collision']=translation_segment(moving,{'wall':box(.2,.8,.8).translate((5.2,.1,.1))},(10,0,0))
    assert out['intermediate_translation_collision']['status']=='CANDIDATE_NOT_PROVEN'
    assert out['intermediate_translation_collision']['candidates'][0]['exact_probe_interferences']
    # A translating annulus never strikes a concentric thin rod, but its AABB
    # includes the rod. It must remain a candidate, not a claimed collision.
    out['conservative_false_positive']=translation_segment({'ring':pipe(1,10,8)},
        {'rod':cyl(2,11)},(0,0,10))
    assert out['conservative_false_positive']['status']=='CANDIDATE_NOT_PROVEN'
    assert not out['conservative_false_positive']['candidates'][0]['exact_probe_interferences']
    # This obstacle lies at22.5 degrees, between the0/45/90 exact probes of a
    # deliberately coarse cell. The inflated mid-angle bound must catch it.
    rod=box(1,.1,1).translate((5,-.05,0))
    a=math.radians(22.5)
    obstacle=box(.1,.1,.8).translate((5.5*math.cos(a)-.05,5.5*math.sin(a)-.05,.1))
    assert intersection_volume(rod.rotate((0,0,0),(0,0,1),22.5),obstacle)>0
    out['between_probe_rotation_collision']=rotation_segment({'arm':rod},{'obstacle':obstacle},
        (0,0,0),'Z',0,90,max_step_deg=90)
    r=out['between_probe_rotation_collision']
    assert r['status']=='CANDIDATE_NOT_PROVEN' and not r['candidates'][0]['exact_probe_interferences']
    out['clear_rotation']=rotation_segment({'arm':rod},{'overhead':box(20,20,1).translate((-10,-10,5))},
        (0,0,0),'Z',0,90,max_step_deg=5)
    assert out['clear_rotation']['status']=='CLEAR'
    report={'result':'PASS','checks':out}
    (ROOT/'sweep-helper-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Sweep helper:5 geometry cases PASS',flush=True)
    return 0

if __name__=='__main__':
    try:code=main()
    except Exception:traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
