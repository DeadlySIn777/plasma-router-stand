"""Orthographic z-buffer previews of the exported CadQuery tessellations."""
from pathlib import Path
import sys,json,base64
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[2]))
from render_cad import _triangle,_unit,RenderResult

def render(name,view=(-1.25,-1.8,1.25),size=(1700,1500),suffix=''):
    data=np.load(ROOT/'previews'/(name+'.npz'));v=data['vertices'];f=data['triangles'];col=data['colors']
    camera=_unit(view);up=np.array([0.,0.,1.])
    right=_unit(np.cross(up,camera));imageup=np.cross(camera,right)
    basis=np.array((right,-imageup,camera));pv=v@basis.T
    w,h=size;lo=pv[:,:2].min(0);hi=pv[:,:2].max(0)
    scale=min((w-130)/(hi[0]-lo[0]),(h-210)/(hi[1]-lo[1]))
    offset=np.array([w/2,(h+40)/2])-(lo+hi)/2*scale
    pv[:,:2]=pv[:,:2]*scale+offset
    pixel=np.empty((h,w,3),np.uint8);pixel[:]=(248,250,252)
    depth=np.full((h,w),-np.inf,np.float32)
    pts=v[f];norm=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]);lens=np.linalg.norm(norm,axis=1)
    valid=lens>1e-8;norm[valid]/=lens[valid,None]
    visible=valid&(norm@camera>1e-8);light=_unit((-1.5,-2,3))
    shade=.58+.42*np.maximum(0,norm@light)
    rgb=np.clip(col*shade[:,None],0,255).astype(np.uint8)
    for i in np.flatnonzero(visible):_triangle(pv[f[i]],rgb[i],pixel,depth)
    # Depth discontinuities add a restrained real silhouette, not painter edges.
    finite=np.isfinite(depth);edge=np.zeros((h,w),bool)
    for axis in(0,1):
        d=np.diff(np.where(finite,depth,-1e9),axis=axis)
        e=(np.abs(d)>10)&(np.abs(d)<1e8)
        if axis==0:edge[:-1]|=e
        else:edge[:,:-1]|=e
    pixel[edge]=(pixel[edge].astype(float)*.72).astype(np.uint8)
    im=Image.fromarray(pixel);draw=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',30)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
    titles={'RevE_ROUTER':'Router deck / one-piece module installed','RevE_PLASMA_SETUP':'Plasma bed / module hoisted clear, water at Z820','RevE_WATER_CUTAWAY':'Water and controls / structure isolated'}
    draw.text((45,28),titles.get(name,name),font=font,fill=(28,43,50))
    draw.text((45,h-42),'Rev F engineering model · supplier interfaces and commissioning checks remain open',font=small,fill=(81,98,106))
    draw.text((45,h-70),'Amber identifies purchased component envelopes; it is not a paint specification.',font=small,fill=(106,100,89))
    path=ROOT/'previews'/(name+suffix+'.png');im.save(path)
    return RenderResult(str(path),w,h,basis,scale,offset,np.array([v.min(0),v.max(0)]))

def orthographic_sheet():
    front=render('RevE_ROUTER',(0,-1,0),(1000,1000),'_front')
    side=render('RevE_ROUTER',(1,0,0),(1000,1000),'_side')
    b=front.bounds;dims=b[1]-b[0]
    def embedded(path):return base64.b64encode(Path(path).read_bytes()).decode()
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="2100" height="1220" viewBox="0 0 2100 1220">
<rect width="2100" height="1220" fill="#f8fafc"/><style>text{{font-family:Segoe UI,Arial;fill:#1c2b32}}.d{{stroke:#536b76;stroke-width:2;fill:none}}</style>
<text x="50" y="48" font-size="30">Rev F • measured assembly envelope</text>
<text x="50" y="83" font-size="20">Orthographic views generated from the actual STEP-source solids. Dimensions in mm. Supplier envelopes included.</text>
<image x="25" y="100" width="1000" height="1000" href="data:image/png;base64,{embedded(front.output_path)}"/>
<image x="1075" y="100" width="1000" height="1000" href="data:image/png;base64,{embedded(side.output_path)}"/>
<path class="d" d="M100,1120H950 M100,1108V1132 M950,1108V1132 M1150,1120H2000 M1150,1108V1132 M2000,1108V1132"/>
<text x="525" y="1155" text-anchor="middle" font-size="26">Overall X {dims[0]:.2f}</text>
<text x="1575" y="1155" text-anchor="middle" font-size="26">Overall Y {dims[1]:.2f}</text>
<text x="1050" y="1200" text-anchor="middle" font-size="23">Overall Z {dims[2]:.2f} · router surface Z959.8 · plasma slats Z850 · rail caps Z1063.94</text>
</svg>'''
    (ROOT/'previews'/'RevE-orthographic-dimensions.svg').write_text(svg,encoding='utf-8')
    return {'min_xyz_mm':b[0].tolist(),'max_xyz_mm':b[1].tolist(),'dimensions_mm':dims.tolist()}

def main():
    for name in('RevE_ROUTER','RevE_PLASMA_SETUP','RevE_WATER_CUTAWAY'):
        print('Render',name,flush=True);render(name)
    bounds=orthographic_sheet()
    (ROOT/'previews'/'preview-metadata.json').write_text(json.dumps(bounds,indent=2)+'\n')
    print(json.dumps(bounds),flush=True)

if __name__=='__main__':main()
