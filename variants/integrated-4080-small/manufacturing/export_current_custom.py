"""Export the current integrated frame/motion custom parts, never old poses."""
from pathlib import Path
import csv, hashlib, json, os, sys

HERE=Path(__file__).resolve().parent
MACHINE=HERE.parent
ROOT=MACHINE.parents[1]
sys.path.insert(0,str(MACHINE))
import assembly as A
import cadquery as cq

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def readcsv(p):
    with Path(p).open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def relative(p):return Path(p).relative_to(ROOT).as_posix()

def run():
    source_paths=[Path(__file__),Path(A.__file__),Path(A.M.__file__),
        ROOT/'variants/extrusion-reengineered/review/frame-fabrication.csv',
        ROOT/'variants/extrusion-reengineered/motion-fabrication.csv']
    source_paths += [Path(A.M.C.__file__),Path(A.Q.__file__),Path(A.P.__file__),Path(A.H.__file__),Path(A.T.__file__),Path(A.GJ.__file__)]
    snapshot=lambda:{relative(p):sha(p)for p in source_paths}
    start=snapshot()
    frames=readcsv(source_paths[3]);motion=readcsv(source_paths[4])
    selected={r['id']:dict(category=r['category'],material=r['material'],
        notes=r.get('qualification',''),source='frame_takeoff')for r in frames
        if r['category']in('Flat plate','One-piece bearing angle','Tension strap','Brace spacer')}
    selected.update({r['id']:dict(category='Motion custom',material=r['material'],notes=r['notes'],source='motion_takeoff')
        for r in motion if r['category'].startswith('CUSTOM')})
    current_frame=A.M.frame_parts()
    for n,s,c in current_frame:
        if n not in selected and not n.endswith('_ALLOWANCE'):
            if n.startswith('INT_PAN_FRONT_HEADER_HANGER_'):
                selected[n]=dict(category='Integrated welded hanger',material='Uncoatedplainsteel6.35mm',
                    notes='Welded stock set: one stepped160x351.85x6.35boundingflatblank (80mmverticalweb with integral160mmtop), plusbearingseat80x80x6.35mm. Not a solid bounding billet. Header4M6facefixings perhanger atY240/280/320/360,Z1033;2M8endcorebeamfixings perhanger atZ720.5/760.5. Actual weld/capacity/profile-nut/fastener qualification held.',source='integrated_frame_new_custom')
            else:
                selected[n]=dict(category='Profile envelope operation reference',material='Purchased4080,actualdie/core/slotsheld',
                    notes='Current source-defined profile envelope and machining/interface allocations. Not actual supplier section CAD; never purchase the bounding box as solid billet.',source='integrated_frame_profile')
    for n in('INT_GANTRY_4080_FRONT','INT_GANTRY_4080_REAR'):
        selected[n]=dict(category='Profile envelope operation reference',material='Purchased4080,actualdie/core/slotsheld',
            notes='Pairedgantry1250mmprofile; through-sleevebores and requiredslot cavities are machining/interface references, not a fabricated supplier die.',source='integrated_gantry_profile')
    for n,s,c in A.T.datum_parts():
        if n.endswith('_BLOCK'):
            selected[n]=dict(category='Manual stop datum block',material='Plainsteel6.35mm',
                notes='Finish20x20x6.35mm; one6.6throughclearancehole. Fourfixedoperating/parkedlocatorblocks; actualslotnut/profilefitandrepeatabilityheld.',source='integrated_front_stop_datum')
    parts={}
    for plasma in(False,True):
        for n,s,c in current_frame+A.integrated_motion(plasma,775.,575.,100.,spindle_context=False):
            if n in selected or n.startswith('INT_GANTRY_GUIDE_BAR_')or n=='CD_GRAVITY_LEDGE':
                parts.setdefault(n,s)
    out=HERE/'current-custom-step';out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for n,s in parts.items():
        b=A.S.bounds(s);origin=b[:3];size=[b[i+3]-b[i]for i in range(3)]
        local=s.translate(tuple(-v for v in origin))
        path=out/(n+'_INTEGRATED.step')
        cq.exporters.export(local,str(path))
        back=cq.importers.importStep(str(path)).val()
        error=abs(back.Volume()-local.Volume());bb=A.S.bounds(back)
        bbox_error=max(abs(a-b)for a,b in zip(bb,[0,0,0]+size))
        valid=back.isValid()and len(back.Solids())==len(local.Solids())and error<max(.01,local.Volume()*1e-7)and bbox_error<1e-5
        assert valid,n
        meta=selected.get(n,dict(category='New integrated custom',material='Aluminum, actual alloy/temper held',notes='',source='integrated_factory'))
        notes=meta['notes']
        if n=='Z_CARRIER':notes='Integrated carrier with candidate through-relief162.95x6.55,R3.275; finished260x270.2x12.7. Supplier300Z attachment transfer-fit held. No owned-sheet credit.'
        if n=='X_LINK_SUPPORT':notes='Integral downstand37mm; finished156x120.8x43.35. Four specified5.0pilots/tapM6x1 through8mm; nominal6mm STEP bores are thread-major envelopes. New billet plus cleanup, no owned credit.'
        if n in('Y_STOP_L_FRONT_BRACKET','Y_STOP_R_FRONT_BRACKET','XR_STOP_CARRIER_L_FRONT','XR_STOP_CARRIER_R_FRONT'):
            notes='Integrated revised front-stop geometry; front fixingY105,rearY140, inherited supplier motor relief. Header side shift and rise are included in this current STEP; use actual axes here. New part, not oldY90 hole-plug repair. Joint capacity remains held.'
        if n.startswith('INT_GANTRY_GUIDE_BAR_'):notes='1200x40x12.7 finished rail datum bar. Current holes/counterbores retained; transfer actual rail fixing pattern. New long aluminum stock, no owned-sheet credit.'
        if n in('XR_EX_DRY_ARM_L_3','XR_EX_DRY_ARM_R_3'):
            notes='Rear4080drysupportarm: machineoneD12.5verticalthroughopen-front-and-outboardcorneraccessnotchatworldX125(left)or1025(right),Y1140. CurrentSTEPcontains42mmthroughcutterover40mmprofileheight. Thisreplacesold105/1045axis,notasecondnotch. Supportsinitialbed-screwheadtiltclearance; actualdie,remainingligamentsandbearingcapacitymustbequalified.'
        rows.append(dict(id=n,category=meta['category'],material=meta['material'],step=relative(path),sha256=sha(path),
            source_world_min_corner_mm=origin,finished_world_aligned_dimensions_mm=size,
            volume_mm3=local.Volume(),solid_count=len(back.Solids()),valid=valid,
            roundtrip_volume_error_mm3=error,roundtrip_bbox_error_mm=bbox_error,
            stock_rule=('Purchasedprofileoperationreference;actualsupplierslots/coresectionisnotmodeledorqualified.Notsolidbillet.'if meta['category']=='Profile envelope operation reference'else
                        'Finished bounding size only; add saw/facing allowance. One-piece angles/integral billets stay one piece. Welded assemblies require the specified constituent stock set.'),
            notes=notes,source=meta['source'],fabrication_release=False))
    (HERE/'current-custom-index.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    report=dict(study='CURRENT_INTEGRATED_CUSTOM_MANUFACTURING_REFERENCES',source_sha256=start,
        source_consistent_during_export=start==snapshot(),part_count=len(rows),all_step_readbacks_passed=all(r['valid']for r in rows),
        output_sha256={r['step']:r['sha256']for r in rows},frame_cutlist=A.M.frame_cutlist(),
        old_poses_reused=False,owned_stock_credit_granted=False,fabrication_release=False)
    # Four new datum blocks can be cut from the already-required NEW stepped
    # hanger blank. This is an explicit new-stock nest, never owned credit.
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    hanger=parts['INT_PAN_FRONT_HEADER_HANGER_L'];b=A.S.bounds(hanger)
    local=hanger.translate(tuple(-v for v in b[:3]));placements=[]
    for i,n in enumerate(sorted(k for k in parts if k.startswith('INT_STOP_DATUM_')and k.endswith('_BLOCK'))):
        u,v=2.,2.+26*i
        blank=cq.Solid.makeBox(6.35,22,22,cq.Vector(0,u,v))
        intersect=blank.intersect(local).Volume()
        d=BRepExtrema_DistShapeShape(blank.wrapped,local.wrapped);d.Perform();distance=d.Value()
        passed=intersect<.0001 and distance>=4-1e-6 and u+22<=158 and v+22<=323.85
        placements.append(dict(id=n,raw_sheet_U_V_mm=[u,v],raw_blank_mm=[22,22,6.35],finished_blank_mm=[20,20,6.35],
            hanger_material_overlap_mm3=intersect,distance_to_finished_hanger_mm=distance,passed=passed))
    assert len(placements)==4 and all(r['passed']for r in placements)
    report['new_hanger_blank_nesting']=dict(parent_material='NEW160x351.85x6.35leftsteppedhangerblank',
        stock_is_owned=False,extra_raw_material_purchase_quantity=0,placements=placements,
        outline_cleanup_allowance_each_edge_mm=1.,separation_mm=4.,passed=True,
        rule='Cutthefour22x22rawblocksfromtheunusedsidebandbeforecuttingthehangeroutline;finish20x20. Do not buyfouradditionalplateblanks. Noowned-stockcreditorsecondhangerblankisclaimed.')
    report['source_consistent_during_export']=start==snapshot()
    report['passed']=report['source_consistent_during_export']and report['all_step_readbacks_passed']
    (HERE/'current-custom-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],custom_parts=len(rows),cuts=len(report['frame_cutlist']))),flush=True)
    return 0 if report['passed']else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
