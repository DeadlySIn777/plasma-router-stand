"""Source-bound installed wet assembly and welded overflow fabrication references.

The upper collector is three butt-welded flat strips, with no bend allowance.
The lower gutter, deflector and two unchanged formed brackets are counted once.
All coordinates and exported drawing units are millimetres.
"""
from pathlib import Path
import hashlib,json,math,os,sys
import cadquery as cq
import ezdxf
import integrated_utilities as U

HERE=Path(__file__).resolve().parent
OUT=HERE/'output'; PARTS=OUT/'lowered-wet-step'; DRAW=OUT/'lowered-wet-drawings'
ROOT=U.ROOT
SUPERSEDED=[
 'OVERFLOW_COLLECTOR_BACK','OVERFLOW_COLLECTOR_SIDES','OVERFLOW_COLLECTOR_FLOOR',
 'OVERFLOW_GUTTER_FLOOR','OVERFLOW_GUTTER_SIDES','OVERFLOW_DEFLECTOR',
 'OVERFLOW_SUPPORT_BRACKET_FLAT',
]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def symmetric_difference(a,b):return a.cut(b).Volume()+b.cut(a).Volume()
def polygon(points,z=0):
 return cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(x,y,z)for x,y in points]+[cq.Vector(*points[0],z)]))
def rectangle(w,h):return polygon([(0,0),(w,0),(w,h),(0,h)])
def drilled_rectangle(w,h,holes):
 s=U.box(0,0,0,w,h,1)
 for x,y,r in holes:s=s.cut(U.cyl(r,1.2,(x,y,-.1)))
 f=max((f for f in s.Faces()if f.normalAt().z>.99),key=lambda f:f.Area())
 return f.translate((0,0,-1))

def decomposition():
 """Independent piece decomposition, proved against the actual U compound."""
 h=U.O.P.PAN_RIM-U.PAN_DROP-465.
 assert abs(h-383.)<1e-8,('Update finished strips for changed collector height',h)
 p=[('U_OVERFLOW_COLLECTOR_BACK_CURRENT',U.box(1074.1,878,465,1.9,44,h)),
    ('U_OVERFLOW_COLLECTOR_SIDE_A_CURRENT',U.box(1056,878,465,18.1,1.9,h)),
    ('U_OVERFLOW_COLLECTOR_SIDE_B_CURRENT',U.box(1056,920.1,465,18.1,1.9,h))]
 pts=[cq.Vector(900,878,462),cq.Vector(1076,878,465),
      cq.Vector(1076,878,466.9),cq.Vector(900,878,463.9)]
 floor=cq.Solid.extrudeLinear(cq.Wire.makePolygon(pts+[pts[0]]),[],cq.Vector(0,44,0))
 p.append(('U_OVERFLOW_GUTTER_FLOOR_CURRENT',floor))
 p.append(('U_OVERFLOW_DEFLECTOR_CURRENT',U.box(898.1,878,410,1.9,44,53.9)))
 for tag,y in(('A',878.),('B',920.1)):
  pts=[cq.Vector(900,y,462),cq.Vector(1076,y,465),cq.Vector(1076,y,477),cq.Vector(900,y,474)]
  p.append(('U_OVERFLOW_GUTTER_SIDE_'+tag+'_CURRENT',
    cq.Solid.extrudeLinear(cq.Wire.makePolygon(pts+[pts[0]]),[],cq.Vector(0,1.9,0))))
 for y in(866.,922.):
  p.append((f'U_OVERFLOW_SUPPORT_BRACKET_{int(y)}_CURRENT',U.O.overflow_bent_bracket(y).translate((0,0,-U.PAN_DROP))))
 return p

def takeoff_rows():
 """Complete current overflow stock; legacy rows in SUPERSEDED are excluded."""
 vals=[
 ('U_OVERFLOW_COLLECTOR_BACK_STOCK',1,'44x383x1.9mm plain steel flat strip; upper C-channel back; butt weld, no bends.'),
 ('U_OVERFLOW_COLLECTOR_SIDE_STOCK',2,'18.1x383x1.9mm plain steel flat strips; upper C-channel sides; butt weld, no bends.'),
 ('U_OVERFLOW_GUTTER_FLOOR_STOCK',1,'176.1x44x1.9mm plain steel rough blank; finish sloped gutter to current STEP. Installed rise3 over176; end bevel0.976543deg; nominal normal thickness1.899724mm. Replaces undersize legacy40.2mm-width floor blank.'),
 ('U_OVERFLOW_GUTTER_SIDE_STOCK',2,'176x15x1.9mm plain steel blank; finish polygon(0,0),(176,3),(176,15),(0,12); weld both cheeks.'),
 ('U_OVERFLOW_DEFLECTOR_STOCK',1,'53.9x44x1.9mm plain steel flat; exit deflector to Z410; no bends.'),
 ('U_OVERFLOW_SUPPORT_BRACKET_STOCK',2,'Unchanged formed1.9mm steel bracket: outer legs53/20, width12, inside radius2; D4.4 hole; use unchanged calibrated-development reference and current STEP installed26mm lower. Actual K-factor/forming coupon qualification held.'),
 ]
 return [dict(id=i,quantity=q,unit='pieces',specification=s,ownership='new',procure=True)for i,q,s in vals]

def guide_stock_rows():
 h=656.5-U.PAN_DROP
 vals=[
 ('U_GUIDE_CLIP_MOUNT_FLAT_STOCK',6,'60x30x1.9mm plain steel; two D6.6 through holes atlocal(10,20),(50,20); weld to offset foot.'),
 ('U_GUIDE_CLIP_OFFSET_FLAT_STOCK',6,'47.3x60x1.9mm plain steel offset-foot flats; welded, no bends.'),
 ('U_GUIDE_CLIP_SCREEN_FLAT_STOCK',6,'60x32.85x1.9mm plain steel upright flats; weld between offset foot and screen edge; no bends.'),
 ('U_GUIDE_RACK_WEB_FLAT_STOCK',2,f'160x{h:g}x1.9mm plain steel rack webs; six D6.6 holes from current mm DXF.'),
 ('U_GUIDE_RACK_RETURN_FLAT_STOCK',4,f'18.1x{h:g}x1.9mm plain steel edge-return flats; weld to web; no bends.'),
 ('U_GUIDE_RACK_ANCHOR_FLAT_STOCK',2,'40x40x1.9mm plain steel anchor flats; two D6.6 holes atlocal(12.3,20),(32.3,20); weld, no bends.'),
 ('U_GUIDE_RACK_LEDGE_FLAT_STOCK',6,'72.3x40x1.9mm plain steel storage ledges; weld to rack web; no bends.'),
 ]
 return [dict(id=i,quantity=q,unit='pieces',specification=s,ownership='new',procure=True)for i,q,s in vals]

def export_all():
 for d in(OUT,PARTS,DRAW):d.mkdir(exist_ok=True)
 pieces=decomposition(); upper=U.O.fuse([s for n,s in pieces[:3]])
 h=U.O.P.PAN_RIM-U.PAN_DROP-465.
 target=U.box(1056,878,465,20,44,h).cut(U.box(1055.9,879.9,464.9,18.2,40.2,U.O.P.PAN_RIM-U.PAN_DROP-464.8))
 upper_error=symmetric_difference(upper,target)
 rebuilt=U.O.fuse([s for n,s in pieces]);actual=U.lowered_overflow_return()
 full_error=symmetric_difference(rebuilt,actual)
 assert upper_error<1e-5 and full_error<1e-4,(upper_error,full_error)
 parts=[];drawings=[];flat_checks=[]
 def step(n,s,notes=''):
  f=PARTS/(n+'.step');cq.exporters.export(s,str(f));back=cq.importers.importStep(str(f)).val()
  error=symmetric_difference(s,back)
  assert back.isValid()and error<.01,(n,error)
  r=dict(id=n,file=f.relative_to(HERE).as_posix(),sha256=sha(f),bounds_mm=U.bb(s),roundtrip_symmetric_difference_mm3=error,notes=notes)
  parts.append(r);return r
 def flat(n,face,t,q,role='CURRENT_WELDED_STEEL_FLAT_CUT_PROFILE',notes=''):
  f=DRAW/(n+'.dxf');cq.exporters.exportDXF(face,str(f),doc_units=4)
  doc=ezdxf.readfile(f);assert doc.units==4 and not doc.audit().has_errors
  rebuilt=cq.importers.importDXF(str(f)).wires().toPending().extrude(t).val()
  volume_error=abs(rebuilt.Volume()-face.Area()*t)
  assert rebuilt.isValid()and volume_error<.01,(n,volume_error)
  b=face.BoundingBox();flat_checks.append(dict(id=n,quantity=q,length_mm=b.xlen,width_mm=b.ylen,thickness_mm=t,units='mm',roundtrip_volume_error_mm3=volume_error,notes=notes))
  drawings.append(dict(id=n,file=f.relative_to(HERE).as_posix(),sha256=sha(f),role=role,notes=notes))
 for n,s in pieces:step(n,s,'Installed pose; stock is listed once in current utility takeoff, not an additional purchase.')
 step('OVERFLOW_WELDED_OPEN_RETURN_AIRGAP19',actual,'Current complete overflow, with383mm open upper channel and lower gutter/deflector unchanged in height.')
 flat('U_OVERFLOW_COLLECTOR_BACK_44x383',rectangle(44,h),1.9,1,notes='Back strip; world X1074.1..1076,Y878..922,Z465..848. Butt-weld sides; no upper-channel floor cap.')
 flat('U_OVERFLOW_COLLECTOR_SIDES_18p1x383',rectangle(18.1,h),1.9,2,notes='Two side strips; world X1056..1074.1; Y878..879.9 and920.1..922. No bends.')
 flat('U_OVERFLOW_GUTTER_FLOOR_ROUGH_BLANK_176p1x44',rectangle(176.1,44),1.9,1,
      role='ROUGH_FLAT_BLANK_FINISH_TO_CURRENT_STEP',notes='Rough blank only. Finish0.976543deg end bevel/installed slope to current STEP; no bend allowance. Source floor has1.9mm vertical rather than normal thickness.')
 flat('U_OVERFLOW_GUTTER_SIDE_POLYGON',polygon([(0,0),(176,3),(176,15),(0,12)]),1.9,2,notes='Two flat cheeks, coordinates in local world-X/world-Z plane. No bends.')
 flat('U_OVERFLOW_DEFLECTOR_53p9x44',rectangle(53.9,44),1.9,1,notes='One flat exit deflector; installed Z410..463.9. No bends.')
 # Screens, cantilever clips and storage racks are welded flat plates, not
 # bent developments. Prove the full manufactured union for both sides.
 guide_checks=[]
 for side in('L','R'):
  for i,(lo,hi,cy)in enumerate(U.GUIDE_SECTIONS):
   mount=U.box(25.8,cy-30,1013,1.9,60,30)
   for yy in(cy-20,cy+20):mount=mount.cut(U.cyl(3.3,3.9,(24.8,yy,1033),(1,0,0)))
   pp=[U.box(75,lo,1013,1.9,hi-lo,94.3),mount,
       U.box(27.7,cy-30,1013,47.3,60,1.9),U.box(73.1,cy-30,1014.9,1.9,60,32.85)]
   error=symmetric_difference(U.mirror(U.O.fuse(pp),side),U.guide_screen(side,i))
   assert error<1e-5,(side,i,error)
   guide_checks.append(dict(id=f'U_GUIDE_REMOVABLE_SCREEN_{side}_{i+1}',flat_plate_count=4,union_error_mm3=error))
 rack_h=656.5-U.PAN_DROP;web_holes=[]
 web=U.box(125.8,200,70,1.9,160,rack_h)
 for i,(lo,hi,cy)in enumerate(U.GUIDE_SECTIONS):
  level=(80.,280.,480.)[i]
  for yy in(336+cy-(lo+hi)/2-20,336+cy-(lo+hi)/2+20):
   web=web.cut(U.cyl(3.3,3.9,(124.8,yy,level+20),(1,0,0)))
   web_holes.append((yy-200,level+20-70,3.3))
 anchor=U.box(127.7,280,724.6-U.PAN_DROP,40,40,1.9)
 for xx in(140.,160.):anchor=anchor.cut(U.cyl(3.3,3.9,(xx,300,723.6-U.PAN_DROP)))
 rack_pieces=[web,U.box(127.7,200,70,18.1,1.9,rack_h),U.box(127.7,358.1,70,18.1,1.9,rack_h),anchor]
 rack_pieces +=[U.box(127.7,280,z-1.9,72.3,40,1.9)for z in(80.,280.,480.)]
 rack_actual={n:s for n,s,c in U.guide_rack_parts()}
 for side in('L','R'):
  n='U_GUIDE_FIXED_UNDER_PAN_RACK_'+side
  error=symmetric_difference(U.mirror(U.O.fuse(rack_pieces),side),rack_actual[n])
  assert error<1e-5,(n,error)
  guide_checks.append(dict(id=n,flat_plate_count=7,union_error_mm3=error))
 flat('U_GUIDE_SCREEN_PANEL_472x94p3',rectangle(472,94.3),1.9,6,notes='Screen plate only; three clip plates are separately scheduled. No bends.')
 flat('U_GUIDE_CLIP_MOUNT_60x30_D6p6',drilled_rectangle(60,30,[(10,20,3.3),(50,20,3.3)]),1.9,6,notes='Clip mount face; local horizontal=world Y, vertical=world Z. Two D6.6 through holes.')
 flat('U_GUIDE_CLIP_OFFSET_47p3x60',rectangle(47.3,60),1.9,6,notes='Offset foot; weld to mount plate and upright. No bends.')
 flat('U_GUIDE_CLIP_UPRIGHT_60x32p85',rectangle(60,32.85),1.9,6,notes='Screen upright; weld to offset foot and panel. No bends.')
 flat('U_GUIDE_RACK_WEB_160x630p5_D6p6',drilled_rectangle(160,rack_h,web_holes),1.9,2,notes='Rack web; local horizontal=world Y-200, vertical=world Z-70; six D6.6 holes. Twelve welded nuts are separate hardware.')
 flat('U_GUIDE_RACK_RETURN_18p1x630p5',rectangle(18.1,rack_h),1.9,4,notes='Two edge-return flats per rack, welded. No bends.')
 flat('U_GUIDE_RACK_ANCHOR_40x40_D6p6',drilled_rectangle(40,40,[(12.3,20,3.3),(32.3,20,3.3)]),1.9,2,notes='Anchor flange; local X=world X-127.7 and local Y=world Y-280 on left; mirror right. No bends.')
 flat('U_GUIDE_RACK_LEDGE_72p3x40',rectangle(72.3,40),1.9,6,notes='Three ledges per rack; install topZ80/280/480. Welded, no bends.')
 # The small end bevel is a machining operation, not an invented bend allowance.
 pitch=math.degrees(math.atan2(3,176))
 local_floor=pieces[3][1].translate((-900,-878,-462)).rotate((0,0,0),(0,1,0),pitch)
 blank=U.box(0,0,0,176.1,44,1.9)
 outside=local_floor.cut(blank).Volume();assert outside<1e-5,outside
 old_flat=U.BASE/'review/fabrication/OVERFLOW_SUPPORT_BRACKET_FLAT.dxf'
 assert old_flat.exists()
 drawings.append(dict(id='U_OVERFLOW_SUPPORT_BRACKET_UNCHANGED_FORMING_REFERENCE',file=os.path.relpath(old_flat,HERE).replace('\\','/'),sha256=sha(old_flat),role='UNCHANGED_FORMING_REFERENCE_COUPON_CALIBRATION_REQUIRED',notes='Existing R2/K0.4 nominal development is unchanged. Forming coupon/received-steel calibration remains required; current installed bracket STEP is26mm lower.'))
 # Installed pose is a reference assembly, never a flat cutting pattern.
 installed=OUT/'LOWERED_WET_INSTALLED_POSE.step';a=cq.Assembly(name='LOWERED_WET_INSTALLED_POSE')
 wet=U.retained_wet_parts()+list(U.drain_parts())
 for n,s,c in wet:a.add(s,name=n,color=cq.Color(*c))
 a.save(str(installed))
 parts.append(dict(id='LOWERED_WET_INSTALLED_POSE',file=installed.relative_to(HERE).as_posix(),sha256=sha(installed),notes='Installed-pose assembly reference only. No additional stock purchase.'))
 pose=DRAW/'LOWERED_PAN_YZ_POSE_REFERENCE.dxf';doc=ezdxf.new('R2010');doc.units=4;ms=doc.modelspace()
 for l in('CURRENT','PREVIOUS','NOTES'):doc.layers.new(l)
 y0,y1=U.O.P.PAN_Y0,U.O.P.PAN_Y1
 for delta,layer in((U.PAN_DROP,'CURRENT'),(0.,'PREVIOUS')):
  z0,z1=U.O.pan_floor_z(y0)-delta,U.O.pan_floor_z(y1)-delta;rim=U.O.P.PAN_RIM-delta
  ms.add_lwpolyline([(y0,z0),(y1,z1),(y1,rim),(y0,rim)],close=True,dxfattribs={'layer':layer})
  ms.add_line((y0,U.O.P.SLAT_TOP-delta),(y1,U.O.P.SLAT_TOP-delta),dxfattribs={'layer':layer})
 ms.add_text('YZ INSTALLED POSE REFERENCE ONLY; horizontal=Y, vertical=Z; mm; previous wet pose +26',dxfattribs={'layer':'NOTES','height':8,'insert':(y0,915)})
 ms.add_line((y0,967.8),(y1,967.8),dxfattribs={'layer':'CURRENT'})
 ms.add_text('Wood workplane Z967.8 remains fixed; receiver outlet Z410 remains fixed',dxfattribs={'layer':'NOTES','height':8,'insert':(y0,935)})
 doc.saveas(pose);assert ezdxf.readfile(pose).units==4
 drawings.append(dict(id='LOWERED_PAN_YZ_POSE_REFERENCE',file=pose.relative_to(HERE).as_posix(),sha256=sha(pose),role='INSTALLED_YZ_POSE_REFERENCE_NOT_CUT_PROFILE',notes='Automatic source-coordinate overlay of current pan/slat envelope and previous wet pose. Not a cut template.'))
 old={n:s for n,s,c in U.O.pan_retainers()}
 rear=[]
 for n,s,c in U.pan_retainers():
  if '_RL'not in n and '_RR'not in n:continue
  error=symmetric_difference(s,old[n].translate((0,0,-U.PAN_DROP)))
  rear.append(dict(id=n,symmetric_difference_from_original_lowered_mm3=error));assert error<1e-5,(n,error)
 src=[Path(__file__),Path(U.__file__),Path(U.M.__file__),Path(U.O.__file__),Path(U.O.P.__file__)]
 report=dict(source_sha256={str(s.relative_to(ROOT)):sha(s)for s in src},pan_lowering_mm=U.PAN_DROP,
  upper_channel_three_strip_union_error_mm3=upper_error,complete_overflow_piece_union_error_mm3=full_error,
  upper_channel_strip_count=3,upper_channel_has_bottom_cap=False,upper_channel_height_mm=h,
  lower_floor_finished_envelope_mm=U.bb(pieces[3][1]),lower_floor_rough_blank_mm=[176.1,44,1.9],
  lower_floor_normal_thickness_mm=1.9*math.cos(math.radians(pitch)),lower_floor_pitch_deg=pitch,
  lower_floor_outside_rough_blank_mm3=outside,lower_floor_width_replaces_legacy_mm=[40.2,44],
  receiver_outlet_Z_mm=410,receiver_lid_Z_mm=391,airgap_mm=19,receiver_pose_unchanged=True,
  rear_retainer_translation_checks=rear,flat_profile_checks=flat_checks,
  guide_flat_plate_union_checks=guide_checks,guide_all_plate_union_errors_zero=all(r['union_error_mm3']<1e-5 for r in guide_checks),
  superseded_retained_flat_ids=SUPERSEDED,parts=parts,additional_manufacturing_drawings=drawings,
  stock_rows=takeoff_rows()+guide_stock_rows(),passed_local_fabrication_geometry=True,
  fabrication_release=False,operating_release=False,
  holds=['Existing formed support-bracket development needs received-material bend-coupon calibration.',
   'Weld sequence, guide/rack distortion and fit, water-tightness, received steel thickness/corrosion finish and floor end fitting need fabrication acceptance.',
   'Supplier valve/union/thread support, receiver usable liquid capacity and interlocks remain unqualified.',
   'Whole-machine collision and screen-handling proofs must be regenerated after the current bed geometry freezes.'])
 f=OUT/'lowered-wet-fabrication-check.json';f.write_text(json.dumps(report,indent=2),encoding='utf-8')
 return report

if __name__=='__main__':
 r=export_all();print(json.dumps(dict(passed=r['passed_local_fabrication_geometry'],parts=len(r['parts']),drawings=len(r['additional_manufacturing_drawings']),upper_union_error=r['upper_channel_three_strip_union_error_mm3'],full_union_error=r['complete_overflow_piece_union_error_mm3'])),flush=True)
 sys.stdout.flush();sys.stderr.flush();os._exit(0)
