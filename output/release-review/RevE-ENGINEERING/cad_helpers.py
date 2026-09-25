"""Nominal solid and fabrication-drawing helpers, millimeters."""
from dataclasses import dataclass, field
from pathlib import Path
import csv, hashlib, json, math
import cadquery as cq
import ezdxf
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

STEEL=(.25,.31,.34); ALU=(.70,.73,.75); WATER=(.40,.58,.62)
PURCHASED=(.76,.49,.19); HARDWARE=(.49,.51,.54)

def box(dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).val()

def cyl(diameter,length):
    return cq.Workplane('XY').circle(diameter/2).extrude(length).val()

def bbox(s):
    b=s.BoundingBox(); return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def place(s,origin=(0,0,0),u=(1,0,0),v=(0,1,0)):
    u=cq.Vector(*u);v=cq.Vector(*v);n=u.cross(v)
    assert abs(u.Length-1)<1e-7 and abs(v.Length-1)<1e-7 and abs(n.Length-1)<1e-7
    return s.moved(cq.Plane(origin=tuple(origin),xDir=u,normal=n).location)

def plate(outline,thickness,holes=(),slots=(),internal=()):
    s=cq.Workplane('XY').polyline(outline).close().extrude(thickness).val()
    tools=[]
    for x,y,d in holes: tools.append(cyl(d,thickness+2).translate((x,y,-1)))
    for x,y,length,width,angle in slots:
        tools.append(cq.Workplane('XY').center(x,y).slot2D(length,width,angle).extrude(thickness+2).translate((0,0,-1)).val())
    for wire in internal:
        tools.append(cq.Workplane('XY').polyline(wire).close().extrude(thickness+2).translate((0,0,-1)).val())
    if tools:s=s.cut(cq.Compound.makeCompound(tools)).clean()
    return s

def rect(w,h): return [(0,0),(w,0),(w,h),(0,h)]

def tube(length,side=50.8,wall=3.048):
    # Local longitudinal axis X; nominal square corners are explicitly documented.
    return box(length,side,side).cut(box(length+2,side-2*wall,side-2*wall).translate((-1,wall,wall))).clean()

def pipe(length,od=48.3,id=40.9):return cyl(od,length).cut(cyl(id,length)).clean()

def intersection_volume(a,b):
    """Accept a completed empty Boolean; never suppress a failed kernel operation."""
    try:return a.intersect(b).Volume()
    except ValueError as error:
        if 'Null TopoDS_Shape' not in str(error):raise
        operation=BRepAlgoAPI_Common(a.wrapped,b.wrapped);operation.Build()
        if not operation.IsDone():raise RuntimeError('Intersection Boolean did not complete') from error
        result=operation.Shape()
        return 0.0 if result.IsNull() else cq.Shape.cast(result).Volume()

@dataclass
class Component:
    id:str
    part_number:str
    shape:cq.Shape
    local:cq.Shape
    group:str
    material:str
    notes:list=field(default_factory=list)
    flat:dict|None=None
    color:tuple=STEEL
    release:str='ENGINEERING DEFINITION - REVIEW BEFORE FABRICATION'
    purchased:bool=False
    length:float|None=None

class Model:
    def __init__(self):self.parts=[];self.allowed_intersections={};self.holds=[]
    def add(self,id,local,origin=(0,0,0),u=(1,0,0),v=(0,1,0),*,pn=None,group='frame',material='A36 steel',notes=(),flat=None,color=STEEL,purchased=False,release=None,length=None):
        p=Component(id,pn or id,place(local,origin,u,v),local,group,material,list(notes),flat,color,
                    release or ('PURCHASED ENVELOPE - VERIFY INTERFACE' if purchased else 'ENGINEERING DEFINITION - REVIEW BEFORE FABRICATION'),purchased,length)
        self.parts.append(p);return p
    def add_shape(self,id,shape,**kwargs):return self.add(id,shape,**kwargs)
    def add_plate(self,id,w,h,t,holes=(),slots=(),internal=(),outline=None,**kwargs):
        outline=outline or rect(w,h)
        f={'outline':outline,'thickness_mm':t,'holes':list(holes),'slots':list(slots),'internal':list(internal)}
        return self.add(id,plate(outline,t,holes,slots,internal),flat=f,**kwargs)
    def find(self,id):return next(p for p in self.parts if p.id==id)
    def remove(self,id):self.parts=[p for p in self.parts if p.id!=id]
    def permit(self,a,b,reason):self.allowed_intersections[frozenset((a,b))]=reason
    def cut(self,id,tool):
        p=self.find(id);p.shape=p.shape.cut(tool).clean()
        # Transformed parts need their individual fabrication local updated by creator.
        p.notes.append('Assembly modification applied; see assembly hole coordinates. Individual blank export is guarded.')
        p.release='ASSEMBLY DETAIL - INDIVIDUAL EXPORT GUARDED'

def write_dxf(path,flat):
    doc=ezdxf.new('R2010');doc.units=4;doc.header['$INSUNITS']=4
    for name in ('CUT_OUTER','CUT_HOLES','CUT_INNER'):
        doc.layers.new(name)
    ms=doc.modelspace()
    ms.add_lwpolyline(flat['outline'],close=True,dxfattribs={'layer':'CUT_OUTER'})
    for x,y,d in flat['holes']:ms.add_circle((x,y),d/2,dxfattribs={'layer':'CUT_HOLES'})
    for wire in flat['internal']:ms.add_lwpolyline(wire,close=True,dxfattribs={'layer':'CUT_INNER'})
    for x,y,L,w,angle in flat['slots']:
        # Closed bulged polyline: two parallel lines and semicircular ends.
        r=w/2;a=(L-w)/2;theta=math.radians(angle)
        def rotate(xx,yy):return (x+xx*math.cos(theta)-yy*math.sin(theta),y+xx*math.sin(theta)+yy*math.cos(theta))
        pts=[]
        for xx,yy,bulge in [(-a,-r,0),(a,-r,1),(a,r,0),(-a,r,1)]:
            px,py=rotate(xx,yy);pts.append((px,py,bulge))
        ms.add_lwpolyline(pts,format='xyb',close=True,dxfattribs={'layer':'CUT_HOLES'})
    # Non-through machining features are deliberately separate from laser contours.
    for op in flat.get('operations',[]):
        layer=op['layer']
        if layer not in doc.layers:doc.layers.new(layer)
        if op['type']=='circle':ms.add_circle((op['x'],op['y']),op['diameter']/2,dxfattribs={'layer':layer})
        elif op['type']=='slot':
            x,y,L,w=op['x'],op['y'],op['length'],op['width'];r=w/2;a=(L-w)/2
            ms.add_lwpolyline([(x-a,y-r,0),(x+a,y-r,1),(x+a,y+r,0),(x-a,y+r,1)],format='xyb',close=True,dxfattribs={'layer':layer})
    notes=flat.get('machining_notes',[])
    if notes:
        doc.layers.new('MACHINING_NOTES')
        xx=max(p[0] for p in flat['outline'])+20;yy=max(p[1] for p in flat['outline'])
        ms.add_mtext('\\P'.join(notes),dxfattribs={'layer':'MACHINING_NOTES','char_height':3,'insert':(xx,yy),'width':150})
    doc.saveas(path)
    reread=ezdxf.readfile(path);assert reread.units==4 and not reread.audit().has_errors

def validate(model):
    records=[]
    for p in model.parts:
        assert p.shape.isValid(),p.id
        assert len(p.shape.Solids())==1,(p.id,len(p.shape.Solids()))
        vol=p.shape.Volume();assert vol>0,p.id
        records.append({'id':p.id,'part_number':p.part_number,'group':p.group,'material':p.material,
                        'status':p.release,'purchased_envelope':p.purchased,'volume_mm3':round(vol,5),
                        'bounds_mm':[round(x,6) for x in bbox(p.shape)],'notes':p.notes})
    clashes=[];permitted=[];candidates=0
    for i,a in enumerate(model.parts):
        aa=records[i]['bounds_mm']
        for j in range(i+1,len(model.parts)):
            b=model.parts[j];bb=records[j]['bounds_mm']
            if not all(min(aa[k+3],bb[k+3])-max(aa[k],bb[k])>1e-5 for k in range(3)):continue
            candidates+=1
            vol=intersection_volume(a.shape,b.shape)
            if vol>.02:
                rec={'a':a.id,'b':b.id,'intersection_mm3':round(vol,5)}
                reason=model.allowed_intersections.get(frozenset((a.id,b.id)))
                if reason:rec['reason']=reason;permitted.append(rec)
                else:clashes.append(rec)
    return {'parts':records,'part_count':len(records),'broadphase_pairs':candidates,
            'unresolved_intersections':clashes,'documented_intersections':permitted,
            'note':'Positive-volume static interference test, not a strength or motion certification.'}

def export(model,root,name,individual=True):
    root=Path(root);(root/'step').mkdir(exist_ok=True,parents=True)
    r=validate(model)
    assembly=cq.Assembly(name=name)
    for p in model.parts:assembly.add(p.shape,name=p.id,color=cq.Color(*p.color))
    path=root/'step'/(name+'.step');assembly.save(str(path),exportType='STEP',mode='default')
    reread=cq.importers.importStep(str(path)).val()
    assert reread.isValid() and len(reread.Solids())==len(model.parts)
    expected=sum(p.shape.Volume() for p in model.parts)
    delta=abs(reread.Volume()-expected);volume_tolerance=max(.2,expected*1e-7)
    assert delta<volume_tolerance,{'expected_volume':expected,'actual_volume':reread.Volume(),'delta':delta,'tolerance':volume_tolerance}
    r['step_readback']={'passed':True,'solids':len(reread.Solids()),'volume_delta_mm3':delta,'volume_tolerance_mm3':volume_tolerance,
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'file':str(path.name)}
    if individual:
        (root/'parts').mkdir(exist_ok=True);(root/'dxf').mkdir(exist_ok=True)
        groups={}
        for p in model.parts:groups.setdefault(p.part_number,[]).append(p)
        cuts=[];operations=[];part_checks=[]
        for pn,parts in groups.items():
            p=parts[0]
            guarded=p.purchased or 'GUARDED' in p.release
            if not guarded:
                dst=root/'parts'/(pn+'.step');cq.exporters.export(p.local,str(dst))
                check=cq.importers.importStep(str(dst)).val()
                volume_delta=abs(check.Volume()-p.local.Volume())
                assert check.isValid() and len(check.Solids())==1 and volume_delta<max(.2,p.local.Volume()*1e-7),pn
                part_checks.append({'part_number':pn,'valid':True,'volume_delta_mm3':volume_delta})
                if p.flat:write_dxf(root/'dxf'/(pn+'.dxf'),p.flat)
            operations.append({'part_number':pn,'quantity':len(parts),'individual_export_guarded':guarded,
                               'datum':'LocalSTEPcoordinates;flatDXFviewislocalXY,thicknessalong+Z.',
                               'manufacturing_flat':p.flat,'notes':p.notes,'release':p.release})
            stock=p.material
            if p.flat:
                t=p.flat['thickness_mm']
                if abs(t-6)<1e-6:stock+='; finish-machine6.000mmfrom1/4in6.35mmstock'
                elif abs(t-8)<1e-6:stock+='; finish-machine8.000mmfrom3/8in9.525mmstock'
                elif abs(t-12)<1e-6:stock+='; finish-machine12.000mmfrom1/2in12.7mmstock'
                elif abs(t-3.048)<1e-6:stock+='; purchase0.120in sheet,verifyactualgauge'
            cuts.append({'part_number':pn,'quantity':len(parts),'material':p.material,'procured_stock':stock,'length_mm':p.length,
                         'thickness_mm':p.flat['thickness_mm'] if p.flat else None,'bounds_local_mm':[round(v,4) for v in bbox(p.local)],
                         'individual_export_guarded':guarded,'status':p.release,'notes':' | '.join(p.notes)})
        with (root/'cutlist.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(cuts[0]));w.writeheader();w.writerows(cuts)
        (root/'cutlist.json').write_text(json.dumps(cuts,indent=2)+'\n',encoding='utf-8')
        (root/'part-operations.json').write_text(json.dumps(operations,indent=2)+'\n',encoding='utf-8')
        r['individual_step_readback']=part_checks
    (root/(name+'-validation.json')).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    return r
