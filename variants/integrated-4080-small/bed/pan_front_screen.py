"""Actual notched pan-comb beam screen after front bearer removal.

No floor-flange credit in the first model. Conditional T action in the second
requires the specified intact-floor twin welds and end transfer details.
"""
from pathlib import Path
import hashlib,json,math,ast
import numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'output'
E,NU,T,WEB=200000.,.3,1.9,3.175
Y0,Y1,S1,S2=100.,1196.,630.,1180.
SLAT=[130.+1036.*i/7 for i in range(8)]
DRAINS=list(range(140,1166,120))
RHO_G=9.80665e-6 #N/mm3 water
def section(y,width,central=False,composite=False):
 floor=812+.006*(y-100)
 drain=any(p<=y<=p+20 for p in DRAINS)
 slot=any(abs(y-p)<1.1 for p in SLAT)
 bottom=floor+(8. if drain else 0.)
 top=(841. if central else 838.)if slot else 853.
 h=top-bottom;aw=WEB*h;cw=bottom+h/2;iw=WEB*h**3/12
 if not composite or drain:return dict(I=iw,cw=cw,cg=cw,bottom=bottom,top=top,Af=0,Q=0,drain=drain)
 af=width*T;cf=floor-T/2;cg=(af*cf+aw*cw)/(af+aw)
 inertia=iw+aw*(cw-cg)**2+width*T**3/12+af*(cf-cg)**2
 return dict(I=inertia,cw=cw,cg=cg,bottom=floor-T,top=top,Af=af,Q=af*abs(cf-cg),drain=drain)

def model(width,central,composite,depth=62.,supports=(300.,630.,1180.)):
 q=RHO_G*depth*width
 nodes=set(np.arange(Y0,Y1+1,3.).tolist()+[Y0,Y1,*supports])
 for y in SLAT:
  for d in(-1.1,1.1):
   if Y0<y+d<Y1:nodes.add(y+d)
 for y in DRAINS:
  for d in(0,20):
   if Y0<y+d<Y1:nodes.add(y+d)
 x=np.array(sorted(nodes));n=len(x);K=np.zeros((2*n,2*n));F=np.zeros(2*n)
 for i in range(n-1):
  l=x[i+1]-x[i];sec=section((x[i]+x[i+1])/2,width,central,composite)
  k=E*sec['I']/l**3*np.array([[12,6*l,-12,6*l],[6*l,4*l*l,-6*l,2*l*l],[-12,-6*l,12,-6*l],[6*l,2*l*l,-6*l,4*l*l]])
  ids=np.arange(2*i,2*i+4);K[np.ix_(ids,ids)]+=k
  F[ids]+=q*np.array([l/2,l*l/12,l/2,-l*l/12])
 fixed=[2*int(np.argmin(abs(x-s)))for s in supports];free=np.setdiff1d(np.arange(2*n),fixed)
 u=np.zeros(2*n);u[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
 r=K@u-F
 total=q*(Y1-Y0);reactions=[float(-r[j])for j in fixed]
 stresses=[];shear=[];flange=[]
 for y in np.linspace(Y0+.05,Y1-.05,10960):
  sec=section(y,width,central,composite)
  M=-q*(y-Y0)**2/2+sum(rr*(y-ss)for ss,rr in zip(supports,reactions)if y>ss)
  V=-q*(y-Y0)+sum(rr for ss,rr in zip(supports,reactions)if y>ss)
  c=max(abs(sec['top']-sec['cg']),abs(sec['bottom']-sec['cg']))
  stresses.append(abs(M)*c/sec['I'])
  if sec['Af']:
   flow=abs(V)*sec['Q']/sec['I'];shear.append(flow/(2*.707*1.5))
   flange.append(abs(M)*sec['Q']/sec['I'])
 return dict(model='WeldedTwherefootintact;web-onlyat8mmfootdrainnotches'if composite else'Uncompositeactualnotchedwebonly',
  tributary_width_mm=width,central_comb=central,water_depth_bound_mm=depth,uniform_line_load_N_per_mm=q,
  support_Y_mm=list(supports),support_condition='Simple vertical supports; all rotations free, actual front/rear overhangs retained',
  nodes=n,max_abs_rib_deflection_mm=float(max(abs(u[0::2]))),front_rib_deflection_mm=float(u[0]),
  max_web_or_T_extreme_bending_stress_MPa=max(stresses),max_nominal_longitudinal_weld_shear_MPa=max(shear,default=0),
  max_floor_flange_axial_force_N=max(flange,default=0),
  flange_force_transfer_over_10mm_twin_weld_MPa=max(flange,default=0)/(2*.707*1.5*10),
  vertical_reactions_N=reactions,
  reaction_equilibrium_error_N=abs(sum(reactions)-total),
  reaction_moment_equilibrium_error_Nmm=abs(sum(rr*ss for rr,ss in zip(reactions,supports))-total*(Y0+Y1)/2))

def floor_plate(a=435.,b=550.,depth=62.):
 q=RHO_G*depth;D=E*T**3/(12*(1-NU**2));s=sx=sy=0.
 for m in range(1,60,2):
  for n in range(1,60,2):
   den=(m/a)**2+(n/b)**2;factor=(-1)**((m-1)//2+(n-1)//2)/(m*n*den**2)
   s+=factor;sx+=factor*((m/a)**2+NU*(n/b)**2);sy+=factor*(NU*(m/a)**2+(n/b)**2)
 return dict(method='Simply supported rectangular plate Navier series,30x30oddterms atcentre',bay_XY_mm=[a,b],thickness_mm=T,
    water_depth_bound_mm=depth,relative_centre_deflection_mm=16*q*s/(math.pi**6*D),
    centre_bending_stress_MPa=6*16*q*max(sx,sy)/(math.pi**4*T*T),
    support_assumption='Three comb lines, welded frontwall and three crossbearers form supported200/330/550mmYbays. Largest435x550mm considered. Rib movement is added; it is not silently clamped away.')

def run():
 bed_source=HERE/'integrated_bed.py'
 tree=ast.parse(bed_source.read_text(encoding='utf-8'))
 lowering=next(float(n.value.value)for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAN_LOWERING_MM'for t in n.targets))
 rows=[]
 for composite in(False,True):
  for central,width in((False,229.5),(True,435.)):
   rows.append(model(width,central,composite))
 plate=floor_plate();un=max(r['max_abs_rib_deflection_mm']for r in rows if r['model'].startswith('Uncomposite'))
 coupled=max(r['max_abs_rib_deflection_mm']for r in rows if r['model'].startswith('Welded'))
 conditional=coupled+plate['relative_centre_deflection_mm']
 source=ROOT/'variants/extrusion-reengineered/bed.py'
 result=dict(study='PAN_FRONT_COMB_AND_FLOOR_SCREEN_THREE_BEARERS_300_630_1180',source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in[Path(__file__),source,bed_source]},
  pan_rigid_vertical_translation_mm=-lowering,global_floor_front_Z_mm=812-lowering,
  translation_effect='Rigid26mmdownwardtranslationpreservessectiondepths/spans/watercapacity;internalanalysisusesoriginalZonlyasdifferencecoordinates.',
  floor_slope=.006,comb_material='Steel E200GPa;minyield250MParequired',floor_thickness_mm=1.9,comb_thickness_mm=3.175,
  comb_slot_centres_Y_mm=SLAT,comb_slot_width_mm=2.2,outer_slot_bottom_Z_mm=838-lowering,centre_slot_bottom_Z_mm=841-lowering,
  bottom_drain_notches_Y_mm=[[y,y+20]for y in DRAINS],bottom_drain_notch_height_mm=8,
  ribs=rows,floor_plate=plate,
  no_composite_total_displacement_screen_mm=un+plate['relative_centre_deflection_mm'],
  no_composite_2mm_displacement_target_passed=un+plate['relative_centre_deflection_mm']<2.,
  conditional_welded_T_total_displacement_screen_mm=conditional,
  conditional_2mm_displacement_target_passed=conditional<2.,
  required_welding=dict(twin_fillet_leg_mm=1.5,scope='Both sides of every intact comb-to-floor foot, with at least10mm sound run adjacent to each drain notch end. No weld closes a drain notch.',
    process='Continuous/fitted low-distortion thin-sheet weld procedure, verified full fusion/leak test; dimensions are design requirements, not a claim about an existing weld.',
    design_shear_allowance_MPa=100,front_wall_to_floor_weld_required=True,
    note='Tflangecreditrequiresqualifiedfoot/shear/endtransfer. Atdrainnotchesnocompositeflangeiscounted. Floorfrontwallandweldsprovidesupportededge; actualflexiblejoint/warpingnotincluded.'),
  passed_without_composite_credit=un+plate['relative_centre_deflection_mm']<2 and all(r['max_web_or_T_extreme_bending_stress_MPa']<125 for r in rows if r['model'].startswith('Uncomposite')),
  passed_conditional_screen=conditional<2 and all(r['max_web_or_T_extreme_bending_stress_MPa']<125 for r in rows if r['model'].startswith('Welded')),
  full_machine_FEA=False,physical_water_or_thermal_qualification=False,fabrication_release=False,
  limitations=['One-dimensional rib and supported-plate idealizations, not coupled3Dplate/weldFEA','Actual floor waviness,weld distortions,local notch peaks and corrosion excluded','Weld/end-transfer and support contact conditions must be verified before Tcredit','Does not change wood-bed rigidity evidence or claim steel machining'])
 OUT.mkdir(exist_ok=True);(OUT/'pan-front-structure-screen.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(uncomposite_total_mm=result['no_composite_total_displacement_screen_mm'],conditional_T_total_mm=conditional,conditional_pass=result['passed_conditional_screen'],ribs=[dict(type=r['model'],width=r['tributary_width_mm'],deflection=r['max_abs_rib_deflection_mm'],stress=r['max_web_or_T_extreme_bending_stress_MPa'])for r in rows])),flush=True)
 return 0

if __name__=='__main__':raise SystemExit(run())
