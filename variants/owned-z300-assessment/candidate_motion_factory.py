"""One explicit physical-Z300/working200 review factory; no source changes."""
import z300_fit_study as S
import custom_joint_repair as R
import front_stop_repair as F

def motion_parts(plasma,gantry_y=775.,head_x=575.,z_lift=50.):
    assert 175.<=head_x<=975. and 275.<=gantry_y<=1275. and 0.<=z_lift<=200.
    return F.apply_repairs(R.apply_repairs(S.overlay(S.M.motion_parts(plasma,gantry_y,head_x,z_lift),extended_carrier=False)))

part_motion_class=S.cls
