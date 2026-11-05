"""Source-bound millimetre drawing and dimensional checks for four stay pivots.

The outline is a turned profile, not a flat laser-cut part. Threads are called
out explicitly; the BRep uses major diameters rather than false helical teeth.
"""
from pathlib import Path
import hashlib,json,os,sys
import cadquery as cq
import ezdxf
import integrated_bed as B

HERE=Path(__file__).resolve().parent;OUT=HERE/'output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def additional_pin_drawing(name,shape,head_d,head_l,bearing_d,shoulder,length,thread,cross_d,cross_at,notes):
 """Side outline and transverse drill are explicit per turned part."""
 step=OUT/(name+'.step');cq.exporters.export(shape,str(step));back=cq.importers.importStep(str(step)).val()
 assert back.isValid()and len(back.Solids())==1 and abs(back.Volume()-shape.Volume())<.001
 assert abs(B.bounds(shape)[0])<1e-6 and abs(B.bounds(shape)[3]-length)<1e-6
 doc=ezdxf.new('R2010',units=ezdxf.units.MM);ms=doc.modelspace()
 for layer,color in(('TURNED_PROFILE',7),('CROSS_DRILL',1),('REFERENCE',8),('NOTES',7)):
  doc.layers.new(layer,dxfattribs={'color':color})
 td=float(thread.split('x')[0][1:])if thread else bearing_d;hd,bd=head_d/2,bearing_d/2
 outline=([(0,-hd),(head_l,-hd),(head_l,-bd),(shoulder,-bd),(shoulder,-td/2),(length,-td/2),(length,td/2),(shoulder,td/2),(shoulder,bd),(head_l,bd),(head_l,hd),(0,hd)]if thread else
          [(0,-hd),(head_l,-hd),(head_l,-bd),(length,-bd),(length,bd),(head_l,bd),(head_l,hd),(0,hd)])
 ms.add_lwpolyline(outline,close=True,dxfattribs={'layer':'TURNED_PROFILE'})
 ms.add_circle((cross_at,0),cross_d/2,dxfattribs={'layer':'CROSS_DRILL'})
 ms.add_line((-3,0),(length+3,0),dxfattribs={'layer':'REFERENCE'})
 texts=[f'{name} - QTY 2 - ALL DIMENSIONS mm',
  'TURNED C45 NORMALIZED OR QUALIFIED 4140; ALL SHARP EDGES DEBURRED',
  f'D{head_d:g} HEAD x {head_l:g}; D{bearing_d:g} SMOOTH LAND x {shoulder-head_l:g}'+(f'; {thread} END x {length-shoulder:g}'if thread else'; NO THREADS'),
  f'TOTAL {length:g}; D{cross_d:g} CROSS DRILL AT {cross_at:g} FROM OUTER HEAD FACE',
  f'D{bearing_d:g} BEARING LAND: NOMINAL -0.02/-0.05; HEAD -0.05/-0.10',
  'SMOOTH BEARING INTERFACES; RETAIN THE PIN WITHOUT AXIALLY CLAMPING THE MOVING JOINT',
  *notes,'LATHE PROFILE AND SIDE-VIEW CROSS DRILL'+('; THREAD HELIX IS A DRAWING CALLOUT'if thread else''),
  'NO FALL-ARREST/IMPACT RATING; VERIFY ACTUAL JOINT CAPACITY BEFORE OPERATION']
 for i,t in enumerate(texts):ms.add_text(t,dxfattribs={'height':1.7,'layer':'NOTES'}).set_placement((0,25-4*i if i<4 else-15-4*(i-4)))
 path=OUT/(name+'_DRAWING.dxf');doc.saveas(path);rd=ezdxf.readfile(path)
 assert not rd.audit().errors and rd.units==ezdxf.units.MM
 pp=list(rd.modelspace().query('LWPOLYLINE[layer=="TURNED_PROFILE"]'))
 assert len(pp)==1 and pp[0].closed and len(pp[0])==(12 if thread else 8)
 return[dict(file=step.name,sha256=sha(step),readback_passed=True),dict(file=path.name,sha256=sha(path),readback_passed=True)]

def run():
 proof=OUT/'bed-local-check.json';local=json.loads(proof.read_text(encoding='utf-8'))
 assert local['passed']and local['source_consistent_during_build']
 for n,h in local['source_sha256'].items():assert sha(B.ROOT/n)==h,n
 paths=[Path(__file__),Path(B.__file__),proof]
 start={p.relative_to(B.ROOT).as_posix():sha(p)for p in paths}
 first=B.stay_pivot_parts('UPPER',B.STAY_MOVING,'L',True)
 pin=first[0]['shape'];bb=B.bounds(pin)
 assert all(p['shape'].isValid()and len(p['shape'].Solids())==1 for p in first)
 L=B.STAY_PIN_END_X-B.STAY_PIN_HEAD_X;shoulder=B.STAY_PIN_SHOULDER_X-B.STAY_PIN_HEAD_X
 hole=B.STAY_PIN_COTTER_X-B.STAY_PIN_HEAD_X
 assert abs(L-30.85)<1e-9 and abs(shoulder-21.65)<1e-9 and abs(hole-27.85)<1e-9
 pinpath=OUT/'STAY_PIVOT_PIN.step'
 canonical=pin.translate((-B.STAY_PIN_HEAD_X,-B.STAY_MOVING[0],-B.STAY_MOVING[1]))
 cq.exporters.export(canonical,str(pinpath));back=cq.importers.importStep(str(pinpath)).val()
 assert back.isValid()and len(back.Solids())==1 and abs(back.Volume()-canonical.Volume())<.001
 doc=ezdxf.new('R2010',units=ezdxf.units.MM);ms=doc.modelspace()
 for layer,color in(('TURNED_PROFILE',7),('CROSS_DRILL',1),('REFERENCE',8),('NOTES',7)):
  doc.layers.new(layer,dxfattribs={'color':color})
 outline=[(0,-7),(2.5,-7),(2.5,-5),(shoulder,-5),(shoulder,-3),(L,-3),(L,3),(shoulder,3),(shoulder,5),(2.5,5),(2.5,7),(0,7)]
 ms.add_lwpolyline(outline,close=True,dxfattribs={'layer':'TURNED_PROFILE'})
 ms.add_circle((hole,0),.9,dxfattribs={'layer':'CROSS_DRILL'})
 ms.add_line((-3,0),(L+3,0),dxfattribs={'layer':'REFERENCE'})
 for d in(14,10,6):ms.add_circle((50,0),d/2,dxfattribs={'layer':'REFERENCE'})
 def note(text,y,x=0,height=1.7):ms.add_text(text,dxfattribs={'height':height,'layer':'NOTES'}).set_placement((x,y))
 note('STAY PIVOT PIN - QTY 4 IDENTICAL - ALL DIMENSIONS mm',24,height=2.1)
 note('TURNED C45 NORMALIZED OR QUALIFIED 4140; STEEL CERTIFICATE REQUIRED',20)
 note('D14 HEAD x 2.50 | D10 BEARING LAND x 19.15 | M6x1 END x 9.20',16)
 note('TOTAL LENGTH 30.85; D1.80 THROUGH CROSS DRILL AT X27.85 FROM HEAD FACE',12)
 note('D10 BEARING: 9.95..9.98; HEAD: 13.90..13.95; BREAK ALL SHARP EDGES',-13)
 note('HEAD THICKNESS 2.50 +/-0.02; HEAD-TO-SHOULDER 21.65 +/-0.03',-17)
 note('CLEVIS OUTER EAR: 5.00 STEEL, D10.20 THROUGH + D14.20 x 2.60 RECESS',-21)
 note('OUTER HEAD RECESSED 0.10 NOMINAL; THREADS OUTSIDE BOTH SHEAR PLANES',-25)
 note('RETAIN INBOARD: M6 DIN125 WASHER + M6 DIN937 NUT + DIN94 1.6x14 COTTER',-29)
 note('WASHER SEATS ON PIN SHOULDER; DO NOT CLAMP MOVING CLEVIS WITH NUT',-33)
 note('ALIGN NEXT SLOT <=60deg BACKOFF; VERIFY FINAL AXIAL FLOAT 0.15..0.50',-37)
 note('FORM BOTH COTTER TAILS WITHIN ASSEMBLY STEP ENVELOPE; NEW PIN AFTER REMOVAL',-41)
 note('AXIAL FIT IS A FINAL ASSEMBLY CHECK; NO IMPACT OR FALL-ARREST RATING',-45)
 note('OUTLINE IS LATHE PROFILE; D1.8 CIRCLE IS TRANSVERSE DRILL IN SIDE VIEW',-49)
 drawing=OUT/'STAY_PIVOT_PIN_DRAWING.dxf';doc.saveas(drawing)
 rd=ezdxf.readfile(drawing);audit=rd.audit()
 assert not audit.errors and rd.units==ezdxf.units.MM
 got=list(rd.modelspace().query('LWPOLYLINE[layer=="TURNED_PROFILE"]'))
 assert len(got)==1 and got[0].closed and len(got[0])==12
 assert len(list(rd.modelspace().query('CIRCLE[layer=="CROSS_DRILL"]')))==1
 hinge=B.hinge_pin_parts('L')[0]['shape'].mirror('YZ').translate((78.2,100,-B.TOP))
 extras=additional_pin_drawing('FRONT_HINGE_PIN',hinge,18,3,12,27.05,27.05,None,2.2,23.85,[
  'HEAD FACES INBOARD; RETAIN OUTSIDE: CUSTOM18OD12.2IDx1.6 WASHER + NEW DIN94 2x16',
  'REMOVE COTTER/WASHER THEN WITHDRAW26mm INBOARD; FRONT POST BLOCKS OUTBOARD SERVICE',
  'FIT AXIAL SHIMS: LEFT18OD12.2IDx1.85; RIGHT18OD12.2IDx1.35',
  'LEFT NOMINAL CHEEK GAP0.125; RIGHT0.625; FIT THE RECEIVED ASSEMBLY FOR THERMAL FLOAT'])
 n=cq.Vector(0,1,0);loc=cq.Location(cq.Plane(origin=(0,0,0),xDir=n,normal=n.cross(cq.Vector(1,0,0))))
 opened=B.full_open_pin_parts('L',(0,0,0),n.toTuple())[0]['shape'].moved(loc.inverse).translate((13.1,0,0))
 extras+=additional_pin_drawing('FULL_OPEN_LOCK_PIN',opened,16,3,10,23.3,32.5,'M6x1',1.8,29.5,[
  'RETAIN: M6 DIN12512OD x 1.6 + M6 DIN937 AF10/h6 + NEW DIN94 1.6x14 SPLIT PIN',
  'INSTALL ONLY AT90deg THROUGH BOTH WALLS OF BOTH TELESCOPIC STAY TUBES',
  'BOTH COTTER HEADS FACE OUTSIDE THE MACHINE; REPLACE SPLIT PINS AT EVERY REMOVAL'])
 hardware=[]
 for side in('L','R'):
  for tag,pt in(('LOWER',B.STAY_ROOT),('UPPER',B.STAY_MOVING)):
   parts=B.stay_pivot_parts(tag,pt,side,tag=='UPPER')
   canonical_parts=[B._mirror(p['shape'],side)for p in parts]
   total=cq.Compound.makeCompound(canonical_parts);bounds=B.bounds(total)
   hardware.append(dict(side=side,tag=tag,components=[p['id']for p in parts],valid=all(p['shape'].isValid()for p in parts),
    canonical_bounds_mm=bounds,outer_face_to_rail_end_gap_mm=bounds[0]-43.3,
    rail_gap_after_maximum_accepted_outboard_float_mm=bounds[0]-.5-43.3,
    inboard_pin_end_to_receiver_web_gap_mm=76.2-bounds[3],inboard_pin_end_to_modified_flange_window_gap_mm=76.0-bounds[3],head_recess_mm=B.STAY_PIN_HEAD_X-44.45))
 assert all(p['outer_face_to_rail_end_gap_mm']>=1.24 and p['inboard_pin_end_to_receiver_web_gap_mm']>=.79 for p in hardware)
 current=start=={p.relative_to(B.ROOT).as_posix():sha(p)for p in paths}
 report=dict(study='MODELED_EIGHT_BED_PIN_RETENTION_JOINTS',source_sha256=start,source_consistent=current,
  quantity=8,stay_pivot_quantity=4,front_hinge_quantity=2,full_open_lock_quantity=2,parts_per_stay_pivot=4,joints=hardware,outer_ear_thickness_mm=5,outer_ear_counterbore_mm=[14.2,2.6],remaining_ear_shaft_bearing_thickness_mm=2.4,
  pin=dict(overall_mm=L,head_diameter_mm=14,head_thickness_mm=2.5,smooth_bearing_diameter_mm=10,smooth_bearing_length_mm=19.15,
   thread='M6x1x9.2',crosshole_diameter_mm=1.8,crosshole_from_outer_head_face_mm=hole),
  axial_float_nominal_mm=.2,final_axial_float_acceptance_mm=[.15,.5],nut_alignment_backoff_max_deg=60,
  rail_float_bound_scope='A maximum0.5mmoutboardpinfloatleaves0.75mmfromthepinheadtotheX43.3railend. AxialtranslationandrotationaboutXcommute,sothisXseparationholdsforallbedangles. Thecounterborefloorsandinnerwashersphysicallystopinboard/outboardmotion;finalreceivedfloatandtherailendsmustbemeasured.',
  published_dimension_source=dict(manufacturer='Aspen Fasteners',url='https://www.aspenfasteners.com/content/pdf/Metric_DIN_937_spec.pdf',
   M6=dict(AF_mm=10,height_mm=6,full_body_mm=3.5,slot_min_mm=2,recommended_DIN94_cotter='1.6x14')),
  front_hinge_pin=B.metadata()['hinge_pin_retention'],full_open_pin=B.metadata()['full_open_pin_retention'],
  raw_pin_stock_nest=dict(raw_diameter_mm=19.05,raw_length_mm=304.8,primary_rough_blanks_mm=[33]*4+[35]*2+[40]*2,saw_kerfs=7,kerf_mm=3,used_length_mm=303,
    remainder_mm=1.8,finished_pin_length_each_mm=[30.85]*4+[32.5]*2+[27.05]*2,minimum_received_OD_mm=18.5,
    secondary_hinge_pack=dict(quantity=2,raw_length_each_mm=40,pin_rough_mm=28.5,washer_rough_mm=2.5,shim_rough_mm=3,internal_kerfs=2,kerf_mm=3,
     finished_pin_mm=27.05,finished_washer_mm=1.6,finished_shim_mm=[1.85,1.35],used_length_each_mm=40),
    meaning='One new3/4x12inch steel bar yields all8pins and4hingerings. The two40mmhingepacks each subcut into pin+retainingwasher+axialshim. Everykerf andfacingallowance isallocated; finishedparts/rawoptionarenonadditive. Noownedstockcredit.'),
  exports=[dict(file=pinpath.name,sha256=sha(pinpath),readback_passed=True),dict(file=drawing.name,sha256=sha(drawing),readback_passed=True),*extras],
  nominal_local_geometry_passed=local['passed'],passed=current,
  scope='All4staypivots,2front12mmhinges and2full-open10mmlockpins include actualpin/washer/slottednut/formedcottergeometry. Frontshimsaremodeled. Dedicatedpairwisechecksareinheritedfromcurrentlocalreport. Noexternalclipoccupiesthe1.15mmrailgap.',
  outstanding=['Actual steel/weld/eye/pin load capacity and impact qualification','Received nut/washer/cotter dimensions; assembled float and cotter forming within the checked envelope','Actual gas dimensions/force and controlled transition/handling'],
  fabrication_release=False,lift_operation_release=False)
 (OUT/'stay-pivot-retention-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=current,joints=8,stay_pivots=len(hardware),minimum_rail_gap_mm=min(x['outer_face_to_rail_end_gap_mm']for x in hardware),rail_gap_after_maximum_float_mm=min(x['rail_gap_after_maximum_accepted_outboard_float_mm']for x in hardware),minimum_inboard_gap_mm=min(x['inboard_pin_end_to_receiver_web_gap_mm']for x in hardware))),flush=True)
 return 0 if current else 1

if __name__=='__main__':
 try:code=run()
 except Exception:
  import traceback;traceback.print_exc();code=2
 sys.stdout.flush();sys.stderr.flush();os._exit(code)
