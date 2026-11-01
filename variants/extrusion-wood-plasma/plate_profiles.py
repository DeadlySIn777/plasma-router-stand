"""Actual face outlines for quoting flat plates/braces; not machine toolpaths."""
import csv,os,sys
from pathlib import Path
import cadquery as cq
import ezdxf
from ezdxf import bbox as dxbox
from frame import frame_parts,wet_support_option

H=Path(__file__).resolve().parent; OUT=H/'plate-profiles'
def main():
    OUT.mkdir(exist_ok=True);index=[]
    for name,s,_ in frame_parts()+wet_support_option():
        if 'SPACER' in name or not name.startswith(('JOIN_','BEARING_SHELF','BRACE_','OPT_BEARER_CLIP')):continue
        faces=[f for f in s.Faces() if f.geomType()=='PLANE'];f=max(faces,key=lambda q:q.Area())
        normal=f.normalAt();straight=[e for e in f.Edges() if e.geomType()=='LINE']
        e=max(straight,key=lambda q:q.Length());v=e.endPoint()-e.startPoint()
        pl=cq.Plane(f.Center(),v.normalized(),normal)
        local=pl.toLocalCoords(f);b=local.BoundingBox()
        local=local.translate((-b.xmin,-b.ymin,-b.zmin))
        dest=OUT/(name+'.dxf');cq.exporters.export(local,str(dest))
        d=ezdxf.readfile(str(dest)); ents=d.modelspace(); bb=dxbox.extents(ents)
        assert d.units==4 and abs(bb.size.x-b.xlen)<.03 and abs(bb.size.y-b.ylen)<.03
        assert sum(e.dxftype()=='CIRCLE' for e in ents)>=2,name
        index.append(dict(id=name,mm_span_x=round(b.xlen,3),mm_span_y=round(b.ylen,3),
            thickness_mm=6.35 if name.startswith('BEARING_SHELF') else 4 if name.startswith('BRACE_') else 6,
            count=1,option='9 feet only' if name.startswith('OPT_') else 'both frames',
            review_DXF=name+'.dxf'))
    with (OUT/'index.csv').open('w',newline='',encoding='utf8') as fh:
        w=csv.DictWriter(fh,fieldnames=list(index[0]));w.writeheader();w.writerows(index)
    print(f'{len(index)} DXFs verified for millimeter units, extents, and holes.')
if __name__=='__main__':
    # The shared OCP build can fault during interpreter teardown after a good export.
    try: main(); code=0
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
