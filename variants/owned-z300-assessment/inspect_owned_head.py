"""Read-only inspection of the recovered owner clamp/boot files.

The old illustrative mating transform is a diagnostic, not an installed pose.
No correction to either supplied solid, substitute clamp, or guessed actuator.
"""
from pathlib import Path
import hashlib,json,os,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
SRC=HERE/'sources/owned-head'
OUT=HERE/'output/owned-head-inspection.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(s):
    b=s.BoundingBox()
    return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def main():
    files={'clamp':SRC/'R10 - original uncut 65 mm spindle clamp.step',
           'boot':SRC/'Spindle dust boot.step'}
    expected={'clamp':'506d12b3f749db3eeec03e133b519fd93e45ff1b6cb80bd8fa568d3fb0dba1cb',
              'boot':'3716855cf25a308de3db696ae827578d7803bfe4665fd1a6535f311a5246a044'}
    paths=[Path(__file__),*files.values(),SRC/'recovered-owner-basis.json',SRC/'prior-mating-inspection.json',
           SRC/'owner-decisions.json',SRC/'owner-actuator-selection.json',SRC/'owner-working-boot.json']
    start={p.relative_to(HERE).as_posix():sha(p)for p in paths}
    assert all(sha(p)==expected[k]for k,p in files.items())
    shapes={k:cq.importers.importStep(str(p)).val()for k,p in files.items()}
    records={k:dict(file=files[k].relative_to(HERE).as_posix(),sha256=sha(files[k]),
                   valid=s.isValid(),solids=len(s.Solids()),faces=len(s.Faces()),
                   native_bounds_mm=bounds(s),volume_mm3=s.Volume(),geometry_modified=False)
             for k,s in shapes.items()}
    prior=json.loads((SRC/'prior-mating-inspection.json').read_text(encoding='utf-8'))
    m=prior['illustrated_candidate']
    clamp=shapes['clamp'].rotate((0,0,0),(0,1,0),m['pitch_about_native_Y_deg']).rotate(
        (0,0,0),(0,0,1),m['yaw_about_boot_Z_deg']).translate(tuple(m['translation_after_rotations_mm']))
    rows=[]
    for t in (0.,10.,20.,30.,40.,50.):
        boot=shapes['boot'].translate((0,0,-t))
        v=abs(boot.intersect(clamp).Volume())
        rows.append(dict(illustrative_boot_Z_offset_mm=-t,overlap_mm3=v,no_nominal_overlap=v<.02))
    report=dict(study='RECOVERED_OWNER_HEAD_INPUTS_AND_PRIOR_MATE_DIAGNOSTIC',
        source_sha256=start,parts=records,expected_source_bytes_match=True,
        source_geometry_modified=False,illustrative_mate=m,diagnostic_rows=rows,
        diagnostic_scope='Six exact sampled positions only. Old inferred coaxial mate; not the real head home datum or a universal proof that these parts cannot work.',
        owner_parts_in_current_proposal=False,
        current_proposal_clamp_is_provisional=True,
        substitute_clamp_is_selected_for_purchase=False,
        owner_confirms_clamp_matches_supplied_STEP=True,
        owner_confirms_existing_boot_assembly_works=True,
        owner_identifies_entire_boot_as_moving_body=True,
        owner_actuator=dict(brand='Pegelong',ASIN='B0D6BCQCVR',stroke_mm=50,
            identity_previously_supplied=True,replace_or_redesign_requested=False),
        required_design_work=[
            'Integrate the actual owned clamp with a removable head adapter; do not machine the substitute split clamp as the final owner part.',
            'Register the existing working whole-boot assembly, selected actuator and 50 mm working endpoints in machine coordinates without changing the assembly or supplied brush groove.',
            'Preserve the owner-confirmed uncut clamp geometry; diagnostic overlap in an inferred placement does not justify cutting it.',
            'Repeat tool/ATC/bed motion and service checks with the integrated owner head and its service loop.'],
        gate='OWNER_HEAD_INTEGRATION_OPEN',
        complete_head_fit_proved=False,fabrication_release=False,operating_release=False)
    report['source_consistent_during_check']=start=={p.relative_to(HERE).as_posix():sha(p)for p in paths}
    report['inspection_completed']=all(p['valid']for p in records.values())and report['source_consistent_during_check']
    OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(inspection_completed=report['inspection_completed'],gate=report['gate'],diagnostic=rows)),flush=True)
    return 0 if report['inspection_completed']else 1

if __name__=='__main__':
    try:code=main()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
