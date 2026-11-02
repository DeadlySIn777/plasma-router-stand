"""Current integrated-table takeoff, exclusive stock allocations and honest costs.

No account data, orders, private history, prices inferred from CAD, or old
83-blank credits. Detailed source rows are reconciled, then grouped into
raw-stock/hardware families for a readable purchase-preparation schedule.
"""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import ast,csv,hashlib,json,re

HERE=Path(__file__).resolve().parent;MACHINE=HERE.parent;ROOT=MACHINE.parents[1]
BASE=ROOT/'variants/extrusion-reengineered'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def relative(p):return Path(p).relative_to(ROOT).as_posix()
def jread(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def cread(p):
    with Path(p).open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def jwrite(p,o):Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
def cwrite(p,rows):
    assert rows
    with Path(p).open('w',encoding='utf-8',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

INPUT={
 'frame_geometry':MACHINE/'mechanical.py',
 'assembly_factory':MACHINE/'assembly.py',
 'current_custom_manifest':HERE/'current-custom-check.json',
 'current_custom_index':HERE/'current-custom-index.json',
 'frame_source_takeoff':BASE/'review/frame-fabrication.csv',
 'motion_source_takeoff':BASE/'motion-fabrication.csv',
 'head_takeoff':MACHINE/'head/output/selected-head-pack/selected-head-requirements.csv',
 'head_manifest':MACHINE/'head/output/selected-head-pack/selected-head-pack-check.json',
 'plasma_takeoff':MACHINE/'head/output/selected-head-pack/retained-plasma-source-requirements.csv',
 'atc_takeoff':MACHINE/'atc/output/atc-takeoff.csv',
 'atc_custom_index':MACHINE/'atc/output/custom-part-index.json',
 'atc_manifest':MACHINE/'atc/output/atc-integration-check.json',
 'atc_primary_prices':MACHINE/'atc/sources/current-primary-evidence.json',
 'owned_z_evidence':ROOT/'variants/owned-z300-assessment/owned-hardware-evidence.json',
 'retained_wet_source_takeoff':BASE/'review/bed-fabrication.csv',
 'retained_receiver_shield_takeoff':BASE/'review/shield-fabrication.csv',
 'retained_wet_drawing_manifest':BASE/'review/bed-manufacturing-check.json',
 'retained_receiver_drawing_manifest':BASE/'review/shield-manufacturing.json',
 'front_stop_transfer_source':MACHINE/'front_stop_bed_clearance.py',
 'front_stop_transfer_report':MACHINE/'output/front-stop-bed-clearance/front-stop-bed-clearance-check.json',
 'front_stop_additive_takeoff':MACHINE/'output/front-stop-bed-clearance/front-stop-additive-takeoff.csv',
 'front_stop_datum_DXF':MACHINE/'output/front-stop-bed-clearance/DATUM_20x20x6p35_D6p6_FACE_REFERENCE.dxf',
}

OWNED_EQUIPMENT=[
 ('Y_DRIVE_MODULES',2,'Complete owned1000mmYmodules with stock motors/carriages','Current owner: all motion already owned; actual lead/mount/cable/current verification remains.'),
 ('X_DRIVE_MODULE',1,'Complete owned800mmXmodule with stock motor/carriage','Current owner: all motion already owned; received interface and scale verification remains.'),
 ('Z300_MODULE',1,'Complete ownedRATTMMOTORZBX80 300mmcatalogtravel module with stock motor','Recovered selected childB09MY7XP9L; new200mmreplacement excluded; current model workingZ250, not300qualified.'),
 ('X_Y_GUIDES_AND_BLOCKS',1,'Owned extra guide-rail/block set; actual supplied fixing inventory to count','Existing rails/blocks are owned; new custom mounting plates, couplers and added fixings do not gain automatic ownership.'),
 ('MOTION_DRIVES_CONTROLLER',1,'Owned driver/control set','Actual channel count, firmware, IO isolation, voltage/current and spare capacity remain inventory/interface gates.'),
 ('SPINDLE_VFD',1,'Owned spindle/VFD kit','ER11/reverse/ATC-nut and actual supplier spindle geometry remain verification gates; no replacement kit purchased.'),
 ('ELECTRONICS_ENCLOSURE',1,'Owned electronics enclosure','Distinct from drain-water reservoir; no duplicate electronics-box purchase.'),
 ('OWNER_WORKING_ROUTER_CLAMP_BOOT',1,'Existing working65mmclamp and complete powered50mmboot with PegelongB0D6BCQCVRactuator','Owner source STEPs preserved. Complete assembly stays together for removable dock; installed boot home registration remains a fit gate.'),
 ('PLASMA_CUTTER_TORCH',1,'OwnedCUT50/VIV-arc cutter and AG60-like torch','Exact starting circuit, torch clamp zone and isolated start/height-control connections still need delivered-machine identification.'),
 ('COMPRESSOR',1,'Owned nominal12CFM air compressor','Actual pressure/duty and combined plasma/ATC air demand to verify.'),
 ('CV15HS',1,'OwnedCV-15HS venturi vacuum generator','Not a liquid pump or justification to pressurize the atmospheric receiver.'),
 ('ATC_SELECTED200_MODULE',1,'Owner-reported motion: selected200mmstroke/311mmoverall slide, motor/carriage/end blocks included','ATC source labels its module envelopes owned-motion-reported; ownership/received content inspection remains. Do not buy five envelope parts.'),
]

def stock_nests(head):
    half=[]
    for r in head['allocation']:
        x,y,w,h=r['raw_plane']
        half.append(dict(id=r['id'],x=x,y=y,w=w,h=h,finish_t=r['finished_thickness_mm']))
    three=[dict(id='BED_HINGE_MOVING_SIDEPLATE_L',x=2,y=2,w=270,h=120,finish_t=9.525),
        dict(id='BED_HINGE_MOVING_SIDEPLATE_R',x=2,y=126,w=270,h=120,finish_t=9.525),
        dict(id='CD_GRAVITY_LEDGE',x=2,y=250,w=30,h=12.7,finish_t=9.525)]
    sheets=[dict(id='EXCLUSIVE_OWNER_HALF',stock_mm=[304.8,304.8,12.7],parts=half),
            dict(id='EXCLUSIVE_OWNER_THREE_EIGHTHS',stock_mm=[304.8,304.8,9.525],parts=three)]
    checks=[]
    for sheet in sheets:
        for a in sheet['parts']:
            checks.append(dict(kind='bounds_and_thickness',sheet=sheet['id'],a=a['id'],
                passed=a['x']>=2 and a['y']>=2 and a['x']+a['w']<=302.8 and a['y']+a['h']<=302.8 and a['finish_t']<=sheet['stock_mm'][2]))
        for i,a in enumerate(sheet['parts']):
            for b in sheet['parts'][i+1:]:
                gap=(a['x']+a['w']+4<=b['x']or b['x']+b['w']+4<=a['x']or
                     a['y']+a['h']+4<=b['y']or b['y']+b['h']+4<=a['y'])
                checks.append(dict(kind='four_mm_separation',sheet=sheet['id'],a=a['id'],b=b['id'],passed=gap))
    assert len(half)==10 and len(three)==3 and all(r['passed']for r in checks)
    return dict(sheets=sheets,checks=checks,passed=True,old83blank_nest_applied=False,
        qualification='Exclusive new nominal allocations; actual alloy, thickness, dimensions, flatness, tool access and finished cleanup remain verification gates. Chips/split thickness/offcuts are never counted as extra owned stock.',
        HDPE_new_stock=dict(source_mm=[2438.4,1219.2,12.7],parts=[dict(id='HDPE_LAYER_1',x=0,y=0,w=1000,h=1219.2),dict(id='HDPE_LAYER_2',x=1003,y=0,w=1000,h=1219.2)],
            separation_kerf_mm=3,crosscut_kerf_count=2,remaining_nominal_length_mm=432.4,owned=False,
            rule='Two1000mmcrosscuts across full48in factory sheet width. Width/squareness must meet actual1219.2mm full-layer requirement; no extra long-edge trim allowance assumed. Saw cuts/circular drilling only.'))

def budget_record():
    facts=[
      dict(id='20100_BED',quantity=5,unit='two-profile1220mmpack',unit_USD='79.99',url='https://www.amazon.com/dp/B0BXNWK99C',
           shipping='Observed freePrime to30510',scope='Observed silver1220x2; only2silverpacks available. Black displayed79.99/in stock; required5pack stock quantity and final cart not confirmed.',selected_case='required'),
      dict(id='HDPE_RAW',quantity=1,unit='48x96x1/2inrawsheet',unit_USD='260.40',url='https://shop.flexpipeinc.com/us_en/d-hdpew-481-2-white-hdpe-plastic-1-2',
           shipping='UNKNOWN_NOT_ZERO',scope='One rawsheet cuts both full layers; shipping/cutting/tax not quoted.',selected_case='required'),
      dict(id='RAPIDCHANGE_BASIC4',quantity=1,unit='4pocketER11Basic',unit_USD='400.00',url='https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/',
           shipping='UNKNOWN_NOT_ZERO',scope='Basic goods floor; ProIR upgrade is separately shown. Actual selected-kit interfaces remain a release gate.',selected_case='minimum_basic'),
      dict(id='ARANA_PAIR',quantity=1,unit='28in200lbpair,4ballstudsincluded,noLmounts',unit_USD='33.24',url='https://www.amazon.com/dp/B08CNGT5Z7',
           shipping='Observed freePrime to30510',scope='SelectedST280M200/28IN200LB candidate, sale33.24/typical36.97. Four10mmballstuds included; mountingbrackets extra. Compressedlength unpublished and a60lbbullet contradicts selected200lb variant. Purchase/fit gate requires actualcompressed<=450mm,extended>=700mm and verifiedforce; these are designacceptance limits, not published dimensions.',selected_case='required_candidate_physical_gate'),
      dict(id='RAPIDCHANGE_TOOLSETTER',quantity=1,unit='opticaltoolsetter',unit_USD='50.00',url='https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/',
           shipping='UNKNOWN_NOT_ZERO',scope='Manufacturer requires tool setter; no proven owned probe credit.',selected_case='required_unless_existing_qualified_probe'),
      dict(id='RAPIDCHANGE_MOUNT_SET',quantity=1,unit='4screwpackage',unit_USD='5.00',url='https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/',
           shipping='UNKNOWN_NOT_ZERO',scope='Official package is separate; kit body price does not include these screws.',selected_case='required'),
      dict(id='RAPIDCHANGE_PRO_IR_UPGRADE',quantity=1,unit='ProIRupgrade',unit_USD='100.00',url='https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/',
           shipping='UNKNOWN_NOT_ZERO',scope='Preferred ProIR case; added toBasic, not a secondmagazine.',selected_case='preferred_upgrade'),
      dict(id='USS_MSV00009_DRAIN_VALVE',quantity=1,unit='1inNPTmotorizedNCvalve',unit_USD='50.42',url='https://ussolid.com/products/u-s-solid-motorized-ball-valve-1-stainless-steel-electrical-ball-valve-with-full-port-9-24-v-ac-dc-2-wire-auto-return-html',
           shipping='UNKNOWN_NOT_ZERO',scope='Official rounded dimension envelope; exact unions/ports/supports and actual supplied valve fit remain held.',selected_case='required_drain_candidate'),
    ]
    for r in facts:r['extended_USD']=str(Decimal(r['unit_USD'])*r['quantity'])
    amount={r['id']:Decimal(r['extended_USD'])for r in facts}
    three=amount['20100_BED']+amount['HDPE_RAW']+amount['RAPIDCHANGE_BASIC4']
    known=sum((amount[k]for k in ['20100_BED','HDPE_RAW','RAPIDCHANGE_BASIC4','ARANA_PAIR','RAPIDCHANGE_TOOLSETTER','RAPIDCHANGE_MOUNT_SET']),Decimal(0))
    assert three==Decimal('1060.35') and known==Decimal('1148.59')
    return dict(observed_date='2026-11-01',currency='USD',delivery_price_region='30510',
        basis='Root agent verified public product facts during this session. Unit-price extensions are not a saved cart, availability reservation, order or a complete delivered quote.',
        rows=facts,three_core_goods_basis_USD=str(three),known_basic_goods_subset_USD=str(known),
        known_preferred_ProIR_goods_subset_USD=str(known+amount['RAPIDCHANGE_PRO_IR_UPGRADE']),
        known_basic_with_drain_valve_goods_subset_USD=str(known+amount['USS_MSV00009_DRAIN_VALVE']),
        gas_pair_typical_price_USD='36.97',gas_typical_price_addition_USD='3.73',
        complete_delivered_total_USD=None,shipping_tax_total_USD=None,budget_cap_USD='1000.00',budget_gate='FAIL',
        minimum_three_item_goods_over_cap_USD=str(three-Decimal('1000')),
        missing_costs=['All4080profile stock and shipping, including one-piece long headers that cannot come from1500mmbars',
          'Pan, slats, receiver/drain fittings/hose, guards/thermal covers and all associated material',
          'Newlongguidebars, Zcarrier/supportbillet, gantrycorner/clevisbillets and otherunallocated custom stock',
          'Gasstrutmountingbrackets, hinges, positiveprop/pin/retention hardware, fasteners/slotnuts/washers/feet; thefourincludedballstudsarenotadditionalpurchases. Replacement/alternativestudsonlyifreceivedfitrequires.',
          'ATCadditionalplate/billet/steel and spindletoolholder/nut/collet/cuttingtool costs',
          'Sensors, cabling, chain/glands/earth interfaces and consumables not specifically inventoried owned',
          'Shipping/freight/tax/cutting and pack rounding on every nonquoted item'],
        pricing_scope='Even the observed10tracks+Basic4magazine+oneHDPEsheet unit-price extension exceeds1000 before frame/pan/hardware/shipping/tax. No design-perfect or delivered-budget-pass claim.')

def pack_profiles(cuts,stock):
    bars=[];unfit=[]
    for row in sorted(cuts,key=lambda r:r['length_mm'],reverse=True):
        need=row['length_mm']+3
        if need>stock-4:unfit.append(row);continue
        for bar in bars:
            if bar['remaining_mm']>=need:bar['cuts'].append(row);bar['remaining_mm']-=need;break
        else:bars.append(dict(stock_mm=stock,cuts=[row],remaining_mm=stock-4-need))
    return dict(stock_mm=stock,bars=bars,unfit=unfit,kerf_each_mm=3,end_trim_total_mm=4,
                raw_stock_mm=len(bars)*stock,complete=not unfit,priced=False)

def run():
    HERE.mkdir(exist_ok=True)
    missing=[relative(p)for p in INPUT.values()if not p.exists()]
    assert not missing,missing
    for key,folder in [('bed_takeoff','bed'),('utilities_takeoff','utilities')]:
        matches=list((MACHINE/folder/'output').glob('*takeoff.csv'))
        assert len(matches)==1,(key,'Need one final current subsystem takeoff, not a guessed source',matches)
        INPUT[key]=matches[0]
    for key,folder in [('bed_custom_index','bed'),('utilities_custom_index','utilities')]:
        path=MACHINE/folder/'output/custom-part-index.json'
        assert path.exists(),path
        INPUT[key]=path
    INPUT['bed_geometry']=MACHINE/'bed/integrated_bed.py'
    INPUT['utilities_geometry']=MACHINE/'utilities/integrated_utilities.py'
    INPUT['bed_geometry_report']=MACHINE/'bed/output/bed-local-check.json'
    INPUT['utilities_geometry_report']=MACHINE/'utilities/output/utility-check.json'
    INPUT['HDPE_drill_coordinates']=MACHINE/'bed/output/HDPE-DRILL.csv'
    INPUT['HDPE_drill_DXF_manifest']=MACHINE/'bed/output/HDPE-drill-dxf-check.json'
    start={k:sha(p)for k,p in INPUT.items()}
    current=jread(INPUT['current_custom_index']);current_by_id={r['id']:r for r in current}
    expected_current_files={(ROOT/r['step']).resolve()for r in current}
    current_directory=(HERE/'current-custom-step').resolve()
    assert current_directory.is_relative_to(HERE.resolve())
    for stale in current_directory.glob('*.step'):
        target=stale.resolve()
        assert target.parent==current_directory
        if target not in expected_current_files:target.unlink()
    custom_report=jread(INPUT['current_custom_manifest']);head=jread(INPUT['head_manifest'])
    nests=stock_nests(head);jwrite(HERE/'exclusive-stock-nests.json',nests)
    credit={p['id']:s['id']for s in nests['sheets']for p in s['parts']}
    rows=[]
    def add(scope,item,q,spec,material='',ownership='NEW_UNLESS_PHYSICALLY_VERIFIED',new=None,role='DISTINCT_REQUIREMENT',source='',notes='',artifacts='',ids=None,unit='each'):
        owned=ownership.startswith('OWNED')
        if new is None:new=0 if owned else q
        rows.append(dict(id=scope+':'+item,scope=scope,component_ids=';'.join(ids or[item]),quantity=q,unit=unit,
            role=role,additive=role!='NONADDITIVE_REFERENCE',ownership=ownership,new_quantity=new,
            material=material,specification=spec,source=source,artifacts=artifacts,notes=notes))
    # Current 4080 geometry, not the old19-cut frozen chassis count.
    cuts=[]
    for r in custom_report['frame_cutlist']:
        cuts.append(dict(id=r['id'],scope='FRAME',section=r['section'],length_mm=r['length_mm']))
        add('FRAME',r['id'],1,f"4080 x{r['length_mm']:.4f}mm finished",'Actual supplier Alprofile, die/core/slot qualification held',source=relative(INPUT['current_custom_manifest']))
    frame_source=cread(INPUT['frame_source_takeoff'])
    for r in frame_source:
        item,category=r['id'],r['category']
        if category=='4080 extrusion'or item in('RATED_M8_ADJUSTER','LEDGER_TO_ARM_M6_BED_SCOPE'):continue
        if category in('Flat plate','One-piece bearing angle','Tension strap','Brace spacer')and item not in current_by_id:continue
        if item in current_by_id:
            c=current_by_id[item];size=sorted((round(v,4)for v in c['finished_world_aligned_dimensions_mm']),reverse=True)
            add('FRAME',item,int(r['quantity']),f"{category}; finished bounding {size}",r['material'],
                source=relative(INPUT['frame_source_takeoff']),artifacts=c['step'],notes=c['notes']+' | Onepieceangles stayonepiece; addrawcleanup.')
        else:
            q=int(r['quantity']);note=r['holes_or_stations']+' | '+r['qualification']
            if item=='PAN_BEARING_ANGLE_M6':
                q=4*sum(n.startswith('XR_PAN_BEARING_ANGLE_')for n in current_by_id)
                note+=' | Currentonlymiddle/rearpanangles; frontanglesandfrontbearerremoved.'
            elif item=='DRY_ARM_BEARING_ANGLE_M6':
                q=4*sum(n.startswith('XR_DRY_ARM_ANGLE_')for n in current_by_id)
                note+=' | Currentonlymiddle/reardryarmangles; frontdryarms/anglesremoved.'
            add('FRAME',item,q,r['material']+' | '+r['finished_blank_or_allowance_mm'],r['material'],
                source=relative(INPUT['frame_source_takeoff']),notes=note,unit='joint set'if category=='Hardware station allowance'else'each')
    for r in current:
        if r['source']=='integrated_frame_new_custom':
            add('FRAME',r['id'],1,'Welded stock set: stepped160x325.85x6.35 flat blank +80x80x6.35 bearing seat','Uncoated plain steel6.35mm',
                source=relative(INPUT['frame_geometry']),notes=r['notes'],artifacts=r['step'],unit='stock set')
    if any(r['id'].startswith('INT_PAN_FRONT_HEADER_HANGER_')for r in current):
        add('FRAME','FRONT_PAN_HANGER_M6_HEADER',8,'M6 profile-face screw/washer/compatible slot-nut set; actual screw length held','Matching rated steel hardware',
            source=relative(INPUT['frame_geometry']),notes='Fourheaderfixingspernewhanger;notpartofmiddle/rearpanangle24/16stationallowance.',unit='joint set')
        add('FRAME','FRONT_PAN_BEAM_M8_ENDCORE',4,'M8x20socket+washer; qualify actual profile end-core tap and12.05mmnominal engagement','Matching rated steel hardware',
            source=relative(INPUT['frame_geometry']),notes='Twopernewhanger/beamend; actualdie/core/threadstrip andweld capacityheld.',unit='joint set')
    datum_ids=[r['id']for r in current if r['source']=='integrated_front_stop_datum']
    assert len(datum_ids)==4 and custom_report['new_hanger_blank_nesting']['passed']
    add('FRONT_STOP','FOUR_DATUM_BLOCKS',4,'Finish20x20x6.35, one6.6throughbore; raw22x22blanks nested inside NEWleftsteppedhangerblank',
        'Plainsteel6.35',ownership='NEW_MATERIAL_ALREADY_INCLUDED_IN_HANGER_BLANK',new=0,role='NONADDITIVE_REFERENCE',
        source=relative(INPUT['current_custom_manifest']),ids=datum_ids,
        notes='FourNEWparts mustbemade; noextra rawstockpurchase becauseactualhanger-solid nestproved4x22x22blanks inunusedsideband, with1mmedgecleanup. Thisisnotownedstockcredit.')
    add('FRONT_STOP','DATUM_M6X16_ANCHOR_SETS',4,'M6x16button+OD12x1.6washer+compatibleM6slotnut','Ratedmatchingsteelhardware',
        source=relative(INPUT['front_stop_transfer_source']),notes='Separatefourdatumanchors, notthefourreusedstopmodulebolts.',unit='joint set')
    add('FRONT_STOP','PARKED_MODULE_M6_SLOT_NUTS',4,'FouradditionalcompatibleM6slotnuts atparkedmoduleaxes','Ratedmatchingsteelhardware',
        source=relative(INPUT['front_stop_transfer_source']),notes='Originaloperatingnutsstayintheirpositions. Fouroriginalstopmodulebolts/washersaretransferred,reusedandnotboughtagain.')
    add('FRONT_STOP','NC_SERVICE_CONNECTOR_PAIRS',2,'TwoNCserviceconnectorpairsforactualfrontswitchleads;exactconnector/terminationselectionheld',
        'Actualcontrollercompatibleelectricalinterfaces',new=2,role='INTERFACE_HOLD',source=relative(INPUT['front_stop_additive_takeoff']),
        notes='Disconnectbeforemanualpark/reconnectandproveNCbeforemotion;partoftheoverallcable/controlinterface,notasecondcompletecableset.',unit='pair')
    add('FRONT_STOP','OPERATING_STATE_INTERLOCK',1,'Positiveoperating-vs-parkedmotion-enableinterlock;actualIO/sensorselectionandhardwarecountheld',
        'Actualcontrollercompatibleelectricalinterfaces',new='',role='INTERFACE_HOLD',source=relative(INPUT['front_stop_additive_takeoff']),
        notes='Onefunctionalsetfortwomodules; verifyreceivedcontrollerIOcapacity,retentionandstate-proofbeforeenergizedmotion.',unit='interface set')
    motion_source=cread(INPUT['motion_source_takeoff'])
    for r in motion_source:
        item=r['id']
        if item.startswith(('I_HEAD_','TOOL_','XR_PLASMA_DROP_','XR_DROP_'))or item in('ZBX80_BASE','ZBX80_BRAKE_MOTOR_CANDIDATE','X_GUIDE_FACE'):continue
        if item not in current_by_id and r['category'].startswith('CUSTOM'):continue
        q=int(r['quantity']);spec=r['part_number'];notes=r['notes'];artifact=''
        if item in current_by_id:
            c=current_by_id[item];spec='Finished bounding '+str(sorted((round(v,4)for v in c['finished_world_aligned_dimensions_mm']),reverse=True));artifact=c['step'];notes=c['notes']
            if item.startswith('XR_STOP_CARRIER_'):
                front='_FRONT'in item;depth=55 if front else 42
                spec=f'Weldedsteelstockset: landing43.3x{71 if front else 50}x6.35; sideleg36x{depth}x6; floor30.2x{depth}x6; tower25x48.5875x6mm'
                notes+=' | One set of FOUR source-defined cut pieces, not a solid bounding billet. Weld/load proof and cleanup remain held.'
            elif item.startswith('Y_STOP_')and item.endswith('_BRACKET'):
                front='_FRONT'in item
                spec=f'Weldedsteelstockset: shapedbase43.3x{71 if front else 50}x6.35; post15.8x50x6.35mm'+('; switchupright42x50x3mm'if front else'')
                notes+=' | Use current finishedSTEP basecornerrelief/axes; constituent rectangles are nominal blank limits, not old hole templates.'
            elif item=='X_STOP_LEFT_BODY':
                spec='Steelstockset: block20x45x26; arm16x12.4x5; switchback45x18x3mm'
                notes+=' | Machine block, weld source-defined arm/back; do not buy47x52.4x49solidbillet.'
        if item=='XR_Y_RAIL_M5_FIXINGS':q='';notes+=' | SourcezeroisquantityHOLD, not0required. Countactualownedrailholes/suppliedfixings.'
        add('MOTION',item,q,spec,r['material'],new=''if q==''else None,source=relative(INPUT['motion_source_takeoff']),notes=notes,artifacts=artifact)
    for r in current:
        if r['id'].startswith('INT_GANTRY_GUIDE_BAR_'):
            add('GANTRY',r['id'],1,'1200x40x12.7mmfinishedrailbar','Alalloy/temperheld',source=r['step'],artifacts=r['step'],notes=r['notes'])
    for item,q,spec in [('COMPRESSION_TUBES',10,'OD10ID7L80sleeve'),('M6X100_COUPLERS',10,'M6x100socket'),('M6_WASHERS',20,'OD12ID6.6x1.6'),('M6_NUTS',10,'M6,5mmhighactualgradeheld')]:
        add('GANTRY',item,q,spec,'Steel/compatiblemetalbearinghardware',source=relative(INPUT['frame_geometry']),notes='Paired4080beam coupler stations: allfourcomponents counted once. Sleeve, hole and die fit held.')
    # The actual selected shared dock has ONE owned half-sheet allocation.
    for r in cread(INPUT['head_takeoff']):
        item=r['item'];q=int(r['quantity']);ownership=r['ownership'];new=r['new_requirement_quantity']
        if item=='Owned router clamp/boot/actuator/spindle/VFD':continue # ownedinventory below
        if item=='Retained plasma float/breakaway stack':
            add('HEAD',item,1,r['specification'],role='NONADDITIVE_REFERENCE',new=0,source=relative(INPUT['head_takeoff']),notes='Detailed retained plasma requirements follow; do not charge complete assembly again.');continue
        if item=='Positive gravity ledge':ownership='OWNED_EXCLUSIVE_THREE_EIGHTHS_NEST';new=0
        elif ownership=='OWNED_HALF_SHEET':ownership='OWNED_EXCLUSIVE_HALF_NEST';new=0
        else:new=int(new)if new else ''
        add('HEAD',item,q,r['specification'],ownership=ownership,new=new,source=relative(INPUT['head_takeoff']),notes=r['qualification'])
    for r in cread(INPUT['plasma_takeoff']):
        c=current_by_id.get(r['id']);spec=r['part_number']
        if c:spec='Finished bounding '+str(sorted((round(v,4)for v in c['finished_world_aligned_dimensions_mm']),reverse=True))
        add('PLASMA_HEAD',r['id'],int(r['quantity']),spec,r['material'],source=relative(INPUT['plasma_takeoff']),artifacts=c['step']if c else'',notes=r['notes']+' | No old83blank ownedcredit.')
    # Selected slide assembly is owned once, the five clearance envelopes are
    # references. Supplier magazine/extra mechanism stock are not owned.
    atc_index={r['id']:r for r in jread(INPUT['atc_custom_index'])}
    for r in cread(INPUT['atc_takeoff']):
        item=r['id'];q=int(r['quantity']);owned=r['ownership'].startswith('owned-motion')
        role='NONADDITIVE_REFERENCE'if owned else'DISTINCT_REQUIREMENT'
        ownership='OWNED_INCLUDED_ATC_MODULE_REFERENCE'if owned else'NEW_UNLESS_PHYSICALLY_VERIFIED'
        new=0 if owned else q;notes=r['notes'];artifact=''
        if item in credit:ownership='OWNED_EXCLUSIVE_THREE_EIGHTHS_NEST';new=0;notes+=' | Facedfromoneexclusive3/8nest; nootherpartmayclaimthesameblank.'
        if item in atc_index:artifact=relative(MACHINE/'atc'/atc_index[item]['step'])
        add('ATC',item,q,r['section_or_finished_stock']or'Includedowned311mmslideenvelope',ownership=ownership,new=new,role=role,
            source=relative(INPUT['atc_takeoff']),notes=notes,artifacts=artifact,unit=r['unit'])
        if item.startswith('ATC_4080_'):
            c=atc_index[item];length=max(c['local_bounds_mm'][i+3]-c['local_bounds_mm'][i]for i in range(3))
            cuts.append(dict(id=item,scope='ATC',section='4080',length_mm=length))
    # Other subsystem takeoffs use their own final, source-bound row schema;
    # all source columns are preserved in a source snapshot JSON for audit.
    subsystem_snapshots={}
    for scope,key in [('BED','bed_takeoff'),('UTILITIES','utilities_takeoff')]:
        raw=cread(INPUT[key]);subsystem_snapshots[key]=raw
        assert raw,scope
        for r in raw:
            item=r.get('id',r.get('item'));q=r.get('quantity',r.get('qty',''))
            try:
                q=float(q);q=int(q)if q.is_integer()else q
            except(ValueError,TypeError):q=''
            spec=r.get('section_or_finished_stock',r.get('specification',r.get('stock_mm',r.get('spec',''))))
            own=r.get('ownership','new');notes=r.get('notes',r.get('qualification',''))
            if item=='BED_HDPE_RAW_OPTION':
                spec='One2438.4x1219.2x12.7rawsheet;two1000mmcrosscutsandtwo3mmkerfsleave432.4mmnominaltail'
                notes+=' | Kerf-adjusted planning normalization; retain full factory1219.2width andverifyactualsize/squareness. This raw option is not extra stock on top of two finished layers.'
            if item=='U_NEW_1P9_STEEL_GUIDE_STOCK':
                spec='Six472x94.3x1.9steelpanelblanks ONLY; weldedclipstockisseparateU_NEW_GUIDE_CLIP_STOCK'
                notes+=' | FinishedscreenSTEPincludesclip, butpurchasecounts6panelblanks+6clipstocksets, not12completeassemblies.'
            source_role=str(r.get('requirement_role',''))
            nonadd=(str(r.get('procure',r.get('additive','true'))).lower()in('false','no','0')or
                    source_role.startswith('nonadditive-')or source_role=='raw-option-not-add-on')
            role='NONADDITIVE_REFERENCE'if nonadd else'INTERFACE_HOLD'if source_role.startswith('held-')else'DISTINCT_REQUIREMENT'
            is_owned=str(own).lower().startswith('owned')
            new=0 if is_owned or role=='NONADDITIVE_REFERENCE'else''if role=='INTERFACE_HOLD'else q
            ownership='OWNED_SOURCE_REPORTED_VERIFY_CONTENTS'if is_owned else'NEW_UNLESS_PHYSICALLY_VERIFIED'
            if item in credit:
                ownership='OWNED_EXCLUSIVE_THREE_EIGHTHS_NEST';new=0;notes+=' | Exclusiveglobal13blanknest; nosecondallocationofthismaterial.'
            add(scope,item,q,spec,r.get('material',r.get('section','')),ownership=ownership,new=new,role=role,
                source=relative(INPUT[key]),notes=notes,artifacts=r.get('artifacts',''),unit=r.get('unit','each'))
            if (str(r.get('section',''))=='4080'or(r.get('category')=='extrusion'and'4080'in str(spec)))and role!='NONADDITIVE_REFERENCE':
                # Explicit takeoff length is preferred. Only parse an
                # unmistakable controlled '4080 x LENGTH' fallback, never
                # a section width from a long prose note.
                length=r.get('length_mm','')
                if not length:
                    match=re.search(r'4080\s*[x\u00d7]\s*(\d+(?:\.\d+)?)',str(spec))
                    assert match,(scope,item,'4080 length field required',r)
                    length=match.group(1)
                assert isinstance(q,int)and q>0,(item,q)
                cuts.extend(dict(id=str(item)+(('_'+str(i+1))if q>1 else''),scope=scope,section='4080',length_mm=float(length))for i in range(q))
    # U_RETAINED_WET_BASE is a reference, not a free pan/reservoir. Expand
    # only the actually retained wet stock/hardware; old cassettes, cabinet,
    # manual drain valve/pipe/hose and original guide screens are excluded.
    retained_flat_ids=set()
    retained_hardware={
        'Pan shim packs','Pan keeper frame brackets','Pan keeper frame fasteners','Pan keeper shoulders','Pan keeper bolts',
        'Overflow external weldstuds','Overflow detachable hardware','Receiver','Receiver lid',
        'Hatch carrier angle stock','Hatch knuckles','Hatch main pins','Hatch index pins/Rclips',
        'Hatch hinge bolts','Hatch hinge lid sleeves','Hatch latch knobs/rivnuts',
    }
    retained_prefixes=('HOT_','SLAT_','PAN_WELDED_EAR_','OVERFLOW_','HATCH_FIXED_','HATCH_MOVING_')
    for r in cread(INPUT['retained_wet_source_takeoff']):
        item=r['item']
        if not(item in retained_hardware or item in('PAN_FLOOR','PAN_KEEPER_CAP','SERVICE_HATCH_COVER','HATCH_RIM_FOOT_25x25')or item.startswith(retained_prefixes)):continue
        note=r['operation']+' | '+r['notes'];spec=r['stock_mm'];q=int(r['quantity']);role='DISTINCT_REQUIREMENT'
        if item=='Receiver lid':role='NONADDITIVE_REFERENCE';note+=' | Included in one reservoir/lid set; no separate lid purchase.'
        if item=='Receiver':note+=' | One complete new/unproven-owned reservoir/lid set. No consumer tote pressure rating inferred.'
        if item=='Pan shim packs':
            q=6;spec='Six25x20shim packs: threeY630,threeY1180; actual sloped pan underside'
            note='Onlysixretainedmiddle/rearpacks; threenewY300packsareseparatelylistedU_FRONT_PAN_SHIM_PACKS. OldY100shimsarenotbought. Nominalmiddle6.78/rear10.08;fitactualsupports/pan.'
        if item.startswith('PAN_WELDED_EAR_F'):note+=' | Front ears relocated to middleY station and+3.18Z; cut shape unchanged, use current utility STEP for installed pose.'
        add('WET_BASE',item,q,spec,r['material'],role=role,new=0 if role=='NONADDITIVE_REFERENCE'else q,source=relative(INPUT['retained_wet_source_takeoff']),notes=note)
        retained_flat_ids.add(item)
    for item,q,spec in [('PAN_KEEPER_MIDDLE_BOSSES',2,'AlOD14x18.18,M6tap; no duplicate15mmboss purchase'),('PAN_KEEPER_REAR_BOSSES',2,'AlOD14x15,M6tap')]:
        add('WET_BASE',item,q,spec,'Alroundstock, weld/threadqualificationheld',source=relative(INPUT['utilities_geometry']),notes='Middlefront-pairbossesare3.18mmtaller;actualengagement/shoulder/floatgapfollowscurrentutilitySTEP.')
    add('WET_BASE','RECEIVER_RIM_FOOT_RETENTION',1,'Compatible hard retention adhesive for four rim feet','Qualifiedadhesive/materialset',source=relative(INPUT['retained_wet_source_takeoff']),notes='Receiver-only tasks; no old cassette pad/locator adhesive credit. Actual plastic/Al surface prep and cure test required.',unit='material lot')
    for r in cread(INPUT['retained_receiver_shield_takeoff']):
        if not r['blank_id'].startswith('RECEIVER_'):continue
        add('RECEIVER_ROOF',r['blank_id'],int(r['quantity']),f"{r['length_mm']}x{r['developed_width_mm']}x{r['thickness_mm']}mmsteelblank",'Uncoatedplainsteel',
            source=relative(INPUT['retained_receiver_shield_takeoff']),notes=r['notes']+' | Only receiver thermal roof retained; no old guide/ledger armor material.')
    add('RECEIVER_ROOF','M6_FRAME_SETS',4,'M6x16button+washer+matchingactual4080slotnut','Steelmatchinghardware',source='RetainedSH_RECEIVERshieldhardware',unit='joint set')
    add('RECEIVER_ROOF','M4_ROOF_SETS',4,'M4x12button+washer+M4nut','Steelmatchinghardware',source='RetainedSH_RECEIVERshieldhardware',unit='joint set')
    for item,q,spec,note in OWNED_EQUIPMENT:
        add('OWNED',item,q,spec,ownership='OWNED_OWNER_REPORTED_VERIFY_CONTENTS',new=0,source='Currentownerstatement; product-onlyowned-Zandheadsourceevidence',notes=note)
    # Distinct required interface sets missing from material-only takeoffs.
    for item,spec in [('PLASMA_HEAD_TETHER','Ratednonconductiveheadtetherandterminations;actualtorchmass/arrestloadheld'),
      ('Z300_POSITIVE_MOUNTING','ActualZbase/outputfasteningandretention;receivednut/slot/threaddepthcountsheld'),
      ('Z_POWER_OFF_RETENTION','Qualifiedpoweroffhold/stoppingarrangement;unownedbrakemotornotautomaticallyselected'),
      ('CABLE_CHAIN_GLAND_EARTH_SET','Route-measuredmotion/spindle/plasmacablesupport,strainrelief,glandsandbonding'),
      ('CLAMP_WORKHOLDING_SET','Selected20100slotcompatibleworkclamps/nuts;actualquantity/workheightheld'),
      ('ATC_NUT_COLLET_TOOL_CONTENTS','Reconcilechosenmagazinekitandownedspindlecontents;actualER11nuts/collets/cuttersforfourpockets, no duplicate includedpartsorunverifiedfreecredit'),
      ('DRAIN_VALVE_POWER_IO','Fused9–24Vpower/control/cable/interlockinterfaceforNCauto-returnvalve;verifyownedpowersupply/IOcapacityandmanufacturercharge/returntiming'),
      ('SEAL_WELD_FINISH_CONSUMABLES','Qualifiedwaterpanweld/seal/corrosionandmetalcontactinsulationconsumables')]:
        add('INTERFACE',item,'',spec,new='',source='Integratedrequirementreconciliation',notes='Quantity/selectionHOLD, neverzeroorassumedfree.')
    assert len({r['id']for r in rows})==len(rows),'Duplicatephysicalrequirementid'
    # A compact stock/fastener family view; part IDs keep drawing identity.
    families=defaultdict(list)
    for r in rows:
        spec=r['specification']
        if r['artifacts']and r['scope']in('FRAME','MOTION','PLASMA_HEAD'):
            spec=spec # exactfinishedrawblankdimensionsarethegroupingbasis
        key=(r['scope'],r['role'],r['ownership'],r['material'],spec,r['unit'])
        families[key].append(r)
    compact=[]
    for i,(key,rs)in enumerate(families.items(),1):
        quantity=''if any(r['quantity']==''for r in rs)else sum(r['quantity']for r in rs)
        new=''if any(r['new_quantity']==''for r in rs)else sum(r['new_quantity']for r in rs)
        compact.append(dict(family_id=f'F{i:03d}',scope=key[0],role=key[1],ownership=key[2],quantity=quantity,new_quantity=new,
            material=key[3],specification=key[4],unit=key[5],member_ids=';'.join(r['id']for r in rs),
            source_files=';'.join(sorted({r['source']for r in rs})),notes='Individualhandedparts/holesfollowcurrentdrawingindex;finishedblanksneedcleanup.'))
    cwrite(HERE/'detailed-requirements.csv',rows);cwrite(HERE/'stock-and-hardware-families.csv',compact)
    jwrite(HERE/'subsystem-source-snapshots.json',subsystem_snapshots)
    jwrite(HERE/'price-and-budget-register.json',budget_record())
    jwrite(HERE/'owned-equipment-register.json',dict(owned_equipment=[dict(id=i,quantity=q,new_quantity=0,specification=s,qualification=n)for i,q,s,n in OWNED_EQUIPMENT],
        bed_tracks_HDPE_kit_not_proven_owned=True,old83blank_credit_applied=False,exclusive_stock_reference='exclusive-stock-nests.json',
        no_private_orders_or_account_history_published=True))
    # Full current drawing index, including other agents' final actual parts.
    drawings=[dict(id=r['id'],scope='FRAME_MOTION',file=r['step'],sha256=r['sha256'],
        role='PROFILE_OPERATION_REFERENCE_NOT_SUPPLIER_DIE'if r['category']=='Profile envelope operation reference'else'CURRENT_FINISHED_CUSTOM_STEP',notes=r['notes'])for r in current]
    for item,r in head['outputs'].items():
        path=MACHINE/'head'/r['file'];drawings.append(dict(id=item,scope='HEAD',file=relative(path),sha256=r['sha256'],role='CURRENT_SELECTED_HEAD_STEP',notes='Exclusiveheadstockallocation;notanadditionalpurchase.'))
    for scope,key in [('ATC','atc_custom_index'),('BED','bed_custom_index'),('UTILITIES','utilities_custom_index')]:
        raw=jread(INPUT[key]);raw=raw.get('parts',raw.get('outputs',[]))if isinstance(raw,dict)else raw
        if isinstance(raw,dict):raw=[dict(id=k,**v)for k,v in raw.items()]
        for r in raw:
            file=r.get('step',r.get('file'));path=MACHINE/scope.lower()/file
            drawing_role='CURRENT_SUBSYSTEM_CUSTOM_STEP';drawing_note=r.get('notes','')
            if r['id'].startswith('ATC_4080_'):drawing_role='PROFILE_OPERATION_REFERENCE_NOT_SUPPLIER_DIE'
            if r['id'].startswith('U_GRAVITY_HOSE_'):
                drawing_role='PURCHASED_FLEXIBLE_HOSE_ROUTE_REFERENCE';drawing_note+=' | Reference route, not a part to machine as rigid material; actual hose/fittings and length toverify.'
            drawings.append(dict(id=r['id'],scope=scope,file=relative(path),sha256=r.get('sha256',sha(path)),role=drawing_role,notes=drawing_note))
    for r in jread(INPUT['retained_wet_drawing_manifest'])['flat_parts']:
        if r['id']not in retained_flat_ids and not r['id'].startswith('HATCH_CROSS_ANGLE_'):continue
        path=BASE/r['dxf'].replace('\\','/')
        drawings.append(dict(id=r['id'],scope='RETAINED_WET_CUT_PROFILE',file=relative(path),sha256=r['sha256'],
            role='UNCHANGED_FLAT_CUT_PROFILE'if not r['id'].startswith('HATCH_CROSS_ANGLE_')else'PURCHASED_ANGLE_OPERATION_REFERENCE',
            notes='Local cut shape retained. Current utilities define installed poses, relocated ear stations and changedbosses; no oldY100support is authorized.'))
    for r in jread(INPUT['retained_receiver_drawing_manifest'])['manufacturing_files']:
        path=BASE/r['file'].replace('\\','/')
        if not path.stem.startswith('RECEIVER_'):continue
        drawings.append(dict(id=path.stem,scope='RETAINED_RECEIVER_ROOF',file=relative(path),sha256=r['sha256'],
            role='RETAINED_RECEIVER_THERMAL_ROOF_MANUFACTURING_REFERENCE',notes='Receiver roof only; oldrail/ledgerguardsnotincluded.'))
    for r in jread(INPUT['HDPE_drill_DXF_manifest'])['exports']:
        path=INPUT['HDPE_drill_DXF_manifest'].parent/r['file']
        drawings.append(dict(id=r['part'],scope='BED_HDPE_DRILL_ONLY',file=relative(path),sha256=r['sha256'],
            role='ROUND_THROUGH_DRILL_PATTERN_ONLY',notes='mm; localleft/frontorigin,80roundholes:1x13.2datum+79x22clearance. NoCNCpockets/slots/counterbores/facing.'))
    drawings.append(dict(id='BOTH_HDPE_DRILL_COORDINATES',scope='BED_HDPE_DRILL_ONLY',file=relative(INPUT['HDPE_drill_coordinates']),sha256=sha(INPUT['HDPE_drill_coordinates']),
        role='ROUND_THROUGH_DRILL_COORDINATES',notes='160rows/80perlayer;worldsheetleftX75/frontY-39.6;uselocalcoordinatecolumns.'))
    drawings.append(dict(id='FOUR_STOP_DATUM_FACE_REFERENCE',scope='FRONT_STOP',file=relative(INPUT['front_stop_datum_DXF']),sha256=sha(INPUT['front_stop_datum_DXF']),
        role='DATUM_BLOCK_FACE_REFERENCE',notes='One20x20face/D6.6at10,10 forfourparts; exactthickness/axesfollowcurrentSTEP. Source is not an additionalstockpurchase.'))
    assert all(sha(ROOT/r['file'])==r['sha256']for r in drawings)
    cwrite(HERE/'current-drawing-index.csv',drawings)
    # Several detailed component IDs may share a stock row, but no source
    # profile is counted in two cut groups. Both machine modes are alternatives.
    jwrite(HERE/'4080-cut-stock-options.json',dict(cuts=cuts,finished_length_mm=sum(r['length_mm']for r in cuts),
        cut_count=len(cuts),options={str(stock):pack_profiles(cuts,stock)for stock in(1500,2000)},
        selected_option=None,prices_included=False,
        rule='StockpackagingoptionsareNONADDITIVEalternatives to listedcutrequirements;thelongonepieceheadersrejectall1500stock.'))
    source_current=start=={k:sha(p)for k,p in INPUT.items()}
    bindings=[]
    for key in('current_custom_manifest','head_manifest','atc_manifest','bed_custom_index','utilities_custom_index','bed_geometry_report','utilities_geometry_report','HDPE_drill_DXF_manifest','front_stop_transfer_report','retained_wet_drawing_manifest','retained_receiver_drawing_manifest'):
        manifest=jread(INPUT[key]);source_map=manifest.get('source_sha256',{})if isinstance(manifest,dict)else{}
        for file,expected in source_map.items():
            candidates=[ROOT/file,INPUT[key].parent/file,INPUT[key].parent.parent/file]
            path=next((p for p in candidates if p.exists()),candidates[0])
            actual=sha(path)if path.exists()else None
            bindings.append(dict(manifest=relative(INPUT[key]),file=str(file),expected_sha256=expected,actual_sha256=actual,passed=actual==expected))
    jwrite(HERE/'source-manifest-binding-checks.json',bindings)
    row_by_id={r['id']:r for r in rows}
    half_credit=sum(r['quantity']for r in rows if r['ownership']=='OWNED_EXCLUSIVE_HALF_NEST')
    three_credit=sum(r['quantity']for r in rows if r['ownership']=='OWNED_EXCLUSIVE_THREE_EIGHTHS_NEST')
    atc_new_plates=['ATC_DROP_PLATE_'+s+'_'+str(i)for s in('L','R')for i in(1,2)]+['ATC_SELECTED_SLIDE_BASE_PLATE']
    cut_totals={scope:sum(r['length_mm']for r in cuts if r['scope']==scope)for scope in('FRAME','BED','ATC')}
    drill_rows=cread(INPUT['HDPE_drill_coordinates'])
    drill_counts=Counter(r['part']for r in drill_rows)
    checks=dict(source_consistent=source_current,current_custom_passed=custom_report['passed'],exclusive_stock_nests_pass=nests['passed'],
        exactly13_unique_rawstock_credits=half_credit==10 and three_credit==3,
        ATC_five_plate_blanks_new=all(row_by_id['ATC:'+item]['new_quantity']==1 for item in atc_new_plates),
        bed_two10mmspacers_new=row_by_id['BED:BED_HINGE_SPACERS']['new_quantity']==2,
        bed_gas_ballstuds_not_doublepurchased=not row_by_id['BED:BED_GAS_INCLUDED_BALLS']['additive'],
        HDPE_rawsheet_not_additional_to_layers=not row_by_id['BED:BED_HDPE_RAW_OPTION']['additive'],
        new_ten_uncut_tracks=row_by_id['BED:BED_UNCUT_20100']['new_quantity']==10,
        new_two_HDPE_layers=row_by_id['BED:BED_HDPE_FULL_LAYERS']['new_quantity']==2,
        RapidChange_kit_not_owned=row_by_id['ATC:RAPIDCHANGE_4_ER11_KIT']['new_quantity']==1,
        ownedZ300_once=row_by_id['OWNED:Z300_MODULE']['quantity']==1 and row_by_id['OWNED:Z300_MODULE']['new_quantity']==0,
        no_new200Z=not any('Z200'in r['id']for r in rows),
        current26profilecuts=len(cuts)==26 and abs(sum(cut_totals.values())-22495.7)<1e-5,
        new_datum_material_not_doublepurchased=not row_by_id['FRONT_STOP:FOUR_DATUM_BLOCKS']['additive']and custom_report['new_hanger_blank_nesting']['passed'],
        parked_nuts_are_four_additional=row_by_id['FRONT_STOP:PARKED_MODULE_M6_SLOT_NUTS']['new_quantity']==4,
        datum_four_anchor_sets_separate=row_by_id['FRONT_STOP:DATUM_M6X16_ANCHOR_SETS']['new_quantity']==4,
        pan_nine_shims_once=row_by_id['WET_BASE:Pan shim packs']['quantity']==6 and row_by_id['UTILITIES:U_FRONT_PAN_SHIM_PACKS']['quantity']==3,
        HDPE_drill_only_160coordinates=len(drill_rows)==160 and sorted(drill_counts.values())==[80,80]and all(float(r['diameter_mm'])in(13.2,22.)for r in drill_rows),
        current_drawings_hash_match=all(sha(ROOT/r['file'])==r['sha256']for r in drawings),
        current_source_manifest_bindings=all(r['passed']for r in bindings),
        all1500stock_explicitly_rejected=not pack_profiles(cuts,1500)['complete'],
        budget_honestly_fails=budget_record()['budget_gate']=='FAIL',bed_and_utilities_takeoffs_present=True)
    report=dict(study='CURRENT_INTEGRATED_MANUFACTURING_AND_BUDGET_RECONCILIATION',checks=checks,passed=all(checks.values()),
        detailed_requirement_rows=len(rows),compact_family_rows=len(compact),current_drawing_rows=len(drawings),
        source_sha256={k:dict(file=relative(p),sha256=start[k])for k,p in INPUT.items()},
        output_sha256={relative(p):sha(p)for p in HERE.rglob('*')if p.is_file()and p.name!='manufacturing-check.json'and'__pycache__'not in p.parts},
        complete_delivered_price_USD=None,budget_gate='FAIL',fabrication_release=False,operating_release=False,
        meaning_of_pass='Source/stock/reference/arithmeticreconciliationonly. Actualsupplierfit,materials,strengthandcommissioninggatesremain;budgetFAILisnotconcealedbyapassflag.')
    jwrite(HERE/'manufacturing-check.json',report)
    print(json.dumps(dict(passed=report['passed'],families=len(compact),requirements=len(rows),drawings=len(drawings),cuts=len(cuts),budget='FAIL')))
    assert report['passed'],checks

if __name__=='__main__':run()
