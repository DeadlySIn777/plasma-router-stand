"""Member buckling, lateral vibration sensitivity and dry support-line screens, N/mm/kg."""
import json
from math import atan, degrees, hypot, pi, sqrt
from pathlib import Path


HERE = Path(__file__).resolve().parent
G = 9.80665
RHO = 7.85e-6  # kg/mm^3, nominal carbon steel
SIDE_POST = 1016 - 31.75 - 69.5
CENTER_POST = 799.5 - 31.75 - 69.5
FOOT_RATING_N = 220 * 4.4482216152605  # retailer claim for one foot


def section_area(width, wall):
    """Hollow square with the same R=2t outside and R=t inside as structure.py."""
    return width**2 - (width-2*wall)**2 - (4-pi) * 3*wall**2


def columns(static):
    rows = []
    for wall, inertia in static["tube_section_I_mm4"].items():
        area = section_area(static["basis"]["tube_width_mm"], float(wall))
        for kind, length in (("outside", SIDE_POST), ("center", CENTER_POST)):
            for K in (1, 2):
                force = pi**2 * static["basis"]["steel_E_MPa"] * inertia / (K*length)**2
                rows.append(dict(post=kind, length_mm=length, wall_mm=float(wall), K=K,
                                 ideal_elastic_Pcr_N=force, stress_at_Pcr_MPa=force/area,
                                 slenderness=K*length/sqrt(inertia/area)))
            assert abs(rows[-2]["ideal_elastic_Pcr_N"]/rows[-1]["ideal_elastic_Pcr_N"] - 4) < 1e-12
    return rows


def vibration(static):
    rows = []
    for b in static["racking"]:
        if b["case"] == "rejected_side":
            continue
        direction = "X" if b["case"] == "end" else "Y"
        key = "830.0" if direction == "X" else "950.0"
        tail = static["individual_post_above_upper_brace_deflection_at_100N_mm"][key]["1.9"]
        force = b["horizontal_force_N"]
        assert force == 100  # tail displacement is evaluated at that load
        # One isolated active panel and one cantilever post head in series at the rail.
        k = force / (b["lateral_drift_mm"] + tail)
        hz = {str(mass):sqrt(1000*k/mass)/(2*pi) for mass in (20, 60, 120)}
        rows.append(dict(direction=direction, panel=b["case"],
                         assumed_net_axial_joint_motion_mm=b["net_axial_end_slip_mm"],
                         secant_stiffness_at_100N_N_per_mm=k, equivalent_Hz_by_effective_kg=hz))
    return rows


def dry_support(static):
    """Subset with known member lengths and locations. Use outside foot centerlines as pivots."""
    basis = static["basis"]
    xs, ys = basis["x_stations_mm"], basis["y_stations_mm"]
    a = section_area(31.75, 1.9)
    pieces = []
    # Intentionally omit drilled backers, beds, 4040s, heads and payload.
    for y in ys:
        pieces.extend((SIDE_POST*a*RHO, x, y) for x in (xs[0], xs[-1]))
        pieces.append((CENTER_POST*a*RHO,xs[1],y))
        pieces.append(((xs[-1]-xs[0]-31.75)*a*RHO,xs[1],y))
    strap_area=25.4*3.175
    for x in (xs[0],xs[-1]):
        for y1,y2 in zip(ys,ys[1:]):
            pieces.append((2*(hypot(y2-y1,800)+25.4)*strap_area*RHO,x,(y1+y2)/2))
    for y in (ys[0],ys[-1]):
        pieces.append((2*(hypot(xs[-1]-xs[0],585)+25.4)*strap_area*RHO,xs[1],y))
    mass=sum(p[0] for p in pieces)
    z=basis["z_rail_center_mm"]
    cases=[]
    for axis,stations,dim,travel in (("X",xs,1,800.),("Y",ys,2,1000.)):
        center=sum(p[0]*p[dim] for p in pieces)/mass
        span=stations[-1]-stations[0]
        # Minimum restoring lever is for motion toward the nearer outside line.
        lever=min(center-stations[0],stations[-1]-center)
        cases.append(dict(axis=axis,subset_CG_mm=center,outer_pivot_spacing_mm=span,
                          smaller_restoring_arm_mm=lever,
                          condition_for_ideal_rigid_tip_external_force_N=mass*G*lever/z,
                          transfer_between_outer_lines_at_100N_N=100*z/span,
                          plane_tilt_for_0p5mm_differential_deg=degrees(atan(.5/span)),
                          height_difference_across_nominal_travel_mm=.5*travel/span))
    return dict(dry_steel_subset_kg=mass,rail_force_height_mm=z,assumed_footprint="Both opposed outer support lines engaged; center feet inside polygon",
                required_static_friction_for_100N_on_subset_only=100/(G*mass),cases=cases)


def main():
    static = json.loads((HERE/"results.json").read_text())
    foot_load=max(max(c["left_center_right_reactions_N"]) for c in static["vertical_wet_crossbeams"])
    modes=vibration(static)
    no_slip=[n for case in modes if case["assumed_net_axial_joint_motion_mm"]==0
             for n in case["equivalent_Hz_by_effective_kg"].values()]
    all_hz=[n for case in modes for n in case["equivalent_Hz_by_effective_kg"].values()]
    result=dict(columns=columns(static), foot=dict(seller_static_one_foot_N=FOOT_RATING_N,
                largest_partial_wet_case_one_support_N=foot_load,
                note="Wet member reactions exclude other frame, gantry and process loads. No installed foot rating or nine-foot load-sharing factor derived."),
                lateral_sensitivity=modes, ideal_no_slip_frequency_scenarios_Hz=[min(no_slip),max(no_slip)],
                all_secant_frequency_scenarios_Hz=[min(all_hz),max(all_hz)],
                excitation_examples=[dict(rpm=rpm,shaft_1x_Hz=rpm/60,two_flute_pass_Hz=2*rpm/60) for rpm in (3000,6000,12000,24000)],
                dry_stability=dry_support(static))
    (HERE/"dynamics.json").write_text(json.dumps(result,indent=2)+"\n")
    return result


if __name__=="__main__":
    main()
