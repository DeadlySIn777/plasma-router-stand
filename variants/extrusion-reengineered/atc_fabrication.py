"""Export the actual ATC solids and an explicit, unpriced material schedule.

Profiles are called CUT_PROFILE only when a full-thickness extrusion matches
the designed solid. Other DXFs are visibly named MIDSECTION_REFERENCE. Bought
items never receive fabricated vendor mounting patterns or nominal STEP files.
"""
from pathlib import Path
import copy,csv,hashlib,json,os,sys
import cadquery as cq
import ezdxf
import params as P
import atc as A

HERE=Path(__file__).resolve().parent
OUT=HERE/'review';STEPS=OUT/'atc-parts';DXFS=OUT/'atc-dxf'
TOL=.05

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bb(s):
    b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def size(s):
    b=bb(s);return [b[i+3]-b[i] for i in range(3)]
def normalized(s):
    b=bb(s);return s.translate(tuple(-v for v in b[:3])),b[:3]
def clip(s,axis,lo,hi):
    b=bb(s);p=[v-1 for v in b[:3]];d=[b[i+3]-b[i]+2 for i in range(3)]
    p[axis]=lo;d[axis]=hi-lo
    return s.intersect(A.box(*p,*d)).clean()
def difference_volume(a,b):return a.cut(b).Volume()+b.cut(a).Volume()

def recorded_model():
    """Retain pre-weld child shapes without changing atc.py or its cache."""
    original=A.Model;initial={}
    class Recorder(original):
        def add(self,*args,**kwargs):
            p=super().add(*args,**kwargs);initial[p.id]=copy.copy(p);return p
    A.Model=Recorder
    try:model,classes=A._build(200.,0.,False)
    finally:A.Model=original
    return model,classes,initial

def weld_members(model,initial):
    final={p.id for p in model.parts};members={}
    for name,raw in initial.items():
        if name in final or raw.purchased:continue
        rb=bb(raw.shape);v=raw.shape.Volume();matches=[]
        for p in model.parts:
            if p.purchased or p.id.startswith('ATC_MOVING_WING_'):continue
            pb=bb(p.shape)
            if not all(rb[i]>=pb[i]-1e-4 and rb[i+3]<=pb[i+3]+1e-4 for i in range(3)):continue
            common=raw.shape.intersect(p.shape).Volume()
            if common>v*.95:matches.append((common/v,p.id))
        if matches:
            target=max(matches)[1];members.setdefault(target,[]).append(name)
    return members

def decomposition(p,initial,members):
    """Disjoint butt-weld constituent solids, always checked against assembly.

    The plane cuts below only define welding fit-up; no bend allowance, kerf
    or supplier geometry is inferred. RHS remains RHS stock, not solid bar.
    """
    n=p.id;s=p.shape;b=bb(s);out=[]
    def part(label,q,stock='plate',note=''):
        if q.Volume()>TOL:out.append((n+'__'+label,q.clean(),stock,note))
    if n in members:
        used=None
        for raw in [n]+members[n]:
            q=initial[raw].shape.intersect(s)
            if used is not None:q=q.cut(used)
            if q.Volume()>TOL:
                part(raw.removeprefix('ATC_'),q,'plate' if raw not in ('ATC_STOP_PARK',) else 'billet',
                  'Weld constituent; finish the assembly holes/rail datum after fit-up. No overlapping stock credit.')
                used=q if used is None else used.fuse(q)
        if used is not None:
            remainder=s.cut(used)
            if remainder.Volume()>TOL:part('ASSEMBLY_FINISH_REMAINDER',remainder,'billet','Actual residual solid; inspect decomposition before fabrication.')
    elif n.startswith('ATC_REAR_CRADLE_'):
        # The leg is trimmed below the6.35 floor for a real butt joint.
        zfloor=b[2]+19.65;ztop=zfloor+6.35
        part('LEG',clip(s,2,b[2],zfloor),'plate','6.35 plate; butt to floor underside, two frame clearance holes.')
        part('FLOOR',clip(s,2,zfloor,ztop),'plate','6.35 plate; square butt joints, no overlapping plate credit.')
        part('UPRIGHT',clip(s,2,ztop,b[5]),'plate','4 mm plate; butt to floor and steel backbar.')
    elif n.startswith('ATC_HOOD_STAND_'):
        y=b[1]+6.35
        part('FRAME_PLATE',clip(s,1,b[1],y),'plate','6.35 plate; source STEP retains frame holes and RHS-access cutout.')
        rhs=clip(s,1,y,b[4]);r=bb(rhs);joint=r[2]+25.4
        part('CANTILEVER_RHS',clip(rhs,2,r[2],joint),'RHS25p4x25p4x1p6','25.4 square steel RHS,1.6 nominal wall. Finish access cut after fit-up.')
        part('UPRIGHT_RHS',clip(rhs,2,joint,r[5]),'RHS25p4x25p4x1p6','25.4 square steel RHS,1.6 wall; butt to cantilever top. Weld3 mm fillets per assembly notes.')
    elif n=='ATC_MOTOR_WELDED_MOUNT':
        y=b[4]-(b[3]-b[0])
        part('MOTOR_PLATE',clip(s,1,y,b[4]),'plate','6.35 plate; pilot, clearance holes and tapped standoff holes are defined by STEP.')
        tab=clip(s,1,b[1],y);thickness=min(size(tab))
        part('BACKBAR_TAB',tab,'plate',f'{thickness:.3f} mm plate; '+('standard 1/8 inch stock; 'if abs(thickness-3.175)<1e-4 else'')+'butt-weld to motor plate and current backbar.')
    elif n.startswith(('ATC_LOCK_','ATC_R_LOCK_')) and n.endswith('_FLAG'):
        tab=clip(s,1,b[1],b[1]+2.)
        part('PUSH_RETURN_TAB',tab,'plate','2 mm plain steel return tab; centre the2 mm flag body on the4 mm return height and butt-weld the end. No overlapping sheet stock.')
        part('FLAG_BODY',s.cut(tab),'plate','2 mm plain steel opaque flag; contour and through bores from profile. Weld the separate return tab, then verify full pin stroke under actual load.')
    elif n=='ATC_DRIVE_STEEL_CASE':
        # Open-bottom case, four walls butt to roof. Front is faced from1.9 to1.85.
        roof=clip(s,2,b[5]-1.9,b[5]);walls=clip(s,2,b[2],b[5]-1.9)
        part('ROOF',roof,'plate','1.9 plain sheet, two through roof screws.')
        for label,axis,lo,hi in [('LEFT',0,b[0],b[0]+1.9),('RIGHT',0,b[3]-1.9,b[3])]:
            q=clip(walls,axis,lo,hi);part(label,q,'plate','1.9 plain sheet; butt-weld case.')
            walls=walls.cut(q)
        for label,lo,hi in [('REAR',b[4]-1.9,b[4]),('FRONT',b[1],b[1]+1.85)]:
            q=clip(walls,1,lo,hi);part(label,q,'plate','Front finished1.85 from nominal1.9 sheet; other walls1.9. Keep cutouts open.')
            walls=walls.cut(q)
        if walls.Volume()>TOL:part('REMAINDER',walls,'plate','Inspect case fit-up; no hidden free stock.')
    if not out:return []
    # Split stockU guides into3 welded straight strips, no invented brake radius.
    expanded=[]
    for label,q,stock,note in out:
        if label.endswith(('__GATE_GUIDE_R','__GATE_GUIDE_L')):
            expanded.extend(channel_strips(label,q,note))
        else:expanded.append((label,q,stock,note))
    return expanded

def channel_strips(n,s,note=''):
    b=bb(s);front=clip(s,1,b[1],b[1]+1.9);rear=clip(s,1,b[4]-1.9,b[4]);web=s.cut(front).cut(rear)
    return [(n+'__FRONT_FLANGE',front,'plate',note+' Welded1.9 straight-strip channel.'),
      (n+'__REAR_FLANGE',rear,'plate',note+' Welded1.9 straight-strip channel.'),
      (n+'__WEB',web,'plate',note+' Welded1.9 straight-strip channel; butt between flanges.')]

def section_frame(s,axis):
    local,origin=normalized(s)
    if axis==0:local=local.rotate((0,0,0),(0,1,0),90)
    elif axis==1:local=local.rotate((0,0,0),(1,0,0),90)
    local,shift=normalized(local)
    R=({0:((0,0,1),(0,1,0),(-1,0,0)),1:((1,0,0),(0,0,-1),(0,1,0)),
        2:((1,0,0),(0,1,0),(0,0,1))})[axis]
    transform=[list(row)+[-sum(row[j]*origin[j]for j in range(3))-shift[i]]for i,row in enumerate(R)]
    transform.append([0,0,0,1])
    return local,{'original_world_origin_mm':origin,'thickness_axis_world':'XYZ'[axis],
      'world_to_profile_frame_4x4':transform,'DXF_discards_profile_Z_mm':size(local)[2]/2,
      'orientation':'Rotate local+Y90 for X thickness; local+X90 for Y thickness; Z unchanged; then normalize bounding-box minimum.'}

def export_solid(n,s,material,stock,note,asset_hashes):
    local,origin=normalized(s);dims=size(s);step=STEPS/(n+'.step')
    cq.exporters.export(local,str(step));back=cq.importers.importStep(str(step)).val()
    verr=abs(back.Volume()-local.Volume());berr=max(abs(a-b) for a,b in zip(bb(back),bb(local)))
    step_ok=back.isValid() and len(back.Solids())==len(local.Solids()) and verr<max(.01,local.Volume()*1e-7) and berr<1e-5
    axis=min(range(3),key=lambda i:dims[i]);sf,transform=section_frame(s,axis);t=size(sf)[2]
    section=cq.Workplane('XY').newObject([sf]).section(t/2)
    profile=section.val();isflat=False;diff=None
    if profile and profile.Edges():
        try:
            rebuilt=section.wires().toPending().extrude(t,combine=False).val()
            rebuilt,_=normalized(rebuilt)
            diff=difference_volume(rebuilt,sf);isflat=stock=='plate' and diff<TOL
        except Exception as e:
            diff=None
    suffix='CUT_PROFILE' if isflat else'MIDSECTION_REFERENCE'
    dxf=DXFS/(n+'_'+suffix+'.dxf')
    cq.exporters.export(section,str(dxf));doc=ezdxf.readfile(dxf);doc.units=4;doc.header['$INSUNITS']=4;doc.saveas(dxf)
    dxf_ok=doc.units==4 and not doc.audit().has_errors and len(doc.modelspace())>0
    rt=None;rdiff=None
    if isflat:
        imp=cq.importers.importDXF(str(dxf)).wires().toPending().extrude(t).val()
        rt=abs(imp.Volume()-sf.Volume());imp,_=normalized(imp)
        rdiff=difference_volume(imp,sf)
        dxf_ok=dxf_ok and imp.isValid() and rt<max(TOL,sf.Volume()*1e-6) and rdiff<TOL
    for f in(step,dxf):asset_hashes[f.relative_to(HERE).as_posix()]=sha(f)
    return {'id':n,'material':material,'stock_type':stock,'notes':note,'quantity':1,
      'world_origin_mm':origin,'finished_world_aligned_size_mm':dims,'finished_volume_mm3':s.Volume(),
      'step':step.relative_to(HERE).as_posix(),'step_roundtrip_passed':step_ok,
      'source_solid_count':len(s.Solids()),'step_roundtrip_solid_count':len(back.Solids()),
      'step_roundtrip_volume_error_mm3':verr,'step_roundtrip_bbox_error_mm':berr,
      'dxf':dxf.relative_to(HERE).as_posix(),'dxf_role':suffix,'dxf_passed':dxf_ok,
      'profile_uniform_extrusion_sym_difference_mm3':diff,'dxf_roundtrip_volume_error_mm3':rt,
      'dxf_roundtrip_sym_difference_mm3':rdiff,
      'profile_thickness_mm':t,'profile_size_mm':size(sf)[:2],'section_transform':transform}

def interface_rows():
    # Procurement requirements: quantities are explicit, dimensions still selected
    # against actual valve/cylinder/controller drawings. Owned valves are not credited.
    return [
      ('RAPIDCHANGE_MAGAZINE_KIT',1,'Supplier kit','Exact magazine/endcaps, dust covers, electronics and accessories; approved dimensions/mounting/pocket/nut datums required. No invented mount DXF.'),
      ('TOOLHOLDER_NUT_COLLET_SET',1,'Supplier-specific matched set','Quantity equals final selected magazine pockets; one procurement set, not one assumed pocket. Cutting tools extra as selected.'),
      ('ATC_AIR_3_2_NC_VALVE',2,'3/2 spring-return, normally closed','One circuit per endpoint pair, fail-to-engage external pin springs. Select actual coil voltage/current, flow, seals and ports.'),
      ('ATC_FLOW_CONTROL',4,'Cylinder-compatible meter-out controls','One per cylinder; confirm single-acting return and available pressure-release path.'),
      ('ATC_FILTER_REGULATOR_GAUGE',1,'Filter/regulator/gauge assembly','Set nominal0.5 MPa only after actual cylinder and supply ratings verified.'),
      ('ATC_AIR_ISOLATOR_DUMP',1,'Lockable manual shutoff and downstream dump','Accessible isolation/bleed for maintenance; do not assume existing compressor isolator serves this branch.'),
      ('ATC_PNEUMATIC_TUBE',10,'metres of compatible air tubing','Cut allowance; final OD/ID and flex radius selected to cylinder/valve fittings. Route and measure before cutting.'),
      ('ATC_CYLINDER_PORT_FITTINGS',4,'Actual SMC revision port fittings','Do not guess small port threads from nominal cylinder body.'),
      ('ATC_PNEUMATIC_TEE',2,'Compatible tube tees','Split each endpoint circuit to two cylinders.'),
      ('ATC_VALVE_SUPPLY_OUTPUT_FITTINGS',4,'Valve-specific fittings','Two supply and two output connections across two valves.'),
      ('ATC_VALVE_EXHAUST_SILENCER',2,'Valve-specific exhaust silencers','One per3/2 valve; keep exhaust release unrestricted.'),
      ('ATC_REGULATOR_ISOLATOR_ADAPTER_SET',1,'Actual thread/tube adapter set','Complete supply/regulator/isolator connection set, including verified hose to owned compressor.'),
      ('ATC_24V_ISOLATED_IO_INTERFACE',1,'Controller-compatible interface set','At least12 sensor inputs (10 proximity+2 gate),2 valve outputs, step/dir motor channel, manufacturer kit IR/nut interfaces and safe spindle reverse/speed. Exact board/firmware unverified.'),
      ('ATC_MOTOR_DRIVER_CHANNEL',1,'1.5A nominal motor-compatible channel','Available integrated driver may satisfy only after controller voltage/current/firmware verification; no ownership credit yet.'),
      ('ATC_AUXILIARY_24V_POWER_INTERFACE',1,'Protected24V power distribution/supply allowance','Size actual sensor/valve/kit demand; existing machine supply may serve only after verified capacity, isolation and protection. No unverified ownership credit.'),
      ('ATC_SENSOR_MOTOR_VALVE_CABLE_SET',1,'Shielded cables/connectors/flex protection','All12 sensors, motor,2 valves and kit interfaces. Physical cable lengths, strain relief and rear flex loop must be measured; one complete procurement set.'),
      ('ATC_GATE_PIN_TETHER',1,'Retained chain/tether','Secure6mm manual index pin to fixed keeper.'),
      ('ATC_FRAME_M6_SLOT_NUTS',12,'Actual40-series M6 slot nuts','8 guide/cradle+4 independent hood-support frame attachments. Match profile groove and safe insertion/engagement.'),
      ('ATC_WELD_FINISH_CONSUMABLES',1,'Qualified weld/coating consumables','No free offcut credit; keep precision rail seats clean and re-inspect after welding.'),
      ('ATC_BELT_CABLE_RESTRAINT_SET',1,'Retainers/strain-relief set','Belt safe-end retention and fixed/continuous cable guides; exact selected interfaces conditional.')]

def run():
    for d in(STEPS,DXFS):d.mkdir(parents=True,exist_ok=True)
    source_names=['params.py','atc.py','motion.py','atc_fabrication.py']
    for module_name in ('cad_helpers',A.guide_source.__name__):
        path=Path(sys.modules[module_name].__file__).resolve()
        source_names.append(Path(os.path.relpath(path,HERE)).as_posix())
    sources={n:sha(HERE/n) for n in source_names}
    model,classes,initial=recorded_model();members=weld_members(model,initial)
    assets={};custom=[];assemblies=[];bom=[];steel=[];note_corrections=[]
    for p in model.parts:
        d=size(p.shape);notes=' | '.join(p.notes);material=p.material
        if p.id in ('ATC_MOVING_WING_L','ATC_MOVING_WING_R'):
            material='6061 aluminum billet; NEW1x3x6in raw blank (25.4x76.2x152.4mm)'
            notes+=' The6.35mm dimension describes the straight wing rib only. Machine the complete integral wing/dogleg from one new billet; finished envelope19.875x63.5x130.8mm. No owned-sheet credit.'
            note_corrections.append({'id':p.id,'source_material_label':p.material,
              'manufacturing_material':material,'reason':'The final fused integral wing/dogleg is19.875mm thick;6.35mm plate cannot contain it.'})
        if p.id.startswith('ATC_LOCATOR_RISER_') and p.id.rsplit('_',1)[-1] in ('325','825'):
            x=p.id.rsplit('_',1)[-1]
            screws=[q for q in model.parts if q.id.startswith('ATC_LOCATOR_RISER_M4x12_'+x+'_')]
            if screws:
                engagement=min(bb(q.shape)[5]-bb(p.shape)[2]for q in screws)
                old=notes;notes=notes.replace('5.65mm',f'{engagement:.2f}mm')
                notes+=' Recessed M4 head is flush with lowerU underside; actual screw-tip/riser-base engagement derived from CAD.'
                note_corrections.append({'id':p.id,'source_note':old,'manufacturing_note':notes,
                  'CAD_derived_engagement_mm':engagement,'reason':'Frozen geometry is current; the inherited5.65mm engagement text predates4mm head recess.'})
        if p.id.startswith('ATC_MGNR12_'):
            notes+=' Procurement:350 mm nominal rail stock, finish335 mm by trimming15 mm at source front; verify retained hole coordinates before cutting. Two MGN12H blocks per rail are separate listed rows.'
        bom.append({'id':p.id,'part_number':p.part_number,'quantity':1,'category':'PURCHASED_NOMINAL' if p.purchased else'CUSTOM_ASSEMBLY_OR_PART',
          'material_or_spec':material,'owned':False,'procure':bool(p.purchased),'supplier_interface_verified':False,
          'finished_size_mm':' x '.join(f'{v:.4f}'for v in d),'stock_type':'purchased' if p.purchased else'custom',
          'notes':notes,'artifacts':''})
        if p.purchased:continue
        pieces=decomposition(p,initial,members)
        if p.id=='ATC_GATE_GUIDE_L':pieces=channel_strips(p.id,p.shape)
        if p.id.startswith('ATC_MOVING_RHS_'):stock='RHS25p4x50p8x3p175'
        elif p.id=='ATC_HOOD_SUPPORT_RHS':stock='RHS25p4x25p4x1p6'
        elif 'Acetal'in material:stock='round_stock'
        elif 'billet'in material.lower():stock='billet'
        elif p.id.endswith(('_PIN','_ROUND','_DIAMOND')):stock='round_stock'
        else:stock='plate'
        row=export_solid(p.id,p.shape,material,stock,notes,assets);custom.append(row)
        if material!=p.material:
            row['source_material_label']=p.material
            row['minimum_selected_raw_stock_mm']=[25.4,76.2,152.4]
            row['selected_raw_stock_in_world_axis_order_mm']=[25.4,152.4,76.2]
            assert all(a>=b for a,b in zip(row['selected_raw_stock_in_world_axis_order_mm'],d))
        bom[-1]['artifacts']=row['step']+' | '+row['dxf']
        if pieces:
            union=pieces[0][1]
            for _,s,_,_ in pieces[1:]:union=union.fuse(s)
            diff=difference_volume(union,p.shape)
            pairvol=sum(a[1].intersect(b[1]).Volume() for i,a in enumerate(pieces)for b in pieces[i+1:])
            assemblies.append({'id':p.id,'constituents':[q[0]for q in pieces],
              'union_sym_difference_mm3':diff,'overlap_mm3':pairvol,'passed':diff<TOL and pairvol<TOL,
              'note':'Assembly STEP is reference, constituent stock rows are additive; do not purchase assembly envelope again.'})
        else:pieces=[(p.id,p.shape,stock,notes)]
        for n,s,st,note in pieces:
            if n!=p.id:
                rr=export_solid(n,s,material,st,note,assets);custom.append(rr)
            else:rr=row
            rawdims=size(s);isflat=rr['dxf_role']=='CUT_PROFILE'
            # Nominal1.9 sheet may be finish-faced to the case-front1.85.
            thick=rr['profile_thickness_mm']
            rawt=1.9 if any(abs(thick-q)<1e-4 for q in (1.8,1.85)) else thick
            blank=rr['profile_size_mm']+[rawt]
            bom.append({'id':n,'part_number':n,'quantity':1,'category':'STOCK_FOR_CUSTOM_PART','material_or_spec':material,
              'owned':False,'procure':True,'supplier_interface_verified':False,
              'finished_size_mm':' x '.join(f'{v:.4f}'for v in rawdims),'stock_type':st,
              'notes':note+' Finished envelope only; add saw/facing allowances. No owned aluminum/offcut credit. '+('Finish to shown1.80/1.85 from nominal1.90 sheet where applicable. 'if rawt!=thick else'')+('Use CUT_PROFILE plus STEP; nominal threaded bores require separate tap-drill/thread operations, not profile cutting to major diameter.'if isflat else'Use STEP for all features; MIDSECTION_REFERENCE is not a cutting template.'),
              'artifacts':rr['step']+' | '+rr['dxf']})
            if not any(k in material.lower() for k in ('aluminum','6061','acetal')) and st=='plate':
                steel.append({'id':n,'quantity':1,'flat_length_mm':blank[0],'flat_width_mm':blank[1],
                  'thickness_mm':blank[2],'material':'plain_low_carbon_steel','profile_bound':isflat,
                  'source_step':rr['step'],'note':note+' Add cutting/facing allowance; retain nominal1.9 sheet where front is faced1.85.'})
        print('ATC_EXPORT',p.id,flush=True)
    for n,q,mat,note in interface_rows():
        bom.append({'id':n,'part_number':'UNSELECTED','quantity':q,'category':'UNMODELED_SUPPLIER_INTERFACE_REQUIREMENT','material_or_spec':mat,
          'owned':False,'procure':True,'supplier_interface_verified':False,'finished_size_mm':'','stock_type':'interface_set',
          'notes':note,'artifacts':''})
    csvpath=OUT/'atc-fabrication.csv'
    with csvpath.open('w',newline='',encoding='utf-8')as f:
        w=csv.DictWriter(f,fieldnames=list(bom[0]));w.writeheader();w.writerows(bom)
    assets[csvpath.relative_to(HERE).as_posix()]=sha(csvpath)
    # Remove only obsolete artifacts in the two generator-owned directories.
    # This keeps stale reference/cut-profile alternatives out of the handoff.
    for directory,extension in ((STEPS,'.step'),(DXFS,'.dxf')):
        root=directory.resolve()
        for path in directory.glob('*'+extension):
            assert path.resolve().parent==root
            if path.relative_to(HERE).as_posix() not in assets:path.unlink()
    unchanged=sources=={n:sha(HERE/n)for n in source_names}
    result={'revision':P.REVISION,'release':False,'prices_included':False,'source_sha256':sources,
      'source_unchanged':unchanged,'output_sha256':assets,'custom_exports':custom,'assembly_decomposition':assemblies,
      'steel_blanks':steel,'procurement_rows':len(bom),'modeled_component_count':len(model.parts),
      'purchased_envelope_count':sum(p.purchased for p in model.parts),'custom_assembly_count':sum(not p.purchased for p in model.parts),
      'custom_step_count':len(custom),'cut_profile_count':sum(r['dxf_role']=='CUT_PROFILE'for r in custom),
      'midsection_reference_count':sum(r['dxf_role']=='MIDSECTION_REFERENCE'for r in custom),
      'unclassified_decomposition_remainders':[r['id']for r in custom if 'REMAINDER'in r['id']],
      'source_note_normalizations':note_corrections,
      'interface_requirements':[dict(id=n,quantity=q,spec=mat,notes=note,owned=False,selected=False)for n,q,mat,note in interface_rows()],
      'runtime_interface_metadata':A.interface_metadata(),
      'limits':['All ATC stock/hardware unowned unless independently verified. No pricing or vendor hole templates.',
        'Full custom STEP files bind the actual current shape; uniform-profile DXFs only are manufacturing contours. Reference sections omit other-axis features and blind operations.',
        'Welded cradles, hood/drive-case/gate/guide constituents and RHS cuts are explicit. Stock rows are additive; assembly/reference rows are nonadditive.',
        'Bore cylinders in nominal-thread STEP geometry are not tap drills. Actual vendor fits, strengths, welds, thermal limits, controls and operating trials remain qualified separately.',
        'Steel blanks are finished rectangular envelopes, not a claimed combined sheet nest. No offcuts are credited.']}
    result['passed']=unchanged and not result['unclassified_decomposition_remainders'] and all(r['step_roundtrip_passed'] and r['dxf_passed']for r in custom)and all(r['passed']for r in assemblies)
    (OUT/'atc-manufacturing.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k]for k in ('passed','source_unchanged','modeled_component_count','custom_assembly_count','purchased_envelope_count','procurement_rows')},indent=2),flush=True)
    return 0 if result['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
