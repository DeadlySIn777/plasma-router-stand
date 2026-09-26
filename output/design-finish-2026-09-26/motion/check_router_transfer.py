"""Ordered disconnected router-tool transfer on frozen Rev I CAD.

The retained panel1 and captured beam1 preparation is proved separately by
check_transfer_staging.py. Nominal rigid geometry does not prove hand access,
operator ability, cable handling, clamp preload or actual purchased details.
"""
from pathlib import Path
import hashlib,json,math,os,sys,traceback
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'output/release-review/RevE-ENGINEERING'
OLD=ROOT/'output/cad-repair-2026-09-25'
sys.path[:0]=[str(SOURCE),str(OLD),str(ROOT/'output/design-finish-2026-09-26/structure')]
import cadquery as cq
import build_revi as builder,bed_cassettes as bc,bed_completion as h
import check_transfer_staging as staging
from build_revg import clone_model,store_router_tool
from cad_helpers import bbox,place,validate,intersection_volume
from check_spoil_transfer import continuous_segment
from check_reinforced_paths import transform,bounds_speed,swept_box
OUT=Path(__file__).with_name('router-transfer-verification.json')
TOOL_IDS={'TOOL_SPINDLE_65x259','TOOL_SPLIT_CLAMP_REAR','TOOL_SPLIT_CLAMP_FRONT','TOOL_CLAMP_PINCH_1','TOOL_CLAMP_PINCH_2'}

def sources():
    paths=list(SOURCE.glob('*.py'))+[Path(__file__),Path(staging.__file__),OLD/'check_spoil_transfer.py',ROOT/'output/design-finish-2026-09-26/structure/check_reinforced_paths.py']
    return {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def prepared_model(router):
    """Boards/panels stored, beam1 captured on beam2, front seats removed."""
    return staging.build_beam_on_second_model(router)

def main():
    before=sources();router,_=builder.build_model();m=prepared_model(router);parked=store_router_tool(router)
    for p in m.parts:
        if p.id.startswith('TOOL_CLAMP_PINCH_'):p.shape=parked.find(p.id).shape
    report={'source_sha256':before,'builder':'build_revi','status':'RUNNING','states':{},'paths':[],
      'scope':__doc__, 'preconditions':[
       'Machine electrically isolated; cutter and spindle cable disconnected. Gantry parked rear/high at X575/Y1275/Z100. No actual torch installed.',
       'Complete the separately proved rear-panel1 table and beam1-on-beam2 preparation. Fit both temporary keepers before removing front seats; beam1 remains captured above beam2 throughout this procedure.',
       'Keep other five panels and all six boards in their defined internal storage, rack rods restored and top bars staged. Do not lower beam1 into the front rack yet: the spindle needs the full 105mm front portal.',
       'Support the 2.7kg spindle continuously before releasing its two pinch screws and front cap. The rear half stays bolted to the adapter until the spindle rests in its cradles. A helper may handle the cap; no unmodeled fixture is assumed.',
       'Front cap rests flat on clean/dry panel1 at X350..460/Y970..1014.75/Z940.8. Remove it to its permanent lid location before any head parts use the table.',
       'Small fastener paths, fingers and grip envelopes are not proved. Pinch screws go to their existing tray locations before cap removal; four rear-clamp mount screws go there only after the spindle is supported in the cradles.',
       'For restoration first recreate the same panel1/beam1 preparation with the plasma head returned to its parking cradle. Reverse the four transfer routes in order; secure rear-clamp mount screws before returning the spindle and fit pinch screws last.'
      ], 'limits':['Rigid nominal envelope only; no hands, tolerance/deformation, lead or collet extensions included.','Real spindle connector and clamp dimensions must match or remain within the represented envelope.','Temporary table support and ordinary hand support are not load-rated lifting fixtures.','Straps, final clamp torque, purchased attachment interfaces and physical commissioning remain separate acceptance work.']}
    history=[]
    def save():OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def state(label):
        v=validate(m);report['states'][label]={'parts':len(m.parts),'clashes':v['unresolved_intersections']};print('STATE',label,report['states'][label],flush=True);save()
    def run(name,ids,ops,remember=True):
        pieces={i:m.find(i).shape for i in ids};shape=cq.Compound.makeCompound(list(pieces.values()));fixed={p.id:p.shape for p in m.parts if p.id not in ids};segments=[]
        print('START',name,bbox(shape),flush=True)
        for label,op in ops:
            speed,curve=bounds_speed(shape,op);sweep=swept_box(shape,op)
            fn=lambda t,s=shape,o=op:transform(s,o,t)
            if '--probe' in sys.argv:
                failures=[]
                for t in [i/10 for i in range(11)]:
                    sh=fn(t);bb=bbox(sh)
                    for k,s in fixed.items():
                        ob=bbox(s)
                        if all(min(bb[i+3],ob[i+3])-max(bb[i],ob[i])>1e-6 for i in range(3)):
                            v=intersection_volume(sh,s)
                            if v>1e-5:failures.append({'obstacle':k,'t':t,'intersection_mm3':v})
                r={'status':'SAMPLED_CLEAR' if not failures else 'FAILED','failures':failures}
            else:
                tested_fixed=fixed.copy();relative_proofs=[]
                # Two split-clamp interfaces start/end at exact bore contact.
                # Prove their entire relative motion by an exact swept solid,
                # then retain every other fixed obstacle in the distance test.
                if op[0]=='T' and op[1][0]==op[1][2]==0 and abs(op[1][1])>0:
                    cylinder=None;target=None;relative_dy=None;pair=None
                    if ids=={'TOOL_SPLIT_CLAMP_FRONT'} and label in ('detach_forward','reverse_detach_forward'):
                        cylinder=fixed['TOOL_SPINDLE_65x259'];target=shape;relative_dy=-op[1][1];pair='TOOL_SPINDLE_65x259'
                    elif ids=={'TOOL_SPINDLE_65x259'} and label in ('withdraw_from_rear_clamp','reverse_withdraw_from_rear_clamp'):
                        cylinder=shape;target=fixed['TOOL_SPLIT_CLAMP_REAR'];relative_dy=op[1][1];pair='TOOL_SPLIT_CLAMP_REAR'
                    if cylinder is not None:
                        b=bbox(cylinder);assert abs(b[3]-b[0]-65)<1e-6 and abs(b[4]-b[1]-65)<1e-6 and abs(b[5]-b[2]-259)<1e-6
                        cx=(b[0]+b[3])/2;cy=(b[1]+b[4])/2
                        swept=cq.Workplane('XY').center(cx,cy+relative_dy/2).slot2D(65+abs(relative_dy),65,90).extrude(259).val().translate((0,0,b[2]))
                        overlap=intersection_volume(swept,target)
                        relative_proofs.append({'pair':pair,'method':'Exact relative swept Ø65 x259 cylinder along Y; capsule cross section extruded along Z.','intersection_mm3':overlap,'passed':overlap<1e-5})
                        if overlap<1e-5:tested_fixed.pop(pair)
                r=continuous_segment(fn,tested_fixed,speed,curve)
                if relative_proofs:r['exact_relative_bore_sweep_checks']=relative_proofs
                # The final spindle seating/initial unseating is a straight
                # translation of an exact circular cylinder along global Z.
                # Its exact continuous union is a capsule extruded along X.
                # This tests every obstacle if a distance bound stalls at the
                # intentional final seat contact; no pair is omitted.
                if ids=={'TOOL_SPINDLE_65x259'} and op[0]=='T' and abs(op[1][2])>0 and op[1][0]==op[1][1]==0 and r['status']!='CLEAR':
                    b=bbox(shape)
                    if abs((b[3]-b[0])-259)<1e-6 and abs((b[4]-b[1])-65)<1e-6 and abs((b[5]-b[2])-65)<1e-6:
                        dz=op[1][2];cy=(b[1]+b[4])/2;cz=(b[2]+b[5])/2
                        swept=cq.Workplane('YZ').center(cy,cz+dz/2).slot2D(65+abs(dz),65,90).extrude(259).val().translate((b[0],0,0))
                        sb=bbox(swept);tests=[]
                        for ident,obstacle in fixed.items():
                            ob=bbox(obstacle)
                            if all(min(sb[k+3],ob[k+3])-max(sb[k],ob[k])>1e-7 for k in range(3)):
                                tests.append({'obstacle':ident,'intersection_mm3':intersection_volume(swept,obstacle)})
                        r['exact_continuous_capsule_refinement']={'method':'Exact cylinder-plus-vertical-segment Minkowski sum, extruded 259mm along X; all bounding candidates tested.','candidate_tests':tests,'original_distance_failures':r['failures']}
                        if all(t['intersection_mm3']<1e-5 for t in tests):r['status']='CLEAR';r['failures']=[]
            r['swept_bounds_mm']=sweep;r['in_footprint']=sweep[0]>=-1e-6 and sweep[1]>=-1e-6 and sweep[3]<=1150+1e-6 and sweep[4]<=1450+1e-6
            segments.append({'name':label,'operation':op,**r});shape=fn(1)
            for k,s in pieces.items():pieces[k]=transform(s,op)
            print(name,label,r['status'],r['in_footprint'],r['failures'][:5],bbox(shape),flush=True)
            report['paths']=[p for p in report['paths'] if p['name']!=name]+[{'name':name,'ids':sorted(ids),'segments':segments}];save()
        for k,s in pieces.items():m.find(k).shape=s
        if remember:history.append((name,ids,ops))
        return pieces
    state('prepared_router_mounted')
    run('front_cap_to_panel1',{'TOOL_SPLIT_CLAMP_FRONT'},[
      ('detach_forward',('T',(0,-80,0))),
      ('left_over_panel1',('T',(-170,0,0))),
      ('position_over_panel1',('T',(0,-26.4,0))),
      ('set_flat_on_panel1',('T',(0,0,-244.2))),
    ])
    state('front_cap_on_panel1_spindle_supported_by_operator')
    run('bare_spindle_to_cradle',{'TOOL_SPINDLE_65x259'},[
      ('withdraw_from_rear_clamp',('T',(0,-80,0))),
      ('right_to_clear_restored_rack_rod',('T',(325,0,0))),
      ('forward_to_open_portal',('T',(0,70-(1121.4-80),0))),
      ('lower_vertical_in_open_portal',('T',(0,0,-710))),
      ('rearward_vertical_past_cabinet',('T',(0,530,0))),
      ('left_to_rotation_axis_behind_cabinet',('T',(-35,0,0))),
      ('turn_horizontal_behind_cabinet',('R',(865,600,350),(865,601,350),90)),
      ('raise_to_low_route',('T',(0,0,270))),
      ('left_behind_cabinet',('T',(-365,0,0))),
      ('rearward_left_of_cradles',('T',(0,480,0))),
      ('axial_insertion_through_cradles',('T',(260.5,0,0))),
      ('lower_into_cradle',('T',(0,0,-20.3))),
    ])
    state('bare_spindle_on_cradles')
    for p in m.parts:
        if p.id.startswith('TOOL_CLAMP_MOUNT_'):p.shape=parked.find(p.id).shape
    run('rear_clamp_to_lid',{'TOOL_SPLIT_CLAMP_REAR'},[
      ('detach_forward',('T',(0,-80,0))),('right_to_portal',('T',(325,0,0))),
      ('front_to_portal',('T',(0,50-1041.65,0))),('lower_in_portal',('T',(0,0,-585))),
      ('rearward_past_cabinet',('T',(0,550,0))),('left_to_bypass_lane',('T',(-415,0,0))),
      ('rearward_past_staged_guard_foot',('T',(0,580,0))),('left_to_park',('T',(-130,0,0))),('lower_to_lid',('T',(0,0,-166.904))),
    ])
    run('front_cap_from_panel1_to_lid',{'TOOL_SPLIT_CLAMP_FRONT'},[
      ('lift_from_table',('T',(0,0,40))),('right_to_portal',('T',(495,0,0))),
      ('front_to_portal',('T',(0,-920,0))),('lower_in_portal',('T',(0,0,-380.8))),
      ('rearward_past_cabinet',('T',(0,550,0))),('left_to_bypass_lane',('T',(-415,0,0))),
      ('rearward_past_staged_guard_foot',('T',(0,630,0))),('left_to_park',('T',(-130,0,0))),('lower_to_lid',('T',(0,0,-166.904))),
    ])
    state('router_tool_all_parked')
    body_ids={'TOOL_SPINDLE_65x259','TOOL_SPLIT_CLAMP_REAR','TOOL_SPLIT_CLAMP_FRONT'}
    def difference(a,b):return a.cut(b).Volume()+b.cut(a).Volume()
    report['permanent_parking_matches']=[{'part':i,'symmetric_difference_mm3':difference(m.find(i).shape,parked.find(i).shape)} for i in sorted(body_ids)]
    for name,ids,ops in reversed(history.copy()):
        inverse=[]
        for label,op in reversed(ops):
            rev=('T',tuple(-v for v in op[1])) if op[0]=='T' else ('R',op[1],op[2],-op[3])
            inverse.append(('reverse_'+label,rev))
        run('restore_'+name,ids,inverse,remember=False)
        if name=='rear_clamp_to_lid':
            for p in m.parts:
                if p.id.startswith('TOOL_CLAMP_MOUNT_'):p.shape=router.find(p.id).shape
    for p in m.parts:
        if p.id.startswith('TOOL_CLAMP_PINCH_'):p.shape=router.find(p.id).shape
    state('router_tool_restored')
    report['restoration_matches']=[{'part':i,'symmetric_difference_mm3':difference(m.find(i).shape,router.find(i).shape)} for i in sorted(body_ids)]
    report['sources_unchanged']=before==sources()
    report['passed']='--probe' not in sys.argv and report['sources_unchanged'] and not any(s['clashes'] for s in report['states'].values()) and all(s['status']=='CLEAR' and s['in_footprint'] for p in report['paths'] for s in p['segments']) and all(r['symmetric_difference_mm3']<1e-5 for r in report['permanent_parking_matches']+report['restoration_matches'])
    report['status']='PASS' if report['passed'] else ('PROBE_ONLY' if '--probe' in sys.argv else 'FAILED_OR_UNRESOLVED')
    save();print('ROUTER_TRANSFER',report['status'],flush=True)
    return 0 if report['passed'] or '--probe' in sys.argv else 2
if __name__=='__main__':
    try:code=main()
    except Exception:traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
