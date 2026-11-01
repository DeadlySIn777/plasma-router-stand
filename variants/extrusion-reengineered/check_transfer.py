"""Conservative complete-path collision proof for four XR1 cassette transfers.

Linear segments use their full swept axis-aligned enclosing box. The two90deg
rotations use an analytic enclosure over every angle, not endpoint sampling.
The enclosure test can produce false positives; any positive must be resolved.
No finite-step sampling is used to claim continuous clearance.
"""
from pathlib import Path
from math import sqrt
import hashlib,json,csv,os,sys
import cadquery as cq
import params as P
from bed import (box,bed_parts,transfer_fixed_parts,transfer_poses,cassette_parts,
    CASSETTE_H,STORE_LEVELS,STORE_Y,pan_parts,pan_retainers,dock_parts,
    storage_parts,water_envelopes,retention_parts,mass_report,cabinet_cover,cabinet_cover_blocks)
from frame import frame_parts
from motion import motion_parts
from build import clashes,bounds,overlap
HERE=Path(__file__).resolve().parent
OUT=HERE/'review'


def swept_enclosure(a,b):
    """Full rectangle sweep, with rotationX in[0,90] and fixed pivot.

    If localy>=0,z>=0 then Y=y0+y*cos-z*sin lies[y0-H,y0+L],
    Z=z0+y*sin+z*cos lies[z0,z0+sqrt(L²+H²)] throughout the rotation.
    The two90degree endpoints differonlyangle. All other stages are rectilinear.
    """
    L,H=P.PANEL_LENGTH,CASSETTE_H
    if a['angle']!=b['angle']:
        assert a['y']==b['y'] and a['z']==b['z']
        assert set((a['angle'],b['angle']))=={0.,90.}
        ext=(P.PANEL_X,a['y']-H,a['z'],P.PANEL_WIDTH,L+H,sqrt(L*L+H*H))
    else:
        assert a['angle'] in (0.,90.)
        if a['angle']==0.:
            ya,yb=min(a['y'],b['y']),max(a['y'],b['y'])+L
            za,zb=min(a['z'],b['z']),max(a['z'],b['z'])+H
        else:
            ya,yb=min(a['y'],b['y'])-H,max(a['y'],b['y'])
            za,zb=min(a['z'],b['z']),max(a['z'],b['z'])+L
        ext=(P.PANEL_X,ya,za,P.PANEL_WIDTH,yb-ya,zb-za)
    return box(*ext)


def run():
    OUT.mkdir(exist_ok=True)
    source={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in
            tuple(n for n in ('params.py','bed.py','frame.py','motion.py','build.py','shields.py','atc.py','check_transfer.py') if (HERE/n).exists())}
    motion=[q for q in motion_parts(False,1275.,575.,P.Z_TRAVEL) if not q[0].startswith(
        ('TOOL_SPINDLE_','TOOL_SPLIT_CLAMP_','TOOL_CLAMP_'))]
    from shields import shield_parts
    accessories=shield_parts(False)
    missing=[]
    try:
        from atc import atc_parts
        accessories+=atc_parts(False,deployed=False)
    except (ImportError,SyntaxError) as e:missing.append('atc.py unavailable/in-progress: '+str(e))
    static=transfer_fixed_parts()+frame_parts()+motion+accessories
    report={'revision':P.REVISION,'source_sha256':source,'passed':False,'release':False,
      'scope':'Exact CAD intersections of conservative enclosing solids for every continuous transfer segment; actual human reach, force and retention are unqualified.',
      'positive_volume_threshold_mm3':.05,'aabb_overlap_tolerance_mm':1e-5,
      'park':{'gantry_y_mm':1275,'head_x_mm':575,'z_lift_mm':P.Z_TRAVEL,
        'required':'Power isolated; REMOVE ENTIRE spindle/split-clamp module or entire plasma-drop/head/torch module before moving any cassette. Only the common Zadapter remains. Remove eightM6 clamp sets into owned tool storage; retain Z; open door. Install next tool module only after bed conversion.'},
      'missing_accessories':missing,'order':[1,2,3,4],'segments':[],'nominal_thread_exceptions':[],
      'intentional_initial_pin_enclosure_exceptions':[],
      'mode_self':{},'stored_case':{},'limits':{'machine_plan_x_mm':[0,1150.],
         'machine_plan_y_mm':[0,1450.],'swap_clearance_outside_plan_mm':0},
      'physical_holds':['14mm front finger pocket ergonomic test','measured cassette mass and manageable lift','side handle proof load and edge durability','lift-off cover screw/tapped-tab and parking-stand physical tests','dock pin fits and repeatability','bolt preload/thread/washer seat and sleeve tolerances','thermal and fume protection before plasma']}
    # Raw self checks retain every positive, including nominalthreads if any.
    for label,hot in (('WOOD',False),('PLASMA',True)):
        parts=bed_parts(hot);raw=clashes(parts,parts,True)
        raw['invalid_ids']=[n for n,s,c in parts if not s.isValid() or not s.Solids() or s.Volume()<=0]
        raw['part_count']=len(parts);raw['passed']=not raw['invalid_ids'] and not raw['positive_intersections']
        report['mode_self'][label]=raw
    # Closed storage envelope including all stored cassettes (already exact selftested above).
    report['stored_case']={'case_clear_x_mm':4.2,'side_shelf_rail_clear_x_mm':2.6,
      'shelf_vertical_gap_mm':5.,'minimum_top_to_primary_roof_mm':11.8,
      'door_closed_to_panel_front_gap_mm':13.0,'minimum_parking_block_to_lowest_stored_panel_mm':1.2,
      'floor_to_lowest_panel_mm':21.2,'passed':report['mode_self']['PLASMA']['passed']}
    removed=[]
    for i in (0,1,2,3):
        obstacles=list(static)
        for j in range(4):
            if j==i:continue
            obstacles+=cassette_parts(j,'stored' if j in removed else'installed')
        poses=transfer_poses(i)
        for k,(a,b) in enumerate(zip(poses,poses[1:])):
            envelope=swept_enclosure(a,b)
            skip={f'DOCK_L_{i+1}_ROUND',f'DOCK_R_{i+1}_DIAMOND_X_RELIEF'} if k==0 else set()
            tested=clashes([('SWEPT_CASSETTE',envelope,(.5,.5,.5))],
                           [q for q in obstacles if q[0] not in skip])
            bb=bounds(envelope)
            within=bb[0]>=-1e-6 and bb[3]<=1150.+1e-6 and bb[1]>=-1e-6 and bb[4]<=1450.+1e-6
            row={'cassette':i+1,'from':a['stage'],'to':b['stage'],
                 'continuous_enclosure_bounds_mm':bb,'within_plan':within,
                 'exact_pairs':tested['exact_pairs'],'positive_intersections':tested['positive_intersections']}
            if skip:
                pins=[q for q in obstacles if q[0] in skip]
                checks=[]
                for lift in (0.,.25,.5,1.,1.5,2.,2.01):
                    parts=cassette_parts(i,'custom',angle=0.,y=a['y'],z=a['z']+lift)
                    checks.append({'lift_mm':lift,**clashes(parts,pins)})
                # Beyond2mm the pins end at890 and solidbottom>=890: exact separation.
                row['initial_pin_hole_checks']=checks
                report['intentional_initial_pin_enclosure_exceptions'].append({
                    'cassette':i+1,'excluded_ids':sorted(skip),
                    'reason':'Pins occupy the conservative solid box but enter the actual vertical datum-pad bores. Analytic engagement proof: round radius2.99 is below bore radius3.02; diamond lies within the same radius. Projection2mm is below3.175mm pad bore depth; vertical coaxial lift monotonically removes engagement. Beyond2mm vertical separation is exact. Sampled exact checks corroborate this geometry.'})
            row['passed']=within and not row['positive_intersections'] and all(
                not c['positive_intersections'] for c in row.get('initial_pin_hole_checks',[]))
            report['segments'].append(row)
        removed.append(i)
    # Lift-offcover:pullforward,lower,lean,and slidealongits8deg stands.
    doorfixed=[q for q in static if not q[0].startswith(('COLD_CASE_LIFTOFF_FRONT_COVER_',
        'COLD_CASE_COVER_PARKING_BLOCK_'))]
    stages=('closed','front','lowered','leaned','parked');door_checks=[]
    for aa,bb in zip(stages,stages[1:]):
        sa,sb=cabinet_cover(aa),cabinet_cover(bb);ba,bc=bounds(sa),bounds(sb)
        lo=[min(ba[i],bc[i]) for i in range(3)];hi=[max(ba[i],bc[i]) for i in range(3,6)]
        enc=box(*lo,*(hi[i]-lo[i] for i in range(3)))
        row={'from':aa,'to':bb,**clashes([('COVER_CONTINUOUS_ENCLOSURE',enc,(.4,.4,.4))],doorfixed)}
        row['within_plan']=lo[0]>=0 and hi[0]<=1150 and lo[1]>=-1e-6 and hi[1]<=1450
        row['passed']=not row['positive_intersections'] and row['within_plan'];door_checks.append(row)
    slot_checks=[]
    for k in range(5):
        ss=cabinet_cover('parked').translate((0,5*k*__import__('math').tan(__import__('math').radians(8)),5*k))
        slot_checks.append({'axial_lift_vertical_component_mm':5*k,**clashes([('COVER',ss,(.4,.4,.4))],cabinet_cover_blocks(True))})
    report['door_motion']={'segments':door_checks,'slot_checks':slot_checks,
        'continuous_slot_proof':'The1.2mm slot and.8mm cover sharean8degreeaxis;finaltranslationisalongthataxiswith.2mmnominalsideclearance. Basefloor5mmprovidespositivebearing.',
        'rotation_proof':'During0..8degrotation,nonnegativepanelY/ZcoordinateshaveYincreasing/Zdecreasing;theendpointenclosurecoversallanglesandthemonotonicbaseYshift.',
        'passed':all(q['passed'] for q in door_checks) and all(not q['positive_intersections'] for q in slot_checks)}
    report['restoration']='Same path in reverse with BOTH complete tool modules removed; restore cassettes4,3,2,1. Refit selected tool only after cassette conversion.'
    report['source_unchanged']=all(hashlib.sha256((HERE/n).read_bytes()).hexdigest()==h for n,h in source.items())
    report['passed']=not missing and report['source_unchanged'] and all(r['passed'] for r in report['segments']) and all(
        q['passed'] for q in report['mode_self'].values()) and report['stored_case']['passed'] and report['door_motion']['passed']
    report['mass_report']=mass_report()
    (OUT/'transfer-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'segments':len(report['segments']),
      'failed_segments':[{'cassette':r['cassette'],'from':r['from'],'to':r['to'],'positive_intersections':r['positive_intersections']} for r in report['segments'] if not r['passed']],
      'self_positives':{k:len(v['positive_intersections']) for k,v in report['mode_self'].items()},
      'door_passed':report['door_motion']['passed'],'source_consistent':report['source_unchanged']},indent=2),flush=True)
    return 0 if report['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
