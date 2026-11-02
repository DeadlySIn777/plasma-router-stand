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
 add('BED_HDPE_FULL_LAYERS',2,'each','1000x1219.2x12.7fullrectangles;profiles0.4mmendoverhang.80roundholes only.','sheet','HDPE',1219.2,1000,0,12.7,covered='BED_HDPE_RAW_OPTION')
 add('BED_HDPE_RAW_OPTION',1,'sheet','48x96inx1/2 nominalHDPE canyieldtwo1000x1219.2pieces;~438.4mmremainingwidth strip.','raw-stock-option','HDPE',2438.4,1219.2,0,12.7,role='raw-option-not-add-on',covered='BED_HDPE_FULL_LAYERS')
 add('BED_CROSS_4080',4,'each','Flat4080crossmember,20D13.1verticalsleevebores;front/rearcores6.8pilot/M8tap22deep.','extrusion','4080',980,80,40)
 add('BED_COLUMNS',80,'each','12.7OD6.35IDAlcompressiontube;65.4nominalsquare-cut, fitactualtwo-sheetstack.','tube','Al_round_tube',65.4,12.7,6.35)
 add('BED_M5X70',80,'each','M5x70sockethead;head8.5x5,directsquarecolumnseat;2.7nutengagement+.6tipnominal.')
 add('BED_BOTTOM_SLOT_NUT_M5',80,'each','Compatible20100bottom-slotM5nut;recoveredCAD8x8x2.7envelope, selectedactualnutfitstillrequired.')
 add('BED_RECEIVER_ANGLE',2,'each','Formed/trimmedsteelangle54horizontalx31.75upwebx3.175, localassistwindow;16flushM5CSfixings toremainingmiddle/reararms.','angle','steel_angle',1050,54,31.75,3.175)
 add('BED_RECEIVER_PATCH',2,'each','120x35x3.175lowerreinforcementweb atassistnotch;newstock/noautomaticoffcutcredit.','plate-blank','steel',120,35,0,3.175)
 add('BED_RECEIVER_FIXING',16,'set','M5x10countersunk+actual40seriesM5Tnut;flushD10x2.75head. Grade,slotfitandprojectionqualified onreceiveddie.')
 add('BED_FIXED_HINGE_ASSEMBLIES',2,'assembly','SeeBED_HINGE_FIXED_L/RSTEP;welded3blankdecompositionbelow.','fabricated-reference',role='nonadditive-assembly-reference')
 add('BED_FIXED_HINGE_BASE_BLANK',2,'each','80x70x6.35steelplate,4D6.6postholes.','plate-blank','steel',80,70,0,6.35)
 add('BED_FIXED_HINGE_CHEEK_BLANK',2,'each','50x32.2x6.35steel,12.1pivotbore.','plate-blank','steel',50,32.2,0,6.35)
 add('BED_FIXED_HINGE_BRIDGE_BLANK',2,'each','25x50x6.35steelbridge;qualifiedweldloadpath.','plate-blank','steel',50,25,0,6.35)
 add('BED_FIXED_HINGE_FASTENERS',8,'set','M6postTnutattachment4perfrontpost atY−120/−80,Z967/1000;6.35plategrip,actualscrewlength/engagementbydie.')
 add('BED_HINGE_MOVING_SIDEPLATE_L',1,'each','270x120x9.525ALarm;12.1pivotbore and2D14.2x4.6counterbores/D8.5through.','plate-blank','aluminum',270,120,0,9.525,owned='owned3/8sheet-global-unique-allocation-required',notes='Reserveperrootmanufacturingnest;notanadditionalnewpurchaseifuniquelyallocated.')
 add('BED_HINGE_MOVING_SIDEPLATE_R',1,'each','Mirrorofleft270x120x9.525arm.','plate-blank','aluminum',270,120,0,9.525,owned='owned3/8sheet-global-unique-allocation-required')
 add('BED_HINGE_SPACERS',2,'each','80x40x10newAlspacer,2D8.5bores.9.525sheetdoesnotprovide10mm.','plate-blank','aluminum',80,40,0,10)
 add('BED_HINGE_BUTTON_FASTENERS',4,'each','M8x35ISO7380buttonhead14OD4.4high;counterbored4.6;20.075endcoreengagementnominal.')
 add('BED_HINGE_PINS',2,'each','12mmgroundretainedsteelpin;24.2runninglength plus18x3head. Appropriatebushing/pinfitandaxialleftdatum/rightthermalfloatacceptance.')
 add('BED_ASSIST_C_ASSEMBLIES',2,'assembly','Gas/stayendbracketSTEP, weldedconstituentsbelow.','fabricated-reference',role='nonadditive-assembly-reference')
 add('BED_ASSIST_END_WEB_BLANK',2,'each','60x30x6.35steelweb,2D8.5corefixings.','plate-blank','steel',60,30,0,6.35)
 add('BED_ASSIST_UPPER_BLANK',2,'each','60x34.2x6.35steelupperbridgewithbodyclearanceUcut;actualSTEPoutlinecontrols.','plate-blank','steel',60,34.2,0,6.35)
 add('BED_ASSIST_GAS_EAR_BLANK',2,'each','40x20x3.175steel,8.5studbore.','plate-blank','steel',40,20,0,3.175)
 add('BED_ASSIST_CAPTURE_EAR_BLANK',4,'each','Planarring+rearstrapfits32.4x65.65x3.175;exactSTEPoutlinecontrols.','plate-blank','steel',65.65,32.4,0,3.175)
 add('BED_ASSIST_END_FIXINGS',4,'each','M8x25endcorefixings;6.35grip18.65engagementnominal.')
 add('BED_GAS_PAIR',1,'pair','ARANA28IN200LBST280M200ASINB08CNGT5Z7;889Neachconditionalon200lblabel. Exactcompressedunpublished:verify≤450mm/expanded≥700mm, body≤24/rod≤10/socketfit. Noassumedliftingrating.')
 add('BED_GAS_INCLUDED_BALLS',4,'each','10mmballstudslistedasincludedwithgaspackage;verifythread/neck/quantity.','included-package-reference',owned='new-with-gas-pair',role='nonadditive-package-reference',covered='BED_GAS_PAIR')
 add('BED_GAS_UPPER_STUD_SPACER',2,'each','Nominal3.95mmspacer,OD12.7ID8.5;fit16.05mmface-to-ballcentrefromactualstudneck.','metal-spacer','Al_round_tube',3.95,12.7,8.5)
 add('BED_GAS_ROOT_PLATE',2,'each','80x80x6.35steelplate4M6holes,M8studhole;on14.9standoffs.','plate-blank','steel',80,80,0,6.35)
 add('BED_GAS_ROOT_SPACER',8,'each','12.7OD6.35ID14.9Alstandoff,canusecolumn-tubepackremainderifexactnestallocated.','tube','Al_round_tube',14.9,12.7,6.35)
 add('BED_CAPTURE_ROOT_ASSEMBLIES',2,'assembly','120x80backplatewithclevisfloor/earsandgascolumn/studclearancebores;seeSTEP.','fabricated-reference',role='nonadditive-assembly-reference')
 add('BED_CAPTURE_ROOT_BASE',2,'each','120x80x6.35steelpostplate,4M6fixings,4D13.1gascolclearanceandD8.5gasstudclearance.','plate-blank','steel',120,80,0,6.35)
 add('BED_CAPTURE_ROOT_FLOOR',2,'each','40x33.85x6.35steelfloor.','plate-blank','steel',40,33.85,0,6.35)
 add('BED_CAPTURE_ROOT_EARS',4,'each','24x32x3.175steelring+stem,10.2pivotbore.','plate-blank','steel',32,24,0,3.175)
 add('BED_ASSIST_ROOT_FASTENERS',16,'set','4M6postTnutjointspergas/captureanchor;gasmount21.25metalstack,capture6.35;selectscrew/engagementactualdie.')
 add('BED_CAPTURE_OUTER',2,'each','20x20x2steelRHS390mm;12mmeyestandoff,10.2fullopenpinbore.','tube','steel_square_tube',390,20,20,2)
 add('BED_CAPTURE_INNER',2,'each','15x15x1.5steelRHS375mm;8.5indexrowand10.2fullopenbore,exactpositioninmodel.','tube','steel_square_tube',375,15,15,1.5)
 add('BED_CAPTURE_END_EYES',4,'each','24OD10.2IDx6.35steelweldedeye;qualifiedtube/eyeweldtransitionrequired.','machined-ring','steel',6.35,24,10.2)
 add('BED_CAPTURE_PIVOT_PINS',4,'set','10mmretainedsteelpinwithfittedmetalspacers/clevisretention. Fulljointwidth,heads/clipclearancearefitacceptance.')
 add('BED_CAPTURE_OPEN_PINS',2,'each','10mmx40retainedsteelthroughpin at90deg, passesbothwallsofbothtubes. Noadropimpactratinginferred.')
 add('BED_CAPTURE_INDEX_INTERFACE',2,'interface','8mmnormallyengagingindexpinIFselected;proposedindexrowisNOTaqualifiedfallarrest. Actualimpact-ratedcontrolorvalidatedsupportedtransitionremainsopen.','held-interface',role='held-not-purchase-ready')
 add('BED_REAR_END_CAP',2,'each','80x40x6.35steelrearendplate,2D8.5bores;clampedthroughfixedwebandmetalspacers.','plate-blank','steel',80,40,0,6.35)
 add('BED_REAR_CLOSED_BOLTS',4,'each','M8x35sockethead;20.4nominalrearcoreengagement. Removedbeforetilt.')
 add('BED_REAR_CLOSED_WASHERS',4,'each','16OD8.5IDx1.6steelwasher.')
 add('BED_REAR_CLOSED_SPACERS',4,'each','12.7OD8.5IDx3.475metalspacer;remove/storewithboltsorfitcaptivemethod.','metal-spacer','Al_round_tube',3.475,12.7,8.5)
 path=OUT/'bed-takeoff.csv'
 with path.open('w',newline='',encoding='utf-8')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 reportpath=OUT/'bed-local-check.json';report=json.loads(reportpath.read_text(encoding='utf-8'))
 index={k:dict(v,category='fabricated-reference'if k.startswith(('BED_ASSIST','BED_HINGE_FIXED','BED_CAPTURE_ROOT'))else'finished-part')for k,v in report['custom_parts'].items()}
 result=dict(source_sha256={p.relative_to(B.ROOT).as_posix():sha(p)for p in[Path(__file__),Path(B.__file__),reportpath]},
   takeoff=dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),rows=len(rows)),parts=index,
   ownership_credit_authority='Rootglobalnestonly;noautomatic83blankorwholebedstockcredit',pricing_performed=False,
   current_geometry_report_passed=report['passed'],fabrication_release=False)
 (OUT/'custom-part-index.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(rows=len(rows),customrefs=len(index),geometry_passed=report['passed'])),flush=True)
 return 0

if __name__=='__main__':
 code=run();sys.stdout.flush();sys.stderr.flush();os._exit(code)
