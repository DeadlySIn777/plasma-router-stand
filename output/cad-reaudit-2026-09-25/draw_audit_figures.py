"""Dimensioned audit figures from source coordinates; these are not cut drawings."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

OUT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,(ax,detail)=plt.subplots(1,2,figsize=(13,8),gridspec_kw={'width_ratios':[1.1,1]})
fig.patch.set_facecolor('#f5f7fa')
fig.suptitle('CAD AUDIT  |  Geometry can be valid and still be wrong to fabricate',
             fontsize=17,fontweight='bold',x=.06,ha='left',y=.97,color='#182b40')
ax.add_patch(Rectangle((73.5,76.5),1000,1197,facecolor='#e2e7ed',edgecolor='#637487',label='T-slot deck: 1000 × 1197'))
ax.add_patch(Rectangle((105.8,76.5),938.4,1197,facecolor='#dfc794',alpha=.75,edgecolor='#9a7639',label='MDF support: 938.4 × 1197'))
ax.add_patch(Rectangle((175,121.4),800,1000,facecolor='#d1e9e7',alpha=.8,edgecolor='#007c83',lw=2,label='Nominal tool-axis travel: 800 × 1000'))
for x,ys in ((103.5,(176.5,676.5,1176.5)),(1043.5,(426.5,926.5))):
    for y in ys:
        ax.add_patch(Circle((x,y),8,facecolor='#bb283e',edgecolor='#bb283e'))
        ax.plot(x,y,'x',color='#bb283e',markersize=10,mew=2)
ax.annotate('3 screw axes outside MDF\n2 edge-breaking seats',xy=(103.5,676.5),xytext=(280,660),
            arrowprops={'arrowstyle':'->','color':'#bb283e'},color='#9c1930',fontweight='bold')
ax.annotate('Rear face is 152.1 mm\nbeyond the axis limit',xy=(700,1230),xytext=(450,1390),
            arrowprops={'arrowstyle':'->','color':'#42536b'},color='#42536b')
ax.set(xlim=(-10,1180),ylim=(-100,1510),xlabel='World X (mm)',ylabel='World Y (mm)')
ax.set_aspect('equal');ax.set_title('BED02 / BED03 — support and reach',loc='left',pad=14,fontweight='bold')
ax.legend(loc='lower center',bbox_to_anchor=(.5,-.21),frameon=False,fontsize=9)
ax.grid(color='#d9e1e8',alpha=.5)

detail.add_patch(Rectangle((0,0),110,90,facecolor='#e8edf3',edgecolor='#637487'))
for x in (20,90):
    # Outline extents show the mismatch; the exact ends are semicircular in CAD.
    detail.add_patch(Rectangle((x-5.5,30),11,30,fill=False,edgecolor='#007c83',lw=2.5,
                              label='Required recess extents in STEP' if x==20 else None))
    detail.add_patch(Rectangle((x-15,39.5),30,11,fill=False,edgecolor='#bb283e',ls='--',lw=2.5,
                              label='Delivered DXF recess extents' if x==20 else None))
    detail.plot(x,45,'+',color='#182b40')
detail.annotate('90° orientation error',xy=(20,45),xytext=(4,73),
                arrowprops={'arrowstyle':'->','color':'#bb283e'},color='#9c1930',fontweight='bold')
detail.set(xlim=(-8,118),ylim=(-8,100),xlabel='Part-local X (mm)',ylabel='Part-local Y (mm)')
detail.set_aspect('equal');detail.set_title('MT01 — Z-adapter milling recesses',loc='left',pad=14,fontweight='bold')
detail.legend(loc='lower center',bbox_to_anchor=(.5,-.35),frameon=False,fontsize=9)
detail.grid(color='#d9e1e8',alpha=.5)
for a in (ax,detail):
    a.spines[['top','right']].set_visible(False)
fig.text(.06,.035,'Audit illustration only. Nominal axis travel is not a cutter sweep. Recess rectangles show extents, not CAM contours.\nSources: bed_details.py, motion_details.py, and dxf/TOOL_ADAPTER_110.dxf. Read the detailed findings before fabrication.',
         fontsize=9,color='#42536b')
fig.subplots_adjust(left=.07,right=.97,top=.87,bottom=.20,wspace=.30)
fig.savefig(OUT/'cad-audit-geometry.png',dpi=160,facecolor=fig.get_facecolor())
fig.savefig(OUT/'cad-audit-geometry.svg',facecolor=fig.get_facecolor())
svg=OUT/'cad-audit-geometry.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
print('Wrote PNG and SVG audit figures')
