"""Copy this revision to the user's existing workspace without hiding edits."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT=Path(__file__).resolve().parent
MIRROR=Path('C:/Users/Gluis/OneDrive/Documents/ChatGPT/New project/plasma_router_stand')
BASELINE='9e3dd66279812c61646b466c55d3aa97895eefb6'
REPORT=Path('output/design-finish-2026-09-26/mirror-verification.json')


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def in_scope(name):
    return (name in {'README.md','build_concept_revi.py','package_revi.py','sync_revi_workspace.py',
                    'output/pdf/plasma-router-stand-concept.pdf',
                    'output/cad-repair-2026-09-25/SUPPLIER-DRAWING-REQUEST.md'}
            or name.startswith(('output/design-finish-2026-09-26/',
                                'output/release-review/RevI-CAD/'))
            or name in {'output/release-review/RevE-ENGINEERING/'+p for p in (
                'build_revi.py','structure_finish.py','service_finish.py','motion_finish.py','render_revi.py')})


def main():
    changed=git('diff','--name-only',BASELINE).decode().splitlines()
    new=git('ls-files','--others','--exclude-standard').decode().splitlines()
    paths={name for name in changed+new if in_scope(name)}
    paths.update(str(p.relative_to(ROOT)).replace('\\','/')
                 for p in (ROOT/'output/release-review/RevI-CAD/previews').glob('*.npz'))
    paths.discard(str(REPORT).replace('\\','/'))
    baseline=set(git('ls-tree','-r','--name-only',BASELINE).decode().splitlines())
    conflicts=[];deletions=[];items=[]
    for name in sorted(paths):
        source=ROOT/name;dest=MIRROR/name
        assert source.resolve().is_relative_to(ROOT.resolve())
        assert dest.resolve().is_relative_to(MIRROR.resolve())
        if not source.is_file():
            deletions.append(name);continue
        if dest.exists() and source.read_bytes()!=dest.read_bytes():
            if name not in baseline or dest.read_bytes()!=git('show',BASELINE+':'+name):
                conflicts.append(name)
        items.append((name,source,dest))
    assert not conflicts, 'Preserved conflicting mirror edits: '+repr(conflicts)
    assert not deletions, 'Source deletions require explicit handling: '+repr(deletions)
    for name,source,dest in items:
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,dest)
    hashes={name:digest(source) for name,source,dest in items}
    assert all(digest(dest)==hashes[name] for name,source,dest in items)
    record={'baseline_commit':BASELINE,'copied_and_hash_verified_files':len(items),
            'conflicting_mirror_edits':conflicts,'deleted_files':[],
            'method':'Copy only revision-scoped files; overwrite only matching baseline or identical current bytes.',
            'sha256':hashes}
    (ROOT/REPORT).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    (MIRROR/REPORT).parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/REPORT,MIRROR/REPORT)
    print('Copied and hash-verified',len(items),'revision files plus the verification record.')


if __name__=='__main__':main()
