"""Reproducible unpriced mechanical bed/pan/service takeoff, no invented ownership."""
from pathlib import Path
import csv,json,hashlib
HERE=Path(__file__).resolve().parent
OUT=HERE/'review'
def run():
    mf=json.loads((OUT/'bed-manufacturing-check.json').read_text(encoding='utf-8'))
    rows=[]
    def add(item,q,mat,stock,op,status='DEFINED_NOMINAL',notes=''):
        rows.append(dict(item=item,quantity=q,material=mat,stock_mm=stock,operation=op,status=status,notes=notes))
    owned_path=OUT/'owned-stock-check.json'
    owned=json.loads(owned_path.read_text(encoding='utf-8')) if owned_path.exists() else{}
    credits={q['id'] for q in owned.get('additional_optional_credit',[])} if owned.get('passed') else set()
    for r in mf['flat_parts']:
        credit=r['id'] in ('CABINET_COVER_THREADED_TAB','CABINET_ROOF_THREADED_BLOCK') and all(r['id']+'_'+str(i) in credits for i in range(1,5))
        if credit:r=dict(r,material='Al_owned_nested_SUBPART_ONLY')
        add(r['id'],r['quantity'],r['material'],f"{r['flat_length_mm']:.4f} x{r['flat_width_mm']:.4f} x{r['thickness_mm']:.4f}",r['dxf'],
           notes='FinishedDXFprofile;readsecondaryoperationtable. Purchasedangle/washerrowsarefinishingviews,notadditionalflatstock.' if r.get('stock_form') else'Finishedprofile;rawstock/plygrainandfacingallowancesfollowmanufacturingreport.')
    for row in rows:
        if row['material']=='Al_owned_nested_SUBPART_ONLY':
            row['status']='OWNED_83_BLANK_NEST';row['notes']='Fourflatblankscreditedbyadditional_optional_credit;notwholefusedcornerangles. Verifyalloy/weldcompatibility.'
    add('Raw structural skin sheet',1,'Qualified plywood','2440x1220x12.7','Eight932x257skins,932alongqualifiedstiffdirection;doNOTaddmaterialtwice','STOCK_SOURCE','Containswoodparkingblockoffcuts atx1900/1934/1968/2002,y2;four30x60layers.')
    add('Raw core plywood',1,'9mm structural plywood','Sheet/strip nest covers28long+32crossprofiles','Half-laps9.10wide19.575deep;batchcutjig andtrialcoupon','STOCK_SOURCE','Buyrawsheetonlyoncetoobtainlistedcoreprofiles;nooverlappingstripassembly.')
    add('Raw MDF wear stock',1,'MDF','9.525raw,finished6.35;fourprofileareas','Facepadsseparately,thenpreparecounterbores/pilots','STOCK_SOURCE','Listedwearprofilesarefinishedparts,notadditionalrawmaterial;donotlowerbedbelowflushtracks.')
    add('Al T-track',8,'Al extrusion','826x19x12.7 envelope','Die/undercut/headmustmatchdrawninterface','RECEIVED_PART_FIT','Total6.608m;actualclamp/lip/nutcapacityrequiresverification.')
    add('Track backing blocks',32,'Al owned if owned-stock-check remains valid','20x20x9.525','Pilot4.2,tapM5x.8','OWNED_ALLOY_AND_NEST','NominalthreadgeometryinSTEPisnotatapdrilldiameter.')
    add('Track compression tubes',32,'Al','OD8 ID5.5 L48.575','Squareparallelends;trialfit8.2woodbores')
    add('Track screws',32,'Steel','M5x60 flathead','Actualhead/countersinkfit;7.925nominalthreadengagement','RECEIVED_PART_FIT')
    add('Dock pads material',16,'Al owned if nest valid','16x25x3.175','Useeightfront-bore/eightplainprofileparts','OWNED_ALLOY_AND_NEST','MaterialrowreferstoalreadylistedDXFparts,not16additionalpads.')
    add('Dock pad screws',32,'Steel','3x10 countersunkwood','2.2pilot;headsflush in1.7countersinks','RECEIVED_PART_FIT')
    add('Hard dock bedding',1,'Filled structural epoxy kit','0.15bondline x16pads','Cureunderflatdatumfixture;verifyfullhardcompressiveseats','MATERIAL_CURE_TEST','Notsofttapeorafloatingvoid;woodscrewspreventpadloss.')
    add('Round locator pins',4,'Steel','5.98ODx6','4deepblindledgerseat,2projection;retainingcompound','RECEIVED_FIT_TEST')
    add('Diamond locator pins',4,'Steel','5.98ODx6 withXwidth4.8','RelieveXwhilepreservingYlocation','RECEIVED_FIT_TEST')
    add('Al dry ledgers',2,'Al angle','50.8x50.8x6.35 L1120','22M6CSstations;blindlocators and8clampbores')
    add('Ledger fasteners',22,'Steel','M6countersunkbolts+matching4080Tnuts','Actualprofilegripsetsboltlength','RECEIVED_PART_FIT','Noextrafastenerat116,80 or1034,80;frontsupportsare3-bolttriangles.')
    add('Cassette clamp sleeves',8,'Al','OD10 ID6.6 L64.45','TwoeachatX117.5/1032.5,localY128.5;10.2woodbores')
    add('Cassette clamp bolts',8,'Steel','M6x80 sockethead','Headonclipped18ODDwasher;removebeforecassettelift','RECEIVED_PRELOAD_TEST','1.0mmnominalendprojectionpastlower5mmnut. Dwashersarealreadylistedfinishingprofiles.')
    add('Cassette lower washers/nuts',8,'Steel','OD12x1.6 washer +M6AF10x5nut','Fullmetalledgerseat;measurepreload/woodcontact','RECEIVED_PRELOAD_TEST')
    add('Wear screws',32,'Steel','3.5x16 flatheadwood','Headtop2belowfinishedsurface;2.5pilot11.75deepinply','RECEIVED_PART_FIT')
    add('Pan shim packs',9,'Al or compatible noncorroding metal','25x20;nominalheights3.6/6.78/10.08','Fitactualslopingpanunderside at3Xbearers','FIT_AND_LOAD_TEST')
    add('Pan keeper frame brackets',4,'One-piece Al angle/formedstock','24wide x6;70verticalbody +45/50horizontalreach','TwoM6faceholes;actualbend/bearingfitsmustmatchSTEP','RECEIVED_SECTION_FIT','Donotsubstitutetwotouchingplates;onepiece/qualifiedweldedassemblyneeded.')
    add('Pan keeper frame fasteners',8,'Steel','M6x16candidate+washer+matchingTnut','Verifyactualprofilegrip','RECEIVED_PART_FIT')
    add('Pan keeper bosses',4,'Al roundstock','OD14 x15;M6tap','Weldbossbase tocapturebracket;10mmboltthreadengagement','WELD_AND_THREAD_TEST','15mmheightnotcreditedto12.7ownedplate.')
    add('Pan keeper shoulders',4,'Metalbushing','OD8 ID6.3 L7','Set1mmupliftcapturegap withoutclampingfloatingsteelpanear')
    add('Pan keeper bolts',4,'Steel','M6x20','Preloadboss/cap/shoulder,notfloatingpanear','RECEIVED_PRELOAD_TEST')
    add('Wet drain stub',1,'Plainsteel tube','OD28 ID24 L26','Smoothweldstub,NOTNPT;matchunionadapter','RECEIVED_ADAPTER_FIT')
    add('Gravity valve',1,'Water-compatiblefullport','1in nominal,bore>=24,54bodylength38ODenvelope','ManualhandleandunionaccessperSTEP','RECEIVED_PART_FIT')
    add('Drain adapters/unions',2,'Water-compatible fittings','OD28/ID24 sideR24 +OD34/ID25downR20envelopes','Reversiblewetstubdisconnectandremovablehose','RECEIVED_PART_FIT')
    add('Drain hose',1,'Water-compatibleflexiblehose','ID25 OD34,minR100;trimactualroute','Sixsupports;R150servicecoilunderhood','RECEIVED_PART_FIT')
    add('Hose supports/clamps',6,'Compatiblehardware','Actualhose/clipgrip','Releaseforrareservice,avoidkinks','RECEIVED_PART_FIT')
    add('Union seals/threadsystem',1,'Matchingfittings/seals','Actualselectedports','NoassumedNPTonplainsmoothtube','RECEIVED_PART_FIT')
    add('Overflow external weldstuds',2,'Plainsteel','M4x16 atY872/928,Z838','Weldwithoutpiercingwetwall;2R2benttabsarelistedDXFs','WELD_TEST')
    add('Overflow detachable hardware',2,'Steel','M4nut+OD9x1.6washer+OD8ID4.4x1spacer','Removeandtranslate17mmrightoffstuds')
    add('Receiver',1,'Redpolymer candidate','712x470x389clearance','ASINB0HN3Q77HR;measure>=65Lusable','RECEIVED_LIQUID_AND_TEMP_TEST','Externalshellisnotarealinteriororliquidrating;floor-supportedandnotframeballast.')
    add('Receiver lid',1,'Candidatepolycarbonatelid','712x470x2clearance','UseRECEIVER_LID_MODIFICATION_TEMPLATE;openingR3corners','RECEIVED_GEOMETRY_TEST','Carrierfeetmustbearactualrim;hardshimheightstoZ391datum. Permanentlyopen25vent.')
    add('Hatch carrier angle stock',2,'Al angle','25x25x3 L712','Cope25eachend;topoperationviewsalreadylisted','STOCK_SOURCE','Notadditionalmaterialbeyondtwoangleoperationviewrows.')
    add('Hatch knuckles',4,'Steelround','OD8 x8;drill4.4axis','Weldandaxisdrill;finishedleaf/earprofileslisted')
    add('Hatch main pins',2,'Steel','4x30coreenvelope+head/cotterretention','Actualpin/retainerfitbeforehingeloadtest','RECEIVED_PART_FIT')
    add('Hatch index pins/Rclips',2,'Steel','4x9indexenvelope,.8crosshole/.7wireRclip','Removebeforeopening;reinsertat90degforpositiveopenlock','RECEIVED_PART_FIT')
    add('Hatch hinge bolts',4,'Steel','M4x16 +OD9x1.6washer +M4nut','2metalcompression-sleevesperhinge bypassplasticlid')
    add('Hatch hinge lid sleeves',4,'Metal','OD6 ID4.4 L2nominal','MatchactualPCthicknesswithoutcrushingit','RECEIVED_PART_FIT')
    add('Hatch latch knobs/rivnuts',2,'Steel','M4x16knob +M4rivnut3mmgrip','Rivnuttailenvelopeandcoverundersidecounterboresdefined','RECEIVED_PART_FIT')
    add('Cabinet corner angle stock',4,'Al angle','25x25x3 L710','FrontreturnreliefZ378..704;weldprofiledledges/blocks/tabs','STOCK_SOURCE','Attachmentsarelistedseparateflatprofileswithownershipperrow;backskinlaprequires8extraM4rivets.')
    add('Cabinet shelf rails',8,'Al angle','20x20x1.6 L257','3blindrivetseach;fourlevels400/475.8/551.6/627.4')
    add('Cabinet blind rivets',48,'Metal','M4nominal:24shelf+16side+8back','SHELFgrip2.4;side/back3.8;tailmuststayoutsidecassette','RECEIVED_GRIP_TEST')
    add('Cabinet anti-tip links',2,'Al','3mmone-piecebracket,sourceSTEP','Z565..595,Y600..620;postslotY610Z580','RECEIVED_JOINT_TEST')
    add('Cabinet anti-tip fasteners',4,'Steel','M4x10 +M4nut','Twoperlink;2M6x12Tnutpostsetsadditional')
    add('Cabinet anti-tip post sets',2,'Steel','M6x12candidate+matchingTnut','Actualprofilegrip','RECEIVED_PART_FIT')
    add('Cabinet cover screws/washers',4,'Steel','M4x8 +OD9x1.6washer','Blind6mmtabs;5.6mmnominalengagement')
    add('Cabinet floor screws/washers',4,'Steel','M3x6 +OD9x.8washer','Tapped3mmledges;floorisnotaworkbed')
    add('Cabinet primary-roof screws/washers',4,'Steel','M3x8 +OD9x.8washer','Tapped6mmroofblocks;headsinairgap')
    add('Cabinet steel-shield fasteners',4,'Steel','M3x12 +OD9x.8lowerwasher+M3nut','Actualholes/spacersmodeled')
    add('Cabinet shield spacers',4,'Al','OD6 ID3.3 L4.2','Airgap4.2aboveprimaryrooftop710.8')
    add('Plywood bond adhesive',1,'Exteriorstructuraladhesivesystem','Actualspread/curebydatasheet','Fullrib/skinandlapbond;trialcouponbeforeassembly','MATERIAL_CURE_TEST')
    add('Edge/pocket sealer',1,'Compatiblecoating','Coverallcutwoodedges','Moisture/thermalcompatibilitytest','MATERIAL_TEST')
    add('Metal retention/bedding adhesive',1,'Hardnoncreepingepoxy/retainer','Pads.15;rimfeetretention;locatorpins','Actualalloy/surfaceprep/cureproof','MATERIAL_CURE_TEST')
    add('Pan service dunnage',2,'Timbertooling','75x70x20','Supportparkedpan;notassumedowned')
    add('Pan adjustable clamp-head safety props',2,'Ratedservicetooling','Nominal500Nminimum each;fitserviceenvelope','Two-personcontroluntilpositivelylatched','RECEIVED_TOOL_RATING','Noownedhoistassumption;clearanceproofisnotanergonomic/liftingrating.')
    add('Unmodeled purchase holds',1,'Receivedinterfacesonly','Trackdie,threads,toterim/liquidrating,actualtoolhardware','NoextraCADchoresorthermalshieldplaceholders','PHYSICAL_QUALIFICATION','Actualshields/ATCareseparatesources/takeoffs;donotduplicateoldside-shadowstrips.')
    with (OUT/'bed-fabrication.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    meta={'rows':len(rows),'prices_included':False,'release':False,
      'scope':'Profilesplusstockandhardware.Material-reference/STOCK_SOURCErowsreferencelistedpartsandmustnotbedouble-purchased.',
      'csv_sha256':hashlib.sha256((OUT/'bed-fabrication.csv').read_bytes()).hexdigest(),
      'owned_stock_report_sha256':hashlib.sha256(owned_path.read_bytes()).hexdigest() if owned_path.exists() else None,
      'manufacturing_report_sha256':hashlib.sha256((OUT/'bed-manufacturing-check.json').read_bytes()).hexdigest(),
      'source_sha256':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('params.py','bed.py','bed_takeoff.py')}}
    (OUT/'bed-fabrication-metadata.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print('Takeoff rows',len(rows))
if __name__=='__main__':run()
