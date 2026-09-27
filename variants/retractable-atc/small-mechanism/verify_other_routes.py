"""Frozen large-part route algorithms applied to the new ATC obstacles."""
from pathlib import Path
import sys,json,hashlib,importlib.util,os,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OLD=ROOT/'output/cad-repair-2026-09-25';LEG=ROOT/'output/release-review/RevE-ENGINEERING';sys.path[:0]=[str(HERE),str(OLD),str(LEG)]
import build,verify,build_revi,bed_completion,bed_cassettes as bc
SLOTS={0:5,1:4,2:3,3:2,5:1,4:0}

def main(kind):
 script=OLD/('check_spoil_transfer.py' if kind=='spoil' else 'verify_revg_beam_path.py')
 spec=importlib.util.spec_from_file_location('small_'+kind+'_route',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 sources=[Path(__file__),HERE/'build.py',HERE/'lock.py',HERE/'sensors.py',HERE/'verify.py',HERE/'verify_panels.py',script,OLD/'check_spoil_transfer.py']+list(LEG.glob('*.py'))
 hashes=lambda:{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
 before=hashes();start=time.time();original=bc.transformed_to_storage
 def storage(p):
  shape=original(p);record=bc._PLACEMENTS.get(p.id,('',-1))
  if record[0]=='panel':shape=shape.translate((0,bc.PANEL_STORE_Y[SLOTS[record[1]]]-bc.PANEL_STORE_Y[record[1]],0))
  return shape
 def builder(*args,**kwargs):
  m,meta=build_revi.build_model(*args,**kwargs);verify.apply_baseline_substitution(m)
  (bed_completion.prepare_handling_model if kind=='spoil' else bed_completion.prepare_beam_handling_model)(m)
  atc,_=build.build(200,False,True);m.parts.extend(atc.parts);return m,meta
 module.build_model=builder;module.hashes=hashes
 outdir=HERE/'routes'/kind;outdir.mkdir(parents=True,exist_ok=True);module.__file__=str(outdir/script.name)
 if kind=='beam':bc.transformed_to_storage=storage
 try:code=module.main()
 finally:bc.transformed_to_storage=original
 path=outdir/('spoil-transfer-check.json' if kind=='spoil' else 'beam-path-check.json');report=json.loads(path.read_text());after=hashes()
 report['new_variant_source_sha256']=before;report['new_variant_sources_changed']={k:v for k,v in before.items() if after.get(k)!=v};report['integration_scope']='Parked270-part retractable mechanism plus unverified magazine allocation; one lower rear-left bed clamp screw. Beam route includes actual newly permuted stored panel solids.';report['new_panel_to_slot_one_based']={str(i+1):j+1 for i,j in SLOTS.items()};report['passed']=code==0 and not report['new_variant_sources_changed'];report['elapsed_seconds']=time.time()-start
 path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(kind,'PASS',report['passed'],flush=True);return 0 if report['passed'] else 2
if __name__=='__main__':
 try:code=main(sys.argv[1])
 except Exception:
  import traceback;traceback.print_exc();code=1
 sys.stdout.flush();sys.stderr.flush();os._exit(code)

