"""Explicit additive full-bed takeoff; no prices or invented ownership credit."""
from pathlib import Path
import csv,hashlib,json,os,sys
import integrated_bed as B

HERE=Path(__file__).resolve().parent;OUT=HERE/'output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
 OUT.mkdir(exist_ok=True);rows=[]
 def add(i,q,unit,spec,category='hardware',section='',length=0,width=0,height=0,t=0,owned='new-unless-independent-evidence',role='additive',covered='',notes=''):
  rows.append(dict(id=i,quantity=q,unit=unit,category=category,section=section,length_mm=length,width_mm=width,height_mm=height,thickness_mm=t,
    specification=spec,ownership=owned,requirement_role=role,covered_by=covered,notes=notes))
 add('BED_UNCUT_20100',10,'each','Uncut1220mm100x20supplier section, fivebroad-face slots6.2openings. Actualdie/nut/lipfitacceptance.','extrusion','20100',1220,100,20)
 add('BED_HDPE_FULL_LAYERS',1,'each','ONE1000x1200x12.7fullcut-area-coveringrectangle;80roundthroughholesonly.Front0.4/rear19.6profileoverhang.','sheet','HDPE',1200,1000,0,12.7,covered='BED_HDPE_RAW_OPTION')
 add('BED_HDPE_RAW_OPTION',1,'sheet','48x48inx1/2rawHDPE;even1212.85minimumcutsizeallows12.85cleanupfor1200finishedlength. Ordinarycuts+80roundholes,noTslotmilling.','raw-stock-option','HDPE',1219.2,1219.2,0,12.7,role='raw-option-not-add-on',covered='BED_HDPE_FULL_LAYERS')
 add('BED_CROSS_4080',4,'each','Upright40Yx80Z4080;20D13.1verticalsleevebores. Endtaps22deepforfront/assist/rear;inwardshiftedendanchorsavoidcoreboltinterference. Actualsupplier/modifiedIqualificationrequired.','extrusion','4080',980,40,80)
 add('BED_COLUMNS',80,'each','12.7OD6.35IDAlcompressiontube;92.7nominalsquare-cut,fitactualsingleHDPEstack.','tube','Al_round_tube',92.7,12.7,6.35)
 add('BED_M5X100_FINISH99P3',80,'each','M5x100socketheadstockfinished99.3+/-0.1underhead,enddeburr/chamfer<=0.4.Head8.5x5on18ODbridgewasher;full2.7nominalnutengagement+1.0tip/1.1cavityreserve.')
 add('BED_CROSS_BRIDGE_WASHERS',80,'each','SteelM6DIN9021/ISO7093largewasher18OD6.4IDx1.6bridges13.1crossbarboreandseatsbothbarundersideandsquarecolumnend;positivelycapturesthebar. VerifyactualreceivedOD/ID/thickness/flatness/grade;notasmallM5washer.')
 add('BED_BOTTOM_SLOT_NUT_M5',80,'each','Compatible20100bottom-slotM5nut;recoveredCAD8x8x2.7envelope, selectedactualnutfitstillrequired.')
 add('BED_RECEIVER_ANGLE',2,'each','Formed/trimmedsteelangle54horizontalx31.75upwebx3.175;27.3lowerseat,22mmwasheraccessatX125/mirrorpartlyopensflangeedge;actualSTEPcontrols.16M5CSmid/rearfixings.','angle','steel_angle',1050,54,31.75,3.175)
 add('BED_RECEIVER_PATCH',2,'each','120x35x3.175lowerreinforcementweb atassistnotch;newstock/noautomaticoffcutcredit.','plate-blank','steel',120,35,0,3.175)
 add('BED_RECEIVER_FIXING',16,'set','M5x10countersunk+actual40seriesM5Tnut;flushD10x2.75head. Grade,slotfitandprojectionqualified onreceiveddie.')
 add('BED_FIXED_HINGE_ASSEMBLIES',2,'assembly','SeeBED_HINGE_FIXED_L/RSTEP;welded3blankdecompositionbelow.','fabricated-reference',role='nonadditive-assembly-reference')
 add('BED_FIXED_HINGE_BASE_BLANK',2,'each','80x70x6.35steelplate,4D6.6postholes.','plate-blank','steel',80,70,0,6.35)
 add('BED_FIXED_HINGE_CHEEK_BLANK',2,'each','50x32.2x6.35steel,12.1pivotbore.','plate-blank','steel',50,32.2,0,6.35)
 add('BED_FIXED_HINGE_BRIDGE_BLANK',2,'each','25x50x6.35steelbridge;qualifiedweldloadpath.','plate-blank','steel',50,25,0,6.35)
 add('BED_FIXED_HINGE_FASTENERS',8,'set','M6postTnutattachment4perfrontpost atY−120/−80,Z967/1000;6.35plategrip,actualscrewlength/engagementbydie.')
 add('BED_HINGE_MOVING_SIDEPLATE_L',1,'each','270x128x9.525ALarm;Y-127..143,hingeaxisunchanged;2D14.2x4.6counterbores/D8.5endboresatY110,Z868.1/908.1local.','plate-blank','aluminum',270,128,0,9.525,owned='owned3/8sheet-global-unique-allocation-required',notes='Newrawnest2,2;rootmustreconcilewithrightarm2,134/ledge2,266/rib276,2.')
 add('BED_HINGE_MOVING_SIDEPLATE_R',1,'each','Mirrorofleft270x128x9.525arm.','plate-blank','aluminum',270,128,0,9.525,owned='owned3/8sheet-global-unique-allocation-required')
 add('BED_HINGE_SPACERS',2,'each','80x40x10newAlspacerrotated40Yx80Z,2D8.5bores.9.525sheetdoesnotprovide10mm.','plate-blank','aluminum',80,40,0,10)
 add('BED_HINGE_BUTTON_FASTENERS',4,'each','M8x35ISO7380buttonhead14OD4.4high;counterbored4.6;20.075endcoreengagementnominal.')
 add('BED_HINGE_PINS',2,'each','Turnedplainsteel12mmpin:inboard18headx3,24.05smoothshaft;27.05overall,D2.2throughcrosshole23.85fromouterheadface. Removeoutsidewasher/cotterthenpull26mminboard;frontpostblocksoldoutboard-fedpin.','turned-component','steel',27.05,18,12,covered='BED_RETAINED_PIN_RAW_OPTION')
 add('BED_HINGE_RETAINER_WASHERS',2,'each','Customsteel18OD12.2IDx1.6;slipontoplain12mmshaftoutsidefixedcheek,retainedby2x16cotter. Samepinbarsecondaryblank,noseparatewasherstock.','machined-ring','steel',1.6,18,12.2,covered='BED_RETAINED_PIN_RAW_OPTION')
 add('BED_HINGE_RETAINER_COTTERS',2,'each','DIN94/ISO1234splitpin2x16,formedinstalledtails;replaceafterremoval.')
 add('BED_HINGE_AXIAL_SHIM_L',1,'each','Steel18OD12.2IDx1.85nominalaxialshimbetweenfixedclevisandmovingarm;0.125nominalleftgap,fitactualbedassembly. Samepinbarsecondaryblank,noseparatestock.','machined-ring','steel',1.85,18,12.2,covered='BED_RETAINED_PIN_RAW_OPTION')
 add('BED_HINGE_AXIAL_SHIM_R',1,'each','Steel18OD12.2IDx1.35nominalaxialshim;0.625nominalrightgapforthermalfloat,fitactualassembly. Samepinbarsecondaryblank,noseparatestock.','machined-ring','steel',1.35,18,12.2,covered='BED_RETAINED_PIN_RAW_OPTION')
 add('BED_ASSIST_C_ASSEMBLIES',2,'assembly','Gas/stayendbracketSTEP, weldedconstituentsbelow.','fabricated-reference',role='nonadditive-assembly-reference')
 add('BED_ASSIST_END_WEB_BLANK',2,'each','60Zx50Yx6.35steelweb;2D8.5corefixings,externalheadclearancesinupperbridgeonly.','plate-blank','steel',60,50,0,6.35)
 add('BED_ASSIST_UPPER_BLANK',2,'each','75Yx34.2Xx6.35steelupperbridge,extendedfront/rearUcutandgas-spacer/headclearances;exactSTEPcontrols.','plate-blank','steel',75,34.2,0,6.35)
 add('BED_ASSIST_GAS_EAR_BLANK',2,'each','20x20x6.35steelgasverticalear;M8studY365movedforwardtoclearuprightendcorebolts.','plate-blank','steel',20,20,0,6.35)
 add('BED_ASSIST_CAPTURE_EAR_BLANK',2,'each','Innerplanarring+rearstrap32.4x68.65x3.175;staypivot3mmlowertoclearlowercorehead.','plate-blank','steel',68.65,32.4,0,3.175)
 add('BED_ASSIST_CAPTURE_OUTER_EAR_BLANK',2,'each','Outerplanarring+rearstrap32.4x68.65x5;10.2through/14.2x2.6headrecess;stay3mmlower.','plate-blank','steel',68.65,32.4,0,5.)
 add('BED_ASSIST_END_FIXINGS',4,'each','M8x25endcorefixings;6.35grip18.65engagementnominal.')
 add('BED_GAS_PAIR',1,'pair','New28in150lb/667Neachpaircandidate;actualeyelength456.184..658.290,requiredcompressed<=445/expanded>=700,body<=24/rod<=10/socketfit. RootselectsactualSKU;notold200lbpair.')
 add('BED_GAS_INCLUDED_BALLS',4,'each','10mmballstudslistedasincludedwithgaspackage;verifythread/neck/quantity.','included-package-reference',owned='new-with-gas-pair',role='nonadditive-package-reference',covered='BED_GAS_PAIR')
 add('BED_GAS_UPPER_STUD_SPACER',2,'each','Nominal1.05mmsteelspacer,OD12.7ID8.5;fits6.35gasearand13.15face-to-ballcentrewithnominal12.1studneckgeometry. Verifyactualstud.','metal-spacer','steel',1.05,12.7,8.5)
 add('BED_GAS_UPPER_WASHERS',2,'each','M8steelflatwasher16OD8.4IDx1.6.')
 add('BED_GAS_UPPER_NYLOC_NUTS',2,'each','M8DIN985nylocAF13/h8;3.0nominalthreadprojectionbeyondnutwithM8x20studthread,verifyactualnylonengagement.')
 add('BED_GAS_ROOT_PLATE',2,'each','80x80x6.35steelplate4M6holes,M8studhole;on14.9standoffs.','plate-blank','steel',80,80,0,6.35)
 add('BED_GAS_ROOT_SPACER',8,'each','12.7OD6.35ID14.9Alstandoff,canusecolumn-tubepackremainderifexactnestallocated.','tube','Al_round_tube',14.9,12.7,6.35)
 add('BED_CAPTURE_ROOT_ASSEMBLIES',2,'assembly','120x80backplatewithclevisfloor/earsandgascolumn/studclearancebores;seeSTEP.','fabricated-reference',role='nonadditive-assembly-reference')
 add('BED_CAPTURE_ROOT_BASE',2,'each','120x80x6.35steelpostplate,4M6fixings,4D13.1gascolclearanceandD8.5gasstudclearance.','plate-blank','steel',120,80,0,6.35)
 add('BED_CAPTURE_ROOT_FLOOR',2,'each','40x33.85x6.35steelfloor.','plate-blank','steel',40,33.85,0,6.35)
 add('BED_CAPTURE_ROOT_EARS',2,'each','Inner24x32x3.175steelring+stem,10.2pivotbore.','plate-blank','steel',32,24,0,3.175)
 add('BED_CAPTURE_ROOT_OUTER_EARS',2,'each','Outer24x32x5steelring+stem,10.2pivotbore/14.2x2.6outboardcounterbore;2.4remainingbearingweb.','plate-blank','steel',32,24,0,5.)
 add('BED_ASSIST_ROOT_FASTENERS',16,'set','4M6postTnutjointspergas/captureanchor;gasmount21.25metalstack,capture6.35;selectscrew/engagementactualdie.')
 add('BED_CAPTURE_OUTER',2,'each','20x20x2steelRHS390mm;12mmeyestandoff,10.2fullopenpinbore.','tube','steel_square_tube',390,20,20,2)
 add('BED_CAPTURE_INNER',2,'each','15x15x1.5steelRHS375mm;8.5indexrowand10.2fullopenbore,exactpositioninmodel.','tube','steel_square_tube',375,15,15,1.5)
 add('BED_CAPTURE_END_EYES',4,'each','24OD10.2IDx6.35steelweldedeye;qualifiedtube/eyeweldtransitionrequired.','machined-ring','steel',6.35,24,10.2)
 add('BED_CAPTURE_PIVOT_PINS',4,'each','CustomturnedC45/4140steelpin:14ODx2.5recessedhead,10smoothland19.15,M6x1x9.2retentionend;30.85overall,D1.8crosshole27.85fromouterheadface. SeeSTAY_PIVOT_PIN drawing/STEP. Separatewasher/nut/cotterrowsbelow.','turned-component','steel',30.85,14,10,covered='BED_RETAINED_PIN_RAW_OPTION')
 add('BED_RETAINED_PIN_RAW_OPTION',1,'bar','3/4inchx12inchC45/4140steelroundbar(19.05x304.8):4stayrough33+2openrough35+2hingepacks40+7x3kerfs=303mm. Each40packsubcuts28.5hingepin+3kerf+2.5washer+3kerf+3axialshim=40. All8pins+4ringsfromsamebar. Receivedusablelength>=303andOD>=18.5. Nonadditiverawoption,notextrafinishedparts.','raw-stock-option','steel_round_bar',304.8,19.05,19.05,role='raw-option-not-add-on',covered='BED_CAPTURE_PIVOT_PINS;BED_HINGE_PINS;BED_CAPTURE_OPEN_PINS;BED_HINGE_RETAINER_WASHERS;BED_HINGE_AXIAL_SHIM_L;BED_HINGE_AXIAL_SHIM_R')
 add('BED_CAPTURE_PIVOT_WASHERS',4,'each','M6DIN125washer12OD6.4IDx1.6;seatsonthepinshoulder,notonthemovingclevis.')
 add('BED_CAPTURE_PIVOT_CASTLE_NUTS',4,'each','M6x1DIN937slottedhexnut,AF10/h6/body3.5/slot2min;lockwith1.6mmsplitpin. PublishedAspenFastenersDIN937dimensions.')
 add('BED_CAPTURE_PIVOT_COTTERS',4,'each','DIN94/ISO1234splitpin1.6x14;replaceaftereveryremoval. BothlegsformedinboardwithintheCADinstalledenvelope.')
 add('BED_CAPTURE_OPEN_PINS',2,'each','Turnedsteel10mmfull-openlockpin:16headx3,20.3smoothland,M6x1x9.2retentionend;32.5overall,D1.8crosshole29.5fromouterheadface. Passesbothwallsofbothtubes;separatenut/washer/cotterbelow. Noimpactratinginferred.','turned-component','steel',32.5,16,10,covered='BED_RETAINED_PIN_RAW_OPTION')
 add('BED_CAPTURE_OPEN_PIN_WASHERS',2,'each','M6DIN125washer12OD6.4IDx1.6.')
 add('BED_CAPTURE_OPEN_PIN_CASTLE_NUTS',2,'each','M6x1DIN937AF10/h6/body3.5/slots2min.')
 add('BED_CAPTURE_OPEN_PIN_COTTERS',2,'each','DIN94/ISO1234splitpin1.6x14,formbothlegsafterlockingnut;replaceaftereverymodechange/removal.')
 add('BED_CAPTURE_INDEX_INTERFACE',2,'interface','8mmnormallyengagingindexpinIFselected;proposedindexrowisNOTaqualifiedfallarrest. Actualimpact-ratedcontrolorvalidatedsupportedtransitionremainsopen.','held-interface',role='held-not-purchase-ready')
 add('BED_REAR_END_CAP',2,'each','80x40x6.35steelrearendplate,2D8.5bores;clampedthroughfixedwebandmetalspacers.','plate-blank','steel',80,40,0,6.35)
 add('BED_REAR_CLOSED_BOLTS',2,'each','M8x35socketheadlowercorelock;20.4nominalengagement. Oneperside,removedbeforetilt;fronttwohinges/reartwolocksretainfourcorners.')
 add('BED_REAR_CLOSED_WASHERS',2,'each','16OD8.5IDx1.6steelwasher.')
 add('BED_REAR_CLOSED_SPACERS',2,'each','12.7OD8.5IDx3.475metalspacer;remove/storewithlowerlockbolts.','metal-spacer','Al_round_tube',3.475,12.7,8.5)
 add('BED_REAR_UPPER_CAP_BOLTS',2,'each','PermanentM8x20socketheadupperendcapbolt,12.05nominalcoreengagementwith1.6washer;stayswithmovingbed.')
 add('BED_REAR_UPPER_CAP_WASHERS',2,'each','M8flatwasher16OD8.5IDx1.6forpermanentupperendcapbolts.')
 path=OUT/'bed-takeoff.csv'
 with path.open('w',newline='',encoding='utf-8')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 reportpath=OUT/'bed-local-check.json';report=json.loads(reportpath.read_text(encoding='utf-8'))
 index={k:dict(v,category='fabricated-reference'if k.startswith(('BED_ASSIST','BED_HINGE_FIXED','BED_CAPTURE_ROOT'))else'finished-part')for k,v in report['custom_parts'].items()}
 pinproof=OUT/'stay-pivot-retention-check.json';retention=json.loads(pinproof.read_text(encoding='utf-8'))
 assert retention['passed']and retention['source_consistent']
 for n,h in retention['source_sha256'].items():assert sha(B.ROOT/n)==h,n
 drawings={r['file']:r for r in retention['exports']if r['file'].endswith('.dxf')}
 for n,r in drawings.items():assert sha(OUT/n)==r['sha256'],n
 for name,r in index.items():
  drawing=('STAY_PIVOT_PIN_DRAWING.dxf'if name.startswith('BED_STAY_PIVOT_PIN_')else
           'FRONT_HINGE_PIN_DRAWING.dxf'if name.startswith('BED_HINGE_PIN_')else
           'FULL_OPEN_LOCK_PIN_DRAWING.dxf'if name.startswith('BED_FULL_OPEN_POSITIVE_PIN_')else None)
  if drawing:r.update(drawing='output/'+drawing,drawing_sha256=drawings[drawing]['sha256'])
 profileproof=OUT/'profile-fastener-retention-check.json';profile=json.loads(profileproof.read_text(encoding='utf-8'))
 assert profile['passed']and profile['source_consistent']
 for n,h in profile['source_sha256'].items():assert sha(B.ROOT/n)==h,n
 profile_drawing=OUT/profile['export']['file'];assert sha(profile_drawing)==profile['export']['sha256']
 paths=[Path(__file__),Path(B.__file__),reportpath,pinproof,profileproof,profile_drawing,*[OUT/n for n in drawings]]
 result=dict(source_sha256={p.relative_to(B.ROOT).as_posix():sha(p)for p in paths},
   takeoff=dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),rows=len(rows)),parts=index,
   additional_manufacturing_drawings=[dict(id='BED_PROFILE_FASTENER_FINISHING',file=profile_drawing.relative_to(HERE).as_posix(),sha256=sha(profile_drawing),role='PURCHASED_SCREW_FINISHING_AND_BRIDGE_WASHER_INSTRUCTIONS')],
   ownership_credit_authority='Rootglobalnestonly;noautomatic83blankorwholebedstockcredit',pricing_performed=False,
   current_geometry_report_passed=report['passed'],fabrication_release=False)
 (OUT/'custom-part-index.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(rows=len(rows),customrefs=len(index),geometry_passed=report['passed'])),flush=True)
 return 0

if __name__=='__main__':
 code=run();sys.stdout.flush();sys.stderr.flush();os._exit(code)
