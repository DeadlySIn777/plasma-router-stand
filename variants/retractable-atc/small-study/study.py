"""Source-bound small retractable-ATC envelope study. No frozen-source mutations."""
from pathlib import Path
import hashlib, json, math, os, sys
import cadquery as cq

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
CACHE = ROOT/'output/release-review/RevI-CAD/RevI_ROUTER-validation.json'
OLD_STEP = ROOT/'variants/small-atc/output/parts/SATC_CARRIER_WELDMENT.step'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def moved(b,dy=0,dz=0): return [b[0],b[1]+dy,b[2]+dz,b[3],b[4]+dy,b[5]+dz]
def sweep(b,dx=0,dy=0,dz=0):
    return [b[0]+min(0,dx),b[1]+min(0,dy),b[2]+min(0,dz),b[3]+max(0,dx),b[4]+max(0,dy),b[5]+max(0,dz)]
def overlap(a,b): return math.prod(max(0,min(a[k+3],b[k+3])-max(a[k],b[k])) for k in range(3))
def box(b): return cq.Workplane('XY').box(*(b[k+3]-b[k] for k in range(3)),centered=False).val().translate(tuple(b[:3]))
def bounds(s):
    b=s.BoundingBox(); return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def inside(b): return b[0]>=0 and b[3]<=1150 and b[1]>=0 and b[4]<=1450

def main():
    inputs=[Path(__file__),OUT/'README.md',CACHE,OLD_STEP,
        ROOT/'variants/small-atc/build_small_atc.py',
        ROOT/'variants/small-atc/output/fit-report.json',
        ROOT/'variants/small-atc/output/interface.json',
        ROOT/'variants/retractable-atc/check_guide_stroke.py',
        ROOT/'variants/retractable-atc/guide-stroke-check.json',
        ROOT/'output/release-review/RevE-ENGINEERING/motion_details.py']
    before={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    parts={p['id']:p for p in json.loads(CACHE.read_text())['parts']}
    spindle=parts['TOOL_SPINDLE_65x259']['bounds_mm']
    assert spindle == [542.5,1088.9,1060.0,607.5,1153.9,1319.0]
    assert parts['G_SPOIL_5']['bounds_mm'][5] == 958.8
    # Exact translating-box envelopes for the named nominal CAD components.
    # Other cached objects are AABB screens, not Boolean collision assertions.
    fixed_head=['ZBX80_BASE','ZBX80_END_BOTTOM','ZBX80_END_TOP','ZBX80_MOTOR',
                'ZBX80_COUPLER_GUARD','Z_CARRIER']
    lift_head=['ZBX80_OUTPUT_HOLD']+[n for n,p in parts.items() if p['group']=='removable_tool']
    gantry=[n for n in parts if n.startswith('GANTRY_') or n.startswith('X_')]
    selected={}
    for n in sorted(set(fixed_head+lift_head+gantry)):
        b=parts[n]['bounds_mm']; dx=800 if n in fixed_head+lift_head or n.startswith('X_BLOCK') else 0
        if dx: b=moved(b);b[0]-=400;b[3]-=400
        # All named X/gantry components move through gantry Y275..1275.
        b=sweep(b,dx=dx,dy=-1000,dz=-100 if n in lift_head else 0)
        selected[n]=b
    body0=[315,1070,966.15,835,1130,1086.15]
    tray0=[295,1060,959.8,855,1140,966.15]
    compact=[]
    for h in (40,60,90,120):
        body=body0[:];body[5]=body[2]+h
        parked={'body':moved(body,200),'tray':moved(tray0,200)}
        hits=[{'allocation':k,'obstacle':n,'aabb_overlap_mm3':overlap(b,o)}
              for k,b in parked.items() for n,o in selected.items() if overlap(b,o)>1e-6]
        compact.append({'assumed_body_height_mm':h,'parked_bounds':parked,
                        'inside_xy_footprint':all(inside(b) for b in parked.values()),
                        'named_full_xyz_swept_aabb_hits':hits})
    # Exact nominal primitive checks at center X, full rear Y; collision is decisive.
    old_carrier=cq.importers.importStep(str(OLD_STEP)).val()
    low_spindle=cq.Solid.makeCylinder(32.5,259,cq.Vector(575,1121.4,960))
    high_spindle=low_spindle.translate((0,0,100))
    old_shift=old_carrier.translate((0,200,0))
    old_cage=[315,1180,966.15,835,1300,1086.15]
    old_box_hits={n:overlap(old_cage,parts[n]['bounds_mm']) for n in ('ZBX80_BASE','ZBX80_END_BOTTOM')}
    old={'original_carrier_bounds_mm':bounds(old_carrier),
         'carrier_200stroke_low_spindle_exact_intersection_mm3':old_shift.intersect(low_spindle).Volume(),
         'carrier_200stroke_high_spindle_exact_intersection_mm3':old_shift.intersect(high_spindle).Volume(),
         'old_120mm_cage_200stroke_exact_nominal_box_intersections_mm3':old_box_hits,
         'shelf_minimum_stroke_for_spindle_plus_5mm_mm':1153.9+5-950,
         'tall_cage_minimum_stroke_for_low_z_module_plus_5mm_mm':1259.6+5-980,
         'whole_carrier_max_stroke_inside_outline_with_5mm_mm':1450-5-1190,
         'magazine_only_leaves_fixed_shelf_over_work':True}
    stock=[]
    for t in (12,25,50,75):
        for extra_fixture in (0,15):
            b=[175,121.4,958.8,975,1121.4,958.8+t+extra_fixture]
            stock.append({'stock_thickness_mm':t,'fixture_extra_above_stock_mm':extra_fixture,
                'stock_plus_fixture_bounds':b,
                'deployed_tray_overlap_mm3':overlap(tray0,b),
                'continuous_tray_translation_sweep_overlap_mm3':overlap(sweep(tray0,dy=200),b),
                'parked_tray_overlap_mm3':overlap(moved(tray0,200),b),
                'minimum_tray_top_for_5mm_gap_mm':b[5]+5+6.35,
                'extra_apparent_retract_clearance_mm':b[5]+5+6.35+90-1060,
                'extra_apparent_retract_with_added_13mm_guide_mm':b[5]+5+6.35+13+90-1060})
    guide=json.loads((ROOT/'variants/retractable-atc/guide-stroke-check.json').read_text())
    max_block=guide['manufacturer_maximum_block_length_mm']
    rail=[{'blocks':n,'block_nominal_length_mm':45.4,'block_catalog_max_length_mm':max_block,
           'center_pitch_if_two_mm':80 if n==2 else None,
           'end_allowance_each_mm':10,'travel_on_200mm_rail_mm':200-max_block-(80 if n==2 else 0)-20,
           'minimum_rail_for_200mm_stroke_mm':200+max_block+(80 if n==2 else 0)+20} for n in (1,2)]
    # Tray sweep is clear of these selected moving envelopes only after the gantry
    # has parked forward; stock is deliberately retained and remains an obstacle.
    forward={n:moved(parts[n]['bounds_mm'],dy=-1000) for n in selected}
    transfer_hits=[{'allocation':k,'obstacle':n,'aabb_overlap_mm3':overlap(sweep(b,dy=200),o)}
                  for k,b in {'body120':body0,'tray':tray0}.items() for n,o in forward.items()
                  if overlap(sweep(b,dy=200),o)>1e-6]
    artifacts={};readbacks=[]
    for name,dy in [('deployed',0),('parked',200)]:
        objects={'UNVERIFIED_520x60x120_MAGAZINE_ALLOCATION':moved(body0,dy),
                 'UNENGINEERED_560x80x6_35_MOVING_TRAY':moved(tray0,dy),
                 'FULL_NOMINAL_STOCK_12MM_CONTEXT':[175,121.4,958.8,975,1121.4,970.8]}
        a=cq.Assembly(name='SMALL_RETRACTABLE_ALLOCATION_ONLY')
        for n,b in objects.items():
            col=cq.Color(.75,.18,.65,.5) if 'MAGAZINE' in n else cq.Color(.18,.5,.75,.5) if 'TRAY' in n else cq.Color(.7,.6,.4,.25)
            a.add(box(b),name=n,color=col)
        path=OUT/f'{name}-allocation.step';a.save(str(path))
        back=cq.importers.importStep(str(path)).val()
        readbacks.append({'file':path.name,'solids':len(back.Solids()),'valid':back.isValid(),
                          'bounds_mm':bounds(back),'scope':'Envelope bodies only; deployed stock intersection is intentional.'})
        artifacts[path.name]=sha(path)
    checks={'all_compact_scenarios_inside_footprint':all(x['inside_xy_footprint'] for x in compact),
            'selected_parked_full_travel_screens_clear':all(not x['named_full_xyz_swept_aabb_hits'] for x in compact),
            'selected_forward_gantry_tray_sweep_clear':not transfer_hits,
            'old_carrier_low_spindle_collision_demonstrated':old['carrier_200stroke_low_spindle_exact_intersection_mm3']>.01,
            'all_loaded_tray_sweeps_blocked':all(x['continuous_tray_translation_sweep_overlap_mm3']>0 for x in stock),
            'all_loaded_parked_trays_clear_of_stock':all(x['parked_tray_overlap_mm3']==0 for x in stock),
            'two_step_readbacks_valid':all(x['valid'] and x['solids']==3 for x in readbacks)}
    after={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    report={'status':'BOUNDED FEASIBILITY STUDY; NO FULL-BED OR FABRICATION RELEASE',
        'date':'2026-09-26','verifier_file':Path(__file__).relative_to(ROOT).as_posix(),
        'verifier_sha256_before':before[Path(__file__).relative_to(ROOT).as_posix()],
        'verifier_sha256_after':after[Path(__file__).relative_to(ROOT).as_posix()],
        'source_sha256':before,'source_hashes_unchanged':before==after,
        'actual_magazine_verified':False,'guide_mount_design_complete':False,
        'full_bed_through_M6_qualified':False,
        'machine_nominal_tool_travel_mm':{'x':[175,975],'y':[121.4,1121.4],'z_lift':[0,100]},
        'allocation_input_status':{'body_width_60mm':'manufacturer nominal body width; endcaps/cover excluded',
            'body_length_520mm':'UNVERIFIED study variable','heights_mm':[40,60,90,120],
            'tool_pocket_y1100':'assumed only; exact pocket drawing absent'},
        'compact_parked_scenarios':compact,'old_bridge_comparison':old,'stock_and_fixture_cases':stock,
        'combined_stock_plus_clamp_height_cases':[{'combined_height_above_MDF_mm':h,
            'extra_apparent_retract_clearance_mm':h+.15,
            'extra_apparent_retract_with_added_13mm_guide_mm':h+13.15} for h in (25,50,75)],
        'guide_length_examples':rail,'named_full_xyz_swept_aabbs':selected,
        'forward_gantry_transfer_sweep_hits':transfer_hits,'STEP_readbacks':readbacks,
        'artifact_sha256':artifacts,'bounded_consistency_checks':checks,
        'bounded_consistency_pass':all(checks.values()) and before==after,
        'unmodeled':['Actual purchased magazine/pockets/cover/cable and below-magazine cutters',
            'Fixed guide supports and load path, actuator, positive stops/clamp, sensing',
            'Full machine collision proof, deflection, dynamic loads and physical repeatability',
            'Actual stock/clamp arrangement and measured nut/tool Z engagement trajectory'],
        'sources':[{'url':'https://rapidchangeatc.com/faq/','used':'60 mm body;90 mm non-inset allowance; actualCAD not retrieved','accessed':'2026-09-26'},
            {'url':'https://www.hiwin.de/en/Products/Linear-guideways/Blocks/Miniature-guides/MGN-HIRES-series/MGN12HZ1CM/p/MGN12HZ1CM','used':'45.4 length,27 width,13 height nominal','accessed':'2026-09-26'}]}
    (OUT/'feasibility.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'bounded_consistency_pass':report['bounded_consistency_pass'],'checks':checks,
                      'old_bridge':old,'report':str(OUT/'feasibility.json')},indent=2),flush=True)
    return 0 if report['bounded_consistency_pass'] else 1

if __name__=='__main__':
    result=main();sys.stdout.flush();sys.stderr.flush();os._exit(result)
