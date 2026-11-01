"""Final six-leg frame member calculations. N and mm. Independent of live machine."""
from pathlib import Path
import importlib.util,json,math
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('b',H.parents[1]/'budget-hybrid-600'/'simulation'/'structure.py')
b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
E=200000.
Y=(100.,600.,1100.)
RAIL_L=1450.
rows=[]
for t in(1.5,1.9,2.1):
    I=b.tube_i(t,50.8)
    single=[]
    paired=[]
    for y in (185.,275.,350.,600.,850.,1000.,1100.,1185.,1275.,1365.,1450.):
        s=b.beam((0.,*Y,RAIL_L),{p:0. for p in Y},E*I,point=(y,100.))
        single.append({'load_y_mm':y,'force_N':100.,'maximum_anywhere_mm':float(s['max_abs_mm']),
                      'loadpoint_mm':float(s['nodal_mm'][y])})
    for center in(275.,600.,775.,1000.,1275.):
        points=[(center-90.,50.),(center+90.,50.)]
        s=b.beam((0.,*Y,RAIL_L),{p:0. for p in Y},E*I,points=points)
        paired.append({'guide_midpoint_Y_mm':center,'force_per_block_N':50.,
                       'maximum_anywhere_mm':float(s['max_abs_mm']),
                       'guide_mean_displacement_mm':float(sum(s['nodal_mm'][p] for p,F in points)/2)})
    rows.append({'wall_mm':t,'rounded_I_mm4':I,'single100N':single,'two_guide_blocks100N_total':paired})
brace=[]
for bay,height in((500.,625.),(1083.2,480.)):
    L=math.hypot(bay,height);horizontal=bay/L;A=19.05*3.175
    T=100/horizontal;extension=T*L/(E*A)
    brace.append({'bay_mm':bay,'height_mm':height,'active_tension_N':T,
                  'ideal_axial_drift_mm':extension/horizontal,
                  'drift_if_total_anchor_motion0p1mm':extension/horizontal+.1/horizontal,
                  'drift_if_total_anchor_motion0p3mm':extension/horizontal+.3/horizontal})
# Actual pan cells supported along edge members, central backbone and three bearer lines.
def plate_w(a,bb,t,head):
    D=E*t**3/(12*(1-.3**2));p=1000*9.80665*(head/1000)/1e6
    return 16*p/(math.pi**6*D)*sum((-1)**((m-1)//2+(n-1)//2)/(m*n*((m/a)**2+(n/bb)**2)**2)
                   for m in range(1,62,2) for n in range(1,62,2))
plate=[{'sheet_mm':t,'head_mm':head,'cell420x500_mm':plate_w(420,500,t,head)}
       for t in(1.52,1.8974,2.6568) for head in(20.,26.,35.)]
out={'scope':'Final member sensitivities for stationary table only. Whole-machine stiffness remains a measured property.',
     'N_mm_MPa':True,'actual_upper_rail_support_y_mm':Y,'upper_rail_overhangs_mm':[100.,350.],
     'leg_length_mm':793.6375,'member_results':rows,'racking':brace,'pan_cells':plate,
     'attachment_requirements':['Rail guides transfer-drilled through the actual RHS with internal mechanically captured nuts/backers. A bare tube face requires flattening/shimming after welding.',
         'The twelve brace straps have different steel post widths at their ends. All modeled contacts and actual weld preparations must avoid unsupported gaps. A steel spacer or a formed end must carry the load at each small post.',
         'Permanent slats must be attached to combs against uplift, and dry clamps must be present at four points per pad.',
         'Welded foot tubes bear through full bearing caps and floor plates; level with trapped steel shims and confirm contact at all six feet.'],
     'limitations':['Vertical support elevations are prescribed; floor rocking, local joint movement and heat distortion are outside these member solves.',
                    'Single100N atY1450 is a deliberate end-load sensitivity beyond the last guide-block center. The actual largest modeled guide center isY1365.',
                    'Loads act on one rail in the single-force screen. Guide pair results share100N equally between two blocks on that rail; true gantry sharing and tool moments need actual geometry.',
                    'Hydrostatic Navier panels assume all four cell edges are supported and the floor itself remains leak tight. No membrane stiffening is credited.']}
(H/'frame.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'steel1p9':rows[1],'racking':brace,'pan14ga':plate[3:6]},indent=2))
