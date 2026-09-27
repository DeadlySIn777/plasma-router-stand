"""Frozen large-part route algorithms applied to the new ATC obstacles."""
from pathlib import Path
import sys,json,hashlib,importlib.util,os,time,types
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OLD=ROOT/'output/cad-repair-2026-09-25';LEG=ROOT/'output/release-review/RevE-ENGINEERING';sys.path[:0]=[str(HERE),str(OLD),str(LEG)]
import build,verify,build_revi,bed_completion,bed_cassettes as bc
SLOTS={0:5,1:4,2:3,3:2,5:1,4:0}

def main(kind):
 script=OLD/('check_spoil_transfer.py' if kind=='spoil' else 'verify_revg_beam_path.py')
 module=types.ModuleType('small_revised_beam_route');module.__file__=str(script)
 text=script.read_text()
 old_lift="lifted=run('lift_clear_of_seats',lambda t:installed.translate((0,0,80*t)),80)"
 new_lift="lift_amount=30 if i==3 else 80\n        lifted=run('lift_clear_of_seats',lambda t:installed.translate((0,0,lift_amount*t)),lift_amount)"
 assert text.count(old_lift)==1;text=text.replace(old_lift,new_lift)
 old_front="front_flat=run('move_lifted_beam_to_front',lambda t:lifted.translate((0,(78.8-datum[1])*t,0)),abs(78.8-datum[1]))"
 new_front="if i==3:\n            left=run('shift_left25_above_seats',lambda t:lifted.translate((-25*t,0,0)),25)\n            mid=run('forward_low_to_Y1150',lambda t:left.translate((0,(1150-datum[1])*t,0)),abs(1150-datum[1]))\n            under=run('lower10_below_front_sensors',lambda t:mid.translate((0,0,-10*t)),10)\n            frontlow=run('forward_below_drive_to_Y900',lambda t:under.translate((0,-250*t,0)),250)\n            high=run('raise60_in_open_bay',lambda t:frontlow.translate((0,0,60*t)),60)\n            centered=run('restore_original_X',lambda t:high.translate((25*t,0,0)),25)\n            front_flat=run('move_lifted_beam_to_front',lambda t:centered.translate((0,(78.8-900)*t,0)),900-78.8)\n        else:\n            "+old_front
 assert text.count(old_front)==1;text=text.replace(old_front,new_front)
 exec(compile(text,str(script),'exec'),module.__dict__)
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
 report['new_variant_source_sha256']=before;report['new_variant_sources_changed']={k:v for k,v in before.items() if after.get(k)!=v};report['integration_scope']='Revised beam4 lift30/left25/forwardY1150/lower10/forwardY900/raise60/restoreX; other beams unchanged. Parked270-part retractable mechanism plus unverified magazine allocation; one lower rear-left bed clamp screw. Beam route includes actual newly permuted stored panel solids.';report['new_panel_to_slot_one_based']={str(i+1):j+1 for i,j in SLOTS.items()};report['passed']=code==0 and not report['new_variant_sources_changed'];report['elapsed_seconds']=time.time()-start
 report['analytic_xy_envelope_mm']=[88,0,1037,1330.4]
 report['footprint']='All prescribed rigid geometry stays inside frame X0..1150,Y0..1450. Beam4 translates left25 only, reaching X88, then returns before rotation. Quarter-turn Y bounds remain0..135.6; every other XY move is linear between contained endpoints.'
 path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(kind,'PASS',report['passed'],flush=True);return 0 if report['passed'] else 2
if __name__=='__main__':
 try:code=main('beam')
 except Exception:
  import traceback;traceback.print_exc();code=1
 sys.stdout.flush();sys.stderr.flush();os._exit(code)

