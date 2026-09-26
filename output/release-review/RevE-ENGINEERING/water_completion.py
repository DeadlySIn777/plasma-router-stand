"""Rev H service hatches and water plumbing definition.

Fabricated parts are real solids. Purchased plumbing reserves remain amber and
guarded: no supplier port datums or thread engagements are invented here.
"""
import math
import cadquery as cq
from cad_helpers import *
from frame_details import hexpart

LID_Z=430.048
LID_TOP=433.096
HATCHES=(
    dict(tag='CLARIFIED',cover=(330.,945.,360.,215.),opening=(350.,965.,320.,175.),park_y=935.),
    dict(tag='SETTLING',cover=(440.,1180.,310.,140.),opening=(460.,1200.,270.,100.),park_y=1168.),
)

def _plate_again(p,origin,u=(1,0,0),v=(0,1,0)):
    f=p.flat
    p.local=plate(f['outline'],f['thickness_mm'],f['holes'],f['slots'],f['internal'])
    p.shape=place(p.local,origin,u,v)

def _hatches(m):
    lid=m.find('WT_LID')
    lid.notes=[n.replace('remove lid for tank washout','use the separate service hatches for routine washout') for n in lid.notes]
    lid.notes.extend(['Rev H: routine washout is through two independent service openings; the equipment lid remains installed.',
                      'The full lid is a major-disassembly item, not a verified routine removal. Drain and isolate before opening either hatch.'])
    for h in HATCHES:
        tag=h['tag'];x,y,w,d=h['cover'];hx,hy,hw,hd=h['opening']
        boltxy=[(x+10,y+10),(x+w/2,y+10),(x+w-10,y+10),
                (x+10,y+d-10),(x+w/2,y+d-10),(x+w-10,y+d-10)]
        lid.flat['internal'].append([(hx-91.952,hy-681.952),(hx+hw-91.952,hy-681.952),
                                     (hx+hw-91.952,hy+hd-681.952),(hx-91.952,hy+hd-681.952)])
        lid.flat['holes'].extend([(xx-91.952,yy-681.952,5.5) for xx,yy in boltxy])
        holes=[(xx-x,yy-y,5.5) for xx,yy in boltxy]
        opening=[(hx-x,hy-y),(hx+hw-x,hy-y),(hx+hw-x,hy+hd-y),(hx-x,hy+hd-y)]
        m.add_plate('H_WT_'+tag+'_GASKET',w,d,2,holes=holes,internal=[opening],origin=(x,y,LID_TOP),
                    material='2mm EPDM gasket; verify coolant compatibility',group='water_service',color=(.12,.12,.12),
                    notes=['Knife cut, not a metal cutting program. Splash seal only; tank remains permanently vented.'])
        cover=m.add_plate('H_WT_'+tag+'_COVER',w,d,3.048,holes=holes,origin=(x,y,LID_TOP+2),
                    material='A36 steel0.120in sheet',group='water_service',color=WATER,
                    notes=['Six M5x16 screws into underside weld nuts. Remove screws before lifting; retain gasket on the fixed lid.',
                           'Lift 50 mm, move forward to parking Y%.3f, rotate +90 degrees about the cover lower/front edge, then lower into both 40 mm deep parking pockets.'%h['park_y'],
                           'Open position is service only. Confirm the panel is fully seated in both pockets; do not operate machine with a hatch open.',
                           'These are vacuum-wand/long-brush washout openings; tank cleaning efficacy is a physical commissioning check.'])
        m.add_plate('H_WT_'+tag+'_PULL_TAB',20,30,3,holes=[(10,20,12)],origin=(x+w/2-10,y+50,LID_TOP+2+3.048),u=(1,0,0),v=(0,0,1),
                    pn='H_WT_PULL_TAB',group='water_service',material='A36 steel3mm',
                    notes=['Weld20 mm lower edge to cover top; deburr12 mm lifting-hook hole. Cover and tab move as one weldment. This is not a rated hoist point.'])
        for i,(xx,yy) in enumerate(boltxy,1):
            m.add(f'H_WT_{tag}_NUT_{i}',hexpart(8,4,5),origin=(xx,yy,LID_Z-4),pn='STD_M5_WELDNUT',
                  material='M5 weld nut',group='water_service',purchased=True,color=HARDWARE)
            bolt=cyl(5,16).fuse(cyl(8.5,5).translate((0,0,16))).clean()
            m.add(f'H_WT_{tag}_BOLT_{i}',bolt,origin=(xx,yy,LID_TOP+2+3.048-16),pn='STD_M5x16_SOCKET',
                  material='M5x16 socket screw',group='water_service',purchased=True,color=HARDWARE)
        # Each loose cover parks vertically against a 40 mm deep pocket, held
        # by both faces and end walls. No hinge, friction-only prop or mystery latch.
        for i,px in enumerate((x+30,x+w-70),1):
            py=h['park_y']-7
            m.add_plate(f'H_WT_{tag}_PARK_FLOOR_{i}',40,14,3,origin=(px,py,LID_TOP),
                        pn='H_WT_PARK_FLOOR',group='water_service',notes=['Seal weld perimeter to equipment lid; bottom support for service cover.'])
            for j,yy in enumerate((py+3,py+14),1):
                m.add_plate(f'H_WT_{tag}_PARK_FACE_{i}_{j}',40,40,3,origin=(px,yy,LID_TOP+3),u=(1,0,0),v=(0,0,1),
                            pn='H_WT_PARK_FACE',group='water_service',notes=['Weld to pocket floor; installed inner gap is 8 mm for the 3.048 mm cover.'])
        # End stops sit beyond the full cover width, not inside its lower edge.
        for j,xx in enumerate((x-3,x+w),1):
            m.add_plate(f'H_WT_{tag}_PARK_END_{j}',8,40,3,origin=(xx,h['park_y']-4,LID_TOP),u=(0,1,0),v=(0,0,1),
                        pn='H_WT_PARK_END',group='water_service',notes=['Weld bottom edge to lid just beyond the service cover ends; limits sideways movement.'])
    _plate_again(lid,(91.952,681.952,LID_Z))

def _refill(m):
    # Three straight NPS1/2 pipe pieces, 45-degree miter cuts, welded into an
    # open inverted U. Polyline sweep is the exact joined nominal miter solid.
    pts=[(385,1255,695),(385,1255,885),(385,1215,885),(385,1215,865)]
    path=cq.Wire.makePolygon([cq.Vector(*p) for p in pts])
    s=cq.Workplane(cq.Plane(origin=pts[0],xDir=(1,0,0),normal=(0,0,1))).circle(10.65).circle(7.9).sweep(path,transition='right').val()
    m.add_shape('H_REFILL_MITER_SPOUT',s,group='water_refill',material='NPS0.5 schedule40 steel pipe, welded miter assembly',color=WATER,
                notes=['Fabricated pipe OD21.3 ID15.8 mm. Centerline: (385,1255,695)->(385,1255,885)->(385,1215,885)->(385,1215,865).',
                       'Two 90-degree turns use paired 45-degree miters. Use individual blank allowance and fit/weld to this centerline; pressure/leak test before assembly.',
                       'Three centerline segment lengths 190/40/20 mm; these are not square-end blank lengths. Long-point miter blank allowances are 200.65/61.3/30.65 mm before dressing/thread allowance.',
                       'Bottom end is 1/2 NPT male, receipt-fit reinforced hose adapter. Top discharge remains open: no downstream valve/nozzle.',
                       'Outlet low edge Z865 gives 30 mm nominal air gap above Z835 pan rim, exceeding the specified 25 mm minimum. Maintain at least25 mm as built.'])
    floor=m.find('WP_FLOOR');cs=1/math.sqrt(1.0001)
    floor.flat['holes'].append((385-115,(1255-105)/cs,21.6))
    _plate_again(floor,(115,105,747),v=(0,cs,-.01*cs))
    floor.notes.append('Rev H: Ø21.6 normal hole at world XY(385,1255) receives the vertical refill riser; seal weld annulus, leak-test and coat after welding.')
    # The radius relief is an actual open profile. It is deliberately polygonal
    # so the single DXF outer contour and STEP have the same cut topology.
    a=math.asin(-3.048/10.9)
    relief=[(13+10.9*math.cos(t),3.048+10.9*math.sin(t)) for t in [a+(math.pi-2*a)*i/48 for i in range(49)]]
    outline=[(0,0),(0,50),(26,50),(26,0)]+relief
    m.add_plate('H_REFILL_STAY',26,50,6,outline=outline,origin=(372,1251.952,790),group='water_refill',material='A36 steel6mm',
          notes=['Weld rear26 mm edge to pan rear inner wall atY1301.952. Fit/weld the open radial relief to the riser after pan welding; do not force the floor.',
                 'Open radius relief is a48-segment contour at nominalR10.9. STEP and DXF share this exact outline; dress before welding.'])
    m.add('H_REFILL_CONNECTION_RESERVE',box(100,100,120),origin=(335,1205,575),group='water_plumbing_reserve',
          material='Purchased hose/adapter space reservation',purchased=True,color=PURCHASED,
          release='HOSE CONNECTION SPACE - ACTUAL ADAPTER / BEND RADIUS UNVERIFIED',
          notes=['Reserve X335..435/Y1205..1305/Z575..695 for the lower spout connection. Bed conversion paths must remain outside this volume.',
                 'This is a keep-out allocation, not a fitted hose or a manufacturer bend-radius claim. Select actual hose/fittings and revise the allocation if required.'])
    return {'outlet_xyz_mm':[385,1215,865],'pan_rim_z_mm':835,'nominal_air_gap_mm':30,
            'minimum_as_built_air_gap_mm':25,'pump_hose_connection':'1/2 NPT male at (385,1255,695), adapter engagement remains receipt-fit.',
            'connection_exclusion_bounds_mm':[335,1205,575,435,1305,695],
            'connection_exclusion_scope':'Reserved for selected adapter and first reinforced hose bend; keep conversion handling out. Not a fitted hose or manufacturer bend-radius claim.'}

def _drain_reserves(m):
    # Missing connection dimensions cannot honestly be converted into fitted
    # purchased solids. These connected keep-out volumes make the allocation
    # visible and collision-testable, without exporting manufacturing files.
    specs=[
        ('H_DRAIN_REDUCER_RESERVE',(865,1235,650),(70,70,43.398152), '1.5 FNPT to1 MNPT reducer and receipt-selected nipple; upper datum meets existing pan neck.'),
        ('H_DRAIN_VALVE_RESERVE',(837.5,1207.5,525),(125,125,125), 'USS-MSV00009 valve: conservative125 mm reserve; actuator orientation and portface datums remain receipt measured.'),
        ('H_DRAIN_UNION_RESERVE',(865,1235,470),(70,70,55), '1in NPT union/tailpiece reserve; exact union release travel and spanner access not established.'),
    ]
    for name,origin,size,note in specs:
        m.add(name,box(*size),origin=origin,group='water_plumbing_reserve',material='Purchased plumbing space reservation',purchased=True,color=PURCHASED,
              release='PLUMBING RESERVE - PORTS AND FITTING ENGAGEMENT UNVERIFIED; NOT FITTED HARDWARE',notes=[note])
    m.add('H_DRAIN_DROP_RESERVE',pipe(20,34,25.4),origin=(900,1270,450),group='water_plumbing_reserve',
          material='1in gravity drain tail/hose space reservation',purchased=True,color=PURCHASED,
          release='PLUMBING RESERVE - FINAL TAIL LENGTH / DISCONNECTION UNVERIFIED',
          notes=['Outlet at Z450 is13.404 mm above basket splash cover. Remove downstream tail at union before lifting basket; exact release path remains a selected-union hold.',
                 'This reserve does not assert the selected fittings achieve the stated face datums. No pressure-vessel connection.'])
    return {'status':'ALLOCATION ONLY - SELECTED CONNECTION DIMENSIONS STILL REQUIRED',
            'axis_xy_mm':[900,1270],'available_stack_mm':[450,693.398152],
            'items':[dict(id=n,origin_mm=o,size_mm=s) for n,o,s,_ in specs],
            'holds':['Supplier valve connection datums and actual actuator orientation','Reducer/union/thread engagement stack and pipe support',
                     'Basket service with selected union and detached downstream tail','Suction strainer/fittings, pressure-rated hoses and hose bends are not released']}

def _washout_cap(m):
    """Fabricated flange below the rear shelf tube, avoiding an unknown NPT cap."""
    neck=m.find('WT_CLEANOUT_NECK')
    neck.local=pipe(178.048-116)
    neck.shape=place(neck.local,(900,1260,116))
    neck.length=178.048-116
    neck.notes=['Flush upper end with tank inner floor; lower end is plain, welded to the fabricated flange. The old1.5 NPT cap callout is superseded.',
                'Tank must be emptied and isolated before loosening the cleanout cover. This large opening is for washout, not controlled draining of115 L.']
    holes=[(35*math.cos(a),35*math.sin(a),6.6) for a in [math.pi/4+i*math.pi/2 for i in range(4)]]
    outer=[(45*math.cos(2*math.pi*i/128),45*math.sin(2*math.pi*i/128)) for i in range(128)]
    m.add_plate('H_WT_WASHOUT_FLANGE',90,90,6,outline=outer,holes=holes+[(0,0,48.5)],origin=(900,1260,110),
                group='water_service',material='A36 steel6mm',notes=['Diameter90 nominal128-sided flange with48.5 bore; lower pipe end seats at flange topZ116. Continuous seal weld around pipe.',
                'Four6.6 holes on70 pitch circle at45/135/225/315 degrees. Rear shelf crossmember stays untouched.'])
    m.add_plate('H_WT_WASHOUT_GASKET',90,90,2,outline=outer,holes=holes+[(0,0,48.5)],origin=(900,1260,108),
                group='water_service',material='2mm EPDM gasket; verify coolant compatibility',color=(.12,.12,.12),
                notes=['Knife cut. Vented gravity tank only; not a pressure-rated flange.'])
    m.add_plate('H_WT_WASHOUT_COVER',90,90,4,outline=outer,holes=holes,origin=(900,1260,104),
                group='water_service',material='A36 steel4mm',notes=['Flat blank with four clearance holes. Cover removal requires the empty isolated tank and a washout catch beneath.'])
    for i,(x,y,d) in enumerate(holes,1):
        bolt=cyl(10,6).fuse(cyl(6,25).translate((0,0,6))).clean()
        m.add(f'H_WT_WASHOUT_BOLT_{i}',bolt,origin=(900+x,1260+y,98),pn='STD_M6x25_SOCKET_HEAD_DOWN',
              group='water_service',material='M6x25 socket screw',purchased=True,color=HARDWARE)
        m.add(f'H_WT_WASHOUT_WASHER_{i}',pipe(1.6,12,6.4),origin=(900+x,1260+y,116),pn='STD_M6_WASHER',
              group='water_service',material='M6 plain washer',purchased=True,color=HARDWARE)
        m.add(f'H_WT_WASHOUT_NUT_{i}',hexpart(10,6,6),origin=(900+x,1260+y,117.6),pn='STD_M6_NYLOC',
              group='water_service',material='M6 nyloc nut',purchased=True,color=HARDWARE)
    return {'flange_bounds_z_mm':[110,116],'clear_bore_mm':48.5,'cover_bounds_z_mm':[104,108],
            'fasteners':'4xM6x25 head-down bolts, M6 washers and nyloc nuts',
            'limitation':'Empty and isolate tank before removal; this is not the full-inventory drain control.'}

def extend_router_model(m):
    _hatches(m)
    refill=_refill(m)
    drain=_drain_reserves(m)
    washout=_washout_cap(m)
    return {'revision':'H water/service definition','routine_washout':'Two independent lift-out hatches with captive upright in-footprint parking; original full lid remains in place.',
            'service_hatches':list(HATCHES),'water_charge_limit_litres':115,'permanently_vented':True,
            'refill':refill,'gravity_drain':drain,'washout_cap':washout,
            'remaining_holds':['Complete selected valve/union/strainer/pump port fit and supported hose route',
                               'Whole reservoir lid removal remains major disassembly, not routine service',
                               'Actual cabinet hinge/latch/door, gland entry and VFD heat rejection require selected enclosure drawings',
                               'Wet-test tank cleaning reach, float calibration, overflow flow and anti-siphon air gap']}

def extend_stored_model(m,source=None):
    # Water state is independent of the bed. The Rev G clone preserves all
    # extensions automatically; no double-adds or hatch opening during cutting.
    return m

def hatch_service_model(source):
    """Actual upright parked state; only the twelve removed cover screws omitted.

    Screw storage and screw-removal helix are outside the lid-path proof. The
    hatches are opened after isolating/draining; never a cutting configuration.
    """
    from build_revg import clone_model
    m=clone_model(source)
    for h in HATCHES:
        tag=h['tag'];x,y,w,d=h['cover'];axis=(x,h['park_y'],LID_TOP+2+50)
        for ident in ('H_WT_'+tag+'_COVER','H_WT_'+tag+'_PULL_TAB'):
            p=m.find(ident)
            p.shape=p.shape.translate((0,h['park_y']-y,50)).rotate(axis,(x+1,axis[1],axis[2]),90).translate((0,0,-49))
            p.group='water_service_open'
        m.parts=[a for a in m.parts if not a.id.startswith('H_WT_'+tag+'_BOLT_')]
    return m
