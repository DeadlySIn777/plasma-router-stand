"""Selected complete model bare temporary C-frame transfer; hardware and hand paths excluded."""
from pathlib import Path
import sys,os,json,hashlib
from check_reinforced_paths import SOURCE,ROOT,transform,bounds_speed,swept_box,continuous_segment,build_model,clone_model,store_router_tool,bbox,h,bc
OUT=Path(__file__).with_name('temporary-fixture-transfer.json')

def hashes():
    paths=list(SOURCE.glob('*.py'))+[Path(__file__),Path(__file__).with_name('check_reinforced_paths.py'),ROOT/'output/cad-repair-2026-09-25/check_spoil_transfer.py']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def main():
    before=hashes();router,details=build_model();temporary=store_router_tool(router);h.prepare_beam_handling_model(temporary)
    for p in temporary.parts:
        kind,index,*_=bc._PLACEMENTS.get(p.id,('',-1))
        if kind in ('spoil','spoil_bolt','clamp','panel') or (kind=='beam_bolt' and index//2==0):p.shape=bc.transformed_to_storage(p)
        if kind=='beam' and index==0:
            datum=bc._PLACEMENTS[p.id][2]
            p.shape=p.shape.translate(tuple(-v for v in datum)).rotate((0,0,0),(1,0,0),90).translate((113,517.9,920.8))
    omitted={p.id for p in temporary.parts if p.id.startswith(('H_TEMP_GATE_','H_TEMP_LOCATOR_','H_TEMP_STORAGE_NUT_'))}
    report={'scope':__doc__,'builder':'build_revi.build_model' if '--integrated' in sys.argv else 'build_revh plus structure_finish','source_sha256':before,'model_parts':len(temporary.parts),'paths':[],
        'preconditions':['All boards/panels stored and their rack retainers fitted. Beam1 rests on beam2. Both front seats remain installed.',
        'Remove each front gate, both gate screws, locator bolt/washer/spacer and storage nut before moving the bare C frame. These small parts and hand paths are excluded.',
        'Move C frame1 then2 by this route; other C body remains a collision obstacle. After both bodies are in place, install gates and locator hardware by the separately documented sequence.']}
    def save():OUT.write_text(json.dumps(report,indent=2)+'\n')
    for side,x in ((1,350),(2,780)):
        ident='H_TEMP_BOX_'+str(side);part=temporary.find(ident);shape=part.shape;y=900+130*(side-1)
        ops=[('T',(0,0,620-436.096)),('T',(55,0,0)),('T',(0,68-y,0)),
             ('R',(200,68,620),(201,68,620),90),('T',(0,0,380)),
             ('R',(200,68,1000),(200,68,1001),90),('T',(x-200,0,0)),
             ('T',(0,480,0)),('T',(0,0,-137)),('T',(0,-120,0))]
        fixed={p.id:p.shape for p in temporary.parts if p.id not in omitted and p.id!=ident}
        rec={'name':ident,'segments':[]}
        for i,op in enumerate(ops):
            speed,curve=bounds_speed(shape,op)
            r=continuous_segment(lambda t,s=shape,o=op:transform(s,o,t),fixed,speed,curve)
            swept=swept_box(shape,op);r['swept_bounding_box_mm']=swept
            r['within_frame_footprint']=swept[0]>=-1e-6 and swept[1]>=-1e-6 and swept[3]<=1150+1e-6 and swept[4]<=1450+1e-6
            rec['segments'].append({'operation':op,'result':r});shape=transform(shape,op)
            print(ident,i+1,r['status'],r.get('failures',[])[:4],flush=True)
        rec['final_bounds_delta_mm']=max(abs(a-b) for a,b in zip(bbox(shape),bbox(h._TEMPORARY[ident])))
        rec['pass']=rec['final_bounds_delta_mm']<1e-5 and all(s['result']['status']=='CLEAR' and s['result']['within_frame_footprint'] for s in rec['segments'])
        report['paths'].append(rec);part.shape=h._TEMPORARY[ident];save()
    report['sources_unchanged']=before==hashes();report['pass']=report['sources_unchanged'] and all(p['pass'] for p in report['paths']);save();print('PASS',report['pass'],flush=True)
    return 0 if report['pass'] else 2
if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
