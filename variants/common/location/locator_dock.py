"""Reusable nominal locating dock, independent of frozen Rev I builders.

This is a source-backed interface candidate, not an integrated machine release.
Coordinates are millimetres. Datum z=0 is the top of a rigid supporting grid.
The diamond's non-functional relief is an explicitly simplified envelope;
its measured relief and clocking are installation acceptance requirements.
"""
from pathlib import Path
import math, sys
import cadquery as cq

ROOT = Path(__file__).resolve().parents[3]
LEGACY = ROOT / 'output/release-review/RevE-ENGINEERING'
sys.path.insert(0, str(LEGACY))
from cad_helpers import Model, box, cyl, plate, rect, export, validate

PIN_D = 9.9905  # midpoint of 10 g6: 9.986..9.995
BUSH_ID = 10.0205  # midpoint of 10 F7: 10.013..10.028
PIN_BASE_T = 12.0
CARRIER_UNDERSIDE = 14.0
RECEIVER_T = 12.0
PIN_SOURCE = 'JW Winco DIN 6321-10-18-B / -C'
BUSH_SOURCE = 'JW Winco DIN 179-B10-12-A-NI'
STEEL = (.30,.36,.40)
HARD = (.70,.53,.20)
ALU = (.72,.76,.79)

def bolt(d, length, hd, hh):
    return cyl(d, length).fuse(cyl(hd, hh).translate((0,0,length))).clean()

def _pin(diamond=False):
    # Published: shank d2=6 n6 x9; head h1=18 +/-0.1;
    # tapered lead h2=6 at15 degrees. Root relief/centre holes omitted.
    head = cyl(PIN_D, 12)
    taper = cq.Solid.makeCone(PIN_D/2, PIN_D/2-6*math.tan(math.radians(15)),6).translate((0,0,12))
    head = head.fuse(taper)
    if diamond:
        # Supplier drawing gives contact land s~2.5 but does not dimension
        # every relief facet. Functional contact axis is local X, relief Y.
        # A 2.5mm-wide band is illustrative, NOT a custom pin manufacturing file.
        head = head.intersect(box(12,2.5,20).translate((-6,-1.25,0)))
    return cyl(6,9).translate((0,0,-9)).fuse(head).clean()

def add_locator_pair(m, prefix, centers, base_z=0.0):
    """Add two fixed pin cartridges and two carrier-side bushing cartridges.

    centers: two XY tuples, round first. Only the diamond pin is clocked;
    cartridge mounting patterns remain world XY. Returned interface records
    specify all mating holes. Caller must support/attach both cartridge sets.
    """
    if len(centers)!=2: raise ValueError('Exactly one round and one diamond pin')
    dx=centers[1][0]-centers[0][0];dy=centers[1][1]-centers[0][1]
    pitch=math.hypot(dx,dy)
    if pitch<100: raise ValueError('Use >=100 mm locator separation')
    # Diamond contacts transverse to the line between pins.
    contact_angle=math.degrees(math.atan2(dy,dx))+90
    interface=[]
    for i,(x,y) in enumerate(centers):
        stem=f'{prefix}_LOC_{i+1}'
        mount=[(8,8,6.6),(52,8,6.6),(8,32,6.6),(52,32,6.6)]
        dowels=[(13,20,4),(47,20,4)]
        baseholes=mount+dowels+[(30,20,6)]
        base_shape=plate(rect(60,40),12,baseholes)
        for mx,my,_ in mount:base_shape=base_shape.cut(cyl(11,6).translate((mx,my,6)))
        p=m.add(stem+'_PIN_BLOCK',base_shape,origin=(x-30,y-20,base_z),
            pn='LOC_PIN_BLOCK_60_40_12_CB_M6',group='locator_fixed',material='Machined steel, certified yield >=250 MPa',color=STEEL,
            flat={'outline':rect(60,40),'thickness_mm':12,'holes':baseholes,'slots':[],'internal':[],
                  'operations':[{'type':'circle','x':mx,'y':my,'diameter':11,'layer':'MILL_CB11_DEPTH6_FROM_TOP'} for mx,my,_ in mount]},
            notes=['Support entire block on rigid grid; four M6 mounting screws. Two Ø4 in-situ dowels transfer lateral load to grid.',
                   'Four Ø11 counterbores6deep accept flush M6 socket heads. Grid thickness/thread attachment must be specified by integrator.',
                   'Pair-bore the central shank seat for 0.010–0.015 mm measured diametral interference; CAD Ø6 is nominal only.',
                   'Press pin shoulder against top face. Do not weld or coat fitted bores. Recheck clocking and fit after pressing.'])
        p.flat['machining_notes']=['CENTRAL Ø6 NOMINAL: MATCH ACTUAL PIN FOR .010-.015 DIAMETRAL INTERFERENCE',
                                  '2x Ø4 DOWEL BORES MATCH-REAM IN ASSEMBLY; M6 MOUNTS Ø6.6 THRU']
        shape=_pin(i==1)
        if i==1: shape=shape.rotate((0,0,0),(0,0,1),contact_angle)
        m.add(stem+'_PIN',shape,origin=(x,y,base_z+12),pn=f'DIN6321-10-18-{"C" if i else "B"}',
            group='locator_fixed',material='Hardened ground steel',color=HARD,purchased=True,
            notes=[PIN_SOURCE,'Published diameter/taper/shank envelope; root relief and centre holes omitted.',
                   'Diamond non-contact relief is schematic. Require measured >=0.20 mm free travel along pin-pair line at full insertion; do not fabricate from this purchased envelope.' if i else 'Round pin fixes two lateral axes.'],
            release='SUPPLIER INTERFACE ENVELOPE; VERIFY CURRENT DRAWING AND DELIVERED PART')
        holes=dowels+[(30,20,15)]+[(mx,my,4.2) for mx,my,_ in mount]
        receiver_shape=plate(rect(60,40),12,holes)
        p=m.add(stem+'_RECEIVER',receiver_shape,origin=(x-30,y-20,base_z+14),
            pn='LOC_RECEIVER_60_40_12_TAP_M5',group='locator_carrier',material='Machined steel, certified yield >=250 MPa',color=STEEL,
            flat={'outline':rect(60,40),'thickness_mm':12,'holes':holes,'slots':[],'internal':[],
                  'operations':[{'type':'circle','x':mx,'y':my,'diameter':5,'layer':'TAP_M5_THRU_NOT_ADDITIONAL_CUT'} for mx,my,_ in mount]},
            notes=['Four top-entry M5 screws plus two in-situ Ø4 dowels attach to a metal carrier lug; clearance bolts alone are not a datum.',
                   'M5x0.8 tapped THRU; minorØ4.2 envelope, helicalthreads omitted. Limit installedscrewpenetration to10.5mm so ends remain inside12mm receiver, above fixedblock. M5x16 through6.35mm wing penetrates9.65mm beforewasher allowance.',
                   'Press-in bushing is replaceable using an arbor press; receiver remains a separately removable service cartridge.',
                   'Match bore to delivered bushing for .010–.020 mm diametral interference. Measure installed bore and verify 10F7 remains valid.',
                   'Replacement/disturbance of cartridge or pin requires requalification and new WCS check. No tight bush directly in HDPE.'])
        p.flat['machining_notes']=['CENTRAL Ø15 NOMINAL: MATCH BUSH OD FOR .010-.020 DIAMETRAL INTERFERENCE',
                                  'CHECK INSTALLED ID10.013..10.028; 2x Ø4 DOWEL BORES MATCH-REAM IN ASSEMBLY']
        b=cyl(15,12).cut(cyl(BUSH_ID,12)).clean()
        m.add(stem+'_BUSH',b,origin=(x,y,base_z+14),pn='DIN179-B10-12-A-NI',group='locator_carrier',
            material='Hardened stainless drill bushing',color=HARD,purchased=True,
            notes=[BUSH_SOURCE,'OD15 n6; ID10 F7; length12. Nominal edge breaks omitted. Installed bore must be gauged after press fit.'],
            release='SUPPLIER INTERFACE ENVELOPE; VERIFY INSTALLED FIT')
        interface.append({'center_mm':[x,y], 'pin_type':'round' if i==0 else 'diamond',
                          'pin_block_bounds_relative_mm':[-30,-20,0,30,20,12],
                          'receiver_bounds_relative_mm':[-30,-20,14,30,20,26],
                          'base_mount_xy_relative_mm':[[-22,-12],[22,-12],[-22,12],[22,12]],
                          'receiver_mount_xy_relative_mm':[[-22,-12],[22,-12],[-22,12],[22,12]],
                          'receiver_mount_thread':'M5x0.8 THRU; max installedscrewpenetration10.5mm',
                          'match_dowel_xy_relative_mm':[[-17,0],[17,0]],
                          'keepout_top_mm':base_z+30.1})
    return {'centers_mm':centers,'pitch_mm':pitch,'diamond_relief_angle_deg':contact_angle-90,
            'carrier_underside_mm':base_z+14,'interfaces':interface,
            'status':'Unintegrated reusable interface; two locators do not support the table.'}

def add_supports(m,prefix,centers,base_z=0.0):
    """Three primary hard seats plus fourth fitted/shimmed support; M6 drawbolts.

    Each upper landing must attach directly to a metal carrier rail/corner.
    Four fixed blocks require a supporting grid node under their whole footprint.
    Clamp screws are shown; lower grid attachment is an integration requirement.
    """
    if len(centers)!=4: raise ValueError('Four support/clamp stations required')
    result=[]
    for i,(x,y) in enumerate(centers):
        stem=f'{prefix}_SUP_{i+1}'
        # Side mounting holes let the grid attachment heads sit below bearing plane.
        holes=[(20,20,5),(8,20,8.5),(32,20,8.5)]
        h=14 if i<3 else 13.5
        s=plate(rect(40,40),h,holes)
        for mx in (8,32): s=s.cut(cyl(14,8).translate((mx,20,h-8)))
        p=m.add(stem+'_FIXED',s,origin=(x-20,y-20,base_z),pn='LOC_Z_PRIMARY' if i<3 else 'LOC_Z_SUPPLEMENTARY',
            group='locator_fixed',material='Machined steel, certified yield >=250 MPa',color=STEEL,
            notes=['M6 central tapped hole model uses Ø5 minor bore; engagement11.4 mm. Threads omitted.',
                   'Two M8 counterbored grid mounting holes; rigid attachment beneath this block must be designed in integrating chassis.',
                   'Machine three primary top bearing lands coplanar within0.02mm after fixture installation; strip paint from contact.',
                   'Fourth station is a fitted .50mm nominal shim stack: fit with three primary seats loaded, then lock. Do not jack carrier off its datums.'] if i==3 else
                  ['M6 central tapped hole, Ø5 minor envelope; thread engagement11.4mm.',
                   'Three primary hard seats establish Z/pitch/roll. Machine installed bearing faces coplanar within0.02mm.',
                   'Two M8 counterbored grid mounts; chassis mating attachment must be integrated.'])
        p.flat={'outline':rect(40,40),'thickness_mm':h,'holes':holes,'slots':[],'internal':[],
                'operations':[{'type':'circle','x':mx,'y':20,'diameter':14,'layer':'MILL_CB14_DEPTH8_FROM_TOP'} for mx in (8,32)],
                'machining_notes':['CENTRAL M6x1 TAP, MIN11.4 ENGAGEMENT','CB Ø14 DEPTH8 AT GRID MOUNTS','GRIND/FLY-CUT Z CONTACT LANDS AFTER INSTALLATION']}
        if i==3:
            m.add_plate(stem+'_SHIM',40,40,.5,holes=[(20,20,7),(8,20,15),(32,20,15)],origin=(x-20,y-20,base_z+13.5),
                pn='LOC_FITTED_SHIM_NOMINAL_050',group='locator_fixed',material='Precision steel shim',notes=['Shown .50mm is nominal; actual stack is fitted after three-seat setup.'])
        foot=plate(rect(40,40),12,slots=[(20,20,12,9,0)])
        m.add(stem+'_LAND',foot,origin=(x-20,y-20,base_z+14),pn='LOC_CARRIER_LAND_40_40_12',group='locator_carrier',
            material='Machined steel, certified yield >=250 MPa',color=STEEL,
            flat={'outline':rect(40,40),'thickness_mm':12,'holes':[],'slots':[(20,20,12,9,0)],'internal':[]},
            notes=['Attach to metal frame with direct bearing beneath frame rail; keep weld distortion out of machined bottom face.',
                   '12x9 clearance slot is NOT a locator. Thermal travel minimum1.5mm transverse to slot at M6 shank.',
                   'Clamps load only metal. Set600–900N verified preload per station; do not infer torque from dry generic charts.'])
        m.add(stem+'_WASHER',cyl(18,1.6).cut(cyl(6.6,1.6)),origin=(x,y,base_z+26),pn='WASHER_M6_OD18_T1.6',group='locator_clamp',material='Steel',color=HARD)
        b=m.add(stem+'_DRAWBOLT',bolt(6,25,10,6),origin=(x,y,base_z+2.6),pn='ISO4762_M6x25',group='locator_clamp',material='Steel class8.8 minimum',color=HARD,
            notes=['Nominal thread/head envelope; shank25 below head.600–900N verified clamp preload. Tool access must be reserved above this bolt.'])
        m.permit(stem+'_FIXED',stem+'_DRAWBOLT','Nominal M6 thread engagement, Ø5 minor versus Ø6 external-thread envelope; threads intentionally not helical.')
        result.append({'center_mm':[x,y], 'fixed_footprint_mm':[40,40], 'land_z_mm':base_z+14,
                       'primary':i<3,'grid_mounts_relative_mm':[[-12,0],[12,0]],'grid_mount_size':'M8',
                       'drawbolt':'M6x25','minimum_grid_bearing_area_requirement_mm2':1600})
    return result

def build_dock(width=438.6666666667,length=423.3333333333):
    m=Model()
    # Separate locating blocks from support feet; all fit inside the panel plan.
    supports=[(25,25),(width-25,25),(25,length-25),(width-25,length-25)]
    locators=[(80,60),(width-80,length-60)]
    metadata=add_locator_pair(m,'COMMON',locators)
    metadata.update({'panel_size_mm':[width,length], 'supports':add_supports(m,'COMMON',supports),
      'grid_required':True,'carrier_required':True,'machine_integrated':False,
      'fit_inspection_required':True,'mechanical_return_target_mm':.15,
      'target_definition':'Maximum XY point displacement between setups at panel corners, 20 clean unloaded re-seats at stable temperature; target, not demonstrated performance.',
      'diagram_only_carrier':'Carrier/grid intentionally absent; all attachment and support requirements are explicit interfaces, not invisible load paths.'})
    m.holds += ['Install on a rigid grid at all four support stations and both locator blocks; no unsupported locator pedestals.',
                'Connect all six carrier-side lands/receiver blocks to the metal carrier; matched dowels required at locator receiver interfaces.',
                'Purchase/inspect current pin diamond relief and installed bush fit; nominal purchased envelopes are not supplier-certified solids.',
                'No integrated machine collision, storage, reach, stiffness or repeated-setup qualification claimed by this module.']
    return m,metadata

def build_protected_dock(width=438.6666666667,length=423.3333333333):
    """Local fixed-interface state after carrier/clamps leave; add gravity caps.

    This is not a claim that the machine's complete bed has a storage route.
    """
    m,metadata=build_dock(width,length)
    m.parts=[p for p in m.parts if p.group=='locator_fixed']
    for i,(x,y) in enumerate(metadata['centers_mm'],1):
        cap=cyl(22,23).cut(cyl(12,22)).clean()
        m.add(f'COMMON_PIN_CAP_{i}',cap,origin=(x,y,12),pn='LOC_CHIP_CAP_OD22_ID12_L23',
              group='locator_protection',material='Steel cap',color=(.14,.35,.55),
              notes=['Gravity slip cap on pin pedestal; 1mm closed end. Fit only after carrier removal; lift off before docking.',
                     'Caps are swarf shields, not watertight seals or load-bearing stops. Clean/dry pins and bushes before docking.'])
    return m,metadata

if __name__=='__main__':
    import json,os
    out=Path(__file__).resolve().parent/'output'
    m,meta=build_dock()
    export(m,out,'common-locator-dock',individual=True)
    (out/'interface.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    print(json.dumps({'parts':len(m.parts),'out':str(out)}),flush=True)
    sys.stdout.flush();sys.stderr.flush();os._exit(0)
