"""Exact supplied 65 mm clamp on the existing removable Z adapter.

The working boot assembly is preserved, never cut or replaced. Its actual home
registration is absent from the supplied separate STEP bodies. The default
boot pose is therefore explicitly an illustrated registration, not a working
50 mm joint. Supply boot_registration_z_mm only from the existing assembly.
"""
from functools import lru_cache
from pathlib import Path
import hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CAND=ROOT/'variants/owned-z300-assessment'
sys.path.insert(0,str(CAND))
import candidate_motion_factory as C
import z300_fit_study as S

SRC=CAND/'sources/owned-head'
CLAMP=SRC/'R10 - original uncut 65 mm spindle clamp.step'
BOOT=SRC/'Spindle dust boot.step'
OWNER_ROTATED_TRANSLATION=(-222.219380921411,28.225-144.246235656735,-35.-187.4179079643)
CLAMP_REGISTER_Z=1142.
ADAPTER_FRONT_Y_AT_REFERENCE=666.9
SPACER_LENGTH=6.
MOUNT_X=(-25.,25.)
MOUNT_Z=(1092.,1122.)
WALL=7.00205925132
SPINDLE_AXIS_Y_AT_REFERENCE=618.39794074868
REFERENCE=(775.,575.,0.)
REMOVED_PREFIXES=('TOOL_SPINDLE_','TOOL_SPLIT_CLAMP_','TOOL_CLAMP_')
HEAD_IDS=('TOOL_ADAPTER_110','OWNER_65MM_CLAMP','OWNER_POWERED_SHIELD_BOOT_BODY')
AL=(.64,.71,.74);DARK=(.22,.25,.28);BOOT_COLOR=(.40,.24,.58)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bounds(s):return S.bounds(s)
def cyl(d,h,o,axis=(0,1,0)):
    return cq.Solid.makeCylinder(d/2,h,cq.Vector(*o),cq.Vector(*axis))

def sources():
    paths=[Path(__file__),HERE/'build_head.py',HERE/'spindle-reference-evidence.json',CLAMP,BOOT,SRC/'prior-mating-inspection.json',
        SRC/'owner-working-boot.json',SRC/'owner-decisions.json',SRC/'owner-actuator-selection.json',
        Path(C.__file__),Path(S.__file__),CAND/'front_stop_repair.py',CAND/'custom_joint_repair.py',
        ROOT/'variants/extrusion-reengineered/motion.py']
    paths.extend(ROOT/n for n in S.M.interface_metadata()['source_sha256'])
    return list(dict.fromkeys(paths))

@lru_cache(maxsize=1)
def source_owner_local():
    mating=json.loads((SRC/'prior-mating-inspection.json').read_text(encoding='utf-8'))['illustrated_candidate']
    clamp=cq.importers.importStep(str(CLAMP)).val().rotate((0,0,0),(0,1,0),90).rotate(
        (0,0,0),(0,0,1),180).translate(tuple(mating['translation_after_rotations_mm']))
    boot=cq.importers.importStep(str(BOOT)).val()
    return tuple(s.rotate((0,0,0),(0,0,1),90).translate(OWNER_ROTATED_TRANSLATION)
        for s in(clamp,boot))

@lru_cache(maxsize=1)
def base_known_parts():
    """Known custom joint at X575/Y775/Z0; same 110 mm receiver blank."""
    original={n:s for n,s,c in C.motion_parts(False,775,575,0)}
    adapter=original['TOOL_ADAPTER_110']
    # New custom-side tapped rows. The supplier output attachment is still
    # transfer-drilled on the removed adapter; no supplier hole is invented.
    for dx in MOUNT_X:
        for z in MOUNT_Z:
            adapter=adapter.cut(cyl(5,14.7,(575+dx,665.9,z)))
    out=[('TOOL_ADAPTER_110',adapter.clean(),AL)]
    clamp,_=source_owner_local()
    # A common rigid transform only. Source geometry and 50x30 pattern survive.
    ty=ADAPTER_FRONT_Y_AT_REFERENCE-SPACER_LENGTH+28.225
    clamp=clamp.rotate((0,0,0),(0,0,1),180).translate((575,ty,CLAMP_REGISTER_Z))
    out.append(('OWNER_65MM_CLAMP',clamp,AL))
    for i,dx in enumerate(MOUNT_X):
        for k,z in enumerate(MOUNT_Z):
            x=575+dx;tag=f'{i+1}_{k+1}'
            mount=ADAPTER_FRONT_Y_AT_REFERENCE-SPACER_LENGTH
            spacer=cyl(10,SPACER_LENGTH,(x,mount,z)).cut(cyl(5.5,SPACER_LENGTH+2,(x,mount-1,z)))
            seat=mount-WALL
            washer=cyl(10,1,(x,seat-1,z)).cut(cyl(5.3,3,(x,seat-2,z)))
            screw=cyl(5,25,(x,seat-1,z)).fuse(cyl(8.5,5,(x,seat-6,z))).clean()
            out.extend([('OWNER_CLAMP_SPACER_'+tag,spacer,AL),
                ('OWNER_CLAMP_M5_SPREADER_'+tag,washer,DARK),('OWNER_CLAMP_M5X25_'+tag,screw,DARK)])
    return tuple(out)

def actual_head_parts(gantry_y=775.,head_x=575.,z_lift=0.,boot_lift=0.,*,
                      boot_registration_z_mm=None,include_boot=True,include_spindle_reference=False):
    """Return named exact owner/custom review solids at the requested pose.

    boot_lift is positive up. With no registered working-home datum, only the
    default illustrated pose boot_lift=0 is accepted. Do not animate that pose
    as the actual working owner joint. No controller settings are implied.
    """
    assert 175<=head_x<=975 and 275<=gantry_y<=1275 and 0<=z_lift<=250
    assert 0<=boot_lift<=50
    if boot_registration_z_mm is None and boot_lift!=0:
        raise ValueError('Actual boot home registration is not encoded; do not animate the old inferred mate as a working joint.')
    shift=(head_x-575,gantry_y-775,z_lift)
    out=[(n,s.translate(shift),c)for n,s,c in base_known_parts()]
    if include_boot:
        _,boot=source_owner_local()
        ty=ADAPTER_FRONT_Y_AT_REFERENCE-SPACER_LENGTH+28.225
        boot=boot.rotate((0,0,0),(0,0,1),180).translate((head_x,ty+shift[1],
            CLAMP_REGISTER_Z+z_lift+boot_lift+(boot_registration_z_mm or 0)))
        out.append(('OWNER_POWERED_SHIELD_BOOT_BODY',boot,BOOT_COLOR))
    if include_spindle_reference:
        # The supplied physical kit is owned. This maximum family cylinder is
        # optional context, not exact nose, gripping-region or collet geometry.
        body=cq.Solid.makeCylinder(32.5,268,cq.Vector(head_x,SPINDLE_AXIS_Y_AT_REFERENCE+shift[1],970+z_lift))
        out.append(('OWNED_SPINDLE_MAX_FAMILY_ENVELOPE_NOT_EXACT',body,(.59,.39,.16)))
    return out

def integrate_motion(parts,gantry_y=775.,head_x=575.,z_lift=0.,boot_lift=0.,**kwargs):
    """Replace all substitute router tool parts; plasma stays a separate mode."""
    common=[p for p in parts if p[0]!='TOOL_ADAPTER_110'and not p[0].startswith(REMOVED_PREFIXES)]
    return common+actual_head_parts(gantry_y,head_x,z_lift,boot_lift,**kwargs)

def metadata():
    return dict(owner_clamp_and_boot_source_geometry_modified=False,
        owner_clamp_matches_as_machined_owner_confirmed=True,
        owned_working_whole_boot_preserved=True,selected_actuator='Pegelong B0D6BCQCVR',
        whole_boot_travel_mm=50,actual_working_boot_registration_encoded=False,
        illustrated_boot_pose_is_operating_registration=False,
        spindle_family_reference_ASIN='B0BF5R3LNC',spindle_family_mount_diameter_mm=65,
        historical_spindle_length_mm=259,current_manufacturer_family_length_mm=268,
        exact_received_spindle_nose_and_collet_datum_verified=False,
        nominal_spindle_axis_at_reference_mm=[575,SPINDLE_AXIS_Y_AT_REFERENCE],
        nominal_reference_lower_Z_mm=970,reference_is_measured_collet_plane=False,
        adapter_finished_blank_X_Z_thickness_mm=[110,110,12.7],
        adapter_unchanged_outer_world_bounds_mm=bounds(base_known_parts()[0][1]),
        new_tapped_pattern_X_Z_mm=[[-25,22],[25,22],[-25,52],[25,52]],
        adapter_local_datum='X0 at platecentre; Z0 at lowerZ1070; Y front666.9 at X575/Y775/Z0',
        clamp_mount_bores_mm=5.5,clamp_mount_pattern_mm=[50,30],
        clamp_source_wall_to_counterbore_seat_mm=WALL,spacer_length_mm=SPACER_LENGTH,
        mount_screw='4x M5x25 socket head, nominal8.5ODx5 head, with10OD5.3ID1thick steelspreader',
        spreader_reason='One source counterbore has a small outer-seat interruption. The10mm steelwasher bridges it while fully supporting the8.5mm screwhead; the owner clamp is not cut.',
        nominal_M5_engagement_mm=25-WALL-SPACER_LENGTH-1,
        adapter_thread_thickness_mm=12.7,
        nominal_screw_tip_reserve_before_rear_face_mm=12.7-(25-WALL-SPACER_LENGTH-1),
        custom_tap_process='4.2mm pilot through, M5x0.8; minor drill is not5mm major CAD void',
        removed_substitute_clamp_parts=True,supplier_Z_output_pattern_invented=False,
        fabrication_release=False,operating_release=False)
