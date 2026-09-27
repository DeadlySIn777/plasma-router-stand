"""Bounded large-machine retractable-ATC packaging study, not purchased-part CAD."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=ROOT/'variants/48x96/layout.py'
spec=importlib.util.spec_from_file_location('large_layout',BASE)
layout=importlib.util.module_from_spec(spec);sys.modules[spec.name]=layout;spec.loader.exec_module(layout)

def box(x0,y0,z0,x1,y1,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).val().translate((x0,y0,z0))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bb(s):return layout.bounds(s)
def volume(a,b):
    aa,ab=bb(a),bb(b)
    if not all(min(aa[k+3],ab[k+3])-max(aa[k],ab[k])>1e-6 for k in range(3)):return 0.
    op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.Build()
    if not op.IsDone():raise RuntimeError('Boolean intersection failed')
    shape=op.Shape();return 0. if shape.IsNull() else cq.Shape.cast(shape).Volume()
def clashes(movers,obstacles):
    hits=[]
    for name,a in movers.items():
        for other,b in obstacles.items():
            v=volume(a,b)
            if v>.01:hits.append({'moving':name,'obstacle':other,'volume_mm3':v})
    return hits

def fixed():
    return {'UNSELECTED_350MM_GUIDE_AND_DRIVE_ALLOCATION':box(1470,390,750,1820,1010,800),
            'HOOD_ROOF_2MM_LAYOUT':box(1655,380,960,1830,1020,962),
            'HOOD_REAR_2MM_LAYOUT':box(1828,380,800,1830,1020,960),
            'HOOD_FRONT_END_2MM_LAYOUT':box(1655,380,800,1828,382,960),
            'HOOD_REAR_END_2MM_LAYOUT':box(1655,1018,800,1828,1020,960)}

def assembly(state):
    parts=fixed()
    start=1465 if state=='change' else 1665
    parts['UNVERIFIED_MAGAZINE_CARRIER_TOOL_ENVELOPE']=box(start,400,800,start+160,1000,940)
    low=970 if state=='change' else 800
    parts['SHUTTER_LAYOUT_NO_ACTUATOR']=box(1653,382,low,1655,1018,low+160)
    return parts

def preview():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,axes=plt.subplots(1,2,figsize=(12,9),facecolor='white')
    for ax,state in zip(axes,('change','parked')):
        ax.set_facecolor('#f7f9fa')
        ax.add_patch(Rectangle((1430,350),20,700,facecolor='#c9cece',label='Existing deck edge'))
        ax.add_patch(Rectangle((1837.5,350),22.5,700,facecolor='#deb17f',label='Y-carriage allocation'))
        ax.add_patch(Rectangle((1470,390),350,620,facecolor='#f6c48b',alpha=.5,edgecolor='#ad6a28',label='Guide/drive reserve, below Z800'))
        ax.add_patch(Rectangle((1655,380),175,640,facecolor='#b8cbd0',alpha=.7,edgecolor='#294a57',linewidth=2,label='Hood'))
        x=1465 if state=='change' else 1665
        ax.add_patch(Rectangle((x,400),160,600,facecolor='#9b79ba',alpha=.85,edgecolor='#694083',linewidth=2,label='Unverified moving envelope'))
        ax.plot([1654,1654],[382,1018],color='#163b4c',lw=3,ls='--' if state=='change' else '-',label='Shutter (dashed = raised)')
        ax.axvline(1475.4,color='#be3d2e',lw=1.5,ls=':',label='Extreme surfacing cutter edge')
        ax.annotate('',xy=(1745,1060),xytext=(1545,1060),arrowprops={'arrowstyle':'<->','color':'#294a57'})
        ax.text(1645,1080,'200 mm actual stroke',ha='center',size=10)
        ax.text(x+80,700,'160 x 600 mm\nALLOCATION',rotation=90,ha='center',va='center',size=11,color='#321d45')
        ax.set_xlim(1415,1870);ax.set_ylim(325,1120);ax.set_aspect('equal')
        ax.set_xlabel('X / mm');ax.set_ylabel('Y / mm')
        ax.set_title('CHANGE / shutter raised' if state=='change' else 'PARKED / shutter closed',size=13,weight='bold')
        ax.grid(alpha=.12)
    fig.suptitle('4 x 8 hybrid: retractable ATC side-lane allocation',size=18,weight='bold',x=.09,ha='left')
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=2,fontsize=9,bbox_to_anchor=(.5,.06))
    fig.text(.09,.025,'Conditional envelopes only. Park before surfacing. Hood is not qualified plasma protection.',size=10,color='#a33d27')
    fig.subplots_adjust(left=.06,right=.98,top=.9,bottom=.22,wspace=.18)
    fig.savefig(OUT/'plan.svg');fig.savefig(OUT/'plan.png',dpi=160);plt.close(fig)

def main():
    inputs=[BASE,Path(__file__),OUT/'README.md']
    before={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    p=layout.Parameters();machine,d=layout.build(p,'router')
    y0=d['tool_centers_y'][0]+p.gantry_tool_y_offset;y1=d['tool_centers_y'][1]+p.gantry_tool_y_offset
    obstacles={};gantry_sweeps=[]
    for item in machine:
        if item.name=='ATC_MAGAZINE':continue
        moving=item.group=='gantry' or item.name in ('Y_CARRIAGE_L','Y_CARRIAGE_R','X_AXIS','Z_TOOL_PACKAGE')
        if moving:
            a=bb(item.shape);a[1]+=y0-p.gantry_y;a[4]+=y1-p.gantry_y
            obstacles[item.name+'_FULL_Y_AABB_SWEEP']=box(*a);gantry_sweeps.append(item.name)
        else:obstacles[item.name]=item.shape
    own=fixed()
    sweeps={'MAGAZINE_200MM_X_SWEEP':box(1465,400,800,1825,1000,940),
            'SHUTTER_170MM_Z_SWEEP':box(1653,382,800,1655,1018,1130)}
    checks={};details={}
    for state in ('change','parked'):
        parts=assembly(state)
        hits=clashes(parts,obstacles)
        internal=[];items=list(parts.items())
        for i,(name,a) in enumerate(items):
            internal.extend(clashes({name:a},dict(items[i+1:])))
        checks[state+'_static_machine_clear']=not hits
        checks[state+'_internal_clear']=not internal
        details[state]={'machine_intersections':hits,'internal_intersections':internal}
        assy=cq.Assembly(name='LARGE_RETRACTABLE_ATC_'+state.upper()+'_ALLOCATION_ONLY')
        for name,shape in parts.items():
            color=(.62,.40,.76) if name.startswith('UNVERIFIED') else ((.91,.55,.20) if name.startswith('UNSELECTED') else (.35,.48,.55))
            assy.add(shape,name=name,color=cq.Color(*color))
        path=OUT/(state+'-allocation.step');assy.save(str(path),exportType='STEP')
        reread=cq.importers.importStep(str(path)).val()
        checks[state+'_STEP_readback']=reread.isValid() and len(reread.Solids())==len(parts) and abs(reread.Volume()-sum(s.Volume() for s in parts.values()))<.01
    # Continuous prism sweeps are exact for these translating box allocations.
    details['machine_sweep_intersections']=clashes(sweeps,obstacles)
    checks['continuous_sweeps_clear_machine']=not details['machine_sweep_intersections']
    mag_obstacles={**own,'SHUTTER_OPEN':assembly('change')['SHUTTER_LAYOUT_NO_ACTUATOR']}
    details['magazine_sweep_internal_intersections']=clashes({'MAGAZINE_SWEEP':sweeps['MAGAZINE_200MM_X_SWEEP']},mag_obstacles)
    checks['magazine_sweep_clear_when_shutter_open']=not details['magazine_sweep_internal_intersections']
    shutter_obstacles={**own,'PARKED_MAGAZINE':assembly('parked')['UNVERIFIED_MAGAZINE_CARRIER_TOOL_ENVELOPE']}
    details['shutter_sweep_internal_intersections']=clashes({'SHUTTER_SWEEP':sweeps['SHUTTER_170MM_Z_SWEEP']},shutter_obstacles)
    checks['shutter_sweep_clear_when_magazine_parked']=not details['shutter_sweep_internal_intersections']
    cutter=box(104.6,149.6,900,1475.4,2750.4,1050)
    parked=assembly('parked');deployed=assembly('change')
    details['parked_full_deck_surfacing_intersections']=clashes({'CUTTER_ALLOCATION':cutter},parked)
    checks['parked_full_deck_surfacing_clear']=not details['parked_full_deck_surfacing_intersections']
    forbidden=volume(cutter,deployed['UNVERIFIED_MAGAZINE_CARRIER_TOOL_ENVELOPE'])
    details['deployed_full_deck_surfacing_overlap_mm3']=forbidden
    checks['deployed_surfacing_interlock_required']=forbidden>.01
    gate_hit=volume(sweeps['MAGAZINE_200MM_X_SWEEP'],parked['SHUTTER_LAYOUT_NO_ACTUATOR'])
    details['slide_through_closed_shutter_overlap_mm3']=gate_hit
    checks['closed_shutter_slide_interlock_required']=gate_hit>.01
    checks['stock_rectangle_preserved']=1465>p.sheet_origin_x+p.sheet_x
    checks['inside_existing_frame']=all(bb(s)[0]>=0 and bb(s)[1]>=0 and bb(s)[3]<=p.frame_x and bb(s)[4]<=p.frame_y for s in list(parked.values())+list(deployed.values())+list(sweeps.values()))
    checks['change_line_within_X_travel']=d['tool_centers_x'][0]<1545<d['tool_centers_x'][1]
    checks['pocket_Y_allocation_within_Y_travel']=d['tool_centers_y'][0]<400 and 1000<d['tool_centers_y'][1]
    preview()
    after={name:sha(ROOT/name) for name in before}
    checks['sources_unchanged']=before==after
    artifacts={n:sha(OUT/n) for n in ('change-allocation.step','parked-allocation.step','plan.svg','plan.png')}
    result={'passed':all(checks.values()),'status':'CONDITIONAL ALLOCATION FEASIBILITY ONLY',
            'checks':checks,'details':details,'source_sha256':after,'sources_unchanged':before==after,
            'artifact_sha256':artifacts,'nominal_X_stroke_mm':200.,'moving_envelope_mm':[160.,600.,140.],
            'change_bounds_mm':[1465.,400.,800.,1625.,1000.,940.],
            'park_bounds_mm':[1665.,400.,800.,1825.,1000.,940.],
            'guide_arithmetic':{'nominal_block_length_mm':45.4,'maximum_block_length_mm':45.8,'catalog_pdf_page':91,'catalog_printed_page':88,'catalog_revision':'G99TE24-2410','blocks_per_rail':2,
               'block_center_spacing_mm':80.,'end_margin_mm':10.,'minimum_rail_for_200mm_stroke_mm':345.8,
               'candidate_rail_length_mm':350.,'two_block_group_center_end_margins_mm':[12.1,12.1],
               'travel_with_200mm_rail_two_blocks_mm':54.2,'travel_with_200mm_rail_single_block_mm':134.2,
               'scope':'Length arithmetic only; no rail load/moment rating, selection, holes or motor specification.'},
            'gantry_parts_conservatively_swept_through_full_Y':gantry_sweeps,
            'clearances_mm':{'park_magazine_to_hood_right_wall':3.,'hood_to_Y_carriage_allocation':7.5,'open_shutter_to_lower_gantry_chord':20.,'stage_top_to_surfacing_Z_floor':100.},
            'scope':'Checks the stated box allocations and simple hood sheets against frozen development CAD. Gantry Y uses conservative AABB sweeps; Z/tool is parked at X780 for slide/shutter operations. This does not prove tool engagement, pocket pitch, mounting, support, seals, rigidity or real supplier interfaces.',
            'supplier_interfaces_verified':False,'tool_change_cycle_verified':False,'actuator_or_guides_selected':False,'fabrication_ready':False,
            'sources':{'HIWIN_nominal_length':'https://www.hiwin.de/en/Products/Linear-guideways/Blocks/Miniature-guides/MGN-HIRES-series/MGN12HZ1CM/p/MGN12HZ1CM',
                       'HIWIN_maximum_length':'https://www.hiwin.com/wp-content/uploads/HIWIN-Linear-Guideway-Catalog.pdf#page=91',
                       'RapidChange_width_and_clearance':'https://rapidchangeatc.com/faq/'}}
    (OUT/'feasibility.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':result['passed'],'checks':checks,'details':details},indent=2),flush=True)
    return 0 if result['passed'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
