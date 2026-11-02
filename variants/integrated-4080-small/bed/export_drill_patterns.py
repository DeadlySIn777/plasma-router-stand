"""Export the source-bound HDPE round-drill CSV as millimetre DXFs."""
from pathlib import Path
import csv,hashlib,json
import ezdxf

HERE=Path(__file__).resolve().parent;OUT=HERE/'output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
 source=OUT/'HDPE-DRILL.csv';proof=OUT/'bed-local-check.json'
 local=json.loads(proof.read_text(encoding='utf-8'))
 assert local['passed'] and local['source_consistent_during_build']
 root=HERE.parents[2]
 for name,h in local['source_sha256'].items():assert sha(root/name)==h,name
 rows=list(csv.DictReader(source.open(newline='',encoding='utf-8')))
 paths=[Path(__file__),source,proof];start={p.name:sha(p)for p in paths}
 records=[]
 for layer in(1,2):
  part=f'FULL_HDPE_{layer}';pattern=[r for r in rows if r['part']==part]
  assert len(pattern)==80
  doc=ezdxf.new('R2010',units=ezdxf.units.MM);space=doc.modelspace()
  for name,color in(('OUTLINE',3),('DRILL_13P2',1),('DRILL_22',5)):doc.layers.new(name,dxfattribs={'color':color})
  space.add_lwpolyline([(0,0),(1000,0),(1000,1219.2),(0,1219.2)],close=True,dxfattribs={'layer':'OUTLINE'})
  expected=[]
  for r in pattern:
   x,y,d=map(float,(r['X_from_left_mm'],r['Y_from_front_mm'],r['diameter_mm']))
   assert d/2<x<1000-d/2 and d/2<y<1219.2-d/2
   expected.append((x,y,d/2))
   space.add_circle((x,y),d/2,dxfattribs={'layer':'DRILL_13P2'if d==13.2 else'DRILL_22'})
  assert sum(r[2]==6.6 for r in expected)==1
  path=OUT/(part+'_ROUND_DRILL.dxf');doc.saveas(path)
  back=ezdxf.readfile(path);audit=back.audit()
  got=[(e.dxf.center.x,e.dxf.center.y,e.dxf.radius)for e in back.modelspace().query('CIRCLE')]
  assert back.units==ezdxf.units.MM and not audit.errors and sorted(got)==sorted(expected)
  outline=list(back.modelspace().query('LWPOLYLINE'))
  assert len(outline)==1 and outline[0].closed and len(got)==80
  records.append(dict(part=part,file=path.name,sha256=sha(path),readback_valid=True,
    outline_mm=[1000,1219.2],drill_count=80,datum_count=1,ordinary_clearance_count=79))
 consistent=start=={p.name:sha(p)for p in paths}
 result=dict(source_sha256=start,source_consistent=consistent,passed=consistent,exports=records,
  units='mm',origin='Each HDPE sheet lower-left; globalX75/Y−39.6. Xright,Yrear.',
  operations='Circular through drilling only. No pockets, slots, countersinks or counterbores in HDPE.',
  fabrication_release=False)
 (OUT/'HDPE-drill-dxf-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=consistent,exports=len(records),holes_each=80)))
 return 0 if consistent else 1

if __name__=='__main__':raise SystemExit(run())
