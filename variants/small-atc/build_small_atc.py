"""Small-machine removable ATC dock candidate; never modifies frozen Rev I.

The magenta cage is an UNVERIFIED allocation, not RapidChange product CAD.
Frame-weld attachment, magazine fit, storage and physical qualification remain open.
"""
from pathlib import Path
import sys, json, hashlib, math, os, time
import cadquery as cq
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
LEGACY=ROOT/'output/release-review/RevE-ENGINEERING'
sys.path[:0]=[str(LEGACY),str(ROOT/'variants/common/location')]
from cad_helpers import Model,box,cyl,plate,rect,tube,bbox,intersection_volume,validate,export
from locator_dock import add_locator_pair
import build_revi

OUT=Path(__file__).resolve().parent/'output'
BLUE=(.12,.48,.65); STEEL=(.30,.38,.44); GOLD=(.82,.58,.18); MAGENTA=(.78,.20,.66)

def cap(d,L,hd,hh):
    return cyl(d,L).fuse(cyl(hd,hh).translate((0,0,L))).clean()

def nut(d,af,h):
    return cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(h).val().cut(cyl(d,h)).clean()

def thread(m,a,b):
    m.permit(a,b,'Nominal thread engagement: minor tapped bore versus external screw envelope; no helical thread modeled.')

def build_dock():
    m=Model(); centers=[(90,1155.4),(1060,1155.4)]
    meta=add_locator_pair(m,'SATC',centers,base_z=964)
    for i,(x,y) in enumerate(centers,1):
        stem=f'SATC_LOC_{i}'
        # Integrating fixture uses flushed M6 heads because the receiver is only
        # 2mm above the fixed block. Distinct PN/operations, no common-source edit.
        p=m.find(stem+'_PIN_BLOCK'); local=p.local
        for xx in (8,52):
            for yy in (8,32): local=local.cut(cyl(11,6).translate((xx,yy,6)))
        p.local=local.clean();p.shape=p.local.translate((x-30,y-20,964))
        p.part_number='SATC_PIN_BLOCK_CB11_60_40_12'
        p.flat['operations']=[{'type':'circle','x':xx,'y':yy,'diameter':11,'layer':'MILL_CB11_DEPTH6_FROM_TOP'} for xx in (8,52) for yy in (8,32)]
        p.notes.append('ATC integration: counterbore four M6 mounts Ø11 depth6 from top; heads flush below receiver.')
        # Outer M5 column moves5mm inward to retain full head seats after wing
        # trimming for yaw clearance. Fixed-block attachment stays unchanged.
        cols=(13,52) if i==1 else (8,47)
        meta['interfaces'][i-1]['receiver_mount_xy_relative_mm']=[[xx-30,yy-20] for xx in cols for yy in (8,32)]
        holes=[(xx,yy,4.2) for xx in cols for yy in (8,32)]+[(13,20,4),(47,20,4),(30,20,15)]
        p=m.find(stem+'_RECEIVER'); p.local=plate(rect(60,40),12,holes)
        p.shape=p.local.translate((x-30,y-20,978));p.part_number=f'SATC_RECEIVER_M5_TAPPED_{"L" if i==1 else "R"}'
        p.flat={'outline':rect(60,40),'thickness_mm':12,'holes':holes,'slots':[],'internal':[],
                'machining_notes':['4x M5x0.8 TAP THRU (Ø4.2 minor shown), min9.6mm screw engagement',
                                   'Ø15 MATCH BUSH FOR .010-.020 DIAMETRAL INTERFERENCE',
                                   '2x Ø4 MATCH REAM WITH CARRIER; check installed bush bore10F7']}
        p.notes=['ATC-specific tapped receiver; four top-down M5x16 bolts through6.35mm carrier wing, nominal9.65mm thread engagement.',
                 'Two Ø4 dowels match-reamed through carrier and receiver; bushing fit and clocking requirements inherited from common interface.']
        # Fixed chassis seats bear on the inner faces of original square tubes.
        left=i==1; sx=50.8 if left else 1099.2-6.35
        leg=box(6.35,70,52.35).translate((sx,1120,957.65))
        shelf=box(62.85,70,6.35).translate((57.15 if left else 1030,1120,957.65))
        seat=leg.fuse(shelf).clean()
        for xx in (x-22,x+22):
            for yy in (y-12,y+12):seat=seat.cut(cyl(6.6,10).translate((xx,yy,956)))
        for xx in (x-17,x+17):seat=seat.cut(cyl(4,10).translate((xx,y,956)))
        m.add(f'SATC_FRAME_SEAT_{i}',seat.clean(),pn=f'SATC_FRAME_SEAT_{"L" if left else "R"}',color=STEEL,
            notes=['6.35mm fabricated steel angle seat; vertical leg welds to clean inside face of chassis top tube.',
                   'No frame drilling or source modification applied. Weld size/sequence, salvage material and distortion require qualification before retrofit.',
                   'Locate after rail alignment; machine seat tops to common964mm datum. Actual weld fillets not represented.'])
        for j,(xx,yy) in enumerate([(x+a,y+b) for a in(-22,22) for b in(-12,12)],1):
            bid=f'{stem}_FIX_BOLT_{j}'
            m.add(bid,cap(6,20,10.5,6),origin=(xx,yy,950),pn='SATC_M6x20_CAP_MAXENV',purchased=True,color=GOLD)
            m.add(f'{stem}_FIX_WASHER_{j}',cyl(12,1.6).cut(cyl(6.6,1.6)),origin=(xx,yy,956.05),pn='SATC_WASHER_M6_OD12',purchased=True,color=GOLD)
            nid=f'{stem}_FIX_NUT_{j}'
            m.add(nid,nut(5,10,5),origin=(xx,yy,951.05),pn='SATC_NUT_M6_AF10_H5',purchased=True,color=GOLD);thread(m,bid,nid)
            bid=f'{stem}_CARRIER_BOLT_{j}'
            cx=xx+5 if i==1 and xx<x else xx-5 if i==2 and xx>x else xx
            m.add(bid,cap(5,16,9.5,2.75),origin=(cx,yy,980.35),pn='SATC_ISO7380_M5x16_BUTTON_MAXENV',purchased=True,color=GOLD,
                notes=['ISO7380-1 M5 envelope: head diameter9.5 maximum, height2.75 maximum. Domed head conservatively modeled as full cylinder.',
                       'Source: https://shop.hpceurope.com/pdf/gbPDFauto/BHC.pdf . Low head required for20mm unseat below continuous Y rail.'])
            thread(m,bid,stem+'_RECEIVER')
        for j,xx in enumerate((x-17,x+17),1):
            m.add(f'{stem}_FIX_DOWEL_{j}',cyl(4,18),origin=(xx,y,958),pn='SATC_DOWEL4x18',purchased=True,color=GOLD)
            m.add(f'{stem}_CARRIER_DOWEL_{j}',cyl(4,18),origin=(xx,y,978),pn='SATC_DOWEL4x18',purchased=True,color=GOLD)
    # One removable welded carrier. Low front shelf clears finished MDF by1mm.
    carrier=tube(906).translate((122,1130,953))
    for x in (63,1003.65):carrier=carrier.fuse(box(83.35,70,6.35).translate((x,1120,990)))
    carrier=carrier.fuse(box(560,180,6.35).translate((295,950,959.8))).clean()
    for i,(x,y) in enumerate(centers,1):
        carrier=carrier.cut(cyl(12,10).translate((x,y,988)))
        for xx in((x-17,x+22) if i==1 else (x-22,x+17)):
            for yy in(y-12,y+12):carrier=carrier.cut(cyl(5.5,10).translate((xx,yy,988)))
        for xx in(x-17,x+17):carrier=carrier.cut(cyl(4,10).translate((xx,y,988)))
    pads=[(75,1127),(1075,1127),(75,1183),(1075,1183)]
    for i,(x,y) in enumerate(pads,1):
        carrier=carrier.cut(cyl(6.6,10).translate((x,y,988)))
        p=box(20,14,26).cut(cyl(5,26).translate((10,7,0)))
        m.add(f'SATC_Z_PAD_{i}',p,origin=(x-10,y-7,964),pn='SATC_Z_PAD_20_14_26',color=STEEL,
            notes=['Weld to frame seat before finish machining; M6x1 tapped fromtop min13mm.',
                   'Three pads establish Z. Fit fourth by machining/shim to avoid rocking. Targetcoplanarity0.02mm; physical qualification required.'])
        wid=f'SATC_CLAMP_WASHER_{i}';bid=f'SATC_CLAMP_BOLT_{i}'
        m.add(wid,cyl(12,1.6).cut(cyl(6.6,1.6)),origin=(x,y,996.35),pn='SATC_WASHER_M6_OD12',purchased=True,color=GOLD)
        m.add(bid,cap(6,20,10.5,6),origin=(x,y,977.95),pn='SATC_M6x20_CAP_MAXENV',purchased=True,color=GOLD)
        thread(m,bid,f'SATC_Z_PAD_{i}')
    m.add('SATC_REMOVABLE_CARRIER',carrier.clean(),pn='SATC_CARRIER_WELDMENT',color=BLUE,
        notes=['906mm 2x2x.120in beam with two6.35mm steel end wings and560x180x6.35mm blank front shelf.',
               'TubeX122..1028 leaves2mm clearance to fixed pin blocks/seats endingX120/1030 during vertical extraction.',
               'Manufacturer magazine holes deliberately absent. Transfer-drill only after verified current mounting drawing and tool-center calibration.',
               'Fullface weld contacts shown without weld beads; weld design/deflection and permanent support retrofit remain engineering qualifications.',
               'Do not infer a magazine from the separate magenta allocation cage.'])
    m.holds=['Exact RapidChange variant, mounting drawing, height datums, pocket pitch, cover envelope and delivered price unconfirmed.',
             'No automatic or in-footprint dock storage/transfer path released. Bridge is manually removable; plasma use requires verified removal/storage.',
             'Actual spindle nut19.5mm maximumOD/17AF, reversal, controlled lowRPM and toolsetter/macros remain to be verified.',
             'New frame welds, pads, carrier bending and repeated location require qualification; nominal solids do not establish load capacity.']
    bearing=[]
    for x,y in pads:
        area=intersection_volume(carrier,box(20,14,.01).translate((x-10,y-7,990)))/.01
        expected=280-math.pi*3.3**2
        assert abs(area-expected)<1e-3,(x,y,area,expected)
        bearing.append({'center_mm':[x,y],'actual_contact_area_mm2':area,'expected_pad_minus_clearance_bore_mm2':expected})
    meta['receiver_underside_mm']=meta.pop('carrier_underside_mm')
    for interface in meta['interfaces']:
        interface['pin_tip_keepout_top_mm']=interface.pop('keepout_top_mm')
        interface['relative_z_datum_mm']=964
    meta.update({'status':'INTEGRATED ALLOCATION CANDIDATE; NOT PURCHASE OR FABRICATION RELEASE',
        'fixed_pin_block_base_z_mm':964,'carrier_weldment_max_z_mm':bbox(carrier)[5],
        'support':'Four independent metal pads; three primary/fourth fitted; pins do not carry vertical weight.',
        'support_bearing_checks':bearing,'outer_M5_head_to_wing_edge_mm':5.25,'outer_M6_washer_to_wing_edge_mm':6.0,
        'receiver_mount_note':'Outer M5 columns shifted inward5mm versus common blocks; use distinct left/right ATC receiver parts and their DXFs.',
        'proposed_routing_tool_axis_mm':{'x':[175,975],'y':[121.4,910],'z_lift':[0,100]},
        'nominal_axis_rectangle_mm':[800,788.6],
        'protected_atc_approach_region_y_mm':[910,1121.4],
        'rear_strip_original_proposal_y_mm':[940,1121.4],
        'why_more_reserved':'CarrierfrontY950 minus32.5 spindlebodyradius minus7.5 clearance givesY910; frontstrip940 alone is insufficient at lowZ.',
        'magazine_allocation_mm':[520,120,120],
        'allocation_status':'Product webpage additional-information dimensions may be shipping metadata; NOT verified magazine envelope.',
        'allocation_origin_mm':[315,980,966.15],
        'finished_MDF_top_mm':958.8,'magazine_shelf_top_mm':966.15,
        'nominal_spindle_lower_envelope_at_retract_mm':1060,
        'apparent_retract_to_carrier_clearance_mm':93.85,
        'clearance_caveat':'1060 is an inherited simplified spindle envelope datum, not measured collet or installed-tool tip. 93.85mm does not prove manufacturer90mm requirement or docking engagement.',
        'carrier_steel_mass_kg':round(carrier.Volume()*7.85e-6,4),'holds':m.holds})
    return m,meta

def allocation_cage():
    m=Model();x,y,z=315,980,966.15;dx,dy,dz=520,120,120;t=2
    for j,(yy,zz) in enumerate([(y,z),(y+dy-t,z),(y,z+dz-t),(y+dy-t,z+dz-t)]):m.add(f'ALLOC_X{j}',box(dx,t,t),origin=(x,yy,zz),color=MAGENTA,release='ALLOCATION ONLY - NOT PRODUCT CAD')
    for j,(xx,zz) in enumerate([(x,z),(x+dx-t,z),(x,z+dz-t),(x+dx-t,z+dz-t)]):m.add(f'ALLOC_Y{j}',box(t,dy,t),origin=(xx,y,zz),color=MAGENTA,release='ALLOCATION ONLY - NOT PRODUCT CAD')
    for j,(xx,yy) in enumerate([(x,y),(x+dx-t,y),(x,y+dy-t),(x+dx-t,y+dy-t)]):m.add(f'ALLOC_Z{j}',box(t,t,dz),origin=(xx,yy,z),color=MAGENTA,release='ALLOCATION ONLY - NOT PRODUCT CAD')
    return m

def mesh(model,path):
    vs=[];fs=[];cs=[];n=0
    for p in model.parts:
        v,f=p.shape.tessellate(.8,.3);v=np.array([q.toTuple() for q in v]);f=np.array(f,dtype=np.int32)
        vs.append(v);fs.append(f+n);cs.append(np.tile(np.array(p.color)*255,(len(f),1)));n+=len(v)
    np.savez_compressed(path,vertices=np.vstack(vs),triangles=np.vstack(fs),colors=np.vstack(cs))

def clashes_with(dock,baseline):
    out=[];tested=0
    for a in dock.parts:
        aa=bbox(a.shape)
        for b in baseline.parts:
            bb=bbox(b.shape)
            if not all(min(aa[k+3],bb[k+3])-max(aa[k],bb[k])>1e-5 for k in range(3)):continue
            tested+=1;v=intersection_volume(a.shape,b.shape)
            if v>.02:out.append({'dock':a.id,'machine':b.id,'volume_mm3':round(v,5)})
    return {'tested_booleans':tested,'clashes':out}

def source_map():
    files=list(LEGACY.glob('*.py'))+[Path(__file__),ROOT/'variants/common/location/locator_dock.py']
    return {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

def main():
    t=time.monotonic();OUT.mkdir(parents=True,exist_ok=True);before=source_map()
    dock,meta=build_dock();result=export(dock,OUT,'SMALL_ATC_DOCK_CANDIDATE',individual=True)
    print('Dock',len(dock.parts),'clashes',result['unresolved_intersections'],flush=True)
    cases=[]
    # Explicit bounded cases; no all-motion swept proof or unverified ATC collision waiver.
    poses=[('router_front_low',275,575,0),('router_front_high',275,575,100),
           ('route_limit_left_low',1063.6,175,0),('route_limit_right_low',1063.6,975,0),
           ('atc_center_retracted',1193.6,575,100),('rear_limit_low_EXPECTED_REJECT',1275,575,0)]
    for name,y,x,z in poses:
        print('Checking',name,flush=True);baseline,_=build_revi.build_model(gantry_y=y,head_x=x,z_lift=z)
        check=clashes_with(dock,baseline);check.update(name=name,gantry_y=y,head_x=x,z_lift=z,tool_axis_y=y-153.6)
        cases.append(check)
        if name=='router_front_high':
            scene=Model();scene.parts=baseline.parts+dock.parts+allocation_cage().parts
            mesh(scene,OUT/'SMALL_ATC_CONTEXT.npz')
    allocation=box(520,120,120).translate((315,980,966.15))
    baseline,_=build_revi.build_model(gantry_y=1193.6,head_x=575,z_lift=100)
    am=Model();am.add('UNVERIFIED_MAGAZINE_VOLUME',allocation)
    allocation_check=clashes_with(am,baseline)
    after=source_map()
    report={'status':'BOUNDED CAD ALLOCATION REVIEW; ACTUAL MAGAZINE/TRANSFER NOT RELEASED',
        'source_sha256':after,'sources_changed_during_check':before!=after,
        'dock_internal_static':result,'machine_cases':cases,'unverified_allocation_at_approach':allocation_check,
        'meta':meta,'elapsed_seconds':round(time.monotonic()-t,2)}
    (OUT/'fit-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (OUT/'interface.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cases':[{k:c[k] for k in('name','clashes')} for c in cases],
                      'allocation_clashes':allocation_check,'sources_changed':before!=after}),flush=True)
    mesh(dock,OUT/'SMALL_ATC_DOCK.npz')
    return 0

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
