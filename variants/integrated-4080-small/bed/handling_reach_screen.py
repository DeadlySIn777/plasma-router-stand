"""Reachable side-edge grip sensitivity; not a manual-handling release."""
from pathlib import Path
import csv,hashlib,json,math

HERE=Path(__file__).resolve().parent;OUT=HERE/'output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
 proof=OUT/'bed-local-check.json';local=json.loads(proof.read_text(encoding='utf-8'))
 assert local['passed']and local['source_consistent_during_build']
 paths=[Path(__file__),proof];start={p.name:sha(p)for p in paths}
 rows=[];summaries=[]
 for masscase in local['analysis']['mass_and_force_cases']:
  for forcecase in masscase['cases']:
   group=[]
   for sample in forcecase['samples']:
    a=sample['angle_deg'];theta=math.radians(a)
    # Side grip is the actual unobstructed outer edge after screen removal,
    # rather than an invented purchased handle. Bed must be empty.
    radius=1280. if a<=35 else 650.
    residual=sample['gravity_moment_Nm']-sample['gas_assist_moment_Nm']
    row=dict(moving_deck_mass_kg=masscase['moving_mass_kg'],gas_force_ratio=forcecase['gas_force_ratio'],
     angle_deg=a,grip='rear-edge'if a<=35 else'mid-side-edge',grip_lever_mm=radius,
     global_closed_grip_Y_mm=-100+radius,
     conservative_grip_height_mm=967.8+radius*math.sin(theta),
     normal_hand_force_N=residual/(radius/1000))
    rows.append(row);group.append(row)
   summaries.append(dict(moving_deck_mass_kg=masscase['moving_mass_kg'],gas_force_ratio=forcecase['gas_force_ratio'],
    maximum_absolute_normal_hand_force_N=max(abs(r['normal_hand_force_N'])for r in group),
    maximum_grip_height_mm=max(r['conservative_grip_height_mm']for r in group)))
 path=OUT/'bed-handling-reach-force.csv'
 with path.open('w',newline='',encoding='utf-8')as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 report=dict(study='STATIC_REACHABLE_EDGE_GRIP_SENSITIVITY',source_sha256=start,
  source_consistent=start=={p.name:sha(p)for p in paths},force_model_inherited_from=proof.name,
  grips=dict(rear_closed_Y_mm=1180,rear_lever_mm=1280,transfer_angle_deg=35,
   midside_closed_Y_mm=550,midside_lever_mm=650,left_right_X_mm=[75,1075],
   prerequisite='Empty bed, all sectional guide screens removed and stored, tool/head module removed, exact qualified machine park.'),
  summary=summaries,force_csv=dict(file=path.name,sha256=sha(path)),
  additional_hardware_invented=False,assist_selfweight_and_measured_force_curve_included=False,
  human_factors_qualified=False,fall_control_qualified=False,operating_release=False,
  scope='Calculated ideal static normal force only. Actual grip dimensions, ability to transfer two hands, reach, edge comfort, assist selfweight and physical safe handling remain acceptance items. This is not a catch or fall-arrest mechanism.')
 report['passed']=report['source_consistent']and len(rows)==1092
 (OUT/'bed-handling-reach-screen.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=report['passed'],summary=summaries)))
 return 0 if report['passed']else 1

if __name__=='__main__':raise SystemExit(run())
