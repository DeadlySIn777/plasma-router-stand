"""Actual bare-carrier extraction route; no fabricated magazine/suspension claim."""
from pathlib import Path
import sys,math,json,hashlib,os,time
import cadquery as cq
import build_small_atc as b
sys.path.insert(0,str(b.ROOT/'output/cad-repair-2026-09-25'))
from check_spoil_transfer import continuous_segment
from cad_helpers import Model,bbox,intersection_volume

def yaw_footprint(shape,cx=575,cy=930):
    """Analytic XY extrema of every face AABB corner through 0..90degrees.

    Face boxes enclose curved surfaces as well as edges. Using individual face
    boxes avoids the nonexistent outer corner of the entire T-shaped carrier.
    """
    xs=[];ys=[];count=0
    for face in shape.Faces():
        bb=bbox(face)
        for x in (bb[0],bb[3]):
            for y in (bb[1],bb[4]):
                px=x-cx;py=y-cy;angles=[0,math.pi/2]
                for raw in (math.atan2(-py,px),math.atan2(px,py)):
                    angles += [raw+k*math.pi for k in range(-2,3) if 0<=raw+k*math.pi<=math.pi/2]
                for t in angles:
                    xs.append(cx+px*math.cos(t)-py*math.sin(t));ys.append(cy+px*math.sin(t)+py*math.cos(t))
                count+=1
    bounds=[min(xs),min(ys),max(xs),max(ys)]
    return {'method':'Analytical sine/cosine endpoint and stationary-angle extrema of all individual face AABB corners; conservative enclosure of each surface.',
            'face_corner_count':count,'continuous_xy_bounds_mm':bounds,
            'within_1150x1450':bounds[0]>=0 and bounds[1]>=0 and bounds[2]<=1150 and bounds[3]<=1450,
            'minimum_outline_margin_mm':min(bounds[0],bounds[1],1150-bounds[2],1450-bounds[3])}

def continuous_rigid_pieces(fn,moving,fixed,speed,curvature):
    # A rigid assembly is clear exactly when every constituent solid is clear.
    # Separate boxes avoid the very loose whole-assembly T-shaped bounding box.
    n=len(moving);records=[]
    for i,p in enumerate(moving):
        r=continuous_segment(lambda t,p=p:fn(t,p.shape),fixed,speed,curvature)
        r.update(solid_index=i,component_id=p.id);records.append(r)
        print(' ',p.id,r['status'],flush=True)
    return {'status':'CLEAR' if all(r['status']=='CLEAR' for r in records) else 'FAILED_OR_UNRESOLVED',
            'solid_count':n,'distance_queries':sum(r['distance_queries'] for r in records),
            'max_subdivision_depth':max(r['max_subdivision_depth'] for r in records),
            'failures':[{'solid_index':r['solid_index'],**f} for r in records for f in r['failures']],
            'component_proofs':records}

def main():
    start=time.monotonic();before=b.source_map()
    solver=b.ROOT/'output/cad-repair-2026-09-25/check_spoil_transfer.py'
    before[str(solver.relative_to(b.ROOT))]=hashlib.sha256(solver.read_bytes()).hexdigest()
    before[str(Path(__file__).relative_to(b.ROOT))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    dock,meta=b.build_dock();baseline,_=b.build_revi.build_model(gantry_y=275,head_x=575,z_lift=100)
    moving=[p for p in dock.parts if p.id=='SATC_REMOVABLE_CARRIER' or any(v in p.id for v in('_RECEIVER','_BUSH','_CARRIER_BOLT_','_CARRIER_DOWEL_'))]
    removed=[p for p in dock.parts if p.id.startswith('SATC_CLAMP_')]
    movingids={p.id for p in moving};removedids={p.id for p in removed}
    fixed={p.id:p.shape for p in baseline.parts+dock.parts if p.id not in movingids|removedids}
    original=cq.Compound.makeCompound([p.shape for p in moving])
    phases=[]
    up=lambda t,shape=original:shape.translate((0,0,20*t))
    raised=up(1)
    forward=lambda t,shape=original:up(1,shape).translate((0,-225*t,0))
    translated=forward(1)
    settle=lambda t,shape=original:forward(1,shape).translate((0,0,-t))
    turning=settle(1)
    footprint=yaw_footprint(turning)
    turn=lambda t,shape=original:settle(1,shape).rotate((575,930,0),(575,930,1),90*t)
    turned=turn(1)
    overhead=lambda t,shape=original:turn(1,shape).translate((0,0,700*t))
    radial=max(math.hypot(x-575,y-930) for p in moving for x in(bbox(p.shape)[0],bbox(p.shape)[3]) for y in(bbox(p.shape)[1]-225,bbox(p.shape)[4]-225))
    for name,fn,speed,curvature in [('unseat20',up,20,0),('translate_forward225',forward,225,0),
                                  ('lower1_for_receiver_to_datum_vertical_clearance',settle,1,0),
                                  ('yaw90_inside_frame',turn,radial*math.pi/2,radial*(math.pi/2)**2),
                                  ('lift_to_overhead_allocation700',overhead,700,0)]:
        print('Checking',name,flush=True)
        # Direct continuous proof, not sampled endpoint acceptance. Axial
        # extraction of the two pins follows their supplier diameter bound and
        # coaxial through bores. Exclude only those pins for this segment.
        selected=fixed if name!='unseat20' else {k:s for k,s in fixed.items() if k not in('SATC_LOC_1_PIN','SATC_LOC_2_PIN')}
        r=continuous_rigid_pieces(fn,moving,selected,speed,curvature)
        if name=='unseat20':r['axial_pin_clearance_proof']={'pin_maximum_diameter_mm':9.995,'minimum_installed_bush_ID_mm':10.013,
            'minimum_radial_clearance_mm':.009,'wing_bore_mm':12,'direction':'Pure +Z, shared axes unchanged; upper pin taper narrows. Full installed bush fit must be measured.',
            'excluded_from_distance_solver':['SATC_LOC_1_PIN','SATC_LOC_2_PIN'],'method':'Analytic coaxial containment, not a collision waiver.'}
        r.update(name=name,start_bounds_mm=bbox(fn(0)),end_bounds_mm=bbox(fn(1)))
        phases.append(r);print(name,r['status'],flush=True)
        if r['status']!='CLEAR':break
    print('Checking additional center routing limit pose',flush=True)
    center,_=b.build_revi.build_model(gantry_y=1063.6,head_x=575,z_lift=0)
    center_case=b.clashes_with(dock,center)
    center_case.update(tool_axis_mm=[575,910],z_lift_mm=0)
    after=b.source_map()
    after[str(solver.relative_to(b.ROOT))]=hashlib.sha256(solver.read_bytes()).hexdigest()
    after[str(Path(__file__).relative_to(b.ROOT))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report={'scope':'Bare carrier plus attached metal receivers/bushes/bolts/dowels; actual RapidChange magazine, tools, electrical leads and handling apparatus excluded.',
            'prerequisites':['Gantry frontY275, X575, Zlift100. Machine stopped; spindle tool absent.',
                'Four carrier drawbolts and fourwashers removed; their small-part transfer is not included.',
                'No claimed owned lifting device. Positive suspension/restraint and overhead support must be designed before this route is executable.'],
            'source_sha256':after,'sources_changed_during_check':before!=after,
            'moving_part_ids':[p.id for p in moving],'removed_hardware_ids':sorted(removedids),
            'phases':phases,'complete_geometry_route_pass':len(phases)==5 and all(p['status']=='CLEAR' for p in phases) and before==after and footprint['within_1150x1450'],
            'additional_routing_center_pose':center_case,
            'parking_support_designed':False,'actual_magazine_fit_verified':False,'full_mode_conversion_proved':False,
            'footprint_analysis':footprint,
            'translation_footprint_method':'For every pure translation, XY coordinates lie between corresponding endpoint coordinates; all phase endpoint bounds must be inside1150x1450.',
            'yaw_radius_mm':radial,'yaw_bounding_disc_xy_mm':[575-radial,930-radial,575+radial,930+radial],
            'overhead_final_bounds_mm':bbox(overhead(1)),'elapsed_seconds':time.monotonic()-start}
    report['translation_footprint_pass']=all(bb[0]>=0 and bb[1]>=0 and bb[3]<=1150 and bb[4]<=1450 for r in phases for bb in(r['start_bounds_mm'],r['end_bounds_mm']))
    report['complete_geometry_route_pass'] &= report['translation_footprint_pass']
    (b.OUT/'carrier-route-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('BARE_CARRIER_ROUTE',report['complete_geometry_route_pass'],flush=True)
    return 0 if report['complete_geometry_route_pass'] else 1

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
