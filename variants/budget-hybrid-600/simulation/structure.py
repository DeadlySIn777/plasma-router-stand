"""Reproducible static member and support screens, N and mm, Python 3 + NumPy."""
from pathlib import Path
import json
from math import hypot, pi

import numpy as np

HERE = Path(__file__).resolve().parent
E_STEEL, E_AL = 200_000., 69_000.
X = (30.8, 575., 1119.2)
Y = (100., 725., 1330.)
BASELINE_Y = (20., 725., 1430.)
WET_N = 1121.3604126184362 + 18.0864 * 9.80665
WALLS = (1.5, 1.9, 2.1)
TOP_RAIL_Z = 1036.  # center of 4040
BRACE_LOW_Z, BRACE_HIGH_Z = 150., 950.
PAN_SUPPORT_X = (370., 780.)
STRAP_AREA = 25.4 * 3.175


def rounded_rectangle_i(width, height, corner):
    """Exact circular-corner section numerically integrated, central Ix=Iy."""
    if corner == 0:
        return width*height**3/12
    a = height/2 - corner
    nodes, weights = np.polynomial.legendre.leggauss(24)
    theta = pi * (nodes + 1) / 4
    y = a + corner * np.sin(theta)
    strips = (width-2*corner + 2*corner*np.cos(theta)) * y*y * corner*np.cos(theta)
    return 2 * (width * a**3 / 3 + pi/4 * np.dot(weights, strips))


def tube_i(t, b=31.75, h=None):
    if h is None:
        h = b
    r = 2*t
    return rounded_rectangle_i(b,h,r) - rounded_rectangle_i(b-2*t,h-2*t,r-t)


def stiffness(EI, length):
    L = length
    return EI / L**3 * np.array([
        [12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],
        [-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])


def beam(stations, support_displacements, EI, q=0., point=None, points=(), loaded_interval=None):
    """Planar Euler-Bernoulli beam; positive displacement and applied load downward."""
    loads = [*points] + ([point] if point else [])
    x = np.array(sorted(set([*stations, *support_displacements, *(xp for xp, _ in loads), *(loaded_interval or ())])))
    start, end = loaded_interval or (x[0], x[-1])
    def line_load(j):
        return q if start <= x[j] < end else 0.
    n = len(x)
    K = np.zeros((2*n,2*n))
    f = np.zeros(2*n)
    for j, L in enumerate(np.diff(x)):
        sl = slice(2*j,2*j+4)
        element_EI = EI((x[j]+x[j+1])/2) if callable(EI) else EI
        K[sl,sl] += stiffness(element_EI,L)
        f[sl] += line_load(j)*L*np.array([.5,L/12,.5,-L/12])
    for xp, force in loads:
        f[2*np.searchsorted(x,xp)] += force
    fixed = np.array([2*np.searchsorted(x,k) for k in support_displacements])
    free = np.setdiff1d(np.arange(2*n),fixed)
    u = np.zeros(2*n)
    u[fixed] = list(support_displacements.values())
    u[free] = np.linalg.solve(K[np.ix_(free,free)], f[free] - K[np.ix_(free,fixed)]@u[fixed])
    # Equilibrium reaction is tabulated positive in upward compression.
    reactions = -(K@u-f)[fixed]
    assert abs(reactions.sum() - (q*(end-start)+sum(force for _,force in loads))) < 1e-5
    # Cubic Hermite displacement plus exact quartic load bubble for uniform q.
    z = np.linspace(0,1,81)
    shape = np.array([1-3*z*z+2*z**3,z-2*z*z+z**3,3*z*z-2*z**3,-z*z+z**3]).T
    samples=[]
    for j,L in enumerate(np.diff(x)):
        vec=u[2*j:2*j+4]*[1,L,1,L]
        element_EI = EI((x[j]+x[j+1])/2) if callable(EI) else EI
        samples.extend(shape@vec + line_load(j)*L**4/(24*element_EI)*z*z*(1-z)**2)
    return {'max_abs_mm':max(abs(np.asarray(samples))),'max_down_mm':max(samples),
            'reactions_N':dict(zip(support_displacements, reactions)),
            'nodal_mm':dict(zip(x,u[::2]))}


def wet_beams(t):
    L=X[-1]-X[0]
    EI=E_STEEL*tube_i(t)
    rows=[]
    for fraction in (1/3, .5):
        P=fraction*WET_N
        q=P/L
        # Also solve with one missing support, and unilateral contact across a known floor gap.
        two=beam(X,{X[0]:0.,X[2]:0.},EI,q)
        for gap in (0.,.5,1.,None):
            engages = gap is not None and bool(two['nodal_mm'][X[1]] > gap)
            supports={X[0]:0.,X[2]:0.}
            if engages: supports[X[1]]=gap
            result=beam(X,supports,EI,q)
            assert min(result['reactions_N'].values()) >= -1e-6
            rows.append({'wall_mm':t, 'wet_share':fraction,'center_gap_mm':gap,
                         'center_contact':engages, 'peak_sag_mm':result['max_down_mm'],
                         'left_center_right_reactions_N':[result['reactions_N'].get(k,0.) for k in X],
                         'gap_that_just_loses_center_contact_mm':two['nodal_mm'][X[1]]})
    return rows


def rail(envelope_start, envelope_end, supports, EI, load=100.):
    # Identify the maximum member displacement and needed hold-down/preload across load locations.
    xs=np.unique(np.r_[np.linspace(envelope_start,envelope_end,151),supports])
    largest=(0,0); uplift=0.
    for loc in xs:
        B=beam([envelope_start,envelope_end],dict.fromkeys(supports,0.),EI,point=(loc,load))
        largest=max(largest,(B['max_abs_mm'],float(loc)))
        uplift=max(uplift,-min(B['reactions_N'].values()))
    return {'peak_abs_mm':largest[0],'load_y_at_peak_mm':largest[1],'max_incremental_uplift_N':uplift}


def brace(width, height, force, anchor_slip):
    # One isolated X panel receives the entire lateral load; only the tension diagonal works.
    length=hypot(width,height)
    projection=width/length
    T=force/projection
    return {'bay_width_mm':width,'brace_height_mm':height,'horizontal_force_N':force,
            'net_axial_end_slip_mm':anchor_slip,'tension_N':T,
            'lateral_drift_mm':(T*length/(E_STEEL*STRAP_AREA)+anchor_slip)/projection}


def pan_frame(t):
    """Separate path: line-loaded longitudinal 4040s -> point loads at the two beam seats."""
    wet_pan_N = 100. * 9.80665  # proof-load scenario including stock; not measured tare
    rows = []
    for share in (.5, .65):
        stringers = []
        for tributary in (share,1-share):
            w = wet_pan_N*tributary/1030.
            stringers.append(beam([0.,1450.],dict.fromkeys(Y,0.),E_AL*8.3e4,
                                  q=w, loaded_interval=(55.,1085.)))
        for y in Y:
            loads = [(k,s['reactions_N'][y]) for k,s in zip(PAN_SUPPORT_X,stringers)]
            for middle in (True,False):
                supports = dict.fromkeys(X if middle else (X[0],X[2]),0.)
                b = beam(X,supports,E_STEEL*tube_i(t),points=loads)
                rows.append({'wall_mm':t,'left_stringer_fraction':share,'frame_station_y':y,
                             'middle_foot_seated':middle,'left_right_seat_loads_N':[p for _,p in loads],
                             'peak_crossbeam_abs_mm':b['max_abs_mm'],
                             'pan_stringer_peak_abs_mm':max(s['max_abs_mm'] for s in stringers)})
    return rows


def pan_floor_strip(t, depth):
    # Hydrostatic pressure at a flat datum (N/mm²); add the steel floor's gravity.
    w = 1000*9.80665*(depth/1000)/1e6 + 7850*9.80665*(t/1000)/1e6
    EI = E_STEEL*t**3/12  # one-millimeter strip
    span = PAN_SUPPORT_X[1]-PAN_SUPPORT_X[0]
    return {'thickness_mm':t,'assumed_water_depth_mm':depth, 'pressure_plus_floor_weight_N_mm2':w,
            'isolated_simple_span_between_stringers_mm':5*w*span**4/(384*EI),
            'isolated_cantilever_lip_with_fixed_root_mm':w*(370.-160.)**4/(8*EI)}


def ledger_and_bridge(web_extra=0., web_thickness=1.90):
    """Priced angle plus optional edge-welded net extra vertical web; no composite workboard credit."""
    b,t = 25.4,3.175
    rects = [(b,t,t/2),(t,b-t,(b+t)/2)]
    if web_extra:
        rects.append((web_thickness,web_extra,b+web_extra/2))
    zbar = sum(w*h*z for w,h,z in rects)/sum(w*h for w,h,z in rects)
    inertia = sum(w*h**3/12+w*h*(z-zbar)**2 for w,h,z in rects)
    intervals=((116.,709.),(741.,1314.))
    rigid_y = sorted({v for s in Y for v in (s-12.7,s,s+12.7)})
    partitions = [60.,1395.,*rigid_y,*[val for pair in intervals for val in pair]]
    I_flange = b*t**3/12
    I_base = 9042.397384759113  # unreinforced L25.4 x 3.175
    def ledger_EI(y):
        if any(abs(y-s) <= 12.7 for s in Y):
            return E_STEEL*I_flange  # vertical leg cut back to land on each riser
        if any(lo<y<hi for lo,hi in intervals):
            return E_STEEL*inertia
        return E_STEEL*I_base
    EIb=E_STEEL*tube_i(1.5,25.4,50.8)
    worst={}
    for panel in range(4):
        ys=[103.4+259*panel+off for off in (34.7,129.7,224.7)]
        for forces in [[(y,100.)] for y in ys]+[[(y,50.),(yy,50.)] for y,yy in zip(ys,ys[1:])]:
            supports=dict.fromkeys(Y,0.)
            ledger=beam(partitions,supports,ledger_EI,points=[(y,P/2) for y,P in forces])
            settle=sum(ledger['nodal_mm'][y] for y,P in forces)/len(forces)
            bend=forces[0][1]*906.6**3/(48*EIb)
            mdf=0. if len(forces)==1 else 100.*95.**3/(48*2500.*100*12.**3/12)
            key='directly_over_one_bar' if len(forces)==1 else 'between_two_bars'
            total=settle+bend+mdf
            if key not in worst or total>worst[key]['partial_work_deflection_mm']:
                worst[key]={'panel_index':panel+1,'load_y_mm':sum(y for y,P in forces)/len(forces),
                            'ledger_settlement_mm':settle,'dry_bar_bending_mm':bend,'mdf_midbay_mm':mdf,
                            'partial_work_deflection_mm':total}
    return {'extra_web_net_mm':web_extra,'extra_web_thickness_mm':web_thickness,
            'ledger_I_mm4':inertia,'cases':worst}


def rack_shelves():
    # Square/rectangular hollow shape area, including the same rounded corners as the tube inertia.
    def area(b,h,t):
        return b*h-(4-pi)*(2*t)**2-((b-2*t)*(h-2*t)-(4-pi)*t**2)
    module_kg=(3*892*area(25.4,50.8,1.5)+4*69.6*area(25.4,25.4,1.5))*7.85e-6
    positions=[1281+55*i-50.8/2 for i in range(4)]
    forward, aft, post_center = 1304.6,1355.4,1330.
    rows=[]
    # Test every subset of the rack, including asymmetric loads during sequential insertion.
    # The local arm attaches to the face of the rectangular post. The post bends also.
    import itertools
    states=[s for n in range(1,5) for s in itertools.combinations(positions,n)]
    post_I=tube_i(1.5,25.4,50.8)
    post_h=120.74
    for web in (0.,25.):
        strips=[(25.4,4.76,4.76/2)]
        if web:
            strips.append((1.9,web,4.76+web/2))
        centroid=sum(w*h*c for w,h,c in strips)/sum(w*h for w,h,c in strips)
        I=sum(w*h**3/12+w*h*(c-centroid)**2 for w,h,c in strips)
        for share in (.5,1.):
            P=share*module_kg*9.80665
            max_defl=max_stress=0.
            for occupied in states:
                moment=P*sum(y-post_center for y in occupied)
                rotation=moment*post_h/(E_STEEL*post_I)
                for plane,tip,sgn in ((forward,1228.,-1.),(aft,1450.,1.)):
                    L=abs(tip-plane)
                    arms=[max(0.,sgn*(p-plane)) for p in occupied]
                    local=sum(P*a*a*(3*L-a) for a in arms)/(6*E_STEEL*I)
                    max_defl=max(max_defl,abs(local+rotation*(tip-post_center)))
                    max_stress=max(max_stress,max(centroid,4.76+web-centroid)*P*sum(arms)/I)
            rows.append({'web_depth_mm':web,'load_share_to_one_arm':share,
                         'maximum_tip_displacement_including_post_rotation_mm':max_defl,
                         'maximum_shelf_root_MPa':max_stress})
    return {'bare_tube_mass_per_carrier_kg':module_kg,'stocked_center_y_mm':sum(positions)/4,
            'approx_carrier_center_z_mm':1032.7,'positions_y_mm':positions,
            'front_and_rear_shelf_lengths_mm':[forward-1228.,1450.-aft],'cases':rows}


def main():
    # Regression to two textbook cases, reaction recovery and symmetry.
    EI=12_345_678_900.; L=900.; F=110.; q=.65
    st={0.:0.,L:0.}
    b=beam([0.,L],st,EI,point=(L/2,F))
    assert abs(b['max_down_mm']-F*L**3/(48*EI))<1e-9
    assert abs(beam([0.,L],st,EI,q)['max_down_mm']-5*q*L**4/(384*EI))<1e-9
    assert abs(rounded_rectangle_i(31.75,31.75,0)-31.75**4/12)<1e-9
    rails=[]
    for Icm in (6.,8.3,10.):
        for name,posts,steel_share in [('prior_4040',BASELINE_Y,0),('new_unbacked',Y,0),
                                       ('new_half_participation',Y,.5),('new_full_noncomposite',Y,1),
                                       ('new_middle_station_lost',(Y[0],Y[2]),1)]:
            beam_EI=E_AL*Icm*1e4 + steel_share*E_STEEL*tube_i(1.9)
            rails.append({'case':name,'al_I_cm4':Icm, 'backer_wall_mm':1.9, 'load_N':100.,
                          **rail(0,1450,posts,beam_EI)})
    # Under the point load applied to one projected side post. Cantilever segment fixed at the high X-brace node.
    # Excludes rotation of the brace node; one-post/local T-slot stiffness is additional.
    head=100.
    r={'basis':{'x_stations_mm':X,'y_stations_mm':Y,'legacy_y_stations_mm':BASELINE_Y,
                'z_rail_center_mm':TOP_RAIL_Z,'brace_low_high_z_mm':[BRACE_LOW_Z,BRACE_HIGH_Z],
                'wet_bed_and_stock_N':WET_N,'steel_E_MPa':E_STEEL,'aluminum_E_MPa':E_AL,
                'tube_width_mm':31.75,'outer_corner_radius_over_wall':2,
                'wet_load_composition':'Inherited 1121.36 N wet assembly plus 18.0864 kg example sheet; no chassis/gantry self-weight applied in individual member load screens.'},
       'tube_section_I_mm4':{str(t):tube_i(t) for t in WALLS},
       'vertical_wet_crossbeams':[row for t in WALLS for row in wet_beams(t)],
       'vertical_Y_beams':rails,
       'pan_frame_concentrated':[r for t in WALLS for r in pan_frame(t)],
       'simplified_pan_floor_strips':[pan_floor_strip(t,d) for t in (1.8974,2.6568) for d in (34.,43.)],
       'pan_volume_liters_flat_steel':{str(d):830.*1030.*(d-5.15/2)/1e6 for d in (34.,43.)},
       'slat_midspan_100N_mm':{str(t):100.*400.**3/(48*E_STEEL*(t*30.**3/12)) for t in (1.8974,2.6568)},
       'thermal_screen':{'ambient_C':20.,'steel_alpha_per_K':12e-6,'al_alpha_per_K':23.5e-6,
            'uniform_temperature_scenarios':[{'body_C':temp,'pan_steel_length_growth_mm':12e-6*(temp-20)*1030,
                 'longitudinal_rail_backer_free_growth_difference_mm':(23.5e-6-12e-6)*(temp-20)*1450}
                 for temp in (45,65)],
            'transverse_410mm_free_strip_bow_due_to_5K_face_to_face_mm':
                {str(t):12e-6*5.*410.**2/(8*t) for t in (1.8974,2.6568)}},
       'racking':[dict(case=label,**brace(w,hi-lo,head,s)) for label,w,lo,hi in
                 [('rejected_side',605.,150.,780.),('side_front',625.,150.,950.),('side_rear',605.,150.,950.),('end',1088.4,245.,830.)] for s in (0.,.1,.3)],
       'individual_post_above_upper_brace_deflection_at_100N_mm':
          {str(high):{str(t):head*(TOP_RAIL_Z-high)**3/(3*E_STEEL*tube_i(t)) for t in WALLS} for high in (780.,830.,BRACE_HIGH_Z)},
       'horizontal_tool_load_foot_checks':{'force_N':head,'centered_wet_subset_N':WET_N,
            'required_mu_if_all_subset_weight_engaged':head/WET_N,
            'transferred_opposing_support_line_load_N_X':head*TOP_RAIL_Z/(X[-1]-X[0]),
            'transferred_opposing_support_line_load_N_Y':head*TOP_RAIL_Z/(Y[-1]-Y[0])},
       'dry_ledger_and_work_stiffness':[ledger_and_bridge(d) for d in (0.,25.)],
       'dry_crossbars':{'width_mm':25.4,'wall_mm':1.5,'span_mm':906.6,'beam_center_pitch_mm':190.,
            'single_midspan_100N_mm':100.*906.6**3/(48*E_STEEL*tube_i(1.5,25.4)),
            'equal_shared_50N_per_bar_mm':50.*906.6**3/(48*E_STEEL*tube_i(1.5,25.4))},
       'rack_shelves':rack_shelves(),
       'narrow_final_carriers':{'bearing_span_mm':866.6,'single_bar_sag_mm_100N':100.*866.6**3/(48*E_STEEL*tube_i(1.5,25.4,50.8))},
       'revised_dry_crossbars':{'tube_width_mm':25.4,'tube_height_mm':50.8,'wall_mm':1.5,
            'quantity_per_module':3,'span_mm':906.6,'pitch_mm':95.,
            'major_I_mm4':tube_i(1.5,25.4,50.8),
            'midspan_mm_by_load_per_bar_N':{str(P):P*906.6**3/(48*E_STEEL*tube_i(1.5,25.4,50.8))
                                            for P in (100.,50.,100./3)}},
       'mdf_strip_sensitivity':[{'width_engaged_mm':b,'E_MPa':em,'pitch_mm':pitch,
            'sag_mm_100N':100.*pitch**3/(48*em*b*12.**3/12)} for pitch in (95.,190.)
                                for b in (50.,100.,200.) for em in (2200.,2500.,3000.)],
       'dry_seat_100N_extra':{'comment':'Isolated member point load at halfway between left and middle column; ignores work carrier/deck compliance.',
            'midbay_100N_max_abs_mm':beam(X,dict.fromkeys(X,0.),E_STEEL*tube_i(1.9),point=((X[0]+X[1])/2,100))['max_abs_mm']},
       'checks':'Two closed-form simple-beam comparisons reproduce to 1e-9 mm; force equilibrium checked on every solve.'}
    (HERE/'results.json').write_text(json.dumps(r,indent=2)+'\n')
    return r

if __name__=='__main__':
    main()

