"""Export exact current parts and actual-solid section DXFs, never stale sketch data."""
from pathlib import Path
import csv,json,sys,os,hashlib,warnings
import cadquery as cq
import mechanism as m
OUT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(parts,path,context=False):
 assembly=cq.Assembly(name=path.stem)
 if context:
  for p in m.context():assembly.add(p.shape,name='BASE_'+p.name,color=cq.Color(*((.75,.25,.62) if p.material=='allocation only' else (.58,.60,.62))))
 for p in parts:assembly.add(p.shape,name=p.id,color=cq.Color(*p.color))
 with warnings.catch_warnings():warnings.simplefilter('ignore');assembly.save(str(path))

def main():
 (OUT/'parts').mkdir(exist_ok=True);(OUT/'flat').mkdir(exist_ok=True)
 inventory=[]
 for name,args in [('deployed',(0,164,False,False)),('parked',(200,0,False,False))]:
  parts=m.build(*args)
  save(parts,OUT/f'{name}-mechanism.step');save(parts,OUT/f'{name}-machine.step',True)
  print('exported',name,len(parts),flush=True)
  if name!='parked':continue
  for p in parts:
   local=p.shape
   if hasattr(p,'frame'):local=local.moved(p.frame.inverse)
   b=local.BoundingBox();local=local.translate((-b.xmin,-b.ymin,-b.zmin));b=local.BoundingBox()
   dest=OUT/'parts'/f'{p.id}.step';cq.exporters.export(local,str(dest))
   flat=False;levels=[]
   if hasattr(p,'frame') and abs(b.zlen-p.thickness)<.01:
    # Every planar height section is derived from finalsolid afterallbooleans.
    zvals=sorted(set(round(v.Center().z,5) for v in local.Vertices()))
    if len(zvals)<2:zvals=[0.,b.zlen]
    samples=sorted(set([.01,b.zlen-.01]+[(a+c)/2 for a,c in zip(zvals,zvals[1:]) if c-a>.03]))
    doc=cq.exporters.DxfDocument()
    for z in samples:
     layer='SECTION_Z'+f'{z:.3f}'.replace('.','p');doc.add_layer(layer,color=7)
     section=cq.Workplane('XY').add(local).section(z)
     if section.vals():doc.add_shape(section,layer=layer);levels.append(z)
    doc.document.saveas(str(OUT/'flat'/f'{p.id}.dxf'));flat=True
   density=7.85e-6 if 'steel' in p.material.lower() or '301' in p.material else(8.8e-6 if 'bronze' in p.material.lower() else(1.42e-6 if 'POM' in p.material else 2.7e-6))
   purchased=p.group.endswith('fasteners') or any(k in p.material for k in ('purchased','Delta','Panasonic')) or p.id.startswith(('MGNR','MGN12'))
   inventory.append({'id':p.id,'group':p.group,'material':p.material,'purchased_reference':purchased,'bounds_mm':m.bbox(p.shape),'local_stock_bounds_mm':[b.xlen,b.ylen,b.zlen],'volume_mm3':p.shape.Volume(),'fabricated_mass_estimate_kg':None if purchased else p.shape.Volume()*density,'local_step':'parts/'+p.id+'.step','section_dxf':'flat/'+p.id+'.dxf' if flat else None,'section_levels_mm':levels,'note':p.note})
  # These two directories contain only this generator's named exports. Remove
  # obsolete generated files after resolving each target inside its exact folder.
  for folder,extension,expected in [('parts','.step',{r['id']+'.step' for r in inventory}),('flat','.dxf',{r['id']+'.dxf' for r in inventory if r['section_dxf']})]:
   directory=(OUT/folder).resolve()
   for old in directory.glob('*'+extension):
    target=old.resolve()
    if target.parent!=directory:raise RuntimeError('Refusing out-of-folder generated-file cleanup')
    if old.name not in expected:old.unlink()
  (OUT/'parts-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
  with (OUT/'stock-and-operations.csv').open('w',newline='',encoding='utf-8') as f:
   w=csv.writer(f);w.writerow(['id','material','reference_only','stock_x_mm','stock_y_mm','stock_z_mm','local_step','section_dxf','operations_or_limit'])
   for r in inventory:w.writerow([r['id'],r['material'],r['purchased_reference'],*r['local_stock_bounds_mm'],r['local_step'],r['section_dxf'] or'',r['note']])
  info={'mechanism_parts_each_state':len(parts),'context_parts':len(m.context()),'fabricated_material_mass_estimate_kg':sum(r['fabricated_mass_estimate_kg'] or 0 for r in inventory),'section_dxf_count':sum(bool(r['section_dxf']) for r in inventory),'warning':'Purchased solid envelopes are not mass specifications. DXF layers are actual-solid sections at labeledZ, not a single-depth cut program. Weldments without a planar blank receive3D STEP and operations only.'}
  (OUT/'export-summary.json').write_text(json.dumps(info,indent=2),encoding='utf-8');print(info,flush=True)
if __name__=='__main__':
 main();sys.stdout.flush();os._exit(0)
