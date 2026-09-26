"""Rev I service detailing, applied after the frozen Rev H builder.

Fabricated geometry is defined here. Purchased valve/cabinet shells remain
explicitly guarded where the manufacturer has not supplied mating datums.
No historical Rev H source or evidence is changed.
"""
import math
import cadquery as cq
from cad_helpers import *
from frame_details import hexpart

VALVE_SOURCE='https://file.ussolid.com/content/JFMSV/MSV-physical-size.pdf'
CABINET_SOURCE='https://www.vevor.com/electrical-enclosure-c_10749/vevor-20x16x8-carbon-steel-electrical-enclosure-wall-mount-junction-box-ip65-p_010399775149'
STRAINER_SOURCE='https://www.seaflo.com/uploads/allimg/20251113/1-25111323053E18.jpg'
HOSE_SOURCE='https://www.parker.com/content/dam/Parker-com/Literature/Hose-Products-Division/Websphere-Supporting-Literature/FCG_HPD-Thermal-Management-Hoses-Bulletin.pdf'

def _route(points,arcs=(),diameter=15.9,inside=9.5):
    """Each arc is (segment index, exact on-arc midpoint); straight elsewhere."""
    arcs=dict(arcs);edges=[]
    for i,(a,b) in enumerate(zip(points,points[1:])):
        edges.append(cq.Edge.makeThreePointArc(cq.Vector(*a),cq.Vector(*arcs[i]),cq.Vector(*b)) if i in arcs else cq.Edge.makeLine(cq.Vector(*a),cq.Vector(*b)))
    w=cq.Wire.assembleEdges(edges);tangent=edges[0].tangentAt(0)
    normal=tuple(tangent.toTuple());u=(1,0,0) if abs(normal[0])<.9 else (0,1,0)
    wp=cq.Workplane(cq.Plane(origin=points[0],xDir=u,normal=normal)).circle(diameter/2)
    if inside:wp=wp.circle(inside/2)
    return wp.sweep(w,isFrenet=True).val(),sum(e.Length() for e in edges)

PRESSURE_POINTS=[(385,1210,665),(465,1130,665),(900,1130,665),(980,1050,665),(980,1000,665),(980,920,585),(980,920,570)]
PRESSURE_ARCS=[(0,(408.431457505,1153.431457505,665)),(2,(956.568542495,1106.568542495,665)),(4,(980,943.431457505,641.568542495))]
SUCTION_POINTS=[(180,1358,280),(180,1358,630),(260,1358,710),(1040,1358,710),(1120,1278,710),(1120,1130,710),(1120,1050,630),(1120,1050,620)]
SUCTION_ARCS=[(1,(203.431457505,1358,686.568542495)),(3,(1096.568542495,1334.568542495,710)),(5,(1120,1073.431457505,686.568542495))]

def _suction_and_strainer(m):
    # Rotate the family envelope so its head, opposite the mounting-foot tail,
    # points into the right plumbing bay. The bores must rotate with the pump.
    pump=m.find('BUY_SEAFLO31_ENVELOPE')
    pump.shape=pump.shape.rotate((865,893,0),(865,893,1),180)
    pump.notes.append('Rev I placement: head toward+X/right plumbing bay.180deg rotation changes world foot columns toX806/864; no inferred port centers.')
    tray=m.find('PUMP_TRAY')
    tray.flat['holes']=[h for h in tray.flat['holes'] if abs(h[2]-5)>1e-6]+[(x-740,y-830,5) for x in (806,864) for y in (850.5,935.5)]
    f=tray.flat;tray.local=plate(f['outline'],f['thickness_mm'],f['holes'],f['slots'],f['internal']);tray.shape=place(tray.local,(740,830,446.952))
    tray.notes.append('Rev I head faces+X: world foot boresX806/864,Y850.5/935.5; supersedes previousX866/924 locations. Receipt-check feet before drilling.')
    s,L=_route(SUCTION_POINTS,SUCTION_ARCS)
    m.add_shape('I_SUCTION_HOSE',s,group='water_hose',purchased=True,color=(.12,.14,.16),length=L,
        release='DEFINED SUCTION ROUTE - FIELD-FIT END82SERIES CONNECTIONS REQUIRED',
        notes=[HOSE_SOURCE,'Parker801-6,3/8ID,15.9OD,350psi,28inHg vacuum rating,minR75; designedR80. Rear main runY1358/Z710 stays ahead of braceY1370.8 and above staged bed hoops.',
               'Endpoint(180,1358,280) is upper end of a field-selected1/2FNPT elbow/82series adapter on existing pickup, not the pickup port itself atZ203.048.',
               'Endpoint(1120,1050,620) connects within rear strainer end zone after port position receipt measurement. No guessed strainer port-axis is asserted.'])
    # Two guides on a narrow external stanchion; nothing penetrates lid or tank.
    m.add_plate('I_SUCTION_STANCHION',20,490,6,origin=(145,1355,220),u=(1,0,0),v=(0,0,1),group='water_hose_support',
        notes=['20x490x6 strip outside lid rear edge. Two welded stand-off arms connect to tank rear wall; keeps hose ahead of rear brace.'])
    for i,z in enumerate((250,400),1):
        m.add_plate(f'I_SUCTION_STANDOFF_{i}',20,30.952,6,origin=(145,1318.048,z),pn='I_SUCTION_STANDOFF',group='water_hose_support',notes=['Weld front20mm edge to outer reservoir rear wall; rear edge meets stanchionY1349. No tank penetration.'])
    for i,z in enumerate((300,600),1):
        m.add_plate(f'I_SUCTION_GUIDE_{i}',35,32,3,holes=[(15,20,20)],origin=(165,1338,z),pn='I_SUCTION_GUIDE',group='water_hose_support',
            notes=['Feed hose throughØ20 before end fittings; fit split soft liner and deburr. Left6mm of side edge welds to stanchion; not a hydraulic joint.'])
    for i,x in enumerate((500,800),1):
        m.add_plate(f'I_SUCTION_REAR_EYE_{i}',61.872,26,6,holes=[(49.872,13,20)],origin=(x,1308.128,697),u=(0,1,0),v=(0,0,1),pn='I_SUCTION_REAR_EYE',group='water_hose_support',
            notes=['Rear hose guideØ20 onX-axis atY1358,Z710; add split liner. Front edge welds to separate pan-wall strap.'])
        m.add_plate(f'I_SUCTION_REAR_STRAP_{i}',20,68,3.048,origin=(x-10,1308.128,697),u=(1,0,0),v=(0,0,1),pn='I_SUCTION_REAR_STRAP',group='water_hose_support',
            notes=['Upper27mm seal-welds outside pan rear wall.0.08mm fit-up clearance to nominal wall; rear eye carries hose only.'])
    # Selected strainer full-length and height are sourced. Transverse width97
    # is a conservative acceptance dimension, not an unpublished exact value.
    m.add('I_BUY_STRAINER',box(97,167,117),origin=(1040,850,500),pn='BUY_SEAFLO_SFWS_500_02',group='water_strainer',purchased=True,color=PURCHASED,
        release='SOURCED L/H ALLOCATION - TRANSVERSE WIDTH AND PORT AXIS ACCEPTANCE HELD',
        notes=[STRAINER_SOURCE,'SFWS-500-02 drawing:body length97,barb-to-barb167,overall height117mm;1/2NPT,50mesh316screen.',
               '97mm transverse acceptance width is reserved, not dimensioned by supplier. Verify actual body fits clear97mm between carrier uprights and beneath620mm top straps before fabrication.',
               'Whole strainer lifts120mm after four top screws and both hose connections are removed. Bowl washing occurs after removal from carrier; never loosen a suction fitting with pump enabled.'])
    for i,y in enumerate((850,990),1):
        local=box(25.4,25.4,57.904).cut(box(21.1836,21.1836,60).translate((2.1082,2.1082,-1))).clean()
        m.add(f'I_STRAINER_POST_{i}',local,origin=(1005,y,433.096),pn='I_STRAINER_POST',length=57.904,group='water_strainer_support',material='1x1x.083steel tube',notes=['Seal weld to lid; right-side tray support using brace stock.'])
        m.add_plate(f'I_STRAINER_POST_CAP_{i}',25.4,25.4,3,holes=[(12.7,12.7,6.6)],origin=(1005,y,491),pn='I_STRAINER_POST_CAP',group='water_strainer_support',notes=['Weld cap to tube end; M6 weld nut beneath atcenter.'])
        m.add(f'I_STRAINER_POST_NUT_{i}',hexpart(10,5,6),origin=(1017.7,y+12.7,486),pn='STD_M6_WELDNUT',purchased=True,group='water_strainer_support')
        b=cyl(6,20).fuse(cyl(10,6).translate((0,0,20))).clean()
        m.add(f'I_STRAINER_TRAY_BOLT_{i}',b,origin=(1017.7,y+12.7,480),pn='STD_M6x20_SOCKET',purchased=True,group='water_strainer_support')
    m.add_plate('I_STRAINER_TRAY',145,187,6,holes=[(12.7,22.7,6.6),(12.7,162.7,6.6)],origin=(1005,840,494),group='water_strainer_support',
        notes=['6mm steel cantilever tray; twoM6 bolts into capped posts. Strainer weight rests on tray through fitted soft pads, not its hoses.',
               'Right edgeX1150 is machine-plan boundary. Do not add outward projecting fittings. Source width acceptance and fit padding remain before fabrication.'])
    for i,y in enumerate((900,970),1):
        for j,x in enumerate((1030,1137),1):
            m.add_plate(f'I_STRAINER_UPRIGHT_{i}_{j}',10,117,3,origin=(x,y+3,500),u=(1,0,0),v=(0,0,1),pn='I_STRAINER_UPRIGHT',group='water_strainer_support',notes=['Weld lower10mm edge to tray; clear inner width97mm.'])
            m.add_plate(f'I_STRAINER_LAND_{i}_{j}',10,15,3,holes=[(5,6.5,4.5)],origin=(x,y-12,617),pn='I_STRAINER_LAND',group='water_strainer_support',notes=['Weld rear edge to upright; M4 weld nut below overhang.'])
            m.add(f'I_STRAINER_NUT_{i}_{j}',hexpart(7,4,4),origin=(x+5,y-5.5,613),pn='STD_M4_WELDNUT',purchased=True,group='water_strainer_support')
            b=cyl(4,16).fuse(cyl(7,4).translate((0,0,16))).clean()
            m.add(f'I_STRAINER_TOP_BOLT_{i}_{j}',b,origin=(x+5,y-5.5,607),pn='STD_M4x16_SOCKET',purchased=True,group='water_strainer_support')
        m.add_plate(f'I_STRAINER_TOP_{i}',117,15,3,holes=[(5,6.5,4.5),(112,6.5,4.5)],origin=(1030,y-12,620),pn='I_STRAINER_TOP',group='water_strainer_support',
            notes=['Remove bothM4 bolts and lift this top bridge before removing strainer. Soft padding secures bought strainer in carrier; never load its bowl threads.'])
    # Explicit short field-fitted inlet/outlet zones, omitted solid volumes so
    # they cannot masquerade as connected plumbing or conceal product clashes.
    return {'suction_hose_source':HOSE_SOURCE,'suction_centerline_length_mm':L,'suction_points_mm':SUCTION_POINTS,'suction_arc_midpoints_mm':SUCTION_ARCS,
        'strainer_source':STRAINER_SOURCE,'strainer_bounds_mm':[1040,850,500,1137,1017,617],
        'unfitted_connection_zones_mm':{'pickup':[155,1338,193,205,1370,280],'strainer_in':[1070,1017,570,1147,1075,630],'strainer_to_pump':[895,810,465,1147,1010,620]},
        'remaining':'Final pump-to-strainer short hose, actual strainer port axis/transverse width and endpoint fittings still need receipt dimensions; these bounded interfaces are not fictitious connected solids.'}

def _pressure_route(m):
    _remove(m,['H_REFILL_CONNECTION_RESERVE'])
    s,L=_route(PRESSURE_POINTS,PRESSURE_ARCS)
    m.add_shape('I_REFILL_PRESSURE_HOSE',s,pn='PARKER_801_6_PRESSURE_ROUTE',group='water_hose',purchased=True,color=(.13,.15,.16),length=L,
        release='DEFINED ROUTE - FIELD-TRIM ENDS / APPROVED82SERIES CONNECTIONS STILL REQUIRED',
        notes=[HOSE_SOURCE,'Parker801-6:3/8in nominal ID,15.9mm OD,350psi,75mm minimum bend radius. All three designed bendsR80mm; bracketed routing retained after end fitting.',
               'Do not substitute unreinforced tube or generic barbs. Use matching Parker82 series fittings; verify liquid/additive and diaphragm-pump pulsation compatibility. Hose pressure exceeds120psi pump shutoff; fittings also must exceed it.',
               'Centerline length is hose-routing length only; cut allowance must account for actual fitting insertion and measured pump/spout interfaces. Endpoint locations are routing datums, not claims of pump port coordinates.',
               'Maintain at leastR80 at every bend after fitting. No loose loops may intrude into hatch or bed-conversion sweep.'])
    # Small explicit connection volume, separated from the actual routed hose.
    m.add('I_REFILL_SPOUT_CONNECTION_ZONE',box(40,65,50),origin=(365,1210,645),group='water_hose_interface',purchased=True,
        release='ADJUSTABLE END CONNECTION ZONE - RECEIPT SELECT 1/2FNPT ELBOW AND82SERIES ADAPTER',
        notes=['Allowed fitting volumeX365..405/Y1210..1275/Z645..695; connects existing1/2MNPT spout end to3/8hose routing datum(385,1210,665).',
               'This is not a fabricated elbow or released port location. Selected threaded elbow/adapter must physically fit this zone and permit hose bend without forcing spout; otherwise revise and recheck.'])
    # Main run lies under the pan, ahead of bearer3. Three split support blocks
    # are made from short metal offcuts; bores take soft liners, never pinch hose.
    for i,x in enumerate((500,700,850),1):
        for half,z in [('UPPER',665),('LOWER',651)]:
            local=box(20,37,14)
            bore=place(cyl(20,22),(-1,20,0 if half=='UPPER' else 14),u=(0,1,0),v=(0,0,1))
            local=local.cut(bore)
            local=local.cut(cq.Compound.makeCompound([cyl(4.5,16).translate((10,yy,-1)) for yy in (5,33)])).clean()
            m.add(f'I_HOSE_CLAMP_{i}_{half}',local,origin=(x-10,1110,z),pn='I_HOSE_CLAMP_'+half,group='water_hose_support',material='6061 aluminum or steel offcut',
                notes=['20x37x14 split block,halfØ20 bore axislocal+X atY20; matchingupper/lower split plane at hose centerZ665.',
                       'TwoØ4.5 through holes localX10,Y5/33. Fit2mm EPDM liner around15.9mm hose; do not clamp directly on rubber or crush hose. Remove lower block for hose replacement.'])
        # 0.2 mm nominal space to bearer underside; strap welds to front face.
        m.add_plate(f'I_HOSE_CLAMP_STRAP_{i}',20,45,3,origin=(x-10,1150,665),u=(1,0,0),v=(0,0,1),pn='I_HOSE_CLAMP_STRAP',group='water_hose_support',
            notes=['Steel20x45x3 support strap, welded to bearer3 front faceY1150 overZ679.2..710. Weld or bolt a STEEL upper block; aluminum upper block needs bolted lug and is not released by this detail.'])
        m.find(f'I_HOSE_CLAMP_{i}_UPPER').material='Mild steel20x37x14 offcut'
        m.find(f'I_HOSE_CLAMP_{i}_LOWER').material='Mild steel20x37x14 offcut'
        for j,yy in enumerate((1115,1143),1):
            b=cyl(7,4).fuse(cyl(4,35).translate((0,0,4))).clean()
            m.add(f'I_HOSE_CLAMP_{i}_BOLT_{j}',b,origin=(x,yy,647),pn='STD_M4x35_HEAD_DOWN',purchased=True,group='water_hose_support')
            m.add(f'I_HOSE_CLAMP_{i}_NUT_{j}',hexpart(7,4,4),origin=(x,yy,679),pn='STD_M4_NYLOC',purchased=True,group='water_hose_support')
    return {'hose':'Parker801-6,3/8ID,15.9OD,350psi,minR75','designed_bend_radius_mm':80,'routed_centerline_length_mm':L,
        'points_mm':PRESSURE_POINTS,'arcs_midpoints_mm':PRESSURE_ARCS,
        'end_zones':{'spout':[365,1210,645,405,1275,695],'pump_connection':[895,810,450,1030,1010,620]},
        'endpoint_hold':'Pump head faces+X; actual3/8FNPT port locations unknown. Field-fit in right-side zone subject to actual tray/strainer solids; zone does not waive interference. No exact mating fit asserted.'}

def _remove(m,ids):
    ids=set(ids)
    m.parts=[p for p in m.parts if p.id not in ids]
    m.allowed_intersections={k:v for k,v in m.allowed_intersections.items() if not (set(k)&ids)}

def _disc(r,n=128):
    return [(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n)) for i in range(n)]

def _drain(m):
    _remove(m,['H_DRAIN_REDUCER_RESERVE','H_DRAIN_VALVE_RESERVE','H_DRAIN_UNION_RESERVE','H_DRAIN_DROP_RESERVE'])
    neck=m.find('WP_DRAIN_NECK')
    neck.notes=[n for n in neck.notes if 'Lower end:' not in n]
    neck.notes.append('Rev I supersedes the old lower1.5NPT thread: keep lower end plain, square and prepared for sealed butt-weld to I_DRAIN_UPPER_SLEEVE. Do not thread it.')
    # Welded reducer instead of an unspecified reducer fitting. Threaded lower
    # nipple length is a fit dimension, not a fictitious NPT stop shoulder.
    outline=[(30*math.cos(t),30*math.sin(t)) for t in [math.pi+math.pi*i/64 for i in range(65)]]+[(30,35),(-30,35)]
    m.add_plate('I_DRAIN_REDUCER_SUPPORT',60,65,6,outline=outline,holes=[(0,0,33.6)],origin=(900,1270,675),group='water_drain',
        notes=['Flat reducer/support plate. Weld NPS1.5 upper sleeve to upper face and NPS1 lower nipple through bore, then leak-test.',
               'Rear straight60 mm edge meets the lower edge of the separate pan-wall support strap. Weld to strap; does not bear on reservoir lid.'])
    m.add('I_DRAIN_UPPER_SLEEVE',pipe(12.398152),origin=(900,1270,681),group='water_drain',length=12.398152,
        notes=['NPS1.5 SCH40 OD48.3/ID40.9. Upper end butts existing pan neck atZ693.398152; continuous sealed weld. Lower end seats on reducer plate.'])
    m.add_plate('I_DRAIN_WALL_STRAP',60,90,3.048,origin=(870,1305,675),u=(1,0,0),v=(0,0,1),group='water_drain',
        notes=['Flat60x90x3.048 support. Upper27 mm attaches outside pan rear wall; lower edge supports reducer ledge. Seal weld to pan after confirming pan remains square.',
               'This strap carries valve/pipe dead weight; no hose or operator loads are permitted on the actuator.'])
    # v=+Z yields normal -Y: put strap outside wall rather than through it.
    p=m.find('I_DRAIN_WALL_STRAP');p.shape=place(p.local,(870,1308.128,675),u=(1,0,0),v=(0,0,1))
    p.notes.append('Rear face datumY1308.128 leaves0.080mm nominal fit-up gap to pan rear wall/floor projection; bridge with continuous weld, not a bolted load path.')
    # A sourced outer allocation. The stem offset is bounded, not a vendor
    # machining model. Both end port clearances only represent NPT engagement.
    s=cyl(49,72).fuse(place(cyl(20,49),(0,-49,36),u=(1,0,0),v=(0,0,-1))).fuse(box(81.6,58,62.1).translate((-40.8,-107,4.95)))
    s=s.cut(cyl(25,74).translate((0,0,-1))).cut(cyl(34,18)).cut(cyl(34,18).translate((0,0,54))).clean()
    m.add('I_BUY_DRAIN_VALVE',s,origin=(900,1270,580),pn='BUY_USS_MSV00009',group='water_drain',purchased=True,color=PURCHASED,
        release='SOURCED PURCHASED ALLOCATION - FACE LENGTH AND STEM OFFSET MUST BE RECEIPT VERIFIED',
        notes=[VALVE_SOURCE+' pages3-4: exact SKU stainless1in full-port, L72,d25,H49; actuator81.6x62.1x58.',
               'Actuator faces forward(-Y). Stem-side extent conservatively107 mm from pipe axis; H is not an explicit port-axis offset. This is an outer allocation, not the manufacturer solid.',
               'Manufacturer product photo separately labels about81 mm overall. Fit upper/lower nipples after measuring the received valve; do not order prefabricated cut nipples from this nominal face stack.',
               '1in FNPT both ends; 24V2wire normally-closed auto-return; no inferred position feedback. Keep actuator dry and below its40C ambient limit.'])
    m.add('I_DRAIN_UPPER_NIPPLE',pipe(45,33.4,26.6),origin=(900,1270,636),group='water_drain',length=45,
        release='GUARDED FIT-TO-ASSEMBLY PIPE - NPT END AND LENGTH REQUIRE RECEIVED VALVE',
        notes=['Nominal45 mm NPS1 SCH40 stub; upper end flush reducer top681. Lower1NPT thread is represented by clearance only.',
               'Fit and mark after valve is hand/makeup assembled to its maker guidance. Nominal16 mm engagement is an allocation, not specified tightening or manufactured length.'])
    m.add('I_DRAIN_LOWER_NIPPLE',pipe(56,33.4,26.6),origin=(900,1270,542),group='water_drain',length=56,
        release='GUARDED FIT-TO-ASSEMBLY PIPE - NPT END AND LENGTH REQUIRE RECEIVED VALVE',
        notes=['Lower plain end welds into top flange with bottom flushZ542. Upper1NPT engages valve; nominal face datum580.',
               'Cut final length after valve assembly to hold fixed flange lower faceZ542; unknown thread makeup must not be imposed on the pan.'])
    holes=[(35*math.cos(a),35*math.sin(a),6.6) for a in [math.pi/4+i*math.pi/2 for i in range(4)]]
    for tag,z,t in [('FIXED_FLANGE',542,6),('TAIL_GASKET',540,2),('TAIL_FLANGE',534,6)]:
        m.add_plate('I_DRAIN_'+tag,90,90,t,outline=_disc(45),holes=holes+[(0,0,33.6 if tag!='TAIL_GASKET' else 34)],origin=(900,1270,z),group='water_drain',
            material='2mm EPDM; verify coolant compatibility' if tag=='TAIL_GASKET' else 'A36 steel6mm',
            notes=['FourØ6.6 holes on70 PCD at45/135/225/315deg. Dimensioned removable gravity tail connection, no purchased union.',
                   'Empty pan and isolate pump before removing all four bolts. Lower6, move90 forward, lift40, move140 right, move90 rearward, then lower47.904 into its parking cup.'])
    m.add('I_DRAIN_TAIL',pipe(90,33.4,26.6),origin=(900,1270,450),group='water_drain',length=90,
        notes=['NPS1 SCH40 straight90 mm. Upper end flush top of lower flangeZ540; continuous weld at flange bore. Lower outletZ450,13.404 mm above basket splash cover.'])
    for i,(x,y,d) in enumerate(holes,1):
        b=cyl(10,6).fuse(cyl(6,30).translate((0,0,6))).clean()
        m.add(f'I_DRAIN_BOLT_{i}',b,origin=(900+x,1270+y,528),pn='STD_M6x30_HEAD_DOWN',purchased=True,group='water_drain')
        m.add(f'I_DRAIN_WASHER_{i}',pipe(1.6,12,6.4),origin=(900+x,1270+y,548),pn='STD_M6_WASHER',purchased=True,group='water_drain')
        m.add(f'I_DRAIN_NUT_{i}',hexpart(10,6,6),origin=(900+x,1270+y,549.6),pn='STD_M6_NYLOC',purchased=True,group='water_drain')
    # Closed parking cup on existing lid: no tank penetration and no loose spool
    # balanced on its flange. Supports pipe on base, collar restrains sideways.
    m.add_plate('I_DRAIN_PARK_BASE',40,60,3,origin=(1020,1240,433.096),group='water_drain',notes=['Weld the three supported edges to lid; right edge overhangs existing lid1.952mm. Supports detached gravity tail only.'])
    m.add('I_DRAIN_PARK_COLLAR',pipe(35,40,35),origin=(1040,1270,436.096),group='water_drain',length=35,
        notes=['Fabricated35 mm collar, ID35.0, OD40.0. Weld bottom to base. Lower pipe into cup until end restsZ436.096; flange thenZ520.096.'])
    return {'valve_reference':VALVE_SOURCE,'valve_nominal_faces_z_mm':[580,652],
        'gravity_tail_outlet_z_mm':450,'tail_flange_seal_plane_z_mm':540,
        'support':'Reducer ledge and rear pan-wall strap; no valve weight carried by reservoir cover',
        'supplier_hold':'Actual valve face length (source conflict72vs~81mm), port-axis/stem offset and NPT makeup; field-trim nipples before welding.',
        'pressure_status':'Fabricated flange is for vented gravity drain only; not a pressure-vessel fitting.'}

def _cabinet(m):
    _remove(m,['BUY_CONTROL_ENCLOSURE_RESERVE'])
    # Manufacturer body dimensions, with a conservative full-area closure
    # allocation. No invented hinges/latches are presented as purchased parts.
    shell=box(400,200,500).cut(box(397,198.5,497).translate((1.5,0,1.5)))
    # User-defined sealed through-bolts. These are drilled as one assembly;
    # vendor wall-mount pendants are intentionally not assumed interchangeable.
    for x in (85,315):
        for z in (25,455):shell=shell.cut(place(cyl(6.6,5),(x,197,z),u=(1,0,0),v=(0,0,-1)))
    # Two distinct gland entry windows. Their fabricated covers have exact flats.
    for x in (25,230):shell=shell.cut(box(145,80,5).translate((x,75,-1)))
    m.add('I_CABINET_BODY',shell.clean(),origin=(375,255,165),pn='BUY_VEVOR_SPT_500_400_200_BODY',group='controls_envelope',purchased=True,
        release='SOURCED BODY ALLOCATION - VENDOR FLANGES/HINGES/LATCH AND MODIFICATION ACCEPTANCE HELD',
        notes=[CABINET_SOURCE,'Published500x400x200 outer;1.5 steel; interior497x397x166.5. Outer shell is a simplified manufacturer allocation, not a fabrication drawing of the bought box.',
               'New custom back holes atX460/690,Z190/620: drill with cage in place and deburr; fit bonded sealing washers. They replace the unknown vendor pendant mounting pattern.',
               'Two145x80 bottom windows defined in assembly, each covered by a separate gasketed175x110 gland plate. Verify they do not intersect the received vendor outlet cutout/returns before cutting. Enclosure rating after modification is not asserted.'])
    m.add('I_CABINET_DOOR_ALLOCATION',box(397,33.5,497),origin=(376.5,255,166.5),group='controls_envelope',purchased=True,
        release='ACCESS-CLOSURE ALLOCATION - HINGE/LATCH DRAWING NOT AVAILABLE; NO OPENING CERTIFICATION',
        notes=['Uses sourced usable-depth exclusion, not assumed physical33.5mm solid door. Actual folded return, hinge pin, lock and opening angle must be checked on selected VEVOR model.',
               'Service the cabinet only with router panels installed and front storage bay empty. No cabinet access is required during normal in-footprint bed conversion.'])
    m.add_plate('I_CABINET_BACKPLATE',350,450,2,origin=(400,422,190),u=(1,0,0),v=(0,0,1),group='controls_panel',purchased=True,
        material='Vendor galvanized backplate2mm',release='SOURCED350x450 PANEL - STANDOFF DATUM AND VENDOR RETENTION HELD',
        notes=['Component faceY420; envelope planeX400..750,Z190..640. Purchased350x450x2 dimensions; Y422 is design placement pending receipt measurement.',
               'Keep component projections toY300..420,10mm clear around panel perimeter, and separate mains/VFD from24V/signal wiring. Root controls authority defines allocation/netlist.',
               'No electronics thermal or EMC qualification follows from shell clearance.'])
    for rail in (1,2):
        p=m.find('CAB_RAIL_'+str(rail));z=190 if rail==1 else 620
        p.local=p.local.cut(cq.Compound.makeCompound([place(cyl(6.6,27.4),(x-352.7,-1,12.7),u=(1,0,0),v=(0,0,-1)) for x in (460,690)])).clean()
        p.shape=place(p.local,(352.7,455,z-12.7));p.notes.append('Rev I: actual twoØ6.6 holes through both rail walls at worldX460/690 and rail centerZ; localX107.3/337.3,Y-axis. Match-drill enclosure, fit sealed washers.')
        # Bore clearances now remove the previous tube overlap exceptions.
        for j in (1,2):m.allowed_intersections.pop(frozenset((f'CAB_BOLT_{rail}_{j}',p.id)),None)
    for ri,z in enumerate((190,620),1):
        for hi,x in enumerate((460,690),1):
            # Existing bolt's head bears exactly against rear-panel inner face.
            # Sealing washer is specified but unmodeled thickness may require
            # shorter/longer screw on actual box, so do not claim sealed joint.
            m.find(f'CAB_BOLT_{ri}_{hi}').notes.append('Rev I hole geometry is explicit; bonded sealing washer/interface thickness remains receipt-fit with enclosure.')
    entries=[]
    for tag,x,holes in [('MAINS',385,[(45,40,20.5),(105,40,20.5)]),('SIGNAL',590,[(35,35,16.5),(85,35,16.5),(135,35,16.5),(35,75,16.5),(85,75,16.5),(135,75,16.5)])]:
        fast=[(10,10,5.5),(165,10,5.5),(10,100,5.5),(165,100,5.5)]
        m.add_plate('I_CAB_GLAND_'+tag,175,110,2,holes=holes+fast,origin=(x,315,161),group='controls_glands',material='304 stainless2mm',
            notes=['Flat removable gland plate under cabinet floor; deburr bores. Mains and signal plates are separate to preserve wiring segregation.',
                   'Hole diameters nominalM20/M16 clearance only. Select glands for actual cable OD, sealing and EMC termination; unused entries need rated blank plugs.',
                   'Before cutting purchased enclosure, verify these footprints avoid vendor bottom returns/cutout; failed acceptance requires redesigned plates, not open holes.'])
        opening=[(15,15),(160,15),(160,95),(15,95)]
        m.add_plate('I_CAB_GLAND_GASKET_'+tag,175,110,2,holes=fast,internal=[opening],origin=(x,315,163),group='controls_glands',material='2mm closed-cell EPDM',
            notes=['Knife-cut gasket; outside145x80 opening. Compression/ingress test required after assembly.'])
        # Custom4-hole mounting through bottom wall, no floating covers.
        body=m.find('I_CABINET_BODY')
        for i,(xx,yy,d) in enumerate(fast,1):
            tool=cyl(d,5).translate((x+xx-375,315+yy-255,-1))
            body.local=body.local.cut(tool).clean()
            b=cyl(8.5,5).fuse(cyl(5,16).translate((0,0,5))).clean()
            m.add(f'I_CAB_GLAND_{tag}_BOLT_{i}',b,origin=(x+xx,315+yy,156),pn='STD_M5x16_HEAD_DOWN',purchased=True,group='controls_glands')
            m.add(f'I_CAB_GLAND_{tag}_NUT_{i}',hexpart(8,4,5),origin=(x+xx,315+yy,166.5),pn='STD_M5_NYLOC',purchased=True,group='controls_glands')
        body.shape=place(body.local,(375,255,165))
        entries.append({'domain':tag,'plate_bounds_mm':[x,315,161,x+175,425,163],'entries_world_xy_d_mm':[[x+xx,315+yy,d] for xx,yy,d in holes]})
    return {'source':CABINET_SOURCE,'outer_xyz_mm':[400,200,500],'inner_xyz_mm':[397,166.5,497],
        'backplate_bounds_mm':[400,420,190,750,422,640],'component_preliminary_bounds_mm':[410,300,200,740,420,630],
        'gland_entries':entries,'service':'Front storage must be empty; hinge/lock full service path remains receipt gate.',
        'thermal':'Sealed enclosure; actual VFD/PSU losses and allowable ambient not yet qualified. No generic fan-flow approval.'}

def extend_router_model(m):
    drain=_drain(m)
    cabinet=_cabinet(m)
    pressure=_pressure_route(m)
    suction=_suction_and_strainer(m)
    return {'revision':'I service detail','drain':drain,'cabinet':cabinet,'pressure_hose':pressure,'suction_strainer':suction,
        'preserved':'Tank permanently vented;115L circuit charge maximum; refill air gap30mm; existing bed conversion/hatches.',
        'open_interfaces':['Valve physical face length/stem offset and nipple fit','Pressure/suction hoses and selected strainer complete route','Pump head port coordinates and mounting feet','Cabinet hinge/latch/gland acceptance, panel retention, thermal/EMC validation']}

def extend_stored_model(m,source=None):
    return m

def tail_service_model(source):
    from build_revg import clone_model
    m=clone_model(source)
    _remove(m,[p.id for p in m.parts if p.id.startswith(('I_DRAIN_BOLT_','I_DRAIN_WASHER_','I_DRAIN_NUT_'))])
    for name in ('I_DRAIN_TAIL','I_DRAIN_TAIL_FLANGE','I_DRAIN_TAIL_GASKET'):
        p=m.find(name);p.shape=p.shape.translate((140,0,436.096-450))
    return m
