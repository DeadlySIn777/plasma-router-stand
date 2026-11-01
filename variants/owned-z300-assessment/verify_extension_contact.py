"""Identify whether a contact seen in a whole-part check was already in XR2."""
import json,os,sys,hashlib
from pathlib import Path
import z300_fit_study as S

HERE=Path(__file__).resolve().parent
original=S.M.motion_parts(False,gantry_y=775,head_x=575,z_lift=100)
old={n:s for n,s,_ in original}
new={n:s for n,s,_ in S.overlay(original,extended_carrier=True)}
obstacle=old['X_LINK_SUPPORT']
old_overlap=old['Z_CARRIER'].intersect(obstacle)
new_overlap=new['Z_CARRIER'].intersect(obstacle)
added=new['Z_CARRIER'].cut(old['Z_CARRIER'])
report=dict(pair=['Z_CARRIER','X_LINK_SUPPORT'],
    old_overlap_mm3=old_overlap.Volume(),new_overlap_mm3=new_overlap.Volume(),
    added_material_overlap_mm3=added.intersect(obstacle).Volume(),
    overlap_symmetric_difference_mm3=old_overlap.cut(new_overlap).Volume()+new_overlap.cut(old_overlap).Volume(),
    actual_original_interface_qualified=False,
    meaning='Unchanged inherited positive-volume interference between custom parts, not introduced by the300mm overlay. This is a real unresolved design defect, not permitted bearing contact; the separate relief/support repair must be verified before fabrication.')
report['unchanged_overlap']=report['overlap_symmetric_difference_mm3']<.05 and report['added_material_overlap_mm3']<.05
primary_step=HERE/'output'/'Z300_STOCK_EXISTING_CARRIER.step'
optional_step=HERE/'output'/'Z300_OPTIONAL_EXTENDED_CARRIER.step'
primary_head=S.cq.importers.importStep(str(primary_step)).val()
optional_head=S.cq.importers.importStep(str(optional_step)).val()
def step_carrier(shape,height):
    matches=[]
    for solid in shape.Solids():
        b=S.bounds(solid)
        if abs(b[3]-b[0]-260)<1e-4 and abs(b[5]-b[2]-height)<1e-4:
            matches.append(solid)
    assert len(matches)==1,(height,len(matches))
    return matches[0]
carrier_before=step_carrier(primary_head,270.2)
carrier_after=step_carrier(optional_head,370.2)
step_added=carrier_after.cut(carrier_before)
step_removed=carrier_before.cut(carrier_after)
head_delta=optional_head.Volume()-primary_head.Volume()
carrier_delta=carrier_after.Volume()-carrier_before.Volume()
report['optional_carrier_exact_STEP_material']=dict(
    primary_head_volume_mm3=primary_head.Volume(),optional_head_volume_mm3=optional_head.Volume(),
    complete_head_volume_difference_mm3=head_delta,carrier_volume_difference_mm3=carrier_delta,
    added_material_volume_mm3=step_added.Volume(),removed_material_volume_mm3=step_removed.Volume(),
    assumed_aluminum_density_kg_per_m3=2700,
    optional_added_nominal_Al_kg=step_added.Volume()*2.7e-6,
    verified=primary_head.isValid()and optional_head.isValid()and step_removed.Volume()<1e-6
        and abs(head_delta-carrier_delta)<.05 and abs(carrier_delta-step_added.Volume())<.05,
    meaning='Exact imported STEP carrier material addition; not a tessellated bounding-box proxy and not the mass of the purchased Z stage.')
files=[Path(__file__),HERE/'z300_fit_study.py',S.BASE/'motion.py',S.BASE/'params.py',primary_step,optional_step]
report['source_sha256']={p.relative_to(S.ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
(HERE/'output'/'extension-contact-disposition.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2),flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0 if report['unchanged_overlap'] and report['optional_carrier_exact_STEP_material']['verified'] else 1)
