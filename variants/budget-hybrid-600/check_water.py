"""Check static water volumes and open routing in the budget hybrid review CAD."""
import hashlib
import json
import math
from pathlib import Path

from build_candidate import PAN, OUT, pieces, yz
from frame import box, cyl


def bbox(shape):
    b = shape.BoundingBox()
    return (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)


def overlap(a, b):
    return all(min(a[i+3], b[i+3]) - max(a[i], b[i]) > 1e-5 for i in range(3))


def run():
    fixed, _, _ = pieces()
    parts = {name: shape for name, shape, _ in fixed}
    bounds = {name: bbox(shape) for name, shape in parts.items()}
    front, rear = bounds['pan_end_0'], bounds['pan_end_1']
    x0, x1 = front[0], front[3]
    y0, y1 = front[4], rear[1]
    floor = bounds['pan_floor']
    rise = floor[5] - floor[2] - PAN
    slope = rise / (floor[4]-floor[1])
    floor_z = lambda y: floor[2] + PAN + slope*(y-floor[1])
    front_face = parts['pan_end_0']
    drain_edge = next(e for e in front_face.Edges() if e.geomType() == 'CIRCLE')
    drain_x, _, drain_z = drain_edge.Center().toTuple()
    drain_r = drain_edge.Length()/(2*math.pi)
    notch = next(e for e in front_face.Edges() if e.geomType() == 'LINE' and 70 < e.Length() < 90)
    notch_invert = notch.Center().z
    notch_b = bbox(notch)
    # Lowest exterior rim is a conservative blocked-notch spill datum.
    rim = min(v.Center().z for v in front_face.Vertices() if v.Center().z > notch_invert+1)
    normal = floor_z(floor[1])+34
    immerse = [v for n, v in parts.items() if n.startswith(('comb_', 'slat_'))]

    def volume(z):
        stop = min(y1, y0+(z-floor_z(y0))/slope)
        profile = [(y0, floor_z(y0)), (stop, floor_z(stop))]
        if stop == y1:
            profile.append((stop, z))
        profile.append((y0, z))
        prism = yz(x0, x1-x0, profile)
        gross = prism.Volume()
        displaced = sum(prism.intersect(s).Volume() for s in immerse if overlap(bbox(prism),bbox(s)))
        # Independent analytic integral for a sloping bottom.
        analytic = (x1-x0)*(stop-y0)*(z-(floor_z(y0)+floor_z(stop))/2)
        assert abs(analytic-gross) < 1
        return dict(surface_Z_mm=round(z,5),gross_L=round(gross/1e6,6),
                    displaced_comb_slat_L=round(displaced/1e6,6),water_L=round((gross-displaced)/1e6,6),
                    depth_at_wet_front_mm=round(z-floor_z(y0),4))
    levels = {key:volume(z) for key,z in [('ideal_drain_stop',drain_z-drain_r),('normal',normal),
                                          ('overflow_begins',notch_invert),('first_rim_spill',rim)]}
    # These are artificial *clear flow* gauges, never added to the machine solids.
    notchw = notch.Length()
    overflow_x = notch.Center().x
    gauges = {
        'drain_bore_19_8mm': cyl(drain_r-.1,9,(drain_x,y0-7,drain_z),(0,1,0)),
        'nipple_25_8mm': cyl(12.9,51.2,(305,32.5,775)),
        'notch_into_hood': box(notch_b[0]+.1,49,notch_invert+.1,notchw-.2,9,rim-notch_invert-.2),
        'hood_bottom_outlet': box(overflow_x-19.9,28.1,846,39.8,13.8,4),
    }
    gauge_hits = {g:[n for n in parts if overlap(bbox(shape),bounds[n]) and
                     shape.intersect(parts[n]).Volume()>.05] for g,shape in gauges.items()}
    plumbing = ('drain_drop_box','drain_1in_nipple_envelope','open_drain_chute',
                'open_overflow_chute','overflow_splash_hood','receiver_open_steel_15gal_envelope')
    clashes=[]
    for i,name in enumerate(plumbing):
        for other,shape in parts.items():
            if name==other or (other in plumbing[:i]) or not overlap(bounds[name],bounds[other]):
                continue
            v=parts[name].intersect(shape).Volume()
            if v>.05:
                clashes.append(dict(first=name,second=other,intersect_mm3=round(v,4)))

    # Project the supplier-envelope rim using all four corners of each chute's outlet edge band.
    receiver=bounds[plumbing[-1]]
    cx=(receiver[0]+receiver[3])/2; cy=(receiver[1]+receiver[4])/2
    clear_radius=(receiver[3]-receiver[0])/2-1.5
    chutes={}
    for name in ('open_drain_chute','open_overflow_chute'):
        a=bounds[name]
        z_high=a[5]-12; z_low=a[2]+1.9
        radial=max(math.hypot(x-cx,a[4]-cy) for x in (a[0],a[3]))
        chutes[name]={'center_X_mm':(a[0]+a[3])/2,'run_Y_mm':round(a[4]-a[1],2),
            'fall_mm':round(z_high-z_low,2),'clear_width_mm':round(a[3]-a[0]-3.8,2),
            'vertical_side_return_mm':12.,'inlet_YZ_mm':[round(a[1],2),round(z_high,2)],
            'exit_YZ_mm':[round(a[4],2),round(z_low,2)],
            'static_clearance_to_frame_mm':{n:round(parts[name].distance(parts[n]),3) for n in
                ['end_X_0_0','end_X_0_1','center_post_0','bearer_0']},'edge_to_nominal_receiver_rim_vertical_gap_mm':round(z_low-receiver[5],2),
            'vertical_projection_to_inner_rim_min_margin_mm':round(clear_radius-radial,2)}
    gross=levels['first_rim_spill']['gross_L']
    net=levels['first_rim_spill']['water_L']
    normal_l=levels['normal']['water_L']; crest=levels['overflow_begins']['water_L']
    residual=levels['ideal_drain_stop']['water_L']
    # 2 L provision is conservative for the drawn small cavities and unmodeled fitting/chute inventory;
    # it is a design allowance that must be measured, alongside the real receiver's usable mark.
    usable, hold_up = 48.,2.
    data={
        'source_sha256':{f:hashlib.sha256(Path(__file__).with_name(f).read_bytes()).hexdigest()
                         for f in ('build_candidate.py','check_water.py')},
        'units':'Millimetres, litres; plasma configuration, 12-ga 2.6568 mm steel. Open, unpressurized system.',
        'pan':{'outer_XY_mm':[floor[3]-floor[0],floor[4]-floor[1]],'inner_XY_mm':[round(x1-x0,4),round(y1-y0,4)],
               'floor_rise_along_Y_mm':round(rise,4),'slope_percent':round(100*slope,4),
               'wet_inner_floor_front_Z_mm':round(floor_z(y0),5),'wet_inner_floor_rear_Z_mm':round(floor_z(y1),5),
               'installed_slats_and_combs':len(immerse),'pan_liquid_only':levels,
               'normal_to_notch_L':round(crest-normal_l,4),'normal_to_rim_L':round(net-normal_l,4),
               'notch_to_rim_L':round(net-crest,4),'normal_recoverable_before_line_inventory_L':round(normal_l-residual,4),
               'residual_wet_length_from_front_mm':round((drain_z-drain_r-floor_z(y0))/slope,2),
               'method':'Intersect the interior sloped prism at each level with all three installed combs and ten slats; gross volume cross-checked by analytic integration. No stock, debris, splash or weld beads.'},
        'drain':{'bore_mm':round(2*drain_r,4),'center_XZ_mm':[drain_x,drain_z],'invert_Z_mm':round(drain_z-drain_r,5),
                 'note':'Gravity flow leaves a shallow wedge. Inspect for retained water and debris and dry the machine before switching to wood; include line inventory in receiver sizing.'},
        'overflow':{'slot_X_limits_mm':[notch_b[0],notch_b[3]],'crest_Z_mm':notch_invert,'crest_width_mm':notchw,
                    'head_to_exterior_rim_mm':round(rim-notch_invert,4),'slot_area_below_rim_mm2':round(notchw*(rim-notch_invert),2),
                    'drop_box_clear_width_mm':82.2,'box_top_Z_mm':903.,'centered_bottom_outlet_mm':[40.,14.],
                    'notch_overlap_inside_box_each_side_mm':1.1,'outlet_to_chute_lateral_margin_each_side_mm':9.1,
                    'collector_bottom_to_chute_inlet_surface_Z_difference_mm':round(847-chutes['open_overflow_chute']['inlet_YZ_mm'][1],3),
                    'hood_lip_over_low_rim_mm':round(903.-rim,3),
                    'collector_outlet_XY_mm':[overflow_x-20,28,overflow_x+20,42],
                    'note':'The under-notch collector feeds a centered downward outlet. Its bare 560 mm2 aperture, 1.1 mm side margins and shallow chute returns require wet testing for debris and splashing; this volume check establishes no flow capacity.'},
        'checks':{'open_gauge_intersections_over_0p05_mm3':gauge_hits,'plumbing_fixed_collisions_over_0p05_mm3':clashes,
                  'chutes':chutes,'result':'PASS for modeled static checks' if not clashes and not any(gauge_hits.values()) else 'FAIL; see recorded geometries',
                  'limits':'Selected water hardware and static frame BReps, without real valve/lever, joints, supply flow, jet trajectory, floor pitch, heat, debris, handles, motion cable or splash/dynamic certification. Receiver is a gross shape, use maker 56.8 L, not CAD cylinder volume.'},
        'receiver':{'envelope_center_XY_mm':[cx,cy],'gross_supplier_L':56.8,'minimum_marked_usable_L':usable,'reserved_fitting_and_chute_liquid_L':hold_up,
                    'worst_liquid_bound_L':round(gross+hold_up,5),
                    'initial_max_L_at_worst_gross_pan':round(usable-gross-hold_up,5),
                    'initial_max_L_at_normal_net_pan_conservative':round(usable-normal_l-hold_up,5),
                    'policy':'Drain only into an empty, leak-tested receiver with the usable mark verified. A full receiver has no safe drain or overflow capacity. The separate overflow cannot prevent receiver overflow.'},
        'faults':[
            {'state':'Valve shut, open overflow','outcome':'Liquid rises from normal to crest; at crest water starts into independent return. No passive throughput rating or unattended fill authorization.'},
            {'state':'Valve shut, blocked overflow','outcome':f'Only {net-crest:.2f} L between notch onset and first spill. At a hypothetical constant 5 L/min this is {(net-crest)*12:.1f} s until rim spill. Stop filling; fail-safe procedure required.'},
            {'state':'Valve open, empty receiver','outcome':f'Gravity can recover about {normal_l-residual:.2f} L of normal pan water; add actual drop-box, nipple and fittings inventory. Low wedge and sludge remain.'},
            {'state':'Drain plugged or obstructed','outcome':'An open valve proves neither flow nor emptiness. Visually check level and isolate before cleaning.'},
            {'state':'Receiver at its usable mark','outcome':'Zero remaining safe capacity; drain and additional filling must be inhibited. Pan overflow or opening drain can spill on the floor.'}],
        'acceptance_tests':['Level the actual frame in both axes, leak-test all seams, and measure pan water by weight or calibrated volume at normal, notch onset, rim reference and after gravity draining. Check all three comb bases pass water.',
            'Mark the real receiver usable level only after demonstrating at least 48 L of clean-water capacity with freeboard and allowance for debris. Check tooling, handle/removal path and both chutes against the actual tub.',
            'With tools isolated and a separate spill catch in place, verify the installed valve travel, minimum flow at near-empty head, drain time, venting, plume and both discharge landing zones. Confirm independent overflow functions with drain shut.',
            'Meter the maximum permitted fill rate. Prove clean and partially obstructed overflow routing keeps water below rim with margin at that rate, including splash and blocked-drain conditions; otherwise reduce/prohibit that rate or revise the collector. Deliberately blocked overflow requires stopping the fill before spill. Never continue filling a full receiver.',
            'Repeat with realistic solids capture, strainer and residue. Demonstrate cooling, complete MDF removal before hot work, empty/clean tray before dry conversion and the real independent level isolation if automation is ever added.']}
    OUT.mkdir(exist_ok=True)
    (OUT/'water-check.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:data[k] for k in ['pan','checks','receiver']},indent=2))
    if clashes or any(gauge_hits.values()):
        raise SystemExit(1)

if __name__=='__main__':
    run()
