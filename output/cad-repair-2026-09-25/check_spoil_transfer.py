"""Continuous clearance proof for ordered bare spoilboard exchange.

Does not prove human reach, finger clearance, or hardware removal.
Already stored boards are obstacles. All spoilboard screws are already removed.
"""
from pathlib import Path
import hashlib,json,math,sys,os
SOURCE=Path(__file__).resolve().parents[1]/'release-review'/'RevE-ENGINEERING'
sys.path.insert(0,str(SOURCE))
from cad_helpers import bbox,place,intersection_volume
from build_revg import build_model
import bed_cassettes as bc

def overlaps(a,b):
    return all(min(a[k+3],b[k+3])-max(a[k],b[k])>1e-7 for k in range(3))

def continuous_segment(shape_at, fixed, speed_bound, curvature_bound=0):
    """Distance is 1-Lipschitz: midpoint gap >= max point displacement proves no overlap.

    Shapes rotate/translate with the supplied uniform speed bound (mm per unit t).
    Endpoint swept bounds are enlarged by max coordinate second derivative /8.
    Pure translations have zero curvature. Yaw uses a bound from its exact sin/cos.
    """
    records=[]; calls=0;max_depth=0;failure=[]
    cache={}
    def shape(t):
        if t not in cache:cache[t]=shape_at(t)
        return cache[t]
    def recurse(a,b,obstacles,depth=0):
        nonlocal calls,max_depth
        max_depth=max(max_depth,depth)
        sa,sb=shape(a),shape(b);ba,bb=bbox(sa),bbox(sb)
        inflate=curvature_bound*(b-a)**2/8
        swept=[min(ba[k],bb[k])-inflate for k in range(3)]+[max(ba[k+3],bb[k+3])+inflate for k in range(3)]
        candidates=[p for p in obstacles if overlaps(swept,p[2])]
        if not candidates:return
        mid=(a+b)/2;sm=shape(mid);motion=speed_bound*(b-a)/2
        unresolved=[]
        for ident,s,bb_fixed in candidates:
            calls+=1;distance=sm.distance(s)
            if distance<1e-7:
                vol=intersection_volume(sm,s)
                if vol>1e-5:
                    failure.append({'obstacle':ident,'t':mid,'intersection_mm3':vol});continue
            if distance+1e-7>=motion:continue
            unresolved.append((ident,s,bb_fixed))
        if not unresolved:return
        if depth>=16:
            failure.extend({'obstacle':p[0],'interval':[a,b],'status':'UNRESOLVED_DISTANCE_BOUND'} for p in unresolved);return
        recurse(a,mid,unresolved,depth+1);recurse(mid,b,unresolved,depth+1)
    obstacles=[(k,s,bbox(s)) for k,s in fixed.items()]
    recurse(0,1,obstacles)
    return {'status':'CLEAR' if not failure else 'FAILED_OR_UNRESOLVED','distance_queries':calls,'max_subdivision_depth':max_depth,'failures':failure}

def main():
    start_hash=hashlib.sha256((SOURCE/'bed_cassettes.py').read_bytes()).hexdigest()
    m,details=build_model();fixed={p.id:p.shape for p in m.parts}
    for p in m.parts:
        # Nuts remain in their top slots until the boards have been lifted off.
        # Their later removal precedes panel handling and is outside this proof.
        if bc._PLACEMENTS.get(p.id,('',))[0]=='spoil_bolt':fixed[p.id]=bc.transformed_to_storage(p)
    records=[]
    order=(3,2,1,0,5,4)
    for i in order:
        p=m.find(f'G_SPOIL_{i+1}');fixed.pop(p.id)
        length=bc.SPOIL_Y[i//2][1]-bc.SPOIL_Y[i//2][0]
        slot=bc.SPOIL_STORE_SLOT[i];sx=135+23*slot
        phases=[]
        phases.append(('lift_from_panel',continuous_segment(lambda t:p.shape.translate((0,0,40*t)),fixed,40)))
        lifted=p.shape.translate((0,0,40))
        bx=bc.SPOIL_X[i%2];ya=bc.SPOIL_Y[i//2][0]
        delta=(135-bx,393.5-ya,0)
        phases.append(('move_horizontal_to_front',continuous_segment(lambda t:lifted.translate(tuple(d*t for d in delta)),fixed,math.sqrt(sum(d*d for d in delta)))))
        front=lifted.translate(delta)
        rz_radius=math.hypot(393.5,length)
        rz=lambda t:front.rotate((135,393.5,980.8),(135,393.5,981.8),-90*t)
        phases.append(('turn_horizontal_board',continuous_segment(rz,fixed,rz_radius*math.pi/2,rz_radius*(math.pi/2)**2)))
        across=rz(1)
        rx_radius=math.hypot(393.5,18)
        rx=lambda t:across.rotate((135,393.5,980.8),(136,393.5,980.8),-90*t)
        phases.append(('stand_board_above_front',continuous_segment(rx,fixed,rx_radius*math.pi/2,rx_radius*(math.pi/2)**2)))
        upright=rx(1)
        phases.append(('move_standing_board_to_drop',continuous_segment(lambda t:upright.translate((0,-393.5*t,0)),fixed,393.5)))
        standing=upright.translate((0,-393.5,0))
        phases.append(('vertical_front_drop',continuous_segment(lambda t:standing.translate((0,0,-745.8*t)),fixed,745.8)))
        low=standing.translate((0,0,-745.8))
        right_local=low.translate((-135-length,0,-235))
        def yaw(t):
            theta=math.pi/2*t
            return right_local.rotate((0,0,0),(0,0,1),-90*t).translate((135+length*math.cos(theta),0,235))
        radius=math.sqrt(length**2+18**2)
        phases.append(('yaw_below_pan',continuous_segment(yaw,fixed,radius*math.pi/2,radius*(math.pi/2)**2)))
        turn=yaw(1)
        phases.append(('move_to_slot_x',continuous_segment(lambda t:turn.translate(((sx-135)*t,0,0)),fixed,sx-135)))
        atx=turn.translate((sx-135,0,0))
        phases.append(('slide_rear',continuous_segment(lambda t:atx.translate((0,250*t,0)),fixed,250)))
        rear=atx.translate((0,250,0))
        phases.append(('lower_to_runner',continuous_segment(lambda t:rear.translate((0,0,-60*t)),fixed,60)))
        final=rear.translate((0,0,-60))
        official=bc.transformed_to_storage(p)
        bb_delta=max(abs(a-b) for a,b in zip(bbox(final),bbox(official)))
        rec={'board':i+1,'slot':slot+1,'handling_width_mm':length,'standing_height_mm':393.5,'final_bounds_delta_mm':bb_delta,'phases':dict(phases)}
        records.append(rec);fixed[p.id]=final
        print(json.dumps({'board':i+1,'phases':{k:v['status'] for k,v in phases},'queries':sum(v['distance_queries'] for k,v in phases)}),flush=True)
    end_hash=hashlib.sha256((SOURCE/'bed_cassettes.py').read_bytes()).hexdigest()
    result={'scope':'All prescribed bare-board motions from installed state through internal storage, after all spoilboard screws are already removed. Human handling, finger clearance and hardware-transfer paths excluded.',
            'hardware_sequence':'All24 spoilboard screws are pre-stored; the24 top-slot nuts remain installed during every board movement. Nuts are removed/stored only after all boards and before the panels; that small-part transfer is not proven here.',
            'source_sha256':start_hash,'source_unchanged_during_check':start_hash==end_hash,
            'method':'Exact B-rep midpoint minimum distance with conservative per-point displacement bound; adaptive subdivision. Coordinates use exact prescribed linear and sinusoidal transforms. Existing parked boards remain fixed obstacles.',
            'analytic_xy_swept_bounds_mm':[135,0,970,1110],
            'footprint_check':'The entire prescribed XY path lies inside the nominal frame rectangle X0..1150/Y0..1450. Linear segments stay between their endpoints. Horizontal quarter-turn maximum X is 135+hypot(393.5,397)<695 and Y is 0..790.5; standing turn stays X135..532 and Y0..411.5; lower yaw stays X135..135+hypot(397,18)<533 and Y0..hypot(397,18)<398.',
            'maximum_prescribed_height_mm':980.8+math.hypot(393.5,18),
            'model_parts':len(m.parts),'order':[i+1 for i in order],'records':records}
    result['pass']=start_hash==end_hash and all(v['status']=='CLEAR' for r in records for v in r['phases'].values()) and max(r['final_bounds_delta_mm'] for r in records)<1e-5
    out=Path(__file__).with_name('spoil-transfer-check.json');out.write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',result['pass'],flush=True)
    return 0 if result['pass'] else 2

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
