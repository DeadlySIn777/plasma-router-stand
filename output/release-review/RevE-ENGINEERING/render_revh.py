"""Render actual corrected CAD tessellations; no generated illustration geometry."""
from pathlib import Path
import sys
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SOURCE=Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCE.parents[2]))
from render_cad import _triangle, _unit
ROOT=SOURCE.parent/'RevH-CAD'


def render(name,view=(-1.25,-1.8,1.25),size=(1600,1400),suffix=''):
    data=np.load(ROOT/'previews'/(name+'.npz'))
    vertices=data['vertices'];faces=data['triangles'];colors=data['colors']
    camera=_unit(view);right=_unit(np.cross(np.array([0.,0.,1.]),camera))
    basis=np.array((right,-np.cross(camera,right),camera))
    projected=vertices@basis.T
    w,h=size;lo=projected[:,:2].min(0);hi=projected[:,:2].max(0)
    scale=min((w-110)/(hi[0]-lo[0]),(h-220)/(hi[1]-lo[1]))
    projected[:,:2]=projected[:,:2]*scale+np.array([w/2,(h+10)/2])-(lo+hi)/2*scale
    pixels=np.empty((h,w,3),np.uint8);pixels[:]=(246,249,251)
    depth=np.full((h,w),-np.inf,np.float32)
    pts=vertices[faces];normal=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0])
    lengths=np.linalg.norm(normal,axis=1);valid=lengths>1e-8
    normal[valid]/=lengths[valid,None]
    visible=valid&(normal@camera>1e-8)
    shade=.60+.40*np.maximum(0,normal@_unit((-1.5,-2,3)))
    rgb=np.clip(colors*shade[:,None],0,255).astype(np.uint8)
    for i in np.flatnonzero(visible):
        _triangle(projected[faces[i]],rgb[i],pixels,depth)
    finite=np.isfinite(depth);edge=np.zeros((h,w),bool)
    for axis in (0,1):
        delta=np.diff(np.where(finite,depth,-1e9),axis=axis)
        selected=(np.abs(delta)>10)&(np.abs(delta)<1e8)
        if axis==0:edge[:-1]|=selected
        else:edge[:,:-1]|=selected
    pixels[edge]=(pixels[edge].astype(float)*.72).astype(np.uint8)
    picture=Image.fromarray(pixels);draw=ImageDraw.Draw(picture)
    titlefont=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',30)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
    titles={'RevH_ROUTER':'Rev H | Router bed installed',
            'RevH_BED_STORED':'Rev H | Bed and router tools stored inside',
            'RevH_STORAGE_DETAIL':'Rev H | Storage and service arrangement'}
    draw.text((42,25),titles.get(name,name),font=titlefont,fill=(28,43,50))
    draw.text((42,69),'Actual CAD geometry. Amber parts are purchased envelopes.',font=font,fill=(85,101,112))
    draw.text((42,h-77),'WORKING DESIGN: manual conversion assumption; supplier interfaces still open.',font=font,fill=(112,66,18))
    note='The stored-bed view does not include a verified plasma head.' if name!='RevH_ROUTER' else 'Nominal motion: X 800 / Y 1000 / Z 100 mm. Not a fabrication release.'
    draw.text((42,h-46),note,font=font,fill=(85,101,112))
    dest=ROOT/'previews'/(name+suffix+'.png');picture.save(dest)
    return {'file':dest.name,'bounds_min':vertices.min(0).tolist(),'bounds_max':vertices.max(0).tolist()}


def main():
    results=[]
    for name in ('RevH_ROUTER','RevH_BED_STORED'):
        print('Render',name,flush=True);results.append(render(name))
    results.append(render('RevH_BED_STORED',view=(0,-1,.18),size=(1400,1400),suffix='_front'))
    (ROOT/'previews'/'preview-metadata.json').write_text(json.dumps(results,indent=2)+'\n')
    print('Rendered',len(results),'CAD views',flush=True)


if __name__=='__main__':main()
