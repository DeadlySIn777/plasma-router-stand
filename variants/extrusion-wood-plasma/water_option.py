"""Atmospheric water-handling option in assembly coordinates (mm). Layout only."""
import json, os, sys
from pathlib import Path
import cadquery as cq
from frame import box, cyl, frame_parts, wet_support_option
from process_bed import bed_parts, PX0, PX1, PY0, PY1, RIM, top

HERE=Path(__file__).resolve().parent
OUT=HERE/'review'
METAL=(.54,.62,.67); BLUE=(.21,.46,.57); PUMP=(.27,.36,.44); VALVE=(.74,.49,.25)
TANK=(120.,160.,20.,380.,840.,310.,2.)
MAX_CHARGE=65.; HARDWARE_AND_SLUDGE_L=2.; LINE_DRAINBACK_L=2.

def merged(*items):
    return items[0].fuse(*items[1:]).clean() if len(items)>1 else items[0]
def rod(a,b,r):
    d=cq.Vector(*b)-cq.Vector(*a)
    return cyl(r,d.Length,a,d.normalized().toTuple())
def envelop(pts,r):
    # Connected passage allocation; balls keep a full bore through the doglegs.
    # This is not a manufacturer's pipe bend or a flexible-hose bend-radius proof.
    return merged(*([rod(a,b,r) for a,b in zip(pts,pts[1:])] +
                    [cq.Solid.makeSphere(r,cq.Vector(*p),cq.Vector(0,0,1),-90,90) for p in pts[1:-1]]))
def pipe(pts,outer,inner):
    return envelop(pts,outer).cut(envelop(pts,inner)).clean()
def ported_header():
    s=box(120,160,330,380,840,2).cut(box(148,451,329,325,395,4))
    for x,y,r in ((235,295,13.),(330,305,13.),(425,360,10.),(445,965,16.),
                  (180,920,4.5),(195,925,4.5),(210,930,4.5)):
        s=s.cut(cyl(r,5,(x,y,329)))
    return s.clean()
def drop_adapter(x,y,zc,shape):
    # The incoming face at y=30 butts up to the existing pan stub. Inner
    # and outer shells are actually open at their front connection and base.
    z0=zc-45; w=42 if shape=='round' else 48
    s=box(x-w/2,4,z0,w,y-4,zc+14-z0)
    cavity=box(x-w/2+2,6,z0+2,w-4,y-8,zc+12-z0-2)
    rear=(rod((x,27,zc),(x,31,zc),12) if shape=='round'
          else box(x-20,27,zc-4,40,4,8))
    return s.cut(cavity).cut(rear).cut(cyl(10 if shape=='round' else 11,5,(x,17,z0-1))).clean()
def valve(x,y,z,outer,inner):
    body=box(x-21,y-18,z,42,36,56).cut(cyl(inner,58,(x,y,z-1)))
    return merged(body,box(x+21,y-15,z+13,39,30,30))

def water_step(state, event, s):
    """Review-only state table. Returns state/pump/NC-fill/NC-drain, never actual I/O."""
    off=lambda nxt:(nxt,False,False,False)
    if (not s['power'] or not s['isolated'] or s['pan_HH'] or s['tank_HH'] or s['timeout']
        or (s['fill_open'] and s['fill_closed']) or (s['pan_low_dry'] and s['pan_at_work'])):
        return off('FAULT')
    if state=='FAULT':
        return off('IDLE' if event=='RESET' else 'FAULT')
    if state=='IDLE':
        if event=='START_FILL' and s['wet_setup'] and not s['pan_at_work'] and s['tank_above_low'] and s['drain_closed']:
            return ('OPEN_FILL',False,True,False)
        if event=='START_DRAIN' and s['tank_headroom_at_start'] and s['fill_closed']:
            return ('DRAIN',False,False,True)
        return off('IDLE')
    if state in ('OPEN_FILL','FILL'):
        if not (s['wet_setup'] and s['drain_closed'] and s['tank_above_low']):
            return off('FAULT')
        if s['pan_at_work']: return off('IDLE')
        if s['fill_open']: return ('FILL',True,True,False)
        return off('FAULT') if state=='FILL' else ('OPEN_FILL',False,True,False)
    if state=='DRAIN':
        if not s['fill_closed']: return off('FAULT')
        # The low-start threshold will normally become wet as the tank fills.
        # Tank HH, pan HH, watchdog and lost machine isolation still trip above.
        if s['pan_low_dry'] and s['drain_tail_complete']: return off('IDLE')
        return ('DRAIN',False,False,True)
    return off('FAULT')

def sequence_examples():
    base={k:True for k in ('power','isolated','wet_setup','tank_above_low','drain_closed',
        'fill_closed','tank_headroom_at_start')}
    base.update({k:False for k in ('pan_HH','tank_HH','timeout','pan_at_work','fill_open',
        'pan_low_dry','drain_tail_complete')})
    tests=[
        ('startup_requires_reset','FAULT','START_FILL',{},('FAULT',0,0,0)),
        ('reset_no_restart','FAULT','RESET',{},('IDLE',0,0,0)),
        ('fill_awaits_proof','IDLE','START_FILL',{},('OPEN_FILL',0,1,0)),
        ('fill_proved','OPEN_FILL','NONE',{'fill_open':True,'fill_closed':False},('FILL',1,1,0)),
        ('contradictory_valve_feedback','OPEN_FILL','NONE',{'fill_open':True},('FAULT',0,0,0)),
        ('lost_valve_proof','FILL','NONE',{},('FAULT',0,0,0)),
        ('normal_level','FILL','NONE',{'pan_at_work':True},('IDLE',0,0,0)),
        ('wood_not_clear','IDLE','START_FILL',{'wet_setup':False},('IDLE',0,0,0)),
        ('no_airspace','IDLE','START_DRAIN',{'tank_headroom_at_start':False},('IDLE',0,0,0)),
        ('start_drain','IDLE','START_DRAIN',{},('DRAIN',0,0,1)),
        ('start_threshold_becomes_wet','DRAIN','NONE',{'tank_headroom_at_start':False},('DRAIN',0,0,1)),
        ('drain_tail_only_after_low','DRAIN','NONE',{'drain_tail_complete':True},('DRAIN',0,0,1)),
        ('drain_done','DRAIN','NONE',{'drain_tail_complete':True,'pan_low_dry':True},('IDLE',0,0,0)),
        ('tank_HH_trip','DRAIN','NONE',{'tank_HH':True},('FAULT',0,0,0)),
        ('pan_HH_trip','FILL','NONE',{'pan_HH':True},('FAULT',0,0,0)),
        ('pump_run_dry_protection','FILL','NONE',{'tank_above_low':False},('FAULT',0,0,0)),
        ('power_loss','DRAIN','NONE',{'power':False},('FAULT',0,0,0)),
        ('timeout','OPEN_FILL','NONE',{'timeout':True},('FAULT',0,0,0)),
        ('machine_isolation_lost','FILL','NONE',{'isolated':False},('FAULT',0,0,0))]
    for name,state,event,overrides,want in tests:
        assert water_step(state,event,{**base,**overrides})==want,name
    return [r[0] for r in tests]

def parts():
    p=[]
    def add(n,s,c=METAL): p.append((n,s,c))
    # Independent tank and runners on the floor. No contact with extrusion.
    for i,x in enumerate((122,306,476)):
        add(f'TANK_floor_runner_{i+1}',box(x,160,0,22,840,20),PUMP)
    x,y,z,w,l,h,t=TANK
    add('TANK_atmospheric_shell',box(x,y,z,w,l,h).cut(box(x+t,y+t,z+t,w-2*t,l-2*t,h)).clean())
    add('TANK_fixed_vented_top',ported_header())
    add('TANK_loose_service_lid_L',box(140,443,332,170,411,2))
    add('TANK_loose_service_lid_R',box(310.5,443,332,170,411,2))
    # Simple permanent top vent: continuously open, no air supply or valve.
    add('TANK_vent_ID28_keep_open',pipe([(445,965,332),(445,965,378)],16,14))
    for name,xx,yy,tip in [('low',180,920,75),('drain_start_limit',210,930,116),('HH',195,925,292)]:
        add('TANK_'+name+'_switch_reservation',cyl(4,343-tip,(xx,yy,tip)),BLUE)
    # A submerged pump allocation, serviced through the large top hatch.
    add('PUMP_submersible_envelope',box(390,625,26,70,70,46),PUMP)
    add('PUMP_inlet_strainer_envelope',box(400,695,27,50,48,26),BLUE)
    add('PAN_drain_butt_drop_ID24_in',drop_adapter(235,30,857,'round'))
    add('PAN_overflow_butt_drop_open',drop_adapter(875,30,900,'slot'))
    gd=[(235,17,812),(235,17,754),(235,73,706),(235,190,585),(235,295,510),(235,295,496)]
    add('DRAIN_gravity_ID20_to_valve',pipe(gd,12,10),BLUE)
    add('DRAIN_NC_full_port_valve_allocation',valve(235,295,440,12,10),VALVE)
    add('DRAIN_ID20_open_tank_discharge',pipe([(235,295,440),(235,295,314)],12,10),BLUE)
    ov=[(875,17,855),(875,17,770),(775,38,748),(625,49,716),(480,55,687),
        (370,105,638),(330,305,415),(330,305,314)]
    add('OVERFLOW_separate_unvalved_ID22',pipe(ov,12,11),BLUE)
    add('FILL_ID12_pump_to_valve',pipe([(425,625,60),(425,360,60),(425,360,405)],8,6),BLUE)
    add('FILL_NC_shutoff_allocation',valve(425,360,405,8,6),VALVE)
    fpath=[(425,360,461),(425,360,478),(425,150,675),(425,42,770),
           (425,42,955),(425,83,955),(425,83,939)]
    add('FILL_ID12_to_air_break',pipe(fpath,8,6),BLUE)
    # Clip-on probe rack: rod tips represent low/work/HH thresholds. Keep
    # the steel face outside the stated Y cut envelope; no holes in the pan.
    bracket=merged(box(606,61,914,65,25,3), box(606,61,893,10,3,21),
                   box(606,61,907,10,9,3),box(606,67,897,10,3,10))
    add('PAN_sensor_bracket_allocation',bracket,METAL)
    for name,xp,tip in [('low',615,851),('work',638,887),('HH',661,893)]:
        add('PAN_'+name+'_switch_reservation',cyl(2,914-tip,(xp,74,tip)),BLUE)
    return p

def measure(p):
    from build import clashes
    f=frame_parts()+wet_support_option()
    samples={'self':clashes(p,p,True),'both_frame_options':clashes(p,f)}
    for name,hot in [('wood',False),('plasma',True)]:
        samples[name+'_bed']=clashes(p,bed_parts(hot))
        # Include actual unmodified export, not just frame/bed nouns; this
        # covers the displayed motion pose and all current hardware in that STEP.
        s=cq.importers.importStep(str(OUT/(name.upper()+'.step'))).val()
        gs=[(str(i),solid,METAL) for i,solid in enumerate(s.Solids())]
        samples[name+'_full_step']=clashes(p,gs)
    x,y,z,w,l,h,t=TANK; area=(w-2*t)*(l-2*t)
    vol=lambda elevation:area*(elevation-z-t)/1e6
    gross=vol(z+h); safe=vol(292)-HARDWARE_AND_SLUDGE_L
    # Independent conservative whole-pan volume at the 896 mm overflow invert:
    # full internal rectangle, slats/comb displacement deliberately ignored.
    a,b=PY0+2,PY1-2; inside_w=PX1-PX0-4
    upper_bound=(b-a)*inside_w*(896-(top(a)+top(b))/2)/1e6
    # Check vessel reserve even if a low-water receiver gets one full upper-
    # bound drain and a separately allowed additional 2 L of line liquid.
    test_return=vol(116)+upper_bound+LINE_DRAINBACK_L
    assert safe>60 and test_return<safe and MAX_CHARGE<safe
    # Either half can lift then stack on the other, without taking the tank out.
    lift=box(140,443,334,340.5,411,110)
    samples['lid_lift_stack_volume_vs_others']=clashes([('lid_swept',lift,METAL)],
        [r for r in p if not r[0].startswith('TANK_loose_service_lid')]+f+bed_parts(True))
    maxv=max([0]+[h['volume_mm3'] for row in samples.values() for h in row['interferences_gt_0p05_mm3']])
    bbs=[s.BoundingBox() for n,s,c in p]
    bounds=[min(b.xmin for b in bbs),min(b.ymin for b in bbs),min(b.zmin for b in bbs),
            max(b.xmax for b in bbs),max(b.ymax for b in bbs),max(b.zmax for b in bbs)]
    assert min(bounds[:3])>-.0001 and bounds[3]<1150 and bounds[4]<1450
    assert all(s.isValid() and s.Volume()>0 for n,s,c in p)
    return dict(source='Separate optional WATER.step in same coordinates as WOOD/PLASMA. All capacities approximate.',
        tank_external_mm=[w,l,h],tank_internal_floor_z_mm=z+t,tank_rim_z_mm=z+h,
        operating_charge_max_L=MAX_CHARGE,gross_to_rim_L=gross,high_high_gross_L=vol(292),
        reserved_hardware_sludge_L=HARDWARE_AND_SLUDGE_L,usable_to_HH_after_reserve_L=safe,
        remaining_to_HH_at_max_charge_L=safe-MAX_CHARGE,
        gross_capacity_at_low_cutoff_L=vol(75),reconstructed_pan_overflow_upper_bound_L=upper_bound,
        full_return_test_L=test_return,full_return_test_headroom_L=safe-test_return,
        line_drainback_allowance_L=LINE_DRAINBACK_L,fill_nozzle_outlet_above_pan_rim_mm=939-RIM,
        pan_levels_mm={'low':851,'work':887,'HH':893,'overflow_invert':896,'rim':RIM},
        tank_levels_mm={'low':75,'drain_start_limit':116,'HH':292},
        gross_capacity_at_drain_start_threshold_L=vol(116),routing_world_bounds_mm=bounds,
        geometry_checks=samples,max_unintended_clash_mm3=maxv,
        limits='Layout and nominal volume only. No pressure vessel, actual pump curve, overflow/vent capacity, dynamic spray, wiring or operating release.')

def main():
    from build import export
    p=parts(); print('water components',len(p),flush=True)
    r=measure(p)
    if r['max_unintended_clash_mm3']>0:
        print([(k,v['interferences_gt_0p05_mm3']) for k,v in r['geometry_checks'].items() if v['interferences_gt_0p05_mm3']],flush=True)
        raise ValueError('water routing collision')
    r['review_only_sequence_checks']=sequence_examples()
    r['STEP']=export(OUT/'WATER.step',p)
    (OUT/'water-option.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    print('water verified',r['usable_to_HH_after_reserve_L'],r['full_return_test_L'],r['STEP'],flush=True)
if __name__=='__main__':
    try: main(); code=0
    except Exception:
        import traceback; traceback.print_exc(); code=1
    sys.stdout.flush(); sys.stderr.flush(); os._exit(code)
