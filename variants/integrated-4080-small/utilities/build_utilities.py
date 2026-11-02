"""Export and screen the new utility material against current integrated sources."""
from pathlib import Path
import csv,hashlib,json,math,os,sys
import cadquery as cq
import integrated_utilities as U
HERE=Path(__file__).resolve().parent;OUT=HERE/'output';ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent));import mechanical as M
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def overlap(a,b):return all(a[k]<b[k+3]-1e-5 and b[k]<a[k+3]-1e-5 for k in range(3))
def clashes(parts,obstacles):
 hits=[];obs=[(n,s,U.bb(s))for n,s,*_ in obstacles]
 for n,s,*_ in parts:
  a=U.bb(s)
  for m,t,b in obs:
   if not overlap(a,b):continue
   v=s.intersect(t).Volume()
   if v>.01:hits.append(dict(utility=n,other=m,volume_mm3=round(v,6)))
 return hits
def run():
 OUT.mkdir(exist_ok=True);custom=OUT/'custom-step';custom.mkdir(exist_ok=True)
 p=U.utility_parts();new=[x for x in p if x[0].startswith('U_')]
 src=[Path(U.__file__),Path(U.B.__file__),Path(M.__file__),Path(U.O.__file__),Path(U.SH.__file__)]
 report=dict(metadata=U.metadata(),source_sha256={str(x.relative_to(ROOT)):sha(x)for x in src},
  component_count=len(p),new_component_count=len(new),invalid=[n for n,s,c in p if not s.isValid()or not s.Solids()or s.Volume()<=0],checks={},holds=[])
 # Most old pan contacts are existing welds/keepers. Check new material against
 # all frozen wet parts as well as the actual root frame/common motion.
 for mode,angle in(('WOOD',0.),('PLASMA',90.)):
  fixed=M.frame_parts()+M.motion_parts(mode=='PLASMA',1275.,575.,250.)
  bed=[(x['id'],x['shape'],x['color'])for x in U.B.bed_parts(angle)]
  report['checks'][mode]=dict(new_vs_frame_motion=clashes(new,fixed),new_vs_bed=clashes(new,bed),
       new_vs_retained_wet=clashes(new,U.retained_wet_parts()))
  print(mode,'checked',flush=True)
 # Exact source poses are a diagnostic; a continuous check needs enclosures.
 # Bound each 0.5deg assist interval by a generous full-shape coordinate
 # box plus radius*dtheta. The drain/guard gap is then proved or held.
 moving=[x for x in U.utility_parts(guards_fitted=False)if x[0].startswith('U_')]
 check=[]
 for a in range(0,91,5):
  bed=[(x['id'],x['shape'],x['color'])for x in U.B.bed_parts(a)if x['moving_bed']or x['id'].startswith(('BED_GAS_','BED_CAPTURE_'))]
  h=clashes(moving,bed)
  if h:check.extend(dict(angle_deg=a,**v)for v in h)
 report['checks']['BED_TRANSITION_5_DEG_DIAGNOSTIC']=check
 report['transition_is_continuously_proved']=False
 report['holds']=[
 'Exact received motorized valve threads, permitted mounting orientation, union lengths and independent pipe/actuator support require verification. Rounded supplier dimensions are conservative package allocations, not exact solids.',
 'Receiver usable volume at least65L, wall/bulkhead support, liquid rating and hot-return temperature remain physical acceptance items; reservoir is vented and never pressurized.',
 'All six screen sections must be transferred to the under-pan racks before bed tilt and refitted before cutting. The9stagehandlingroute requires actual-source finite/continuous checks before conversion release.',
 'Guide screens are spatter/dust barriers, not a sealed extraction enclosure or tested thermal barrier. Rail block shoes prevent a continuous fixed wall atX44throughrailheight.',
 'Valve NC power-off return requires at least60s energized charging per manufacturer. Drain closure, receiver-present/level and mode interlocks require actual controller I/O qualification.',
 'New formed/welded screen parts require developed bend/weld fabrication drawings and actual slot fastener fit/engagement; the nominal solids are not final sheet flat patterns.']
 index=[]
 changed_keepers=[x for x in U.pan_retainers()if any(t in x[0]for t in('_ML','_MR'))]
 for n,s,c in new+changed_keepers:
  if any(t in n for t in('M6x20','WELDNUT','VALVE_'))or(n.startswith('U_')and any(t in n for t in('M4_','M6_'))):continue
  path=custom/(n+'.step');cq.exporters.export(s,str(path))
  back=cq.importers.importStep(str(path)).val();assert back.isValid()and abs(back.Volume()-s.Volume())<.1
  index.append(dict(id=n,file=path.relative_to(HERE).as_posix(),sha256=sha(path),bounds_mm=U.bb(s)))
 (OUT/'custom-part-index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
 rows=[dict(id='U_NEW_1P9_STEEL_GUIDE_STOCK',quantity=6,unit='screens',specification='472x94.3x1.9mmsteel vertical screen, one welded offsetclip each; 2mmseams; exact finishedSTEPbounds control; sheetdevelopmentsunissued.',ownership='new',procure=True),
 dict(id='U_NEW_GUIDE_CLIP_STOCK',quantity=6,unit='clips',specification='1.9mmsteel formed/welded detachable-with-screen cantileverclips; exactsupplierfitsheld.',ownership='new',procure=True),
 dict(id='U_GUIDE_FRAME_M6_SETS',quantity=12,unit='sets',specification='M6x12retainedframe/rackscrews with actual4080slot nuts; externalgrip1.9mmshown inframe; actualnutprojectionheld.',ownership='new',procure=True),
 dict(id='U_GUIDE_RACK_STOCK',quantity=2,unit='racks',specification='New1.9steel channelweb160x656.5, two18.1returns,40x40anchorflange and three72.3x40ledges each. WeldedfinishedSTEPcontrolsnominalgeometry.',ownership='new',procure=True),
 dict(id='U_GUIDE_RACK_M6_NUTS',quantity=12,unit='nuts',specification='M6steelnuts weldedtoactualrackbores,5mmthickallocation.',ownership='new',procure=True),
 dict(id='U_GUIDE_RACK_ANCHOR_SETS',quantity=4,unit='sets',specification='M6anchorboltandactualslotnuttofrontpanbeamundersideY300; externalsheetgrip1.9mmshown.',ownership='new',procure=True),
 dict(id='USS_MSV00009',quantity=1,unit='valve',specification='1inNPTstainlessfullport9–24VAC/DC2wireauto-returnNC; supplierdimensions3.2×3×4.3in; unit$50.42shippingunquoted.',ownership='new',procure=True),
 dict(id='U_DRAIN_PIPE_AND_UNIONS',quantity=1,unit='lot',specification='OD28ID24weldedfront/downrouting; received1inNPTvalveunions andindependentpipeclamps required; no direct borrowedsolenoidcredit.',ownership='new',procure=True),
 dict(id='U_DRAIN_25ID_HOSE',quantity=2.,unit='metres allocation',specification='25IDflexhoseOD34,maxminimumcenterlinebend100mm; finalfittingsandlengthmeasureaftervalveacceptance.',ownership='new',procure=True),
 dict(id='U_FRONT_PAN_SHIM_PACKS',quantity=3,unit='packs',specification='25x20fitpacks atY300; bottom806.5,top811.3nominal, slopeactualpan. Newmaterial.',ownership='new',procure=True),
 dict(id='U_PAN_KEEPER_STATION_CHANGE',quantity=2,unit='stations',specification='Frontkeeperpairrelocated530mmrear tobearer630; bossesheight18.18,shouldercap/weldear/bolt+3.18Z; customearmanufacturingincludedinpanstock.',ownership='new',procure=False),
 dict(id='U_RETAINED_WET_BASE',quantity=1,unit='assembly',specification='Retainedsteelpan/slats/combsoverflow,tote/lid/hatchandthermalroof; entirelyincludeinthewholemachineBOM, notfreeorownedbythisreference.',ownership='unproven',procure=False)]
 with(OUT/'utility-takeoff.csv').open('w',newline='',encoding='utf-8')as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 assembly=cq.Assembly(name='INTEGRATED_UTILITIES')
 for n,s,c in p:assembly.add(s,name=n,color=cq.Color(*c))
 assembly.save(str(OUT/'INTEGRATED_UTILITIES.step'))
 report['passed_static_geometry']=not report['invalid']and all(not h for k,v in report['checks'].items()if isinstance(v,dict)for h in v.values())and not check
 report['fabrication_release']=False;report['operating_release']=False
 (OUT/'utility-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print('utilities exported; static',report['passed_static_geometry'],flush=True)
 for k,v in report['checks'].items():
  if isinstance(v,dict):print(k,{x:len(y)for x,y in v.items()},flush=True)
  elif v:print(k,len(v),v[:12],flush=True)
 sys.stdout.flush();os._exit(0 if report['passed_static_geometry']else 2)
if __name__=='__main__':run()
