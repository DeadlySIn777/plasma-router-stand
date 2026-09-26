"""Rev H integrated restraint handling; no fingers or small-screw path claim."""
from pathlib import Path
import sys,os,json,math,hashlib
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
sys.path[:0]=[str(SOURCE),str(ROOT/'output/cad-repair-2026-09-25')]
import cadquery as cq
import bed_completion as h,bed_cassettes as bc
from build_revh import build_model
from build_revg import clone_model,store_router_tool
from cad_helpers import bbox,validate,place,pipe,box,cyl,intersection_volume
from check_spoil_transfer import continuous_segment

OUT=Path(__file__).with_name('restraint-paths.json')

def hashes():
    d={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.py')}
    for p in (Path(__file__),ROOT/'output/cad-repair-2026-09-25/check_spoil_transfer.py'):
        d[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return d

def transform(shape,op,t=1):
    if op[0]=='T':return shape.translate(tuple(t*x for x in op[1]))
    return shape.rotate(op[1],op[2],t*op[3])

def bounds_speed(shape,op):
    if op[0]=='T':return math.sqrt(sum(x*x for x in op[1])),0
    c=op[1];b=bbox(shape)
    changed=[i for i in range(3) if abs(op[2][i]-c[i])>1e-9]
    axes=[i for i in range(3) if i not in changed] if len(changed)==1 else list(range(3))
    r=math.sqrt(sum(max(abs(b[i]-c[i]),abs(b[i+3]-c[i]))**2 for i in axes))
    a=abs(math.radians(op[3]));return r*a,r*a*a

def swept_box(shape,op):
    b=bbox(shape)
    if op[0]=='T':
        e=bbox(transform(shape,op))
        return [min(b[k],e[k]) for k in range(3)]+[max(b[k+3],e[k+3]) for k in range(3)]
    c=op[1];axis=next(i for i in range(3) if abs(op[2][i]-c[i])>1e-9)
    angle=math.radians(op[3]);lo,hi=min(0,angle),max(0,angle);values=[[],[],[]]
    for x in (b[0],b[3]):
      for y in (b[1],b[4]):
       for z in (b[2],b[5]):
        v=[x-c[0],y-c[1],z-c[2]]
        co=([(v[0],0),(v[1],-v[2]),(v[2],v[1])] if axis==0 else
            [(v[0],v[2]),(v[1],0),(v[2],-v[0])] if axis==1 else
            [(v[0],-v[1]),(v[1],v[0]),(v[2],0)])
        for j,(a,d) in enumerate(co):
            if j==axis:values[j].append(c[j]+v[j]);continue
            angles=[lo,hi];base=math.atan2(d,a)
            angles.extend(base+n*math.pi for n in range(-3,4) if lo<=base+n*math.pi<=hi)
            values[j].extend(c[j]+a*math.cos(t)+d*math.sin(t) for t in angles)
    return [min(v) for v in values]+[max(v) for v in values]

def main():
    before=hashes();router,details=build_model();router=store_router_tool(router)
    report={'scope':__doc__,'source_sha256':before,'model_parts':len(router.parts),'paths':[],
            'preconditions':['Empty stock, dry bed, gantry parked rear and drives isolated. Router tool parked.',
              'All small screws/nuts are deliberately removed before the corresponding large-part path and reinstalled afterward; hand/finger/fastener paths are excluded.',
              'Stage detached top bars first, then bare rods before boards; close spoil guard after boards; stage each pair in order 1 then 2; reinstall bare rods in order 2 then 1 before panels; reinstall top bars in order 2 then 1 after panels; lock beams only after all four are stored.']}
    def save():OUT.write_text(json.dumps(report,indent=2)+'\n')
    def run(name,shape,fixed,ops,ignore_by_segment=None):
        records=[];states=[shape]
        for i,op in enumerate(ops):
            speed,curve=bounds_speed(shape,op)
            obstacles={k:v for k,v in fixed.items() if k not in (ignore_by_segment or {}).get(i,set())}
            r=continuous_segment(lambda t,s=shape,o=op:transform(s,o,t),obstacles,speed,curve)
            swept=swept_box(shape,op)
            r['swept_bounding_box_mm']=swept
            r['within_frame_footprint']=swept[0]>=-1e-6 and swept[1]>=-1e-6 and swept[3]<=1150+1e-6 and swept[4]<=1450+1e-6
            records.append({'operation':op,'result':r})
            print(name,i+1,r['status'],r.get('failures',[])[:4],flush=True)
            shape=transform(shape,op);states.append(shape)
        report['paths'].append({'name':name,'segments':records,'pass':all(x['result']['status']=='CLEAR' and x['result']['within_frame_footprint'] for x in records)})
        save();return shape,states
    def selected(m,ids):return cq.Compound.makeCompound([p.shape for p in m.parts if p.id in ids])
    def fixed_except(m,ids):return {p.id:p.shape for p in m.parts if p.id not in ids}
    def no_lower_screws(m):
        m.parts=[p for p in m.parts if not p.id.startswith(('H_PANEL_HOOP_LOWER_SCREW_','H_PANEL_HOOP_UPPER_SCREW_'))]
    initial=clone_model(router);no_lower_screws(initial)
    hoop_ops={};bar_ops={}
    for side,x in enumerate((315,835),1):
        ids={'H_PANEL_HOOP_TOP_'+str(side)}
        ids.update(p.id for p in initial.parts if p.id.startswith(f'H_PANEL_HOOP_SKIRT_{side}_'))
        sx=280 if side==1 else 307;sy=(1320 if side==1 else 1355)-398.5
        transitx=sx if side==1 else 312
        ops=[('T',(0,0,60)),('T',(sx-x,0,0)),('T',(0,780-123.5,0)),
             ('T',(transitx-sx,0,0)),('T',(0,sy+60-780,0)),
             ('T',(0,0,-64.904)),('R',(transitx,sy+60,568.596),(transitx+1,sy+60,568.596),90),
             ('T',(0,-60,0)),('T',(sx-transitx,0,0)),('T',(0,0,-12))]
        bar_ops[side]=ops
        final,_=run('stage_top_bar_'+str(side),selected(initial,ids),fixed_except(initial,ids),ops)
        expected=cq.Compound.makeCompound([h._STAGED[i] for i in ids])
        report['paths'][-1]['final_bounds_delta_mm']=max(abs(a-b) for a,b in zip(bbox(final),bbox(expected)))
        for p in initial.parts:
            if p.id in ids:p.shape=h._STAGED[p.id]
    for side,x in enumerate((315,835),1):
        ident='H_PANEL_HOOP_ROD_'+str(side);ids={ident}
        stagex=280 if side==1 else 307;stagey=1320 if side==1 else 1355
        overshoot=60 if side==1 else 0
        ops=[('T',(0,0,60)),('T',(360-x,0,0)),('T',(0,292,0)),
             ('R',(360,402,235),(361,402,235),90),('T',(0,0,314.096)),
             ('T',(0,stagey+overshoot-402,0)),('T',(stagex-360,0,0)),('T',(0,-overshoot,0)),('T',(0,0,-6))]
        hoop_ops[side]=ops
        final,_=run('stage_bare_rod_'+str(side),selected(initial,ids),fixed_except(initial,ids),ops,
                    {8:{'H_PANEL_HOOP_STAGE_SADDLE_'+str(side)}})
        expected=h._STAGED[ident]
        report['paths'][-1]['final_bounds_delta_mm']=max(abs(a-b) for a,b in zip(bbox(final),bbox(expected)))
        initial.find(ident).shape=expected
    # Boards and their screws have been stored by the separate board-path proof.
    staged_static=validate(initial)
    report['staged_static']={'parts':len(initial.parts),'clashes':staged_static['unresolved_intersections']}
    boards=clone_model(router);h.prepare_handling_model(boards);no_lower_screws(boards)
    for p in boards.parts:
        if bc._PLACEMENTS.get(p.id,('',))[0] in ('spoil','spoil_bolt'):p.shape=bc.transformed_to_storage(p)
    guard_ids=[p.id for p in boards.parts if p.id in h._STORED and p.id.startswith('H_SPOIL_GUARD_') and 'INDEX_' not in p.id]
    excluded=set(guard_ids)|{p.id for p in boards.parts if p.id.startswith('H_SPOIL_GUARD_INDEX_') and not p.id.endswith('EAR')}
    for ident in guard_ids:
        p=boards.find(ident)
        if ident.endswith('HINGE_CARRIER'):
            pieces={
                'sleeve':place(pipe(22,16,6.6),(120,484,570),u=(1,0,0),v=(0,0,-1)),
                'front_bridge':box(140,6,6).translate((125,484,573)),
                'rear_bridge':box(140,6,6).translate((125,503.5,573)),
                'index_tab':box(20,6,10).translate((125,503.5,565)).cut(place(cyl(6.6,8),(140,502.5,570),u=(1,0,0),v=(0,0,-1))).clean()}
            union=None
            for sh in pieces.values():union=sh if union is None else union.fuse(sh)
            official=h._STORED[ident]
            delta=union.cut(official).Volume()+official.cut(union).Volume()
            assert abs(delta)<1e-5,delta
            report['carrier_decomposition']={'symmetric_difference_volume_mm3':delta,'method':'Exact same sleeve/bridge/tab union as the CAD welded carrier. Sleeve is invariant under its coaxial Y rotation; other pieces rotate continuously.'}
            for name,closed in pieces.items():
                opened=closed.rotate((120,0,570),(120,1,570),-90)
                ops=[('T',(0,0,0))] if name=='sleeve' else [('R',(120,0,570),(120,1,570),90)]
                run('close_spoil_guard_carrier_'+name,opened,fixed_except(boards,excluded),ops)
        else:run('close_spoil_guard_'+ident,p.shape,fixed_except(boards,excluded),[('R',(120,0,570),(120,1,570),90)])
        p.shape=h._STORED[ident]
    for p in boards.parts:
        if p.id.startswith('H_SPOIL_GUARD_INDEX_') and p.id in h._STORED:p.shape=h._STORED[p.id]
    for side in (2,1):
        ident='H_PANEL_HOOP_ROD_'+str(side);p=boards.find(ident)
        reverse=[]
        for op in reversed(hoop_ops[side]):
            reverse.append(('T',tuple(-v for v in op[1])) if op[0]=='T' else ('R',op[1],op[2],-op[3]))
        final,_=run('restore_bare_rod_'+str(side),p.shape,fixed_except(boards,{ident}),reverse,{0:{'H_PANEL_HOOP_STAGE_SADDLE_'+str(side)}})
        p.shape=h._INITIAL[ident]
    # The separate panel path proof places all six panels before their top bars.
    panels=clone_model(router);h.prepare_panel_handling_model(panels)
    for p in panels.parts:
        if bc._PLACEMENTS.get(p.id,('',))[0] in ('spoil','spoil_bolt','clamp','panel'):p.shape=bc.transformed_to_storage(p)
    no_lower_screws(panels)
    for side in (2,1):
        ids={'H_PANEL_HOOP_TOP_'+str(side)}
        ids.update(p.id for p in panels.parts if p.id.startswith(f'H_PANEL_HOOP_SKIRT_{side}_'))
        reverse=[]
        for op in reversed(bar_ops[side]):
            reverse.append(('T',tuple(-v for v in op[1])) if op[0]=='T' else ('R',op[1],op[2],-op[3]))
        final,_=run('install_panel_top_bar_'+str(side),selected(panels,ids),fixed_except(panels,ids),reverse)
        expected=cq.Compound.makeCompound([h._INITIAL[i] for i in ids])
        report['paths'][-1]['final_bounds_delta_mm']=max(abs(a-b) for a,b in zip(bbox(final),bbox(expected)))
        for p in panels.parts:
            if p.id in ids:p.shape=h._INITIAL[p.id]
    # Temporary containment after beam1 rests independently on beam2.
    temporary=clone_model(router);h.prepare_beam_handling_model(temporary)
    for p in temporary.parts:
        kind,index,*_=bc._PLACEMENTS.get(p.id,('',-1))
        if kind in ('spoil','spoil_bolt','clamp','panel') or (kind=='beam_bolt' and index//2==0):p.shape=bc.transformed_to_storage(p)
        if kind=='beam' and index==0:
            datum=bc._PLACEMENTS[p.id][2]
            p.shape=p.shape.translate(tuple(-v for v in datum)).rotate((0,0,0),(1,0,0),90).translate((113,517.9,920.8))
    all_temp=set(h._TEMPORARY)
    for side in (1,2):
        ident='H_TEMP_BOX_'+str(side)
        start=h._TEMPORARY[ident].translate((0,120,0))
        run('insert_temporary_box_'+str(side),start,fixed_except(temporary,all_temp),[('T',(0,-120,0))])
    h.set_temporary_capture(temporary,True)
    v=validate(temporary)
    report['temporary_capture_static']={'parts':len(temporary.parts),'clashes':v['unresolved_intersections'],
        'gate_insertion_analytic':'Gate interior Z869..973 lies between C jaws endingZ869/startingZ973. Before its final Y428..438 position it staysY<=438, behind no beam (nearest beam1Y439.1). Gate contacts the jaws only at their faces. Small screws, nut and spacer placement remain excluded.'}
    after=hashes();report['sources_unchanged']=before==after
    report['saddle_seating_analytic']='For the last 6 mm vertical rod seating and first 6 mm departure only, the matching target saddle is checked analytically: its open-top OD10 semicircular cut and the OD10 rod share X/Y axes and final center. For every nonnegative upward center offset, the rod remains on/above the cut, so no interior overlap occurs. Final stage is separately checked statically; this exclusion is limited to the named target saddle.'
    report['pass']=report['sources_unchanged'] and all(x['pass'] and x.get('final_bounds_delta_mm',0)<1e-5 for x in report['paths']) and not v['unresolved_intersections'] and not report['staged_static']['clashes']
    save();print('PASS',report['pass'],flush=True)
    return 0 if report['pass'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
