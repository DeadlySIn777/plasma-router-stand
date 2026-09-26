"""Reproducible technical previews of the full-sheet layout; no photo assets."""
from pathlib import Path
import hashlib,json,os,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from layout import Parameters,build,dimensions,bounds

OUT=Path(__file__).resolve().parent

def raster(parts, width=2200, height=1750):
    """Orthographic triangle rasterizer with a per-pixel depth buffer.

    A real depth test is needed for large pan triangles beneath small panels;
    painter's average-triangle ordering is not sufficient for this geometry.
    """
    view=np.array([.8,-1.25,.82]);view/=np.linalg.norm(view)
    right=np.cross([0.,0.,1.],view);right/=np.linalg.norm(right)
    up=np.cross(view,right);basis=np.stack([right,up,view],axis=1)
    triangles=[];colors=[]
    light=np.array([-.4,-.7,1.]);light/=np.linalg.norm(light)
    for item in parts:
        vertices,indices=item.shape.tessellate(1.0,.15)
        points=np.array([v.toTuple() for v in vertices])
        for index in indices:
            tri=points[list(index)]
            normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);norm=np.linalg.norm(normal)
            if norm<1e-12:continue
            normal/=norm
            # Both sides can appear on hollow members; illuminate the viewed side.
            if np.dot(normal,view)<0:normal=-normal
            shade=.61+.39*max(0.,np.dot(normal,light))
            colors.append(np.clip(np.array(item.color)*shade*255,0,255))
            triangles.append(tri@basis)
    triangles=np.array(triangles);xy=triangles[:,:,:2]
    lo=xy.min(axis=(0,1));hi=xy.max(axis=(0,1))
    scale=min((width-70)/(hi[0]-lo[0]),(height-70)/(hi[1]-lo[1]))
    center=(lo+hi)/2
    triangles[:,:,0]=(triangles[:,:,0]-center[0])*scale+width/2
    triangles[:,:,1]=height/2-(triangles[:,:,1]-center[1])*scale
    buffer=np.full((height,width),-np.inf,dtype=np.float64)
    pixels=np.full((height,width,3),[241,244,245],dtype=np.uint8)
    for tri,color in zip(triangles,colors):
        xmin=max(0,int(np.floor(tri[:,0].min())));xmax=min(width-1,int(np.ceil(tri[:,0].max())))
        ymin=max(0,int(np.floor(tri[:,1].min())));ymax=min(height-1,int(np.ceil(tri[:,1].max())))
        if xmin>xmax or ymin>ymax:continue
        x,y=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
        x0,y0,z0=tri[0];x1,y1,z1=tri[1];x2,y2,z2=tri[2]
        den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
        if abs(den)<1e-10:continue
        aa=((y1-y2)*(x-x2)+(x2-x1)*(y-y2))/den
        bb=((y2-y0)*(x-x2)+(x0-x2)*(y-y2))/den;cc=1-aa-bb
        depth=aa*z0+bb*z1+cc*z2
        region=buffer[ymin:ymax+1,xmin:xmax+1]
        mask=(aa>=-1e-9)&(bb>=-1e-9)&(cc>=-1e-9)&(depth>region)
        region[mask]=depth[mask]
        pixels[ymin:ymax+1,xmin:xmax+1][mask]=color
    # One-pixel depth discontinuities clarify silhouettes without triangle edges.
    occupied=np.isfinite(buffer)
    edge=np.zeros_like(occupied)
    for axis in (0,1):
        neighbor=np.roll(buffer,1,axis=axis);neighbor_ok=np.isfinite(neighbor)
        difference=np.zeros_like(buffer)
        np.subtract(buffer,neighbor,out=difference,where=occupied&neighbor_ok)
        edge|=occupied&((~neighbor_ok)|(np.abs(difference)>16.))
    pixels[edge]=(pixels[edge].astype(float)*.67).astype(np.uint8)
    return pixels


def main():
    p=Parameters();d=dimensions(p)
    sources={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (OUT/'layout.py',Path(__file__))}
    for state in ('router','plasma_layout'):
        parts,_=build(p,state);fig=plt.figure(figsize=(13.5,10),facecolor='#f1f4f5')
        ax=fig.add_axes([.02,.10,.96,.79]);ax.imshow(raster(parts));ax.axis('off')
        title='ROUTER LAYOUT' if state=='router' else 'PLASMA / INTERNAL STORAGE LAYOUT'
        fig.suptitle('48 × 96 in HYBRID  |  '+title,x=.06,ha='left',y=.965,size=19,weight='bold',color='#193b47')
        fig.text(.06,.925,'Full-sheet area 1219.2 × 2438.4 mm  •  Frame 1950 × 2950 mm  •  18 separate carriers + HDPE tops',size=11,color='#334c56')
        fig.text(.06,.060,'DEVELOPMENT GEOMETRY — NOT A FABRICATION RELEASE',size=12,weight='bold',color='#ab4727')
        fig.text(.06,.035,'Orange = unselected motion allocations. Purple = ATC bay. Storage poses do not prove handling routes or restraint.',size=10,color='#334c56')
        fig.savefig(OUT/('layout-router.png' if state=='router' else 'layout-plasma.png'),dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9.5,13),facecolor='white');ax.set_facecolor('#f8fafb')
    ax.add_patch(Rectangle((0,0),p.frame_x,p.frame_y,fill=False,linewidth=3,edgecolor='#233e47'))
    ax.add_patch(Rectangle((p.pan_origin_x,p.pan_origin_y),p.pan_inner_x,p.pan_inner_y,facecolor='#d3e2e9',edgecolor='#58798a'))
    ax.add_patch(Rectangle((p.deck_origin_x,p.deck_origin_y),p.deck_x,p.deck_y,fill=False,edgecolor='#233e47',linewidth=2))
    for c in range(1,p.columns):
        x=p.deck_origin_x+c*(d['panel_x']+p.panel_gap)-p.panel_gap/2
        ax.plot([x,x],[p.deck_origin_y,p.deck_origin_y+p.deck_y],color='#738992',lw=1)
    for r in range(1,p.rows):
        y=p.deck_origin_y+r*(d['panel_y']+p.panel_gap)-p.panel_gap/2
        ax.plot([p.deck_origin_x,p.deck_origin_x+p.deck_x],[y,y],color='#738992',lw=1)
    ax.add_patch(Rectangle((p.sheet_origin_x,p.sheet_origin_y),p.sheet_x,p.sheet_y,fill=False,edgecolor='#147765',linewidth=2,linestyle='--'))
    ax.add_patch(Rectangle((1600,400),200,600,facecolor='#baa7d1',edgecolor='#665080'))
    ax.text(1700,700,'ATC BAY\n600 × 200\nNOT selected',ha='center',va='center',rotation=90,size=10)
    ax.add_patch(Rectangle((d['tool_centers_x'][0],d['tool_centers_y'][0]),d['tool_centers_x'][1]-d['tool_centers_x'][0],d['tool_centers_y'][1]-d['tool_centers_y'][0],fill=False,edgecolor='#db7b29',linewidth=1.4,linestyle=':'))
    ax.text(790,1450,'USABLE SHEET\n1219.2 × 2438.4 mm',ha='center',va='center',size=15,weight='bold',color='#147765',bbox=dict(facecolor='white',alpha=.85,edgecolor='none',pad=10))
    ax.text(800,2835,'1320 × 2550 deck  /  438.667 × 423.333 modules',ha='center',size=10)
    for xc in (75,1875):
        for yc in (100,1000,1900,2850):ax.add_patch(Rectangle((xc-50,yc-50),100,100,facecolor='#233e47'))
    ax.set_aspect('equal');ax.set_xlim(-100,2100);ax.set_ylim(-80,3100);ax.set_xlabel('X / mm');ax.set_ylabel('Y / mm')
    ax.set_title('Full-sheet hybrid — plan allocation\n1950 × 2950 mm overall',loc='left',size=18,weight='bold',pad=20)
    fig.text(.10,.035,'Orange dotted line: tool-center allocation including full-deck surfacing and dry ATC reach.\nDashed green: full sheet. Eight dark squares: frame feet. No handling path or structural release implied.',size=9,color='#41565f')
    fig.subplots_adjust(bottom=.09,top=.91)
    fig.savefig(OUT/'layout-plan.svg');fig.savefig(OUT/'layout-plan.png',dpi=150);plt.close(fig)
    names=['layout-router.png','layout-plasma.png','layout-plan.svg','layout-plan.png']
    report={'source_sha256':sources,'sources_unchanged':all(hashlib.sha256((OUT/n).read_bytes()).hexdigest()==h for n,h in sources.items()),
            'artifact_sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names},
            'scope':'Rendered source geometry and parameter plan. Inspection does not certify fabrication, interfaces, motion or strength.'}
    (OUT/'preview-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Previews rendered; source unchanged',report['sources_unchanged'],flush=True)

if __name__=='__main__':
    try:main();code=0
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
