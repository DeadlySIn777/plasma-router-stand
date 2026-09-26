"""Render actual candidate CAD meshes; magenta allocation is explicitly labeled."""
from pathlib import Path
import sys, numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from render_cad import _triangle,_unit
OUT=Path(__file__).resolve().parent/'output'

def render(name,view=(-1.25,-1.8,1.25),size=(1600,1400)):
    data=np.load(OUT/(name+'.npz'));v=data['vertices'];f=data['triangles'];c=data['colors']
    camera=_unit(view);right=_unit(np.cross([0.,0.,1.],camera));basis=np.array((right,-np.cross(camera,right),camera))
    p=v@basis.T;w,h=size;lo=p[:,:2].min(0);hi=p[:,:2].max(0);scale=min((w-100)/(hi[0]-lo[0]),(h-250)/(hi[1]-lo[1]))
    p[:,:2]=p[:,:2]*scale+np.array([w/2,(h+35)/2])-(lo+hi)/2*scale
    pixels=np.full((h,w,3),(246,249,251),np.uint8);depth=np.full((h,w),-np.inf,np.float32)
    pts=v[f];n=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]);length=np.linalg.norm(n,axis=1);ok=length>1e-8;n[ok]/=length[ok,None]
    visible=ok&(n@camera>1e-8);shade=.60+.40*np.maximum(0,n@_unit((-1.5,-2,3)));rgb=np.clip(c*shade[:,None],0,255).astype(np.uint8)
    for i in np.flatnonzero(visible):_triangle(p[f[i]],rgb[i],pixels,depth)
    im=Image.fromarray(pixels);d=ImageDraw.Draw(im);bold=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',30);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21)
    d.text((40,25),'SMALL ATC | Removable rear bridge candidate',font=bold,fill=(24,47,59))
    d.text((40,72),'Blue: fabricated carrier. Magenta cage: unverified magazine allocation, not supplier CAD.',font=font,fill=(119,41,108))
    d.text((40,h-89),'Proposed routing axis rectangle with dock deployed: 800 x 788.6 mm (nominal).',font=font,fill=(28,70,87))
    d.text((40,h-53),'Magazine fit, approach, frame retrofit and in-footprint storage remain unqualified.',font=font,fill=(122,67,22))
    im.save(OUT/(name+'.png'))

if __name__=='__main__':
    render('SMALL_ATC_CONTEXT');render('SMALL_ATC_DOCK',size=(1600,950))
