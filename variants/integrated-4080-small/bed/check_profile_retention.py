"""Verify the repaired profile/column/crossbar capture and fastener finishing.

The80 bridging washers close a real missing metal retention path. Nominal
contact geometry is proved; washer bending, actual die/nut capacity and torque
still require physical material/interface qualification.
"""
from pathlib import Path
import hashlib,json,math,os,sys
import cadquery as cq
import ezdxf
import integrated_bed as B

HERE=Path(__file__).resolve().parent;OUT=HERE/'output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
 localpath=OUT/'bed-local-check.json';local=json.loads(localpath.read_text(encoding='utf-8'))
 assert local['passed']and local['source_consistent_during_build']
 for n,h in local['source_sha256'].items():assert sha(B.ROOT/n)==h,n
 paths=[Path(__file__),Path(B.__file__),localpath]
 start={p.relative_to(B.ROOT).as_posix():sha(p)for p in paths}
 parts={p['id']:p for p in B.bed_parts(0)};records=[]
 bottom=B.CROSS_BOTTOM+B.ASSEMBLY_Z_SHIFT
 profile_bottom=B.PROFILE_BOTTOM+B.ASSEMBLY_Z_SHIFT
 ring_area=math.pi*(18**2-13.1**2)/4
 for k,(cy,x)in enumerate(B.anchor_rows(),1):
  washer=parts[f'BED_CROSS_BRIDGE_WASHER_{k:02}']['shape']
  screw=parts[f'BED_M5x72_FINISHED_{k:02}']['shape']
  column=parts[f'BED_COLUMN_{k:02}']['shape']
  nut=parts[f'BED_M5_BOTTOM_NUT_{k:02}']['shape']
  cross=parts[f'BED_4080_CROSS_{B.CROSS_CENTRES.index(cy)+1}']['shape']
  wb,sb,cb,nb=map(B.bounds,(washer,screw,column,nut))
  assert abs(wb[5]-bottom)<1e-6 and abs(cb[2]-bottom)<1e-6
  assert abs(wb[2]-(bottom-1.6))<1e-6 and abs((sb[5]-wb[2])-72)<1e-6
  # This0.1mmprobe is wholly on the nominal bottom metal surface outside
  # the13.1bore. Its overlap/height gives the actual modeled bearing area.
  probe=B.ring(18,13.1,.1,(x,cy,bottom))
  area=abs(probe.intersect(cross).Volume())/.1
  assert abs(area-ring_area)<.01,(k,area,ring_area)
  full_thread_tip=sb[5]-.4
  engagement=min(nb[5],full_thread_tip)-max(nb[2],wb[2])
  assert abs(engagement-2.7)<1e-5
  tip=sb[5]-nb[5];ceiling=profile_bottom+6.1-sb[5]
  assert abs(tip-1)<1e-5 and abs(ceiling-1.1)<1e-5
  records.append(dict(station=k,X_mm=x,Y_mm=cy,nominal_crossbar_bearing_area_mm2=area,
   full_nominal_nut_engagement_mm=engagement,nominal_tip_beyond_nut_mm=tip,
   nominal_tip_to_slot_ceiling_mm=ceiling,column_unchanged_length_mm=cb[5]-cb[2],
   nominal_washer_underside_Z_mm=wb[2],nominal_head_bottom_Z_mm=sb[2],passed=True))
 assert len(records)==80
 # Nominal DIN9021 thickness range and finished screw tolerance. The fixed
 # profile/nut/cavity values remain source assumptions, not another supplier.
 tolerance=[]
 for length in(71.9,72.1):
  for thickness in(1.4,1.8):
   relative_tip=length-65.4-thickness
   tolerance.append(dict(finished_underhead_length_mm=length,washer_thickness_mm=thickness,
    full_thread_after_nominal_nut_mm=relative_tip-.4-4.,tip_to_nominal_cavity_ceiling_mm=6.1-relative_tip,
    passed=relative_tip-.4>=4 and relative_tip<6.1))
 assert all(q['passed']for q in tolerance)
 doc=ezdxf.new('R2010',units=ezdxf.units.MM);ms=doc.modelspace()
 for layer,color in(('FINISHED_SCREW_PROFILE',7),('REFERENCE',8),('NOTES',7)):
  doc.layers.new(layer,dxfattribs={'color':color})
 ms.add_lwpolyline([(-5,-4.25),(0,-4.25),(0,-2.5),(72,-2.5),(72,2.5),(0,2.5),(0,4.25),(-5,4.25)],close=True,dxfattribs={'layer':'FINISHED_SCREW_PROFILE'})
 ms.add_lwpolyline([(72,-2.5),(75,-2.5),(75,2.5),(72,2.5)],close=True,dxfattribs={'layer':'REFERENCE'})
 for xx in(68.3,71.,73.1):ms.add_line((xx,-5),(xx,5),dxfattribs={'layer':'REFERENCE'})
 notes=['M5 PROFILE FASTENERS - QTY80 - ALL mm',
  'BUY M5x75 SOCKET-HEAD STEEL SCREWS; FINISH72.0 +/-0.1 UNDER THE HEAD',
  'REMOVE3.0mm FROM THE TIP; DEBURR/END CHAMFER <=0.4; PRESERVE UNDAMAGED THREAD',
  'USE ONE STEEL M6 DIN9021 LARGE WASHER18OD/6.4IDx1.6 AT EACH STATION',
  'WASHER SEATS THE CROSSBAR UNDERSIDE AND THE SQUARE COLUMN END TOGETHER',
  '65.4mm COLUMNS/D13.1 CROSSBAR BORES/ALL BED DATUMS ARE UNCHANGED',
  'NOMINAL NUT SPAN68.3..71.0 FROM UNDERHEAD;72mm TIP;73.1 CAVITY CEILING',
  'UNCUT75mm SCREW WOULD EXCEED NOMINAL CAVITY CEILING BY1.9mm: DO NOT INSTALL',
  'RECEIVER ACCESS HOLES22mm CLEAR THE18mm WASHERS; DRY-ARM HEAD ACCESS STAYS12.5',
  'FIT COLUMN ENDS/ACTUAL SHEET STACK SO WASHER BEARS BOTH BAR AND COLUMN',
  'VERIFY RECEIVED WASHER DIMENSIONS, ACTUAL PROFILE/NUT FIT AND QUALIFIED PRELOAD']
 for i,t in enumerate(notes):ms.add_text(t,dxfattribs={'height':1.7,'layer':'NOTES'}).set_placement((-5,20-4*i if i<3 else-14-4*(i-3)))
 drawing=OUT/'BED_PROFILE_FASTENER_FINISHING.dxf';doc.saveas(drawing);back=ezdxf.readfile(drawing)
 assert not back.audit().errors and back.units==ezdxf.units.MM
 assert len(list(back.modelspace().query('LWPOLYLINE[layer=="FINISHED_SCREW_PROFILE"]')))==1
 consistent=start=={p.relative_to(B.ROOT).as_posix():sha(p)for p in paths}
 report=dict(study='POSITIVE_20100_COLUMN_CROSSBAR_RETENTION',source_sha256=start,source_consistent=consistent,
  quantity=80,washer=dict(OD_mm=18,ID_mm=6.4,thickness_mm=1.6,standard='M6DIN9021/ISO7093,steel',
   dimension_source='https://www.aspenfasteners.com/content/pdf/Metric_DIN_9021_spec.pdf',
   nominal_radial_bridge_beyond_crossbar_bore_mm=2.45,min_radial_bridge_at_OD17p57_bore13p2_mm=2.185),
  old_retention_failure=dict(crossbar_bore_mm=13.1,column_OD_mm=12.7,head_OD_mm=8.5,
    both_column_and_head_passed_through_bar_bore=True,repair='Largewashernowbridgesbarboreandcapturesthecrossbartogetherwiththecolumn/profile.'),
  screw=dict(stock_underhead_length_mm=75,finished_underhead_length_mm=72,tolerance_mm=.1,tip_chamfer_max_mm=.4,
   nominal_head_OD_mm=8.5,head_height_mm=5,uncut75_tip_beyond_nominal_cavity_ceiling_mm=1.9),
  bearing_area_mm2=dict(minimum_modeled_crossbar_surface=min(q['nominal_crossbar_bearing_area_mm2']for q in records),
   column_to_washer=math.pi*(12.7**2-6.4**2)/4,head_to_washer=math.pi*(8.5**2-6.4**2)/4),
  metal_seat_scope='All80nominalwasherupperfacescoincidewithcrossbarundersidesandcolumnbottoms. Theactualnominalbarbearingpatchoutsideeachborewasintersectedandmeasured. NoHDPEpreloadorstiffnesscredit.',
  receiver_washer_access_holes_mm=22,dry_arm_head_access_holes_mm=12.5,stations=records,tolerance_cases=tolerance,
  local_bed_report_passed=local['passed'],all_eight_pin_retention_unchanged=True,
  export=dict(file=drawing.name,sha256=sha(drawing),readback_passed=True),passed=consistent,
  remaining_qualification='Actualreceivedprofiledie/nutlip/material/washerflatness/thickness,preload,washerbendingandjointslipcapacityrequirequalification. FitactualcolumnlengthtoreceivedHDPEstack;ensurebothmetalseatscontact.',
  fabrication_release=False,operating_release=False)
 (OUT/'profile-fastener-retention-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=consistent,stations=80,minimum_bearing_area_mm2=report['bearing_area_mm2']['minimum_modeled_crossbar_surface'],minimum_tolerance_cavity_clearance_mm=min(x['tip_to_nominal_cavity_ceiling_mm']for x in tolerance))),flush=True)
 return 0 if consistent else 1

if __name__=='__main__':
 try:code=run()
 except Exception:
  import traceback;traceback.print_exc();code=2
 sys.stdout.flush();sys.stderr.flush();os._exit(code)
