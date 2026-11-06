"""Assemble one source-bound small-table revision from the integrated subsystems.

Exact owner clamp/boot source shapes are preserved. The boot's illustrated
registration and the spindle family/ATC acceptance envelopes are labelled
separately from verified installed hardware. No operating release is implied.
"""
from pathlib import Path
import csv,hashlib,importlib.util,json,os,sys
import cadquery as cq
import mechanical as M
import gantry_joint as GJ
import front_stop_bed_clearance as T

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=HERE/'output'
for folder in('head','atc','bed','utilities'):sys.path.insert(0,str(HERE/folder))
import quick_dock as Q
import plasma_quick_dock as P
import owner_head as H
import actual_atc as A
import integrated_bed as B
import bed as OLD_BED

S=M.S
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def integrated_motion(plasma=False,gantry_y=775.,head_x=575.,z_lift=100.,*,module_removed=False,spindle_context=True):
    parts=[p for p in M.motion_parts(plasma,gantry_y,head_x,z_lift)
        if p[0]!='TOOL_ADAPTER_110'and not p[0].startswith(H.REMOVED_PREFIXES)
        and not p[0].startswith(('I_HEAD_','XR_DROP_','XR_PLASMA_DROP_'))]
    head=(P.plasma_head_dock_parts(gantry_y,head_x,z_lift)if plasma else
          Q.actual_head_dock_parts(gantry_y,head_x,z_lift))
    if module_removed:
        local,_=Q.local_parts()
        fixed_ids={p['id']for p in local if p.get('move')!='head'}
        head=[p for p in head if p[0]in fixed_ids]
    elif not plasma and spindle_context:
        axis=Q.local_parts()[1]['nominal_spindle_axis_Y_at_guide775_mm']
        body=cq.Solid.makeCylinder(32.5,268,cq.Vector(head_x,axis+gantry_y-775,970+z_lift))
        head.append(('OWNED_SPINDLE_FAMILY_ENVELOPE_NOT_EXACT',body,(.60,.39,.65)))
    return T.apply_front_stop_state(parts+head,'parked'if module_removed else'operating')

def motion_class(n):
    if n.startswith('INT_STOP_DATUM_'):return 'stationary'
    if n.startswith(('OWNER_','CD_','PLASMA_','OWNED_SPINDLE_')):return 'Y_X_Z_tool'
    return M.motion_class(n)

def wet_parts(*,guards_fitted=True):
    """A utility factory is preferred; no cassette cabinet is inherited."""
    try:
        import integrated_utilities as U
    except ImportError:
        return OLD_BED.pan_parts()+OLD_BED.pan_retainers()+OLD_BED.water_envelopes()
    return U.utility_parts(guards_fitted=guards_fitted)

def bed_parts(angle):
    return [(p['id'],p['shape'],p['color'])for p in B.bed_parts(angle)]

def machine_parts(mode='WOOD',*,pose=None):
    plasma=mode=='PLASMA';removed=mode=='CHANGEOVER'
    if pose is None:pose=(1275.,975.,250.)if removed else(775.,575.,80.)
    gy,hx,z=pose
    parts=M.frame_parts()+wet_parts(guards_fitted=not removed)+bed_parts(45. if removed else(90. if plasma else 0.))
    parts+=integrated_motion(plasma,gy,hx,z,module_removed=removed)
    # The magazine is parked rearward during either cutting mode. Deployment
    # is an explicit interlocked tool-change state, never the default scene.
    parts+=A.actual_atc_parts(200.,hood='fitted'if(plasma or removed)else'stored',include_allocations=True)
    assert len({n for n,s,c in parts})==len(parts),'Duplicate assembly component IDs'
    return parts

def run():
    OUT.mkdir(exist_ok=True)
    paths=[Path(__file__),Path(M.__file__),Path(GJ.__file__),Path(T.__file__),Path(Q.__file__),Path(P.__file__),Path(H.__file__),Path(A.__file__),Path(B.__file__),A.VENDOR_HOUSING_SOURCE]
    try:
        import integrated_utilities as U
        paths.append(Path(U.__file__))
    except ImportError:U=None
    assert U is not None,'Wait for integrated utility factory; do not silently export the old conflicting drain layout.'
    hashes=lambda:{p.relative_to(ROOT).as_posix():sha(p)for p in paths}
    start=hashes();report=dict(revision='INTEGRATED_4080_SMALL',source_sha256=start,
        assessed_X_Y_Z_mm=[800,1000,250],owned_catalogue_Z_mm=300,
        frame_header_length_mm=M.FRAME_LENGTH,frame_header_Y_mm=[M.FRAME_FRONT,M.FRAME_REAR],Y_side_shift_each_mm=25,gantry_rise_mm=40,
        workplane_Z_mm=B.metadata()['workplane_Z_mm'],
        owner_clamp_boot_geometry_modified=False,actual_boot_working_registration_encoded=False,
        actual_vendor_spindle_model=False,
        manufacturer_magazine_external_housing_model=True,
        magazine_housing_model_source=A.VENDOR_HOUSING_SOURCE.relative_to(ROOT).as_posix(),
        actual_received_magazine_revision_or_functional_socket_geometry_verified=False,
        budget_cap_usd=1000,delivered_budget_verified=False,
        fabrication_release=False,operating_release=False,assemblies={})
    scenes={}
    for mode in('WOOD','PLASMA','CHANGEOVER'):
        parts=machine_parts(mode);scenes[mode]=parts
        invalid=[n for n,s,c in parts if not s.isValid()or not s.Solids()or s.Volume()<=0]
        assert not invalid,(mode,invalid)
        a=cq.Assembly(name='INTEGRATED_4080_SMALL_'+mode)
        for n,s,c in parts:A.add_assembly_part(a,n,s,c)
        path=OUT/('INTEGRATED_4080_SMALL_'+mode+'.step');a.save(str(path))
        back=cq.importers.importStep(str(path)).val()
        vol=sum(s.Volume()for n,s,c in parts);err=abs(back.Volume()-vol)
        check=dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path),
            components=len(parts),solids=len(back.Solids()),native_solids=sum(len(s.Solids())for n,s,c in parts),
            valid=back.isValid(),volume_error_mm3=err,bounds_mm=S.bounds(back),
            sum_component_volume_is_not_physical_mass=True)
        check['passed']=check['valid']and check['solids']==check['native_solids']and err<max(.5,vol*1e-7)
        report['assemblies'][mode]=check
        print(mode,'STEP',check['passed'],check['components'],flush=True)
    from preview import legacy
    for mode,parts in scenes.items():
        path=OUT/('INTEGRATED_4080_SMALL_'+mode+'.png')
        legacy.render(parts,back=mode=='PLASMA',w=1600,h=1500).save(path)
        report['assemblies'][mode]['preview']=dict(file=path.relative_to(HERE).as_posix(),sha256=sha(path))
    with(OUT/'assembly-components.csv').open('w',newline='',encoding='utf-8')as f:
        w=csv.writer(f);w.writerow(['mode','component','solid_count'])
        for mode,parts in scenes.items():
            for n,s,c in parts:w.writerow([mode,n,len(s.Solids())])
    report['source_consistent_during_build']=start==hashes()
    report['passed']=report['source_consistent_during_build']and all(q['passed']for q in report['assemblies'].values())
    report['meaning_of_pass']='Assembly validity and independent STEP readback only; combined clearance, requirements, actual supplier interfaces and delivered cost are separate release gates.'
    (OUT/'assembly-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],source_consistent=report['source_consistent_during_build'])),flush=True)
    return 0 if report['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
