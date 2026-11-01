"""Render actual XR1 solids. No illustrative substitute for generated geometry."""
from pathlib import Path
import importlib.util
from PIL import Image, ImageDraw
import params as P

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('legacy_render',HERE.parent/'extrusion-wood-plasma'/'preview.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)

def draw(assemblies,out):
    ims=[]
    for label in ('WOOD','PLASMA','FRAME'):
        im=legacy.render(assemblies[label],back=label=='PLASMA',w=1300,h=1050)
        im.save(out/f'{label.lower()}-view.png');ims.append(im)
    page=Image.new('RGB',(1800,1020),'#f3f6f7');d=ImageDraw.Draw(page)
    ink='#15333e';mut='#4b6670';font=legacy.font
    d.text((46,28),P.REVISION+'  |  4080 WOOD + PLASMA TABLE',font=font(43,True),fill=ink)
    d.text((48,91),f'{P.X_TRAVEL:,.0f} X / {P.Y_TRAVEL:,.0f} Y / {P.Z_TRAVEL:,.0f} Z nominal travel     •     Engineering revision',font=font(25),fill=mut)
    titles=('01  WOODWORKING','02  PLASMA','03  FRAME')
    captions=('Removable dry bed with aluminum T-slot workholding.',
              'Steel hot zone; dry bed in covered storage.',
              'Six continuous posts; no second full-length frame tier.')
    for i,im in enumerate(ims):
        x=37+591*i
        d.rounded_rectangle((x,151,x+571,821),radius=15,fill='#e8eff1',outline='#cad7db',width=2)
        d.text((x+17,170),titles[i],font=font(25,True),fill=ink)
        im.thumbnail((550,535),Image.Resampling.LANCZOS)
        page.paste(im,(x+(571-im.width)//2,222+(535-im.height)//2))
        words=captions[i].split();lines=['']
        for word in words:
            if len(lines[-1])+len(word)>39:lines.append('')
            lines[-1]+=(' ' if lines[-1] else '')+word
        for k,line in enumerate(lines):d.text((x+15,759+k*24),line,font=font(19),fill=mut)
    d.text((48,866),'Geometry, loads and conversion paths are checked separately.',font=font(28,True),fill=ink)
    d.text((48,916),'Read the current ATC fit result and physical release register before fabrication. No prices.',font=font(23),fill=mut)
    d.text((48,958),'Actual CAD solids shown. Tool, torch and cable envelopes remain subject to measurement.',font=font(21),fill=mut)
    page.save(out/'overview.png')
