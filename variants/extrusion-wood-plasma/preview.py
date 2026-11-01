"""Orthographic previews from the actual review solids, via VTK's depth buffer."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np

def render(parts,back=False,w=1000,h=850):
    scene=vtk.vtkRenderer();scene.SetBackground(.96,.97,.975)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetShowWindow(False)
    win.SetSize(w,h);win.SetMultiSamples(4);win.AddRenderer(scene)
    for name,solid,c in parts:
        mesh=solid.toVtkPolyData(tolerance=0.65,angularTolerance=0.3,normals=True)
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(mesh);mapper.ScalarVisibilityOff()
        actor=vtk.vtkActor();actor.SetMapper(mapper)
        prop=actor.GetProperty();prop.SetColor(*c);prop.SetAmbient(.38);prop.SetDiffuse(.68)
        prop.SetSpecular(.13);prop.SetSpecularPower(25)
        scene.AddActor(actor)
    center=(575,725,670); v=(1.6,2.35,1.45) if back else (1.65,-2.35,1.5)
    cam=scene.GetActiveCamera();cam.SetFocalPoint(*center)
    cam.SetPosition(*(i+1000*j for i,j in zip(center,v)));cam.SetViewUp(0,0,1)
    cam.ParallelProjectionOn();cam.SetParallelScale(1125);scene.ResetCameraClippingRange()
    win.Render(); filt=vtk.vtkWindowToImageFilter();filt.SetInput(win);filt.ReadFrontBufferOff();filt.Update()
    dat=vtk_to_numpy(filt.GetOutput().GetPointData().GetScalars()).reshape(h,w,-1)
    img=Image.fromarray(np.flipud(dat).copy()).convert('RGB');win.Finalize()
    bg=img.getpixel((0,0)); a=np.asarray(img,dtype=int)
    mask=np.max(abs(a-np.array(bg)),axis=2)>15; ys,xs=np.where(mask)
    if len(xs): img=img.crop((max(0,int(xs.min()-9)),max(0,int(ys.min()-9)),min(w,int(xs.max()+10)),min(h,int(ys.max()+10))))
    return img
def font(n,bold=False):
    for f in (('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf'),
              ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')):
        try:return ImageFont.truetype(f,n)
        except OSError:pass
    return ImageFont.load_default()
def draw(assys,f,out):
    tiles=[]
    for mode,parts in [('WOOD',assys['WOOD']),('PLASMA',assys['PLASMA']),('FRAME',f)]:
        im=render(parts,back=(mode=='PLASMA'));im.save(out/(mode.lower()+'-view.png'));tiles.append(im)
    page=Image.new('RGB',(1650,842),'#f5f7f9'); d=ImageDraw.Draw(page); ink='#172c35';mut='#3e5a64'
    d.text((45,22),'4040   /   CARVING + PLASMA',font=font(40,True),fill=ink)
    d.text((48,77),'Small machine  •  800 × 1,000 mm nominal XY travel  •  Design review',font=font(23),fill=mut)
    labels=[('01   CARVING','Four metal panels + removable job backers.'),
            ('02   PLASMA','Steel slats exposed; cleaned panels park at rear.'),
            ('03   FRAME','Nine feet; each pan bearer has a center support.')]
    for i,(im,(title,sub)) in enumerate(zip(tiles,labels)):
        x=42+535*i;d.rounded_rectangle((x,140,x+514,684),radius=14,fill='#ecf0f2',outline='#c5d1d6',width=2)
        d.text((x+15,150),title,font=font(24,True),fill=ink)
        im.thumbnail((488,435),Image.Resampling.LANCZOS)
        page.paste(im,(x+(514-im.width)//2,195+(435-im.height)//2));d.text((x+12,646),sub,font=font(19),fill=mut)
    d.text((45,721),'Shown: 9-foot frame  /  $379.78 extrusion   •   6-foot base frame  /  $319.88 extrusion',font=font(28,True),fill=ink)
    d.text((47,775),'Profile stock only. Motion, steel process parts and hardware are separate. The torch insert is shown unbored.',font=font(21),fill=mut)
    page.save(out/'overview.png')
