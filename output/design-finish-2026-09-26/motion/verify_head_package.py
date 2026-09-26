"""Bind current head exports and verify every modeled head fastener envelope."""
from pathlib import Path
import hashlib,json,os,re,sys
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
SRC=ROOT/'output/release-review/RevE-ENGINEERING';sys.path.insert(0,str(SRC))
import motion_finish as mf
from cad_helpers import Model,bbox

def main():
    source=hashlib.sha256((SRC/'motion_finish.py').read_bytes()).hexdigest()
    checker=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    m=Model();mf.extend_router_model(m);rows=[]
    diameters={3:5.5,4:7.,5:8.5,6:10.2}
    for p in m.parts:
        match=re.fullmatch(r'I_STD_M(\d+)x([\d.]+)_(y|z)_SOCKET',p.part_number)
        if match:
            d,L,axis=int(match[1]),float(match[2]),match[3]
            expected=[diameters[d],diameters[d],L+d]
            if axis=='y':expected=[diameters[d],L+d,diameters[d]]
        elif p.id.startswith('I_HEAD_MAGNET_SCREW_'):expected=[8.96,8.96,16.]
        elif p.id.startswith('I_PARK_BOLT_'):expected=[8.5,8.5,23.]
        elif p.id.startswith('I_TOOL_MOUNT_'):expected=[10.2,10.2,22.]
        else:continue
        bb=bbox(p.local);actual=[bb[i+3]-bb[i] for i in range(3)]
        rows.append({'id':p.id,'part_number':p.part_number,'expected_local_extent_mm':expected,'actual_local_extent_mm':actual,'passed':max(abs(a-b) for a,b in zip(actual,expected))<1e-5})
    package=OUT/'head-cad';ops=json.loads((package/'part-operations.json').read_text(encoding='utf8'))
    expected_steps={o['part_number']+'.step' for o in ops if not o['individual_export_guarded']}
    expected_dxf={o['part_number']+'.dxf' for o in ops if not o['individual_export_guarded'] and o['manufacturing_flat']}
    actual_steps={p.name for p in (package/'parts').glob('*.step')};actual_dxf={p.name for p in (package/'dxf').glob('*.dxf')}
    validation=json.loads((package/'RevI_FLOAT_BREAKAWAY_HEAD_BLANK-validation.json').read_text(encoding='utf8'))
    mechanism=json.loads((OUT/'mechanism-verification.json').read_text(encoding='utf8'))
    r={'motion_source_sha256':source,'mechanism_source_matches':source==mechanism['source_sha256']['motion_finish.py'],
       'verifier_file':str(Path(__file__).relative_to(ROOT)).replace('\\','/'),'verifier_sha256_before':checker,
       'socket_head_basis':'Unknurled ISO4762 selected envelope M3 5.5x3, M4 7x4, M5 8.5x5; M6 modeled10.2x6 conservatively covers supplier10x6. Larger knurled heads are outside selection.',
       'countersunk_basis':'ISO10642 M4x16, head8.96x2.48,90degree cone.16mm is total overall length, not under-head length.',
       'recesses':'Button M3 counterbores6.0x3; stop M4 counterbores7.5x4; clamp M4 counterbores8x4. Magnet supplier countersink9.46x2.48 exceeds selected head by0.50mm diameter.',
       'cam_screw_correction':'Second cam screw movedV96.8 to96.5, giving0.25mm nominal radial clearance from its5.5mm head to bridge startV99.5.',
       'sources':{'M3':mf.SOURCES['socket_m3'],'M4':mf.SOURCES['socket_m4'],'M5':'https://www.accu.co.uk/metric-cap-head-screws/250442-SSCF-M5-18-A2-R360','M6':'https://www.accu.co.uk/metric-cap-head-screws/250454-SSCF-M6-16-A2-R360','M4_CSK':mf.SOURCES['countersunk_m4']},
       'fastener_checks':rows,'expected_individual_steps':len(expected_steps),'expected_dxfs':len(expected_dxf),
       'missing_step':sorted(expected_steps-actual_steps),'obsolete_step':sorted(actual_steps-expected_steps),'missing_dxf':sorted(expected_dxf-actual_dxf),'obsolete_dxf':sorted(actual_dxf-expected_dxf),
       'assembly_step_readback':validation['step_readback'],'individual_readbacks':validation['individual_step_readback'],
       'file_sha256':{str(p.relative_to(package)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in package.rglob('*') if p.is_file()}}
    r['verifier_sha256_after']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    r['source_unchanged']=source==hashlib.sha256((SRC/'motion_finish.py').read_bytes()).hexdigest()
    r['passed']=r['mechanism_source_matches'] and mechanism['passed'] and r['source_unchanged'] and checker==r['verifier_sha256_after'] and all(x['passed'] for x in rows) and not any(r[k] for k in ('missing_step','obsolete_step','missing_dxf','obsolete_dxf')) and r['assembly_step_readback']['passed'] and len(r['individual_readbacks'])==len(expected_steps)
    (OUT/'head-package-verification.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    print('HEAD_PACKAGE',r['passed'],'fasteners',len(rows),'STEP',len(expected_steps),'DXF',len(expected_dxf),flush=True)
    return r['passed']
if __name__=='__main__':
    try:code=0 if main() else 2
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
