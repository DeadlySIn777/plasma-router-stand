"""Verify the final1/8in tab update against its frozen5mm reference.
Only this script and reports are written; atc.py/motion.py stay untouched.
"""
from pathlib import Path
import hashlib,json,math,types,sys,os
import atc,motion,params as P
from cad_helpers import bbox,intersection_volume
HERE=Path(__file__).resolve().parent
OLD_SHA='0ab5bc8755287a8100ad735a2139aa21d05855d855bd32fd9e8d6f8bb8998d2d'
NEW_SHA='3fd018d7817fbc7652f07f93e6dded23e7bc84c66c2994cf071a9bb50c70ed1a'

def run():
 names=('atc.py','motion.py','params.py','atc_tab_update_audit.py')
 start={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest()for n in names}
 p=HERE/'atc.py';data=p.read_bytes();newtext=p.read_text();nl='\r\n'
 oldtext=newtext.replace('7.675,21.75,3.175))','7.675,21.75,5))').replace('welded3.175mmtabtocurrentbackbartop;cantilever9.75mm','welded5mmtabtocurrentbackbartop;cantilever10mm')
 reconstructed=oldtext.replace('\n',nl).encode('utf-8')
 assert hashlib.sha256(reconstructed).hexdigest()==OLD_SHA,'Reference reconstruction differs from frozen baseline.'
 assert hashlib.sha256(newtext.replace('\n',nl).encode('utf-8')).hexdigest()==NEW_SHA,'Unexpected new geometry source.'
 reference=types.ModuleType('atc_before_final_tab');reference.__file__=str(p)
 exec(compile(oldtext,str(p),'exec'),reference.__dict__)
 before=reference._cached(200.,0.,False)[0];after=atc._cached(200.,0.,False)[0]
 old={q.id:q for q in before.parts};new={q.id:q for q in after.parts};assert set(old)==set(new)
 records=[];modified='ATC_MOTOR_WELDED_MOUNT'
 for n in sorted(set(old)-{modified}):
  a,b=old[n].shape,new[n].shape;va,vb=a.Volume(),b.Volume();v=intersection_volume(a,b)
  tol=max(1e-6,max(va,vb)*1e-9);raw=va+vb-2*v
  bb=max(abs(x-y)for x,y in zip(bbox(a),bbox(b)))
  records.append(dict(id=n,symmetric_difference_mm3=max(0.,raw),bbox_difference_mm=bb,
                      passed=abs(raw)<=tol and bb<1e-7 and a.isValid()and b.isValid()))
 a,b=old[modified].shape,new[modified].shape
 extra=b.cut(a).Volume();removed=a.cut(b)
 expected=atc.box(1039.975,1390,1069.675,7.675,21.75,1.825)
 delta=removed.Volume()+expected.Volume()-2*intersection_volume(removed,expected)
 bracket=motion._gantry_bracket(False,1275.)
 gap=bracket.distance(b)
 #Isolatedtab component: uniformsteelstrip,1kg assembly,50N radialbeltresultant,
 #0.4Nm motorreaction; rigid17.65mm offset beyond9.75mm free tab. Not a weld test.
 B,t,L,offset=7.675,3.175,9.75,17.65
 E=P.STEEL_E_MPA;nu=.3;G=E/(2*(1+nu));Fz=9.80665;Fy=50.;Tz=400.
 xoffset=1043.8125-1030.;zoffset=1079-(1066.5+t/2)
 Ix=B*t**3/12;Iz=t*B**3/12;A=B*t
 Mx=Fz*offset+Fy*zoffset;Mz=Tz+Fy*xoffset
 vtip=Fz*L**3/(3*E*Ix)+Mx*L**2/(2*E*Ix)
 slope=Fz*L**2/(2*E*Ix)+Mx*L/(E*Ix)
 vshaft=vtip+slope*offset
 xshaft=Mz*L**2/(2*E*Iz)+Mz*L/(E*Iz)*offset
 J=B*t**3/3*(1-.63*t/B+.052*(t/B)**5)
 Ty=Fz*xoffset;twist=Ty*L/(G*J)
 torsion_z=abs(twist*xoffset)
 bending=(Mx+Fz*L)*(t/2)/Ix+Mz*(B/2)/Iz+Fy/A
 shear_proxy=abs(Ty*t/J)+1.5*Fz/A
 vm_proxy=math.sqrt(bending*bending+3*shear_proxy*shear_proxy)
 screen=dict(scope='Isolatedtabcomponentlinearstaticproxy;notphysicalorweldqualification.',
   width_mm=B,raw_stock_thickness_mm=t,cantilever_mm=L,rigid_motor_centre_offset_mm=offset,
   assumed_mass_kg=1.,radial_belt_resultant_N=Fy,motor_reaction_about_Z_Nm=Tz/1000,
   assumed_E_MPa=E,assumed_poisson=nu,I_out_of_plane_mm4=Ix,I_in_plane_mm4=Iz,
   out_of_plane_motor_centre_deflection_mm=vshaft,torsion_motor_centre_deflection_proxy_mm=torsion_z,
   in_plane_motor_centre_deflection_mm=xshaft,
   combined_deflection_proxy_mm=math.hypot(vshaft+torsion_z,xshaft),
   bending_plus_axial_stress_bound_MPa=bending,combined_stress_proxy_MPa=vm_proxy,
   assumed_yield_reference_MPa=235.,yield_reference_to_stress_proxy_ratio=235/vm_proxy,
   weld_capacity_qualified=False,fatigue_qualified=False,
   fabrication='Use3.175mm plainsteelstock; weld/fit while retaining the modeled top envelope. Inspectfor distortion and verify>=2mm fulltravelphysicalclearance. Weldcapacitymustbequalifiedseparately.')
 passed=all(r['passed']for r in records)and extra<1e-7 and abs(delta)<1e-6 and abs(gap-2.625)<1e-7 and b.isValid()and len(b.Solids())==1
 end={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest()for n in names}
 passed=passed and start==end
 out=dict(passed=passed,source_consistent_during_check=start==end,reference_hash_line_endings='CRLF for bundled baseline comparison; actual native-file hashes recorded separately.',scope='Onlythemounttabmaterialremovalplusunchangedpartidentityandcomponentproxy.',
   old_source_sha256=OLD_SHA,new_source_sha256=NEW_SHA,
   source_sha256=end,
   unchanged_part_count=len(records),unchanged_parts=records,
   modified_part=modified,new_part_valid=b.isValid(),new_part_solid_count=len(b.Solids()),
   new_material_outside_old_mm3=extra,removed_volume_mm3=removed.Volume(),
   expected_removed_cuboid_mm=[1039.975,1390,1069.675,1047.65,1411.75,1071.5],
   removal_symmetric_difference_mm3=max(0.,delta),exact_nominal_minimum_gap_mm=gap,
   monotone_clearance_disposition='Theupdatedfixedmountisapuresubsetofthepreviousone;allother222physicalpartsaremateriallyidentical. Removingmaterialcannotintroduceageometriccollisionwiththisfixedmount. Theparentstillregeneratesaffectedreports/exports.',
   component_screen=screen,physical_rigidity_qualified=False,release=False)
 (HERE/'review'/'atc-tab-update-check.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in('passed','unchanged_part_count','new_material_outside_old_mm3','removed_volume_mm3','exact_nominal_minimum_gap_mm')}),flush=True)
 return 0 if passed else 1

if __name__=='__main__':
 try:code=run()
 except Exception:
  import traceback;traceback.print_exc();code=2
 sys.stdout.flush();sys.stderr.flush();os._exit(code)

