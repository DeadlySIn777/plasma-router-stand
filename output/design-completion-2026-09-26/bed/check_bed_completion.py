from pathlib import Path
import sys,json,os,hashlib
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
sys.path.insert(0,str(SOURCE))
from build_revh import build_model,stored_model
from cad_helpers import validate,bbox
import bed_completion as h

def main():
    m,details=build_model();extra=details["bed_completion"]
    print('Built',len(m.parts),flush=True)
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    report={'scope':'Full integrated Rev H router and stored assemblies','details':extra,'source_sha256':before}
    for name,model in [('router',m),('stored',stored_model(m))]:
        v=validate(model)
        report[name]={'parts':v['part_count'],'clashes':v['unresolved_intersections'],'documented_intersections':v['documented_intersections']}
        print(name,json.dumps({'parts':v['part_count'],'clashes':v['unresolved_intersections']}),flush=True)
    report['sources_unchanged']=before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    report['pass']=report['sources_unchanged'] and all(not report[k]['clashes'] for k in ('router','stored'))
    Path(__file__).with_name('bed-completion-check.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if report['pass'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
