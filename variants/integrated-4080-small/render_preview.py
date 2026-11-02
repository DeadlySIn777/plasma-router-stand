"""Render actual CAD meshes with a camera fitted to the complete assembly."""
from PIL import Image
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

def render(parts,back=False,w=1600,h=1500):
    scene=vtk.vtkRenderer();scene.SetBackground(.96,.97,.975)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetShowWindow(False)
    window.SetSize(w,h);window.SetMultiSamples(4);window.AddRenderer(scene)
    for name,solid,color in parts:
        mesh=solid.toVtkPolyData(tolerance=.65,angularTolerance=.3,normals=True)
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(mesh);mapper.ScalarVisibilityOff()
        actor=vtk.vtkActor();actor.SetMapper(mapper)
        prop=actor.GetProperty();prop.SetColor(*color);prop.SetAmbient(.38);prop.SetDiffuse(.68)
        prop.SetSpecular(.13);prop.SetSpecularPower(25);scene.AddActor(actor)
    b=scene.ComputeVisiblePropBounds()
    center=tuple((b[2*k]+b[2*k+1])/2 for k in range(3))
    direction=(1.6,2.35,1.45)if back else(1.65,-2.35,1.5)
    camera=scene.GetActiveCamera();camera.SetFocalPoint(*center)
    camera.SetPosition(*(c+3000*d for c,d in zip(center,direction)))
    camera.SetViewUp(0,0,1);camera.ParallelProjectionOn()
    scene.ResetCamera();camera.SetParallelScale(camera.GetParallelScale()*1.04)
    scene.ResetCameraClippingRange();window.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.ReadFrontBufferOff();capture.Update()
    pixels=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(h,w,-1)
    result=Image.fromarray(np.flipud(pixels).copy()).convert('RGB');window.Finalize()
    a=np.asarray(result,dtype=int);mask=np.max(abs(a-np.array(result.getpixel((0,0)))),axis=2)>15
    yy,xx=np.where(mask)
    if len(xx):
        assert xx.min()>4 and xx.max()<w-5 and yy.min()>4 and yy.max()<h-5,'CAD preview touches viewport edge'
        result=result.crop((int(xx.min()-8),int(yy.min()-8),int(xx.max()+9),int(yy.max()+9)))
    return result
