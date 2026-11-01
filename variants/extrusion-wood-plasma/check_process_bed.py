"""Check variant-only bed geometry, water inventory, and nominal manual panel transfers."""
from pathlib import Path
import functools, hashlib, json, math, os, sys
import cadquery as cq
from process_bed import *
from frame import frame_parts
from motion_context import _bare_motion
HERE=Path(__file__).resolve().parent

def limits(s):
    b=s.BoundingBox()
    return (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)
def overlap(a,b):
    return all(min(a[i+3],b[i+3])-max(a[i],b[i])>1e-5 for i in range(3))
def lerp(a,b,n):return [a+(b-a)*i/n for i in range(n+1)]
def desc(items):return [(n,s,limits(s)) for n,s,c in items]
def hits(record,shape,env):
    b=limits(shape);record['poses']+=1
    for n,s,bb in env:
        if not overlap(b,bb): continue
        record['exact_pairs']+=1
        v=shape.intersect(s).Volume()
        if v>.05:record['unexpected'].append([n,round(v,4)])
def run():
    model={m:bed_parts(hot) for m,hot in [('wood',False),('plasma',True)]}
    checks={}
    for mode,items in model.items():
        ref=desc(items); found=[]; known=[]
        for i,(a,sa,ba) in enumerate(ref):
            for b,sb,bb in ref[i+1:]:
                if not overlap(ba,bb):continue
                v=sa.intersect(sb).Volume()
                if v<=.05:continue
                bucket=known if ((a.startswith('RACK_keeper_pedestal_') and b.startswith('RACK_keeper_pivot_'))
                    or (a.startswith('CARVE_LEDGER_') and a.endswith('weldnuts') and b.endswith('hold_down_bolts'))) else found
                bucket.append([a,b,round(v,4)])
        checks[mode]={'body_count_including_compounds':len(items),'unclassified_intersections':found,'nominal_thread_envelopes':known}
    assert not any(v['unclassified_intersections'] for v in checks.values()),checks
    # Prove the drawing defines closed pan retention and thermal float. Analytical
    # allowances are checked using translated real ears against the actual sleeves/stops.
    hold={n:s for n,s,_ in pan_retainers()}; chassis={n:s for n,s,_ in frame_parts()}
    retention={}
    for key in ('FL','FR','RL','RR'):
        name='PAN_HOLD_'+key+'_'; front=key[0]=='F'
        ear=hold['PAN_EAR_'+key+'_welded_to_dry_wall']
        wall=next(s for n,s,_ in pan_parts() if n==('PAN_front_wall_drain_overflow' if front else 'PAN_rear_wall'))
        cap=hold[name+'keeper_cap']; sleeve=hold[name+'shoulder_8mm']
        beam=chassis['EX_X_PAN_'+('1' if front else '3')]
        topstrap=hold[name+'upper_strap']; lowstrap=hold[name+'base_strap']
        d=(.25,0,0) if key=='FL' else ((2.,0,0) if key=='FR' else (1.,2.,0))
        stop=(.6,0,0) if key=='FL' else ((0,.6,0) if key=='FR' else (0,3.6,0))
        r={'ear_to_dry_pan_wall_mm':ear.distance(wall),'boss_to_bearer_top_via_strap_mm':topstrap.distance(beam),
           'lower_strap_to_bearer_mm':lowstrap.distance(beam),'nominal_sleeve_radial_clearance_mm':ear.distance(sleeve),
           'keeper_cap_axial_clearance_mm':ear.distance(cap),'free_test_offset_mm':d,
           'free_test_interference_mm3':ear.translate(d).intersect(sleeve).Volume(),
           'stop_test_offset_mm':stop,'stop_test_interference_mm3':ear.translate(stop).intersect(sleeve).Volume(),
           'quarter_mm_past_uplift_stop_interference_mm3':ear.translate((0,0,1.25)).intersect(cap).Volume(),
           'no_profile_modification':max(topstrap.intersect(beam).Volume(),lowstrap.intersect(beam).Volume())<.01}
        assert max(r['ear_to_dry_pan_wall_mm'],r['boss_to_bearer_top_via_strap_mm'],r['lower_strap_to_bearer_mm'])<1e-4
        assert abs(r['keeper_cap_axial_clearance_mm']-1.)<.001 and r['free_test_interference_mm3']<.001
        assert min(r['stop_test_interference_mm3'],r['quarter_mm_past_uplift_stop_interference_mm3'])>.05 and r['no_profile_modification'],r
        retention[key]=r
    # Work-referenced bare cutter-free spindle, physically retained/retracted for the swap.
    ed=frame_parts()+pan_parts()+frame_interfaces()+storage(False)+list(_bare_motion(275.,575.,100.))
    static=desc(ed); local=local_panel()
    record={'poses':0,'exact_pairs':0,'unexpected':[]}
    maxZ=1008.; pivot=1080.
    for i in (3,2,1,0):
        work_y=panel_y(i)
        other=[]
        for j in range(4):
            if i==j:continue
            if j>i: other.append((f'previously_stored_{j}',stored(local,j),STEEL))
            else:
                other.append((f'still_installed_{j}',local.translate((0,panel_y(j),0)),STEEL))
                other.extend(p for p in model['wood'] if p[0]==f'BED_panel_{j+1}_hold_down_bolts')
        env=static+desc(other)
        for z in lerp(PLANE,maxZ,7):hits(record,local.translate((0,work_y,z-PLANE)),env)
        for y in lerp(work_y,pivot,max(2,math.ceil(abs(work_y-pivot)/45))):hits(record,local.translate((0,y,maxZ-PLANE)),env)
        for a in lerp(0,90,18):hits(record,rotate_panel(local,a).translate((0,pivot,maxZ-PLANE)),env)
        vert=rotate_panel(local,90)
        for y in lerp(pivot,SLOT_Y[i],8):hits(record,vert.translate((0,y,maxZ-PLANE)),env)
        for z in lerp(maxZ,STORED_Z,18):hits(record,vert.translate((0,SLOT_Y[i],z-PLANE)),env)
    assert not record['unexpected'],record
    # Cut planar free-water wedge against modeled solids (floor/walls bound separately).
    vol=lambda z:yz(PX0+2,PX1-PX0-4,[(PY0+2,top(PY0+2)),(PY1-2,top(PY1-2)),(PY1-2,z),(PY0+2,z)])
    water=[]
    for z in (WATER,896.,RIM):
        gross=vol(z); net=gross.Volume()
        for n,s,_ in pan_parts():
            if n.startswith('SLAT_') or n.startswith('PAN_slotted_comb_'):net-=gross.intersect(s).Volume()
        water.append({'surface_Z_mm':z,'gross_L':gross.Volume()/1e6,'net_L':net/1e6})
    # Mass excludes fasteners designated unmodeled; density 7850 kg/m³ for all steel, 750 for MDF.
    panel_mass=local.Volume()*7.85e-6
    grav=9.80665
    pan_mass=sum(s.Volume() for n,s,c in pan_parts())*7.85e-6
    dry_process_mass=sum(s.Volume() for n,s,c in model['plasma'])*7.85e-6
    report={'units':'mm unless noted; 1 L of water treated as 1 kg','assembly_internal_pairs':checks,
        'four_captive_pan_mounts':retention,'added_clips_steel_mass_kg':sum(s.Volume() for s in hold.values())*7.85e-6,
        'pan_volume_cases':water,'pan_saddles_combs_slats_total_dry_kg':pan_mass,
        'pan_saddles_combs_slats_plus_operating_water_kg':pan_mass+water[0]['net_L'],
        'all_plasma_mode_bed_parts_dry_kg':dry_process_mass,
        'all_bed_parts_plus_operating_water_weight_N':(dry_process_mass+water[0]['net_L'])*grav,
        'panel_mass_including_permanent_fastener_details_kg':panel_mass,
        'job_backer_mass_at_750kgm3_each_kg':next(s.Volume()*0.75e-6 for n,s,c in model['wood'] if n.startswith('JOB_')),
        'park_xy_and_z_lift_mm':[575,275,100],'manual_transfer':record,
        'path':'Backer/job, cutter and wood extraction removed. All four keepers open, hold-downs removed from moving bridge, bare spindle front and raised. Transfer bridges 4→1. Lift level top to Z1008. Translate front edge to Y1080. Rotate +90° about front top edge; translate upright to rack slot Y. Lower edge to Z714 on rack, close keepers after all four are seated. Reverse in opposite order. Sampling, not continuous collision certification.',
        'all_positive_solids_valid':all(s.isValid() and s.Volume()>0 for items in model.values() for n,s,c in items),
        'limits':'No tool/actual torch, hoses, hand envelopes, compliance, installation tolerances, open/closing keeper path proof, joint proof, thermal management or fire-rated compartment qualification. Two-way transfer geometrically reversible with identical bare spindle parked on both transitions. Density is assumed.',
        'source_sha256':{f:hashlib.sha256((HERE/f).read_bytes()).hexdigest() for f in ('process_bed.py','check_process_bed.py','frame.py','motion_context.py')}}
    (HERE/'bed-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('assembly_internal_pairs','source_sha256','path','limits')},indent=2),flush=True)
if __name__=='__main__':
    try:run();code=0
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
